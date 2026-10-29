---
origin: curated
sources:
  - "Software Carpentry, Databases and SQL, episodes 08–09 — https://swcarpentry.github.io/sql-novice-survey/ (CC-BY 4.0)"
  - "PGExercises, Modifying Data — https://pgexercises.com/questions/updates/ (CC BY-SA 3.0)"
concepts: [sql-ddl, sql-constraints, sql-normalization, sql-transactions, sql-upsert]
cleaned: 2026-10-29
---
# 7 — Designing Tables and Changing Data

> A schema makes promises about its data. Constraints let the database keep those promises for you.

---

## Data hygiene: the rules behind normal forms

From Software Carpentry's checklist, which covers 90% of normalisation in practice:

1. **Each value is atomic.** Store `personal` and `family` names separately, not `"William Dyer"` in one field. You can always concatenate later, but splitting reliably is hard.
2. **Each record has a unique key** that never changes and carries no meaning (`memid`, not the member's email).
3. **No redundant data.** Store the facility's cost once, in `facilities`, not copied into every booking. Redundant copies drift apart.
4. **Units are explicit.** Put them in the column name (`reading_c`, `duration_slots`) or in a separate column.

Breaking rule 3 on purpose, by denormalising, is a legitimate choice for analytics tables built by a pipeline. Make sure the pipeline, not humans, keeps the copies in sync.

## Creating tables

```sql
CREATE TABLE facility_price_history (
    facid      INTEGER NOT NULL REFERENCES facilities(facid),
    valid_from DATE    NOT NULL,
    membercost NUMERIC NOT NULL CHECK (membercost >= 0),
    guestcost  NUMERIC NOT NULL CHECK (guestcost >= membercost),
    PRIMARY KEY (facid, valid_from)
);
```

| Constraint | Promise |
|---|---|
| `PRIMARY KEY` | Unique and not `NULL`. One per table, and it can span several columns |
| `UNIQUE` | No duplicates, though it allows multiple `NULL`s |
| `NOT NULL` | The value must be present |
| `CHECK (…)` | An arbitrary condition on each row |
| `REFERENCES` / `FOREIGN KEY` | The value must exist in the parent table. `ON DELETE CASCADE / SET NULL / RESTRICT` sets what happens when the parent row goes |
| `DEFAULT …` | The value used when an insert omits the column |

SQLite enforces foreign keys only after `PRAGMA foreign_keys = ON;` (once per connection). This is the single most common SQLite surprise.

## Changing data

```sql
INSERT INTO facilities (facid, name, membercost, guestcost, initialoutlay, monthlymaintenance)
VALUES (9, 'Spa', 20, 30, 100000, 800);

UPDATE facilities SET initialoutlay = 10000 WHERE facid = 1;

DELETE FROM bookings WHERE memid = 37;
```

**`UPDATE` or `DELETE` without `WHERE` changes every row.** Before running one, run the same `WHERE` as a `SELECT count(*)` to see how many rows it would touch.

### Upsert

```sql
INSERT INTO facilities (facid, name, membercost, guestcost, initialoutlay, monthlymaintenance)
VALUES (9, 'Spa', 25, 35, 100000, 800)
ON CONFLICT (facid) DO UPDATE SET membercost = excluded.membercost, guestcost = excluded.guestcost;
```

`ON CONFLICT … DO UPDATE` works in SQLite, Postgres and DuckDB. `excluded` refers to the row you tried to insert. Idempotent loads, where re-running a pipeline step doesn't duplicate data, are built on upserts or on delete-then-insert inside a transaction.

## Transactions

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;      -- or ROLLBACK; to undo both
```

A transaction is **atomic**: either every statement takes effect or none does. Wrap multi-step writes in one. In Python, `with sqlite3.connect(…) as conn:` commits on success and rolls back on an exception ([note 09](09-sql-from-python.md)).

## Views

```sql
CREATE VIEW member_usage AS
SELECT memid, count(*) AS bookings, sum(slots) AS slots FROM bookings GROUP BY memid;
```

A view is a saved query, so it always reflects the current data. A materialised view (Postgres), or a table rebuilt by your pipeline, stores the result for speed at the cost of going stale.

---

## Exercises

[`practice/exercises/07-modeling-and-ddl.sql`](../practice/exercises/07-modeling-and-ddl.sql). The exercises run against a throwaway copy of `clubdata.db`.
