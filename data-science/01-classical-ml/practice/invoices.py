"""Generated invoices and the two-threshold router, shared by review_queue.py and learning_from_corrections.py.

Nothing here comes from a real business. The features, the rules that make an invoice a problem and every
price are invented so that the truth is known. Results on this data describe the generator, which is why
review_queue.py repeats the policy on a real credit file.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

FEATURES = ["log_amount", "tenure_months", "prior_issue_rate", "po_match", "price_diff", "qty_mismatch",
            "bank_changed", "dup_sim", "extract_conf", "round_amount"]
PAY, REVIEW, REJECT = 0, 1, 2


@dataclass(frozen=True)
class Prices:
    """What each outcome costs, in euros per invoice. Invented; a real system has to measure them."""
    pay_problem: float = 150.0   # paying an invoice that has a problem
    reject_good: float = 30.0    # sending a good invoice back to the supplier
    review: float = 3.0          # four minutes of a clerk's time
    catch: float = 0.9           # share of problems the clerk catches
    false_alarm: float = 0.02    # share of good invoices the clerk sends back


def true_probability(x, new_pattern=0.0):
    """P(problem | features). `new_pattern` adds a fraud type on round-amount invoices, absent at training time."""
    z = (-5.0 + 1.3 * (1 - x["po_match"]) + 12 * x["price_diff"].clip(upper=0.3) + 1.1 * x["qty_mismatch"]
         + 2.2 * x["bank_changed"] + 7 * x["dup_sim"] ** 2 + 16 * x["prior_issue_rate"]
         + 0.8 * (x["tenure_months"] < 6) + 1.2 * x["bank_changed"] * (x["tenure_months"] < 6)
         - 6 * (x["extract_conf"] - 0.9) + 0.25 * (x["log_amount"] - 6.3))
    p = 1 / (1 + np.exp(-z))
    return p + (1 - p) * new_pattern * x["round_amount"]


def make_invoices(n, seed, new_pattern=0.0, tenure_mean=40.0, po_rate=0.82):
    """n invoices with features, the true probability and a drawn outcome `y`."""
    rng = np.random.default_rng(seed)
    po = rng.binomial(1, po_rate, n)
    x = pd.DataFrame({
        "log_amount": rng.normal(6.3, 1.1, n),
        "tenure_months": rng.exponential(tenure_mean, n),
        "prior_issue_rate": rng.beta(1, 40, n),
        "po_match": po,
        "price_diff": np.abs(rng.laplace(0, 0.02, n)) + (1 - po) * np.abs(rng.laplace(0, 0.08, n)),
        "qty_mismatch": rng.binomial(1, 0.05 + 0.10 * (1 - po), n),
        "bank_changed": rng.binomial(1, 0.03, n),
        "dup_sim": rng.beta(1, 8, n),
        "extract_conf": rng.beta(20, 2, n),
        "round_amount": rng.binomial(1, 0.06, n),
    })
    x["true_p"] = true_probability(x, new_pattern)
    x["y"] = rng.binomial(1, x["true_p"])
    return x


def fit_boosted(x, y, seed=0, weights=None, class_weight=None):
    m = HistGradientBoostingClassifier(learning_rate=0.05, max_iter=200, max_leaf_nodes=8, early_stopping=False,
                                       random_state=seed, class_weight=class_weight)
    return m.fit(x, y, sample_weight=weights)


def score(m, x):
    return m.predict_proba(x)[:, 1]


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def platt(p, y, weights=None):
    """Fit a slope and an intercept on the log-odds, on data the model did not train on."""
    m = LogisticRegression(C=1e6, max_iter=1000).fit(logit(p).reshape(-1, 1), y, sample_weight=weights)
    return lambda q: m.predict_proba(logit(q).reshape(-1, 1))[:, 1]


def thresholds(c=Prices()):
    """The two cut-offs from the prices: pay below `lo`, reject above `hi`, review between."""
    lo = (c.review + c.false_alarm * c.reject_good) / (c.catch * c.pay_problem + c.false_alarm * c.reject_good)
    keep = c.reject_good * (1 - c.false_alarm)
    hi = (keep - c.review) / ((1 - c.catch) * c.pay_problem + keep)
    return lo, hi


def one_threshold(c=Prices()):
    """With no review route: reject when the cost of paying passes the cost of rejecting."""
    return c.reject_good / (c.reject_good + c.pay_problem)


def route(p, lo, hi):
    return np.where(p < lo, PAY, np.where(p >= hi, REJECT, REVIEW))


def unit_cost(y, r, c=Prices(), pay_problem=None):
    """Expected euros per invoice. The clerk's catch and false alarm are taken in expectation."""
    a = c.pay_problem if pay_problem is None else pay_problem
    pay = y * a
    reject = (1 - y) * c.reject_good
    review = c.review + y * (1 - c.catch) * a + (1 - y) * c.false_alarm * c.reject_good
    return np.where(r == PAY, pay, np.where(r == REJECT, reject, review))


def report(y, p, r, c=Prices()):
    """The product metrics for one routing of one batch."""
    y, r = np.asarray(y), np.asarray(r)
    paid, rej, rev = r == PAY, r == REJECT, r == REVIEW
    suggest_reject = p >= one_threshold(c)
    # What share of the reviewed invoices does the clerk's decision differ from the model's suggestion?
    clerk_rejects = y * c.catch + (1 - y) * c.false_alarm
    changed = np.where(suggest_reject, 1 - clerk_rejects, clerk_rejects)
    return {
        "straight_through": float((paid | rej).mean()),
        "paid": float(paid.mean()),
        "reviewed": float(rev.mean()),
        "rejected": float(rej.mean()),
        "error_paid": float(y[paid].mean()) if paid.any() else float("nan"),
        "precision_reject": float(y[rej].mean()) if rej.any() else float("nan"),
        "correction_rate": float(changed[rev].mean()) if rev.any() else float("nan"),
        "cost": float(unit_cost(y, r, c).mean()),
    }
