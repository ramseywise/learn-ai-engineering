# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scipy", "torch", "matplotlib"]
# ///
"""Measured figure for notes/03: HR@10 for EASE and a two-tower model as the negative sample grows.

Run from this folder (a few minutes):
    uv run 03_sampled_metric_plot.py

Two-tower with logQ correction, tau 0.2, seed 0, as in the note and 03_two_tower_lab.py.
Writes recsys-sampled-metric.png.
"""
# %%
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import chartstyle as cs
import matplotlib.pyplot as plt
from movielens import GENRES, chrono_split, fit_ease, load, positives, to_matrix

ratings, items, users = load()
n_users, n_items = ratings.user.max() + 1, ratings.item.max() + 1
shape = (n_users, n_items)
train, valid, test = chrono_split(ratings)
pos = train[train.rating >= 4]
R, seen = to_matrix(pos, shape), to_matrix(train, shape)
truth_test = positives(test)

items["year"] = pd.to_datetime(items["date"], errors="coerce").dt.year.fillna(1995)
item_feat = np.zeros((n_items, 20), dtype="float32")
item_feat[items.item, :19] = items[GENRES].to_numpy(dtype="float32")
item_feat[items.item, 19] = (items["year"] - 1990) / 10
user_num = np.zeros((n_users, 2), dtype="float32")
user_num[users.user, 0] = users.age / 50
user_num[users.user, 1] = users.gender == "M"
user_occ = np.zeros(n_users, dtype="int64")
user_occ[users.user] = users.occupation.astype("category").cat.codes.to_numpy() + 1


class TwoTower(nn.Module):
    def __init__(self, dim=64):
        super().__init__()
        self.uid, self.iid = nn.Embedding(n_users, dim), nn.Embedding(n_items, dim)
        self.occ = nn.Embedding(user_occ.max() + 1, 8)
        self.user_mlp = nn.Sequential(nn.Linear(dim + 10, 128), nn.ReLU(), nn.Linear(128, dim))
        self.item_mlp = nn.Sequential(nn.Linear(dim + 20, 128), nn.ReLU(), nn.Linear(128, dim))
        self.uf, self.uo, self.itf = map(torch.tensor, (user_num, user_occ, item_feat))

    def user(self, u):
        x = torch.cat([self.uid(u), self.occ(self.uo[u]), self.uf[u]], 1)
        return nn.functional.normalize(self.user_mlp(x), dim=1)

    def item(self, i):
        return nn.functional.normalize(self.item_mlp(torch.cat([self.iid(i), self.itf[i]], 1)), dim=1)


def train_tower(bs=512, tau=.2, epochs=30, lr=2e-3, seed=0):
    torch.manual_seed(seed)
    m = TwoTower()
    opt = torch.optim.Adam(m.parameters(), lr=lr, weight_decay=1e-5)
    u, i = torch.tensor(pos.user.to_numpy()), torch.tensor(pos.item.to_numpy())
    logp = torch.tensor(np.log(np.maximum(np.bincount(pos.item, minlength=n_items) / len(pos), 1e-9)), dtype=torch.float32)
    for _ in range(epochs):
        for b in torch.randperm(len(u)).split(bs):
            logits = m.user(u[b]) @ m.item(i[b]).T / tau - logp[i[b]]
            same = i[b][:, None] == i[b][None, :]
            same.fill_diagonal_(False)
            loss = nn.functional.cross_entropy(logits.masked_fill(same, -1e9), torch.arange(len(b)))
            opt.zero_grad(); loss.backward(); opt.step()
    return m.eval()


def scores(m):
    with torch.no_grad():
        V = m.item(torch.arange(n_items))

    def f(us):
        with torch.no_grad():
            return (m.user(torch.tensor(us)) @ V.T).numpy()
    return f


def hit_rates(score_fn, n_neg, k=10, seed=0):
    rng = np.random.default_rng(seed)
    us = np.array(sorted(truth_test))
    S = np.asarray(score_fn(us), dtype=float)
    full, sampled = [], []
    for row, u in enumerate(us):
        sn = set(seen[u].indices)
        cand = np.array([i for i in range(1, n_items) if i not in sn and i not in truth_test[u]])
        for p in truth_test[u]:
            neg = rng.choice(cand, min(n_neg, len(cand)), replace=False)
            full.append((S[row, cand] > S[row, p]).sum() < k)
            sampled.append((S[row, neg] > S[row, p]).sum() < k)
    return float(np.mean(full)), float(np.mean(sampled))


B = fit_ease(R)
tower = scores(train_tower())
negs = [49, 99, 199, 499, 999]
res = {}
for name, f in [("EASE", lambda us: R[us] @ B), ("Two-tower with logQ", tower)]:
    vals = [hit_rates(f, n) for n in negs]
    res[name] = ([v[1] for v in vals], vals[0][0])
    print(name, "full", round(vals[0][0], 4), {n: round(v[1], 4) for n, v in zip(negs, vals)}, flush=True)

# %%
cs.apply()
fig, ax = plt.subplots()
x = list(range(len(negs))) + [len(negs)]
labels = [str(n) for n in negs] + ["Full catalogue"]
for (name, (sampled, full)), colour in zip(res.items(), [cs.BLUE, cs.ORANGE]):
    ax.plot(x, sampled + [full], color=colour, marker="o", ms=6, label=name)
ax.set_xticks(x, labels)
ax.set(xlabel="Negatives each test item is ranked against", ylabel="HR@10", ylim=(0, .9))
ax.grid(False, axis="x")
a, b = res["EASE"], res["Two-tower with logQ"]
ax.annotate(f"99 negatives: EASE {a[0][1]:.3f}, tower {b[0][1]:.3f}", (1, max(a[0][1], b[0][1])), xytext=(14, 18), textcoords="offset points")
ax.annotate(f"Full: EASE {a[1]:.3f}, tower {b[1]:.3f}", (len(negs), .30), ha="right")
ax.legend(loc="upper right")
ax.set_title("Sampled hit rates run high, and the tower leads until 999 negatives. Full catalogue: EASE")
cs.save(fig, "recsys-sampled-metric.png")
