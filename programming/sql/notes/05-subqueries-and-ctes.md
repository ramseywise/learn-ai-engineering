---
origin: curated
sources:
  - "PGExercises, Joins and Subqueries; Recursive Queries — https://pgexercises.com/questions/ (CC BY-SA 3.0)"
  - "SQLite, The WITH Clause — https://www.sqlite.org/lang_with.html"
concepts: [sql-subqueries, sql-correlated-subquery, sql-exists, sql-cte, sql-recursive-cte]
cleaned: 2026-10-29
---
# 5 — Subqueries and CTEs

> A query is a table. Anywhere SQL expects a table or a value, you can put another query. CTEs give those inner queries names.

---

## Scalar subqueries

A subquery that returns one row and one column can go anywhere a value can:

```sql
-- Bookings longer than average
SELECT bookid, slots FROM bookings
WHERE slots > (SELECT avg(slots) FROM bookings);
```

## Correlated subqueries

A correlated subquery refers to the outer row, so in principle it runs once per outer row:

```sql
-- Each member's first booking
SELECT m.surname, m.firstname,
       (SELECT min(b.starttime) FROM bookings b WHERE b.memid = m.memid) AS first_booking
FROM members m;
```

Planners often rewrite these as joins. When they can't, a correlated subquery over a large table is slow. A join to a pre-aggregated subquery, or a window function ([note 06](06-window-functions.md)), usually does better.

## Subqueries in `FROM` (derived tables)

```sql
SELECT facid, total
FROM (SELECT facid, sum(slots) AS total FROM bookings GROUP BY facid) t
WHERE total > 1000;
```

## `EXISTS` vs `IN`

```sql
-- Members who have booked a tennis court
SELECT m.surname FROM members m
WHERE EXISTS (
  SELECT 1 FROM bookings b JOIN facilities f ON f.facid = b.facid
  WHERE b.memid = m.memid AND f.name LIKE 'Tennis%'
);
```

- `EXISTS` stops at the first match and ignores the selected columns (`SELECT 1` is the convention).
- `IN (subquery)` is fine for positive matches.
- **`NOT IN (subquery)` is broken if the subquery can return `NULL`.** It returns no rows at all ([note 02](02-nulls-and-expressions.md)). Use `NOT EXISTS` for anti-joins.

---

## Common table expressions

`WITH` names a subquery and puts it before the main query, so a multi-step query reads top to bottom:

```sql
WITH member_slots AS (
  SELECT memid, sum(slots) AS slots
  FROM bookings
  GROUP BY memid
),
ranked AS (
  SELECT memid, slots, slots * 1.0 / (SELECT sum(slots) FROM member_slots) AS share
  FROM member_slots
)
SELECT m.surname, m.firstname, r.slots, round(r.share * 100, 1) AS pct
FROM ranked r JOIN members m USING (memid)
WHERE m.memid > 0           -- exclude the GUEST account
ORDER BY r.slots DESC
LIMIT 5;
```

**Why use CTEs.** You can test each step on its own (`SELECT * FROM member_slots`), name intermediate results, and reuse one CTE several times. Postgres 12+, DuckDB and SQLite inline CTEs into the main query unless you ask for `MATERIALIZED`, so in general they cost nothing.

## Recursive CTEs

A recursive CTE has an anchor query, then `UNION ALL`, then a step that refers to the CTE itself. It repeats until the step returns no rows. Use it for hierarchies, graphs and number series:

```sql
-- The chain of recommenders above member 27
WITH RECURSIVE chain(memid, recommendedby, depth) AS (
  SELECT memid, recommendedby, 0 FROM members WHERE memid = 27
  UNION ALL
  SELECT m.memid, m.recommendedby, c.depth + 1
  FROM members m JOIN chain c ON m.memid = c.recommendedby
)
SELECT c.depth, m.firstname, m.surname
FROM chain c JOIN members m USING (memid)
WHERE c.depth > 0
ORDER BY c.depth;
```

```sql
-- Generate a date series, then LEFT JOIN the facts onto it so empty days still show
WITH RECURSIVE days(d) AS (
  SELECT '2012-09-01'
  UNION ALL
  SELECT date(d, '+1 day') FROM days WHERE d < '2012-09-30'
)
SELECT d, count(b.bookid) AS bookings
FROM days LEFT JOIN bookings b ON date(b.starttime) = d
GROUP BY d;
```

Always give recursion a stopping condition. A cycle in the data (A recommends B, B recommends A) loops forever without a depth limit or a visited-path check.

---

## Exercises

[`practice/exercises/05-subqueries-and-ctes.sql`](../practice/exercises/05-subqueries-and-ctes.sql)
