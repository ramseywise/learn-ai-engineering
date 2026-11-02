"""Transaction aggregation & anomaly detection — practical, 35 min, stdlib only.

PROMPT
    "Given a list of transaction records, compute per-user monthly totals,
    flag anomalous transactions, and return a summary. Some records are
    malformed."

Constraint: pure stdlib. No pandas. (If pandas were available, say what you
would do with it and why the grader may still want the stdlib version.)

The interviewer answered:
    - Pick a reasonable anomaly rule yourself.
    - Skip malformed records and report the count -- do not fail the batch.
    - It fits in memory.

There is an architectural observation this prompt is fishing for. Say it out
loud before you start coding.
"""

from decimal import Decimal

RECORDS = [
    {"user_id": "u1", "amount": "10.00", "occurred_at": "2026-01-05T10:00:00Z"},
    {"user_id": "u1", "amount": "12.50", "occurred_at": "2026-01-11T10:00:00Z"},
    {"user_id": "u1", "amount": "11.25", "occurred_at": "2026-01-19T10:00:00Z"},
    {"user_id": "u1", "amount": "9.75", "occurred_at": "2026-01-22T10:00:00Z"},
    {"user_id": "u1", "amount": "980.00", "occurred_at": "2026-01-28T10:00:00Z"},
    {"user_id": "u2", "amount": "40.00", "occurred_at": "2026-02-02T10:00:00Z"},
    {"user_id": "u2", "amount": "not_a_number", "occurred_at": "2026-02-03T10:00:00Z"},
    {"user_id": "u2", "amount": "41.00", "occurred_at": "2026-02-09T10:00:00Z"},
    {"user_id": None, "amount": "5.00", "occurred_at": "2026-02-09T10:00:00Z"},
]


def parse_record(raw: dict):
    """Return a normalized record, or None if malformed."""
    raise NotImplementedError


def monthly_totals(records: list[dict]) -> dict:
    """(user_id, YYYY-MM) -> total."""
    raise NotImplementedError


def find_anomalies(records: list[dict]) -> list[dict]:
    raise NotImplementedError


def summarize(raw_records: list[dict]) -> dict:
    """Totals, anomalies, and the count of records that could not be parsed."""
    raise NotImplementedError


if __name__ == "__main__":
    summary = summarize(RECORDS)
    assert summary["rejected"] == 2, f"expected 2 rejects, got {summary['rejected']}"
    assert summary["totals"][("u1", "2026-01")] == Decimal("1023.50")
    print("smoke test passed")

    # your edge cases here -- identical amounts, single-record users, tz handling
