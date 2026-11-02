# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "scikit-learn", "torch", "pandas", "matplotlib"]
# ///
"""Measured figure for notes/06: four text models on 5,000 reviews, train versus test.

Run from this folder (about three minutes on a CPU):
    uv run imdb_models.py

Reads ../../03-nlp/practice/intro-to-nlp/data/IMDB Dataset.csv, the file the note uses. Writes dl-imdb-models.png.
"""
# %%
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import chartstyle as cs
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

DATA = Path(__file__).resolve().parents[2] / "03-nlp/practice/intro-to-nlp/data/IMDB Dataset.csv"
df = pd.read_csv(DATA).sample(frac=1, random_state=0).reset_index(drop=True)
train, test = df[:5000], df[5000:10000]
train_texts, test_texts = train.review.tolist(), test.review.tolist()
train_labels = (train.sentiment == "positive").to_numpy().astype(int)
test_labels = (test.sentiment == "positive").to_numpy().astype(int)


def tokenize(s):
    return re.findall(r"[a-z']+", s.lower().replace("<br />", " "))


vocab_size, max_length, embedding_dim = 10_000, 250, 16
counts = Counter(w for s in train_texts for w in tokenize(s))
vocab = ["<pad>", "<unk>"] + [w for w, _ in counts.most_common(vocab_size - 2)]
stoi = {w: i for i, w in enumerate(vocab)}


def encode(s):
    ids = [stoi.get(w, 1) for w in tokenize(s)][:max_length]
    return ids + [0] * (max_length - len(ids))


X_tr, X_te = (torch.tensor([encode(s) for s in t]) for t in (train_texts, test_texts))
y_tr, y_te = torch.tensor(train_labels), torch.tensor(test_labels)


class Average(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.out = nn.Linear(embedding_dim, 2)

    def forward(self, x):
        mask = (x != 0).float()[..., None]
        return self.out((self.emb(x) * mask).sum(1) / mask.sum(1).clamp(min=1))


class TextCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.conv = nn.Conv1d(embedding_dim, 128, 5)
        self.out = nn.Linear(128, 2)

    def forward(self, x):
        return self.out(F.relu(self.conv(self.emb(x).transpose(1, 2))).amax(2))


class BiLSTM(nn.Module):
    def __init__(self, h=64):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.rnn = nn.LSTM(embedding_dim, h, batch_first=True, bidirectional=True)
        self.out = nn.Linear(2 * h, 2)

    def forward(self, x):
        n = (x != 0).sum(1).clamp(min=1).cpu()
        packed = nn.utils.rnn.pack_padded_sequence(self.emb(x), n, batch_first=True, enforce_sorted=False)
        _, (h, _) = self.rnn(packed)
        return self.out(torch.cat([h[0], h[1]], dim=1))


def accuracy(m, X, y, bs=500):
    m.eval()
    with torch.no_grad():
        return float(np.mean([(m(X[i:i+bs]).argmax(1) == y[i:i+bs]).float().mean().item() for i in range(0, len(X), bs)]))


def fit(m, epochs, lr):
    opt = torch.optim.Adam(m.parameters(), lr=lr)
    for _ in range(epochs):
        m.train()
        perm = torch.randperm(len(X_tr))
        for i in range(0, len(perm), 32):
            b = perm[i:i+32]
            loss = F.cross_entropy(m(X_tr[b]), y_tr[b])
            opt.zero_grad(); loss.backward(); opt.step()
    return m


rows = []
for name, build, epochs, lr in [("Average of embeddings", Average, 8, 3e-3), ("Text CNN", TextCNN, 5, 3e-3), ("BiLSTM", BiLSTM, 4, 3e-3)]:
    torch.manual_seed(0)
    m = fit(build(), epochs, lr)
    rows.append((name, accuracy(m, X_tr, y_tr), accuracy(m, X_te, y_te)))
    print(rows[-1], flush=True)
tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
A, B = tfidf.fit_transform(train_texts), tfidf.transform(test_texts)
clf = LogisticRegression(max_iter=1000, C=10).fit(A, train_labels)
rows.append(("TF-IDF bigrams + logistic", clf.score(A, train_labels), clf.score(B, test_labels)))
print(rows[-1])

# %%
cs.apply()
fig, ax = plt.subplots()
rows = sorted(rows, key=lambda r: r[2])
for i, (name, tr, te) in enumerate(rows):
    ax.plot([te, tr], [i, i], color=cs.BASELINE, lw=2, zorder=1)
    ax.scatter(te, i, s=70, color=cs.ORANGE, edgecolor=cs.SURFACE, lw=1.2, zorder=3, label="Test" if i == 0 else None)
    ax.scatter(tr, i, s=70, color=cs.BLUE, edgecolor=cs.SURFACE, lw=1.2, zorder=3, label="Train" if i == 0 else None)
    ax.annotate(f"{te:.3f}", (te, i), xytext=(-10, 0), textcoords="offset points", ha="right", va="center")
    ax.annotate(f"{tr:.3f}", (tr, i), xytext=(10, 0), textcoords="offset points", ha="left", va="center")
ax.set_yticks(range(len(rows)), [r[0] for r in rows])
ax.set(xlabel="Accuracy", xlim=(.65, 1.05))
ax.grid(False, axis="y"); ax.grid(True, axis="x"); ax.tick_params(axis="y", length=0)
ax.legend(loc="lower right", ncol=2)
ax.set_title("On 5,000 reviews, the gap is the story: the linear baseline wins on test")
cs.save(fig, "dl-imdb-models.png")
