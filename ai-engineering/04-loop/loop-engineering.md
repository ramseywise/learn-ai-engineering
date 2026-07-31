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
cleaned: 2026-07-29
---

# Loop Engineering — deep note

## 1. Definition and where it sits

Loop engineering is designing the cycle that keeps an agent correct and productive **when
nobody is watching**. Not "how do I phrase this?" but "what cycle re-prompts the agent,
checks it, and decides when it quits?"

Two framings worth holding together:

- **Addy Osmani (operator framing):** *"Loop engineering is replacing yourself as the
  person who prompts the agent. You design the system that does it instead."*
- **Adnan Masood (systems framing):** a loop is *"the trigger, the topology, the verifier,
  and the stop rules that decide what an agent does next and when it quits."* His tl;dr:
  *"stop prompting your agents and start designing the loops that prompt them."*

Boris Cherny's version of the shift, quoted in Pragmatic Engineer: agents now "prompt
Claude and figure out what to do. My job is to write loops."

Position in the progression: prompt → context → harness → **loop**. The harness
([03-harness](../03-harness/README.md)) supplies tools, state, and guardrails; the loop
decides how many times to use them and when to stop. The graph layer
([05-graph](../05-graph/README.md)) composes loops into multi-agent topologies.

A loop is *dynamic*, unlike a chain: the agent may go A → B, discover B failed, revise,
and only then reach C. A chain executes a predetermined sequence regardless of
intermediate results. That difference — feedback changing the next step — is the whole
discipline.

### Lineage

Geoffrey Huntley's "Ralph Wiggum" technique (mid-2025) was the crude ancestor: a bash
loop that re-invokes the agent forever, breaking work into small context windows and
persisting progress to the filesystem so the agent can amend its own plan between runs.
By May 2026 the harnesses absorbed the pattern — `/loop` (cadence-based) and `/goal`
(condition-based, run until done) ship in Codex, Hermes, and Claude Code, so nobody hand-rolls
the bash wrapper anymore.

---

## 2. The four levels (LangChain)

The canonical taxonomy. Each level wraps the previous one; production systems stack all four.

| Loop | Function | LangChain primitive | Buys you |
|------|----------|---------------------|----------|
| 1 — Agent | Model calls tools until the task is done | `create_agent` | Work automation |
| 2 — Verification | Grade the output, feed failures back | `RubricMiddleware`, `after_agent` hooks | Quality/consistency |
| 3 — Event-driven | External events trigger runs in the background | LangSmith Deployment (cron, webhooks), Fleet channels | Scale without invocation |
| 4 — Hill-climbing | Analyze traces, rewrite the harness itself | LangSmith Engine | Continuous self-improvement |

**Level 1 — Agent loop.** *"At its core, an agent is just a model calling tools in a loop
until a task is complete."* Running example in the post: a docs agent that takes an
improvement request, plans changes, clones the repo, edits files, opens a PR.

**Level 2 — Verification loop.** Wrap the agent in a grader that checks output against
criteria and returns feedback when it falls short. The docs agent runs tests post-submission:
links resolve, CI passes, the diff stayed in scope. Tradeoff stated plainly: *"adding
verification increases latency and cost per run. It's worth it when quality matters more
than speed"* — which is most production use cases.

**Level 3 — Event-driven loop.** The integrations layer: schedules, webhooks, and messages
trigger the agent inside your ecosystem. *"The agent isn't something you invoke manually;
it's a component running continuously."* The docs agent fires on every Slack message in a
channel.

**Level 4 — Hill-climbing loop.** The first three automate *work*; the fourth automates
*improvement*. Trace → analysis agent → rewritten harness config (prompt tweaks, tool
changes, grader refinements). *"The return arrow doesn't just loop back to the top — it
reaches inside and updates the agent loop directly."* For open-weight models the same
traces can feed an RL fine-tuning pipeline.

**Humans at every level**, explicitly: approval before sensitive tool calls (L1), humans as
graders for sensitive workflows (L2), review before output reaches users (L3), harness
changes reviewed before deploy (L4). *"Automation doesn't mean removing humans from the loop."*

---

## 3. Anatomy — the five required components

Consistent across ML Mastery, MindStudio, and Masood. A loop that is missing any of these
is a loop that will hang, thrash, or silently ship garbage.

1. **Testable goal.** Specific enough to *evaluate*. "Make all auth tests pass" is a loop
   invariant; "improve the app" is an infinite loop.
2. **Tool set.** Real environmental access — code execution, filesystem, terminal, test
   runner, docs lookup. Without it the agent cannot observe consequences, and the loop
   degenerates into repeated guessing.
3. **Context management.** Summarize and prune prior iterations into compact working
   memory. Prevents token overflow and keeps continuity across attempts.
4. **Termination logic.** *Layered, independent* exit conditions: success verification,
   iteration cap, token/budget cap, stalled-progress detection, escalation path to a human.
5. **Error handling.** Distinguish recoverable errors from hard blockers; change strategy
   based on error type rather than retrying the identical failed approach.

### The canonical loop skeleton

```
initialize state with goal
for step in range(MAX_STEPS):
    reason about current state
    choose a concrete action
    execute the tool against the real environment
    update state with the outcome
    compact context to prevent overflow
    if verifier says goal met: return success
    if no progress for N steps or budget exhausted: escalate
escalate to human  # cap reached, not success
```

*"Engineering is everything wrapped around"* the model — the model supplies the reasoning
step; every other line above is yours.

### Loop patterns — pick by task shape

| Pattern | Use when |
|---------|----------|
| Retry | Atomic task, clear pass/fail |
| Plan–Execute–Verify | Multi-step work where order matters |
| Explore–Narrow | Unfamiliar territory; fan out in parallel, then converge |
| Human-in-the-loop | Ambiguity or high stakes require judgment |

Vercel's parallel taxonomy for agentic workflows: **planning**, **tool use**,
**reflection**, **multi-agent collaboration** — with the sequencing advice to *start with
tool use, add reflection once stable, and introduce planning/multi-agent only after eval
infrastructure exists*.

---

## 4. Production building blocks (Osmani)

Five primitives plus a spine. This is the concrete inventory behind "design the system
that prompts the agent."

- **Automations — the heartbeat.** Scheduled discovery and triage that run independently.
  Findings land in a triage inbox. Example: daily CI-failure analysis, issue summarization,
  bug hunting.
- **Worktrees — parallel safety.** Isolated working directories so concurrent agents don't
  collide on files; each gets its own branch context over shared repo history.
- **Skills — intent preservation.** Standardized `SKILL.md` files codifying project
  knowledge so the agent doesn't re-derive conventions each cycle. Osmani's term for the
  cost of not doing this: **intent debt** — agents confidently guessing your conventions.
- **Plugins & connectors — environmental integration.** MCP connectors into trackers,
  databases, APIs, Slack. This is what upgrades a loop from "here's the fix" to "PR opened,
  ticket linked, Slack notified."
- **Sub-agents — separation of concerns.** Split the **maker** from the **checker** so the
  model never grades its own work. Common shape: explorer → implementer → verifier, with
  different models/effort per role.
- **Memory — the spine.** Durable markdown files or a board holding state *outside* the
  conversation, because the model forgets between runs. Tracks what's done, what was found,
  what's next.

**Worked example (Osmani's morning loop):** automation fires the triage skill → reads CI
failures, issues, commits → writes findings to markdown → opens isolated worktrees →
spawns a sub-agent to draft each fix → spawns a second sub-agent to verify → connectors
open the PR and update the ticket → anything unhandled lands in the triage inbox for human
review.

### Patterns in the wild (Pragmatic Engineer)

Two dominant architectures — **event-triggered** (Sentry error, new ticket, outage) and
**scheduled cron** (test stabilization, design review passes, long migrations). Reported
uses: automated incident response that investigates alerts and opens PRs; flaky-test agents
that reproduce and propose fixes; nightly test-babysitting that separates real regressions
from false negatives; a React → React Native migration running in 30-minute cycles.

Worth keeping the skeptical note in view — engineer Oded Messer observes that a repeatable
workflow "becomes tactical if the AI is capable enough or it's just a high level old-school
automation I can set up like a cron or a trigger." Much of loop engineering is automation
rediscovered; the new part is that the thing on the cron is nondeterministic, which is
exactly why verification and stop rules carry the weight.

---

## 5. Failure modes

**The three structural ones** (Masood):

1. **Context rot.** Working memory degrades as the transcript grows. Fix: summarization and
   pruning inside the loop, not after it.
2. **Termination failures.** Loops that run forever or stop arbitrarily. Fix: layered
   independent exit conditions *plus* no-progress detection.
3. **Weak verification.** Model self-grading is gameable. Fix: anchor on deterministic
   checks — tests, compilers, linters, type checkers — and use model judgment only above
   that floor.

**Loop-level pitfalls** (MindStudio): no exit condition; repeated failures without
adaptation; context overflow; vague goal specification; insufficient tool access.

**The human failure modes** (Osmani) — the more important half, since they don't show up in
traces:

- **Verification burden.** Loops make unattended mistakes *unattended*. Verifier sub-agents
  reduce but do not remove the need for human confirmation.
- **Comprehension debt.** Unreviewed code accrues faster than understanding. Faster loops
  widen the knowledge gap unless review is active.
- **Cognitive surrender.** *"The comfortable posture is the dangerous one."* The same loop
  structure produces opposite outcomes depending on the operator's intention.

> *"Build the loop. But build it like someone who intends to stay the engineer, not just
> the person who presses go."* — Osmani

---

## 6. Best practices

- **Start minimal** — one simple loop with one verifier before adding levels.
- **Define termination before implementation**, not after the first runaway.
- **Prefer deterministic verification** over model judgment wherever a check exists.
- **Layer independent exits**: success verifier, iteration cap, token budget, stall detector.
- **Feed structured feedback**, not raw output dumps, back into the next iteration.
- **Budget tool calls per iteration**; log everything with periodic summaries.
- **Keep durable memory outside the model.**
- **Test the failure paths deliberately** — not just the happy path.
- **Keep humans at decision points**: approval for sensitive actions, review gates on output.
- **Guardrails are explicit** (Vercel): iteration limits, tool allowlists, confidence
  thresholds; roll out shadow → canary → wide.

The through-line: treat an autonomous run as a **thermostat**, not a conversation partner.
Measurable checks, clear termination, deliberate human checkpoints where judgment matters.

---

## 7. Framework bindings

### Google ADK — `LoopAgent`

A workflow-agent class that runs its `sub_agents` **sequentially, in order, each iteration**,
repeating until a termination condition fires.

- `sub_agents` — the ordered list executed per iteration.
- `max_iterations` — hard cap; the loop halts when reached.
- **Termination is not automatic**: *"the LoopAgent itself does not inherently decide when
  to stop looping. You must implement a termination mechanism."* A sub-agent signals early
  exit by setting `tool_context.actions.escalate = True` (typically via an `exit_loop` tool).

Documented refinement shape: `InitialWriterAgent` (draft) → `CriticAgent` (evaluate against
criteria) → `RefinerAgent` (apply improvements, or call `exit_loop` when the critic returns
its completion phrase, e.g. "No major issues found"). Sub-agents share state through the
context/state dict. Available in Python, TypeScript, Go, Java.

Practices: define completion criteria before designing the loop; always provide the
escalation escape hatch; keep `max_iterations` as the safety backstop, not the primary exit.

> Note the shape: ADK's critic/refiner split is the same **maker/checker separation** as
> Osmani's sub-agents and LangChain's Level-2 grader. Three vocabularies, one pattern.

### Vercel AI SDK — `ToolLoopAgent` / `WorkflowAgent`

- `ToolLoopAgent` coordinates model calls with tool execution across steps.
- `stopWhen: stepCountIs(25)` — the required ceiling. Non-optional in practice when the
  loop calls paid search tools.
- `generate()` runs the loop locally, returning `result.text` (final answer) and
  `result.steps` (the tool-call history — your trace).
- Tools are `tool({ description, inputSchema: z.object({...}), execute })`; the model reads
  description + schema to decide when to call, and fills the params.

**Durability** via `WorkflowAgent` from `@ai-sdk/workflow`: each tool's `execute` carries a
`'use step'` directive, making a checkpoint boundary. Completed steps **replay from recorded
output** instead of re-executing; failed steps retry automatically. Use `stream()` over
`generate()` for long runs, writing into a persisted writable stream. Wiring: `withWorkflow()`
in `next.config.ts`, `'use workflow'` on the workflow function.

**Model routing per step** rather than one frontier model for everything: frontier model
(`claude-fable-5`) for loop reasoning and synthesis; a smaller model (`claude-sonnet-5`) for
aggregation and structured extraction via `generateObject()`. Format `creator/model-name`
through the AI Gateway; failover list in `providerOptions.gateway.models`.

**Sandboxing** untrusted model-written code:

```typescript
const sandbox = await Sandbox.getOrCreate({
  name: `analysis-${researchId}`,
  runtime: 'node24',
  timeout: 600_000,
  networkPolicy: 'deny-all',
});
```

Keying by run id gives one sandbox per run, reused across calls, and retried steps reattach
to the existing one.

**Runtime envelope:** Vercel Functions with fluid compute run to 800s — a real constraint on
loop length; anything longer must checkpoint and resume rather than hold the process.
Cost/security controls: bearer-token auth on the start/status routes, AI Gateway keys with
budgets, per-call token/latency/cost logging.

The research-agent loop itself: *"search, read, aggregate, synthesize, then decide whether
to keep going."*

---

## 8. Level 4 at the frontier — recursive self-improvement

Anthropic's institute piece is the hill-climbing loop taken to its endpoint: AI systems that
autonomously design and develop their successors. The escalation it traces —

- 2021–2023 humans write code → 2023–2025 chatbots emit snippets for humans to integrate →
  2025–2026 coding agents write and edit whole files → next, systems that build and train models.

Measurements worth quoting when arguing about loop horizons:

- Task length an AI can complete independently is **doubling every ~4 months** (was ~7).
  Claude Opus 3 (Mar 2024) handled ~4-minute tasks; Claude Opus 4.6 handled 12-hour tasks by 2026.
- **>80% of merged production code at Anthropic authored by Claude** (May 2026), from single
  digits before Feb 2025; engineers shipped 8× more code per quarter vs 2024.
- CORE-Bench (research reproduction): ~20% success in 2024 → benchmark saturated within 15 months.
- Experiment-optimization speedups: ~3× (May 2025) → ~52× (Apr 2026).
- On open-ended research problems, models chose a better next step than humans **64%** of the
  time (Apr 2026), up from 51% (Nov 2025).

Risks named: acceleration past human oversight; misalignment compounding as systems build
successors ("more frequent but less understood"); and an **Amdahl's-law bottleneck** —
automating development shifts the constraint onto human review and verification. That last
one is the direct connection to §5: at every scale, from a nightly test-fixer to a
self-improving lab, the binding constraint becomes verification capacity, not generation
capacity.

Proposed safeguard: verification mechanisms enabling a coordinated multi-lab slowdown or
pause, with clear triggers — acknowledged as harder than arms control because training runs
are easy to conceal, and no credible system exists today.

The human-value quote that pairs with Osmani's warning:

> *"The comparative advantage of humans as of right now is still in seeing the bigger
> picture and thinking beyond the confines of the immediate task."*

### The worked example: `autoresearch`

The trends above are macro measurements. `autoresearch` (Karpathy, released **2026-03-06**,
MIT, ~630 lines of Python) is the smallest concrete artifact that exhibits the level-4 shape,
and it is worth reading precisely because it is small enough to hold in your head.

The setup: give an agent **one Python file, one GPU, one metric.** It reads the code,
proposes a change, runs a ~5-minute training run, checks whether validation improved, keeps
or discards, repeats.

**The load-bearing design decision is the write boundary**, and it maps exactly onto the
maker/checker split in §4:

| Artifact | Who writes it | Why |
|---|---|---|
| `train.py` — model, optimizer, training logic | **Agent** | The search space |
| `prepare.py` — evaluation utilities | **Nobody** (agent cannot touch) | The verifier must not be editable by the thing it grades |
| `program.md` — instructions | **Human** | The contract |

An agent that can edit its own evaluator does not have a verifier; it has a negotiation.
Making `prepare.py` off-limits is what converts "loop that reports success" into "loop whose
success means something" — the same rule as §5's *the model never grades its own work*,
enforced structurally rather than by instruction.

**Results:** 700 experiments over two days → **20 genuine stackable improvements**, cutting
GPT-2 training from **2.02 → 1.80 hours (11%)**. Shopify's Tobi Lütke reported 19% on the
same setup after 37 experiments.

Note the hit rate: 20 of 700 is **under 3%**. The loop's value is not that it is clever —
it is that a ~3% hit rate is perfectly acceptable when attempts are cheap and unattended.
That reframes the economics: *"if you have an objective metric, you are the bottleneck."*
Humans exhaust after roughly a dozen experiments; the loop does not.

The prerequisite is a hard one, and it bounds where this transfers: **an automatic gate that
can fail the work.** Model training, refactoring, content rewrites, and pipeline tuning
qualify. Anything whose success is only expressible as "looks right" does not — see the
rung-2 gate in [loop-autonomy-ladder.md](loop-autonomy-ladder.md).

**Bilevel autoresearch** ([arXiv:2603.23420](https://arxiv.org/abs/2603.23420), Qu & Lu,
2026-03-24) closes the level-4 circle: an outer loop reads the inner loop's traces and
**generates new search mechanisms as Python code, injected at runtime.** The inner loop
optimizes the task; the outer loop optimizes *how the inner loop searches*.

Three findings worth carrying:

- **5× improvement** over the inner loop alone (−0.045 vs. −0.009 val_bpb) on Karpathy's
  GPT pretraining benchmark.
- **Parameter-level tuning without mechanism change yielded no reliable gain.** The outer
  loop had to write new *code*, not new hyperparameters — the structural analogue of
  [evolve-loop.md](evolve-loop.md)'s "rewrites files, not weights."
- **Both loops use the same LLM.** No stronger model at the meta level — the gain comes from
  loop *structure*, not model capability. This is the sharpest available evidence for the
  pillar's governing claim.

The outer loop autonomously reached for combinatorial optimization, multi-armed bandits, and
design of experiments without being told those domains existed — succeeding, per the
authors, by *breaking the inner loop's deterministic search patterns*.

---

## 9. Design checklist

Before shipping a loop, answer:

- [ ] What is the **trigger** — manual, cron, or event?
- [ ] What is the **testable goal**, and which deterministic check proves it?
- [ ] What are the **stop rules** — success, iteration cap, budget cap, stall detector?
- [ ] Who is the **verifier**, and is it a different agent/model from the maker?
- [ ] Where does **state** live between runs, outside the context window?
- [ ] How is context **compacted** each iteration?
- [ ] Which actions require **human approval** before execution?
- [ ] What is the **escalation path** when the cap is hit without success?
- [ ] Are parallel agents **isolated** (worktrees/sandboxes) so they can't collide?
- [ ] Are traces captured well enough to feed a **hill-climbing** pass later?
