# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "matplotlib", "scikit-learn", "scipy"]
# ///
"""Chapter 2: which credit applications should the bank approve, and what do they cost in capital?

Run from this folder with: uv run ch02_credit_scoring.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold, train_test_split

import chartstyle as cs

cs.apply()
SEED = 20250101

# %% load
names = {"laufkont": "status", "laufzeit": "duration", "moral": "credit_history", "verw": "purpose",
         "hoehe": "amount", "sparkont": "savings", "beszeit": "employment", "rate": "installment_rate",
         "famges": "personal_status_sex", "buerge": "other_debtors", "wohnzeit": "residence", "verm": "property",
         "alter": "age", "weitkred": "other_plans", "wohn": "housing", "bishkred": "number_credits", "beruf": "job",
         "pers": "people_liable", "telef": "telephone", "gastarb": "foreign_worker", "kredit": "good"}
raw = pd.read_csv(Path("data/SouthGermanCredit.asc"), sep=" ").rename(columns=names)
raw["bad"] = 1 - raw.pop("good")
print(raw.shape, "bad rate", raw.bad.mean())
# Sanity check against Table 1 of Groemping (2019): "no checking account" is 45.00% of bad and 19.86% of good.
print((pd.crosstab(raw.status, raw.bad, normalize="columns") * 100).round(2).head(1).to_string())
train, test = train_test_split(raw, test_size=.3, stratify=raw.bad, random_state=SEED)
print(len(train), "train,", len(test), "test")

# %% woe
PROTECTED = ["personal_status_sex", "age", "foreign_worker"]    # never used to decide
CONTINUOUS = ["duration", "amount"]
candidates = [c for c in raw.columns if c not in PROTECTED + ["bad"]]


def fit_bins(x, y):
    """Coarse classes learned on training data only, then a weight of evidence for each."""
    if x.name in CONTINUOUS:
        edges = np.unique(np.quantile(x, [0, .2, .4, .6, .8, 1]))
        edges[0], edges[-1] = -np.inf, np.inf
        classes = pd.cut(x, edges)
    else:
        share = x.value_counts(normalize=True)
        rare = share[share < .05].index
        edges = list(rare)
        classes = x.where(~x.isin(rare), -1)        # sparse levels share one class
    good, bad = (y == 0), (y == 1)
    # 0.5 added to each cell so an empty class cannot give an infinite weight
    table = pd.DataFrame({"good": good.groupby(classes, observed=False).sum() + .5,
                          "bad": bad.groupby(classes, observed=False).sum() + .5})
    table["pct_good"] = table.good / table.good.sum()
    table["pct_bad"] = table.bad / table.bad.sum()
    table["woe"] = np.log(table.pct_good / table.pct_bad)
    iv = ((table.pct_good - table.pct_bad) * table.woe).sum()
    return {"edges": edges, "table": table, "iv": iv}


def apply_bins(x, fit):
    if x.name in CONTINUOUS:
        classes = pd.cut(x, fit["edges"])
    else:
        classes = x.where(~x.isin(fit["edges"]), -1)
    prior = 0.0                                      # a level unseen in training has no evidence
    return classes.map(fit["table"].woe).astype(float).fillna(prior)


bins = {c: fit_bins(train[c], train.bad) for c in candidates}
iv = pd.Series({c: f["iv"] for c, f in bins.items()}).sort_values(ascending=False)
print(iv.round(3).to_string())
print(bins["status"]["table"][["good", "bad", "woe"]].round(2).to_string())

# %% chart_woe
levels = {1: "No checking account", 2: "Below 0 DM", 3: "0 to 200 DM", 4: "200 DM or more, or salary"}
t = bins["status"]["table"]
fig, ax = plt.subplots(figsize=(8, 3.4))
labels = [levels[i] for i in t.index]
bars = ax.barh(labels[::-1], t.woe[::-1], height=.6,
               color=[cs.BLUE if v > 0 else cs.ORANGE for v in t.woe[::-1]])
ax.bar_label(bars, fmt="%+.2f", padding=4, color=cs.SECONDARY)
ax.axvline(0, color=cs.BASELINE, lw=1)
ax.grid(False)
ax.set_xlim(-1.1, 1.4)
ax.set_xlabel("Weight of evidence, training set (ln of share of goods / share of bads)")
ax.set_title("Checking-account status: above zero is safer than average")
ax.bar(0, 0, color=cs.BLUE, label="Safer")
ax.bar(0, 0, color=cs.ORANGE, label="Riskier")
ax.legend(loc="lower right")
cs.save(fig, "applied-credit-woe-status.png")

# %% fit
features = [c for c in iv.index if iv[c] >= .02]


def woe_frame(frame, bin_fits, cols):
    return pd.DataFrame({c: apply_bins(frame[c], bin_fits[c]) for c in cols}, index=frame.index)


model = LogisticRegression(C=1e6, max_iter=1000).fit(woe_frame(train, bins, features), train.bad)
coef = pd.Series(model.coef_[0], index=features)
print(len(features), "of", len(candidates), "candidates pass IV >= 0.02")
# Target is "bad" and a higher WoE is safer, so every coefficient should be negative.
wrong_sign = coef[coef > 0].index.tolist()
print("wrong sign, dropped:", wrong_sign)
features = [c for c in features if c not in wrong_sign]
model = LogisticRegression(C=1e6, max_iter=1000).fit(woe_frame(train, bins, features), train.bad)
coef = pd.Series(model.coef_[0], index=features)
print("intercept", round(model.intercept_[0], 3))
print(coef.round(2).to_string())


def pd_sample(frame):
    return model.predict_proba(woe_frame(frame, bins, features))[:, 1]


def gini(y, p):
    return 2 * roc_auc_score(y, p) - 1


def ks(y, p):
    order = np.argsort(p)
    y = np.asarray(y)[order]
    return np.abs(np.cumsum(y) / y.sum() - np.cumsum(1 - y) / (1 - y).sum()).max()


rng = np.random.default_rng(SEED)
p_test, y_test = pd_sample(test), test.bad.to_numpy()
boot = [gini(y_test[i], p_test[i]) for i in (rng.integers(0, len(test), len(test)) for _ in range(2000))]
print(f"train Gini {gini(train.bad, pd_sample(train)):.3f}, KS {ks(train.bad, pd_sample(train)):.3f}")
print(f"test  Gini {gini(y_test, p_test):.3f}, KS {ks(y_test, p_test):.3f}")
print(f"test Gini 95% bootstrap interval {np.quantile(boot, .025):.3f} to {np.quantile(boot, .975):.3f}")

# %% benchmark
rows = {"WoE logistic": [], "Raw codes logistic": [], "Gradient boosting": []}
X_raw = raw[candidates]
for fit_i, val_i in RepeatedStratifiedKFold(n_splits=5, n_repeats=4, random_state=SEED).split(X_raw, raw.bad):
    a, b = raw.iloc[fit_i], raw.iloc[val_i]
    fold = {c: fit_bins(a[c], a.bad) for c in candidates}
    keep = [c for c in candidates if fold[c]["iv"] >= .02]
    m = LogisticRegression(C=1e6, max_iter=1000).fit(woe_frame(a, fold, keep), a.bad)
    rows["WoE logistic"].append(gini(b.bad, m.predict_proba(woe_frame(b, fold, keep))[:, 1]))
    m = LogisticRegression(C=1e6, max_iter=5000).fit(a[candidates], a.bad)
    rows["Raw codes logistic"].append(gini(b.bad, m.predict_proba(b[candidates])[:, 1]))
    m = HistGradientBoostingClassifier(max_depth=3, learning_rate=.05, max_iter=150, random_state=SEED)
    m.fit(a[candidates], a.bad)
    rows["Gradient boosting"].append(gini(b.bad, m.predict_proba(b[candidates])[:, 1]))
print("Gini over 5-fold cross-validation, repeated 4 times: mean and sd of the 20 folds")
for name, values in rows.items():
    print(f"{name:20s} {np.mean(values):.3f}  {np.std(values):.3f}")

# %% prior
sample_bad, true_bad = raw.bad.mean(), .05
shift = np.log(true_bad / (1 - true_bad)) - np.log(sample_bad / (1 - sample_bad))


def pd_true(frame):
    """Move the log odds by a constant: ranking and Gini do not change, the PD does."""
    logit = np.log(pd_sample(frame) / (1 - pd_sample(frame))) + shift
    return 1 / (1 + np.exp(-logit))


p_true = pd_true(test)
# Population weights undo the stratified sample: each good stands for more goods than each bad does.
w_test = np.where(y_test == 1, true_bad / sample_bad, (1 - true_bad) / (1 - sample_bad))
print(f"log-odds shift {shift:.3f}")
print(f"mean PD before correction {p_test.mean():.3f}, after correction, population weighted {np.average(p_true, weights=w_test):.3f}")
print(f"Gini after correction {gini(y_test, p_true):.3f}")

# %% scorecard
PDO, BASE_SCORE, BASE_ODDS = 20, 600, 30
factor = PDO / np.log(2)
offset = BASE_SCORE - factor * np.log(BASE_ODDS)


def score(frame):
    return offset + factor * np.log((1 - pd_true(frame)) / pd_true(frame))


n = len(features)
alpha = model.intercept_[0] + shift
print(f"factor {factor:.2f}, offset {offset:.2f}; score = {offset:.0f} + {factor:.1f} ln(good:bad odds)")
for char in ["status", "duration"]:
    t = bins[char]["table"]
    points = -(coef[char] * t.woe + alpha / n) * factor + offset / n
    print(char, {str(k): v for k, v in points.round(0).astype(int).items()})
sample = test.iloc[[0]]
print(f"first test applicant: PD {pd_true(sample)[0]:.3f}, score {score(sample)[0]:.0f}")

# %% chart_ks
s_test = score(test)
grid = np.sort(s_test)
cdf_bad = np.array([(s_test[y_test == 1] <= v).mean() for v in grid])
cdf_good = np.array([(s_test[y_test == 0] <= v).mean() for v in grid])
gap = np.abs(cdf_bad - cdf_good).argmax()
fig, ax = plt.subplots()
ax.plot(grid, cdf_bad, color=cs.ORANGE, label="Bad credits")
ax.plot(grid, cdf_good, color=cs.BLUE, label="Good credits")
ax.vlines(grid[gap], cdf_good[gap], cdf_bad[gap], color=cs.INK, lw=1)
ax.text(grid[gap] + 3, (cdf_good[gap] + cdf_bad[gap]) / 2, f"KS = {cdf_bad[gap] - cdf_good[gap]:.2f}", color=cs.INK)
ax.set_xlabel("Score (higher is safer)")
ax.set_ylabel("Share at or below this score")
ax.set_title("KS is the widest gap between the two score distributions")
ax.legend(loc="upper left")
cs.save(fig, "applied-credit-ks.png")

# %% cutoff
COST_BAD_ACCEPTED, COST_GOOD_REJECTED = 5, 1
print(f"Bayes cutoff on a calibrated PD: reject above {COST_GOOD_REJECTED / (COST_BAD_ACCEPTED + COST_GOOD_REJECTED):.3f}")


def expected_cost(threshold, pd_used):
    accept = pd_used <= threshold
    per_app = (w_test * ((accept & (y_test == 1)) * COST_BAD_ACCEPTED + (~accept & (y_test == 0)) * COST_GOOD_REJECTED)).sum() / w_test.sum()
    return per_app, np.average(accept, weights=w_test)


cuts = {"Approve everyone": (1.0, p_true), "Sample PD, cutoff 1/6 (prior ignored)": (1 / 6, p_test),
        "True-prior PD, cutoff 1/6": (1 / 6, p_true), "Reject everyone": (-1.0, p_true)}
for name, (th, used) in cuts.items():
    cost, approve = expected_cost(th, used)
    print(f"{name:38s} approve {approve:6.1%}  cost per application {cost:.3f}")

grid_pd = np.quantile(p_true, np.linspace(0, 1, 201))
curve = pd.DataFrame([expected_cost(th, p_true) for th in grid_pd], columns=["cost", "approve"])
best = curve.cost.idxmin()
print(f"lowest test cost {curve.cost[best]:.3f} at PD cutoff {grid_pd[best]:.3f}, approving {curve.approve[best]:.1%}")

# %% chart_cost
fig, ax = plt.subplots()
ax.plot(curve.approve * 100, curve.cost, color=cs.BLUE)
c, a = expected_cost(1 / 6, p_true)
ax.scatter([a * 100], [c], s=60, color=cs.ORANGE, zorder=3, edgecolor=cs.SURFACE, linewidth=2, label="True-prior PD, cutoff 1/6")
c2, a2 = expected_cost(1 / 6, p_test)
ax.scatter([a2 * 100], [c2], s=60, color=cs.AQUA, zorder=3, edgecolor=cs.SURFACE, linewidth=2, label="Sample PD, cutoff 1/6 (prior ignored)")
ax.set_ylim(0)
ax.set_xlabel("Share of population approved (%)")
ax.set_ylabel("Expected cost per application")
ax.set_title("Ignoring the 5% prior rejects good customers at a high price")
ax.legend(loc="upper right")
cs.save(fig, "applied-credit-cost-curve.png")

# %% capital
def irb_other_retail(pd_, lgd):
    """IRB capital requirement K per unit of exposure, other retail (BCBS 2005 explanatory note)."""
    pd_ = max(pd_, .0005)                                 # CRE32 retail PD floor
    share = (1 - np.exp(-35 * pd_)) / (1 - np.exp(-35))
    r = .03 * share + .16 * (1 - share)
    conditional = norm.cdf((norm.ppf(pd_) + np.sqrt(r) * norm.ppf(.999)) / np.sqrt(1 - r))
    return lgd * conditional - pd_ * lgd


EAD, LGD = 5000, .60                                      # assumed: a 5,000 unsecured loan, 60% loss given default
print(f"{'PD':>6} {'EL':>7} {'K':>7} {'capital':>8} {'RWA':>8}")
for p in (.005, .01, .03, .10):
    k = irb_other_retail(p, LGD)
    print(f"{p:6.1%} {p * LGD * EAD:7.0f} {k:7.2%} {k * EAD:8.0f} {k * 12.5 * EAD:8.0f}")

# %% psi
def psi(expected, actual, n_bins=10):
    edges = np.unique(np.quantile(expected, np.linspace(0, 1, n_bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    e = np.histogram(expected, edges)[0] / len(expected) + 1e-4
    a = np.histogram(actual, edges)[0] / len(actual) + 1e-4
    return ((a - e) * np.log(a / e)).sum()


s_train = score(train)
print(f"PSI train vs test {psi(s_train, s_test):.3f}")
drift = test.assign(status=test.status.replace({4: 1}))     # what if the safest status class vanished
print(f"PSI train vs test with top status class recoded as no account {psi(s_train, score(drift)):.3f}")
