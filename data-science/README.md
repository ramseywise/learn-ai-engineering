# Data Science

> What a data scientist has to know beyond the analyst: fit, evaluate and explain a model, know the classical and neural families, and know what a text or an embedding is to a model.
>
> Position: [data analytics](../data-analytics/README.md) comes first, for statistics, inference and Bayes. [Generative AI](../generative-ai/README.md) builds on this subject, from [LLM fundamentals](../generative-ai/01-llm-fundamentals/README.md) onward. The sequenced path and prerequisites are in [CURRICULUM.md](CURRICULUM.md), and the shared library is in [references.md](references.md). Interview guide: [Pillar 1, Foundations](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/1-foundations/00-overview.md).

## What it adds to the analyst

An analyst describes what happened and tests whether a difference is real. A data scientist has to predict what comes next, on rows nobody has seen, and be able to say whether that prediction holds. That job asks for three things on top of the analyst's statistics:

- **A way to fit, evaluate and explain a model**, so that a score means something: the train/test contract, leakage, metrics that match the cost of an error, and explanations you can check.
- **The classical and neural families**, with a reason to pick one: boosting on tables, convolutions on images, recurrence and attention on sequences, and word counts as the baseline all of them have to beat.
- **What a text or an embedding is to a model**, because a model can't read: from token counts to embeddings to a GPT you build yourself.

Running through all five pillars is one habit. Every run keeps a baseline and a control, and several results here go against the expected story: TF-IDF beats an LSTM on 5,000 reviews, and transfer learning loses to training from scratch on a small digits task.

## The five pillars

| # | Pillar | Question it answers | Notes | Deck |
|---|---|---|---|---|
| 01 | [Classical ML](01-classical-ml/README.md) | How do you fit a model on a table, measure it honestly, and explain it? | 8 | [pptx](01-classical-ml/slides/classical-ml.pptx) |
| 02 | [Deep learning](02-deep-learning/README.md) | How do you train a network, debug it, and match the architecture to the data? | 6 | [pptx](02-deep-learning/slides/deep-learning.pptx) |
| 03 | [NLP](03-nlp/README.md) | How does text become numbers, and what does that choice decide? | 7 | [pptx](03-nlp/slides/nlp.pptx) |
| 04 | [LLMs from scratch](04-llms-from-scratch/README.md) | What is inside a GPT, line by line? | 3 | See the pillar README |
| 05 | [Time series and recommenders](05-time-series-and-recommenders/README.md) | What changes when rows aren't exchangeable? | 3 | [pptx](05-time-series-and-recommenders/slides/time-series-and-recommenders.pptx) |

## Start here

1. [Statistical foundations](01-classical-ml/notes/01-statistical-foundations.md) for the vocabulary: generalisation, bias and variance, the train/test contract.
2. [Supervised learning](01-classical-ml/notes/02-supervised-learning.md), then [Model evaluation](01-classical-ml/notes/04-model-evaluation.md). Leakage and metric choice are the most common interview failures.
3. [Neural network fundamentals](02-deep-learning/notes/01-neural-networks-fundamentals.md) or [micrograd](04-llms-from-scratch/notes/01-micrograd.md), for backprop you can write from memory.
4. Then follow [CURRICULUM.md](CURRICULUM.md).

## Layout

```text
data-science/
├── README.md, CURRICULUM.md, references.md
├── 01-classical-ml/                  notes 01-08, deck
│   └── practice/                     boosting-comparison/, intro-to-ml-in-python/,
│                                     ng-machine-learning/, udacity_mlnd_python_practice.ipynb
├── 02-deep-learning/                 notes 01-06, deck
│   └── practice/                     ng-deep-learning/ (five courses),
│                                     deep-learning-starter-simple-lstm.ipynb
├── 03-nlp/                           notes 01-07, deck
│   └── practice/                     intro-to-nlp/, text-analytics-with-python/,
│                                     approaching-almost-any-nlp-problem-on-kaggle.ipynb
├── 04-llms-from-scratch/             notes 01-03
│   └── practice/                     nn-zero-to-hero/
├── 05-time-series-and-recommenders/  notes 01-03, deck
│   └── practice/                     forecast, collaborative-filtering and two-tower labs
└── sources/                          book PDFs, papers, images/
```

Each pillar has a README with its reading order, a `references.md` that maps its papers to its notes, and a `slides/` folder with the deck source.

## Rules of thumb

| Rule | Where |
|---|---|
| Fit every preprocessing step inside the CV loop, since a scaler fitted on all the data leaks | [Features and pipelines](01-classical-ml/notes/03-feature-engineering-and-pipelines.md), [evaluation](01-classical-ml/notes/04-model-evaluation.md) |
| Compare every score against a dummy baseline before reading it as good | [Evaluation](01-classical-ml/notes/04-model-evaluation.md) |
| Choose the metric from the business cost, and pick the threshold separately from the model | [Evaluation](01-classical-ml/notes/04-model-evaluation.md) |
| High train and low test scores mean variance, so add data or regularise. Both low means bias, so add capacity | [Foundations](01-classical-ml/notes/01-statistical-foundations.md), [projects](02-deep-learning/notes/03-structuring-ml-projects.md) |
| On tabular data, try gradient boosting before a neural net | [Ensembles](01-classical-ml/notes/06-ensembles.md), [boosting in practice](01-classical-ml/notes/07-boosting-in-practice.md) |
| Scale features for kNN, SVMs, PCA and gradient descent, as trees don't care | [Supervised](01-classical-ml/notes/02-supervised-learning.md), [unsupervised](01-classical-ml/notes/05-unsupervised-learning.md) |
| Sweep the learning rate by factors of ten before anything else, and use AdamW rather than L2 in Adam | [Optimisation](02-deep-learning/notes/02-optimisation-and-regularisation.md) |
| Find the largest gap between human, train, train-dev, dev and test, then fix that one | [Projects](02-deep-learning/notes/03-structuring-ml-projects.md) |
| On text, a TF-IDF and logistic regression baseline is hard to beat, so run it first | [Text classification](03-nlp/notes/02-text-classification.md), [neural text](02-deep-learning/notes/06-neural-text-models.md) |
| Check the loss at initialisation: it should be close to −log(1/vocab), not far above | [makemore](04-llms-from-scratch/notes/02-makemore.md) |
| Gradient-check backprop against finite differences once, then switch it off | [Fundamentals](02-deep-learning/notes/01-neural-networks-fundamentals.md), [micrograd](04-llms-from-scratch/notes/01-micrograd.md) |
| When rows have an order, split by time and beat the naive forecast first | [Time series](05-time-series-and-recommenders/notes/01-time-series-ml.md) |

## Coursework and practice

Don't run these in bulk. Each pillar README and each note's Practice section say what a notebook needs.

| Folder | Pillar | Runs |
|---|---|---|
| [`boosting-comparison/`](01-classical-ml/practice/boosting-comparison/README.md) | 01 | Offline, a few minutes |
| [`intro-to-ml-in-python/`](01-classical-ml/practice/intro-to-ml-in-python) | 01 | Offline. Needs scikit-learn 1.4 or later, `mglearn` (bundled) and graphviz. Notebook 07 needs the aclImdb download |
| [`ng-machine-learning/`](01-classical-ml/practice/ng-machine-learning) | 01 | Offline, NumPy and SciPy with bundled `.mat` data |
| [`udacity_mlnd_python_practice.ipynb`](01-classical-ml/practice/udacity_mlnd_python_practice.ipynb) | 01 | Offline, needs `data/iris.txt` (not in repo) |
| [`ng-deep-learning/`](02-deep-learning/practice/ng-deep-learning) | 02 | Legacy: TF 1.x through `tf.compat.v1`, two notebooks still need `tf.contrib`, some need course helper files and weights. Note 01 has a table for rewriting them in PyTorch |
| [`deep-learning-starter-simple-lstm.ipynb`](02-deep-learning/practice/deep-learning-starter-simple-lstm.ipynb) | 02 | GPU recommended, needs Kaggle Ventilator Pressure data |
| [`intro-to-nlp/`](03-nlp/practice/intro-to-nlp) | 03 | Data is git-ignored. [Download instructions](03-nlp/README.md#intro-to-nlp-datasets) are in the NLP README. Start Jupyter inside the folder |
| [`text-analytics-with-python/`](03-nlp/practice/text-analytics-with-python) | 03 | Partly legacy: spaCy 2, standalone Keras, gensim 3, `skater`, TF 2.15 or earlier for Ch10a. Ch09 and Ch10 need `movie_reviews.csv` (not in repo) |
| [`approaching-almost-any-nlp-problem-on-kaggle.ipynb`](03-nlp/practice/approaching-almost-any-nlp-problem-on-kaggle.ipynb) | 03 | Legacy, needs Kaggle spooky-author data and GloVe |
| [`nn-zero-to-hero/`](04-llms-from-scratch/practice/nn-zero-to-hero) | 04 | micrograd is offline. makemore needs `names.txt` (not in repo). nanoGPT's `bigram.py` runs on CPU, `gpt.py` on a GPU, and `build-nanogpt` needs 8 GPUs and FineWeb-Edu |
| [`05-time-series-and-recommenders/practice/`](05-time-series-and-recommenders/practice/README.md) | 05 | See its README |

## Related

- [Bayesian modelling](../data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc.md) lives in data analytics, and [building knowledge graphs with LLMs](../ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms.md) succeeds the NER in NLP note 05.
- Interview notes: sisyphus `interviewing/notes/foundations.md`, with the guide [1-foundations](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/1-foundations/00-overview.md).

**Previous subject:** [data analytics](../data-analytics/README.md) · **Next subject:** [generative AI](../generative-ai/README.md)
