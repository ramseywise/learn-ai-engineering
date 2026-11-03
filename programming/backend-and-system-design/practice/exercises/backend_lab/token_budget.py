"""A per-tenant token budget with reservations. Chapter 10."""
from dataclasses import dataclass

class OverBudget(Exception):
    """Reserving this many tokens would pass the tenant's limit."""

@dataclass(frozen=True)
class Reservation:
    id: int
    tenant: str
    tokens: int
    window: int

class TokenBudget:

    def __init__(self, limit: int, window: float) -> None:
        """Each tenant has `limit` tokens per window; windows are multiples of `window`."""
        raise NotImplementedError()

    def remaining(self, tenant: str, now: float) -> int:
        """Tokens left now: the limit minus what's used and what's held."""
        raise NotImplementedError()

    def reserve(self, tenant: str, prompt_tokens: int, max_tokens: int, now: float) -> Reservation:
        """Hold prompt_tokens + max_tokens, or raise OverBudget and hold nothing."""
        raise NotImplementedError()

    def settle(self, reservation: Reservation, actual: int) -> None:
        """Replace the hold with actual usage. Raise ValueError if already settled.

        Actual usage may exceed the hold: a budget records what was really spent.
        Usage counts in the window the reservation was made in.
        """
        raise NotImplementedError()

    def release(self, reservation: Reservation) -> None:
        """A call that failed before any usage: give the whole hold back."""
        raise NotImplementedError()
