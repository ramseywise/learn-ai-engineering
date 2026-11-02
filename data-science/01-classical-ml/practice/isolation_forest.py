# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "scipy", "scikit-learn", "matplotlib"]
# ///
"""Numbers and figure for notes/05: an isolation forest beside the Gaussian detector on tabular data.

Run from this folder:
    uv run isolation_forest.py

ex8data1 is the data the note's Gaussian example uses; the other tables are generated, seeded, five seeds each.
Writes classical-iforest-limits.png.
"""
# %%
from pathlib import Path

import chartstyle as cs
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat
from scipy.stats import multivariate_normal
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).parent
SEEDS = range(5)


def best_f1(y, score):
    """Best F1 over thresholds on score, where higher means more anomalous. Same rule as the note's select_threshold."""
    best, at = 0, None
    for t in np.unique(score):
        pred = score >= t
        tp, fp, fn = (pred & (y == 1)).sum(), (pred & (y == 0)).sum(), (~pred & (y == 1)).sum()
        if tp and 2 * tp / (2 * tp + fp + fn) > best:
            best, at = 2 * tp / (2 * tp + fp + fn), t
    return best, at


def gauss_diag(Xtr):
    mu, var = Xtr.mean(0), Xtr.var(0)
    return lambda X: ((X - mu) ** 2 / (2 * var) + .5 * np.log(2 * np.pi * var)).sum(1)      # negative log density


def gauss_full(Xtr):
    d = multivariate_normal(Xtr.mean(0), np.cov(Xtr.T), allow_singular=True)
    return lambda X: -d.logpdf(X)


def iforest(Xtr, seed, psi=256, t=100):
    m = IsolationForest(n_estimators=t, max_samples=min(psi, len(Xtr)), random_state=seed).fit(Xtr)
    return lambda X: -m.score_samples(X)


# %% The same server data as the Gaussian example
ex = loadmat(HERE / "ng-machine-learning/ex8/data/ex8data1.mat")
X, Xval, yval = ex["X"], ex["Xval"], ex["yval"].ravel()
print(f"ex8: train {len(X)}, validation {len(Xval)}, validation anomalies {yval.sum()}")
for name, fit in [("Gaussian per feature", gauss_diag), ("Isolation forest", lambda x: iforest(x, 0))]:
    f = fit(X)
    f1, t = best_f1(yval, f(Xval))
    print(f"{name:<22} AUC {roc_auc_score(yval, f(Xval)):.3f}  best validation F1 {f1:.3f}  flagged in train {(f(X) >= t).sum()} of {len(X)}")
for s in range(5):
    f = iforest(X, s)
    print(f"  forest seed {s}: AUC {roc_auc_score(yval, f(Xval)):.3f}  F1 {best_f1(yval, f(Xval))[0]:.3f}")


# %% A table with two normal regimes
def regimes(seed, n=4000, d=6, skew=False):
    """Normal rows sit in two operating regimes. Two kinds of anomaly: far out in one column, and in the valley between."""
    r = np.random.default_rng(seed)
    side = r.random(n) < .5
    centre = np.where(side[:, None], 3.0, -3.0)
    normal = centre + r.normal(0, 1, (n, d))
    train, test = normal[:n // 2], normal[n // 2:]
    far = r.normal(0, 1, (100, d)) + np.where(r.random((100, 1)) < .5, 3.0, -3.0)
    far[np.arange(100), r.integers(0, d, 100)] += r.choice([-9, 9], 100)
    valley = r.normal(0, .35, (100, d))                 # every column near zero, where no normal row lives
    if skew:
        train, test, far, valley = [np.column_stack([np.exp(a[:, 0] / 2), a[:, 1:]]) for a in (train, test, far, valley)]
    return train, test, far, valley


rows = {k: {"far": [], "valley": []} for k in ["Gaussian per feature", "Gaussian, full covariance", "Isolation forest"]}
for s in SEEDS:
    tr, te, far, valley = regimes(s)
    fits = {"Gaussian per feature": gauss_diag(tr), "Gaussian, full covariance": gauss_full(tr), "Isolation forest": iforest(tr, s)}
    for k, f in fits.items():
        for kind, A in (("far", far), ("valley", valley)):
            y = np.r_[np.zeros(len(te)), np.ones(len(A))]
            rows[k][kind].append(roc_auc_score(y, f(np.vstack([te, A]))))
print("\ntwo regimes, six columns, mean AUC (sd) over five seeds")
for k, v in rows.items():
    print(f"{k:<26} far {np.mean(v['far']):.3f} ({np.std(v['far']):.3f})  valley {np.mean(v['valley']):.3f} ({np.std(v['valley']):.3f})")

g, h = [], []
for s in SEEDS:
    tr, te, far, valley = regimes(s, skew=True)
    A = np.vstack([far, valley])
    y = np.r_[np.zeros(len(te)), np.ones(len(A))]
    g.append(roc_auc_score(y, gauss_full(tr)(np.vstack([te, A]))))
    h.append(roc_auc_score(y, iforest(tr, s)(np.vstack([te, A]))))
print(f"one column on an exponential scale, both anomaly kinds: full Gaussian {np.mean(g):.3f}, forest {np.mean(h):.3f}")


# %% How the sub-sample size and irrelevant columns move the score
def clustered(seed, n=4000, a=200, d=6):
    """Anomalies arriving as one tight, dense clump: the case the paper calls masking."""
    r = np.random.default_rng(seed)
    normal = r.normal(0, 1, (n, d))
    clump = r.normal(3.2, .05, (a, d))
    return normal, clump


psis = [16, 64, 256, 1024, 4096]
sweep_psi = []
for psi in psis:
    aucs = []
    for s in SEEDS:
        normal, clump = clustered(s)
        X = np.vstack([normal, clump])
        y = np.r_[np.zeros(len(normal)), np.ones(len(clump))]
        aucs.append(roc_auc_score(y, iforest(X, s, psi=psi)(X)))
    sweep_psi.append((np.mean(aucs), np.std(aucs)))
print("\nclumped anomalies inside the training data, AUC by sub-sample size")
for psi, (m, sd) in zip(psis, sweep_psi):
    print(f"  psi {psi:<5} {m:.3f} ({sd:.3f})")

extras = [0, 6, 20, 60, 200]
sweep_noise = {"Isolation forest": [], "Gaussian per feature": []}
for k in extras:
    a, b = [], []
    for s in SEEDS:
        tr, te, far, valley = regimes(s)
        r = np.random.default_rng(100 + s)
        A = np.vstack([far, valley])
        tr, te2, A2 = [np.column_stack([x, r.normal(0, 1, (len(x), k))]) for x in (tr, te, A)]
        y = np.r_[np.zeros(len(te2)), np.ones(len(A2))]
        a.append(roc_auc_score(y, iforest(tr, s)(np.vstack([te2, A2]))))
        b.append(roc_auc_score(y, gauss_diag(tr)(np.vstack([te2, A2]))))
    sweep_noise["Isolation forest"].append(np.mean(a))
    sweep_noise["Gaussian per feature"].append(np.mean(b))
print("\nirrelevant noise columns added to the six real ones, mean AUC, both anomaly kinds")
for k, a, b in zip(extras, sweep_noise["Isolation forest"], sweep_noise["Gaussian per feature"]):
    print(f"  {k:<4} forest {a:.3f}  Gaussian per feature {b:.3f}")

# %% Figure
cs.apply()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
a1.plot(range(len(psis)), [m for m, _ in sweep_psi], color=cs.BLUE, marker="o", ms=6)
a1.set_xticks(range(len(psis)), psis)
a1.set(xlabel="Rows sampled for each tree", ylabel="AUC", title="Anomalies in a dense clump", ylim=(.4, 1.02))
a1.grid(False, axis="x")
for (name, vals), colour in zip(sweep_noise.items(), [cs.BLUE, cs.ORANGE]):
    a2.plot(range(len(extras)), vals, color=colour, marker="o", ms=6, label=name)
a2.set_xticks(range(len(extras)), extras)
a2.set(xlabel="Irrelevant columns added to the six real ones", title="Columns that carry no signal")
a2.legend(loc="upper right")
a2.grid(False, axis="x")
cs.save(fig, "classical-iforest-limits.png")
