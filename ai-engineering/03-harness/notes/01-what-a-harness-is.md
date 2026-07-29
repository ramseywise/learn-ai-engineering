---
origin: web-authored
sources:
  - https://addyosmani.com/blog/agent-harness-engineering/
  - https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
  - https://harness-engineering.ai/blog/what-is-harness-engineering/
  - https://robearlam.com/blog/an-introduction-to-harness-engineering
  - https://ai-native-playbook.vercel.app/guides/the-machine/harness-engineering
confidence: high
cleaned: 2026-07-29
---
# 1 — What a Harness Is

> The definition, the four load-bearing parts, and why the same failure keeps being a configuration problem.

---

## The equation

> **Agent = Model + Harness.**

A raw model is a text transformer. It becomes an *agent* only when something gives it durable state, tool execution, feedback loops, and enforceable constraints. That something is the harness: **every line of code, configuration, and execution logic beyond the weights themselves**.

The formal version (harness-engineering.ai): harness engineering is *"the discipline of designing, building, and operating the infrastructure that constrains, informs, verifies, and corrects AI agents in production."*

Four verbs worth keeping — a harness **constrains** (boundaries), **informs** (context), **verifies** (checks), and **corrects** (recovery). Most incomplete harnesses have the first two and are missing the last two.

---

## Where the metaphor comes from

Horse tack. A harness directs a powerful animal's energy toward useful work without letting it bolt.

Rob Earlam's framing is the most beginner-legible: *"you think of AI like a horse, it's fast and it's powerful"* — but ad-hoc prompting means fighting it every time. The shift is **from continuous prompting to upfront orchestration**: build the harness once, then "repeatedly ride the horse to different destinations, but with the same ease."

That's the economic argument for the whole discipline. Prompting cost is linear in tasks; harness cost is paid once and amortized.

---

## The four parts

The minimal decomposition — a harness comprises at least:

| Part | Question it answers |
|---|---|
| **Acceptance baseline** | What does "done and correct" mean, checkably? |
| **Execution boundary** | Where does the agent run, and what can it touch? |
| **Feedback signals** | How does the agent learn its last action was wrong? |
| **Rollback mechanisms** | How do we undo a bad action? |

A system missing any one of these is not a harness — it is a prompt with tools attached. The most commonly missing part is **rollback**, and the most commonly *faked* one is the acceptance baseline (a vibes-based "looks good" instead of a binary check).

---

## Why the harness dominates the model

**Reliability compounds negatively.** A step that succeeds 90% of the time, chained five times, lands near 60%. Real agents exceed five steps as soon as you count tool calls, output parses, and handoffs. Model quality shifts per-step accuracy a few points; harness structure changes *how many steps must succeed in a row* and *what happens when one doesn't*.

Two data points:

- **LangChain DeepAgents**: 52.8% → 66.5% on Terminal Bench 2.0 (~rank 30 → top five), harness-only changes, fixed model.
- **Osmani's observation**: Claude Opus 4.6 performs far below its ceiling in a loose harness and far above it in one with tighter tool design and prompts.

Hence the slogan: *a decent model with a great harness beats a great model with a bad harness.* And the diagnostic order that falls out of it — when an agent fails, **audit the orchestration layer first** (tool descriptions, retry budgets, handoff schemas), **then the context layer** (data quality, coverage, recency). In a mature setup the model is rarely the bottleneck.

---

## The "skill issue" reframe

Most agent failures are **configuration problems, not model limitations**. HumanLayer's reframe, mapped to fixes:

| Failure | Not this | But this |
|---|---|---|
| Ignored a convention | "The model is dumb" | The convention isn't in `AGENTS.md` |
| Ran `rm -rf` | "The model is unsafe" | There's no blocking hook |
| Lost the thread at step 40 | "Context window too small" | No planner/executor split, no plan file |
| Shipped broken code | "It can't code" | No typecheck back-pressure in the loop |
| Rated its own work 9/10 | "It's sycophantic" | Generator and evaluator are the same agent |

Each right-hand cell is a build task. That's the whole discipline in one table.

---

## The ratchet

The operating principle that makes a harness improve monotonically:

> Anytime an agent makes a mistake, engineer a solution such that the agent **never makes that mistake again**.

Each failure becomes a permanent signal — a hook, a lint rule, a line in the instruction file, a new gate. The harness *tightens every time the agent slips*.

The corollary is a strong test for instruction files:

> **Every line in a good `AGENTS.md` should be traceable back to a specific thing that went wrong.**

Osmani's rules for that file:
- Keep it **under ~60 lines** — a pilot's checklist, not a style guide.
- Every rule traces to an actual failure or an external constraint.
- Bias toward the load-bearing basics: package manager, test framework, formatting conventions.

Lines that can't name their originating failure are speculative, and speculative rules are what turn a checklist into an ignored wall of text. See [02-context/notes/02](../../02-context/notes/02-context-anatomy.md) on system-prompt altitude — the same drift, one layer down.

---

## Convergent design as evidence

Claude Code, Cursor, Codex, Aider, and Cline **"look more like each other than their underlying models do."**

Independent teams, different models, different companies — converging on filesystem access, bash, sandboxes, hooks, subagents, progressive disclosure, plan files, and verification loops. That convergence is the field's best evidence that these specific primitives are load-bearing rather than stylistic. [Note 02](02-harness-anatomy.md) enumerates them.

---

## The co-training loop

Harness complexity doesn't shrink as models improve — it **shifts**. Better models eliminate the scaffolding built to mitigate old weaknesses (context anxiety, myopic planning) and unlock new capabilities that expose new failure modes needing different constraints.

Meanwhile the useful primitives get standardized into products, then embedded into the next generation's training data, which makes models better at exactly those primitives. Harness design and model development co-train.

Practical consequence: **a harness needs periodic subtraction, not just addition.** See [note 08](08-maturity-and-failure-modes.md#iterative-simplification).

---

## Working reference

`~/.claude/refs/agent-architecture.md` — where responsibility sits between model, loop, and scaffolding; when a capability belongs in the harness rather than the prompt.

---

→ Next: [02-harness-anatomy.md](02-harness-anatomy.md) — the component inventory.
