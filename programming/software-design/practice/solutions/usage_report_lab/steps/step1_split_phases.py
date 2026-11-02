"""Step 1: extract functions and split parsing, aggregation and rendering.

No behaviour change, bugs and globals included. Render to one string, then send
that string to two places, so the duplicated print and write branches collapse.
"""
import json
import sys

OUT = "report_out.txt"
seen = []
TOTAL = 0


def read_rows(path, dedupe):
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
                yield row


def call_cost(model, prompt, completion):
    if model == "atlas-large":
        return prompt / 1000 * 0.015 + completion / 1000 * 0.075
    if model == "atlas-medium":
        return prompt / 1000 * 0.003 + completion / 1000 * 0.015
    if model == "atlas-small" or model == "atlas-small-2":
        return prompt / 1000 * 0.0008 + completion / 1000 * 0.004
    return prompt / 1000 * 0.001 + completion / 1000 * 0.002


def aggregate(rows):
    global TOTAL
    by_model = {}
    latencies = []
    for row in rows:
        cost = call_cost(row["model"], row["prompt_tokens"], row["completion_tokens"])
        entry = by_model.setdefault(row["model"], [0, 0, 0, 0.0])
        entry[0] += 1
        entry[1] += row["prompt_tokens"]
        entry[2] += row["completion_tokens"]
        entry[3] += cost
        TOTAL += cost
        latencies.append(row["latency_ms"])
    return by_model, latencies


def p95(latencies):
    if not latencies:
        return 0
    return sorted(latencies)[int(len(latencies) * 0.95)]


def render_full(by_model, calls, latency, show_cost):
    out = ["model            calls   prompt   compl     cost"]
    for name in sorted(by_model, key=lambda k: -by_model[k][3]):
        v = by_model[name]
        row = "%-15s %6d %8d %7d" % (name, v[0], v[1], v[2])
        out.append(row + (" %8.4f" % v[3] if show_cost else ""))
    out.append("calls: %d" % calls)
    out.append("p95 latency: %d ms" % latency)
    if show_cost:
        out.append("total: %.4f" % TOTAL)
    return "\n".join(out) + "\n"


def render_summary(calls, show_cost):
    if show_cost:
        return "calls: %d total: %.4f\n" % (calls, TOTAL)
    return "calls: %d\n" % calls


def report(path, mode="full", show_cost=True, write=False, dedupe=True):
    by_model, latencies = aggregate(read_rows(path, dedupe))
    calls = len(latencies)
    if mode == "full":
        text = render_full(by_model, calls, p95(latencies), show_cost)
    elif mode == "summary":
        text = render_summary(calls, show_cost)
    else:
        print("bad mode", file=sys.stderr)
        return None
    print(text, end="")
    if write:
        with open(OUT, "w") as out:
            out.write(text)
    return round(TOTAL, 4)
