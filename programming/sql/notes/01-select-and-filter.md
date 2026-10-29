---
origin: curated
sources:
  - "Software Carpentry, Databases and SQL, episodes 01–03 — https://swcarpentry.github.io/sql-novice-survey/ (CC-BY 4.0)"
  - "PGExercises, Simple SQL Queries — https://pgexercises.com/questions/basic/ (CC BY-SA 3.0)"
concepts: [sql-select, sql-where, sql-order-by, sql-distinct, sql-limit]
cleaned: 2026-10-29
---
# 1 — Selecting, Sorting and Filtering

> A query describes the rows you want. The database decides how to fetch them.

---

## The two practice databases

| Database | Tables | What it models |
|---|---|---|
| `survey.db` | `Person`, `Site`, `Visited`, `Survey` | A 1920s–30s Antarctic expedition: who measured what (`rad`, `sal`, `temp`) where, and when. Small enough to check every answer by eye |
| `clubdata.db` | `members`, `facilities`, `bookings` | A country club: members, the courts and rooms they book, and 4,000 bookings over 2012. Big enough for aggregation and window functions to matter |

Build them with `bash practice/setup.sh`, then open one with `sqlite3 -header -column practice/data/survey.db`.

---

## `SELECT … FROM`

```sql
SELECT family, personal FROM Person;
SELECT * FROM Person;                 -- every column, in table order
```

- SQL keywords are case-insensitive. Table and column names are case-insensitive in SQLite and folded to lowercase in Postgres unless quoted. Pick one style and stick to it.
- **Rows in a table have no order.** Without `ORDER BY`, the order you see is an accident of storage and can change between runs.
- `SELECT *` is fine at the prompt. In code, name the columns, so that adding a column to the table doesn't break the consumer.

## Sorting and removing duplicates

```sql
SELECT DISTINCT quant FROM Survey;                     -- one row per distinct value
SELECT DISTINCT taken, quant FROM Survey;              -- distinct over the *pair*
SELECT * FROM Person ORDER BY family DESC;
SELECT taken, person, quant FROM Survey ORDER BY taken ASC, person DESC;
```

`ORDER BY` can name a column that isn't in the `SELECT` list, and it can use a column alias or an expression.

## Filtering with `WHERE`

```sql
SELECT * FROM Visited WHERE site = 'DR-1' AND dated < '1930-01-01';
SELECT * FROM Survey  WHERE person = 'lake' OR person = 'roe';
SELECT * FROM Survey  WHERE person IN ('lake', 'roe');                 -- same thing
SELECT * FROM Survey  WHERE quant = 'sal' AND (person = 'lake' OR person = 'roe');
SELECT * FROM Visited WHERE site LIKE 'DR%';                            -- % = any run, _ = one char
SELECT * FROM Survey  WHERE reading BETWEEN 0 AND 1;                    -- inclusive at both ends
```

- `AND` binds tighter than `OR`. **Always parenthesise mixed `AND`/`OR`.** Leaving out the brackets in the third query returns every reading by `roe`, salinity or not.
- Dates in ISO-8601 text (`YYYY-MM-DD`) compare correctly as strings. That is why SQLite gets away with storing them as `TEXT`.
- `WHERE` runs **before** `SELECT`, so it can't see column aliases defined in the `SELECT` list (see [order of evaluation](#order-of-evaluation)).

## Calculated columns

```sql
SELECT taken, reading * 100 AS pct FROM Survey WHERE quant = 'sal';
SELECT personal || ' ' || family AS full_name FROM Person;               -- string concat
SELECT name, membercost, CASE WHEN membercost > 0 THEN 'paid' ELSE 'free' END AS kind
FROM facilities;
```

`CASE WHEN … THEN … ELSE … END` is SQL's `if`. It can go anywhere an expression can: `SELECT`, `WHERE`, `ORDER BY`, or inside an aggregate.

## Limiting

```sql
SELECT * FROM bookings ORDER BY starttime DESC LIMIT 10;            -- SQLite, Postgres, DuckDB
SELECT * FROM bookings ORDER BY starttime DESC LIMIT 10 OFFSET 20;  -- page 3
```

`LIMIT` without `ORDER BY` returns *some* ten rows, not the first ten. Large `OFFSET`s get slow because the database still reads and throws away the skipped rows. Production APIs page by key instead (`WHERE starttime < :last_seen ORDER BY starttime DESC LIMIT 10`).

---

## Order of evaluation

You write a query in one order and the database evaluates it in another. Most "why can't I use that alias here" errors come from this:

| Written | Evaluated |
|---|---|
| `SELECT` | 1. `FROM` / `JOIN` |
| `FROM` | 2. `WHERE` |
| `WHERE` | 3. `GROUP BY` |
| `GROUP BY` | 4. `HAVING` |
| `HAVING` | 5. `SELECT` (aliases are created here, along with window functions) |
| `ORDER BY` | 6. `DISTINCT` |
| `LIMIT` | 7. `ORDER BY` (can use aliases) → 8. `LIMIT` |

---

## Exercises

[`practice/exercises/01-select-and-filter.sql`](../practice/exercises/01-select-and-filter.sql). Solutions are in [`practice/solutions/`](../practice/solutions/).
