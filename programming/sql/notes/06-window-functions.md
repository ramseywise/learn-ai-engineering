---
origin: curated
sources:
  - "PGExercises, Aggregation (window-function questions) — https://pgexercises.com/questions/aggregates/ (CC BY-SA 3.0)"
  - "SQLite, Window Functions — https://www.sqlite.org/windowfunctions.html"
concepts: [sql-window-functions, sql-ranking, sql-running-total, sql-lag-lead, sql-moving-average, sql-top-n-per-group]
cleaned: 2026-10-29
---
# 6 — Window Functions

> An aggregate collapses a group into one row. A window function computes over a group but keeps every row.

---

## Anatomy

```sql
func(args) OVER (
  PARTITION BY …     -- restart the calculation for each group (optional)
  ORDER BY …         -- order within the partition (required for ranking, running totals, lag/lead)
  ROWS BETWEEN …     -- the frame: which rows around the current one to include (optional)
)
```

```sql
-- Each booking, alongside its member's total slots
SELECT bookid, memid, slots,
       sum(slots) OVER (PARTITION BY memid) AS member_total
FROM bookings;
```

Window functions are evaluated *after* `WHERE`, `GROUP BY` and `HAVING`, so you can't filter on them in the same query. Wrap the query in a CTE and filter outside it.

## Ranking

| Function | Ties | Example ranks for scores 10, 10, 8 |
|---|---|---|
| `row_number()` | Arbitrary tie-break, always unique | 1, 2, 3 |
| `rank()` | Ties share a rank, then gaps | 1, 1, 3 |
| `dense_rank()` | Ties share a rank, no gaps | 1, 1, 2 |
| `ntile(n)` | Splits into *n* buckets of roughly equal size | — |

**Top-N per group** is the most common window question in interviews:

```sql
-- Each member's 3 longest bookings
WITH ranked AS (
  SELECT memid, bookid, slots,
         row_number() OVER (PARTITION BY memid ORDER BY slots DESC, bookid) AS rn
  FROM bookings
)
SELECT * FROM ranked WHERE rn <= 3;
```

Add a unique column (`bookid`) to the `ORDER BY` so that the result is deterministic.

## Running totals and moving averages

```sql
SELECT date(starttime) AS day, sum(slots) AS slots,
       sum(sum(slots)) OVER (ORDER BY date(starttime)) AS running_total,
       avg(sum(slots)) OVER (ORDER BY date(starttime)
                             ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7d
FROM bookings
GROUP BY date(starttime);
```

- `sum(sum(slots)) OVER …` aggregates first (per day), then windows over the daily totals. This is legal because window functions run after `GROUP BY`.
- **The default frame catches people out.** With an `ORDER BY` and no frame clause, the frame is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, so peers (rows with equal sort keys) are included together. That is correct for running totals over unique days. With duplicate sort keys, say `ROWS` explicitly.
- `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` means "this row and the six before it". It only covers seven days if every day has a row. Fill the gaps first with a date series ([note 05](05-subqueries-and-ctes.md#recursive-ctes)).

## `lag` / `lead`: comparing with neighbouring rows

```sql
-- Days between a member's consecutive bookings
SELECT memid, starttime,
       julianday(starttime) - julianday(lag(starttime) OVER (PARTITION BY memid ORDER BY starttime))
         AS days_since_previous
FROM bookings;
```

`lag(x, n, default)` looks *n* rows back. `lead` looks forward. `first_value` and `last_value` read the edges of the frame (for `last_value`, set the frame to `UNBOUNDED FOLLOWING`).

## Share of total

```sql
SELECT facid, sum(slots) AS slots,
       round(100.0 * sum(slots) / sum(sum(slots)) OVER (), 1) AS pct_of_all
FROM bookings GROUP BY facid;
```

`OVER ()` is a window over the entire result.

## Analytics patterns built from windows

| Pattern | Recipe |
|---|---|
| Deduplicate (keep the latest per key) | `row_number() OVER (PARTITION BY key ORDER BY updated_at DESC) = 1` |
| Sessionise | `lag` to find gaps longer than a threshold, then a running `sum` of "new session" flags gives each session an ID |
| Gaps and islands | Consecutive runs share the same `date - row_number()` value. Group by it |
| Retention cohorts | `min(date) OVER (PARTITION BY user)` gives each user's cohort. Group by cohort × period |

---

## Exercises

[`practice/exercises/06-window-functions.sql`](../practice/exercises/06-window-functions.sql)
