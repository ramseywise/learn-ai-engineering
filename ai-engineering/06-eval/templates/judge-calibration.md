# Judge Calibration — `<judge name / version>`

> Fill one of these in per judge version. A judge without a completed sheet is **experimental** and can't gate releases. See [notes/05](../notes/05-llm-as-judge.md#calibrate-against-human-labels).

| Field | Value |
|---|---|
| Criterion | |
| Judge prompt version | |
| Judge model (pinned) | |
| System under test model | (must be a different family) |
| Labeler(s) | |
| Label source | expert / user signal (👍👎, escalation) / both |
| Domain / traffic slice | |
| Date | |

## 1. Labels

| Split | Rows | Human PASS | Human FAIL | Use |
|---|---|---|---|---|
| train | | | | Few-shot examples only |
| dev | | | | Iterate on prompt |
| test | | | | Measure once |

**Human–human agreement** (if two labelers on an overlap of `n` rows): `__%`, κ = `__`

## 2. Dev iterations

| Iteration | Change | TPR | TNR | Notes from disagreements |
|---|---|---|---|---|
| 1 | baseline prompt | | | |
| 2 | | | | |

## 3. Test result (measured once)

|  | Human PASS | Human FAIL |
|---|---|---|
| **Judge PASS** | TP = | FP = |
| **Judge FAIL** | FN = | TN = |

| Metric | Value | Target for this job |
|---|---|---|
| TPR = TP / (TP + FN) | | |
| TNR = TN / (TN + FP) | | ≥ ___ (release gate) |
| Precision on PASS = TP / (TP + FP) | | ≥ ___ (golden labels) |
| Cohen's κ | | ≥ human–human |
| Score separation (continuous judges): mean(PASS) − mean(FAIL), Cohen's *d* | | > 0.05, *d* > 0.5 |
| CANNOT_GRADE rate | | |

**Corrected pass-rate formula** for reports: `(p̂ + TNR − 1) / (TPR + TNR − 1)`

## 4. Bias checks

- [ ] Verbosity: score vs. response length correlation = `__`
- [ ] Position (pairwise only): verdict flips on order swap in `__%` of cases
- [ ] Self-preference: judge family ≠ SUT family

## 5. Decision

- [ ] **Calibrated** for: release gate / golden labels / monitoring (circle)
- [ ] **Experimental**: tracking only. Reason:

**Re-calibrate when:** judge model or prompt changes, SUT changes, new domain or slice, or human–judge agreement in production drops below `__%`.

Signed off by: `<criteria owner>`
