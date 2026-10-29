---
origin: curated
sources:
  - "Charles Severance, Python for Everybody, ch. 6–7 — https://www.py4e.com/book (CC BY-NC-SA 3.0; paraphrased)"
concepts: [python-strings, python-slicing, python-string-methods, python-files, python-f-strings, python-encoding]
cleaned: 2026-10-29
---
# 4 — Strings and Files

> A string is an immutable sequence of characters, and a text file is a sequence of lines. "Read a file, pick out the lines you care about, pull a field out of each" is half of all scripting.

---

## Strings are sequences

```python
s = "banana"
s[0], s[-1]        # 'b', 'a'
s[1:4]             # 'ana': the start is included, the end excluded
s[:3], s[3:]       # 'ban', 'ana'. s[:i] + s[i:] == s for every i
s[::-1]            # 'ananab'
len(s), "nan" in s # 6, True
```

Strings are **immutable**. `s[0] = "B"` is an error. Every method returns a *new* string: `s = s.upper()`.

## Methods you'll use constantly

| Method | Example | Result |
|---|---|---|
| `strip()` / `rstrip()` | `"  hi\n".strip()` | `'hi'` |
| `lower()` / `upper()` | `"Ada".lower()` | `'ada'` |
| `startswith()` / `endswith()` | `line.startswith("From ")` | `True` / `False` |
| `find()` | `"a@b.org".find("@")` | `1` (`-1` if not found) |
| `split()` | `"a b  c".split()` | `['a', 'b', 'c']`. With no argument it splits on any run of whitespace |
| `split(sep)` | `"a,,b".split(",")` | `['a', '', 'b']` |
| `join()` | `", ".join(["a", "b"])` | `'a, b'` |
| `replace()` | `"a-b".replace("-", "_")` | `'a_b'` |

## f-strings

```python
f"{name} owes ${amount:,.2f}"     # 'Ada owes $1,234.50'
f"{ratio:.1%}"                     # '12.5%'
f"{n:>5}|{n:<5}|{n:05d}"           # right-align, left-align, zero-pad
f"{value=}"                        # 'value=42': handy when debugging
```

## Reading files

```python
with open("mbox.txt", encoding="utf-8") as fh:     # the with block closes the file for you
    for line in fh:                                # one line at a time, so memory use stays constant
        line = line.rstrip()                       # drop the trailing newline
        if not line.startswith("From "):
            continue                               # the "skip uninteresting lines" pattern
        words = line.split()
        print(words[1])                            # the sender's address
```

- **Always pass `encoding="utf-8"`.** The default depends on the operating system.
- `fh.read()` returns the whole file as one string. Fine for small files only.
- Guard against a missing file with `try: … except FileNotFoundError:`.
- `pathlib` is the modern way to handle paths: `Path("data") / "mbox.txt"`, `path.read_text(encoding="utf-8")`, `path.exists()`.

## Writing files

```python
with open("out.txt", "w", encoding="utf-8") as out:   # "w" truncates the file; "a" appends
    out.write("line one\n")                            # write() adds no newline
```

---

## Exercises

[`practice/exercises/04_strings_and_files.py`](../practice/exercises/04_strings_and_files.py): parse email headers, extract fields with slicing, and read a temporary file.
