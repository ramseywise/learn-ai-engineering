# Worked Example: SQLite Data Pipeline → The Scaling Trap (40 min, offline)

> **Constraint note:** `sqlite3` is in the Python standard library — no install, no server, no network. That is exactly why assessments use it, and exactly why the scaling question is coming.

**Format:** 40 min, browser editor, interviewer watching.
**Prompt:** *"Build a pipeline that ingests these event records into a database and supports querying daily totals per user."*
**The follow-up that is the actual exercise:** *"This needs to serve millions of requests a day. Does this design hold?"*

The prompt is a trap in the useful sense: the tool you're handed is correct for the exercise and wrong for the stated scale. Candidates fail this in two opposite directions — defending SQLite because they wrote it, or trashing SQLite as a toy. Both miss. The graded answer names *the specific mechanism* that breaks and maps each workload to the right store.

---

## 0–5 min — build it well, but flag the seam early

Do not pre-emptively refuse to use SQLite. Build the thing, but plant the flag in minute three so the follow-up finds you already there.

[NARRATE: "I'll use `sqlite3` since it's stdlib and zero-setup — right call for this exercise. I want to flag now that I'm putting all database access behind a small interface, because if this ever needs to serve real concurrent traffic, SQLite's write model becomes the constraint and I'd want the swap to be one class, not a grep across the codebase."]

That sentence costs eight seconds and buys the entire follow-up.

---

## 5–20 min — the implementation

```python
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    event_id   TEXT PRIMARY KEY,          -- natural key -> idempotent ingest
    user_id    TEXT NOT NULL,
    amount     INTEGER NOT NULL,          -- cents, not float
    occurred_at TEXT NOT NULL             -- ISO8601 UTC
);
CREATE INDEX IF NOT EXISTS idx_events_user_day ON events(user_id, occurred_at);
"""


class EventStore:
    """All database access lives here — the seam to swap for Postgres."""

    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")     # readers don't block on the writer
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript(SCHEMA)

    @contextmanager
    def transaction(self):
        """Explicit transaction boundary; rolls back on any exception."""
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
```

[NARRATE: "Three decisions worth naming. Amounts as integer cents rather than a float column — SQLite has no decimal type, and float currency accumulates representation error. `event_id` as the primary key so re-ingesting the same batch is idempotent rather than duplicating. And WAL mode, which lets readers proceed while a write is in flight — without it, readers block the writer and each other."]

WAL is the detail that separates someone who has *operated* SQLite from someone who has only imported it.

```python
    def ingest(self, records: list[dict]) -> tuple[int, int]:
        """Bulk insert, ignoring duplicates. Returns (inserted, skipped)."""
        rows = []
        for r in records:
            try:
                rows.append((
                    r["event_id"],
                    r["user_id"],
                    int(round(float(r["amount"]) * 100)),
                    datetime.fromisoformat(r["occurred_at"])
                        .astimezone(timezone.utc).isoformat(),
                ))
            except (KeyError, ValueError, TypeError) as e:
                log.warning("skipping malformed record %r: %s", r.get("event_id"), e)

        with self.transaction() as conn:
            before = conn.total_changes
            conn.executemany(
                "INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?)", rows
            )
            inserted = conn.total_changes - before
        return inserted, len(records) - inserted
```

[NARRATE: "`executemany` inside a single transaction, not a loop of individual inserts — each implicit transaction is an fsync, so per-row commits are roughly two orders of magnitude slower. `INSERT OR IGNORE` against the primary key gives me idempotency for free: re-running a batch is a no-op rather than a duplicate-key crash."]

[NARRATE: "And parameterized queries throughout — never f-strings into SQL. That's the injection boundary, and it's also faster because SQLite caches the prepared statement."]

```python
    def daily_totals(self, user_id: str) -> list[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT substr(occurred_at, 1, 10) AS day,
                   SUM(amount) AS total_cents,
                   COUNT(*)    AS event_count
            FROM events
            WHERE user_id = ?
            GROUP BY day
            ORDER BY day
            """,
            (user_id,),
        ).fetchall()
```

[NARRATE: "The index on `(user_id, occurred_at)` matches the filter — leading column is the equality predicate, so this is an index seek rather than a table scan."]

**Then actually check it**, rather than asserting it. `EXPLAIN QUERY PLAN` is one line and it is a strong move in an interview:

```python
>>> conn.execute("EXPLAIN QUERY PLAN " + QUERY, (user_id,)).fetchall()
SEARCH events USING INDEX idx_events_user_day (user_id=?)
USE TEMP B-TREE FOR GROUP BY
```

[NARRATE: "The seek is confirmed. But note the second line — it's still building a temp B-tree for the GROUP BY, because I'm grouping on `substr(occurred_at, 1, 10)`, which is a derived expression the index can't satisfy. If this query were hot I'd store a `day` column directly and index `(user_id, day)`, so the grouping reads in index order and the temp B-tree disappears. I'm leaving it for now because the dataset is small — but I'd rather show you the plan than claim the index does more than it does."]

Running the plan and reading it honestly — including the part that didn't get optimized — is a stronger signal than an index that happens to be right.

---

## 20–35 min — the follow-up, which is the real question

> *"This needs to serve millions of requests a day. Does this design hold?"*

**The wrong answers**, both common:

- *"SQLite doesn't scale, we'd use Postgres."* — True conclusion, no reasoning. Reads as memorized.
- *"It's fine, SQLite is fast, it handles terabytes."* — Also technically true and completely non-responsive.

**The answer that lands** — name the mechanism, then split the workload:

[NARRATE: "It holds for reads and breaks on writes, and the reason is specific: SQLite allows exactly one writer at a time. It's a file with a lock, not a server with a connection pool. Even in WAL mode — which is what lets readers run concurrently with a writer — writes still serialize. So at millions of requests a day, if a meaningful share are writes, they queue behind that single lock and you get `SQLITE_BUSY` and lock-timeout errors. That's not something you tune away; it's the architecture."]

[NARRATE: "There's a second, more operational problem: SQLite is a local file. It lives on one machine's disk, so you can't run three stateless API replicas against it. The moment you want horizontal scaling or a rolling deploy, you need a database that speaks over a network."]

Then split the workload — this is the OLTP/OLAP discrimination the MCQ bank tests:

[NARRATE: "I'd also stop treating this as one workload. There are two here with opposite access patterns. The ingest-and-serve path is transactional — high-frequency small writes, point lookups by user, needs row-level concurrency and ACID. That's **Postgres**: real MVCC so readers never block writers, a connection pool, replicas for read scaling. The daily-totals path is analytical — it scans a large fraction of the table and aggregates one or two columns. That's a **columnar** store: Redshift, BigQuery, Snowflake, ClickHouse. Column storage means a `SUM(amount)` reads only the amount column instead of every row, and it compresses far better because a column is uniform in type."]

[NARRATE: "Running heavy aggregations against the transactional primary is the specific failure I'd want to avoid — the analytical scan competes for buffer pool and I/O with the writes that are serving users, so a reporting query degrades checkout latency. You separate them and move data across with CDC or a periodic batch load, accepting some staleness on the analytics side."]

**If asked "how would you migrate?"** — the honest, unglamorous answer:

[NARRATE: "The schema ports almost directly; the work is in the details. `TEXT` timestamps become real `TIMESTAMPTZ`, integer cents become `NUMERIC(12,2)`, and `INSERT OR IGNORE` becomes `ON CONFLICT DO NOTHING`. Because all access is behind `EventStore`, the surface area is one class. The genuinely hard part isn't the code — it's the cutover: dual-write, backfill, verify counts match, then flip reads."]

**If asked "when is SQLite actually right?"** — do not over-correct into dismissing it:

[NARRATE: "It's an excellent choice more often than its reputation suggests: single-writer workloads, embedded and edge deployments, local caches, test fixtures, anything read-mostly on one machine. It's the most-deployed database in the world. The constraint is concurrent writers and network access, not capability or size — a read-heavy service on one box with SQLite can outperform a network round-trip to Postgres because there's no serialization or socket in the path."]

That balance is the difference between judgment and pattern-matching. An interviewer who hears only "SQLite bad" learns less about you than one who hears "here is precisely when it's right."

---

## 35–40 min — close

[NARRATE: "To summarize the path: SQLite is correct today and correct for a single-writer service. At the stated scale I'd move the transactional path to Postgres for write concurrency and network access, and fan the analytical path out to a columnar warehouse so reporting scans don't contend with user-facing writes. The migration surface is one class because the access is already isolated. What I'd want before committing: the actual read/write ratio and whether the daily totals need to be real-time or can tolerate an hour of staleness — that single answer decides whether this is CDC or a nightly batch."]

Ending on the question whose answer changes the design is a strong close. It shows you know which unknown actually matters.

---

## The comparison table, for recall under pressure

| | SQLite | Postgres | Redshift / BigQuery / ClickHouse |
|---|---|---|---|
| Model | Embedded file | Client–server | Columnar warehouse |
| Concurrent writers | **One** (file lock) | Many (MVCC) | Batch / bulk load |
| Workload | Read-mostly, single-node | OLTP | OLAP |
| Scaling | Vertical only | Vertical + read replicas | Horizontal, MPP |
| Network access | No — local file | Yes | Yes |
| Aggregation over millions of rows | Slow (row storage) | Workable, contends with writes | Purpose-built |
| Right when | Edge, embedded, tests, local cache | Transactions, concurrency | Reporting, dashboards, BI |

**The one-liner to have cold**: *SQLite serializes writers because it's a locked file, not a server — that's the wall, and it arrives long before storage size does.*

---

## What the interviewer is grading

| Signal | Where it appeared |
|---|---|
| Builds correctly before critiquing | Working pipeline first; didn't refuse the tool |
| Planted the seam early | Named the swap boundary in minute 3, before the follow-up |
| Operational depth | WAL mode, `executemany` in one transaction, index matched to the query |
| Names the mechanism | Single-writer lock — not "doesn't scale" |
| Second-order constraint | Local file blocks horizontal scaling and rolling deploys |
| OLTP/OLAP split | Two workloads, opposite access patterns, mapped to Postgres + columnar |
| Knows why columnar wins | Reads one column, compresses uniformly |
| Balanced | Can say when SQLite is the *right* answer |
| Knows the real risk | Cutover, not code |

The weakest version writes string-formatted SQL, commits per row, stores currency as float, and answers the follow-up with "we'd use a bigger database."
