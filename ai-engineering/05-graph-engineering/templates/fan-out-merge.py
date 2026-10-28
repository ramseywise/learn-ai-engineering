"""Fan-out / merge with Send and a reducer (notes/03).

plan -> N x review_item (parallel, via Send) -> synthesize -> END

Remove the reducer on `findings` and run with two or more items to see
InvalidUpdateError: parallel writes to one key with no merge rule.

pip install langgraph
"""
from typing import Annotated, TypedDict
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

MAX_FANOUT = 20  # cap N (notes/07: unbounded fan-out)


class State(TypedDict):
    items: list[str]
    findings: Annotated[list[str], operator.add]  # many writers, merged by append
    summary: str


class ItemInput(TypedDict):
    item: str


def plan(state: State) -> dict:
    return {}  # e.g. retrieve or list the items to review


def fan_out(state: State) -> list[Send]:
    return [Send("review_item", {"item": x}) for x in state["items"][:MAX_FANOUT]]


def review_item(inp: ItemInput) -> dict:
    # Each instance gets only its own input. Replace with a model call.
    return {"findings": [f"{inp['item']}: ok"]}


def synthesize(state: State) -> dict:
    return {"summary": f"{len(state['findings'])} findings"}


builder = StateGraph(State)
builder.add_node("plan", plan)
builder.add_node("review_item", review_item)
builder.add_node("synthesize", synthesize)
builder.add_edge(START, "plan")
builder.add_conditional_edges("plan", fan_out, ["review_item"])
builder.add_edge("review_item", "synthesize")
builder.add_edge("synthesize", END)
graph = builder.compile()

if __name__ == "__main__":
    out = graph.invoke({"items": ["a.py", "b.py", "c.py"], "findings": []})
    print(out["summary"], out["findings"])
