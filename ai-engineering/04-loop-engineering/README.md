# 04 — Loop Engineering

> Depth layer. Summary: [interviewing/guides/4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md)
> Position in the stack: *the harness runs one agent well; the loop runs it again, against a goal, until a scorekeeper says stop*.
> Start with [note 01](notes/01-what-a-loop-is.md) · Notes: [notes/](notes/) · Deck: [slides/](slides/loop-engineering.pptx)

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

## Start here

1. Read [note 01](notes/01-what-a-loop-is.md) (the cycle, goal + scorekeeper, the two axes) and [note 03](notes/03-the-scorekeeper.md) (the part everything depends on).
2. Read the rest of the notes in order; each is earned by the one before.
3. The [lecture deck](slides/loop-engineering.pptx) is the notes as a 4-part talk. Everything on a slide is in the note named in its footer.

## Lab

A loop with a scorekeeper: scripted makers, an independent checker with held-out tests, and a stop reason for each run. It comes in both languages, side by side, on the same inputs. Both run offline with a stub by default, and each README says how to swap in a real model.

| Language | Folder | Run |
|---|---|---|
| TypeScript | [practice/loop-scorekeeper/](practice/loop-scorekeeper/README.md) | `cd practice/loop-scorekeeper && npx tsx run.ts` |
| Python | [practice/loop-scorekeeper-py/](practice/loop-scorekeeper-py/README.md) | `cd practice/loop-scorekeeper-py && uv run run.py` |

## Layout

```
README.md      this file: overview, syllabus, rules of thumb, sources
notes/         01–10, the course. Copy-ready artefacts live inline: maker/checker
               prompts (03), loop-state.md and ralph.sh (05), loop-contract.md (09)
slides/        deck.yaml → loop-engineering.pptx (make slides PILLAR=04-loop-engineering)
practice/      the lab, in TypeScript and Python
sources/       the papers (Chen, Zhong, Zhu 2026) and images/ with every figure the notes use
```

## Syllabus

| # | Note | Covers |
|---|---|---|
| 1 | [What a loop is](notes/01-what-a-loop-is.md) | The cycle, goal + scorekeeper, green first, when not to loop, lineage, inside vs outside, the two axes |
| 2 | [Loop shapes](notes/02-loop-shapes.md) | Five required parts, the canonical skeleton, decision points, patterns by task shape, loop vs workflow vs graph |
| 3 | [The scorekeeper](notes/03-the-scorekeeper.md) | Five traits, hard-to-fake defenses, write boundary, deterministic first, maker/checker prompts |
| 4 | [Building blocks](notes/04-building-blocks.md) | Automations, worktrees, skills, connectors, sub-agents, memory; the whole loop in motion |
| 5 | [Long-running loops](notes/05-long-running-loops.md) | Context budget, memory tiers, the loop-state file, context drift, the guarded Ralph script, initializer/worker, compaction vs reset |
| 6 | [Triggers and schedules](notes/06-triggers-and-schedules.md) | Level 3, run-until-done vs timer, `/goal` / `/loop` / `/schedule`, pre-checks, cost ceilings |
| 7 | [The autonomy ladder](notes/07-autonomy-ladder.md) | The four handoffs and the evidence each needs, mapping to capability levels, the adoption ladder |
| 8 | [Self-improving loops](notes/08-self-improving-loops.md) | Level 4, the evolve loop, anti-busywork, three-layer verification, four media, self-modification as release, plasticity vs stability, sleep learning, `autoresearch`, bilevel, RSI |
| 9 | [Failure modes and guardrails](notes/09-failure-modes-and-guardrails.md) | Structural and human failures, four silent costs, ratchet rules, layered exits, budgets, design checklist, the loop contract |
| 10 | [Framework bindings](notes/10-framework-bindings.md) | ADK `LoopAgent`, Vercel `ToolLoopAgent` / `WorkflowAgent`, LangGraph |

### Upstream labs

- Upstream labs, worked through in [note 08](notes/08-self-improving-loops.md): [trajectory-verifier](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/trajectory-verifier) (Exp. 9-1, three-layer verification with calibration) and [self-modifying-agent](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/self-modifying-agent) (Exp. 9-6, failure-triggered patch behind a canary gate). Clone `bojieli/ai-agent-book`, `cd chapter9/<lab>`, run `python demo.py` (offline, no API key).

---

## Rules of thumb

- **Foundation:** goal and scorekeeper before anything runs. Go green once, then add parts only when a failure demands them.
- **Scorekeeper:** deterministic first, outside the loop's write scope, some checks held out. The checker is a different agent and may say "clean".
- **Ratchet:** the score only goes up. One small change per pass; save it or roll it back. Fix breaks before new work.
- **Long runs:** state on disk, not in context. One item per session; leave the repo clean.
- **Triggers:** prefer events to polling; a no-op run exits before calling the model. Cap per run and per day.
- **Autonomy:** climb one rung at a time, each earned with a verifier you have seen catch a real failure.
- **Stopping:** layered, independent exits. A cap is an escalation, never a success.
- **Self-improvement:** "no change needed" is a successful outcome; every self-edit is a candidate that must pass a gate the loop cannot edit.

---

## Resource map

### Related
- [03 note 08, production reliability primitives](../03-harness-engineering/notes/08-maturity-and-failure-modes.md#production-reliability-primitives) — reliability patterns: retry logic, graceful degradation, human-in-the-loop escalation.
- [Harness note 06: long-horizon execution](../03-harness-engineering/notes/06-long-horizon-execution.md) — Ralph and compaction from the harness side.

### Interviewing guide
- [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [AI-Agents-in-LangGraph-main](../../generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph.md) — agent loops implemented as LangGraph graphs.
- [internet-search-agent-main](../../generative-ai/07-agentic-applications/notes/01-internet-search-agent.md) — concrete loop with web-search tooling.

### External sources

Read into [notes/](notes/) on 2026-10-28; papers in [sources/](sources/) added 2026-10.

| Source | Contributes |
|---|---|
| [Osmani](https://addyosmani.com/blog/loop-engineering/) | The definition, building blocks, morning loop, human failure modes |
| [LangChain](https://www.langchain.com/blog/the-art-of-loop-engineering) | The four capability levels |
| [KodeKloud course notes](https://notes.kodekloud.com/docs/Loop-Engineering/What-Is-a-Loop/What-is-Loop-Engineering/page.md) | Try/test/fix/save, scorekeeper traits, the six components, traps table, design-your-own-loop (summarized, not copied) |
| [AI Builder Club](https://www.aibuilderclub.com/blog/loop-engineering-anthropic-playbook) | The Anthropic playbook map, the autonomy ladder, the evolve loop |
| [learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering) | Lecture 13 (`/goal` vs `/loop`, silent costs, adoption ladder) and project 07 (the labs, maker/checker prompts) |
| [Karpathy `autoresearch`](https://github.com/karpathy/autoresearch) + [bilevel](https://arxiv.org/abs/2603.23420) | The level-4 worked example |
| Li, *AI Agents in Depth* (2026), [ch. 9 Continual Evolution](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter9.md) | Synthesized into [08](notes/08-self-improving-loops.md#verify-before-you-learn): three-layer verification, four media, change contracts, harness updating vs benefit, sleep learning, "done ≠ progress"; safety boundaries in [09](notes/09-failure-modes-and-guardrails.md#guardrails-for-self-modifying-loops). Labs [trajectory-verifier](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/trajectory-verifier) (Exp. 9-1) and [self-modifying-agent](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/self-modifying-agent) (Exp. 9-6) are worked examples in note 08. Upstream only: [tau2-escalation-experience](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/tau2-escalation-experience) (9-2), [prompt-auto-optimization](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/prompt-auto-optimization) (9-3), [browser-use-rpa](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/browser-use-rpa) (9-5), [harness-safety-gate](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/harness-safety-gate) (9-7), [hermes-self-evolution](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/hermes-self-evolution) (9-8), [self-evolution-eval](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/self-evolution-eval) (9-9), [self-evolving-tools](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/self-evolving-tools) |
| Zhu et al. (2026), [JevAgentHarness](https://arxiv.org/abs/2610.21412) ([PDF](sources/zhu-2026-jevagentharness.pdf)) | Eight decision points per loop step and the confidence-threshold cascade, in [02](notes/02-loop-shapes.md#the-canonical-skeleton) (Fig. 3) |
| Chen et al. (2026), [Are Self-Evolving Agents Continual Learners?](https://arxiv.org/abs/2610.25858) ([PDF](sources/chen-2026-self-evolving-agents-continual-learners.pdf)) | Plasticity vs stability (r = −0.72) and why shared-prompt edits forget, in [08](notes/08-self-improving-loops.md#measuring-the-evolve-loop-itself) (Fig. 2) |
| Zhong et al. (2026), [DiscoveryRSI](https://arxiv.org/abs/2610.23839) ([PDF](sources/zhong-2026-discoveryrsi.pdf)) | A research-scale self-improving loop and the limits of its rubric, in [08](notes/08-self-improving-loops.md#at-the-frontier-recursive-self-improvement) (Fig. 1) |

Figures in [sources/images/](sources/images/): `aibuilderclub-*` (AI Builder Club, note 01), `li-ai-agents-in-depth-fig9-*` (Li, Apache-2.0, note 08), and crops from the three papers above (notes 02, 08). The other notes carry mermaid diagrams.

Further reading, cited in the notes:

- Pragmatic Engineer, what is loop engineering: https://newsletter.pragmaticengineer.com/p/what-is-loop-engineering
- Masood, a guide for engineers and practitioners: https://medium.com/@adnanmasood/loop-engineering-a-guide-for-engineers-and-practitioners-893bb65ea943
- Machine Learning Mastery, an introduction to loop engineering: https://machinelearningmastery.com/an-introduction-to-loop-engineering/
- MindStudio, loop engineering for AI coding agents: https://www.mindstudio.ai/blog/what-is-loop-engineering-ai-coding-agents
- MarkTechPost, guide to loop engineering: https://www.marktechpost.com/2026/07/12/guide-to-loop-engineering/
- Level Up Coding, loop vs harness engineering: https://levelup.gitconnected.com/what-is-loop-engineering-how-it-is-different-than-harness-engineering-0e764f373fb1
- Claude, getting started with loops: https://claude.com/blog/getting-started-with-loops
- Anthropic, recursive self-improvement: https://www.anthropic.com/institute/recursive-self-improvement
- Google ADK `LoopAgent`: https://adk.dev/agents/workflow-agents/loop-agents/
- Vercel, agentic workflows: https://vercel.com/i/what-are-agentic-workflows · multi-step research agent: https://vercel.com/kb/guide/how-to-run-a-multi-step-research-agent-on-vercel

Papers with local PDFs, mapped to notes: [references.md](references.md). **★** marks the ones to read first.

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
