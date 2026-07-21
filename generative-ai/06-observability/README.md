# 06 — Observability

> Depth layer. Summary: [interviewing/guides/4-agents](../../interviewing/guides/4-agents/00-overview.md)
> Position: sixth pillar — tracing, scoring, and evaluation pipelines for LLM applications.
> Presumes: [03-agentic-foundations](../03-agentic-foundations/README.md).

---

## What it is

Observability for LLM applications means being able to see what happened inside an agent
run: which tools were called, what the model received, how it responded, and whether the
output was good. LangFuse is the primary tool covered here — it provides tracing,
scoring, dataset management, and LLM-as-judge evaluation pipelines.

This pillar is the gen-AI complement to [ai-engineering/06-eval/](../../ai-engineering/06-eval/README.md),
which covers evaluation methodology and benchmark design. Observability is the
infrastructure; eval is the discipline.

---

## Resource map

### Course material (hands-on)

- **[`Learning-LangFuse-main/`](Learning-LangFuse-main/)** —
  LangFuse basics: instrumentation, tracing, scoring, and the LangFuse UI. Entry point
  for anyone new to LLM observability.
- **[`langfuse-evaluation-main/`](langfuse-evaluation-main/)** —
  evaluation pipelines in LangFuse: golden sets, LLM-as-judge scoring, regression
  tracking across model versions.
- **[`langfuse-mcp-python-main/`](langfuse-mcp-python-main/)** —
  LangFuse + MCP integration: adding observability to MCP-enabled Python agents.

### Cleaned notes

- [observability.md](observability.md) — LangFuse concepts: traces, spans, scores,
  datasets, and the evaluation loop.

---

## Cross-links to ai-engineering

- [ai-engineering/06-eval/](../../ai-engineering/06-eval/README.md) — evaluation
  methodology: task decomposition, trajectory evaluation, benchmark design, and the
  Evaluating AI Agents course material.

---

## Next pillar

→ [07-agentic-applications/](../07-agentic-applications/README.md) — specific projects
built with the frameworks and patterns from the earlier pillars.
