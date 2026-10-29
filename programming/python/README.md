# Python

> From your first `if` to async, typed, tested code, then on to pandas. Four modules: the
> *Python for Everybody* spine (01–02), the language features engineering code relies on (03), and
> Python for data (04).
> Jump to: [Modules](#modules) · [Setup](#setup) · [How exercises work](#how-exercises-work) · [Rules of thumb](#rules-of-thumb) · [Sources](#sources)

---

## Modules

### 01 — Foundations

| # | Note | You can… | Exercises |
|---|---|---|---|
| 01 | [Values, expressions and conditionals](01-foundations/notes/01-values-and-conditionals.md) | Use types, operators, `if`/`elif`, truthiness, `try` on bad input | [py](01-foundations/practice/exercises/01_values_and_conditionals.py) |
| 02 | [Functions](01-foundations/notes/02-functions.md) | Write functions that return rather than print, with defaults and docstrings | [py](01-foundations/practice/exercises/02_functions.py) |
| 03 | [Loops and loop patterns](01-foundations/notes/03-loops.md) | Count, sum, find the max, search, with `for`/`while`/`break` | [py](01-foundations/practice/exercises/03_loops.py) |
| 04 | [Strings and files](01-foundations/notes/04-strings-and-files.md) | Slice, search and format strings; read files line by line with `with` | [py](01-foundations/practice/exercises/04_strings_and_files.py) |
| 05 | [Lists, dictionaries and tuples](01-foundations/notes/05-collections.md) | Pick the right collection, count with dicts, sort by value | [py](01-foundations/practice/exercises/05_collections.py) |

### 02 — Informatics

| # | Note | You can… | Exercises |
|---|---|---|---|
| 01 | [Regular expressions](02-informatics/notes/01-regular-expressions.md) | Extract with groups, named groups, non-greedy matches | [py](02-informatics/practice/exercises/01_regex.py) |
| 02 | [Networks and HTTP](02-informatics/notes/02-network-and-http.md) | Fetch with `urllib`, handle status codes, parse links | [py](02-informatics/practice/exercises/02_http.py) |
| 03 | [Web data: JSON, XML and APIs](02-informatics/notes/03-web-data-json-xml.md) | Walk nested JSON, read XML, follow pagination | [py](02-informatics/practice/exercises/03_web_data.py) |
| 04 | [Objects](02-informatics/notes/04-objects.md) | Write classes with validation, inheritance, `__repr__`/`__eq__` | [py](02-informatics/practice/exercises/04_objects.py) |
| 05 | [Using databases from Python](02-informatics/notes/05-databases.md) | Normalise data into `sqlite3` tables, upsert, join | [py](02-informatics/practice/exercises/05_databases.py) |

### 03 — Language for engineers

| # | Note | You can… | Exercises |
|---|---|---|---|
| 01 | [The data model and idioms](03-language-for-engineers/notes/01-data-model-and-idioms.md) | Reason about names vs objects, avoid the mutable-default trap, implement dunders | [py](03-language-for-engineers/practice/exercises/01_data_model.py) |
| 02 | [Iterators, generators and comprehensions](03-language-for-engineers/notes/02-generators-and-iteration.md) | Write lazy pipelines, use `itertools` and `collections` | [py](03-language-for-engineers/practice/exercises/02_iteration.py) |
| 03 | [Functions, closures and decorators](03-language-for-engineers/notes/03-functions-deeper.md) | Write closures, decorators and decorator factories | [py](03-language-for-engineers/practice/exercises/03_functions.py) |
| 04 | [Errors and context managers](03-language-for-engineers/notes/04-errors-and-context-managers.md) | Design exception hierarchies, chain errors, write `with` managers | [py](03-language-for-engineers/practice/exercises/04_errors.py) |
| 05 | [Type hints and dataclasses](03-language-for-engineers/notes/05-types-and-dataclasses.md) | Type signatures, use Protocols, frozen dataclasses, Pydantic at boundaries | [py](03-language-for-engineers/practice/exercises/05_types.py) |
| 06 | [Modules, packaging and tooling](03-language-for-engineers/notes/06-modules-packaging-tooling.md) | Lay out a package with `pyproject.toml`; use uv, ruff and pytest | [package](03-language-for-engineers/practice/exercises/06_tooling/) |
| 07 | [Concurrency](03-language-for-engineers/notes/07-concurrency.md) | Choose threads vs asyncio vs processes, limit concurrency, add timeouts | [py](03-language-for-engineers/practice/exercises/07_concurrency.py) |

### 04 — Python for data

Seven course notebooks (arrays, DataFrames, plotting, aggregation, time series) plus McKinney's
chapter notebooks and earlier Michigan/Wesleyan coursework. See [04-python-for-data/README.md](04-python-for-data/README.md).

Worked answers are in each module's `practice/solutions/`. Try each exercise before you open them.

---

## Setup

```bash
cd programming/python
python3 --version                         # 3.12+ (the course is tested on 3.14)
python3 01-foundations/practice/exercises/01_values_and_conditionals.py
bash check.sh                             # ok / FAIL for every exercise
bash check.sh exercises 03                # one module
bash check.sh solutions                   # every worked answer must pass
```

01–03 need only the standard library. 03 · 06 is a small package run with [uv](https://docs.astral.sh/uv/)
(`uv run pytest`), which installs pytest and ruff for you. 04 needs the scientific stack. Its
README has a one-line `uv run` command for Jupyter.

---

## How exercises work

Every exercise file is a set of functions (or classes) whose docstrings start with `Q1.`, `Q2.` …
and whose bodies are `raise NotImplementedError`. The bottom of each file is a block of `assert`s
under `if __name__ == "__main__":`. Run the file: it stops at the first unsolved question, and it
prints `all good` once everything passes. Exercises run offline. The HTTP exercise starts its own
local server, and the concurrency exercise simulates the network with sleeps.

---

## Rules of thumb

- Functions **return** values. Printing is for the edge of the program.
- Use `with` for anything that must be closed or released: files, connections, locks.
- Catch the narrowest exception you can actually handle. Let the rest crash with a traceback.
- `None` as a default, never `[]` or `{}`.
- Values reach SQL as `?` parameters, never through f-strings.
- Type every function signature. Validate data from outside the program (Pydantic), and trust it afterwards.
- Iterate lazily (generators) over anything that might be large.

---

## Sources

| Source | License | Used for |
|---|---|---|
| Charles Severance, [*Python for Everybody*](https://www.py4e.com/book) (formerly *Python for Informatics*) | CC BY-NC-SA 3.0 | Structure and topics of 01–02. Notes are paraphrased and the exercises are written for this repo; no text or data is copied |
| Jake VanderPlas, [*A Whirlwind Tour of Python*](https://github.com/jakevdp/WhirlwindTourOfPython) | CC0 | 03 · 01–04 |
| [Python documentation](https://docs.python.org/3/) | PSF | 03 throughout |
| [uv](https://docs.astral.sh/uv/), [Ruff](https://docs.astral.sh/ruff/), [pytest](https://docs.pytest.org/), [Pydantic](https://docs.pydantic.dev/) docs | MIT / Apache-2.0 | 03 · 05–06 |
| Wes McKinney, *Python for Data Analysis*, 2nd ed. | Code and data MIT | 04 (see its README) |
| Luciano Ramalho, *Fluent Python* | Proprietary | Further reading for 03, link only |

Timed and interview-style Python problems are in [sisyphus `drills/`](https://github.com/ramseywise/sisyphus/blob/main/drills/README.md).
