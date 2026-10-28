---
origin: synthesis
sources:
  - https://arxiv.org/abs/2309.15217
  - https://arxiv.org/abs/2311.09476
  - https://arxiv.org/abs/2305.14627
  - https://arxiv.org/abs/2303.08896
  - https://arxiv.org/abs/2109.07958
  - case-study/grounding-claims.md
  - case-study/gate-contract.md
confidence: high
cleaned: 2026-10-28
---
# 7 — Evaluating RAG and Grounding

> A RAG answer can fail in retrieval, in generation, or in the gap between them. Score each stage separately, score only the rows each stage could have got right, and check grounding claim by claim instead of asking a judge for a vibe.

*Context-side view (what to put in the window and how to measure that) is in [02/12](../../02-context-engineering/notes/12-evaluating-context.md). This chapter is the measurement machinery.*

---

## Split the pipeline

```
query → [rewrite] → retrieve → [rerank] → context → generate → answer (+ citations)
           │           │           │          │          │            │
       rewrite hit   recall@k    MRR/nDCG   context    faithful    citations
                                            precision  complete    valid
```

| Stage | Question | Metric | Needs |
|---|---|---|---|
| **Retrieval** | Did the right documents come back? | Recall@k, hit rate | Expected source IDs per row |
| **Ranking** | Were they near the top? | MRR, nDCG@k | Expected sources (graded relevance for nDCG) |
| **Context** | How much of the window is relevant? | Context precision | Relevance judgment per chunk |
| **Generation: faithfulness** | Is every claim supported by the context? | Supported claims / total claims | Context **text** |
| **Generation: completeness** | Did it answer every part? | Answered sub-questions / total | Decomposed question or reference |
| **Generation: relevance** | Does it address the question asked? | Judge | Query |
| **Citations** | Do citations point at sources that support the claim? | Citation precision / recall | Citation → passage mapping |

**Score generation only on rows where retrieval succeeded** (the `generation_eligible` pool, [03](03-eval-datasets.md#row-eligibility-is-this-row-fair-for-this-gate)). If the source wasn't retrieved, a bad answer is a retrieval failure. Counting it against generation sends you to fix the prompt when the index is the problem.

---

## Retrieval metrics

| Metric | Definition | Use when |
|---|---|---|
| **Hit rate@k** | Fraction of queries with ≥ 1 relevant doc in top k | One good source is enough |
| **Recall@k** | Relevant docs in top k ÷ all relevant docs | The answer needs several sources |
| **Precision@k** | Relevant docs in top k ÷ k | Context window is tight; noise hurts |
| **MRR** | Mean of 1 / rank of first relevant doc | Users (or the model) read top-down |
| **nDCG@k** | Rank-discounted gain, normalized to the ideal ranking | Graded relevance (highly / partly / not) |

Pick *k* to match what actually goes into the prompt. Recall@50 is irrelevant if only the top 5 are passed to the model.

Getting **expected sources** is the expensive part. Options, cheapest first: the doc a support agent linked in the original ticket; the source a human-approved answer cited; an LLM judge labeling relevance of retrieved chunks (calibrate it, [05](05-llm-as-judge.md)); expert labeling.

---

## Faithfulness: claim by claim

"Is this answer faithful?" as one judge question is weak and lenient. Decompose:

1. **Extract claims.** A model splits the answer into atomic factual statements. "Go to Settings → Payouts and click Edit. Changes take 2 business days." → three claims.
2. **Verify each claim** against the retrieved passages: *supported*, *contradicted*, or *not found*.
3. **Score** = supported ÷ total. Report contradicted separately: a contradiction is worse than an omission.

This is the core of RAGAS faithfulness (Es et al. 2023) and of the case study's grounding grader ([case study](case-study/grounding-claims.md)). Benefits: partial credit, a pointer to the exact bad claim, and easier work for the judge than a holistic verdict.

### Grounding tiers

Not every claim needs the same evidence. The case study grades on tiers:

| Tier | Claim type | Must be supported by |
|---|---|---|
| **Strict** | Specific facts: menu paths, numbers, prices, dates, policy | Verbatim or near-verbatim in a passage |
| **Paraphrase** | Explanations, procedures in other words | Semantically entailed by a passage |
| **General** | Greetings, hedges, common knowledge, "let me know if…" | Exempt |

Without tiers, a judge either fails harmless filler or waves through invented specifics.

### Faithful is not correct

An answer can be perfectly faithful to a stale or wrong document. Faithfulness measures the generator. **Correctness** against a reference measures the system. Track both: faithful-but-wrong points at the corpus.

### Grounding without retrieval

For answers with no retrieved context (closed-book, or checking a model's own knowledge):

- **Self-consistency.** Sample several answers. Claims that vary between samples are likely hallucinated (SelfCheckGPT, Manakul et al. 2023).
- **Adversarial factuality sets.** TruthfulQA (Lin et al. 2021) targets questions where the popular answer is false. Good for measuring a model's tendency to repeat misconceptions.

---

## Citation checks in code

Citations are one of the few places in RAG where code can grade semantics cheaply:

| Check | Code |
|---|---|
| **Citation exists** | Every cited ID / URL is in the retrieved set. Anything else is a `citation_hallucination` |
| **Quote is real** | Quoted text appears (fuzzy-matched) in the cited passage |
| **Coverage** | Every strict-tier claim has a citation |
| **Format** | Citation markers parse |

Then, with a judge: **citation precision** (does the cited passage support the sentence it's attached to?) and **citation recall** (is every claim that needs a citation cited?). ALCE (Gao et al. 2023) defines both and shows models citing irrelevant passages often.

---

## Pass the text, not the pointer

The most common grounding eval bug: the grader receives passage IDs or URLs instead of passage text, can't verify anything, and scores near zero, or worse, scores from its own knowledge. The case study's cross-check against RAGAS showed near-zero agreement for exactly this reason ([case study](case-study/grader-methodology.md#why-the-cross-check-showed-low-agreement)).

Guard against it in the grader interface (`requires = {"retrieved_context"}`, [04](04-graders.md#the-grader-interface)) and label it `context_missing` in the taxonomy. Assert in CI that grounding graders received non-empty text.

---

## Frameworks

| Framework | Gives you | Watch out for |
|---|---|---|
| **RAGAS** | Faithfulness, answer relevance, context precision / recall, reference-free | Generic definitions. Uncalibrated for your domain ([05](05-llm-as-judge.md#cross-checking-with-other-judges)) |
| **ARES** (Saad-Falcon et al. 2023) | Fine-tuned small judges + a small human set with prediction-powered inference for confidence intervals | Setup cost. Worth it at volume |
| **DeepEval, TruLens, Phoenix evals** | Ready-made RAG judges, tracing integration | Same as RAGAS: calibrate before gating |

Use frameworks to get started and for cross-checks. Gate on graders you've calibrated against your own labels.

---

## Checklist

- [ ] Retrieval, ranking, generation and citations scored separately
- [ ] Generation scored only on generation-eligible rows; ineligible rows reported as their own slice
- [ ] *k* matches what reaches the prompt
- [ ] Faithfulness by claim extraction + per-claim verification, with grounding tiers
- [ ] Citation existence and quotes checked in code
- [ ] Graders receive passage text; `context_missing` asserted in CI
- [ ] Correctness tracked alongside faithfulness

---

→ Next: [08-tracing-and-observability.md](08-tracing-and-observability.md) — the data every grader reads from.
