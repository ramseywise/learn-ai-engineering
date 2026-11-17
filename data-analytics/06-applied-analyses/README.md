# Applied analyses

Complete analyses, each going from a business question through a dataset to a recommendation someone could act on. Five steps: forecast and score, read the customers, value a customer's lifetime and spend, run operations and define metrics, and ask people with a survey.

**What you should already know.** Nothing below is taught again here. Tick each line off, and go back to the chapter it links for any you cannot.

SQL, from [programming: SQL](../../programming/sql/README.md):

- [ ] Write joins, grouping and aggregation in SQL, because chapter 6 teaches analytics queries on top of them

Processing data, from [module 01](../01-python-for-data-analysis/README.md):

- [ ] Get one number per group with groupby and check that the groups add up ([groupby and aggregation](../01-python-for-data-analysis/notes/07-groupby-and-aggregation.md))
- [ ] Join and reshape tables, and count rows before and after ([reshaping and joins](../01-python-for-data-analysis/notes/04-reshaping-and-joins.md))

Probability and statistics, from [module 02](../02-probability-and-statistics/README.md):

- [ ] Read regression output ([regression and GLMs](../02-probability-and-statistics/notes/06-regression-and-glms.md))
- [ ] Say how the rows got into the table ([data generating process](../02-probability-and-statistics/notes/07-data-generating-process.md))

Experimentation, from [module 03](../03-experimentation-and-causality/README.md):

- [ ] Size an A/B test ([A/B testing](../03-experimentation-and-causality/notes/01-ab-testing.md))
- [ ] Weight a sample to match a target population ([matching and weighting](../03-experimentation-and-causality/notes/05-matching-and-weighting.md))

## Lecture

Start with the overview deck, [Applied analyses](slides/applied-analyses.pptx), with its source in [slides/deck.yaml](slides/deck.yaml). It covers the module's chapters in reading order. There is one deck for the module, not one per step.

## The core

The earlier modules teach tools one at a time. Real work arrives as a vague question from someone with a decision to make, and most of the skill lies in what surrounds the method: choosing a baseline, finding what to check the answer against, pricing the result, and saying what it does not establish. A model that nobody can act on is unfinished. These chapters finish the job each time, and each has the same shape: a question, a dataset, a check against something known, and a recommendation with its limits.

Fernhill Home, the fictional retailer from the [visualisation module](../05-visualisation-and-storytelling/README.md), has a busy year. Its operations manager needs to book warehouse staff for the fourth quarter, so we forecast demand and find that the point of a forecast is the plan it sets. Credit scoring steps outside the shop to a real dataset of German loans, where the sample is not the population and correcting for that changes the decision. Back at Fernhill, retention has fallen, and cohorts split the fall into what happened to customers and who was bought. A new mobile checkout looks harmless on the headline, and the funnel finds the broken step behind it. A win-back campaign would have gone to the wrong customers, and a holdout shows why. The whole year then goes into one SQL query that ends an argument about where the growth came from.

A new subscription box raises a harder question, when customers will leave given that many have not yet, and a welcome call that looks excellent turns out to work for three months and to be worth about half of what its chart suggested. Following customers month by month through states puts a price on each and shows why one chain for everybody undervalues them. Marketing then asks where next quarter's budget should go: last-touch attribution credits the channel that closes the sale, a geo test and a mix model show how much of that it caused, and a new customer's worth becomes a range.

Chapter 1's forecast finally reaches the warehouse floor, as how much stock to hold and how many packers to roster on a Monday. Then an email blast says 73% of customers are satisfied, and chapter 12 rebuilds that as a survey whose error can be stated.

## Syllabus

One row per step. **Core concepts** are the ideas that make the step go right, **Study** is what to read, **Labs** is what to run afterwards, and **Sources** is where to read more. The chapters can be read in any order, though 3 to 6 share a dataset and refer to each other. Chapter 9 picks up chapter 3's pointer to BG/NBD and sets a fitted lifetime value beside chapter 8's Markov one, and chapter 10 starts from the forecast in chapter 1. Chapter 12 leans on [the data generating process](../02-probability-and-statistics/notes/07-data-generating-process.md) and [matching and weighting](../03-experimentation-and-causality/notes/05-matching-and-weighting.md). Chapter 5 also holds a separate case, [segmenting B2B customers by behaviour](notes/05-segmentation-and-rfm.md#case-segmenting-b2b-customers-by-behaviour), which tests whether cohorts found by clustering deserve trust on synthetic data. Every chapter's script is described in [practice/README.md](practice/README.md).

| Submodule | Core concepts | Study | Labs | Sources |
|---|---|---|---|---|
| **1. Forecast and score:** a plan and a cutoff | Write down the decision before you start the analysis, and beat a baseline first. Backtest over many origins, because one split is one anecdote. Check a method against something known: a synthetic truth, a published table, or a second implementation. Price the result, because a rate persuades nobody until it becomes money. | [1 Forecasting](notes/01-forecasting.md) · [2 Credit scoring](notes/02-credit-scoring.md) | [ch01_forecasting.py](practice/ch01_forecasting.py) · [ch02_credit_scoring.py](practice/ch02_credit_scoring.py) | Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* sections 5.2, 5.8, 5.10 and 13.1 · Hyndman & Koehler, [Another look at measures of forecast accuracy](https://doi.org/10.1016/j.ijforecast.2006.03.001) · Taylor & Letham, [Forecasting at Scale](https://doi.org/10.1080/00031305.2017.1380080) · Grömping, [South German Credit Data](http://www1.beuth-hochschule.de/FB_II/reports/Report-2019-004.pdf) · Basel Committee, [IRB risk weight functions](https://www.bis.org/publications/explanatory-note-basel-ii-irb-risk-weight-functions.pdf) |
| **2. Read the customers:** cohorts, funnels, segments and SQL | Split a change in any aggregate into rate and mix before you explain it. A before-and-after is not an experiment, so find a comparison group or randomise. Score every segmentation on a later period, otherwise it is a description and not a prediction. Predicting who buys is not the same as knowing who is persuadable, and only a holdout tells you. Reconcile each report's total against the source before anyone reads it. | [3 Cohort and retention](notes/03-cohort-and-retention.md) · [4 Funnel and conversion](notes/04-funnel-and-conversion.md) · [5 Segmentation and RFM](notes/05-segmentation-and-rfm.md) · [6 SQL for analytics](notes/06-sql-for-analytics.md) | [ch03_cohort_retention.py](practice/ch03_cohort_retention.py) · [ch04_funnel.py](practice/ch04_funnel.py) · [ch05_segmentation_rfm.py](practice/ch05_segmentation_rfm.py) · [ch06_sql_analytics.py](practice/ch06_sql_analytics.py) | Fader & Hardie, [How to Project Customer Retention](https://doi.org/10.1002/dir.20074) · Kohavi et al., [Controlled experiments on the web](https://doi.org/10.1007/s10618-008-0114-1) · Bickel, Hammel & O'Connell, [Sex Bias in Graduate Admissions](https://doi.org/10.1126/science.187.4175.398) · Gutierrez & Gérardy, [Causal Inference and Uplift Modelling](https://proceedings.mlr.press/v67/gutierrez17a.html) · Rousseeuw, [Silhouettes](https://doi.org/10.1016/0377-0427(87)90125-7) · Ben-David et al., [A Sober Look at Clustering Stability](https://doi.org/10.1007/11776420_4) |
| **3. Lifetime and spend:** survival, states, marketing and lifetime value | A customer who has not churned yet is censored, not retained, so never average lifetimes over the churned only. A transition matrix describes the past, and forecasts only if the process is stationary, so check it on a holdout period. Attribution allocates credit, and only an experiment or a model with a causal design measures incrementality. | [7 Survival and event history](notes/07-survival-and-event-history.md) · [8 States and sequences](notes/08-states-and-sequences.md) · [9 Marketing measurement](notes/09-marketing-measurement.md) · [9b Customer lifetime value](notes/09b-customer-lifetime-value.md) | [ch07_survival.py](practice/ch07_survival.py) · [ch08_states_sequences.py](practice/ch08_states_sequences.py) · [ch09_marketing_measurement.py](practice/ch09_marketing_measurement.py), which also covers 9b | Hernán & Robins, *Causal Inference: What If* ch. 17 · James et al., *ISLP* ch. 11 · Efron & Hastie, *Computer Age Statistical Inference* ch. 9 · Grinstead & Snell, *Introduction to Probability* section 11.2 · Pfeifer & Carraway, *Modeling Customer Relationships as Markov Chains* · Fader, Hardie & Lee, [Counting Your Customers the Easy Way](https://brucehardie.com/papers/018/) · Chan & Perry, [Challenges and Opportunities in Media Mix Modeling](https://research.google/pubs/challenges-and-opportunities-in-media-mix-modeling/) · Fader & Hardie, [The Gamma-Gamma Model](https://brucehardie.com/notes/025/) |
| **4. Operations and metrics:** stock, packers and metric trees | The forecast's error distribution is the input to the stock decision, not the point forecast. Little's law ties the queue to the roster. A metric needs a definition, a tree of what feeds it, and a check that would catch it being gamed. | [10 Operations and supply chain](notes/10-operations-and-supply-chain.md) · [10b Packers: queues, Little's law and a shift plan](notes/10b-packers-queues-and-a-shift-plan.md) · [11 Metric trees and defining metrics](notes/11-metric-trees.md) | [ch10_operations_supply_chain.py](practice/ch10_operations_supply_chain.py), which also covers 10b · [ch11_metric_trees.py](practice/ch11_metric_trees.py) | Little, [A Proof for the Queuing Formula: L = λW](https://doi.org/10.1287/opre.9.3.383) · Makridakis et al., [The M5 uncertainty competition](https://doi.org/10.1016/j.ijforecast.2021.10.009) · Manheim & Garrabrant, [Categorizing Variants of Goodhart's Law](https://arxiv.org/abs/1803.04585) · Rodden, Hutchinson & Fu, [Measuring the User Experience on a Large Scale](https://research.google.com/pubs/archive/36299.pdf) · Wilson, *Machine Learning Engineering in Action* ch. 5 |
| **5. Surveys:** who to ask and how to weight them | A margin of error measures sampling error only. It says nothing about coverage, nonresponse or the wording of the question. | [12 Surveys and sampling design](notes/12-surveys-and-sampling-design.md) · [12b Weighting, the margin and the question](notes/12b-weighting-the-margin-and-the-question.md) | [ch12_surveys.py](practice/ch12_surveys.py), which covers both | Statistics Canada, [*Survey Methods and Practices*](https://www150.statcan.gc.ca/n1/en/pub/12-587-x/12-587-x2003001-eng.pdf) · United Nations, [*Designing Household Survey Samples*](https://unstats.un.org/unsd/publication/seriesf/seriesf_98e.pdf) · Kish, [Methods for Design Effects](https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/methods-for-design-effects.pdf) · Kalton & Flores-Cervantes, [Weighting Methods](https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/weighting-methods.pdf) · Brick & Tourangeau, [Responsive Survey Designs](https://reference-global.com/download/article/10.1515/jos-2017-0034.pdf) · Bradley et al., [Unrepresentative big surveys](https://www.nature.com/articles/s41586-021-04198-4) |

Every source and the notes it maps to: [references.md](references.md).

## Rules of thumb

- **Write down the decision before you start the analysis.** If no result could change it, stop.
- **Beat a baseline first.** A model that can't beat last year's numbers isn't a model yet.
- **Backtest over many origins,** because one split is one anecdote.
- **Check a method against something known:** a synthetic truth, a published table, or a second implementation.
- **Price the result.** A rate persuades nobody until it becomes money, with its assumptions stated.
- **Split a change in any aggregate into rate and mix** before you explain it.
- **A before-and-after isn't an experiment.** Find a comparison group, or randomise.
- **Score every segmentation on a later period.** Otherwise it is a description, not a prediction.
- **Predicting who buys is not the same as knowing who is persuadable.** Only a holdout tells you.
- **Reconcile each report's total against the source** before anyone reads it.
- **A customer who has not churned yet is censored, not retained.** Never average lifetimes over the churned only.
- **A transition matrix is a description of the past;** it forecasts only if the process is stationary, so check it on a holdout period.
- **Attribution allocates credit;** only an experiment or a model with a causal design measures incrementality.
- **The forecast's error distribution is the input to the stock decision,** not the point forecast.
- **A margin of error measures sampling error only.** It says nothing about coverage, nonresponse or the wording of the question.
- **End with the recommendation,** then say what would change it.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [Programming: SQL](../../programming/sql/README.md) | The SQL chapter assumes this module, which teaches the language |

**Feeds into**

| Chapter | Why |
|---|---|
| [DE 07/03 Catalog, semantic layer and contracts](../../data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts.md) | Executes the metric definitions from note 11 at any grain, and traces who a change breaks |
| [DS 05/01 Time-series ML](../../data-science/05-time-series-and-recommenders/notes/01-time-series-ml.md) | Forecasting carries the same idea through to a staffing decision, and note 10 through to a stock order |
| [DS 01/10 Imbalance, errors and drift](../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md) | Picks up where the credit scorecard stops |
| [DS 01/05 Unsupervised learning](../../data-science/01-classical-ml/notes/05-unsupervised-learning.md) | Segmentation puts k-means to work on customers, and note 08 clusters journeys by their order |
| [DS 01/05b Clustering categorical and mixed data](../../data-science/01-classical-ml/notes/05b-clustering-categorical-and-mixed-data.md) | Segmentation with plan, channel or industry columns beside the numbers |
| [DE 06/04 Drift](../../data-engineering/06-ml-platform/notes/04-drift.md) | PSI is computed in the credit chapter |
| [GA 05 RL](../../generative-ai/05-RL/README.md) | Note 08's Markov chain with rewards is an MDP without actions |
| [DS 01/12 Reading the errors](../../data-science/01-classical-ml/notes/12-reading-the-errors.md) | Credit's cut-off leads on to reading who is wrongly declined |

<a id="deck-and-practice"></a>

## Practice

The code is in [practice/](practice/). There is one script per chapter, split into `# %%` sections that match the note's code blocks, and every chart is saved to `data-analytics/sources/images/`. `retail.py` is the seeded Fernhill generator, so chapters 1 and 3 to 12 need no download. Chapter 2 uses the open South German Credit data, kept in `practice/data/` and described in its [README](practice/data/README.md).

```bash
cd data-analytics/06-applied-analyses/practice
uv run ch01_forecasting.py          # statsmodels and Prophet, about a minute
uv run ch02_credit_scoring.py
uv run ch03_cohort_retention.py
uv run ch04_funnel.py
uv run ch05_segmentation_rfm.py
uv run ch06_sql_analytics.py        # DuckDB, no server
uv run ch07_survival.py             # lifelines, about a minute
uv run ch08_states_sequences.py     # sequenzo for the distance matrix
uv run ch09_marketing_measurement.py   # pymc-marketing and nutpie, several minutes
uv run ch10_operations_supply_chain.py # pulp with CBC, about half a minute
uv run ch11_metric_trees.py
uv run ch12_surveys.py
```

The deck is rebuilt with `make slides PILLAR=data-analytics/06-applied-analyses STRICT=1`.

## Primary texts

- Hyndman and Athanasopoulos, *Forecasting: Principles and Practice*
- Hernán and Robins, *Causal Inference: What If*
- Fader and Hardie, *How to Project Customer Retention*
- Siddiqi, *Intelligent Credit Scoring*: further reading, not read for these notes

Everything else: [references.md](references.md).

## Next

Start with submodule 1, **Forecast and score**: read [1 Forecasting](notes/01-forecasting.md), then the other notes in the syllabus order.

After submodule 5 you can take a vague business question to a recommendation with its limits stated, and say what would change it. Then go on to [data science](../../data-science/README.md).
