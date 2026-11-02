---
origin: synthesized
sources:
  - data-analytics/02-probability-and-statistics/
  - data-analytics/03-experimentation-and-causality/
  - data-analytics/04-bayesian-analysis/
confidence: high
cleaned: 2026-11-02
units:
  - data-analytics/02-probability-and-statistics
  - data-analytics/03-experimentation-and-causality
  - data-analytics/04-bayesian-analysis
---
# Pillar 11 — Stats & Experimentation

"The new checkout lifted conversion by 0.6 points. Should we ship it?" Answering that well is the core of an analyst's job and a
large part of a data scientist's interview. This pillar covers how to tell a real difference from noise, how to run an experiment
that can show one, and the ways results mislead even when the arithmetic is right.

You need basic Python and comfort with averages. It runs alongside [pillar 1](../1-foundations/00-overview.md). Analysts and data
scientists should treat it as core; ML engineers need the first half; others can skim.

## Learning path

1. **Distributions and sampling.** What a sample can tell you about a population, and why averages behave.
2. **Estimation and intervals.** How to report a number with its uncertainty.
3. **Hypothesis tests.** What a p-value does and doesn't say, and how to choose a test.
4. **Regression and GLMs.** The same tests in a more flexible form.
5. **A/B testing.** The whole pipeline from metric to readout, then the at-scale problems: CUPED, peeking, clusters.
6. **Causality.** Simpson's paradox, and what to do when you can't randomise.
7. **Bayesian analysis.** The same questions answered with a posterior.

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| Probability foundations | note | [02/02](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md) | Conditional probability, Bayes' rule, expectation |
| Distributions and sampling | note | [02/03](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md) | Named distributions, the CLT and where it fails |
| Estimation | note | [02/04](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md) | Intervals, bootstrap, sample size |
| Hypothesis testing | note | [02/05](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md) | p-values, choosing a test, multiple comparisons |
| Regression and GLMs | note | [02/06](../../../../data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md) | OLS, logistic, Poisson, diagnostics |
| A/B testing | note | [03/01](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md) | The worked pipeline on the course's fictional shop |
| Metrics and KPI design | note | [03/02](../../../../data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design.md) | Choosing what to measure |
| Experimentation at scale | note | [03/03](../../../../data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md) | CUPED, sequential tests, SRM, interference |
| Correlation and causation | note | [03/04](../../../../data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation.md) | Confounding, Simpson, quasi-experiments |
| Bayesian inference | note | [04/01](../../../../data-analytics/04-bayesian-analysis/notes/01-bayesian-inference.md) | Priors, posteriors, credible intervals |
| Bayesian A/B testing | note | [04/04](../../../../data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing.md) | P(B beats A), expected loss, peeking |
| Multilevel models | — | No course chapter yet | Brief explanation in [§11 of the guide](interview-guide.md#11-partial-pooling-and-multilevel-models) |

## Test yourself

[interview-guide.md](interview-guide.md) teaches each topic and ends with a question bank. Then try the rounds:
[technical-questions](../../rounds/technical-questions/README.md) (DS loops fold this into the stats and SQL screen) and
[case-study](../../rounds/case-study/README.md).
