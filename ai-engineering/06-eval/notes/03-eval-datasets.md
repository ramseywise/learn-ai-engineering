---
origin: synthesis
sources:
  - https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  - https://developers.openai.com/cookbook/examples/realtime_eval_guide
  - https://hamel.dev/blog/posts/field-guide/
  - "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly 2024) — Ch 10"
  - case-study/gate-contract.md
confidence: high
cleaned: 2026-10-28
---
# 3 — Eval Datasets

> The dataset decides what your eval can see. Start small and real, grow it from failures, keep it versioned, and make sure every row is fair for the gate that scores it.

---

## Start small, start real

The first useful dataset is **20–50 tasks taken from real failures**: user complaints, support tickets, bad traces from error analysis ([02](02-defining-correct.md#find-failure-modes-by-reading-error-analysis)). Review each one by hand. A small, clean, realistic set beats a large, noisy benchmark, because every row in it is about *your* system.

| Stage | Size | Purpose |
|---|---|---|
| **Example suite** | 5–20 | Eyeball diffs while iterating on a prompt ([01/09](../../01-prompt-engineering/notes/09-evaluating-prompts.md#offline-the-tech-tree)) |
| **First golden set** | 20–50 | Real failures, hand-reviewed. Enough to catch big regressions |
| **Working set** | 100–300 | Enough for ±5–8 point error bars on a pass rate ([09](09-reading-results.md#how-many-tasks)) |
| **LLM-graded sample** | 50–200 | Cost-capped subset for expensive judges |
| **Large harness** | 1,000+ | Detecting small effects. Usually needs synthetic or logged data |

Grow toward the next stage when the current one can't separate two versions you need to tell apart. Statistics tells you when that is ([09](09-reading-results.md)).

---

## Where tasks come from

| Source | Strength | Watch out for |
|---|---|---|
| **Production logs / telemetry** | Real distribution, real phrasing | Doesn't exist before launch. Consent and PII. Biased by what your app already does well |
| **Real failures** (tickets, 👎, escalations) | The highest-value rows. Directly about your weak spots | Over-represents failure. Balance with normal traffic |
| **Existing records** (pre-AI support logs, docs, forums) | Plentiful, realistic | Shape mismatch. You may need to adapt them into tasks |
| **Domain experts writing cases** | Hits the edge cases that matter | Slow. Experts write *hard* cases and under-sample common ones |
| **Synthetic (LLM-generated)** | Cheap coverage of combinations | Tropes, unrealistic phrasing, bias toward the generating model |

### Synthetic data done right

Don't ask a model for "100 test questions". You'll get 100 variations of the same polite question. Generate along **dimensions** instead:

1. Pick 3–4 dimensions that matter for your product: *persona* (new user, power user, frustrated), *intent* (billing, how-to, bug report), *complexity* (one-step, multi-step, ambiguous), *channel* (chat, email).
2. Generate **tuples** of dimension values first (`frustrated × billing × ambiguous`). Check the tuples cover what you need.
3. Turn each tuple into a natural-language query in a **separate** call.
4. Read a sample. Delete the unrealistic ones.

Two traps:

- **Self-preference.** If the model generating the data is also a candidate under test, it'll find its own phrasing easy. Generate with a different model family.
- **Synthetic-only suites.** Use synthetic data to bootstrap and fill coverage gaps, then replace it with real traffic as you get it.

### Harvest from failures

The suite stays relevant by eating its own production failures. Every confirmed failure becomes a row:

```
production failure → triage (real failure, or eval bug?) → label with taxonomy → add to discovery set
                                                                                     ↓ once fixed
                                                                              move to regression set
```

OpenAI recommends keeping two pools: a **regression suite** of known, fixed failures that must keep passing, and a rolling **discovery set** of new production failures that shows where the system currently breaks.

---

## Coverage and balance

Check the dataset against the distribution you care about:

- **Slice by the dimensions** from your failure taxonomy and user mix: intent, language, difficulty, source type, user segment. Record the slice on every row so you can report by slice later.
- **Match production frequencies** for the headline number. Over-sample rare-but-costly cases in *separate* slices, not the headline.
- **Balance positive and negative cases** ([02](02-defining-correct.md#positive-and-negative-cases)).
- **Watch the denominator.** "92% pass" means nothing until you say *of what*. Report pass rate per slice, with the slice size.

---

## Row eligibility: is this row fair for this gate?

A row can be a valid task but unfair for a particular measurement. If the expected source isn't in the index, scoring that row on retrieval measures your corpus, not your retriever.

The case study handles this with **named row pools**, each a subset of the one above it ([case study](case-study/gate-contract.md#canonical-row-pools)):

| Pool | Contains | Fair for |
|---|---|---|
| `all_gt` | Every golden row | Demand analysis: what users ask |
| `source_mapped_gt` | Rows whose expected source maps to a known document | Corpus coverage |
| `retrieval_eligible_gt` | Mapped rows whose source is actually indexed | Retrieval metrics |
| `generation_eligible_gt` | Rows where retrieval found the expected source | Answer quality |
| `quality_sample` | Deterministic, cost-capped sample of the above | LLM judges |

The rule: **a downstream gate never silently scores rows an upstream gate marked ineligible.** Ineligible rows appear only as a separate diagnostic slice. Otherwise a retrieval miss shows up as a "bad answer" and you fix the wrong thing.

---

## What a row contains

A general shape (adapt the fields to your system):

```json
{
  "id": "billing-refund-014",
  "input": {"messages": [{"role": "user", "content": "I was charged twice for order 8812"}]},
  "reference": {
    "answer": "Apologizes, confirms the duplicate charge, issues a refund for one charge",
    "expected_tool_calls": [{"name": "lookup_order", "args": {"order_id": "8812"}},
                            {"name": "issue_refund", "match": "ANY_ARGS"}],
    "expected_sources": ["help/billing/duplicate-charges"]
  },
  "labels": {"intent": "billing", "difficulty": "easy", "case_type": "positive", "language": "en"},
  "eligibility": {"retrieval": true, "generation": true},
  "provenance": {"source": "ticket", "added": "2026-10-02", "added_by": "ops-review"},
  "graders": ["tool_trajectory", "grounding", "completeness"]
}
```

What matters:

- **A reference, not always an answer.** For open-ended tasks, the reference is a rubric or a list of required points, not a gold string to match.
- **Labels** for slicing, **eligibility** per gate, **provenance** for trust.
- **Graders named per row**, so a row only gets graders that make sense for it.

Schema: [templates/evalset.schema.json](../templates/evalset.schema.json).

---

## Splits, versioning, contamination

- **Split it.** Keep a **dev** set you iterate against and a **held-out test** set you look at rarely. Tuning prompts against the full set overfits to it, exactly as in ML ([12](12-failure-modes.md#overfitting-the-dev-set)). For judge calibration, use train/dev/test splits of the human labels too ([05](05-llm-as-judge.md#calibrate-against-human-labels)).
- **Version it.** Datasets change. Store them in git (or a dataset tool with versions) and record the dataset version in every result. A score from v3 and a score from v4 are not comparable.
- **Freeze the reference with the data.** If labels came from a grader, record the grader version. Change the grader and the labels shift ([case study](case-study/grader-methodology.md#would-different-judges-give-different-golden-traces)).
- **Keep it out of training and prompts.** Don't paste eval rows into few-shot examples. Don't fine-tune on them. Don't let the agent see them at runtime.
- **Reset state per trial.** If tasks touch a database, sandbox or file system, every trial starts from a clean snapshot. Otherwise one trial's side effects look like the next trial's failure.

---

## Checklist

- [ ] First 20–50 rows are real failures, hand-reviewed
- [ ] Synthetic rows generated along dimensions by a different model family, then read
- [ ] Every row has slice labels, eligibility and provenance
- [ ] Positive, negative and boundary cases present
- [ ] Dev / held-out split. Held-out looked at rarely
- [ ] Dataset versioned; version recorded with every result
- [ ] A path for production failures to become rows

---

→ Next: [04-graders.md](04-graders.md) — how each row gets scored.
