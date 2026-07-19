# Retry Decorator — Live Coding Walkthrough

**Prompt**: "Write a retry decorator with exponential backoff. It should be configurable for max attempts, base delay, and which exceptions to retry on."

**Time budget**: 25–30 minutes

---

## Step 1: Clarify

[NARRATE: "A few quick questions before I start. Should this reraise the original exception on exhaustion, or raise a custom RetryError? And should jitter be included — to prevent thundering herd if many callers retry simultaneously?"]

*Interviewer*: Reraise the original. Jitter is up to you.

[NARRATE: "I'll add jitter — I'll explain why as I go. And I'll assume the decorator should be usable with or without arguments, so both `@retry` and `@retry(max_attempts=5)` should work."]

---

## Step 2: Write the tests first

[NARRATE: "For a project-style prompt, I want to write the tests before the implementation. It helps me nail the interface."]

```python
import pytest
import time
from unittest.mock import patch, call

# Tests I want to pass:

def test_succeeds_on_first_try():
    """No retries needed — function returns immediately."""
    call_count = 0

    @retry(max_attempts=3)
    def always_succeeds():
        nonlocal call_count
        call_count += 1
        return "ok"

    assert always_succeeds() == "ok"
    assert call_count == 1


def test_retries_on_specified_exception():
    """Retries on the configured exception, succeeds on third try."""
    call_count = 0

    @retry(max_attempts=3, exceptions=(ValueError,))
    def fails_twice():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("transient")
        return "ok"

    with patch("time.sleep"):  # don't actually sleep in tests
        result = fails_twice()

    assert result == "ok"
    assert call_count == 3


def test_reraises_on_exhaustion():
    """Raises the last exception after max_attempts."""
    @retry(max_attempts=2, exceptions=(ConnectionError,))
    def always_fails():
        raise ConnectionError("no connection")

    with patch("time.sleep"):
        with pytest.raises(ConnectionError, match="no connection"):
            always_fails()


def test_does_not_retry_unspecified_exceptions():
    """TypeError should propagate immediately, not be retried."""
    call_count = 0

    @retry(max_attempts=3, exceptions=(ConnectionError,))
    def raises_wrong_exception():
        nonlocal call_count
        call_count += 1
        raise TypeError("programmer error")

    with pytest.raises(TypeError):
        raises_wrong_exception()

    assert call_count == 1  # no retry
```

[NARRATE: "Four tests: happy path, successful retry, exhaustion, and non-retried exception. These define the contract. Now I'll implement to make them pass."]

---

## Step 3: Implement

```python
import functools
import time
import random
import logging

logger = logging.getLogger(__name__)


def retry(
    func=None,
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    jitter: float = 0.5,
    exceptions: tuple = (Exception,),
):
    """
    Retry decorator with exponential backoff and jitter.

    Can be used as @retry or @retry(max_attempts=5).
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt == max_attempts - 1:
                        break  # exhausted — reraise below
                    delay = base_delay * (2 ** attempt) + random.uniform(0, jitter)
                    logger.warning(
                        "Attempt %d/%d failed (%s: %s). Retrying in %.2fs.",
                        attempt + 1,
                        max_attempts,
                        type(e).__name__,
                        e,
                        delay,
                    )
                    time.sleep(delay)
            raise last_exc
        return wrapper

    # Support both @retry and @retry(max_attempts=5)
    if func is not None:
        return decorator(func)
    return decorator
```

[NARRATE: "Let me walk through the key decisions:"]

[NARRATE: "First, `functools.wraps(fn)` — this preserves the wrapped function's `__name__`, `__doc__`, and `__module__`. Without it, all decorated functions look like `wrapper` to introspection tools and stack traces. Always required on decorators."]

[NARRATE: "Second, jitter: `random.uniform(0, jitter)` adds a random component to the delay. Why? If 50 workers all fail at the same time and retry at exactly the same interval, they create a thundering herd — all hammering the backend again simultaneously. Jitter spreads them out. The cost is negligible; the benefit is meaningful in production."]

[NARRATE: "Third, `except exceptions` where `exceptions` is a tuple — Python lets you pass a tuple of exception types to `except`. This gives the caller control over which errors are transient."]

[NARRATE: "Fourth, the `func=None` pattern: allows `@retry` (no parens) and `@retry(max_attempts=5)` (with parens) to both work. When called without arguments, `func` is the decorated function. When called with arguments, `func` is None and we return the decorator."]

---

## Step 4: Trace through a retry scenario

[NARRATE: "Let me trace the retry sequence for `max_attempts=3, base_delay=1.0, jitter=0.0` (removing jitter for clarity):"]

```
attempt=0: call fn() → raises → delay = 1.0 * 2^0 = 1.0s → sleep
attempt=1: call fn() → raises → delay = 1.0 * 2^1 = 2.0s → sleep
attempt=2: call fn() → raises → attempt == max_attempts-1 → break → raise last_exc
```

[NARRATE: "Three calls total, two sleeps, then reraise. That matches the test expectations."]

---

## Step 5: Check the edge cases

[NARRATE: "What if `max_attempts=1`? We'd make one call, fail, hit `attempt == max_attempts-1 == 0`, break, and reraise. No sleep. Correct."]

[NARRATE: "What if the first call succeeds? We return immediately, `last_exc` is never set. The `raise last_exc` line is unreachable. Correct."]

[NARRATE: "What if a non-retried exception is raised? The `except exceptions` clause won't catch it — it propagates immediately up the stack. Correct, matches `test_does_not_retry_unspecified_exceptions`."]

---

## Step 6: Run the tests

```bash
pytest test_retry.py -v
```

Expected:
```
test_succeeds_on_first_try PASSED
test_retries_on_specified_exception PASSED
test_reraises_on_exhaustion PASSED
test_does_not_retry_unspecified_exceptions PASSED
```

---

## Step 7: Production considerations (offer if time permits)

[NARRATE: "A few things I'd add in production that I've kept out of the interview version:"]

- **Circuit breaker**: after N consecutive failures, stop retrying entirely and fail fast. Prevents slow cascade failures.
- **Max delay cap**: `min(delay, max_delay)` so delays don't grow unbounded on high attempt counts.
- **Async version**: `async def wrapper(*args, **kwargs)` with `await asyncio.sleep(delay)` for async code paths.
- **Metrics**: increment a counter (`retries_total`, labeled by function name) so you can alert on retry rate spikes.

---

## What signals this answer

- Clarified the interface (reraise vs custom exception, jitter decision) before writing any code
- Wrote tests first — defined the contract before the implementation
- `functools.wraps` used immediately and explained
- Jitter added unprompted with a correct explanation (thundering herd)
- The `func=None` pattern handles both call styles cleanly
- Traced the sequence explicitly to verify attempt count
- Edge cases checked verbally before declaring done
- Production additions offered but not forced into the interview solution
