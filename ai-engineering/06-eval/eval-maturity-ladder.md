---
origin: web-authored
sources:
  - https://www.aibuilderclub.com/blog/how-to-evaluate-ai-agents
confidence: medium
cleaned: 2026-07-30
---
# The Eval Maturity Ladder

> Topic note. Overview: [eval-harness.md](eval-harness.md).
> The **adoption path**: what to build first when a system has no evals at all.
> Distinct from the *gate ladder* in [README.md](README.md) (`agent-eval.md` — data quality
> → retrieval → generation → grader calibration → release), which orders the gates *within*
> a mature eval suite. This note orders the **stages of getting there**.

---

## The ladder

| Level | What exists | What it catches | What it misses |
|---|---|---|---|
| **0** | Manual review ("vibes") | Whatever you happen to look at | Everything you don't |
| **1** | Deterministic gates (hooks, tests, linters) | Structural failures | Anything requiring judgment |
| **2** | Separated evaluator | Behavioral failures | Failures not in your sample |
| **3** | Eval sets built from real failures + tracing | Regressions; *where* a run broke | Slow drift in production |
| **4** | Continuous sampling with drift alerts | Divergence from baseline over time | — |

> **Most builders sit at Level 0. Production demands Level 3+.**

The gap between where people are and where they need to be is the entire point of the
ladder — and it is why "we'll add evals later" reliably means "we have no signal when this
breaks."

### Level 1 — deterministic gates

Tests and linters wired to hooks. Cheap, fast, no LLM in the loop. This is the highest
return-per-effort rung: it catches the structural failures (schema violations, broken
builds, malformed output) that would otherwise consume your judgment-tier budget.

### Level 2 — separated evaluator

A **fresh-context** reviewer. The key property is separation: the evaluator did not write
the thing it is judging, so it has no commitment to it. The strong form *operates* the
output behaviourally — clicking, running, testing — rather than reading the code and
forming an opinion about it.

This is the generator/evaluator separation already covered in
[03-harness/notes/05-verification-loops.md](../03-harness/notes/05-verification-loops.md);
the eval-side contribution is the insistence on behavioural verification over review.

### Level 3 — eval sets from failures + tracing

Two things arrive together, and neither works alone:

- **Eval sets seeded from real observed failures** — not synthetic cases invented up front.
  Every production failure becomes a row. This is how the suite stays about *your* system.
- **Tracing**: *"log every step's input, tool calls with arguments, results, and decision."*

### Level 4 — continuous sampling with drift alerts

Run the scoring pipeline against live traffic on an ongoing basis, alert on divergence from
baseline. Already covered in [eval-harness.md](eval-harness.md) — drift monitoring and the
capability→regression eval transition.

---

## Trajectory over outcome

The methodological claim behind levels 3–4: measuring only final success tells you *that*
a run failed. Trajectory analysis through traces tells you **where** — retrieval was wrong
at step 3, an error was swallowed at step 7.

This matters most for agents specifically, because a multi-step run has many ways to reach
the same wrong answer, and they need different fixes. An outcome-only eval scores them
identically.

---

## Grader types

Four approaches, meant to be **layered rather than chosen between**:

| Grader | Scales | Cost | Role |
|---|---|---|---|
| Deterministic gates | Fully | Near-zero | First line — structural failures |
| Separated evaluator agent | Well | Medium | Behavioural verification |
| LLM-as-judge | Fully | Medium | Subjective criteria at volume |
| Human spot-checks | Poorly | High | **Calibration** of the judge |

**LLM-as-judge requires rubric specificity plus explicit mitigation of three documented
biases:** position bias, verbosity preference, and self-preference (a model favouring its
own output). Left unmitigated, the judge is confidently miscalibrated rather than merely
noisy.

**Human spot-checks are a 5–10% calibration sample**, not a review queue. Their job is to
tell you whether the judge can be trusted — which maps onto the `calibrated` vs.
`experimental` grader states in `agent-eval.md` (an uncalibrated judge is tracking-only and
must never be a release gate).

---

## Metrics

Beyond pass/fail rates on the eval set:

- **Steps-to-completion** — efficiency. Rising steps at a flat pass rate means the agent is
  thrashing its way to the right answer; a regression that outcome-only evals score as green.
- **Cost-per-success** — the sustainability metric. Note the denominator: cost per *success*,
  not per run. Failed runs are pure cost, so a loop with a 50% pass rate is twice as
  expensive as its per-run cost implies.
- **Trace-level input/output at each step** — the substrate for everything at level 3+.

---

## Design checklist

- [ ] What level is this system on today — honestly?
- [ ] Are deterministic gates exhausted before reaching for an LLM judge?
- [ ] Does the evaluator have fresh context, and does it *operate* the output or just read it?
- [ ] Are eval rows seeded from observed failures, or invented?
- [ ] Is the judge calibrated against a human sample, and how recently?
- [ ] Is cost tracked per *success* rather than per run?

---

## Working reference

`~/.claude/refs/agent-eval.md` — grader interface contract, grader calibration states, the
gate ladder, failure taxonomy; `~/.claude/refs/agent-observability.md` — span types and the
six questions a complete trace must answer.
