---
origin: curated
sources:
  - "Software Carpentry, Databases and SQL, episode 07 — https://swcarpentry.github.io/sql-novice-survey/ (CC-BY 4.0)"
  - "PGExercises, Joins and Subqueries — https://pgexercises.com/questions/joins/ (CC BY-SA 3.0)"
concepts: [sql-joins, sql-inner-join, sql-left-join, sql-self-join, sql-anti-join, sql-set-operations]
cleaned: 2026-10-29
---
# 4 — Joins

> A join pairs rows from two tables that satisfy a condition. The kind of join decides what happens to rows that don't find a partner.

---

## Inner join

```sql
SELECT Site.lat, Site.long, Visited.dated
FROM Site
JOIN Visited ON Site.name = Visited.site;
```

Conceptually, the database builds every pair of rows (the cross product) and keeps the pairs where the `ON` condition is true. Rows with no match on either side disappear.

**Watch the row count.** If the join key isn't unique on one side, rows multiply. Joining `bookings` (4,044 rows) to `members` on `memid` returns 4,044 rows because `memid` is unique in `members`. Joining it to a table that has several rows per `memid` would return more. Duplicated rows after a join usually mean the key isn't the one you assumed.

## Multi-table joins and aliases

```sql
SELECT s.name, v.dated, sv.quant, sv.reading
FROM Site s
JOIN Visited v  ON s.name = v.site
JOIN Survey  sv ON v.id   = sv.taken
WHERE v.dated IS NOT NULL;
```

## Outer joins

| Join | Keeps |
|---|---|
| `LEFT JOIN` | Every row from the left table. Right-hand columns are `NULL` where there's no match |
| `RIGHT JOIN` | The mirror image. Rewrite it as a `LEFT JOIN` for readability |
| `FULL OUTER JOIN` | Unmatched rows from both sides (SQLite 3.39+, Postgres, DuckDB) |

```sql
-- Every member, plus who recommended them (if anyone)
SELECT m.firstname, m.surname, r.firstname AS rec_first, r.surname AS rec_last
FROM members m
LEFT JOIN members r ON r.memid = m.recommendedby
ORDER BY m.surname, m.firstname;
```

This is also a **self-join**: one table, two aliases, with a foreign key pointing back into the same table.

**The `LEFT JOIN` + `WHERE` trap.** A filter on the right-hand table in `WHERE` throws away the `NULL` rows that the `LEFT JOIN` just kept, which turns it back into an inner join. Put conditions on the right-hand table in the `ON` clause instead:

```sql
-- Every facility, with its September bookings (0 if none)
SELECT f.name, count(b.bookid) AS n
FROM facilities f
LEFT JOIN bookings b
  ON b.facid = f.facid
 AND b.starttime >= '2012-09-01' AND b.starttime < '2012-10-01'
GROUP BY f.name;
```

Note `count(b.bookid)`, not `count(*)`: a facility with no bookings still has one row (with `NULL`s), so `count(*)` would return 1.

## Anti-joins: "rows with no match"

```sql
-- Members who have never booked anything
SELECT m.memid, m.surname
FROM members m
LEFT JOIN bookings b ON b.memid = m.memid
WHERE b.memid IS NULL;
```

`NOT EXISTS` does the same job ([note 05](05-subqueries-and-ctes.md)). Use whichever reads better. Modern planners usually run them the same way.

## Cross joins

`CROSS JOIN` returns every pair. It is occasionally useful for generating combinations, such as every facility × every month, which you then `LEFT JOIN` the facts onto so that empty cells show up as zeros.

## Set operations

```sql
SELECT surname FROM members
UNION              -- deduplicates; UNION ALL keeps duplicates and is faster
SELECT name FROM facilities;
```

`INTERSECT` and `EXCEPT` work the same way. Both sides must have the same number of columns with compatible types.

---

## Exercises

[`practice/exercises/04-joins.sql`](../practice/exercises/04-joins.sql)
