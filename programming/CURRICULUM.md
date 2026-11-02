# Programming: course curriculum

> Learn the three languages used throughout this repository: Python for data and services, SQL for data systems, and TypeScript for typed applications and AI interfaces.

This is the learner-facing syllabus for Programming. Work through a track's notes, use its deck for review, solve exercises before opening solutions, and keep the stated evidence of mastery. Track READMEs contain setup and exact run commands; [references.md](references.md) records complete sources and licences.

## Course outcomes

By the end of the course, you can:

1. Write readable, tested Python programs that work with files, structured data, databases, packages, types, and concurrency.
2. Query, model, and change relational data safely; inspect a query plan and use SQL from Python.
3. Build strict, maintainable TypeScript programs with runtime validation, asynchronous control flow, and typed AI boundaries.
4. Read, test, and improve the Python and TypeScript examples used by the data and AI-engineering courses.

## Before you begin

There are no programming prerequisites. You need a terminal, Python 3.12+, the `sqlite3` CLI, and Node 22.18+ for the parts you choose to take. Start with Python 01. Begin SQL after Python 01; begin TypeScript after Python 03, when types and asynchronous work have context.

## How to use the course

| Activity | What you do | What it demonstrates |
|---|---|---|
| Notes | Read a module in sequence and reproduce its small examples. | You understand the language rule and its trade-off. |
| Deck review | Use the module or track deck as a recall prompt. | You can state the rule without copying code. |
| Exercises | Implement the stubs before reading worked solutions. | You can apply the idea in a constrained problem. |
| Checks | Run the track's test/check command. | Your code meets the executable specification. |
| Drills | Use the linked drills after a module. | You can retrieve the skill under time pressure. |

## Course map

| Track | Recommended entry | Main units | Primary evidence |
|---|---|---|---|
| [Python](#track-01--python) | Start here | Foundations → Informatics → Language for engineers | Passing exercises and a small tested package |
| [SQL](#track-02--sql) | After Python foundations | Querying → analysis → data design → performance → Python | Checked queries and an investigative capstone |
| [TypeScript](#track-03--typescript) | After Python engineers | JavaScript → types → async/tooling → typed AI apps | Type-safe exercises and a validated async boundary |

The tracks deliberately overlap. Python gives SQL and TypeScript their programming vocabulary; SQL sharpens the data model before [Data Analytics](../data-analytics/CURRICULUM.md); Python plus TypeScript prepares you for [AI Engineering](../ai-engineering/README.md).

---

## Track 01 — Python

**Purpose:** Move from first programs to the idioms used in reliable Python services and data tooling. The track ends at the language boundary; pandas begins in [Data Analytics 01](../data-analytics/01-python-for-data-analysis/README.md).

**Learning objectives**

After this track, you can:

1. Write functions that return useful values, choose appropriate built-in collections, and handle ordinary control flow and files.
2. Extract and validate information from text, HTTP responses, JSON/XML, and a SQLite database.
3. Reason about names, objects, iteration, errors, resource lifetimes, and common Python traps.
4. Use type hints, dataclasses, tests, linting, packaging, and boundary validation in a small package.
5. Choose threads, asyncio, or processes for a workload and apply timeouts and concurrency limits.

**Units and chapters**

| Unit | Chapters | Practice |
|---|---|---|
| [01 Foundations](python/01-foundations/notes/01-values-and-conditionals.md) | Values and conditionals; functions; loops; strings and files; collections | [Exercises](python/01-foundations/practice/exercises/) |
| [02 Informatics](python/02-informatics/notes/01-regular-expressions.md) | Regular expressions; HTTP; JSON/XML/APIs; objects; databases | [Exercises](python/02-informatics/practice/exercises/) |
| [03 Language for engineers](python/03-language-for-engineers/notes/01-data-model-and-idioms.md) | Data model; iteration; deeper functions; errors; types; packaging/tooling; concurrency | [Exercises](python/03-language-for-engineers/practice/exercises/) |

**Review and practice:** [foundations deck](python/01-foundations/slides/python-foundations.pptx) · [informatics deck](python/02-informatics/slides/python-informatics.pptx) · [engineering deck](python/03-language-for-engineers/slides/python-for-engineers.pptx) · module exercises and worked solutions.

**Mastery lab:** Create a small typed Python package that reads structured input, validates it at the boundary, uses a resource safely, returns useful errors, and has tests for its core behavior. Add bounded concurrent work only where it improves the design.

**Evidence:** Your own solutions pass [`python/check.sh`](python/check.sh); the lab includes a `pyproject.toml`, typed public functions, tests, and a short explanation of its error and concurrency choices.

**Key sources:** Severance, [*Python for Everybody*](https://www.py4e.com/book/) · VanderPlas, [*A Whirlwind Tour of Python*](https://github.com/jakevdp/WhirlwindTourOfPython) · [Python documentation](https://docs.python.org/3/) · [uv](https://docs.astral.sh/uv/), [Ruff](https://docs.astral.sh/ruff/), [pytest](https://docs.pytest.org/), and [Pydantic](https://docs.pydantic.dev/).

**Next:** [Data Analytics 01](../data-analytics/01-python-for-data-analysis/README.md) for pandas and tabular work; SQL 01 for relational querying; TypeScript 01–05 after the engineering unit.

---

## Track 02 — SQL

**Purpose:** Learn to ask, verify, and change questions of relational data safely—from a first `SELECT` to query plans and a real investigation.

**Learning objectives**

After this track, you can:

1. Write clear `SELECT`, filtering, ordering, expression, aggregation, and conditional-aggregation queries.
2. Reason correctly about `NULL`, dates, strings, and three-valued logic.
3. Choose joins, subqueries, CTEs, recursion, and window functions without changing a result's grain accidentally.
4. Design tables with constraints, perform safe changes in transactions, and use parameterised SQL from Python.
5. Read a query plan, write sargable predicates, and select indexes appropriate to a query.

**Units and chapters**

| Unit | Chapters | Practice |
|---|---|---|
| [Core querying](sql/notes/01-select-and-filter.md) | Select/filter; nulls, dates, strings; aggregation; joins; subqueries and CTEs | [Exercises 01–05](sql/practice/exercises/) |
| [Analytical and operational SQL](sql/notes/06-window-functions.md) | Window functions; DDL and changes; indexes and query plans; SQL from Python | [Exercises 06–09](sql/practice/exercises/) |
| [Capstone](sql/notes/10-capstone-murder-mystery.md) | SQL Murder Mystery investigation | [Practice data](sql/practice/) |

**Review and practice:** [SQL deck](sql/slides/sql.pptx) · offline SQL/Python exercises and solutions · the capstone investigation.

**Mastery lab:** Solve the capstone with a query trail that another person can reproduce. Add one analytical query using a window function and one safe data-change or parameterised Python example, explaining grain, `NULL` behavior, and validation checks.

**Evidence:** Your queries pass [`sql/practice/check.sh`](sql/practice/check.sh). The capstone includes the answer, the queries that establish it, and a short explanation of why each join cannot fan out the result.

**Key sources:** [Software Carpentry: Databases and SQL](https://swcarpentry.github.io/sql-novice-survey/) · [PGExercises](https://pgexercises.com/) · [SQL Murder Mystery](https://github.com/NUKnightLab/sql-mysteries) · [Use The Index, Luke](https://use-the-index-luke.com/) · [SQLite documentation](https://sqlite.org/lang.html).

**Next:** [Data Analytics](../data-analytics/CURRICULUM.md) for analytical interpretation and pandas; [Data Engineering](../data-engineering/README.md) for data systems and pipelines.

---

## Track 03 — TypeScript

**Purpose:** Move from JavaScript fluency to a strict type system, safe runtime boundaries, and the async patterns required in typed applications and AI integrations.

**Learning objectives**

After this track, you can:

1. Translate Python habits into idiomatic JavaScript while avoiding coercion, sorting, and truthiness traps.
2. Model application data with interfaces, types, unions, narrowing, generics, and type transformations.
3. Configure a strict TypeScript project, describe modules, and make type-level guarantees executable through tests.
4. Write async work with timeouts, retries, parallelism, and concurrency limits.
5. Validate environment variables, JSON, and model output at runtime rather than trusting erased types.
6. Build a typed tool-loop or streaming AI integration that narrows content blocks and handles stop reasons safely.

**Units and chapters**

| Unit | Chapters | Practice |
|---|---|---|
| [JavaScript and core types](typescript/notes/01-js-for-python-devs.md) | JavaScript for Python developers; everyday types; unions and narrowing | [Type exercises](typescript/practice/typescript-exercises/) |
| [Type-level design](typescript/notes/04-generics.md) | Generics; transformations from types | [Exercises and type challenges](typescript/practice/) |
| [Production boundaries](typescript/notes/06-async.md) | Async; modules/tooling; Zod runtime validation; TypeScript for AI apps | [Runtime exercises](typescript/practice/exercises/) |

**Review and practice:** [TypeScript deck](typescript/slides/typescript.pptx) · vendored type exercises and challenges · runtime exercises with tests. The live SDK example is optional and requires its own key; it is not required for mastery.

**Mastery lab:** Build a small strict TypeScript boundary: parse untrusted input with Zod, model outcomes as a discriminated union, run independent work concurrently with a limit and timeout, and test success and failure paths. An optional extension can call a model or tool API.

**Evidence:** The implementation and its tests pass [`npm run check`](typescript/practice/package.json); explain the runtime boundary and how the union makes an unhandled outcome impossible to ignore.

**Key sources:** [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) · [typescript-exercises](https://github.com/typescript-exercises/typescript-exercises) · [type-challenges](https://github.com/type-challenges/type-challenges) · [Zod](https://zod.dev) · [Anthropic TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript).

**Next:** [AI Engineering](../ai-engineering/README.md) for production LLM systems, or [Generative AI](../generative-ai/README.md) for LLM foundations and applications.

---

## Completion standard and further practice

Complete the Python track before moving to data or AI work. Take SQL when you will query or model data; take TypeScript when you will build typed applications. A complete programming foundation includes a passing Python exercise set and package, checked SQL exercises and capstone, and passing TypeScript checks plus a validated asynchronous boundary.

For timed or interview-format practice, use [the practice drills](../practice/drills/README.md). The [Programming interview guide](../practice/interviewing/guides/00-start-here.md) is a review layer, not a substitute for implementing the exercises.

## Complete references

See [programming references](references.md) for source licences, complete mappings, and additional reading. Each track README also maps sources directly to its notes.
