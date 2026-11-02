# Applied analyses

Complete analyses, each going from a business question through a dataset to a recommendation someone could act on.

**Why this pillar.** The earlier pillars teach tools one at a time. Real work arrives as a vague question from someone with a decision to make, and most of the skill lies in what surrounds the method: choosing a baseline, finding what to check the answer against, pricing the result, and saying what it does not establish. A model that nobody can act on is unfinished. These chapters finish the job each time.

**The story.** Fernhill Home, the fictional retailer from the [visualisation pillar](../05-visualisation-and-storytelling/README.md), has a busy year. Its operations manager needs to book warehouse staff for the fourth quarter, so we forecast demand and find that the point of a forecast is the plan it sets. Credit scoring steps outside the shop to a real dataset of German loans, where the sample isn't the population and correcting for that changes the decision. Back at Fernhill, retention has fallen, and cohorts split the fall into what happened to customers and who was bought. A new mobile checkout looks harmless on the headline, and the funnel finds the broken step behind it. A win-back campaign would have gone to the wrong customers, and a holdout shows why. The whole year then goes into one SQL query that ends an argument about where the growth came from. A new subscription box raises a harder question, when customers will leave given that many haven't yet, and a welcome call that looks excellent turns out to work for three months and to be worth about half of what its chart suggested. Following customers month by month through states puts a price on each and shows why one chain for everybody undervalues them. Marketing then asks where next quarter's budget should go: last-touch attribution credits the channel that closes the sale, a geo test and a mix model show how much of that it caused, and a new customer's worth becomes a range. Chapter 1's forecast finally reaches the warehouse floor, as how much stock to hold and how many packers to roster on a Monday. Every chapter has the same shape: a question, a dataset, a check against something known, and a recommendation with its limits.

## Reading order

| # | Note | The question it answers |
|---|---|---|
| 1 | [Forecasting](notes/01-forecasting.md) | How many people does the warehouse need, and which forecast should we trust? |
| 2 | [Credit scoring](notes/02-credit-scoring.md) | Which applications should a bank approve, and at what cutoff? |
| 3 | [Cohort and retention](notes/03-cohort-and-retention.md) | Did we lose customers, or buy worse ones? |
| 4 | [Funnel and conversion](notes/04-funnel-and-conversion.md) | Did the checkout redesign hurt, and should we roll it back? |
| 5 | [Segmentation and RFM](notes/05-segmentation-and-rfm.md) | Who should a campaign target, and how will we know it worked? |
| 6 | [SQL for analytics](notes/06-sql-for-analytics.md) | Where did the year's revenue change come from? |
| 7 | [Survival and event history](notes/07-survival-and-event-history.md) | When will a customer leave, and does the welcome call delay it? |
| 8 | [States and sequences](notes/08-states-and-sequences.md) | Which journeys lead to a second order, and what is a customer in each state worth? |
| 9 | [Marketing measurement](notes/09-marketing-measurement.md) | Where should next quarter's budget go, and what is a new customer worth? |
| 10 | [Operations and supply chain](notes/10-operations-and-supply-chain.md) | How much of each product should the warehouse hold, and how many packers on a Monday? |

Chapter 5 also holds a separate case, [segmenting B2B customers by behaviour](notes/05-segmentation-and-rfm.md#case-segmenting-b2b-customers-by-behaviour), which tests whether cohorts found by clustering deserve trust on synthetic data.

The chapters can be read in any order, though 3 to 6 share a dataset and refer to each other. They lean on [experimentation and causality](../03-experimentation-and-causality/README.md) for test sizing and causal reasoning, and chapter 6 on the [SQL module](../../programming/sql/README.md) for the language. Chapter 9 picks up chapter 3's pointer to BG/NBD and sets a fitted lifetime value beside chapter 8's Markov one, and chapter 10 starts from the forecast in chapter 1. Then go on to [data science](../../data-science/README.md).

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [Programming: SQL](../../programming/sql/README.md) | The SQL chapter assumes this module, which teaches the language |

**Feeds into**

| Chapter | Why |
|---|---|
| [DS 05/01 Time-series ML](../../data-science/05-time-series-and-recommenders/notes/01-time-series-ml.md) | Forecasting carries the same idea through to a staffing decision, and note 10 through to a stock order |
| [DS 01/10 Imbalance, errors and drift](../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md) | Picks up where the credit scorecard stops |
| [DS 01/05 Unsupervised learning](../../data-science/01-classical-ml/notes/05-unsupervised-learning.md) | Segmentation puts k-means to work on customers, and note 08 clusters journeys by their order |
| [DE 06/04 Drift](../../data-engineering/06-ml-platform/notes/04-drift.md) | PSI is computed in the credit chapter |
| [GA 05 RL](../../generative-ai/05-RL/README.md) | Note 08's Markov chain with rewards is an MDP without actions |
| [DS 01/12 Reading the errors](../../data-science/01-classical-ml/notes/12-reading-the-errors.md) | Credit's cut-off leads on to reading who is wrongly declined |

## Rules of thumb

- Write down the decision before you start the analysis. If no result could change it, stop.
- Beat a baseline first. A model that can't beat last year's numbers isn't a model yet.
- Backtest over many origins, because one split is one anecdote.
- Check a method against something known: a synthetic truth, a published table, or a second implementation.
- Price the result. A rate persuades nobody until it becomes money, with its assumptions stated.
- Split a change in any aggregate into rate and mix before you explain it.
- A before-and-after isn't an experiment. Find a comparison group, or randomise.
- Score every segmentation on a later period. Otherwise it is a description, not a prediction.
- Predicting who buys is not the same as knowing who is persuadable. Only a holdout tells you.
- Reconcile each report's total against the source before anyone reads it.
- A customer who has not churned yet is censored, not retained. Never average lifetimes over the churned only.
- A transition matrix is a description of the past; it forecasts only if the process is stationary, so check it on a holdout period.
- Attribution allocates credit; only an experiment or a model with a causal design measures incrementality.
- The forecast's error distribution is the input to the stock decision, not the point forecast.
- End with the recommendation, then say what would change it.

## Deck and practice

The deck is [`slides/applied-analyses.pptx`](slides/applied-analyses.pptx), with its source in [`slides/deck.yaml`](slides/deck.yaml). Rebuild it with `make slides PILLAR=data-analytics/06-applied-analyses STRICT=1`.

The code is in [`practice/`](practice/). There is one script per chapter, split into `# %%` sections that match the note's code blocks, and every chart is saved to `data-analytics/sources/images/`. `retail.py` is the seeded Fernhill generator, so chapters 1 and 3 to 10 need no download. Chapter 2 uses the open South German Credit data, kept in `practice/data/` and described in its [README](practice/data/README.md).

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
```
