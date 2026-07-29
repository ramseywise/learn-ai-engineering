---
origin: web-authored
sources:
  - https://vercel.com/academy/build-ai-agent-harness
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
  - https://harness-engineering.ai/blog/what-is-harness-engineering/
confidence: high
cleaned: 2026-07-29
---
# 3 — Tool Design as Harness Surface

> Tools are the agent's action surface, and their descriptions are the routing logic. This is where most harnesses leak.

---

## ACI, not API

Tool design follows **ACI principles — Agent-Computer Interface, not Application Programming Interface.** A tool is designed for a reader that has no documentation, no type hints, no autocomplete, and no ability to ask a follow-up question. It sees a name, a description, and a parameter schema.

Consequences:

- **Boundaries must be explicit.** Where one tool ends and the next begins has to be legible from descriptions alone.
- **Parameters must be error-proof.** Prefer enums over free strings, absolute paths over relative, required over optional-with-surprising-default.
- **Examples belong inside the definition**, not in external docs. Content invisible to the agent is non-existent.

The debugging heuristic that follows:

> When a tool is used wrongly, **check the tool description before questioning the model's capability.**

---

## The clarity test

Anthropic's rule, and the sharpest available test for a tool set:

> **"If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better."**

Hand your tool list to a colleague with no context, describe three realistic tasks, and ask which tool they'd reach for. Every hesitation is a bug in a description or an overlap that needs collapsing.

Tools should be **"self-contained, robust to error, and extremely clear with respect to their intended use."** The dominant failure mode is **bloated tool sets with overlapping functionality** — and note that LangChain's Terminal Bench gain came partly from *reducing* tools. Subtraction is a legitimate optimization.

---

## The five-section tool contract

Vercel Academy's tool description structure, which turns a one-liner into a decision procedure:

| Section | Purpose |
|---|---|
| **What it does** | The operation, plainly |
| **WHEN TO USE** | Positive triggers — the situations this tool owns |
| **WHEN NOT TO USE** | Boundary cases that belong to a neighboring tool |
| **DO NOT USE FOR** | Hard negatives — misuse patterns seen in practice |
| **EXAMPLES** | Concrete invocations with realistic arguments |

The two negative sections do the heavy lifting. Positive descriptions alone leave the model to infer boundaries between similar tools; explicit negatives are what disambiguate `search` from `grep` from `read`. Each entry in `DO NOT USE FOR` should be **ratchet output** — traceable to an actual observed misuse ([note 01](01-what-a-harness-is.md#the-ratchet)).

Structurally, separate the **contract** (schema + description) from the **execution logic** via a factory pattern. Contracts are prompt-engineering artifacts that get iterated on and versioned; implementations are code. Coupling them means every wording change touches executable code.

---

## The four gating questions

Ask of every tool before it ships:

1. **Reversible?** — can its effect be undone?
2. **Idempotent?** — is calling it twice the same as once?
3. **Observable?** — does it emit a trace the harness can inspect?
4. **Parallel-safe?** — can two instances run concurrently without corruption?

**A tool that fails #1 needs a confirmation gate.** A tool that fails #2 must not be retried without an idempotency key. A tool that fails #3 cannot be debugged. A tool that fails #4 must be serialized in the orchestrator.

---

## Schema rules

- `snake_case` **verb-noun** names — `read_file`, `create_issue`, `send_email`. The name is the first routing signal.
- **Side effects declared in the description**, not just implied by the name.
- **Typed return structure** — never a bare string when the next step needs to branch on the result.
- **Structured errors** with a stable `error_code`, plus `is_fatal` and `retry_after` where relevant. An error the agent can classify is an error it can recover from; a stringly-typed one forces guessing.
- **Token-efficient returns.** Tools should "encourage efficient agent behavior by returning token-efficient information." Return the answer, not the raw dump — and offload the dump to disk with a path reference.

Zod (or Pydantic) schemas give you validation and the model-facing schema from one definition. Pin versions deliberately — Vercel's course notes Zod v3 specifically for AI SDK v6 compatibility, since v4 introduces type breaks.

---

## Progressive disclosure: skills

Loading every tool and MCP server at startup **degrades performance before the agent starts working** — context is consumed and selection accuracy drops as the candidate set grows.

Skills invert this. A short name and description (*what* + *when*, ~10 tokens) stay resident; the full procedure loads only when the task activates it. A capability library of dozens of skills costs a few hundred tokens at rest.

This is the same mechanism as layer 2 in [02-context/notes/02](../../02-context/notes/02-context-anatomy.md), applied to capability rather than knowledge. See also [skills-design.md](../skills-design.md).

---

## MCP vs. in-process

| Choose MCP when | Choose in-process when |
|---|---|
| Multiple distinct callers need the capability | Only this agent uses it |
| A security boundary must be crossed | Trust domain is shared |
| It deploys independently | It ships with the agent |
| Discovery matters (tools change at runtime) | The tool set is fixed |
| It holds its own state | It's stateless |

Cost: latency per hop, plus a process to operate. Default to in-process; promote when one of the left-hand conditions actually holds rather than in anticipation.

---

## Write-operation safety

For anything that mutates, sends, or spends:

1. The description **declares the side effect** explicitly.
2. A **confirmation step** precedes irreversible execution.
3. An **idempotency key** is supplied by the caller so retries are safe.
4. Model-generated inputs are **validated against schema before execution** — tool inputs are agent-composed and therefore only semi-trusted ([note 04](04-execution-boundaries.md#the-five-protection-layers)).

Rule: tools without idempotency keys must not be auto-retried. Retrying a non-idempotent write is how one transient timeout becomes three charged invoices.

---

## Working reference

`~/.claude/refs/agent-tools.md` — the four gating questions, promote-from-bash heuristic, schema rules, MCP decision table, write-operation safety.

---

→ Next: [04-execution-boundaries.md](04-execution-boundaries.md) — where the tools are allowed to run.
