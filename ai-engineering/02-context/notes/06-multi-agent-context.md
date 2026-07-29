---
origin: web-authored
sources:
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.promptingguide.ai/guides/context-engineering-guide
confidence: high
cleaned: 2026-07-29
---
# 6 — Multi-Agent Context and Tool Design

> Isolation is the highest-cost context lever. Use it when compression is not enough.

---

## Sub-agent architectures

The pattern: specialized agents handle focused tasks with **clean context windows**, returning condensed summaries to a lead coordinator.

The economics are the point. A sub-agent may burn 100k tokens exploring a codebase and return a 2k-token summary. The orchestrator pays 2k for work that would have cost it 100k of its own window — and, more importantly, would have left 98k of exploration debris polluting the window it needs for synthesis.

```
Orchestrator (holds plan, stays small)
  ├── Sub-agent A: explore subsystem X  ->  2k summary  (spent 80k internally)
  ├── Sub-agent B: explore subsystem Y  ->  2k summary  (spent 60k internally)
  └── Sub-agent C: explore subsystem Z  ->  2k summary  (spent 90k internally)

Orchestrator window: ~6k of findings, not 230k of exploration.
```

The sub-agent's window is **discarded**, not merged. That discarding is the feature.

### Orchestrator-holds-plan

The settled default: the **orchestrator owns the plan and the synthesis**; sub-agents own bounded investigations.

Sub-agents should not decide overall strategy, because each sees only its slice. An agent that explored one subsystem will over-weight that subsystem — it has no basis for comparison. Cross-cutting judgment requires the window that saw all the summaries.

### What a sub-agent receives

The prompt is the entire interface. A sub-agent gets:

- Its specific task, scoped and bounded
- The minimum context needed to do it
- The expected return shape

And does *not* get:

- The full conversation history
- The overall plan
- The other sub-agents' findings

That last exclusion is what makes isolation work, and it is also the failure mode — see below.

### Costs

Isolation is the **most expensive** of the four levers (Write → Select → Compress → Isolate), and it is last in that ordering for a reason:

- **Lost shared context.** Sub-agents can't coordinate, can duplicate work, or reach contradictory conclusions from disjoint evidence.
- **Summary is lossy.** Whatever the sub-agent doesn't include is gone. If its judgment about relevance was wrong, the orchestrator never learns what it missed.
- **Prompt is the whole interface.** An under-specified sub-agent prompt yields an off-target investigation, discovered only after it burned its budget.
- **Token multiplier.** Three sub-agents spending 80k each is 240k of real tokens for 6k of visible output. Cheap for the *orchestrator's window*, expensive in absolute spend.

Try Compress before reaching for Isolate. Sub-agents are the right answer for genuinely parallel, genuinely separable investigation — not for work that a compaction would have handled.

---

## Tool design is context engineering

Tools consume context twice: their **definitions** sit in the window permanently, and their **results** enter it per call. Both are context-engineering surfaces.

### Token-efficient results

A tool returning 50k tokens of raw output defeats just-in-time retrieval — you've reintroduced the bulk-loading problem through the tool layer. Tools should return what the agent needs to *decide*, not everything they could produce.

- Paginate or truncate large outputs with an explicit continuation affordance
- Return structured summaries with drill-down identifiers rather than full payloads
- Filter at the tool boundary, where filtering is cheap and deterministic — not in the model, where it costs attention

### Tool overlap

**Tool overlap** — multiple tools covering similar functionality — creates ambiguous decision points. The agent must spend attention choosing, and may choose inconsistently across runs.

Test: *given this task, is there exactly one obviously correct tool?* If two plausibly apply, either merge them or sharpen their descriptions until the boundary is unambiguous.

### Self-contained and robust to error

Each tool should be usable without knowledge of the others, handle its own errors, and return **structured errors** the agent can act on. `{"error_code": "not_found", "is_fatal": false}` is actionable; a stack trace is 500 tokens of noise the agent cannot use.

### Descriptive parameters

Parameter names and descriptions should be unambiguous and play to model strengths. `query: str` tells the model nothing; `search_query: natural-language description of the code you're looking for` tells it what to generate.

Tool descriptions follow the same **routing-logic** discipline as skill descriptions:

- When should I use this?
- When should I *not* use this?
- What are the outputs and success criteria?

Terse descriptions beat verbose ones. These tokens are resident in every window:

```
# bad (~45 tokens)
description: |
  This skill handles the complete deployment process to production.
  It covers environment checks, rollback procedures, and post-deploy
  verification. Use this before deploying any code to production.

# good (~9 tokens)
description: Use when deploying to production or rolling back.
```

Negative examples reduce misfires: "Don't call this when…" plus what to do instead.

---

## Context isolation as a security boundary

Isolation is also a containment mechanism. A sub-agent processing untrusted content — scraped web pages, user uploads, third-party API responses — has a window that gets discarded. An injection landing in that window cannot reach the orchestrator except through the **summary**, which is a narrow, inspectable channel.

This only holds if the summary is treated as data, not instructions. A sub-agent summary interpolated directly into an orchestrator prompt is an injection path — see [07-context-failure-modes.md](07-context-failure-modes.md).

Skills plus open network access is a high-risk combination. Skills make procedures more capable; network access makes exfiltration possible. Together they are a data-exfiltration path that is easy to introduce and hard to retrofit against. A defensible default posture:

- Skills: **allowed**
- Shell: **allowed**
- Network: **enabled only with a minimal allowlist**, per request, for narrowly scoped tasks

Assume tool output is untrusted regardless of source.

---

## Working reference

`~/.claude/refs/agent-context.md` — sub-agent context isolation: what the sub-agent receives vs. what it does not; orchestrator-holds-plan as the settled default.
`~/.claude/refs/agent-tools.md` — the four tool design questions (reversible, idempotent, observable, parallel-safe), tool schema rules, MCP vs. in-process decision table.
`~/.claude/refs/agent-safety.md` — trust zones and the five protection layers.

---

→ Next: [07-context-failure-modes.md](07-context-failure-modes.md) — how context goes wrong.
