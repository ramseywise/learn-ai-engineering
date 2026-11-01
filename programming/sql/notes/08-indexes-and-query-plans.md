---
origin: curated
sources:
  - "Markus Winand, Use The Index, Luke — https://use-the-index-luke.com/ (read online; not copied)"
  - "SQLite, EXPLAIN QUERY PLAN — https://www.sqlite.org/eqp.html"
concepts: [sql-indexes, sql-explain, sql-sargable, sql-query-performance]
cleaned: 2026-11-01
---
# 8 — Indexes and Query Plans

> An index is a sorted copy of some columns that points back to the rows. It turns "read everything" into "jump to the right place", and every write pays to keep it up to date.

---

## What an index is

Most databases use a **B-tree**: a balanced, sorted tree of keys. A lookup costs O(log n) instead of a full scan's O(n), and a range (`BETWEEN`, `>=`/`<`, `LIKE 'abc%'`) is a lookup followed by a walk along the leaves.

```sql
CREATE INDEX bookings_memid_starttime ON bookings (memid, starttime);
```

## Reading a plan

```sql
EXPLAIN QUERY PLAN
SELECT * FROM bookings WHERE memid = 5 AND starttime >= '2012-09-01';
-- SEARCH bookings USING INDEX bookings.memid_starttime (memid=? AND starttime>?)
```

| SQLite says | Meaning |
|---|---|
| `SCAN table` | Full table scan: every row is read |
| `SEARCH table USING INDEX idx (col=?)` | An index lookup |
| `USING COVERING INDEX` | The index contains every needed column, so the table itself is never read |
| `USE TEMP B-TREE FOR ORDER BY` | An extra sort step that no index could provide |

`clubdata.db` ships with this index (under the name `bookings.memid_starttime`, as `.schema bookings` shows), which is why the plan above needs no `CREATE`. A plan is a recipe, and it reads as a pipeline. Here is one member's bookings per facility, since September:

```sql
EXPLAIN QUERY PLAN
SELECT f.name, count(*) AS n
FROM bookings b JOIN facilities f ON f.facid = b.facid
WHERE b.memid = 5 AND b.starttime >= '2012-09-01'
GROUP BY f.name
ORDER BY n DESC;
-- |--SEARCH b USING INDEX bookings.memid_starttime (memid=? AND starttime>?)
-- |--SEARCH f USING INTEGER PRIMARY KEY (rowid=?)
-- |--USE TEMP B-TREE FOR GROUP BY
-- `--USE TEMP B-TREE FOR ORDER BY
```

```text
  bookings                                     outer loop: index range, not a scan
  SEARCH b USING INDEX (memid=? AND starttime>?)
        │  one row per matching booking
        ▼
  facilities                                   inner loop: one lookup per row
  SEARCH f USING INTEGER PRIMARY KEY
        │  (booking, facility name)
        ▼
  TEMP B-TREE FOR GROUP BY                     no index is sorted by f.name, so build one
        │  one row per name, with count(*)
        ▼
  TEMP B-TREE FOR ORDER BY                     n exists only after grouping, so sort again
        │
        ▼
  result: 7 rows
```

The first line of the plan is the outer table of a nested-loop join, and each line after it runs for the rows above it. Two questions find most problems: is the first step a `SEARCH` or a `SCAN`, and how many rows does it feed the rest? A temp b-tree is not a bug. Sorting 50 rows is cheap, and sorting 50 million is not. A query filtered only by `date(starttime) = '2012-09-14'` plans as `SCAN bookings`, because the function hides the column from the index ([below](#sargable-predicates)).

Postgres and DuckDB use `EXPLAIN ANALYZE`, which actually runs the query and reports real row counts and timings per node. Compare *estimated* with *actual* rows. A big gap means stale statistics (`ANALYZE`) or a predicate the planner can't estimate.

## Composite indexes: column order matters

An index on `(memid, starttime)` is sorted by `memid`, then by `starttime` within each `memid`, like a phone book sorted by surname then first name.

| Query | Can it use `(memid, starttime)`? |
|---|---|
| `WHERE memid = 5` | Yes, using the leftmost prefix |
| `WHERE memid = 5 AND starttime >= …` | Yes: equality first, then a range |
| `WHERE starttime >= …` | Not efficiently, because the leading column is missing |
| `WHERE memid > 5 AND starttime = …` | Only for `memid`. After a range column, later columns can't narrow the search |

**Rule of thumb:** put equality columns first and the range or sort column last.

## Sargable predicates

A predicate is *sargable* (Search ARGument ABLE) if the index can satisfy it. Wrapping the indexed column in a function or expression usually stops the index from being used:

| Not sargable | Sargable rewrite |
|---|---|
| `WHERE date(starttime) = '2012-09-14'` | `WHERE starttime >= '2012-09-14' AND starttime < '2012-09-15'` |
| `WHERE slots * 2 > 6` | `WHERE slots > 3` |
| `WHERE lower(surname) = 'smith'` | An expression index `ON members (lower(surname))`, or store the value normalised |
| `WHERE surname LIKE '%mith'` | No B-tree helps a leading wildcard. Use full-text search or a trigram index |

## When indexes don't help

- **Low selectivity.** If the predicate matches a large share of the table, a scan is cheaper than thousands of random lookups, and the planner rightly ignores the index.
- **Small tables.** A 9-row `facilities` table always gets scanned.
- **Write cost.** Every `INSERT`, `UPDATE` and `DELETE` also updates every index. Index for the queries you actually run, not for every column.

## Columnar engines

DuckDB, BigQuery, Snowflake and ClickHouse store data by column and scan compressed column chunks. They rely on min/max statistics per block (zone maps) instead of B-trees. There, performance comes from reading fewer columns (avoid `SELECT *`), partitioning or clustering by the common filter column, and pre-aggregation, rather than from adding indexes.

---

## Exercises

[`practice/exercises/08-indexes-and-query-plans.sql`](../practice/exercises/08-indexes-and-query-plans.sql)
