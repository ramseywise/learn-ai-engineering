"""Note 01: the research agent with no framework. A text protocol, a regex and a loop."""
import re

from research_lab import Final, Observation, decide, read_source, search

PROMPT = """You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer.
Use Thought to describe your reasoning about the question.
Use Action to run one of the actions available to you, then return PAUSE.
Observation will be the result of running that action.

Your available actions are:
search:
e.g. search: why agents loop
read_source:
e.g. read_source: wang-2025
"""
KNOWN_ACTIONS = {"search": search, "read_source": read_source}
ACTION_RE = re.compile(r"^Action: (\w+): (.*)$")
ARG_NAME = {"search": "query", "read_source": "source_id"}


def text_model(messages: list[dict], behavior: str = "normal") -> str:
    """Stands in for a completion call: reads the transcript, writes ReAct text."""
    question = next(m["content"] for m in messages if m["role"] == "user")
    observations, pending = [], None
    for m in messages:
        match = ACTION_RE.search(m["content"].split("\nPAUSE")[0].split("\n")[-1]) if m["role"] == "assistant" else None
        if match:
            pending = match.groups()
        if m["role"] == "user" and m["content"].startswith("Observation: ") and pending:
            observations.append(Observation(pending[0], {ARG_NAME[pending[0]]: pending[1]},
                                            m["content"].removeprefix("Observation: ")))
    step = decide(question, observations, behavior)
    if isinstance(step, Final):
        return f"Answer: {step.text}"
    return f"Thought: {step.thought}\nAction: {step.name}: {next(iter(step.args.values()))}\nPAUSE"


def query(question: str, max_turns: int = 6, model=text_model, verbose: bool = True) -> str | None:
    """Parse Action lines, dispatch, feed back the observation, stop on no action."""
    messages = [{"role": "system", "content": PROMPT}, {"role": "user", "content": question}]
    for _ in range(max_turns):
        reply = model(messages)
        messages.append({"role": "assistant", "content": reply})
        actions = [m for m in map(ACTION_RE.match, reply.split("\n")) if m]
        if not actions:
            if verbose:
                print(reply)
            return reply
        name, arg = actions[0].groups()
        if name not in KNOWN_ACTIONS:
            observation = f"ERROR: no action named {name}"
        else:
            observation = KNOWN_ACTIONS[name](arg)
        if verbose:
            print(f"{name}({arg[:50]}) -> {observation[:50]!r}")
        messages.append({"role": "user", "content": f"Observation: {observation}"})
    return None


if __name__ == "__main__":
    from research_lab import QUESTION
    query(QUESTION)
