"""Synthetic B2B transactions, in three worlds. Nothing here describes a real company.

The idea is taken from atlas's `core/preprocessing/synthetic.py`
(https://github.com/ramseywise/atlas): customers are business archetypes with different cash flow
shapes. The code and every parameter are written fresh for this lab, so the lab needs nothing from atlas.

  planted   five archetypes, tightly grouped. The easy case: a clusterer should find them.
  blurred   the same five, with the spread within each archetype multiplied by BLUR.
  control   no archetypes. Each customer is drawn from one Gaussian with the mean and covariance
            of the planted population, then simulated by the same code. Nothing to find.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 42
START = pd.Timestamp("2023-01-02")   # a Monday, so weeks line up
N_WEEKS = 156
BLUR = 2.5

# Each parameter is on the scale where a Gaussian makes sense.
PARAMS = ["log_revenue", "log_invoices", "invoice_sigma", "growth", "q4_boost", "log_burn", "log_tranches"]
#                     log_revenue  log_invoices  sigma  growth  q4     log_burn      log_tranches
ARCHETYPES = {
    "saas_growth":     ([10.5,     np.log(30),   0.30,  0.60,  0.00,  np.log(0.85), np.log(0.02)], 2.0),
    "smb_services":    ([10.0,     np.log(6),    0.50,  0.05,  0.05,  np.log(0.92), np.log(0.02)], 2.0),
    "manufacturing":   ([11.5,     np.log(3),    1.10,  0.02,  0.10,  np.log(0.95), np.log(0.02)], 1.0),
    "retail_seasonal": ([11.0,     np.log(40),   0.50,  0.03,  1.20,  np.log(0.95), np.log(0.02)], 1.0),
    "early_stage":     ([ 8.5,     np.log(1.5),  0.60,  0.30,  0.00,  np.log(3.00), np.log(1.00)], 1.5),
}
#                 log_revenue log_invoices sigma growth q4   log_burn log_tranches
SPREAD = np.array([0.35,      0.15,        0.05, 0.06,  0.05, 0.04,   0.10])
LOWER = np.array([6.0, np.log(0.5), 0.05, -0.5, 0.0, np.log(0.4), np.log(0.01)])
UPPER = np.array([14.0, np.log(80), 1.60, 1.2, 2.0, np.log(6.0), np.log(3.0)])


def _planted_params(n, rng, spread=1.0):
    names = list(ARCHETYPES)
    weights = np.array([ARCHETYPES[a][1] for a in names])
    which = rng.choice(len(names), size=n, p=weights / weights.sum())
    centres = np.array([ARCHETYPES[a][0] for a in names])
    theta = centres[which] + rng.normal(0, 1, (n, len(PARAMS))) * SPREAD * spread
    return np.clip(theta, LOWER, UPPER), np.array(names)[which]


def _control_params(n, rng):
    """One Gaussian with the planted population's mean and covariance: same spread, no groups."""
    big, _ = _planted_params(20_000, np.random.default_rng(SEED + 1))
    theta = rng.multivariate_normal(big.mean(0), np.cov(big.T), size=n)
    return np.clip(theta, LOWER, UPPER), np.array(["none"] * n)


def _simulate_one(cid, theta, rng):
    """Daily inflow invoices, fortnightly payroll, irregular payables and rare funding tranches."""
    log_rev, log_inv, sigma, growth, q4, log_burn, log_tr = theta
    days = np.arange(N_WEEKS * 7)
    dates = START + pd.to_timedelta(days, unit="D")
    bump = np.exp(-0.5 * ((dates.dayofyear.to_numpy() - 335) / 30) ** 2)        # peaks at the start of December
    monthly = np.exp(log_rev + growth * days / 365.25) * (1 + q4 * bump)
    invoices = np.exp(log_inv)

    rows = []
    n_in = rng.poisson(invoices / 30.44, size=len(days))
    idx = np.repeat(days, n_in)
    amount = monthly[idx] / invoices * rng.lognormal(-sigma ** 2 / 2, sigma, size=len(idx))
    rows.append(pd.DataFrame({"day": idx, "amount": amount, "kind": "invoice"}))

    burn = np.exp(log_burn)
    base = np.exp(log_rev + growth * days / 365.25) * burn          # costs follow the trend, not the Q4 spike
    pay_days = days[(days + rng.integers(14)) % 14 == 0]
    rows.append(pd.DataFrame({"day": pay_days, "amount": -0.6 * base[pay_days] * 12 / 26 * rng.lognormal(-.0002, .02, len(pay_days)),
                              "kind": "payroll"}))
    n_out = rng.poisson(4 / 30.44, size=len(days))
    idx = np.repeat(days, n_out)
    rows.append(pd.DataFrame({"day": idx, "amount": -0.4 * base[idx] * (1 + 0.5 * q4 * bump[idx]) / 4 * rng.lognormal(-.08, .4, len(idx)),
                              "kind": "payable"}))

    n_tr = rng.poisson(np.exp(log_tr) / 365.25, size=len(days))
    idx = np.repeat(days, n_tr)
    rows.append(pd.DataFrame({"day": idx, "amount": 12 * base[idx] * rng.lognormal(0, .3, len(idx)), "kind": "tranche"}))

    out = pd.concat(rows, ignore_index=True).sort_values("day", kind="stable")
    out.insert(0, "customer_id", cid)
    return out


def make_world(kind="planted", n_customers=400, seed=SEED):
    """Return (transactions, truth). Amounts are signed: money in is positive, money out negative."""
    rng = np.random.default_rng(seed)
    if kind == "planted":
        theta, truth = _planted_params(n_customers, rng)
    elif kind == "blurred":
        theta, truth = _planted_params(n_customers, rng, spread=BLUR)
    elif kind == "control":
        theta, truth = _control_params(n_customers, rng)
    else:
        raise ValueError(kind)
    frames = [_simulate_one(i, theta[i], rng) for i in range(n_customers)]
    tx = pd.concat(frames, ignore_index=True)
    tx["date"] = START + pd.to_timedelta(tx.pop("day"), unit="D")
    return tx, pd.Series(truth, name="archetype")
