---
origin: curated
sources:
  - "Jake VanderPlas, A Whirlwind Tour of Python — https://github.com/jakevdp/WhirlwindTourOfPython (CC0)"
  - "Python docs, itertools — https://docs.python.org/3/library/itertools.html"
concepts: [python-iterators, python-generators, python-comprehensions, python-itertools, python-lazy-evaluation]
cleaned: 2026-10-29
---
# 2 — Iterators, generators and comprehensions

> An iterator hands out values one at a time and remembers where it is. A generator is the easiest way to write one. Laziness lets you process a 10 GB log file in constant memory.

---

## The iteration protocol

```python
it = iter([10, 20])   # calls __iter__
next(it)              # 10
next(it)              # 20
next(it)              # raises StopIteration — the for loop catches this for you
```

An **iterable** can produce an iterator (`list`, `dict`, `str`, files). An **iterator** is single-use: once exhausted, it stays empty. That is why looping twice over a generator or a `map` object silently yields nothing the second time.

## Comprehensions

```python
squares = [x * x for x in range(10)]
evens   = [x for x in nums if x % 2 == 0]
lookup  = {u["id"]: u for u in users}
letters = {c.lower() for c in text if c.isalpha()}
total   = sum(x * x for x in range(10**6))   # generator expression: no list built
```

Read them left to right as the loop they replace. Stop at two `for` clauses; beyond that a plain loop is clearer.

## Generators

```python
def read_records(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                yield line.rstrip("\n").split(",")

def take(n, it):
    for i, x in enumerate(it):
        if i == n:
            return
        yield x
```

- A function with `yield` returns a generator object. Its body runs only as values are requested, pausing at each `yield`.
- Chain them into a pipeline: `parse(filter(read(path)))`. Each stage holds one item at a time.
- `yield from other` delegates to another iterable.
- The `with` block stays open until the generator finishes or is garbage-collected. Consume it fully, or the file stays open longer than you expect.

## itertools: the parts you'll use

| Function | Does |
|---|---|
| `islice(it, n)` | First n items of any iterator |
| `chain(a, b)` / `chain.from_iterable(xs)` | Concatenate / flatten one level |
| `groupby(it, key)` | Group **consecutive** equal keys, so sort first |
| `batched(it, n)` (3.12+) | Tuples of n |
| `pairwise(it)` | `(a, b), (b, c), …` |
| `accumulate(it)` | Running totals |
| `product`, `permutations`, `combinations` | Combinatorics |
| `count`, `cycle`, `repeat` | Infinite streams, so pair with `islice` or `zip` |

`collections` adds `Counter`, `defaultdict`, `deque` (fast at both ends, `maxlen` for a sliding window) and `namedtuple`.

---

## Exercises

[`practice/exercises/02_iteration.py`](../practice/exercises/02_iteration.py)
