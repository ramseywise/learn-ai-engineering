---
origin: curated
sources:
  - "Jake VanderPlas, A Whirlwind Tour of Python — https://github.com/jakevdp/WhirlwindTourOfPython (CC0)"
  - "Python docs, Errors and exceptions — https://docs.python.org/3/tutorial/errors.html"
  - "Ben Wilson, Machine Learning Engineering in Action (Manning, 2022), ch. 10 — chapter PDF in data-engineering/sources/ml-engineering-in-action/"
  - "Robert C. Martin, Clean Code (Prentice Hall, 2008), chapter 7 (error handling, by Michael Feathers: context in exceptions, wrapping a third-party API, special cases instead of null) — chapter PDF in programming/sources/martin-clean-code/"
  - "Python docs, contextlib — https://docs.python.org/3/library/contextlib.html"
concepts: [python-exceptions, python-custom-exceptions, python-context-managers, python-contextlib, python-logging]
cleaned: 2026-10-29
---
# 4 — Errors and context managers

> Catch what you can handle, let everything else crash loudly, and put cleanup in `with` or `finally` so it happens no matter what.

---

## try / except / else / finally

```python
try:
    cfg = json.loads(path.read_text())
except FileNotFoundError:
    cfg = {}                              # expected: fall back
except json.JSONDecodeError as err:
    raise ValueError(f"{path} is not valid JSON: {err}") from err
else:
    log.info("loaded %s", path)           # only if no exception
finally:
    ...                                   # always, even after return
```

- Catch the **narrowest** exception. A bare `except:` or `except Exception:` hides bugs like `NameError` and `KeyboardInterrupt` (bare only).
- `raise ... from err` keeps the original traceback as the cause. Use `raise` alone to re-raise unchanged.
- Keep the `try` block small: only the line that can fail, so you don't catch errors from code you didn't mean to guard.

### Blind catches hide wrong input

Wilson shows how a bare `except: pass` turns a caller's mistake into a plausible-looking result (*Machine Learning Engineering in Action*, ch. 10); the pattern is on the smell list in [readable code and smells](../../../software-design/notes/01-readable-code-and-smells.md), and the fix is the narrow catch and `log` call below.

## Your own exceptions

```python
class PipelineError(Exception):
    """Base for this package's errors."""

class SchemaError(PipelineError):
    def __init__(self, column: str, problem: str):
        super().__init__(f"{column}: {problem}")
        self.column = column
```

One base class per package lets callers write `except PipelineError` without catching everything else. Add fields for anything a caller might branch on, instead of making them parse the message.

`ExceptionGroup` and `except*` (3.11+) handle several failures at once, e.g. from `asyncio.TaskGroup` ([note 07](07-concurrency.md)).

### What the error should say, and what to return instead

Michael Feathers's chapter in *Clean Code* is written for Java and argues from examples, with no measurements, but most of it carries over.

- **Say what was being attempted.** "A stack trace can't tell you the intent of the operation that failed" (*Clean Code*, ch. 7, p. 107). The message should name the operation and the kind of failure, which is what the `ValueError` naming the path does in the first example.
- **Define exception classes by how callers catch them.** If every handler for a vendor library does the same thing, wrap the library and raise one type of your own. He calls wrapping third-party APIs "a best practice" (pp. 108-109) and says one class is often enough. In Python that's `raise PipelineError(...) from err` at the wrapper, and the [gateway](../../../software-design/notes/04-patterns-worth-knowing.md#adapter-and-gateway-confine-a-foreign-api) is where it goes.
- **Return a special case instead of making the caller branch.** His example returns an empty list where the code used to return null, so the loop needs no check (pp. 110-111). The Python version is returning `[]` or `{}` instead of `None` from a function whose callers iterate.
- **His "don't return null" and "don't pass null" rules** (pp. 110-112) carry over only in part. `None` for "absent" is ordinary Python (`dict.get`, `re.match`). The part to keep is to raise when absence is an error, and to write `X | None` in the signature when it isn't, so a type checker makes the caller handle it.

The chapter's case against checked exceptions needs no translation. Python has none, and Feathers cites that as evidence they aren't needed: "Neither do Python or Ruby. Yet it is possible to write robust software in all of these languages" (p. 106).

## Context managers

`with` guarantees cleanup: the file is closed, the lock released, the transaction committed or rolled back.

```python
with open(src) as fin, open(dst, "w") as fout:
    fout.write(fin.read())
```

Write your own with `contextlib.contextmanager`. Code before `yield` is setup, code after is teardown, and the `try/finally` makes teardown run on error:

```python
from contextlib import contextmanager
import os, time

@contextmanager
def timer(label: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {time.perf_counter() - start:.2f}s")

@contextmanager
def env(**values):
    old = {k: os.environ.get(k) for k in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
```

As a class, implement `__enter__` and `__exit__(exc_type, exc, tb)`. Returning `True` from `__exit__` swallows the exception, which is rarely what you want. Also useful: `contextlib.suppress(FileNotFoundError)`, `ExitStack` for a variable number of resources, and `tempfile.TemporaryDirectory()`.

## Logging, not print

```python
import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log.info("loaded %d rows from %s", n, path)     # lazy formatting
log.exception("upload failed")                  # inside except: adds the traceback
```

---

## Exercises

[`practice/exercises/04_errors.py`](../practice/exercises/04_errors.py)
