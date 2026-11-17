# Python

Go from your first `if` to async, typed, tested code. Five steps across three modules: the *Python for Everybody* spine (01 and 02) and the language features that engineering code relies on (03). Each note is short and ends in exercises that check themselves.

**What you should already know.** Nothing: this is the entry point of the course. One note, [02 · 05 databases](02-informatics/notes/05-databases.md), borrows joins and upsert from the [SQL track](../sql/README.md) and links the two notes it needs.

## Lecture

One deck per module, on the same examples as the notes: [Python foundations](01-foundations/slides/python-foundations.pptx) ([PDF](01-foundations/slides/python-foundations.pdf)) for step 1, [Python informatics](02-informatics/slides/python-informatics.pptx) ([PDF](02-informatics/slides/python-informatics.pdf)) for step 2, and [Python for engineers](03-language-for-engineers/slides/python-for-engineers.pptx) ([PDF](03-language-for-engineers/slides/python-for-engineers.pdf)) for steps 3 to 5. Librarian turns each slide into a flashcard: the title is the question and the takeaway is the rule that answers it.

## The core

This track teaches the language and stops there. Pandas and the scientific stack start in [data-analytics 01](../../data-analytics/01-python-for-data-analysis/README.md), and the ideas underneath the language (cost, memory, the operating system) are in [computer science foundations](../computer-science/README.md). The question it keeps asking is: **what does this line do, and to which object?** Most Python surprises are answers to it: a default list shared between calls, a function that prints where it should return, a file left open, a coroutine that was never awaited.

There are five steps. The first two get you writing programs that read real text and data. The last three are the same language seen the way production code uses it: its idioms, the habits that keep a package maintainable, and the runtime underneath.

## Syllabus

One row per step. **Core concepts** are the ideas the step turns on, **Study** is what to read, **Labs** is what to do afterwards (the track's own exercises first, then the drills on the same topic), and **Sources** is where to read more. How to run the labs: [practice/README.md](practice/README.md).

| Submodule | Core concepts | Study | Labs | Sources |
|---|---|---|---|---|
| **1. Foundations:** first programs | Values have types, and conversion is explicit. A function returns a value; printing is for the edge of the program. Most loops are one of four patterns: count, sum, find the largest, search. Pick the collection by how you will look things up. | [1 Values and conditionals](01-foundations/notes/01-values-and-conditionals.md) · [2 Functions](01-foundations/notes/02-functions.md) · [3 Loops](01-foundations/notes/03-loops.md) · [4 Strings and files](01-foundations/notes/04-strings-and-files.md) · [5 Collections](01-foundations/notes/05-collections.md) | Exercises [01](01-foundations/practice/exercises/01_values_and_conditionals.py) · [02](01-foundations/practice/exercises/02_functions.py) · [03](01-foundations/practice/exercises/03_loops.py) · [04](01-foundations/practice/exercises/04_strings_and_files.py) · [05](01-foundations/practice/exercises/05_collections.py) | Severance, [*Python for Everybody*](https://www.py4e.com/book): topic order, paraphrased |
| **2. Informatics:** text, the web and a database | A regular expression extracts with groups. An HTTP response is a status, headers and a body, and you check the status. JSON is nested dictionaries and lists. A class keeps data valid at the point it is made. Values reach SQL as `?` parameters. | [1 Regular expressions](02-informatics/notes/01-regular-expressions.md) · [2 Networks and HTTP](02-informatics/notes/02-network-and-http.md) · [3 Web data](02-informatics/notes/03-web-data-json-xml.md) · [4 Objects](02-informatics/notes/04-objects.md) · [5 Databases](02-informatics/notes/05-databases.md) | Exercises [01](02-informatics/practice/exercises/01_regex.py) · [02](02-informatics/practice/exercises/02_http.py) · [03](02-informatics/practice/exercises/03_web_data.py) · [04](02-informatics/practice/exercises/04_objects.py) · [05](02-informatics/practice/exercises/05_databases.py) | Severance, [*Python for Everybody*](https://www.py4e.com/book) |
| **3. Idioms:** the language as it is meant to be written | A name refers to an object, and assignment never copies. `None` is the default, never `[]`. Iterate lazily over anything that might be large. A decorator is a function that takes a function. Catch the narrowest exception you can handle, and use `with` for anything that must be released. | [1 The data model and idioms](03-language-for-engineers/notes/01-data-model-and-idioms.md) · [2 Iterators and generators](03-language-for-engineers/notes/02-generators-and-iteration.md) · [3 Closures and decorators](03-language-for-engineers/notes/03-functions-deeper.md) · [4 Errors and context managers](03-language-for-engineers/notes/04-errors-and-context-managers.md) | Exercises [01](03-language-for-engineers/practice/exercises/01_data_model.py) · [02](03-language-for-engineers/practice/exercises/02_iteration.py) · [03](03-language-for-engineers/practice/exercises/03_functions.py) · [04](03-language-for-engineers/practice/exercises/04_errors.py) · drills: [advanced Python](../drills/python/advanced/README.md), the functional idioms and resources sections | VanderPlas, [*A Whirlwind Tour of Python*](https://github.com/jakevdp/WhirlwindTourOfPython) · [Python documentation](https://docs.python.org/3/) |
| **4. Production habits:** types, tooling and concurrency | Type every signature, validate data at the boundary, and trust it afterwards. A package is a `pyproject.toml`, a `src/` layout and tests that run with one command. Threads and `asyncio` are for waiting, processes for CPU work, and every fan-out needs a limit and a timeout. | [5 Type hints and dataclasses](03-language-for-engineers/notes/05-types-and-dataclasses.md) · [6 Modules, packaging and tooling](03-language-for-engineers/notes/06-modules-packaging-tooling.md) · [7 Concurrency](03-language-for-engineers/notes/07-concurrency.md) | Exercises [05](03-language-for-engineers/practice/exercises/05_types.py) · [06, a package](03-language-for-engineers/practice/exercises/06_tooling/) · [07](03-language-for-engineers/practice/exercises/07_concurrency.py) · drills: [advanced Python](../drills/python/advanced/README.md), the concurrency and typing sections | [uv](https://docs.astral.sh/uv/), [Ruff](https://docs.astral.sh/ruff/), [pytest](https://docs.pytest.org/) and [Pydantic](https://docs.pydantic.dev/) docs · Iusztin and Labonne, *LLM Engineer's Handbook*, ch. 2 |
| **5. The runtime:** objects and memory | Attribute lookup follows the MRO, and `super()` follows it too. Prefer composition until a second behaviour exists, and avoid metaclasses. Memory is reference counts plus a cycle collector, and `tracemalloc` shows where it went. | [8 Objects, inheritance and the MRO](03-language-for-engineers/notes/08-objects-inheritance-and-mro.md) · [9 Memory and the runtime](03-language-for-engineers/notes/09-memory-and-the-runtime.md) | Exercise [08](03-language-for-engineers/practice/exercises/08_objects_mro.py) · note 9's Try it, kept in the note because its results depend on the machine · drills: [advanced Python](../drills/python/advanced/README.md), the memory and OOP sections | [Python documentation](https://docs.python.org/3/) · Ramalho, *Fluent Python*: further reading |

Worked answers are in each module's `practice/solutions/`. Try each exercise before you open them. The drills are a senior-interview concept list with runnable examples, not graded exercises: use them to test recall after the step. Timed problems are in [`programming/drills/`](../drills/README.md).

## Rules of thumb

- Functions **return** values. Printing is for the edge of the program.
- Use `with` for anything that must be closed or released: files, connections, locks.
- Catch the narrowest exception you can actually handle. Let the rest crash with a traceback.
- `None` as a default, never `[]` or `{}`.
- Values reach SQL as `?` parameters, never through f-strings.
- Type every function signature. Validate data from outside the program (Pydantic), and trust it afterwards.
- Iterate lazily (generators) over anything that might be large.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| None in other subjects | The entry point of the course |
| [SQL 04 Joins](../sql/notes/04-joins.md) and [SQL 07 upsert](../sql/notes/07-modeling-and-ddl.md#upsert) | Needed for [02 · 05 databases](02-informatics/notes/05-databases.md) only |

**Feeds into**

| Chapter | Why |
|---|---|
| [DA 01 Python for data analysis](../../data-analytics/01-python-for-data-analysis/README.md) | Pandas starts where this track ends |
| [SQL 09 SQL from Python](../sql/notes/09-sql-from-python.md) | Parameters, DuckDB and pandas, from the Python side of [databases](02-informatics/notes/05-databases.md) |
| [TypeScript](../typescript/README.md) | Starts after step 5; its [async](../typescript/notes/06-async.md) note leans on [concurrency](03-language-for-engineers/notes/07-concurrency.md) |
| [Computer science foundations](../computer-science/README.md) | Read after step 5: cost and memory arguments made on Python's own objects |
| [Software design](../software-design/README.md) | Refactoring and patterns written in Python |

## Primary texts

- Severance, *Python for Everybody*: topic order for modules 01 and 02, paraphrased
- VanderPlas, *A Whirlwind Tour of Python*
- Python documentation
- Ramalho, *Fluent Python*: further reading

Licences and what each source was used for:

| Source | License | Used for |
|---|---|---|
| Charles Severance, [*Python for Everybody*](https://www.py4e.com/book) (formerly *Python for Informatics*) | CC BY-NC-SA 3.0 | Structure and topics of 01–02. Notes are paraphrased and the exercises are written for this repo; no text or data is copied |
| Jake VanderPlas, [*A Whirlwind Tour of Python*](https://github.com/jakevdp/WhirlwindTourOfPython) | CC0 | 03 · 01–04 |
| [Python documentation](https://docs.python.org/3/) | PSF | 03 throughout |
| [uv](https://docs.astral.sh/uv/), [Ruff](https://docs.astral.sh/ruff/), [pytest](https://docs.pytest.org/), [Pydantic](https://docs.pydantic.dev/) docs | MIT / Apache-2.0 | 03 · 05–06 |
| Wes McKinney, *Python for Data Analysis*, 2nd ed. | Code and data MIT | The next pillar, [data-analytics 01](../../data-analytics/01-python-for-data-analysis/README.md) |
| Luciano Ramalho, *Fluent Python* | Proprietary | Further reading for 03, link only |
| Ben Wilson, *Machine Learning Engineering in Action* (Manning, 2022), ch. 10 | Proprietary | One-sentence examples in 03 · 01, 04 and 05; the longer treatment is in [software design](../software-design/README.md) |
| Iusztin and Labonne, *LLM Engineer's Handbook* (Packt, 2024), ch. 2 | Proprietary | Tooling comparison in 03 · 06 |

Everything else: [references.md](../references.md). Each deck is built from its module's `slides/deck.yaml` with `make slides PILLAR=programming/python/01-foundations`.

## Next

Start with step 1, **Foundations**: read [1 Values and conditionals](01-foundations/notes/01-values-and-conditionals.md), then do its exercise from the syllabus row.

This track stops at the language. After step 1 you can start [SQL](../sql/README.md). After step 5 the path hands off to [data-analytics 01](../../data-analytics/01-python-for-data-analysis/README.md), which owns pandas, the course notebooks and McKinney's chapter notebooks, and to [TypeScript](../typescript/README.md) if you will build typed applications.
