"""Event ingest pipeline — practical, 40 min, stdlib only.

PROMPT
    "Build a pipeline that ingests these event records into a database and
    supports querying daily totals per user."

Constraint: `sqlite3` is stdlib -- no install, no server, no network.

Expect a follow-up question once it works. Build it well.
"""

import sqlite3

EVENTS = [
    {"event_id": "e1", "user_id": "u1", "amount": 1000, "occurred_at": "2026-01-05T10:00:00Z"},
    {"event_id": "e2", "user_id": "u1", "amount": 2500, "occurred_at": "2026-01-05T18:30:00Z"},
    {"event_id": "e3", "user_id": "u2", "amount": 700, "occurred_at": "2026-01-05T09:15:00Z"},
    {"event_id": "e4", "user_id": "u1", "amount": 1250, "occurred_at": "2026-01-06T11:00:00Z"},
    # replayed from an at-least-once source -- duplicate of e2
    {"event_id": "e2", "user_id": "u1", "amount": 2500, "occurred_at": "2026-01-05T18:30:00Z"},
]


class EventStore:
    def __init__(self, path: str = ":memory:") -> None:
        raise NotImplementedError

    def ingest(self, events: list[dict]) -> int:
        """Ingest events. Return the number newly written."""
        raise NotImplementedError

    def daily_totals(self, user_id: str) -> list[tuple[str, int]]:
        """[(YYYY-MM-DD, total), ...] ascending by day."""
        raise NotImplementedError


if __name__ == "__main__":
    store = EventStore()
    store.ingest(EVENTS)

    totals = store.daily_totals("u1")
    assert totals[0] == ("2026-01-05", 3500), f"got {totals[0]}"

    # Re-ingesting the same batch must not change anything.
    store.ingest(EVENTS)
    assert store.daily_totals("u1") == totals, "ingest is not idempotent"

    print("smoke test passed")

    # your edge cases here -- unknown user, empty batch, day boundaries
