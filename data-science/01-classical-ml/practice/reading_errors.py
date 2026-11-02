# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scipy", "scikit-learn", "imbalanced-learn", "xlrd", "matplotlib", "shap"]
# ///
"""Experiments for notes/12-reading-the-errors.md: read a credit model's errors, then learn from them
without fitting to them.

Run from this folder:
    uv run reading_errors.py

Uses the natural 22.1% default rate, not the 3% subset of note 10: at 3% the test set holds too few
defaulters to slice. Writes one figure to ../../sources/images/.
"""
# %% Setup: train, eyeball, blackbox and test
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "credit-default-lab"))
import numpy as np
import pandas as pd
import credit_default_lab as lab
from scipy import stats
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score, train_test_split

pd.set_option("display.width", 150, "display.max_columns", None, "display.max_rows", 200)
T = lab.TARGET
PARAMS = {"max_leaf_nodes": 4, "max_iter": 300}
SEED = 0


def carve(raw, seed):
    """The test set stays fixed. Everything else is re-dealt: 18,000 train, 1,500 eyeball, 4,500 blackbox."""
    _, _, test = lab.split(raw, seed=0)
    rest = raw.drop(test.index)
    train, dev = train_test_split(rest, train_size=18_000, stratify=rest[T], random_state=seed)
    eyeball, blackbox = train_test_split(dev, train_size=1_500, stratify=dev[T], random_state=seed)
    return train, eyeball, blackbox, test


def fit(train, seed=SEED, feats=lab.features):
    return lab.make_pipeline(None, "boosted", PARAMS, False, seed=seed).fit(feats(train), train[T])


def describe(raw):
    """Readable, unscaled columns for reading rows and cutting slices. None of these are new model inputs."""
    d = pd.DataFrame(index=raw.index)
    d["limit"] = raw["LIMIT_BAL"]
    d["bill"] = raw["BILL_AMT1"]
    d["paid"] = raw["PAY_AMT1"]
    d["status"] = raw["PAY_0"]
    d["months_late"] = (raw[lab.PAY] > 0).sum(axis=1)
    d["util"] = raw["BILL_AMT1"] / raw["LIMIT_BAL"]
    d["paid_share"] = (raw["PAY_AMT1"] / raw["BILL_AMT2"].clip(lower=1)).clip(upper=2)
    d["age"] = raw["AGE"]
    d["sex"] = raw["SEX"].map({1: "male", 2: "female"})
    d["marriage"] = raw["MARRIAGE"].map({1: "married", 2: "single"}).fillna("other")
    d["education"] = raw["EDUCATION"].map({1: "graduate", 2: "university", 3: "high school"}).fillna("other")
    d["age_band"] = pd.cut(raw["AGE"], [0, 29, 39, 49, 200], labels=["under 30", "30-39", "40-49", "50+"]).astype(str)
    return d


def cells(y, p, t):
    return np.select([(y == 1) & (p >= t), (y == 0) & (p >= t), (y == 1) & (p < t)], ["TP", "FP", "FN"], "TN")


raw = lab.load_credit()
train, eyeball, blackbox, test = carve(raw, SEED)
print(f"rows: train {len(train)}, eyeball {len(eyeball)}, blackbox {len(blackbox)}, test {len(test)}; "
      f"default rate {raw[T].mean():.3f}; defaulters in eyeball {eyeball[T].sum()}, in test {test[T].sum()}")
model = fit(train)
peye = model.predict_proba(lab.features(eyeball))[:, 1]
yeye = eyeball[T].to_numpy()

# %% Step 1: name the errors, at the decision threshold
print("\n--- step 1: positive class = will default, predicted positive = declined (eyeball) ---")
for t in (0.5, lab.BAYES):
    tn, fp, fn, tp = confusion_matrix(yeye, peye >= t).ravel()
    print(f"threshold {t:.3f}: TP {tp:4d}  FP {fp:4d}  FN {fn:4d}  TN {tn:4d}   declined {(peye >= t).mean():.3f}  "
          f"cost per 1,000 {lab.expected_cost(yeye, peye, t):.1f}")
print(f"approve everyone: cost per 1,000 {lab.expected_cost(yeye, np.zeros(len(yeye)), 0.5):.1f}")

# %% Step 2: profile the four cells
d = describe(eyeball)
d["cell"] = cells(yeye, peye, lab.BAYES)
d["score"] = peye
print("\n--- step 2: the four cells, median of each column (months_late and score are means; eyeball) ---")
prof = d.groupby("cell")[["limit", "bill", "paid", "status", "util", "paid_share", "age"]].median()
prof.insert(0, "n", d.groupby("cell").size())
prof["months_late"] = d.groupby("cell").months_late.mean()
prof["score"] = d.groupby("cell").score.mean()
print(prof.loc[["TP", "FN", "FP", "TN"]].round(2))


def std_diff(a, b, cols):
    """Difference in means in pooled standard deviations, on log-scaled money so one bill can't dominate."""
    rows = {}
    for c in cols:
        x, y = a[c], b[c]
        if c in ("limit", "bill", "paid"):
            x, y = np.sign(x) * np.log1p(np.abs(x)), np.sign(y) * np.log1p(np.abs(y))
        rows[c] = (x.mean() - y.mean()) / np.sqrt((x.var() + y.var()) / 2)
    return rows


cols = ["limit", "bill", "paid", "status", "months_late", "util", "paid_share", "age"]
g = {c: d[d.cell == c] for c in ("TP", "FP", "FN", "TN")}
print("\nstandardised differences (0.2 small, 0.8 large)")
print(pd.DataFrame({"FN vs TP": std_diff(g["FN"], g["TP"], cols), "FN vs TN": std_diff(g["FN"], g["TN"], cols),
                    "FP vs TN": std_diff(g["FP"], g["TN"], cols), "FP vs TP": std_diff(g["FP"], g["TP"], cols)}).round(2))

print("\nthe approved and the declined: mean predicted risk against what happened (eyeball)")
for name, mask in {"approved": peye < lab.BAYES, "declined": peye >= lab.BAYES}.items():
    print(f"{name:9s} n {mask.sum():4d}  mean score {peye[mask].mean():.3f}  default rate {yeye[mask].mean():.3f}")

# can anything in the features tell a missed defaulter from a correctly approved customer?
xa = lab.features(eyeball[peye < lab.BAYES])
ya = yeye[peye < lab.BAYES]
sep = cross_val_score(lab.make_pipeline(None, "logistic", {"C": 1.0}, False, seed=SEED), xa, ya, cv=5, scoring="roc_auc")
print(f"FN against TN among the approved, a fresh logistic on the same inputs, 5-fold ROC-AUC {sep.mean():.3f}")

# %% Step 3: read rows. Random first, then the most confident mistakes.
show = ["limit", "bill", "paid", "status", "months_late", "util", "age", "education", "score"]
rng = np.random.default_rng(SEED)
for cell, what in [("FN", "defaulter approved"), ("FP", "good customer declined")]:
    part = d[d.cell == cell]
    print(f"\n--- step 3: five random {cell} ({what}) ---")
    print(part.iloc[rng.choice(len(part), 5, replace=False)][show].round(2).to_string())
    worst = part.sort_values("score", ascending=cell == "FN").head(5)
    print(f"five most confident {cell}")
    print(worst[show].round(2).to_string())

no_bills = (eyeball[lab.BILL].abs().sum(axis=1) == 0) & (eyeball[lab.PAID].sum(axis=1) == 0)
print(f"\nno bill and no payment in six months: {no_bills.sum()} rows, {eyeball.loc[no_bills, T].sum()} labelled default "
      f"({eyeball.loc[no_bills, T].mean():.3f}); of those defaults, {(d.cell[no_bills] == 'FN').sum()} are FN")
print(f"share of all FN: {(d.cell[no_bills] == 'FN').sum() / (d.cell == 'FN').sum():.3f}")

# %% Step 3b: a local explanation of two chosen errors
import shap

clf, scale = model.named_steps["clf"], model.named_steps["scale"]
explainer = shap.TreeExplainer(clf)
fn_row, fp_row = g["FN"].score.idxmin(), g["FP"].score.idxmax()
for name, idx in {"most confident FN": fn_row, "most confident FP": fp_row}.items():
    x = lab.features(eyeball.loc[[idx]])
    v = explainer.shap_values(scale.transform(x))[0]
    top = pd.Series(v, index=lab.FEATURES).sort_values(key=np.abs, ascending=False).head(4)
    parts = ", ".join(f"{k}={raw.loc[idx, k]:.0f} ({w:+.2f})" for k, w in top.items())
    print(f"{name}: score {d.score[idx]:.3f}, log-odds pushes: {parts}")


# %% Step 4: slice and count, with Wilson intervals and each slice's share of all errors
def wilson(x, n, z=1.96):
    """As in DA 02/04."""
    if n == 0:
        return (np.nan, np.nan)
    p = x / n
    c = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return c - h, c + h


def bh(pvalues, q=0.05):
    """Benjamini-Hochberg, as in DA 02/05: which p-values survive at false discovery rate q."""
    p = np.asarray(pvalues)
    order = np.argsort(p)
    passed = p[order] <= q * np.arange(1, len(p) + 1) / len(p)
    keep = np.zeros(len(p), bool)
    if passed.any():
        keep[order[: np.flatnonzero(passed).max() + 1]] = True
    return keep


def row_cost(y, p, t=lab.BAYES):
    return lab.COST_FN * ((y == 1) & (p < t)) + lab.COST_FP * ((y == 0) & (p >= t))


def scan(frame, y, p, slices):
    """One row per slice: error rates with intervals, share of errors, and a test of cost against the rest."""
    c = row_cost(y, p)
    wrong = c > 0
    rows = []
    for name, mask in slices.items():
        mask = np.asarray(mask)
        fp, good = ((y == 0) & (p >= lab.BAYES))[mask].sum(), (y == 0)[mask].sum()
        fn, bad = ((y == 1) & (p < lab.BAYES))[mask].sum(), (y == 1)[mask].sum()
        rows.append({
            "slice": name, "n": mask.sum(), "default": y[mask].mean(),
            "FPR": fp / max(good, 1), "FPR lo": wilson(fp, good)[0], "FPR hi": wilson(fp, good)[1],
            "FNR": fn / max(bad, 1), "FNR lo": wilson(fn, bad)[0], "FNR hi": wilson(fn, bad)[1],
            "cost/1000": 1000 * c[mask].mean(), "share of rows": mask.mean(),
            "share of cost": c[mask].sum() / c.sum(),
            "p": stats.ttest_ind(c[mask], c[~mask], equal_var=False).pvalue,
        })
    out = pd.DataFrame(rows).set_index("slice")
    out["BH"] = bh(out.p)
    return out


def real_slices(frame):
    s = {}
    for col in ("sex", "marriage", "age_band", "education"):
        for v in sorted(frame[col].unique()):
            s[f"{col}: {v}"] = frame[col] == v
    for a, b, name in [(0, 50_000, "under 50k"), (50_000, 140_000, "50k-140k"), (140_000, 240_000, "140k-240k"),
                       (240_000, 10**9, "240k+")]:
        s[f"limit: {name}"] = (frame.limit > a) & (frame.limit <= b)
    s["status: paid or none (<=0)"] = frame.status <= 0
    s["status: 1 month late"] = frame.status == 1
    s["status: 2+ months late"] = frame.status >= 2
    s["bill: near limit (util>=0.8)"] = frame.util >= 0.8
    return s


sl = scan(d, yeye, peye, real_slices(d))
print("\n--- step 4: slices of the eyeball set ---")
print(sl.drop(columns=["FPR lo", "FPR hi", "FNR lo", "FNR hi"]).round(3).to_string())
print("\nintervals for the largest gaps")
print(sl.loc[["sex: male", "sex: female", "age_band: under 30", "age_band: 50+", "status: 2+ months late"],
             ["n", "FPR", "FPR lo", "FPR hi", "FNR", "FNR lo", "FNR hi"]].round(3).to_string())

# %% Chouldechova's identity on a slice the model never sees (blackbox, so a larger count)
pbb = model.predict_proba(lab.features(blackbox))[:, 1]
ybb = blackbox[T].to_numpy()
dbb = describe(blackbox)
print("\n--- sex, a column the model does not use (blackbox) ---")
for v in ("male", "female"):
    m = (dbb.sex == v).to_numpy()
    tn, fp, fn, tp = confusion_matrix(ybb[m], pbb[m] >= lab.BAYES).ravel()
    prev, ppv, fnr, fpr = (tp + fn) / m.sum(), tp / (tp + fp), fn / (fn + tp), fp / (fp + tn)
    implied = prev / (1 - prev) * (1 - ppv) / ppv * (1 - fnr)
    print(f"{v:7s} n {m.sum():4d}  prevalence {prev:.3f}  PPV {ppv:.3f}  FPR {fpr:.3f}  FNR {fnr:.3f}  "
          f"FPR from the identity {implied:.3f}")

# %% Step 5: the threshold, one of the diagnoses
print("\n--- step 5: moving the threshold on the eyeball set ---")
for t in (0.1, 0.13, lab.BAYES, 0.2, 0.25, 0.3, 0.4, 0.5):
    tn, fp, fn, tp = confusion_matrix(yeye, peye >= t).ravel()
    print(f"t {t:.3f}  FP {fp:4d}  FN {fn:4d}  cost/1000 {lab.expected_cost(yeye, peye, t):6.1f}")
