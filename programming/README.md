# Programming

> Depth layer for the languages everything else in this repo is written in: **Python**, **SQL** and **TypeScript**, plus **computer science foundations** and **software design**: keeping code cheap to change. Timed practice (HackerRank, LeetCode, interview-format coding rounds) lives in [`practice/drills/`](../practice/drills/README.md).
>
> Position in the path: the entry point, no prerequisites; next are [data-analytics](../data-analytics/README.md) and [ai-engineering](../ai-engineering/README.md).

## What it is

A self-paced course in the three languages an AI or data engineer writes every day, and in how to keep that code cheap to change. Each language track goes from first principles to the idioms you need in production code. Each module is a short set of notes followed by exercises you can run offline.

This repo started as a Python learning repo built from *Python for Informatics* (now *Python for Everybody*) and McKinney's *Python for Data Analysis*. The Python track keeps the first of those as its spine and adds a module on the language features that engineering code relies on. The pandas half now has its own home: when Python 03 is done, the path hands off to [data-analytics 01, Python for data analysis](../data-analytics/01-python-for-data-analysis/README.md).

Notes use `concepts:` slugs in their frontmatter. Drills list the same slugs, so a drill can link back to the note that teaches it.

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

## Tracks

| Track | Recommended entry | Main units | Built from | Primary evidence |
|---|---|---|---|---|
| [Python](python/README.md) | Start here | Foundations → informatics → language for engineers, then a hand-off to [data-analytics 01](../data-analytics/01-python-for-data-analysis/README.md) | Severance, *Python for Everybody* (paraphrased); VanderPlas, *A Whirlwind Tour of Python*; Python documentation | Passing exercises and a small tested package |
| [SQL](sql/README.md) | After Python foundations | Querying → analysis → data design → performance → Python, plus a capstone | Software Carpentry *Databases and SQL*; PGExercises; Knight Lab *SQL Murder Mystery* | Checked queries and an investigative capstone |
| [TypeScript](typescript/README.md) | After Python for engineers | JavaScript → types → async and tooling → typed AI apps | TypeScript Handbook; *typescript-exercises*; *type-challenges* | Type-safe exercises and a validated async boundary |
| [Computer science foundations](computer-science/README.md) | After Python foundations; pairs with Python for engineers | Cost models and Big-O → data structures → algorithm patterns → numbers and memory → processes, threads and I/O → networks | OSTEP, Erickson's *Algorithms*, MIT 6.042 notes, CPython source notes, RFCs and Goldberg; see its [references](computer-science/references.md) | Data structures, a stream decoder and an RFC 6298 timer built against tests, and every timing in the notes reproducible |
| [Software design](software-design/README.md) | After Python for engineers | Readable code → refactoring → design principles → patterns → testing → debugging → Git, review and design docs | Authors' free writing, papers and tool documentation; see its [references](software-design/references.md) | A smelly module refactored under tests, then extended |
| [Backend and system design](backend-and-system-design/README.md) | After computer science foundations; pairs with software design | API design → auth → caching and queues → load balancing and rate limiting → estimation and scaling → containers and deployment → reliability under load → design walkthroughs → AI system reference architecture | RFCs, OWASP, the Google SRE book, project docs and published papers; see its [references](backend-and-system-design/references.md) | A rate limiter, single-flight cache, JWT verifier, lease scheduler, small LSM store and token budget built against tests, and a container that drains correctly on SIGTERM |

The tracks deliberately overlap. Python gives SQL and TypeScript their programming vocabulary; SQL sharpens the data model before [Data Analytics](../data-analytics/README.md); Python plus TypeScript prepares you for [AI Engineering](../ai-engineering/README.md).

### [Python](python/README.md)

**Purpose:** Move from first programs to the idioms used in reliable Python services and data tooling. The track ends at the language boundary; pandas begins in [Data Analytics 01](../data-analytics/01-python-for-data-analysis/README.md).

**Learning objectives.** After this track, you can:

1. Write functions that return useful values, choose appropriate built-in collections, and handle ordinary control flow and files ([Severance](https://www.py4e.com/book/)).
2. Extract and validate information from text, HTTP responses, JSON/XML, and a SQLite database.
3. Reason about names, objects, iteration, errors, resource lifetimes, and common Python traps ([Python documentation](https://docs.python.org/3/)).
4. Use type hints, dataclasses, tests, linting, packaging, and boundary validation in a small package.
5. Choose threads, asyncio, or processes for a workload and apply timeouts and concurrency limits.

| Unit | Focus | Practice |
|---|---|---|
| [01 Foundations](python/README.md) | Control flow, functions, strings, files and collections | [Exercises](python/01-foundations/practice/exercises/) |
| [02 Informatics](python/README.md) | Text, the web, structured data, objects and databases | [Exercises](python/02-informatics/practice/exercises/) |
| [03 Language for engineers](python/README.md) | The data model, types, errors, packaging and concurrency | [Exercises](python/03-language-for-engineers/practice/exercises/) |

**Review and practice:** [foundations deck](python/01-foundations/slides/python-foundations.pptx) · [informatics deck](python/02-informatics/slides/python-informatics.pptx) · [engineering deck](python/03-language-for-engineers/slides/python-for-engineers.pptx) · module exercises and worked solutions.

**Mastery lab:** Create a small typed Python package that reads structured input, validates it at the boundary, uses a resource safely, returns useful errors, and has tests for its core behavior. Add bounded concurrent work only where it improves the design.

**Evidence:** Your own solutions pass [`python/check.sh`](python/check.sh); the lab includes a `pyproject.toml`, typed public functions, tests, and a short explanation of its error and concurrency choices.

**Key sources:** Severance, [*Python for Everybody*](https://www.py4e.com/book/) · VanderPlas, [*A Whirlwind Tour of Python*](https://github.com/jakevdp/WhirlwindTourOfPython) · [Python documentation](https://docs.python.org/3/) · [uv](https://docs.astral.sh/uv/), [Ruff](https://docs.astral.sh/ruff/), [pytest](https://docs.pytest.org/), and [Pydantic](https://docs.pydantic.dev/).

**Next:** [Data Analytics 01](../data-analytics/01-python-for-data-analysis/README.md) for pandas and tabular work; SQL for relational querying; TypeScript after the engineering unit.

### [SQL](sql/README.md)

**Purpose:** Learn to ask, verify, and change questions of relational data safely, from a first `SELECT` to query plans and a real investigation.

**Learning objectives.** After this track, you can:

1. Write clear `SELECT`, filtering, ordering, expression, aggregation, and conditional-aggregation queries ([Software Carpentry](https://swcarpentry.github.io/sql-novice-survey/)).
2. Reason correctly about `NULL`, dates, strings, and three-valued logic.
3. Choose joins, subqueries, CTEs, recursion, and window functions without changing a result's grain accidentally.
4. Design tables with constraints, perform safe changes in transactions, and use parameterised SQL from Python.
5. Read a query plan, write sargable predicates, and select indexes appropriate to a query ([Winand](https://use-the-index-luke.com/)).

| Unit | Focus | Practice |
|---|---|---|
| [Core querying](sql/README.md) | Selection, nulls, aggregation, joins and CTEs | [Exercises](sql/practice/exercises/) |
| [Analytical and operational SQL](sql/README.md) | Window functions, schema changes, query plans and SQL from Python | [Exercises](sql/practice/exercises/) |
| [Capstone](sql/README.md) | SQL Murder Mystery investigation | [Practice data](sql/practice/) |

**Review and practice:** [SQL deck](sql/slides/sql.pptx) · offline SQL/Python exercises and solutions · the capstone investigation.

**Mastery lab:** Solve the capstone with a query trail that another person can reproduce. Add one analytical query using a window function and one safe data-change or parameterised Python example, explaining grain, `NULL` behavior, and validation checks.

**Evidence:** Your queries pass [`sql/practice/check.sh`](sql/practice/check.sh). The capstone includes the answer, the queries that establish it, and a short explanation of why each join cannot fan out the result.

**Key sources:** [Software Carpentry: Databases and SQL](https://swcarpentry.github.io/sql-novice-survey/) · [PGExercises](https://pgexercises.com/) · [SQL Murder Mystery](https://github.com/NUKnightLab/sql-mysteries) · [Use The Index, Luke](https://use-the-index-luke.com/) · [SQLite documentation](https://sqlite.org/lang.html).

**Next:** [Data Analytics](../data-analytics/README.md) for analytical interpretation and pandas; [Data Engineering](../data-engineering/README.md) for data systems and pipelines.

### [TypeScript](typescript/README.md)

**Purpose:** Move from JavaScript fluency to a strict type system, safe runtime boundaries, and the async patterns required in typed applications and AI integrations.

**Learning objectives.** After this track, you can:

1. Translate Python habits into idiomatic JavaScript while avoiding coercion, sorting, and truthiness traps.
2. Model application data with interfaces, types, unions, narrowing, generics, and type transformations ([TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)).
3. Configure a strict TypeScript project, describe modules, and make type-level guarantees executable through tests.
4. Write async work with timeouts, retries, parallelism, and concurrency limits.
5. Validate environment variables, JSON, and model output at runtime rather than trusting erased types ([Zod](https://zod.dev)).
6. Build a typed tool-loop or streaming AI integration that narrows content blocks and handles stop reasons safely.

| Unit | Focus | Practice |
|---|---|---|
| [JavaScript and core types](typescript/README.md) | JavaScript for Python developers, everyday types, unions and narrowing | [Type exercises](typescript/practice/typescript-exercises/) |
| [Type-level design](typescript/README.md) | Generics and transformations from types | [Exercises and type challenges](typescript/practice/) |
| [Production boundaries](typescript/README.md) | Async, modules and tooling, runtime validation, TypeScript for AI apps | [Runtime exercises](typescript/practice/exercises/) |

**Review and practice:** [TypeScript deck](typescript/slides/typescript.pptx) · vendored type exercises and challenges · runtime exercises with tests. The live SDK example is optional and requires its own key; it is not required for mastery.

**Mastery lab:** Build a small strict TypeScript boundary: parse untrusted input with Zod, model outcomes as a discriminated union, run independent work concurrently with a limit and timeout, and test success and failure paths. An optional extension can call a model or tool API.

**Evidence:** The implementation and its tests pass [`npm run check`](typescript/practice/package.json); explain the runtime boundary and how the union makes an unhandled outcome impossible to ignore.

**Key sources:** [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) · [typescript-exercises](https://github.com/typescript-exercises/typescript-exercises) · [type-challenges](https://github.com/type-challenges/type-challenges) · [Zod](https://zod.dev) · [Anthropic TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript).

**Next:** [AI Engineering](../ai-engineering/README.md) for production LLM systems, or [Generative AI](../generative-ai/README.md) for LLM foundations and applications.

### [Computer science foundations](computer-science/README.md)

**Purpose:** The university-level ideas behind the Python you write, and how to reason about making it faster. Math is taught where it's used. Like software design, its notes follow the full chapter standard.

**Evidence:** Build the [lab](computer-science/practice/README.md)'s array, hash table, LRU cache, compensated sum, frame decoder and retransmission timer against their tests, and explain a slow request by counting its round trips and its costs.

**Next:** [Software design](software-design/README.md). The reading order and sources are in the [track README](computer-science/README.md).

### [Software design](software-design/README.md)

**Purpose:** Keep code cheap to change: read it, refactor it, test it, debug it, and work on it with other people. Unlike the language tracks, its notes follow the full chapter standard.

**Evidence:** Take the [lab](software-design/practice/README.md)'s module through refactoring under tests, then add a feature, and say honestly whether the refactoring made the feature cheaper.

**Next:** Apply it in any later course. The reading order and sources are in the [track README](software-design/README.md).

### [Backend and system design](backend-and-system-design/README.md)

**Purpose:** How a service holds up with real users: API contracts, identity, caches and queues, balancing and limits, capacity sums, deployment and behaviour under load, then five design walkthroughs and a reference architecture for an AI system. Like software design, its notes follow the full chapter standard.

**Evidence:** Build the [lab](backend-and-system-design/practice/README.md)'s modules against their tests, size a design from computed numbers, and say for every box on your diagram what happens to a request if it is slow, down, or running twice.

**Next:** [Storage and compute foundations](../data-engineering/01-storage-and-compute-foundations/README.md) for what's underneath a store. The reading order and sources are in the [track README](backend-and-system-design/README.md).

## Completion standard and further practice

Complete the Python track before moving to data or AI work. Take SQL when you will query or model data; take TypeScript when you will build typed applications. A complete programming foundation includes a passing Python exercise set and package, checked SQL exercises and capstone, and passing TypeScript checks plus a validated asynchronous boundary.

For timed or interview-format practice, use [the practice drills](../practice/drills/README.md).

## Study decks

One deck per Python module and one per other track. Each slide is a flashcard in librarian: the
title is the question and the takeaway is the rule that answers it. Rebuild one with
`make slides PILLAR=programming/sql`.

| Deck | Source |
|---|---|
| [Python foundations](python/01-foundations/slides/python-foundations.pptx) | [deck.yaml](python/01-foundations/slides/deck.yaml) |
| [Python informatics](python/02-informatics/slides/python-informatics.pptx) | [deck.yaml](python/02-informatics/slides/deck.yaml) |
| [Python for engineers](python/03-language-for-engineers/slides/python-for-engineers.pptx) | [deck.yaml](python/03-language-for-engineers/slides/deck.yaml) |
| [SQL](sql/slides/sql.pptx) | [deck.yaml](sql/slides/deck.yaml) |
| [TypeScript](typescript/slides/typescript.pptx) | [deck.yaml](typescript/slides/deck.yaml) |

## Running the code

Every practice set and script, with what it needs. The track READMEs give the full commands.

| Practice set | Runs | Command |
|---|---|---|
| Python exercise and solution files | Offline: Python 3.12+, standard library | `python3 practice/exercises/<file>.py` (each file runs its own `assert`s) |
| Python 03 · 06 package (`06_tooling/`) | Needs `uv`; the first run downloads pytest and ruff into a local `.venv/` | `uv run pytest` inside the package |
| [`python/check.sh`](python/check.sh) | Offline after that first `uv` run: it runs every exercise file, then `uv run pytest` for 06 | `bash check.sh`, `bash check.sh solutions`, `bash check.sh exercises 03` |
| Python for data (hand-off) | Moved to [data-analytics 01](../data-analytics/01-python-for-data-analysis/README.md), which owns the notebooks, the McKinney chapters, `courses/` and [`fetch_data.sh`](../data-analytics/01-python-for-data-analysis/practice/fetch_data.sh) (clones ~240 MB from wesm/pydata-book) | See that pillar's README |
| SQL exercise and solution files | Offline: `sqlite3` CLI (bundled with macOS); `survey.db` is committed, `clubdata.db` is built locally by `setup.sh` | `sqlite3 data/survey.db < exercises/<file>.sql`; `python3 exercises/09_sql_from_python.py` |
| [`sql/practice/setup.sh`](sql/practice/setup.sh) | Needs download on first run: fetches `sql-murder-mystery.db` (3.6 MB) with `curl`; building `clubdata.db` is offline | `bash setup.sh` |
| [`sql/practice/check.sh`](sql/practice/check.sh) | Offline once `setup.sh` has run (it calls `setup.sh` itself if `clubdata.db` is missing) | `bash check.sh`, `bash check.sh exercises` |
| SQL capstone | Needs the downloaded `sql-murder-mystery.db` | `sqlite3 data/sql-murder-mystery.db` |
| TypeScript exercises, tests, vendored `typescript-exercises/` and `type-challenges/`, [`check.ts`](typescript/practice/check.ts) | Needs Node 22.18+ (runs `.ts` directly, no build step) and one `npm install` (downloads TypeScript 7, zod, `@types/node`, the Anthropic SDK into the gitignored `node_modules/`) | `cd typescript/practice && npm install && npm run check` |
| TypeScript live example [`examples/claude.ts`](typescript/practice/examples/claude.ts) | Needs an API key (`ANTHROPIC_API_KEY`); exits cleanly without one | `node examples/claude.ts` |
| [`computer-science/practice/check.sh`](computer-science/practice/check.sh) | Needs `uv` and Python 3.14; the first run downloads pytest, numpy and `python3.14t`. Runs the lab's tests and every code block in the notes. Network blocks are opt-in | `bash check.sh`, `bash check.sh exercises`, `bash check.sh network` |
| [`backend-and-system-design/practice/check.sh`](backend-and-system-design/practice/check.sh) | Needs `uv` and Python 3.14; the container checks also need Docker, and print a skip without it. Runs the lab's tests and every code block in the notes | `bash check.sh`, `bash check.sh exercises` |

## Primary texts

- Severance, *Python for Everybody*: topic order for Python 01 and 02, paraphrased
- VanderPlas, *A Whirlwind Tour of Python*: Python
- [Python documentation](https://docs.python.org/3/): the language features in Python 03
- Software Carpentry, *Databases and SQL*: the structure of the SQL track
- PGExercises: SQL exercise themes and data
- Winand, *Use The Index, Luke*: background for indexes and query plans
- TypeScript Handbook, with *typescript-exercises* and *type-challenges* as practice
- Ramalho, *Fluent Python*: further reading for Python 03
- Computer science foundations: the [track's primary texts](computer-science/README.md#primary-texts)
- Software design: the [track's primary texts](software-design/README.md#primary-texts)
- Backend and system design: the [track's primary texts](backend-and-system-design/README.md#primary-texts)
- McKinney, *Python for Data Analysis*: where the path goes next, in [data-analytics 01](../data-analytics/01-python-for-data-analysis/README.md)

Everything else, with licences: [references.md](references.md). Each track README also maps sources directly to its notes.
