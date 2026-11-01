# illustrative: needs ANTHROPIC_API_KEY and the anthropic package, and costs money to run.
"""Ask a real question with Claude in place of the scripted model.

    uv run --with anthropic --with pandas --with matplotlib python claude_model.py "Which day has the largest tip share?"

create() returns the SDK's response, whose stop_reason and content blocks are all run_agent() reads.
Opus 5.5 can decline a request, so this opts in to the API's server-side fallback model.
"""
import sys

import anthropic

sys.dont_write_bytecode = True

from agent import run_agent  # noqa: E402
from run import session  # noqa: E402

SYSTEM = (
    "You answer questions about the tables you can query. Look at the schema and metrics first. "
    "Use only the agreed metrics in claims. Every number in your answer must come from a tool result. "
    "End with submit_answer, and if it is rejected, fix what it names and submit again."
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
    analyst = session()
    result = run_agent(ClaudeModel(), analyst, sys.argv[1])
    print(result.status, analyst.answer)
