# 02 — Context Engineering

> Depth layer. Summary: [interviewing/guides/5-context-cost](../../interviewing/guides/5-context-cost/00-overview.md)
> Position in the stack: *each loop step assembles context*.
> Overview note: [context-engineering.md](context-engineering.md) · Topic depth: [notes/](notes/)

---

## What it is

Context engineering is the discipline of composing what goes *into* the model's context window on each call: which documents to include, which memory chunks to surface, which tool outputs to inject, how much conversation history to retain, and how to manage the token budget across all of it. Where prompt engineering ends (the instructions themselves) context engineering begins (the surrounding content those instructions act on).

Memory and tool-design are **sub-components of this layer and the harness layer** — not sibling pillars. Every source that enumerates the foundations treats them as context/harness primitives, never as top-level disciplines.

The governing objective is a *minimization*: **find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome**. Context is a finite resource with diminishing — eventually negative — marginal returns, because transformer attention divides a fixed budget across n² token pairs. Every technique in this pillar responds to that constraint.

**Inherits the weaknesses of:** prompt engineering — a well-assembled context window cannot compensate for poorly written instructions inside it.

---

## Resource map

### Deep notes
- [context-engineering.md](context-engineering.md) — pillar overview: the thesis, the four levers (Write → Select → Compress → Isolate), the prompt↔context boundary, context types.

#### Topic notes ([notes/](notes/))
1. [Why context is finite](notes/01-why-context-is-finite.md) — attention budget, n² attention, context rot, diminishing returns.
2. [The anatomy of effective context](notes/02-context-anatomy.md) — system prompt altitude, the five layers, stable-before-dynamic ordering, cache prefix matching, and a worked deep-research example.
3. [Retrieval strategies](notes/03-retrieval-strategies.md) — pre-computed vs. just-in-time, lightweight identifiers, progressive disclosure, the hybrid default, the pre-retrieval pipeline.
4. [Compression and compaction](notes/04-compression-compaction.md) — the compaction pipeline, retention priority, tool-result clearing, state extraction, crash recovery.
5. [Memory as a context sub-component](notes/05-memory-as-context.md) — memory types, structured note-taking, index-plus-detail, memory hygiene.
6. [Multi-agent context and tool design](notes/06-multi-agent-context.md) — sub-agent isolation, orchestrator-holds-plan, token-efficient tools, tool overlap.
7. [Context failure modes](notes/07-context-failure-modes.md) — rot, poisoning, distraction, clash, injection, and the diagnostic flow.

#### Related
- [memory.md](../05-graph/memory.md) — memory depth: in-context, external, episodic, semantic.
- [skills-design.md](../03-harness/skills-design.md) — skills as a harness primitive; relies on the progressive-disclosure mechanism from note 02.

### Origin readings
Where the term "context engineering" came from (mid-2025), and the essays that shaped it:
- Karpathy, [the "context engineering" post](https://x.com/karpathy/status/1937902205765607626): "the delicate art and science of filling the context window"
- LangChain, [*The rise of context engineering*](https://blog.langchain.com/the-rise-of-context-engineering/)
- Lance Martin, [*Context engineering for agents*](https://rlancemartin.github.io/2025/06/23/context_engineering/), the source of the Write → Select → Compress → Isolate levers
- Phil Schmid, [*The new skill in AI is not prompting, it's context engineering*](https://www.philschmid.de/context-engineering)
- Walden Yan (Cognition), [*Don't build multi-agents*](https://cognition.ai/blog/dont-build-multi-agents): share full context, not messages
- HumanLayer, [*12-factor agents*](https://github.com/humanlayer/12-factor-agents): "own your context window"
- Anthropic, [*Effective context engineering for AI agents*](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- DAIR, [*Context Engineering Guide*](https://www.promptingguide.ai/guides/context-engineering-guide), the source of the worked example in note 02

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
