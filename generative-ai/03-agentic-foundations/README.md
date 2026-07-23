# 03 — Agentic Foundations

> Depth layer. Summary: [interviewing/guides/4-agents](../../interviewing/guides/4-agents/00-overview.md)
> Position: third pillar — framework learning for agentic AI.
> Presumes: [01-llm-fundamentals](../01-llm-fundamentals/README.md), [02-rag-retrieval](../02-rag-retrieval/README.md).

---

## What it is

Agentic foundations is where LLM systems graduate from single-call patterns to planning,
tool use, multi-turn state, and multi-agent coordination. This pillar covers the course
material for learning the major agentic frameworks: LangGraph, AutoGen, and Google ADK.

For framework comparison and selection guides (which framework for which problem), see
[04-agentic-frameworks/](../04-agentic-frameworks/README.md). For deployed projects built
with these frameworks, see [07-agentic-applications/](../07-agentic-applications/README.md).

---

## Resource map

### Course material (hands-on)

**Design patterns and frameworks:**

- **[`AI-Agentic-Design-Patterns-with-AutoGen-main/`](AI-Agentic-Design-Patterns-with-AutoGen-main/)** —
  AutoGen multi-agent design patterns: conversation, tool use, code execution, orchestration.
- **[`AI-Agents-in-LangGraph-main/`](../04-agentic-frameworks/AI-Agents-in-LangGraph-main/)** —
  LangGraph agent construction: state machines, persistence, streaming, human-in-the-loop.
- **[`AgenticAIFrameworks-master/`](AgenticAIFrameworks-master/)** —
  survey of agentic frameworks: comparative patterns across AutoGen, LangGraph, CrewAI.

**Context and memory:**

- **[`../../ai-engineering/02-context/Context-Engineering-main/`](../../ai-engineering/02-context/Context-Engineering-main/)** —
  context engineering for agents: what goes in the context window and why it matters.
- **[`LLMs-as-Operating-Systems--Agent-Memory-main/`](LLMs-as-Operating-Systems--Agent-Memory-main/)** —
  agent memory architectures: in-context, external (vector/KG), procedural memory.
- **[`Long-Term-Agentic-Memory-With-LangGraph-main/`](../04-agentic-frameworks/Long-Term-Agentic-Memory-With-LangGraph-main/)** —
  long-term memory implementation with LangGraph persistence layer.

**Generative AI design patterns:**

- **[`ai design/`](<ai design/>)** — "Generative AI Design Patterns" chapters (PDFs):
  content style, knowledge augmentation, tool use, reliability, safety, composable workflows.

**Evaluation and observability:**

- **[`../06-observability/Learning-LangFuse-main/`](../06-observability/Learning-LangFuse-main/)** —
  LangFuse basics: tracing, scoring, and observability for LLM applications.
- **[`../06-observability/langfuse-evaluation-main/`](../06-observability/langfuse-evaluation-main/)** —
  evaluation pipelines in LangFuse: golden sets, LLM-as-judge, regression tracking.
- **[`../06-observability/langfuse-mcp-python-main/`](../06-observability/langfuse-mcp-python-main/)** —
  LangFuse + MCP integration: observability for MCP-enabled agents.
- **[`../../ai-engineering/06-eval/DeepLearning.AI-Evaluating-AI-Agents-master/`](../../ai-engineering/06-eval/DeepLearning.AI-Evaluating-AI-Agents-master/)** —
  end-to-end agent evaluation: task decomposition, trajectory evaluation, benchmark design.

### Interviewing guides

- [4-agents](../../interviewing/guides/4-agents/00-overview.md) — compressed summary for
  interview prep: agent harness, tool use, loop design, memory, multi-agent orchestration.

### Cleaned notes

- [agents-google-adk.md](agents-google-adk.md) — Google ADK: agent framework, tool use, deployment.
- [agent-harness.md](../../ai-engineering/03-harness/agent-harness.md) — harness architecture: tool
  registration, the agent loop, structured output parsing, error handling.
- [agents-design.md](../../ai-engineering/03-harness/agents-design.md) — agent design patterns:
  ReAct, plan-and-execute, reflection, multi-agent orchestration.
- [agents-guardrails.md](../../ai-engineering/03-harness/agents-guardrails.md) — safety and
  guardrails: input/output filtering, scope limiting, human-in-the-loop gates.
- [reliable-agents.md](../../ai-engineering/03-harness/reliable-agents.md) — reliability patterns:
  retries, fallbacks, circuit breakers, determinism vs. stochasticity tradeoffs.
- [loop-engineering.md](../../ai-engineering/04-loop/loop-engineering.md) — loop reliability:
  termination conditions, loop invariants, stuck-agent detection.
- [deep-agents.md](../../ai-engineering/04-loop/deep-agents.md) — advanced agent patterns:
  long-horizon planning, self-correction, agentic evals.
- [memory.md](../../ai-engineering/05-graph/memory.md) — memory architectures: in-context,
  episodic, semantic, procedural.
- [context-engineering.md](../../ai-engineering/02-context/context-engineering.md) — context
  assembly for agents: what to include, what to compress, what to externalize.

---

## Cross-links to ai-engineering

The ai-engineering folder is the **discipline layer** on top of these application patterns.
For each agentic concern, there is a corresponding ai-engineering pillar:

| Agentic concern | ai-engineering depth |
|---|---|
| Building the agent container | [03-harness/](../../ai-engineering/03-harness/README.md) |
| Designing the agent loop | [04-loop/](../../ai-engineering/04-loop/README.md) |
| Multi-agent graphs and KG retrieval | [05-graph/](../../ai-engineering/05-graph/README.md) |
| Measuring and observing agent behavior | [06-eval/](../../ai-engineering/06-eval/README.md) |

---

## Next pillar

→ [04-agentic-frameworks/](../04-agentic-frameworks/README.md) — framework reference
material: comparison docs and selection guides for LangGraph, LangFuse, LangSmith, and ADK.
