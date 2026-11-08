# Programming — references

Everything the Python, SQL and TypeScript tracks are built from, with how each source is used. Per-note sources are
in each note's frontmatter. [Sources and depth](../CURRICULUM.md#sources-and-depth) says how source maps work across the courses.

## Python

| Source | License | How it's used |
|---|---|---|
| Charles Severance, [*Python for Everybody*](https://www.py4e.com/book) / *Python for Informatics* | CC BY-NC-SA 3.0 | Topic order for 01–02, **paraphrased**. No book text, slides or data files are copied |
| Jake VanderPlas, [*A Whirlwind Tour of Python*](https://github.com/jakevdp/WhirlwindTourOfPython) | CC0 | 03 · 01–04 |
| Ben Wilson, *Machine Learning Engineering in Action* (Manning, 2022), ch. 10 | Book proprietary; chapter PDF in [data-engineering/sources/ml-engineering-in-action/](../data-engineering/sources/ml-engineering-in-action/). Folded in as: ch. 10 exception handling → [03 · 04](python/03-language-for-engineers/notes/04-errors-and-context-managers.md#blind-catches-hide-wrong-input); mutable default → [03 · 01](python/03-language-for-engineers/notes/01-data-model-and-idioms.md#the-mutable-default-trap); named tuples → [03 · 05](python/03-language-for-engineers/notes/05-types-and-dataclasses.md). Ch. 4, 9 and 10 smells are in the [software-design references](software-design/references.md) | 03 · 01, 04, 05 |
| Jake VanderPlas, *Python Data Science Handbook* (O'Reilly, 2016), ch. 1 and 2 | Book is CC BY-NC-ND for text; chapter PDFs in [data-analytics/sources/python-data-science-handbook/](../data-analytics/sources/python-data-science-handbook/); the book's home is [data-analytics 01](../data-analytics/01-python-for-data-analysis/references.md). Folded in as: ch. 1 → [software-design 06](software-design/notes/06-debugging-and-profiling.md#the-same-tools-inside-ipython); ch. 2 → [computer-science 04](computer-science/notes/04-numbers-and-memory.md#broadcasting-stretching-without-copying) | software-design 06, computer-science 04 |
| [Python documentation](https://docs.python.org/3/) (tutorial, data model, `itertools`, `functools`, `contextlib`, `asyncio`) | PSF | 03 |
| [uv](https://docs.astral.sh/uv/), [Ruff](https://docs.astral.sh/ruff/), [pytest](https://docs.pytest.org/), [Pydantic](https://docs.pydantic.dev/) | MIT / Apache-2.0 | 03 · 05–06 |
| Wes McKinney, [*Python for Data Analysis*](https://wesmckinney.com/book/), 2nd ed., [code and data](https://github.com/wesm/pydata-book/tree/2nd-edition) | Code and data MIT; book proprietary | Moved with the hand-off: chapter notebooks and `fetch_data.sh` are in [data-analytics 01](../data-analytics/01-python-for-data-analysis/references.md) |
| University of Michigan, *Applied Data Science with Python*; Wesleyan, *Data Analysis and Interpretation* (Coursera) | Proprietary | Moved with the hand-off: own course notes in [data-analytics 01](../data-analytics/01-python-for-data-analysis/references.md) `practice/courses/`; no course data included |
| Ben Gorman, [*DataWrangling*](https://github.com/ben519/DataWrangling) | Read online | Moved with the hand-off: [data-analytics 01](../data-analytics/01-python-for-data-analysis/references.md) `practice/courses/wrangle_pandas.py` (reads its CSVs from GitHub) |
| Luciano Ramalho, *Fluent Python*, 2nd ed. | Proprietary | Further reading for 03 |
| Iusztin and Labonne, *LLM Engineer's Handbook* (Packt, 2024), ch. 2. Chapter PDF in [generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/](../generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/) | Proprietary; paraphrased | 03 · 06 (lock file against ranges; the pyenv, Poetry and Poe toolchain) |
| Python 3.14 documentation: [descriptor guide](https://docs.python.org/3.14/howto/descriptor.html), [MRO](https://docs.python.org/3.14/howto/mro.html), [data model](https://docs.python.org/3.14/reference/datamodel.html), [gc](https://docs.python.org/3.14/library/gc.html), [free threading](https://docs.python.org/3.14/howto/free-threading-python.html), [tracemalloc](https://docs.python.org/3.14/library/tracemalloc.html) | PSF | 03 · 08–09 |
| [PEP 487](https://peps.python.org/pep-0487/), [PEP 779](https://peps.python.org/pep-0779/) | Public domain or CC0 | 03 · 08 (487), 09 (779) |
| Raymond Hettinger, [*Python's super() considered super!*](https://rhettinger.wordpress.com/2011/05/26/super-considered-super/) | Read online | 03 · 08 |

The computer science foundations track keeps its own list: [computer-science/references.md](computer-science/references.md).

The frontend and UX track keeps its own list: [frontend-and-ux/references.md](frontend-and-ux/references.md).

The backend and system design track keeps its own list: [backend-and-system-design/references.md](backend-and-system-design/references.md).

The software design track keeps its own list: [software-design/references.md](software-design/references.md).

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
