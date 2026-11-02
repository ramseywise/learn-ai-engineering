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
from sklearn.model_selection import cross_val_score, KFold

log_cv = cross_val_score(models["logistic"], Xa_dev, ya_dev, cv=cv5, scoring="roc_auc")
hgb_cv = cross_val_score(models["boosting"], Xa_dev, ya_dev, cv=cv5, scoring="roc_auc")
print("logistic", log_cv.round(4), f"mean {log_cv.mean():.4f} sd {log_cv.std(ddof=1):.4f}")
print("boosting", hgb_cv.round(4), f"mean {hgb_cv.mean():.4f} sd {hgb_cv.std(ddof=1):.4f}")
d = hgb_cv - log_cv
print("boosting minus logistic, fold by fold", d.round(4), f"mean {d.mean():.4f} sd {d.std(ddof=1):.4f}")

shuffled = np.random.default_rng(0).permutation(len(Xa_dev))
for n in (500, 2000):
    means, naive = [], []
    for k in range(len(Xa_dev) // n)[:20]:          # disjoint samples, so these runs are truly independent
        i = shuffled[k * n:(k + 1) * n]
        s = cross_val_score(models["boosting"], Xa_dev.iloc[i], ya_dev.iloc[i], cv=cv5, scoring="roc_auc")
        means.append(s.mean()); naive.append(s.std(ddof=1) / np.sqrt(5))
    print(f"n={n:5d}, {len(means)} independent samples: mean CV AUC {np.mean(means):.4f}; true sd of the CV mean {np.std(means, ddof=1):.4f}; "
          f"naive fold sd/sqrt(5) averages {np.mean(naive):.4f}, ranges {min(naive):.4f}-{max(naive):.4f}")
```
```python
from sklearn.model_selection import GroupKFold, TimeSeriesSplit
from sklearn.ensemble import HistGradientBoostingRegressor as HGR

Xt, yt = Xa_dev.iloc[:200], ya_dev.iloc[:200]
for name, cv in [("plain", KFold(5, shuffle=True, random_state=1)), ("stratified", StratifiedKFold(5, shuffle=True, random_state=1))]:
    rates = [yt.iloc[te].mean() for _, te in cv.split(Xt, yt)]
    print(f"{name:10s} positive rate per fold {np.round(rates, 3)}")

gkf = GroupKFold(5)
groups = Xa_dev["occupation"].astype(object).fillna("unknown")
g = cross_val_score(models["boosting"], Xa_dev, ya_dev, cv=gkf, groups=groups, scoring="roc_auc")
print("GroupKFold on occupation", g.round(4), f"mean {g.mean():.4f} sd {g.std(ddof=1):.4f}")

bikes = pd.read_csv("../practice/intro-to-ml-in-python/data/citibike.csv", parse_dates=["starttime"])
y_b = bikes.set_index("starttime").resample("3h").size().astype(float)
X_b = pd.DataFrame({"hour": y_b.index.hour, "weekday": y_b.index.weekday, "t": np.arange(len(y_b)),
                    "prev": y_b.shift(1).values, "prev_day": y_b.shift(8).values}, index=y_b.index).dropna()
y_b = y_b.loc[X_b.index]
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
    """Fit one model per knob value on the 1,500 rows; score on the full validation set."""
    out = []
    for v in values:
        m = make_model(v).fit(Xs, ys)
        out.append((v, roc_auc_score(ys, m.predict_proba(Xs)[:, 1]), roc_auc_score(ya_val, m.predict_proba(Xa_val)[:, 1])))
    return np.array(out)

gbc = lambda **k: make_pipeline(prep, GBC(n_estimators=300, max_depth=3, random_state=0, **k))
tree = lambda **k: make_pipeline(prep, DecisionTreeClassifier(random_state=0, **k))
results = {
    "logistic: L2 strength C": curve(lambda c: make_pipeline(prep, LogisticRegression(C=c, max_iter=5000)), [.001, .003, .01, .03, .1, .3, 1, 3, 10, 100, 1000]),
    "tree: max_depth": curve(lambda d: tree(max_depth=d), [1, 2, 3, 4, 6, 8, 12, 16, 24]),
    "tree: min_samples_leaf": curve(lambda l: tree(min_samples_leaf=l), [1, 2, 5, 10, 20, 50, 100, 200]),
    "boosting: learning_rate": curve(lambda r: gbc(learning_rate=r), [.003, .01, .03, .1, .3, 1]),
    "boosting: subsample": curve(lambda s: gbc(learning_rate=.1, subsample=s), [.1, .2, .3, .5, .7, 1.0]),
}
print(f"{'knob':26s} {'value':>6s} {'train':>6s} {'val':>6s}")
for k, a in results.items():
    for i in sorted({0, int(a[:, 2].argmax()), len(a) - 1}):
        print(f"{k:26s} {a[i, 0]:6g} {a[i, 1]:6.3f} {a[i, 2]:6.3f}" + ("  <- best" if i == a[:, 2].argmax() else ""))

print("\n    C   L1 nonzero  L1 val   L2 nonzero  L2 val")
for c in (.01, .03, .1, 1, 100):
    l1 = make_pipeline(prep, LogisticRegression(penalty="l1", solver="liblinear", C=c)).fit(Xs, ys)
    l2 = make_pipeline(prep, LogisticRegression(C=c, max_iter=5000)).fit(Xs, ys)
    print(f"{c:5g} {np.sum(l1[-1].coef_ != 0):11d} {roc_auc_score(ya_val, l1.predict_proba(Xa_val)[:, 1]):7.3f} "
          f"{np.sum(l2[-1].coef_ != 0):12d} {roc_auc_score(ya_val, l2.predict_proba(Xa_val)[:, 1]):7.3f}")
```
```python
import torch
from torch import nn
torch.set_num_threads(4)
enc = clone(prep).fit(Xs)
def dense(X):
    Z = enc.transform(X)
    return Z.toarray() if hasattr(Z, "toarray") else Z

Xs_np, Xv_np = dense(Xs), dense(Xa_val)
T_s, T_val = torch.tensor(Xs_np, dtype=torch.float32), torch.tensor(Xv_np, dtype=torch.float32)
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

wd_vals, do_vals = [0, .1, 1, 3, 10, 30, 100], [0, .1, .3, .5, .7, .9, .95]
results["net: weight decay"] = np.array([(w, *net_auc(weight_decay=w)) for w in wd_vals])
results["net: dropout"] = np.array([(p, *net_auc(dropout=p)) for p in do_vals])
for k in ("net: weight decay", "net: dropout"):
    print(k)
    for v, tr, va in results[k]:
        print(f"  {v:6g} train {tr:.3f} val {va:.3f}")
```
```python
show = ["logistic: L2 strength C", "tree: max_depth", "boosting: learning_rate", "boosting: subsample", "net: weight decay", "net: dropout"]
logx = {"logistic: L2 strength C", "boosting: learning_rate"}
fig, axes = plt.subplots(2, 3, figsize=(11, 5.6), sharey=True)
for ax, k in zip(axes.flat, show):
    a = results[k]
    ax.plot(a[:, 0], a[:, 1], "o-", color=TRAIN, label="train"); ax.plot(a[:, 0], a[:, 2], "o-", color=VAL, label="validation")
    if k in logx: ax.set_xscale("log")
    if k == "net: weight decay": ax.set_xscale("symlog", linthresh=.1)
    ax.set_title(k, loc="left"); i = a[:, 2].argmax(); ax.plot(a[i, 0], a[i, 2], "o", ms=11, mfc="none", color=INK)
    ax.set_ylim(.7, 1.005)
axes[0, 0].legend(frameon=False, loc="lower right")
for ax in axes[:, 0]: ax.set_ylabel("AUC, 1,500 training rows")
fig.tight_layout(); fig.savefig(IMG + "training-tuning-regularisation-knobs-adult.png", dpi=150)
```
```python
w, b = np.zeros(Xs_np.shape[1]), 0.0
yy = ys.values
for step in range(1, 100001):
    p = 1 / (1 + np.exp(-(Xs_np @ w + b)))
    w -= 0.3 * Xs_np.T @ (p - yy) / len(yy); b -= 0.3 * (p - yy).mean()
    if step in {10, 100, 1000, 10000, 100000}:
        s = Xv_np @ w + b
        print(f"gradient descent, step {step:6d}: size of weights {np.linalg.norm(w):6.2f}  val AUC {roc_auc_score(ya_val, s):.4f}")
for c in (.003, .01, .03, .1, 1, 10, 1000):
    m = LogisticRegression(C=c, max_iter=20000).fit(Xs_np, yy)
    print(f"L2 penalty, C={c:<6g}          : size of weights {np.linalg.norm(m.coef_):6.2f}  val AUC {roc_auc_score(ya_val, m.decision_function(Xv_np)):.4f}")
```
```python
base = dict(categorical_features="from_dtype", learning_rate=0.3, max_leaf_nodes=63, min_samples_leaf=5, random_state=0)
print("patience  stopped at  best round  val loss as fitted  val loss cut back to best")
for pat in (5, 25, 100):
    # sklearn holds out 15% of the training rows to decide when to stop
    m = HGB(max_iter=1000, early_stopping=True, n_iter_no_change=pat, validation_fraction=0.15, **base).fit(Xa_tr, ya_tr)
    best = int(np.argmax(m.validation_score_))       # entry 0 is before any tree, so the index is the round
    staged = list(m.staged_predict_proba(Xa_val))
    print(f"{pat:8d} {m.n_iter_:11d} {best:11d} {log_loss(ya_val, staged[-1]):19.4f} {log_loss(ya_val, staged[best - 1]):26.4f}")
m = HGB(max_iter=1000, early_stopping=False, **base).fit(Xa_tr, ya_tr)
print(f"no early stopping, 1000 rounds: val loss {log_loss(ya_val, m.predict_proba(Xa_val)):.4f}")
```
```python
import time, itertools, optuna
from optuna.samplers import RandomSampler, TPESampler
from optuna.importance import get_param_importances, FanovaImportanceEvaluator
optuna.logging.set_verbosity(optuna.logging.WARNING)

X_sr, X_rr = train_test_split(Xa_val, stratify=ya_val, test_size=0.5, random_state=0)
search_idx, report_idx = Xa_val.index.get_indexer(X_sr.index), Xa_val.index.get_indexer(X_rr.index)
yv_ = ya_val.values

def evaluate(p):
    """Fit one configuration. Returns its AUC on the search rows, its AUC on the report rows, and its scores."""
    m = HGB(categorical_features="from_dtype", max_iter=200, early_stopping=False, random_state=0, **p).fit(Xa_tr, ya_tr)
    q = m.predict_proba(Xa_val)[:, 1]
    return roc_auc_score(yv_[search_idx], q[search_idx]), roc_auc_score(yv_[report_idx], q[report_idx]), q

def suggest(tr):
    return {"learning_rate": tr.suggest_float("learning_rate", .01, .5, log=True),
            "max_leaf_nodes": tr.suggest_int("max_leaf_nodes", 4, 128, log=True),
            "min_samples_leaf": tr.suggest_int("min_samples_leaf", 5, 200, log=True),
            "l2_regularization": tr.suggest_float("l2_regularization", 1e-3, 30, log=True),
            "max_features": tr.suggest_float("max_features", .3, 1.)}

def run_sampler(sampler, budget=32):
    log = []
    def objective(tr):
        p = suggest(tr); r = evaluate(p); log.append((p, *r))
        return r[0]                                  # the search only ever sees the search rows
    study = optuna.create_study(direction="maximize", sampler=sampler)
    study.optimize(objective, n_trials=budget)
    return log, study

t0 = time.time()
default = evaluate({})
keys = ["learning_rate", "max_leaf_nodes", "min_samples_leaf", "l2_regularization", "max_features"]
grid5 = [dict(zip(keys, v)) for v in itertools.product((.03, .2), (8, 64), (10, 100), (.01, 1.), (.5, 1.))]
grid3 = [dict(zip(keys, v)) for v in itertools.product((.01, .03, .1, .3), (4, 8, 32, 128), (10, 100))]
runs, studies = {}, {}
for name, g in [("grid 2x2x2x2x2", grid5), ("grid 4x4x2", grid3)]:
    res = [(p, *evaluate(p)) for p in g]
    runs[name] = [[res[i] for i in np.random.default_rng(s).permutation(32)] for s in range(5)]   # arrival order only
for name, S in [("random", RandomSampler), ("TPE", TPESampler)]:
    out = [run_sampler(S(seed=s)) for s in range(5)]
    runs[name], studies[name] = [o[0] for o in out], [o[1] for o in out]

def winner(run, k=32): return max(run[:k], key=lambda t: t[1])
print(f"default settings: search {default[0]:.4f} report {default[1]:.4f}   ({time.time() - t0:.0f}s for all trials)")
print(f"{'method':15s} {'search@8':>8s} {'report@8':>8s} {'search@32':>9s} {'report@32':>9s} {'sd':>7s} {'distinct LRs':>12s}")
for name, rs in runs.items():
    w8, w32 = [winner(r, 8) for r in rs], [winner(r) for r in rs]
    print(f"{name:15s} {np.mean([w[1] for w in w8]):8.4f} {np.mean([w[2] for w in w8]):8.4f} {np.mean([w[1] for w in w32]):9.4f} "
          f"{np.mean([w[2] for w in w32]):9.4f} {np.std([w[2] for w in w32], ddof=1):7.4f} {len({t[0]['learning_rate'] for t in rs[0]}):12d}")
imps = [get_param_importances(s, evaluator=FanovaImportanceEvaluator(seed=0)) for s in studies["random"]]
print("importance over the random searches, mean (min-max):")
for k in keys:
    v = [i[k] for i in imps]
    print(f"  {k:18s} {np.mean(v):.2f} ({min(v):.2f}-{max(v):.2f})")
print("TPE seed 0 winner:", {k: round(v, 3) for k, v in winner(runs["TPE"][0])[0].items()})
```
```python
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
styles = {"grid 2x2x2x2x2": ("#6b6b68", "--"), "grid 4x4x2": ("#7a4fbf", ":"), "random": (TRAIN, "-"), "TPE": (VAL, "-")}
ax = axes[0]
for name, rs in runs.items():
    bsf = np.maximum.accumulate(np.array([[t[1] for t in r] for r in rs]), axis=1)
    ax.plot(range(1, 33), bsf.mean(0), color=styles[name][0], ls=styles[name][1], label=name)
ax.axhline(default[0], color=INK, lw=1); ax.annotate("default settings", (32, default[0]), xytext=(0, -11), textcoords="offset points", fontsize=8, ha="right")
ax.set_xlabel("trials spent, mean of 5 seeds"); ax.set_ylabel("best search-rows AUC so far"); ax.legend(frameon=False, loc="lower right", fontsize=8)
ax = axes[1]
rand = [t for r in runs["random"] for t in r]
ax.plot([t[0]["learning_rate"] for t in rand], [t[1] for t in rand], "o", ms=5, color=TRAIN, alpha=.6, label="random trials, 5 seeds")
ax.plot([t[0]["learning_rate"] for t in runs["grid 2x2x2x2x2"][0]], [t[1] for t in runs["grid 2x2x2x2x2"][0]], "D", ms=6, color="#6b6b68", alpha=.7, label="grid 2x2x2x2x2")
ax.set_xscale("log"); ax.set_xlabel("learning_rate"); ax.set_ylabel("search-rows AUC"); ax.legend(frameon=False, loc="lower left", fontsize=8)
fig.tight_layout(); fig.savefig(IMG + "training-tuning-search-comparison-adult.png", dpi=150)
```
```python
q = np.array([t[3] for t in runs["random"][0]])    # 32 configurations' scores on every validation row
rng = np.random.default_rng(0)
print("selection rows  winner there  winner on the other rows  optimism  sd on other rows")
for n_sel in (100, 300, 1000, 3256):
    there, other = [], []
    for _ in range(100):
        perm = rng.permutation(len(yv_)); a, b = perm[:n_sel], perm[n_sel:]
        sc = [roc_auc_score(yv_[a], c[a]) for c in q]
        j = int(np.argmax(sc)); there.append(sc[j]); other.append(roc_auc_score(yv_[b], q[j, b]))
    print(f"{n_sel:14d} {np.mean(there):13.4f} {np.mean(other):25.4f} {np.mean(there) - np.mean(other):9.4f} {np.std(other, ddof=1):17.4f}")
print(f"best of the 32 on all {len(yv_)} rows: {max(roc_auc_score(yv_, c) for c in q):.4f}")
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
print("outer folds", out[:, 1].round(4), "chosen learning rates", out[:, 2].round(3))
print(f"inner best {out[:, 0].mean():.4f}, nested outer {out[:, 1].mean():.4f} sd {out[:, 1].std(ddof=1):.4f}  [{time.time() - t0:.0f}s]")
```
