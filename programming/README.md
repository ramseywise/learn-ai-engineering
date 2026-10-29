# Programming

> Depth layer for the languages everything else in this repo is written in: **Python**, **SQL**
> and **TypeScript**. Practice reps (HackerRank, LeetCode, interview-format coding rounds) live in
> [sisyphus `drills/`](https://github.com/ramseywise/sisyphus/blob/main/drills/README.md).
> librarian shows both.
> Jump to: [Tracks](#tracks) · [How the pieces fit](#how-the-pieces-fit) · [Running the code](#running-the-code) · [References](references.md)

---

## What it is

A self-paced course in the three languages an AI or data engineer writes every day. Each track
goes from first principles to the idioms you need in production code. Each module is a short set of
notes followed by exercises you can run offline.

This repo started as a Python learning repo built from *Python for Informatics* (now *Python for
Everybody*) and McKinney's *Python for Data Analysis*. The Python track keeps that spine and adds a
module on the language features that engineering code relies on.

The ordering is in [CURRICULUM.md](CURRICULUM.md).

---

## Tracks

| Track | Modules | Built from | Start here |
|---|---|---|---|
| **Python** | 01 foundations · 02 informatics · 03 language for engineers · 04 Python for data | Severance, *Python for Everybody* (paraphrased); VanderPlas, *A Whirlwind Tour of Python* (CC0); McKinney, *Python for Data Analysis* (code MIT); Michigan *Applied Data Science* and Wesleyan coursework | [python/README.md](python/README.md) |
| **SQL** | 01–09, from `SELECT` to query plans, plus a capstone | Software Carpentry *Databases and SQL* (CC-BY 4.0); PGExercises (CC BY-SA 3.0); Knight Lab *SQL Murder Mystery* (MIT) | [sql/README.md](sql/README.md) |
| **TypeScript** | 01–09, from JavaScript for Python developers to TS for AI apps | TypeScript Handbook (CC-BY 4.0); *typescript-exercises* (MIT); *type-challenges* (MIT) | [typescript/README.md](typescript/README.md) |

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

| Track | Needs | Command |
|---|---|---|
| Python 01–03 | Python 3.12+, standard library only (03 · 06 uses `uv`) | `python3 practice/exercises/<file>.py` (each file runs its own `assert`s) |
| Python 04 | `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, Jupyter | `bash fetch_data.sh` once, then open the notebooks |
| SQL | `sqlite3` CLI (bundled with macOS) or `duckdb` | `bash practice/setup.sh`, then `sqlite3 practice/data/survey.db` |
| TypeScript | Node 22.18+ (runs `.ts` directly) | `cd typescript/practice && npm install && npm test` |

Nothing needs an API key except the last TypeScript module, which says so at the top.
