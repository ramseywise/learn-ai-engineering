# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scikit-learn", "torch"]
# ///
"""Card fraud as a sequence problem, for notes/05: aggregates against a GRU, leaks, late labels, cost and drift.

Run from this folder (about three minutes on a laptop CPU, downloads nothing, needs no key):
    uv run transaction_sequence_lab.py
    uv run transaction_sequence_lab.py --delay-median 60      # chargebacks take longer
    uv run transaction_sequence_lab.py --drift none           # the pattern never changes
    uv run transaction_sequence_lab.py --seeds 1              # skip the repeat on other generated datasets

What is generated: every customer, merchant, charge and label comes from a seeded generator. No real card data is
involved. What we planted: fraud is a few small online test charges followed quickly by a large online charge, with no
card-present charge after the tests. Decoys hold the same charges in a different order or further apart, so totals
can't see it. That pattern was written to favour order and timing, so a sequence model doing well here is a fact about
this generator and not about fraud in general. Every price and rate below is an assumption. The generator's constants
were fixed before any model was compared, and they were not adjusted to change which model wins.

The fundamentals of imbalance, PR-AUC, the cost rule, calibration and PSI are in
data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md. This lab applies them to ordered events.
"""
# %%
import argparse
import time

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score

SEED = 7
CUSTOMERS, DAYS = 3000, 420
EVENTS_PER_DAY = 0.8                 # mean per customer
SCORE_FROM = 50.0                    # only charges at or above this are scored: the decisions worth a model
SMALL = 10.0                         # what counts as a small charge
ATTACK_RATE, TIMING_DECOYS, ORDER_DECOYS, TWIN_DECOYS = 0.25, 1.0, 0.5, 0.03   # per customer per year
SEQ_LEN = 12
TRAIN_END, VAL_END, TEST_END, DRIFT_END = 180, 240, 300, 360   # days; 360 to 420 is held for the retraining section
MATURITY_DAYS = 75                   # treat a label as final after this many days
FP_COST, LOSS_SHARE, CB_FEE = 8.0, 0.9, 20.0   # a blocked good charge; share of a missed fraud lost; chargeback fee

CATEGORIES = ["grocery", "fuel", "restaurant", "transit", "pharmacy", "apparel", "digital", "electronics", "travel",
              "gift_card"]
CAT = {c: i for i, c in enumerate(CATEGORIES)}
MIX = np.array([.26, .10, .17, .10, .05, .08, .10, .04, .07, .03])
ONLINE = np.array([.02, 0, .05, .10, .05, .35, 1, .45, .70, .80])
LOG_MEAN = np.log([35, 50, 28, 6, 18, 60, 9, 180, 200, 60])
LOG_SD = np.array([.6, .3, .6, .6, .6, .7, .6, .9, .9, .6])
POOL = 40                            # merchants per category
AMOUNT_EDGES = np.array([2, 5, 10, 20, 50, 100, 200, 500, 1000])
MINUTES = 1440


# %% The generator
def small_amount(rng):
    return float(np.round(rng.uniform(1, 5), 2))


def large_amount(rng):
    return float(np.round(max(60.0, rng.lognormal(np.log(420), .6)), 2))


def attack_rows(rng, t0, campaign, slow):
    """One compromised card: tests, then the cash-out. `slow` is the pattern that replaces it in the final period."""
    rows = []
    t = t0
    if rng.random() < .35:                       # the real customer happens to be out shopping shortly before
        cat = rng.choice([CAT["grocery"], CAT["restaurant"]])
        rows.append((t, cat, 0, float(np.round(rng.lognormal(LOG_MEAN[cat], LOG_SD[cat]), 2)), merchant(rng, cat), 0, 0))
        t += rng.integers(10, 41)
    tests = 0 if rng.random() < .08 else rng.choice([1, 2, 3, 4], p=[.15, .35, .35, .15])  # 8% are plain stolen cards
    if slow:
        for _ in range(tests):
            rows.append((t, CAT["transit"], 1, small_amount(rng), merchant(rng, CAT["transit"]), 0, 1))
            t += rng.integers(180, 541)
        t += rng.integers(120, 481)
        cat = CAT["travel"]
    else:
        for _ in range(tests):
            rows.append((t, CAT["digital"], 1, small_amount(rng), merchant(rng, CAT["digital"]), 0, 1))
            t += rng.integers(3, 26)
        t += rng.integers(5, 41)
        cat = CAT["electronics"] if rng.random() < .7 else CAT["gift_card"]
    rows.append((t, cat, 1, large_amount(rng), rng.choice(campaign[cat]), 1, 2))
    return rows


def merchant(rng, cat):
    return int(cat * POOL + rng.integers(POOL))


def decoy_rows(rng, t0, kind):
    """Legitimate activity holding the same charges as an attack, and a different order or spacing."""
    rows = []
    t = t0
    for _ in range(rng.choice([1, 2, 3, 4], p=[.15, .35, .35, .15])):
        rows.append((t, CAT["digital"], 1, small_amount(rng), merchant(rng, CAT["digital"]), 0, 3))
        t += rng.integers(3, 26) if kind != "timing" else rng.integers(MINUTES, 3 * MINUTES)
    if kind == "order":                          # the customer is present between the tests and the large charge
        cat = rng.choice([CAT["grocery"], CAT["restaurant"]])
        rows.append((t, cat, 0, float(np.round(rng.lognormal(LOG_MEAN[cat], LOG_SD[cat]), 2)), merchant(rng, cat), 0, 3))
        t += rng.integers(5, 21)
    else:
        t += rng.integers(5, 41)
    cat = CAT["electronics"] if rng.random() < .7 else CAT["gift_card"]
    rows.append((t, cat, 1, large_amount(rng), merchant(rng, cat), 0, 3))
    return rows


def make_events(seed, drift="slow", delay_median=28.0):
    """One row per charge, sorted by customer and time. `fraud` is the final truth; `delay` is days to the chargeback."""
    rng = np.random.default_rng(seed)
    campaigns = [{c: rng.integers(c * POOL, (c + 1) * POOL, 2) for c in (CAT["electronics"], CAT["gift_card"], CAT["travel"])}
                 for _ in range(DAYS // 30 + 2)]
    parts = []
    years = DAYS / 365
    for c in range(CUSTOMERS):
        rate = rng.gamma(2, EVENTS_PER_DAY / 2)
        n = rng.poisson(rate * DAYS)
        day = rng.integers(0, DAYS, n)
        minute = np.clip(rng.normal(13 * 60, 4 * 60, n), 0, MINUTES - 1).astype(int)
        cat = rng.choice(len(CATEGORIES), n, p=MIX)
        rows = [(int(day[i] * MINUTES + minute[i]), int(cat[i]), int(rng.random() < ONLINE[cat[i]]),
                 float(np.round(rng.lognormal(LOG_MEAN[cat[i]], LOG_SD[cat[i]]), 2)), merchant(rng, int(cat[i])), 0, 0)
                for i in range(n)]
        for _ in range(rng.poisson(ATTACK_RATE * years)):
            t0 = int(rng.integers(0, (DAYS - 2) * MINUTES))
            slow = drift == "slow" and t0 >= TEST_END * MINUTES
            rows += attack_rows(rng, t0, campaigns[t0 // (30 * MINUTES)], slow)
        for kind, per_year in (("timing", TIMING_DECOYS), ("order", ORDER_DECOYS), ("twin", TWIN_DECOYS)):
            for _ in range(rng.poisson(per_year * years)):
                rows += decoy_rows(rng, int(rng.integers(0, (DAYS - 12) * MINUTES)), kind)
        rows.sort(key=lambda r: r[0])
        part = pd.DataFrame(rows, columns=["t", "cat", "online", "amount", "merchant", "fraud", "kind"])
        part["customer"] = c
        parts.append(part)
    ev = pd.concat(parts, ignore_index=True)
    ev = ev[ev.t < DAYS * MINUTES].reset_index(drop=True)
    ev["day"] = ev.t // MINUTES
    ev["scored"] = ev.amount >= SCORE_FROM
    ev["delay"] = np.where(ev.fraud == 1, rng.lognormal(np.log(delay_median), .6, len(ev)), np.nan)
    return ev


def known_labels(fraud, day, delay, as_of):
    """What the fraud team knows on day `as_of`: a fraud with no chargeback yet looks exactly like a clean charge."""
    return ((fraud == 1) & (day + delay <= as_of)).astype(int)


# %% Features: three levels of hand-building
TOTALS = ["amount", "cat", "online", "hour", "n_30d", "sum_30d", "max_30d", "n_small_30d", "n_online_30d", "n_digital_30d"]
WINDOWS = {"1h": 60, "6h": 360, "24h": MINUTES, "7d": 7 * MINUTES}
VELOCITY = TOTALS + [f"{m}_{w}" for w in WINDOWS for m in ("n", "sum", "small_online", "present")] + [
    "gap_1", "gap_2", "gap_3", "since_small_online", "amount_vs_mean", "cat_1", "cat_2", "cat_3", "online_1", "online_2",
    "online_3", "log_amount_1", "log_amount_2", "log_amount_3"]
ORACLE = VELOCITY + ["tests_since_present_2h"]   # the planted rule, written as one feature
CATEGORICAL = {"cat", "cat_1", "cat_2", "cat_3"}


def customer_features(g):
    """Features for one customer's scored charges, using only charges before each one. Takes a time-sorted frame."""
    t, a, cat, onl = g.t.to_numpy(), g.amount.to_numpy(), g["cat"].to_numpy(), g.online.to_numpy()
    idx = np.flatnonzero(g.scored.to_numpy())
    if not len(idx):
        return pd.DataFrame()
    small_online = (a < SMALL) & (onl == 1)
    present = onl == 0
    cs = {"n": np.arange(len(t) + 1), "sum": np.r_[0, np.cumsum(a)], "small_online": np.r_[0, np.cumsum(small_online)],
          "present": np.r_[0, np.cumsum(present)], "online": np.r_[0, np.cumsum(onl)], "small": np.r_[0, np.cumsum(a < SMALL)],
          "digital": np.r_[0, np.cumsum(cat == CAT["digital"])]}
    f = {"amount": a[idx], "cat": cat[idx], "online": onl[idx], "hour": (t[idx] % MINUTES) // 60}
    lo30 = np.searchsorted(t, t[idx] - 30 * MINUTES)
    f["n_30d"] = idx - lo30
    f["sum_30d"] = cs["sum"][idx] - cs["sum"][lo30]
    f["max_30d"] = [a[l:i].max() if i > l else 0.0 for l, i in zip(lo30, idx)]
    f["n_small_30d"] = cs["small"][idx] - cs["small"][lo30]
    f["n_online_30d"] = cs["online"][idx] - cs["online"][lo30]
    f["n_digital_30d"] = cs["digital"][idx] - cs["digital"][lo30]
    for w, minutes in WINDOWS.items():
        lo = np.searchsorted(t, t[idx] - minutes)
        for m in ("n", "sum", "small_online", "present"):
            f[f"{m}_{w}"] = cs[m][idx] - cs[m][lo]
    last_small = np.maximum.accumulate(np.where(small_online, np.arange(len(t)), -1))
    prior_small = np.where(idx > 0, last_small[np.maximum(idx - 1, 0)], -1)
    f["since_small_online"] = np.where(prior_small >= 0, t[idx] - t[prior_small], np.nan)
    f["amount_vs_mean"] = a[idx] / np.maximum(f["sum_30d"] / np.maximum(f["n_30d"], 1), 1.0)
    for k in (1, 2, 3):
        back, ok = idx - k, idx - k >= 0
        f[f"gap_{k}"] = np.where(ok, t[idx] - t[np.maximum(back, 0)], np.nan)
        f[f"cat_{k}"] = np.where(ok, cat[np.maximum(back, 0)], -1)
        f[f"online_{k}"] = np.where(ok, onl[np.maximum(back, 0)], -1)
        f[f"log_amount_{k}"] = np.where(ok, np.log1p(a[np.maximum(back, 0)]), np.nan)
    tests = np.zeros(len(idx), int)
    for n, i in enumerate(idx):                  # walk back: small online charges inside 2h, stopping at a present charge
        j = i - 1
        while j >= 0 and t[i] - t[j] <= 120 and not present[j]:
            tests[n] += small_online[j]
            j -= 1
    f["tests_since_present_2h"] = tests
    return pd.DataFrame(f, index=g.index[idx])


def build_table(ev):
    x = pd.concat([customer_features(g) for _, g in ev.groupby("customer", sort=False)]).sort_index()
    meta = ev.loc[x.index, ["customer", "day", "fraud", "delay", "amount", "merchant", "kind"]]
    x["hour"] = x.hour.astype(int)
    return x, meta


def build_sequences(ev, index):
    """The last SEQ_LEN charges up to and including each scored one. Padded on the left, so the last step is always real."""
    n = len(index)
    cat = np.zeros((n, SEQ_LEN), np.int64)
    onl, amt, mer = cat.copy(), cat.copy(), cat.copy()
    gap = np.zeros((n, SEQ_LEN), np.float32)
    bins = np.digitize(ev.amount.to_numpy(), AMOUNT_EDGES) + 1
    position = pd.Series(np.arange(len(index)), index=index)
    tt, cc, oo, mm, cust = (ev[c].to_numpy() for c in ("t", "cat", "online", "merchant", "customer"))
    for row, i in zip(position.to_numpy(), index):
        start = max(i - SEQ_LEN + 1, 0)
        while cust[start] != cust[i]:
            start += 1
        span = np.arange(start, i + 1)
        k = len(span)
        cat[row, -k:], onl[row, -k:], amt[row, -k:], mer[row, -k:] = cc[span] + 1, oo[span] + 1, bins[span], mm[span] + 1
        gaps = np.diff(tt[span], prepend=tt[start])
        gap[row, -k:] = np.log1p(gaps) / 10
    return {"cat": cat, "online": onl, "amount": amt, "merchant": mer, "gap": gap}


# %% Models
def fit_boost(x, y, columns, seed=0):
    x = x[columns]
    cats = [c for c in columns if c in CATEGORICAL or c == "merchant_risk" and False]
    frame = x.copy()
    for c in cats:
        frame[c] = frame[c].astype(int) + 1
    model = HistGradientBoostingClassifier(learning_rate=.05, max_iter=300, max_leaf_nodes=31, early_stopping=False,
                                           categorical_features=cats, random_state=seed)
    model.fit(frame, y)

    def score(q):
        q = q[columns].copy()
        for c in cats:
            q[c] = q[c].astype(int) + 1
        return model.predict_proba(q)[:, 1]

    return score


class EventGRU(nn.Module):
    """Each charge becomes a sum of embeddings plus its log gap, and the GRU's last state scores the final charge."""

    def __init__(self, use_merchant=False, hidden=48):
        super().__init__()
        self.cat = nn.Embedding(len(CATEGORIES) + 1, 6)
        self.online = nn.Embedding(3, 2)
        self.amount = nn.Embedding(len(AMOUNT_EDGES) + 2, 6)
        self.merchant = nn.Embedding(len(CATEGORIES) * POOL + 1, 8) if use_merchant else None
        self.gru = nn.GRU(6 + 2 + 6 + 1 + (8 if use_merchant else 0), hidden, batch_first=True)
        self.head = nn.Linear(hidden, 1)

    def forward(self, s):
        parts = [self.cat(s["cat"]), self.online(s["online"]), self.amount(s["amount"]), s["gap"].unsqueeze(-1)]
        if self.merchant is not None:
            parts.append(self.merchant(s["merchant"]))
        out, _ = self.gru(torch.cat(parts, -1))
        return self.head(out[:, -1]).squeeze(-1)


def take(seq, mask):
    return {k: torch.as_tensor(v[mask]) for k, v in seq.items()}


def predict_gru(model, s):
    model.eval()
    with torch.no_grad():
        n = len(s["cat"])
        return np.concatenate([torch.sigmoid(model({k: v[i:i + 2048] for k, v in s.items()})).numpy()
                               for i in range(0, n, 2048)])


def fit_gru(seq, y, train, val, use_merchant=False, seed=0, epochs=8, lr=2e-3, batch=256):
    """Plain binary cross-entropy with no resampling, so the outputs stay on the scale of the base rate (see DS 01/10)."""
    torch.manual_seed(seed)
    gen = np.random.default_rng(seed)
    model = EventGRU(use_merchant)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    str_, sva, ytr = take(seq, train), take(seq, val), torch.as_tensor(y[train], dtype=torch.float32)
    best, best_state = -1.0, None
    for _ in range(epochs):
        model.train()
        order = gen.permutation(len(ytr))
        for i in range(0, len(order), batch):
            b = torch.as_tensor(order[i:i + batch])
            loss = nn.functional.binary_cross_entropy_with_logits(model({k: v[b] for k, v in str_.items()}), ytr[b])
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        ap = average_precision_score(y[val], predict_gru(model, sva))
        if ap > best:
            best, best_state = ap, {k: v.clone() for k, v in model.state_dict().items()}
    model.load_state_dict(best_state)
    return lambda mask: predict_gru(model, take(seq, mask))


def merchant_risk(meta, y, train):
    """Target encoding: fraud rate per merchant on the training rows, shrunk towards the base rate."""
    base = y[train].mean()
    grouped = pd.DataFrame({"m": meta.merchant.to_numpy()[train], "y": y[train]}).groupby("m").y.agg(["sum", "count"])
    risk = (grouped["sum"] + 20 * base) / (grouped["count"] + 20)
    return meta.merchant.map(risk).fillna(base).to_numpy()


# %% Measures
def pr_auc(y, p):
    return float(average_precision_score(y, p))


def boot_diff(y, a, b, seed=SEED, n=200):
    """Paired bootstrap over scored charges: PR-AUC of a minus PR-AUC of b, with a 90% interval."""
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(n):
        s = rng.integers(0, len(y), len(y))
        if y[s].sum():
            d.append(pr_auc(y[s], a[s]) - pr_auc(y[s], b[s]))
    return float(np.mean(d)), float(np.quantile(d, .05)), float(np.quantile(d, .95))


def boot_ci(y, p, seed=SEED, n=200):
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(n):
        s = rng.integers(0, len(y), len(y))
        if y[s].sum():
            v.append(pr_auc(y[s], p[s]))
    return float(np.quantile(v, .05)), float(np.quantile(v, .95))


def event_costs(y, amount, block):
    """Euros per scored charge. A missed fraud loses a share of its amount plus the fee; a blocked good charge costs friction."""
    return np.where(y == 1, np.where(block, 0.0, LOSS_SHARE * amount + CB_FEE), np.where(block, FP_COST, 0.0))


def cost_per_1000(y, amount, block):
    return float(event_costs(y, amount, block).mean() * 1000)


def psi(reference, current, bins=10):
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        edges = np.array([reference.min() - 1, reference.min() + .5, reference.max() + 1])
    r = np.histogram(np.clip(reference, edges[0], edges[-1]), edges)[0] / len(reference)
    c = np.histogram(np.clip(current, edges[0], edges[-1]), edges)[0] / len(current)
    r, c = np.clip(r, 1e-4, None), np.clip(c, 1e-4, None)
    return float(((c - r) * np.log(c / r)).sum())


def verdict(mean, lo, hi, a, b):
    if lo > 0:
        return f"{a} ahead of {b}"
    if hi < 0:
        return f"{b} ahead of {a}"
    return f"no clear winner between {a} and {b}: the interval covers zero"


# %% The whole lab
def checks(ev, x, seq, meta, delay_median):
    """Invariants the rest of the lab relies on."""
    fraud, day, delay = meta.fraud.to_numpy(), meta.day.to_numpy(), meta.delay.to_numpy()
    assert TRAIN_END < VAL_END < TEST_END < DRIFT_END < DAYS
    assert ev.groupby("customer").t.apply(lambda s: s.is_monotonic_increasing).all()
    assert (known_labels(fraud, day, delay, 240) <= fraud).all(), "a label cannot be known without being true"
    assert (known_labels(fraud, day, delay, 10 ** 6) == fraud).all(), "every chargeback eventually arrives here"
    assert (seq["amount"][:, -1] > 0).all(), "left padding must leave the scored charge in the last step"
    # No look-ahead: dropping every later charge must not change a customer's features.
    cust = int(meta.customer.iloc[len(meta) // 2])
    g = ev[ev.customer == cust]
    cut = g.index[len(g) // 2]
    full, short = customer_features(g), customer_features(g.loc[:cut])
    assert len(short) and full.loc[short.index].equals(short[full.columns]), "features looked ahead"
    assert abs(pr_auc(fraud, np.random.default_rng(0).random(len(fraud))) - fraud.mean()) < 5 * fraud.mean()


def compare(ev, x, meta, seq, seed):
    """Train on days before TRAIN_END with final labels, tune on the next window, test on the one after."""
    y, d = meta.fraud.to_numpy(), meta.day.to_numpy()
    tr, va, te = d < TRAIN_END, (d >= TRAIN_END) & (d < VAL_END), (d >= VAL_END) & (d < TEST_END)
    models = {"totals": TOTALS, "velocity": VELOCITY, "oracle": ORACLE}
    scorers = {n: fit_boost(x[tr], y[tr], c, seed=seed) for n, c in models.items()}
    gru = fit_gru(seq, y, tr, va, seed=seed)
    return (tr, va, te), scorers, gru


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--seed", type=int, default=SEED)
    ap_.add_argument("--seeds", type=int, default=3, help="generated datasets for the repeat at the end of section 2")
    ap_.add_argument("--delay-median", type=float, default=28.0, help="median days from fraud to chargeback")
    ap_.add_argument("--drift", choices=["slow", "none"], default="slow")
    ap_.add_argument("--epochs", type=int, default=8)
    args = ap_.parse_args()
    torch.set_num_threads(4)
    start = time.time()

    # %% 0. The data
    ev = make_events(args.seed, args.drift, args.delay_median)
    x, meta = build_table(ev)
    seq = build_sequences(ev, x.index.to_numpy())
    checks(ev, x, seq, meta, args.delay_median)
    y, d, amount = meta.fraud.to_numpy(), meta.day.to_numpy(), meta.amount.to_numpy()
    print("Generated card data, not real. Every number describes this generator and these assumptions.")
    print(f"{len(ev):,} charges, {CUSTOMERS:,} customers, {DAYS} days; {len(x):,} scored (amount >= {SCORE_FROM:.0f}); "
          f"{int(y.sum())} frauds, base rate {y.mean():.3%}")
    print(f"split in days: train <{TRAIN_END}, validation <{VAL_END}, test <{TEST_END}, drift <{DRIFT_END}, retrain test <{DAYS}\n")

    (tr, va, te), scorers, gru = compare(ev, x, meta, seq, args.seed)
    p_val = {n: s(x[va]) for n, s in scorers.items()} | {"gru": gru(va)}
    p_te = {n: s(x[te]) for n, s in scorers.items()} | {"gru": gru(te)}
    yte, yva = y[te], y[va]

    # %% 1. Accuracy against PR-AUC at the real base rate
    print("1. What a metric says at the real base rate (test days, velocity aggregates)")
    p = p_te["velocity"]
    print(f"   always approve: accuracy {1 - yte.mean():.4f}, frauds caught 0")
    print(f"   model at 0.5:   accuracy {((p >= .5) == yte).mean():.4f}, frauds caught {int(((p >= .5) & (yte == 1)).sum())} of {int(yte.sum())}")
    rng = np.random.default_rng(args.seed)
    pos, neg = np.flatnonzero(yte == 1), np.flatnonzero(yte == 0)
    balanced = np.r_[pos, rng.choice(neg, len(pos), replace=False)]
    print(f"   PR-AUC at base rate {yte.mean():.3%}: {pr_auc(yte, p):.3f}  (random ranking scores the base rate)")
    print(f"   PR-AUC on a 50/50 rebalanced test set: {pr_auc(yte[balanced], p[balanced]):.3f}  (the same model, an easier question)\n")

    # %% 2. Aggregates against the GRU
    print("2. Same time split, final labels, behaviour only (no merchant IDs). PR-AUC on test days with a 90% bootstrap interval")
    labels = {"totals": "boosting on totals, 30-day counts and sums", "velocity": "boosting on velocity windows and last 3 events",
              "oracle": "velocity plus the planted rule as a feature", "gru": "GRU over the last 12 event embeddings"}
    for n in labels:
        lo, hi = boot_ci(yte, p_te[n])
        print(f"   {labels[n]:48s} {pr_auc(yte, p_te[n]):.3f}  [{lo:.3f}, {hi:.3f}]")
    for a, b in (("gru", "totals"), ("gru", "velocity"), ("gru", "oracle")):
        m, lo, hi = boot_diff(yte, p_te[a], p_te[b])
        print(f"   {a} minus {b:9s} {m:+.3f} [{lo:+.3f}, {hi:+.3f}]  {verdict(m, lo, hi, a, b)}")
    order_rng = np.random.default_rng(args.seed)
    shuffled = {k: v.copy() for k, v in seq.items()}
    for row in np.flatnonzero(te):              # scramble each window's order, keeping the scored charge last
        perm = np.r_[order_rng.permutation(SEQ_LEN - 1), SEQ_LEN - 1]
        for k in shuffled:
            shuffled[k][row] = seq[k][row][perm]
    model_input = take(shuffled, te)
    print("   GRU with each test window's order scrambled: ", end="")
    gru_model = gru.__closure__[0].cell_contents
    print(f"{pr_auc(yte, predict_gru(gru_model, model_input)):.3f}  (the same charges, the order gone)")
    if args.seeds > 1:
        rows = [{"data seed": args.seed, **{n: pr_auc(yte, p_te[n]) for n in labels}}]
        for extra in range(1, args.seeds):
            s = args.seed + extra
            ev2 = make_events(s, args.drift, args.delay_median)
            x2, meta2 = build_table(ev2)
            seq2 = build_sequences(ev2, x2.index.to_numpy())
            (_, _, te2), scorers2, gru2 = compare(ev2, x2, meta2, seq2, s)
            y2 = meta2.fraud.to_numpy()[te2]
            rows.append({"data seed": s, **{n: pr_auc(y2, sc(x2[te2])) for n, sc in scorers2.items()}, "gru": pr_auc(y2, gru2(te2))})
        print("   the same comparison on other generated datasets, PR-AUC")
        print(pd.DataFrame(rows).round(3).to_string(index=False, col_space=8))
    print()

    # %% 3. A random split against a time split
    print("3. Random split against time split, days before", VAL_END, "(merchant fraud rate and merchant embeddings allowed)")
    print("   Fraud moves between a few merchants each month, so merchant history is a strong signal inside a month and stale after it.")
    pool = np.flatnonzero(d < VAL_END)
    rng = np.random.default_rng(args.seed)
    shuffled_pool = rng.permutation(pool)
    cut = int(.8 * len(pool))
    rtr, rho = np.zeros(len(d), bool), np.zeros(len(d), bool)
    rtr[shuffled_pool[:cut]], rho[shuffled_pool[cut:]] = True, True
    ttr = d < VAL_END
    columns = VELOCITY + ["merchant_risk"]
    xr = x.assign(merchant_risk=merchant_risk(meta, y, rtr))
    xt = x.assign(merchant_risk=merchant_risk(meta, y, ttr))
    random_boost = fit_boost(xr[rtr], y[rtr], columns, seed=args.seed)
    time_boost = fit_boost(xt[ttr], y[ttr], columns, seed=args.seed)
    plain_val = np.zeros(len(d), bool)
    inner = shuffled_pool[int(.9 * cut):cut]
    plain_val[inner] = True
    rtr_gru = rtr & ~plain_val
    random_gru = fit_gru(seq, y, rtr_gru, plain_val, use_merchant=True, seed=args.seed, epochs=args.epochs)
    time_gru = fit_gru(seq, y, d < TRAIN_END, va, use_merchant=True, seed=args.seed, epochs=args.epochs)
    table = [("boosting, velocity + merchant rate", pr_auc(y[rho], random_boost(xr[rho])), pr_auc(yte, random_boost(xr[te])), pr_auc(yte, time_boost(xt[te]))),
             ("GRU + merchant embedding", pr_auc(y[rho], random_gru(rho)), pr_auc(yte, random_gru(te)), pr_auc(yte, time_gru(te)))]
    print(f"   {'':36s} {'random holdout':>15s} {'same model, later days':>23s} {'trained by time, later days':>28s}")
    for name, a, b, c in table:
        print(f"   {name:36s} {a:15.3f} {b:23.3f} {c:28.3f}")
    print(f"   without any merchant signal, velocity aggregates scored {pr_auc(yte, p_te['velocity']):.3f} and the GRU {pr_auc(yte, p_te['gru']):.3f} on those later days\n")

    # %% 4. Late labels
    print(f"4. Labels arrive late: median {args.delay_median:.0f} days to a chargeback, standing on day {VAL_END}")
    delay = meta.delay.to_numpy()
    seen = known_labels(y, d, delay, VAL_END)
    print("   days before today    charges  true fraud rate  rate known today  frauds not yet reported")
    for lo, hi in ((0, 15), (15, 30), (30, 60), (60, 90), (90, 120), (120, 240)):
        m = (d >= VAL_END - hi) & (d < VAL_END - lo)
        print(f"   {lo:3d} to {hi:3d}          {m.sum():8d}  {y[m].mean():14.3%}  {seen[m].mean():16.3%}  {int(y[m].sum() - seen[m].sum()):23d}")
    late = delay[y == 1]
    print(f"   chargebacks later than {MATURITY_DAYS} days: {np.mean(late > MATURITY_DAYS):.1%} of frauds, an assumption you can move with --delay-median")
    # Training on those labels: treat unreported as clean, or leave out what hasn't matured.
    known_tr = d < VAL_END
    mature_tr = d < VAL_END - MATURITY_DAYS
    delay_rows = []
    for name, mask, labels_used in (("hindsight, final labels (impossible live)", known_tr, y),
                                    ("all days, unreported counted as clean", known_tr, seen),
                                    (f"only days older than {MATURITY_DAYS} days", mature_tr, seen)):
        boost = fit_boost(x[mask], labels_used[mask], VELOCITY, seed=args.seed)
        window = np.flatnonzero(mask)
        cut_val = window[d[window] >= np.quantile(d[window], .8)]
        vmask = np.zeros(len(d), bool)
        vmask[cut_val] = True
        g = fit_gru(seq, labels_used, mask & ~vmask, vmask, seed=args.seed, epochs=args.epochs)
        delay_rows.append((name, int(labels_used[mask].sum()), pr_auc(yte, boost(x[te])), pr_auc(yte, g(te))))
    print(f"   {'training labels':44s} {'frauds in train':>16s} {'boosting':>9s} {'GRU':>7s}   PR-AUC on test days, judged on final labels")
    for name, n, a, b in delay_rows:
        print(f"   {name:44s} {n:16d} {a:9.3f} {b:7.3f}")
    as_of = TEST_END
    s_seen = known_labels(y[te], d[te], delay[te], as_of)
    pv = p_te["velocity"]
    t_blocks = pv >= np.quantile(pv, .99)
    print(f"   Judging the test days as of day {as_of}, with the labels known by then:")
    print(f"     frauds visible {int(s_seen.sum())} of {int(yte.sum())};  PR-AUC looks like {pr_auc(s_seen, pv):.3f}, truly {pr_auc(yte, pv):.3f};  "
          f"fraud losses look like {cost_per_1000(s_seen, amount[te], t_blocks):,.0f} per 1,000, truly {cost_per_1000(yte, amount[te], t_blocks):,.0f}\n")

    # %% 5. A threshold from prices
    print(f"5. A threshold from prices. Assumed: blocking a good charge costs {FP_COST:.0f}; a missed fraud costs {LOSS_SHARE:.0%} of its amount plus {CB_FEE:.0f}")
    print(f"   Calibration on validation days: mean predicted vs rate, velocity {p_val['velocity'].mean():.4f} vs {yva.mean():.4f}, GRU {p_val['gru'].mean():.4f} vs {yva.mean():.4f}")
    a_va, a_te = amount[va], amount[te]
    grid = np.r_[1e-4, np.geomspace(1e-3, .95, 60)]
    print(f"   {'model and rule':42s} {'threshold':>10s} {'blocked':>8s} {'caught':>7s} {'cost per 1,000':>15s}")
    print(f"   {'block nothing':42s} {'':>10s} {0.0:8.2%} {0.0:7.1%} {cost_per_1000(yte, a_te, np.zeros(len(yte), bool)):15,.0f}")
    costs = {}
    for name in ("velocity", "gru"):
        pv, pt = p_val[name], p_te[name]
        by_cost = grid[np.argmin([cost_per_1000(yva, a_va, pv >= t) for t in grid])]
        f1 = [2 * ((pv >= t) & (yva == 1)).sum() / max((pv >= t).sum() + yva.sum(), 1) for t in grid]
        by_f1 = grid[int(np.argmax(f1))]
        amount_aware = pt * (LOSS_SHARE * a_te + CB_FEE) >= (1 - pt) * FP_COST
        for rule, block, t in (("at 0.5", pt >= .5, .5), ("best F1 on validation", pt >= by_f1, by_f1),
                               ("cheapest on validation", pt >= by_cost, by_cost), ("expected cost, charge by charge", amount_aware, None)):
            c = cost_per_1000(yte, a_te, block)
            costs[name, rule] = c
            shown = "per charge" if t is None else f"{t:.4f}"
            print(f"   {name + ', ' + rule:42s} {shown:>10s} {block.mean():8.2%} {block[yte == 1].mean():7.1%} {c:15,.0f}")
    none = cost_per_1000(yte, a_te, np.zeros(len(yte), bool))
    assert abs(none - (LOSS_SHARE * a_te[yte == 1] + CB_FEE).sum() / len(yte) * 1000) < 1e-6
    print()

    # %% 6. Drift
    label = "the planted pattern changes" if args.drift == "slow" else "no change (--drift none)"
    print(f"6. Drift from day {TEST_END}: {label}. Tests and the cash-out now run hours apart, through other categories")
    dr = (d >= TEST_END) & (d < DRIFT_END)
    ydr = y[dr]
    pd_dr = {n: s(x[dr]) for n, s in scorers.items()} | {"gru": gru(dr)}
    print(f"   {'model':10s} {'test days':>10s} {'drift days':>11s} {'frauds caught at the cheapest validation threshold':>52s}")
    for name in labels:
        pv = p_val[name]
        t = grid[np.argmin([cost_per_1000(yva, a_va, pv >= g) for g in grid])]
        before, after = (p_te[name] >= t)[yte == 1].mean(), (pd_dr[name] >= t)[ydr == 1].mean()
        print(f"   {name:10s} {pr_auc(yte, p_te[name]):10.3f} {pr_auc(ydr, pd_dr[name]):11.3f} {before:26.1%} before, {after:.1%} after")
    print("   What a monitor sees, reference window the validation days:")
    for name, col in (("charge amount", "amount"), ("30-day spend", "sum_30d"), ("small online charges, 1h", "small_online_1h"), ("small online charges, 24h", "small_online_24h")):
        print(f"     PSI {name:28s} {psi(x[va][col].to_numpy(), x[dr][col].to_numpy()):.3f}")
    print(f"     PSI velocity model score         {psi(p_val['velocity'], pd_dr['velocity']):.3f}")
    print(f"     PSI GRU score                    {psi(p_val['gru'], pd_dr['gru']):.3f}")
    print("     PSI between test days and validation days, for scale: "
          f"velocity score {psi(p_val['velocity'], p_te['velocity']):.3f}, GRU score {psi(p_val['gru'], p_te['gru']):.3f}")
    delay_dr, day_dr = delay[dr], d[dr]
    pv = pd_dr["velocity"]
    print("   What the label feed sees, velocity model, drift days so far (median delay as above):")
    print("     as of day   frauds reported / truly happened    PR-AUC on reported labels / on final labels")
    for as_of in (310, 320, 330, 345, 360, 420):
        so_far = day_dr < min(as_of, DRIFT_END)
        known = known_labels(ydr[so_far], day_dr[so_far], delay_dr[so_far], as_of)
        shown = f"{pr_auc(known, pv[so_far]):.3f}" if known.sum() else "no labels yet"
        print(f"     {as_of:9d}   {int(known.sum()):7d} / {int(ydr[so_far].sum()):<7d} {shown:>24s} / {pr_auc(ydr[so_far], pv[so_far]):.3f}")
    # Retraining on day DRIFT_END, judged on the following days.
    after = d >= DRIFT_END
    yaf = y[after]
    seen_now = known_labels(y, d, delay, DRIFT_END)
    rows = []
    for name, mask, used in (("no retrain, the model from day 180", None, None),
                             (f"retrain on labels older than {MATURITY_DAYS} days", d < DRIFT_END - MATURITY_DAYS, seen_now),
                             ("retrain on everything reported so far", d < DRIFT_END, seen_now)):
        if mask is None:
            rows.append((name, int(y[tr].sum()), 0, pr_auc(yaf, scorers["velocity"](x[after])), pr_auc(yaf, gru(after))))
            continue
        boost = fit_boost(x[mask], used[mask], VELOCITY, seed=args.seed)
        window = np.flatnonzero(mask)
        cut_val = window[d[window] >= np.quantile(d[window], .8)]
        vmask = np.zeros(len(d), bool)
        vmask[cut_val] = True
        g = fit_gru(seq, used, mask & ~vmask, vmask, seed=args.seed, epochs=args.epochs)
        new_pattern = int(used[mask & (d >= TEST_END)].sum())
        rows.append((name, int(used[mask].sum()), new_pattern, pr_auc(yaf, boost(x[after])), pr_auc(yaf, g(after))))
    print(f"   Retraining on day {DRIFT_END}, PR-AUC on days {DRIFT_END} to {DAYS}, judged on final labels:")
    print(f"     {'':42s} {'frauds in train':>16s} {'of the new pattern':>19s} {'boosting':>9s} {'GRU':>7s}")
    for name, n, k, a, b in rows:
        print(f"     {name:42s} {n:16d} {k:19d} {a:9.3f} {b:7.3f}")

    print(f"\nRuntime {time.time() - start:.0f} s. Results describe this generated data, these prices and these seeds, not fraud in general.")


if __name__ == "__main__":
    main()
