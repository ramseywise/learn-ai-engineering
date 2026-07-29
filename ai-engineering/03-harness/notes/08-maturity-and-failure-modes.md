---
origin: web-authored
sources:
  - https://ai-native-playbook.vercel.app/guides/the-machine/harness-engineering
  - https://www.anthropic.com/engineering/harness-design-long-running-apps
  - https://addyosmani.com/blog/agent-harness-engineering/
  - https://harness-engineering.ai/blog/what-is-harness-engineering/
  - https://martinfowler.com/articles/reliable-llm-bayer.html
confidence: high
cleaned: 2026-07-29
---
# 8 — Harness Maturity and Failure Modes

> Where a harness sits today, what to build next, and the five ways teams fool themselves.

---

## The five-stage maturity model

| Stage | Name | What exists |
|---|---|---|
| **0** | Ad-hoc | Scripts, manual tool invocation, no registry, no structured logging |
| **1** | Basic | Schema-first tool specs, simple registry, minimal verification via unit tests |
| **2** | Verified | Static verification in CI, sandboxed execution, structured tracing, behavioral evals, **branch-per-agent** |
| **3** | Observability-first | End-to-end tracing, LLM-as-judge scoring, composable middleware, versioned memory |
| **4** | Self-healing | Automated remediation, cost-aware orchestration, policy-as-code governance |

Stage 4 remains **emerging as of 2026** — treat it as direction, not a target.

Reading the ladder: **Stage 1 makes the agent work. Stage 2 makes it trustworthy. Stage 3 makes it improvable.** Most production value lands at 2→3, and most teams claiming 3 are at 1 — see failure mode 1.

Reference implementations: **LangChain DeepAgents** (Stage 2→3, branch-per-agent A/B testing), **Claude Code** (opinionated commercial starter with visible orchestration), **Goose** (Block, model-agnostic MCP-native open source).

---

## The canonical six-stage pipeline

The per-task shape a mature harness runs:

```
Preflight → Plan → Approve → Tasks → Verify → Finish
```

| Stage | What happens |
|---|---|
| **Preflight** | Gather context; establish current state |
| **Plan** | Decompose into steps |
| **Approve** | **Mandatory human gate** on the plan |
| **Tasks** | Execute, documenting as you go |
| **Verify** | Quality gate — binary pass/fail |
| **Finish** | Export artifacts, log outcome |

Three gates constrain behavior throughout: **scope boundary, permissions, responsibility boundary.**

The **Approve** gate is the one teams skip and the one that pays best. It costs one human review of a *plan* — cheap, fast, high-information — and prevents plan errors from propagating through an entire expensive execution. Reviewing a wrong plan takes two minutes; reviewing the code produced by a wrong plan takes an hour.

An **incident memory** captures problems for future reference, enabling compound learning — the ratchet ([note 01](01-what-a-harness-is.md#the-ratchet)) as a persistent artifact rather than a habit.

---

## Three parallel branches, not a progression

A common category error: treating these as an evolutionary ladder. They are **choices to make on problem fit.**

| | **Pipelines** | **Agents** | **Self-improvers** |
|---|---|---|---|
| Who orchestrates | Code orchestrates LLM calls | LLM orchestrates tool calls | Agent modifies its own prompts from evals |
| Strength | Observability, cost control, determinism | Handles unpredictable task shapes | Compounds without human tuning |
| Cost | Lowest | Higher | Highest |
| Precondition | Known task shape | Task shape varies | **Binary evals** + team accepts unreadable prompts |

If the task shape is known, a pipeline is *better* than an agent, not less advanced. Self-improvers only earn their cost with binary evals in place — without them the system optimizes against a distorted signal.

---

## Core practices

### KISS discipline

> **The dumbest variant that works outperforms elaborate prompts under production noise.**

Elaborate scaffolding is tuned to conditions observed during development. Production has different noise, and complexity fails in ways nobody anticipated. Complexity should be **pulled in by an observed failure**, never pushed in by anticipation.

### Diagnose in order

When an agent fails, audit:

1. **Orchestration layer** — tool descriptions, retry budgets, handoff schemas
2. **Context layer** — data quality, coverage, recency
3. **Model** — last, and rarely the answer

*"The model itself is rarely the bottleneck in mature setups."* Reaching for a model upgrade before auditing tool descriptions is the field's most expensive reflex.

### Sequence accuracy before cost

> **Get it right, then get it cheap. Optimizing cost before accuracy compromises both.**

PRINCE deliberately ate high inference costs during its early phase and only optimized after reaching target accuracy. The reasoning: a system that isn't yet good enough to adopt has no usage worth optimizing, and cost-driven choices made early — a smaller model, fewer retrieval passes, a dropped reranker — remove exactly the headroom you need to find the quality bar.

The corollary is that **cheap-and-wrong is the more expensive failure**, because it burns adoption. Note 05's asymmetric-QA economics assume you already know where the quality bar is; you cannot spend selectively until you've found it. This does not license permanent extravagance — it sequences two optimizations that conflict when run simultaneously.

### The rules from prior notes

- **Asymmetric QA** — verifier smarter than executor ([note 05](05-verification-loops.md#asymmetric-qa))
- **Two-retry rule** — beyond two, it's context or spec, not execution
- **Eval-first gate** — binary pass/fail before tuning anything else

---

## Production reliability primitives

The maturity ladder says *what* to build; these are the mechanisms that keep a Stage 2–3 harness running once real traffic hits it. All four come from PRINCE, and all four are unglamorous.

### Resume from the failed node

State persisted **after every step** means a failure resumes from that step instead of restarting the workflow. PRINCE checkpoints agent state to Postgres via a LangGraph checkpointer, with application-level state (logs, intermediate steps, citations) kept separately in DynamoDB.

Three payoffs, in ascending order of importance:

1. **Cost** — completed steps aren't re-executed or re-billed.
2. **Latency** — recovery is proportional to what remains, not what was attempted.
3. **User-initiated retry becomes viable** — a user can retry a failed query and the system continues from the failure point. Without checkpointing, "retry" means "start the multi-minute workflow over," which nobody does twice.

This is [note 06](06-long-horizon-execution.md#state-externalization)'s state externalization arriving for a different reason: not context-window survival, but failure recovery. The same mechanism buys both, which is a good sign it's the right primitive.

### Cross-provider model fallback

When a model fails after its retries, fall back to **a different model, ideally on a different provider**. Retrying the same endpoint cannot fix a provider outage — and provider availability is outside your control, so it must be designed around rather than monitored.

The enabling detail is boring and load-bearing: PRINCE's internal platforms expose every model behind **a single OpenAI-compatible endpoint**, which is what makes swapping one for another a config change rather than an integration. Uniform interface first, fallback policy second.

### Fail fast on ambiguity

Rather than trial-and-error across every data source, PRINCE asks a clarifying question when intent is ambiguous — and offers AI-suggested sources the user can accept, adjust, or override.

> **A clarifying question is cheaper than a wrong execution, but only if it's rare.**

Both halves matter. The gate must trigger on genuine ambiguity and stay silent when intent is clear, or it becomes friction users learn to click through — the same false-positive economics that killed the SQL reviewer in [note 05](05-verification-loops.md#when-a-verifier-is-worth-deleting). Note the default: the machine proposes, the domain expert disposes.

### Confidence-scored automation with a quarantine lane

For its metadata-enrichment pipeline, PRINCE scores each extracted field and **routes by confidence**: high-confidence fields apply automatically, low-confidence fields are quarantined for human review.

This is the generalizable shape for HITL at volume. Full automation is unsafe and full review doesn't scale, so the threshold decides which regime each item lands in — and human attention concentrates where the model is *uncertain*, which is where it's most likely wrong. The threshold is a tunable knob, and moving it as measured accuracy improves is the ratchet running in the direction of less human work.

---

## The five failure modes

| # | Failure | Tell |
|---|---|---|
| **1** | **Skipped harness** — claiming Stage 2 while at Stage 0 | "We have evals" means one notebook run manually |
| **2** | **No Approve gate** | Plan errors propagate into fully executed wasted work |
| **3** | **No incident memory** | The same failure recurs monthly; nobody remembers the earlier fix |
| **4** | **Symmetric verification** | The same model confirms its own wrong work, confidently |
| **5** | **No binary eval** | Changes are argued about; nothing can be measured or tuned |

Failure 1 is the meta-failure — it hides the other four. The honest test is not *"do we have verification?"* but *"can I point to the code that runs it, on every task, without a human remembering to?"*

---

## Iterative simplification

The counterweight to the ratchet, and the practice most teams lack entirely:

> **Every component encodes an assumption about what the model can't do on its own.**

When models improve, those assumptions expire — but the components remain, adding cost, latency, and constraint for no benefit. Worse, they can actively suppress capability the newer model has.

The method: **strip load-bearing components one at a time and re-evaluate.**

Anthropic's own case: Opus 4.6's improvements allowed **removing sprint decomposition entirely** while maintaining quality. Similarly, context resets were needed for Sonnet 4.5 and largely unnecessary for Opus 4.6 ([note 06](06-long-horizon-execution.md#compaction-vs-context-reset)).

Practical protocol on every model upgrade:

1. List components and the weakness each was built to mitigate.
2. Disable one; run the eval suite.
3. Quality holds → delete it. Quality drops → keep it, note the model version.
4. Repeat.

This requires the binary eval from failure mode 5. Without it, subtraction is unmeasurable and nobody dares — which is exactly how harnesses calcify.

Note the direction of travel: harness complexity **shifts rather than shrinks.** Removing anxiety-mitigation scaffolding frees budget for constraints on newly-unlocked failure modes.

Two independent corroborations are worth having, because this is the practice teams most doubt:

- **A component can be worth removing before any model upgrade.** PRINCE deleted its LLM SQL-reviewer for false positives ([note 05](05-verification-loops.md#when-a-verifier-is-worth-deleting)) — not because the model got better, but because the component never paid for itself. Subtraction has two triggers: capability arrived, or the component was always a net negative. The second is more common and less often checked.
- **The expiry is anticipated by practitioners, not just vendors.** PRINCE's own conclusion is that parts of today's harness will thin out as models absorb them — while holding that explicit control over state, recovery, and verification stays essential where trust and traceability are requirements. Both halves belong: regulated domains don't get to delete the audit trail because the model improved. Scaffolding that compensates for a *model weakness* expires; scaffolding that satisfies an *external constraint* does not.

---

## Open frontiers

Three unsolved problems, named consistently across sources:

1. **Orchestrating hundreds of parallel agents on a shared codebase** — merge conflict resolution and coordination at a scale current tooling doesn't reach.
2. **Agents analyzing their own traces to identify and fix harness-level failure modes** — automating the ratchet. LangChain's Trace Analyzer Skill ([note 05](05-verification-loops.md#trace-driven-improvement)) is an early instance.
3. **Just-in-time harness assembly** — dynamically composing the right tools and context per task instead of pre-configuring everything.

The third points somewhere interesting:

> **Harnesses stop being static config and start becoming something closer to a compiler.**

Rather than a fixed configuration, the harness becomes a system that *compiles* a task specification into the tool set, context, and constraint layer that task needs.

---

## A build checklist

Ordered by return on effort:

- [ ] Tool schemas typed; descriptions carry WHEN NOT TO USE
- [ ] Sandbox with a real execution boundary
- [ ] Filesystem + git for durable state and rollback
- [ ] Plan file for anything past ~5 steps
- [ ] **One binary eval** — pass/fail, runs automatically
- [ ] Verification gate that the agent cannot skip
- [ ] Structured traces on every step
- [ ] State checkpointed per step — resume from the failed node, not the start
- [ ] Blocking hooks on destructive operations
- [ ] Approve gate between plan and execution
- [ ] Separate evaluator, stronger model than the generator
- [ ] Retry caps + cost ceiling per run
- [ ] Errors fed back as context, not just re-attempted
- [ ] Model fallback across providers behind a uniform interface
- [ ] Live-traffic eval alongside the dataset eval
- [ ] Incident memory — failures become permanent fixes
- [ ] Subtraction pass scheduled on each model upgrade — and on any gate that false-positives

Items 1–8 get you to Stage 2. Items 9–16 get you to Stage 3. Item 17 keeps it from calcifying.

---

## Working reference

`~/.claude/refs/agent-observability.md` — traces, event streams, structured logging.
`~/.claude/refs/agent-eval.md` — binary evals, regression baselines, LLM-as-judge calibration.

---

→ Next layer: [04-loop/](../../04-loop/README.md) — the loops this harness implements.
