```python
import warnings
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from sklearn.compose import make_column_transformer, make_column_selector
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier as HGB
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss

warnings.filterwarnings("ignore")
cols = ["age", "workclass", "fnlwgt", "education", "education-num", "marital-status",
        "occupation", "relationship", "race", "gender", "capital-gain", "capital-loss",
        "hours-per-week", "native-country", "income"]
adult = pd.read_csv("../practice/intro-to-ml-in-python/data/adult.data", header=None, names=cols,
                    skipinitialspace=True, na_values="?").drop(columns=["fnlwgt", "education"])
ya = (adult.pop("income") == ">50K").astype(int)
for c in adult.columns[~adult.columns.isin(adult.select_dtypes("number").columns)]:
    adult[c] = adult[c].astype("category")     # HGB reads this dtype natively

Xa_dev, Xa_test, ya_dev, ya_test = train_test_split(adult, ya, stratify=ya, test_size=0.2, random_state=0)
Xa_tr, Xa_val, ya_tr, ya_val = train_test_split(Xa_dev, ya_dev, stratify=ya_dev, test_size=0.25, random_state=0)
prep = make_column_transformer(
    (StandardScaler(), make_column_selector(dtype_include="number")),
    (OneHotEncoder(handle_unknown="ignore"), make_column_selector(dtype_exclude="number")))

print(f"train {len(Xa_tr)}, validation {len(Xa_val)}, test {len(Xa_test)}; positive rate {ya.mean():.3f}")
```
```python
models = {
    "dummy": DummyClassifier(strategy="most_frequent"),
    "logistic": make_pipeline(prep, LogisticRegression(max_iter=1000)),
    "boosting": HGB(categorical_features="from_dtype", random_state=0),
}
for name, m in models.items():
    m.fit(Xa_tr, ya_tr)
    print(f"{name:9s} train acc {accuracy_score(ya_tr, m.predict(Xa_tr)):.3f}  val acc {accuracy_score(ya_val, m.predict(Xa_val)):.3f}"
          f"  train AUC {roc_auc_score(ya_tr, m.predict_proba(Xa_tr)[:, 1]):.3f}  val AUC {roc_auc_score(ya_val, m.predict_proba(Xa_val)[:, 1]):.3f}")
```
```python
from sklearn.model_selection import learning_curve, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier

TRAIN, VAL, INK, MUTED = "#2a78d6", "#eb6834", "#222222", "#6b6b68"
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": MUTED,
                     "axes.grid": True, "grid.color": "#e6e6e3", "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 10, "lines.linewidth": 2,
                     "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED})
IMG = "../../sources/images/"

cv5 = StratifiedKFold(5, shuffle=True, random_state=0)
sizes = [250, 500, 1000, 2000, 4000, 8000, 16000]
curves = {"depth-2 tree": make_pipeline(prep, DecisionTreeClassifier(max_depth=2, random_state=0)),
          "unlimited tree": make_pipeline(prep, DecisionTreeClassifier(random_state=0)),
          "boosting": HGB(categorical_features="from_dtype", random_state=0)}
fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
for ax, (name, m) in zip(axes, curves.items()):
    n, tr, va = learning_curve(m, Xa_dev, ya_dev, train_sizes=sizes, cv=cv5, scoring="roc_auc")
    ax.plot(n, tr.mean(1), "o-", color=TRAIN, label="train"); ax.plot(n, va.mean(1), "o-", color=VAL, label="validation")
    ax.fill_between(n, va.min(1), va.max(1), color=VAL, alpha=.15)
    ax.set_xscale("log"); ax.set_title(name, loc="left"); ax.set_xlabel("training rows")
    print(f"{name:15s} n=250: train {tr[0].mean():.3f} val {va[0].mean():.3f} | n={n[-1]}: train {tr[-1].mean():.3f} val {va[-1].mean():.3f} gap {tr[-1].mean() - va[-1].mean():.3f}")
axes[0].set_ylabel("AUC"); axes[0].legend(frameon=False, loc="lower right")
fig.tight_layout(); fig.savefig(IMG + "training-tuning-learning-curves-adult.png", dpi=150)
```
```python
hot = HGB(categorical_features="from_dtype", learning_rate=0.3, max_leaf_nodes=63, min_samples_leaf=5,
          max_iter=300, early_stopping=False, random_state=0).fit(Xa_tr, ya_tr)
tr_loss = [log_loss(ya_tr, p) for p in hot.staged_predict_proba(Xa_tr)]
va_loss = [log_loss(ya_val, p) for p in hot.staged_predict_proba(Xa_val)]
best = int(np.argmin(va_loss)) + 1
print(f"best round {best}: val loss {min(va_loss):.4f}; round 300: val loss {va_loss[-1]:.4f}, train loss {tr_loss[-1]:.4f}")

fig, ax = plt.subplots(figsize=(6.5, 3.4))
r = np.arange(1, 301)
ax.plot(r, tr_loss, color=TRAIN, label="train"); ax.plot(r, va_loss, color=VAL, label="validation")
ax.axvline(best, color=MUTED, ls=":", lw=1); ax.annotate(f"best round {best}", (best, .62), xytext=(best + 8, .62))
ax.set_xlabel("boosting round"); ax.set_ylabel("log loss"); ax.set_ylim(0, .7); ax.legend(frameon=False, loc="upper right")
fig.tight_layout(); fig.savefig(IMG + "training-tuning-iteration-curve-adult.png", dpi=150)
```
```python
from sklearn.model_selection import cross_val_score, KFold, GroupKFold, TimeSeriesSplit

log_cv = cross_val_score(models["logistic"], Xa_dev, ya_dev, cv=cv5, scoring="roc_auc")
hgb_cv = cross_val_score(models["boosting"], Xa_dev, ya_dev, cv=cv5, scoring="roc_auc")
print("logistic", log_cv.round(4), f"mean {log_cv.mean():.4f} sd {log_cv.std(ddof=1):.4f}")
print("boosting", hgb_cv.round(4), f"mean {hgb_cv.mean():.4f} sd {hgb_cv.std(ddof=1):.4f}")
d = hgb_cv - log_cv
print("boosting minus logistic, fold by fold", d.round(4), f"mean {d.mean():.4f} sd {d.std(ddof=1):.4f}")

for n in (500, 2000, 8000, len(Xa_dev)):
    Xs, ys = (Xa_dev, ya_dev) if n == len(Xa_dev) else train_test_split(Xa_dev, ya_dev, train_size=n, stratify=ya_dev, random_state=0)[0::2]
    s = cross_val_score(models["boosting"], Xs, ys, cv=cv5, scoring="roc_auc")
    print(f"n={n:6d} mean {s.mean():.4f} sd {s.std(ddof=1):.4f} range {s.min():.4f}-{s.max():.4f}")
```
```python
Xt, yt = Xa_dev.iloc[:200], ya_dev.iloc[:200]
for name, cv in [("plain", KFold(5, shuffle=True, random_state=1)), ("stratified", StratifiedKFold(5, shuffle=True, random_state=1))]:
    rates = [yt.iloc[te].mean() for _, te in cv.split(Xt, yt)]
    print(f"{name:10s} positive rate per fold {np.round(rates, 3)}")

gkf = GroupKFold(5)
X_ng = Xa_dev.drop(columns="occupation")
groups = Xa_dev["occupation"].astype(str)
g = cross_val_score(models["boosting"], Xa_dev, ya_dev, cv=gkf, groups=groups, scoring="roc_auc")
print("GroupKFold on occupation", g.round(4), f"mean {g.mean():.4f} sd {g.std(ddof=1):.4f}")

bikes = pd.read_csv("../practice/intro-to-ml-in-python/data/citibike.csv", parse_dates=["starttime"])
y_b = bikes.set_index("starttime").resample("3h").size().astype(float)
X_b = pd.DataFrame({"hour": y_b.index.hour, "weekday": y_b.index.weekday, "t": np.arange(len(y_b)),
                    "prev": y_b.shift(1).values, "prev_day": y_b.shift(8).values}, index=y_b.index).dropna()
y_b = y_b.loc[X_b.index]
from sklearn.ensemble import HistGradientBoostingRegressor as HGR
reg = HGR(max_iter=100, learning_rate=0.1, min_samples_leaf=5, random_state=0)
sh = cross_val_score(reg, X_b, y_b, cv=KFold(5, shuffle=True, random_state=0), scoring="r2")
ts = cross_val_score(reg, X_b, y_b, cv=TimeSeriesSplit(5), scoring="r2")
print(len(y_b), "slots")
print("shuffled KFold R2", sh.round(3), f"mean {sh.mean():.3f}")
print("TimeSeriesSplit R2", ts.round(3), f"mean {ts.mean():.3f}")
```
```python
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingClassifier as GBC
Xs, _, ys, _ = train_test_split(Xa_tr, ya_tr, train_size=1500, stratify=ya_tr, random_state=0)

def curve(make_model, values):
    """Fit one model per knob value on the small training set; score on the full validation set."""
    out = []
    for v in values:
        m = make_model(v).fit(Xs, ys)
        out.append((v, roc_auc_score(ys, m.predict_proba(Xs)[:, 1]), roc_auc_score(ya_val, m.predict_proba(Xa_val)[:, 1])))
    return np.array(out)

gbc = lambda **k: make_pipeline(prep, GBC(n_estimators=300, max_depth=3, random_state=0, **k))
knobs = {
    "logistic: L2 strength C": (lambda c: make_pipeline(prep, LogisticRegression(C=c, max_iter=5000)), [.001, .003, .01, .03, .1, .3, 1, 3, 10, 100, 1000], True),
    "tree: max_depth": (lambda d: make_pipeline(prep, DecisionTreeClassifier(max_depth=d, random_state=0)), [1, 2, 3, 4, 6, 8, 12, 16, 24], False),
    "tree: min_samples_leaf": (lambda l: make_pipeline(prep, DecisionTreeClassifier(min_samples_leaf=l, random_state=0)), [1, 2, 5, 10, 20, 50, 100, 200], True),
    "boosting: learning_rate": (lambda r: gbc(learning_rate=r), [.003, .01, .03, .1, .3, 1], True),
    "boosting: subsample": (lambda s: gbc(learning_rate=.3, subsample=s), [.1, .2, .3, .5, .7, 1.0], False),
}
results = {k: curve(f, v) for k, (f, v, _) in knobs.items()}
for k, a in results.items():
    i = a[:, 2].argmax()
    print(f"{k:26s} best {a[i, 0]:g}: train {a[i, 1]:.3f} val {a[i, 2]:.3f} | loosest {a[-1 if k[:4] != 'tree' or 'depth' in k else 0, 0]:g}: train {a[-1 if k[:4] != 'tree' or 'depth' in k else 0, 1]:.3f} val {a[-1 if k[:4] != 'tree' or 'depth' in k else 0, 2]:.3f}")
    print("   ", np.round(a, 3).tolist())

Z = make_pipeline(prep, LogisticRegression(penalty="l1", solver="liblinear", C=1))
from sklearn.linear_model import LogisticRegression as LR
for c in (.01, .03, .1, 1, 100):
    l1 = make_pipeline(prep, LR(penalty="l1", solver="liblinear", C=c)).fit(Xs, ys)
    l2 = make_pipeline(prep, LR(C=c, max_iter=5000)).fit(Xs, ys)
    print(f"C={c:<5} L1 nonzero {np.sum(l1[-1].coef_ != 0):3d} val {roc_auc_score(ya_val, l1.predict_proba(Xa_val)[:, 1]):.3f} | L2 nonzero {np.sum(l2[-1].coef_ != 0):3d} val {roc_auc_score(ya_val, l2.predict_proba(Xa_val)[:, 1]):.3f}")
```
```python
import torch
from torch import nn
torch.set_num_threads(4)
enc = clone(prep).fit(Xs)
dense = lambda X: torch.tensor(enc.transform(X).toarray() if hasattr(enc.transform(X), "toarray") else enc.transform(X), dtype=torch.float32)
T_s, T_val = dense(Xs), dense(Xa_val)
t_y = torch.tensor(ys.values, dtype=torch.float32)

def net_auc(weight_decay=0.0, dropout=0.0, epochs=120, seeds=(0, 1, 2)):
    tr, va = [], []
    for s in seeds:
        torch.manual_seed(s)
        net = nn.Sequential(nn.Linear(T_s.shape[1], 256), nn.ReLU(), nn.Dropout(dropout),
                            nn.Linear(256, 256), nn.ReLU(), nn.Dropout(dropout), nn.Linear(256, 1))
        opt = torch.optim.AdamW(net.parameters(), lr=1e-3, weight_decay=weight_decay)
        for _ in range(epochs):
            net.train()
            for idx in torch.randperm(len(t_y)).split(64):
                opt.zero_grad()
                nn.functional.binary_cross_entropy_with_logits(net(T_s[idx]).squeeze(1), t_y[idx]).backward()
                opt.step()
        net.eval()
        with torch.no_grad():
            tr.append(roc_auc_score(ys, net(T_s).squeeze(1).numpy())); va.append(roc_auc_score(ya_val, net(T_val).squeeze(1).numpy()))
    return np.mean(tr), np.mean(va)

wd_vals, do_vals = [0, .01, .1, .3, 1, 3, 10], [0, .1, .3, .5, .7, .8, .9]
results["net: weight decay"] = np.array([(w, *net_auc(weight_decay=w)) for w in wd_vals])
results["net: dropout"] = np.array([(p, *net_auc(dropout=p)) for p in do_vals])
for k in ("net: weight decay", "net: dropout"):
    print(k, np.round(results[k], 3).tolist())
```
```python
show = ["logistic: L2 strength C", "tree: max_depth", "boosting: learning_rate", "boosting: subsample", "net: weight decay", "net: dropout"]
logx = {"logistic: L2 strength C", "boosting: learning_rate"}
fig, axes = plt.subplots(2, 3, figsize=(11, 5.6), sharey=True)
for ax, k in zip(axes.flat, show):
    a = results[k]
    ax.plot(a[:, 0], a[:, 1], "o-", color=TRAIN, label="train"); ax.plot(a[:, 0], a[:, 2], "o-", color=VAL, label="validation")
    if k in logx: ax.set_xscale("log")
    if k == "net: weight decay": ax.set_xscale("symlog", linthresh=.01)
    ax.set_title(k, loc="left"); i = a[:, 2].argmax(); ax.plot(a[i, 0], a[i, 2], "o", ms=11, mfc="none", color=INK)
    ax.set_ylim(.7, 1.005)
axes[0, 0].legend(frameon=False, loc="lower right")
for ax in axes[:, 0]: ax.set_ylabel("AUC, 1,500 training rows")
fig.tight_layout(); fig.savefig(IMG + "training-tuning-regularisation-knobs-adult.png", dpi=150)
```
```python
Xs_dense, Xv_dense = enc.transform(Xs), enc.transform(Xa_val)
Xs_dense = Xs_dense.toarray() if hasattr(Xs_dense, "toarray") else Xs_dense
Xv_dense = Xv_dense.toarray() if hasattr(Xv_dense, "toarray") else Xv_dense
w, b = np.zeros(Xs_dense.shape[1]), 0.0
yy = ys.values
marks = {10, 100, 1000, 10000, 100000}
for step in range(1, 100001):
    p = 1 / (1 + np.exp(-(Xs_dense @ w + b)))
    w -= 0.3 * Xs_dense.T @ (p - yy) / len(yy); b -= 0.3 * (p - yy).mean()
    if step in marks:
        s = Xv_dense @ w + b
        print(f"GD step {step:6d}: |w| {np.linalg.norm(w):6.2f}  val AUC {roc_auc_score(ya_val, s):.4f}  val loss {log_loss(ya_val, 1 / (1 + np.exp(-s))):.4f}")
for c in (.003, .01, .03, .1, 1, 10, 1000):
    m = LR(C=c, max_iter=20000).fit(Xs_dense, yy)
    s = m.decision_function(Xv_dense)
    print(f"L2 C={c:<6g}: |w| {np.linalg.norm(m.coef_):6.2f}  val AUC {roc_auc_score(ya_val, s):.4f}  val loss {log_loss(ya_val, 1 / (1 + np.exp(-s))):.4f}")
```
```python
base = dict(categorical_features="from_dtype", learning_rate=0.3, max_leaf_nodes=63, min_samples_leaf=5, random_state=0)
Xe_tr, Xe_stop, ye_tr, ye_stop = Xa_tr, Xa_val, ya_tr, ya_val
for pat in (5, 10, 25, 50, 100):
    # sklearn holds out its own fraction of train for this, so stop on rows the report never sees
    m = HGB(max_iter=1000, early_stopping=True, n_iter_no_change=pat, validation_fraction=0.15, **base).fit(Xa_tr, ya_tr)
    print(f"patience {pat:3d}: stopped at {m.n_iter_:3d} rounds, val AUC {roc_auc_score(ya_val, m.predict_proba(Xa_val)[:, 1]):.4f}, val loss {log_loss(ya_val, m.predict_proba(Xa_val)):.4f}")
m = HGB(max_iter=1000, early_stopping=False, **base).fit(Xa_tr, ya_tr)
print(f"no stopping, 1000 rounds: val AUC {roc_auc_score(ya_val, m.predict_proba(Xa_val)[:, 1]):.4f}, val loss {log_loss(ya_val, m.predict_proba(Xa_val)):.4f}")
```
```python
import time, itertools, optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
from optuna.samplers import TPESampler

X_sr, X_rr, y_sr, y_rr = train_test_split(Xa_val, ya_val, stratify=ya_val, test_size=0.5, random_state=0)
search_idx = Xa_val.index.get_indexer(X_sr.index); report_idx = Xa_val.index.get_indexer(X_rr.index)
BOUNDS = {"learning_rate": (.01, .5), "max_leaf_nodes": (4, 128), "min_samples_leaf": (5, 200), "l2_regularization": (1e-3, 30), "max_features": (.3, 1.)}

def evaluate(p):
    m = HGB(categorical_features="from_dtype", max_iter=200, early_stopping=False, random_state=0, **p).fit(Xa_tr, ya_tr)
    q = m.predict_proba(Xa_val)[:, 1]
    return roc_auc_score(ya_val.values[search_idx], q[search_idx]), roc_auc_score(ya_val.values[report_idx], q[report_idx]), q

def random_trial(rng):
    return {"learning_rate": float(np.exp(rng.uniform(*np.log(BOUNDS["learning_rate"])))),
            "max_leaf_nodes": int(round(np.exp(rng.uniform(*np.log(BOUNDS["max_leaf_nodes"]))))),
            "min_samples_leaf": int(round(np.exp(rng.uniform(*np.log(BOUNDS["min_samples_leaf"]))))),
            "l2_regularization": float(np.exp(rng.uniform(*np.log(BOUNDS["l2_regularization"])))),
            "max_features": float(rng.uniform(*BOUNDS["max_features"]))}

BUDGET, SEEDS = 32, range(5)
t0 = time.time()
default = evaluate({})
print(f"default HGB, 200 rounds: search {default[0]:.4f} report {default[1]:.4f}  [{time.time() - t0:.1f}s per fit]")

grid2 = [dict(zip(BOUNDS, v)) for v in itertools.product((.03, .2), (8, 64), (10, 100), (.01, 1.), (.5, 1.))]
lop = [dict(learning_rate=a, max_leaf_nodes=b, min_samples_leaf=c) for a, b, c in itertools.product((.01, .03, .1, .3), (4, 8, 32, 128), (10, 100))]
runs = {"grid 2x2x2x2x2": [], "grid 4x4x2": [], "random": [], "TPE": []}
cache = {}
for name, g in [("grid 2x2x2x2x2", grid2), ("grid 4x4x2", lop)]:
    res = [(p, *evaluate(p)) for p in g]
    for s in SEEDS:                               # same 32 points, shuffled arrival order per seed
        runs[name].append([res[i] for i in np.random.default_rng(s).permutation(len(res))])
for s in SEEDS:
    rng = np.random.default_rng(s)
    runs["random"].append([(p, *evaluate(p)) for p in (random_trial(rng) for _ in range(BUDGET))])
    trials = []
    def objective(tr):
        p = {"learning_rate": tr.suggest_float("learning_rate", .01, .5, log=True),
             "max_leaf_nodes": tr.suggest_int("max_leaf_nodes", 4, 128, log=True),
             "min_samples_leaf": tr.suggest_int("min_samples_leaf", 5, 200, log=True),
             "l2_regularization": tr.suggest_float("l2_regularization", 1e-3, 30, log=True),
             "max_features": tr.suggest_float("max_features", .3, 1.)}
        r = evaluate(p); trials.append((p, *r)); return r[0]
    study = optuna.create_study(direction="maximize", sampler=TPESampler(seed=s)); study.optimize(objective, n_trials=BUDGET)
    runs["TPE"].append(trials)
    cache[s] = study
print(f"total {time.time() - t0:.0f}s")

def winner(run, k=BUDGET): return max(run[:k], key=lambda t: t[1])
print(f"{'method':16s} {'search@8':>9s} {'report@8':>9s} {'search@32':>10s} {'report@32':>10s}  sd report@32")
for name, rs in runs.items():
    w8 = [winner(r, 8) for r in rs]; w32 = [winner(r) for r in rs]
    print(f"{name:16s} {np.mean([w[1] for w in w8]):9.4f} {np.mean([w[2] for w in w8]):9.4f} {np.mean([w[1] for w in w32]):10.4f} {np.mean([w[2] for w in w32]):10.4f}  {np.std([w[2] for w in w32], ddof=1):.4f}")
for name, rs in runs.items():
    print(name, "per seed report", np.round([winner(r)[2] for r in rs], 4), "distinct learning rates", len({round(t[0].get("learning_rate", .1), 6) for t in rs[0]}))
    print("   worst, median trial search:", round(min(t[1] for t in rs[0]), 4), round(float(np.median([t[1] for t in rs[0]])), 4), " winner:", {k: round(v, 3) for k, v in winner(rs[0])[0].items()})
print(optuna.importance.get_param_importances(cache[0]))
```
```python
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
colors = {"grid 2x2x2x2x2": "#6b6b68", "grid 4x4x2": "#eda100", "random": TRAIN, "TPE": VAL}
ax = axes[0]
for name, rs in runs.items():
    bsf = np.maximum.accumulate(np.array([[t[1] for t in r] for r in rs]), axis=1)
    ax.plot(range(1, BUDGET + 1), bsf.mean(0), color=colors[name], label=name)
    ax.annotate(name, (BUDGET, bsf.mean(0)[-1]), xytext=(4, 0), textcoords="offset points", fontsize=8, va="center", annotation_clip=False)
ax.axhline(default[0], color=INK, ls=":", lw=1); ax.annotate("default settings", (1.2, default[0]), xytext=(0, 3), textcoords="offset points", fontsize=8)
ax.set_xlabel("trials spent"); ax.set_ylabel("best search-rows AUC so far"); ax.legend(frameon=False, loc="lower right", fontsize=8)
ax = axes[1]
rand = [t for r in runs["random"] for t in r]
ax.plot([t[0]["learning_rate"] for t in rand], [t[1] for t in rand], "o", ms=5, color=TRAIN, alpha=.6, label="random trials")
g2 = runs["grid 2x2x2x2x2"][0]
ax.plot([t[0]["learning_rate"] for t in g2], [t[1] for t in g2], "D", ms=6, color="#6b6b68", alpha=.7, label="grid 2^5 trials")
ax.set_xscale("log"); ax.set_xlabel("learning_rate"); ax.set_ylabel("search-rows AUC"); ax.legend(frameon=False, loc="lower left", fontsize=8)
fig.tight_layout(); fig.savefig(IMG + "training-tuning-search-comparison-adult.png", dpi=150)
```
```python
q = np.array([t[3] for t in runs["random"][0]])    # 32 configurations' validation scores
ysr, yrr = ya_val.values[search_idx], ya_val.values[report_idx]
rng = np.random.default_rng(0)
print(f"{'selection rows':>14s} {'winner AUC there':>17s} {'same winner, fresh rows':>24s} {'optimism':>9s} {'sd fresh':>9s}")
for m_ in (100, 300, 1000, 3256):
    sel, fresh = [], []
    for _ in range(200):
        i = rng.choice(len(search_idx), m_, replace=False)
        sc = [roc_auc_score(ysr[i], q[j, search_idx][i]) for j in range(len(q))]
        b = int(np.argmax(sc)); sel.append(sc[b]); fresh.append(roc_auc_score(yrr, q[b, report_idx]))
        if m_ == 3256: break
    print(f"{m_:14d} {np.mean(sel):17.4f} {np.mean(fresh):24.4f} {np.mean(sel) - np.mean(fresh):9.4f} {np.std(fresh):9.4f}")
```
```python
win = winner(runs["TPE"][0])
final = HGB(categorical_features="from_dtype", max_iter=200, early_stopping=False, random_state=0, **win[0]).fit(Xa_dev, ya_dev)
dflt = HGB(categorical_features="from_dtype", max_iter=200, early_stopping=False, random_state=0).fit(Xa_dev, ya_dev)
logi = clone(models["logistic"]).fit(Xa_dev, ya_dev)
dum = clone(models["dummy"]).fit(Xa_dev, ya_dev)
print("winner", {k: round(v, 3) for k, v in win[0].items()})
rng = np.random.default_rng(0)
pt = final.predict_proba(Xa_test)[:, 1]; yv = ya_test.values
boots = [roc_auc_score(yv[i], pt[i]) for i in (rng.integers(0, len(yv), len(yv)) for _ in range(500))]
print(f"dummy acc {accuracy_score(ya_test, dum.predict(Xa_test)):.3f}")
print(f"logistic AUC {roc_auc_score(ya_test, logi.predict_proba(Xa_test)[:, 1]):.4f} acc {accuracy_score(ya_test, logi.predict(Xa_test)):.3f}")
print(f"default boosting AUC {roc_auc_score(ya_test, dflt.predict_proba(Xa_test)[:, 1]):.4f} acc {accuracy_score(ya_test, dflt.predict(Xa_test)):.3f}")
print(f"tuned boosting AUC {roc_auc_score(yv, pt):.4f} acc {accuracy_score(yv, final.predict(Xa_test)):.3f}, bootstrap 95% {np.percentile(boots, 2.5):.4f}-{np.percentile(boots, 97.5):.4f}")
```
```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import loguniform, randint, uniform
space = {"learning_rate": loguniform(.01, .5), "max_leaf_nodes": randint(4, 129), "min_samples_leaf": randint(5, 201),
         "l2_regularization": loguniform(1e-3, 30), "max_features": uniform(.3, .7)}
t0 = time.time()
inner = StratifiedKFold(3, shuffle=True, random_state=1)
search = RandomizedSearchCV(HGB(categorical_features="from_dtype", max_iter=200, early_stopping=False, random_state=0),
                            space, n_iter=8, cv=inner, scoring="roc_auc", random_state=0, refit=True)
out = []
for tr_i, te_i in cv5.split(Xa_dev, ya_dev):
    search.fit(Xa_dev.iloc[tr_i], ya_dev.iloc[tr_i])
    out.append((search.best_score_, roc_auc_score(ya_dev.iloc[te_i], search.predict_proba(Xa_dev.iloc[te_i])[:, 1]), search.best_params_["learning_rate"]))
out = np.array(out)
print(np.round(out, 4).tolist())
print(f"inner best {out[:, 0].mean():.4f}, nested outer {out[:, 1].mean():.4f} sd {out[:, 1].std(ddof=1):.4f}  [{time.time() - t0:.0f}s]")
```
```python
X_small = make_pipeline(clone(prep)).fit_transform(Xa_dev.iloc[:400])
X_small = X_small.toarray() if hasattr(X_small, "toarray") else X_small
tree_space = {"max_depth": randint(1, 12), "min_samples_leaf": randint(1, 40), "max_features": uniform(.2, .8), "criterion": ["gini", "entropy"]}
res = []
for s in range(10):
    y_null = np.random.default_rng(s).permutation(ya_dev.values[:400])
    sr = RandomizedSearchCV(DecisionTreeClassifier(random_state=s), tree_space, n_iter=30, cv=StratifiedKFold(5, shuffle=True, random_state=s), scoring="roc_auc", random_state=s)
    nonnest = sr.fit(X_small, y_null).best_score_
    nest = cross_val_score(sr, X_small, y_null, cv=StratifiedKFold(5, shuffle=True, random_state=s + 100), scoring="roc_auc").mean()
    res.append((nonnest, nest))
res = np.array(res)
print(f"shuffled labels, true AUC 0.5: best inner score {res[:, 0].mean():.3f} (range {res[:, 0].min():.3f}-{res[:, 0].max():.3f}); nested {res[:, 1].mean():.3f} (range {res[:, 1].min():.3f}-{res[:, 1].max():.3f})")
```
