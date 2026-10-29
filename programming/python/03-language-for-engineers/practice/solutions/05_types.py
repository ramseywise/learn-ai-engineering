"""05 — Type hints and dataclasses. Run: python3 05_types.py   (and: uvx mypy 05_types.py)"""

from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from typing import Protocol


@dataclass(frozen=True, order=True)
class Version:
    """Q1. A semantic version. Make it frozen (hashable) and orderable by (major, minor, patch).
    Add a classmethod parse('1.2.3') -> Version; anything else raises ValueError."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, text: str) -> "Version":
        parts = text.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError(f"not a version: {text!r}")
        return cls(*map(int, parts))


@dataclass
class Cart:
    """Q2. items: dict of sku -> quantity, default empty (no shared mutable default!).
    add(sku, qty=1) adds; qty must be positive (ValueError). total(prices) sums qty * price."""

    items: dict[str, int] = field(default_factory=dict)

    def add(self, sku: str, qty: int = 1) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        self.items[sku] = self.items.get(sku, 0) + qty

    def total(self, prices: dict[str, float]) -> float:
        return sum(q * prices[s] for s, q in self.items.items())


class HasName(Protocol):
    name: str


@dataclass
class Dog:
    name: str


@dataclass
class Robot:
    name: str
    serial: int


def names(things: Iterable[HasName]) -> list[str]:
    """Q3. The sorted names of anything with a `name` attribute (a Protocol, no inheritance)."""
    return sorted(t.name for t in things)


def bump(v: Version, part: str) -> Version:
    """Q4. Return a NEW version with `part` ('major' | 'minor' | 'patch') incremented and the
    lower parts reset to 0. Use dataclasses.replace."""
    if part == "major":
        return replace(v, major=v.major + 1, minor=0, patch=0)
    if part == "minor":
        return replace(v, minor=v.minor + 1, patch=0)
    if part == "patch":
        return replace(v, patch=v.patch + 1)
    raise ValueError(part)


if __name__ == "__main__":
    v = Version.parse("1.10.0")
    assert v == Version(1, 10, 0) and Version.parse("1.9.9") < v
    assert max(map(Version.parse, ["0.1.0", "1.2.3", "1.10.0"])) == v
    assert len({Version(1, 0, 0), Version(1, 0, 0)}) == 1
    for bad in ["1.2", "a.b.c", "1.2.3.4"]:
        try:
            Version.parse(bad)
            raise AssertionError(bad)
        except ValueError:
            pass
    a, b = Cart(), Cart()
    a.add("apple", 2)
    a.add("apple")
    assert b.items == {} and a.items == {"apple": 3}
    assert a.total({"apple": 0.5}) == 1.5
    assert names([Robot("R2", 1), Dog("Ace")]) == ["Ace", "R2"]
    assert bump(v, "major") == Version(2, 0, 0) and bump(v, "minor") == Version(1, 11, 0)
    assert bump(v, "patch") == Version(1, 10, 1) and v == Version(1, 10, 0)
    print("all good")
