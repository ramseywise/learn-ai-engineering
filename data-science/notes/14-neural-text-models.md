---
origin: vendored snapshots: Text Analytics with Python (kept), own coursework: intro-to-nlp (kept as practice); own notebook
sources:
  - ../practice/Text Analytics with Python/Ch10 - The Promise of Deep Learning/
  - ../practice/deep-learning-starter-simple-lstm.ipynb
  - ../sources/building-ai-agents-llms-rag-kgs/ch01-analyzing-text-data-deep-learning.pdf
  - ../sources/buduma-fundamentals-of-deep-learning.pdf
  - ../practice/intro-to-nlp/tensorFlow/ (tensor intro, pipeline review, RNN classification, LSTM text generation)
  - ../practice/intro-to-nlp/transformers/transformers_models_apis.ipynb
  - https://huggingface.co/docs/transformers/main_classes/pipelines
confidence: high
cleaned: 2026-10-31
---
# 14 — Neural Text Models

> From bags of words to models that read in order. Recurrent networks (RNN, LSTM, GRU) and 1-D convolutions over learned embeddings, next-word text generation with an LSTM, transfer learning with pre-trained sentence encoders, and finally pre-trained transformers behind a one-line `pipeline()`. This is the last stop before building a language model from scratch in [15](15-micrograd.md)–[17](17-nanogpt.md).

---

## Tensors and the Keras text pipeline

The intro-to-nlp TensorFlow track opened with tensors: rank (0 scalar, 1 vector, 2 matrix, 3+), `dtype`, `shape`, conversion with `.numpy()`, `tf.argmax`, `tf.reduce_max`, and the fact that `tf.constant` is immutable while `tf.Variable` can be assigned. Everything below is a stack of such tensors with a batch axis first: text batches are `(batch, seq_len)` token ids, embedded to `(batch, seq_len, d)`.

The repeated end-to-end recipe, which every notebook in this note follows:

```python
import tensorflow as tf
from tensorflow import keras

vocab_size, max_length, embedding_dim = 10_000, 250, 16
vectorize = keras.layers.TextVectorization(max_tokens=vocab_size, output_sequence_length=max_length)
vectorize.adapt(train_texts)          # learns the vocabulary from TRAIN only; index 1 is [UNK] (the old oov_token)

model = keras.Sequential([
    keras.Input(shape=(1,), dtype=tf.string),
    vectorize,                                                    # raw strings in: no separate preprocessing path
    keras.layers.Embedding(vocab_size, embedding_dim, mask_zero=True),
    keras.layers.Bidirectional(keras.layers.LSTM(64)),
    keras.layers.Dense(64, activation="relu"),
    keras.layers.Dense(1, activation="sigmoid"),
])
model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
history = model.fit(train_texts, train_labels, epochs=10,
                    validation_data=(val_texts, val_labels),
                    callbacks=[keras.callbacks.EarlyStopping(patience=2, restore_best_weights=True)])
```

The notebooks used the older `Tokenizer(num_words=10000, oov_token="<OOV>")` + `texts_to_sequences` + `pad_sequences(maxlen=250, padding="post", truncating="post")`. Those live in `tf.keras.preprocessing`, which is deprecated and absent from Keras 3; [08](08-text-representation.md) has the mapping.

Choices that matter:

| Setting | Effect | Typical |
|---|---|---|
| `vocab_size` | Rare words become `[UNK]` | 10k–30k for reviews |
| `max_length`, truncation side | Long reviews lose their end (`post`) or beginning (`pre`); the verdict is often at the end | Cover the 90th percentile of lengths |
| `embedding_dim` | Capacity of each word vector | 16–300 |
| `mask_zero=True` | Recurrent layers skip padding | On for RNNs |
| Pre-trained embeddings | `Embedding(..., embeddings_initializer=Constant(glove_matrix), trainable=False)` | Helps with small data ([11](11-embeddings-and-similarity.md)) |

---

## Recurrent networks

An RNN reads one token at a time and carries a hidden state:

```
h_t = tanh(W_x x_t + W_h h_{t-1} + b)        # same weights at every step
```

The state is a running summary of everything read so far; the last state (or a pooling of all states) feeds the classifier. Training unrolls the loop and backpropagates through time, so the gradient for an early word is a product of many `W_h`-dependent Jacobians, which shrinks or explodes. A plain `SimpleRNN` effectively forgets anything more than 10–20 tokens back.

### LSTM and GRU

The **LSTM** adds a cell state `c_t` that is updated additively, with gates deciding what to forget, what to write, and what to expose:

```
f_t = σ(W_f [h_{t-1}, x_t] + b_f)          # forget gate
i_t = σ(W_i [h_{t-1}, x_t] + b_i)          # input gate
g_t = tanh(W_g [h_{t-1}, x_t] + b_g)       # candidate values
c_t = f_t ⊙ c_{t-1} + i_t ⊙ g_t            # additive update: gradients flow through ⊙ f_t, not through a squashing matrix
o_t = σ(W_o [h_{t-1}, x_t] + b_o)
h_t = o_t ⊙ tanh(c_t)
```

The **GRU** merges the forget and input gates into one update gate and drops the separate cell state: fewer parameters, usually similar accuracy.

| Layer | Params for input d, units n | Notes |
|---|---|---|
| `SimpleRNN(n)` | n(d + n + 1) | Vanishing gradients; a teaching device |
| `LSTM(n)` | 4 n(d + n + 1) | The default recurrent layer through 2017 |
| `GRU(n)` | 3 n(d + n + 1) (+ bias detail) | Cheaper LSTM |
| `Bidirectional(LSTM(n))` | 2× | Reads both ways, output 2n; for classification, not generation |
| Stacked: `LSTM(n, return_sequences=True)` then `LSTM(n)` | — | Lower layer must return the full sequence |

Ng's Sequence Models course builds the RNN and LSTM cells by hand in NumPy ([07](07-neural-networks-fundamentals.md#tensorflow-1x-to-2x-status-and-migration-map) lists those notebooks).

### 1-D convolutions

`Conv1D(128, 5)` slides 128 filters over windows of 5 embeddings; each filter becomes an n-gram detector, and `GlobalMaxPooling1D` keeps the strongest match anywhere in the text. CNNs are fast (parallel over positions) and match LSTMs on classification where local phrases decide the label, but they have no long-range memory.

### Results on IMDb in the intro-to-nlp notebooks

The RNN classification notebook (`vocab_size=10000`, `embedding_dim=16`, `max_length=250`) compared architectures. Typical outcomes:

| Model | Val accuracy | Training behaviour |
|---|---|---|
| Embedding + GlobalAveragePooling + Dense | ~0.87 | Seconds per epoch; overfits after epoch 2–3 |
| Embedding + Conv1D + GlobalMaxPooling | ~0.88 | Fast, overfits quickly |
| Embedding + Bidirectional LSTM(64) | ~0.87–0.89 | Slowest; validation loss rises while training accuracy hits 0.99 |
| TF-IDF bigrams + logistic regression ([09](09-text-classification.md)) | ~0.90 | No GPU, no tuning |

The lesson the curves teach: on 25k labelled reviews, a model that learns its embeddings from scratch has too many parameters for the data, and overfitting dominates. Pre-training (below) is what changed that.

---

## Text generation with an LSTM

The same layers, trained to predict the next word, become a language model. The intro-to-nlp notebook trained on a file of Irish song lyrics:

```python
corpus = open("irish-lyrics.txt").read().lower().split("\n")
tok = Tokenizer(); tok.fit_on_texts(corpus)
total_words = len(tok.word_index) + 1

# every prefix of every line is a training example: [w1] → w2, [w1 w2] → w3, ...
seqs = [ids[:i + 1] for line in corpus for ids in [tok.texts_to_sequences([line])[0]] for i in range(1, len(ids))]
max_len = max(map(len, seqs))
seqs = pad_sequences(seqs, maxlen=max_len, padding="pre")         # pre-padding: the target is always the last column
X, y = seqs[:, :-1], seqs[:, -1]

model = keras.Sequential([
    keras.layers.Embedding(total_words, 100),
    keras.layers.Bidirectional(keras.layers.LSTM(150)),
    keras.layers.Dense(total_words, activation="softmax"),         # a distribution over the next word
])
model.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
model.fit(X, y, epochs=100)                                        # notebook: to_categorical + 10 epochs

seed = "I too am a human being and I"
for _ in range(100):
    ids = pad_sequences([tok.texts_to_sequences([seed])[0]], maxlen=max_len - 1, padding="pre")
    next_id = int(np.argmax(model.predict(ids, verbose=0)))        # greedy: picks the single most likely word
    seed += " " + tok.index_word[next_id]
```

What goes wrong and why it matters for what follows:

| Symptom | Cause | Fix (and where it reappears) |
|---|---|---|
| Output loops ("the the the", repeated lines) | Greedy `argmax` | Sample from the softmax with a temperature; top-k / top-p ([17](17-nanogpt.md)) |
| Grammatical for a few words, then drifts | Small corpus; context is one line | More data, longer context |
| Huge output layer | Word-level vocabulary | Character or subword tokens ([16](16-makemore.md), BPE in [17](17-nanogpt.md)) |
| Bidirectional generator | Uses the future at training time but not at sampling | Causal (left-to-right) models only |

This is the same task, next-token prediction trained with cross-entropy, that makemore and nanoGPT solve with better architectures.

---

## LSTMs beyond text: sequence regression in PyTorch

The own notebook `deep-learning-starter-simple-lstm` is a Kaggle starter for the **Ventilator Pressure Prediction** competition: predict airway pressure at each of 80 time steps of a simulated breath from the control inputs (`u_in`, `u_out`) and lung attributes (`R`, `C`). It is not NLP, but it is the cleanest PyTorch LSTM in the folder:

```python
class RNNModel(nn.Module):
    def __init__(self, input_dim=5, dense_dim=512, lstm_dim=512, logit_dim=512, num_classes=1):
        super().__init__()
        self.mlp = nn.Sequential(nn.Linear(input_dim, dense_dim // 2), nn.ReLU(),
                                 nn.Linear(dense_dim // 2, dense_dim), nn.ReLU())
        self.lstm = nn.LSTM(dense_dim, lstm_dim, batch_first=True, bidirectional=True)
        self.logits = nn.Sequential(nn.Linear(lstm_dim * 2, logit_dim), nn.ReLU(),
                                    nn.Linear(logit_dim, num_classes))
    def forward(self, x):                      # x: (batch, 80, input_dim)
        h, _ = self.lstm(self.mlp(x))          # (batch, 80, 2*lstm_dim): an output for EVERY step
        return self.logits(h)                  # (batch, 80, 1)

class VentilatorLoss(nn.Module):
    """Optimise the competition metric directly: MAE on the inspiratory phase only."""
    def __call__(self, preds, y, u_out):
        w = 1 - u_out                          # u_out == 0 during inspiration
        return ((w * (y - preds).abs()).sum(-1) / w.sum(-1))
```

Worth copying: a per-step MLP before the LSTM, a masked loss that matches the metric, `GroupKFold` by `breath_id` so no breath is in both train and validation ([04](04-model-evaluation.md)), `seed_everything` plus deterministic cuDNN, and a linear warm-up scheduler. `Bidirectional` is legitimate here because the whole breath is known at prediction time.

---

## Transfer learning with sentence encoders (Sarkar ch. 10a)

Instead of learning embeddings from 25k reviews, start from an encoder pre-trained on billions of sentences and train only a small head. Sarkar compares encoders from TensorFlow Hub on IMDb with the same `DNNClassifier(hidden_units=[512, 128])` head:

| Encoder | Output | Frozen vs fine-tuned |
|---|---|---|
| NNLM (`nnlm-en-dim128`) | 128-d, a feed-forward language model's embedding | Fine-tuning adds a few points |
| Universal Sentence Encoder (`universal-sentence-encoder/2`) | 512-d, transformer/DAN trained on many tasks | Best: ~0.86 frozen, ~0.90 fine-tuned |

![Accuracy of IMDb classifiers built on different TF-Hub sentence encoders, frozen vs fine-tuned](../sources/images/sarkar-universal-embeddings-classification.png)
*Image source: Sarkar, Text Analytics with Python (2nd ed.), ch. 10 figure*

The modern equivalent is three lines and needs no TF 1.x estimator:

```python
from sentence_transformers import SentenceTransformer
enc = SentenceTransformer("all-MiniLM-L6-v2")                   # 384-d, runs on CPU
X_train = enc.encode(train_texts, batch_size=64, show_progress_bar=True)
clf = LogisticRegression(max_iter=1000).fit(X_train, train_labels)   # frozen encoder + linear head
```

A frozen pre-trained encoder plus logistic regression is a strong baseline for any small labelled text set, and the same vectors power semantic search ([11](11-embeddings-and-similarity.md), [`../../generative-ai/02-rag-retrieval/README.md`](../../generative-ai/02-rag-retrieval/README.md)).

---

## Transformers pipelines

The intro-to-nlp transformers notebook (from the Hugging Face course, chapter on `pipeline`) ran eight tasks with defaults:

```python
from transformers import pipeline

pipeline("sentiment-analysis")("I've been waiting for a HuggingFace course my whole life.")
# [{'label': 'POSITIVE', 'score': 0.96}]
pipeline("ner", aggregation_strategy="simple")("My name is Sylvain and I work at Hugging Face in Brooklyn.")
# [{'entity_group': 'PER', 'word': 'Sylvain'}, {'entity_group': 'ORG', ...}, {'entity_group': 'LOC', ...}]
pipeline("question-answering")(question="Where do I work?", context="I work at Hugging Face in Brooklyn.")
pipeline("fill-mask")("This course will teach you all about <mask> models.", top_k=2)
pipeline("summarization")(long_text)
pipeline("translation_en_to_fr")("How old are you?")
pipeline("text-generation", model="gpt2")("In this course, we will teach you how to", max_new_tokens=30)
pipeline("feature-extraction")(text)            # raw hidden states: (1, n_tokens, 768)
pipeline("zero-shot-classification")(text, candidate_labels=["education", "politics", "business"])
```

| Task | Default model family | Architecture | Earlier note |
|---|---|---|---|
| sentiment-analysis | DistilBERT fine-tuned on SST-2 | Encoder | [13](13-sentiment-analysis.md) |
| ner | BERT fine-tuned on CoNLL-03 | Encoder | [12](12-semantic-analysis-and-ner.md) |
| question-answering | DistilBERT on SQuAD (extractive span) | Encoder | — |
| fill-mask | DistilRoBERTa | Encoder (masked LM) | — |
| summarization, translation | BART / T5 | Encoder–decoder | [10](10-topic-models-and-summarization.md) |
| text-generation | GPT-2 | Decoder (causal LM) | [17](17-nanogpt.md) |
| zero-shot-classification | BART-large-MNLI | Encoder–decoder, NLI trick | [09](09-text-classification.md) |

Pin a `model=` in anything you keep; defaults change between library versions. A pipeline is tokenizer → model → post-processing; open it up with `AutoTokenizer` / `AutoModelForSequenceClassification` when you need batching control or fine-tuning (`Trainer`).

---

## TensorFlow status of the text notebooks

| Notebook | API era | Status |
|---|---|---|
| Sarkar `Ch10a` (universal embeddings) | `tf.estimator`, `hub.text_embedding_column`, `tf.estimator.inputs.numpy_input_fn` | Partly migrated: the confusion-matrix cell uses `tf.math.confusion_matrix(...).numpy()`, but the estimator API was removed in TF 2.16 and the TF-Hub v1 modules need `tensorflow_hub` with TF ≤ 2.15. Read for the idea; use `sentence-transformers` to run it |
| Sarkar `Ch04b`, `Ch09b`, `Ch09c` | Standalone `keras` 2.x, `keras.layers.normalization`, `predict_classes` | Legacy; port to `tensorflow.keras` / Keras 3 |
| Kaggle NLP notebook | `keras.layers.recurrent`, standalone keras | Legacy ([09](09-text-classification.md)) |
| intro-to-nlp (practice) | `tf.keras` 2.x with `preprocessing.text.Tokenizer` | Snippets in this note use `TextVectorization` |
| Ng Sequence Models | standalone `keras` 2.x, TF 1.x backend | Legacy, reading-only ([07](07-neural-networks-fundamentals.md#tensorflow-1x-to-2x-status-and-migration-map)) |
| own `deep-learning-starter-simple-lstm` | PyTorch + `transformers` scheduler | Current |

The general TF 1.x → 2.x map (sessions, placeholders, `tf.contrib`) is in [07](07-neural-networks-fundamentals.md#tensorflow-1x-to-2x-status-and-migration-map).

---

## What attention fixed

An encoder RNN squeezes a whole sentence into one final state, and its steps cannot run in parallel. Attention lets every position look directly at every other position with learned weights, and the transformer drops recurrence entirely. Building that from scratch, one piece at a time, is the job of the next three notes: autograd ([15](15-micrograd.md)), language-model training ([16](16-makemore.md)), and the transformer itself ([17](17-nanogpt.md)). The LLM-level view continues in [`../../generative-ai/01-llm-fundamentals/README.md`](../../generative-ai/01-llm-fundamentals/README.md).

**Reading:** Building AI Agents with LLMs, RAG, and Knowledge Graphs, ch. 1 ([PDF](../sources/building-ai-agents-llms-rag-kgs/ch01-analyzing-text-data-deep-learning.pdf)) walks the same arc, from one-hot and TF-IDF through word2vec to RNN, LSTM, GRU and CNN text classifiers. Buduma, *Fundamentals of Deep Learning* ([PDF](../sources/buduma-fundamentals-of-deep-learning.pdf)), covers the recurrent and embedding chapters in more depth.

---

## Practice

| Notebook | Covers | Runs |
|---|---|---|
| [`Ch10a - Text Classification with Universal Embeddings`](../practice/Text%20Analytics%20with%20Python/Ch10%20-%20The%20Promise%20of%20Deep%20Learning/Ch10a%20-%20Deep%20Transfer%20Learning%20for%20NLP%20-%20Text%20Classification%20with%20Universal%20Embeddings.ipynb) | TF-Hub NNLM and USE encoders, frozen vs fine-tuned | Legacy: needs TF ≤ 2.15 + `tensorflow_hub`, internet for the modules, GPU recommended, IMDb `movie_reviews.csv` (not in this snapshot) |
| [`deep-learning-starter-simple-lstm`](../practice/deep-learning-starter-simple-lstm.ipynb) | PyTorch BiLSTM sequence regression, masked loss, GroupKFold | Needs data: Kaggle `ventilator-pressure-prediction`; GPU (5 folds × 200 epochs); `transformers` for the scheduler |

The intro-to-nlp TensorFlow notebooks are in [`practice/intro-to-nlp/tensorFlow/`](../practice/intro-to-nlp/tensorFlow/) and the transformers notebook in [`practice/intro-to-nlp/transformers/`](../practice/intro-to-nlp/transformers/). They use the older `Tokenizer` API.

---

→ Next: [15-micrograd.md](15-micrograd.md) — a scalar autograd engine in ~100 lines, the machinery under every model above.
