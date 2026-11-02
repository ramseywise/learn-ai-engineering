# Data Analytics

> What a data analyst has to know: get data into a frame, describe it, test a claim, model a relationship, forecast it, explain it to someone, and know when the numbers lie.

Position in the path: [programming/python](../programming/python/README.md) modules 01 to 03 come first. [Data science](../data-science/README.md), [data engineering](../data-engineering/README.md) and [generative AI](../generative-ai/README.md) build on this subject.

## What it is

An analyst is handed a question and some data, and owes back an answer that somebody can act on. That takes more than statistics. The data has to be loaded and cleaned before anyone can test it, and a correct result is wasted if the person deciding cannot read the chart. The six pillars follow that order of work, from a messy export to a recommendation.

The thread through all of them is the last clause of the framing, knowing when the numbers lie. A many-to-many join inflates revenue without raising an error. A mean of rates ranks regions wrongly. A test stopped at the first small p-value finds effects that are not there. A chart with two y axes implies a relationship its author chose. None of these announce themselves, so each pillar teaches the check along with the method.

## The six pillars

| Pillar | The analyst's job | What you learn | Chapters | Deck |
|---|---|---|---|---|
| [01 Python for data analysis](01-python-for-data-analysis/README.md) | get data into a frame | Load, clean, select, join, summarise and plot data in pandas, assuming no earlier pandas. | 7 | [deck](01-python-for-data-analysis/slides/python-for-data-analysis.pptx) |
| [02 Probability and statistics](02-probability-and-statistics/README.md) | describe it, test a claim, model a relationship | Describe data, reason with probability, estimate with intervals, test, and fit regressions. | 6 | [deck](02-probability-and-statistics/slides/probability-and-statistics.pptx) |
| [03 Experimentation and causality](03-experimentation-and-causality/README.md) | test a claim about a change | Run A/B tests, run them at scale, and decide when a correlation can bear a causal reading. | 4 | [deck](03-experimentation-and-causality/slides/experimentation-and-causality.pptx) |
| [04 Bayesian analysis](04-bayesian-analysis/README.md) | decide under uncertainty | Answer the same questions with posteriors: PyMC, priors, Bayesian A/B tests and loss functions. | 6 | [deck](04-bayesian-analysis/slides/bayesian-analysis.pptx) |
| [05 Visualisation and storytelling](05-visualisation-and-storytelling/README.md) | explain it to someone | Choose a chart, draw it in Python and JavaScript, and use it to get a decision made. | 5 | [deck](05-visualisation-and-storytelling/slides/visualisation-and-storytelling.pptx) |
| [06 Applied analyses](06-applied-analyses/README.md) | forecast it, and do the real work | End-to-end analyses: forecasting, credit scoring, cohorts, funnels, segmentation and SQL. | 6 | [deck](06-applied-analyses/slides/applied-analyses.pptx) |

Read them in order the first time. [CURRICULUM.md](CURRICULUM.md) gives the sequence, the practice for each step and how you know you are done. [references.md](references.md) is the shared book library, with free courses and videos.

## Two ways to answer the same question

Pillars 02 and 03 and pillar 04 answer the same questions by different routes, and an analyst should be able to do both.

| | Frequentist (02, 03) | Bayesian (04) |
|---|---|---|
| Core question | How surprising is this data if nothing is going on? | Given the data, what should I believe and do? |
| Tools | `scipy.stats`, `statsmodels` | PyMC, ArviZ, conjugate Beta updates |
| A/B testing | [Power, sample size, z-test, peeking](03-experimentation-and-causality/notes/01-ab-testing.md) | [P(B > A), expected loss](04-bayesian-analysis/notes/04-bayesian-ab-testing.md) |
| Strength | Standard, fast, and what most teams report | Small samples, prior knowledge, decisions with asymmetric costs |

Name the distribution, fix the sample size before you look, and report effect sizes with intervals and not bare p-values.

## Syllabus

These are the chapters on disk as of 2 November 2026.

### [01 Python for data analysis](01-python-for-data-analysis/README.md)

1. [Series and DataFrame](01-python-for-data-analysis/notes/01-series-and-dataframe.md)
2. [Loading and Cleaning](01-python-for-data-analysis/notes/02-loading-and-cleaning.md)
3. [Indexing and Selection](01-python-for-data-analysis/notes/03-indexing-and-selection.md)
4. [Reshaping and Joins](01-python-for-data-analysis/notes/04-reshaping-and-joins.md)
5. [Groupby and Aggregation](01-python-for-data-analysis/notes/05-groupby-and-aggregation.md)
6. [Time Series](01-python-for-data-analysis/notes/06-time-series.md)
7. [Plotting](01-python-for-data-analysis/notes/07-plotting.md)

### [02 Probability and statistics](02-probability-and-statistics/README.md)

1. [Descriptive Statistics and EDA](02-probability-and-statistics/notes/01-descriptive-statistics-and-eda.md)
2. [Probability Foundations](02-probability-and-statistics/notes/02-probability-foundations.md)
3. [Distributions and Sampling](02-probability-and-statistics/notes/03-distributions-and-sampling.md)
4. [Estimation](02-probability-and-statistics/notes/04-estimation.md)
5. [Hypothesis Testing](02-probability-and-statistics/notes/05-hypothesis-testing.md)
6. [Regression and GLMs](02-probability-and-statistics/notes/06-regression-and-glms.md)

### [03 Experimentation and causality](03-experimentation-and-causality/README.md)

1. [A/B Testing](03-experimentation-and-causality/notes/01-ab-testing.md)
2. [Metrics and KPI Design](03-experimentation-and-causality/notes/02-metrics-and-kpi-design.md)
3. [Experimentation at Scale](03-experimentation-and-causality/notes/03-experimentation-at-scale.md)
4. [Correlation, Confounding and Causation](03-experimentation-and-causality/notes/04-correlation-and-causation.md)

### [04 Bayesian analysis](04-bayesian-analysis/README.md)

1. [Bayesian Inference](04-bayesian-analysis/notes/01-bayesian-inference.md)
2. [MCMC and PyMC](04-bayesian-analysis/notes/02-mcmc-and-pymc.md)
3. [Priors and Bandits](04-bayesian-analysis/notes/03-priors-and-bandits.md)
4. [Bayesian A/B Testing](04-bayesian-analysis/notes/04-bayesian-ab-testing.md)
5. [Loss Functions and Bayesian Decisions](04-bayesian-analysis/notes/05-loss-functions-and-decisions.md)
6. [Bayesian Machine Learning](04-bayesian-analysis/notes/06-bayesian-machine-learning.md)

### [05 Visualisation and storytelling](05-visualisation-and-storytelling/README.md)

1. [Grammar of graphics and chart choice](05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice.md)
2. [Matplotlib and seaborn](05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn.md)
3. [Plotly and interactive charts](05-visualisation-and-storytelling/notes/03-plotly-and-interactive.md)
4. [JavaScript: D3, Vega-Lite and Observable Plot](05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot.md)
5. [Dashboards and storytelling with data](05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling.md)

### [06 Applied analyses](06-applied-analyses/README.md)

1. [Forecasting: how many people does the warehouse need?](06-applied-analyses/notes/01-forecasting.md)
2. [Credit scoring: which applications should a bank approve?](06-applied-analyses/notes/02-credit-scoring.md)
3. [Cohort and retention: did we lose customers, or buy worse ones?](06-applied-analyses/notes/03-cohort-and-retention.md)
4. [Funnel and conversion: why a flat headline can hide a broken page](06-applied-analyses/notes/04-funnel-and-conversion.md)
5. [Segmentation and RFM: who to contact, and who would have bought anyway](06-applied-analyses/notes/05-segmentation-and-rfm.md)
6. [SQL for analytics: the revenue bridge, and the patterns behind it](06-applied-analyses/notes/06-sql-for-analytics.md)

## Rules of thumb

| Rule | Where |
|---|---|
| State `how` and `validate` on a merge, then compare row counts and one total before and after | [01](01-python-for-data-analysis/notes/04-reshaping-and-joins.md) |
| For a group's rate, sum the numerator and the denominator and then divide; never average the rates | [01](01-python-for-data-analysis/notes/05-groupby-and-aggregation.md) |
| Make absent days visible with `asfreq`, and keep model features looking backward | [01](01-python-for-data-analysis/notes/06-time-series.md) |
| `sf(k)` is P(X > k); for "k or more" on a discrete distribution, pass k − 1 | [02](02-probability-and-statistics/notes/03-distributions-and-sampling.md) |
| The most extreme averages come from the smallest groups, so always show N | [02](02-probability-and-statistics/notes/03-distributions-and-sampling.md) |
| Default to Welch's t (`equal_var=False`) | [02](02-probability-and-statistics/notes/05-hypothesis-testing.md) |
| Twenty independent tests at α = 0.05 give a 64% chance of at least one false positive; use Holm or BH | [02](02-probability-and-statistics/notes/05-hypothesis-testing.md) |
| Halving the minimum detectable effect multiplies the sample size by about four | [03](03-experimentation-and-causality/notes/01-ab-testing.md) |
| Do not stop a fixed-horizon test the first time p < 0.05 | [03](03-experimentation-and-causality/notes/01-ab-testing.md) |
| Control for confounders, never for colliders | [03](03-experimentation-and-causality/notes/04-correlation-and-causation.md) |
| R-hat at most 1.01, no divergences and ESS in the hundreds before you trust a posterior | [04](04-bayesian-analysis/notes/02-mcmc-and-pymc.md) |
| Never put zero prior mass where the truth could be | [04](04-bayesian-analysis/notes/03-priors-and-bandits.md) |
| Ship B when the expected loss of choosing it is below the smallest difference you care about | [04](04-bayesian-analysis/notes/04-bayesian-ab-testing.md) |
| Squared loss gives the mean, absolute loss the median, zero-one loss the MAP; any other loss needs an optimiser | [04](04-bayesian-analysis/notes/05-loss-functions-and-decisions.md) |
| Beat a baseline first, and backtest over many origins because one split is one anecdote | [06](06-applied-analyses/README.md#rules-of-thumb) |
| Split a change in any aggregate into rate and mix before you explain it | [06](06-applied-analyses/README.md#rules-of-thumb) |

## Layout

```text
data-analytics/
├── README.md         this file
├── CURRICULUM.md     the sequenced path
├── references.md     the shared book library, courses and videos
├── sources/          PDFs and images/ shared by all six pillars
└── 0N-<pillar>/      README.md, references.md, notes/, practice/, slides/
```

Each pillar's README says how to run its practice, and its `references.md` maps books and papers to chapters.

## Interview guide

[1-foundations](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/1-foundations/00-overview.md) is a compressed summary for interview preparation, in a private repo.
