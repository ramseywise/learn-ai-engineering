#!/usr/bin/env python3
"""Experiments for notes/02-collaborative-filtering-and-matrix-factorisation.md.

Run from the pillar folder:
    uv run --with numpy --with pandas --with scipy python practice/02_cf_lab.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd
from movielens import chrono_split, evaluate, fit_ease, load, positives, to_matrix

ratings, items, _ = load()
shape = (ratings.user.max() + 1, ratings.item.max() + 1)
train, valid, test = chrono_split(ratings)
pos = train[train.rating >= 4]
R, seen = to_matrix(pos, shape), to_matrix(train, shape)
truth = positives(test)
B = fit_ease(R)
baseline = evaluate(lambda us: R[us] @ B, truth, seen)
print("EASE on the chapter's split            ", {k: round(v, 4) for k, v in baseline.items()})

print("\n-- exercise 1: leak the future with a random split")
perm = ratings.sample(frac=1, random_state=0)
n = len(perm)
tr_r, te_r = perm.iloc[: int(0.9 * n)], perm.iloc[int(0.9 * n):]
Rr, seen_r = to_matrix(tr_r[tr_r.rating >= 4], shape), to_matrix(tr_r, shape)
Br = fit_ease(Rr)
print("EASE on a random 90/10 split           ",
      {k: round(v, 4) for k, v in evaluate(lambda us: Rr[us] @ Br, positives(te_r), seen_r).items()})
cr = np.asarray(Rr.sum(0)).ravel()
print("popularity on a random 90/10 split     ",
      {k: round(v, 4) for k, v in evaluate(lambda us: np.tile(cr, (len(us), 1)), positives(te_r), seen_r).items()})

print("\n-- exercise 2: every rating counts as a signal of interest, even a 1")
Ra = to_matrix(train, shape)
Ba = fit_ease(Ra)
print("EASE trained on all ratings            ",
      {k: round(v, 4) for k, v in evaluate(lambda us: Ra[us] @ Ba, truth, seen).items()})

print("\n-- exercise 3: who gets the lift? split users by history length")
hist = np.asarray(seen.sum(1)).ravel()
cut = np.median([hist[u] for u in truth])
light = {u: s for u, s in truth.items() if hist[u] <= cut}
heavy = {u: s for u, s in truth.items() if hist[u] > cut}
counts = np.asarray(R.sum(0)).ravel()
for name, t in [("light users", light), ("heavy users", heavy)]:
    e = evaluate(lambda us: R[us] @ B, t, seen)["ndcg"]
    p = evaluate(lambda us: np.tile(counts, (len(us), 1)), t, seen)["ndcg"]
    print(f"{name:12s} n={len(t):3d}  popularity ndcg {p:.4f}  EASE ndcg {e:.4f}")
