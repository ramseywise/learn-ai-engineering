"""Retry decorator with exponential backoff — live coding, 25-30 min.

PROMPT
    "Write a retry decorator with exponential backoff. It should be
    configurable for max attempts, base delay, and which exceptions to
    retry on."

The interviewer answered:
    - Reraise the original exception on exhaustion, not a custom RetryError.
    - Jitter is up to you. (If you add it, be ready to say why.)

Assume it should work both as `@retry` and `@retry(max_attempts=5)`.

Tests-first is expected on project-style prompts like this one. Write the
exhaustion test before the implementation.
"""

import time


def retry(func=None, *, max_attempts=3, base_delay=0.01, exceptions=(Exception,)):
    raise NotImplementedError


if __name__ == "__main__":
    calls = {"n": 0}

    @retry(max_attempts=3, base_delay=0.01)
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("transient")
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 3, f"expected 3 attempts, got {calls['n']}"

    @retry
    def bare():
        return "ok"

    assert bare() == "ok", "bare @retry should work too"
    print("smoke test passed")

    # your edge cases here -- exhaustion, metadata preservation, non-retryable errors
