---
origin: curated
sources:
  - "Jake VanderPlas, A Whirlwind Tour of Python — https://github.com/jakevdp/WhirlwindTourOfPython (CC0)"
  - "Python docs, functools — https://docs.python.org/3/library/functools.html"
concepts: [python-closures, python-decorators, python-args-kwargs, python-first-class-functions, python-functools]
cleaned: 2026-10-29
---
# 3 — Functions, closures and decorators

> Functions are values: you can pass them, return them and store them. Closures let a function remember variables from where it was made. Decorators are just functions that wrap functions.

---

## Flexible signatures

```python
def call(model, /, *messages, temperature=1.0, **extra):
    ...
call("m", "hi", "there", temperature=0.2, top_k=5)
# model="m", messages=("hi", "there"), temperature=0.2, extra={"top_k": 5}
```

- Parameters before `/` are positional-only. Parameters after `*` or `*args` are keyword-only, which is a good default for flags like `temperature`.
- `f(*xs, **kw)` spreads a sequence and a dict into a call.

## Closures

```python
def counter():
    count = 0
    def inc():
        nonlocal count      # rebinding an outer variable needs nonlocal
        count += 1
        return count
    return inc

c = counter(); c(); c()     # 2
```

Classic trap: closures capture **variables, not values**. `[lambda: i for i in range(3)]` all return 2. Bind early with a default: `lambda i=i: i`.

## Decorators

```python
import functools, time

def timed(fn):
    @functools.wraps(fn)            # keep fn's name and docstring
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__} took {time.perf_counter() - start:.3f}s")
    return wrapper

@timed                              # same as: load = timed(load)
def load(path): ...
```

A decorator **with arguments** is a function that returns a decorator, so there is one more level:

```python
def retry(times: int):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except ConnectionError:
                    if attempt == times - 1:
                        raise
        return wrapper
    return decorate

@retry(times=3)
def fetch(url): ...
```

## functools you'll actually use

- `@functools.cache` / `@lru_cache(maxsize=…)`: memoise a pure function. The arguments must be hashable.
- `functools.partial(fn, x=1)`: pre-fill arguments, which is handy for callbacks.
- `functools.reduce`: usually a loop or `sum` / `max` reads better.
- `operator.itemgetter("score")` / `attrgetter("name")`: faster, clearer `key=` functions than lambdas.

---

## Exercises

[`practice/exercises/03_functions.py`](../practice/exercises/03_functions.py)
