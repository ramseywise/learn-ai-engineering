---
origin: web-authored
sources:
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.promptingguide.ai/guides/context-engineering-guide
  - https://developers.openai.com/api/docs/guides/compaction
  - https://medium.com/ai-in-plain-english/10-context-engineering-techniques-every-ai-engineer-should-know-b54b486a6921
confidence: high
cleaned: 2026-07-29
---
# Context Engineering

> Overview note. Topic depth lives in [notes/](notes/).

---

## Position in the stack

Context engineering is the **second layer**: context contains prompts, and the harness assembles context. Where prompt engineering governs the instructions themselves, context engineering governs everything delivered alongside them — which documents, which memory, which tool results, how much history, and how the token budget is divided across all of it.

**Inherits the weaknesses of:** prompt engineering. A well-assembled context window cannot compensate for poorly written instructions inside it.

Memory and tool design are **sub-components of this layer and the harness layer**, not sibling pillars. Every source that enumerates the foundations treats them as context/harness primitives.

---

## The thesis

> **Find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome.**
> — Anthropic, *Effective Context Engineering for AI Agents*

A *minimization* objective. This is the field's central counterintuition: large windows invite filling, and filling degrades output. Context is a finite resource with diminishing — eventually negative — marginal returns, because transformer attention divides a fixed budget across n² token pairs.

Every technique in this pillar is a response to that constraint.

---

## The four levers

The operational frame (`~/.claude/refs/agent-context.md`). Apply in order — cost rises left to right.

| Lever | Question | Where |
|---|---|---|
| **Write** | Can this live outside the window? | [05-memory](notes/05-memory-as-context.md) |
| **Select** | What comes back in, and when? | [03-retrieval](notes/03-retrieval-strategies.md) |
| **Compress** | Can this be smaller? | [04-compaction](notes/04-compression-compaction.md) |
| **Isolate** | Does this need a separate window? | [06-multi-agent](notes/06-multi-agent-context.md) |

Isolate is last because it is most expensive: real tokens multiply, and cross-agent context is lost.

---

## Topic notes

1. [Why context is finite](notes/01-why-context-is-finite.md) — attention budget, n² attention, context rot, diminishing returns.
2. [The anatomy of effective context](notes/02-context-anatomy.md) — system prompt altitude, the five layers, stable-before-dynamic ordering, cache prefix matching.
3. [Retrieval strategies](notes/03-retrieval-strategies.md) — pre-computed vs. just-in-time, lightweight identifiers, progressive disclosure, the hybrid default, the pre-retrieval pipeline.
4. [Compression and compaction](notes/04-compression-compaction.md) — the compaction pipeline, retention priority, tool-result clearing, state extraction, crash recovery.
5. [Memory as a context sub-component](notes/05-memory-as-context.md) — memory types, structured note-taking, index-plus-detail, memory hygiene.
6. [Multi-agent context and tool design](notes/06-multi-agent-context.md) — sub-agent isolation, orchestrator-holds-plan, token-efficient tools, tool overlap.
7. [Context failure modes](notes/07-context-failure-modes.md) — rot, poisoning, distraction, clash, injection, and the diagnostic flow.

---

## The prompt ↔ context boundary

| Prompt engineering | Context engineering |
|---|---|
| The instructions and examples themselves | What to *include* alongside the instructions |
| How you phrase the task, format requests, structure XML | Which documents, memory, tool outputs, history to inject |
| Role setting, CoT, few-shot, output format | Window composition, token budget, retrieval strategy |

Once you are deciding *what* is in the window rather than *how* to phrase what's already there, you are in context engineering.

Reciprocally, the context ↔ harness boundary: once the assembly becomes stateful and conditional — a loop that decides *when* to retrieve, compact, or spawn — you have crossed into [03-harness](../03-harness/README.md).

---

## Context types

| Type | Source | Volatility |
|---|---|---|
| Static | Role, instructions, rules | Stable across sessions |
| Dynamic | Date/time, user, environment | Per turn |
| Retrieved | Vector store, search, file reads | Per query |
| Historical | Prior states, revisions, outputs | Grows monotonically |

Historical is the only type without a natural bound. Compaction exists to bound it.

---

## Security facet

Context has no type system — instructions and data are the same tokens. Prompt injection is therefore a context-layer problem as much as a prompt-layer one, and every added context source is added attack surface. See [notes/07](notes/07-context-failure-modes.md#prompt-injection) and [prompt-injection.md](../../interviewing/guides/7-security-safety/prompt-injection.md).

---

## Resources

- Pillar guide: [5-context-cost](../../interviewing/guides/5-context-cost/00-overview.md)
- Anthropic: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- promptingguide.ai: https://www.promptingguide.ai/guides/context-engineering-guide
- OpenAI compaction: https://developers.openai.com/api/docs/guides/compaction
- Vendored course: [Context-Engineering-main](Context-Engineering-main/) — see [#106](https://github.com/ramseywise/learn-ai-engineering/issues/106) for consolidation scope
