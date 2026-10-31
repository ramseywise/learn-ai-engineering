# Data Analytics — Curriculum

Last updated: 2026-10-31

> The sequenced path through this layer. What each note covers is in the [README syllabus](README.md#syllabus); sources, readings and removed snapshots are in [references.md](references.md).

## Prerequisites

| Need | Where |
|---|---|
| Python language basics | [programming/python/](../programming/python/README.md) 01–03 |
| NumPy, pandas, plotting, time series | [programming/python/04-python-for-data/](../programming/python/04-python-for-data/README.md) |
| High-school probability (events, conditional probability) | note 01 recaps what is needed |

Text feature engineering and text modelling, listed as layers 4 and 6 in earlier versions of this file, are taught in [data-science/](../data-science/README.md).

## Path

Do the frequentist track first; the Bayesian track reuses its vocabulary and re-answers its A/B question.

| Step | Notes | Practice | Done when you can |
|---|---|---|---|
| 1. Distributions | [02](notes/02-distributions-and-sampling.md) | `practice/5_Statistical_Analysis.ipynb` part 1 | name the distribution behind a count, rate or waiting time and query it with `scipy.stats` |
| 2. Testing | [04](notes/04-hypothesis-testing.md) | notebook part 2; `practice/courses/` Wesleyan scripts | pick the test for two groups, k groups or a contingency table, and correct for many tests |
| 3. A/B testing | [06](notes/06-ab-testing.md) | notebook part 3; `practice/AB-Bayes/` | size a test, run the z-test, and explain why peeking inflates false positives |
| 4. Causation | [08](notes/08-correlation-and-causation.md) | notebook part 4 | spot a confounder or collider and name the quasi-experimental design that fits |
| 5. Bayesian basics | [09](notes/09-bayesian-inference.md), [10](notes/10-mcmc-and-pymc.md) | `practice/BayesianML/` week 4 (read only) | write a PyMC model, sample it, and check R-hat and ESS |
| 6. Priors and decisions | [11](notes/11-priors-and-bandits.md), [12](notes/12-bayesian-ab-testing.md), [13](notes/13-loss-functions-and-decisions.md) | — | report P(B > A) with expected loss, and pick an action from a loss function |
| 7. Bayesian ML (optional) | [14](notes/14-bayesian-machine-learning.md) | `practice/BayesianML/` weeks 2, 5, 6 (read only) | derive the EM updates for a GMM and explain the ELBO |

Steps 1–4 are the critical path: model evaluation in data science and experiment monitoring in data engineering both assume them. Steps 5–7 can be done later.

## What comes next — the branching decision

| Goal | Next subject |
|---|---|
| Build data pipelines and infrastructure | [data-engineering/](../data-engineering/README.md) |
| Build predictive models and do ML research | [data-science/](../data-science/README.md) |
| Build LLM-powered applications | [generative-ai/](../generative-ai/README.md), starting at 01-llm-fundamentals |
