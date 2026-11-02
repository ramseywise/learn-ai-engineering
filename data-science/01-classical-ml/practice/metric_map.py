# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scipy", "scikit-learn", "imbalanced-learn", "xlrd", "matplotlib"]
# ///
"""Experiments for notes/11-choosing-a-metric.md: the loss, the rare class, counts and ranking.

Run from this folder:
    uv run metric_map.py

Uses the credit lab's data and helpers (internet needed once, if credit-default-lab/data is empty).
Writes one figure to ../../sources/images/. Every seed is stated where it is used.
"""
# %% Setup
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "credit-default-lab"))
import numpy as np
import pandas as pd
import credit_default_lab as lab
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import PoissonRegressor
from sklearn.metrics import (
    accuracy_score, average_precision_score, balanced_accuracy_score, brier_score_loss,
    d2_tweedie_score, matthews_corrcoef, mean_absolute_error, mean_pinball_loss,
    mean_poisson_deviance, ndcg_score, roc_auc_score,
)
from sklearn.model_selection import train_test_split

pd.set_option("display.width", 130, "display.max_columns", None)
BOOSTED = {"max_leaf_nodes": 4, "max_iter": 300}


# %% 1. The loss decides what a model estimates (one skewed target, four constant forecasts)
def losses_table(seed=0, n=100_000):
    y = np.random.default_rng(seed).lognormal(mean=0.0, sigma=1.0, size=n)
    grid = np.quantile(y, np.linspace(0.001, 0.999, 999))
    mape = lambda c: np.mean(np.abs(y - c) / y)
    forecasts = {
        "the mean": y.mean(),
        "the median": np.median(y),
        "90th percentile": np.quantile(y, 0.9),
        "best for MAPE": grid[np.argmin([mape(c) for c in grid])],
    }
    rows = {}
    for name, c in forecasts.items():
        f = np.full(n, c)
        rows[name] = {
            "forecast": c,
            "RMSE": np.sqrt(np.mean((y - c) ** 2)),
            "MAE": mean_absolute_error(y, f),
            "pinball 0.9": mean_pinball_loss(y, f, alpha=0.9),
            "MAPE": mape(c),
        }
    return pd.DataFrame(rows).T


print("--- one target, four forecasts (lognormal, n=100,000, seed 0) ---")
print(losses_table().round(3))
_y = np.random.default_rng(0).lognormal(mean=0.0, sigma=1.0, size=100_000)
print(f"share of outcomes above the MAPE forecast: {(_y > losses_table().loc['best for MAPE', 'forecast']).mean():.3f}")


# %% 2. Several models on the same rare-class data
def rare_split(raw, seed=0):
    rare, _ = lab.make_rare(raw, seed=seed)
    tr, va, te = lab.split(rare, seed=seed)
    return tr, va, te


def rare_models(seed=0):
    return {
        "approve everyone": DummyClassifier(strategy="prior"),
        "tree, depth 2": lab.DecisionTreeClassifier(max_depth=2, random_state=seed),
        "logistic": lab.LogisticRegression(max_iter=2000),
        "boosted": None,
    }


def scored(raw, seed=0):
    tr, va, te = rare_split(raw, seed)
    xtr, ytr = lab.features(tr), tr[lab.TARGET].to_numpy()
    out = {}
    for name, m in rare_models(seed).items():
        if m is None:
            m = lab.make_pipeline(None, "boosted", BOOSTED, False, seed=seed)
        elif name == "logistic":
            m = lab.make_pipeline(None, "logistic", {"C": 1.0}, False, seed=seed)
        m.fit(xtr, ytr)
        out[name] = (m.predict_proba(lab.features(va))[:, 1], m.predict_proba(lab.features(te))[:, 1])
    return out, va[lab.TARGET].to_numpy(), te[lab.TARGET].to_numpy()


def report(y, p, t):
    d = (p >= t).astype(int)
    return {
        "accuracy": accuracy_score(y, d),
        "balanced": balanced_accuracy_score(y, d),
        "MCC": matthews_corrcoef(y, d),
        "PR-AUC": average_precision_score(y, p),
        "ROC-AUC": roc_auc_score(y, p),
        "Brier": brier_score_loss(y, p),
        "cost": lab.expected_cost(y, p, t),
        "declined": d.mean(),
    }


raw = lab.load_credit()
models, yva, yte = scored(raw, seed=0)
print(f"\n--- 3% default rate, test set {len(yte)} rows, {yte.sum()} defaulters, seed 0 ---")
print("decisions at the 5:1 threshold, 1/6; cost per 1,000 applicants")
print(pd.DataFrame({k: report(yte, v[1], lab.BAYES) for k, v in models.items()}).T.round(3))

SEEDS = range(10)
rows = []
for s in SEEDS:
    m, _, y = scored(raw, seed=s)
    for k, v in m.items():
        rows.append({"seed": s, "model": k, **report(y, v[1], lab.BAYES)})
many = pd.DataFrame(rows)
print("\nmean over seeds 0-9 (a new rare subset and split each time)")
print(many.drop(columns="seed").groupby("model", sort=False).mean().round(3))
print("seeds where each metric ranks 'approve everyone' above 'tree, depth 2':")
w = many.pivot(index="seed", columns="model")
for c, sign in [("accuracy", 1), ("balanced", 1), ("MCC", 1), ("PR-AUC", 1), ("cost", -1)]:
    n = (sign * w[c]["approve everyone"] > sign * w[c]["tree, depth 2"]).sum()
    print(f"  {c:9s}{n:3d} of {len(SEEDS)}")


# %% 3. The threshold each metric would choose, tuned on validation and scored on test
def sweep(y, p, grid):
    out = []
    for t in grid:
        d = (p >= t).astype(int)
        out.append((t, accuracy_score(y, d), balanced_accuracy_score(y, d), matthews_corrcoef(y, d),
                    lab.expected_cost(y, p, t), lab.expected_cost(y, p, t, fn=20), d.mean()))
    return pd.DataFrame(out, columns=["t", "accuracy", "balanced", "MCC", "cost 5:1", "cost 20:1", "declined"])


pva, pte = models["boosted"]
grid = np.unique(np.r_[np.geomspace(0.005, 0.9, 150), lab.BAYES, 1 / 21])
sv, st = sweep(yva, pva, grid), sweep(yte, pte, grid)
picks = {
    "accuracy": sv.accuracy.idxmax(),
    "balanced accuracy": sv.balanced.idxmax(),
    "MCC": sv.MCC.idxmax(),
    "cost 5:1, tuned": sv["cost 5:1"].idxmin(),
    "cost 20:1, tuned": sv["cost 20:1"].idxmin(),
}
table = pd.DataFrame({k: st.loc[i, ["t", "declined", "cost 5:1", "cost 20:1"]] for k, i in picks.items()}).T
print("\n--- boosted model: threshold chosen on validation by each metric, scored on test (seed 0) ---")
print(table.round(3))
print(f"approve everyone costs {lab.expected_cost(yte, np.zeros(len(yte)), 0.5):.1f} at 5:1, "
      f"{lab.expected_cost(yte, np.zeros(len(yte)), 0.5, fn=20):.1f} at 20:1")
print(f"N/P on this test set is {(yte == 0).sum() / yte.sum():.1f}")

# %% 4. MCC is not a cost, and it does not need recall to be high (Chicco and Jurman's example, then ours)
print("\n--- MCC against accuracy, by hand-built confusion tables ---")
for name, (tp, fn, tn, fp) in {
    "Chicco and Jurman A1": (90, 1, 0, 9),
    "recall 0.45, no false alarms": (45, 55, 900, 0),
}.items():
    y = np.r_[np.ones(tp + fn), np.zeros(tn + fp)]
    d = np.r_[np.ones(tp), np.zeros(fn), np.zeros(tn), np.ones(fp)]
    print(f"{name:30s} accuracy {accuracy_score(y, d):.3f}  recall {tp / (tp + fn):.3f}  "
          f"balanced {balanced_accuracy_score(y, d):.3f}  MCC {matthews_corrcoef(y, d):.3f}")

# %% 5. Same model, two base rates: ROC holds still and PR moves
tr, va, te = lab.split(raw, seed=0)
m = lab.make_pipeline(None, "boosted", BOOSTED, False, seed=0).fit(lab.features(tr), tr[lab.TARGET])
rare_te, _ = lab.make_rare(te, seed=0)
print("\n--- one model, trained at 22.1%, scored on the natural test set and on a 3% subset of it ---")
for name, part in {"natural": te, "3% subset": rare_te}.items():
    y, p = part[lab.TARGET].to_numpy(), m.predict_proba(lab.features(part))[:, 1]
    d = (p >= lab.BAYES).astype(int)
    print(f"{name:10s} rows {len(y):5d}  rate {y.mean():.3f}  ROC-AUC {roc_auc_score(y, p):.3f}  "
          f"PR-AUC {average_precision_score(y, p):.3f}  balanced {balanced_accuracy_score(y, d):.3f}  "
          f"MCC {matthews_corrcoef(y, d):.3f}  accuracy {accuracy_score(y, d):.3f}")


# %% 6. Counts: deviance against a constant rate (simulated gamma-Poisson, seed 0)
def counts(seed=0, n=20_000):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(n, 2))
    mu = np.exp(0.5 + 0.6 * x[:, 0])  # the second column carries nothing
    y = rng.poisson(mu * rng.gamma(shape=2.0, scale=0.5, size=n))
    return train_test_split(x, y, test_size=0.5, random_state=seed)


xa, xb, ya, yb = counts()
pois = PoissonRegressor(alpha=0.0).fit(xa, ya)
for name, f in {"constant rate": np.full(len(yb), ya.mean()), "Poisson model": pois.predict(xb)}.items():
    print_head = "--- counts, 10,000 test rows, seed 0 ---\n" if name == "constant rate" else ""
    disp = np.sum((yb - f) ** 2 / f) / (len(yb) - (3 if name == "Poisson model" else 1))
    print(f"{print_head}{name:14s} deviance {mean_poisson_deviance(yb, f):.3f}  "
          f"D2 {d2_tweedie_score(yb, f, power=1):+.3f}  MAE {mean_absolute_error(yb, f):.3f}  "
          f"dispersion {disp:.2f}")


# %% 7. Ranking: MRR and NDCG can disagree (simulated queries)
def simulate_rankers(seed=0, n_queries=500, n_docs=100, n_rel=5):
    """Finder lifts one relevant document a lot. Broad lifts all of them a little. Built to differ."""
    rng = np.random.default_rng(seed)
    rel = np.zeros((n_queries, n_docs), dtype=int)
    rel[:, :n_rel] = 1  # document order is irrelevant: scores carry no position information
    finder = rng.normal(size=rel.shape)
    finder[:, 0] += 4.0
    broad = rng.normal(size=rel.shape)
    broad[:, :n_rel] += 1.7
    return rel, {"finder": finder, "broad": broad}


def mrr(rel, score):
    order = np.argsort(-score, axis=1)
    hits = np.take_along_axis(rel, order, axis=1)
    return np.mean(1 / (hits.argmax(axis=1) + 1))  # argmax finds the first relevant position


def recall_at(rel, score, k):
    top = np.argsort(-score, axis=1)[:, :k]
    return np.mean(np.take_along_axis(rel, top, axis=1).sum(axis=1) / rel.sum(axis=1))


print("\n--- 500 simulated queries, 100 documents, 5 relevant each ---")
res = []
for s in range(5):
    rel, rankers = simulate_rankers(seed=s)
    for name, score in rankers.items():
        res.append({"seed": s, "ranker": name, "MRR": mrr(rel, score), "NDCG@10": ndcg_score(rel, score, k=10),
                    "recall@10": recall_at(rel, score, 10)})
res = pd.DataFrame(res)
print(res[res.seed == 0].drop(columns="seed").set_index("ranker").round(3))
print("mean over seeds 0-4")
print(res.drop(columns="seed").groupby("ranker").mean().round(3))

rel, rankers = simulate_rankers(seed=0)
row = np.argsort(-rankers["broad"][0])
print("\n--- one query, broad ranker: the confusion table at each cut-off ---")
sw = []
for k in (1, 3, 5, 10, 20, 100):
    tp = rel[0][row[:k]].sum()
    fp, fn, tn = k - tp, rel[0].sum() - tp, 100 - k - (rel[0].sum() - tp)
    sw.append({"k": k, "TP": tp, "FP": fp, "FN": fn, "TN": tn, "precision": tp / k, "recall": tp / rel[0].sum(),
               "accuracy": (tp + tn) / 100})
print(pd.DataFrame(sw).set_index("k").round(2))
pos = np.flatnonzero(rel[0][row]) + 1
print(f"relevant documents at positions {pos.tolist()}")


# %% Try it: how strong must the single lift be before the finder leads on MRR?
print("\n--- Try it: the finder's lift against MRR (seed 0, broad stays at +1.7) ---")
rel, rankers = simulate_rankers(seed=0)
for lift in (1.0, 2.0, 3.0, 4.0):
    score = np.random.default_rng(0).normal(size=rel.shape)
    score[:, 0] += lift
    print(f"lift {lift:.0f}  finder MRR {mrr(rel, score):.3f}  NDCG@10 {ndcg_score(rel, score, k=10):.3f}"
          f"  broad MRR {mrr(rel, rankers['broad']):.3f}  NDCG@10 {ndcg_score(rel, rankers['broad'], k=10):.3f}")


# %% 8. Figure: what each threshold-based metric prefers
import chartstyle as cs
import matplotlib.pyplot as plt

cs.apply()
fig, (a, b) = plt.subplots(2, 1, sharex=True, height_ratios=[3, 2])
for col, colour, label in [("accuracy", cs.BLUE, "Accuracy"), ("balanced", cs.ORANGE, "Balanced accuracy"),
                           ("MCC", cs.AQUA, "Matthews correlation")]:
    a.plot(st.t, st[col], color=colour, lw=2, label=label)
    i = st[col].idxmax()
    a.plot(st.t[i], st[col][i], "o", color=colour, ms=8, mec=cs.SURFACE, mew=2)
a.set_ylabel("Score on test")
a.set_title("Each metric prefers a different threshold; only cost says what that costs")
a.legend(loc="center right", bbox_to_anchor=(1, 0.36))
b.plot(st.t, st["cost 5:1"], color=cs.SECONDARY, lw=2, label="Cost per 1,000 at 5:1")
i = st["cost 5:1"].idxmin()
b.plot(st.t[i], st["cost 5:1"][i], "o", color=cs.SECONDARY, ms=8, mec=cs.SURFACE, mew=2)
b.annotate(f"Lowest {st['cost 5:1'][i]:.1f}", (st.t[i], st["cost 5:1"][i]), xytext=(-4, 9), textcoords="offset points", ha="right")
i = picks["balanced accuracy"]
b.plot(st.t[i], st["cost 5:1"][i], "o", color=cs.ORANGE, ms=8, mec=cs.SURFACE, mew=2)
b.annotate(f"Balanced accuracy's pick: {st['cost 5:1'][i]:.0f}", (st.t[i], st["cost 5:1"][i]), xytext=(9, 9),
           textcoords="offset points")
b.axvline(lab.BAYES, color=cs.MUTED, lw=1, ls="--")
b.annotate("1/6, from the 5:1 cost ratio", (lab.BAYES, st["cost 5:1"].max() * 0.9), xytext=(6, 0),
           textcoords="offset points", color=cs.SECONDARY)
b.set_xscale("log")
b.set_xlabel("Threshold on predicted default probability (log scale; dots mark each line's best)")
b.set_ylabel("Cost per 1,000")
b.legend(loc="upper right", bbox_to_anchor=(1, .75))
cs.save(fig, "metric-map-threshold.png")
