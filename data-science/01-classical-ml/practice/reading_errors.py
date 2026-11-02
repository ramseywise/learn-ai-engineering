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
    lo, hi = wilson(fp, fp + tn), wilson(fn, fn + tp)
    print(f"        95% Wilson: FPR {lo[0]:.3f} to {lo[1]:.3f}, FNR {hi[0]:.3f} to {hi[1]:.3f}")

# %% Step 5: the threshold, one of the diagnoses
print("\n--- step 5: moving the threshold on the eyeball set ---")
for t in (0.1, 0.13, lab.BAYES, 0.2, 0.25, 0.3, 0.4, 0.5):
    tn, fp, fn, tp = confusion_matrix(yeye, peye >= t).ravel()
    print(f"t {t:.3f}  FP {fp:4d}  FN {fn:4d}  cost/1000 {lab.expected_cost(yeye, peye, t):6.1f}")

# how much of the FN against TN separation is just the model's own score?
from sklearn.metrics import roc_auc_score

print(f"\nthe model's own score, FN against TN among the approved, ROC-AUC {roc_auc_score(ya, peye[peye < lab.BAYES]):.3f}")

for t in (0.13, lab.BAYES):
    print(f"blackbox cost/1000 at t {t:.3f}: {lab.expected_cost(ybb, pbb, t):.1f}")

# %% Step 6: confirm the eyeball's slices on data nobody read
sbb = scan(dbb, ybb, pbb, real_slices(dbb))
print("\n--- step 6: the same slices on the blackbox set (4,500 rows, not read) ---")
pick = ["limit: under 50k", "limit: 240k+", "status: 2+ months late", "status: paid or none (<=0)",
        "education: high school", "bill: near limit (util>=0.8)"]
both = pd.concat({"eyeball": sl.loc[pick, ["cost/1000", "p", "BH"]], "blackbox": sbb.loc[pick, ["cost/1000", "p", "BH"]]}, axis=1)
print(both.round(3).to_string())
print("calibration inside slices on the blackbox set: mean score against default rate")
for k in ("limit: under 50k", "limit: 240k+", "status: 2+ months late", "status: paid or none (<=0)"):
    m = np.asarray(real_slices(dbb)[k])
    print(f"  {k:28s} score {pbb[m].mean():.3f}  default {ybb[m].mean():.3f}")
print(f"slices surviving BH: eyeball {sl.BH.sum()} of {len(sl)}, blackbox {sbb.BH.sum()} of {len(sbb)}")
print(f"blackbox cost overall {1000 * row_cost(ybb, pbb).mean():.1f}; approve everyone "
      f"{lab.expected_cost(ybb, np.zeros(len(ybb)), 0.5):.1f}")


# %% The hypothesis from reading, written down before any scoring of a fix
# Mechanism: the model sees money in absolute amounts. Reading the eyeball rows, declined good customers
# include people with tiny bills who paid little (ids 1126, 28810, 10531), and approved defaulters include
# people at status 0 with a bill near their limit (ids 16325, 27689, 18340). Risk should depend on the amount
# relative to the limit and to what was due, and shallow trees on separate logged amounts build ratios badly.
# Fix: add utilisation (BILL_AMTk / LIMIT_BAL, six months) and payment share (PAY_AMTk / BILL_AMT(k+1), five
# months, capped at 2). All of these are dated September or earlier, before the October outcome.
def features_plus(raw):
    x = lab.features(raw)
    for k in range(1, 7):
        x[f"util_{k}"] = raw[f"BILL_AMT{k}"] / raw["LIMIT_BAL"]
    for k in range(1, 6):
        x[f"paid_share_{k}"] = (raw[f"PAY_AMT{k}"] / raw[f"BILL_AMT{k + 1}"].clip(lower=1)).clip(upper=2)
    return x


def noise_slices(n, rng, columns=10):
    """Ten pure-noise columns cut into five equal slices each: fifty slices, none of which means anything."""
    cuts = stats.norm.ppf([0.2, 0.4, 0.6, 0.8])
    out = {}
    for c in range(columns):
        q = np.digitize(rng.normal(size=n), cuts)
        for b in range(5):
            out[f"noise_{c} q{b + 1}"] = q == b
    return out


def per_1000(c):
    return 1000 * c.mean()


def costs(y, p, t):
    return lab.COST_FN * ((y == 1) & (p < t)) + lab.COST_FP * ((y == 0) & (p >= t))


# %% The demonstration. Seeds 0-29, fixed before the first run and reported whatever they give.
SEEDS = range(30)


def one_seed(seed):
    tr, eye, bb, _ = carve(raw, seed)
    base = fit(tr, seed)
    plus = fit(tr, seed, features_plus)
    ye, yb = eye[T].to_numpy(), bb[T].to_numpy()
    pe, pb = base.predict_proba(lab.features(eye))[:, 1], base.predict_proba(lab.features(bb))[:, 1]
    # new noise each seed, for eyeball and blackbox rows alike
    rng = np.random.default_rng(1000 + seed)
    n_all = len(eye) + len(bb)
    slices = noise_slices(n_all, rng)
    se = {k: v[: len(eye)] for k, v in slices.items()}
    sb = {k: v[len(eye):] for k, v in slices.items()}
    res = scan(None, ye, pe, se)
    worst = res["cost/1000"].idxmax()
    t = lab.tune_threshold(ye[se[worst]], pe[se[worst]])
    te = np.where(se[worst], t, lab.BAYES)
    tb = np.where(sb[worst], t, lab.BAYES)
    base_e, base_b = per_1000(costs(ye, pe, lab.BAYES)), per_1000(costs(yb, pb, lab.BAYES))
    qe = plus.predict_proba(features_plus(eye))[:, 1]
    qb = plus.predict_proba(features_plus(bb))[:, 1]
    # the worst slice's own cost, read on eyeball and then on blackbox
    return {
        "seed": seed, "worst": worst, "worst cost eye": res.loc[worst, "cost/1000"],
        "worst cost bb": 1000 * costs(yb, pb, lab.BAYES)[sb[worst]].mean(), "base eye": base_e, "base bb": base_b,
        "raw p<.05": (res.p < 0.05).sum(), "BH": res.BH.sum(), "worst p": res.loc[worst, "p"], "patch t": t,
        "noise eye": base_e - per_1000(costs(ye, pe, te)), "noise bb": base_b - per_1000(costs(yb, pb, tb)),
        "real eye": base_e - per_1000(costs(ye, qe, lab.BAYES)), "real bb": base_b - per_1000(costs(yb, qb, lab.BAYES)),
    }


demo = pd.DataFrame([one_seed(s) for s in SEEDS])
print(f"\n--- the demonstration: seeds 0-{len(SEEDS) - 1}, {len(SEEDS)} runs, each a new split and new noise ---")
print("seed 0:")
print(demo.loc[0, ["worst", "worst cost eye", "worst cost bb", "worst p", "raw p<.05", "BH", "patch t",
                   "noise eye", "noise bb", "real eye", "real bb"]].to_string())
print(f"\nover {len(SEEDS)} seeds: base cost eyeball {demo['base eye'].mean():.1f}, blackbox {demo['base bb'].mean():.1f}")
print(f"worst noise slice cost: on eyeball {demo['worst cost eye'].mean():.1f}, the same slice on blackbox {demo['worst cost bb'].mean():.1f}")
print(f"noise slices with raw p<.05, mean of 50: {demo['raw p<.05'].mean():.1f}; seeds with any BH survivor: {(demo.BH > 0).sum()}")
print("gain in cost per 1,000 applicants, positive is better")
g = demo[["noise eye", "noise bb", "real eye", "real bb"]]
print(pd.DataFrame({"mean": g.mean(), "sd": g.std(), "min": g.min(), "max": g.max(), "seeds > 0": (g > 0).sum(),
                    "seeds < 0": (g < 0).sum()}).round(2).to_string())


# %% Count the rounds: keep every noise patch that helps half the blackbox, score on the other half
def rounds_seed(seed, rounds=20):
    tr, _, bb, _ = carve(raw, seed)
    base = fit(tr, seed)
    y, p = bb[T].to_numpy(), base.predict_proba(lab.features(bb))[:, 1]
    rng = np.random.default_rng(2000 + seed)
    a = rng.permutation(len(y)) < len(y) // 2  # half A is reused every round, half B is only scored
    slices = list(noise_slices(len(y), rng).values())
    t = np.full(len(y), lab.BAYES)
    start_a, start_b = per_1000(costs(y[a], p[a], t[a])), per_1000(costs(y[~a], p[~a], t[~a]))
    out = []
    for r in range(1, rounds + 1):
        mask = slices[rng.integers(len(slices))]
        trial = t + mask * rng.uniform(-0.05, 0.05)
        if per_1000(costs(y[a], p[a], trial[a])) < per_1000(costs(y[a], p[a], t[a])):
            t = trial
        out.append({"seed": seed, "round": r, "reused half": start_a - per_1000(costs(y[a], p[a], t[a])),
                    "fresh half": start_b - per_1000(costs(y[~a], p[~a], t[~a]))})
    return out


rr = pd.DataFrame([x for s in SEEDS for x in rounds_seed(s)])
print(f"\n--- reusing a holdout: noise patches kept if they help half A, 20 rounds, {len(SEEDS)} seeds ---")
print("gain in cost per 1,000, mean over seeds")
print(rr[rr["round"].isin([1, 5, 10, 20])].groupby("round")[["reused half", "fresh half"]].mean().round(2).to_string())

# %% The test set, once: the baseline and the mechanism fix, chosen before any of this ran
tr, eye, bb, te = carve(raw, SEED)
yte = te[T].to_numpy()
base = fit(tr, SEED)
pte = base.predict_proba(lab.features(te))[:, 1]
qte = fit(tr, SEED, features_plus).predict_proba(features_plus(te))[:, 1]
cb, cr = costs(yte, pte, lab.BAYES), costs(yte, qte, lab.BAYES)
rng = np.random.default_rng(SEED)
boots = [(lambda i: 1000 * (cb[i].mean() - cr[i].mean()))(rng.integers(len(yte), size=len(yte))) for _ in range(2000)]
print("\n--- the test set, used once (seed 0, 6,000 rows, a noise slice can't transfer so it isn't scored) ---")
print(f"baseline {1000 * cb.mean():.1f}  real-mechanism fix {1000 * cr.mean():.1f}  "
      f"gain {1000 * (cb.mean() - cr.mean()):.1f} (bootstrap 95% {np.quantile(boots, 0.025):.1f} to {np.quantile(boots, 0.975):.1f})  "
      f"approve everyone {lab.expected_cost(yte, np.zeros(len(yte)), 0.5):.1f}")

# %% Figure: what looked like a gain on the eyeball set, and what remained on the blackbox set
plt = lab._style()
fig, ax = plt.subplots(figsize=(7.2, 3.4))
jit = np.random.default_rng(0)
rows = [("Noise fix", "noise eye", "noise bb"), ("Real-mechanism fix", "real eye", "real bb")]
for i, (name, a, b) in enumerate(rows):
    for col, off, colour, label in [(a, 0.17, lab.BLUE, "Eyeball set (read)"), (b, -0.17, lab.ORANGE, "Blackbox set (not read)")]:
        y = 1 - i + off + jit.uniform(-0.07, 0.07, len(demo))
        ax.plot(demo[col], y, "o", ms=5, color=colour, alpha=0.6, mec="none", label=label if i == 0 else None)
        ax.plot([demo[col].mean()] * 2, [1 - i + off - 0.13, 1 - i + off + 0.13], color=lab.INK, lw=2)
ax.axvline(0, color=lab.MUTED, lw=1)
ax.set_yticks([1, 0], [r[0] for r in rows])
ax.set_ylim(-0.5, 1.5)
ax.grid(axis="y", visible=False)
ax.set_xlabel("Fall in cost per 1,000 applicants; dots are seeds, black bars their means")
ax.set_title(f"What each fix gained, read and unread ({len(SEEDS)} seeds)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
print("\nwrote", lab._save(fig, "reading-errors-noise-fix.png").name)
