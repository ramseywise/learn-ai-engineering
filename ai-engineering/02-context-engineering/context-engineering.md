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
| **Write** | Can this live outside the window? | [06-memory](notes/06-memory.md) |
| **Select** | What comes back in, and when? | [04-retrieval](notes/04-retrieval.md) |
| **Compress** | Can this be smaller? | [05-compaction](notes/05-compression-compaction.md) |
| **Isolate** | Does this need a separate window? | [10-multi-agent](notes/10-tools-and-multi-agent.md) |

Isolate is last because it is most expensive: real tokens multiply, and cross-agent context is lost.

---

## Topic notes

The full chapter index, with what each covers, is in the [README](README.md#topic-notes-notes):

01 [finite](notes/01-why-context-is-finite.md) · 02 [anatomy](notes/02-context-anatomy.md) · 03 [budgeting](notes/03-budgeting-the-window.md) · 04 [retrieval](notes/04-retrieval.md) · 05 [compaction](notes/05-compression-compaction.md) · 06 [memory](notes/06-memory.md) · 07 [structure](notes/07-structured-context.md) · 08 [cognitive tools](notes/08-cognitive-tools.md) · 09 [protocols](notes/09-protocols.md) · 10 [multi-agent](notes/10-tools-and-multi-agent.md) · 11 [failure modes](notes/11-failure-modes.md) · 12 [evaluation](notes/12-evaluating-context.md) · 13 [putting it together](notes/13-putting-it-together.md) · 99 [speculative track](notes/99-speculative-field-track.md)

---

## The prompt ↔ context boundary

| Prompt engineering | Context engineering |
|---|---|
| The instructions and examples themselves | What to *include* alongside the instructions |
| How you phrase the task, format requests, structure XML | Which documents, memory, tool outputs, history to inject |
| Role setting, CoT, few-shot, output format | Window composition, token budget, retrieval strategy |

Once you are deciding *what* is in the window rather than *how* to phrase what's already there, you are in context engineering.

Reciprocally, the context ↔ harness boundary: once the assembly becomes stateful and conditional — a loop that decides *when* to retrieve, compact, or spawn — you have crossed into [03-harness](../03-harness-engineering/README.md).

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

Context has no type system — instructions and data are the same tokens. Prompt injection is therefore a context-layer problem as much as a prompt-layer one, and every added context source is added attack surface. See [notes/07](notes/11-failure-modes.md#prompt-injection) and [prompt-injection.md](../../interviewing/guides/7-security-safety/prompt-injection.md).

---

## Resources

- Pillar guide: [5-context-cost](../../interviewing/guides/5-context-cost/00-overview.md)
- Anthropic: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- promptingguide.ai: https://www.promptingguide.ai/guides/context-engineering-guide
- OpenAI compaction: https://developers.openai.com/api/docs/guides/compaction
- Course material (synthesized from davidkimai/Context-Engineering): chapters 03, 07–09, 12–13 and 99 in [notes/](notes/), plus [templates/](templates/) and [notebooks/](notebooks/)
- Papers: [references.md](references.md) · PDFs in [sources/](sources/)
