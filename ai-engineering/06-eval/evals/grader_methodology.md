# Grader Methodology & Selection

> **Scope:** Framework selection rationale and methodology principles. For calibration run results and score evidence, see [llm-calibration-insights.md](llm-calibration-insights.md).

**Context:** BKH eval pipeline — choosing which LLM-as-judge graders to use for the quality gate and for golden trace creation.

---

## The right ground truth

User sentiment (liked / disliked ratings) is the oracle. A grader is "good" if it agrees with those ratings — not if it agrees with another LLM judge. All selection decisions should be driven by P/R/F1 measured against liked/disliked, not by grader sophistication.

## What each metric tells you

| Metric | Meaning | Use case |
|---|---|---|
| **Recall** | Fraction of bad responses caught | Pipeline quality gate — you want high recall to not let bad responses through |
| **Precision** | Fraction of passes that are actually liked | Golden trace creation — you want high precision for clean labels |
| **F1** | Balanced score | General comparison when you need one number |
| **score_delta** | liked_avg_score − disliked_avg_score | Raw discriminability — if delta < 0.05, the threshold is doing the work, not the score. Prompt needs iteration. |

## What the deepeval cross-check tells you (section 11)

Section 11 runs independent LLM-judge implementations (faithfulness, relevancy, completeness, G-Eval) on a small sample and compares to our grader scores.

**Directional agreement (Pearson r):**
- r > 0.6 → both judges measuring the same thing. Either works; pick the one with better sentiment calibration.
- r 0.3–0.6 → moderate overlap. Worth investigating which disagrees with user sentiment more.
- r < 0.3 → one of them is off. Run the LLM-judge scores through the same P/R/F1 calibration to find out which.

**The deepeval scores are NOT automatically better.** They're generic implementations not tuned for BKH / CS context. Our graders include domain-specific prompts (intent alignment, sub-question coverage, citation-level grounding) that a generic judge misses.

## Would different judges give different golden traces?

Yes, significantly. Golden traces are built from `is_correct` flags. Change the judge → change quadrant assignments → change what counts as TP/TN. If two judges have 70% pass/fail agreement, ~30% of golden traces flip. This means:

- **Don't mix judges** across trace collection runs without re-labelling.
- The golden traces are only as stable as the grader that produced them. Track `prompt_version` in labels (already done).
- When you advance from train → test → validate splits, keep the same grader version unless you do a full re-label.

## Grounding: three judges, one dimension

Grounding is the hardest dimension to calibrate because it requires article body text — not URL citations.

### Prompt comparison

| | `GroundingGrader` (ours) | `evaluate_faithfulness` | G-Eval `accuracy` |
|---|---|---|---|
| **Output** | grounding_ratio (0–1) + has_hallucination flag | binary is_faithful | score 1–5 with CoT trace |
| **Approach** | Enumerate ≤7 claims → grounded / hallucinated / unverifiable → ratio | Single holistic question: does answer contain only info from context? | 4 explicit steps: identify claims → verify → check contradictions → note unsupported |
| **Partial credit** | Yes — mixed response gets fractional score | No — one bad claim = not faithful | Yes, continuous |
| **Context guard** | Yes — returns 0.5/context_missing on URL citations | No — hallucinates a judgment on URLs | No — same problem |
| **Domain-tuned** | Yes — BKH CS, threshold 0.6 AND no hallucination | No | No |
| **Token cost** | ~1x | ~1x | ~3x (CoT) |

### Why the cross-check showed low agreement

Almost certainly context. In section 11 the grounding comparison runs against URL citation strings, not article body text. Our grader's context guard fires and returns 0.5, while faithfulness and G-Eval try to evaluate against the URLs and produce unreliable results. The comparison is apples-to-oranges until `article_loader.py` is wired in.

**To validate this hypothesis:** run the section 11 grounding deep-dive cell — it shows how many sample records were `context_missing` and re-computes correlation for records that did have passage text.

### The 3-way weighted composite option

Once article text is available for all three, you can run a weighted composite:

```
composite = 0.5 × grounding_ratio + 0.3 × faithfulness + 0.2 × geval_accuracy
```

Worth doing only if the composite's sentiment calibration (F1 vs liked/disliked) beats any individual signal. The cost is 3× the grounding API calls per record. If GroundingGrader alone matches composite sentiment alignment, stick with it — it's cheaper and domain-tuned.

The deep-dive cell in section 11 computes the composite and lets you compare visually before committing to it.

## Decision framework

1. **Check F1 leaderboard** (notebook section 11, after cross-check) — sorted by F1 with cross-check r column alongside.
2. **Check score_delta** — if delta < 0.05, the threshold is doing the work, not the score. Prompt needs iteration.
3. **Pipeline gate vs. trace creation are different jobs:**
   - Gate: use highest-recall grader
   - Traces: use highest-precision grader
   - If the same grader wins both, easy. If not, wire two separate graders.
4. **Low cross-check r** — investigate root cause first (context? threshold? prompt framing?) before switching judges. See grounding deep-dive cell.
5. **Grounding: hold judgement** until article_loader is wired. Current train split grounding calibration is under-powered due to context_missing exclusions.

## Current status (train split)

- Grading cell: `nbks/bkh/04_quality_grader_eval.ipynb`
- Leaderboard + cross-check: section 11, cells 35–37
- Graders in registry: grounding, completeness, answer_relevancy, escalation, conciseness, epa, intent
- Known gap: grounding cross-check unreliable until article body text wired in via `article_loader.py`
- Next: wire article_loader for section 11, then advance to test split once prompt_versions stabilise
