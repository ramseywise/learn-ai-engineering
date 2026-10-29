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

## Rollups

```sql
-- Postgres / DuckDB: subtotals per facility and month, plus a grand total
SELECT facid, date_trunc('month', starttime) AS month, sum(slots)
FROM bookings GROUP BY ROLLUP (facid, month) ORDER BY facid, month;
```

SQLite has no `ROLLUP`. Emulate it with `UNION ALL` of the detailed query and a query grouped at the coarser level.

---

## Exercises

[`practice/exercises/03-aggregation.sql`](../practice/exercises/03-aggregation.sql)
