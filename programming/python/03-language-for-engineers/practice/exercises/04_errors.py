"""04 — Errors and context managers. Run: python3 04_errors.py"""

import json
import os
from contextlib import contextmanager
from pathlib import Path


class ConfigError(Exception):
    """Base error for config loading. Given."""


class MissingKeyError(ConfigError):
    """Q1. Raised with the missing key: str(err) == "missing key: 'port'" and err.key == 'port'."""

    def __init__(self, key: str):
        raise NotImplementedError


def load_config(path: Path, required: tuple[str, ...] = ("host", "port")) -> dict:
    """Q2. Read JSON config.
    - A missing file returns {} (only if `required` is empty; otherwise raise MissingKeyError for the first key).
    - Invalid JSON raises ConfigError chained `from` the JSONDecodeError.
    - A missing required key raises MissingKeyError."""
    raise NotImplementedError


def safe_ratio(a: float, b: float) -> float | None:
    """Q3. a / b, or None when b is zero. Use try/except, not an if."""
    raise NotImplementedError


@contextmanager
def set_env(**values: str):
    """Q4. Set environment variables inside the block; restore the previous state afterwards,
    even if the block raises (variables that didn't exist must be removed again)."""
    raise NotImplementedError


class Transaction:
    """Q5. A context manager over a list `log`.
    - On enter, append 'begin' and return self.
    - On a clean exit append 'commit'; on an exception append 'rollback' and let it propagate."""

    def __init__(self, log: list[str]):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        good, bad, partial = Path(d, "good.json"), Path(d, "bad.json"), Path(d, "partial.json")
        good.write_text('{"host": "x", "port": 1}')
        bad.write_text("{nope")
        partial.write_text('{"host": "x"}')
        assert load_config(good) == {"host": "x", "port": 1}
        assert load_config(Path(d, "missing.json"), required=()) == {}
        try:
            load_config(bad)
            raise AssertionError
        except ConfigError as err:
            assert isinstance(err.__cause__, json.JSONDecodeError)
        try:
            load_config(partial)
            raise AssertionError
        except MissingKeyError as err:
            assert err.key == "port" and str(err) == "missing key: 'port'" and isinstance(err, ConfigError)

    assert safe_ratio(1, 4) == 0.25 and safe_ratio(1, 0) is None

    os.environ.pop("LEARN_X", None)
    os.environ["LEARN_Y"] = "old"
    try:
        with set_env(LEARN_X="1", LEARN_Y="new"):
            assert os.environ["LEARN_X"] == "1" and os.environ["LEARN_Y"] == "new"
            raise RuntimeError
    except RuntimeError:
        pass
    assert "LEARN_X" not in os.environ and os.environ["LEARN_Y"] == "old"

    log: list[str] = []
    with Transaction(log) as t:
        assert isinstance(t, Transaction)
    try:
        with Transaction(log):
            raise KeyError
    except KeyError:
        pass
    assert log == ["begin", "commit", "begin", "rollback"]
    print("all good")
