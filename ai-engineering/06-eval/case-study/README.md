# Case Study — Evaluating a Multi-Agent Support System

> Real design notes from building the eval suite for a RAG-grounded, multi-agent customer-support system. The [notes](../notes/) teach the general method; these files show one team applying it, including the mistakes.

These were written inside a project repo and moved here as worked examples. Some point at files from that project (`evals/README.md`, `invocation-flow.md`, agent names like `kb_adk` / `kb_lg` / `kb_rag`). Those aren't in this repo; the text is marked where that matters.

---

## Read in this order

| File | What it shows | Pairs with |
|---|---|---|
| [eval-architecture.md](eval-architecture.md) | Why routing evals and domain evals are separate suites. Metadata signals as free labels. Why custom graders over a framework's built-in eval | [06 agents](../notes/06-evaluating-agents.md#routing-vs-domain-evals-in-multi-agent-systems) |
| [gate-contract.md](gate-contract.md) | The full gate ladder, row pools and eligibility, failure taxonomy, grader states | [03 datasets](../notes/03-eval-datasets.md#row-eligibility-is-this-row-fair-for-this-gate), [10 CI](../notes/10-evals-in-ci.md#the-gate-ladder) |
| [grounding-claims.md](grounding-claims.md) | Claim extraction before generation, explained for non-specialists | [07 RAG](../notes/07-evaluating-rag-and-grounding.md#faithfulness-claim-by-claim) |
| [grader-methodology.md](grader-methodology.md) | How to choose between custom and off-the-shelf judges. Precision vs. recall by job | [05 judges](../notes/05-llm-as-judge.md#what-to-measure) |
| [calibration-results.md](calibration-results.md) | Liked/disliked separation for custom vs. DeepEval graders. Inverted metrics. Domain shift | [05 judges](../notes/05-llm-as-judge.md#calibrate-against-human-labels) |
| [harness-patterns.md](harness-patterns.md) | Four suite types in pytest. Tool-trajectory scoring. Adversarial cases | [04 graders](../notes/04-graders.md), [10 CI](../notes/10-evals-in-ci.md#two-phases-run-then-assert) |

---

## Lessons worth taking away

- **The grounding cross-check failed for an eval reason, not a model reason.** The judge got URLs instead of passage text and returned a flat 0.5. That's why `context_missing` is a taxonomy label and `requires` is part of the grader interface.
- **Off-the-shelf judges can be inverted.** DeepEval scored disliked answers *higher* on completeness and escalation. Generic metrics don't know what your users dislike.
- **Prompt iteration on a judge is measurable.** Custom answer-relevancy went from Δ −0.08 (v2) to +0.21 (v3) on the same calibration sample.
- **A zero-separation judge isn't a signal.** Custom escalation scored identically on liked and disliked answers (Δ 0.000). An earlier draft called it a reliable discriminator; that was corrected on 2026-10-28.
- **Calibration doesn't transfer across domains.** Strong separation on one product's traffic, near zero on another's.

## Caveats

- Calibration samples are small (50 tasks, 25/25). Read the Δ values with [09](../notes/09-reading-results.md)'s error bars in mind: at n = 25 per group, a Δ of 0.03 is noise.
- "Liked / disliked" is user feedback, a proxy label with its own biases ([11](../notes/11-production-and-the-maturity-ladder.md#user-feedback-as-signal)).
