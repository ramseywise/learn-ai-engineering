# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scipy", "scikit-learn", "imbalanced-learn", "xlrd", "matplotlib"]
# ///
"""Experiments for notes/14-learning-from-corrections.md: labels, noise, active learning and silent acceptance.

Run from this folder:
    uv run learning_from_corrections.py

Invoices are generated (see invoices.py), so the truth is known and the clerk is simulated. Active learning is
also run on the real credit file, whose labels are nobody's simulation. Takes about ten minutes. Writes two
figures to ../../sources/images/.
"""
# %% Setup
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "credit-default-lab"))
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd
from dataclasses import replace
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import cohen_kappa_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import credit_default_lab as lab
import invoices as inv
from invoices import FEATURES, PAY, REJECT, REVIEW, Prices

pd.set_option("display.width", 170, "display.max_columns", None, "display.max_rows", 200)
pd.options.display.float_format = "{:.3f}".format
C = Prices()
LO, HI = inv.thresholds(C)

# %% Agreement: two annotators, a rare class
rng = np.random.default_rng(0)
d = inv.make_invoices(20_000, 100)
y = d.y.to_numpy()
blind = d.bank_changed.to_numpy() == 1


def annotate(y, recall, false_alarm, rng):
    return np.where(y == 1, rng.random(len(y)) < recall, rng.random(len(y)) < false_alarm).astype(int)


a_good = annotate(y, 0.8, 0.02, rng)
b_good = annotate(y, 0.8, 0.02, rng)
lazy = annotate(y, 0.05, 0.01, rng)
a_blind = np.where(blind & (y == 1), 0, annotate(y, 0.95, 0.01, rng))
b_blind = np.where(blind & (y == 1), 0, annotate(y, 0.95, 0.01, rng))
print("Pairs of annotators on 20,000 invoices")
rows = []
for name, a, b in [("two careful, independent", a_good, b_good), ("careful and one who rarely flags", a_good, lazy),
                   ("two careful, same blind spot", a_blind, b_blind)]:
    rows.append({"pair": name, "raw_agreement": (a == b).mean(), "kappa": cohen_kappa_score(a, b), "recall_a": a[y == 1].mean(), "recall_b": b[y == 1].mean(),
                 "recall_on_blind_spot": a[(y == 1) & blind].mean()})
print(pd.DataFrame(rows).to_string(index=False))
print(f"Problems in the blind spot: {((y == 1) & blind).sum() / (y == 1).sum():.3f} of all problems")
rows = []
for n in (200, 500, 2000):
    ks = [cohen_kappa_score(a_good[i], b_good[i]) for i in (rng.integers(0, len(y), n) for _ in range(500))]
    rows.append({"double_labelled": n, "problems_expected": n * y.mean(), "kappa_5th": np.quantile(ks, .05), "kappa_95th": np.quantile(ks, .95)})
print("How far kappa moves on a sample of double-labelled invoices")
print(pd.DataFrame(rows).to_string(index=False))


# %% Label noise: what it does to a model, and what confident learning finds
def noisy_labels(df, kind, rng):
    """Return labels as a person recorded them. Three ways of being wrong."""
    y = df.y.to_numpy()
    u = rng.random(len(y))
    if kind == "none":
        return y.copy()
    if kind == "symmetric 5%":
        return np.where(u < 0.05, 1 - y, y)
    if kind == "misses 30% of problems":
        return np.where(y == 1, (u >= 0.30).astype(int), (u < 0.005).astype(int))
    if kind == "misses small invoices":  # the same overall miss rate, but it depends on the invoice
        miss = df.log_amount.to_numpy() < np.quantile(df.log_amount[df.y == 1], 0.40)
        return np.where(y == 1, ((u >= 0.75) | ~miss).astype(int), (u < 0.005).astype(int))
    raise ValueError(kind)


def out_of_fold(x, y, seed, folds=4):
    """Predicted probabilities for rows the model did not train on, as confident learning requires."""
    p = np.zeros(len(y))
    for a, b in StratifiedKFold(folds, shuffle=True, random_state=seed).split(x, y):
        p[b] = inv.score(inv.fit_boosted(x.iloc[a], y[a], seed), x.iloc[b])
    return p


def confident_flags(y_noisy, p):
    """Binary confident joint. A class's threshold is its mean self-confidence; collisions go to the larger probability."""
    t1, t0 = p[y_noisy == 1].mean(), (1 - p[y_noisy == 0]).mean()
    conf1, conf0 = p >= t1, (1 - p) >= t0
    says1 = conf1 & (~conf0 | (p >= 0.5))
    says0 = conf0 & (~conf1 | (p < 0.5))
    return (y_noisy == 0) & says1, (y_noisy == 1) & says0, t0, t1


rows, flagrows = [], []
kinds = ["none", "symmetric 5%", "misses 30% of problems", "misses small invoices"]
for s in range(5):
    tr, va, te = inv.make_invoices(20_000, 2000 + s), inv.make_invoices(5_000, 2100 + s), inv.make_invoices(50_000, 2200 + s)
    yt = te.y.to_numpy()
    rng = np.random.default_rng(s)
    for kind in kinds:
        ytr, yva = noisy_labels(tr, kind, rng), noisy_labels(va, kind, rng)
        m = inv.fit_boosted(tr[FEATURES], ytr, s)
        rv, rt = inv.score(m, va[FEATURES]), inv.score(m, te[FEATURES])
        noisy_cal, clean_cal = inv.platt(rv, yva)(rt), inv.platt(rv, va.y)(rt)
        rn, rc = inv.report(yt, noisy_cal, inv.route(noisy_cal, LO, HI)), inv.report(yt, clean_cal, inv.route(clean_cal, LO, HI))
        rows.append({"labels": kind, "auc": roc_auc_score(yt, rt), "mean_score": noisy_cal.mean(), "paid_noisy_cal": rn["paid"], "error_paid_noisy_cal": rn["error_paid"],
                     "cost_noisy_cal": rn["cost"], "paid_clean_cal": rc["paid"], "error_paid_clean_cal": rc["error_paid"], "cost_clean_cal": rc["cost"]})
        if kind == "none":
            continue
        ytrue = tr.y.to_numpy()
        p = out_of_fold(tr[FEATURES], ytr, s)
        missed, spurious, t0, t1 = confident_flags(ytr, p)
        wrong = ytr != ytrue
        flag = missed | spurious
        base = ((p >= 0.5).astype(int) != ytr)
        est = (missed.sum() / (missed.sum() + (ytr == 0).sum() - missed.sum())) * (ytr == 0).sum() / ytr.sum()
        # Three uses of the flags, all calibrated on the same clean validation set
        keep = ~flag
        mp = inv.fit_boosted(tr[FEATURES][keep], ytr[keep], s)
        clerk = np.where(ytrue == 1, rng.random(len(ytrue)) < C.catch, rng.random(len(ytrue)) < C.false_alarm).astype(int)
        y_fix = np.where(flag, clerk, ytr)
        mf = inv.fit_boosted(tr[FEATURES], y_fix, s)
        mc = inv.fit_boosted(tr[FEATURES], ytrue, s)
        res = {}
        for tag, model in [("kept", m), ("pruned", mp), ("clerk_fixed", mf), ("all_true", mc)]:
            q = inv.platt(inv.score(model, va[FEATURES]), va.y)(inv.score(model, te[FEATURES]))
            res[f"auc_{tag}"] = roc_auc_score(yt, q)
            res[f"cost_{tag}"] = inv.report(yt, q, inv.route(q, LO, HI))["cost"]
        flagrows.append({"labels": kind, "share_wrong": wrong.mean(), "flagged": flag.mean(), "precision": wrong[flag].mean(), "recall": flag[wrong].mean(),
                         "argmax_flagged": base.mean(), "argmax_precision": wrong[base].mean(), "argmax_recall": base[wrong].mean(),
                         "missed_true": ((ytr == 0) & (ytrue == 1)).mean(), "missed_found_estimate": missed.mean(), "t_problem": t1, "t_good": t0, **res})
print("\nNoisy labels, 20,000 training rows, mean of 5 seeds. All judged on true outcomes")
print(pd.DataFrame(rows).groupby("labels", sort=False).mean(numeric_only=True).to_string())
flagrows = pd.DataFrame(flagrows).groupby("labels", sort=False).mean(numeric_only=True)
print("\nConfident learning against 'prediction disagrees with label'")
print(flagrows[["share_wrong", "flagged", "precision", "recall", "argmax_flagged", "argmax_precision", "argmax_recall", "t_problem", "t_good"]].to_string())
print("\nRetraining after the flags; all calibrated on 5,000 true labels")
print(flagrows[[c for c in flagrows if c.startswith(("auc_", "cost_"))]].to_string())


# %% Weak supervision: rules instead of hand labels
def labelling_functions(x):
    """Each rule votes 1 (problem), 0 (good) or -1 (abstain)."""
    v = {
        "bank details changed": np.where(x.bank_changed == 1, 1, -1),
        "price far from the order": np.where(x.price_diff > 0.15, 1, -1),
        "near-duplicate": np.where(x.dup_sim > 0.5, 1, -1),
        "no order and wrong quantity": np.where((x.po_match == 0) & (x.qty_mismatch == 1), 1, -1),
        "supplier with a poor record": np.where(x.prior_issue_rate > 0.08, 1, -1),
        "order matches closely": np.where((x.po_match == 1) & (x.price_diff < 0.01) & (x.bank_changed == 0), 0, -1),
        "long-standing supplier, no duplicate": np.where((x.tenure_months > 24) & (x.dup_sim < 0.1), 0, -1),
        "clean extraction, right quantity": np.where((x.extract_conf > 0.95) & (x.qty_mismatch == 0), 0, -1),
    }
    return pd.DataFrame(v)


def majority(votes):
    pos, neg = (votes == 1).sum(axis=1), (votes == 0).sum(axis=1)
    return np.where(pos + neg == 0, np.nan, np.where(pos == neg, 0.5, (pos > neg).astype(float)))


def dawid_skene(votes, rounds=30):
    """Estimate each rule's reliability from agreements alone, with no true labels, by EM on class-conditional votes."""
    v = votes.to_numpy()
    mv = majority(votes)
    q = np.where(np.isnan(mv), 0.5, mv)
    for _ in range(rounds):
        prior = q.mean()
        log1, log0 = np.full(len(q), np.log(prior)), np.full(len(q), np.log(1 - prior))
        for j in range(v.shape[1]):
            for val in (-1, 0, 1):
                hit = v[:, j] == val
                p1 = (q[hit].sum() + 1) / (q.sum() + 3)
                p0 = ((1 - q)[hit].sum() + 1) / ((1 - q).sum() + 3)
                log1[hit] += np.log(p1)
                log0[hit] += np.log(p0)
        q = 1 / (1 + np.exp(log0 - log1))
    return q


pool = inv.make_invoices(20_000, 3000)
votes = labelling_functions(pool)
lf = []
for name in votes:
    fired = votes[name] != -1
    lf.append({"rule": name, "votes": "problem" if votes[name][fired].iloc[0] == 1 else "good", "fires_on": fired.mean(),
               "accuracy": (votes[name][fired] == pool.y[fired].to_numpy()).mean()})
print("\nLabelling functions on 20,000 invoices")
print(pd.DataFrame(lf).to_string(index=False))
print(f"Mean votes per invoice {(votes != -1).sum(axis=1).mean():.2f}; share with no vote {((votes != -1).sum(axis=1) == 0).mean():.3f}")


def train_soft(x, q, seed):
    """Train on probabilistic labels: each row appears twice, weighted by its probability of each class."""
    keep = ~np.isnan(q)
    xx = pd.concat([x[keep], x[keep]])
    yy = np.r_[np.ones(keep.sum()), np.zeros(keep.sum())]
    w = np.r_[q[keep], 1 - q[keep]]
    use = w > 0
    return inv.fit_boosted(xx[use], yy[use], seed, weights=w[use])


rows = []
for s in range(5):
    pool, va, te = inv.make_invoices(20_000, 3000 + s), inv.make_invoices(5_000, 3100 + s), inv.make_invoices(50_000, 3200 + s)
    yt = te.y.to_numpy()
    v = labelling_functions(pool)
    rng = np.random.default_rng(s)
    v_dup = v.copy()
    for k in range(4):  # a rule copied four more times: correlated voters
        v_dup[f"copy {k}"] = v["clean extraction, right quantity"]
    methods = {
        "rules: majority vote": train_soft(pool[FEATURES], majority(v), s),
        "rules: learned weights": train_soft(pool[FEATURES], dawid_skene(v), s),
        "rules + 4 copies: majority vote": train_soft(pool[FEATURES], majority(v_dup), s),
        "rules + 4 copies: learned weights": train_soft(pool[FEATURES], dawid_skene(v_dup), s),
    }
    for n in (200, 1000, 5000):
        i = rng.choice(len(pool), n, replace=False)
        clerk = np.where(pool.y.to_numpy()[i] == 1, rng.random(n) < C.catch, rng.random(n) < C.false_alarm).astype(int)
        methods[f"{n:,} clerk labels"] = inv.fit_boosted(pool[FEATURES].iloc[i], clerk, s)
    q_dep = dawid_skene(v)
    for name, m in methods.items():
        q = inv.platt(inv.score(m, va[FEATURES]), va.y)(inv.score(m, te[FEATURES]))
        rows.append({"source": name, "auc": roc_auc_score(yt, q), "cost_priced": inv.report(yt, q, inv.route(q, LO, HI))["cost"]})
    rows.append({"source": "label accuracy, majority", "auc": np.nan, "cost_priced": np.nan, "label_acc": np.nanmean(np.round(np.nan_to_num(majority(v), nan=0.5)) == pool.y)})
    rows.append({"source": "label auc, learned weights", "auc": roc_auc_score(pool.y, q_dep), "cost_priced": np.nan})
print("\nModels trained on each source of labels, calibrated on 5,000 true labels, mean of 5 seeds")
print(pd.DataFrame(rows).drop(columns="label_acc").groupby("source", sort=False).mean(numeric_only=True).to_string())


# %% Active learning: uncertainty against random, on both data sets
def make_logistic():
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=500))


def make_boosted(seed):
    return HistGradientBoostingClassifier(learning_rate=0.05, max_iter=100, max_leaf_nodes=8, early_stopping=False, random_state=seed)


def active_run(x_pool, y_pool, x_val, y_val, x_test, y_test, strategy, learner, seed, start=100, batch=100, stop=2000, miss=0.0, cost_prices=C):
    """Pool-based loop. Returns (labels, auc, priced cost after Platt on a random labelled set, share of problems labelled)."""
    rng = np.random.default_rng(seed)
    y_seen = np.where((y_pool == 1) & (rng.random(len(y_pool)) < miss), 0, y_pool)
    labelled = list(rng.choice(len(y_pool), start, replace=False))
    available = np.setdiff1d(np.arange(len(y_pool)), labelled)
    lo, hi = inv.thresholds(cost_prices)
    out = []
    while True:
        if y_seen[labelled].min() == y_seen[labelled].max():  # a batch of one class: take a random batch
            extra = rng.choice(available, batch, replace=False)
            labelled += list(extra)
            available = np.setdiff1d(available, extra)
            continue
        model = make_logistic() if learner == "logistic" else make_boosted(seed)
        model.fit(x_pool[labelled], y_seen[labelled])
        rt = model.predict_proba(x_test)[:, 1]
        q = inv.platt(model.predict_proba(x_val)[:, 1], y_val)(rt)
        out.append({"labels": len(labelled), "auc": roc_auc_score(y_test, rt), "cost": inv.report(y_test, q, inv.route(q, lo, hi), cost_prices)["cost"],
                    "problems": y_pool[labelled].mean()})
        if len(labelled) >= stop:
            return out
        p = model.predict_proba(x_pool[available])[:, 1]
        if strategy == "random":
            pick = rng.choice(len(available), batch, replace=False)
        elif strategy == "uncertainty":
            pick = np.argsort(np.abs(p - 0.5))[:batch]
        elif strategy == "highest score":  # what a queue of the riskiest items hands to people
            pick = np.argsort(-p)[:batch]
        labelled += list(available[pick])
        available = np.delete(available, pick)


CREDIT = Prices(pay_problem=3000.0, reject_good=600.0, review=60.0, catch=0.7, false_alarm=0.1)
raw = lab.load_credit()


def invoice_arrays(seed):
    a, b, c = inv.make_invoices(20_000, 4000 + seed), inv.make_invoices(2_000, 4100 + seed), inv.make_invoices(30_000, 4200 + seed)
    return (a[FEATURES].to_numpy(), a.y.to_numpy(), b[FEATURES].to_numpy(), b.y.to_numpy(), c[FEATURES].to_numpy(), c.y.to_numpy())


def credit_arrays(seed):
    a, b, c = lab.split(raw, seed=seed)
    return (lab.features(a).to_numpy(), a[lab.TARGET].to_numpy(), lab.features(b).to_numpy(), b[lab.TARGET].to_numpy(), lab.features(c).to_numpy(), c[lab.TARGET].to_numpy())


SETTINGS = [
    ("invoices", "logistic", 100, 0.0, 10), ("invoices", "boosted", 100, 0.0, 10), ("invoices", "boosted", 500, 0.0, 10), ("invoices", "boosted", 100, 0.3, 10),
    ("credit", "logistic", 100, 0.0, 10), ("credit", "boosted", 100, 0.0, 10), ("credit", "boosted", 500, 0.0, 10),
]
rows = []
for data, learner, batch, miss, seeds in SETTINGS:
    for s in range(seeds):
        arrays = invoice_arrays(s) if data == "invoices" else credit_arrays(s)
        prices = C if data == "invoices" else CREDIT
        for strategy in ("random", "uncertainty", "highest score"):
            for r in active_run(*arrays, strategy, learner, s, batch=batch, stop=2000, miss=miss, start=100 if batch == 100 else 500, cost_prices=prices):
                rows.append({"data": data, "learner": learner, "batch": batch, "miss": miss, "seed": s, "strategy": strategy, **r})
al = pd.DataFrame(rows)
print("\nActive learning, 10 seeds. Each row is at a label count; diff is strategy minus random, with seeds won of 10")
out = []
for (data, learner, batch, miss), g in al.groupby(["data", "learner", "batch", "miss"], sort=False):
    for n in (500, 1000, 2000):
        at = g[g.labels == n]
        if at.empty:
            continue
        wa = at.pivot(index="seed", columns="strategy", values="auc")
        wc = at.pivot(index="seed", columns="strategy", values="cost")
        row = {"data": data, "learner": learner, "batch": batch, "miss": miss, "labels": n, "auc_random": wa["random"].mean(), "auc_unc_diff": (wa["uncertainty"] - wa["random"]).mean(),
               "auc_wins": int((wa["uncertainty"] > wa["random"]).sum()), "cost_random": wc["random"].mean(), "cost_unc_diff": (wc["uncertainty"] - wc["random"]).mean(),
               "cost_wins": int((wc["uncertainty"] < wc["random"]).sum()), "auc_top_diff": (wa["highest score"] - wa["random"]).mean(),
               "problems_random": at[at.strategy == "random"].problems.mean(), "problems_unc": at[at.strategy == "uncertainty"].problems.mean()}
        out.append(row)
print(pd.DataFrame(out).to_string(index=False))


# %% Selection bias: what the corrections can see
def month(n, seed, m, cal, c=C, discover=0.1, new_pattern=0.0):
    """One month of invoices through the router. Returns the frame with what each party saw."""
    df = inv.make_invoices(n, seed, new_pattern=new_pattern)
    rng = np.random.default_rng(seed + 1)
    p = cal(inv.score(m, df[FEATURES]))
    df["p"] = p
    df["route"] = inv.route(p, LO, HI)
    y = df.y.to_numpy()
    df["clerk_rejects"] = np.where(y == 1, rng.random(n) < c.catch, rng.random(n) < c.false_alarm)
    df["discovered"] = rng.random(n) < discover  # a paid problem that later surfaces: a complaint, a chargeback
    df["final_reject"] = (df.route == REJECT) | ((df.route == REVIEW) & df.clerk_rejects)
    return df


tr, va = inv.make_invoices(30_000, 7000), inv.make_invoices(10_000, 7001)
m0 = inv.fit_boosted(tr[FEATURES], tr.y, 0)
cal0 = inv.platt(inv.score(m0, va[FEATURES]), va.y)
tiny = inv.make_invoices(2_000, 7002)
m_weak = inv.fit_boosted(tiny[FEATURES], tiny.y, 0)
cal_weak = inv.platt(inv.score(m_weak, va[FEATURES]), va.y)

rows = []
cases = [("strong model, clerk catch 0.9", m0, cal0, C), ("strong model, clerk catch 0.6", m0, cal0, replace(C, catch=0.6)), ("strong model, clerk catch 0.3", m0, cal0, replace(C, catch=0.3)),
         ("weak model, clerk catch 0.9", m_weak, cal_weak, C), ("weak model, clerk catch 0.6", m_weak, cal_weak, replace(C, catch=0.6))]
for name, model, cal, c in cases:
    df = month(50_000, 7100, model, cal, c)
    suggest = df.p >= inv.one_threshold()
    rev = df.route == REVIEW
    changed = (df.clerk_rejects != suggest)[rev]
    accepted = rev & ~df.clerk_rejects
    wrong_final = np.where(df.final_reject, df.y == 0, df.y == 1)
    rows.append({"case": name, "reviewed": rev.mean(), "correction_rate": changed.mean(), "problems_in_accepted": df.y[accepted].mean(), "error_paid": df.y[df.route == PAY].mean(), "final_error": wrong_final.mean()})
print("\nThe correction rate cannot tell a tired clerk from a good model")
print(pd.DataFrame(rows).to_string(index=False))

df = month(50_000, 7200, m0, cal0)
paid = df.route == PAY
accepted = (df.route == REVIEW) & ~df.clerk_rejects
wrong_final = np.where(df.final_reject, df.y == 0, df.y == 1)
print(f"\nOne month, strong model, 50,000 invoices. Share paid {paid.mean():.3f}, reviewed {(df.route == REVIEW).mean():.3f}, rejected {(df.route == REJECT).mean():.3f}")
print(f"Truth: error on paid {df.y[paid].mean():.4f}, problems among clerk-accepted {df.y[accepted].mean():.4f}, wrong final decisions {wrong_final.mean():.4f}")
print(f"Share of all problems that land in the paid route: {df.y[paid].sum() / df.y.sum():.3f}; in review: {df.y[df.route == REVIEW].sum() / df.y.sum():.3f}; in reject: {df.y[df.route == REJECT].sum() / df.y.sum():.3f}")

truth = {"paid": df.y[paid].mean(), "final": wrong_final.mean()}
y = df.y.to_numpy()
rows = []
n_paid, n_acc = paid.sum(), accepted.sum()
for rep in range(500):
    r = np.random.default_rng(rep)
    found = r.random(len(df)) < 0.1
    silent_est = (y[paid] & found[paid]).mean()
    # The dashboard: every clerk decision counts as truth, and silence counts as correct
    dash_final = ((y & found & paid).sum() + (df.route == REJECT).sum() * 0) / len(df)
    # Audit a random 1% of paid, 1% of accepted, 10% of auto-rejected, then reweight to the whole flow
    rates = np.where(paid, 0.01, np.where(accepted, 0.01, np.where(df.route == REJECT, 0.10, 0.0)))
    audited = r.random(len(df)) < rates
    sel_paid = audited & paid
    audit_paid = y[sel_paid].mean()
    same_clerk = r.random(len(df)) < C.catch
    audit_paid_clerk = (y[sel_paid] & same_clerk[sel_paid]).mean()
    decided = wrong_final.astype(float)
    ht = (decided[audited] / rates[audited]).sum() / len(df) + ((df.route == REVIEW) & df.clerk_rejects & (df.y == 0)).mean()
    rows.append({"silent_paid": silent_est, "audit_paid": audit_paid, "audit_paid_same_clerk": audit_paid_clerk, "dash_final": dash_final, "ht_final": ht, "n_audited": audited.mean() * len(df), "n_paid_audit": sel_paid.sum()})
est = pd.DataFrame(rows)
print(f"\nEstimates over 500 audit draws. True error on paid {truth['paid']:.4f}; true share of wrong final decisions {truth['final']:.4f}")
for col, label in [("silent_paid", "paid: silence counts as correct, 10% of problems surface"), ("audit_paid", "paid: random audit, careful auditor"), ("audit_paid_same_clerk", "paid: random audit, the same clerk"),
                   ("dash_final", "final: silence and acceptance count as correct"), ("ht_final", "final: audit strata reweighted")]:
    print(f"{label:62s} mean {est[col].mean():.4f}, 5th to 95th {est[col].quantile(.05):.4f} to {est[col].quantile(.95):.4f}")
print(f"Audit size: {est.n_audited.mean():.0f} invoices of 50,000, of which {est.n_paid_audit.mean():.0f} paid; {est.n_audited.mean() * C.review / 50_000:.3f} euros per invoice at the clerk's price")


# %% Sizing the audit
base, drifted = 0.013, 0.033
rows = []
for n in (100, 300, 1000, 3000):
    k = int(round(n * base))
    low = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
    high = stats.beta.ppf(0.975, k + 1, n - k)
    critical = stats.binom.ppf(0.95, n, base) + 1  # one-sided test against the baseline, at most 5% false alarms
    rows.append({"audited": n, "errors_expected": n * base, "ci_low": low, "ci_high": high, "zero_found_rule_of_3": 3 / n, "zero_found_exact_95": 1 - 0.05 ** (1 / n),
                 "false_alarm": stats.binom.sf(critical - 1, n, base), "power_at_drift": stats.binom.sf(critical - 1, n, drifted),
                 "euros_at_clerk_price": n * C.review})
print(f"\nAudit size, with error on paid at {base:.1%} and a drift to {drifted:.1%}")
print(pd.DataFrame(rows).to_string(index=False))
print(f"Normal-approximation size for 80% power, two-sided: {lab.sample_size_two_proportions(base, drifted)} per period")


# %% The loop: retraining from what the system saw, with a new fraud type from month 3
def labels_for(df, policy, audit_rate, rng):
    """Turn a month's routes into training rows and weights under one labelling policy."""
    y = df.y.to_numpy()
    paid, review, reject = df.route == PAY, df.route == REVIEW, df.route == REJECT
    found = (y == 1) & df.discovered.to_numpy() & paid.to_numpy()
    clerk = df.clerk_rejects.to_numpy().astype(int)
    if policy == "true labels":
        return np.ones(len(df), bool), y, np.ones(len(df))
    if policy == "silence is correct":
        label = np.where(review, clerk, np.where(reject, 1, found.astype(int)))
        return np.ones(len(df), bool), label, np.ones(len(df))
    if policy == "reviewed only":
        return review.to_numpy(), clerk, np.ones(len(df))
    if policy == "audit":
        audited = paid.to_numpy() & (rng.random(len(df)) < audit_rate)
        keep = review.to_numpy() | reject.to_numpy() | audited | found
        label = np.where(audited, y, np.where(review, clerk, np.where(reject, 1, found.astype(int))))
        weight = np.where(audited, 1 / audit_rate, 1.0)
        return keep, label, weight
    raise ValueError(policy)


def run_loop(policy, seed, audit_rate=0.05, months=8, n=10_000, start_drift=3, strength=0.35):
    rng = np.random.default_rng(seed)
    hist = inv.make_invoices(10_000, 8000 + seed)
    m = inv.fit_boosted(hist[FEATURES], hist.y, seed)
    vh = inv.make_invoices(3_000, 8100 + seed)
    cal = inv.platt(inv.score(m, vh[FEATURES]), vh.y)
    window = [(hist[FEATURES], hist.y.to_numpy(), np.ones(len(hist)))]
    rows = []
    for t in range(1, months + 1):
        np_t = strength if t >= start_drift else 0.0
        test = inv.make_invoices(30_000, 8500 + 100 * seed + t, new_pattern=np_t)
        q = cal(inv.score(m, test[FEATURES]))
        rep = inv.report(test.y.to_numpy(), q, inv.route(q, LO, HI))
        rows.append({"policy": policy, "seed": seed, "month": t, "paid": rep["paid"], "reviewed": rep["reviewed"], "error_paid": rep["error_paid"], "cost": rep["cost"], "auc": roc_auc_score(test.y, q),
                     "cost_with_audit": rep["cost"] + (rep["paid"] * audit_rate * C.review if policy == "audit" else 0.0),
                     "new_type_paid": (inv.route(q, LO, HI)[(test.round_amount == 1).to_numpy()] == PAY).mean()})
        df = month(n, 9000 + 100 * seed + t, m, cal, new_pattern=np_t)
        keep, label, w = labels_for(df, policy, audit_rate, rng)
        window.append((df[FEATURES][keep], label[keep], w[keep]))
        window = window[-4:]
        x = pd.concat([a for a, _, _ in window])
        yy, ww = np.concatenate([b for _, b, _ in window]), np.concatenate([c for _, _, c in window])
        idx = rng.permutation(len(x))
        cut = int(0.8 * len(idx))
        a, b = idx[:cut], idx[cut:]
        m = inv.fit_boosted(x.iloc[a], yy[a], seed, weights=ww[a])
        cal = inv.platt(inv.score(m, x.iloc[b]), yy[b], weights=ww[b])
    return rows


rows = []
for s in range(8):
    for policy in ("true labels", "silence is correct", "reviewed only", "audit"):
        rows += run_loop(policy, s)
    rows += [{**r, "policy": "audit 2%"} for r in run_loop("audit", s, audit_rate=0.02)]
    frozen = run_loop("true labels", s, months=1)[0]
loop = pd.DataFrame(rows)
print("\nEight months, 10,000 invoices each, retrained monthly on the last three months. New fraud type from month 3. Mean of 8 seeds, judged on fresh true outcomes")
pv = loop.groupby(["policy", "month"], sort=False)[["paid", "reviewed", "error_paid", "new_type_paid", "auc", "cost_with_audit"]].mean()
print(pv[pv.index.get_level_values("month").isin([2, 3, 5, 8])].to_string())
m8 = loop[loop.month == 8].pivot(index="seed", columns="policy", values="cost_with_audit")
for a in ("silence is correct", "reviewed only", "audit 2%"):
    diff = m8[a] - m8["audit"]
    print(f"Month 8 cost, {a} minus audit 5%: {diff.mean():+.3f} (sd {diff.std():.3f}, {(diff > 0).sum()}/8 seeds)")

# %% Production failures as test cases: fix the class, not the rows
rows = []
for s in range(5):
    old = inv.make_invoices(20_000, 11000 + s)
    live = inv.make_invoices(60_000, 11100 + s, new_pattern=0.35)
    fresh = inv.make_invoices(60_000, 11200 + s, new_pattern=0.35)
    val = inv.make_invoices(5_000, 11300 + s, new_pattern=0.35)
    m = inv.fit_boosted(old[FEATURES], old.y, s)
    calm = inv.platt(inv.score(m, old[FEATURES]), old.y)
    p_live = calm(inv.score(m, live[FEATURES]))
    failures = live[(p_live < LO) & (live.y == 1) & (live.round_amount == 1)].iloc[:30]
    audit_rows = live[(p_live < LO)].iloc[:3000]
    fresh_failures = fresh[(fresh.y == 1) & (fresh.round_amount == 1)]
    candidates = {
        "old model": (old, None),
        "add the 30 failures": (pd.concat([old, failures]), None),
        "add the 30 failures, weight 50": (pd.concat([old, failures]), np.r_[np.ones(len(old)), np.full(len(failures), 50.0)]),
        "add 3,000 audited invoices": (pd.concat([old, audit_rows]), None),
    }
    for name, (frame, w) in candidates.items():
        cand = inv.fit_boosted(frame[FEATURES], frame.y, s, weights=w)
        cal_c = inv.platt(inv.score(cand, val[FEATURES]), val.y)
        suite = inv.route(cal_c(inv.score(cand, failures[FEATURES])), LO, HI)
        unseen = inv.route(cal_c(inv.score(cand, fresh_failures[FEATURES])), LO, HI)
        q = cal_c(inv.score(cand, fresh[FEATURES]))
        rows.append({"candidate": name, "suite_stopped": (suite != PAY).mean(), "same_class_unseen_stopped": (unseen != PAY).mean(), "auc": roc_auc_score(fresh.y, q), "cost": inv.report(fresh.y.to_numpy(), q, inv.route(q, LO, HI))["cost"]})
print("\nThirty confirmed failures of a new class. 'stopped' means not paid automatically. Mean of 5 seeds")
print(pd.DataFrame(rows).groupby("candidate", sort=False).mean(numeric_only=True).to_string())

# %% Figures
import chartstyle as cs
import matplotlib.pyplot as plt

cs.apply()
fig, axes = plt.subplots(1, 2, figsize=(9, 4.2))
for ax, data, title in [(axes[0], "invoices", "Generated invoices"), (axes[1], "credit", "Real credit file")]:
    g = al[(al.data == data) & (al.learner == "boosted") & (al.batch == 100) & (al.miss == 0)]
    for strategy, colour in [("random", cs.BLUE), ("uncertainty", cs.ORANGE), ("highest score", cs.AQUA)]:
        c = g[g.strategy == strategy].groupby("labels").auc.mean()
        ax.plot(c.index, c.values, color=colour, label=strategy.capitalize())
    ax.set_xlabel("Labels bought")
    ax.set_ylabel("AUC on test")
    ax.set_title(title)
axes[0].legend(loc="lower right")
cs.save(fig, "corrections-active-learning.png")

fig, ax = plt.subplots()
for policy, colour, ls in [("true labels", cs.INK, ":"), ("silence is correct", cs.ORANGE, "-"), ("reviewed only", cs.YELLOW, "-"), ("audit", cs.BLUE, "-")]:
    c = loop[loop.policy == policy].groupby("month").error_paid.mean()
    ax.plot(c.index, c.values, color=colour, ls=ls, label={"audit": "Random audit, 5%", "true labels": "Every true label (unobtainable)", "silence is correct": "Silence counts as correct", "reviewed only": "Reviewed invoices only"}[policy])
ax.axvline(3, color=cs.MUTED, lw=1)
ax.annotate("new fraud type arrives", (3, ax.get_ylim()[1]), xytext=(5, -12), textcoords="offset points", color=cs.SECONDARY)
ax.set_xlabel("Month")
ax.set_ylabel("True error rate among invoices paid automatically")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1%}"))
ax.set_ylim(0, None)
ax.set_title("What each labelling policy does to the invoices nobody looks at")
ax.legend(loc="center right")
cs.save(fig, "corrections-silent-acceptance.png")
