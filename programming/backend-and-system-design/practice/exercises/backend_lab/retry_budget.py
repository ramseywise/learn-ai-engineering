"""A retry budget and a circuit breaker. Chapter 7."""

class RetryBudget:

    def __init__(self, ratio: float=0.1, floor: int=10) -> None:
        """Set up whatever state you need."""
        raise NotImplementedError()

    def request(self) -> None:
        """Count one first attempt."""
        raise NotImplementedError()

    def allow_retry(self) -> bool:
        """Allow while retries stay under floor + ratio x requests, and count it."""
        raise NotImplementedError()

class Breaker:
    """Closed; open after `threshold` failures in a row; half open after `cool_down`."""

    def __init__(self, threshold: int=5, cool_down: float=30.0) -> None:
        """Set up whatever state you need."""
        raise NotImplementedError()

    def allow(self, now: float) -> bool:
        """Closed: yes. Open: no until cool_down has passed, then exactly one trial."""
        raise NotImplementedError()

    def record(self, ok: bool, now: float) -> None:
        """Success closes and clears. Failure counts, and a failed trial reopens."""
        raise NotImplementedError()
