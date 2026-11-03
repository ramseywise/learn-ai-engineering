"""Rate limiters with the clock passed in. Chapter 4."""
from collections import deque

class FixedWindow:

    def __init__(self, limit: int, window: float) -> None:
        """Set up whatever state you need."""
        raise NotImplementedError()

    def allow(self, now: float) -> bool:
        """Allow up to `limit` per window; windows start at multiples of `window`."""
        raise NotImplementedError()

class SlidingLog:

    def __init__(self, limit: int, window: float) -> None:
        """Set up whatever state you need."""
        raise NotImplementedError()

    def allow(self, now: float) -> bool:
        """Allow if fewer than `limit` accepted requests are in (now - window, now]."""
        raise NotImplementedError()

class SlidingCounter:

    def __init__(self, limit: int, window: float) -> None:
        """Set up whatever state you need."""
        raise NotImplementedError()

    def allow(self, now: float) -> bool:
        """Weight the previous window by how much of it still overlaps."""
        raise NotImplementedError()

class TokenBucket:

    def __init__(self, rate: float, burst: float) -> None:
        """Set up whatever state you need."""
        raise NotImplementedError()

    def allow(self, now: float) -> bool:
        """Refill at `rate` per second up to `burst`; spend one token per request."""
        raise NotImplementedError()

class LeakyBucket:

    def __init__(self, rate: float, burst: float) -> None:
        """Set up whatever state you need."""
        raise NotImplementedError()

    def allow(self, now: float) -> bool:
        """A queue of size `burst` draining at `rate` per second; a full one refuses."""
        raise NotImplementedError()
