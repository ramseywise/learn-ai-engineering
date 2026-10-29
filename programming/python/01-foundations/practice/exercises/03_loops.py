"""03 — Loop patterns. Write each with a plain loop; the asserts compare against built-ins.
Run: python3 03_loops.py"""


def count_if_even(xs: list[int]) -> int:
    """Q1. How many items are even. Counting pattern."""
    raise NotImplementedError


def largest(xs: list[float]) -> float | None:
    """Q2. The largest item, or None if empty. Start from None, not 0."""
    raise NotImplementedError


def first_index(xs: list[str], target: str) -> int:
    """Q3. Index of the first item equal to target, or -1. Search pattern: stop early."""
    raise NotImplementedError


def running_totals(xs: list[int]) -> list[int]:
    """Q4. [1, 2, 3] -> [1, 3, 6]."""
    raise NotImplementedError


def collatz_steps(n: int) -> int:
    """Q5. Steps for n to reach 1: halve if even, else 3n + 1. Use a while loop."""
    raise NotImplementedError


if __name__ == "__main__":
    import itertools

    data = [4, -7, 10, 3, -2, 8]
    assert count_if_even(data) == sum(1 for x in data if x % 2 == 0) == 4
    assert largest(data) == max(data) and largest([]) is None
    assert largest([-5, -2, -9]) == -2
    assert first_index(["a", "b", "a"], "a") == 0 and first_index(["a"], "z") == -1
    assert running_totals(data) == list(itertools.accumulate(data))
    assert collatz_steps(1) == 0 and collatz_steps(6) == 8 and collatz_steps(27) == 111
    print("all good")
