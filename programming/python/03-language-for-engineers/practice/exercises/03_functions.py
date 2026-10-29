"""03 — Closures and decorators. Run: python3 03_functions.py"""

import functools
from collections.abc import Callable


def make_counter(start: int = 0) -> Callable[[], int]:
    """Q1. Return a function that returns start+1, start+2, … on successive calls (closure + nonlocal)."""
    raise NotImplementedError


def multipliers() -> list[Callable[[int], int]]:
    """Q2. [f0, f1, f2] where fi(x) == x * i. Watch out for late binding."""
    raise NotImplementedError


def count_calls(fn):
    """Q3. Decorator: count calls in wrapper.calls. Keep fn's __name__ and __doc__ (functools.wraps)."""

    raise NotImplementedError


def retry(times: int, on: tuple[type[Exception], ...] = (Exception,)):
    """Q4. Decorator factory: call fn up to `times` times while it raises one of `on`;
    re-raise the last error. Other exceptions propagate immediately."""

    raise NotImplementedError


def memoize(fn):
    """Q5. Your own cache decorator for functions of hashable positional args (a dict in a closure).
    Don't use functools.cache."""
    raise NotImplementedError


if __name__ == "__main__":
    c = make_counter(10)
    assert (c(), c(), make_counter()()) == (11, 12, 1)
    assert [f(5) for f in multipliers()] == [0, 5, 10]

    @count_calls
    def hello(name):
        """Say hi."""
        return f"hi {name}"

    hello("a"); hello("b")
    assert hello.calls == 2 and hello.__name__ == "hello" and hello.__doc__ == "Say hi."

    attempts = []

    @retry(times=3, on=(ConnectionError,))
    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise ConnectionError
        return "ok"

    assert flaky() == "ok" and len(attempts) == 3

    @retry(times=3, on=(ConnectionError,))
    def broken():
        attempts.append(1)
        raise ValueError("bad input")

    attempts.clear()
    try:
        broken()
    except ValueError:
        pass
    assert len(attempts) == 1

    calls = []

    @memoize
    def fib(n):
        calls.append(n)
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(30) == 832040 and len(calls) == 31
    print("all good")
