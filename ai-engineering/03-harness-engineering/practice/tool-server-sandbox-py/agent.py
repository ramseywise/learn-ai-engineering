from __future__ import annotations

import re

from server import Server


def run_scripted(server: Server, plan: list[dict], log=print) -> list[dict]:
    """A scripted stand-in for the model: a fixed plan, including the attacks a real model might be talked into."""
    results = []
    for step in plan:
        r = server.call(step["name"], step["input"])
        text = r["content"][0]["text"]
        log(f"{'BLOCKED' if r.get('isError') else 'ok':<8} {step['why']:<38} {re.sub(r'\s+', ' ', text)[:70]}")
        results.append({**step, "is_error": bool(r.get("isError")), "text": text})
    return results


def run_claude(server: Server, model: str, task: str, max_turns: int = 8) -> str:
    """The real loop: Claude picks the tools. Used only when MODEL is set. Manual, so every step is visible."""
    import anthropic

    client = anthropic.Anthropic()
    tools = [{"name": t.name, "description": t.description, "input_schema": t.input_schema} for t in server.tools]
    messages: list[dict] = [{"role": "user", "content": task}]
    for _ in range(max_turns):
        res = client.messages.create(model=model, max_tokens=16000, tools=tools, messages=messages)
        if res.stop_reason == "refusal":
            return f"model refused: {res.stop_details.category if res.stop_details else 'unknown'}"
        messages.append({"role": "assistant", "content": res.content})
        if res.stop_reason != "tool_use":
            return "".join(b.text for b in res.content if b.type == "text")
        results = []
        for block in res.content:
            if block.type != "tool_use":
                continue
            out = server.call(block.name, block.input)
            print(f"{'BLOCKED' if out.get('isError') else 'ok'} {block.name} {block.input}")
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": out["content"][0]["text"], "is_error": bool(out.get("isError"))})
        messages.append({"role": "user", "content": results})  # all results in one message
    return f"stopped: hit the limit of {max_turns} turns"
