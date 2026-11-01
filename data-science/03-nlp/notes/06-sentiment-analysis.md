---
origin: vendored snapshots: Text Analytics with Python (kept as practice) + own coursework: intro-to-nlp (kept as practice)
sources:
  - ../practice/Text Analytics with Python/Ch09 - Sentiment Analysis/
  - ../../sources/sarkar-text-analytics-with-python-2e.pdf
  - ../practice/intro-to-nlp/tensorFlow/neural-network/ (CNN and RNN/LSTM sentiment)
  - ../practice/intro-to-nlp/word-cloud/world-cloud-pet-finder.ipynb
  - https://github.com/cjhutto/vaderSentiment
confidence: medium
cleaned: 2026-10-31
---
# 13 — Sentiment Analysis

> Is this review positive or negative, and why? Three generations of answer on the same IMDb movie-review data: hand-built lexicons (no training data), supervised classifiers on sparse or dense features, and sequence models. Then the more useful question for a business: what drives the sentiment, answered with model interpretation and topic models split by class.

---

## The task and the data

Sentiment is binary or graded polarity (positive, negative, sometimes neutral or a 1–5 score); finer forms are **aspect-based** (the battery is great, the screen is poor) and emotion detection. All of Sarkar's chapter 9 uses the 50,000-review IMDb dataset (`movie_reviews.csv`, balanced, 35k train / 15k test), normalised with the chapter's `text_normalizer.py` (HTML strip, accent removal, contraction expansion, lemmatisation, stopwords; see [08](01-text-representation.md)).

**Normalisation warning for sentiment:** default stopword lists contain *not*, *no*, *nor*, and *very*. Removing them turns "not good" into "good". Sarkar's normaliser keeps negations out of the stopword list; check yours.

---

## 1. Unsupervised lexicons (ch. 9a)

A lexicon maps words to polarity scores; a document's score is an aggregate. No labels needed, which makes lexicons the baseline when you have none.

| Lexicon | Scores | How it aggregates | Notes |
|---|---|---|---|
| TextBlob (Pattern) | Polarity −1..1, subjectivity 0..1 per adjective | Averages, handles some modifiers ("very") and negation | Quick, adjective-centred |
| AFINN | Integer −5..+5 per word (~3,300 words, plus emoticons) | Sum | Long documents get extreme scores; threshold on the sum |
| SentiWordNet | Pos / neg / objectivity per WordNet synset ([12](05-semantic-analysis-and-ner.md)) | POS-tag, take first synset, sum pos − neg, normalise by token count | Sense choice is naive (always first synset) |
| VADER | Valence per word, tuned on social media | Rules for negation, intensifiers ("extremely"), "but", caps, punctuation, emoji; `compound` −1..1 | Best of the lexicons on short informal text |

```python
from afinn import Afinn
afn = Afinn(emoticons=True)
scores = [afn.score(r) for r in test_reviews]
pred = ["positive" if s >= 1.0 else "negative" for s in scores]

from nltk.sentiment.vader import SentimentIntensityAnalyzer   # nltk.download("vader_lexicon")
vader = SentimentIntensityAnalyzer()
def vader_label(text, threshold=0.1):
    s = vader.polarity_scores(text)            # {'neg':.., 'neu':.., 'pos':.., 'compound':..}
    return "positive" if s["compound"] >= threshold else "negative"
```

SentiWordNet scoring, the core of the notebook's function:

```python
from nltk.corpus import sentiwordnet as swn
pos = neg = n = 0
for word, tag in tagged_tokens:
    wn_pos = {"NN": "n", "VB": "v", "JJ": "a", "RB": "r"}.get(tag[:2])
    synsets = list(swn.senti_synsets(word, wn_pos)) if wn_pos else []
    if synsets:
        pos += synsets[0].pos_score(); neg += synsets[0].neg_score(); n += 1
label = "positive" if (pos - neg) / max(n, 1) >= 0 else "negative"
```

Lexicons reach roughly 70% accuracy on long movie reviews (the book reports AFINN and VADER near 71%, SentiWordNet slightly lower). They fail on domain vocabulary ("unpredictable" is good for a thriller, bad for a car), sarcasm, and reviews that describe a sad plot positively. Note that each lexicon needs a threshold, and the threshold is a parameter you are tuning on the test set if you pick it by looking at accuracy.

---

## 2. Supervised models (ch. 9b)

With labels, the text classification recipe from [09](02-text-classification.md) applies directly.

```python
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier

cv = CountVectorizer(binary=False, min_df=0.0, max_df=1.0, ngram_range=(1, 2))   # unigrams + bigrams
tv = TfidfVectorizer(use_idf=True, min_df=0.0, max_df=1.0, ngram_range=(1, 2), sublinear_tf=True)
lr  = LogisticRegression(penalty="l2", max_iter=100, C=1)
svm = SGDClassifier(loss="hinge", max_iter=100)           # linear SVM via SGD
```

Bigrams matter here: "not good", "waste of", "must see". Linear models on BoW or TF-IDF bigrams reach about 90% accuracy, beating everything else in the chapter, deep models included.

The same notebook then tries dense features into a small Keras network:

| Features | Model | Approx. accuracy (book) |
|---|---|---|
| Lexicon (AFINN, VADER) | none | ~0.71 |
| BoW / TF-IDF 1–2 grams | LogisticRegression, linear SVM | ~0.90 |
| Averaged word2vec (512-d, trained on the reviews) | 3-layer dense net with dropout | ~0.88 |
| spaCy GloVe document vector (300-d) | same dense net | ~0.85 |
| Learned embedding + LSTM (ch. 9c) | sequence model | ~0.88 |

The dense network, in modern Keras (the notebook uses standalone `keras` and `keras.layers.normalization`):

```python
from tensorflow import keras
model = keras.Sequential([
    keras.Input(shape=(512,)),
    keras.layers.Dense(512, activation="relu"), keras.layers.Dropout(0.2),
    keras.layers.Dense(512, activation="relu"), keras.layers.Dropout(0.2),
    keras.layers.Dense(512, activation="relu"), keras.layers.Dropout(0.2),
    keras.layers.Dense(2, activation="softmax"),
])
model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
model.fit(avg_wv_train, y_train_onehot, epochs=5, batch_size=100, validation_split=0.1)
```

Averaging word vectors throws away word order and negation scope, which is why it loses to bigrams. The averaging function is in [11](04-embeddings-and-similarity.md).

---

## 3. Sequence models (ch. 9c, intro-to-nlp)

Feed token ids, not a bag. The model learns embeddings and reads in order.

```python
# Sarkar ch. 9c, modernised: keras.layers / TextVectorization instead of a hand-built vocab
model = keras.Sequential([
    keras.layers.Embedding(input_dim=vocab_size, output_dim=128),
    keras.layers.SpatialDropout1D(0.2),                           # drops whole embedding channels
    keras.layers.LSTM(64, dropout=0.2, recurrent_dropout=0.2),
    keras.layers.Dense(1, activation="sigmoid"),
])
model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
model.fit(train_X, train_y, epochs=5, batch_size=100, validation_split=0.1)
pred = (model.predict(test_X) > 0.5).astype(int)                  # predict_classes() was removed in TF 2.6
```

The intro-to-nlp notebooks compared four architectures on the same IMDb split (first 25k reviews train, last 25k test; `Tokenizer(num_words=10000, oov_token="<oov>")`, `max_length=120`, `truncating="post"`):

| Architecture | Layers after `Embedding(10000, 64)` | Behaviour |
|---|---|---|
| Pooled embeddings | `GlobalAveragePooling1D → Dense(6) → Dense(1, sigmoid)` | Fast, a learned BoW; overfits after 2–3 epochs |
| CNN | `Conv1D(128, 3) → GlobalMaxPooling1D → Dense(16) → Dense(1)`, Adam 1e-4 | Learns n-gram detectors ("not worth", "highly recommend") |
| SimpleRNN | `SimpleRNN(64) → Dense(1)` | Vanishing gradients on 120-token reviews |
| LSTM | `LSTM(64) → Dense(1)` (or `Bidirectional(LSTM(64))`) | Handles negation scope; slower |

All of them show the same learning-curve shape: training accuracy climbs towards 1.0, validation peaks around epoch 2 and loss then rises. Use early stopping on `val_loss` ([07](../../02-deep-learning/notes/01-neural-networks-fundamentals.md)).

**A bug worth remembering.** The LSTM notebook's "experiment" cells pad two hand-written reviews to `maxlen=20`, but the model was trained on length 120. Keras runs it anyway (the LSTM accepts any length), the predictions are off, and nothing errors. Preprocess inference inputs with exactly the training settings, ideally by putting `TextVectorization` inside the model so there is one code path.

The CNN/RNN mechanics belong to [14](../../02-deep-learning/notes/02-neural-text-models.md); the contextual models that replaced them (a fine-tuned DistilBERT gets ~93% on IMDb, an off-the-shelf `pipeline("sentiment-analysis")` ~89% with no training) are in [14 — Transformers pipelines](../../02-deep-learning/notes/02-neural-text-models.md#transformers-pipelines).

---

## 4. What drives sentiment (ch. 9d, 9e)

Accuracy says the model works; the business wants to know *why* customers are unhappy.

### Explaining individual predictions with LIME

LIME perturbs the document (drops words at random), watches how `predict_proba` changes, and fits a local linear model whose weights say which words pushed this prediction.

```python
from lime.lime_text import LimeTextExplainer      # the notebook imports it via skater, which is dead
pipe = make_pipeline(CountVectorizer(ngram_range=(1, 2)), LogisticRegression(max_iter=1000))
pipe.fit(norm_train_reviews, train_sentiments)
explainer = LimeTextExplainer(class_names=list(pipe.classes_))
exp = explainer.explain_instance(norm_test_reviews[100], pipe.predict_proba, num_features=10, labels=[1])
exp.show_in_notebook()        # words highlighted by contribution to 'positive'
```

For a linear pipeline, the global coefficients already explain the model ([09](02-text-classification.md)); LIME earns its cost on nonlinear models. SHAP's text explainer is the more principled alternative ([06](../../01-classical-ml/notes/06-ensembles.md) covers SHAP values and lists the explanation papers, including LIME's: [Ribeiro et al. 2016](../../sources/ribeiro-2016-why-should-i-trust-you.pdf)).

### Topic models per class

Split the corpus by label and run NMF on each half ([10](03-topic-models-and-summarization.md)): the topics of the negative reviews are the complaint themes.

```python
pos_docs = [r for r, s in zip(norm_reviews, sentiments) if s == "positive"]
ptv = TfidfVectorizer(use_idf=True, min_df=0.05, max_df=0.95, ngram_range=(1, 1), sublinear_tf=True)
pos_nmf = NMF(n_components=10, solver="cd", max_iter=500, random_state=42, alpha_W=0.1, l1_ratio=0.85)
pos_nmf.fit(ptv.fit_transform(pos_docs))     # notebook: alpha=0.1, renamed alpha_W in sklearn 1.0
# repeat for negative reviews; visualise each with pyLDAvis
```

In the book's run, positive topics are about performances, story and "must watch", and negative topics are about bad acting, boring plots, and wasted money. On product reviews the same split surfaces delivery, quality and support complaints.

---

## Word clouds and quick text EDA

The intro-to-nlp PetFinder notebook (Kaggle adoption-speed data) used word clouds to explore free-text fields: top cat vs dog names, breed names, and description text by adoption speed.

```python
from wordcloud import WordCloud
text = " ".join(df.loc[df.Type == "Cat", "Name"].fillna(""))
wc = WordCloud(background_color="white", width=1200, height=1000, collocations=False).generate(text)
plt.imshow(wc); plt.axis("off")
```

Findings were EDA-grade: many "names" are descriptions ("Kitten", "Puppies", "No Name"), which is itself a feature (unnamed pets adopt more slowly). Word clouds are fine for a first look, but they encode frequency as font size, which is hard to compare. For anything you will act on, use a sorted bar chart of counts or of class-conditional log-odds (which words are most over-represented in slow-adoption descriptions).

---

## Rules of thumb

| Rule | Why |
|---|---|
| Start with TF-IDF 1–2 grams + logistic regression | ~90% on reviews, seconds to train, explainable |
| Keep negations out of the stopword list | "not good" must survive preprocessing |
| Use VADER when you have no labels and short informal text | Rules for negation, intensifiers, emoji |
| Use the same preprocessing at inference as in training | The maxlen=20 bug fails silently |
| Pair a sentiment model with per-class topics | The score says how many are unhappy; topics say about what |
| For new work, try a pre-trained transformer before training anything | Zero-shot or fine-tuned beats every model here |

---

## Practice

| Notebook | Covers | Runs |
|---|---|---|
| [`Ch09a - Unsupervised Lexical`](../practice/text-analytics-with-python/Ch09%20-%20Sentiment%20Analysis/Ch09a%20-%20Sentiment%20Analysis%20-%20Unsupervised%20Lexical.ipynb) | TextBlob, AFINN, SentiWordNet, VADER | Needs data: `movie_reviews.csv.bz2` (not in this snapshot; IMDb 50k from the book repo). `afinn`, `textblob`, spaCy `en_core_web_sm` |
| `Ch09b - Supervised` | BoW/TF-IDF + LR/SVM; word2vec and GloVe + dense net | Needs data as above; standalone `keras`, `keras.layers.normalization` (TF 1.x era), gensim 3 `size=` / `index2word`, spaCy vectors model |
| `Ch09c - Advanced Deep Learning` | Embedding + LSTM | Needs data; standalone `keras`; `predict_classes` removed in TF 2.6 |
| `Ch09d - Model Interpretation` | LIME explanations | Needs data; legacy: `skater` is unmaintained, swap in `lime` |
| `Ch09e - Topic Models` | NMF per sentiment class, pyLDAvis | Needs data; NMF `alpha` → `alpha_W`; pyLDAvis `.sklearn` → `.lda_model` |

The intro-to-nlp CNN/RNN sentiment notebooks are in [`practice/intro-to-nlp/tensorFlow/neural-network/`](../practice/intro-to-nlp/tensorFlow/neural-network) and the PetFinder word clouds in [`practice/intro-to-nlp/word-cloud/`](../practice/intro-to-nlp/word-cloud). Their data is in `practice/intro-to-nlp/data/` (CSVs gitignored, local only).

---

→ Next: [14-neural-text-models.md](../../02-deep-learning/notes/02-neural-text-models.md) — RNNs, LSTMs, text generation, pre-trained encoders and Hugging Face pipelines.
