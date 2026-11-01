---
origin: synthesis
sources:
  - Kohavi, Tang & Xu, Trustworthy Online Controlled Experiments (Cambridge, 2020; not yet held)
  - ../../sources/2017-08-kddmetricinterpretationpitfalls.pdf (Dmitriev et al., A Dirty Dozen, KDD 2017)
  - Deng, Xu, Kohavi & Walker, CUPED (WSDM 2013; not yet held)
  - Johari, Koomen, Pekelis & Walsh, Peeking at A/B Tests (KDD 2017; not yet held)
confidence: low
cleaned: 2026-10-31
---
# 7 — Experimentation at Scale

> What changes when an A/B test runs on an experimentation platform with millions of users: variance reduction (CUPED), always-valid sequential tests, sample ratio mismatch and other trust checks, and the metric pitfalls that make a clean test give the wrong answer.

> **Status: skeleton (2026-10-31).** Section plan only. Fill with `/papers analytics` (CUPED, Peeking at A/B Tests, Diagnosing SRM, A Dirty Dozen) and `/chapter` once Kohavi, Tang & Xu is held.

---

## Why this note

Note 06 covers one well-run test. At scale the hard parts are different: tests are too noisy to detect the effects that matter, people look at dashboards every day, and the assignment pipeline itself breaks. This note is the platform view.

---

## Variance reduction: CUPED

- Regress the metric on its pre-period value (note 05) and test the residual; variance falls by ρ².
- Choosing the covariate; missing pre-period data; relation to ANCOVA and stratification.

## Sequential and always-valid tests

- Why peeking inflates false positives (recap of note 06).
- mSPRT and always-valid p-values (Johari et al.); group-sequential boundaries as the classical alternative.

## Trust checks

- Sample ratio mismatch: the chi-square check, common causes, what to do when it fires.
- A/A tests; novelty and primacy effects; interference and network effects.

## Metric pitfalls

- Ratio metrics and the delta method (note 03); metric sensitivity vs directionality.
- The twelve pitfalls from Dmitriev et al. (KDD 2017), mapped to checks.

## Many tests, many metrics

- Overall evaluation criterion, guardrail metrics; false discovery across a platform (note 04).
- Hand-off: online evaluation of LLM features in [ai-engineering/06-eval](../../../ai-engineering/06-eval/README.md) uses the same machinery.

---

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| How does CUPED reduce variance? | to be written |
| The split is 50.4 / 49.6 on 2 million users. Problem? | to be written |
| The PM wants to check results daily. What do you do? | to be written |

---

→ Next: [08-correlation-and-causation.md](03-correlation-and-causation.md) — what to do when you cannot randomise: confounding, Simpson's paradox, partial correlation and the quasi-experimental toolkit.
