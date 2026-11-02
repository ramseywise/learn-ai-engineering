# Applied analyses

Six complete analyses, each going from a business question through a dataset to a recommendation someone could act on.

**Why this pillar.** The earlier pillars teach tools one at a time. Real work arrives as a vague question from someone with a decision to make, and most of the skill lies in what surrounds the method: choosing a baseline, finding what to check the answer against, pricing the result, and saying what it does not establish. A model that nobody can act on is unfinished. These chapters finish the job six times.

**The story.** Fernhill Home, the fictional retailer from the [visualisation pillar](../05-visualisation-and-storytelling/README.md), has a busy year. Its operations manager needs to book warehouse staff for the fourth quarter, so we forecast demand and find that the point of a forecast is the plan it sets. Credit scoring steps outside the shop to a real dataset of German loans, where the sample isn't the population and correcting for that changes the decision. Back at Fernhill, retention has fallen, and cohorts split the fall into what happened to customers and who was bought. A new mobile checkout looks harmless on the headline, and the funnel finds the broken step behind it. A win-back campaign would have gone to the wrong customers, and a holdout shows why. Finally, the whole year goes into one SQL query that ends an argument about where the growth came from. Every chapter has the same shape: a question, a dataset, a check against something known, and a recommendation with its limits.

## Reading order

| # | Note | The question it answers |
|---|---|---|
| 1 | [Forecasting](notes/01-forecasting.md) | How many people does the warehouse need, and which forecast should we trust? |
| 2 | [Credit scoring](notes/02-credit-scoring.md) | Which applications should a bank approve, and at what cutoff? |
| 3 | [Cohort and retention](notes/03-cohort-and-retention.md) | Did we lose customers, or buy worse ones? |
| 4 | [Funnel and conversion](notes/04-funnel-and-conversion.md) | Did the checkout redesign hurt, and should we roll it back? |
| 5 | [Segmentation and RFM](notes/05-segmentation-and-rfm.md) | Who should a campaign target, and how will we know it worked? |
| 6 | [SQL for analytics](notes/06-sql-for-analytics.md) | Where did the year's revenue change come from? |

The chapters can be read in any order, though 3 to 6 share a dataset and refer to each other. They lean on [experimentation and causality](../03-experimentation-and-causality/README.md) for test sizing and causal reasoning, and chapter 6 on the [SQL module](../../programming/sql/README.md) for the language. Then go on to [data science](../../data-science/README.md).

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
- End with the recommendation, then say what would change it.

## Deck and practice

The deck is [`slides/applied-analyses.pptx`](slides/applied-analyses.pptx), with its source in [`slides/deck.yaml`](slides/deck.yaml). Rebuild it with `make slides PILLAR=data-analytics/06-applied-analyses STRICT=1`.

The code is in [`practice/`](practice/). There is one script per chapter, split into `# %%` sections that match the note's code blocks, and every chart is saved to `data-analytics/sources/images/`. `retail.py` is the seeded Fernhill generator, so chapters 1 and 3 to 6 need no download. Chapter 2 uses the open South German Credit data, kept in `practice/data/` and described in its [README](practice/data/README.md).

```bash
cd data-analytics/06-applied-analyses/practice
uv run ch01_forecasting.py          # statsmodels and Prophet, about a minute
uv run ch02_credit_scoring.py
uv run ch03_cohort_retention.py
uv run ch04_funnel.py
uv run ch05_segmentation_rfm.py
uv run ch06_sql_analytics.py        # DuckDB, no server
```
