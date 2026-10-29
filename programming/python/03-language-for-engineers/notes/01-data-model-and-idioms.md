---
origin: curated
sources:
  - "Jake VanderPlas, A Whirlwind Tour of Python — https://github.com/jakevdp/WhirlwindTourOfPython (CC0)"
  - "Python docs, Data model — https://docs.python.org/3/reference/datamodel.html"
concepts: [python-data-model, python-dunder-methods, python-mutability, python-idioms, python-unpacking]
cleaned: 2026-10-29
---
# 1 — The data model and idioms

> Everything in Python is an object with an identity, a type and a value. Names are labels stuck on objects, not boxes holding values. Most "weird" Python behaviour follows from that one fact.

---

## Names, identity and mutability

```python
a = [1, 2, 3]
b = a            # a second label on the SAME list
b.append(4)
a                # [1, 2, 3, 4]
a is b           # True: same object
a == [1, 2, 3, 4]  # True: equal value, different object
```

- `==` compares values (calls `__eq__`). `is` compares identity. Use `is` only for `None`, `True`, `False` and sentinels.
- **Mutable**: `list`, `dict`, `set`, most objects. **Immutable**: `int`, `float`, `str`, `tuple`, `frozenset`, `bytes`.
- Arguments are passed by assignment: the function gets another label on the caller's object. Mutating it is visible to the caller; rebinding it is not.

### The mutable default trap

```python
def add(item, bucket=[]):      # the [] is created ONCE, at def time
    bucket.append(item)
    return bucket

add(1); add(2)                 # [1, 2]  — shared between calls

def add(item, bucket=None):    # the fix
    bucket = [] if bucket is None else bucket
    ...
```

## Dunder methods: how syntax maps to methods

| You write | Python calls |
|---|---|
| `len(x)` | `x.__len__()` |
| `x[k]`, `x[k] = v` | `__getitem__`, `__setitem__` |
| `for i in x` | `iter(x)` → `__iter__`, then `__next__` |
| `a + b`, `a == b`, `a < b` | `__add__`, `__eq__`, `__lt__` |
| `if x:` | `__bool__`, else `__len__` |
| `with x:` | `__enter__`, `__exit__` |
| `x(...)` | `__call__` |
| `repr(x)`, `f"{x}"` | `__repr__`, `__str__` / `__format__` |

Implement `__len__` and `__getitem__` and your class already works with `len`, indexing, slicing (if you handle `slice`), `in` and `for`. That is the point of the data model: your objects plug into the language instead of inventing their own method names.

## Idioms worth having by reflex

```python
first, *rest = [1, 2, 3, 4]          # unpacking with a star
a, b = b, a                          # swap
for i, name in enumerate(names, 1):  # index without range(len(...))
for x, y in zip(xs, ys, strict=True):  # strict: lengths must match
counts = {}; counts[w] = counts.get(w, 0) + 1
best = max(rows, key=lambda r: r["score"])
if not items:                        # empty check, not len(items) == 0
value = config.get("port") or 8080   # careful: 0 and "" are falsy too
merged = {**defaults, **overrides}   # or defaults | overrides
```

- **EAFP** ("easier to ask forgiveness"): try the operation and catch the specific exception, rather than checking first. It avoids race conditions on files and dict lookups.
- `copy.copy` is shallow (new outer container, same inner objects). `copy.deepcopy` copies all the way down. `list(x)`, `x[:]` and `dict(x)` are shallow.

## Hashability

Dict keys and set members must be **hashable**: their hash must never change. Immutable built-ins are hashable; lists and dicts aren't. A tuple is hashable only if everything inside it is. If you define `__eq__` on a class, define `__hash__` too (or use a frozen dataclass, [note 05](05-types-and-dataclasses.md)), or instances stop working as keys.

---

## Exercises

[`practice/exercises/01_data_model.py`](../practice/exercises/01_data_model.py)
