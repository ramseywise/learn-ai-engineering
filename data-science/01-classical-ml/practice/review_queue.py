# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scipy", "scikit-learn", "imbalanced-learn", "xlrd", "matplotlib"]
# ///
"""Experiments for notes/13-automate-review-or-reject.md: two thresholds, their prices and their limits.

Run from this folder:
    uv run review_queue.py

Invoices are generated (see invoices.py), so the truth is known and every price is an assumption. The same
policy is repeated on the real credit file at the end. Writes two figures to ../../sources/images/.
"""
# %% Setup: fresh train, validation and test invoices for each seed
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "credit-default-lab"))
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd
from dataclasses import replace
from scipy import stats
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score

import credit_default_lab as lab
import invoices as inv
from invoices import FEATURES, PAY, REJECT, REVIEW, Prices

pd.set_option("display.width", 170, "display.max_columns", None, "display.max_rows", 200)
pd.options.display.float_format = "{:.3f}".format
C = Prices()
SEEDS = range(20)


def world(seed, n_train=30_000, n_val=10_000, n_test=50_000, **test_kwargs):
    base = 1000 * (seed + 1)
    return (inv.make_invoices(n_train, base), inv.make_invoices(n_val, base + 1),
            inv.make_invoices(n_test, base + 2, **test_kwargs))


def fitted(seed, **kw):
    """Model, Platt map fitted on validation, and calibrated scores for validation and test."""
    tr, va, te = world(seed, **kw)
    m = inv.fit_boosted(tr[FEATURES], tr.y, seed)
    raw_va, raw_te = inv.score(m, va[FEATURES]), inv.score(m, te[FEATURES])
    cal = inv.platt(raw_va, va.y)
    return m, cal, va, te, cal(raw_va), cal(raw_te)


def expected_costs(p, c=C, pay_problem=None):
    """Expected euros per invoice of each route, given a probability. Columns: pay, review, reject."""
    a = c.pay_problem if pay_problem is None else pay_problem
    pay = a * p
    review = c.review + p * (1 - c.catch) * a + (1 - p) * c.false_alarm * c.reject_good
    reject = c.reject_good * (1 - p)
    return np.column_stack([pay, review, reject])


def search_thresholds(y, p, c=C):
    """Pick the pair with the lowest cost on a labelled set, by brute force."""
    los, his = np.geomspace(0.002, 0.5, 40), np.linspace(0.1, 0.99, 30)
    best = (np.inf, 0.0, 1.0)
    for lo in los:
        for hi in his[his > lo]:
            cost = inv.unit_cost(y, inv.route(p, lo, hi), c).mean()
            if cost < best[0]:
                best = (cost, lo, hi)
    return best[1], best[2]


LO, HI = inv.thresholds(C)
ONE = inv.one_threshold(C)
print(f"Prices: paying a problem {C.pay_problem:.0f}, rejecting a good invoice {C.reject_good:.0f}, review {C.review:.0f}, "
      f"catch {C.catch}, false alarm {C.false_alarm}")
print(f"Perfect clerk: pay below {C.review / C.pay_problem:.3f}, reject above {1 - C.review / C.reject_good:.3f}")
print(f"This clerk:    pay below {LO:.3f}, reject above {HI:.3f}. No review route: reject above {ONE:.3f}")
d = inv.make_invoices(200_000, 0)
print(f"Problem rate {d.y.mean():.3f}; oracle AUC {roc_auc_score(d.y, d.true_p):.3f}")

# %% Policies compared on the same invoices
PERFECT = (C.review / C.pay_problem, 1 - C.review / C.reject_good)
rows = []
for s in SEEDS:
    _, _, va, te, pv, pt = fitted(s)
    y = te.y.to_numpy()
    slo, shi = search_thresholds(va.y.to_numpy(), pv)
    policies = {
        "pay everything": (pt, inv.route(pt, 2.0, 3.0)),
        "review everything": (pt, inv.route(pt, -1.0, 2.0)),
        "one threshold": (pt, inv.route(pt, ONE, ONE)),
        "two, perfect clerk assumed": (pt, inv.route(pt, *PERFECT)),
        "two, priced": (pt, inv.route(pt, LO, HI)),
        "two, searched on validation": (pt, inv.route(pt, slo, shi)),
        "two, priced, true probability": (te.true_p.to_numpy(), inv.route(te.true_p.to_numpy(), LO, HI)),
    }
    for name, (q, r) in policies.items():
        rows.append({"policy": name, "seed": s, "lo": slo, "hi": shi, "auc": roc_auc_score(y, pt), **inv.report(y, q, r)})
policies = pd.DataFrame(rows)
order = list(dict.fromkeys(policies.policy))
cols = ["straight_through", "paid", "reviewed", "rejected", "error_paid", "precision_reject", "correction_rate", "cost"]
print(f"\nPolicies, mean of {len(SEEDS)} seeds on 50,000 test invoices; model AUC {policies.auc.mean():.3f}")
print(policies.groupby("policy")[cols].mean().loc[order].to_string())
wide = policies.pivot(index="seed", columns="policy", values="cost")
for a, b in [("one threshold", "two, priced"), ("two, perfect clerk assumed", "two, priced"), ("two, priced", "two, searched on validation")]:
    diff = wide[a] - wide[b]
    print(f"{a} minus {b}: {diff.mean():+.3f} euros per invoice (sd {diff.std():.3f}, {(diff > 0).sum()}/{len(diff)} seeds)")
print(f"Searched thresholds: lo {policies.lo.mean():.3f} (sd {policies.lo.std():.3f}), hi {policies.hi.mean():.3f} (sd {policies.hi.std():.3f})")

# %% Sensitivity: when does the review route stop paying?
_, _, va, te, pv, pt = fitted(0)
y = te.y.to_numpy()
base = inv.unit_cost(y, inv.route(pt, ONE, ONE)).mean()
rows = []
for review in (1, 3, 10, 20):
    for catch in (0.6, 0.75, 0.9, 0.99):
        c = replace(C, review=review, catch=catch)
        lo, hi = inv.thresholds(c)
        if lo >= hi:
            rows.append({"review": review, "catch": catch, "lo": lo, "hi": hi, "reviewed": 0.0, "saving": 0.0})
            continue
        cost1 = inv.unit_cost(y, inv.route(pt, ONE, ONE), c).mean()
        rows.append({"review": review, "catch": catch, "lo": lo, "hi": hi, "reviewed": (inv.route(pt, lo, hi) == REVIEW).mean(),
                     "saving": cost1 - inv.unit_cost(y, inv.route(pt, lo, hi), c).mean()})
sens = pd.DataFrame(rows)
print("\nReview price and catch rate (seed 0); saving in euros per invoice against one threshold")
print(sens.to_string(index=False))

# %% Capacity: only so many invoices can be reviewed. Which ones?
benefit = np.minimum(expected_costs(pt)[:, 0], expected_costs(pt)[:, 2]) - expected_costs(pt)[:, 1]
default = inv.route(pt, ONE, ONE)
rows = []
for share in (0.40, 0.20, 0.10, 0.05, 0.02):
    k = int(share * len(pt))
    for name, order_by in [("largest expected saving", -benefit), ("highest score", -pt)]:
        r = default.copy()
        picked = np.argsort(order_by)[:k]
        r[picked[benefit[picked] > 0] if name.startswith("largest") else picked] = REVIEW
        rows.append({"capacity": share, "rule": name, "cost": inv.unit_cost(y, r).mean(),
                     "lowest_p": pt[r == REVIEW].min(), "highest_p": pt[r == REVIEW].max()})
print("\nReview capacity, seed 0. Outside capacity the one-threshold rule decides")
print(pd.DataFrame(rows).to_string(index=False))
print(f"Share with a positive expected saving from review: {(benefit > 0).mean():.3f}")

# %% Costs that vary by invoice: paying a problem costs a share of its amount
amount = np.exp(te.log_amount.to_numpy())
a_i = amount * C.pay_problem / np.exp(6.3 + 1.1 ** 2 / 2)
flat = inv.route(pt, LO, HI)
per_invoice = expected_costs(pt, pay_problem=a_i).argmin(axis=1)
rows = []
for name, r in [("flat thresholds", flat), ("thresholds per invoice", per_invoice)]:
    rep = inv.report(y, pt, r)
    rows.append({"policy": name, "paid": rep["paid"], "reviewed": rep["reviewed"], "rejected": rep["rejected"], "error_paid": rep["error_paid"],
                 "money_lost_paid": (y * a_i * (r == PAY)).mean(), "cost": inv.unit_cost(y, r, pay_problem=a_i).mean()})
print(f"\nPaying a problem scales with amount, mean {a_i.mean():.0f}, median {np.median(a_i):.0f} (seed 0)")
print(pd.DataFrame(rows).to_string(index=False))

# %% Calibration: the formula assumes the score is a probability
rows = []
for s in range(10):
    tr, va, te = world(s)
    plain = inv.fit_boosted(tr[FEATURES], tr.y, s)
    weighted = inv.fit_boosted(tr[FEATURES], tr.y, s, class_weight="balanced")
    small = va.iloc[:2000]
    variants = {}
    for mname, m in [("plain", plain), ("class weights", weighted)]:
        rv, rs, rt = inv.score(m, va[FEATURES]), inv.score(m, small[FEATURES]), inv.score(m, te[FEATURES])
        variants[f"{mname}, raw"] = (rv, rt)
        variants[f"{mname}, Platt"] = (inv.platt(rv, va.y)(rv), inv.platt(rv, va.y)(rt))
        if mname == "class weights":
            variants[f"{mname}, Platt on 2,000"] = (inv.platt(rs, small.y)(rv), inv.platt(rs, small.y)(rt))
            iso = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(rs, small.y)
            variants[f"{mname}, isotonic on 2,000"] = (iso.predict(rv), iso.predict(rt))
    yt, yv = te.y.to_numpy(), va.y.to_numpy()
    for name, (qv, qt) in variants.items():
        band = (qt >= LO / 2) & (qt < LO * 2)
        slo, shi = search_thresholds(yv, qv)
        rep = inv.report(yt, qt, inv.route(qt, LO, HI))
        rows.append({"variant": name, "auc": roc_auc_score(yt, qt), "ece": lab.ece(yt, qt),
                     "predicted_near_lo": qt[band].mean() if band.any() else np.nan, "actual_near_lo": yt[band].mean() if band.any() else np.nan,
                     "paid": rep["paid"], "error_paid": rep["error_paid"], "cost_priced": rep["cost"],
                     "cost_searched": inv.unit_cost(yt, inv.route(qt, slo, shi)).mean()})
calib = pd.DataFrame(rows)
print("\nCalibration, mean of 10 seeds. 'near lo' is the scores within a factor of two of the pay threshold")
print(calib.groupby("variant", sort=False).mean(numeric_only=True).to_string())

# %% Drift: what moves, what stays still, and what a label-free dashboard can see
m, cal, va, te, pv, pt = fitted(0)


def prior_doubled(n, seed):
    """Keep what a problem looks like and double the odds of one: P(x | y) stays fixed."""
    pool = inv.make_invoices(n * 4, seed)
    rng = np.random.default_rng(seed)
    pos, neg = pool[pool.y == 1], pool[pool.y == 0]
    rate = pool.y.mean()
    target = 2 * rate / (1 + rate)
    k = int(n * target)
    return pd.concat([pos.sample(min(k, len(pos)), random_state=seed), neg.sample(n - min(k, len(pos)), random_state=seed)]).sample(frac=1, random_state=seed)


scenarios = {
    "no change": inv.make_invoices(50_000, 5001),
    "prior: twice the problems": prior_doubled(50_000, 5002),
    "covariate: newer suppliers, fewer POs": inv.make_invoices(50_000, 5003, tenure_mean=12.0, po_rate=0.6),
    "concept: new fraud type": inv.make_invoices(50_000, 5004, new_pattern=0.35),
}
reference = cal(inv.score(m, va[FEATURES]))
rows = []
for name, df in scenarios.items():
    q = cal(inv.score(m, df[FEATURES]))
    yy = df.y.to_numpy()
    rep = inv.report(yy, q, inv.route(q, LO, HI))
    fresh = df.iloc[:10_000]
    recal = inv.platt(inv.score(m, fresh[FEATURES]), fresh.y)
    q2 = recal(inv.score(m, df.iloc[10_000:][FEATURES]))
    y2 = df.iloc[10_000:].y.to_numpy()
    rep2 = inv.report(y2, q2, inv.route(q2, LO, HI))
    rows.append({"scenario": name, "problem_rate": yy.mean(), "score_psi": lab.psi(reference, q), "mean_score": q.mean(), "paid": rep["paid"], "reviewed": rep["reviewed"],
                 "error_paid": rep["error_paid"], "cost": rep["cost"], "paid_recal": rep2["paid"], "error_paid_recal": rep2["error_paid"], "cost_recal": rep2["cost"]})
print("\nDrift with the model frozen. 'recal' refits Platt on 10,000 fresh labelled invoices")
print(pd.DataFrame(rows).to_string(index=False))


# %% A risk target: pay as many as possible while keeping the error on paid invoices under 1%
def naive_threshold(y, p, target):
    """The highest cut-off whose validation error meets the target. No allowance for chance."""
    order = np.argsort(p)
    err = np.cumsum(y[order]) / np.arange(1, len(y) + 1)
    ok = np.flatnonzero(err <= target)
    return p[order][ok[-1]] if len(ok) else -1.0


def binomial_upper(errors, n, delta):
    """The Clopper-Pearson upper limit: the error rate we can rule out exceeding, with probability 1 - delta."""
    return 1.0 if errors >= n else stats.beta.ppf(1 - delta, errors + 1, n - errors)


def sgr_threshold(y, p, target, delta):
    """Geifman and El-Yaniv's binary search, with the budget split over its log2(n) tests."""
    order = np.argsort(p)
    ys, ps, n = y[order], p[order], len(y)
    steps = int(np.ceil(np.log2(n)))
    low, high, best = 0, n, -1.0
    errs = np.cumsum(ys)
    for _ in range(steps):
        mid = (low + high + 1) // 2
        if mid == 0:
            break
        if binomial_upper(int(errs[mid - 1]), mid, delta / steps) <= target:
            best, low = ps[mid - 1], mid
        else:
            high = mid - 1
        if low >= high:
            break
    return best


DELTA = 0.01
pool = inv.make_invoices(400_000, 6001)
hold = inv.make_invoices(200_000, 6002)
pool_p, hold_p = cal(inv.score(m, pool[FEATURES])), cal(inv.score(m, hold[FEATURES]))
pool_y, hold_y = pool.y.to_numpy(), hold.y.to_numpy()
order = np.argsort(hold_p)
hold_err = np.cumsum(hold_y[order]) / np.arange(1, len(hold_y) + 1)
rng = np.random.default_rng(0)
rows = []
for target in (0.01, 0.02):
    best = (hold_err <= target).nonzero()[0].max() / len(hold_y)
    for n in (500, 2_000, 10_000, 50_000):
        for method in ("naive", "SGR"):
            out = []
            for _ in range(200):
                i = rng.integers(0, len(pool_y), n)
                t = naive_threshold(pool_y[i], pool_p[i], target) if method == "naive" else sgr_threshold(pool_y[i], pool_p[i], target, DELTA)
                paid = hold_p <= t
                out.append((paid.mean(), hold_y[paid].mean() if paid.any() else 0.0))
            out = np.array(out)
            rows.append({"target": target, "best_share": best, "labelled": n, "method": method, "paid": out[:, 0].mean(), "paid_none": (out[:, 0] == 0).mean(),
                         "error_paid": out[:, 1].mean(), "broke_target": (out[:, 1] > target).mean()})
print(f"\nPay as many as possible under an error target, confidence {1 - DELTA:.0%}; 200 draws per row, judged on 200,000 fresh invoices")
print("best_share is the largest share a very large sample allows")
print(pd.DataFrame(rows).to_string(index=False))
i = rng.integers(0, len(pool_y), 50_000)
t = sgr_threshold(pool_y[i], pool_p[i], 0.02, DELTA)
concept = scenarios["concept: new fraud type"]
paid = cal(inv.score(m, concept[FEATURES])) <= t
print(f"SGR threshold for 2% on 50,000 labels: certified on clean data, then under the new fraud type: paid {paid.mean():.3f}, error {concept.y.to_numpy()[paid].mean():.4f}")


# %% Does conformal prediction earn its place?
def conformal_sets(p_cal, y_cal, p_test, alpha, by_class=False):
    """Split conformal with score 1 - f(x)_y. Returns whether 'good' and 'problem' are in each test set."""
    def q(scores):
        n = len(scores)
        level = min(np.ceil((n + 1) * (1 - alpha)) / n, 1.0)
        return np.quantile(scores, level, method="higher")
    s_good, s_prob = p_cal[y_cal == 0], 1 - p_cal[y_cal == 1]
    if by_class:
        q_good, q_prob = q(s_good), q(s_prob)
    else:
        q_good = q_prob = q(np.where(y_cal == 1, 1 - p_cal, p_cal))
    return p_test <= q_good, 1 - p_test <= q_prob


def conformal_row(name, alpha, has_good, has_prob, y):
    covered = np.where(y == 1, has_prob, has_good)
    only_good, only_prob = has_good & ~has_prob, has_prob & ~has_good
    r = np.where(only_good, PAY, np.where(only_prob, REJECT, REVIEW))
    return {"method": name, "alpha": alpha, "coverage": covered.mean(), "cover_problem": covered[y == 1].mean(), "cover_good": covered[y == 0].mean(),
            "only_good": only_good.mean(), "only_problem": only_prob.mean(), "both": (has_good & has_prob).mean(), "empty": (~has_good & ~has_prob).mean(),
            "error_paid": y[only_good].mean() if only_good.any() else np.nan, "cost": inv.unit_cost(y, r).mean()}


va, te = world(0)[1:]
pv, pt = cal(inv.score(m, va[FEATURES])), cal(inv.score(m, te[FEATURES]))
yv, yt = va.y.to_numpy(), te.y.to_numpy()
rows = []
for alpha in (0.2, 0.1, 0.05, 0.02, 0.01):
    for name, by_class in [("marginal", False), ("by class", True)]:
        rows.append(conformal_row(name, alpha, *conformal_sets(pv, yv, pt, alpha, by_class), yt))
conf = pd.DataFrame(rows)
print("\nSplit conformal on 10,000 calibration invoices (seed 0); singletons automated, the rest reviewed")
print(conf.to_string(index=False))
priced = inv.report(yt, pt, inv.route(pt, LO, HI))
print(f"Priced thresholds on the same invoices: cost {priced['cost']:.3f}, paid {priced['paid']:.3f}, reviewed {priced['reviewed']:.3f}, error on paid {priced['error_paid']:.4f}")
print(f"Lowest conformal cost in the table: {conf.cost.min():.3f}. Trivial 'always good' set covers {1 - yt.mean():.3f}")

rngc = np.random.default_rng(0)
cover = []
for _ in range(300):
    i = rngc.integers(0, len(pool_y), 1000)
    hg, hp = conformal_sets(pool_p[i], pool_y[i], hold_p, 0.1)
    cover.append(np.where(hold_y == 1, hp, hg).mean())
cover = np.array(cover)
print(f"Coverage across 300 calibration draws, n = 1,000, alpha 0.1: mean {cover.mean():.3f}, 5th to 95th percentile {np.quantile(cover, .05):.3f} to {np.quantile(cover, .95):.3f}")

tr, va, te = world(0)
weighted = inv.fit_boosted(tr[FEATURES], tr.y, 0, class_weight="balanced")
wv, wt = inv.score(weighted, va[FEATURES]), inv.score(weighted, te[FEATURES])
row = conformal_row("by class, uncalibrated model", 0.05, *conformal_sets(wv, va.y.to_numpy(), wt, 0.05, True), te.y.to_numpy())
print(f"Uncalibrated class-weighted scores, by class, alpha 0.05: cover problem {row['cover_problem']:.3f}, cover good {row['cover_good']:.3f}")
drift = scenarios["concept: new fraud type"]
qd = cal(inv.score(m, drift[FEATURES]))
for name, by_class in [("marginal", False), ("by class", True)]:
    row = conformal_row(name, 0.05, *conformal_sets(pool_p[:10_000], pool_y[:10_000], qd, 0.05, by_class), drift.y.to_numpy())
    print(f"Concept drift, {name}, alpha 0.05, promised 0.95: coverage {row['coverage']:.3f}, cover problem {row['cover_problem']:.3f}")

# %% The same policy on real credit data, natural default rate
raw = lab.load_credit()
CREDIT = Prices(pay_problem=3000.0, reject_good=600.0, review=60.0, catch=0.7, false_alarm=0.1)
WEAK = replace(CREDIT, catch=0.5, false_alarm=0.2)
clo, chi = inv.thresholds(CREDIT)
cone = inv.one_threshold(CREDIT)
print(f"\nCredit prices, reused from note 10 with an assumed analyst: review 60, catch 0.7, false alarm 0.1. Approve below {clo:.3f}, decline above {chi:.3f}, one threshold {cone:.3f}")
rows, sgr_rows, curve = [], [], None
print(f"Weak analyst, catch 0.5, false alarm 0.2: approve below {inv.thresholds(WEAK)[0]:.3f}, decline above {inv.thresholds(WEAK)[1]:.3f}")
for s in range(20):
    tr, va, te = lab.split(raw, seed=s)
    model = lab.make_pipeline(None, "boosted", {"max_leaf_nodes": 4, "max_iter": 300}, False, seed=s).fit(lab.features(tr), tr[lab.TARGET])
    rv, rt = model.predict_proba(lab.features(va))[:, 1], model.predict_proba(lab.features(te))[:, 1]
    calc = lab.platt(rv, va[lab.TARGET].to_numpy())
    q, yy = calc(rt), te[lab.TARGET].to_numpy()
    qv, yyv = calc(rv), va[lab.TARGET].to_numpy()
    t_sgr = sgr_threshold(yyv, qv, 0.10, DELTA)
    rows.append({"policy": "approve everyone", **inv.report(yy, q, inv.route(q, 2.0, 3.0), CREDIT)})
    rows.append({"policy": "review everyone", **inv.report(yy, q, inv.route(q, -1.0, 2.0), CREDIT)})
    rows.append({"policy": "one threshold", **inv.report(yy, q, inv.route(q, cone, cone), CREDIT)})
    rows.append({"policy": "two, priced", **inv.report(yy, q, inv.route(q, clo, chi), CREDIT)})
    rows.append({"policy": "two, priced, weak analyst", **inv.report(yy, q, inv.route(q, *inv.thresholds(WEAK)), WEAK)})
    rows.append({"policy": "one threshold, weak analyst prices", **inv.report(yy, q, inv.route(q, inv.one_threshold(WEAK), inv.one_threshold(WEAK)), WEAK)})
    sgr_rows.append(((q <= t_sgr).mean(), yy[q <= t_sgr].mean()))
    if s == 0:
        curve = (q, yy)
credit = pd.DataFrame(rows)
print(credit.groupby("policy", sort=False)[cols].mean().to_string())
for a, b in [("one threshold", "two, priced"), ("one threshold, weak analyst prices", "two, priced, weak analyst")]:
    diff = credit[credit.policy == a].cost.to_numpy() - credit[credit.policy == b].cost.to_numpy()
    print(f"{a} minus {b}: {diff.mean():+.2f} per applicant (sd {diff.std():.2f}, {(diff > 0).sum()}/20 seeds)")
print(f"SGR for a 10% default target on 6,000 validation rows: approves {np.mean(sgr_rows, axis=0)[0]:.3f}, default rate {np.mean(sgr_rows, axis=0)[1]:.3f}")

# %% Figures
import chartstyle as cs
import matplotlib.pyplot as plt

cs.apply()
grid = np.linspace(0, 1, 501)
ec = expected_costs(grid)
fig, ax = plt.subplots()
for j, (label, colour) in enumerate([("Pay", cs.BLUE), ("Review", cs.ORANGE), ("Reject", cs.AQUA)]):
    ax.plot(grid, ec[:, j], color=colour, label=label)
ax.plot(grid, ec.min(axis=1), color=cs.INK, lw=1, ls=":", label="Cheapest route")
for t, txt in [(LO, f"pay below {LO:.3f}"), (HI, f"reject above {HI:.3f}")]:
    ax.axvline(t, color=cs.MUTED, lw=1)
    ax.annotate(txt, (t, 34), xytext=(5, 0), textcoords="offset points", color=cs.SECONDARY)
ax.set_xlim(0, 1)
ax.set_ylim(0, 36)
ax.set_xlabel("Probability that this invoice has a problem")
ax.set_ylabel("Expected cost, euros")
ax.set_title("Each route has a cost line; the thresholds are where the lowest line changes")
ax.legend(loc="upper right")
cs.save(fig, "review-queue-three-routes.png")

te = world(0)[2]
pt = cal(inv.score(m, te[FEATURES]))

fig, axes = plt.subplots(1, 2, figsize=(9, 4.2))
ax = axes[0]
for q, label, colour in [(pt, "Model", cs.BLUE), (te.true_p.to_numpy(), "True probability", cs.ORANGE)]:
    o = np.argsort(q)
    cov = np.arange(1, len(q) + 1) / len(q)
    err = np.cumsum(te.y.to_numpy()[o]) / np.arange(1, len(q) + 1)
    ax.plot(cov[200:], err[200:], color=colour, label=label)
paid = pt < LO
ax.plot(paid.mean(), te.y.to_numpy()[paid].mean(), "o", ms=8, color=cs.INK)
ax.annotate(f"priced: {paid.mean():.0%} paid,\n{te.y.to_numpy()[paid].mean():.1%} error", (paid.mean(), te.y.to_numpy()[paid].mean()), xytext=(-8, 16), textcoords="offset points", ha="right")
ax.set_xlabel("Share paid without review")
ax.set_ylabel("Error rate among those paid")
ax.set_title("Generated invoices")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
ax.legend(loc="upper left")
ax = axes[1]
q, yy = curve
o = np.argsort(q)
cov = np.arange(1, len(q) + 1) / len(q)
err = np.cumsum(yy[o]) / np.arange(1, len(q) + 1)
ax.plot(cov[30:], err[30:], color=cs.BLUE, label="Model")
paid = q < clo
ax.plot(paid.mean(), yy[paid].mean(), "o", ms=8, color=cs.INK)
ax.annotate(f"priced: {paid.mean():.0%} approved,\n{yy[paid].mean():.1%} error", (paid.mean(), yy[paid].mean()), xytext=(10, -22), textcoords="offset points")
ax.set_xlabel("Share approved without review")
ax.set_ylabel("Default rate among those approved")
ax.set_title("Real credit file")
ax.set_ylim(0, None)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
cs.save(fig, "review-queue-risk-coverage.png")
