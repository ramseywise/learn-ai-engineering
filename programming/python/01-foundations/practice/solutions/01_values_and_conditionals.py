"""01 — Values, expressions and conditionals. Run: python3 01_values_and_conditionals.py"""


def compute_pay(hours: float, rate: float) -> float:
    """Q1. Pay for the week: time-and-a-half for hours over 40. Negative hours pay 0."""
    if hours <= 0:
        return 0.0
    if hours <= 40:
        return hours * rate
    return 40 * rate + (hours - 40) * rate * 1.5


def grade(score: float) -> str:
    """Q2. Letter grade: >= 0.9 'A', >= 0.8 'B', >= 0.7 'C', >= 0.6 'D', else 'F'.
    A score outside 0..1 returns 'Bad score'."""
    if not 0 <= score <= 1:
        return "Bad score"
    if score >= 0.9:
        return "A"
    if score >= 0.8:
        return "B"
    if score >= 0.7:
        return "C"
    if score >= 0.6:
        return "D"
    return "F"


def parse_number(raw: str) -> float | None:
    """Q3. Turn user input like ' 42 ' or '3.5' into a float. Return None if it isn't a number."""
    try:
        return float(raw)
    except ValueError:
        return None


def celsius_to_fahrenheit(c: float) -> float:
    """Q4. F = C * 9/5 + 32, rounded to one decimal place."""
    return round(c * 9 / 5 + 32, 1)


if __name__ == "__main__":
    assert compute_pay(35, 10) == 350
    assert compute_pay(45, 10) == 475
    assert compute_pay(-1, 10) == 0
    assert [grade(s) for s in (0.95, 0.85, 0.75, 0.65, 0.5)] == ["A", "B", "C", "D", "F"]
    assert grade(0.9) == "A" and grade(1.2) == "Bad score" and grade(-0.1) == "Bad score"
    assert parse_number(" 42 ") == 42.0 and parse_number("3.5") == 3.5
    assert parse_number("forty") is None and parse_number("") is None
    assert celsius_to_fahrenheit(100) == 212.0 and celsius_to_fahrenheit(-40) == -40.0
    assert celsius_to_fahrenheit(21.5) == 70.7
    print("all good")
