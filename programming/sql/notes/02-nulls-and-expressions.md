---
origin: curated
sources:
  - "Software Carpentry, Databases and SQL, episodes 04–05 — https://swcarpentry.github.io/sql-novice-survey/ (CC-BY 4.0)"
  - "SQLite date and time functions — https://www.sqlite.org/lang_datefunc.html"
concepts: [sql-null, sql-three-valued-logic, sql-coalesce, sql-dates, sql-strings]
cleaned: 2026-10-29
---
# 2 — Missing Data, Dates and Strings

> `NULL` means "unknown", not "zero" or "empty". Any comparison with an unknown is itself unknown.

---

## Three-valued logic

`NULL` propagates. Any arithmetic or comparison involving `NULL` gives `NULL`, and `WHERE` keeps only rows where the condition is **true**. Unknown counts as not true:

| Expression | Result |
|---|---|
| `NULL = NULL` | `NULL` (not true!) |
| `NULL <> 1` | `NULL` |
| `1 + NULL` | `NULL` |
| `NULL AND false` | `false` |
| `NULL OR true` | `true` |

```sql
SELECT * FROM Visited WHERE dated = NULL;      -- always empty: wrong
SELECT * FROM Visited WHERE dated IS NULL;     -- correct
SELECT * FROM Visited WHERE dated IS NOT NULL;
```

**The trap that catches everyone.** "Everything not measured by Lake" isn't `WHERE person != 'lake'`, because rows where `person` is `NULL` drop out too. Say what you mean:

```sql
SELECT * FROM Survey WHERE person != 'lake' OR person IS NULL;
```

The same applies to `NOT IN`. If the subquery returns even one `NULL`, `x NOT IN (…)` is never true, so the query returns nothing. Use `NOT EXISTS` instead ([note 05](05-subqueries-and-ctes.md#exists-vs-in)).

## Replacing `NULL`

```sql
SELECT id, COALESCE(dated, 'unknown') AS dated FROM Visited;         -- first non-NULL argument
SELECT memid, NULLIF(recommendedby, 0) FROM members;                 -- turn a sentinel into NULL
```

`COALESCE` is standard SQL and works everywhere. `IFNULL` (SQLite and MySQL) and `ISNULL` (SQL Server) are dialect-specific versions with two arguments.

## Aggregates ignore `NULL`

`COUNT(*)` counts rows. `COUNT(col)` counts non-`NULL` values. `AVG(col)` divides by the non-`NULL` count. That is usually right, but be deliberate about it: if a missing reading really means zero, write `AVG(COALESCE(reading, 0))`.

---

## Dates and times

Each engine stores dates differently. The ideas are the same everywhere:

| Task | SQLite | Postgres / DuckDB |
|---|---|---|
| Truncate to a month | `strftime('%Y-%m', starttime)` | `date_trunc('month', starttime)` |
| Extract a part | `CAST(strftime('%H', starttime) AS INTEGER)` | `extract(hour FROM starttime)` |
| Add an interval | `datetime(starttime, '+30 minutes')` | `starttime + interval '30 minutes'` |
| Difference in days | `julianday(b) - julianday(a)` | `b::date - a::date` |
| Current time | `datetime('now')` | `now()` |

```sql
-- Bookings in September 2012 (half-open range: index-friendly and exact)
SELECT * FROM bookings
WHERE starttime >= '2012-09-01' AND starttime < '2012-10-01';
```

**Prefer half-open ranges** (`>= start AND < end`) to `BETWEEN` for timestamps. `BETWEEN '2012-09-01' AND '2012-09-30'` silently drops every booking after midnight on the 30th. Wrapping the column in a function (`WHERE strftime('%Y-%m', starttime) = '2012-09'`) also stops the database from using an index on it ([note 08](08-indexes-and-query-plans.md)).

## Strings

```sql
SELECT upper(surname), length(surname), substr(telephone, 2, 3) FROM members;
SELECT replace(telephone, '-', '') FROM members;
SELECT trim('  padded  ');
SELECT * FROM members WHERE surname LIKE 'S%';           -- case-insensitive for ASCII in SQLite
SELECT * FROM members WHERE lower(surname) = 'smith';
```

Postgres `LIKE` is case-sensitive, and it uses `ILIKE` for case-insensitive matching. Both Postgres and DuckDB support regular expressions (`~`, `regexp_matches`). Plain SQLite does not.

## Types and casting

```sql
SELECT CAST('42' AS INTEGER) + 1;
SELECT 7 / 2, 7 / 2.0, CAST(7 AS REAL) / 2;               -- 3, 3.5, 3.5: integer division!
SELECT round(avg(slots), 2) FROM bookings;
```

Integer division catches people in every dialect. Turn one side into a decimal before you compute a ratio.

---

## Exercises

[`practice/exercises/02-nulls-and-expressions.sql`](../practice/exercises/02-nulls-and-expressions.sql)
