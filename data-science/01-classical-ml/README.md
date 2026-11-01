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
| 6 | [Ensembles](notes/06-ensembles.md) | Why do many trees beat one? |
| 7 | [Boosting in practice](notes/07-boosting-in-practice.md) | Which library, and which knobs? |
| 8 | [Model interpretability](notes/08-model-interpretability.md) | What did the model learn, and why this answer for this row? |

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

## Practice

| Folder | What | How to run |
|---|---|---|
| [`practice/boosting-comparison/`](practice/boosting-comparison/) | Four boosting libraries on adult census across five seeds | See its [README](practice/boosting-comparison/README.md); a few minutes |
| [`practice/intro-to-ml-in-python/`](practice/intro-to-ml-in-python/) | Müller and Guido's notebooks, with local `mglearn` and data | `uv run --with scikit-learn --with pandas --with matplotlib --with jupyter jupyter lab`, from that folder |
| [`practice/ng-machine-learning/`](practice/ng-machine-learning/) | Own Python ports of Ng's ex1 to ex8 | Same command, from that folder |
| [`practice/udacity_mlnd_python_practice.ipynb`](practice/udacity_mlnd_python_practice.ipynb) | Python and data-handling warm-up | Same command |

## Deck

```bash
make slides PILLAR=data-science/01-classical-ml STRICT=1 PREVIEW=1
```

Next pillar: [Deep learning](../02-deep-learning/README.md).
