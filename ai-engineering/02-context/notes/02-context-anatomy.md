---
origin: web-authored
sources:
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.promptingguide.ai/guides/context-engineering-guide
  - https://developers.openai.com/api/docs/guides/compaction
  - https://github.com/davidkimai/Context-Engineering (00_foundations/01–03, 00_COURSE/01_context_retrieval_generation/01–03) — snapshot 2026-08-14)
confidence: high
cleaned: 2026-10-28
---
# 2 — The Anatomy of Effective Context

> What goes in the window, in what order, and which layer each piece belongs to.

---

## The components

A context window at inference time is composed of, roughly in order:

1. **System prompt** — role, task framing, behavioral constraints
2. **Tool definitions** — names, descriptions, parameter schemas
3. **Retrieved knowledge** — documents, search results, RAG chunks
4. **Memory** — summaries and facts carried across sessions
5. **Runtime state** — date, user, environment, permissions
6. **Message history** — the conversation, including tool calls and results
7. **The current turn** — what the user just asked

Context engineering is the discipline of deciding, per call, what occupies each of these and at what size.

---

## System prompt altitude

Anthropic's framing: system prompts must be calibrated to the **right altitude** — a Goldilocks zone between two failure modes.

| Too low | Right altitude | Too high |
|---|---|---|
| Hardcoded if/else logic in prose | Specific enough to guide, flexible enough to generalize | Vague guidance assuming context the model lacks |
| Brittle — breaks on any case not enumerated | Heuristics with clear signals | Under-specified — model invents its own interpretation |
| "If the user says X, reply Y. If Z, reply W…" | "Prefer X when the signal is A; escalate when uncertain." | "Be helpful and use good judgment." |

The low-altitude failure is more common in engineered systems, because each production bug tempts you to add one more rule. The result is a system prompt that reads like a decision tree, is unmaintainable, and still misses the next edge case. When you catch yourself adding a fourth conditional to a prompt, the fix is usually a **tool or a code-level control**, not a fifth conditional. See layer 5 below.

---

## The five layers

Organize context by **usage frequency, stability, and enforcement requirement** — not by topic. Keep the active window small and inject the rest only when relevant.

### Layer 1 — Persistent instruction

Must be valid in every session: agent identity and role, project-wide conventions, architectural invariants, safety constraints, prohibited actions.

Properties: short, explicit, stable, operational, easy to follow. In Claude Code this is `CLAUDE.md`.

Test for this layer: *if it isn't true in nearly every task, it doesn't belong here.*

### Layer 2 — On-demand knowledge

Reusable procedures and domain knowledge relevant only to certain tasks: skills, playbooks, deployment procedures, evaluation methodologies, debugging checklists, API-specific instructions, long reference docs.

Governed by **progressive disclosure** — only a short name and description (*what* + *when*) stay permanently visible; full content loads when the task activates it. The `skills/` directory is this pattern made concrete: ~10 tokens of description resident, thousands of tokens of procedure loaded on demand.

### Layer 3 — Runtime injection

Dynamic values that change between sessions, turns, users, or environments: current date/time, user or tenant ID, channel ID, environment variables, permission state, task status.

Assemble programmatically at request time rather than storing in the system prompt. Two benefits: the information stays current, and irrelevant dynamic data doesn't consume context on every interaction.

Date/time is the canonical case — without injection the model guesses, and every relative date ("last quarter", "recent") resolves wrong.

### Layer 4 — Long-term memory

Knowledge accumulated across sessions: user preferences, repeated corrections, project discoveries, effective workflows, prior decisions, known failure patterns.

Never a full transcript pasted forward. Organize as a **compact index plus retrievable detail** — Claude Code's auto-memory loads the `MEMORY.md` index (first 200 lines / 25 KB) at session start; topic files are read only when needed.

Memory must be **editable and auditable**. Wrong, outdated, or contradictory entries have to be removable rather than accumulating. See [06-memory.md](06-memory.md).

### Layer 5 — Deterministic system

Behavior that must be reliable belongs in **code**, not context: hooks, permissions, schemas, validators, tool constraints. Blocking dangerous commands, enforcing allowed paths, validating structured output, checking argument schemas.

The rule: a model may ignore, misunderstand, or inconsistently follow a textual instruction. A code-level control cannot be talked out of enforcing itself.

This layer is the answer to prompt-altitude drift. "The agent keeps doing X" is usually a hook, not a stronger sentence.

---

## Ordering: stable before dynamic

Ordering is not cosmetic — it determines cache economics and attention placement.

**Prompt caching works by prefix matching.** The cache hits only on an exact-match prefix; the first differing token invalidates everything after it. So:

```
[ system prompt ] [ tools ] [ stable memory ]   <- static, cacheable prefix
[ retrieved docs ] [ history ] [ runtime state ] <- dynamic, changes per call
[ current query ]                                <- last
```

Put a timestamp at the top of the system prompt and you have destroyed cache reuse for the entire window on every single call.

This aligns with a second effect: for long-document work, **put longform data above the query**. Anthropic measures up to 30% quality improvement when the query appears at the end rather than the beginning. Cache economics and attention placement point the same direction.

---

## Context types taxonomy

A useful cross-cut, orthogonal to the five layers:

| Type | Source | Volatility |
|---|---|---|
| **Static** | Role, instructions, rules, constraints | Stable across sessions |
| **Dynamic** | Date/time, user input, environment | Changes per turn |
| **Retrieved** | Vector store, search, file reads | Changes per query |
| **Historical** | Prior states, revisions, agent outputs | Grows monotonically |

Historical is the one that gets away from you — it is the only type that grows without an explicit bound. Everything in [05-compression-compaction.md](05-compression-compaction.md) exists to bound it.

---

## Structure within the window

- **Delimit untrusted content.** Wrap user input and retrieved documents in tags (`<user_query>`, `<document index="1">`) so the model can distinguish instructions from data. This is also the first line of prompt-injection defense — see [11-failure-modes.md](11-failure-modes.md).
- **Structured outputs are context engineering.** A JSON schema or typed field list constrains what comes back, which determines what the *next* turn's context contains. Schema discipline compounds across a loop.
- **Few-shot examples: diverse and canonical.** A handful of well-chosen examples outperforms an exhaustive rule list, and costs fewer tokens. Prefer examples over enumerated edge cases.

---

## Worked example: tuning a deep-research agent

DAIR's case study (Saravia, n8n) is a planner agent that writes search tasks, plus a worker agent that runs them. Each failure it hit was fixed by changing the context, not the model:

| Symptom | Context fix |
|---|---|
| Planned 3 searches, ran 2, and gave no reason | State the completion rule. **Flexible** — "skip a task only if it overlaps another, and say why" — while developing and observing; **strict** — "execute every planned task" — in production |
| Status values drifted between runs (`pending` / `to-do`, `done` / `completed` / `finished`) | **Enumerate the allowed values** in the tool instructions. Every free-text field that code reads needs a closed set |
| Searched for stale news ("latest" meant last year) | **Inject the current date** as dynamic context, after the stable prefix so it doesn't break the cache (see [Ordering](#ordering-stable-before-dynamic)) |
| One agent managed tasks, memory, search and the report; it forgot steps as the context grew | Split out a **search worker** that receives *only the query text* and returns results plus an error state. Run it on a cheaper model ([10](10-tools-and-multi-agent.md#what-a-sub-agent-receives)) |
| Unclear why it made a decision | Write the task list to external state (id, query, status, result summary, timestamp), so every decision is inspectable ([06](06-memory.md#structured-note-taking)) |
| Undefined behavior when a search failed | Add **error-path instructions**: retry once, then record the failure and continue |

Before shipping, check the context against four questions: **completeness** (does it cover every scenario?), **clarity** (could any part be read two ways?), **consistency** (do the system prompt and the tool descriptions agree?), and **testability** (can you check the behavior with an eval?). Then track task-completion rate, behavioral consistency across similar inputs, and error rate as the context changes. Avoiding over-constraint (rules that break on edge cases) and under-specification (vague goals) is a calibration problem. Evals settle it ([06-eval](../../06-eval/README.md)).

---

## The formal view

The Mei et al. survey (2507.13334) writes context as an assembly of typed components rather than a single string:

```
C = A(c_instr, c_know, c_tools, c_mem, c_state, c_query)
```

| Component | Is | Layer above |
|---|---|---|
| `c_instr` | System instructions and rules | Instructions |
| `c_know` | Retrieved external knowledge | Retrieved |
| `c_tools` | Tool definitions and signatures | Tools |
| `c_mem` | Persistent memory from prior sessions | Memory |
| `c_state` | Dynamic state: user, world, task progress | Dynamic |
| `c_query` | The immediate request | Query |

`A` is the assembly function: selection, ordering, formatting. The framing makes one point worth keeping: **context engineering is designing `A`**, not writing any single component. Optimising the assembly under a token budget is [03](03-budgeting-the-window.md).

### Examples: how many, which ones

The upstream "molecule" material comes down to three rules:

- **Two to five examples** usually capture most of the gain. Measure before adding more ([03](03-budgeting-the-window.md)).
- **Select by similarity to the query** when you have an example pool. Retrieved examples beat a fixed set on heterogeneous traffic.
- **Cover the output space.** Include at least one example of each output class (including "none" or "refuse"), or the model will under-produce the missing ones.

---

## Working reference

`~/.claude/refs/agent-context.md` — content priority ordering: stable content (system prompt, memory summaries) before ephemeral content (history, tool results, scratch reasoning). Also covers prompt versioning (`PROMPT_VERSION` identifiers; version bumps invalidate eval baselines).

---

→ Next: [03-budgeting-the-window.md](03-budgeting-the-window.md) — how much of each component the window can afford.
