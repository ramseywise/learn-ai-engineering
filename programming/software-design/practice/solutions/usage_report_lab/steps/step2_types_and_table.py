"""Step 2: name the data, and make prices a table rather than a branch per model.

Still no behaviour change. The `report` signature stays, with its flags, because
callers use it. The globals stay too: removing them changes behaviour, which is step 3.
"""
import json
import sys
from dataclasses import dataclass

OUT = "report_out.txt"
seen = []
TOTAL = 0


@dataclass(frozen=True)
class Price:
    """Currency units per 1,000 tokens. All prices in this lab are invented."""

    prompt: float
    completion: float


PRICES = {
    "atlas-large": Price(0.015, 0.075),
    "atlas-medium": Price(0.003, 0.015),
    "atlas-small": Price(0.0008, 0.004),
    "atlas-small-2": Price(0.0008, 0.004),
}
DEFAULT_PRICE = Price(0.001, 0.002)


@dataclass(frozen=True)
class Call:
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int


@dataclass
class ModelUsage:
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0


def read_calls(path, dedupe):
    with open(path) as lines:
        for line in lines:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if dedupe:
                if row["id"] in seen:
                    continue
                seen.append(row["id"])
            if row.get("status") == "ok":
                yield Call(row["model"], row["prompt_tokens"], row["completion_tokens"], row["latency_ms"])


def call_cost(call):
    price = PRICES.get(call.model, DEFAULT_PRICE)
    return call.prompt_tokens / 1000 * price.prompt + call.completion_tokens / 1000 * price.completion


def aggregate(calls):
    global TOTAL
    by_model = {}
    latencies = []
    for call in calls:
        cost = call_cost(call)
        usage = by_model.setdefault(call.model, ModelUsage())
        usage.calls += 1
        usage.prompt_tokens += call.prompt_tokens
        usage.completion_tokens += call.completion_tokens
        usage.cost += cost
        TOTAL += cost
        latencies.append(call.latency_ms)
    return by_model, latencies


def p95(latencies):
    if not latencies:
        return 0
    return sorted(latencies)[int(len(latencies) * 0.95)]


def render_full(by_model, calls, latency, total, show_cost):
    out = ["model            calls   prompt   compl     cost"]
    for name, usage in sorted(by_model.items(), key=lambda kv: -kv[1].cost):
        row = f"{name:<15} {usage.calls:6d} {usage.prompt_tokens:8d} {usage.completion_tokens:7d}"
        out.append(row + (f" {usage.cost:8.4f}" if show_cost else ""))
    out.append(f"calls: {calls}")
    out.append(f"p95 latency: {latency} ms")
    if show_cost:
        out.append(f"total: {total:.4f}")
    return "\n".join(out) + "\n"


def render_summary(calls, total, show_cost):
    return f"calls: {calls} total: {total:.4f}\n" if show_cost else f"calls: {calls}\n"


def report(path, mode="full", show_cost=True, write=False, dedupe=True):
    by_model, latencies = aggregate(read_calls(path, dedupe))
    calls = len(latencies)
    if mode == "full":
        text = render_full(by_model, calls, p95(latencies), TOTAL, show_cost)
    elif mode == "summary":
        text = render_summary(calls, TOTAL, show_cost)
    else:
        print("bad mode", file=sys.stderr)
        return None
    print(text, end="")
    if write:
        with open(OUT, "w") as out:
            out.write(text)
    return round(TOTAL, 4)
