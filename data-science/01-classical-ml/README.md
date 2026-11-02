# 01 — Classical ML

> Fit a model on a table, measure it honestly, and explain it. Deck: [`slides/classical-ml.pptx`](slides/classical-ml.pptx) (source [`slides/deck.yaml`](slides/deck.yaml)). Practice: [`practice/`](practice/). References: [`references.md`](references.md).

## What it is

The classical machine-learning toolkit for tabular data: linear models, trees, kernels, clustering and boosting, with the practices that make their scores believable. This is where a data scientist moves beyond an analyst: an analyst describes last year, and a data scientist predicts the next one and can say whether the prediction holds.

## Why it matters

Most business data is a table. On tables of ordinary size, boosted trees remain state of the art ([Grinsztajn et al., NeurIPS 2022](https://arxiv.org/abs/2207.08815)), and the discipline learned here (splits, leakage, metrics, calibration) applies unchanged to every neural model later in the course.

## The story

You are asked whether someone will earn over $50k. A one-line split and a linear model give a number, but is it believable? So you split the data properly, wrap every fitted step in a pipeline so nothing leaks, and pick a metric from what each mistake costs. The adult census runs through the pillar: a dummy scores 0.759 accuracy, logistic regression reaches AUC 0.901, and boosting gets to about 0.93, at which point four libraries tie within noise. With no labels at all, you look for structure instead. Finally a reviewer asks why the model rejected this applicant, and you need tools that explain a model without fooling you.

## Reading order

| # | Note | Question it answers |
|---|---|---|
| 1 | [Statistical foundations](notes/01-statistical-foundations.md) | What is a model estimating, and why does it fail on new data? |
| 2 | [Supervised learning](notes/02-supervised-learning.md) | Which family first, and what controls its complexity? |
| 3 | [Feature engineering and pipelines](notes/03-feature-engineering-and-pipelines.md) | What should the model see, and how do you keep it from cheating? |
| 4 | [Model evaluation](notes/04-model-evaluation.md) | A model scored 90%. Is that good? |
| 5 | [Unsupervised learning](notes/05-unsupervised-learning.md) | What can you learn with no labels? |
| 5b | [Clustering categorical and mixed data](notes/05b-clustering-categorical-and-mixed-data.md) | How do you segment customers when the columns aren't all numbers? |
| 6 | [Ensembles](notes/06-ensembles.md) | Why do many trees beat one? |
| 7 | [Boosting in practice](notes/07-boosting-in-practice.md) | Which library, and which knobs? |
| 8 | [Model interpretability](notes/08-model-interpretability.md) | What did the model learn, and why this answer for this row? |
| 9 | [Training and tuning](notes/09-training-and-tuning.md) | How do you run the whole loop and end with a number you can defend? |
| 10 | [Imbalance, errors and drift](notes/10-imbalance-errors-and-drift.md) | What does a good score hide when the event is rare and the world moves? |
| 11 | [Choosing a metric](notes/11-choosing-a-metric.md) | Given this target and this decision, which loss, metric and baseline? |
| 12 | [Reading the errors](notes/12-reading-the-errors.md) | Which rows does the model get wrong, why, and how do you learn from them without fitting to them? |
| 13 | [Automate, review or reject](notes/13-automate-review-or-reject.md) | Which decisions may the model take alone, and what is a person's review worth? |
| 14 | [Learning from corrections](notes/14-learning-from-corrections.md) | What can people's corrections teach a model, and how do you measure what they never see? |

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DA 02/02 Probability foundations](../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md) | Conditional probability, expectation and variance |
| [DA 02/04 Estimation](../../data-analytics/02-probability-and-statistics/notes/04-estimation.md) | Bias, variance, maximum likelihood, the bootstrap and Wilson intervals |
| [DA 02/05 Hypothesis testing](../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md) | Type I and II errors and multiple comparisons |
| [DA 02/06 Regression and GLMs](../../data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md) | Inference for linear models, which scikit-learn leaves out |
| [DA 03/04 Correlation and causation](../../data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation.md) | Why a model's explanations are not causal |
| [DA 06/02 Credit scoring](../../data-analytics/06-applied-analyses/notes/02-credit-scoring.md) | The scorecard that the imbalance chapter starts from |
| [GA 08/03 Eval datasets](../../generative-ai/08-eval/notes/03-eval-datasets.md) | Harvesting failures into a test set, which note 14 measures |
| [GA 08/11 Production and the maturity ladder](../../generative-ai/08-eval/notes/11-production-and-the-maturity-ladder.md) | Sampling live traffic for review, which note 14 prices |

**Feeds into**

| Chapter | Why |
|---|---|
| [GA 02/01 RAG pipeline](../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md) | Recall and precision at k are the confusion matrix at one cut-off |
| [GA 08/15 Calibrating a judge](../../generative-ai/08-eval/notes/15-calibration-against-human-labels.md#what-to-measure) | A judge's matrix, with PASS as positive |
| [GA 08/07 Evaluating RAG and grounding](../../generative-ai/08-eval/notes/07-evaluating-rag-and-grounding.md) | The retrieval reading of the same table |
| [AIE 09/03 Guardrail models](../../ai-engineering/09-safety-and-security/notes/03-guardrail-models.md) | The guard's reading of the same table |
| [AIE 02/12 Evaluating context](../../ai-engineering/02-context-engineering/notes/12-evaluating-context.md) | Low recall and low precision as cells of the table |
| [AIE 03/05 Verification loops](../../ai-engineering/03-harness-engineering/notes/05-verification-loops.md) | A verifier that cries wolf is a false positive with a cost |
| [DE 06/04 Drift](../../data-engineering/06-ml-platform/notes/04-drift.md) | Drift monitoring in production |
| [DS 05/03 Two-tower and evaluation](../05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md) | Recall, NDCG and MRR at work on a ranking task |
| [GA 08/02 Defining correct](../../generative-ai/08-eval/notes/02-defining-correct.md) | Open coding of traces is error analysis on text |
| [GA 08/03 Eval datasets](../../generative-ai/08-eval/notes/03-eval-datasets.md) | Dev and held-out eval sets play the eyeball and blackbox roles |
| [GA 08/09 Reading results](../../generative-ai/08-eval/notes/09-reading-results.md) | Slicing and reading transcripts, with the same traps |
| [AIE 01/09 Evaluating prompts](../../ai-engineering/01-prompt-engineering/notes/09-evaluating-prompts.md) | A prompt tuned on failures it is scored on is the noise fix again |
| [GA 08/04 Graders](../../generative-ai/08-eval/notes/04-graders.md) | Abstention, seen from the grader's side |
| [GA 08/11 Production and the maturity ladder](../../generative-ai/08-eval/notes/11-production-and-the-maturity-ladder.md) | Human corrections are labelled examples only with the audit that notes 13 and 14 describe |

## Rules of thumb

- Start with a dummy, then a linear model, then boosting. Each gives a bar for the next.
- Test once. Choose on validation or cross-validation.
- Any step with a `fit` goes inside the pipeline.
- Choose the metric from what each error costs. Accuracy misleads when classes are imbalanced.
- Try a domain feature before a bigger model: on Citi Bike, hour and weekday take a forest's R² from -0.04 to 0.84.
- Compare models across seeds. A 0.001 AUC lead is noise when the seed moves it by 0.003.
- Let early stopping pick the rounds.
- Report permutation importance or SHAP, not impurity importance.
- Explanations describe the model, not the world.
- Name the target and the decision before the metric. A metric's favourite prediction is what you are asking the model for.
- Read errors on one split and score fixes on another. A fix built from noise gained 18.6 per 1,000 on the rows that chose it and lost 8.3 on the rest.
- Price the review route before building it. Thresholds come from the error costs, the review cost and how often the reviewer catches a problem, and the straight-through rate is a constraint, not a goal.
- Silence isn't confirmation. Audit a random sample of what nobody looks at, because no other number can see a new kind of failure.

## Practice

| Folder | What | How to run |
|---|---|---|
| [`practice/boosting-comparison/`](practice/boosting-comparison/) | Four boosting libraries on adult census across five seeds | See its [README](practice/boosting-comparison/README.md); a few minutes |
| [`practice/credit-default-lab/`](practice/credit-default-lab/) | Credit card default at a 3% rate: what each way of handling imbalance costs, for [note 10](notes/10-imbalance-errors-and-drift.md) | See its [README](practice/credit-default-lab/README.md); about four minutes, internet needed once |
| [`practice/music-clustering-lab/`](practice/music-clustering-lab/) | Clustering a real music library with a light reranker on top, for [note 05](notes/05-unsupervised-learning.md#case-clustering-a-music-library) | See its [README](practice/music-clustering-lab/README.md); about a minute, internet needed once |
| [`practice/isolation_forest.py`](practice/isolation_forest.py) | An isolation forest beside the Gaussian detector on ex8 and on generated tables, for [note 05](notes/05-unsupervised-learning.md#isolation-forest-on-tabular-data) | `uv run isolation_forest.py`, from `practice/`; a few seconds |
| [`practice/mixed_clustering.py`](practice/mixed_clustering.py) | FAMD, MCA, Gower with PAM, k-prototypes and latent class on generated worlds with a control, for [note 05b](notes/05b-clustering-categorical-and-mixed-data.md) | `uv run mixed_clustering.py`, from `practice/`; a few minutes |
| [`practice/metric_map.py`](practice/metric_map.py) | Metrics by target, thresholds by cost, and retrieval on one table, for [note 11](notes/11-choosing-a-metric.md) | `uv run metric_map.py`, from `practice/` |
| [`practice/reading_errors.py`](practice/reading_errors.py) | Six steps of error analysis on the credit model, and a noise fix against a mechanism fix over 30 seeds, for [note 12](notes/12-reading-the-errors.md) | `uv run reading_errors.py`, from `practice/`; under a minute |
| [`practice/review_queue.py`](practice/review_queue.py) | Two thresholds on generated invoices and real credit data: prices, capacity, calibration, drift, risk targets and conformal, for [note 13](notes/13-automate-review-or-reject.md). Shares [`invoices.py`](practice/invoices.py) | `uv run review_queue.py`, from `practice/`; about three minutes, internet needed once |
| [`practice/learning_from_corrections.py`](practice/learning_from_corrections.py) | Agreement, label noise, weak supervision, active learning, audits and regression cases, for [note 14](notes/14-learning-from-corrections.md) | `uv run learning_from_corrections.py`, from `practice/`; about 15 minutes, internet needed once |
| [`practice/intro-to-ml-in-python/`](practice/intro-to-ml-in-python/) | Müller and Guido's notebooks, with local `mglearn` and data | `uv run --with scikit-learn --with pandas --with matplotlib --with jupyter jupyter lab`, from that folder |
| [`practice/ng-machine-learning/`](practice/ng-machine-learning/) | Own Python ports of Ng's ex1 to ex8 | Same command, from that folder |
| [`practice/udacity_mlnd_python_practice.ipynb`](practice/udacity_mlnd_python_practice.ipynb) | Python and data-handling warm-up | Same command |

## Deck

```bash
make slides PILLAR=data-science/01-classical-ml STRICT=1 PREVIEW=1
```

## Primary texts

- Müller and Guido, *Introduction to Machine Learning with Python*
- James et al., *An Introduction to Statistical Learning with Applications in Python*
- Ng, *Machine Learning Yearning*
- Chen and Guestrin, *XGBoost*

Everything else: [references.md](references.md).

Next pillar: [Deep learning](../02-deep-learning/README.md).
