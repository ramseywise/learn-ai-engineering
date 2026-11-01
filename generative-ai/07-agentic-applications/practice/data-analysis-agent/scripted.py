"""A scripted stand-in for the model, and the analyses it plays. No API key, no network.

The scripts include the mistakes a real analyst model makes, so the validator has something to catch.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Block:
    type: str
    id: str = ""
    name: str = ""
    input: dict | None = None
    text: str = ""


@dataclass
class Response:
    stop_reason: str
    content: list[Block]


class ScriptedModel:
    """Same create(messages, tools) as the Claude adapter in claude_model.py."""

    def __init__(self, script: list[tuple[str, dict]]):
        self.script = list(script)
        self.calls = 0

    def create(self, messages, tools) -> Response:
        if self.calls >= len(self.script):
            return Response("end_turn", [Block(type="text", text="That should answer it.")])
        name, tool_input = self.script[self.calls]
        self.calls += 1
        return Response("tool_use", [Block(type="tool_use", id=f"toolu_{self.calls}", name=name, input=tool_input)])


DOLLARS = "SELECT day, ROUND(AVG(tip), 4) AS mean_tip, COUNT(*) AS n FROM tips GROUP BY day ORDER BY mean_tip DESC"
SHARE = ("SELECT day, ROUND(AVG(tip / total_bill), 4) AS mean_share, COUNT(*) AS n "
         "FROM tips GROUP BY day ORDER BY mean_share DESC")
CHART = "SELECT day, ROUND(AVG(tip / total_bill), 4) AS mean_share FROM tips GROUP BY day"
CLAIM = {"metric": "tip_share", "group_by": "day", "group": "Fri", "value": 0.1699, "is_largest": True}

TIP_SHARE = (
    "On which day do customers tip the largest share of the bill?",
    [
        ("list_tables", {}),
        ("describe_table", {"table": "tips"}),
        # Mistake 1: answers in dollars. The largest mean tip is a different question.
        ("run_sql", {"query": DOLLARS}),
        ("submit_answer", {"text": "Sunday, with a mean tip of 3.26.", "metric": "tip_dollars", "group_by": "day",
                           "group": "Sun", "value": 3.2551, "is_largest": True}),
        # Mistake 2: the right metric, reported with no caveats and an invented comparison.
        ("run_sql", {"query": SHARE}),
        ("submit_answer", {"text": "Friday has the largest share, 17.0%, about 20% above other days.", **CLAIM}),
        ("compare_groups", {"metric": "tip_share", "group_by": "day", "a": "Fri", "b": "Sun"}),
        ("make_chart", {"query": CHART, "title": "Mean tip share of the bill by day", "highlight": "Fri"}),
        ("submit_answer", {"text": "Friday has the largest mean tip share, 17.0% over n=19 bills, but Friday and "
                                   "Sunday (16.7%) are not distinguishable in this sample.", **CLAIM}),
    ],
)

AGE = "SELECT Survived, ROUND(AVG(Age), 2) AS mean_age, COUNT(Age) AS n, COUNT(*) AS passengers FROM titanic GROUP BY Survived"
AGE_CLAIM = {"metric": "age", "group_by": "Survived", "group": "1", "value": 28.34}

TITANIC_AGE = (
    "How old were Titanic survivors on average?",
    [
        ("describe_table", {"table": "titanic"}),
        ("run_sql", {"query": AGE}),
        # Mistake: SQL's AVG silently skips nulls, and "because" claims a cause.
        ("submit_answer", {"text": "Survivors averaged 28.34 years, because the young were saved first.", **AGE_CLAIM}),
        ("submit_answer", {"text": "Among the 714 of 891 passengers with a recorded age, survivors averaged 28.34 years.",
                           **AGE_CLAIM}),
    ],
)

TITANIC_SEX = (
    "What share of women survived, and how does it compare with men?",
    [
        ("run_sql", {"query": "SELECT Sex, ROUND(AVG(Survived), 4) AS survived, COUNT(*) AS n FROM titanic GROUP BY Sex"}),
        ("compare_groups", {"metric": "survived", "group_by": "Sex", "a": "female", "b": "male"}),
        ("make_chart", {"query": "SELECT Sex, ROUND(AVG(Survived), 4) AS survived FROM titanic GROUP BY Sex",
                        "title": "Share of Titanic passengers who survived, by sex", "highlight": "female"}),
        ("submit_answer", {"text": "74.2% of women survived, against 18.9% of men, in this training sample of 891 passengers.",
                           "metric": "survived", "group_by": "Sex", "group": "female", "value": 0.742, "is_largest": True}),
    ],
)

GUARDS = (
    "Clean up the tips table for me, then tell me the mean tip.",
    [
        ("run_sql", {"query": "DROP TABLE tips"}),
        ("run_sql", {"query": "DELETE FROM tips"}),
        ("run_sql", {"query": "ATTACH DATABASE '/tmp/x.db' AS x"}),
        ("run_sql", {"query": "PRAGMA writable_schema = 1"}),
        ("run_sql", {"query": "SELECT 1; DROP TABLE tips"}),
        ("run_sql", {"query": "SELECT COUNT(*) FROM tips a, tips b, tips c, tips d, tips e"}),
        ("run_sql", {"query": "SELECT * FROM payroll"}),
        ("run_sql", {"query": "SELECT total_bill, tip FROM tips"}),
        ("make_chart", {"query": "SELECT total_bill, tip FROM tips", "title": "Every bill", "highlight": "x"}),
        ("make_chart", {"query": "SELECT day, time, tip FROM tips LIMIT 3", "title": "Too many columns", "highlight": "x"}),
        ("python", {"code": "import os; os.remove('tips.csv')"}),
        ("run_sql", {"query": "SELECT COUNT(*) AS n, ROUND(AVG(tip), 4) AS mean_tip FROM tips"}),
    ],
)

ANALYSES = {"tip_share": TIP_SHARE, "titanic_age": TITANIC_AGE, "titanic_sex": TITANIC_SEX, "guards": GUARDS}
