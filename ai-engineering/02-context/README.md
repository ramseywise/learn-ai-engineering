# 02 — Context Engineering

> Depth layer. Summary: [interviewing/guides/5-context-cost](../../interviewing/guides/5-context-cost/00-overview.md)
> Position in the stack: *each loop step assembles context*.
> Deep note: [context-engineering.md](../../interviewing/notes/context-engineering.md)

---

## What it is

Context engineering is the discipline of composing what goes *into* the model's context window on each call: which documents to include, which memory chunks to surface, which tool outputs to inject, how much conversation history to retain, and how to manage the token budget across all of it. Where prompt engineering ends (the instructions themselves) context engineering begins (the surrounding content those instructions act on).

Memory and tool-design are **sub-components of this layer and the harness layer** — not sibling pillars. Every source that enumerates the foundations treats them as context/harness primitives, never as top-level disciplines.

**Inherits the weaknesses of:** prompt engineering — a well-assembled context window cannot compensate for poorly written instructions inside it.

---

## Resource map

### Deep notes
- [context-engineering.md](../../interviewing/notes/context-engineering.md) — the 10 core context-engineering techniques (window composition, retrieval integration, memory types, token budget management).
- [context-management.md](../../interviewing/notes/context-management.md) — operational patterns for managing context across multi-turn conversations.
- [memory.md](../../interviewing/notes/memory.md) — memory as a context sub-component: in-context, external, episodic, semantic.

### Interviewing guide
- [5-context-cost](../../interviewing/guides/5-context-cost/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [Context-Engineering-main](./Context-Engineering-main/) — hands-on context engineering patterns.
- [LLMs-as-Operating-Systems--Agent-Memory-main](../../generative-ai/03-agentic-foundations/LLMs-as-Operating-Systems--Agent-Memory-main/) — memory as OS primitive.
- [Long-Term-Agentic-Memory-With-LangGraph-main](../../generative-ai/04-agentic-frameworks/Long-Term-Agentic-Memory-With-LangGraph-main/) — long-term memory patterns.

### Next layer
→ [03-harness/](../03-harness/README.md) — the harness wraps the loops that assemble context.

---

## Working References

Claude Code convention references that map to this pillar. These files live at `~/.claude/refs/` and can be consulted in any Claude Code session.

### `agent-context.md`
Conventions for what goes in the context window, in what order, and what gets evicted first — and how a long-running agent stays under the window limit without losing decisions.

Key topics for this pillar:
- Four-lever model: Write → Select → Compress → Isolate (apply in order; isolate is highest cost)
- Content priority ordering: stable content (system prompt, memory summaries) before ephemeral content (history, tool results, scratch reasoning)
- Compaction strategy: trigger points (80% limit, phase boundaries, before subagent spawn), what to compact, what must survive
- Prompt versioning: prompts as versioned artifacts with `PROMPT_VERSION` identifiers; version bumps invalidate eval baselines
- Progressive disclosure: loading task-specific instruction blocks only when active; the `skills/` directory as a practice of this pattern
- Subagent context isolation: what the subagent receives vs. what it does not; orchestrator-holds-plan as the settled default
