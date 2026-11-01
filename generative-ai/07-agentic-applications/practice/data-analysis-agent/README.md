# Data-analysis-agent lab

An analysis agent over real datasets: read-only SQL and pandas tools, profiling, a validator that recomputes each claim, and charts. A scripted stub model plays the LLM, so it needs no API key. The chapter is [notes/05-data-analysis-agent.md](../../notes/05-data-analysis-agent.md).

## Run it

```bash
uv run --with pandas --with matplotlib python run.py            # every analysis
uv run --with pandas --with matplotlib python run.py tip_share  # one of them
uv run --with pandas --with matplotlib python -m unittest test_agent  # 15 tests
```

Charts are written to `out/`.

## Data

Both tables are read in place from the data-analytics pillar, and neither is copied here:

- `tips`: [data-analytics/01-python-for-data-analysis/practice/data/tips.csv](../../../../data-analytics/01-python-for-data-analysis/practice/data/tips.csv)
- `titanic`: [data-analytics/01-python-for-data-analysis/practice/mckinney/datasets/titanic/train.csv](../../../../data-analytics/01-python-for-data-analysis/practice/mckinney/datasets/titanic/train.csv)

If those files move, change the paths in `datasets.py`.

## Files

| File | What it is |
|---|---|
| `datasets.py` | Loads the tables and profiles them |
| `agent.py` | The loop, the tools, the read-only connection and the validator |
| `scripted.py` | The stub model: tool calls per analysis |
| `run.py` | Runs an analysis and prints the transcript |
| `test_agent.py` | Unit tests of the tools and the validator |
| `claude_model.py` | Illustrative: the same interface against Claude. Needs `ANTHROPIC_API_KEY` and the `anthropic` package. It was not run for this course |

## Analyses

| Analysis | Result |
|---|---|
| `tip_share` | Answered in 9 steps, after 2 refused submissions: one with no agreed metric, one that did not state Friday's sample of 19 |
| `titanic_age` | Survivors averaged 28.34 years. The first answer is refused until it says it covers 714 of 891 passengers and describes an association and not a cause |
| `titanic_sex` | Survival 74.2% for women and 18.9% for men; difference .5531, interval [.4935, .6098] |
| `guards` | 10 refused calls, including writes, multiple statements, a runaway query and an unknown table |
