"""Predicting credit default when defaulters are rare: errors, imbalance, calibration, drift.

Run from this folder:
    uv run --python 3.12 --with scikit-learn --with imbalanced-learn --with pandas \
        --with xlrd --with matplotlib --with scipy python credit_default_lab.py

The first run downloads the UCI "Default of Credit Card Clients" file (CC BY 4.0), checks its
sha256 and caches it under data/. Every experiment repeats over seeds, keeps each seed's split
the same for every method, and saves a table under results/. Figures go to
../../../sources/images/. Delete results/ to recompute everything.

The discussion is in ../../notes/10-imbalance-errors-and-drift.md, which imports this file.
"""

import hashlib
import io
import os
import sys
import urllib.request
import warnings
import zipfile
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")  # parallelism is across seeds, not inside a fit

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE, SMOTENC, RandomOverSampler
from imblearn.pipeline import Pipeline
from imblearn.under_sampling import RandomUnderSampler
from joblib import Parallel, delayed
from scipy.stats import norm
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore", message=".*xlrd engine is deprecated.*")

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
RESULTS = HERE / "results"
IMAGES = HERE.parents[2] / "sources" / "images"

URL = "https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip"
SHA256 = "56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602"

TARGET = "default payment next month"
PAY = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
BILL = [f"BILL_AMT{i}" for i in range(1, 7)]
PAID = [f"PAY_AMT{i}" for i in range(1, 7)]
FEATURES = ["LIMIT_BAL", "EDUCATION"] + PAY + BILL + PAID

PREVALENCE = 0.03  # the case: 3% of applicants default
COST_FN = 5.0  # approving a defaulter costs five times...
COST_FP = 1.0  # ...what declining a good customer costs
BAYES = COST_FP / (COST_FP + COST_FN)  # decline when PD >= 1/6
N_SEEDS = 20

BLUE, ORANGE, AQUA, YELLOW, MAGENTA, VIOLET = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6")
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"


# ---------------------------------------------------------------------------------------- data
def load_credit():
    """Fetch the pinned file once, verify it, and return the 30,000 raw rows."""
    DATA.mkdir(exist_ok=True)
    path = DATA / "default-of-credit-card-clients.zip"
    if not path.exists():
        print(f"downloading {URL}", file=sys.stderr)
        with urllib.request.urlopen(URL, timeout=120) as r:
            path.write_bytes(r.read())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != SHA256:
        path.unlink()
        raise RuntimeError(f"checksum mismatch: got {digest}, expected {SHA256}")
    with zipfile.ZipFile(path) as z:
        raw = z.read("default of credit card clients.xls")
    return pd.read_excel(io.BytesIO(raw), header=1, index_col=0, engine="xlrd")


def features(raw):
    """Turn raw rows into model inputs. Sex, marriage and age are left out on purpose."""
    x = pd.DataFrame(index=raw.index)
    x["LIMIT_BAL"] = np.log1p(raw["LIMIT_BAL"])
    x["EDUCATION"] = raw["EDUCATION"].where(raw["EDUCATION"].isin([1, 2, 3]), 4)  # 0, 5, 6 undocumented
    for c in PAY:
        x[c] = raw[c]
    for c in BILL + PAID:
        x[c] = np.sign(raw[c]) * np.log1p(np.abs(raw[c]))  # bills can be negative (credit balance)
    return x[FEATURES].astype(float)


def make_rare(raw, prevalence=PREVALENCE, seed=0):
    """Keep every good customer and a random subset of defaulters, to reach `prevalence`.

    Returns the kept rows and the defaulters left over. This changes the prior and nothing else:
    who defaults, given their features, is untouched. Absolute rates are artefacts of this choice.
    """
    y = raw[TARGET].to_numpy()
    good, bad = np.flatnonzero(y == 0), np.flatnonzero(y == 1)
    want = min(int(round(prevalence / (1 - prevalence) * len(good))), len(bad))
    rng = np.random.default_rng(seed)
    bad = rng.permutation(bad)
    keep = rng.permutation(np.concatenate([good, bad[:want]]))
    return raw.iloc[keep], raw.iloc[bad[want:]]


def split(raw, seed=0):
    """A stratified 60/20/20 train, validation and test split of raw rows."""
    tr, rest = train_test_split(raw, test_size=0.4, stratify=raw[TARGET], random_state=seed)
    va, te = train_test_split(rest, test_size=0.5, stratify=rest[TARGET], random_state=seed)
    return tr, va, te


# ------------------------------------------------------------------------------------- metrics
def expected_cost(y, p, threshold, fn=COST_FN, fp=COST_FP):
    """Cost per 1,000 applicants when we decline everyone with p >= threshold."""
    decline = p >= threshold
    return 1000 * (fn * np.sum((y == 1) & ~decline) + fp * np.sum((y == 0) & decline)) / len(y)


def tune_threshold(y, p, fn=COST_FN, fp=COST_FP):
    """The threshold that minimises cost on (y, p). Above max(p) means approve everyone."""
    order = np.argsort(-p)
    ys, ps = y[order], p[order]
    costs = fn * (y.sum() - np.cumsum(ys)) + fp * np.cumsum(1 - ys)
    valid = np.r_[ps[1:] != ps[:-1], True]  # tied scores move together
    best = np.flatnonzero(valid)[np.argmin(costs[valid])]
    if fn * y.sum() <= costs[best]:
        return float(ps[0]) + 1e-9
    return float(ps[best])


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def expit(z):
    return 1 / (1 + np.exp(-z))


def calibration_intercept(y, p):
    """Log-odds shift that makes the mean right, slope fixed at 1. Below 0 means overestimation."""
    z, a = logit(p), 0.0
    for _ in range(50):
        q = expit(a + z)
        a += (y - q).sum() / max((q * (1 - q)).sum(), 1e-9)
    return a


def calibration_slope(y, p):
    """Slope below 1 means the predictions are too extreme."""
    m = LogisticRegression(C=1e6, max_iter=1000).fit(logit(p).reshape(-1, 1), y)
    return float(m.coef_[0, 0])


def ece(y, p, bins=10):
    """Expected calibration error over equal-count bins."""
    parts = np.array_split(np.argsort(p), bins)
    return float(sum(len(i) / len(y) * abs(p[i].mean() - y[i].mean()) for i in parts))


def psi(reference, current, bins=10, eps=1e-4):
    """Population stability index on quantile bins of the reference (same recipe as note 02)."""
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    if len(edges) < 3:
        edges = np.array([-np.inf, float(np.median(reference)), np.inf])
    r = np.histogram(reference, edges)[0] / len(reference) + eps
    c = np.histogram(current, edges)[0] / len(current) + eps
    return float(np.sum((c - r) * np.log(c / r)))


def platt(p_val, y_val):
    m = LogisticRegression(C=1e6, max_iter=1000).fit(logit(p_val).reshape(-1, 1), y_val)
    return lambda p: m.predict_proba(logit(p).reshape(-1, 1))[:, 1]


def isotonic(p_val, y_val):
    m = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(p_val, y_val)
    return lambda p: m.predict(p)


def prior_shift(p, odds_train, odds_true):
    """Undo a known change of class odds by shifting log-odds, as in note 02."""
    return expit(logit(p) - np.log(odds_train / odds_true))


# ------------------------------------------------------------------------------------ learners
LEARNERS = {
    "boosted": (
        lambda s: HistGradientBoostingClassifier(learning_rate=0.05, early_stopping=False, random_state=s),
        [{"max_leaf_nodes": a, "max_iter": b} for a in (4, 15) for b in (100, 300)],
    ),
    "logistic": (
        lambda s: LogisticRegression(max_iter=2000),
        [{"C": c} for c in (0.01, 1.0)],
    ),
    "tree": (
        lambda s: DecisionTreeClassifier(random_state=s),
        [{"max_depth": d, "min_samples_leaf": m} for d in (4, 8) for m in (5, 50)],
    ),
}

CATEGORICAL = [FEATURES.index(c) for c in ["EDUCATION"] + PAY]

# method name -> (list of sampler settings to try, whether to use class weights)
METHODS = {
    "nothing": ([None], False),
    "class weights": ([None], True),
    "undersample 1:1": ([("rus", 1.0)], False),
    "oversample 1:1": ([("ros", 1.0)], False),
    "SMOTE 1:1": ([("smote", 1.0)], False),
    "SMOTE, ratio tuned": ([("smote", r) for r in (0.1, 0.25, 0.5, 1.0)], False),
    "SMOTE + undersample": ([("smote+rus", 0.2)], False),
    "SMOTE-NC 1:1": ([("smotenc", 1.0)], False),
}


def make_pipeline(sampler, learner, params, weights, seed):
    """Scale, resample, fit. The sampler is a pipeline step, so it runs only on training folds."""
    steps = [("scale", StandardScaler())]
    if sampler:
        kind, ratio = sampler
        if kind == "rus":
            steps.append(("rus", RandomUnderSampler(sampling_strategy=ratio, random_state=seed)))
        if kind == "ros":
            steps.append(("ros", RandomOverSampler(sampling_strategy=ratio, random_state=seed)))
        if kind == "smote":
            steps.append(("smote", SMOTE(sampling_strategy=ratio, k_neighbors=5, random_state=seed)))
        if kind == "smotenc":
            steps.append(("smote", SMOTENC(CATEGORICAL, sampling_strategy=ratio, random_state=seed)))
        if kind == "smote+rus":  # Chawla's recipe: oversample the rare class, then shrink the common one
            steps.append(("smote", SMOTE(sampling_strategy=ratio, random_state=seed)))
            steps.append(("rus", RandomUnderSampler(sampling_strategy=1.0, random_state=seed)))
    clf = LEARNERS[learner][0](seed).set_params(**params)
    if weights:
        clf.set_params(class_weight="balanced")
    steps.append(("clf", clf))
    return Pipeline(steps)


def fit_best(xtr, ytr, xva, yva, method, learner, seed):
    """Try each setting and keep the best validation PR-AUC. Validation data is never resampled."""
    samplers, weights = METHODS[method]
    odds = ytr.mean() / (1 - ytr.mean())
    # a ratio at or below today's odds would mean removing defaulters, so it cannot be tried
    samplers = [s if not s or s[1] > 1.05 * odds else (s[0], min(1.0, 2 * odds)) for s in samplers]
    samplers = list(dict.fromkeys(samplers))
    best = (-1.0, None, None)
    for sampler in samplers:
        for params in LEARNERS[learner][1]:
            m = make_pipeline(sampler, learner, params, weights, seed).fit(xtr, ytr)
            score = average_precision_score(yva, m.predict_proba(xva)[:, 1])
            if score > best[0]:
                best = (score, m, sampler)
    return best[1], best[2]


# ---------------------------------------------------------------------------------- comparison
def one_seed(raw, seed, prevalence, learner, methods):
    rare, _ = make_rare(raw, prevalence, seed)
    tr, va, te = split(rare, seed)
    xtr, xva, xte = features(tr), features(va), features(te)
    ytr, yva, yte = (d[TARGET].to_numpy() for d in (tr, va, te))
    rows = []
    for method in methods:
        m, sampler = fit_best(xtr, ytr, xva, yva, method, learner, seed)
        pv, pt = m.predict_proba(xva)[:, 1], m.predict_proba(xte)[:, 1]
        cal = platt(pv, yva)(pt)
        row = dict(
            seed=seed, method=method, learner=learner, prevalence=prevalence,
            pr_auc=average_precision_score(yte, pt), roc_auc=roc_auc_score(yte, pt),
            brier=brier_score_loss(yte, pt), brier_platt=brier_score_loss(yte, cal),
            mean_pd=pt.mean(), mean_pd_platt=cal.mean(), observed=yte.mean(),
            cal_intercept=calibration_intercept(yte, pt), cal_slope=calibration_slope(yte, pt),
            ece=ece(yte, pt), ece_platt=ece(yte, cal),
            accuracy=np.mean((pt >= 0.5) == yte), recall_05=np.mean(pt[yte == 1] >= 0.5),
            ratio=sampler[1] if sampler else np.nan, test_events=int(yte.sum()),
        )
        for r in (5, 10, 20):
            t = tune_threshold(yva, pv, fn=r)
            b = 1 / (1 + r)
            row[f"thr_tuned_{r}"] = t
            row[f"cost_05_{r}"] = expected_cost(yte, pt, 0.5, fn=r)
            row[f"cost_tuned_{r}"] = expected_cost(yte, pt, t, fn=r)
            row[f"cost_bayes_{r}"] = expected_cost(yte, pt, b, fn=r)
            row[f"cost_platt_{r}"] = expected_cost(yte, cal, b, fn=r)
            row[f"cost_all_{r}"] = 1000.0 * r * yte.mean()
        row["decline_tuned_5"] = np.mean(pt >= row["thr_tuned_5"])
        row["recall_tuned_5"] = np.mean(pt[yte == 1] >= row["thr_tuned_5"])
        rows.append(row)
    return rows


def _cached(name, fn):
    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / f"{name}.csv"
    if path.exists():
        return pd.read_csv(path)
    df = fn()
    df.to_csv(path, index=False)
    return df


def compare(raw, learner="boosted", prevalence=PREVALENCE, seeds=N_SEEDS, methods=None):
    """One row per seed and method. The same seed gives every method the same split."""
    methods = list(methods or METHODS)
    name = f"compare-{learner}-{prevalence:g}-{seeds}-{len(methods)}"

    def run():
        out = Parallel(n_jobs=-1)(
            delayed(one_seed)(raw, s, prevalence, learner, methods) for s in range(seeds))
        return pd.DataFrame([r for rows in out for r in rows])

    return _cached(name, run)


def paired(df, a, b, col):
    """Mean difference a minus b across seeds, its SD, and how often a is lower."""
    wide = df.pivot(index="seed", columns="method", values=col)
    d = wide[a] - wide[b]
    return d.mean(), d.std(ddof=1), int((d < 0).sum()), len(d)


# ----------------------------------------------------------------------------------- the leak
def _leak_seed(raw, seed, kind):
    rare, _ = make_rare(raw, PREVALENCE, seed)
    tr, va, te = split(rare, seed)
    pool = pd.concat([tr, va])
    x, y = features(pool), pool[TARGET].to_numpy()
    xte, yte = features(te), te[TARGET].to_numpy()
    params = {"max_leaf_nodes": 15, "max_iter": 300}
    sampler = (kind, 1.0)
    cv = StratifiedKFold(5, shuffle=True, random_state=seed)
    pipe = make_pipeline(sampler, "boosted", params, False, seed)
    honest = cross_val_score(pipe, x, y, cv=cv, scoring="roc_auc").mean()
    # the mistake: resample first, then cross-validate on the resampled table
    pre = Pipeline(pipe.steps[:-1]).fit_resample(x, y)
    bare = make_pipeline(None, "boosted", params, False, seed)
    leaked = cross_val_score(bare, pre[0], pre[1], cv=cv, scoring="roc_auc").mean()
    true = roc_auc_score(yte, pipe.fit(x, y).predict_proba(xte)[:, 1])
    return dict(seed=seed, sampler=kind, leaked_cv=leaked, pipeline_cv=honest, test=true)


def leak(raw, seeds=10):
    return _cached(f"leak-{seeds}", lambda: pd.DataFrame(Parallel(n_jobs=-1)(
        delayed(_leak_seed)(raw, s, k) for s in range(seeds) for k in ("ros", "smote"))))


# ----------------------------------------------------------------------------- how much data
def sample_size_two_proportions(p1, p2, alpha=0.05, power=0.8):
    """Applicants per arm to tell two default rates apart, two-sided normal approximation."""
    z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    return int(np.ceil(z**2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p1 - p2) ** 2))


def simulated_power(p1, p2, n, alpha=0.05, sims=20000, seed=0):
    """Check the formula: how often does a two-proportion z test detect the difference?"""
    rng = np.random.default_rng(seed)
    a, b = rng.binomial(n, p1, sims) / n, rng.binomial(n, p2, sims) / n
    pool = (a + b) / 2
    z = (a - b) / np.sqrt(2 * pool * (1 - pool) / n)
    return float(np.mean(np.abs(z) > norm.ppf(1 - alpha / 2)))


def _events_seed(raw, seed):
    """Fit once, then measure how much the score moves with the number of test events."""
    rare, spare = make_rare(raw, PREVALENCE, seed)
    tr, va, te = split(rare, seed)
    m = make_pipeline(None, "boosted", {"max_leaf_nodes": 4, "max_iter": 300}, False, seed)
    m.fit(features(tr), tr[TARGET].to_numpy())
    pool = pd.concat([va, te, spare])
    p, y = m.predict_proba(features(pool))[:, 1], pool[TARGET].to_numpy()
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    rng = np.random.default_rng(seed + 1000)
    odds = (1 - PREVALENCE) / PREVALENCE
    rows = []
    for events in (10, 25, 50, 100, 200):
        for b in range(200):
            i = np.r_[rng.choice(pos, events, replace=False),
                      rng.choice(neg, int(events * odds), replace=False)]
            rows.append(dict(seed=seed, events=events, rep=b, roc_auc=roc_auc_score(y[i], p[i]),
                             pr_auc=average_precision_score(y[i], p[i]),
                             rate_ok=np.mean(p[i] >= BAYES)))
    return rows


def metric_noise(raw, seeds=5):
    """SD of a test score, by number of defaulters in the test set."""
    def run():
        rows = Parallel(n_jobs=-1)(delayed(_events_seed)(raw, s) for s in range(seeds))
        d = pd.DataFrame([r for s in rows for r in s])
        return d.groupby(["seed", "events"])[["roc_auc", "pr_auc"]].std().groupby("events").mean().reset_index()
    return _cached(f"metric-noise-{seeds}", run)


def _train_seed(raw, seed):
    rare, _ = make_rare(raw, PREVALENCE, seed)
    tr, va, te = split(rare, seed)
    xte, yte = features(te), te[TARGET].to_numpy()
    pos, neg = tr[tr[TARGET] == 1], tr[tr[TARGET] == 0]
    rng = np.random.default_rng(seed + 2000)
    rows = []
    grid = [(e, int(round(e * 32.33))) for e in (25, 50, 100, 200, 433)] + [
        (433, 433), (433, 1299), (433, 4330), (100, 14000 - 1)]
    for events, goods in grid:
        goods = min(goods, len(neg))
        s = pd.concat([pos.sample(min(events, len(pos)), random_state=int(rng.integers(1e9))),
                       neg.sample(goods, random_state=int(rng.integers(1e9)))])
        m = make_pipeline(None, "boosted", {"max_leaf_nodes": 4, "max_iter": 100}, False, seed)
        m.fit(features(s), s[TARGET].to_numpy())
        p = m.predict_proba(xte)[:, 1]
        rows.append(dict(seed=seed, events=min(events, len(pos)), goods=goods, roc_auc=roc_auc_score(yte, p),
                         pr_auc=average_precision_score(yte, p)))
    return rows


def training_events(raw, seeds=N_SEEDS):
    """Test score against defaulters and good customers in the training set."""
    def run():
        rows = Parallel(n_jobs=-1)(delayed(_train_seed)(raw, s) for s in range(seeds))
        return pd.DataFrame([r for s in rows for r in s])
    return _cached(f"training-events-{seeds}", run)


# --------------------------------------------------------------------------------- calibration
def _calibration_seed(raw, seed):
    rare, _ = make_rare(raw, PREVALENCE, seed)
    tr, va, te = split(rare, seed)
    xtr, xva, xte = features(tr), features(va), features(te)
    ytr, yva, yte = (d[TARGET].to_numpy() for d in (tr, va, te))
    odds_true = ytr.mean() / (1 - ytr.mean())
    rows, curves = [], []
    for method in ("nothing", "class weights", "undersample 1:1", "oversample 1:1", "SMOTE 1:1"):
        m, _ = fit_best(xtr, ytr, xva, yva, method, "boosted", seed)
        pv, pt = m.predict_proba(xva)[:, 1], m.predict_proba(xte)[:, 1]
        versions = {"raw": pt, "Platt": platt(pv, yva)(pt), "isotonic": isotonic(pv, yva)(pt)}
        if method != "nothing":
            versions["prior shift"] = prior_shift(pt, 1.0, odds_true)  # all these train at 1:1 odds
        for fix, p in versions.items():
            rows.append(dict(seed=seed, method=method, fix=fix, mean_pd=p.mean(), observed=yte.mean(),
                             brier=brier_score_loss(yte, p), ece=ece(yte, p),
                             intercept=calibration_intercept(yte, p), slope=calibration_slope(yte, p),
                             roc_auc=roc_auc_score(yte, p), cost_bayes=expected_cost(yte, p, BAYES),
                             # pricing: expected loss on the book, per 1,000 approved at PD < 1/6
                             approved=np.mean(p < BAYES),
                             pred_loss=1000 * p[p < BAYES].mean() if (p < BAYES).any() else np.nan,
                             real_loss=1000 * yte[p < BAYES].mean() if (p < BAYES).any() else np.nan))
            if fix in ("raw", "Platt"):
                curves.append(pd.DataFrame(dict(seed=seed, method=method, fix=fix, p=p, y=yte)))
    return rows, pd.concat(curves)


def calibration(raw, seeds=N_SEEDS):
    """Each method's probabilities, before and after each fix, plus pooled reliability points."""
    RESULTS.mkdir(exist_ok=True)
    table, points = RESULTS / f"calibration-{seeds}.csv", RESULTS / f"reliability-{seeds}.csv"
    if table.exists() and points.exists():
        return pd.read_csv(table), pd.read_csv(points)
    out = Parallel(n_jobs=-1)(delayed(_calibration_seed)(raw, s) for s in range(seeds))
    df = pd.DataFrame([r for rows, _ in out for r in rows])
    curves = pd.concat([c for _, c in out])
    curves["bin"] = curves.groupby(["method", "fix"])["p"].transform(
        lambda s: pd.qcut(s.rank(method="first"), 10, labels=False))
    rel = curves.groupby(["method", "fix", "bin"]).agg(p=("p", "mean"), y=("y", "mean")).reset_index()
    df.to_csv(table, index=False)
    rel.to_csv(points, index=False)
    return df, rel


# --------------------------------------------------------------------------------------- drift
def monthly_psi(raw):
    """Real drift inside the file: each month's repayment status and bill against April 2005."""
    months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]
    x = features(raw)
    rows = []
    for i, month in enumerate(months):
        pay, bill = PAY[5 - i], BILL[5 - i]
        rows.append(dict(month=month, pay_psi=psi(x["PAY_6"], x[pay]), bill_psi=psi(x["BILL_AMT6"], x[bill]),
                         pay_at_1=int((raw[pay] == 1).sum())))
    return pd.DataFrame(rows)


def stale_by_one_month(raw):
    """Serving reads a feature store that is one month behind training's view of the customer."""
    out = raw.copy()
    for cols in (PAY, BILL, PAID):
        for now, before in zip(cols[:-1], cols[1:]):
            out[now] = raw[before]
    return out


def bills_in_thousands(raw):
    """A broken feed: an upstream job starts sending amounts in thousands."""
    out = raw.copy()
    out[BILL + PAID] = raw[BILL + PAID] / 1000
    return out


def latest_status_defaults_to_zero(raw):
    """A late join: this month's status is missing, and serving fills it with 0, 'revolving'."""
    out = raw.copy()
    out["PAY_0"] = 0
    return out


def _window_report(name, m, cal, xref, sref, raw_window, y_window, seed):
    x = features(raw_window)
    p = cal(m.predict_proba(x)[:, 1])
    by_feature = {c: psi(xref[c], x[c]) for c in FEATURES}
    worst = max(by_feature, key=by_feature.get)
    return dict(seed=seed, scenario=name, n=len(y_window), events=int(y_window.sum()),
                default_rate=y_window.mean(), mean_pd=p.mean(), worst_feature=worst,
                worst_psi=by_feature[worst], score_psi=psi(sref, p), roc_auc=roc_auc_score(y_window, p),
                pr_auc=average_precision_score(y_window, p), decline=np.mean(p >= BAYES),
                cost=expected_cost(y_window, p, BAYES), brier=brier_score_loss(y_window, p))


def _drift_seed(raw, seed):
    rare, spare = make_rare(raw, PREVALENCE, seed)
    tr, va, te = split(rare, seed)
    m = make_pipeline(None, "boosted", {"max_leaf_nodes": 4, "max_iter": 300}, False, seed)
    m.fit(features(tr), tr[TARGET].to_numpy())
    cal = platt(m.predict_proba(features(va))[:, 1], va[TARGET].to_numpy())
    xref = features(va)
    sref = cal(m.predict_proba(xref)[:, 1])  # held-out reference, because train scores are overfitted
    rng = np.random.default_rng(seed + 3000)
    size = len(te) // 2
    rows = []

    def report(name, window, labels=None):
        y = window[TARGET].to_numpy() if labels is None else labels
        rows.append(_window_report(name, m, cal, xref, sref, window, y, seed))

    # no change: a random half of the test set, which also gives PSI's noise floor
    base = te.iloc[rng.choice(len(te), size, replace=False)]
    report("no change", base)

    # covariate shift: pick rows by their features only, so P(default | x) cannot change
    z = np.log1p(te["LIMIT_BAL"].to_numpy())
    z = (z - z.mean()) / z.std()
    w = np.exp(-1.0 * z)
    report("covariate: towards low limits", te.iloc[rng.choice(len(te), size, replace=False, p=w / w.sum())])

    # prior shift: the default rate doubles and P(x | default) stays the same, using spare real defaulters
    extra = spare.iloc[rng.choice(len(spare), int(base[TARGET].sum()), replace=False)]
    goods = base[base[TARGET] == 0]
    drop = goods.iloc[rng.choice(len(goods), len(extra), replace=False)].index
    report("prior: default rate doubles", pd.concat([base.drop(index=drop), extra]))

    # concept shift: the same customers and features, but what predicts default changes.
    # Forbearance cures most late payers, and a shock hits high-utilisation customers who paid on time.
    util = (base["BILL_AMT1"] / base["LIMIT_BAL"]).to_numpy()
    late, high = base["PAY_0"].to_numpy() >= 1, util >= np.quantile(util, 2 / 3)
    y = base[TARGET].to_numpy().copy()
    y[late & (y == 1) & (rng.random(len(y)) < 0.6)] = 0
    y[high & ~late & (y == 0) & (rng.random(len(y)) < 0.08)] = 1
    report("concept: what predicts default changes", base, labels=y)

    # train/serve skew: the same customers and labels, but serving computes features differently
    report("skew: features one month stale", stale_by_one_month(base))
    report("skew: amounts in thousands", bills_in_thousands(base))
    report("skew: PAY_0 filled with 0", latest_status_defaults_to_zero(base))
    return rows


def drift(raw, seeds=N_SEEDS):
    return _cached(f"drift-{seeds}", lambda: pd.DataFrame(
        [r for rows in Parallel(n_jobs=-1)(delayed(_drift_seed)(raw, s) for s in range(seeds)) for r in rows]))
