# illustrative: needs ANTHROPIC_API_KEY and the anthropic package, and costs money to run.
"""Drive the same harness with Claude instead of the scripted model.

    uv run --with anthropic python claude_model.py

create() returns the SDK's response object, whose stop_reason and content blocks are what
run_agent() reads, so no other file changes. Opus 5.5 can decline a request, so this opts in
to the API's server-side fallback, which reruns a declined request on another model.
"""
import sys

import anthropic

sys.dont_write_bytecode = True

from agent import Limits, Workspace, run_agent  # noqa: E402

SYSTEM = (
    "You fix bugs in a small Python repo. Reproduce the failure with run_tests, read the code, "
    "make the smallest general fix, run the tests again, then call finish. Do not edit the tests."
)


class ClaudeModel:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def create(self, messages, tools):
        return self.client.beta.messages.create(
            model="claude-opus-5-5",
            max_tokens=16000,
            system=SYSTEM,
            tools=tools,
            messages=messages,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )


if __name__ == "__main__":
    workspace = Workspace(Limits())
    result = run_agent(ClaudeModel(), workspace, "tests/test_stats.py fails on tipkit.stats.median. Fix it.")
    print(result.status, result.steps)
    if result.status == "finished":
        print("held-out:", workspace.score_heldout())
    workspace.close()
