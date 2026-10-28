"""Generate-then-verify: the first graph to build (notes/02, notes/05).

generate (LLM) -> validate (code) -> review (LLM) -> END, or back to generate
with feedback, bounded at MAX_ATTEMPTS.

pip install langgraph langchain-anthropic
"""
from typing import Annotated, TypedDict
import operator

from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

MAX_ATTEMPTS = 3
model = ChatAnthropic(model="claude-sonnet-5-5", temperature=0)


class State(TypedDict):
    task: str
    draft: str                                    # one writer: generate
    feedback: Annotated[list[str], operator.add]  # validate and review both append
    attempts: int
    verdict: str                                  # one writer: review


def generate(state: State) -> dict:
    notes = "\n".join(state.get("feedback", [])) or "none"
    prompt = f"Task:\n{state['task']}\n\nFeedback on earlier attempts:\n{notes}"
    return {"draft": model.invoke(prompt).content,
            "attempts": state.get("attempts", 0) + 1}


def validate(state: State) -> dict:
    # Deterministic checks first: cheaper and more reliable than a model.
    # Replace with a schema check, a test run, a linter.
    problems = []
    if not state["draft"].strip():
        problems.append("validator: draft is empty")
    return {"feedback": problems, "verdict": "fail" if problems else ""}


def review(state: State) -> dict:
    # The reviewer sees the task and the output, not the generator's reasoning (notes/07).
    prompt = (f"Task:\n{state['task']}\n\nOutput:\n{state['draft']}\n\n"
              "Reply PASS, or FAIL followed by one line saying what to fix.")
    reply = model.invoke(prompt).content.strip()
    if reply.startswith("PASS"):
        return {"verdict": "pass"}
    return {"verdict": "fail", "feedback": [f"reviewer: {reply}"]}


def after_validate(state: State) -> str:
    if state["verdict"] != "fail":
        return "review"
    return "generate" if state["attempts"] < MAX_ATTEMPTS else END


def after_review(state: State) -> str:
    if state["verdict"] == "pass" or state["attempts"] >= MAX_ATTEMPTS:
        return END
    return "generate"


builder = StateGraph(State)
builder.add_node("generate", generate)
builder.add_node("validate", validate)
builder.add_node("review", review)
builder.add_edge(START, "generate")
builder.add_edge("generate", "validate")
builder.add_conditional_edges("validate", after_validate)
builder.add_conditional_edges("review", after_review)
graph = builder.compile(checkpointer=InMemorySaver())

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "gtv-1"}}
    result = graph.invoke({"task": "Write a haiku about state machines."}, config)
    print(result["verdict"], result["attempts"])
    print(result["draft"])
