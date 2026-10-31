# Data Analytics

> Foundation layer. Summary: [interviewing/guides/1-foundations](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/1-foundations/00-overview.md) (sisyphus has no separate statistics pillar).
> Position in the path: Python for data → **statistics and experimentation** → data science, data engineering or generative AI. Builds on [programming/python/04-python-for-data](../programming/python/04-python-for-data/README.md).

---

## What it is

Data analytics here means the statistics you need to draw conclusions from data: which distribution generated it, whether a difference is real, how big a test has to be, when a correlation says nothing about cause, and how to turn a posterior into a decision. The Python itself (language, NumPy, pandas, plotting) is taught in [programming/python/](../programming/python/README.md); this layer assumes it.

The layer has two tracks that answer the same questions in different ways.

| | Frequentist track (notes 01–08) | Bayesian track (notes 09–14) |
|---|---|---|
| Core question | how surprising is this data if nothing is going on? | given the data, what should I believe and do? |
| Tools | `scipy.stats`, `statsmodels` | PyMC 5, ArviZ, conjugate Beta updates |
| A/B testing | power, sample size, z-test, peeking ([06](notes/06-ab-testing.md)) | P(B > A), expected loss ([12](notes/12-bayesian-ab-testing.md)) |
| Strength | standard, fast, what most teams report | small N, prior knowledge, decisions under asymmetric cost |

> **Name the distribution, fix the sample size before you look, and report effect sizes with intervals rather than bare p-values.**

---

## Start here

1. [01 — Probability foundations](notes/01-probability-foundations.md) if conditional probability and expectation are rusty, then [02 — Distributions and sampling](notes/02-distributions-and-sampling.md), [03 — Estimation](notes/03-estimation.md) and [04 — Hypothesis testing](notes/04-hypothesis-testing.md).
2. [05 — Regression and GLMs](notes/05-regression-and-glms.md), then [06 — Frequentist A/B testing](notes/06-ab-testing.md) with [practice/5_Statistical_Analysis.ipynb](practice/5_Statistical_Analysis.ipynb) open alongside, then [07 — Experimentation at scale](notes/07-experimentation-at-scale.md).
3. [08 — Correlation and causation](notes/08-correlation-and-causation.md).
4. [09 — Bayesian inference](notes/09-bayesian-inference.md) and [12 — Bayesian A/B testing](notes/12-bayesian-ab-testing.md) to see the same A/B question answered the other way.
5. The rest of the Bayesian track (10, 11, 13, 14) in order.

Notes 01, 03, 05 and 07 are skeletons (added 2026-10-31); their sources are being gathered through `scripts/papers/discover.py`.

---

## Layout

```
data-analytics/
├── README.md            this file
├── CURRICULUM.md        sequenced path and prerequisites
├── references.md        every source, mapped to notes; readings; removed snapshots
├── notes/               01–14, the course (01, 03, 05, 07 are skeletons)
├── sources/             reference PDFs (14) and images/
└── practice/            own coursework
    ├── 5_Statistical_Analysis.ipynb
    ├── AB-Bayes/        AB_Testing_with_Python.ipynb
    ├── BayesianML/      Coursera Bayesian Methods for ML, weeks 2, 4, 5, 6 and final
    └── courses/         Michigan and Wesleyan statistics scripts
```

---

## Syllabus

| # | Note | Covers |
|---|---|---|
| 01 | [Probability foundations](notes/01-probability-foundations.md) (skeleton) | sample spaces, conditional probability, Bayes' rule, independence, expectation and variance, joint and marginal distributions |
| 02 | [Distributions and sampling](notes/02-distributions-and-sampling.md) | Normal, Binomial, Poisson, Exponential; `scipy.stats` API; LLN, CLT; the small-N trap |
| 03 | [Estimation](notes/03-estimation.md) (skeleton) | bias and variance, MLE, standard errors, confidence intervals, bootstrap, delta method |
| 04 | [Hypothesis testing](notes/04-hypothesis-testing.md) | t, chi-square, ANOVA; p-value misreadings; Mann-Whitney, Wilcoxon, KS, bootstrap; Bonferroni, Holm, BH |
| 05 | [Regression and GLMs](notes/05-regression-and-glms.md) (skeleton) | OLS in `statsmodels`, diagnostics, robust and clustered SEs, logistic and Poisson GLMs |
| 06 | [Frequentist A/B testing](notes/06-ab-testing.md) | power and sample size; assignment cleaning, SRM; two-proportion z-test; peeking; CUPED |
| 07 | [Experimentation at scale](notes/07-experimentation-at-scale.md) (skeleton) | CUPED, always-valid sequential tests, SRM and A/A checks, metric pitfalls, guardrails |
| 08 | [Correlation and causation](notes/08-correlation-and-causation.md) | Pearson vs Spearman; confounding, partial correlation, colliders; Simpson's paradox; DiD, IV, RD, matching |
| 09 | [Bayesian inference](notes/09-bayesian-inference.md) | Bayes' theorem; Beta-Binomial; switchpoint model; randomised response; Challenger; German tank |
| 10 | [MCMC and PyMC](notes/10-mcmc-and-pymc.md) | Metropolis, NUTS; mixture model; diagnostics (R-hat, ESS, autocorrelation); PyMC3 → PyMC 5 map |
| 11 | [Priors and bandits](notes/11-priors-and-bandits.md) | prior types; prior washout; ridge and lasso as priors; Thompson sampling, regret |
| 12 | [Bayesian A/B testing](notes/12-bayesian-ab-testing.md) | PyMC delta model; Beta closed form; P(B > A); expected-loss stopping; ranking by lower credible bound |
| 13 | [Loss functions and decisions](notes/13-loss-functions-and-decisions.md) | loss catalogue; Bayes action; Price is Right; sign-sensitive stock loss; Dark Worlds |
| 14 | [Bayesian machine learning](notes/14-bayesian-machine-learning.md) | EM for GMMs; Bayesian logistic regression; VAEs and the ELBO; Gaussian processes, Bayesian optimisation |

---

## Rules of thumb

| Rule | Note |
|---|---|
| `sf(k)` is P(X > k); for "k or more" on a discrete distribution pass k − 1 | [02](notes/02-distributions-and-sampling.md) |
| The most extreme averages come from the smallest groups; always show N | [02](notes/02-distributions-and-sampling.md) |
| Default to Welch's t (`equal_var=False`) | [04](notes/04-hypothesis-testing.md) |
| Twenty tests at α = 0.05 give a 64% chance of a false positive; use Holm or BH | [04](notes/04-hypothesis-testing.md) |
| Halving the minimum detectable effect quadruples the sample size | [06](notes/06-ab-testing.md) |
| Do not stop a fixed-horizon test the first time p < 0.05 | [06](notes/06-ab-testing.md) |
| Control for confounders, never for colliders | [08](notes/08-correlation-and-causation.md) |
| Compute derived quantities within each posterior sample, then summarise | [10](notes/10-mcmc-and-pymc.md) |
| R-hat ≤ 1.01, no divergences, ESS in the hundreds before you trust a posterior | [10](notes/10-mcmc-and-pymc.md) |
| Never put zero prior mass where the truth could be | [11](notes/11-priors-and-bandits.md) |
| Ship B when the expected loss of choosing it is below the smallest difference you care about | [12](notes/12-bayesian-ab-testing.md) |
| Rank items with few ratings by a lower credible bound, not the raw average | [12](notes/12-bayesian-ab-testing.md) |
| Squared loss → mean, absolute loss → median, zero-one → MAP; any other loss needs an optimiser | [13](notes/13-loss-functions-and-decisions.md) |

---

## Resource map

### Related notes elsewhere
- [programming/python/04-python-for-data/](../programming/python/04-python-for-data/README.md): the seven `1_Overview` → `7_Time_Series` notebooks (NumPy, pandas, plotting, time series) and the Michigan/Wesleyan pandas scripts.
- [data-science/](../data-science/README.md): modelling, evaluation metrics and the text-analytics companion code.

### Books and courses
- Davidson-Pilon, *Bayesian Methods for Hackers* (MIT): condensed into notes 09–13 and part of 02; the snapshot was removed 2026-10-31 (see [references.md](references.md#removed-snapshots)).
- Bruce & Bruce, *Practical Statistics for Data Scientists*, and Reinhart, *Statistics Done Wrong*: the frequentist references for notes 02–07.
- Full list with chapter-to-note mapping: [references.md](references.md#books-and-courses).

### Coursework and practice
| Path | What | Label |
|---|---|---|
| [practice/5_Statistical_Analysis.ipynb](practice/5_Statistical_Analysis.ipynb) | distributions, tests, A/B testing, correlation and Simpson's paradox on synthetic data (notes 02–08) | runs offline; needs `numpy scipy statsmodels pandas seaborn` |
| [practice/AB-Bayes/AB_Testing_with_Python.ipynb](practice/AB-Bayes/AB_Testing_with_Python.ipynb) | frequentist A/B test on Kaggle `ab_data.csv` (note 06); restored from history 2026-10-31 | needs `ab_data.csv` (Kaggle, not included); add the missing imports `import statsmodels.stats.api as sms` and `from math import ceil` |
| [practice/courses/](practice/courses/) | Michigan *Applied Data Science* and Wesleyan *Data Analysis and Interpretation* scripts (note 04) | needs the Coursera datasets (NESARC, AddHealth, grades; not included); paths hardcoded to `/Users/wiseer85/Desktop/` |
| [practice/BayesianML/](practice/BayesianML/) | Coursera *Bayesian Methods for ML*: EM, MCMC, VAE, GPs, final project (notes 10, 14) | legacy; needs `bayesian.yml` (Python 3.7, TF 1.15, `pymc3==3.11.4`, `theano-pymc==1.1.2`) and the Coursera `grader` module (not included) |

### Readings
- [sources/](sources/): 14 PDFs (statistics, Bayesian methods, experimentation, pandas references) and figures in `images/`. Status of each file, including the duplicate ISLP copy: [references.md](references.md#readings-in-sources).

### Interviewing guide
- [1-foundations](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/1-foundations/00-overview.md): compressed summary for interview prep. There is no statistics-specific pillar; notes 04–06 and 12 cover the usual stats and experimentation questions.

### External references and source quality
Every source the notes cite, the PyMC version audit, Jupyter quick hacks and quality flags: [references.md](references.md).

### Previous and next layer
← Builds on [programming/python/04-python-for-data/](../programming/python/04-python-for-data/README.md)
→ [data-science/](../data-science/README.md) — models, evaluation and ML.
→ [data-engineering/](../data-engineering/README.md) — pipelines and infrastructure.
→ [generative-ai/](../generative-ai/README.md) — LLM applications, starting at 01-llm-fundamentals.
