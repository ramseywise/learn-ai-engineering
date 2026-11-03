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
        self.limit, self.window = limit, window
        self.used: dict[tuple[str, int], int] = {}
        self.held: dict[tuple[str, int], int] = {}
        self.open: set[int] = set()
        self.next_id = 0

    def _slot(self, now: float) -> int:
        return int(now // self.window)

    def remaining(self, tenant: str, now: float) -> int:
        """Tokens left now: the limit minus what's used and what's held."""
        key = (tenant, self._slot(now))
        return self.limit - self.used.get(key, 0) - self.held.get(key, 0)

    def reserve(self, tenant: str, prompt_tokens: int, max_tokens: int, now: float) -> Reservation:
        """Hold prompt_tokens + max_tokens, or raise OverBudget and hold nothing."""
        tokens = prompt_tokens + max_tokens
        if tokens > self.remaining(tenant, now):
            raise OverBudget(tenant)
        slot = self._slot(now)
        self.held[(tenant, slot)] = self.held.get((tenant, slot), 0) + tokens
        self.next_id += 1
        self.open.add(self.next_id)
        return Reservation(self.next_id, tenant, tokens, slot)

    def settle(self, reservation: Reservation, actual: int) -> None:
        """Replace the hold with actual usage. Raise ValueError if already settled.

        Actual usage may exceed the hold: a budget records what was really spent.
        Usage counts in the window the reservation was made in.
        """
        if reservation.id not in self.open:
            raise ValueError("already settled")
        self.open.remove(reservation.id)
        key = (reservation.tenant, reservation.window)
        self.held[key] -= reservation.tokens
        self.used[key] = self.used.get(key, 0) + actual

    def release(self, reservation: Reservation) -> None:
        """A call that failed before any usage: give the whole hold back."""
        self.settle(reservation, 0)
