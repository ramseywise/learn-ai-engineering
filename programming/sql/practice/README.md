# Running the SQL exercises

How the track's exercises are laid out, run and checked, and what is in each database. What to do after which note is in the [syllabus](../README.md#syllabus).

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

## Run it

```bash
cd programming/sql/practice
bash setup.sh                                      # builds clubdata.db, downloads the murder-mystery db
sqlite3 -header -column data/survey.db             # explore interactively
sqlite3 -header -column data/survey.db < exercises/01-select-and-filter.sql
bash check.sh                                      # runs every solution; `bash check.sh exercises` for yours
```

Files that switch databases do so with `.open data/clubdata.db`, so run them from `practice/`.
Module 07 runs against `:memory:` and loads a fresh copy of the club data, so nothing you change persists.

## The databases

| Database | Tables | Used in | Origin |
|---|---|---|---|
| `survey.db` (committed) | `Person`, `Site`, `Visited`, `Survey`: 1920s–30s Antarctic expedition readings, small enough to check by eye, with real `NULL`s | 01–04 | Software Carpentry |
| `clubdata.db` (built from `clubdata.sql`) | `members`, `facilities`, `bookings` (4,044 rows): a country club's booking system, with a self-referencing `recommendedby` | 01–09 | PGExercises, converted from Postgres to SQLite |
| `sql-murder-mystery.db` (downloaded) | Crime-scene reports, people, licences, gym check-ins, interviews | 10 | Knight Lab |

The notes point out where Postgres or DuckDB differ from SQLite, mostly for dates and `EXPLAIN`.

## Drills

Timed and interview-style SQL problems are in [`programming/drills/`](../../drills/README.md): the [window-functions drill](../../drills/sql/window-functions/top-orders-per-user.md) goes with step 2 of the syllabus.
