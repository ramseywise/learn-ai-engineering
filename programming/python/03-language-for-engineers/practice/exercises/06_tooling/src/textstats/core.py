"""Word frequencies and reading time, with a small CLI.

TODO: implement the three functions so `uv run pytest` passes, then make
`uv run ruff check .` and `uv run ruff format --check .` clean (there are lint problems on purpose)."""

import sys, os
import argparse
from pathlib import Path
from typing import Dict, List, Optional


def word_frequencies(text: str) -> Dict[str, int]:
    """Lower-cased word counts, ignoring punctuation, most common first."""
    raise NotImplementedError


def reading_time(text: str, wpm: int = 200) -> int:
    """Minutes to read text at wpm words per minute, rounded up. wpm <= 0 raises ValueError."""
    raise NotImplementedError


def main(argv: Optional[List[str]] = None) -> int:
    """CLI: print the top words ('word count' per line) and 'reading time: N min'.
    A missing file prints 'textstats: <path> not found' to stderr and returns 1."""
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
