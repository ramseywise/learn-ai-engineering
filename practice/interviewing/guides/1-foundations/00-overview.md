---
origin: synthesized
sources:
  - data-analytics/README.md
  - data-science/README.md
  - data-engineering/README.md
confidence: high
cleaned: 2026-11-02
units:
  - data-science/01-classical-ml
  - data-science/02-deep-learning
  - data-analytics/01-python-for-data-analysis
  - data-analytics/06-applied-analyses/notes/06-sql-for-analytics.md
---
# Pillar 1 — Foundations (classical ML, stats, SQL)

Everything else in AI is built on this: how models learn from data, how you know they work, and how you
query the data in the first place. If you're starting from zero, this pillar is where terms like
"overfitting", "precision/recall" and "train/test split" stop being jargon and become tools you reach for.

## Pick your target first

Data jobs share some foundations and then split. These are the usual shapes, though titles vary by company.

- **Data analyst.** Someone asks "why did sign-ups fall?" You pull the data, test whether the difference is
  real and explain it so that someone can decide. Prepare for SQL, statistics, A/B tests and product sense.
- **Data scientist.** Someone asks "which customers will leave next month, and can we trust the list?" You
  build a model, measure it honestly and explain its limits. Prepare for everything the analyst does, plus ML
  fundamentals and coding.
- **Data engineer.** Someone asks "why is yesterday's revenue table wrong?" You build the pipelines that get
  correct data to everyone else on time. Prepare for SQL, coding, data modelling and pipeline design.

The [interview guide](interview-guide.md#0-three-jobs-and-what-each-is-interviewed-on) compares the three, along
with ML and AI engineers.

## Learning path

Each step lists the course material. You don't need all of it: follow your role's path, and stop when you can explain
a step aloud without notes.

**Everyone**

1. **Python and data handling.** The [Python course](../../../../programming/python/README.md), then
   [Python for data analysis](../../../../data-analytics/01-python-for-data-analysis/README.md), until pandas feels boring.
2. **SQL.** [SQL for analytics](../../../../data-analytics/06-applied-analyses/notes/06-sql-for-analytics.md). Write the
   queries yourself; reading doesn't stick. Interview patterns are in [§6 of the guide](interview-guide.md#6-sql--analytics-screen-folded-in).
3. **Statistics.** [Pillar 11, stats and experimentation](../11-stats-experimentation/00-overview.md), with its
   course chapters on [probability and statistics](../../../../data-analytics/02-probability-and-statistics/README.md).

**Analyst, next**

4. [Experimentation and causality](../../../../data-analytics/03-experimentation-and-causality/README.md),
   [visualisation and storytelling](../../../../data-analytics/05-visualisation-and-storytelling/README.md) and
   [applied analyses](../../../../data-analytics/06-applied-analyses/README.md).

**Data scientist, next**

4. **Core ML by doing.** [Classical ML](../../../../data-science/01-classical-ml/README.md): fit your first models, break them, and
   plot learning curves. Read the notes in order, up to
   [training and tuning](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md) and
   [imbalance, errors and drift](../../../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md).
5. **Project discipline.** [Structuring ML projects](../../../../data-science/02-deep-learning/notes/03-structuring-ml-projects.md):
   error analysis and single-number metrics, the habits that survive into every later pillar.
6. **A second lens.** [Bayesian analysis](../../../../data-analytics/04-bayesian-analysis/README.md).

**Data engineer, next**

4. [Data engineering](../../../../data-engineering/README.md), from
   [data systems and data models](../../../../data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models.md)
   and [ingest](../../../../data-engineering/02-ingest-and-modelling/notes/01-ingest.md) onward, then
   [pillar 8](../8-data-eng-mlops/00-overview.md).

**Then build something.** A public project you can walk through for
[the deep-dive round](../../rounds/project-deep-dive/README.md) beats another course: a real dataset, a baseline, an honest
metric, and a note on what failed.

## Resource map

| Topic | Type | Where | What it teaches |
|---|---|---|---|
| Train, validation, test; bias and variance | note | [statistical foundations](../../../../data-science/01-classical-ml/notes/01-statistical-foundations.md) | The problem setting and why error splits the way it does |
| The training loop, CV, regularisation, search | note | [training and tuning](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md) | One loop on adult census, measured at each step |
| Models | notes | [supervised](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md), [ensembles](../../../../data-science/01-classical-ml/notes/06-ensembles.md), [boosting](../../../../data-science/01-classical-ml/notes/07-boosting-in-practice.md) | The families, with reasons to pick one |
| Features, leakage, pipelines | note | [feature engineering](../../../../data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines.md) | Why pipelines exist |
| Metrics and calibration | note | [model evaluation](../../../../data-science/01-classical-ml/notes/04-model-evaluation.md) | Confusion matrix, ROC, PR, calibration |
| Imbalance, error costs, drift | note | [imbalance, errors and drift](../../../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md) | SMOTE tested against a tuned threshold on one credit dataset |
| Scaling and clustering | note | [unsupervised learning](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md) | Scalers, k-means, silhouette |
| Ranking metrics | notes | [RAG evaluation](../../../../generative-ai/08-eval/notes/07-evaluating-rag-and-grounding.md), [recommenders](../../../../data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation.md) | MRR and NDCG |
| Monitoring | note | [drift](../../../../data-engineering/06-ml-platform/notes/04-drift.md) | Tests, false alarms, retraining policy |
| Explanations | note | [interpretability](../../../../data-science/01-classical-ml/notes/08-model-interpretability.md) | Permutation importance, SHAP, LIME |
| Deep learning | notes | [deep learning pillar](../../../../data-science/02-deep-learning/README.md) | Networks, optimisation, CNNs, sequence models |

## Test yourself

[interview-guide.md](interview-guide.md) teaches each topic and answers
[all 18 ML Fundamentals questions](interview-guide.md#72-the-ml-fundamentals-questions). Then try the rounds:
[technical-questions](../../rounds/technical-questions/README.md),
[coding-challenge](../../rounds/coding-challenge/README.md) (SQL screens) and
[case-study](../../rounds/case-study/README.md) (ML cases).
