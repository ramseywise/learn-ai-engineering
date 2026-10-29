---
origin: curated
sources:
  - "Jake VanderPlas, A Whirlwind Tour of Python — https://github.com/jakevdp/WhirlwindTourOfPython (CC0)"
  - "Python docs, Errors and exceptions — https://docs.python.org/3/tutorial/errors.html"
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
