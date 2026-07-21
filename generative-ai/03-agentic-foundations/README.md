# 03 — Agentic Applications

> Depth layer. Summary: [interviewing/guides/4-agents](../../interviewing/guides/4-agents/00-overview.md)
> Position: third pillar — the current frontier of generative AI.
> Presumes: [01-llm-fundamentals](../01-llm-fundamentals/README.md), [02-rag-retrieval](../02-rag-retrieval/README.md).

---

## What it is

Agentic applications are LLM systems that plan, use tools, maintain state across turns,
and operate in loops — often with multiple cooperating agents. This is where generative AI
becomes software engineering: harnesses, loops, memory, evaluation, and guardrails all
become first-class concerns.

This pillar is the largest because the agentic frontier is where most active development
is happening. It maps to the highest concentration of course material, notes, and
real project work in this repo.

---

## Resource map

### Course material (hands-on)

**Design patterns and frameworks:**
- **[`../coursera-references/AI-Agentic-Design-Patterns-with-AutoGen-main/`](../coursera-references/AI-Agentic-Design-Patterns-with-AutoGen-main/)** —
  AutoGen multi-agent design patterns: conversation, tool use, code execution, orchestration.
- **[`../coursera-references/AI-Agents-in-LangGraph-main/`](../coursera-references/AI-Agents-in-LangGraph-main/)** —
  LangGraph agent construction: state machines, persistence, streaming, human-in-the-loop.
- **[`../coursera-references/AgenticAIFrameworks-master/`](../coursera-references/AgenticAIFrameworks-master/)** —
  survey of agentic frameworks: comparative patterns across AutoGen, LangGraph, CrewAI.

**Context and memory:**
- **[`../coursera-references/Context-Engineering-main/`](../coursera-references/Context-Engineering-main/)** —
  context engineering for agents: what goes in the context window and why it matters.
- **[`../coursera-references/LLMs-as-Operating-Systems--Agent-Memory-main/`](../coursera-references/LLMs-as-Operating-Systems--Agent-Memory-main/)** —
  agent memory architectures: in-context, external (vector/KG), procedural memory.
- **[`../coursera-references/Long-Term-Agentic-Memory-With-LangGraph-main/`](../coursera-references/Long-Term-Agentic-Memory-With-LangGraph-main/)** —
  long-term memory implementation with LangGraph persistence layer.

**Tool use and search:**
- **[`../coursera-references/internet-search-agent-main/`](../coursera-references/internet-search-agent-main/)** —
  building a web-search agent: tool calling, result parsing, iterative refinement.

**Evaluation and observability:**
- **[`../coursera-references/Learning-LangFuse-main/`](../coursera-references/Learning-LangFuse-main/)** —
  LangFuse basics: tracing, scoring, and observability for LLM applications.
- **[`../coursera-references/langfuse-evaluation-main/`](../coursera-references/langfuse-evaluation-main/)** —
  evaluation pipelines in LangFuse: golden sets, LLM-as-judge, regression tracking.
- **[`../coursera-references/langfuse-mcp-python-main/`](../coursera-references/langfuse-mcp-python-main/)** —
  LangFuse + MCP integration: observability for MCP-enabled agents.
- **[`../coursera-references/DeepLearning.AI-Evaluating-AI-Agents-master/`](../coursera-references/DeepLearning.AI-Evaluating-AI-Agents-master/)** —
  end-to-end agent evaluation: task decomposition, trajectory evaluation, benchmark design.

**Active project:**
- **[`../chatbot/deep-research-bot/`](../chatbot/deep-research-bot/)** — the one genuinely
  active project in this repo: a 2025 agent-building workshop clone with real post-clone
  activity (eval scripts and notebooks edited after the initial clone). Good reference for
  what a real agent research loop looks like.

### Interviewing guides

- [4-agents](../../interviewing/guides/4-agents/00-overview.md) — compressed summary for
  interview prep: agent harness, tool use, loop design, memory, multi-agent orchestration.

### Cleaned notes

- [agent-harness.md](../../interviewing/notes/agent-harness.md) — harness architecture: tool
  registration, the agent loop, structured output parsing, error handling.
- [agents-design.md](../../interviewing/notes/agents-design.md) — agent design patterns:
  ReAct, plan-and-execute, reflection, multi-agent orchestration.
- [deep-agents.md](../../interviewing/notes/deep-agents.md) — advanced agent patterns:
  long-horizon planning, self-correction, agentic evals.
- [loop-engineering.md](../../interviewing/notes/loop-engineering.md) — loop reliability:
  termination conditions, loop invariants, stuck-agent detection.
- [reliable-agents.md](../../interviewing/notes/reliable-agents.md) — reliability patterns:
  retries, fallbacks, circuit breakers, determinism vs. stochasticity tradeoffs.
- [agents-guardrails.md](../../interviewing/notes/agents-guardrails.md) — safety and
  guardrails: input/output filtering, scope limiting, human-in-the-loop gates.
- [memory.md](../../interviewing/notes/memory.md) — memory architectures: in-context,
  episodic, semantic, procedural.
- [context-engineering.md](../../interviewing/notes/context-engineering.md) — context
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

## TypeScript

Google ADK repo (TS) — coming as a pointer target once linked. The Python course material
above remains canonical for now. Vercel AI SDK agent patterns will also be added here.
