"""04 — Strings and files. Run: python3 04_strings_and_files.py"""

from pathlib import Path

SAMPLE = """\
From alice@example.org Sat Jan  5 09:14:16 2008
Subject: [course] build failed
X-Spam-Confidence: 0.8475

From bob@uni.edu Fri Jan  4 18:10:48 2008
Subject: re: build failed
X-Spam-Confidence: 0.6178
From: not-a-header-line
From carol@example.org Fri Jan  4 16:10:39 2008
X-Spam-Confidence: 0.6961
"""


def senders(text: str) -> list[str]:
    """Q1. Addresses from lines that start with 'From ' (with the space), in order."""
    raise NotImplementedError


def domain(address: str) -> str:
    """Q2. 'alice@example.org' -> 'example.org', using find() and slicing (not split)."""
    raise NotImplementedError


def mean_spam_confidence(text: str) -> float:
    """Q3. Average of the numbers on 'X-Spam-Confidence:' lines, rounded to 4 places."""
    raise NotImplementedError


def hour_of(from_line: str) -> int:
    """Q4. 'From x@y Sat Jan  5 09:14:16 2008' -> 9 (the hour of the time field)."""
    raise NotImplementedError


def count_matching_lines(path: Path, prefix: str) -> int:
    """Q5. Read the file at path (utf-8) and count lines starting with prefix.
    A missing file counts 0 instead of crashing."""
    raise NotImplementedError


if __name__ == "__main__":
    import tempfile

    assert senders(SAMPLE) == ["alice@example.org", "bob@uni.edu", "carol@example.org"]
    assert domain("alice@example.org") == "example.org"
    assert mean_spam_confidence(SAMPLE) == 0.7205
    assert [hour_of(line) for line in SAMPLE.splitlines() if line.startswith("From ")] == [9, 18, 16]
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "mbox.txt"
        p.write_text(SAMPLE, encoding="utf-8")
        assert count_matching_lines(p, "Subject:") == 2
        assert count_matching_lines(Path(tmp) / "missing.txt", "From") == 0
    print("all good")
