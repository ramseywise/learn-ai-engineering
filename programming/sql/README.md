# SQL

> From `SELECT` to query plans, in nine modules and a capstone. Every module is a short note plus
> exercises you can run offline against SQLite.
> Study deck: [sql.pptx](slides/sql.pptx), which librarian turns into flashcards (source: [deck.yaml](slides/deck.yaml)).
> Jump to: [Syllabus](#syllabus) · [Layout](#layout) · [Setup](#setup) · [The databases](#the-databases) · [Rules of thumb](#rules-of-thumb) · [Sources](#sources)

---

## Syllabus

| # | Note | You can… | Exercises |
|---|---|---|---|
| 01 | [Selecting, sorting and filtering](notes/01-select-and-filter.md) | Write `SELECT … WHERE … ORDER BY`, `CASE`, paging | [sql](practice/exercises/01-select-and-filter.sql) |
| 02 | [Missing data, dates and strings](notes/02-nulls-and-expressions.md) | Reason with three-valued logic, use half-open date ranges | [sql](practice/exercises/02-nulls-and-expressions.sql) |
| 03 | [Aggregation](notes/03-aggregation.md) | Use `GROUP BY` / `HAVING` and pivot with conditional aggregation | [sql](practice/exercises/03-aggregation.sql) |
| 04 | [Joins](notes/04-joins.md) | Choose inner, left, self and anti-joins; avoid the `LEFT JOIN … WHERE` trap | [sql](practice/exercises/04-joins.sql) |
| 05 | [Subqueries and CTEs](notes/05-subqueries-and-ctes.md) | Use correlated subqueries, `EXISTS`, recursive CTEs, date series | [sql](practice/exercises/05-subqueries-and-ctes.sql) |
| 06 | [Window functions](notes/06-window-functions.md) | Do top-N per group, running totals, `lag`/`lead`, dedup | [sql](practice/exercises/06-window-functions.sql) |
| 07 | [Designing tables and changing data](notes/07-modeling-and-ddl.md) | Write DDL with constraints, upserts, transactions, views | [sql](practice/exercises/07-modeling-and-ddl.sql) |
| 08 | [Indexes and query plans](notes/08-indexes-and-query-plans.md) | Read `EXPLAIN QUERY PLAN`, order composite indexes, write sargable predicates | [sql](practice/exercises/08-indexes-and-query-plans.sql) |
| 09 | [SQL from Python](notes/09-sql-from-python.md) | Use `sqlite3`, parameters, DuckDB, pandas | [py](practice/exercises/09_sql_from_python.py) |
| 10 | [Capstone: the SQL Murder Mystery](notes/10-capstone-murder-mystery.md) | Solve an open-ended investigation using everything above | — |

Worked answers are in [`practice/solutions/`](practice/solutions/). Try each exercise before you open them.

---

## Layout

```
sql/
├── README.md
├── notes/                        01–10
├── slides/                       deck.yaml and the built study deck; `make slides PILLAR=programming/sql`
└── practice/
    ├── setup.sh                  builds data/clubdata.db from clubdata.sql; downloads sql-murder-mystery.db
    ├── check.sh                  runs every solution (or exercise) file; calls setup.sh if clubdata.db is missing
    ├── exercises/                01–08 .sql, 09 .py
    ├── solutions/                same names, worked
    └── data/                     survey.db and clubdata.sql committed; clubdata.db and sql-murder-mystery.db gitignored
```

---

## Setup

```bash
cd programming/sql/practice
bash setup.sh                                      # builds clubdata.db, downloads the murder-mystery db
sqlite3 -header -column data/survey.db             # explore interactively
sqlite3 -header -column data/survey.db < exercises/01-select-and-filter.sql
bash check.sh                                      # runs every solution; `bash check.sh exercises` for yours
```

Files that switch databases do so with `.open data/clubdata.db`, so run them from `practice/`.
Module 07 runs against `:memory:` and loads a fresh copy of the club data, so nothing you change persists.

---

## The databases

| Database | Tables | Used in | Origin |
|---|---|---|---|
| `survey.db` (committed) | `Person`, `Site`, `Visited`, `Survey`: 1920s–30s Antarctic expedition readings, small enough to check by eye, with real `NULL`s | 01–04 | Software Carpentry |
| `clubdata.db` (built from `clubdata.sql`) | `members`, `facilities`, `bookings` (4,044 rows): a country club's booking system, with a self-referencing `recommendedby` | 01–09 | PGExercises, converted from Postgres to SQLite |
| `sql-murder-mystery.db` (downloaded) | Crime-scene reports, people, licences, gym check-ins, interviews | 10 | Knight Lab |

The notes point out where Postgres or DuckDB differ from SQLite, mostly for dates and `EXPLAIN`.

---

## Rules of thumb

- Write the query in evaluation order (`FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY`), not reading order.
- `NULL` is "unknown", not a value. `= NULL` is never true, and `NOT IN` with a `NULL` in the list returns nothing.
- Date ranges are half-open: `>= start AND < next_start`. That is correct for timestamps and keeps the index usable.
- A filter on the right table of a `LEFT JOIN` belongs in `ON`, not `WHERE`.
- Top-N per group is `row_number() OVER (PARTITION BY … ORDER BY …, unique_col)` in a CTE, filtered outside.
- Run `SELECT count(*)` with the same `WHERE` before any `UPDATE` or `DELETE`.
- Values reach SQL as parameters, never through f-strings.

---

## Sources

| Source | License | Used for |
|---|---|---|
| [Software Carpentry, *Databases and SQL*](https://swcarpentry.github.io/sql-novice-survey/) | CC-BY 4.0 (content), MIT (code) | `survey.db`, structure of 01–04 and 07, 09 |
| [PGExercises](https://pgexercises.com/) | CC BY-SA 3.0 | `clubdata.sql` (adapted, keeps the license) and exercise themes |
| [Knight Lab, *SQL Murder Mystery*](https://github.com/NUKnightLab/sql-mysteries) | MIT | Capstone database (downloaded, not committed) |
| [Use The Index, Luke](https://use-the-index-luke.com/) | Read online | Background for 08 |
| [Select Star SQL](https://selectstarsql.com/) | Proprietary, link only | Optional extra practice: an interactive book on a real dataset |

Timed and interview-style SQL problems are in [sisyphus `drills/`](https://github.com/ramseywise/sisyphus/blob/main/drills/README.md).
