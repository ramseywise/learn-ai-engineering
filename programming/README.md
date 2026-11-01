# Programming

> Depth layer for the languages everything else in this repo is written in: **Python**, **SQL**
> and **TypeScript**. Practice reps (HackerRank, LeetCode, interview-format coding rounds) live in
> [sisyphus `drills/`](https://github.com/ramseywise/sisyphus/blob/main/drills/README.md).
> librarian shows both. The summary layer is sisyphus
> [interview guide Pillar 0 — Programming](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md).
> Position in the path: the entry point, no prerequisites; next are
> [data-analytics](../data-analytics/README.md) and [ai-engineering](../ai-engineering/README.md).
> Jump to: [Tracks](#tracks) · [Layout](#layout) · [How the pieces fit](#how-the-pieces-fit) · [Running the code](#running-the-code) · [References](references.md)

---

## What it is

A self-paced course in the three languages an AI or data engineer writes every day. Each track
goes from first principles to the idioms you need in production code. Each module is a short set of
notes followed by exercises you can run offline.

This repo started as a Python learning repo built from *Python for Informatics* (now *Python for
Everybody*) and McKinney's *Python for Data Analysis*. The Python track keeps that spine and adds a
module on the language features that engineering code relies on.

The ordering is in [CURRICULUM.md](CURRICULUM.md); sources and licences are in [references.md](references.md).

---

## Tracks

| Track | Modules | Built from | Start here |
|---|---|---|---|
| **Python** | 01 foundations · 02 informatics · 03 language for engineers · 04 Python for data | Severance, *Python for Everybody* (paraphrased); VanderPlas, *A Whirlwind Tour of Python*; McKinney, *Python for Data Analysis*; Michigan *Applied Data Science* and Wesleyan coursework | [python/README.md](python/README.md) |
| **SQL** | 01–09, from `SELECT` to query plans, plus a capstone | Software Carpentry *Databases and SQL*; PGExercises; Knight Lab *SQL Murder Mystery* | [sql/README.md](sql/README.md) |
| **TypeScript** | 01–09, from JavaScript for Python developers to TS for AI apps | TypeScript Handbook; *typescript-exercises*; *type-challenges* | [typescript/README.md](typescript/README.md) |

---

## Layout

```
programming/
├── README.md            this file
├── CURRICULUM.md        order, hand-offs and prerequisites
├── references.md        every source, with licence and how it is used
├── python/              README + check.sh; 01–03 are NN-module/{notes, practice/{exercises, solutions}}; 04 is notebooks + mckinney/ + courses/ + fetch_data.sh
├── sql/                 README + notes/ + practice/{exercises, solutions, data, setup.sh, check.sh}
└── typescript/          README + notes/ + practice/ (one npm project: exercises, solutions, tests, examples, typescript-exercises/, type-challenges/, check.ts)
```

Each track README has its own tree.

---

## How the pieces fit

| Repo | Role | Programming content |
|---|---|---|
| **learn-ai-engineering** (here) | Learn the skill | Notes, worked notebooks and guided exercises with solutions |
| **sisyphus** `drills/` | Practise the skill | HackerRank and LeetCode solutions, timed drills, interview-format coding rounds |
| **librarian** | Read both | Imports this folder as the *Programming* course and sisyphus `drills/` as *Drills* (`make import-courses`) |

Notes use `concepts:` slugs in their frontmatter. Drills list the same slugs, so a drill can link
back to the note that teaches it.

---

## Running the code

Every practice set and script, with what it needs. The track READMEs give the full commands.

| Practice set | Runs | Command |
|---|---|---|
| Python 01–03 exercise and solution files | Offline: Python 3.12+, standard library | `python3 practice/exercises/<file>.py` (each file runs its own `assert`s) |
| Python 03 · 06 package (`06_tooling/`) | Needs `uv`; the first run downloads pytest and ruff into a local `.venv/` | `uv run pytest` inside the package |
| [`python/check.sh`](python/check.sh) | Offline after that first `uv` run: it runs every exercise file, then `uv run pytest` for 06 | `bash check.sh`, `bash check.sh solutions`, `bash check.sh exercises 03` |
| Python 04 notebooks and McKinney chapters | Needs download: [`fetch_data.sh`](../data-analytics/01-python-for-data-analysis/practice/fetch_data.sh) clones ~240 MB from wesm/pydata-book (gitignored); needs `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, Jupyter | `bash fetch_data.sh` once, then open the notebooks |
| Python 04 `courses/` scripts | Legacy, read next to a REPL: `wrangle_pandas.py` needs network (reads its CSVs from GitHub); the two Michigan scripts need course data that is not redistributed | — |
| SQL 01–09 exercise and solution files | Offline: `sqlite3` CLI (bundled with macOS); `survey.db` is committed, `clubdata.db` is built locally by `setup.sh` | `sqlite3 data/survey.db < exercises/<file>.sql`; `python3 exercises/09_sql_from_python.py` |
| [`sql/practice/setup.sh`](sql/practice/setup.sh) | Needs download on first run: fetches `sql-murder-mystery.db` (3.6 MB) with `curl`; building `clubdata.db` is offline | `bash setup.sh` |
| [`sql/practice/check.sh`](sql/practice/check.sh) | Offline once `setup.sh` has run (it calls `setup.sh` itself if `clubdata.db` is missing) | `bash check.sh`, `bash check.sh exercises` |
| SQL 10 capstone | Needs the downloaded `sql-murder-mystery.db` | `sqlite3 data/sql-murder-mystery.db` |
| TypeScript exercises, tests, vendored `typescript-exercises/` and `type-challenges/`, [`check.ts`](typescript/practice/check.ts) | Needs Node 22.18+ (runs `.ts` directly, no build step) and one `npm install` (downloads TypeScript 7, zod, `@types/node`, the Anthropic SDK into the gitignored `node_modules/`) | `cd typescript/practice && npm install && npm run check` |
| TypeScript live example [`examples/claude.ts`](typescript/practice/examples/claude.ts) | Needs an API key (`ANTHROPIC_API_KEY`); exits cleanly without one | `node examples/claude.ts` |
