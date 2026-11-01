"""Run the data-analysis agent offline over the course's datasets. No API key, no network.

    uv run --with pandas --with matplotlib python run.py            # every analysis
    uv run --with pandas --with matplotlib python run.py tip_share  # one analysis
"""
import sys

sys.dont_write_bytecode = True

from agent import HERE, Analyst, Metric, run_agent  # noqa: E402
from datasets import load  # noqa: E402
from scripted import ANALYSES, ScriptedModel  # noqa: E402

METRICS = [
    Metric("tip_share", "tips", "tip", "total_bill", "tip as a fraction of that bill, averaged over bills"),
    Metric("survived", "titanic", "Survived", None, "share of passengers who survived"),
    Metric("age", "titanic", "Age", None, "mean age where age is recorded"),
]


def session() -> Analyst:
    return Analyst({"tips": load("tips"), "titanic": load("titanic")}, METRICS, HERE / "out")


def main(names: list[str]) -> None:
    for name in names or ANALYSES:
        question, script = ANALYSES[name]
        print(f"\n=== {name}: {question}")
        analyst = session()
        result = run_agent(ScriptedModel(script), analyst, question)
        print(f"status={result.status} steps={result.steps} refused={result.rejected}")
        if analyst.answer:
            print(f"answer: {analyst.answer}")


if __name__ == "__main__":
    main(sys.argv[1:])
