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

1. [01 — Statistical foundations](notes/01-statistical-foundations.md) for the vocabulary: generalisation, bias-variance, the train/test contract.
2. [02 — Supervised learning](notes/02-supervised-learning.md) with `practice/Intro to Machine Learning in Python/02`.
3. [04 — Model evaluation](notes/04-model-evaluation.md). Leakage and metric choice are the most common interview failures.
4. [15 — micrograd](notes/15-micrograd.md) for backprop you can write from memory.
5. Then follow [CURRICULUM.md](CURRICULUM.md).

## Layout

```
data-science/
├── README.md, CURRICULUM.md, references.md
├── notes/                                   01–17, one topic each
├── practice/
│   ├── Intro to Machine Learning in Python/ Müller & Guido companion notebooks + mglearn
│   ├── Text Analytics with Python/          Sarkar 2e companion notebooks, Ch01–Ch10
│   ├── intro-to-nlp/                        own coursework: NLTK, TensorFlow NLP, transformers, word2vec (data/ CSVs gitignored)
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
| 01 | [Statistical foundations](notes/01-statistical-foundations.md) | Generalisation, bias-variance, over/underfitting, the ML vocabulary |
| 02 | [Supervised learning](notes/02-supervised-learning.md) | kNN, linear and logistic models, naive Bayes, trees, SVMs, from-scratch Ng versions |
| 03 | [Feature engineering and pipelines](notes/03-feature-engineering-and-pipelines.md) | Encoding, binning, interactions, transforms, feature selection, `Pipeline` and `ColumnTransformer` |
| 04 | [Model evaluation](notes/04-model-evaluation.md) | Cross-validation, grid search, metrics, PR/ROC, calibration, learning curves, the sklearn migration map |
| 05 | [Unsupervised learning](notes/05-unsupervised-learning.md) | Scaling, PCA, NMF, t-SNE, k-means, DBSCAN, agglomerative, anomaly detection, recommenders |
| 06 | [Ensembles](notes/06-ensembles.md) | Random forests, gradient boosting, XGBoost/LightGBM, stacking, SHAP |
| 07 | [Neural network fundamentals](notes/07-neural-networks-fundamentals.md) | Forward and backward pass, initialisation, regularisation, optimisers, CNNs, sequence models, TF 1→2 map |
| 08 | [Text representation](notes/08-text-representation.md) | Normalisation, tokenisation, POS, parsing, bag-of-words, TF-IDF, n-grams |
| 09 | [Text classification](notes/09-text-classification.md) | Classical text classifiers, grid search on text pipelines, the Kaggle NLP walkthrough |
| 10 | [Topic models and summarization](notes/10-topic-models-and-summarization.md) | Keyphrases, LSA, LDA, NMF, coherence, TextRank, document clustering |
| 11 | [Embeddings and similarity](notes/11-embeddings-and-similarity.md) | word2vec, GloVe, FastText, document similarity, the embedding projector |
| 12 | [Semantic analysis and NER](notes/12-semantic-analysis-and-ner.md) | WordNet, word-sense disambiguation, NER with spaCy and CRFs, logic in NLTK |
| 13 | [Sentiment analysis](notes/13-sentiment-analysis.md) | Lexicons, supervised and deep models, LIME, per-class topic models |
| 14 | [Neural text models](notes/14-neural-text-models.md) | RNN/LSTM/GRU, Conv1D, text generation, sentence encoders, transformers pipelines |
| 15 | [micrograd](notes/15-micrograd.md) | Scalar autograd engine, the chain rule, neurons to MLP, PyTorch mapping |
| 16 | [makemore](notes/16-makemore.md) | Bigram to MLP to WaveNet character models, initialisation, BatchNorm, manual backprop |
| 17 | [nanoGPT](notes/17-nanogpt.md) | Self-attention, the transformer block, reproducing GPT-2 124M |

## Rules of thumb

| Rule | Note |
|---|---|
| Fit every preprocessing step inside the CV loop; a scaler fitted on all the data leaks | [03](notes/03-feature-engineering-and-pipelines.md), [04](notes/04-model-evaluation.md) |
| Compare every score against a dummy baseline before reading it as good | [04](notes/04-model-evaluation.md) |
| Choose the metric from the business cost, and pick the threshold separately from the model | [04](notes/04-model-evaluation.md) |
| High train and low test scores mean variance: add data or regularise. Both low means bias: add capacity | [01](notes/01-statistical-foundations.md), [04](notes/04-model-evaluation.md) |
| On tabular data, try gradient boosting before a neural net | [06](notes/06-ensembles.md) |
| Scale features for kNN, SVMs, PCA and gradient descent; trees don't care | [02](notes/02-supervised-learning.md), [05](notes/05-unsupervised-learning.md) |
| A TF-IDF + logistic regression baseline is hard to beat on short-text classification | [09](notes/09-text-classification.md) |
| Check the loss at initialisation: it should be −log(1/vocab), not far above | [16](notes/16-makemore.md) |
| Gradient-check backprop against finite differences once, then switch it off | [07](notes/07-neural-networks-fundamentals.md), [15](notes/15-micrograd.md) |

## Resource map

**Related notes:** [data-analytics 06 — MCMC and PyMC](../data-analytics/notes/06-mcmc-and-pymc.md) (Bayesian modelling lives there); [ai-engineering graph engineering 10 — building KGs with LLMs](../ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms.md) (successor to the NER in note 12).

**Books and courses:** Müller & Guido; Sarkar, *Text Analytics with Python*; Karpathy, *Zero to Hero*; Ng's ML and DL courses; ISLR. Each is mapped to notes in [references.md](references.md).

**Coursework and practice** (do not run in bulk; each note's Practice table lists per-notebook needs):

| Surface | Notes | Runs |
|---|---|---|
| [Intro to Machine Learning in Python/](practice/Intro%20to%20Machine%20Learning%20in%20Python/) | 01–05, 08, 09 | Offline. Needs scikit-learn ≥ 1.4, `mglearn` (bundled) and graphviz; 07 needs the aclImdb download |
| [Text Analytics with Python/](practice/Text%20Analytics%20with%20Python/) | 08–14 | Needs nltk/spaCy/gensim models; partly legacy (spaCy 2, standalone keras, gensim 3, `skater`, TF ≤ 2.15 for Ch10a); Ch09–10 need `movie_reviews.csv` (not in repo) |
| [intro-to-nlp/](practice/intro-to-nlp/) | 08, 10, 11, 13, 14 | Own DeepLearning.AI TensorFlow NLP and Hugging Face course work. Data is in `data/` (CSVs are gitignored and local only; unzip `IMDB Dataset.csv.zip` on a fresh clone; PetFinder, Yelp and text-emotion CSVs are not in git). Notebooks read `./data/`, so start Jupyter in `intro-to-nlp/`. `tf.keras` 2.x `Tokenizer` API; transformers notebook needs internet for model downloads |
| [nn-zero-to-hero/](practice/nn-zero-to-hero/) | 15–17 | micrograd offline (graphviz, torch). makemore needs `names.txt` (not in repo). nanoGPT `bigram.py` offline CPU, `gpt.py` GPU, `build-nanogpt` 8×GPU + FineWeb-Edu |
| [approaching-almost-any-nlp-problem-on-kaggle.ipynb](practice/approaching-almost-any-nlp-problem-on-kaggle.ipynb) | 09 | Legacy (needs Kaggle spooky-author data + GloVe; old keras/xgboost APIs) |
| [deep-learning-starter-simple-lstm.ipynb](practice/deep-learning-starter-simple-lstm.ipynb) | 14 | GPU recommended; needs Kaggle Ventilator Pressure data |
| [udacity_mlnd_python_practice.ipynb](practice/udacity_mlnd_python_practice.ipynb) | 02 | Offline; needs `data/iris.txt` (not in repo) |
| [Ng's Machine Learning Nbks/](Ng's%20Machine%20Learning%20Nbks/) | 02, 04, 05, 07 | Offline; NumPy/SciPy with bundled `.mat` data |
| [Ng's Deep Learning Nbks/](Ng's%20Deep%20Learning%20Nbks/) | 07, 11, 14 | Legacy (TF 1.x via `tf.compat.v1`; two notebooks still need `tf.contrib`; some need course helper files and weights) |

**Readings:** [sources/](sources/), with the calibration, interpretability and BatchNorm papers; statistics books are in [`../data-analytics/sources/`](../data-analytics/sources/). Each is mapped to notes in [references.md](references.md).

**Interviewing guide:** [1-foundations](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/1-foundations/00-overview.md). Condensed notes are in sisyphus `interviewing/notes/foundations.md`.

**Previous layer:** [data-analytics](../data-analytics/README.md) · **Next layer:** [generative-ai / 01 LLM fundamentals](../generative-ai/01-llm-fundamentals/README.md)
