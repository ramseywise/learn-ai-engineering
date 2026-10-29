"""02 — Iterators, generators and comprehensions. Run: python3 02_iteration.py"""

from collections import Counter, deque
from collections.abc import Iterable, Iterator
from itertools import groupby, islice


def squares_of_evens(nums: list[int]) -> list[int]:
    """Q1. One list comprehension: squares of the even numbers."""
    return [n * n for n in nums if n % 2 == 0]


def invert(d: dict[str, int]) -> dict[int, list[str]]:
    """Q2. {'a': 1, 'b': 2, 'c': 1} -> {1: ['a', 'c'], 2: ['b']} (keys in first-seen order)."""
    out: dict[int, list[str]] = {}
    for k, v in d.items():
        out.setdefault(v, []).append(k)
    return out


def read_rows(lines: Iterable[str]) -> Iterator[list[str]]:
    """Q3. Generator: skip blank lines and lines starting with '#', strip, split on ','."""
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            yield line.split(",")


def chunks(it: Iterable, n: int) -> Iterator[list]:
    """Q4. Generator of lists of up to n items. Must work on an infinite iterator (use islice)."""
    it = iter(it)
    while batch := list(islice(it, n)):
        yield batch


def moving_average(xs: Iterable[float], window: int) -> Iterator[float]:
    """Q5. Average of each full window of the last `window` values. Use a deque(maxlen=…)."""
    buf: deque[float] = deque(maxlen=window)
    for x in xs:
        buf.append(x)
        if len(buf) == window:
            yield sum(buf) / window


def runs(s: str) -> list[tuple[str, int]]:
    """Q6. Run-length encoding with itertools.groupby: 'aaabcc' -> [('a', 3), ('b', 1), ('c', 2)]."""
    return [(ch, sum(1 for _ in grp)) for ch, grp in groupby(s)]


def top_words(text: str, n: int) -> list[tuple[str, int]]:
    """Q7. The n most common lower-cased words, using Counter."""
    return Counter(text.lower().split()).most_common(n)


if __name__ == "__main__":
    from itertools import count

    assert squares_of_evens([1, 2, 3, 4]) == [4, 16]
    assert invert({"a": 1, "b": 2, "c": 1}) == {1: ["a", "c"], 2: ["b"]}
    rows = read_rows(["# header", "a,b", "", "  c,d  "])
    assert isinstance(rows, Iterator) and list(rows) == [["a", "b"], ["c", "d"]]
    assert list(chunks(range(5), 2)) == [[0, 1], [2, 3], [4]]
    assert next(chunks(count(), 3)) == [0, 1, 2]
    assert list(moving_average([1, 2, 3, 4, 5], 3)) == [2.0, 3.0, 4.0]
    assert runs("aaabcc") == [("a", 3), ("b", 1), ("c", 2)] and runs("") == []
    assert top_words("the cat The dog the", 2) == [("the", 3), ("cat", 1)]
    print("all good")
