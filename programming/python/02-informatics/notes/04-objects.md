---
origin: curated
sources:
  - "Charles Severance, Python for Everybody, ch. 14 — https://www.py4e.com/book (CC BY-NC-SA 3.0; paraphrased)"
concepts: [python-classes, python-objects, python-inheritance, python-dunder-methods, object-lifecycle]
cleaned: 2026-10-29
---
# 4 — Objects

> A class bundles data with the functions that act on it. You've been using objects all along (`str`, `list`, file handles). Now you'll write your own.

---

## A class

```python
class PartyAnimal:
    def __init__(self, name: str):      # runs when you call PartyAnimal("Sally")
        self.name = name                # attributes live on self
        self.x = 0

    def party(self) -> int:
        self.x += 1
        return self.x

s = PartyAnimal("Sally")
s.party(); s.party()     # s.x == 2
```

- `self` is the instance. `s.party()` is shorthand for `PartyAnimal.party(s)`.
- Each instance has its own attributes, and the class holds the shared methods.
- `dir(s)` and `type(s)` let you look inside any object.

## Inheritance

```python
class FootballFan(PartyAnimal):
    def __init__(self, name: str):
        super().__init__(name)          # let the parent set up its part
        self.points = 0

    def touchdown(self) -> None:
        self.points += 7
        self.party()
```

A subclass gets everything from its parent and adds to it or overrides it. Keep hierarchies shallow. Composition (an object that *has* another object) is usually more flexible than deep inheritance.

## Validating in `__init__`

An object should not exist in a bad state. Check the arguments in `__init__` and `raise` ([Python 01 · 02](../../01-foundations/notes/02-functions.md#rejecting-bad-arguments)):

```python
class Account:
    def __init__(self, owner: str, balance: float = 0):
        if balance < 0:
            raise ValueError("opening balance cannot be negative")
        self.owner, self.balance = owner, balance
```

[Python 03 · 01](../../03-language-for-engineers/notes/01-data-model-and-idioms.md) has the full table of dunder methods, and [Python 03 · 08](../../03-language-for-engineers/notes/08-objects-inheritance-and-mro.md) covers the MRO and descriptors.

## Dunder methods

Special `__names__` hook your class into Python's syntax:

| Method | Enables |
|---|---|
| `__repr__` | A useful display in the REPL and in logs. Always define it |
| `__eq__` | `a == b` (the default is identity) |
| `__lt__` | `sorted()`, `<` |
| `__len__`, `__iter__`, `__getitem__` | `len()`, `for`, `obj[i]` |
| `__enter__` / `__exit__` | `with obj:` ([Python 03 · note 04](../../03-language-for-engineers/notes/04-errors-and-context-managers.md)) |

For classes that mostly hold data, `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you ([Python 03 · note 05](../../03-language-for-engineers/notes/05-types-and-dataclasses.md)).

## When to write a class

Write one when several functions share the same state, or when you need many instances with the same behaviour. A module of plain functions is fine otherwise. Not everything has to be an object.

---

## Exercises

[`practice/exercises/04_objects.py`](../practice/exercises/04_objects.py): a bank account with validation, a subclass, and `__repr__`/`__eq__`/sorting.

## Next

[5 — Using databases from Python](05-databases.md): storing your records in `sqlite3`.
