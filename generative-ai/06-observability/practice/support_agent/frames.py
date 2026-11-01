"""Flatten traces into the two tables every dashboard and analysis starts from."""

import pandas as pd


def traces_frame(traces):
    """One row per trace. Scores become columns; a score nobody gave stays NaN."""
    rows = []
    for t in traces:
        llm = [s for s in t.spans if s.model]
        rows.append({
            "trace_id": t.trace_id, "ts": pd.Timestamp(t.ts), "day": t.ts[:10], "release": t.release,
            "route": t.route, "language": t.language, "outcome": t.outcome, "latency_ms": t.latency_ms,
            "cost_usd": t.cost_usd, "input_tokens": sum(s.input_tokens for s in llm),
            "output_tokens": sum(s.output_tokens for s in llm),
            "cache_read_tokens": sum(s.cache_read_tokens for s in llm),
            "cache_write_tokens": sum(s.cache_write_tokens for s in llm),
            "n_spans": len(t.spans) - 1, "seeded_failure": t.seeded_failure, **t.scores,
        })
    return pd.DataFrame(rows)


def spans_frame(traces):
    """One row per span below the root, with the trace fields a group-by needs."""
    rows = []
    for t in traces:
        for s in t.spans[1:]:
            rows.append({
                "trace_id": t.trace_id, "day": t.ts[:10], "release": t.release, "route": t.route,
                "name": s.name, "kind": s.kind, "model": s.model, "latency_ms": s.latency_ms,
                "input_tokens": s.input_tokens, "output_tokens": s.output_tokens,
                "cache_read_tokens": s.cache_read_tokens, "cache_write_tokens": s.cache_write_tokens,
                "cost_usd": s.cost_usd, "level": s.level,
            })
    return pd.DataFrame(rows)
