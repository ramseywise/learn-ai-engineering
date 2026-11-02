---
origin: curated
sources:
  - sources/
confidence: high
cleaned: 2026-11-01
---
# References: data science

> The shared library: books and courses that serve more than one pillar. Papers live in each pillar's own `references.md`: [01](01-classical-ml/references.md), [02](02-deep-learning/references.md), [03](03-nlp/references.md), [04](../generative-ai/09-llms-from-scratch/references.md), [05](05-time-series-and-recommenders/references.md). **★** = read first. Local PDFs live in [sources/](sources/) and figures in [sources/images/](sources/images/). Licence and size flags are in [Source quality](#source-quality).

## Books

| | Source | Pillars |
|---|---|---|
| ★ | Müller and Guido, *Introduction to Machine Learning with Python* (O'Reilly, 2016), [PDF](sources/mueller-guido-introduction-to-ml-with-python.pdf). Companion notebooks in [`intro-to-ml-in-python/`](01-classical-ml/practice/intro-to-ml-in-python), from [amueller/introduction_to_ml_with_python](https://github.com/amueller/introduction_to_ml_with_python), with `mglearn` | [01](01-classical-ml/references.md), [03](03-nlp/references.md) |
| ★ | Sarkar, *Text Analytics with Python*, 1st ed. (Apress, 2016, seven chapters), [PDF](sources/sarkar-text-analytics-with-python-2e.pdf), which is the 1st edition despite the `2e` in its file name. The companion notebooks in [`text-analytics-with-python/`](03-nlp/practice/text-analytics-with-python) follow the 2nd ed. (Apress, 2019, not in the repo), from [dipanjanS/text-analytics-with-python](https://github.com/dipanjanS/text-analytics-with-python), Apache-2.0 | [03](03-nlp/references.md), [02](02-deep-learning/references.md) (ch. 10) |
| | James, Witten, Hastie, Tibshirani and Taylor, *An Introduction to Statistical Learning with Applications in Python* (2023). Held in [`../data-analytics/sources/`](../data-analytics/sources/). Ch. 2 to 6 pair with 01 notes 01 to 04, ch. 8 with note 06, and ch. 12 with note 05 | [01](01-classical-ml/references.md) |
| | Bird, Klein and Loper, *Natural Language Processing with Python* (the NLTK book, online edition CC BY-NC-ND 3.0), [PDF](sources/bird-klein-loper-nlp-with-python.pdf) | [03](03-nlp/references.md) |
| | Buduma, *Fundamentals of Deep Learning* (O'Reilly), [PDF](sources/buduma-fundamentals-of-deep-learning.pdf) | [02](02-deep-learning/references.md) |
| | Raieli and Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 1 only, [PDF](sources/building-ai-agents-llms-rag-kgs/ch01-analyzing-text-data-deep-learning.pdf). The rest of the book lives under `ai-engineering/` | [02](02-deep-learning/references.md), [03](03-nlp/references.md) |
| | Raschka, *Build a Large Language Model (From Scratch)* (Manning, 2024), appendix A on PyTorch, [PDF](../generative-ai/01-llm-fundamentals/sources/build-a-large-language-model-from-scratch/appendix-a-intro-to-pytorch.pdf) | [02](02-deep-learning/references.md) |

## Courses and videos

Each URL was checked to load on 2026-11-02, and the costs are as the platform listed them.

| Course | Platform, cost | Why take it | Pillars |
|---|---|---|---|
| ★ [Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction) | Ng, Coursera. Paid certificate, audit options vary | The current edition of the course behind the own ports in [`ng-machine-learning/`](01-classical-ml/practice/ng-machine-learning), which come from the 2011 edition | 01 |
| ★ [Deep Learning Specialization](https://www.coursera.org/specializations/deep-learning) | Ng, DeepLearning.AI on Coursera. Paid certificate, audit options vary | The course behind [`ng-deep-learning/`](02-deep-learning/practice/ng-deep-learning) and the chapter split in pillar 02 | 02 |
| ★ [Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html) | Karpathy, YouTube, free. Code at [karpathy/nn-zero-to-hero](https://github.com/karpathy/nn-zero-to-hero), MIT | Builds autograd, makemore and a GPT line by line. Kept in [`nn-zero-to-hero/`](../generative-ai/09-llms-from-scratch/practice/nn-zero-to-hero), with [build-nanogpt](https://github.com/karpathy/build-nanogpt) | 04, 02 |
| [StatQuest: Machine Learning](https://www.youtube.com/playlist?list=PLblh5JKOoLUICTaGLRoHQDuF_7q2GfuJF) | Starmer, YouTube, free | Short refreshers when a model family or metric won't stick | 01, 03 |
| [Practical Deep Learning for Coders](https://course.fast.ai/) | fast.ai, free | Top-down alternative to Ng: working models first, theory afterwards | 02, 03 |
| [CS229: Machine Learning, Autumn 2018 lectures](https://www.youtube.com/playlist?list=PLoROMvodv4rMiGQp3WXShtMGgzqpfVfbU) | Stanford, YouTube, free. [Course site](https://cs229.stanford.edu/) | The derivations behind pillar 01 | 01, 05 |
| [CS224N: NLP with Deep Learning, Winter 2021 lectures](https://www.youtube.com/playlist?list=PLoROMvodv4rOSH4v6133s9LFPRHjEmbmJ) | Stanford, YouTube, free. [Course site](https://web.stanford.edu/class/cs224n/) | From word vectors to Transformers, with the maths | 03, 02 |
| Kaggle Learn: [Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning), [Intermediate Machine Learning](https://www.kaggle.com/learn/intermediate-machine-learning), [Feature Engineering](https://www.kaggle.com/learn/feature-engineering) | Kaggle, free | Short exercises that run in the browser | 01 |
| [Hugging Face LLM Course](https://huggingface.co/learn/llm-course) | Hugging Face, free. [Ch. 1](https://huggingface.co/learn/llm-course/chapter1/3) is the source of the pipeline examples | Tokenizers, pipelines and fine-tuning | 02, 03 |
| Thakur, [*Approaching (Almost) Any NLP Problem on Kaggle*](https://www.kaggle.com/code/abhishek/approaching-almost-any-nlp-problem-on-kaggle) | Kaggle notebook, free. Own copy in [`practice/`](03-nlp/practice/approaching-almost-any-nlp-problem-on-kaggle.ipynb) | A competition baseline worked end to end | 03 |

## Shared docs

| Source | Pillars |
|---|---|
| [scikit-learn user guide](https://scikit-learn.org/stable/user_guide.html) and [release highlights](https://scikit-learn.org/stable/whats_new.html) | 01, 03 |
| [spaCy](https://spacy.io/), [NLTK](https://www.nltk.org/), [gensim](https://radimrehurek.com/gensim/), [sklearn-crfsuite](https://sklearn-crfsuite.readthedocs.io/) docs | 03 |

## Papers not yet in a pillar

These are the original sources for methods taught in [03 NLP](03-nlp/README.md), and that pillar's `references.md` has no row for them yet.

| Source | Taught in |
|---|---|
| Blei, Ng and Jordan, [*Latent Dirichlet Allocation*](https://www.jmlr.org/papers/v3/blei03a.html) (JMLR, 2003) | [03 note 03](03-nlp/notes/03-topic-models-and-summarization.md) |
| Mihalcea and Tarau, [*TextRank: Bringing Order into Text*](https://aclanthology.org/W04-3252/) (EMNLP, 2004) | [03 note 03](03-nlp/notes/03-topic-models-and-summarization.md) |
| Hutto and Gilbert, *VADER* (ICWSM, 2014), [code and lexicon](https://github.com/cjhutto/vaderSentiment) | [03 note 06](03-nlp/notes/06-sentiment-analysis.md) |

## Dependency audits

The full per-notebook fix tables live in the notes, and this is the index.

| Library | Status (2026-10-31) | Where |
|---|---|---|
| scikit-learn 0.20 to 1.4+ | Resolved for Müller and Guido 02, 04, 05 (2026-07) and, on 2026-10-31, `get_feature_names` to `get_feature_names_out` in eight notebooks (M&G 04, 07; Sarkar Ch04a, Ch06c, Ch06d, Ch06e, Ch07c, Ch09e) and `sklearn.externals.joblib` to `joblib` in Sarkar Ch08c. The Kaggle NLP notebook still uses `needs_proba` (removed 1.6) and `iid` | [Migration map](01-classical-ml/notes/04-model-evaluation.md#scikit-learn-migration-map-020--14) |
| TensorFlow 1.x to 2.x | Ng DL notebooks: `tf.compat.v1` bridge done, and Tensorflow Tutorial and Convolution model still need the `tf.contrib` rewrite. Sarkar Ch10a: confusion-matrix cell fixed, but `tf.estimator` (removed in TF 2.16) remains | [TF map](02-deep-learning/notes/01-neural-networks-fundamentals.md#tensorflow-1x-to-2x-status-and-migration-map), [text notebooks](02-deep-learning/notes/06-neural-text-models.md#tensorflow-status-of-the-text-notebooks) |
| transformers 4 to 5 | Version 5.22.1 removed the `question-answering`, `summarization` and `translation` pipeline tasks | [Neural text models](02-deep-learning/notes/06-neural-text-models.md#transformers-pipelines) |
| Standalone Keras, gensim 3, spaCy 2, pyLDAvis, skater | Not fixed, and reported per notebook in the Practice tables: spaCy `'en'` shortcuts, `keras.layers.normalization`, gensim `size=` and `index2word`, `pyLDAvis.sklearn`, `skater` (dead) in Ch09d, Stanford NER paths `E:/stanford/...` in Ch08b | Pillar 03 notes |
| PyMC3 to PyMC 5 | Bayesian notebooks belong to data analytics | [Migration map](../data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc.md#pymc3-to-pymc-5-migration-map), status in the data-analytics [PyMC version audit](../data-analytics/references.md#pymc-version-audit) |

## Source quality

| Item | Flag |
|---|---|
| Book PDFs in `sources/` (Müller and Guido, Sarkar, Buduma, the Packt chapter) | Publisher-copyrighted. Fine for private study, but do not publish the repo with them in it |
| Müller and Guido companion repo | No licence file upstream, so all rights reserved by default. Kept because it is the main practice surface for pillar 01, so do not redistribute |
| Ng course notebooks | Own graded Coursera work containing solutions. Coursera's honour code asks that solutions not be posted publicly |
| Data not in the repo | Sarkar ch. 9 and 10 `movie_reviews.csv`, ch. 6 NIPS papers; makemore `names.txt`; Kaggle competition data (spooky authors, ventilator); FineWeb-Edu shards for build-nanogpt; Ng DL helper modules and weights |
| Size | `ng-deep-learning/` 163 MB and `ng-machine-learning/` 22 MB (own work, left untouched) |
| Accuracy figures quoted from the books | Pillar 03 sentiment and 02 neural text notes quote approximate accuracies from the book text where the stored notebooks have no outputs. Elsewhere, figures come from each chapter's own run |
