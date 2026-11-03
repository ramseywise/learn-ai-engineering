"""A retry budget and a circuit breaker. Chapter 7."""


class RetryBudget:
    def __init__(self, ratio: float = 0.1, floor: int = 10) -> None:
        self.ratio, self.floor, self.requests, self.retries = ratio, floor, 0, 0

    def request(self) -> None:
        """Count one first attempt."""
        self.requests += 1

    def allow_retry(self) -> bool:
        """Allow while retries stay under floor + ratio x requests, and count it."""
        if self.retries < self.floor + self.ratio * self.requests:
            self.retries += 1
            return True
        return False


class Breaker:
    """Closed; open after `threshold` failures in a row; half open after `cool_down`."""

    def __init__(self, threshold: int = 5, cool_down: float = 30.0) -> None:
        self.threshold, self.cool_down = threshold, cool_down
        self.failures, self.opened_at, self.trial = 0, None, False

    def allow(self, now: float) -> bool:
        """Closed: yes. Open: no until cool_down has passed, then exactly one trial."""
        if self.opened_at is None:
            return True
        if now - self.opened_at < self.cool_down or self.trial:
            return False
        self.trial = True
        return True

    def record(self, ok: bool, now: float) -> None:
        """Success closes and clears. Failure counts, and a failed trial reopens."""
        self.trial = False
        if ok:
            self.failures, self.opened_at = 0, None
            return
        self.failures += 1
        if self.opened_at is not None or self.failures >= self.threshold:
            self.opened_at = now
