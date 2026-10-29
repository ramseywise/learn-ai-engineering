---
origin: curated
sources:
  - "Charles Severance, Python for Everybody, ch. 15 — https://www.py4e.com/book (CC BY-NC-SA 3.0; paraphrased)"
concepts: [sqlite3, relational-modeling, foreign-keys, data-ingest, many-to-many]
cleaned: 2026-10-29
---
# 5 — Using Databases from Python

> When data outgrows a dict in memory, or needs to survive between runs, put it in a database. SQLite is a single file plus the standard library: enough for most scripts.

---

This note covers the Python side of py4e's chapter. **SQL itself has its own track**: start at [SQL 01](../../../sql/notes/01-select-and-filter.md), and [SQL 09](../../../sql/notes/09-sql-from-python.md) covers parameters, DuckDB and pandas.

## The ingest pattern

py4e's database projects (email counts, the iTunes track list, a roster, a geocoding cache) all follow this pattern:

```python
import sqlite3

conn = sqlite3.connect("tracks.sqlite")
conn.executescript("""
CREATE TABLE IF NOT EXISTS artist (id INTEGER PRIMARY KEY, name TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS track  (id INTEGER PRIMARY KEY, title TEXT UNIQUE,
                                   artist_id INTEGER REFERENCES artist(id), plays INTEGER);
""")

def get_or_create(conn, table, name):
    conn.execute(f"INSERT OR IGNORE INTO {table} (name) VALUES (?)", (name,))   # table name: from code, never user input
    return conn.execute(f"SELECT id FROM {table} WHERE name = ?", (name,)).fetchone()[0]

with conn:                                      # one transaction for the whole load
    for title, artist, plays in rows:
        artist_id = get_or_create(conn, "artist", artist)
        conn.execute("INSERT OR REPLACE INTO track (title, artist_id, plays) VALUES (?, ?, ?)",
                     (title, artist_id, plays))
```

- **Normalise.** Store each artist once and reference it by `id`. Join them back together when you query.
- **`INSERT OR IGNORE` + `SELECT id`** is the get-or-create step. A `UNIQUE` constraint makes it safe to re-run.
- **Many-to-many** relations (students ↔ courses) need a join table with a composite primary key: `member(user_id, course_id, role)`.
- Commit once per batch, not once per row. Committing every row is about 100× slower.
- **Re-runnable scripts**: a crawler or geocoder should store progress in the database, so it can resume after a crash or a rate limit instead of starting over.

---

## Exercises

[`practice/exercises/05_databases.py`](../practice/exercises/05_databases.py): load tracks into normalised tables in `:memory:` and query them with a join.
