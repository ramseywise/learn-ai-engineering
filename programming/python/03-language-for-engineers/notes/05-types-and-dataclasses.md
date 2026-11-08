---
origin: curated
sources:
  - "Ben Wilson, Machine Learning Engineering in Action (Manning, 2022), ch. 10 — chapter PDF in data-engineering/sources/ml-engineering-in-action/"
  - "Python docs, typing — https://docs.python.org/3/library/typing.html"
  - "Python docs, dataclasses — https://docs.python.org/3/library/dataclasses.html"
  - "Pydantic docs — https://docs.pydantic.dev/"
concepts: [python-type-hints, python-dataclasses, python-protocols, python-generics, pydantic]
cleaned: 2026-10-29
---
# 5 — Type hints and dataclasses

> Type hints are checked by tools, not by Python. Add them to every function signature and let mypy or pyright find the bugs before your users do. Dataclasses remove the boilerplate from classes that are mostly data.

---

## Hints you'll write daily

```python
from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import Literal, TypedDict

def top(scores: Mapping[str, float], n: int = 3) -> list[tuple[str, float]]: ...
def find(name: str) -> User | None: ...                  # may return None: callers must check
def apply(fn: Callable[[str], int], xs: Iterable[str]) -> Iterator[int]: ...
Role = Literal["user", "assistant"]
class Message(TypedDict):
    role: Role
    content: str

def first[T](xs: list[T]) -> T: ...                        # generic (3.12 syntax)
```

- Accept the loosest type that works (`Iterable`, `Mapping`) and return the most specific one (`list`, `dict`).
- `X | None` forces the checker to make callers handle `None`, which is most of the value of typing.
- `Any` turns checking off. Prefer `object` and narrow with `isinstance`.
- Run a checker: `uv run mypy src/` or `pyright`. The [TypeScript track](../../../typescript/README.md) teaches the same ideas with a stricter checker.

## Protocols: structural typing

```python
from typing import Protocol

class SupportsClose(Protocol):
    def close(self) -> None: ...

def shutdown(things: list[SupportsClose]) -> None:
    for t in things:
        t.close()
```

Any class with a `close()` method fits, with no inheritance. This is "duck typing" that the checker understands.

## Dataclasses

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class Chunk:
    doc_id: str
    text: str
    score: float = 0.0
    tags: tuple[str, ...] = ()
    meta: dict[str, str] = field(default_factory=dict, compare=False)

    def __post_init__(self):
        if not self.text:
            raise ValueError("empty chunk")
```

- You get `__init__`, `__repr__` and `__eq__` for free. `order=True` adds comparisons in field order.
- `frozen=True` makes instances immutable and hashable, so they work as dict keys and set members.
- Mutable defaults need `field(default_factory=list)`, the same trap as in [note 01](01-data-model-and-idioms.md).
- `dataclasses.replace(c, score=0.9)` makes a modified copy of a frozen instance. `asdict(c)` converts it to a dict.

Returning a plain tuple, or a tuple of tuples, from a function makes every caller depend on position. Wilson's example returns nested tuples and breaks each caller when the signature gains a value (*Machine Learning Engineering in Action*, ch. 10, Listings 10.5 to 10.8). He suggests `collections.namedtuple`, comparing it to a Scala case class. `typing.NamedTuple` is the same thing with type hints; a frozen dataclass as above is the choice once the result needs methods or validation.

## Pydantic: when data comes from outside

A dataclass trusts its inputs. **Pydantic** validates and converts them at runtime, which is what you need at a boundary: JSON from an API, config, LLM output.

```python
from pydantic import BaseModel, Field

class Review(BaseModel):
    rating: int = Field(ge=1, le=5)
    summary: str

Review.model_validate_json('{"rating": "4", "summary": "ok"}')   # rating coerced to 4
Review.model_validate({"rating": 9, "summary": "x"})              # ValidationError
```

The rule is the same as with Zod in TypeScript: dataclasses inside the program, a validator at every edge.

---

## Exercises

[`practice/exercises/05_types.py`](../practice/exercises/05_types.py)
