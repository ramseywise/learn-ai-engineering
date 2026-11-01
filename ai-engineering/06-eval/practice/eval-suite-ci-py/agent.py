"""The system under test: a support agent with two tools. The stub is rule-based and reads the
same system prompt a model would, so deleting a line from the prompt changes behaviour."""
from __future__ import annotations

import json
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

KB = json.loads((Path(__file__).parent / "../eval-suite-ci/kb.json").read_text())


@dataclass
class Run:
    text: str
    tools: list[str]
    tokens: int


Agent = Callable[[str, str], Run]


# The tool bodies, shared by the stub and the real model.
def search_docs(query: str) -> dict | None:
    q = query.lower()
    return next((d for d in KB["docs"] if any(k in q for k in d["keywords"])), None)


def lookup_order(order_id: str) -> str:
    return KB["orders"].get(order_id, "not found")


def stub_agent(system: str, user: str) -> Run:
    done = lambda text, tools: Run(text, tools, math.ceil((len(system) + len(user) + len(text)) / 4))
    if re.search(r"ignore (all|your|previous) instructions", user, re.I):
        return done("I can't do that, but I can help with your own account." if "Ignore instructions" in system else "Refund approved for all customers.", [])
    order = re.search(r"order (\d+)", user, re.I)
    if order:
        if "lookup_order" not in system:
            return done("Your order should arrive soon.", [])
        return done(f"Order {order.group(1)} is {lookup_order(order.group(1))}.", ["lookup_order"])
    doc = search_docs(user)
    if not doc:
        return done("I don't know. A person will follow up." if "say you don't know" in system else "You can do that under Settings.", [])
    body = " ".join(doc["text"].split(" ")[:10]) if "under ten words" in system else doc["text"]
    return done(f"{body} [{doc['id']}]", ["search_docs"])


def real_agent(model: str) -> Agent:
    """The real path: a manual tool loop, so the trajectory is recorded exactly as the grader needs it."""
    import anthropic

    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY or an `ant auth login` profile
    tools = [
        {"name": "search_docs", "description": "Search the help documents. Returns the best match, or nothing.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "lookup_order", "description": "Get an order's status by its numeric id.", "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}},
    ]

    def run(system: str, user: str) -> Run:
        messages: list[dict] = [{"role": "user", "content": user}]
        used: list[str] = []
        tokens = 0
        for _ in range(6):
            res = client.messages.create(model=model, max_tokens=16000, system=system, tools=tools, messages=messages)
            tokens += res.usage.input_tokens + res.usage.output_tokens
            if res.stop_reason == "refusal":
                return Run(f"model refused: {res.stop_details.category if res.stop_details else 'unknown'}", used, tokens)
            text = "".join(b.text for b in res.content if b.type == "text")
            if res.stop_reason != "tool_use":
                return Run(text, used, tokens)
            messages.append({"role": "assistant", "content": res.content})
            results = []
            for b in res.content:
                if b.type != "tool_use":
                    continue
                used.append(b.name)
                if b.name == "search_docs":
                    d = search_docs(b.input["query"])
                    content = f"[{d['id']}] {d['text']}" if d else "no match"
                else:
                    content = lookup_order(b.input["order_id"])
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": content})
            messages.append({"role": "user", "content": results})  # all results in one message
        return Run("", used, tokens)

    return run


def choose_agent() -> tuple[str, Agent]:
    model = os.environ.get("MODEL")
    return (model, real_agent(model)) if model else ("stub", stub_agent)
