"""01 — The data model and idioms. Run: python3 01_data_model.py"""

from collections.abc import Iterator


def append_to(item, bucket=None) -> list:
    """Q1. Append item to bucket and return it. With no bucket, start a NEW list each call
    (avoid the mutable default trap)."""
    bucket = [] if bucket is None else bucket
    bucket.append(item)
    return bucket


def head_tail(xs: list) -> tuple:
    """Q2. Return (first, last, middle) using star-unpacking: [1, 2, 3, 4] -> (1, 4, [2, 3])."""
    first, *middle, last = xs
    return first, last, middle


def merge_config(defaults: dict, overrides: dict) -> dict:
    """Q3. A NEW dict: defaults updated by overrides, ignoring overrides whose value is None.
    Neither input may be modified."""
    return defaults | {k: v for k, v in overrides.items() if v is not None}


class Deck:
    """Q4. A sequence of cards built from ranks x suits ('2♠', '3♠', …, 'A♥').
    - len(deck), deck[i], deck[a:b] (a list), `card in deck` and `for card in deck` all work.
    - Implement only __init__, __len__ and __getitem__; Python provides the rest."""

    ranks = [str(n) for n in range(2, 11)] + list("JQKA")
    suits = "♠♦♣♥"

    def __init__(self):
        self._cards = [r + s for s in self.suits for r in self.ranks]

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, i):
        return self._cards[i]


class Money:
    """Q5. An amount in a currency, usable as a dict key.
    - Money(5, 'EUR') + Money(2, 'EUR') == Money(7, 'EUR'); mixing currencies raises ValueError.
    - repr: Money(7, 'EUR'). Equal values must hash equal."""

    def __init__(self, amount: int, currency: str):
        self.amount = amount
        self.currency = currency

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Money) and (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    def __repr__(self) -> str:
        return f"Money({self.amount}, {self.currency!r})"


def _cards(deck) -> Iterator[str]:
    yield from deck


if __name__ == "__main__":
    assert append_to(1) == [1] and append_to(2) == [2]
    mine = [0]
    assert append_to(1, mine) is mine and mine == [0, 1]
    assert head_tail([1, 2, 3, 4]) == (1, 4, [2, 3]) and head_tail([1, 2]) == (1, 2, [])
    d, o = {"port": 80, "host": "x"}, {"port": 8080, "host": None}
    assert merge_config(d, o) == {"port": 8080, "host": "x"} and d["port"] == 80 and o["host"] is None
    deck = Deck()
    assert len(deck) == 52 and deck[0] == "2♠" and deck[-1] == "A♥" and deck[:3] == ["2♠", "3♠", "4♠"]
    assert "Q♦" in deck and sum(1 for _ in _cards(deck)) == 52
    assert Money(5, "EUR") + Money(2, "EUR") == Money(7, "EUR")
    assert repr(Money(7, "EUR")) == "Money(7, 'EUR')"
    assert {Money(1, "USD"): "a"}[Money(1, "USD")] == "a"
    try:
        Money(1, "USD") + Money(1, "EUR")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    print("all good")
