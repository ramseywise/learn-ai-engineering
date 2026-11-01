---
origin: synthesis
sources:
  - ../../sources/Practical_Statistics_for_Data_Scientist.pdf (ch. 2, Data and Sampling Distributions)
  - ../../sources/computer%20age%20statistical%20inference.pdf (Efron & Hastie, ch. 2–4, 10–11)
  - Efron, Bootstrap Methods: Another Look at the Jackknife (Annals of Statistics, 1979; not yet held)
confidence: low
cleaned: 2026-10-31
---
# 3 — Estimation

> How to get a number from a sample and say how sure you are: estimators and their bias and variance, maximum likelihood, standard errors, confidence intervals, the bootstrap, and power as the planning-side view of the same uncertainty.

> **Status: skeleton (2026-10-31).** Section plan only. Fill with `/chapter` (Bruce & Bruce ch. 2, Efron & Hastie ch. 2–4 and 10–11) and `/papers analytics` (Efron 1979 and whatever `discover.py` finds for this note).

---

## Why this note

Note 02 says what a sample mean does as N grows. This note turns that into a reported number: an estimate with an interval. Note 04 then asks whether the interval rules out zero.

---

## Estimators, bias and variance

- Estimator vs estimate; bias, variance, mean squared error; consistency.
- Why the sample variance divides by n − 1.

## Maximum likelihood

- The likelihood function; MLE for a Bernoulli rate and a Normal mean, by hand and with `scipy.optimize`.
- Fisher information and the asymptotic standard error.
- Hand-off: note 05 fits regression and GLMs by maximum likelihood; note 09 adds a prior.

## Standard errors and confidence intervals

- SE of a mean and of a proportion; the Normal-approximation interval; Wilson interval for small counts.
- What a 95% interval does and does not mean (contrast with a credible interval, note 09).
- The delta method for ratio metrics (revenue per session), used again in note 07.

## The bootstrap

- Resample with replacement, recompute, read the spread; percentile and BCa intervals.
- When it fails: tiny N, heavy tails, dependent data (block or cluster bootstrap).

## Power and sample size, the estimation view

- The interval half-width you can afford sets N; MDE as "the smallest effect the interval can separate from zero".
- Hand-off: note 06 does the full A/B sample-size calculation.

---

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| What does a 95% confidence interval mean? | to be written |
| Bootstrap vs analytical SE? | to be written |
| How do you get an interval for a ratio metric? | to be written |

---

→ Next: [04-hypothesis-testing.md](04-hypothesis-testing.md) — turning an estimate into a decision: t, chi-square, ANOVA, non-parametric tests and multiple comparisons.
