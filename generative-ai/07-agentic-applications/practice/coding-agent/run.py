"""Run the coding agent offline against the toy repo. No API key, no network.

    uv run python run.py            # every scenario
    uv run python run.py fix        # one scenario
"""
import sys

sys.dont_write_bytecode = True

from agent import Limits, Workspace, run_agent  # noqa: E402
from scripted import SCENARIOS, ScriptedModel  # noqa: E402

TASK = "tests/test_stats.py fails on tipkit.stats.median. Fix the bug, keep the tests as they are."
LIMITS = {"budget": Limits(max_steps=4), "timeout": Limits(test_timeout_s=2.0)}


def main(names: list[str]) -> None:
    for name in names or SCENARIOS:
        print(f"\n=== {name}: {SCENARIOS[name].__doc__.strip()}")
        workspace = Workspace(LIMITS.get(name, Limits()))
        model = ScriptedModel(SCENARIOS[name](workspace.root))
        result = run_agent(model, workspace, TASK)
        print(f"status={result.status} steps={result.steps} refused={result.refused}")
        if result.status == "finished":
            passed, line = workspace.score_heldout()
            print(f"held-out tests: {'pass' if passed else 'FAIL'} ({line})")
        escaped = workspace.outside / "escaped.txt"
        if escaped.exists():
            print(f"file written outside the repo by code under test: {escaped.name} = {escaped.read_text()!r}")
        workspace.close()


if __name__ == "__main__":
    main(sys.argv[1:])
