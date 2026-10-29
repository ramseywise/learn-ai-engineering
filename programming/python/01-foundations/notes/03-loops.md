---
origin: curated
sources:
  - "Charles Severance, Python for Everybody, ch. 5 — https://www.py4e.com/book (CC BY-NC-SA 3.0; paraphrased)"
concepts: [python-loops, python-while, python-for, python-loop-patterns, python-break-continue]
cleaned: 2026-10-29
---
# 3 — Loops and Loop Patterns

> Most loops are one of a handful of patterns: count, total, find the largest, search, filter. Learn to recognise them; then learn the built-in that already does each one.

---

## `while` and `for`

```python
n = 5
while n > 0:              # an indefinite loop: runs until the condition is false
    n -= 1

for word in ["a", "b"]:   # a definite loop: runs once per item
    print(word)

for i in range(3):        # 0, 1, 2. range(start, stop, step) excludes stop
    ...
```

- An infinite loop on purpose is `while True:` with a `break` inside.
- `break` leaves the loop. `continue` skips to the next iteration.
- Prefer `for` whenever you're walking a collection. A `while` loop needs its own counter, and that counter is where off-by-one errors live.

## The patterns, and the idiomatic replacements

Each pattern is: set up a variable before the loop, update it inside, use it after.

| Pattern | Loop | Built-in |
|---|---|---|
| Count | `count = 0` / `count += 1` | `len(xs)`, `sum(1 for x in xs if cond)` |
| Total | `total = 0` / `total += x` | `sum(xs)` |
| Largest | `best = None` / `if best is None or x > best: best = x` | `max(xs, default=None)` |
| Search | `found = False` / `if x == target: found = True; break` | `target in xs`, `any(cond(x) for x in xs)` |
| Filter | `out = []` / `if cond(x): out.append(x)` | `[x for x in xs if cond(x)]` |
| Transform | `out = []` / `out.append(f(x))` | `[f(x) for x in xs]` |

Write the loop version once to understand it, then use the built-in. Note the `None` start in the "largest" pattern: starting from `0` gives the wrong answer for all-negative data.

## Loops that need the index

```python
for i, word in enumerate(words, start=1):
    print(i, word)

for name, score in zip(names, scores):    # walk two sequences together
    ...
```

`for i in range(len(xs))` almost always means you wanted `enumerate`.

## `else` on loops

`for … else` runs the `else` block only if the loop **didn't** `break`. It is useful for "searched everything and found nothing", but confusing to readers. A helper function that returns early is usually clearer.

---

## Exercises

[`practice/exercises/03_loops.py`](../practice/exercises/03_loops.py): write each pattern by hand. The asserts compare your answers with the built-ins.
