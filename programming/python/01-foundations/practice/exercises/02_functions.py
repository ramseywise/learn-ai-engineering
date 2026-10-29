"""02 — Functions. Run: python3 02_functions.py"""


def average(xs: list[float]) -> float | None:
    """Q1. Mean of xs, or None for an empty list (don't divide by zero)."""
    raise NotImplementedError


def greet(name: str, greeting: str = "Hello", shout: bool = False) -> str:
    """Q2. 'Hello, Ada!' by default. shout=True upper-cases the whole message."""
    raise NotImplementedError


def append_item(item: str, items: list[str] | None = None) -> list[str]:
    """Q3. Append item to items and return the list. With no list given, start a fresh one
    on every call: avoid the mutable-default bug."""
    raise NotImplementedError


def clamp(x: float, low: float, high: float) -> float:
    """Q4. Limit x to the range [low, high]. Raise ValueError if low > high."""
    raise NotImplementedError


if __name__ == "__main__":
    assert average([1, 2, 3, 4]) == 2.5 and average([]) is None
    assert greet("Ada") == "Hello, Ada!"
    assert greet("Ada", greeting="Hi") == "Hi, Ada!"
    assert greet("Ada", shout=True) == "HELLO, ADA!"
    assert append_item("a") == ["a"]
    assert append_item("b") == ["b"], "the default list leaked between calls"
    shared = ["x"]
    assert append_item("y", shared) is shared and shared == ["x", "y"]
    assert clamp(5, 0, 10) == 5 and clamp(-1, 0, 10) == 0 and clamp(11, 0, 10) == 10
    try:
        clamp(1, 10, 0)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    print("all good")
