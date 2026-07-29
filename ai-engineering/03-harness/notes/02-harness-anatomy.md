---
origin: web-authored
sources:
  - https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
  - https://addyosmani.com/blog/agent-harness-engineering/
  - https://harness-engineering.ai/blog/what-is-harness-engineering/
  - https://vercel.com/academy/build-ai-agent-harness
confidence: high
cleaned: 2026-07-29
---
# 2 — Harness Anatomy

> The component inventory: what ships inside a harness, and which primitives are foundational.

---

## The nine components

LangChain's anatomy, grouped by the job each does:

### Knowledge & configuration

**1. System prompts and context policies** — behavioral framing, plus the *rules for what gets assembled* per call. The policy is harness; the assembled result is context.

**2. Tools, skills, and MCPs — and their descriptions** — the action surface. Descriptions are load-bearing: they are the *only* thing the model sees at selection time. Skills add **progressive disclosure** so a large capability library doesn't flood the window at startup. See [note 03](03-tool-design.md).

### Infrastructure

**3. Filesystem abstractions** — *"arguably the most foundational harness primitive."* Durable storage, context offloading, cross-session persistence, and a shared medium for multi-agent handoff.

**4. Bash + code execution** — the general-purpose escape hatch.

**5. Sandboxes** — safe execution environments with pre-configured tooling (runtimes, CLIs, browsers). See [note 04](04-execution-boundaries.md).

**6. Memory systems** — file-based standards (`AGENTS.md`, `MEMORY.md`) for continual learning across sessions. See [02-context/notes/05](../../02-context/notes/05-memory-as-context.md).

### Orchestration & control

**7. Orchestration logic** — subagent spawning, handoffs, model routing, HITL feedback loops. See [note 07](07-orchestration.md).

**8. Hooks / middleware** — deterministic control flow: compaction, continuation, lint checks, verification gates. The part of the harness that **cannot be talked out of enforcing itself**.

**9. Context management tools** — web search, retrieval, and MCP access for information past the training cutoff; plus compaction and tool-output offloading.

Supporting: git versioning, planning files, test runners, self-verification hooks.

---

## Why the filesystem is foundational

The filesystem is the primitive that the others lean on, because it solves four problems at once:

| Problem | Filesystem answer |
|---|---|
| Context window is finite | Offload large outputs to disk; keep a reference in-window |
| Sessions end | Plans, notes, and state survive as files |
| Subagents need to hand off | A file is a shared, inspectable medium |
| Work needs auditing | Git gives you history, diff, and rollback for free |

This is the mechanism behind **state externalization** ([note 06](06-long-horizon-execution.md)) — progress lives in files, so the loop becomes re-entrant and independent of any single context window. It's also the mechanism behind **tool-call offloading**: keep the head and tail of a large tool output in-window above a token threshold, write the full output to disk, and let the model read it back only if needed. A 2,000-line log becomes ~40 lines plus a path.

Git deserves separate mention: it is the only rollback mechanism most harnesses have. Branch-per-agent turns parallel experimentation into a safe operation with a free undo.

---

## Bash as a general-purpose tool

The design bet: **you cannot pre-design every tool an agent will need.**

Harnesses ship a bash tool so the model can compose solutions by writing and executing code, rather than being limited to the API surface someone anticipated. A curated tool set handles known operations well; bash handles the long tail.

The tension is real — bash is maximally capable and maximally dangerous, which is exactly why it must be paired with a sandbox and hooks ([note 04](04-execution-boundaries.md)). The promote-from-bash heuristic resolves it: **start with shell, promote to a typed tool when you need a gate, a rendered result, an audit record, parallelism, or a retry policy.**

---

## The layered mental model

Reading the components as concentric layers:

```
┌─ Deterministic shell ──────────────────────────┐  hooks, permissions,
│  ┌─ Orchestration ──────────────────────────┐  │  schema validation
│  │  ┌─ The loop ─────────────────────────┐  │  │  (cannot be argued with)
│  │  │  ┌─ Context assembly ──────────┐   │  │  │
│  │  │  │   [ model call ]            │   │  │  │
│  │  │  └─────────────────────────────┘   │  │  │
│  │  │   tool execution · verification    │  │  │
│  │  └────────────────────────────────────┘  │  │
│  │   subagents · handoffs · model routing   │  │
│  └──────────────────────────────────────────┘  │
│   sandbox · filesystem · git · observability   │
└────────────────────────────────────────────────┘
```

Two rules read straight off the diagram:

1. **Reliability requirements move outward.** Anything that must hold every time belongs in the deterministic shell, not in a sentence inside the model call. A prompt can be ignored; a hook cannot.
2. **Cost and blast radius grow outward too.** Adding a sentence is cheap and reversible; adding a subagent tier multiplies tokens and loses cross-agent context. Reach for the innermost layer that can actually hold the requirement.

---

## Curriculum view: the causal build order

Vercel Academy's 38-lesson harness build is organized so that *"each step exists because the previous one broke something."* That ordering is the best available answer to **what to build first**:

| # | Module | The break it answers |
|---|---|---|
| 1 | The agent loop | A chatbot can't act |
| 2 | Tool design | The model picks the wrong tool |
| 3 | System prompt | Behavior is inconsistent across runs |
| 4 | Sandbox abstraction | Execution is unsafe / environment-coupled |
| 5 | Context management | Tokens grow unbounded in long sessions |
| 6 | Subagent delegation | One context can't hold the whole task |
| 7 | Sandbox lifecycle | Cloud sandboxes cost money while idle |
| 8 | Human-in-the-loop | The agent guesses when it should ask |
| 9 | Planning & verification | Work is declared done without being checked |
| 10 | Surfaces | The same agent needs CLI and web |
| 11 | Extensibility | Adding a tool means editing the core |

Note the shape: **capability first (1–4), then the constraints that make capability survivable at scale (5–9), then productization (10–11).** Teams that invert this — building orchestration before verification — produce the Stage-0-claiming-Stage-2 failure in [note 08](08-maturity-and-failure-modes.md).

Two design principles worth lifting out:

- **"Swap the backend, the tools don't change."** The `Sandbox` interface is uniform; local `fs`/`child_process`, in-memory copy-on-write, and remote cloud sandboxes are interchangeable behind it. Tools bind to the interface, never the backend.
- **Extensibility without core edits.** Event buses, a tool registry, and progressive skill disclosure mean adding capability is registration, not surgery.

---

## Minimum viable harness

Cutting the inventory to what a first real harness needs:

1. A **tool loop** with typed schemas
2. A **sandbox** (even just a working-directory boundary)
3. A **filesystem** the agent can read and write
4. A **plan file** for anything past ~5 steps
5. One **verification gate** with a binary pass/fail
6. **Structured traces** of every step

Six items. Everything else in this note is elaboration on those.

---

## Working reference

`~/.claude/refs/agent-runtime.md` — runtime boundaries and where execution happens.
`~/.claude/refs/agent-tools.md` — tool schema rules and the promote-from-bash heuristic.

---

→ Next: [03-tool-design.md](03-tool-design.md) — the component with the highest failure rate.
