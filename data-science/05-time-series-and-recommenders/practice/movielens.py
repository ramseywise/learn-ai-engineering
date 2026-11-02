"""Shared MovieLens 100K setup for the recommender labs: data, split, metrics, baselines.

The data is downloaded from GroupLens on first use and cached outside the repo, because its
licence forbids redistribution. Please read the README inside the zip before using it.
"""
import urllib.request, zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

CACHE = Path.home() / ".cache" / "learn-ai-engineering"
URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
GENRES = [f"g{i}" for i in range(19)]


def load():
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "ml-100k.zip"
    if not path.exists():
        path.write_bytes(urllib.request.urlopen(URL, timeout=60).read())
    with zipfile.ZipFile(path) as z:
        ratings = pd.read_csv(z.open("ml-100k/u.data"), sep="\t", names=["user", "item", "rating", "ts"])
        items = pd.read_csv(z.open("ml-100k/u.item"), sep="|", encoding="latin-1", header=None,
                            names=["item", "title", "date", "video", "url"] + GENRES)
        users = pd.read_csv(z.open("ml-100k/u.user"), sep="|", header=None,
                            names=["user", "age", "gender", "occupation", "zip"])
    return ratings, items, users


def chrono_split(ratings):
    """Each user's oldest 80% train, next 10% validate, newest 10% test."""
    r = ratings.sort_values(["user", "ts"])
    frac = (r.groupby("user").cumcount() + 1) / r.groupby("user").user.transform("size")
    return r[frac <= 0.8], r[(frac > 0.8) & (frac <= 0.9)], r[frac > 0.9]


def to_matrix(df, shape):
    return sparse.csr_matrix((np.ones(len(df)), (df.user, df.item)), shape=shape)


def positives(df):
    return df[df.rating >= 4].groupby("user").item.apply(set).to_dict()


def evaluate(score_fn, truth, seen, k=10):
    """Rank the whole catalogue minus what each user has seen. Item ids start at 1."""
    us = np.array(sorted(truth))
    S = np.asarray(score_fn(us), dtype=float).copy()
    S[seen[us].nonzero()] = -np.inf
    S[:, 0] = -np.inf
    top = np.argpartition(-S, k, axis=1)[:, :k]
    top = np.take_along_axis(top, np.argsort(-np.take_along_axis(S, top, 1), axis=1), 1)
    disc = 1 / np.log2(np.arange(2, k + 2))
    rec, ndcg, shown = [], [], set()
    for row, u in zip(top, us):
        hits = np.array([i in truth[u] for i in row], dtype=float)
        m = min(k, len(truth[u]))
        rec.append(hits.sum() / m)
        ndcg.append((hits * disc).sum() / disc[:m].sum())
        shown.update(row.tolist())
    return dict(recall=float(np.mean(rec)), ndcg=float(np.mean(ndcg)), coverage=len(shown) / (S.shape[1] - 1))


def fit_ease(R, lam=100.0):
    """Closed-form item-item model with a zero diagonal (Steck, WWW 2019)."""
    G = (R.T @ R).toarray().astype(float)
    G[np.diag_indices_from(G)] += lam
    P = np.linalg.inv(G)
    B = -P / np.diag(P)
    np.fill_diagonal(B, 0)
    return B
