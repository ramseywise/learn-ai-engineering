---
origin: langfuse-mcp-python-main
sources:
  - https://github.com/Log-LogN/langfuse-mcp-python (README.md, src/langfuse_mcp_python/server.py, core/base_tool.py, integrations/langfuse_client.py, tools/) — MIT, © 2026 LogLogN, v1.0.0
  - https://modelcontextprotocol.io/
  - https://langfuse.com/docs/api-and-data-platform/features/public-api
confidence: high
cleaned: 2026-10-31
---
# 4 — A Langfuse MCP Server

> Put your observability platform behind MCP and the agent that writes code can also read its own traces: "which agent got slower since yesterday, and show me the worst trace". This note dissects a 34-tool community server: transports, the tool base class, caching, retries, rate limiting, and the read-only-key rule.

Source: *langfuse-mcp-python* (Log-LogN, MIT). MCP itself is covered in [ai-engineering/02-context-engineering 09 — protocols](../../../ai-engineering/02-context-engineering/notes/09-protocols.md); how to build an MCP server in general is the `mcp-builder` skill. This note is the observability use.

---

## Why an MCP server for traces

| Without | With |
|---|---|
| Open the Langfuse UI, filter, click through, copy into chat | The assistant calls `watch_agents`, then `get_trace` on the outlier |
| Export to CSV for cost questions | `get_cost_metrics` grouped by model or agent |
| Write a script to submit human scores | `submit_score` from the conversation |
| Separate dashboards per framework | One query surface over whatever sends to Langfuse |

It closes a loop: the agent you develop with can inspect the agents you ship.

---

## Running it

| Transport | Command | Use |
|---|---|---|
| stdio (default) | `uvx --python 3.11 langfuse-mcp-python` or `python -m langfuse_mcp_python` | Claude Desktop, Cursor, Claude Code: the client spawns the process |
| Streamable HTTP | `python -m langfuse_mcp_python --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp` | Shared server for a team |
| SSE | `python -m langfuse_mcp_python --transport sse --host 127.0.0.1 --port 8000` | Older clients |

Flags: `--no-rate-limit`, `--json-response`, `--stateless`, `--stats`. Env equivalents: `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT`, `MCP_PATH`.

```json
// Claude Desktop: claude_desktop_config.json
{
  "mcpServers": {
    "langfuse-monitor": {
      "command": "uvx",
      "args": ["--python", "3.11", "langfuse-mcp-python"],
      "env": {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-...",
        "LANGFUSE_SECRET_KEY": "sk-lf-...",
        "LANGFUSE_HOST": "https://cloud.langfuse.com"
      }
    }
  }
}
```

```bash
# Claude Code equivalent (stdio)
claude mcp add langfuse-monitor \
  -e LANGFUSE_PUBLIC_KEY=pk-lf-... -e LANGFUSE_SECRET_KEY=sk-lf-... \
  -e LANGFUSE_HOST=https://cloud.langfuse.com \
  -- uvx --python 3.11 langfuse-mcp-python
```

### What the server expects in your traces

Filtering by agent relies on metadata your app writes. The README's LangGraph example:

```python
# Instrumentation the server's filters assume
from langfuse.langchain import CallbackHandler
handler = CallbackHandler()
app.invoke({"input": "user query"},
           config={"callbacks": [handler],
                   "metadata": {"agent_name": "planner_agent", "version": "v2"}})
```

No `agent_name` in metadata, no per-agent views. This is the same point as the trace schema in [note 05](05-support-agent-observability.md): the queries you can ask later are fixed by what you log now.

---

## Architecture

```
MCP client (Claude, Cursor)
   │  list_tools / call_tool  (stdio | streamable-http | sse)
   ▼
EnhancedLangfuseMonitoringServer
   ├─ Server("langfuse-monitoring-enhanced")   MCP SDK low-level server
   ├─ InMemoryCache(default_ttl=300)            5-minute response cache
   ├─ MetricsCollector                          per-tool p50 / p95 / avg latency (--stats)
   └─ tools{name → BaseLangfuseTool}            34 tools
          │
          ▼
   EnhancedLangfuseClient
   ├─ RateLimiter(60/min, token bucket)
   ├─ httpx pool: 100 connections, 20 keep-alive, 30 s timeout
   └─ Langfuse SDK + public REST API
```

```python
# Registration pattern (server.py, simplified)
@server.list_tools()
async def list_tools():
    return [t.definition for t in tools.values()]        # name, description, inputSchema

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        text = await tools[name].execute(arguments)
    except Exception as e:
        text = f"Error: {e}"                             # errors return as text, not exceptions
    return [TextContent(type="text", text=text)]
```

Returning errors as text lets the model read the message and retry with different arguments, instead of the client surfacing a protocol error.

### The tool base class

| Helper on `BaseLangfuseTool` | What it does |
|---|---|
| `_fetch_with_retry` | tenacity: 3 attempts, exponential backoff 2–10 s, on `httpx.RequestError` / `HTTPStatusError` |
| `_get_cached_or_fetch` | Key → cache (300 s TTL) or fetch |
| `_fetch_all_paginated` | Page/limit pagination, 100 per page, cap 100 pages |
| `_fetch_all_cursor_paginated` | Cursor-based endpoints |
| `_calculate_trace_metrics` | Latency, `usage.total` tokens, `total_cost` / `calculatedTotalCost`, observation count |
| `_get_trace_status` | Status from observation `level` (ERROR / WARNING) |
| Formatting helpers | Markdown tables the model can read |

```python
# One tool: schema + execute (watch_agents.py, abridged)
Tool(
    name="watch_agents",
    description="Monitor active agents in real-time with performance metrics.",
    inputSchema={"type": "object", "properties": {
        "time_window": {"type": "string", "enum": ["last_1h", "last_24h", "last_7d"],
                        "default": "last_1h"},
        "agent_names": {"type": "array", "items": {"type": "string"}},
        "session_ids": {"type": "array", "items": {"type": "string"}},
        "user_id": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "summary_only": {"type": "boolean", "default": False},
        "include_tokens": {"type": "boolean"},
        "limit": {"type": "integer", "default": 10}}})

async def execute(self, args):
    hours = {"last_1h": 1, "last_24h": 24, "last_7d": 168}[args.get("time_window", "last_1h")]
    end = datetime.now(timezone.utc); start = end - timedelta(hours=hours)
    fetch_args = {"from_timestamp": start, "to_timestamp": end}   # server-side filtering
    ...
```

Design points worth copying into any MCP server you write:

| Point | Why |
|---|---|
| Enums for time windows, not free-text dates | The model can't produce an invalid range |
| `summary_only` / `include_tokens` switches | The caller controls how much text comes back: tool output is context |
| Server-side filters, then a `limit` | Don't pull 10k traces to show 10 |
| Cache with a short TTL | Agents ask the same question several times in one session |
| Rate limiter in the client | One chatty agent can't exhaust the Langfuse API quota |

### Client details

| Detail | Behaviour |
|---|---|
| Credential check | Keys must start `pk-lf-` / `sk-lf-` |
| Host | `LANGFUSE_BASE_URL` beats `LANGFUSE_HOST` |
| Metrics | `client.api.legacy.metrics_v1.metrics(query=json.dumps(query))` with `view`, `dimensions`, `metrics`, `filters`, time range, `granularity` |

---

## The 34 tools

| Group | Tools | Writes? |
|---|---|---|
| Monitoring | `watch_agents`, `get_trace`, `analyze_performance`, `get_cost_metrics`, `get_metrics` | No |
| Scores | `get_scores`, `submit_score`, `get_score_configs` | `submit_score` |
| Prompts | `get_prompts`, `create_prompt`, `delete_prompt` | Yes |
| Sessions | `get_sessions` | No |
| Datasets | `get_datasets`, `create_dataset`, `create_dataset_item` | Yes |
| Models (pricing) | `get_models`, `create_model`, `delete_model` | Yes |
| Comments | `get_comments`, `add_comment` | `add_comment` |
| Traces | `delete_trace` | **Destructive** |
| Annotation queues | `get_annotation_queues`, `create_annotation_queue`, `get_queue_items`, `resolve_queue_item` | Yes |
| Blob storage | `get_blob_storage_integrations`, `upsert_…`, `get_…_status`, `delete_…` | Yes |
| LLM connections | `get_llm_connections`, `upsert_llm_connection` | Yes (holds provider keys) |
| Projects | `get_projects`, `create_project`, `update_project`, `delete_project` | **Destructive**, org-level |

Roughly half the surface writes, and some of it deletes data or touches provider credentials. An agent with this server and an admin key can delete traces or projects on a misread instruction.

| Risk control | How |
|---|---|
| Least privilege | Project-scoped keys; read-only where Langfuse supports it |
| Trim the tool list | Fork and register only the monitoring, scores and datasets groups; fewer tools also means better tool selection |
| Client-side approval | Require confirmation for `delete_*`, `upsert_llm_connection`, project tools |
| Data in traces | Mask PII at instrumentation time; anything in a trace can now reach a model |

---

## Workflows from the README

| Workflow | Tool sequence |
|---|---|
| Daily health check | `watch_agents(time_window="last_24h")` → `analyze_performance` → `get_metrics` → `get_trace` on the worst |
| Optimisation cycle | Ship with `metadata.version`; compare versions with `analyze_performance`; drill into regressions |
| Cost control | `get_cost_metrics` by model and agent → find the expensive path → `get_trace` to see why |
| Human review | `get_annotation_queues` → `get_queue_items` → read trace → `submit_score` → `resolve_queue_item` |

The human-review loop is the same one note 03 feeds: judge pipeline flags traces, a person resolves them, and the scores land back in Langfuse.

---

## Labs

| Lab | Where | Runs |
|---|---|---|
| Install and connect | [upstream README](https://github.com/Log-LogN/langfuse-mcp-python#readme) | Needs a Langfuse project (cloud or self-hosted) and its keys; Python ≥ 3.11 |
| Read-only exploration | Register only `watch_agents`, `get_trace`, `get_metrics` | Safe against a production project with a read-only key |

---

→ Next: [05-support-agent-observability.md](05-support-agent-observability.md) — a worked example: the trace schema, experiment metadata and promotion policy for a support agent running on two frameworks.
