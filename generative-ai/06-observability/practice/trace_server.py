"""A read-only MCP server over the synthetic traces.

Run it over stdio:  uv run --no-project --with mcp==2.3.0 python trace_server.py
Register it in Claude Code:  claude mcp add support-traces -- uv run --no-project --with mcp==2.3.0 python trace_server.py
"""

from collections import Counter

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from support_agent import generate_traces

TRACES = generate_traces()
BY_ID = {t.trace_id: t for t in TRACES}
READ_ONLY = ToolAnnotations(read_only_hint=True)
MAX_TEXT = 200

server = MCPServer("support-traces", instructions="Read support agent traces. Start with find_traces, then get_trace on an id.")


def _summary(t):
    return {"trace_id": t.trace_id, "ts": t.ts, "route": t.route, "release": t.release, "outcome": t.outcome,
            "latency_ms": t.latency_ms, "cost_usd": round(t.cost_usd, 5)}


@server.tool(annotations=READ_ONLY)
def find_traces(route: str | None = None, release: str | None = None, outcome: str | None = None,
                min_latency_ms: float = 0, limit: int = 10) -> dict:
    """Find traces by route, release, outcome or minimum latency. Returns summaries, slowest first, at most 50."""
    hits = [t for t in TRACES if (route is None or t.route == route) and (release is None or t.release == release)
            and (outcome is None or t.outcome == outcome) and t.latency_ms >= min_latency_ms]
    hits.sort(key=lambda t: -t.latency_ms)
    return {"total": len(hits), "traces": [_summary(t) for t in hits[:min(limit, 50)]]}


@server.tool(annotations=READ_ONLY)
def get_trace(trace_id: str, include_text: bool = False) -> dict:
    """Fetch one trace with its spans and scores. Long text is omitted unless include_text is true."""
    t = BY_ID.get(trace_id)
    if t is None:
        raise ToolError(f"No trace {trace_id!r}. Use find_traces to list ids.")
    spans = [{"name": s.name, "kind": s.kind, "latency_ms": s.latency_ms, "level": s.level, "model": s.model,
              "input_tokens": s.input_tokens, "cache_read_tokens": s.cache_read_tokens,
              "cache_write_tokens": s.cache_write_tokens, "output_tokens": s.output_tokens, "error": s.error}
             for s in t.spans[1:]]
    out = {**_summary(t), "scores": t.scores, "spans": spans}
    if include_text:
        out |= {"question": t.question[:MAX_TEXT], "answer": t.answer[:MAX_TEXT], "citations": t.citations}
    return out


@server.tool(annotations=READ_ONLY)
def tool_errors(release: str | None = None) -> dict:
    """Count spans with WARNING or ERROR level by span name, for one release or all."""
    counts = Counter((s.name, s.level) for t in TRACES if release is None or t.release == release
                     for s in t.spans[1:] if s.level != "DEFAULT")
    return {"counts": [{"span": n, "level": lv, "count": c} for (n, lv), c in counts.most_common()]}


if __name__ == "__main__":
    server.run()
