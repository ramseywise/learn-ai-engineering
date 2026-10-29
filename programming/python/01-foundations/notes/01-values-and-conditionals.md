---
origin: curated
sources:
  - "Charles Severance, Python for Everybody, ch. 1–3 — https://www.py4e.com/book (CC BY-NC-SA 3.0; paraphrased, not copied)"
concepts: [python-values, python-types, python-expressions, python-conditionals, python-try-except]
cleaned: 2026-10-29
---
# 1 — Values, Expressions and Conditionals

> A program is a sequence of statements. Each one reads values, computes new ones and decides what to do next. Know what each value's type is, and the rest follows.

---

## Values and types

```python
>>> type(17), type(3.2), type("17"), type(True), type(None)
(<class 'int'>, <class 'float'>, <class 'str'>, <class 'bool'>, <class 'NoneType'>)
```

- **Variables are names bound to values.** Assigning to a name never copies the value ([note 05](05-collections.md) shows why that matters for lists).
- Names are case-sensitive, can't start with a digit and can't be keywords. Use `snake_case`.
- Convert explicitly: `int("42")`, `float("3.5")`, `str(42)`. `int("3.5")` raises a `ValueError`. Use `int(float("3.5"))` instead, which truncates.

## Operators

| Operator | Meaning | Gotcha |
|---|---|---|
| `/` | True division, always returns a `float` | `7 / 2 == 3.5` |
| `//` | Floor division | `-7 // 2 == -4` (it rounds toward −∞, not toward zero) |
| `%` | Remainder | `x % 2 == 0` tests for even. `n % 10` gives the last digit |
| `**` | Power | `2 ** 10` |
| `+`, `*` on strings | Concatenate, repeat | `"ab" * 3 == "ababab"`. `"1" + 1` is a `TypeError` |

Precedence follows PEMDAS. When in doubt, add parentheses: they cost nothing.

## Conditionals

```python
if hours > 40:
    pay = 40 * rate + (hours - 40) * rate * 1.5
elif hours > 0:
    pay = hours * rate
else:
    pay = 0
```

- Indentation *is* the block structure. Use four spaces, never tabs.
- Comparisons chain: `0 <= score <= 1`.
- `and` / `or` **short-circuit**. `x != 0 and 10 / x > 2` never divides by zero, so put the guard first.
- Empty values are falsy: `0`, `0.0`, `""`, `[]`, `{}`, `None`. Write `if items:`, not `if len(items) > 0:`.

## Catching bad input: `try` / `except`

```python
raw = input("Hours: ")
try:
    hours = float(raw)
except ValueError:
    print("Please enter a number")
    hours = None
```

Wrap only the line that can fail, and name the exception you expect. A bare `except:` also swallows typos and `Ctrl-C`. [Python 03 · note 04](../../03-language-for-engineers/notes/04-errors-and-context-managers.md) covers exceptions properly.

## Debugging checklist

- **Syntax errors** point at, or just after, the problem: a missing colon, an unclosed bracket.
- **Runtime errors**: read the traceback *from the bottom up*. The last line names the exception, and the line above it shows where it happened.
- **Semantic errors**: the program runs but gives the wrong answer. Print the intermediate values, or test small cases with `assert`.

---

## Exercises

[`practice/exercises/01_values_and_conditionals.py`](../practice/exercises/01_values_and_conditionals.py): pay with overtime, a grade from a score, and safe numeric parsing.
