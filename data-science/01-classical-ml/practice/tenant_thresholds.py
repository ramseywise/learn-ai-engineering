# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scipy"]
# ///
"""The numbers in notes/13's section on per-customer thresholds. Run with `uv run tenant_thresholds.py`, a few seconds.

Generated data, no real customer. One shared score. Each customer's true log-odds sit an unknown offset from that score.
We estimate each offset from that customer's labels, three ways, and route with the note's prices on fresh rows.
"""
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import expit, logit

pd.set_option("display.width", 160)
A, R, H, C, F = 150.0, 30.0, 3.0, .9, .02  # the prices in invoices.Prices: pay a problem, reject good, review, catch, false alarm
LABELS = [20, 50, 200, 1000, 5000]
METHODS = ["one global threshold", "each customer alone", "alone, global if no fit", "partial pooling"]
N_TENANTS, TEST, SEEDS = 40, 20_000, range(20)


def cost(p_true, p_used):
    """Mean euro cost per invoice when routing on p_used and the truth is p_true."""
    lines = lambda p: np.stack([p * A, H + p * (1 - C) * A + (1 - p) * F * R, (1 - p) * R])  # pay, review, reject
    return lines(p_true)[lines(p_used).argmin(0), np.arange(len(p_true))].mean()


def fit_offset(score, y):
    """Offset on the log-odds with the score's slope held at one, and its approximate variance.

    Maximum likelihood sets expected problems equal to observed ones. With no problem, or no good invoice, in the labels
    it has no finite answer, so `finite` is False and the fit aims half a problem away from the edge instead.
    """
    events, finite = y.sum(), 0 < y.sum() < len(y)
    target = events if finite else (.5 if events == 0 else len(y) - .5)
    d = brentq(lambda d: target - expit(score + d).sum(), -25, 25)
    p = expit(score + d)
    return d, 1 / (p * (1 - p)).sum(), finite


rows, weights = [], []
for seed in SEEDS:
    rng = np.random.default_rng(seed)
    for sd_true in (.0, .4, 1.0):
        offsets = rng.normal(0, sd_true, N_TENANTS)
        sizes = np.tile(LABELS, N_TENANTS // len(LABELS))
        fits, ones = [], []
        for t, n in zip(offsets, sizes):
            s = logit(np.clip(rng.beta(.6, 8, n), 1e-4, 1 - 1e-4))
            y = rng.binomial(1, expit(s + t))
            fits.append(fit_offset(s, y))
            ones.append(y.sum() == 1)
        ones = np.array(ones)
        est, var, keep = (np.array(column) for column in zip(*fits))
        keep = keep.astype(bool)
        # between-customer variance by moments, floored at zero, then shrink each offset by how much its data can say
        tau2 = max(np.average(est[keep] ** 2 - var[keep], weights=1 / var[keep]), 0)
        shrunk = est * tau2 / (tau2 + var)
        small, large = sizes == 20, sizes == 5000
        weights.append(dict(sd_true=sd_true, tau2=tau2, no_fit_at_20=(~keep[small]).mean(), v_at_20=var[small & keep], v_no_fit=var[small & ~keep], v_at_5000=var[large],
                            no_problem_offset=shrunk[small & ~keep & (est < 0)], one_problem_offset=np.array([sh for sh, y1 in zip(shrunk[small], ones[small]) if y1])))
        for t, n, e, sh, finite in zip(offsets, sizes, est, shrunk, keep):
            s = logit(np.clip(rng.beta(.6, 8, TEST), 1e-4, 1 - 1e-4))
            true = expit(s + t)
            base = cost(true, true)
            literal = e if finite else -30.0 if e < 0 else 30.0  # the literal fit: no problem seen, so pay everything
            for name, d in (("one global threshold", 0.0), ("each customer alone", literal), ("alone, global if no fit", e if finite else 0.0), ("partial pooling", sh)):
                rows.append(dict(seed=seed, sd_true=sd_true, labels=n, method=name, regret=cost(true, expit(s + d)) - base))
res = pd.DataFrame(rows)
print(f"{N_TENANTS} customers, {len(SEEDS)} seeds. Regret: euros per invoice above routing on the true probability\n")
print(res.pivot_table(index=["sd_true", "labels"], columns="method", values="regret")[METHODS].round(3).to_string())
print("\nmean over all customer sizes, equal weight per customer")
print(res.pivot_table(index="sd_true", columns="method", values="regret")[METHODS].round(3).to_string())

print("\nwhat the shrinkage saw, by sd_true: mean tau^2, share of 20-label customers with no finite fit, median v_k over the finite fits")
for sd_true, w in pd.DataFrame(weights).groupby("sd_true"):
    tau2, v20, v5000 = w.tau2.mean(), np.median(np.concatenate(w.v_at_20.values)), np.median(np.concatenate(w.v_at_5000.values))
    vnone = np.median(np.concatenate(w.v_no_fit.values))
    none, one = np.concatenate(w.no_problem_offset.values).mean(), np.concatenate(w.one_problem_offset.values).mean()
    print(f"{sd_true}: tau^2 {tau2:.3f}, no fit {w.no_fit_at_20.mean():.3f}, v at 20 labels {v20:.3f} keeps {tau2 / (tau2 + v20):.2f}, no-fit v {vnone:.3f} keeps {tau2 / (tau2 + vnone):.2f}, "
          f"v at 5000 {v5000:.3f}, pooled offset with 0 problems {none:.3f}, with 1 problem {one:.3f}")

close = res[(res.sd_true == 1.0) & (res.labels == 200)].pivot_table(index="seed", columns="method", values="regret")
gap = close["partial pooling"] - close["each customer alone"]
print(f"\npartial pooling minus each customer alone, sd_true 1.0, 200 labels: mean {gap.mean():.3f}, sd {gap.std():.3f}, pooling lost {(gap > 0).sum()} of {len(gap)} seeds")
