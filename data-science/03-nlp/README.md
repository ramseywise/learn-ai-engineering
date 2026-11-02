# 03 — Natural language processing

> How text becomes numbers, what classical models do with those numbers, and what changes when a pretrained encoder supplies them. Deck: [`slides/nlp.pptx`](slides/nlp.pptx) (source [`slides/deck.yaml`](slides/deck.yaml)). Practice: [`practice/`](practice/). References: [`references.md`](references.md).

## What it is

The pre-transformer NLP toolkit, taught as something you can still use: preprocessing, bag of words and TF-IDF, text classification, topic models and summarisation, word embeddings, named entity recognition and sentiment analysis. It closes on the modern shortcut, in which sentence embeddings from a pretrained encoder become ordinary features for classification, clustering and anomaly detection.

## Why it matters

A data scientist is handed text far more often than a clean table, and the first question is rarely which transformer to use. It is whether a TF-IDF baseline already does the job, what it costs to beat it, and how you would know. On this pillar's own film task, tuned TF-IDF reaches a macro-F1 of 0.423, MiniLM embeddings with a logistic head reach 0.484, and on IMDb a TF-IDF bigram model scores 0.906 where averaged word vectors score 0.831. A person who has run those comparisons can spend the budget where it pays.

## The story

A model cannot read, so somebody decides how text becomes numbers, and that decision quietly sets what the model can learn: remove "not" as a stop word and "not good" flips from 0.02 to 0.99 positive. With words as columns, a linear model on TF-IDF sets a baseline that is hard to beat and easy to read. Without labels, the same matrix gives topics and clusters, which need a human reading before anyone names them. Sparse columns treat "hotel" and "motel" as unrelated, so embeddings learn nearness from context, and sequence labellers such as CRFs pull entities out of the text. Sentiment then tests every method on one task, and shows that a dictionary with no labels reaches 0.76, TF-IDF 0.91, and a small LSTM on 6,000 reviews about 0.80. Pretrained sentence encoders finally make those labelled comparisons cheap, because you encode once, cache a matrix and go back to scikit-learn.

## Reading order

| # | Note | Question it answers |
|---|---|---|
| 01 | [Text representation](notes/01-text-representation.md) | How does text become numbers, and what do those choices cost? |
| 02 | [Text classification](notes/02-text-classification.md) | How good is the baseline, and how do you compare anything else against it? |
| 03 | [Topic models and summarisation](notes/03-topic-models-and-summarization.md) | What is in a corpus when nobody has labelled it? |
| 04 | [Embeddings and similarity](notes/04-embeddings-and-similarity.md) | How does a model learn that "hotel" is near "motel"? |
| 05 | [Semantic analysis and NER](notes/05-semantic-analysis-and-ner.md) | How do you pull out who, where and when, and how do you score it? |
| 06 | [Sentiment analysis](notes/06-sentiment-analysis.md) | Dictionary, linear model or LSTM, and why do people feel that way? |
| 07 | [LLM embeddings as features](notes/07-llm-embeddings-as-features.md) | When does a pretrained encoder beat TF-IDF, and what else can its vectors do? |

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DA 04/01 Bayesian inference](../../data-analytics/04-bayesian-analysis/notes/01-bayesian-inference.md) | Conjugacy and generative stories behind LDA |
| [DA 04/02 MCMC and PyMC](../../data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc.md) | Samplers and variational inference |
| [DA 06/05 Segmentation and RFM](../../data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm.md) | Scoring clusters against an outcome |

**Feeds into**

| Chapter | Why |
|---|---|
| [GA 01/01 Tokens and embeddings](../../generative-ai/01-llm-fundamentals/notes/01-tokens-and-embeddings.md) | Word counts to word2vec to a learned embedding table |
| [GA 02/03 Keyword, semantic and hybrid search](../../generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search.md) | TF-IDF, BM25 and sentence embeddings are taught here first |
| [GA 09/03 nanoGPT](../../generative-ai/09-llms-from-scratch/notes/03-nanogpt.md) | Compares a GPT with these earlier text models |
| [AIE 05/10 Building KGs with LLMs](../../ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms.md) | NER without an LLM |
| [AIE 08/03 Multimodal RAG](../../ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag.md) | Comparing vectors in one space |

## Rules of thumb

- Fit TF-IDF and a linear model first. It takes seconds, and everything else has to beat it.
- Fit every vectoriser, scaler and PCA inside the training fold, since a vocabulary built on test text is a leak.
- Keep negation when sentiment matters, and read what a stop word list removes.
- Use macro-F1 with imbalanced classes, and entity-level F1 for NER. Token accuracy on tags is flattered by `O`.
- Read top documents, not just top words, before naming a topic, and refit with another seed.
- Cache embeddings keyed by model name, and re-embed everything when the model changes.
- Reach for an encoder when labels are few or absent. With plenty of labels the gap narrows, so measure it.
- Report differences alongside their noise. On 960 test films, one or two points is not a win.
- Do not use cosine scores as probabilities. Rank, then pick a threshold from your review capacity.

## Practice

Each chapter's code runs top to bottom with [`practice/run_note.py`](practice/run_note.py), which uses only data in the repo or downloaded on first use, cached under `~/.cache/`. From this folder:

```bash
uv run --python 3.12 --with gensim --with scikit-learn --with pandas python practice/run_note.py notes/02-text-classification.md
TOKENIZERS_PARALLELISM=false uv run --python 3.12 --with sentence-transformers --with setfit --with scikit-learn --with pandas --with scipy --with umap-learn --with hdbscan --with datasets python practice/run_note.py notes/07-llm-embeddings-as-features.md
```

Packages for each note, on Python 3.12:

| Note | `--with` packages |
|---|---|
| 01 | `nltk`, `spacy`, the `en_core_web_sm` 3.8.0 wheel (see below), `scikit-learn`, `pandas`, `tensorflow` |
| 02 | `gensim`, `scikit-learn`, `pandas` |
| 03 | `nltk`, `gensim`, `scikit-learn`, `pandas`, `networkx`, `scipy` |
| 04 | `gensim`, `scikit-learn`, `pandas`, `tensorflow`, `scipy` |
| 05 | `nltk`, `spacy`, the `en_core_web_sm` wheel, `sklearn-crfsuite`, `seqeval`, `pandas` |
| 06 | `nltk`, `afinn`, `textblob`, `gensim`, `lime`, `wordcloud`, `scikit-learn`, `pandas`, `pyarrow`, `tensorflow` |
| 07 | As in the command above; the API block is illustrative and is skipped |

The spaCy model goes on the command line as `--with "en_core_web_sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"`. Set `TF_CPP_MIN_LOG_LEVEL=3` to quieten TensorFlow.

### Coursework folders

| Folder | Notes | How it runs |
|---|---|---|
| [`practice/text-analytics-with-python/`](practice/text-analytics-with-python/) | 01-06 | Notebooks from Sarkar's book. They need the nltk, spaCy and gensim models and are partly legacy: spaCy 2, standalone keras, gensim 3, `skater`, and TF 2.15 or earlier for Ch10a. Ch09 and Ch10 need `movie_reviews.csv`, which is not in the repo |
| [`practice/intro-to-nlp/`](practice/intro-to-nlp/) | 01, 03, 04, 06 | Own DeepLearning.AI TensorFlow NLP and Hugging Face course work, using the `tf.keras` 2.x `Tokenizer` API. The transformers notebook needs internet access for model downloads |
| [`practice/approaching-almost-any-nlp-problem-on-kaggle.ipynb`](practice/approaching-almost-any-nlp-problem-on-kaggle.ipynb) | 02 | Legacy. Needs Kaggle's spooky-author data and GloVe, with old keras and xgboost APIs |

### intro-to-nlp datasets

The notebooks read `./data/`, so start Jupyter inside `practice/intro-to-nlp/`. That folder is gitignored except for `irish-lyrics.txt`, because every other file is over the 1 MB pre-commit limit. On a fresh clone, download these into `practice/intro-to-nlp/data/`:

| File | Where to get it |
|---|---|
| `sarcasm.json` | [TensorFlow course copy](https://storage.googleapis.com/tensorflow-1-public/course3/sarcasm.json), or the [Kaggle dataset](https://www.kaggle.com/datasets/rmisra/news-headlines-dataset-for-sarcasm-detection) (needs reformatting into one JSON array) |
| `IMDB Dataset.csv` | [Kaggle: IMDB dataset of 50k movie reviews](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews) |
| `pet-train.csv`, `pet-test.csv`, `breed_labels.csv` | [Kaggle: PetFinder adoption prediction](https://www.kaggle.com/c/petfinder-adoption-prediction/data) |
| `yelp_ratings.csv`, `text_emotion.csv`, `all_data_new.csv` | No recorded source, so the notebooks using these will not run on a fresh clone without a substitute |

Kaggle downloads need a free account and, for the competition, accepting its rules.
