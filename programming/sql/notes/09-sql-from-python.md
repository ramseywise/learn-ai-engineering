---
origin: curated
sources:
  - "Software Carpentry, Databases and SQL, episode 10 — https://swcarpentry.github.io/sql-novice-survey/10-prog.html (CC-BY 4.0)"
  - "Python docs, sqlite3 — https://docs.python.org/3/library/sqlite3.html"
  - "DuckDB Python API — https://duckdb.org/docs/api/python/overview"
concepts: [sql-from-python, sql-injection, sql-parameters, duckdb, pandas-sql]
cleaned: 2026-10-29
---
# 9 — SQL from Python

> SQL does the set operations. Python does the orchestration. Values cross the boundary as **parameters**, never as pasted strings.

---

## `sqlite3`: in the standard library

```python
import sqlite3

with sqlite3.connect("practice/data/clubdata.db") as conn:      # commits or rolls back on exit
    conn.row_factory = sqlite3.Row                               # rows behave like dicts
    rows = conn.execute(
        "SELECT surname, firstname FROM members WHERE joindate >= ? ORDER BY joindate",
        ("2012-09-01",),
    ).fetchall()

for r in rows:
    print(r["firstname"], r["surname"])
```

- `execute` returns a cursor. Use `fetchone()`, `fetchall()`, or iterate over it to stream rows.
- `executemany(sql, rows)` does a batch insert. Wrap large loads in one transaction, which is what the `with` block does.
- The `with` block commits or rolls back. It does **not** close the connection; call `conn.close()` or use `contextlib.closing`.

## Parameters, not f-strings

```python
name = "O'Brien'; DROP TABLE members; --"
conn.execute(f"SELECT * FROM members WHERE surname = '{name}'")   # SQL injection
conn.execute("SELECT * FROM members WHERE surname = ?", (name,))  # safe
```

The driver sends the SQL and the values separately, so a value can never become code. Placeholder styles differ: `?` (sqlite3, DuckDB), `%s` (psycopg), `:name` (sqlite3, SQLAlchemy). Parameters work only for **values**. You can't parameterise a table or column name. If those must be dynamic, check them against an allow-list.

## DuckDB: analytics in-process

```python
import duckdb

duckdb.sql("SELECT facid, sum(slots) FROM 'bookings.parquet' GROUP BY facid").show()
duckdb.sql("SELECT * FROM read_csv('data/*.csv') WHERE amount > 100").df()   # → pandas

import pandas as pd
df = pd.DataFrame({"x": [1, 2, 3]})
duckdb.sql("SELECT avg(x) FROM df")      # queries a DataFrame in scope by its variable name
```

DuckDB is columnar and vectorised. It queries CSV, Parquet and JSON files, and pandas or Polars frames, directly with no load step. It can also attach SQLite files: `ATTACH 'clubdata.db' (TYPE sqlite)`. It is the quickest way to put SQL in front of files.

## pandas ↔ SQL

```python
df = pd.read_sql("SELECT * FROM bookings WHERE facid = ?", conn, params=(1,))
df.to_sql("bookings_copy", conn, if_exists="replace", index=False)
```

Which side does the work: **filter and aggregate in SQL** (the database reads less and sends back less), and **reshape and plot in pandas**. Pulling a million rows to compute one `groupby` in pandas is the classic anti-pattern.

## SQLAlchemy (when you need it)

SQLAlchemy Core gives you one API across database engines plus connection pooling. The ORM maps classes to tables. Use it in applications. For analysis scripts and pipelines, plain DB-API (`sqlite3`, `psycopg`) or DuckDB is simpler.

```python
from sqlalchemy import create_engine, text
engine = create_engine("sqlite:///practice/data/clubdata.db")
with engine.connect() as c:
    c.execute(text("SELECT count(*) FROM bookings WHERE facid = :f"), {"f": 1}).scalar_one()
```

---

## Exercises

[`practice/exercises/09_sql_from_python.py`](../practice/exercises/09_sql_from_python.py) runs with the standard library only.
