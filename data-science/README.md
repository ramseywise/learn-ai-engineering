# Data Science

> Interview guide: [Pillar 1 — Foundations](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/1-foundations/00-overview.md).
> Position: second layer. It comes after [data-analytics](../data-analytics/README.md) (statistics, inference, Bayes) and before [generative-ai](../generative-ai/01-llm-fundamentals/README.md) (LLMs). The sequenced path and prerequisites are in [CURRICULUM.md](CURRICULUM.md).

## What it is

Classical machine learning, NLP and neural networks, from first principles to a GPT-2 reproduction. The notes cover:

- the scikit-learn workflow: supervised and unsupervised models, features, pipelines, evaluation and ensembles;
- neural networks as taught in Ng's two Coursera courses;
- the pre-transformer NLP toolkit, from bag-of-words to LSTMs and sentence encoders;
- Karpathy's micrograd → makemore → nanoGPT arc.

Each note condenses a book or course and points to the notebooks it was built from.

## Start here

1. [01 — Statistical foundations](01-classical-ml/notes/01-statistical-foundations.md) for the vocabulary: generalisation, bias-variance, the train/test contract.
2. [02 — Supervised learning](01-classical-ml/notes/02-supervised-learning.md) with `practice/Intro to Machine Learning in Python/02`.
3. [04 — Model evaluation](01-classical-ml/notes/04-model-evaluation.md). Leakage and metric choice are the most common interview failures.
4. [15 — micrograd](04-llms-from-scratch/notes/01-micrograd.md) for backprop you can write from memory.
5. Then follow [CURRICULUM.md](CURRICULUM.md).

## Layout

```
data-science/
├── README.md, CURRICULUM.md, references.md
├── notes/                                   01–17, one topic each
├── practice/
│   ├── Intro to Machine Learning in Python/ Müller & Guido companion notebooks + mglearn
│   ├── Text Analytics with Python/          Sarkar 2e companion notebooks, Ch01–Ch10
│   ├── intro-to-nlp/                        own coursework: NLTK, TensorFlow NLP, transformers, word2vec (data/ gitignored except irish-lyrics.txt)
│   ├── nn-zero-to-hero/                     Karpathy: micrograd/, makemore/, nanogpt/ (+ build-nanogpt)
│   ├── approaching-almost-any-nlp-problem-on-kaggle.ipynb
│   ├── deep-learning-starter-simple-lstm.ipynb
│   └── udacity_mlnd_python_practice.ipynb
├── Ng's Machine Learning Nbks/              own Coursera ML work, ex1–ex8
├── Ng's Deep Learning Nbks/                 own Coursera DL Specialization work, 5 courses
└── sources/                                 book PDFs, papers, images/
```

## Syllabus

| # | Note | Covers |
|---|---|---|
| 01 | [Statistical foundations](01-classical-ml/notes/01-statistical-foundations.md) | Generalisation, bias-variance, over/underfitting, the ML vocabulary |
| 02 | [Supervised learning](01-classical-ml/notes/02-supervised-learning.md) | kNN, linear and logistic models, naive Bayes, trees, SVMs, from-scratch Ng versions |
| 03 | [Feature engineering and pipelines](01-classical-ml/notes/03-feature-engineering-and-pipelines.md) | Encoding, binning, interactions, transforms, feature selection, `Pipeline` and `ColumnTransformer` |
| 04 | [Model evaluation](01-classical-ml/notes/04-model-evaluation.md) | Cross-validation, grid search, metrics, PR/ROC, calibration, learning curves, the sklearn migration map |
| 05 | [Unsupervised learning](01-classical-ml/notes/05-unsupervised-learning.md) | Scaling, PCA, NMF, t-SNE, k-means, DBSCAN, agglomerative, anomaly detection, recommenders |
| 06 | [Ensembles](01-classical-ml/notes/06-ensembles.md) | Random forests, gradient boosting, XGBoost/LightGBM, stacking, SHAP |
| 07 | [Neural network fundamentals](02-deep-learning/notes/01-neural-networks-fundamentals.md) | Forward and backward pass, initialisation, regularisation, optimisers, CNNs, sequence models, TF 1→2 map |
| 08 | [Text representation](03-nlp/notes/01-text-representation.md) | Normalisation, tokenisation, POS, parsing, bag-of-words, TF-IDF, n-grams |
| 09 | [Text classification](03-nlp/notes/02-text-classification.md) | Classical text classifiers, grid search on text pipelines, the Kaggle NLP walkthrough |
| 10 | [Topic models and summarization](03-nlp/notes/03-topic-models-and-summarization.md) | Keyphrases, LSA, LDA, NMF, coherence, TextRank, document clustering |
| 11 | [Embeddings and similarity](03-nlp/notes/04-embeddings-and-similarity.md) | word2vec, GloVe, FastText, document similarity, the embedding projector |
| 12 | [Semantic analysis and NER](03-nlp/notes/05-semantic-analysis-and-ner.md) | WordNet, word-sense disambiguation, NER with spaCy and CRFs, logic in NLTK |
| 13 | [Sentiment analysis](03-nlp/notes/06-sentiment-analysis.md) | Lexicons, supervised and deep models, LIME, per-class topic models |
| 14 | [Neural text models](02-deep-learning/notes/02-neural-text-models.md) | RNN/LSTM/GRU, Conv1D, text generation, sentence encoders, transformers pipelines |
| 15 | [micrograd](04-llms-from-scratch/notes/01-micrograd.md) | Scalar autograd engine, the chain rule, neurons to MLP, PyTorch mapping |
| 16 | [makemore](04-llms-from-scratch/notes/02-makemore.md) | Bigram to MLP to WaveNet character models, initialisation, BatchNorm, manual backprop |
| 17 | [nanoGPT](04-llms-from-scratch/notes/03-nanogpt.md) | Self-attention, the transformer block, reproducing GPT-2 124M |
| 18 | LLM embeddings as features *(planned)* | Sentence-transformer and API embeddings fed to classical ML: classification with a linear head, clustering and BERTopic, embedding-based anomaly detection and recommenders, choosing a model on MTEB, cost vs. TF-IDF. Sources: Alammar & Grootendorst, *Hands-On LLMs* ch. 4, 5, 10 ([code](https://github.com/HandsOnLLM/Hands-On-Large-Language-Models)); Boykis, [*What are embeddings*](https://github.com/veekaybee/what_are_embeddings); [sentence-transformers](https://sbert.net/) docs |

## Rules of thumb

| Rule | Note |
|---|---|
| Fit every preprocessing step inside the CV loop; a scaler fitted on all the data leaks | [03](01-classical-ml/notes/03-feature-engineering-and-pipelines.md), [04](01-classical-ml/notes/04-model-evaluation.md) |
| Compare every score against a dummy baseline before reading it as good | [04](01-classical-ml/notes/04-model-evaluation.md) |
| Choose the metric from the business cost, and pick the threshold separately from the model | [04](01-classical-ml/notes/04-model-evaluation.md) |
| High train and low test scores mean variance: add data or regularise. Both low means bias: add capacity | [01](01-classical-ml/notes/01-statistical-foundations.md), [04](01-classical-ml/notes/04-model-evaluation.md) |
| On tabular data, try gradient boosting before a neural net | [06](01-classical-ml/notes/06-ensembles.md) |
| Scale features for kNN, SVMs, PCA and gradient descent; trees don't care | [02](01-classical-ml/notes/02-supervised-learning.md), [05](01-classical-ml/notes/05-unsupervised-learning.md) |
| A TF-IDF + logistic regression baseline is hard to beat on short-text classification | [09](03-nlp/notes/02-text-classification.md) |
| Check the loss at initialisation: it should be −log(1/vocab), not far above | [16](04-llms-from-scratch/notes/02-makemore.md) |
| Gradient-check backprop against finite differences once, then switch it off | [07](02-deep-learning/notes/01-neural-networks-fundamentals.md), [15](04-llms-from-scratch/notes/01-micrograd.md) |

## Resource map

**Related notes:** [data-analytics 10 — MCMC and PyMC](../data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc.md) (Bayesian modelling lives there); [ai-engineering graph engineering 10 — building KGs with LLMs](../ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms.md) (successor to the NER in note 12).

**Books and courses:** Müller & Guido; Sarkar, *Text Analytics with Python*; Karpathy, *Zero to Hero*; Ng's ML and DL courses; ISLR. Each is mapped to notes in [references.md](references.md).

**Coursework and practice** (do not run in bulk; each note's Practice table lists per-notebook needs):

| Surface | Notes | Runs |
|---|---|---|
| [Intro to Machine Learning in Python/](01-classical-ml/practice/intro-to-ml-in-python) | 01–05, 08, 09 | Offline. Needs scikit-learn ≥ 1.4, `mglearn` (bundled) and graphviz; 07 needs the aclImdb download |
| [Text Analytics with Python/](03-nlp/practice/text-analytics-with-python) | 08–14 | Needs nltk/spaCy/gensim models; partly legacy (spaCy 2, standalone keras, gensim 3, `skater`, TF ≤ 2.15 for Ch10a); Ch09–10 need `movie_reviews.csv` (not in repo) |
| [intro-to-nlp/](03-nlp/practice/intro-to-nlp) | 08, 10, 11, 13, 14 | Own DeepLearning.AI TensorFlow NLP and Hugging Face course work. Data is in `data/`, which is gitignored (every file but `irish-lyrics.txt` is over the 1 MB pre-commit limit). On a fresh clone, download: [sarcasm.json](https://storage.googleapis.com/laurencemoroney-blog.appspot.com/sarcasm.json), [IMDB Dataset.csv](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews), PetFinder train/test/breed labels ([Kaggle](https://www.kaggle.com/c/petfinder-adoption-prediction/data)); Yelp, text-emotion and `all_data_new.csv` have no recorded source. Notebooks read `./data/`, so start Jupyter in `intro-to-nlp/`. `tf.keras` 2.x `Tokenizer` API; transformers notebook needs internet for model downloads |
| [nn-zero-to-hero/](04-llms-from-scratch/practice/nn-zero-to-hero) | 15–17 | micrograd offline (graphviz, torch). makemore needs `names.txt` (not in repo). nanoGPT `bigram.py` offline CPU, `gpt.py` GPU, `build-nanogpt` 8×GPU + FineWeb-Edu |
| [approaching-almost-any-nlp-problem-on-kaggle.ipynb](03-nlp/practice/approaching-almost-any-nlp-problem-on-kaggle.ipynb) | 09 | Legacy (needs Kaggle spooky-author data + GloVe; old keras/xgboost APIs) |
| [deep-learning-starter-simple-lstm.ipynb](02-deep-learning/practice/deep-learning-starter-simple-lstm.ipynb) | 14 | GPU recommended; needs Kaggle Ventilator Pressure data |
| [udacity_mlnd_python_practice.ipynb](01-classical-ml/practice/udacity_mlnd_python_practice.ipynb) | 02 | Offline; needs `data/iris.txt` (not in repo) |
| [Ng's Machine Learning Nbks/](01-classical-ml/practice/ng-machine-learning) | 02, 04, 05, 07 | Offline; NumPy/SciPy with bundled `.mat` data |
| [Ng's Deep Learning Nbks/](02-deep-learning/practice/ng-deep-learning) | 07, 11, 14 | Legacy (TF 1.x via `tf.compat.v1`; two notebooks still need `tf.contrib`; some need course helper files and weights) |

**Readings:** [sources/](sources/), with the calibration, interpretability and BatchNorm papers; statistics books are in [`../data-analytics/sources/`](../data-analytics/sources/). Each is mapped to notes in [references.md](references.md).

**Interviewing guide:** [1-foundations](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/1-foundations/00-overview.md). Condensed notes are in sisyphus `interviewing/notes/foundations.md`.

**Previous layer:** [data-analytics](../data-analytics/README.md) · **Next layer:** [generative-ai / 01 LLM fundamentals](../generative-ai/01-llm-fundamentals/README.md)
