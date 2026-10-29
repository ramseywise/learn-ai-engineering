"""Word frequencies and reading time, with a small CLI."""

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path


def word_frequencies(text: str) -> dict[str, int]:
    """Lower-cased word counts, ignoring punctuation, most common first."""
    return dict(Counter(re.findall(r"[a-z']+", text.lower())).most_common())


def reading_time(text: str, wpm: int = 200) -> int:
    """Minutes to read text at wpm words per minute, rounded up."""
    if wpm <= 0:
        raise ValueError("wpm must be positive")
    return math.ceil(len(text.split()) / wpm)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="textstats")
    parser.add_argument("path", type=Path)
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args(argv)
    try:
        text = args.path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"textstats: {args.path} not found", file=sys.stderr)
        return 1
    for word, n in list(word_frequencies(text).items())[: args.top]:
        print(word, n)
    print(f"reading time: {reading_time(text)} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
