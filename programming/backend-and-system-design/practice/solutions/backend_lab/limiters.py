"""Rate limiters with the clock passed in. Chapter 4."""
from collections import deque


class FixedWindow:
    def __init__(self, limit: int, window: float) -> None:
        self.limit, self.window, self.slot, self.count = limit, window, None, 0

    def allow(self, now: float) -> bool:
        """Allow up to `limit` per window; windows start at multiples of `window`."""
        slot = int(now // self.window)
        if slot != self.slot:
            self.slot, self.count = slot, 0
        if self.count < self.limit:
            self.count += 1
            return True
        return False


class SlidingLog:
    def __init__(self, limit: int, window: float) -> None:
        self.limit, self.window, self.log = limit, window, deque()

    def allow(self, now: float) -> bool:
        """Allow if fewer than `limit` accepted requests are in (now - window, now]."""
        while self.log and self.log[0] <= now - self.window:
            self.log.popleft()
        if len(self.log) < self.limit:
            self.log.append(now)
            return True
        return False


class SlidingCounter:
    def __init__(self, limit: int, window: float) -> None:
        self.limit, self.window, self.slot, self.previous, self.count = limit, window, None, 0, 0

    def allow(self, now: float) -> bool:
        """Weight the previous window by how much of it still overlaps."""
        slot = int(now // self.window)
        if slot != self.slot:
            self.previous = self.count if self.slot == slot - 1 else 0
            self.slot, self.count = slot, 0
        into = (now % self.window) / self.window
        if self.previous * (1 - into) + self.count < self.limit:
            self.count += 1
            return True
        return False


class TokenBucket:
    def __init__(self, rate: float, burst: float) -> None:
        self.rate, self.burst, self.tokens, self.last = rate, burst, burst, 0.0

    def allow(self, now: float) -> bool:
        """Refill at `rate` per second up to `burst`; spend one token per request."""
        self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class LeakyBucket:
    def __init__(self, rate: float, burst: float) -> None:
        self.rate, self.burst, self.level, self.last = rate, burst, 0.0, 0.0

    def allow(self, now: float) -> bool:
        """A queue of size `burst` draining at `rate` per second; a full one refuses."""
        self.level = max(0.0, self.level - (now - self.last) * self.rate)
        self.last = now
        if self.level + 1 <= self.burst:
            self.level += 1
            return True
        return False
