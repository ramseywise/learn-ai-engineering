---
origin: synthesis
sources:
  - https://arxiv.org/abs/2411.00640
  - https://www.anthropic.com/research/statistical-approach-to-model-evals
  - "Dmitriev et al., A Dirty Dozen: Twelve Common Metric Interpretation Pitfalls in Online Controlled Experiments (KDD 2017)"
confidence: high
cleaned: 2026-10-28
---
# 9 — Reading Results

> An eval score is an estimate from a sample, not a fact. Put an error bar on it, compare versions on the same tasks, and break it down by slice before deciding anything. Most "improvements" on small suites are noise.

---

## The error bar on a pass rate

A pass rate *p* measured on *n* independent tasks has a standard error of:

```
SE = √( p(1 − p) / n )          95% CI ≈ p ± 1.96 · SE
```

| n | p = 0.80 | 95% CI |
|---|---|---|
| 20 | SE 0.089 | 62% – 98% |
| 50 | SE 0.057 | 69% – 91% |
| 100 | SE 0.040 | 72% – 88% |
| 300 | SE 0.023 | 75% – 85% |
| 1,000 | SE 0.013 | 77% – 83% |

On 50 tasks, 80% and 72% are not distinguishable. That's the most important table in this chapter. Report the interval with every headline number.

For small *n* or *p* near 0 or 1, use the **Wilson interval** instead of the normal approximation. It doesn't produce bounds outside [0, 1].

---

## How many tasks

The question isn't "how big should the suite be?" It's "**what's the smallest change I need to detect?**"

Rough sizes for detecting a difference between two versions run on the *same* tasks (paired, 80% power, α = 0.05, pass rates around 70–85%):

| Smallest difference that matters | Tasks needed (roughly) |
|---|---|
| 15 points | 50–100 |
| 10 points | 100–200 |
| 5 points | 400–800 |
| 2 points | 2,500+ |

The paired range depends on how often the two versions disagree on the same task: fewer disagreements, fewer tasks needed. Unpaired comparisons need noticeably more.

Practical consequence: a 50-task golden set is a **smoke detector** for big regressions. It cannot tell you that a prompt tweak gained 3 points. Either grow the suite, or stop making decisions on 3-point differences.

---

## Compare on the same tasks: paired differences

When comparing version A and B, run both on the same tasks and analyze **per-task differences**, not two independent pass rates.

```
task   A    B    B − A
t1     1    1     0
t2     0    1    +1
t3     1    0    −1
t4     1    1     0
…
mean difference = Δ;  SE(Δ) = sd(differences) / √n
```

Most tasks pass or fail on both versions, so the differences are mostly zero, and the SE of the difference is much smaller than the SE of either rate. Miller (Anthropic, "Adding Error Bars to Evals", 2024) shows pairing can cut the variance of a comparison substantially for free.

For binary outcomes, the same idea is **McNemar's test**: only the tasks where A and B disagree carry information. If B wins 14 and loses 6 of the 20 discordant tasks, that's evidence. If it wins 11 and loses 9, it isn't.

---

## Repeats and clustering

### Repeated trials

With *k* trials per task ([06](06-evaluating-agents.md#non-determinism-run-every-task-k-times)), first average the trials **within** each task, then compute the SE across tasks. Treating 100 tasks × 5 trials as 500 independent samples understates the error bar, because trials of the same task are correlated.

Repeats reduce the noise from sampling randomness within each task. They don't reduce noise from *which tasks you picked*. For that you need more tasks. Beyond a few repeats, more tasks beat more repeats.

### Clustered tasks

If tasks come in groups (10 questions about the same document, 5 turns of one conversation), they're not independent either. Use **clustered standard errors** (cluster by document or conversation). Miller reports clustered SEs can be several times larger than naive ones on popular benchmarks. Ignoring clustering makes results look more certain than they are.

---

## Slice before you conclude

A flat headline can hide a win and a loss that cancel out:

| Slice | n | A | B | Δ |
|---|---|---|---|---|
| Billing | 120 | 82% | 90% | +8 |
| How-to | 150 | 88% | 89% | +1 |
| Non-English | 40 | 75% | 58% | **−17** |
| **Overall** | 310 | 84% | 85% | +1 |

"+1 overall" would ship a change that breaks non-English users. Always break results down by the slices you labeled ([03](03-eval-datasets.md#coverage-and-balance)), and show *n* per slice so nobody over-reads a 12-task slice.

Watch for **Simpson's paradox**: B can beat A in every slice and lose overall (or the reverse) if the slice mix differs between runs. Compare on identical task sets.

### Too many slices

Slice 20 ways and one will show a "significant" change by chance at α = 0.05. Treat surprising slice results as hypotheses to confirm on fresh data, not conclusions. Pre-register the slices that gate releases.

---

## Read the transcripts

Numbers say how much. Transcripts say why. Before accepting any change in a score:

1. Pull 10–20 tasks that **flipped** (pass → fail and fail → pass).
2. Read them. Is the flip real, or a grader quirk, an infra error, a flaky task?
3. If fails are mostly one failure label, that's your story. If they're scattered, it may be noise.

Anthropic's guidance puts it plainly: you won't know whether your graders work unless you read transcripts and grades together.

---

## Metric pitfalls

From the KDD 2017 "Dirty Dozen" paper on online experiments, the ones that bite LLM evals most:

| Pitfall | In LLM evals |
|---|---|
| **Metric sample ratio mismatch** | Version B errored on 8% of tasks, which were dropped. B's pass rate is over its easier 92% |
| **Ratio metrics with changing denominators** | "Grounding rate" rose because B answers fewer questions (refuses more) |
| **Novelty effects** | Online, users engage more with any change for the first week |
| **Overall vs. segment confusion** | The slicing problem above |
| **Ignoring the error bar** | Shipping on +2 points over 50 tasks |

Rule: **count errors and refusals as failures**, or report them as their own rate. Never let them silently leave the denominator.

---

## Report template

```
Suite: support-golden v4 (n=310, 3 trials/task)     Judge: grounding-v2 (calibrated, TNR 0.88)
                    A (prod)        B (candidate)   Δ (paired)
Pass rate           84.2% ±3.9      85.1% ±3.8      +0.9  [−1.6, +3.4]
  Non-English (40)  75.0% ±13       57.5% ±15       −17.5 [−29, −6]    ⚠
Errors / refusals   1.3%            4.2%                                ⚠
Steps (median)      4               4
Cost per success    $0.014          $0.016          +14%
Flipped tasks read: 18 / 18 — 9 of 11 regressions are `refusal` on non-English
Decision: do not ship. Investigate refusal behavior for non-English.
```

---

## Checklist

- [ ] Every headline number has a 95% CI
- [ ] Suite size chosen from the smallest difference that matters
- [ ] Comparisons paired on identical tasks; SE of the difference reported
- [ ] Trials averaged within task; clustered SEs where tasks group
- [ ] Results broken down by labeled slices with n
- [ ] Errors and refusals counted, not dropped
- [ ] Flipped transcripts read before any decision

---

→ Next: [10-evals-in-ci.md](10-evals-in-ci.md) — turning a result into a gate.
