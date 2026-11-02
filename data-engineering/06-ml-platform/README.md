# 06 ML platform

**What.** The machinery around a model: features that mean the same thing in training and serving, a record of every run, a registry that names what is live, three ways to serve, drift monitoring, and the engineering that lets a team do all of this without a hero.

**Why.** A model trusts its inputs without question and keeps answering when they are wrong. Most of what breaks in production ML breaks around the model and not in it, and it usually breaks silently, so each of these pieces exists to make a silent failure visible or reversible.

**The story.** One model that predicts taxi trip duration goes from a notebook to a monitored service. Its first offline score, 2.79, is a lie: a leaky join makes production come in at 5.48, and a point-in-time join with one shared feature function brings both to 3.81. Then we track runs, register versions and let a gate reject a retrain that is newer but worse, and roll back in one line. Serving asks when the answer is needed, and shows the model is the cheapest part of a request. Drift monitoring first cries wolf, firing every day on healthy data, then misses a doubled error because the inputs never moved. Finally the maturity model and the ML Test Score ask how much of this a given team should automate.

## Reading order

| # | Chapter | Question it answers |
|---|---|---|
| 1 | [Feature stores](notes/01-feature-stores.md) | How do you compute a feature as it was then, and identically in training and serving? |
| 2 | [Experiment tracking and the model registry](notes/02-experiment-tracking-and-model-registry.md) | Which run made this model, and what happens when its replacement is worse? |
| 3 | [Batch and online serving](notes/03-batch-and-online-serving.md) | When is the answer needed, and how do you roll out a new version safely? |
| 4 | [Drift](notes/04-drift.md) | How do you know the world moved, and when does that matter? |
| 5 | [The MLOps maturity model and best practices](notes/05-mlops-maturity-and-best-practices.md) | How much should you automate, and how do you test it? |

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DA 06/02 Credit scoring](../../data-analytics/06-applied-analyses/notes/02-credit-scoring.md) | PSI on a model's scores |
| [DS 01/10 Imbalance, errors and drift](../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md) | Simulated shifts on a credit model |

**Feeds into**

| Chapter | Why |
|---|---|
| [AIE 07/06 Serving at scale](../../ai-engineering/07-inference-engineering/notes/06-serving-at-scale.md) | Deployment shapes, rollout and the registry |

## Rules of thumb

- Join features as of the prediction time. Random splits and plain joins flatter the model.
- One function computes a feature everywhere, or training and serving will drift apart.
- A feature store is optional at first. Reach for one when several models share features or you need online lookups.
- Log what you need to rerun a model: code version, data version, parameters and metrics.
- Newer is not better. A retrain goes through a gate on a current holdout.
- Point services at an alias, so that rollback is one registry call.
- Default to batch. Go online only when someone is waiting.
- Return the model version with every prediction.
- On a drift alert, check for a pipeline fault before retraining.
- Report a magnitude alongside a p-value, and calibrate thresholds on your own quiet windows.
- Inputs that do not move prove nothing. Only labels show concept drift.
- Start with scheduled retraining, and add triggers only with good monitoring.
- Score maturity by the weakest section, and aim for level 2 to 3 before level 4.

## Deck and practice

- **Deck:** [slides/ml-platform.pptx](slides/ml-platform.pptx). Build with `make slides PILLAR=data-engineering/06-ml-platform STRICT=1 PREVIEW=1`.
- **Practice:** [practice/datatalks-mlops](practice/datatalks-mlops) is the MLOps Zoomcamp coursework, modules 01 to 07. Each module has a README. Modules 01 and 02 need Python and the taxi data. Module 03 needs an orchestrator (Prefect, or the folder's own instructions). Module 04's `web-service` needs Docker; `web-service-mlflow`, `streaming` and `batch` need AWS for the real thing. Module 05 needs Docker for its Postgres and Grafana stack. Module 06's unit tests run offline with `pipenv install --dev && pytest tests/`; its integration test needs Docker but no AWS account; its Terraform needs AWS.
- **Chapter code:** every block without an `# illustrative` label runs locally on synthetic data. Each chapter gives its `uv run --with ...` line. No cloud account is required.

[References](references.md)
