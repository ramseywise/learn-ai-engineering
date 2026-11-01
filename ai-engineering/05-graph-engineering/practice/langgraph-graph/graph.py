"""A support-triage graph. Every LangGraph primitive the pillar teaches appears once:
reducers, conditional routing, a cycle, Send fan-out, a checkpointer, interrupt and resume."""
from __future__ import annotations

import json
import operator
import re
from pathlib import Path
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send, interrupt

from model import Complete

KB = json.loads((Path(__file__).parent / "kb.json").read_text())
SOURCES = ["docs", "tickets"]
MAX_DRAFTS = 2


class State(TypedDict, total=False):
    ticket: str
    label: str
    reply: str
    drafts: int
    approved: bool
    status: str
    # A reducer says how parallel writes merge. Without one, two searches writing the same key
    # in one step is an error. `operator.add` concatenates, so both results survive.
    evidence: Annotated[list[dict], operator.add]
    trail: Annotated[list[str], operator.add]
    tokens: Annotated[int, operator.add]


def build_graph(complete: Complete, checkpointer, outbox: list[str]):
    def classify(s: State) -> dict:
        res = complete(
            f"<ticket>\n{s['ticket']}\n</ticket>",
            system="CLASSIFY the ticket. Reply with exactly one word: billing, bug or how_to.",
            max_tokens=2000,
        )
        return {"label": res.text.strip(), "trail": ["classify"], "tokens": res.input_tokens + res.output_tokens}

    def fan_out(s: State) -> list[Send]:
        # Send starts one parallel `search` per source, each with its own input.
        return [Send("search", {"ticket": s["ticket"], "source": source}) for source in SOURCES]

    def search(s: dict) -> dict:
        hits = [d for d in KB if d["source"] == s["source"] and any(k in s["ticket"].lower() for k in d["keywords"])]
        return {"evidence": hits, "trail": [f"search:{s['source']}"]}

    def gather(s: State) -> dict:
        return {"trail": ["gather"]}  # the join: runs once, after every search has finished

    def after_gather(s: State) -> str:
        return "draft" if s.get("evidence") else "escalate"

    def draft(s: State) -> dict:
        docs = "\n".join(f"[{d['id']}] {d['text']}" for d in sorted(s["evidence"], key=lambda d: d["id"]))
        retry = "\n\nYour last draft cited nothing. Cite a document id in square brackets." if s.get("drafts") else ""
        res = complete(
            f"<ticket>\n{s['ticket']}\n</ticket>\n\n<documents>\n{docs}\n</documents>{retry}",
            system="DRAFT a one-sentence reply from the documents only.",
            max_tokens=2000,
        )
        return {"reply": res.text.strip(), "drafts": s.get("drafts", 0) + 1, "trail": ["draft"], "tokens": res.input_tokens + res.output_tokens}

    def check(s: State) -> dict:
        return {"trail": ["check"]}

    def after_check(s: State) -> str:
        """Deterministic: the draft must cite evidence that was actually retrieved."""
        cited = set(re.findall(r"\[([\w-]+)\]", s["reply"]))
        if cited & {d["id"] for d in s["evidence"]}:
            return "approve" if s["label"] == "billing" else "send"
        return "draft" if s["drafts"] < MAX_DRAFTS else "escalate"

    def approve(s: State) -> dict:
        # On resume the node re-runs from its first line, and `interrupt` returns the resume value
        # this time. So put no side effect above this call: it would run twice. The decision is a
        # string to match the TypeScript lab, where a falsy resume value is rejected as empty input.
        decision = interrupt({"ticket": s["ticket"], "draft": s["reply"]})
        return {"approved": decision == "approve", "trail": ["approve"]}

    def after_approve(s: State) -> str:
        return "send" if s["approved"] else "escalate"

    def send(s: State) -> dict:
        outbox.append(s["reply"])
        return {"status": "sent", "trail": ["send"]}

    def escalate(s: State) -> dict:
        return {"status": "escalated", "trail": ["escalate"]}

    g = StateGraph(State)
    for name, fn in [("classify", classify), ("search", search), ("gather", gather), ("draft", draft), ("check", check), ("approve", approve), ("send", send), ("escalate", escalate)]:
        g.add_node(name, fn)
    g.add_edge(START, "classify")
    g.add_conditional_edges("classify", fan_out, ["search"])
    g.add_edge("search", "gather")
    g.add_conditional_edges("gather", after_gather, ["draft", "escalate"])
    g.add_edge("draft", "check")
    g.add_conditional_edges("check", after_check, ["approve", "send", "draft", "escalate"])
    g.add_conditional_edges("approve", after_approve, ["send", "escalate"])
    g.add_edge("send", END)
    g.add_edge("escalate", END)
    return g.compile(checkpointer=checkpointer)
