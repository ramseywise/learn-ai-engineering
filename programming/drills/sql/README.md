# SQL

SQL's teaching lives in [`programming/sql/`](../../../programming/sql/README.md). For cold reps on
`SELECT`, joins and aggregation, use the HackerRank SQL track; solutions stay local and are not in
this repo.

| Folder | What | Count |
|---|---|---|
| [`window-functions/`](window-functions/) | Schema drills: [top orders per user + running total](window-functions/top-orders-per-user.md) | 1 |

## Gaps — what interviews ask that isn't here

- **Window functions**: started (ranking, running totals). Still to add: `LAG`/`LEAD` gaps, moving averages, `NTILE`.
- **CTEs and recursion**: multi-step queries, `WITH RECURSIVE` hierarchies.
- **Analytics patterns**: retention/cohorts, funnels, sessionization, deduplication.
- **Query performance**: reading `EXPLAIN`, index choice.

Build these as schema drills (`window-functions/`, `ctes/`, `analytics/`) per
[`../README.md`](../README.md), each with a small seed schema so the answer can be run in
SQLite or DuckDB.
