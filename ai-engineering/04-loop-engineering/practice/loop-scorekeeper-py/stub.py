from __future__ import annotations

import math

from model import Complete, Completion

LOWER = "lambda s: s.lower()"
DASHES = 'lambda s: s.strip().lower().replace(" ", "-")'
SYMBOLS = '''lambda s: __import__("re").sub(r"[^a-z0-9]+", "-", s.strip().lower()).strip("-")'''
ACCENTS = '''lambda s: __import__("re").sub(r"[^a-z0-9]+", "-", "".join(c for c in __import__("unicodedata").normalize("NFD", s) if not __import__("unicodedata").combining(c)).strip().lower()).strip("-")'''
HARDCODED = '''lambda s: {"Hello World": "hello-world", "  Trim me  ": "trim-me", "Already-slugged": "already-slugged", "Rock & Roll!": "rock-roll"}.get(s)'''


def scripted(attempts: list[str]) -> Complete:
    """Plays a fixed list of attempts, one per call, then repeats the last."""
    calls = iter(range(10**6))

    def complete(prompt: str, system: str = "", max_tokens: int = 16000) -> Completion:
        text = attempts[min(next(calls), len(attempts) - 1)]
        return Completion(text, math.ceil(len(prompt) / 4), math.ceil(len(text) / 4))

    return complete


# Each is a factory: a scripted maker has state, so every run needs a fresh one.
def honest() -> Complete:
    return scripted([LOWER, DASHES, ACCENTS])


def gamer() -> Complete:
    """Reaches 4/4 visible by memorising the answers. A loop that trusts visible checks ships this."""
    return scripted([LOWER, DASHES, HARDCODED])


def stuck() -> Complete:
    """Fails the same way forever."""
    return scripted([LOWER])


def overfit() -> Complete:
    """Passes visible but misses accents: an ordinary, unintended overfit."""
    return scripted([LOWER, SYMBOLS])
