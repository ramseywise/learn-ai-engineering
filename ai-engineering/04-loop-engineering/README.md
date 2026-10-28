# 04 — Loop Engineering

> Depth layer. Summary: [interviewing/guides/4-agents](../../interviewing/guides/4-agents/00-overview.md)
> Position in the stack: *the harness runs one agent well; the loop runs it again, against a goal, until a scorekeeper says stop*.
> Overview note: [loop-engineering.md](loop-engineering.md) · Topic depth: [notes/](notes/) · Practice: [practice/](practice/) · Templates: [templates/](templates/)

---

## What it is

Loop engineering is the discipline of designing the system that prompts your agent, so you don't have to. A loop is **a goal plus a scorekeeper, repeated, with a way to stop**: each cycle gathers context, acts, verifies, and either saves the change or rolls it back.

*"Loop engineering is replacing yourself as the person who prompts the agent. You design the system that does it instead."* — Addy Osmani

Two independent axes place any loop:

- **Capability level** (LangChain), *what the loop automates*: agent loop (work) → verification loop (quality) → event-driven loop (invocation) → hill-climbing loop (improvement).
- **Autonomy rung**, *what the operator has handed off*: tool approval → the stop condition (`/goal`) → the trigger, to a clock (`/loop`) → the trigger and session (`/schedule`).

The binding constraint moves from generation to **verification**. That's why the scorekeeper comes before the loop, and why the hardest failures are human ones (comprehension rot, cognitive surrender), not mechanical ones.

**Inherits the weaknesses of:** harness engineering. A loop running inside a poorly instrumented harness repeats unreliable behavior faster, and that's harder to debug than a single bad run.

---

## Syllabus

Read the notes in order; each one is earned by the one before. Start the labs after note 03.

| # | Note | Covers | Lab |
|---|---|---|---|
| 1 | [What a loop is](notes/01-what-a-loop-is.md) | The cycle, goal + scorekeeper, green first, when not to loop, lineage, inside vs outside, the map | — |
| 2 | [Loop shapes](notes/02-loop-shapes.md) | Five required parts, the canonical skeleton, patterns by task shape, loop vs workflow vs graph | — |
| 3 | [The scorekeeper](notes/03-the-scorekeeper.md) | Five traits, hard-to-fake defenses, write boundary, deterministic first, maker/checker | [Lab 1](practice/01-exercises.md#lab-1--goal-loop-manual-vs-goal) |
| 4 | [Building blocks](notes/04-building-blocks.md) | Automations, worktrees, skills, connectors, sub-agents, memory; add only when a failure demands it | [Lab 3](practice/01-exercises.md#lab-3--makerchecker-step-outside-the-loop) |
| 5 | [Long-running loops](notes/05-long-running-loops.md) | Context budget, memory tiers and fields, context drift, Ralph, initializer/worker, compaction vs reset | [Lab 4](practice/01-exercises.md#lab-4--guarded-ralph-loop) |
| 6 | [Triggers and schedules](notes/06-triggers-and-schedules.md) | Level 3, run-until-done vs timer, `/goal` / `/loop` / `/schedule`, cost ceilings | [Lab 2](practice/01-exercises.md#lab-2--timer-loop-monitoring-as-a-heartbeat) |
| 7 | [The autonomy ladder](notes/07-autonomy-ladder.md) | The four handoffs, mapping to capability levels, the adoption ladder | — |
| 8 | [Self-improving loops](notes/08-self-improving-loops.md) | Level 4, the evolve loop, anti-busywork, three-layer verification, four media, self-modification as release, sleep learning, `autoresearch`, bilevel, RSI | [Lab 5](practice/01-exercises.md#lab-5--evolve-loop) · [P2](practice/02-trajectory-verifier/README.md) · [P3](practice/03-self-modifying-agent/README.md) |
| 9 | [Failure modes and guardrails](notes/09-failure-modes-and-guardrails.md) | Structural and human failures, four silent costs, ratchet rules, layered exits, budgets, design checklist | Drills |
| 10 | [Framework bindings](notes/10-framework-bindings.md) | ADK `LoopAgent`, Vercel `ToolLoopAgent` / `WorkflowAgent`, LangGraph | — |

### Practice ([practice/](practice/))

- [P1 — Exercises](practice/01-exercises.md): five labs (goal loop → timer loop → maker/checker → guarded Ralph → evolve) and a drill per note. These continue the [harness labs](../03-harness-engineering/notes/practice/04-exercises.md); Labs 1–3 adapt project 07 of *learn-harness-engineering*.
- [P2 — Trajectory verifier](practice/02-trajectory-verifier/README.md): outcome, process and quality layers with evidence for each dimension, calibrated against expert labels (from *AI Agents in Depth*, Exp. 8-1). Offline, no API key.
- [P3 — Self-modifying agent](practice/03-self-modifying-agent/README.md): failure trajectories trigger a retry-policy patch behind a release gate that emits `release_to_canary` or `reject_candidate` (Exp. 8-5). Offline, no API key.

### Templates ([templates/](templates/))

| File | Use |
|---|---|
| [loop-contract.md](templates/loop-contract.md) | Fill in before the first pass: goal, acceptance criteria, scorekeeper, write boundary, trigger, stop rules, ratchet, human gates |
| [loop-state.md](templates/loop-state.md) | Read at the start of each pass, rewritten at the end: the five fields plus run stats |
| [maker-prompt.md](templates/maker-prompt.md) | The implementing agent: one small change per round, inside the boundary |
| [checker-prompt.md](templates/checker-prompt.md) | The verifying agent: runs the scorekeeper itself; PASS is a legitimate verdict |
| [ralph.sh](templates/ralph.sh) | Guarded Ralph loop: score ratchet with rollback, iteration, wall-clock and stall caps |

### Images ([images/](images/))

- `anthropic-agent-loop.png`, `anthropic-playbook-map.png`, used in [note 01](notes/01-what-a-loop-is.md).

---

## Resource map

### Related
- [reliable-agents.md](../03-harness-engineering/reliable-agents.md) — reliability patterns: retry logic, graceful degradation, human-in-the-loop escalation.
- [Harness note 06: long-horizon execution](../03-harness-engineering/notes/06-long-horizon-execution.md) — Ralph and compaction from the harness side.

### Interviewing guide
- [4-agents](../../interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [AI-Agents-in-LangGraph-main](../../generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main/) — agent loops implemented as LangGraph graphs.
- [internet-search-agent-main](../../generative-ai/07-agentic-applications/internet-search-agent-main/) — concrete loop with web-search tooling.

### External sources

Read into [notes/](notes/) on 2026-10-28. Full list in [loop-engineering.md](loop-engineering.md#resources).

| Source | Contributes |
|---|---|
| [Osmani](https://addyosmani.com/blog/loop-engineering/) | The definition, building blocks, morning loop, human failure modes |
| [LangChain](https://www.langchain.com/blog/the-art-of-loop-engineering) | The four capability levels |
| [KodeKloud course notes](https://notes.kodekloud.com/docs/Loop-Engineering/What-Is-a-Loop/What-is-Loop-Engineering/page.md) | Try/test/fix/save, scorekeeper traits, the six components, traps table, design-your-own-loop (summarized, not copied) |
| [AI Builder Club](https://www.aibuilderclub.com/blog/loop-engineering-anthropic-playbook) | The Anthropic playbook map, the autonomy ladder, the evolve loop |
| [learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering) | Lecture 13 (`/goal` vs `/loop`, silent costs, adoption ladder) and project 07 (the labs, maker/checker prompts) |
| [Karpathy `autoresearch`](https://github.com/karpathy/autoresearch) + [bilevel](https://arxiv.org/abs/2603.23420) | The level-4 worked example |
| Li, *AI Agents in Depth* (2026), [ch. 8 Continual Evolution](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter8.md) | Synthesized into [08](notes/08-self-improving-loops.md#verify-before-you-learn): three-layer verification, four media, change contracts, harness updating vs benefit, sleep learning, "done ≠ progress"; safety boundaries in [09](notes/09-failure-modes-and-guardrails.md#guardrails-for-self-modifying-loops). Labs copied as [P2](practice/02-trajectory-verifier/README.md) and [P3](practice/03-self-modifying-agent/README.md). Upstream only: [gaia-experience](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/gaia-experience) (8-2), [prompt-auto-optimization](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/prompt-auto-optimization) (8-3), [browser-use-rpa](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/browser-use-rpa) (8-4), [self-evolution-eval](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/self-evolution-eval) (8-6), [self-evolving-tools](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/self-evolving-tools) |

### Next layer
→ [05-graph-engineering/](../05-graph-engineering/README.md) — graph engineering composes loops into multi-agent topologies.

---

## Working References

Claude Code convention references that map to this pillar. These files live at `~/.claude/refs/` and can be consulted in any Claude Code session.

### `agent-architecture.md`
Conventions for loop shape selection, termination control, planning strategy, and multi-agent coordination.

Key topics for this pillar:
- Three loop shapes: ReAct (observe→reason→act, repeat), Plan-then-Act (fixed plan), Plan-and-Revise (plan→act→assess→replan) — prefer ReAct for ≤10 steps
- What terminates a turn: `end_turn`, `tool_use`, `max_tokens` (treat as error), context exhaustion — the harness (not the model) sets max iteration count
- Planning: plan-up-front vs. ReAct choice is architectural; hybrid: generate plan, execute, allow per-step replan flag
- Schema contracts: request/response/error schemas as the public API; add fields, never remove until all callers migrate
- State vs. context: context window (this turn), agent state (session), persistent store (cross-session)

### `agent-tools.md`
Conventions for tool design and the agent-loop integration points where tools are called and their results processed.

Key topics for this pillar:
- Promote-from-bash heuristic: when the loop needs a structured gate or retry hook, promote the tool
- Tool result handling: evict completed-step results from context; keep final outputs only (from `agent-context.md`)
- Parallel-safe tool design: tools called in the same loop turn must not race; document serialization strategy
- Observability hooks: each tool call emits a span with tool name, version, input hash, duration, return code, parent trace ID

### `agent-runtime.md`
Conventions for the deployment topology that hosts the agent loop — what each topology forces on loop design.

Key topics for this pillar:
- Three topologies: stateless function, long-lived process, managed runtime — each imposes different constraints on loop state and timeout
- Stateless function constraints: no in-memory session manager, strict timeout bound (Vercel: 10s/60s/300s by tier), no background tasks, state must be externalized
- Cost and latency levers: LLM input tokens (30–50%), output tokens (20–30%), retrieval (10–20%); prompt caching and model tier selection are highest-leverage
- Model routing: cheapest model that can do the job per step type; cascade on refusal or quality gate failure (last resort, not first-line)
- Streaming: stream early; close with structured error frame on mid-stream failure

### `agent-reliability.md`
Conventions for loop-level error recovery — what the loop does when a tool fails, when the model refuses, or when the context is exhausted.

Key topics for this pillar:
- Context exhaustion handling: compact and resume from last checkpoint (coordinated with `agent-context.md §3`)
- Resumability requirements: checkpoint after each plan step; deterministic step re-execution; log resume point on restart
- Refusals: never retry as-is; log, emit `refusal` span event, route to human or return structured error
- Schema violation: retry with rephrased prompt once; fail hard on second violation
