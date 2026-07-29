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

- [support-agent-observability.md](support-agent-observability.md) — support-agent
  observability & experiment-tracking schema contract: base trace metadata every agent must
  emit, `ExperimentRun`/`RagConfig`/`BedrockConfig`/`ChunkRecord` dataclasses, current
  implementation state per agent (`hc_adk`, `hc_lg`, `hc_rag`), grounding tier promotion
  policy, and the pending work queue. Includes a "Concepts" preamble on agent-run tracing
  (what to record in a trace, two-layer manual+LLM-as-judge sampling strategy). Platform
  wiring (LangFuse/LangSmith setup) is separate — see
  [`04-agentic-frameworks/notes/langfuse.md`](../04-agentic-frameworks/notes/langfuse.md) and
  [`langsmith.md`](../04-agentic-frameworks/notes/langsmith.md).

**Support-agent content note:** content for the `hc_adk`/`hc_lg`/`hc_rag` support-agent
system is distributed across both pillars by design — `ai-engineering/06-eval/evals/`
(gate-contract, eval-architecture) covers evaluation methodology; `generative-ai/02-rag-retrieval/rag/`
(hc-rag-pipeline, semantic-cache, bedrock-kb) covers the retrieval pipeline; and
`support-agent-observability.md` (here) covers the observability schema contract. There is
no single canonical directory — this cross-pillar distribution is intentional.

---

## Cross-links to ai-engineering

- [ai-engineering/06-eval/](../../ai-engineering/06-eval/README.md) — evaluation
  methodology: task decomposition, trajectory evaluation, benchmark design, and the
  Evaluating AI Agents course material.

---

## Next pillar

→ [07-agentic-applications/](../07-agentic-applications/README.md) — specific projects
built with the frameworks and patterns from the earlier pillars.
