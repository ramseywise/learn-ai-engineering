# Programming — references

Everything the three tracks are built from, with how each source is used. Per-note sources are
in each note's frontmatter. Vendored files are also listed in [CURRICULUM.md → Sources](../CURRICULUM.md#sources).

## Python

| Source | License | How it's used |
|---|---|---|
| Charles Severance, [*Python for Everybody*](https://www.py4e.com/book) / *Python for Informatics* | CC BY-NC-SA 3.0 | Topic order for 01–02, **paraphrased**. No book text, slides or data files are copied |
| Jake VanderPlas, [*A Whirlwind Tour of Python*](https://github.com/jakevdp/WhirlwindTourOfPython) | CC0 | 03 · 01–04 |
| [Python documentation](https://docs.python.org/3/) (tutorial, data model, `itertools`, `functools`, `contextlib`, `asyncio`) | PSF | 03 |
| [uv](https://docs.astral.sh/uv/), [Ruff](https://docs.astral.sh/ruff/), [pytest](https://docs.pytest.org/), [Pydantic](https://docs.pydantic.dev/) | MIT / Apache-2.0 | 03 · 05–06 |
| Wes McKinney, [*Python for Data Analysis*](https://wesmckinney.com/book/), 2nd ed., [code and data](https://github.com/wesm/pydata-book/tree/2nd-edition) | Code and data MIT; book proprietary | Moved with the hand-off: chapter notebooks and `fetch_data.sh` are in [data-analytics 01](../data-analytics/01-python-for-data-analysis/references.md) |
| University of Michigan, *Applied Data Science with Python*; Wesleyan, *Data Analysis and Interpretation* (Coursera) | Proprietary | Moved with the hand-off: own course notes in [data-analytics 01](../data-analytics/01-python-for-data-analysis/references.md) `practice/courses/`; no course data included |
| Ben Gorman, [*DataWrangling*](https://github.com/ben519/DataWrangling) | Read online | Moved with the hand-off: [data-analytics 01](../data-analytics/01-python-for-data-analysis/references.md) `practice/courses/wrangle_pandas.py` (reads its CSVs from GitHub) |
| Luciano Ramalho, *Fluent Python*, 2nd ed. | Proprietary | Further reading for 03 |

## SQL

| Source | License | How it's used |
|---|---|---|
| Software Carpentry, [*Databases and SQL*](https://swcarpentry.github.io/sql-novice-survey/) | CC-BY 4.0 (content), MIT (code) | `survey.db`; structure of 01–04, 07, 09 |
| [PGExercises](https://pgexercises.com/) | CC BY-SA 3.0 | `clubdata.sql`, converted to SQLite; exercise themes |
| Knight Lab, [*SQL Murder Mystery*](https://github.com/NUKnightLab/sql-mysteries) | MIT | Capstone database, downloaded by `setup.sh` |
| Markus Winand, [*Use The Index, Luke*](https://use-the-index-luke.com/) | Read online | Background for 08 |
| [SQLite](https://sqlite.org/lang.html), [DuckDB](https://duckdb.org/docs/), [PostgreSQL](https://www.postgresql.org/docs/) docs | Public domain / MIT / PostgreSQL | Dialect notes throughout |

## TypeScript

| Source | License | How it's used |
|---|---|---|
| [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) | CC-BY 4.0 | Notes 02–05 and 07, paraphrased |
| [typescript-exercises](https://github.com/typescript-exercises/typescript-exercises) (Marat Dulin) | MIT | 15 vendored exercises; TS 7 patches in their `NOTICE.md` |
| [type-challenges](https://github.com/type-challenges/type-challenges) (Anthony Fu) | MIT | 26 easy and medium challenges |
| [Zod](https://zod.dev) | MIT | Note 08 |
| [Anthropic TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript) | MIT | Note 09 and `examples/claude.ts` |
| Matt Pocock, [Total TypeScript](https://www.totaltypescript.com/); Basarat, [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/) | Proprietary / read online | Further reading |
