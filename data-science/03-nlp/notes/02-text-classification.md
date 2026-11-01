---
origin: vendored snapshot: Text Analytics with Python (kept as practice) + Intro to Machine Learning in Python (kept) + own work (Kaggle notebook)
sources:
  - ../practice/Text Analytics with Python/Ch05 - Text Classification/
  - ../practice/Intro to Machine Learning in Python/07-working-with-text-data.ipynb
  - ../practice/approaching-almost-any-nlp-problem-on-kaggle.ipynb
  - https://www.kaggle.com/code/abhishek/approaching-almost-any-nlp-problem-on-kaggle
  - ../../sources/sarkar-text-analytics-with-python-2e.pdf
confidence: high
cleaned: 2026-10-31
---
# 9 — Text Classification

> A sparse TF-IDF matrix plus a linear model is the baseline every text classifier must beat, and it is hard to beat on small and medium data. Naive Bayes is faster and nearly as good; trees are worse on sparse text; averaged word vectors rarely win without fine-tuning. Tune with a pipeline, score with a metric that fits the task, and read the coefficients.

---

## The task

Assign one (multi-class) or several (multi-label) labels to a document: spam/ham, sentiment, topic, author, intent, toxicity. Everything in [02](../../01-classical-ml/notes/02-supervised-learning.md)–[04](../../01-classical-ml/notes/04-model-evaluation.md) applies; what changes is that features are very many, very sparse and mostly irrelevant individually.

| Datasets used in the practice notebooks | Classes | Size |
|---|---|---|
| IMDb reviews (M&G ch. 7) | pos / neg | 25k train, 25k test |
| 20 Newsgroups (Sarkar ch. 5) | 20 topics | ~18k posts |
| Spooky Author Identification (Kaggle notebook) | EAP / HPL / MWS | ~20k sentences |
| Jigsaw toxic comments (Kaggle) | 6 labels, multi-label | ~160k |

---

## The baseline: TF-IDF + linear model

```python
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV

pipe = make_pipeline(TfidfVectorizer(min_df=5), LogisticRegression(max_iter=1000))
param_grid = {"logisticregression__C": [0.001, 0.01, 0.1, 1, 10, 100],
              "tfidfvectorizer__ngram_range": [(1, 1), (1, 2), (1, 3)]}
grid = GridSearchCV(pipe, param_grid, cv=5, n_jobs=-1).fit(text_train, y_train)
print(grid.best_params_, grid.best_score_)    # IMDb: C=100, (1, 3), CV 0.91
```

The vectoriser is inside the pipeline, so the vocabulary and IDF are refit on each training fold ([03](../../01-classical-ml/notes/03-feature-engineering-and-pipelines.md#leakage-and-why-pipelines-exist)).

M&G's IMDb progression:

| Setup | CV accuracy |
|---|---|
| `CountVectorizer` + `LogisticRegression` | 0.88 |
| + `min_df=5` (27k features instead of 75k) | 0.88 |
| + `stop_words="english"` | 0.88 (slightly lower) |
| `TfidfVectorizer` | 0.89 |
| + `ngram_range=(1, 3)`, tuned `C` | 0.91 |
| spaCy lemmatisation, small training sample | Small gain; matters more with less data |

### Reading the model

A linear model's coefficients are per-token weights:

```python
vect = grid.best_estimator_.named_steps["tfidfvectorizer"]
coef = grid.best_estimator_.named_steps["logisticregression"].coef_.ravel()
names = vect.get_feature_names_out()
print(names[coef.argsort()[:15]])     # most negative: 'worst', 'waste', 'awful', 'disappointment', ...
print(names[coef.argsort()[-15:]])    # most positive: 'excellent', 'perfect', '7/10', 'wonderful', ...
```

With trigrams, M&G find "not worth", "definitely worth", "well worth" among the strongest features: n-grams capture the negation that unigrams miss. Inspecting coefficients is also how you catch leakage: a top feature like a reviewer's signature means the model learned the wrong thing.

---

## Comparing classifiers on text (Sarkar ch. 5b)

Sarkar fits six classifiers on 20 Newsgroups, with both bag-of-words and TF-IDF features, and reports 5-fold CV and test accuracy.

| Model | Result on sparse text | Why |
|---|---|---|
| `MultinomialNB(alpha=1)` | Strong; best for its training time | Counts fit the multinomial assumption; one pass |
| `LogisticRegression` | Among the best | Linear, regularised, handles many features |
| `LinearSVC` | Among the best; usually top on TF-IDF | Same, hinge loss |
| `SGDClassifier(loss="hinge")` | Close to `LinearSVC` | Online; scales to data that doesn't fit in memory |
| `RandomForestClassifier(n_estimators=10)` | Clearly worse | Each split sees one sparse feature; few trees |
| `GradientBoostingClassifier(n_estimators=10)` | Worst and slowest | Same, plus sequential |

Then he grid-searches `MultinomialNB(alpha)`, `LogisticRegression(C)` and `LinearSVC(C)` with TF-IDF n-grams in a pipeline: the tuned linear SVM wins (mid-70s % accuracy on 20 classes), and the confusion matrix shows the errors are between related groups (`comp.*`, `talk.religion.misc` vs `alt.atheism`, `soc.religion.christian`). Errors between neighbouring classes are often label ambiguity, not model failure.

### Dense features (Sarkar ch. 5c)

| Features | Model | Outcome |
|---|---|---|
| Averaged word2vec (trained on the corpus, `gensim`) | `SGDClassifier` | Below TF-IDF |
| Averaged GloVe (spaCy `en_core_web_md` vectors) | `SGDClassifier` | Below TF-IDF |
| Averaged FastText | `SGDClassifier` | Below TF-IDF |
| Averaged GloVe | `MLPClassifier` | Better than linear on the same vectors, still not above tuned TF-IDF |

Averaging throws away word order and dilutes the informative words with common ones. Dense vectors win when training data is small, the vocabulary at test time differs, or the vectors are contextual and fine-tuned ([14](../../02-deep-learning/notes/02-neural-text-models.md)). [11](04-embeddings-and-similarity.md) explains the vectors themselves.

---

## Metrics for text classification

Sarkar's ch. 5a re-derives the metrics of [04](../../01-classical-ml/notes/04-model-evaluation.md#metrics-keep-the-end-goal-in-mind) on breast cancer before applying them to text; the additional points for text:

| Situation | Metric |
|---|---|
| Balanced topics | Accuracy, macro-F1 |
| Rare positive (spam, toxicity, fraud) | Precision/recall at an operating point, PR-AUC |
| Calibrated probabilities matter (Kaggle, downstream ranking) | Multiclass log-loss |
| Multi-label | Per-label ROC-AUC averaged (Jigsaw), micro/macro F1 |

Log-loss punishes confident mistakes without limit; clip predictions:

```python
def multiclass_logloss(actual, predicted, eps=1e-15):
    """Kaggle's metric: actual is (n,) int labels, predicted is (n, k) probabilities."""
    p = np.clip(predicted, eps, 1 - eps)
    p /= p.sum(axis=1, keepdims=True)
    return -np.log(p[np.arange(len(actual)), actual]).mean()
```

---

## Worked example: the Kaggle recipe

Your copy of Abhishek Thakur's *Approaching (Almost) Any NLP Problem on Kaggle*, on Spooky Author Identification (predict which of Poe, Lovecraft or Shelley wrote a sentence; log-loss). It is a ladder of models, each a few lines, scored on a stratified 90/10 split:

| Step | Features | Model | Idea |
|---|---|---|---|
| 1 | TF-IDF word 1–3-grams, `sublinear_tf`, `min_df=3` | `LogisticRegression` | First baseline: log-loss 0.626 |
| 2 | Counts, word 1–3-grams | `LogisticRegression` | Counts beat TF-IDF here |
| 3 | TF-IDF / counts | `MultinomialNB` | NB on counts is the best of the basic models |
| 4 | TF-IDF → `TruncatedSVD(120)` → `StandardScaler` | `SVC(probability=True)` | SVMs need dense, scaled, low-dim input; slow |
| 5 | TF-IDF, counts, SVD | XGBoost | Trees on sparse text are mediocre ([06](../../01-classical-ml/notes/06-ensembles.md)) |
| 6 | Pipeline SVD + scaler + LR; NB alone | `GridSearchCV` with a log-loss scorer | Tuned NB alpha: 8% better than default |
| 7 | GloVe 840B averaged sentence vectors | XGBoost | Dense vectors help trees |
| 8 | GloVe embedding layer (frozen) | LSTM, Bi-LSTM, GRU (Keras), early stopping | Sequence models on embeddings ([14](../../02-deep-learning/notes/02-neural-text-models.md)) |
| 9 | All of the above | Ensembling | Blend out-of-fold predictions ([06](../../01-classical-ml/notes/06-ensembles.md#stacking-and-voting)) |

```python
# The grid search in step 6, with a custom scorer
from sklearn import metrics, pipeline
from sklearn.decomposition import TruncatedSVD
mll_scorer = metrics.make_scorer(multiclass_logloss, greater_is_better=False,
                                 response_method="predict_proba")   # notebook: needs_proba=True (removed in 1.6)
clf = pipeline.Pipeline([("svd", TruncatedSVD()), ("scl", StandardScaler()),
                         ("lr", LogisticRegression(solver="liblinear"))])   # liblinear supports l1
param_grid = {"svd__n_components": [120, 180], "lr__C": [0.1, 1.0, 10], "lr__penalty": ["l1", "l2"]}
model = GridSearchCV(clf, param_grid, scoring=mll_scorer, cv=2, n_jobs=-1).fit(xtrain_tfv, ytrain)
```

Two things in the notebook to *not* copy into production:

- **The vectoriser is fit on train + validation text** ("semi-supervised"). Legitimate on Kaggle where test text is given; leakage anywhere you must score unseen data.
- **The grid search is outside a pipeline that contains the vectoriser**, so CV folds share a vocabulary. Small effect here; see [03](../../01-classical-ml/notes/03-feature-engineering-and-pipelines.md#leakage-and-why-pipelines-exist).

---

## Practical notes

| Topic | Advice |
|---|---|
| Imbalance | `class_weight="balanced"`; evaluate with PR curves; don't trust accuracy |
| Many classes, little data | Hierarchical labels; few-shot with sentence embeddings or an LLM |
| Multi-label | `OneVsRestClassifier(LogisticRegression())`, one sigmoid per label in neural models |
| Very large data | `HashingVectorizer` + `SGDClassifier.partial_fit` (no vocabulary to hold) |
| Character n-grams | `TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5))`: robust to typos, good for author style and short text |
| When to go neural | Order and context matter, lots of labelled data, or a pretrained transformer can be fine-tuned |
| When to use an LLM | No labelled data, label set changes often: zero/few-shot classification; compare against this baseline |

---

## Practice

| Notebook | Covers | Runs |
|---|---|---|
| [`Ch05a`](../practice/text-analytics-with-python/Ch05%20-%20Text%20Classification), `Ch05b`, `Ch05c` | Metrics; six classifiers on 20 Newsgroups; word2vec/GloVe/FastText features | Needs internet once (`fetch_20newsgroups`); `Ch05c` needs spaCy `en_core_web_md` and `gensim` (the `size=` argument is `vector_size=` in gensim 4) |
| [`07-working-with-text-data.ipynb`](../../01-classical-ml/practice/intro-to-ml-in-python/07-working-with-text-data.ipynb) | IMDb sentiment with BoW/TF-IDF/n-grams, coefficients | Needs the `aclImdb` download into `data/` |
| [`approaching-almost-any-nlp-problem-on-kaggle.ipynb`](../practice/approaching-almost-any-nlp-problem-on-kaggle.ipynb) (own) | The full Kaggle ladder | Needs the Kaggle `spooky` data and `glove.840B.300d.txt` (5.6 GB) at `../input/`; `xgboost`, standalone `keras` 2.x (`keras.layers.recurrent`); `make_scorer(needs_proba=True)` removed in scikit-learn 1.6 |

---

→ Next: [10-topic-models-and-summarization.md](03-topic-models-and-summarization.md) — unsupervised text: keyphrases, topic models and extractive summaries.
