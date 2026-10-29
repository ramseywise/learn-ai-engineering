---
origin: curated
sources:
  - "Charles Severance, Python for Everybody, ch. 8–10 — https://www.py4e.com/book (CC BY-NC-SA 3.0; paraphrased)"
concepts: [python-lists, python-dicts, python-tuples, python-aliasing, python-counting-pattern, python-sorting]
cleaned: 2026-10-29
---
# 5 — Lists, Dictionaries and Tuples

> A list is an ordered, mutable sequence. A dict maps keys to values. A tuple is an immutable record. Combined, they count, group and sort almost anything.

---

## Lists

```python
xs = [3, 1, 2]
xs.append(4); xs.extend([5, 6]); xs.insert(0, 0)
xs.pop()          # removes and returns the last item
xs.remove(3)      # removes the first 3
xs.sort()         # sorts in place and returns None
ys = sorted(xs)   # returns a new list
```

**Aliasing.** `b = a` makes `b` a second name for the *same* list, so appending through `b` changes `a`. Copy explicitly with `a.copy()`, `a[:]` or `list(a)`. The same trap appears when you pass a list to a function: the function can mutate the caller's list.

## Dictionaries

```python
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1     # the counting idiom

for word, n in counts.items():                 # iterate over key/value pairs
    ...
"spam" in counts                               # checks keys, in O(1)
```

- Lookup, insert and `in` are O(1) on average. That is the reason to use a dict.
- Keys must be **hashable** (immutable): strings, numbers, tuples. Lists can't be keys.
- Dicts keep insertion order (Python 3.7+).
- `d[k]` raises `KeyError` when the key is missing. `d.get(k, default)` doesn't.

The standard library already has the counting patterns:

```python
from collections import Counter, defaultdict
Counter(words).most_common(10)
by_domain = defaultdict(list)
for email in emails:
    by_domain[email.split("@")[1]].append(email)
```

## Tuples

```python
point = (3, 4)
x, y = point                  # unpacking
a, b = b, a                   # swap
for name, n in counts.items():   # each item is a (key, value) tuple
    ...
```

Tuples are immutable and hashable, so they can be dict keys (`{(lat, lon): city}`). Use them for fixed-size records. For named fields, use `NamedTuple` or a dataclass ([Python 03 · note 05](../../03-language-for-engineers/notes/05-types-and-dataclasses.md)).

## Sorting with a key

```python
top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
# Ties broken alphabetically: sort by (-count, word)
top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
```

Python compares tuples element by element, which makes multi-key sorts one-liners. The old "decorate, sort, undecorate" (DSU) pattern is what `key=` does for you.

---

## Exercises

[`practice/exercises/05_collections.py`](../practice/exercises/05_collections.py): word counts, top-N with ties, grouping, and the aliasing trap.
