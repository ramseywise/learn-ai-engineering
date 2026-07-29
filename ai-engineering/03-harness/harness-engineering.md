---
origin: web-authored
sources:
  - https://www.anthropic.com/engineering/harness-design-long-running-apps
  - https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
  - https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering
  - https://addyosmani.com/blog/agent-harness-engineering/
  - https://harness-engineering.ai/blog/what-is-harness-engineering/
  - https://ai-native-playbook.vercel.app/guides/the-machine/harness-engineering
  - https://vercel.com/academy/build-ai-agent-harness
  - https://robearlam.com/blog/an-introduction-to-harness-engineering
  - https://medium.com/google-cloud/harness-engineering-for-multi-agent-systems-using-google-adk-2-0-e248b885cb95
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
confidence: high
cleaned: 2026-07-29
---
# Harness Engineering

> Overview note. Topic depth lives in [notes/](notes/).

---

## Position in the stack

Harness engineering is the **third layer**: the harness assembles context, and context contains prompts. Where context engineering governs what enters the window on a single call, harness engineering governs everything *around* the call — the loop that decides when to call, which tools exist, where execution happens, what verifies the result, and what happens when it fails.

The nesting is explicit in the literature:

> **Prompt engineering is a subset of context engineering. Context engineering is a subset of harness engineering.**
> — harness-engineering.ai

**Inherits the weaknesses of:** context engineering. A harness that supplies poorly composed context to its loops fails at scale no matter how well the scaffolding itself is built.

---

## The thesis

> **Agent = Model + Harness.**

The model holds the intelligence; the harness is the system that makes that intelligence useful. Everything between the user's request and the agent's output — except the weights — is harness.

The operative corollary, stated nearly verbatim across Osmani, LangChain, and the AI-native playbook:

> **A decent model with a great harness beats a great model with a bad harness.**

Two pieces of evidence anchor this. LangChain moved its coding agent from **52.8% → 66.5%** on Terminal Bench 2.0 (rank ~30 → top five) using *harness-only changes* on a fixed model. And Osmani notes that Claude Opus 4.6 scores materially lower inside Claude Code's original harness than in custom harnesses with tighter tool design — "the gap between what today's models can do and what you see them doing is largely a harness gap."

Reliability is why. Per-step reliability **compounds negatively**: a 90%-reliable step chained five times lands near 60%. Production agents routinely exceed five steps once you count tool calls, parses, and handoffs. Harness discipline is the only thing that arrests that decay.

---

## The reframe: failures are configuration problems

The discipline's central move (HumanLayer's "skill issue" reframe, popularized by Osmani) is to treat agent failure as a **harness bug rather than a model limitation**:

| Symptom | Harness fix |
|---|---|
| Agent didn't follow a convention | Add the line to `AGENTS.md` / `CLAUDE.md` |
| Agent ran a destructive command | Add a blocking hook |
| Agent got lost in a 40-step task | Split into planner / executor |
| Agent shipped broken code | Wire typecheck back-pressure into the loop |
| Agent praised its own mediocre work | Separate the evaluator from the generator |

This is **the ratchet**: every failure gets engineered out permanently, so the agent never makes that mistake again.

> **Every line in a good `AGENTS.md` should be traceable back to a specific thing that went wrong.**
> — Addy Osmani

The ratchet is what makes a harness an *artifact* rather than a config file — it tightens every time the agent slips.

---

## Topic notes

1. [What a harness is](notes/01-what-a-harness-is.md) — Agent = Model + Harness, the four parts, the harness gap, the ratchet, convergent design.
2. [Harness anatomy](notes/02-harness-anatomy.md) — the nine components, filesystem as foundational primitive, bash-as-general-tool, sandboxes.
3. [Tool design as harness surface](notes/03-tool-design.md) — ACI over API, the five-section tool contract, the four gating questions, MCP vs. in-process.
4. [Execution boundaries and guardrails](notes/04-execution-boundaries.md) — sandboxes, hooks, permission gates, silent-success/verbose-failure, the five protection layers.
5. [Verification and feedback loops](notes/05-verification-loops.md) — self-verification, asymmetric QA, generator/evaluator separation, sprint contracts, the two-retry rule.
6. [Long-horizon execution](notes/06-long-horizon-execution.md) — state externalization, compaction vs. context reset, context anxiety, Ralph loops, plans as artifacts.
7. [Orchestration and multi-agent harnesses](notes/07-orchestration.md) — subagents as context firewall, planner/executor, ADK 2.0 graph primitives, oscillation and deadlock.
8. [Harness maturity and failure modes](notes/08-maturity-and-failure-modes.md) — the five-stage model, the canonical six-stage pipeline, five failure modes, iterative simplification.

---

## The context ↔ harness boundary

| Context engineering | Harness engineering |
|---|---|
| What goes in the window on *this* call | The loop that decides *whether and when* to call |
| Which documents, memory, tool results to inject | Which tools exist at all, and what they're allowed to do |
| Token budget within one assembly | Cost envelope across a whole run |
| Compaction as a technique | Compaction as a middleware that fires on a trigger |

The moment assembly becomes **stateful and conditional** — a loop deciding when to retrieve, compact, verify, or spawn — you have crossed from context into harness.

---

## The five components

The tightest available decomposition (harness-engineering.ai), useful as a checklist:

1. **Context engineering** — assembling calibrated information per step → [02-context](../02-context/README.md)
2. **Tool orchestration** — external system interaction, input validation, output parsing, error handling → [note 03](notes/03-tool-design.md)
3. **Verification loops** — schema-based or semantic checks before proceeding → [note 05](notes/05-verification-loops.md)
4. **Cost envelope management** — per-task budget ceilings preventing runaway spend → [note 08](notes/08-maturity-and-failure-modes.md)
5. **Observability and evaluation** — structured traces and automated measurement → [06-eval](../06-eval/README.md)

Claimed reliability impact by layer: prompt engineering 5–15%, context engineering 15–30%, harness engineering 50–80%. Treat the numbers as directional rather than measured — the ordering is the point.

---

## Convergent design

Leading coding agents — Claude Code, Cursor, Codex, Aider, Cline — **"look more like each other than their underlying models do."** That convergence is the field's strongest evidence that a specific set of scaffolding patterns is load-bearing: filesystem, bash, sandbox, hooks, subagents, progressive disclosure, plan files, verification.

The feedback loop closes on itself: primitives discovered in harnesses get standardized into products, then embedded into the next generation's training, which makes models better at exactly those primitives. Harness design and model development co-train.

---

## Resources

- Pillar guide: [4-agents](../../interviewing/guides/4-agents/00-overview.md)
- Anthropic, harness design for long-running apps: https://www.anthropic.com/engineering/harness-design-long-running-apps
- LangChain, anatomy of an agent harness: https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
- LangChain, improving deep agents: https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering
- Addy Osmani: https://addyosmani.com/blog/agent-harness-engineering/
- harness-engineering.ai: https://harness-engineering.ai/blog/what-is-harness-engineering/
- AI-native playbook: https://ai-native-playbook.vercel.app/guides/the-machine/harness-engineering
- Vercel Academy (hands-on, 38 lessons): https://vercel.com/academy/build-ai-agent-harness
- Rob Earlam, introduction: https://robearlam.com/blog/an-introduction-to-harness-engineering
- Google ADK 2.0 multi-agent: https://medium.com/google-cloud/harness-engineering-for-multi-agent-systems-using-google-adk-2-0-e248b885cb95
- `awesome-harness-engineering`: https://github.com/ai-boost/awesome-harness-engineering
