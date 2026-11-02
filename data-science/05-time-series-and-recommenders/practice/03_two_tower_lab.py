#!/usr/bin/env python3
"""Experiments for notes/03-two-tower-and-evaluation.md.

Run from the pillar folder:
    uv run --with numpy --with pandas --with scipy --with torch python practice/03_two_tower_lab.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd
import torch
from torch import nn
from movielens import GENRES, chrono_split, evaluate, fit_ease, load, positives, to_matrix

ratings, items, users = load()
n_users, n_items = ratings.user.max() + 1, ratings.item.max() + 1
shape = (n_users, n_items)
train, valid, test = chrono_split(ratings)
pos = train[train.rating >= 4]
R, seen = to_matrix(pos, shape), to_matrix(train, shape)
truth_test, truth_valid = positives(test), positives(valid)

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


def train_tower(bs=512, tau=0.2, epochs=30, lr=2e-3, seed=0):
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
            opt.zero_grad()
            loss.backward()
            opt.step()
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


def simulate(explore, n_events=200_000, n_actions=20, seed=0):
    rng = np.random.default_rng(seed)
    ctr = rng.beta(1, 20, size=(5, n_actions))
    seg = rng.integers(0, 5, n_events)
    logging = np.full(n_actions, explore / n_actions)
    logging[np.argsort(-ctr.mean(0))[:5]] += (1 - explore) / 5
    act = rng.choice(n_actions, n_events, p=logging)
    click = rng.random(n_events) < ctr[seg, act]
    target = ctr.argmax(1)
    w = (act == target[seg]) / logging[act]
    print(f"explore {explore:.2f}: truth {ctr[np.arange(5), target].mean():.4f}  IPS {(w * click).mean():.4f}  "
          f"SNIPS {(w * click).sum() / w.sum():.4f}  max weight {w.max():.0f}  ESS {w.sum() ** 2 / (w ** 2).sum():.0f}")


print("-- exercise 1: batch size (validation NDCG@10)")
for bs in (128, 512, 2048):
    r = evaluate(scores(train_tower(bs=bs)), truth_valid, seen)
    print(f"batch {bs:5d}  ndcg {r['ndcg']:.4f}  coverage {r['coverage']:.3f}")

print("\n-- exercise 2: 99 versus 999 sampled negatives (test HR@10)")
B = fit_ease(R)
tower = scores(train_tower())
for name, f in [("EASE", lambda us: R[us] @ B), ("two-tower logQ", tower)]:
    full, s99 = hit_rates(f, 99)
    _, s999 = hit_rates(f, 999)
    print(f"{name:16s} full {full:.4f}  sampled-99 {s99:.4f}  sampled-999 {s999:.4f}")

print("\n-- exercise 3: starve the estimator")
for explore in (0.2, 0.05, 0.02):
    simulate(explore)
