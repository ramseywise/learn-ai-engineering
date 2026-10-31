---
origin: synthesis
sources:
  - https://projects.iq.harvard.edu/stat110 (Blitzstein & Hwang, Introduction to Probability, free PDF; not yet held)
  - ../sources/thinkstats.pdf
  - ../sources/Practical_Statistics_for_Data_Scientist.pdf
confidence: low
cleaned: 2026-10-31
---
# 1 — Probability Foundations

> The rules every later note leans on: sample spaces and events, conditional probability and Bayes' rule, independence, random variables, expectation and variance, and joint, marginal and conditional distributions.

> **Status: skeleton (2026-10-31).** Section plan only. Fill with `/chapter` (Blitzstein & Hwang ch. 1–4 and 7, *Think Stats* ch. 1–6) and `/papers analytics`. Sources found by `scripts/papers/discover.py` for this note are listed in `scripts/papers/discover/review-analytics.md`.

---

## Why start here

Note 02 names distributions, note 04 computes p-values, and note 09 applies Bayes' rule to parameters. All three assume you can work with a conditional probability and an expectation without looking them up. This note is that recap.

---

## Sample spaces, events and the axioms

- Sample space, event, the three axioms; complement and inclusion–exclusion.
- Counting when outcomes are equally likely (naive definition) and when they are not.
- Worked example to add: the birthday problem, simulated with NumPy and computed exactly.

## Conditional probability and Bayes' rule

- P(A | B) = P(A ∩ B) / P(B); the multiplication rule; the law of total probability.
- Bayes' rule as "invert the conditional"; base-rate neglect (the medical-test example).
- Hand-off: note 09 applies the same rule to a parameter instead of an event.

## Independence

- Independence vs conditional independence; why pairwise does not imply mutual.
- Where it breaks in analytics: repeated users, sessions within users, clustered assignment (note 07).

## Random variables, expectation and variance

- Discrete and continuous random variables; PMF, PDF, CDF.
- Linearity of expectation (no independence needed); indicator variables; P(A) = E[1_A].
- Variance and covariance; Var(X + Y) and when the cross term vanishes; the standard error of a mean (note 03).

## Joint, marginal and conditional distributions

- Joint tables, marginalising, conditioning; correlation as normalised covariance (note 08).
- Law of total expectation and variance (useful for CUPED in note 07).

---

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| P(A \| B) vs P(B \| A)? | to be written |
| Does linearity of expectation need independence? | to be written |
| A test is 99% accurate and the condition affects 1 in 1,000. P(condition \| positive)? | to be written |

---

→ Next: [02-distributions-and-sampling.md](02-distributions-and-sampling.md) — the named distributions behind counts, rates and waiting times, and why sample means behave until N gets small.
