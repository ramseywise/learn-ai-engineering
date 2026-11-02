# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scikit-learn", "sentence-transformers", "matplotlib"]
# ///
"""Measured figure for notes/07: macro-F1 against labelled films, TF-IDF versus MiniLM embeddings.

Run from this folder (a few minutes; embedding is cached after the first run):
    uv run labels_vs_f1.py

The note's split, grids and five repeats. Writes nlp-labels-vs-f1.png.
"""
# %%
import json
from pathlib import Path

import numpy as np
import pandas as pd
import chartstyle as cs
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline

DATA = Path(__file__).parent / "text-analytics-with-python/Ch07 - Text Similarity and Clustering/tmdb_5000_movies.csv.gz"
movies = pd.read_csv(DATA)
movies["description"] = (movies["tagline"].fillna("") + " " + movies["overview"].fillna("")).str.strip()
movies["genre_list"] = movies["genres"].map(lambda g: [x["name"] for x in json.loads(g)])
movies = movies[movies.genre_list.str.len() > 0].reset_index(drop=True)
movies["genre"] = movies.genre_list.str[0]

CACHE = Path.home() / ".cache/learn-ai-engineering"
CACHE.mkdir(parents=True, exist_ok=True)
path = CACHE / "tmdb-minilm.npy"
if path.exists():
    X_all = np.load(path)
else:
    from sentence_transformers import SentenceTransformer
    X_all = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu").encode(movies.description.tolist(), batch_size=64, normalize_embeddings=True)
    np.save(path, X_all)
assert len(X_all) == len(movies), "cached embeddings do not match the frame"

top = movies.genre.value_counts().head(6).index
idx = movies.index[movies.genre.isin(top)].to_numpy()
idx_train, idx_test = train_test_split(idx, test_size=.25, random_state=0, stratify=movies.genre[idx])
y = movies.genre.to_numpy()
text = movies.description.to_numpy()
Cs = [.1, 1, 10, 100]
cv = lambda: StratifiedKFold(3, shuffle=True, random_state=0)


def fit_minilm(rows):
    return GridSearchCV(LogisticRegression(max_iter=3000), {"C": Cs}, cv=cv(), scoring="f1_macro", n_jobs=4).fit(X_all[rows], y[rows])


def fit_tfidf(rows):
    pipe = make_pipeline(TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2)), LogisticRegression(max_iter=3000))
    return GridSearchCV(pipe, {"logisticregression__C": Cs}, cv=cv(), scoring="f1_macro", n_jobs=4).fit(text[rows], y[rows])


rng = np.random.RandomState(0)
sizes = [60, 150, 300, 600, 1200, len(idx_train)]
T, M = [], []
for n in sizes:
    t, m = [], []
    for _ in range(5 if n < len(idx_train) else 1):
        rows = train_test_split(idx_train, train_size=n, random_state=rng, stratify=y[idx_train])[0] if n < len(idx_train) else idx_train
        t.append(f1_score(y[idx_test], fit_tfidf(rows).predict(text[idx_test]), average="macro"))
        m.append(f1_score(y[idx_test], fit_minilm(rows).predict(X_all[idx_test]), average="macro"))
    T.append(np.mean(t)); M.append(np.mean(m))
    print(f"{n:5d} TF-IDF {T[-1]:.3f} +- {np.std(t):.3f}  MiniLM {M[-1]:.3f} +- {np.std(m):.3f}", flush=True)

# %%
cs.apply()
fig, ax = plt.subplots()
ax.plot(sizes, M, color=cs.BLUE, marker="o", ms=6, label="MiniLM embeddings + logistic")
ax.plot(sizes, T, color=cs.ORANGE, marker="o", ms=6, label="TF-IDF + logistic")
ax.set_xscale("log")
ax.set(xlabel="Labelled films (log scale)", ylabel="Test macro-F1, mean of five samples", xticks=sizes, xticklabels=[str(s) for s in sizes], ylim=(0, .6))
ax.minorticks_off()
ax.grid(False, axis="x")
for vals in (M, T):
    ax.annotate(f"{vals[0]:.3f}", (sizes[0], vals[0]), xytext=(0, 9), textcoords="offset points", ha="center")
    ax.annotate(f"{vals[-1]:.3f}", (sizes[-1], vals[-1]), xytext=(0, 9), textcoords="offset points", ha="center")
ax.legend(loc="lower right")
ax.set_title("With few labels, pretrained embeddings lead; the gap narrows as labels grow")
cs.save(fig, "nlp-labels-vs-f1.png")
