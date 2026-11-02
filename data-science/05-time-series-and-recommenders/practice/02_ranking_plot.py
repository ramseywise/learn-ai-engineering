# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scipy", "matplotlib"]
# ///
"""Measured figure for notes/02: ranking quality against catalogue coverage on MovieLens 100K.

Run from this folder (about two minutes, the SGD and BPR loops are plain Python):
    uv run 02_ranking_plot.py

Models and settings from the note. Random is left out: coverage 0.995 at NDCG 0.005 would flatten the
rest. Writes recsys-ranking-coverage.png.
"""
# %%
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import chartstyle as cs
import matplotlib.pyplot as plt
from movielens import chrono_split, evaluate, fit_ease, load, positives, to_matrix

ratings, items, _ = load()
n_users, n_items = ratings.user.max() + 1, ratings.item.max() + 1
shape = (n_users, n_items)
train, valid, test = chrono_split(ratings)
pos = train[train.rating >= 4]
R, seen = to_matrix(pos, shape), to_matrix(train, shape)
truth = positives(test)
mu = train.rating.mean()


def fit_mf(tr, k=20, lr=.01, reg=.05, epochs=30, seed=0):
    rng = np.random.default_rng(seed)
    P, Q = rng.normal(0, .1, (n_users, k)), rng.normal(0, .1, (n_items, k))
    bu_, bi_ = np.zeros(n_users), np.zeros(n_items)
    u, i, r = tr.user.to_numpy(), tr.item.to_numpy(), tr.rating.to_numpy(dtype=float)
    for _ in range(epochs):
        for j in rng.permutation(len(r)):
            a, b = u[j], i[j]
            e = r[j] - (mu + bu_[a] + bi_[b] + P[a] @ Q[b])
            bu_[a] += lr * (e - reg * bu_[a]); bi_[b] += lr * (e - reg * bi_[b])
            pa = P[a].copy()
            P[a] += lr * (e * Q[b] - reg * P[a]); Q[b] += lr * (e * pa - reg * Q[b])
    return P, Q, bu_, bi_


def fit_item_knn(R, k=50, shrink=10.0):
    C = (R.T @ R).toarray().astype(float)
    d = np.sqrt(np.diag(C)); np.fill_diagonal(C, 0)
    S = C / (np.outer(d, d) + shrink)
    for j in range(S.shape[1]):
        col = S[:, j]; col[np.argsort(col)[:-k]] = 0
    return S


def fit_ials(R, k=40, alpha=1.0, reg=5.0, sweeps=15, seed=0):
    rng = np.random.default_rng(seed)
    U, V = rng.normal(0, .1, (n_users, k)), rng.normal(0, .1, (n_items, k))
    Rc, Rt = R.tocsr(), R.T.tocsr()
    I = np.eye(k) * reg

    def sweep(X, Y, M):
        YtY = Y.T @ Y
        for a in range(X.shape[0]):
            idx = M[a].indices
            if len(idx) == 0:
                continue
            Yi = Y[idx]
            X[a] = np.linalg.solve(YtY + alpha * Yi.T @ Yi + I, (1 + alpha) * Yi.sum(0))
    for _ in range(sweeps):
        sweep(U, V, Rc); sweep(V, U, Rt)
    return U, V


def fit_bpr(R, k=40, lr=.05, reg=.002, epochs=40, seed=0):
    rng = np.random.default_rng(seed)
    U, V = rng.normal(0, .1, (n_users, k)), rng.normal(0, .1, (n_items, k))
    b = np.zeros(n_items)
    us, its = R.nonzero(); seen_set = set(zip(us.tolist(), its.tolist()))
    for _ in range(epochs):
        for j in rng.permutation(len(us)):
            u, i = us[j], its[j]
            while True:
                n = rng.integers(1, n_items)
                if (u, n) not in seen_set:
                    break
            g = 1 / (1 + np.exp(U[u] @ (V[i] - V[n]) + b[i] - b[n]))
            b[i] += lr * (g - reg * b[i]); b[n] += lr * (-g - reg * b[n])
            ui = U[u].copy()
            U[u] += lr * (g * (V[i] - V[n]) - reg * U[u])
            V[i] += lr * (g * ui - reg * V[i]); V[n] += lr * (-g * ui - reg * V[n])
    return U, V, b


counts = np.asarray(R.sum(0)).ravel()
P, Q, bu, bi = fit_mf(train)
Sk, B = fit_item_knn(R), fit_ease(R)
U, V = fit_ials(R)
Ub, Vb, bb = fit_bpr(R)
models = {
    "EASE": lambda us: R[us] @ B,
    "Item kNN": lambda us: R[us] @ Sk,
    "Implicit ALS": lambda us: U[us] @ V.T,
    "BPR": lambda us: Ub[us] @ Vb.T + bb,
    "Popularity": lambda us: np.tile(counts, (len(us), 1)),
    "MF on ratings": lambda us: mu + bu[us, None] + bi[None, :] + P[us] @ Q.T,
}
table = {name: evaluate(f, truth, seen) for name, f in models.items()}
for name, r in table.items():
    print(f"{name:<14} recall {r['recall']:.4f} ndcg {r['ndcg']:.4f} coverage {r['coverage']:.4f}")

# %%
cs.apply()
fig, ax = plt.subplots()
offs = {"EASE": (0, 10, "center"), "Item kNN": (-9, -3, "right"), "Implicit ALS": (9, 4, "left"), "BPR": (9, 0, "left"), "Popularity": (9, 0, "left"), "MF on ratings": (9, 0, "left")}
for name, r in table.items():
    colour = cs.BLUE if name not in ("Popularity", "MF on ratings") else cs.MUTED
    ax.scatter(r["coverage"], r["ndcg"], s=70, color=colour, edgecolor=cs.SURFACE, lw=1.2, zorder=3)
    dx, dy, ha = offs[name]
    ax.annotate(f"{name} {r['ndcg']:.3f}", (r["coverage"], r["ndcg"]), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center")
ax.set(xlabel="Share of the catalogue ever recommended (coverage)", ylabel="NDCG@10", xlim=(0, .4), ylim=(0, .15))
ax.grid(True, axis="x")
ax.set_title("Quality and coverage are separate axes: 861 users, full-catalogue top-10")
cs.save(fig, "recsys-ranking-coverage.png")
