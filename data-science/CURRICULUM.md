# Data science: course curriculum

> Learn to build, evaluate, and explain models that must work on rows they have not seen—from a tabular baseline to neural networks, text, forecasts, and ranked recommendations.

This is the learner-facing syllabus for Data Science. The course is a tree: classical ML establishes the evaluation discipline for everything else; deep learning and NLP can then proceed in parallel; time series and recommenders apply the same discipline where ordinary random splits fail. Pillar READMEs contain runnable details, and each pillar's `references.md` contains its complete source map.

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

**Course language:** Python. Primary libraries include scikit-learn, PyTorch, pandas, NumPy, matplotlib, and selected NLP and recommender packages. Setup and dataset instructions belong in the pillar READMEs.

## How to use the course

| Activity | What you do | What it shows |
|---|---|---|
| Chapters | Read notes in the listed order and reproduce their worked examples. | You understand the method and its failure mode. |
| Deck review | Use the pillar deck for lecture recap and retrieval practice. | You can explain a model choice and its trade-off. |
| Drills | Complete each chapter's `Try it` work and error-analysis questions. | You can apply one idea in isolation. |
| Labs | Run or adapt a purpose-built experiment. | You can compare a baseline, validate a result, and diagnose failures. |
| Portfolio evidence | Save a concise model card or decision memo for each unit. | You can defend a model's intended use and limits. |

## Course map and order

| Unit | Focus | Chapters | Recommended order |
|---|---|---:|---|
| [01 Classical ML](#unit-01--classical-machine-learning) | Trustworthy models for tables | 10 | First; required foundation |
| [02 Deep learning](#unit-02--deep-learning) | Train and debug representation-learning systems | 6 | After Classical ML; can run alongside NLP |
| [03 Natural language processing](#unit-03--natural-language-processing) | Turn text into useful, measurable features | 7 | After Classical ML; can run alongside Deep Learning |
| [04 LLMs from scratch](#unit-04--llms-from-scratch-bridge) | Build the neural machinery behind an LLM | 3 | Optional bridge in Generative AI after Deep Learning / neural text |
| [05 Time series and recommenders](#unit-05--time-series-and-recommenders) | Model ordered observations and ranked catalogues | 3 | After Classical ML and Deep Learning; independent of most NLP |

Deep Learning note 06, *Neural text models*, is the intended meeting point of Units 02 and 03. Unit 04 lives in Generative AI so it remains one coherent hands-on progression; it is included here as a bridge, not a duplicate pillar.

---

## Unit 01 — Classical machine learning

**Purpose:** Learn the full modelling loop for tabular data: formulate the target, avoid leakage, select a metric from error costs, compare baselines, tune responsibly, and explain the resulting model without mistaking explanation for causation.

**Learning objectives**

After this unit, you can:

1. Explain generalisation, bias, variance, and the train/validation/test contract.
2. Select a supervised model family and control complexity for a tabular prediction problem.
3. Build leakage-safe preprocessing and feature engineering pipelines.
4. Choose a metric and threshold that reflect the costs of false positives and false negatives, then compare against a dummy baseline.
5. Use clustering or dimensionality reduction cautiously, validate the result, and avoid treating visual structure as proof.
6. Compare ensembles and boosting libraries across seeds, tune with cross-validation and early stopping, and report uncertainty in a claimed improvement.
7. Use permutation importance, PDPs, and SHAP appropriately while distinguishing model explanations from causal claims.
8. Diagnose imbalance, recurring errors, and distribution shift before deploying a model.

**Chapters:** [Statistical foundations](01-classical-ml/notes/01-statistical-foundations.md) · [Supervised learning](01-classical-ml/notes/02-supervised-learning.md) · [Feature engineering and pipelines](01-classical-ml/notes/03-feature-engineering-and-pipelines.md) · [Model evaluation](01-classical-ml/notes/04-model-evaluation.md) · [Unsupervised learning](01-classical-ml/notes/05-unsupervised-learning.md) · [Ensembles](01-classical-ml/notes/06-ensembles.md) · [Boosting in practice](01-classical-ml/notes/07-boosting-in-practice.md) · [Model interpretability](01-classical-ml/notes/08-model-interpretability.md) · [Training and tuning](01-classical-ml/notes/09-training-and-tuning.md) · [Imbalance, errors and drift](01-classical-ml/notes/10-imbalance-errors-and-drift.md)

**Review and practice:** [deck](01-classical-ml/slides/classical-ml.pptx) · chapter exercises · [boosting comparison](01-classical-ml/practice/boosting-comparison/README.md) · [credit-default lab](01-classical-ml/practice/credit-default-lab/README.md) · [music-clustering lab](01-classical-ml/practice/music-clustering-lab/README.md).

**Mastery lab:** Build a leakage-safe prediction pipeline for a tabular decision. Compare a dummy, linear model, and boosted-tree model across appropriate splits; inspect the errors; select a threshold from costs; and explain the result with a checked explanation method.

**Evidence:** A concise model card with target and unit, split rationale, baselines, metric and threshold rationale, cross-validation or seed variation, error slices, explanation, limitations, and the condition that would stop deployment.

**Key sources:** James et al., [*An Introduction to Statistical Learning*](https://www.statlearning.com/) · Müller and Guido, *Introduction to Machine Learning with Python* · [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html) · Grinsztajn et al., [*Why do tree-based models still outperform deep learning on tabular data?*](https://arxiv.org/abs/2207.08815).

---

## Unit 02 — Deep learning

**Purpose:** Train a neural network deliberately, locate the source of failure when it does not learn, and match an architecture to the structure of image, sequence, and text data.

**Learning objectives**

After this unit, you can:

1. Derive a forward pass and backpropagation for a small network, then validate gradients and initial loss.
2. Diagnose optimisation and generalisation problems using activations, learning curves, learning-rate sweeps, regularisation, and clean validation data.
3. Use gap analysis to choose the intervention with the largest plausible gain.
4. Explain why convolutions, residual connections, and data augmentation suit image tasks.
5. Build and diagnose sequence models, including recurrent networks and attention, for ordered inputs.
6. Compare TF-IDF, frozen encoders, and fine-tuned text models against the same held-out baseline.

**Chapters:** [Neural network fundamentals](02-deep-learning/notes/01-neural-networks-fundamentals.md) · [Optimisation and regularisation](02-deep-learning/notes/02-optimisation-and-regularisation.md) · [Structuring ML projects](02-deep-learning/notes/03-structuring-ml-projects.md) · [Convolutional networks](02-deep-learning/notes/04-convolutional-networks.md) · [Sequence models](02-deep-learning/notes/05-sequence-models.md) · [Neural text models](02-deep-learning/notes/06-neural-text-models.md)

**Review and practice:** [deck](02-deep-learning/slides/deep-learning.pptx) · runnable chapter examples in PyTorch · optional historical [Ng coursework](02-deep-learning/practice/ng-deep-learning/) for comparison.

**Mastery lab:** Train a small neural model with a linear or from-scratch control. Diagnose one deliberate failure (such as poor initialisation, train/eval mode, or learning rate), correct it, and justify the next experiment from the measurements.

**Evidence:** A training report containing the control, data split, learning curves, initialisation and optimiser choices, error analysis, final metric, and an explanation of why the chosen architecture fits the data.

**Key sources:** Goodfellow, Bengio, and Courville, [*Deep Learning*](https://www.deeplearningbook.org/) · [PyTorch tutorials](https://pytorch.org/tutorials/) · He et al., [*Deep Residual Learning*](https://arxiv.org/abs/1512.03385) · Vaswani et al., [*Attention Is All You Need*](https://arxiv.org/abs/1706.03762).

---

## Unit 03 — Natural language processing

**Purpose:** Make text measurable. Establish the sparse baseline first, then learn when embeddings, pretrained encoders, and sequence methods earn their added complexity.

**Learning objectives**

After this unit, you can:

1. Choose and justify a text representation, including tokenisation, normalisation, bag-of-words, TF-IDF, and embeddings.
2. Train and assess a text classifier against a TF-IDF linear baseline using leakage-safe evaluation.
3. Explore an unlabelled corpus with topics or summaries while validating interpretations against source documents.
4. Use word and sentence embeddings for similarity, retrieval-style ranking, classification, clustering, and anomaly detection.
5. Evaluate semantic analysis, NER, and sentiment systems with the correct unit and metric.
6. Compare a pretrained encoder with sparse features while accounting for label quantity, compute cost, and result variation.

**Chapters:** [Text representation](03-nlp/notes/01-text-representation.md) · [Text classification](03-nlp/notes/02-text-classification.md) · [Topic models and summarisation](03-nlp/notes/03-topic-models-and-summarization.md) · [Embeddings and similarity](03-nlp/notes/04-embeddings-and-similarity.md) · [Semantic analysis and NER](03-nlp/notes/05-semantic-analysis-and-ner.md) · [Sentiment analysis](03-nlp/notes/06-sentiment-analysis.md) · [LLM embeddings as features](03-nlp/notes/07-llm-embeddings-as-features.md)

**Review and practice:** [deck](03-nlp/slides/nlp.pptx) · reproducible [note runner](03-nlp/practice/run_note.py) · chapter drills. Older course folders remain optional reference material rather than required labs.

**Mastery lab:** Choose a labelled text problem and compare a TF-IDF linear model with a pretrained-embedding approach. Include a split-safe vectorisation pipeline, macro-F1 or another justified metric, sample error review, cost/latency trade-off, and a recommendation.

**Evidence:** A short text-model report with representation rationale, baseline and candidate comparison, variance or interval where appropriate, confusion/error examples, and a documented limitation.

**Key sources:** Jurafsky and Martin, [*Speech and Language Processing*](https://web.stanford.edu/~jurafsky/slp3/) · [scikit-learn text-feature guide](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction) · Mikolov et al., [*Efficient Estimation of Word Representations*](https://arxiv.org/abs/1301.3781) · Reimers and Gurevych, [*Sentence-BERT*](https://arxiv.org/abs/1908.10084).

---

## Unit 04 — LLMs from scratch bridge

**Purpose:** Build the neural machinery behind a language model once, so later generative-AI abstractions remain inspectable. This sequence is hosted in Generative AI to keep its code and prerequisites together.

**Learning objectives**

After this bridge, you can:

1. Implement automatic differentiation and backpropagation in a minimal scalar engine.
2. Train a character-level language model and diagnose its loss, embeddings, activations, and optimisation behaviour.
3. Build and train a small GPT, explaining the relationship between attention, logits, sampling, and generation.

**Chapters and practice:** [Micrograd](../generative-ai/09-llms-from-scratch/notes/01-micrograd.md) · [makemore](../generative-ai/09-llms-from-scratch/notes/02-makemore.md) · [nanoGPT](../generative-ai/09-llms-from-scratch/notes/03-nanogpt.md) · [practice](../generative-ai/09-llms-from-scratch/practice/nn-zero-to-hero/README.md).

**Evidence:** A short implementation note that validates gradients, explains the expected initial loss, and shows a small generative model improving against a baseline.

**Key source:** Karpathy, [*Neural Networks: Zero to Hero*](https://karpathy.ai/zero-to-hero.html).

---

## Unit 05 — Time series and recommenders

**Purpose:** Handle two cases where rows are not exchangeable: predicting the future and ranking a catalogue for a person. In both, evaluation design is the primary technical skill.

**Learning objectives**

After this unit, you can:

1. Define an issue time, forecast horizon, and legal information set, then evaluate forecasts with rolling backtests.
2. Compare feature-based and sequence forecasting models against an appropriate naive baseline without temporal leakage.
3. Build collaborative-filtering and factorisation recommenders and evaluate ranking rather than only rating error.
4. Explain how two-tower retrieval handles large catalogues and cold-start content features.
5. Design offline and online evaluation for ranking systems, including sampled-negative, exposure-bias, and counterfactual-evaluation pitfalls.

**Chapters:** [Time-series ML](05-time-series-and-recommenders/notes/01-time-series-ml.md) · [Collaborative filtering and matrix factorisation](05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation.md) · [Two-tower retrieval and evaluation](05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md)

**Review and practice:** [deck](05-time-series-and-recommenders/slides/time-series-and-recommenders.pptx) · chapter labs in [practice](05-time-series-and-recommenders/practice/README.md) · [customer-segments lab](05-time-series-and-recommenders/practice/customer-segments-lab/README.md).

**Mastery lab:** Complete either a rolling-origin demand forecast or a recommendation-ranking comparison. State the information boundary, include the naive or popularity baseline, show the correct evaluation metric, inspect failure cases, and convert the model choice into an operational decision.

**Evidence:** A reproducible notebook or script with temporal or interaction split, baseline comparison, metric rationale, leakage audit, result limitations, and a plan for the online test required before rollout.

**Key sources:** Hyndman and Athanasopoulos, [*Forecasting: Principles and Practice*](https://otexts.com/fpp3/) · Koren, Bell, and Volinsky, [*Matrix Factorization Techniques for Recommender Systems*](https://doi.org/10.1109/MC.2009.263) · Rendle et al., [*BPR*](https://arxiv.org/abs/1205.2618) · Dacrema et al., [*Are We Really Making Much Progress?*](https://arxiv.org/abs/1907.06902).

---

## Completion standard and next steps

You have completed this course when your portfolio includes: a documented tabular-model comparison, a neural-training diagnosis, a text-model comparison, and either a time-series or recommender evaluation. Each artifact should identify its unit, split, baseline, metric, errors, limitations, and deployment or experiment decision.

Continue to [Generative AI](../generative-ai/README.md) for LLMs, retrieval, agents, and evaluation; to [Data Engineering](../data-engineering/README.md) for production data and ML infrastructure; or to [AI Engineering](../ai-engineering/README.md) for reliable LLM systems.

## Complete references

The chapter-level source maps are maintained in the pillar reference files:

- [01 Classical ML](01-classical-ml/references.md)
- [02 Deep learning](02-deep-learning/references.md)
- [03 NLP](03-nlp/references.md)
- [05 Time series and recommenders](05-time-series-and-recommenders/references.md)
