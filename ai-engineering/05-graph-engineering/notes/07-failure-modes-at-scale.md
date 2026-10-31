---
origin: web-authored
sources:
  - https://www.eigent.ai/blog/graph-engineering-ai-agents
  - https://docs.langchain.com/langgraph
  - https://youmind.com/landing/x-viral-articles/graph-engineering-ai-agent-loops
  - https://www.anthropic.com/engineering/multi-agent-research-system
  - https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter10.md
  - https://arxiv.org/abs/2512.08296
confidence: medium
cleaned: 2026-10-31
---
# 7 — Failure Modes at Scale

> A single loop fails by not converging. A graph fails by mis-routing, deadlocking, racing on shared state, and drifting away from reality while staying perfectly self-consistent.

---

## Two families of failure

| Family | Comes from | Examples |
|---|---|---|
| **Mechanical** | The wiring | Infinite cycles, races on shared keys, unbounded fan-out, mis-routing |
| **Control** | Many feedback loops interacting | Goodhart, upward blindness, inter-loop conflict, measurement decay |

Mechanical failures are mostly caught by the framework if you let it. Control failures aren't caught by anything unless you design for them.

---

## Mechanical failures

| Failure | Symptom | Root cause | Detect | Fix |
|---|---|---|---|---|
| **Oscillation / infinite cycle** | Run never ends; the same two nodes alternate | A back-edge with no bound; two nodes that each route to the other | `GraphRecursionError` (LangGraph's `recursion_limit`, default 25 super-steps) | An attempt counter in state checked by the router; a per-node bound |
| **Deadlock** | Run stalls at a join | A join waits for a branch that was never scheduled, or two nodes each wait for the other's output | Run idle with no node active | Make every join's inputs explicit; route errors to a node that still writes the expected key |
| **Race on shared state** | `InvalidUpdateError`, or silently lost work outside LangGraph | Two parallel branches write one key with no reducer | The error, if your framework raises it | A reducer, or one writer per key ([03](03-state-and-reducers.md)) |
| **Unbounded fan-out** | Token spend spikes; rate limits | `Send` over an input with no cap | Cost per run | Cap N; batch; budget per run *and* per node ([08](08-governance-and-production.md)) |
| **Mis-routing** | Right answer from the wrong specialist, or a wrong answer from a confident one | Router prompt too vague; status values drift | Route distribution in traces; eval on the router alone | Treat the router as a classifier: give it a labelled test set ([06-eval](../../06-eval/README.md)) |
| **File-space collision** | Parallel workers overwrite each other's files | Workers share a working directory | Diffs that don't match any one worker | One worktree or directory per worker |

Every node that loops should be bounded on its own, not only the graph as a whole. n8n's workflow builder caps its Discovery node at 50 iterations and its Builder at 100 per session ([08](08-governance-and-production.md#case-study-n8ns-ai-workflow-builder)).

---

## Swarm-scale failures

These failures only appear once work is parallel or spread across agents.

### Correlated errors

Parallel workers usually share a model, a prompt template and a retrieval index. When one makes a mistake, the others tend to make the same one, so N agreeing workers are much less evidence than N independent ones. A synthesiser that counts votes will be confidently wrong. Vary what you can (sources, prompts, models), and make the synthesiser check claims against sources rather than against each other.

### Verifiers need isolated context

> **A verifier that can see the generator's reasoning tends to ratify it.**

Self-agreement bias: if the reviewer reads the generator's chain of thought, it inherits the generator's framing and finds its argument convincing. Give the verifier the **task and the output**, not the conversation that produced it. This is the graph form of the maker/checker separation ([04-loop note 03](../../04-loop-engineering/notes/03-the-scorekeeper.md)), and it's why subagents' separate context windows are a feature ([03-harness note 07](../../03-harness-engineering/notes/07-orchestration.md)).

### Byzantine, not crash

Distributed systems separate **crash faults** (a node stops) from **Byzantine faults** (a node keeps running and returns wrong answers). Agents fail the second way: a worker that hallucinates still returns a well-formed summary. Timeouts and retries catch crashes; only **cross-validation, voting over independent sources, and deterministic checks** catch Byzantine faults ([Li ch. 10](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter10.md)).

### Semantic conflicts

Locks and reducers prevent **lost updates**, where two writers clobber one key. They don't prevent **semantic conflicts**, where both writes succeed and the result is still wrong. The book's example: two agents each insert a figure and renumber the figures, and every number in the document is now off by one. Optimistic locking (read `config.json` at version 3, write only if it's still 3, then bump it to 4) turns the silent conflict into a retry. One worktree per agent is copy-on-write: conflicts surface at merge time, where a human or a test can see them.

### Cascading amplification

An early error becomes a premise for everything downstream. In the book's translation lab, the glossary agent rendered "reasoning" as 推理 (inference). The translator applied it faithfully, and the proofreader, checking against the glossary, saw perfect consistency and passed it. Every stage did its job and the error survived all of them. The fix is a check from an **independent perspective**: a reviewer that reads the output against the source, not against the upstream artifact.

Topology sets how far an error travels. Kim et al. ([arXiv:2512.08296](https://arxiv.org/abs/2512.08296), 2025-12) counted trace-level errors relative to a single agent across six benchmarks: independent agents whose outputs were merged without any cross-checking amplified errors 17.2×, while a centralized orchestrator that validated workers' output before aggregating held it to 4.4×. Read that as descriptive: in their regression, once efficiency and overhead were controlled for, error amplification itself was not a significant predictor of success (p = 0.658).

### MAST: a taxonomy

MAST (Multi-Agent System failure Taxonomy) classifies 14 failure modes from annotated traces into three groups, with inter-annotator agreement κ = 0.88:

| Group | Examples |
|---|---|
| **System design** | Disobeying the role spec; step repetition; losing conversation history; not knowing when to stop |
| **Inter-agent misalignment** | Ignoring another agent's input; withholding information; reasoning–action mismatch; derailing from the task |
| **Missing verification** | Premature termination; no or incomplete verification; incorrect verification |

The finding that matters: fixing prompts and roles in ChatDev improved it by only **+15.6%**. Most failures are structural and need topology or verification changes, not better wording.

### Runaway loops

An unbounded multi-agent loop fails three ways: **token cost**, **comprehension debt** (the system produces more than anyone can review) and **cognitive surrender** (people stop reviewing and accept whatever comes out). The first shows up on the bill; the other two don't show up anywhere until something breaks.

---

## Control failures

Eigent's contribution is a control-theory reading of why independent loops degrade once there are many of them. Eigent is a vendor blog and doesn't cite the underlying literature, but each failure has a well-known name:

| Failure | What happens | Older name |
|---|---|---|
| **Goodhart** | A metric detaches from what it was meant to measure once a loop optimises it hard | Goodhart's law: "when a measure becomes a target, it ceases to be a good measure" |
| **Upward blindness** | A loop can't question its own target or reference value | A controller can't see its own setpoint |
| **Inter-loop conflict** | Independent loops fight over shared resources without knowing about each other | Coupled control loops |
| **Measurement decay** | Sensors drift and definitions change while loops keep running on stale data | Sensor drift; concept drift |

### Four design principles

| Principle | Counter to | Description |
|---|---|---|
| **Paired metrics** | Goodhart | Every optimisation metric gets a counter-metric and an anchor metric |
| **Owned references** | Upward blindness | Targets are owned by slower loops, so objectives can't change silently |
| **Separated cadences** | Inter-loop conflict | Fast loops *escalate* to slower loops rather than overriding them |
| **Frozen nodes** | Measurement decay | Some measurements are deliberately not tunable |

### Anchors

> **Anchors are "external fixed nodes the internal machinery is forbidden to rewrite."**

Held-out test sets, physical inventory counts, banked revenue, safety specifications. Without anchors, a graph becomes *"perfectly self-consistent while drifting arbitrarily far from reality."* Every loop agrees with every other loop, and all of them are wrong.

This is the 不易 (immutable) layer of the SANYI change contract (`~/workspace/librarian/data/wiki/meta/sanyi-change-contract.md`): the invariants that must never become configurable. **An anchor made tunable is an anchor that will eventually be tuned.**

---

## A pre-flight check

Before running a graph unattended:

- [ ] Every back-edge has a counter, and `recursion_limit` is set deliberately.
- [ ] Every looping node has its own iteration bound.
- [ ] Every shared key has one writer or a reducer.
- [ ] Every `Send` has a cap on N.
- [ ] Every verifier sees the output and the task, not the generator's reasoning.
- [ ] Parallel workers have separate file spaces.
- [ ] Every reviewer can check against something the producer didn't write: tests, sources, or execution.
- [ ] At least one anchor the graph cannot edit, and someone watching it.

---

## Working reference

`~/.claude/refs/agent-reliability.md` — bounds, retries, failure handling. `~/workspace/librarian/data/wiki/meta/sanyi-change-contract.md` — the immutable layer.

---

→ Next: [08-governance-and-production.md](08-governance-and-production.md) — tracing, attribution, budgets, and a production case study.
