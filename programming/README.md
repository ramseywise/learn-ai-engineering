# Programming

> Depth layer for the code everything else in this repo is written in. Three **languages** (Python, SQL, TypeScript), four **core** tracks on engineering with them (computer science foundations, software design, backend and system design, frontend and UX), and **practice**: timed drills in [`drills/`](drills/README.md), linked from the step of each track they belong to.
>
> Position in the path: the entry point, no prerequisites; next are [data-analytics](../data-analytics/README.md) and [ai-engineering](../ai-engineering/README.md).

## What it is

A self-paced course in the three languages an AI or data engineer writes every day, and in the engineering around them: what code costs, how to keep it cheap to change, how a service holds up under real users, and how to put an interface in front of a person. Each language track goes from first principles to the idioms you need in production code, as short notes followed by exercises you can run offline. Each core track is a set of full chapters with one lab. Every track README has the same syllabus table: one row per step, with what to study, the lab and drills that go with it, and the sources.

This repo started as a Python learning repo built from *Python for Informatics* (now *Python for Everybody*) and McKinney's *Python for Data Analysis*. The Python track keeps the first of those as its spine and adds a module on the language features that engineering code relies on. The pandas half now has its own home: when Python 03 is done, the path hands off to [data-analytics 01, Python for data analysis](../data-analytics/01-python-for-data-analysis/README.md).

Notes use `concepts:` slugs in their frontmatter. Drills list the same slugs, so a drill can link back to the note that teaches it.

## Course outcomes

By the end of the course, you can:

1. Write readable, tested Python programs that work with files, structured data, databases, packages, types, and concurrency.
2. Query, model, and change relational data safely; inspect a query plan and use SQL from Python.
3. Build strict, maintainable TypeScript programs with runtime validation, asynchronous control flow, and typed AI boundaries.
4. Read, test, and improve the Python and TypeScript examples used by the data and AI-engineering courses.
5. Say what a piece of code costs in time and memory, and where a request's time goes across the process, the operating system and the network.
6. Refactor code under tests, choose a testing strategy, debug by hypothesis, and work with others through Git, review and design docs.
7. Take a backend design from requirements to failure modes, with the contract, identity, caches, queues, limits, capacity and deployment worked out in numbers.
8. Build an accessible interface, including a streaming AI interface that shows citations, uncertainty, failure and handoff honestly.

## Before you begin

There are no programming prerequisites. You need a terminal, Python 3.12+, the `sqlite3` CLI, and Node 22.18+ for the parts you choose to take. Start with Python 01. Begin SQL after Python 01; begin TypeScript after Python 03, when types and asynchronous work have context. The core tracks all start after Python 03. Computer science foundations and software design need nothing else. Backend and system design also needs SQL 07 and 08 and the transactions note in data engineering 01. Frontend and UX needs TypeScript.

## How to use the course

| Activity | What you do | What it demonstrates |
|---|---|---|
| Notes | Read a module in sequence and reproduce its small examples. | You understand the language rule and its trade-off. |
| Deck review | Use the module or track deck as a recall prompt. | You can state the rule without copying code. |
| Exercises | Implement the stubs before reading worked solutions. | You can apply the idea in a constrained problem. |
| Checks | Run the track's test/check command. | Your code meets the executable specification. |
| Drills | Use the drills in a syllabus row's Labs cell after that step. | You can retrieve the skill under time pressure. |

## Tracks

Seven tracks in two groups, and one practice bank. Languages come first because the core tracks are written in them.

## Languages

| Track | Recommended entry | Main units | Built from | Primary evidence |
|---|---|---|---|---|
| [Python](python/README.md) | Start here | Foundations → informatics → idioms → production habits → the runtime, then a hand-off to [data-analytics 01](../data-analytics/01-python-for-data-analysis/README.md) | Severance, *Python for Everybody* (paraphrased); VanderPlas, *A Whirlwind Tour of Python*; Python documentation | Passing exercises and a small tested package |
| [SQL](sql/README.md) | After Python foundations | Query → combine → design and tune → use from Python, with a capstone | Software Carpentry *Databases and SQL*; PGExercises; Knight Lab *SQL Murder Mystery* | Checked queries and an investigative capstone |
| [TypeScript](typescript/README.md) | After Python for engineers | JavaScript and core types → type-level design → production boundaries | TypeScript Handbook; *typescript-exercises*; *type-challenges* | Type-safe exercises and a validated async boundary |

## Core

| Track | Recommended entry | Main units | Built from | Primary evidence |
|---|---|---|---|---|
| [Computer science foundations](computer-science/README.md) | After Python 03 (builds on its concurrency, objects and MRO, and memory notes) | Reasoning about code (cost models, data structures, algorithm patterns) → the machine underneath (numbers and memory, processes and I/O, networks) | OSTEP, Erickson's *Algorithms*, MIT 6.042 notes, CPython source notes, RFCs and Goldberg; see its [references](computer-science/references.md) | Data structures, a stream decoder and an RFC 6298 timer built against tests, and every timing in the notes reproducible |
| [Software design](software-design/README.md) | After Python 03 | Writing code that can change → knowing that it works → working with other people | Authors' free writing, papers and tool documentation; see its [references](software-design/references.md) | A smelly module refactored under tests, then extended |
| [Backend and system design](backend-and-system-design/README.md) | After SQL 07 and 08 and the transactions note in data engineering 01; computer science 05 and 06 and software design 05 and 06 help | The contract and who may use it → the building blocks → sums and shipping → whole designs | RFCs, OWASP, the Google SRE book, project docs and published papers; see its [references](backend-and-system-design/references.md) | A rate limiter, single-flight cache, JWT verifier, lease scheduler, small LSM store and token budget built against tests, and a container that drains correctly on SIGTERM |
| [Frontend and UX](frontend-and-ux/README.md) | After TypeScript | The platform → people → AI interfaces | MDN, WHATWG, W3C, react.dev, Nielsen Norman Group, People + AI Guidebook and papers; see its [references](frontend-and-ux/references.md) | A streaming chat UI with citations, uncertain, error and handoff states, passing browser tests against a local mock server |

## Practice

| Track | Recommended entry | Main units | Built from | Primary evidence |
|---|---|---|---|---|
| [Drills](drills/README.md) | After the step that teaches the skill: each track's syllabus row names its drills | Python, SQL and TypeScript drills, coding prompts, algorithm and system design problems, tooling | Collected and written problems; see [its README](drills/README.md) | A drill solved under time, without the worked answer open |

## Track guides

The tracks deliberately overlap. Python gives SQL and TypeScript their programming vocabulary; SQL sharpens the data model before [Data Analytics](../data-analytics/README.md); Python plus TypeScript prepares you for [AI Engineering](../ai-engineering/README.md).

### [Python](python/README.md)

**Purpose:** Move from first programs to the idioms used in reliable Python services and data tooling. The track ends at the language boundary; pandas begins in [Data Analytics 01](../data-analytics/01-python-for-data-analysis/README.md).

**Learning objectives.** After this track, you can:

1. Write functions that return useful values, choose appropriate built-in collections, and handle ordinary control flow and files ([Severance](https://www.py4e.com/book/)).
2. Extract and validate information from text, HTTP responses, JSON/XML, and a SQLite database.
3. Reason about names, objects, iteration, errors, resource lifetimes, and common Python traps ([Python documentation](https://docs.python.org/3/)).
4. Use type hints, dataclasses, tests, linting, packaging, and boundary validation in a small package.
5. Choose threads, asyncio, or processes for a workload and apply timeouts and concurrency limits.
6. Predict attribute lookup and the MRO, and reason about refcounting, the garbage collector and what lives in memory at runtime.

| Unit | Focus | Practice |
|---|---|---|
| [1 Foundations](python/README.md#syllabus) | Control flow, functions, strings, files and collections | [Exercises](python/01-foundations/practice/exercises/01_values_and_conditionals.py) |
| [2 Informatics](python/README.md#syllabus) | Text, the web, structured data, objects and databases | [Exercises](python/02-informatics/practice/exercises/01_regex.py) |
| [3 Idioms](python/README.md#syllabus) | The data model, iteration, closures and decorators, errors and context managers | [Exercises](python/03-language-for-engineers/practice/exercises/01_data_model.py) |
| [4 Production habits](python/README.md#syllabus) | Types and dataclasses, packaging and tooling, concurrency | [Exercises](python/03-language-for-engineers/practice/exercises/05_types.py) · [advanced Python drills](drills/python/advanced/README.md) |
| [5 The runtime](python/README.md#syllabus) | Objects and the MRO, memory and the runtime | [Exercise](python/03-language-for-engineers/practice/exercises/08_objects_mro.py) · [advanced Python drills](drills/python/advanced/README.md) |

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
| [1 Query](sql/README.md#syllabus) | Selection, nulls and expressions, aggregation | [Exercises](sql/practice/exercises/01-select-and-filter.sql) |
| [2 Combine](sql/README.md#syllabus) | Joins, subqueries and CTEs, window functions | [Exercises](sql/practice/exercises/04-joins.sql) · [window-functions drill](drills/sql/window-functions/top-orders-per-user.md) |
| [3 Design and tune](sql/README.md#syllabus) | Tables, constraints and safe changes, indexes and query plans | [Exercises](sql/practice/exercises/07-modeling-and-ddl.sql) · [index quiz](drills/mcq/quiz1.md) |
| [4 Use](sql/README.md#syllabus) | SQL from Python, and the SQL Murder Mystery capstone | [Exercise](sql/practice/exercises/09_sql_from_python.py) · [setup and data](sql/practice/setup.sh) |

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
| [1 JavaScript and core types](typescript/README.md#syllabus) | JavaScript for Python developers, everyday types, unions and narrowing | [Type exercises](typescript/practice/typescript-exercises/01/index.ts) |
| [2 Type-level design](typescript/README.md#syllabus) | Generics and transformations from types | [Exercises and type challenges](typescript/practice/type-challenges/challenges/00004-easy-pick.ts) · [typed `groupBy` drill](drills/typescript/types/group-by.md) |
| [3 Production boundaries](typescript/README.md#syllabus) | Async, modules and tooling, runtime validation, TypeScript for AI apps | [Runtime exercises](typescript/practice/exercises/06-async.ts) · [ESLint drill](drills/typescript/eslint.md) |

**Review and practice:** [TypeScript deck](typescript/slides/typescript.pptx) · vendored type exercises and challenges · runtime exercises with tests. The live SDK example is optional and requires its own key; it is not required for mastery.

**Mastery lab:** Build a small strict TypeScript boundary: parse untrusted input with Zod, model outcomes as a discriminated union, run independent work concurrently with a limit and timeout, and test success and failure paths. An optional extension can call a model or tool API.

**Evidence:** The implementation and its tests pass [`npm run check`](typescript/practice/package.json); explain the runtime boundary and how the union makes an unhandled outcome impossible to ignore.

**Key sources:** [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) · [typescript-exercises](https://github.com/typescript-exercises/typescript-exercises) · [type-challenges](https://github.com/type-challenges/type-challenges) · [Zod](https://zod.dev) · [Anthropic TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript).

**Next:** [Frontend and UX](frontend-and-ux/README.md) to put a typed program in front of a person; [AI Engineering](../ai-engineering/README.md) for production LLM systems, or [Generative AI](../generative-ai/README.md) for LLM foundations and applications.

### [Computer science foundations](computer-science/README.md)

**Purpose:** The university-level ideas behind the Python you write, and how to reason about making it faster. Math is taught where it's used. Like software design, its notes follow the full chapter standard.

**Learning objectives.** After this track, you can:

1. Count work with sums and recurrences, state a Big-O claim properly, and budget a request.
2. Explain how CPython's `list` and `dict` work, and choose a data structure by what its operations cost.
3. Recognise the common algorithm patterns and argue that they are correct.
4. Predict float error and explain why data layout changes speed by orders of magnitude.
5. Price a process, a thread and a system call, prevent races and deadlocks, and count the round trips in a cold request.

**Evidence:** Build the [lab](computer-science/practice/README.md)'s array, hash table, LRU cache, compensated sum, frame decoder and retransmission timer against their tests, and explain a slow request by counting its round trips and its costs.

**Next:** [Software design](software-design/README.md) or [backend and system design](backend-and-system-design/README.md), in either order. The syllabus and sources are in the [track README](computer-science/README.md#syllabus).

### [Software design](software-design/README.md)

**Purpose:** Keep code cheap to change: read it, refactor it, test it, debug it, and work on it with other people. Unlike the language tracks, its notes follow the full chapter standard.

**Learning objectives.** After this track, you can:

1. Name what is wrong with a function, and pin its behaviour with characterization tests before changing its structure.
2. Apply information hiding and deep modules, and argue both sides of SOLID, DRY and clean code.
3. Choose test sizes and doubles, and tell coverage from mutation score.
4. Debug by hypothesis, and read a profile and a flame graph.
5. Reason from Git's object model, review a change for design, and write a design doc or ADR when it is worth it.

**Evidence:** Take the [lab](software-design/practice/README.md)'s module through refactoring under tests, then add a feature, and say honestly whether the refactoring made the feature cheaper.

**Next:** [Backend and system design](backend-and-system-design/README.md), and apply it in any later course. The syllabus and sources are in the [track README](software-design/README.md#syllabus).

### [Backend and system design](backend-and-system-design/README.md)

**Purpose:** How a service holds up with real users: API contracts, identity, caches and queues, balancing and limits, capacity sums, deployment and behaviour under load, then five design walkthroughs and a reference architecture for an AI system. Like software design, its notes follow the full chapter standard.

**Learning objectives.** After this track, you can:

1. Say what each API method promises, make a write survive a retry, and check identity and access per object.
2. Stop a cache stampede, handle at-least-once delivery, and choose a balancing policy and a rate limiter.
3. Write a capacity estimate as a program, deploy a container that drains correctly, and stop a retry storm.
4. Run a design from requirements to failure modes, and place each part of an AI system.

**Evidence:** Build the [lab](backend-and-system-design/practice/README.md)'s modules against their tests, size a design from computed numbers, and say for every box on your diagram what happens to a request if it is slow, down, or running twice.

**Next:** [Frontend and UX](frontend-and-ux/README.md) for the part a person sees; [storage and compute foundations](../data-engineering/01-storage-and-compute-foundations/README.md) for what's underneath a store. The syllabus and sources are in the [track README](backend-and-system-design/README.md#syllabus).

### [Frontend and UX](frontend-and-ux/README.md)

**Purpose:** Enough of the browser, React, accessibility and usability for a backend, data or AI engineer to build a usable interface or judge one, then what AI interfaces need that ordinary ones don't: streaming, citations, uncertainty, handoff and failure. It's awareness depth, and its notes follow the full chapter standard.

**Learning objectives.** After this track, you can:

1. Pick the element that brings its behaviour for free, and model a screen as a function of state.
2. Do a ten-minute manual accessibility pass, and say what automated tools cannot see.
3. Review a screen with the usability heuristics and the three response-time limits.
4. Parse a stream and classify how it failed, check citations before showing them, show uncertainty honestly, and treat model output as untrusted.

**Evidence:** Build the [lab](frontend-and-ux/practice/README.md)'s stream parser, state machine and chat interface against their tests, then walk every scenario by keyboard and try it with a screen reader, which no script here can do.

**Next:** [Application patterns](../generative-ai/07-agentic-applications/notes/06-application-patterns.md). The syllabus and sources are in the [track README](frontend-and-ux/README.md#syllabus).

## Completion standard and further practice

Complete the Python track before moving to data or AI work. Take SQL when you will query or model data; take TypeScript when you will build typed applications. A complete language foundation includes a passing Python exercise set and package, checked SQL exercises and capstone, and passing TypeScript checks plus a validated asynchronous boundary. Each core track is complete when its lab passes its own checks and you can give the explanation its Evidence line asks for.

For timed or interview-format practice, use [the drills](drills/README.md). Each track's syllabus names the drills that go with a step, so do them after the lecture and notes they belong to.

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
| [Computer science foundations](computer-science/slides/computer-science.pptx) | [deck.yaml](computer-science/slides/deck.yaml) |
| [Software design](software-design/slides/software-design.pptx) | [deck.yaml](software-design/slides/deck.yaml) |
| [Backend and system design](backend-and-system-design/slides/backend-and-system-design.pptx) | [deck.yaml](backend-and-system-design/slides/deck.yaml) |
| [Frontend and UX](frontend-and-ux/slides/frontend-and-ux.pptx) | [deck.yaml](frontend-and-ux/slides/deck.yaml) |

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
| [`frontend-and-ux/practice/check.sh`](frontend-and-ux/practice/check.sh) | Needs Node 22.18+ and Chromium for Playwright, no API key. Runs the type check, unit and browser tests, axe, planted faults and every code block in the notes | `bash check.sh`, `bash check.sh exercises`, `bash check.sh no-browser` |

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
- Frontend and UX: the [track's primary texts](frontend-and-ux/README.md#primary-texts)
- McKinney, *Python for Data Analysis*: where the path goes next, in [data-analytics 01](../data-analytics/01-python-for-data-analysis/README.md)

Everything else, with licences: [references.md](references.md). Each track README also maps sources directly to its notes.
