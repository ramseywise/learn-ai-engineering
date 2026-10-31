# 03 — Agentic Foundations

> Depth layer. Summary: [interviewing/guides/4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md)
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

- **[`../../ai-engineering/02-context-engineering/`](../../ai-engineering/02-context-engineering/README.md)** —
  context engineering for agents: what goes in the context window and why it matters
  (13-chapter course in `notes/`, with labs, templates and paper PDFs).
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
- **[`../../ai-engineering/06-eval/notes/06-evaluating-agents.md`](../../ai-engineering/06-eval/notes/06-evaluating-agents.md)** —
  end-to-end agent evaluation: task decomposition, trajectory evaluation, benchmark design.

### Interviewing guides

- [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md) — compressed summary for
  interview prep: agent harness, tool use, loop design, memory, multi-agent orchestration.

### Book

- Bojie Li, *AI Agents in Depth* (2026, [upstream](https://github.com/bojieli/ai-agent-book), Apache-2.0).
  Ch. 1 is synthesized in [agent-fundamentals.md](agent-fundamentals.md): Agent = LLM + Context + Tools,
  the context ablation, ReAct, workflow vs. autonomous, and guardrails. Later chapters are folded
  into the ai-engineering pillars; each note's `sources:` cites the chapter it draws on.

### Cleaned notes

- [agent-fundamentals.md](agent-fundamentals.md) — start here: the agent formula, the five context
  parts and their ablation, the ReAct trajectory, model-as-agent, model choice, and workflow vs. autonomous.
- [agents-google-adk.md](agents-google-adk.md) — Google ADK: agent framework, tool use, deployment.
- [Harness engineering](../../ai-engineering/03-harness-engineering/README.md): harness architecture
  ([what a harness is](../../ai-engineering/03-harness-engineering/notes/01-what-a-harness-is.md), [anatomy](../../ai-engineering/03-harness-engineering/notes/02-harness-anatomy.md)), tool design,
  [orchestration](../../ai-engineering/03-harness-engineering/notes/07-orchestration.md) and multi-agent patterns,
  [execution boundaries](../../ai-engineering/03-harness-engineering/notes/04-execution-boundaries.md) and guardrails,
  [verification loops](../../ai-engineering/03-harness-engineering/notes/05-verification-loops.md) and reliability,
  [long-horizon execution](../../ai-engineering/03-harness-engineering/notes/06-long-horizon-execution.md) (Deep Agents, session lifecycle).
- [Loop engineering](../../ai-engineering/04-loop-engineering/README.md) — loop reliability:
  termination conditions, scorekeepers, stuck-agent detection.
- [Memory](../../ai-engineering/02-context-engineering/notes/06-memory.md) — memory architectures: in-context,
  episodic, semantic, procedural; production memory designs.
- [Context engineering](../../ai-engineering/02-context-engineering/README.md) — context
  assembly for agents: what to include, what to compress, what to externalize.

---

## Cross-links to ai-engineering

The ai-engineering folder is the **discipline layer** on top of these application patterns.
For each agentic concern, there is a corresponding ai-engineering pillar:

| Agentic concern | ai-engineering depth |
|---|---|
| Building the agent container | [03-harness-engineering/](../../ai-engineering/03-harness-engineering/README.md) |
| Designing the agent loop | [04-loop-engineering/](../../ai-engineering/04-loop-engineering/README.md) |
| Multi-agent graphs and KG retrieval | [05-graph-engineering/](../../ai-engineering/05-graph-engineering/README.md) |
| Measuring and observing agent behavior | [06-eval/](../../ai-engineering/06-eval/README.md) |

---

## Next pillar

→ [04-agentic-frameworks/](../04-agentic-frameworks/README.md) — framework reference
material: comparison docs and selection guides for LangGraph, LangFuse, LangSmith, and ADK.
