---
origin: curated
sources:
  - "Charles Severance, Python for Everybody, ch. 4 — https://www.py4e.com/book (CC BY-NC-SA 3.0; paraphrased)"
concepts: [python-functions, python-parameters, python-return, python-scope, python-builtins]
cleaned: 2026-10-29
---
# 2 — Functions

> A function names a piece of work, so you can write it once, test it once and reuse it. Most bugs in beginners' code come from functions that print where they should return.

---

## Defining and calling

```python
def compute_pay(hours: float, rate: float) -> float:
    """Pay with time-and-a-half after 40 hours."""
    if hours <= 40:
        return hours * rate
    return 40 * rate + (hours - 40) * rate * 1.5

weekly = compute_pay(45, 10.0)   # 475.0
```

- `def` creates a function object and binds it to a name. The body runs only when the function is called.
- **Parameters** are the names in the definition. **Arguments** are the values you pass in.
- A function with no `return` returns `None`. If you write `x = print(...)`, `x` is `None`.
- The docstring (the first string in the body) is what `help(compute_pay)` shows.
- Type hints (`hours: float`) document intent. Python doesn't enforce them, but tools like mypy and pyright check them ([Python 03 · note 05](../../03-language-for-engineers/notes/05-types-and-dataclasses.md)).

## Return, don't print

```python
def average(xs):          # usable from anywhere: tests, other functions, a web handler
    return sum(xs) / len(xs)

def show_average(xs):     # only good for the terminal
    print(sum(xs) / len(xs))
```

Keep calculation and I/O separate. A function that returns a value can be tested with `assert average([1, 2, 3]) == 2`.

## Default and keyword arguments

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Ada")                       # 'Hello, Ada!'
greet("Ada", greeting="Hi")        # keyword arguments are clearer for optional settings
```

**Never use a mutable default** (`def f(xs=[])`). The list is created once, when the function is defined, and every call shares it. Use `None` and create a new list inside the function.

## Scope

Names assigned inside a function are **local** and disappear when it returns. A function can *read* global names, but assigning to one creates a new local name instead (unless you declare it `global`, which you almost never should). Pass values in as arguments and return results.

## Built-ins worth knowing on day one

`len`, `min`, `max`, `sum`, `abs`, `round`, `sorted`, `range`, `enumerate`, `zip`, `int`/`float`/`str`, `isinstance`, `print`, `input`, `open`. Also `import math, random` for `math.sqrt`, `math.pi` and `random.choice`.

---

## Exercises

[`practice/exercises/02_functions.py`](../practice/exercises/02_functions.py)
