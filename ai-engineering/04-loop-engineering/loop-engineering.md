---
origin: notion-export
confidence: high
sources:
  - https://www.langchain.com/blog/the-art-of-loop-engineering
  - https://addyosmani.com/blog/loop-engineering/
  - https://newsletter.pragmaticengineer.com/p/what-is-loop-engineering
  - https://machinelearningmastery.com/an-introduction-to-loop-engineering/
  - https://www.mindstudio.ai/blog/what-is-loop-engineering-ai-coding-agents
  - https://medium.com/@adnanmasood/loop-engineering-a-guide-for-engineers-and-practitioners-893bb65ea943
  - https://www.anthropic.com/institute/recursive-self-improvement
  - https://www.marktechpost.com/2026/07/12/guide-to-loop-engineering/
  - https://github.com/karpathy/autoresearch
  - https://arxiv.org/abs/2603.23420
  - https://adk.dev/agents/workflow-agents/loop-agents/
  - https://vercel.com/i/what-are-agentic-workflows
  - https://vercel.com/kb/guide/how-to-run-a-multi-step-research-agent-on-vercel
  - https://claude.com/blog/getting-started-with-loops
  - https://levelup.gitconnected.com/what-is-loop-engineering-how-it-is-different-than-harness-engineering-0e764f373fb1
  - https://notes.kodekloud.com/docs/Loop-Engineering/What-Is-a-Loop/What-is-Loop-Engineering/page.md
  - https://www.aibuilderclub.com/blog/loop-engineering-anthropic-playbook
  - https://github.com/walkinglabs/learn-harness-engineering
cleaned: 2026-10-28
---
# Loop Engineering

> Overview note. Topic depth lives in [notes/](notes/), practice in [practice/](practice/), copy-ready files in [templates/](templates/).

---

## Position in the stack

Loop engineering is the **fourth layer**. The harness gives one agent run its tools, boundaries and verification. The loop decides **when the run happens again, against what goal, and when it stops**. With a full harness you are still inside the loop: you read the progress file, choose the next task, type the prompt. Loop engineering moves you outside it.

> *"Loop engineering is replacing yourself as the person who prompts the agent. You design the system that does it instead."* — Addy Osmani

**Inherits the weaknesses of:** harness engineering. A loop running inside a poorly instrumented harness repeats unreliable behavior faster, and that's harder to debug than a single bad run.

---

## The thesis

> **A loop is a goal plus a scorekeeper, repeated, with a way to stop.**

Every cycle is the same shape in every vocabulary: gather → act → verify (Anthropic), try → test → fix → save (KodeKloud). Two things must exist before the first pass: a **goal** small enough to finish, and a **scorekeeper** that is objective, automatic, fast, clear and hard to fake. Generation becomes nearly free; the binding constraint moves to **verification**, which is why the hard failures are human ones (comprehension rot, cognitive surrender) rather than mechanical ones.

---

## Two axes

A loop has a position on each:

| Capability level (LangChain): *what it automates* | Autonomy rung: *what the operator handed off* |
|---|---|
| 1. Agent loop: work | 1. Turn-based: tool approval |
| 2. Verification loop: quality | 2. Goal-based: the stop condition (`/goal`) |
| 3. Event-driven loop: invocation | 3. Time-based: the trigger, to a clock (`/loop`) |
| 4. Hill-climbing loop: improvement | 4. Proactive: the trigger and session (`/schedule`) |

Levels 1–3 automate work; level 4 automates improvement and starts editing the harness underneath it. Earn each rung with a verifier that has been seen catching a real failure.

---

## Topic notes

1. [What a loop is](notes/01-what-a-loop-is.md) — the cycle, goal + scorekeeper, green first, when not to build a loop, lineage, inside vs outside the loop, the map of the pillar.
2. [Loop shapes](notes/02-loop-shapes.md) — the five required parts, the canonical skeleton, patterns by task shape, ReAct / Plan-then-Act / Plan-and-Revise, loop vs workflow vs graph.
3. [The scorekeeper](notes/03-the-scorekeeper.md) — the five traits, hard-to-fake defenses, the write boundary, deterministic first, maker and checker.
4. [Building blocks](notes/04-building-blocks.md) — automations, worktrees, skills, connectors, sub-agents, memory; the whole loop in motion; add them only when a failure demands it.
5. [Long-running loops](notes/05-long-running-loops.md) — context as a budget, three memory tiers and five fields, context drift, Ralph, initializer/worker, compaction vs reset.
6. [Triggers and schedules](notes/06-triggers-and-schedules.md) — capability level 3, run-until-done vs timer, `/goal` / `/loop` / `/schedule`, cost ceilings, patterns in the wild.
7. [The autonomy ladder](notes/07-autonomy-ladder.md) — the four handoffs, how they map to capability levels, the adoption ladder.
8. [Self-improving loops](notes/08-self-improving-loops.md) — capability level 4, the evolve loop and the anti-busywork rule, `autoresearch`, bilevel autoresearch, RSI.
9. [Failure modes and guardrails](notes/09-failure-modes-and-guardrails.md) — the structural three, the traps table, the four silent costs, the ratchet rules, layered exits, budgets, the design checklist.
10. [Framework bindings](notes/10-framework-bindings.md) — ADK `LoopAgent`, Vercel `ToolLoopAgent` / `WorkflowAgent`, LangGraph.

---

## The loop ↔ harness boundary

| Harness engineering | Loop engineering |
|---|---|
| One run: tools, sandbox, hooks, verification inside the run | Many runs: what starts the next one, and when to stop |
| Progress file written at session end | Progress file *read* by the next pass to pick its own task |
| Generator/evaluator separation | Maker/checker as the loop's quality ceiling |
| Ratchet on the harness (every failure → a rule) | Ratchet on the work (score only goes up, else roll back) |

The moment the agent's next run starts without you typing a prompt, you've crossed from harness into loop.

---

## Resources

- Osmani, loop engineering: https://addyosmani.com/blog/loop-engineering/
- LangChain, the art of loop engineering: https://www.langchain.com/blog/the-art-of-loop-engineering
- Pragmatic Engineer: https://newsletter.pragmaticengineer.com/p/what-is-loop-engineering
- KodeKloud, Loop Engineering course notes: https://notes.kodekloud.com/docs/Loop-Engineering/What-Is-a-Loop/What-is-Loop-Engineering/page.md
- AI Builder Club, the Anthropic playbook: https://www.aibuilderclub.com/blog/loop-engineering-anthropic-playbook
- *learn-harness-engineering*, lecture 13 and project 07: https://github.com/walkinglabs/learn-harness-engineering
- Claude, getting started with loops: https://claude.com/blog/getting-started-with-loops
- Masood, a guide for engineers: https://medium.com/@adnanmasood/loop-engineering-a-guide-for-engineers-and-practitioners-893bb65ea943
- Karpathy, `autoresearch`: https://github.com/karpathy/autoresearch
- Qu & Lu, bilevel autoresearch: https://arxiv.org/abs/2603.23420
- Anthropic, recursive self-improvement: https://www.anthropic.com/institute/recursive-self-improvement
- Google ADK `LoopAgent`: https://adk.dev/agents/workflow-agents/loop-agents/
- Vercel, agentic workflows: https://vercel.com/i/what-are-agentic-workflows
