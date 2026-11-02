# Code From Heart — the fundamentals to have cold

The browser-assessment constraint (no AI, no docs, no autocomplete, 30–45 min) changes what "prepared" means. You don't need breadth; you need a small set of patterns your fingers produce without thinking, so the whole timebox goes to the *problem* instead of to recalling syntax.

This is that set. Everything here is stdlib. If you can write these without looking, you can build any of the six worked examples in [examples/](examples/).

**How to use it**: cover the code column, read the "you need this when" column, and write the pattern from scratch. Anything you hesitate on for more than five seconds is a drill target. Twenty minutes a day beats one long session.

---

## 1. Aggregation — the single most likely thing you write

Almost every practical prompt reduces to *group these records and compute something per group*.

```python
from collections import defaultdict, Counter

# Sum per key
totals = defaultdict(int)
for r in records:
    totals[r["user_id"]] += r["amount"]

# Collect per key
by_user = defaultdict(list)
for r in records:
    by_user[r["user_id"]].append(r)

# Count occurrences / top-N
counts = Counter(r["category"] for r in records)
counts.most_common(3)

# Nested grouping: user -> day -> total
nested = defaultdict(lambda: defaultdict(int))
for r in records:
    nested[r["user_id"]][r["date"]] += r["amount"]
```

`defaultdict(lambda: defaultdict(int))` is the one people fumble under pressure. Practice it specifically — the inner factory must be callable, so `defaultdict(defaultdict(int))` is the wrong version that looks right.

**`setdefault` vs `defaultdict`**: `setdefault` is fine for one-off use; `defaultdict` is cleaner when you're accumulating in a loop. Know both exist, use `defaultdict`.

**Gotcha worth naming out loud**: `defaultdict` inserts on *read*. `if totals[k] > 0` creates the key. Use `.get(k, 0)` when you only want to look.

---

## 2. Sorting

```python
sorted(records, key=lambda r: r["amount"], reverse=True)

# Multi-key, same direction
sorted(records, key=lambda r: (r["user_id"], r["date"]))

# Multi-key, OPPOSITE directions — negate the numeric one
sorted(records, key=lambda r: (-r["amount"], r["name"]))

# Sort a dict by value
sorted(totals.items(), key=lambda kv: kv[1], reverse=True)

from operator import itemgetter
sorted(records, key=itemgetter("amount"))     # faster, less flexible
```

Descending by number *and* ascending by name in one pass requires the negation trick — `reverse=True` flips both. That's the version interviewers probe.

**Stability**: Python's sort is stable, so sorting twice (secondary key first, then primary) also works and is sometimes more readable.

---

## 3. Comprehensions

```python
[r["id"] for r in records if r["amount"] > 100]
{r["user_id"] for r in records}                          # set — dedup
{r["id"]: r for r in records}                            # dict — index by id
{k: v for k, v in totals.items() if v > 0}               # filter a dict
[item for sub in nested_lists for item in sub]           # flatten (order: outer, inner)
(r["amount"] for r in records)                           # generator — lazy, no list built
```

Flatten order is the classic slip: it reads left-to-right exactly like the nested `for` loops you'd write out.

Reach for a generator when you're feeding `sum()`/`max()`/`any()` and don't need the list.

---

## 4. Dicts and sets

```python
d.get(key, default)                  # no KeyError
d.setdefault(key, []).append(x)
{**a, **b}                           # merge, b wins   (or a | b, 3.9+)
d.items() / d.keys() / d.values()

a & b    # intersection — "which of these are also in that"
a | b    # union
a - b    # difference — "which are missing"
a <= b   # subset — the scope check in the auth example
```

Set operations are how you write membership logic without loops. `set(claimed) & set(valid_ids)` is the grounding check in the RAG example; `set(required) <= set(granted)` is the scope check in the auth example. Both are one line because sets are the right tool.

---

## 5. Strings

```python
"\n".join(parts)                      # never build with += in a loop
f"{value:.2f}"                        # 2 decimals
f"{value:,}"                          # thousands separator
f"{ratio:.1%}"                        # percent
f"{name:<20}{count:>5}"               # left/right pad — table output
text.strip().lower().split()
line.partition(" ")                   # split ONCE, always returns 3 parts
", ".join(f"[{d}]" for d in doc_ids)
```

`partition` over `split(" ", 1)` when you want the "before / sep / after" shape and need it safe on a missing separator — it returns empty strings rather than a short list you have to length-check. That's how the `Authorization: Bearer <tok>` header gets parsed.

Building a prompt is just `"\n".join(...)` over a list of sections. Don't overthink it.

---

## 6. Dataclasses and validation

```python
from dataclasses import dataclass, field

@dataclass
class Answer:
    text: str
    confidence: str
    sources: list[str] = field(default_factory=list)   # NEVER = []

    def __post_init__(self):
        if self.confidence not in {"high", "medium", "low"}:
            raise ValueError(f"bad confidence: {self.confidence}")
```

Two things graded here:

- **`field(default_factory=list)`** — a bare `= []` is a shared mutable default across all instances. Dataclasses actually raise on this, which is a gift; the same bug in a plain function signature (`def f(x=[])`) is silent and is a top-tier interview question.
- **`__post_init__`** for validation — this is where you say *"in production this is a Pydantic model with a field validator; the constructor check is the stdlib equivalent."* Naming the mapping is the signal.

Also have `@dataclass(frozen=True)` (hashable, usable as a dict key) and `@dataclass(slots=True)` (lower memory) in your back pocket.

---

## 7. Exceptions

```python
try:
    data = json.loads(raw)
except json.JSONDecodeError as e:          # specific, not bare except
    log.warning("bad payload: %s", e)
    return FALLBACK
except (KeyError, TypeError) as e:         # group related handling
    raise ValueError(f"malformed record: {e}") from e   # preserve the chain
finally:
    conn.close()                            # runs regardless

class RetrievalError(Exception):
    """Domain error — lets callers catch YOUR failures, not every failure."""
```

The graded decisions: **catch specific exceptions**, **`raise ... from e`** so the original traceback survives, and **know when to swallow vs propagate**. Swallow at a boundary where you have a sane fallback (one malformed record in a batch of 10,000). Propagate when continuing would produce a wrong answer silently.

`log.exception(...)` inside an `except` block logs the traceback automatically — use it instead of `log.error(str(e))`, which throws the stack away.

---

## 8. Similarity and retrieval

```python
from collections import Counter

def score(query: str, doc: str) -> float:
    """Lexical overlap, length-normalized. BM25's intuition, ten lines."""
    q = Counter(query.lower().split())
    d = Counter(doc.lower().split())
    if not d:
        return 0.0
    overlap = sum(min(c, d[t]) for t, c in q.items())
    return overlap / (len(doc.split()) ** 0.5)

top_k = sorted(docs, key=lambda doc: score(query, doc["text"]), reverse=True)[:3]
```

The `** 0.5` matters: without length normalization, long documents win every query just by containing more words. Saying that out loud is the difference between "I wrote a scorer" and "I know why retrieval ranks the way it does."

Cosine similarity, if you have vectors and no numpy:

```python
def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0
```

The `if na and nb` guard is the zero-vector case. Divide-by-zero guards are cheap and always noticed.

---

## 9. Money, time, and numbers

```python
from decimal import Decimal
Decimal("19.99") + Decimal("0.01")        # exact
0.1 + 0.2 == 0.3                          # False — never float for currency

from datetime import datetime, timezone
datetime.now(timezone.utc)                                    # aware, always
datetime.fromisoformat(s).astimezone(timezone.utc).isoformat()  # normalize on ingest
```

Store money as `Decimal` or integer cents. Store time as UTC and convert at the display edge. Both are one-line habits that read as production experience, and both come up in any transaction-processing prompt.

**Median over mean** when outliers exist — and MAD (median absolute deviation) over standard deviation for anomaly detection, because a single large outlier inflates σ enough to hide itself.

---

## 10. Files, JSON, CSV

```python
import json, csv

with open(path) as f:              # context manager closes on exception
    data = json.load(f)

with open(path, newline="") as f:
    for row in csv.DictReader(f):  # row is a dict keyed by header
        ...

json.dumps(obj, separators=(",", ":"))   # compact
json.dumps(obj, indent=2, sort_keys=True)  # stable diffs
```

`csv.DictReader` over manual `.split(",")` — the split version breaks on the first quoted field containing a comma, and someone will hand you that file.

---

## 11. The API/HTTP layer

You rarely write a real server in a browser assessment, but you're expected to *reason* about it.

| Code | Meaning | The confusion to avoid |
|---|---|---|
| 200 / 201 | OK / Created | 201 for a resource-creating POST |
| 400 | Malformed request | Client sent junk |
| 401 | Unauthenticated | **We don't know who you are** |
| 403 | Unauthorized | **We know, you're not allowed** |
| 404 | Not found | Also used to hide 403s from probing |
| 409 | Conflict | Duplicate create, version mismatch |
| 422 | Valid syntax, invalid content | Well-formed JSON, bad field values |
| 429 | Rate limited | Send `Retry-After` |
| 500 / 503 | Our fault / temporarily down | 503 is retryable, 500 usually isn't |

Concepts to be able to define in one sentence each:

- **Idempotency** — same request twice has the same effect as once. `PUT` and `DELETE` are idempotent by definition; `POST` isn't, which is why creation endpoints take an idempotency key. `INSERT OR IGNORE` on a natural key is the database-level version of the same idea.
- **Pagination** — offset/limit is simple but drifts when rows are inserted mid-scan; cursor/keyset pagination is stable and is what you want for large or live datasets.
- **Rate limiting** — token bucket (allows bursts, refills at a fixed rate) vs fixed window (simple, but lets a client double the limit across a window boundary). Token bucket is the usual answer.
- **Retries** — exponential backoff **with jitter**. Without jitter, all failed clients retry in lockstep and you rebuild the thundering herd you were avoiding. Only retry idempotent operations, and only on retryable statuses.
- **Circuit breaker** — closed (traffic flows) → open (fail fast after a failure threshold, don't even try) → half-open (let one probe through; success closes it, failure re-opens). Retries make cascading failures *worse*; the breaker is what stops them.
- **Timeouts** — every network call gets one. A hung call holds a connection, and enough of them exhaust the pool. Timeouts bound a single call; a breaker bounds the *pattern*.
- **REST vs streaming** — for LLM responses, streaming (SSE) exists because time-to-first-token is the perceived latency, not total generation time.

---

## 12. Concurrency — know which lever, and why

```python
# I/O-bound (API calls, DB queries, file reads) -> threads or asyncio
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(fetch, urls))

# CPU-bound (parsing, math, embeddings on CPU) -> processes
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor() as ex:
    results = list(ex.map(crunch, chunks))
```

The sentence to have exactly right: **the GIL allows only one thread to execute Python bytecode at a time, but blocking I/O releases it.** That single fact explains both rows — threads help for I/O because the waiting thread isn't holding the lock; threads don't help for CPU because bytecode execution is precisely what's serialized. Processes get separate interpreters and separate GILs, at the cost of pickling data across the boundary.

---

## 13. The security minimums

Even outside an auth question, these come up:

- **Parameterized SQL, always.** `cur.execute("... WHERE id = ?", (uid,))` — never an f-string. This is the injection boundary.
- **`hmac.compare_digest`, never `==`,** for any secret comparison. String equality short-circuits and leaks the value by timing.
- **Slow hash + per-user salt** for passwords. PBKDF2/bcrypt/scrypt/Argon2, never plain SHA-256.
- **Verify before you parse.** Check the signature before reading any claim from a token.
- **Never log secrets.** Tokens, passwords, keys, and PII stay out of log lines — logs get shipped to systems with wider access than the database.

---

## What NOT to spend time on

For an AIE/MLE practical, deprioritize: dynamic programming, graph algorithms beyond BFS/DFS, balancing trees, bit manipulation tricks, and anything competitive-programming shaped. If an algorithm shows up at all it will be simple, and clean readable code will score better than a clever one-liner.

Spend the time instead on: **narrating while you type**, **clarifying before you code**, and the aggregation/sorting/validation patterns above — which is what these prompts are actually made of.

---

## The drill

Set a 25-minute timer and write, from scratch, no reference:

1. Group a list of transaction dicts by user and by day, summing amounts as `Decimal`. Sort users by total descending, then name ascending.
2. Write a `@dataclass` with a validated enumerated field and a list default.
3. Parse a JSON string that may be malformed and return a typed fallback on failure.
4. Score and rank documents against a query by length-normalized lexical overlap.
5. Sign a payload with HMAC-SHA256 and verify it in constant time.

If all five land inside 25 minutes, the environment isn't going to be what costs you the round.

---

## Where each pattern is exercised

| Pattern | Worked example |
|---|---|
| Aggregation, sorting, `Decimal`, anomaly detection | [transaction-aggregation.md](examples/transaction-aggregation.md) |
| Retrieval scoring, prompt construction, schema validation | [rag-pipeline-offline.md](examples/rag-pipeline-offline.md) |
| Exceptions, step gating, failure taxonomy | [workflow-orchestration.md](examples/workflow-orchestration.md) |
| SQL, parameterization, transactions, OLTP/OLAP | [sqlite-pipeline-scaling.md](examples/sqlite-pipeline-scaling.md) |
| HMAC, constant-time compare, status codes, scopes | [auth-api-endpoint.md](examples/auth-api-endpoint.md) |
| `functools.wraps`, backoff with jitter | [retry-decorator.md](examples/retry-decorator.md) |
