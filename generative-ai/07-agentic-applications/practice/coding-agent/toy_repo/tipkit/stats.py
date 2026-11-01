"""Summary statistics over tip records. The agent's job is to fix a bug here."""


def tip_rate(total_bill, tip):
    """Tip as a fraction of the bill."""
    if total_bill <= 0:
        raise ValueError("total_bill must be positive")
    return tip / total_bill


def median(values):
    """Middle value of a non-empty list."""
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid]


def top_value(values):
    """Largest value of a non-empty list."""
    ordered = sorted(values)
    return ordered[-1]
