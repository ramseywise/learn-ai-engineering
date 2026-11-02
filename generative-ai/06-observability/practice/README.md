# Practice: the support agent's fortnight

Everything the six chapters print comes from this folder. `support_agent/` is a stubbed invoicing agent with 1,400 synthetic turns from 5 to 18 October 2026, and a real Langfuse SDK client wired to a local fake, so nothing leaves the machine and no key is needed.

| File | What it is |
|---|---|
| `check_blocks.py` | Runs every Python block in `../notes/` as written and compares it to the printed output below it |
| `trace_server.py` | The read-only MCP server from chapter 4, three tools over the synthetic traces |
| `make_dashboard_chart.py` | Renders `../sources/images/support-agent-dashboard.png` for chapter 6 |
| `support_agent/traces.py`, `frames.py` | The trace generator and the flat tables built from it |
| `support_agent/golden.py`, `judges.py`, `scorers.py` | The golden set, the rule-based judge stubs and the online heuristics |
| `support_agent/pricing.py`, `replay.py`, `kb.py` | Model prices, the alert replay and the small knowledge base |
| `support_agent/fakes.py` | Local stand-ins for the Langfuse and Messages APIs, used to exercise blocks marked `# illustrative` |

## Run it

From this folder, check every block in every chapter (about a minute):

```bash
uv run --no-project --with 'langfuse>=5' --with pandas --with numpy --with langgraph --with langchain --with anthropic --with 'mcp>=2' --with matplotlib python check_blocks.py
```

Add a chapter name to check one, for example `... python check_blocks.py 04-langfuse`. Add `--write` to refill the output fences after a deliberate change to the data.

Blocks marked `# illustrative` need a real Anthropic key or Langfuse project in production. Here they run against `support_agent/fakes.py`, which tests their logic and request shapes, and they carry no output fence because a fake's reply is not a result.

Start the MCP server over stdio:

```bash
uv run --no-project --with mcp==2.3.0 python trace_server.py
```

Redraw the dashboard figure:

```bash
uv run --no-project --with pandas --with matplotlib python make_dashboard_chart.py
```

## The numbers are synthetic

The traces, verdicts and token counts are generated with planted failures, so that a chapter can state what the right answer is. They show how the methods behave. They are not measurements of a real agent, and the judges are rule-based stubs rather than model calls.
