"""05 — Lists, dicts and tuples. Run: python3 05_collections.py"""

TEXT = """But soft what light through yonder window breaks
It is the east and Juliet is the sun
Arise fair sun and kill the envious moon
Who is already sick and pale with grief"""


def word_counts(text: str) -> dict[str, int]:
    """Q1. Count each word (lower-cased, split on whitespace) with a plain dict and .get()."""
    raise NotImplementedError


def top_n(counts: dict[str, int], n: int) -> list[tuple[str, int]]:
    """Q2. The n most common (word, count) pairs: highest count first, ties alphabetical."""
    raise NotImplementedError


def group_by_domain(emails: list[str]) -> dict[str, list[str]]:
    """Q3. {'example.org': ['a@example.org', ...], ...}, keeping input order within each list."""
    raise NotImplementedError


def without_duplicates(xs: list[str]) -> list[str]:
    """Q4. Drop repeats but keep first-seen order (a set alone loses the order)."""
    raise NotImplementedError


def add_tag(tags: list[str], tag: str) -> list[str]:
    """Q5. Return tags plus tag WITHOUT modifying the caller's list."""
    raise NotImplementedError


if __name__ == "__main__":
    from collections import Counter

    counts = word_counts(TEXT)
    assert counts == dict(Counter(TEXT.lower().split()))
    assert counts["is"] == 3 and counts["the"] == 3
    assert top_n(counts, 4) == [("and", 3), ("is", 3), ("the", 3), ("sun", 2)]
    emails = ["a@x.org", "b@y.edu", "c@x.org"]
    assert group_by_domain(emails) == {"x.org": ["a@x.org", "c@x.org"], "y.edu": ["b@y.edu"]}
    assert without_duplicates(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]
    original = ["x"]
    assert add_tag(original, "y") == ["x", "y"] and original == ["x"]
    print("all good")
