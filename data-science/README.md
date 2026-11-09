# Data Science

> What a data scientist has to know beyond the analyst: fit, evaluate and explain a model, know the classical and neural families, and know what a text or an embedding is to a model.
>
> Position: [Generative AI](../generative-ai/README.md) builds on this subject, from [LLM fundamentals](../generative-ai/01-llm-fundamentals/README.md) onward.

## Builds on

| Chapter | Why |
|---|---|
| [Data analytics](../data-analytics/README.md) | Comes first, for statistics, inference and Bayes |
| [DA 02/04 Estimation](../data-analytics/02-probability-and-statistics/notes/04-estimation.md) and [02/05 Hypothesis testing](../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md) | Intervals on a test score; comparing many models is many tests |
| [DA 02/06 Regression and GLMs](../data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md) | The same regressions, read for inference there and for prediction here |
| [DA 02/07 The data generating process](../data-analytics/02-probability-and-statistics/notes/07-data-generating-process.md) | "A model is an estimate of f", in the analyst's terms |
| [DA 03/04 Correlation and causation](../data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation.md) and [03/05 Matching and weighting](../data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting.md) | A feature's importance is not its causal effect |
| [DA 04/01 Bayesian inference](../data-analytics/04-bayesian-analysis/notes/01-bayesian-inference.md) and [04/07 Multilevel models](../data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling.md) | The vocabulary for topic models, and partial pooling for small slices and segments |
| [DA 06 Applied analyses](../data-analytics/06-applied-analyses/README.md) | RFM, forecasting and credit scoring: what the models here are for |

## What it adds to the analyst

An analyst describes what happened and tests whether a difference is real. A data scientist has to predict what comes next, on rows nobody has seen, and be able to say whether that prediction holds. That job asks for three things on top of the analyst's statistics:

- **A way to fit, evaluate and explain a model**, so that a score means something: the train/test contract, leakage, metrics that match the cost of an error, and explanations you can check.
- **The classical and neural families**, with a reason to pick one: boosting on tables, convolutions on images, recurrence and attention on sequences, and word counts as the baseline all of them have to beat.
- **What a text or an embedding is to a model**, because a model can't read: from token counts to embeddings to a GPT you build yourself.

Running through all the pillars is one habit. Every run keeps a baseline and a control, and several results here go against the expected story: TF-IDF beats an LSTM on 5,000 reviews, and transfer learning loses to training from scratch on a small digits task.
## Course outcomes

By the end of this course, you will be able to:

1. Frame a prediction problem, construct a valid split, and establish a baseline that later models must beat.
2. Train, tune, evaluate, and explain classical models for tabular data without leakage or misleading metrics.
3. Build and debug neural networks, selecting architectures and interventions from measured failure modes.
4. Represent text as features, compare sparse and learned representations, and evaluate NLP systems honestly.
5. Forecast time-dependent data and build recommender systems using evaluation that respects time, ranking, and logged-policy bias.
6. Communicate model performance, uncertainty, error costs, and operational limitations to a decision-maker.

## Before you begin

**Required:** [Data Analytics](../data-analytics/README.md), especially probability, estimation, hypothesis testing, regression, experimentation, and the practice of working safely with data frames. You also need Python and NumPy fluency from [Programming: Python](../programming/python/README.md).

**Needed for some units:** calculus through the chain rule and matrix products for neural-network fundamentals. Bayesian modelling remains in [Data Analytics](../data-analytics/04-bayesian-analysis/README.md) and is not repeated here.

**Course language:** Python. Primary libraries include scikit-learn, PyTorch, pandas, NumPy, matplotlib, and selected NLP and recommender packages. Each pillar README covers its own setup and datasets.

## How to use the course

| Activity | What you do | What it shows |
|---|---|---|
| Chapters | Read notes in the listed order and reproduce their worked examples. | You understand the method and its failure mode. |
| Deck review | Use the pillar deck for lecture recap and retrieval practice. | You can explain a model choice and its trade-off. |
| Drills | Complete each chapter's `Try it` work and error-analysis questions. | You can apply one idea in isolation. |
| Labs | Run or adapt a purpose-built experiment. | You can compare a baseline, validate a result, and diagnose failures. |
| Portfolio evidence | Save a concise model card or decision memo for each unit. | You can defend a model's intended use and limits. |

## The pillars

The course is a tree. Classical ML establishes the evaluation discipline for everything else, deep learning and NLP can then proceed in parallel, and time series and recommenders apply the same discipline where ordinary random splits fail.

| Unit | Question it answers | Focus | Recommended order |
|---|---|---|---|
| [01 Classical ML](01-classical-ml/README.md) | How do you fit a model on a table, measure it honestly, and explain it? | Trustworthy models for tables | First; required foundation |
| [02 Deep learning](02-deep-learning/README.md) | How do you train a network, debug it, and match the architecture to the data? | Train and debug representation-learning systems | After Classical ML; can run alongside NLP |
| [03 NLP](03-nlp/README.md) | How does text become numbers, and what does that choice decide? | Turn text into useful, measurable features | After Classical ML; can run alongside Deep Learning |
| [04 LLMs from scratch](../generative-ai/09-llms-from-scratch/README.md) | What is inside a GPT, line by line? | Build the neural machinery behind an LLM | Optional bridge in Generative AI after Deep Learning and neural text |
| [05 Time series and recommenders](05-time-series-and-recommenders/README.md) | What changes when rows aren't exchangeable? | Model ordered observations and ranked catalogues | After Classical ML and Deep Learning; independent of most NLP |

*Neural text models*, in Deep Learning, is the intended meeting point of Units 02 and 03. Unit 04 lives in Generative AI so it remains one coherent hands-on progression; it is included here as a bridge, not a duplicate pillar. Folder numbers are stable, so 04 is a gap: LLMs from scratch moved to [generative AI](../generative-ai/09-llms-from-scratch/README.md) on 2026-11-02.

**Start here.** Begin with [Classical ML](01-classical-ml/README.md) for the vocabulary of generalisation, bias and variance, and the train/test contract, then supervised learning and model evaluation, since leakage and metric choice are the most common interview failures. For backprop you can write from memory, go on to [Deep learning](02-deep-learning/README.md) or [LLMs from scratch](../generative-ai/09-llms-from-scratch/README.md).

Each pillar has a README with its reading order, a `references.md` that maps its papers to its notes, and a `slides/` folder with the deck source.

## Units

### [01 Classical machine learning](01-classical-ml/README.md)

**Purpose:** Learn the full modelling loop for tabular data: formulate the target, avoid leakage, select a metric from error costs, compare baselines, tune responsibly, and explain the resulting model without mistaking explanation for causation.

**Learning objectives.** After this unit, you can:

1. Explain generalisation, bias, variance, and the train/validation/test contract ([James et al.](https://www.statlearning.com/)).
2. Select a supervised model family and control complexity for a tabular prediction problem ([Grinsztajn et al.](https://arxiv.org/abs/2207.08815) on why trees still lead there).
3. Build leakage-safe preprocessing and feature engineering pipelines.
4. Choose a metric and threshold that reflect the costs of false positives and false negatives, then compare against a dummy baseline.
5. Use clustering or dimensionality reduction cautiously, on numeric, categorical or [mixed columns](01-classical-ml/notes/05b-clustering-categorical-and-mixed-data.md), validate the result, and avoid treating visual structure as proof.
6. Compare ensembles and boosting libraries across seeds, tune with cross-validation and early stopping, and report uncertainty in a claimed improvement.
7. Use permutation importance, PDPs, and SHAP appropriately while distinguishing model explanations from causal claims.
8. Diagnose imbalance, recurring errors, and distribution shift before deploying a model.
9. Start from the target to pick the family, loss, metric and baseline ([Choosing a metric](01-classical-ml/notes/11-choosing-a-metric.md)).
10. Read false positives and false negatives before tuning, and fix a class of error on one split while scoring on another ([Reading the errors](01-classical-ml/notes/12-reading-the-errors.md)).
11. Split predictions into automate, review and reject, pricing the thresholds from error costs and review time ([Automate, review or reject](01-classical-ml/notes/13-automate-review-or-reject.md)).
12. Learn from corrections without trusting silence: measure label noise, test active learning against random, and audit a random sample ([Learning from corrections](01-classical-ml/notes/14-learning-from-corrections.md)).
13. Measure group gaps in a screening model, say which of them cannot be closed together, and state what an audit must report ([Fairness in automated scoring](01-classical-ml/notes/15-fairness-in-automated-scoring.md)).
14. Detect anomalies with a density model, a classifier or an isolation forest, and fit a matrix-factorisation recommender on a ratings matrix ([Unsupervised learning](01-classical-ml/notes/05-unsupervised-learning.md#anomaly-detection-ng-ex8-part-1); [DS 05](05-time-series-and-recommenders/README.md) takes recommenders further).

**Review and practice:** [deck](01-classical-ml/slides/classical-ml.pptx) · chapter exercises · [boosting comparison](01-classical-ml/practice/boosting-comparison/README.md) · [credit-default lab](01-classical-ml/practice/credit-default-lab/README.md) · [music-clustering lab](01-classical-ml/practice/music-clustering-lab/README.md).

**Mastery lab:** Build a leakage-safe prediction pipeline for a tabular decision. Compare a dummy, linear model, and boosted-tree model across appropriate splits; inspect the errors; select a threshold from costs; and explain the result with a checked explanation method.

**Evidence:** A concise model card with target and unit, split rationale, baselines, metric and threshold rationale, cross-validation or seed variation, error slices, explanation, limitations, and the condition that would stop deployment.

**Key sources:** James et al., [*An Introduction to Statistical Learning*](https://www.statlearning.com/) · Müller and Guido, *Introduction to Machine Learning with Python* · [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html) · Grinsztajn et al., [*Why do tree-based models still outperform deep learning on tabular data?*](https://arxiv.org/abs/2207.08815).

### [02 Deep learning](02-deep-learning/README.md)

**Purpose:** Train a neural network deliberately, locate the source of failure when it does not learn, and match an architecture to the structure of image, sequence, and text data.

**Learning objectives.** After this unit, you can:

1. Derive a forward pass and backpropagation for a small network, then validate gradients and initial loss ([Goodfellow et al.](https://www.deeplearningbook.org/)).
2. Diagnose optimisation and generalisation problems using activations, learning curves, learning-rate sweeps, regularisation, and clean validation data.
3. Use gap analysis to choose the intervention with the largest plausible gain.
4. Explain why convolutions, residual connections, and data augmentation suit image tasks ([He et al.](https://arxiv.org/abs/1512.03385)), and choose between training from scratch, a frozen pretrained backbone and fine-tuning from a measured comparison on your own data size ([note 04b](02-deep-learning/notes/04b-vision-in-practice.md)).
5. Build and diagnose sequence models, including recurrent networks, attention and [transformer encoders](02-deep-learning/notes/05b-transformer-encoders.md), for ordered inputs ([Vaswani et al.](https://arxiv.org/abs/1706.03762)).
6. Compare TF-IDF, frozen encoders, and fine-tuned text models against the same held-out baseline.

**Review and practice:** [deck](02-deep-learning/slides/deep-learning.pptx) · runnable chapter examples in PyTorch · optional historical [Ng coursework](02-deep-learning/practice/ng-deep-learning/) for comparison.

**Mastery lab:** Train a small neural model with a linear or from-scratch control. Diagnose one deliberate failure (such as poor initialisation, train/eval mode, or learning rate), correct it, and justify the next experiment from the measurements.

**Evidence:** A training report containing the control, data split, learning curves, initialisation and optimiser choices, error analysis, final metric, and an explanation of why the chosen architecture fits the data.

**Key sources:** Goodfellow, Bengio, and Courville, [*Deep Learning*](https://www.deeplearningbook.org/) · [PyTorch tutorials](https://pytorch.org/tutorials/) · He et al., [*Deep Residual Learning*](https://arxiv.org/abs/1512.03385) · Vaswani et al., [*Attention Is All You Need*](https://arxiv.org/abs/1706.03762).

### [03 Natural language processing](03-nlp/README.md)

**Purpose:** Make text measurable. Establish the sparse baseline first, then learn when embeddings, pretrained encoders, and sequence methods earn their added complexity.

**Learning objectives.** After this unit, you can:

1. Choose and justify a text representation, including tokenisation, normalisation, bag-of-words, TF-IDF, and embeddings ([Jurafsky and Martin](https://web.stanford.edu/~jurafsky/slp3/)).
2. Train and assess a text classifier against a TF-IDF linear baseline using leakage-safe evaluation.
3. Explore an unlabelled corpus with topics or summaries while validating interpretations against source documents.
4. Use word and sentence embeddings for similarity, retrieval-style ranking, classification, clustering, and anomaly detection ([Mikolov et al.](https://arxiv.org/abs/1301.3781); [Reimers and Gurevych](https://arxiv.org/abs/1908.10084)).
5. Evaluate semantic analysis, NER, and sentiment systems with the correct unit and metric.
6. Compare a pretrained encoder with sparse features while accounting for label quantity, compute cost, and result variation.

**Review and practice:** [deck](03-nlp/slides/nlp.pptx) · reproducible [note runner](03-nlp/practice/run_note.py) · chapter drills. Older course folders remain optional reference material rather than required labs.

**Mastery lab:** Choose a labelled text problem and compare a TF-IDF linear model with a pretrained-embedding approach. Include a split-safe vectorisation pipeline, macro-F1 or another justified metric, sample error review, cost/latency trade-off, and a recommendation.

**Evidence:** A short text-model report with representation rationale, baseline and candidate comparison, variance or interval where appropriate, confusion/error examples, and a documented limitation.

**Key sources:** Jurafsky and Martin, [*Speech and Language Processing*](https://web.stanford.edu/~jurafsky/slp3/) · [scikit-learn text-feature guide](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction) · Mikolov et al., [*Efficient Estimation of Word Representations*](https://arxiv.org/abs/1301.3781) · Reimers and Gurevych, [*Sentence-BERT*](https://arxiv.org/abs/1908.10084).

### [04 LLMs from scratch: a bridge to generative AI](../generative-ai/09-llms-from-scratch/README.md)

**Purpose:** Build the neural machinery behind a language model once, so later generative-AI abstractions remain inspectable ([Karpathy](https://karpathy.ai/zero-to-hero.html)). This sequence is hosted in Generative AI to keep its code and prerequisites together.

**Learning objectives.** After this bridge, you can:

1. Implement automatic differentiation and backpropagation in a minimal scalar engine.
2. Train a character-level language model and diagnose its loss, embeddings, activations, and optimisation behaviour.
3. Build and train a small GPT, explaining the relationship between attention, logits, sampling, and generation.

**Learning:** the [LLMs from scratch](../generative-ai/09-llms-from-scratch/README.md) pillar and its [practice](../generative-ai/09-llms-from-scratch/practice/nn-zero-to-hero/README.md).

**Evidence:** A short implementation note that validates gradients, explains the expected initial loss, and shows a small generative model improving against a baseline.

**Key source:** Karpathy, [*Neural Networks: Zero to Hero*](https://karpathy.ai/zero-to-hero.html).

### [05 Time series and recommenders](05-time-series-and-recommenders/README.md)

**Purpose:** Handle two cases where rows are not exchangeable: predicting the future and ranking a catalogue for a person. In both, evaluation design is the primary technical skill.

**Learning objectives.** After this unit, you can:

1. Define an issue time, forecast horizon, and legal information set, then evaluate forecasts with rolling backtests ([Hyndman and Athanasopoulos](https://otexts.com/fpp3/)).
2. Compare feature-based and sequence forecasting models against an appropriate naive baseline without temporal leakage.
3. Build collaborative-filtering and factorisation recommenders and evaluate ranking rather than only rating error ([Koren et al.](https://doi.org/10.1109/MC.2009.263)).
4. Explain how two-tower retrieval handles large catalogues and cold-start content features.
5. Design offline and online evaluation for ranking systems, including sampled-negative, exposure-bias, and counterfactual-evaluation pitfalls ([Dacrema et al.](https://arxiv.org/abs/1907.06902)).
6. Match records with no shared key by blocking, scoring and ranking candidates, train pointwise, pairwise and listwise rankers, and score a match by whole records with room to abstain ([Fellegi and Sunter](https://www.irs.gov/pub/irs-soi/1985preprintar28.pdf); [Burges](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/MSR-TR-2010-82.pdf)).
7. Decide when an encoder is worth tuning, build training pairs from match labels without leaking matches, and measure what hard-negative mining changes ([Musgrave et al.](https://arxiv.org/abs/2003.08505); [Huang et al.](https://arxiv.org/abs/2006.11632)).

**Review and practice:** [deck](05-time-series-and-recommenders/slides/time-series-and-recommenders.pptx) · labs in [practice](05-time-series-and-recommenders/practice/README.md) · [customer-segments lab](05-time-series-and-recommenders/practice/customer-segments-lab/README.md) · [matching lab](05-time-series-and-recommenders/practice/04_matching_lab.py) · [similarity lab](05-time-series-and-recommenders/practice/05_similarity_lab.py).

**Mastery lab:** Complete either a rolling-origin demand forecast or a recommendation-ranking comparison. State the information boundary, include the naive or popularity baseline, show the correct evaluation metric, inspect failure cases, and convert the model choice into an operational decision.

**Evidence:** A reproducible notebook or script with temporal or interaction split, baseline comparison, metric rationale, leakage audit, result limitations, and a plan for the online test required before rollout.

**Key sources:** Hyndman and Athanasopoulos, [*Forecasting: Principles and Practice*](https://otexts.com/fpp3/) · Koren, Bell, and Volinsky, [*Matrix Factorization Techniques for Recommender Systems*](https://doi.org/10.1109/MC.2009.263) · Rendle et al., [*BPR*](https://arxiv.org/abs/1205.2618) · Dacrema et al., [*Are We Really Making Much Progress?*](https://arxiv.org/abs/1907.06902).

## Rules of thumb

| Rule | Where |
|---|---|
| Fit every preprocessing step inside the CV loop, since a scaler fitted on all the data leaks | [Features and pipelines](01-classical-ml/notes/03-feature-engineering-and-pipelines.md), [evaluation](01-classical-ml/notes/04-model-evaluation.md) |
| Compare every score against a dummy baseline before reading it as good | [Evaluation](01-classical-ml/notes/04-model-evaluation.md) |
| Choose the metric from the business cost, and pick the threshold separately from the model | [Evaluation](01-classical-ml/notes/04-model-evaluation.md), [thresholds](01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration.md) |
| High train and low test scores mean variance, so add data or regularise. Both low means bias, so add capacity | [Foundations](01-classical-ml/notes/01-statistical-foundations.md), [projects](02-deep-learning/notes/03-structuring-ml-projects.md) |
| On tabular data, try gradient boosting before a neural net | [Ensembles](01-classical-ml/notes/06-ensembles.md), [boosting in practice](01-classical-ml/notes/07-boosting-in-practice.md) |
| Scale features for kNN, SVMs, PCA and gradient descent, as trees don't care | [Supervised](01-classical-ml/notes/02-supervised-learning.md), [unsupervised](01-classical-ml/notes/05-unsupervised-learning.md) |
| Sweep the learning rate by factors of ten before anything else, and use AdamW rather than L2 in Adam | [Optimisation](02-deep-learning/notes/02-optimisation-and-regularisation.md) |
| Find the largest gap between human, train, train-dev, dev and test, then fix that one | [Projects](02-deep-learning/notes/03-structuring-ml-projects.md) |
| On text, a TF-IDF and logistic regression baseline is hard to beat, so run it first | [Text classification](03-nlp/notes/02-text-classification.md), [neural text](02-deep-learning/notes/06-neural-text-models.md) |
| Check the loss at initialisation: it should be close to −log(1/vocab), not far above | [makemore](../generative-ai/09-llms-from-scratch/notes/02-makemore.md) |
| Gradient-check backprop against finite differences once, then switch it off | [Fundamentals](02-deep-learning/notes/01-neural-networks-fundamentals.md), [micrograd](../generative-ai/09-llms-from-scratch/notes/01-micrograd.md) |
| When rows have an order, split by time and beat the naive forecast first | [Time series](05-time-series-and-recommenders/notes/01-time-series-ml.md) |

## Coursework and practice

Don't run these in bulk. Each pillar README and each note's Practice section say what a notebook needs.

| Folder | Pillar | Runs |
|---|---|---|
| [`boosting-comparison/`](01-classical-ml/practice/boosting-comparison/README.md) | 01 | Offline, a few minutes |
| [`credit-default-lab/`](01-classical-ml/practice/credit-default-lab/README.md) | 01 | Fetches its data from UCI once, about four minutes |
| [`music-clustering-lab/`](01-classical-ml/practice/music-clustering-lab/README.md) | 01 | Fetches its feature file once, about a minute |
| [`intro-to-ml-in-python/`](01-classical-ml/practice/intro-to-ml-in-python) | 01 | Offline. Needs scikit-learn 1.4 or later, `mglearn` (bundled) and graphviz. Notebook 07 needs the aclImdb download |
| [`ng-machine-learning/`](01-classical-ml/practice/ng-machine-learning) | 01 | Offline, NumPy and SciPy with bundled `.mat` data |
| [`udacity_mlnd_python_practice.ipynb`](01-classical-ml/practice/udacity_mlnd_python_practice.ipynb) | 01 | Offline, needs `data/iris.txt` (not in repo) |
| [`ng-deep-learning/`](02-deep-learning/practice/ng-deep-learning) | 02 | Legacy: TF 1.x through `tf.compat.v1`, two notebooks still need `tf.contrib`, some need course helper files and weights. Note 01 has a table for rewriting them in PyTorch |
| [`deep-learning-starter-simple-lstm.ipynb`](02-deep-learning/practice/deep-learning-starter-simple-lstm.ipynb) | 02 | GPU recommended, needs Kaggle Ventilator Pressure data |
| [`intro-to-nlp/`](03-nlp/practice/intro-to-nlp) | 03 | Data is git-ignored. [Download instructions](03-nlp/README.md#intro-to-nlp-datasets) are in the NLP README. Start Jupyter inside the folder |
| [`text-analytics-with-python/`](03-nlp/practice/text-analytics-with-python) | 03 | Partly legacy: spaCy 2, standalone Keras, gensim 3, `skater`, TF 2.15 or earlier for Ch10a. Ch09 and Ch10 need `movie_reviews.csv` (not in repo) |
| [`approaching-almost-any-nlp-problem-on-kaggle.ipynb`](03-nlp/practice/approaching-almost-any-nlp-problem-on-kaggle.ipynb) | 03 | Legacy, needs Kaggle spooky-author data and GloVe |
| [`nn-zero-to-hero/`](../generative-ai/09-llms-from-scratch/practice/nn-zero-to-hero) | GA 09 | micrograd is offline. makemore needs `names.txt` (not in repo). nanoGPT's `bigram.py` runs on CPU, `gpt.py` on a GPU, and `build-nanogpt` needs 8 GPUs and FineWeb-Edu |
| [`05-time-series-and-recommenders/practice/`](05-time-series-and-recommenders/practice/README.md) | 05 | See its README |
| [`customer-segments-lab/`](05-time-series-and-recommenders/practice/customer-segments-lab/README.md) | 05 | Offline and synthetic, one to four minutes |

## Known gaps

- [Statistical foundations](01-classical-ml/notes/01-statistical-foundations.md) has no coursework of its own. Its practice is in the chapter's Try it section, with ISLP ch. 2 and *Statistics Done Wrong* as readings.
- The Ng deep learning notebooks remain as they were submitted, in NumPy and TF 1.x. Note 01 has the table for reproducing them in PyTorch, but no PyTorch copies of the notebooks exist in the repo.

## Related

[Bayesian modelling](../data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc.md) lives in data analytics, and [building knowledge graphs with LLMs](../ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms.md) succeeds the NER in NLP note 05.

## Completion standard and next steps

You have completed this course when your portfolio includes: a documented tabular-model comparison, a neural-training diagnosis, a text-model comparison, and either a time-series or recommender evaluation. Each artifact should identify its unit, split, baseline, metric, errors, limitations, and deployment or experiment decision.

Continue to [Generative AI](../generative-ai/README.md) for LLMs, retrieval, agents, and evaluation; to [Data Engineering](../data-engineering/README.md) for production data and ML infrastructure; or to [AI Engineering](../ai-engineering/README.md) for reliable LLM systems.

**Previous subject:** [data analytics](../data-analytics/README.md) · **Next subject:** [generative AI](../generative-ai/README.md)

## Primary texts

- Müller and Guido, *Introduction to Machine Learning with Python*: the practical spine of Unit 01
- James et al., *An Introduction to Statistical Learning with Applications in Python*: the statistical reasoning behind Unit 01
- Ng, *Machine Learning Yearning*: error analysis and structuring projects, Units 01 and 02
- Buduma, *Fundamentals of Deep Learning*: parallel text for Unit 02
- Sarkar, *Text Analytics with Python*, 2nd ed.: the practical spine of Unit 03
- Jurafsky and Martin, *Speech and Language Processing*: depth for Unit 03
- Hyndman and Athanasopoulos, *Forecasting: Principles and Practice*: the statistical side of Unit 05
- Karpathy, *Neural Networks: Zero to Hero*: the course behind Unit 04

Everything else: [references.md](references.md). Each pillar's own `references.md` maps its sources to its chapters.
