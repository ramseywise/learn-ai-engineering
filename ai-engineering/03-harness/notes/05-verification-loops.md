---
origin: web-authored
sources:
  - https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering
  - https://www.anthropic.com/engineering/harness-design-long-running-apps
  - https://ai-native-playbook.vercel.app/guides/the-machine/harness-engineering
  - https://vercel.com/academy/build-ai-agent-harness
  - https://martinfowler.com/articles/reliable-llm-bayer.html
confidence: high
cleaned: 2026-07-29
---
# 5 — Verification and Feedback Loops

> Models lean toward the first plausible solution and rate their own work generously. Verification is the harness's answer to both.

---

## The core failure

Agents **stop after writing code without testing it**. The output looks complete, the model is confident, and nothing checked. LangChain identified this as a primary source of Terminal Bench failures.

Two distinct problems underneath:

1. **Models lean toward the first plausible solution.** Without pressure to verify, plausible is where they stop.
2. **Agents rate their own work generously.** Anthropic: *"agents tend to respond by confidently praising the work — even when quality is mediocre."*

The first needs a forced verification pass. The second needs an *external* evaluator. They are not the same fix.

---

## The self-verification loop

Make the workflow explicit rather than implied:

```
plan → build → verify → fix → (repeat until verify passes)
```

Verification must cover **happy paths and edge cases** — an agent asked to "test it" will test the case it just built for.

Enforcement is a hook, not a hope. `PreCompletionChecklistMiddleware` intercepts the agent's attempt to exit and **forces a verification pass before completion is allowed**. The agent cannot declare done; it can only *request* done, and the harness adjudicates.

This is what grounds a solution in tests and creates the feedback signal that self-improvement runs on. It's also why sandbox tooling matters ([note 04](04-execution-boundaries.md)) — test runners, logs, and screenshots are what "verify" reads.

---

## Three kinds of reflection

"Verify" is not one check. Bayer's PRINCE separates it into three loops that fail independently, and the distinction is the note's most portable idea:

| Loop | Question | Catches |
|---|---|---|
| **Process reflection** | Am I on the right trajectory? | Bad sequencing, wrong tool choice, steps that don't advance the goal |
| **Data reflection** | Is the evidence sufficient? | Thin evidence, missing context, gaps in coverage |
| **Draft reflection** | Is the output complete? | Missing sections, inconsistent tables, synthesis gaps |

The reason to split them: **an agent can execute a flawless workflow and still retrieve nothing useful** — good process, bad data. The inverse also holds. A single "did it work?" check collapses both into one verdict and gives the agent nothing to act on.

Placement matters as much as existence. Process reflection runs *between* steps (PRINCE's Think & Plan node, in the lineage of Anthropic's think tool); data reflection runs *before* synthesis, and when evidence is short it emits **specific follow-up questions** that route back to retrieval rather than a bare "insufficient"; draft reflection runs *after* generation. Each loop's output is an instruction to a named upstream stage — that's what makes them loops rather than assertions.

The payoff PRINCE reports from the process-reflection step specifically: **tool-selection accuracy improved sharply** once the agent had a dedicated space to reason about which tool matched the intent. That gain arrived as the tool count grew and domain boundaries began overlapping — the failure mode note 03 addresses with `DO NOT USE FOR` sections. Reflection and tool description are two attacks on the same problem.

---

## Asymmetric QA

The single highest-leverage rule in this note:

> **The verification model must be smarter than the execution model.**

Cheap fast model for the task; expensive smart model **at the verification gate only**. This inverts the intuition that you spend on generation, and it's economically favorable — verification runs once per gate over a bounded artifact, while generation runs over many steps.

The symmetric alternative — same model checking its own work — is listed among the field's canonical failure modes. It produces confident agreement, not review.

### When a verifier is worth deleting

The counterweight, and the rarer report: PRINCE ran an LLM review step over generated SQL and **removed it**. The reviewer kept flagging valid queries as erroneous — cost and latency for a net loss in throughput, with no accuracy gain to trade against.

The rule that survives:

> **A verifier earns its place only if its false-positive rate is low enough that acting on its verdict beats ignoring it.**

A gate that cries wolf gets routed around by whoever operates it, which is worse than no gate — it produces the appearance of verification plus the habit of overriding it. Where a **deterministic** check can cover the same ground, prefer it: PRINCE kept a hard allowlist (`SELECT` only; `DELETE`/`INSERT`/`UPDATE` blocked) and a result cap, both of which are exact and free. The LLM reviewer was the layer that went, not the validation.

The generalization: **verify with the cheapest mechanism that is actually decisive.** Schema check before reference comparison before LLM judge — the eval-tier ladder below, applied to gates. This is note 08's [iterative simplification](08-maturity-and-failure-modes.md#iterative-simplification) reaching verification itself; verification layers are subject to the subtraction pass like everything else.

---

## Separating generation from evaluation

Self-evaluation bias is structural, not a prompting problem:

> **External evaluators can be tuned to skepticism far more effectively than generators can be made self-critical.**

An agent asked to critique its own output is being asked to hold two conflicting objectives. A separate evaluator holds only one.

Anthropic's three-agent architecture for long-running app generation:

| Agent | Function | Notes |
|---|---|---|
| **Planner** | Expand a brief prompt into a full spec | High-level scope; identifies opportunities |
| **Generator** | Implement features incrementally | Self-evaluates per cycle; uses version control |
| **Evaluator** | QA the running app; verify against spec | Drives the live app (Playwright); scores against explicit criteria |

The evaluator **navigates the actual running application** rather than reading the diff. That distinction matters: reading code verifies intent, driving the app verifies behavior.

Measured result: a solo run (20 min, $9) produced broken core gameplay; the full harness (6 hr, $200) produced a functional game with working AI integration. **~20× the cost for the difference between broken and working** — the harness ROI question is rarely "is it cheaper," it's "does it produce a result at all."

---

## Grading criteria beat vibes

Subjective judgment doesn't transfer to an evaluator agent. Replace it with **weighted, named criteria**. Anthropic's set for frontend work:

| Criterion | Question |
|---|---|
| **Design quality** | Coherent visual identity, or a collection of parts? |
| **Originality** | Custom decisions, or stock template components? |
| **Craft** | Typography, spacing, contrast, hierarchy |
| **Functionality** | Can a user actually complete the task? |

The generalizable move: **name the dimensions, weight them, score each separately.** A single 1–10 score collapses distinct failures into one number and gives the generator nothing actionable.

---

## Sprint contracts

Before implementation, generator and evaluator **negotiate deliverables in writing.**

This bridges the gap between a high-level spec and testable acceptance criteria — the gap where scope creep and misalignment live. The contract is written *before* work starts, by both parties, so the evaluator can't invent criteria afterward and the generator can't redefine done.

It is the **acceptance baseline** from [note 01](01-what-a-harness-is.md#the-four-parts), made concrete and per-task. Related: verification contracts with **scoped claims** — the agent states precisely what it verified, which prevents "tests pass" from covering an untested path.

---

## Eval-first

> **Establish binary pass/fail criteria before tuning anything else.**

Without a binary eval, there is no signal to improve against, and every change is a vibe. Three tiers, cheapest first:

1. **Schema checks** — does the output parse and conform?
2. **Reference comparison** — does it match known-good output?
3. **Calibrated LLM-as-judge** — rubric-scored, with the rubric itself validated against human judgment.

Two related disciplines: **Pass@k** measures capability boundaries (can it ever do this?); **Pass^k** measures deployment quality (does it do this *every* time?). Ship on Pass^k.

And the meta-rule: **if the eval system is broken, fix the eval system first.** Never steer on a distorted signal. See [06-eval](../../06-eval/README.md).

### Two eval surfaces, different triggers

Offline evals are only half of it. PRINCE runs both, on deliberately different cadences:

| | **Dataset eval** | **Live-traffic eval** |
|---|---|---|
| Input | Curated questions + SME reference answers | Real production queries, no reference |
| Trigger | On change to workflow, prompts, or models | Daily batch |
| Measures | Accuracy, semantic similarity to reference | Faithfulness, answer relevancy |
| Catches | Regressions | Drift, hallucination, the query distribution you didn't anticipate |

The split exists because **reference-free metrics work on live traffic and reference-based ones don't.** Faithfulness (is the answer supported by retrieved context?) and relevancy (does it address the query?) are computable without ground truth, so they run on everything; accuracy needs a labeled answer, so it runs on the curated set. Ship with both — the dataset eval is the regression gate, the live eval is the one that finds what your dataset never contained.

### Evaluate the stages, not just the endpoint

> **Apply metrics at each workflow stage, like a testing pyramid — not only end-to-end.**

An end-to-end score tells you the answer was wrong; it does not tell you whether retrieval missed the document, reflection accepted thin evidence, or synthesis dropped a finding that was present in context. In a multi-stage pipeline, per-stage metrics (context relevancy at retrieval, faithfulness at synthesis) are what localize a regression to the component that caused it. This is the same argument as multi-criteria grading above, applied along the pipeline instead of across quality dimensions — and it's the concrete reason a decomposed workflow beats a monolithic agent: **each stage can be evaluated, debugged, and improved in isolation.**

---

## Loop detection

The doom loop: an agent produces 10+ variations of a broken solution, each a small mutation of the last, converging on nothing.

`LoopDetectionMiddleware` tracks **per-file edit counts** and triggers a *"reconsider your approach"* prompt after N edits. The intervention is deliberately not a hard stop — it forces re-planning rather than repair, which is the actual missing move.

Paired with the **two-retry rule**:

> **Cap retries at two per gate failure. Beyond that, the problem is in the context or the specification — not the execution.**

Three failures on the same gate means the agent lacks information or the spec is wrong. More attempts spend money to confirm that.

---

## Retry taxonomy

Not all failures are retryable:

| Failure | Response |
|---|---|
| **Transient** (network, rate limit) | Retry with exponential backoff (2×, jitter ±20%), max 3 |
| **Tool error** | Retry once, then escalate |
| **Model refusal** | **Never retry** — it will refuse again |
| **Schema violation** | Return the validation error; retry once with it in context |
| **Context exhaustion** | Compact or reset, then resume ([note 06](06-long-horizon-execution.md)) |
| **Fatal** | Stop; surface the error |

Retry budget is **per-invocation, not per-tool** — otherwise five tools with three retries each become fifteen attempts. Circuit-break after 5 consecutive failures with a 60s cooldown, then fail fast.

**Degrade loudly.** A partial result carries a `degraded: true` flag; silent degradation is worse than failure because it looks like success.

### Retry at two levels

A single retry tier is too coarse for a multi-step workflow. PRINCE retries at **both the individual LLM call and the logical node** — the whole step in the agent's plan:

- **Call-level** absorbs transient noise: a timeout, a rate limit, a malformed response. Nothing about the plan was wrong.
- **Node-level** re-runs the step. Use it when the call succeeded but the step didn't achieve its purpose.

Retrying the wrong level wastes the attempt: re-issuing a call cannot fix a step whose *approach* was wrong, and re-running a whole node to recover from a rate limit pays for work that already succeeded.

### Feed the error back as context

The move that makes retries more than repetition:

> **Give the agent the error, not just another attempt.**

An identical retry re-runs the reasoning that just failed and tends to fail identically. PRINCE passes the failure back in — the database error message, the generated query, and the original context all return to the model, which then produces a *corrected* query rather than the same one. Capped at 3 attempts, after which the tool reports failure honestly.

This is the same instinct as the schema-violation row above (return the validation error, retry with it in context) generalized to every retryable failure, and it's what makes a retry a re-plan. It also explains why the two-retry rule holds: once the error is already in context, further attempts add no new information, so a third failure genuinely indicates a bad spec rather than bad luck.

---

## Reasoning budgets

Where models expose reasoning effort tiers, spend asymmetrically — the **"reasoning sandwich"**:

```
planning:     extra-high
execution:    high
verification: extra-high
```

High effort at the ends, where decisions are made and checked; moderate through the middle, where work is mechanical. LangChain found this split avoided timeouts while preserving quality. The shape mirrors asymmetric QA — pay for judgment, economize on labor.

---

## Trace-driven improvement

The ratchet needs input, and traces are it. LangChain's **Trace Analyzer Skill** automatically fetches production traces, **spawns parallel error-analysis agents**, and synthesizes recurring failure patterns — reasoning errors, task misunderstanding, insufficient testing.

Each recurring pattern becomes a harness change. This is the closest thing the field has to an automated ratchet, and it's one of the discipline's three open frontiers ([note 08](08-maturity-and-failure-modes.md#open-frontiers)).

Prerequisite: **traces exist and are structured.** Observability isn't a nice-to-have — it's the raw material for every subsequent improvement. Manual annotation and calibration first, then automatic LLM scoring; use both layers together.

Worth noting how modest the production version of this is. PRINCE stores traces and eval datasets **in the same tool**, so a failing score links directly to the trace that produced it. No parallel analysis agents — just the ability to go from "this metric dropped" to "here is the run" without a join across systems. That adjacency is most of the value; the automation on top is the frontier.

---

## Verification the user performs

The last verification layer isn't in the harness at all — it's the affordance that lets a human check the work cheaply.

PRINCE grounds every claim in retrieved context with a citation carrying **source document, page number, and the exact supporting quote**, surfaced on hover. Intermediate steps — queries formulated, tools called, chunks shortlisted — are displayed as the workflow runs.

Two distinct functions:

1. **Verification cost drops far enough to be routine.** A reviewer who must locate the supporting passage themselves will spot-check; one who is handed the quote and page checks every claim. Same reviewer, different behavior.
2. **Visible intermediate steps make a wrong answer diagnosable** rather than merely wrong — the user sees *where* it went off, which is a bug report instead of a complaint.

The general principle: **in any domain where a human must sign off, traceability is a harness feature, not a UI nicety.** It also disciplines the generator — an agent required to cite can only assert what it retrieved, which constrains hallucination at the point of writing rather than catching it afterward. Where the output is regulated, the harness produces a draft and a qualified human authors the final submission; the citation layer is what makes that review tractable.

---

## Working reference

`~/.claude/refs/agent-reliability.md` — failure taxonomy, retry defaults, idempotency, graceful degradation, circuit breaking, structured error returns.
`~/.claude/refs/agent-eval.md` — eval design and regression baselines.

---

→ Next: [06-long-horizon-execution.md](06-long-horizon-execution.md) — surviving past one context window.
