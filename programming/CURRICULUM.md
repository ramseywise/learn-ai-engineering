# Programming — Curriculum

Last updated: 2026-10-29

## Prerequisites

None. This is an entry point. You need a terminal, Python 3.12+, the `sqlite3` CLI and Node 22.18+.

## The order

The three tracks run partly in parallel. Python comes first because the other two assume you can
read it. SQL starts once Python 01 is done, and TypeScript once Python 03 is done.

| Phase | Python | SQL | TypeScript | Roughly |
|---|---|---|---|---|
| 1. Write programs | 01 foundations (5 notes) | — | — | 2 weeks |
| 2. Talk to the world | 02 informatics (5 notes) | 01–05: select → CTEs | — | 2–3 weeks |
| 3. Write it like an engineer | 03 language for engineers (7 notes) | 06–09: windows, DDL, indexes, SQL from Python | — | 3 weeks |
| 4. Analyse data | 04 Python for data (7 notebooks + McKinney) | 10: capstone | 01–05: JS → type transformations | 3–4 weeks |
| 5. Build typed apps | — | — | 06–09: async, tooling, Zod, TS for AI apps | 2 weeks |

Skip what you already know. Every module's exercises double as a placement test: if the file
passes on your first try, move on.

## Hand-offs

| When you finish | You're ready for |
|---|---|
| Python 02 · 05 | SQL 01 (the Python side of databases ends there; SQL itself starts) |
| SQL 09 | Python 04 notebook 4 (joins in pandas, with the SQL mental model) |
| Python 03 · 07 | TypeScript 06 (the same async model with promises) |
| Python 03 · 05 | TypeScript 02 and 08 (types and boundary validation, now with a stricter checker) |
| Python 04 | [data-analytics](../data-analytics/CURRICULUM.md), [data-science](../data-science/CURRICULUM.md) |
| Python 03 + TypeScript 09 | [ai-engineering](../ai-engineering/README.md) (every pillar's code is Python or TS) |

## Practice beyond the course

| Need | Where |
|---|---|
| Timed problems, HackerRank / LeetCode style | [sisyphus `drills/`](https://github.com/ramseywise/sisyphus/blob/main/drills/README.md), which links back here by `concepts:` slug |
| Interview-format review | sisyphus [interview guide Pillar 0 (programming)](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md) |
| More type puzzles | [type-challenges](https://github.com/type-challenges/type-challenges) hard and extreme |
| More SQL | [PGExercises](https://pgexercises.com/), [Select Star SQL](https://selectstarsql.com/) |

## Definition of done (per module)

1. The note's code samples run as written.
2. Every exercise has a worked solution, and `check.sh solutions` / `npm run check` is green.
3. The exercises run offline, or say what they need (only TypeScript's live example needs a key).
4. Every note has `sources` and `concepts` in its frontmatter.
