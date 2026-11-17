---
origin: curated
sources:
  - "Software Carpentry, Databases and SQL, episode 06 — https://swcarpentry.github.io/sql-novice-survey/ (CC-BY 4.0)"
  - "PGExercises, Aggregation — https://pgexercises.com/questions/aggregates/ (CC BY-SA 3.0)"
concepts: [sql-group-by, sql-having, sql-aggregate-functions, sql-conditional-aggregation]
cleaned: 2026-10-29
---
# 3 — Aggregation

> `GROUP BY` collapses many rows into one per group. Every column in the output must either be in the group key or be summarised by an aggregate.

---

## Aggregate functions

```sql
SELECT count(*), min(reading), max(reading), avg(reading), sum(reading)
FROM Survey WHERE quant = 'sal';
```

| Function | Notes |
|---|---|
| `count(*)` | Counts rows, `NULL`s included |
| `count(col)` / `count(DISTINCT col)` | Counts non-`NULL` values / distinct non-`NULL` values |
| `sum`, `avg`, `min`, `max` | Ignore `NULL`. `sum` of zero rows is `NULL`, not 0. Wrap it in `COALESCE(…, 0)` |
| `group_concat(col, ', ')` (SQLite) / `string_agg(col, ', ')` (Postgres, DuckDB) | Joins the values in a group into one string |

## `GROUP BY`

```sql
SELECT person, quant, count(*) AS n, round(avg(reading), 2) AS mean
FROM Survey
GROUP BY person, quant
ORDER BY person, quant;
```

**The bare-column rule.** `SELECT person, reading FROM Survey GROUP BY person` is an error in Postgres and DuckDB. SQLite accepts it and returns an arbitrary `reading` from each group, which is a silent bug. If a column isn't in `GROUP BY`, aggregate it.

## `HAVING` filters groups; `WHERE` filters rows

```sql
-- Facilities with more than 1,000 slots booked in total
SELECT facid, sum(slots) AS total_slots
FROM bookings
GROUP BY facid
HAVING sum(slots) > 1000
ORDER BY facid;
```

`WHERE` runs before grouping, so it can't see aggregates. `HAVING` runs after. Push every filter you can into `WHERE`: fewer rows reach the grouping step.

## Conditional aggregation (pivoting)

Putting `CASE` inside an aggregate turns rows into columns. It is the portable way to pivot:

```sql
SELECT facid,
       sum(CASE WHEN strftime('%m', starttime) = '07' THEN slots ELSE 0 END) AS jul,
       sum(CASE WHEN strftime('%m', starttime) = '08' THEN slots ELSE 0 END) AS aug,
       sum(CASE WHEN strftime('%m', starttime) = '09' THEN slots ELSE 0 END) AS sep
FROM bookings
WHERE starttime >= '2012-07-01' AND starttime < '2012-10-01'
GROUP BY facid;
```

Postgres and DuckDB also support `count(*) FILTER (WHERE …)`, which reads more cleanly. DuckDB has a `PIVOT` statement as well.

## A rate per group per month

A rate is two aggregates over the same rows, so compute both in one `GROUP BY`. The average of a 0/1 flag is the rate:

```sql
-- Share of each facility's bookings made by guests (memid 0), by month
SELECT facid, strftime('%Y-%m', starttime) AS month,
       count(*) AS bookings,
       round(avg(CASE WHEN memid = 0 THEN 1.0 ELSE 0 END), 3) AS guest_share
FROM bookings
WHERE facid IN (0, 4)
GROUP BY facid, month
ORDER BY facid, month;
```

```text
0|2012-07|88|0.261
0|2012-08|146|0.24
0|2012-09|174|0.241
4|2012-07|123|0.374
4|2012-08|224|0.317
4|2012-09|282|0.323
```

Write `1.0` and not `1`: dividing two integers truncates in SQLite and Postgres. When the numerator and denominator live in different tables, as clicks and impressions do for a click-through rate, aggregate each to one row per group and month first and join after. Joining the raw rows multiplies them and inflates both counts ([note 04](04-joins.md)).

## Rollups

```sql
-- Postgres / DuckDB: subtotals per facility and month, plus a grand total
SELECT facid, date_trunc('month', starttime) AS month, sum(slots)
FROM bookings GROUP BY ROLLUP (facid, month) ORDER BY facid, month;
```

SQLite has no `ROLLUP`. Emulate it with `UNION ALL` of the detailed query and a query grouped at the coarser level.

## Interview checklist

| Question | Answer |
|---|---|
| `WHERE` or `HAVING`? | `WHERE` filters rows before grouping and cannot see aggregates. `HAVING` filters groups after it. |
| How do you compute a rate per group per month? | Group by the group and the month, and take `avg` of a 0/1 `CASE` flag. Write 1.0 to avoid integer division, and aggregate before joining tables. |

---

## Exercises

[`practice/exercises/03-aggregation.sql`](../practice/exercises/03-aggregation.sql)
