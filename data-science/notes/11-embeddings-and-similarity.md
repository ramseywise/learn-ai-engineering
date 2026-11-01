---
origin: vendored snapshot: Text Analytics with Python (kept as practice) + own coursework: intro-to-nlp (kept as practice) + own coursework (Ng DL Sequence Models W2)
sources:
  - ../practice/Text Analytics with Python/Ch04 - Feature Engineering for Text Representation/Ch04b - Feature Engineering Text Data - Advanced Deep Learning Strategies.ipynb
  - ../practice/Text Analytics with Python/Ch07 - Text Similarity and Clustering/
  - ../Ng's Deep Learning Nbks/Sequence Models/Week2/
  - ../sources/sarkar-text-analytics-with-python-2e.pdf
  - ../practice/intro-to-nlp/word2vec/word_embeddings_word2vec.ipynb
  - ../practice/intro-to-nlp/tensorFlow/encoding-embeddings/
  - ../practice/intro-to-nlp/tensorFlow/text-processing/text_preprocessing_and_word_embeddings.ipynb
  - https://arxiv.org/abs/1301.3781
  - https://nlp.stanford.edu/projects/glove/
  - "Raieli & Iuculano, Building AI Agents with LLMs, RAG, and Knowledge Graphs (Packt, 2025), ch. 1"
  - https://aclanthology.org/Q18-1034/
  - https://doi.org/10.1162/tacl_a_00051
  - https://arxiv.org/abs/1310.4546
confidence: high
cleaned: 2026-10-31
---
# 11 — Embeddings and Similarity

> "You shall know a word by the company it keeps." Train a shallow network to predict a word from its context (or the reverse) and the hidden weights become dense vectors where similar words are close. From there: distances between strings, documents and vectors; a content-based recommender; and the line from word2vec to the sentence embeddings that power retrieval.

---

## From sparse to dense

A one-hot or TF-IDF vector ([08](08-text-representation.md)) has one dimension per vocabulary word: "hotel" and "motel" are orthogonal, exactly as far apart as "hotel" and "banana". An **embedding** maps each word to a dense vector of 50–300 numbers learned so that words used in similar contexts get similar vectors.

| | One-hot / TF-IDF | Embedding |
|---|---|---|
| Dimensions | Vocabulary size (10k–1M) | 50–1024 |
| Sparsity | Sparse | Dense |
| Similar words | Orthogonal | Close |
| Learned from | Counting | Prediction (or factorising co-occurrence) |
| Out-of-vocabulary | Dropped | Dropped (word2vec, GloVe); subwords (FastText) |

---

## word2vec

Mikolov et al. (2013) proposed two shallow architectures. Sarkar's Ch04b builds both in Keras on the King James Bible before using gensim:

| Architecture | Predicts | Training pairs | Better for |
|---|---|---|---|
| CBOW | Target word from the average of its context words | `([w-2, w-1, w+1, w+2], w)` | Frequent words; faster |
| Skip-gram | Each context word from the target | `(w, w-2)`, `(w, w-1)`, ... | Rare words; small corpora |

The original paper ([arXiv:1301.3781](https://arxiv.org/abs/1301.3781)) measured the two on its analogy test set (8,869 semantic and 10,675 syntactic questions). With 300-d vectors trained on 783M words, **skip-gram scored 50.0% on semantic questions against CBOW's 15.5%**, and 55.9% against 53.1% on syntactic ones. CBOW trained in about a day and skip-gram in about three. The "rare words, small corpora" rule of thumb in the table comes from the later word2vec documentation, not from this paper. The paper also shows that more data and wider vectors both help, and that each must grow with the other.

The 2013 paper made the output layer cheap with a hierarchical softmax over a Huffman tree. **Negative sampling** came in the follow-up paper ([arXiv:1310.4546](https://arxiv.org/abs/1310.4546) (Mikolov et al., NIPS 2013)). It turns the expensive softmax over the vocabulary into binary classification: is this (word, context) pair real, or one of *k* random pairs? The noise words are drawn from the unigram distribution raised to the 3/4 power, and the paper suggests k = 5–20 for small corpora and 2–5 for large ones. The same paper also discards each frequent word with probability 1 − √(t/f), with t ≈ 10⁻⁵. On about 1B words of Google News (300-d skip-gram, same analogy test), negative sampling with 5 noise words scored 59% in 38 minutes, against 47% in 41 minutes for the hierarchical softmax. With subsampling added, it scored 60% in 14 minutes. The vectors also add: the nearest tokens to *Russian* + *river* are *Moscow* and *Volga River*. Phrase vectors (frequent word pairs merged into single tokens) reached 72% on a phrase-analogy set, but only with 33B training words. These are single runs on Google-internal data, with no error bars.

```python
# Sarkar Ch04b: skip-gram with negative sampling, from scratch in Keras (sketch)
from tensorflow.keras.preprocessing.sequence import skipgrams
pairs, labels = skipgrams(word_ids, vocabulary_size=vocab_size, window_size=10)  # label 1 = real, 0 = negative

w_in  = tf.keras.Input((1,)); c_in = tf.keras.Input((1,))
w_emb = tf.keras.layers.Embedding(vocab_size, 100)(w_in)        # these weights ARE the word vectors
c_emb = tf.keras.layers.Embedding(vocab_size, 100)(c_in)
dot   = tf.keras.layers.Dot(axes=2)([w_emb, c_emb])
out   = tf.keras.layers.Dense(1, activation="sigmoid")(tf.keras.layers.Flatten()(dot))
model = tf.keras.Model([w_in, c_in], out)
model.compile(loss="binary_crossentropy", optimizer="rmsprop")
```

In practice, use gensim:

```python
from gensim.models import Word2Vec
model = Word2Vec(sentences=tokenized_corpus,   # list of token lists
                 vector_size=100,              # notebooks: size= (gensim 3); renamed in gensim 4
                 window=10, min_count=2, sg=1, # sg=1 skip-gram, 0 CBOW
                 epochs=5, workers=4)          # notebooks: iter= (gensim 3)
model.wv.most_similar("god", topn=5)
model.wv["jesus"]                              # the 100-d vector
```

The condensed NLP course notebooks trained the same model on NLTK's Project Gutenberg books (`most_similar("father")`) and on a news corpus (`most_similar("president")`), then plotted the vectors with t-SNE ([05](05-unsupervised-learning.md#manifold-learning-t-sne)). On a corpus of a few books the neighbours are already sensible: family words cluster, character names cluster.

### GloVe and FastText

| Model | Idea | Get it |
|---|---|---|
| GloVe (Pennington et al., 2014) | Factorise the log word co-occurrence matrix: $w_i \cdot \tilde w_j + b_i + \tilde b_j \approx \log X_{ij}$ | Pretrained 50–300d on Wikipedia, Common Crawl (840B tokens); spaCy `en_core_web_md`/`lg` ship them |
| FastText (Bojanowski et al., 2017) | word2vec over character n-grams: a word's vector is the sum of its n-gram vectors | `gensim.models.FastText`; handles misspellings and unseen words |

The subword gain shows up where words are rare or heavily inflected. FastText sums character 3- to 6-grams, hashed into 2M buckets. On the English Rare Words similarity set it scored 47 (Spearman ×100) against 43 for skip-gram and CBOW, and trained on just 1% of Wikipedia it scored 45, still beating CBOW trained on all of it. Czech syntactic analogies rose from 52.8% to 77.8%. Semantic analogies did not improve (German fell from 66.5% to 62.3%), and English WS353 stayed flat at 71 vs 72 ([doi:10.1162/tacl_a_00051](https://doi.org/10.1162/tacl_a_00051) (Bojanowski et al., TACL 2017)).

### Embedding geometry: analogies and bias

Your *Operations on word vectors* notebook (DL Sequence Models, week 2) uses 50-d GloVe:

```python
def cosine_similarity(u, v):
    return u @ v / (np.linalg.norm(u) * np.linalg.norm(v))

def complete_analogy(a, b, c, word_to_vec):
    """a is to b as c is to ?   e.g. man : woman :: king : queen"""
    ea, eb, ec = (word_to_vec[w] for w in (a, b, c))
    return max((w for w in word_to_vec if w not in {a, b, c}),
               key=lambda w: cosine_similarity(eb - ea, word_to_vec[w] - ec))
```

The same notebook shows the vectors encode social bias: projecting names and occupations onto the `woman - man` direction separates "receptionist" from "engineer". It removes the bias component from gender-neutral words (**neutralise**) and makes gendered pairs equidistant from the neutral axis (**equalise**), after Bolukbasi et al. (2016). Embeddings learned from text inherit the text's associations; any similarity system built on them does too.

Two more properties follow from "similar means shares contexts" (*Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. 1). First, **antonyms land close together**: "good" and "bad" fill the same slots, so a word2vec neighbour list mixes synonyms and antonyms. The context window decides which kind of similarity you get. Windows of about 2 group words by part of speech. Wider windows group them by topic. Second, **one vector holds every sense of a word**. Arora et al. ([TACL 2018](https://aclanthology.org/Q18-1034/)) show that a polysemous word's vector is approximately a linear superposition of its sense vectors, weighted by how often each sense occurs. "Apple" is mostly fruit or mostly company depending on the corpus. Sparse coding over the embeddings can pull the senses apart. Contextual models ([14](14-neural-text-models.md#what-attention-fixed)) remove the problem by giving each occurrence of a word its own vector.

---

## Embeddings inside a model

An `Embedding` layer is a lookup table trained with the rest of the network. The condensed NLP course trained one on IMDb sentiment and exported it for the TensorFlow Projector:

```python
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, 16),        # (batch, seq) -> (batch, seq, 16)
    tf.keras.layers.GlobalAveragePooling1D(),          # average over tokens
    tf.keras.layers.Dense(6, activation="relu"),
    tf.keras.layers.Dense(1, activation="sigmoid"),
])
weights = model.layers[0].get_weights()[0]             # (vocab_size, 16)
# write vecs.tsv (one vector per line) and meta.tsv (one word per line) -> projector.tensorflow.org
```

Trained for one task, the vectors organise by that task: in the projector the IMDb embedding splits into a "positive" and a "negative" pole rather than by topic. Pretrained vectors (GloVe, word2vec) carry general meaning; task-trained ones carry what the label needed. You can initialise with pretrained vectors and freeze or fine-tune them (the Kaggle notebook's LSTM in [09](09-text-classification.md#worked-example-the-kaggle-recipe), *Emojify*).

### Learning-curve check

The *embeddings learning curve* notebook trains on the sarcasm headlines and plots train/validation loss per epoch: validation loss bottoms out after a few epochs and climbs while accuracy stays flat, the overfitting signature of [04](04-model-evaluation.md#learning-curves-and-bias-variance-diagnosis). Smaller vocabulary, shorter sequences, smaller embedding dimension, or dropout flatten it.

---

## Document vectors

| Method | How | Quality |
|---|---|---|
| Average of word vectors | `np.mean([wv[w] for w in doc if w in wv], axis=0)` | Baseline; loses order; Sarkar's Ch04b clusters the toy corpus correctly with it |
| TF-IDF-weighted average | Weight each word vector by its TF-IDF | Better: downweights common words |
| Doc2Vec | Learn a paragraph vector alongside word vectors | Better than averaging; needs training |
| Topic proportions | LDA/NMF ([10](10-topic-models-and-summarization.md)) | Interpretable, coarse |
| Sentence encoders | Universal Sentence Encoder ([14](14-neural-text-models.md)), Sentence-BERT, modern embedding APIs | Current practice |

---

## Similarity and distance

Sarkar's Ch07a compares terms with several metrics, implemented by hand:

| Measure | Definition | Use for |
|---|---|---|
| Hamming | Count of positions that differ (equal-length strings) | Codes, fixed-length IDs |
| Manhattan | $\sum \lvert u_i - v_i\rvert$ | Character vectors |
| Euclidean | $\sqrt{\sum (u_i - v_i)^2}$ | Dense vectors of similar magnitude |
| Levenshtein (edit) | Minimum insertions, deletions, substitutions | Typos, fuzzy matching: "belief" vs "believe" |
| Cosine | $1 - \frac{u \cdot v}{\lVert u\rVert\lVert v\rVert}$ | Text vectors: ignores length |
| Jaccard | $\lvert A \cap B\rvert / \lvert A \cup B\rvert$ on token sets | Near-duplicate detection (MinHash) |

```python
def levenshtein(u, v):
    D = np.zeros((len(u) + 1, len(v) + 1), dtype=int)
    D[:, 0] = range(len(u) + 1); D[0, :] = range(len(v) + 1)
    for i in range(1, len(u) + 1):
        for j in range(1, len(v) + 1):
            D[i, j] = min(D[i-1, j] + 1, D[i, j-1] + 1, D[i-1, j-1] + (u[i-1] != v[j-1]))
    return D[-1, -1]
```

The raw dot product is unbounded and grows with vector length, so it favours long vectors. In count-based vectors that means frequent, uninformative words. Cosine divides the length out. **Normalise before cosine or dot product.** With L2-normalised vectors, cosine similarity is the dot product and Euclidean distance is a monotone function of it, so all three rank neighbours identically. Vector databases rely on this.

---

## A content-based recommender (Sarkar ch. 7b)

Recommend TMDB movies similar to one you liked, from descriptions alone:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies["description"] = movies["tagline"].fillna("") + " " + movies["overview"].fillna("")
tv = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
tfidf = tv.fit_transform(movies["description"].map(normalize))
sim = cosine_similarity(tfidf)                     # 4,800 x 4,800

def recommend(title, k=5):
    i = movies.index[movies.title == title][0]
    best = np.argsort(-sim[i])[1:k + 1]            # skip itself
    return movies.title.iloc[best].tolist()

recommend("Minions")   # other animated family films: 'Despicable Me 2', ...
```

He then swaps cosine for **BM25**, the probabilistic ranking function behind classic search engines:

$$\text{BM25}(q, d) = \sum_{t \in q} \text{idf}(t) \cdot \frac{f(t, d)\,(k_1 + 1)}{f(t, d) + k_1\left(1 - b + b \frac{|d|}{\text{avgdl}}\right)}$$

$k_1 \approx 1.2$–2 saturates term frequency; $b \approx 0.75$ normalises for document length. BM25 is still the lexical half of hybrid retrieval.

| Recommender type | Uses | Cold start |
|---|---|---|
| Content-based (this section) | Item features (text) | Works for new items, not new users |
| Collaborative filtering ([05](05-unsupervised-learning.md#recommender-systems-ng-ex8-part-2)) | User–item ratings | Fails for new items and users |
| Hybrid | Both | |

---

## The bridge to retrieval

Everything in RAG is here in small: documents become vectors (TF-IDF, BM25, or a neural encoder), a query becomes a vector, cosine similarity ranks candidates, and hybrid systems fuse lexical (BM25) and dense scores. The jump is in the encoder: contextual sentence embeddings trained contrastively (like the triplet-loss face embeddings in [07](07-neural-networks-fundamentals.md#convolutional-networks-dl-course-4)) instead of averaged word vectors. Continue in `../../generative-ai/02-rag-retrieval/README.md`.

---

## Practice

| Notebook | Covers | Runs |
|---|---|---|
| [`Ch04b - Advanced Deep Learning Strategies`](../practice/Text%20Analytics%20with%20Python/Ch04%20-%20Feature%20Engineering%20for%20Text%20Representation/Ch04b%20-%20Feature%20Engineering%20Text%20Data%20-%20Advanced%20Deep%20Learning%20Strategies.ipynb) | CBOW and skip-gram in Keras, gensim word2vec, document vectors, GloVe via spaCy, FastText | Needs `nltk` Gutenberg data, spaCy `en_vecs` (→ `en_core_web_md`); standalone `keras` 2.x; gensim 3 argument names (`size`, `iter`) |
| [`Ch07a`](../practice/Text%20Analytics%20with%20Python/Ch07%20-%20Text%20Similarity%20and%20Clustering/), `Ch07b` | Distance metrics, TF-IDF movie recommender, BM25 | Runs offline; `tmdb_5000_movies.csv.gz` included |
| [`Operations on word vectors - v2`](../Ng's%20Deep%20Learning%20Nbks/Sequence%20Models/Week2/Word%20Vector%20Representation/Operations%20on%20word%20vectors%20-%20v2.ipynb), [`Emojify - v2`](../Ng's%20Deep%20Learning%20Nbks/Sequence%20Models/Week2/Emojify/Emojify%20-%20v2.ipynb) (own) | Cosine, analogies, debiasing; GloVe-based classifier | Legacy: needs the course's `w2v_utils`/`emo_utils` and `glove.6B.50d.txt` (not in the repo) |

---

→ Next: [12-semantic-analysis-and-ner.md](12-semantic-analysis-and-ner.md) — meaning beyond vectors: WordNet, named entities, taggers and semantic representations.
