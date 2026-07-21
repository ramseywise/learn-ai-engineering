# LLM-as-Judge Calibration — Grader Reference

How custom graders compare to DeepEval and RAGAS on the BKH calibration sample.
Evidence base for grader selection decisions in the registry.

> **Scope:** Calibration run results and score evidence. For framework selection rationale and methodology principles, see [grader_methodology.md](grader_methodology.md).

New calibration runs (GT ablation) → `.claude/docs/research/` until final → then Notion.

---

## Key findings

### Custom v3 outperforms DeepEval on BKH (50 tasks, 25 liked / 25 disliked)

| Grader | Liked μ | Disliked μ | Δ | Cohen's d | Verdict |
|---|---|---|---|---|---|
| **Custom answer_relevancy v3** | 0.885 | 0.670 | **+0.214** | 0.75 | ✅ Strong |
| DeepEval answer_relevancy | 0.728 | 0.642 | +0.086 | 0.25 | Weak |
| Custom completeness | 0.750 | 0.720 | +0.030 | 0.07 | Marginal |
| DeepEval completeness | 0.681 | 0.723 | −0.042 | — | ❌ Inverted |
| Custom escalation | 0.800 | 0.800 | 0.000 | 0.00 | No signal |
| DeepEval escalation | 0.600 | 0.680 | −0.080 | — | ❌ Inverted |

**v3 prompt progression on answer_relevancy Δ:**
| Version | Δ |
|---|---|
| Custom v2 | −0.080 (inverted) |
| Custom v3 | **+0.214** |
| DeepEval | +0.086 |

v3 improved Δ by +0.294 on answer_relevancy vs v2.

---

## Grader selection decisions (from calibration)

| Decision | Rationale |
|---|---|
| Ship custom v3 as production `answer_relevancy` | Only grader with meaningful positive Δ on calibration sample |
| Don't ship DeepEval graders | Inverted on multiple dimensions — optimise for something different than user sentiment |
| Use custom escalation as high-confidence signal | Reliable discriminator; DeepEval inverted here |
| Hold grounding calibration | Grounding cross-check ran against URL strings not passage text — `context_missing` fires, returns 0.5 flat. Rerun after `article_loader.py` is wired. Pass `context=[passage.text ...]` not URLs. |

---

## Domain-shift pattern to watch

Custom graders calibrated on BKH show strong Δ on BKH but near-zero Δ on VA staging data.
Likely causes: VA disliked responses are disliked for reasons answer_relevancy doesn't capture
(tone, escalation handling, multi-turn context loss) rather than irrelevance.

When re-running calibration on GT dataset, isolate by query type — accounting-specific
queries vs. nav/UI queries to see if Δ holds within domain before drawing cross-domain conclusions.

---

## Related

- Calibration methodology and P/R/F1 framework → [grader_methodology.md](grader_methodology.md)
- Active calibration runs → `.claude/docs/research/` 
- Final results (VA staging showdown) → Notion
