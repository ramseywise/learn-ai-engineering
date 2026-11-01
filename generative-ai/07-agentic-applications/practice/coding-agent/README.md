# Coding-agent lab

A small coding agent with a read, edit, test loop and sandbox limits, run end to end against a toy repo. A scripted stub model plays the LLM, so it needs no API key and costs nothing. The chapter is [notes/04-coding-agent.md](../../notes/04-coding-agent.md).

## Run it

```bash
uv run python run.py                 # every scenario
uv run python run.py fix guards      # some of them
uv run python -m unittest test_agent # 10 tests
```

Set `PYTHONDONTWRITEBYTECODE=1` to keep `__pycache__` out of the tree.

## Files

| File | What it is |
|---|---|
| `agent.py` | The loop, the tools, the limits and the stopping rules. Each run works on a temporary copy of `toy_repo/` |
| `scripted.py` | The stub model: a list of tool calls per scenario |
| `run.py` | Runs the scenarios you name and prints each transcript |
| `toy_repo/` | The small project with the bug |
| `heldout/` | Tests the agent cannot see, run after it finishes |
| `test_agent.py` | Unit tests of the tools and limits |
| `claude_model.py` | Illustrative: the same interface against Claude. Needs `ANTHROPIC_API_KEY` and the `anthropic` package. It was not run for this course |

## Scenarios

| Scenario | What happens |
|---|---|
| `fix` | Finishes in 5 steps and passes the held-out tests |
| `overfit` | Finishes with visible tests green and fails the held-out tests |
| `guards` | 15 steps with 9 refused calls: paths outside the repo, a tool that does not exist, editing tests, blind, ambiguous, stale and unparseable edits, and an early `finish` |
| `timeout` | A hanging command is killed after 2 s, and the agent recovers |
| `loop` | A repeated call is refused the third time and halted the fourth |
| `budget` | Stops with `step_limit` at 4 |
| `giveup` | Stops with `stopped_without_finish:end_turn` |
| `escape` | Writes `escaped.txt` outside the repo through a subprocess |

The `escape` scenario is a demonstration of an honest limit. Path checks guard the file tools only, so anything run as a subprocess needs an operating-system sandbox, which this lab does not provide. Do not point it at a repository you care about.
