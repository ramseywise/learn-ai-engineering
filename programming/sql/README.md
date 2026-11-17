# SQL

Ask a relational database a question and know the answer is right, from a first `SELECT` to reading a query plan. Four steps, nine short notes and a capstone, each with exercises you can run offline against SQLite.

**What you should already know.** [Python 01 Foundations](../python/README.md): SQL starts after it. The last step drives SQL from Python, so it also needs [functions](../python/01-foundations/notes/02-functions.md) and [collections](../python/01-foundations/notes/05-collections.md).

## Lecture

Start with the overview deck, [SQL](slides/sql.pptx) ([PDF](slides/sql.pdf)), on the same databases as the notes. Librarian turns each slide into a flashcard: the title is the question and the takeaway is the rule that answers it.

## The core

A query that runs is not a query that is right. A join can multiply rows, a `NULL` can drop them, and an aggregate will return a clean number either way. So the question this track keeps asking is: **what is one row of this result, and how many should there be?** Answer it before the query runs, and count afterwards.

There are four steps: query one table, combine tables without changing what a row means, design tables and make queries fast, then use all of it from a program and on an open-ended investigation. This track teaches the language. What an analyst does with it (cohorts, funnels, retention) is in [data-analytics 06/06](../../data-analytics/06-applied-analyses/notes/06-sql-for-analytics.md), and what the engine does underneath is in [data-engineering 01](../../data-engineering/01-storage-and-compute-foundations/README.md).

## Syllabus

One row per step. **Core concepts** are the ideas the step turns on, **Study** is what to read, **Labs** is what to do afterwards (the track's own exercises first, then the drills on the same topic), and **Sources** is where to read more. How to run the labs, and what is in each database: [practice/README.md](practice/README.md).

| Submodule | Core concepts | Study | Labs | Sources |
|---|---|---|---|---|
| **1. Query:** one table | A query is evaluated `FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY`, not in reading order. `NULL` is "unknown", so `= NULL` is never true. Date ranges are half-open. `GROUP BY` sets what one row means. | [1 Selecting, sorting and filtering](notes/01-select-and-filter.md) · [2 Missing data, dates and strings](notes/02-nulls-and-expressions.md) · [3 Aggregation](notes/03-aggregation.md) | Exercises [01](practice/exercises/01-select-and-filter.sql) · [02](practice/exercises/02-nulls-and-expressions.sql) · [03](practice/exercises/03-aggregation.sql) | [Software Carpentry, *Databases and SQL*](https://swcarpentry.github.io/sql-novice-survey/) · [PGExercises](https://pgexercises.com/) |
| **2. Combine:** several tables, same grain | State what a join should do to the row count, then count. A filter on the right table of a `LEFT JOIN` belongs in `ON`. A CTE names a step. A window function adds a column without collapsing rows, and top-N per group is `row_number()` in a CTE, filtered outside. | [4 Joins](notes/04-joins.md) · [5 Subqueries and CTEs](notes/05-subqueries-and-ctes.md) · [6 Window functions](notes/06-window-functions.md) | Exercises [04](practice/exercises/04-joins.sql) · [05](practice/exercises/05-subqueries-and-ctes.sql) · [06](practice/exercises/06-window-functions.sql) · drill: [top orders per user](../drills/sql/window-functions/top-orders-per-user.md) | [PGExercises](https://pgexercises.com/) · [Select Star SQL](https://selectstarsql.com/): optional extra practice |
| **3. Design and tune:** tables, changes and plans | Constraints are the checks you never have to remember to run. Changes that belong together go in one transaction, and you count with the same `WHERE` before any `UPDATE` or `DELETE`. An index is a sorted copy: column order decides which predicates can use it, and the plan tells you whether it did. | [7 Designing tables and changing data](notes/07-modeling-and-ddl.md) · [8 Indexes and query plans](notes/08-indexes-and-query-plans.md) | Exercises [07](practice/exercises/07-modeling-and-ddl.sql) · [08](practice/exercises/08-indexes-and-query-plans.sql) · drills: [index quiz](../drills/mcq/quiz1.md) · [scaling a SQLite query](../drills/coding/prompts/db-sqlite-scaling.py) | [Software Carpentry, *Databases and SQL*](https://swcarpentry.github.io/sql-novice-survey/) · Winand, [*Use The Index, Luke*](https://use-the-index-luke.com/) |
| **4. Use:** from Python, and on a real question | Values reach SQL as parameters, never through f-strings. Filter and aggregate in the database, then hand a small result to pandas. An investigation is a trail of queries someone else can rerun. | [9 SQL from Python](notes/09-sql-from-python.md) · [10 Capstone: the SQL Murder Mystery](notes/10-capstone-murder-mystery.md) | Exercise [09](practice/exercises/09_sql_from_python.py) · the capstone itself, on `sql-murder-mystery.db` | [Software Carpentry, *Databases and SQL*](https://swcarpentry.github.io/sql-novice-survey/) · [Knight Lab, *SQL Murder Mystery*](https://github.com/NUKnightLab/sql-mysteries) |

Worked answers are in [`practice/solutions/`](practice/solutions/). Try each exercise before you open them. The drills folder is thin for SQL: [its README](../drills/sql/README.md) lists what interviews ask that is not there yet.

## Rules of thumb

- Write the query in evaluation order (`FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY`), not reading order.
- `NULL` is "unknown", not a value. `= NULL` is never true, and `NOT IN` with a `NULL` in the list returns nothing.
- Date ranges are half-open: `>= start AND < next_start`. That is correct for timestamps and keeps the index usable.
- A filter on the right table of a `LEFT JOIN` belongs in `ON`, not `WHERE`.
- Top-N per group is `row_number() OVER (PARTITION BY … ORDER BY …, unique_col)` in a CTE, filtered outside.
- Run `SELECT count(*)` with the same `WHERE` before any `UPDATE` or `DELETE`.
- Values reach SQL as parameters, never through f-strings.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [Python 01 Foundations](../python/README.md) | SQL starts after it, and [09](notes/09-sql-from-python.md) drives SQL from Python |

**Feeds into**

| Chapter | Why |
|---|---|
| [DA 06/06 SQL for analytics](../../data-analytics/06-applied-analyses/notes/06-sql-for-analytics.md) | Analytical SQL on top of these joins and window functions |
| [Python 02/05 Databases](../python/02-informatics/notes/05-databases.md) | Hands the SQL itself to this track |
| [Backend and system design](../backend-and-system-design/README.md) | Its chapters 1 and 3 run SQLite and assume [07](notes/07-modeling-and-ddl.md) and [08](notes/08-indexes-and-query-plans.md) from the first page |

## Primary texts

- Software Carpentry, *Databases and SQL*
- PGExercises
- Knight Lab, *SQL Murder Mystery*
- Winand, *Use The Index, Luke*

Licences and what each source was used for:

| Source | License | Used for |
|---|---|---|
| [Software Carpentry, *Databases and SQL*](https://swcarpentry.github.io/sql-novice-survey/) | CC-BY 4.0 (content), MIT (code) | `survey.db`, structure of 01–04 and 07, 09 |
| [PGExercises](https://pgexercises.com/) | CC BY-SA 3.0 | `clubdata.sql` (adapted, keeps the license) and exercise themes |
| [Knight Lab, *SQL Murder Mystery*](https://github.com/NUKnightLab/sql-mysteries) | MIT | Capstone database (downloaded, not committed) |
| [Use The Index, Luke](https://use-the-index-luke.com/) | Read online | Background for 08 |
| [Select Star SQL](https://selectstarsql.com/) | Proprietary, link only | Optional extra practice: an interactive book on a real dataset |

Everything else: [references.md](../references.md). The deck is built from [`slides/deck.yaml`](slides/deck.yaml) with `make slides PILLAR=programming/sql`.

## Next

Start with step 1, **Query**: read [1 Selecting, sorting and filtering](notes/01-select-and-filter.md), then do its exercise from the syllabus row.

After step 4 you can get a correct answer out of a database and show how you got it. What the answer means for a product is the next subject, [data analytics](../../data-analytics/README.md). How the store underneath keeps its promises is [data engineering](../../data-engineering/README.md).
