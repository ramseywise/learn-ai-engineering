# 02 — Context Engineering

> Depth layer. Summary: [interviewing/guides/5-context-cost](../../interviewing/guides/5-context-cost/00-overview.md)
> Position in the stack: *each loop step assembles context*.
> Deep note: [context-engineering.md](context-engineering.md)

---

## What it is

Context engineering is the discipline of composing what goes *into* the model's context window on each call: which documents to include, which memory chunks to surface, which tool outputs to inject, how much conversation history to retain, and how to manage the token budget across all of it. Where prompt engineering ends (the instructions themselves) context engineering begins (the surrounding content those instructions act on).

Memory and tool-design are **sub-components of this layer and the harness layer** — not sibling pillars. Every source that enumerates the foundations treats them as context/harness primitives, never as top-level disciplines.

**Inherits the weaknesses of:** prompt engineering — a well-assembled context window cannot compensate for poorly written instructions inside it.

---

## Resource map

### Deep notes
- [context-engineering.md](context-engineering.md) — the 10 core context-engineering techniques (window composition, retrieval integration, memory types, token budget management).
- [context-management.md](context-management.md) — operational patterns for managing context across multi-turn conversations.
- [memory.md](memory.md) — memory as a context sub-component: in-context, external, episodic, semantic.
- [hooks-architecture.md](hooks-architecture.md) — hooks architecture as context injection mechanism.

### Interviewing guide
- [5-context-cost](../../interviewing/guides/5-context-cost/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [Context-Engineering-main](Context-Engineering-main/) — hands-on context engineering patterns.
- [LLMs-as-Operating-Systems--Agent-Memory-main](../../generative-ai/03-agentic-foundations/LLMs-as-Operating-Systems--Agent-Memory-main/) — memory as OS primitive.
- [Long-Term-Agentic-Memory-With-LangGraph-main](../../generative-ai/03-agentic-foundations/Long-Term-Agentic-Memory-With-LangGraph-main/) — long-term memory patterns.

### Next layer
→ [03-harness/](../03-harness/README.md) — the harness wraps the loops that assemble context.
