# 05 — Time series and recommenders

> Two problems that break the assumption that rows are exchangeable: predicting the next value of a series, and ranking a catalogue for one person. Deck: [`slides/time-series-and-recommenders.pptx`](slides/time-series-and-recommenders.pptx) (source [`slides/deck.yaml`](slides/deck.yaml)). Practice: [`practice/`](practice/). References: [`references.md`](references.md).

## What it is

Time series ML turns a history into a forecast using feature tables, gradient boosting and sequence models, tested with backtests. Recommender systems learn preferences from interaction logs using matrix factorisation, linear item models and two-tower networks, and are tested on full-catalogue ranking, counterfactual estimates and A/B tests.

## Why it matters

These are two of the most common jobs a data scientist is handed that a tidy train/test split does not cover. The [M5 competition](https://ideas.repec.org/a/eee/intfor/v38y2022i4p1346-1364.html) found only 35.8% of teams beat a seasonal naive forecast, and [Dacrema et al.](https://arxiv.org/abs/1907.06902) found most published deep recommenders they could reproduce lost to simple methods. In both fields the common failure is an evaluation that flatters the model, so the procedure is what you are really learning.

## The story

An operator needs tomorrow's bike demand by midnight. A copy of last week is the bar to beat, trees clear it once they stop trying to extrapolate, and three leaks would have made the number look twice as good as it is. Then a film site wants a top-ten list. The model with the best rating error loses to a bestseller list, a closed-form linear model wins on this data, and a two-tower network needs a one-line correction before it competes at all, then earns its place when a new film has no history. Finally we ask how anyone knows any of this works: a sampled metric reverses two models, a reweighted log recovers the value of an unshipped policy, and a real A/B test needs millions of users.

## Reading order

| # | Note | Question it answers |
|---|---|---|
| 1 | [Time series ML](notes/01-time-series-ml.md) | What would this forecast really have scored at the moment it was issued? |
| 2 | [Collaborative filtering and matrix factorisation](notes/02-collaborative-filtering-and-matrix-factorisation.md) | Why can the most accurate rating predictor make the worst list? |
| 3 | [Two-tower retrieval and evaluation](notes/03-two-tower-and-evaluation.md) | How do you serve millions of items and new items, and how do you know it works? |

Comes after [classical ML](../01-classical-ml/README.md) and [deep learning](../02-deep-learning/README.md). Chapter 3 points at [LLM embeddings as features](../03-nlp/notes/07-llm-embeddings-as-features.md) for content features.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DA 01/06 Time series](../../data-analytics/01-python-for-data-analysis/notes/06-time-series.md) | Resampling and shifting |
| [DA 03/01 A/B testing](../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md) | Online evaluation and its arithmetic |
| [DA 03/03 Experimentation at scale](../../data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md) | Peeking and sequential methods |
| [DA 06/01 Forecasting](../../data-analytics/06-applied-analyses/notes/01-forecasting.md) | Baselines, and a forecast taken through to a decision |
| [DA 06/05 Segmentation and RFM](../../data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm.md) | The segments in the cash-flow case |

**Feeds into**

| Chapter | Why |
|---|---|
| [GA 02/01 RAG pipeline](../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md) | Ranking metrics used on chunks |
| [GA 02/04 Vector databases and ANN](../../generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann.md) | The same index machinery, for documents |
| [GA 08/07 Evaluating RAG and grounding](../../generative-ai/08-eval/notes/07-evaluating-rag-and-grounding.md) | Recall and NDCG on retrieval |
| [DE 06/04 Drift](../../data-engineering/06-ml-platform/notes/04-drift.md) | Forecast models drift in production |

## Rules of thumb

- State the issue time, horizon and information set before fitting anything.
- Put the seasonal naive in every forecasting table, and popularity in every recommender table.
- A feature is legal only if its value existed at the issue time.
- Divide by a known level before giving a series to trees.
- Start forecasting with features and boosted trees. A deep model must beat them in the same backtest.
- Never score a list with RMSE, and never rank against 99 sampled negatives.
- Try EASE and item kNN before any neural recommender.
- Split interaction data by time. Random holdout more than doubled our NDCG with no change in the model.
- Apply the logQ correction to in-batch softmax, in training only.
- Log propensities and keep some randomisation, or you lose counterfactual evaluation for good.
- Offline results choose what to test. Only a live test decides.

## Practice

Each chapter's code runs top to bottom with [`practice/run_note.py`](practice/run_note.py), and each chapter has a lab holding its exercises. See [`practice/README.md`](practice/README.md). Data is downloaded on first use and cached under `~/.cache/learn-ai-engineering/`.

The [customer segments lab](practice/customer-segments-lab/README.md) backs the [segment forecasting case](notes/01-time-series-ml.md#case-forecasting-each-segments-cash-flow) and needs no download, since its customers are synthetic. It takes one to four minutes on a laptop CPU.

```bash
uv run --with scikit-learn --with pandas --with torch python practice/run_note.py notes/01-time-series-ml.md
uv run --with numpy --with pandas --with scipy python practice/02_cf_lab.py
```
