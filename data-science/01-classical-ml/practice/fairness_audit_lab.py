# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scikit-learn"]
# ///
"""A fairness audit of a generated hiring screen, for notes/15-fairness-in-automated-scoring.md.

Run from this folder (a few seconds once uv has the packages, no downloads of data, no API key):
    uv run fairness_audit_lab.py

Everything is generated from SEED. Brackwater Freight is invented, and groups A, B, C and attributes X, Y are labels on
random draws. The generator gives group B a lower pass rate on a work sample, makes past recruiters mark down groups B
and C and above all B-and-Y together, and makes postcode band track group. Those are assumptions we planted so that an
audit has something to find. They are not claims about any real group, employer or product, and no number here is a
general finding. The metrics, the intervals and the arithmetic are real. Nothing here is legal advice.

Things to change and watch: RECRUITER_BIAS (set every value in the dict to 0.0), INTERSECTION_BIAS and GAP_BIAS (with
those two at 0 as well you have the control), PROXY_STRENGTH (how well postcode reveals group), SKILL_GAP (set every value
to 0.0 to equalise base rates, and the impossibility conflict shrinks to noise), CAPACITY, AUDIT_SIZE.
The assertions state what this planted world should show, so a setting that removes a planted effect can trip one. That
failure is the result: read its message, and comment it out to see the rest.
"""

# %%
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SEED = 15
N_TRAIN, N_VAL, N_TEST = 40_000, 20_000, 20_000
AUDIT_SIZE = 5_000  # applicants who sat the work sample whatever the recruiter decided
CAPACITY = 0.20  # the share of applicants who can be advanced to interview
SITE_SIZE = 400  # applicants at one depot, for the small-group section

GROUP_SHARE = {"A": 0.70, "B": 0.24, "C": 0.06}
SKILL_GAP = {"A": 0.0, "B": -0.35, "C": -0.05}  # mean skill by group: stands in for unequal access to prior training
RECRUITER_BIAS = {"A": 0.0, "B": 0.8, "C": 0.5}  # log-odds taken off by past recruiters, on top of what skill explains
INTERSECTION_BIAS = 0.9  # further log-odds taken off applicants who are both B and Y
GAP_BIAS = 0.25  # log-odds per unit of employment gap, which says nothing about the work sample
PROXY_STRENGTH = 1.0  # how strongly postcode band tracks group; 0 makes the two independent
FOUR_FIFTHS = 0.8

BANDS = np.arange(5)
pd.set_option("display.width", 160, "display.max_columns", 30)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


# %% The generator: skill drives the true outcome, recruiters add a penalty, postcode tracks group
def band_probabilities(proxy_strength=PROXY_STRENGTH):
    """P(postcode band | group). Group A leans to low bands, B to high bands and C sits in the middle."""
    centre = {"A": 0.0, "B": 4.0, "C": 2.0}
    table = {}
    for group, c in centre.items():
        weight = np.exp(-proxy_strength * 0.5 * np.abs(BANDS - c))
        table[group] = weight / weight.sum()
    return table


def make_applicants(
    rng,
    n,
    skill_gap=None,
    recruiter_bias=None,
    intersection_bias=INTERSECTION_BIAS,
    gap_bias=GAP_BIAS,
    proxy_strength=PROXY_STRENGTH,
):
    skill_gap = SKILL_GAP if skill_gap is None else skill_gap
    recruiter_bias = RECRUITER_BIAS if recruiter_bias is None else recruiter_bias
    groups = np.array(list(GROUP_SHARE))
    group = rng.choice(groups, n, p=list(GROUP_SHARE.values()))
    attr = rng.choice(["X", "Y"], n)
    skill = rng.normal(np.vectorize(skill_gap.get)(group), 1.0)
    table = band_probabilities(proxy_strength)
    band = np.empty(n, dtype=int)
    for g in groups:
        at = group == g
        band[at] = rng.choice(BANDS, at.sum(), p=table[g])
    test_score = skill + rng.normal(0, 0.7, n)
    experience = 0.6 * skill + rng.normal(0, 1.0, n)
    gap = np.maximum(0, rng.normal(0.5 + 0.8 * (attr == "Y"), 0.8, n))  # employment gap, tracks attribute Y
    passed_work_sample = rng.random(n) < sigmoid(-0.9 + 1.6 * skill)
    penalty = (
        np.vectorize(recruiter_bias.get)(group) + intersection_bias * ((group == "B") & (attr == "Y")) + gap_bias * gap
    )
    advanced_by_recruiter = rng.random(n) < sigmoid(-1.0 + 1.3 * test_score + 0.4 * experience - penalty)
    return pd.DataFrame(
        {
            "group": group,
            "attr": attr,
            "band": band,
            "test_score": test_score,
            "experience": experience,
            "gap": gap,
            "history": advanced_by_recruiter.astype(int),
            "outcome": passed_work_sample.astype(int),
        }
    )


def matrix(df, columns):
    """Numeric columns plus one-hot bands and groups, with fixed columns whatever the slice holds."""
    out = pd.DataFrame(index=df.index)
    for c in columns:
        if c == "band":
            for b in BANDS:
                out[f"band_{b}"] = (df["band"] == b).astype(float)
        elif c == "group":
            for g in GROUP_SHARE:
                out[f"group_{g}"] = (df["group"] == g).astype(float)
        elif c == "attr":
            out["attr_Y"] = (df["attr"] == "Y").astype(float)
        else:
            out[c] = df[c].astype(float)
    return out.to_numpy()


def fit_score(train, columns, label):
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    model.fit(matrix(train, columns), train[label])
    return lambda df: model.predict_proba(matrix(df, columns))[:, 1]


# %% The metrics, each written out rather than imported
def selection_rates(selected, group):
    return {g: float(selected[group == g].mean()) for g in pd.unique(group)}


def impact_ratios(selected, group):
    """Each group's selection rate over the highest group's rate."""
    rates = selection_rates(selected, group)
    top = max(rates.values())
    return {g: r / top for g, r in rates.items()}


def rates_against(selected, label):
    """TPR, FPR, FNR and PPV of a selection against one label. `label` says which truth we are auditing against."""
    tp = int((selected & (label == 1)).sum())
    fp = int((selected & (label == 0)).sum())
    fn = int((~selected & (label == 1)).sum())
    tn = int((~selected & (label == 0)).sum())
    tpr, fpr = tp / max(tp + fn, 1), fp / max(fp + tn, 1)
    return {
        "tpr": tpr,
        "fpr": fpr,
        "fnr": 1 - tpr,
        "ppv": tp / max(tp + fp, 1),
        "base": (tp + fn) / max(tp + fp + fn + tn, 1),
    }


def by_group(selected, label, group):
    return {g: rates_against(selected[group == g], label[group == g]) for g in GROUP_SHARE if (group == g).any()}


def calibration_table(score, label, group, edges=(0.0, 0.1, 0.2, 0.35, 0.5, 0.7, 1.0)):
    """Observed rate of `label` in each score bin, by group. A calibrated score has rows close to the bin's mean score."""
    rows = []
    bins = pd.cut(score, edges, include_lowest=True)
    for b in bins.categories:
        at = bins == b
        row = {"score_bin": str(b), "mean_score": score[at].mean() if at.any() else float("nan")}
        for g in GROUP_SHARE:
            mask = at & (group == g)
            row[f"obs_{g}"] = label[mask].mean() if mask.sum() >= 30 else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, centre - half), min(1.0, centre + half)


def ratio_interval(k1, n1, k2, n2, z=1.96):
    """95% interval for (k1/n1) / (k2/n2) by the delta method on the log ratio. 0.5 is added when a count is zero."""
    if k1 == 0 or k2 == 0:
        k1, k2, n1, n2 = k1 + 0.5, k2 + 0.5, n1 + 0.5, n2 + 0.5
    ratio = (k1 / n1) / (k2 / n2)
    se = math.sqrt(max(1 / k1 - 1 / n1 + 1 / k2 - 1 / n2, 0.0))
    return ratio, ratio * math.exp(-z * se), ratio * math.exp(z * se)


def fisher_two_sided(k1, n1, k2, n2):
    """Exact test that two selection rates are equal, summing tables no likelier than the one observed."""
    total, picked = n1 + n2, k1 + k2

    def log_comb(n, k):
        return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)

    def log_prob(k):
        return log_comb(n1, k) + log_comb(n2, picked - k) - log_comb(total, picked)

    observed = log_prob(k1)
    low, high = max(0, picked - n2), min(n1, picked)
    return min(1.0, sum(math.exp(lp) for lp in map(log_prob, range(low, high + 1)) if lp <= observed + 1e-9))


def shortfall(k, n, top_rate, floor=FOUR_FIFTHS):
    """How many more people this group would need selected to reach the floor against the top rate."""
    return max(0, math.ceil(round(floor * top_rate * n - k, 9)))  # round first: 0.8 * 0.3 * 100 is not exactly 24


def auc(score, label):
    ranks = pd.Series(score).rank().to_numpy()
    pos = label == 1
    n_pos, n_neg = pos.sum(), (~pos).sum()
    return (ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


# %% Decision rules: one cutoff for everybody, or one per group
def one_cutoff(val_score, capacity=CAPACITY):
    return float(np.quantile(val_score, 1 - capacity))


def parity_cutoffs(val_score, val_group, capacity=CAPACITY):
    """Equal selection rates: the top `capacity` of each group."""
    return {g: float(np.quantile(val_score[val_group == g], 1 - capacity)) for g in GROUP_SHARE}


def tpr_cutoffs(val_score, val_group, val_label, capacity=CAPACITY):
    """Equal TPR against `val_label`, at the common TPR that fills capacity overall. Bisection on that TPR."""

    def cuts(tpr):
        return {g: float(np.quantile(val_score[(val_group == g) & (val_label == 1)], 1 - tpr)) for g in GROUP_SHARE}

    low, high = 0.0, 1.0
    for _ in range(40):
        mid = (low + high) / 2
        share = np.mean(apply_cutoffs(val_score, val_group, cuts(mid)))
        low, high = (mid, high) if share < capacity else (low, mid)
    return cuts((low + high) / 2)


def apply_cutoffs(score, group, cutoffs):
    if isinstance(cutoffs, dict):
        return score >= np.vectorize(cutoffs.get)(group)
    return score >= cutoffs


@dataclass
class World:
    train: pd.DataFrame
    val: pd.DataFrame
    test: pd.DataFrame
    audit: pd.DataFrame


def make_world(seed=SEED, **kwargs):
    rng = np.random.default_rng(seed)
    train = make_applicants(rng, N_TRAIN, **kwargs)
    val = make_applicants(rng, N_VAL, **kwargs)
    test = make_applicants(rng, N_TEST, **kwargs)
    return World(train, val, test, train.iloc[:AUDIT_SIZE])


ALL_COLS = ["group", "attr", "band", "test_score", "experience", "gap"]
UNAWARE = ["band", "test_score", "experience", "gap"]
NO_PROXY = ["test_score", "experience"]


def evaluate(world, name, score_fn, rule="one", label_for_tpr="history", val_label=None):
    """Fit the rule on validation, apply it on test, and report against both labels."""
    val_score, test_score = score_fn(world.val), score_fn(world.test)
    if rule == "one":
        cutoffs = one_cutoff(val_score)
    elif rule == "parity":
        cutoffs = parity_cutoffs(val_score, world.val["group"].to_numpy())
    else:
        labels = world.val[label_for_tpr].to_numpy() if val_label is None else val_label
        cutoffs = tpr_cutoffs(val_score, world.val["group"].to_numpy(), labels)
    selected = apply_cutoffs(test_score, world.test["group"].to_numpy(), cutoffs)
    group, history, outcome = (
        world.test["group"].to_numpy(),
        world.test["history"].to_numpy(),
        world.test["outcome"].to_numpy(),
    )
    rates, ratios = selection_rates(selected, group), impact_ratios(selected, group)
    truth, hist = by_group(selected, outcome, group), by_group(selected, history, group)
    return {
        "approach": name,
        "share": selected.mean(),
        "sel_A": rates["A"],
        "sel_B": rates["B"],
        "sel_C": rates["C"],
        "ratio_B": ratios["B"],
        "ratio_C": ratios["C"],
        "tpr_A": truth["A"]["tpr"],
        "tpr_B": truth["B"]["tpr"],
        "fpr_A": truth["A"]["fpr"],
        "fpr_B": truth["B"]["fpr"],
        "ppv_A": truth["A"]["ppv"],
        "ppv_B": truth["B"]["ppv"],
        "ppv_true": outcome[selected].mean(),
        "ppv_hist": history[selected].mean(),
        "_selected": selected,
        "_hist": hist,
    }


# %% 1. The world, and the first ratio
def section_data(world):
    test = world.test
    print(f"1. Generated applicants at Brackwater Freight (fictional). Train {N_TRAIN:,}, validation {N_VAL:,}, test {N_TEST:,}")
    print(
        test.groupby("group")
        .agg(n=("history", "size"), work_sample_pass=("outcome", "mean"), advanced_by_recruiter=("history", "mean"))
        .round(3)
    )
    pass_hist = selection_rates(test["history"].to_numpy() == 1, test["group"].to_numpy())
    pass_true = selection_rates(test["outcome"].to_numpy() == 1, test["group"].to_numpy())
    print(f"   Past recruiters' ratio, B against A: {pass_hist['B'] / pass_hist['A']:.3f}")
    print(
        f"   The work sample's ratio, B against A: {pass_true['B'] / pass_true['A']:.3f}. The test would flag this too: "
        "a ratio is not a verdict on the cause.\n"
    )


# %% 2. The approaches side by side
def section_approaches(world):
    raw = fit_score(world.train, ALL_COLS, "history")
    unaware = fit_score(world.train, UNAWARE, "history")
    no_proxy = fit_score(world.train, NO_PROXY, "history")
    audited = fit_score(world.audit, NO_PROXY, "outcome")
    val_outcome = world.val["outcome"].to_numpy()
    rows = [
        evaluate(world, "naive: all columns, one cutoff", raw),
        evaluate(world, "unaware: group and attribute dropped, one cutoff", unaware),
        evaluate(world, "unaware: proxies dropped too, one cutoff", no_proxy),
        evaluate(world, "group cutoffs on unaware, equal selection", unaware, rule="parity"),
        evaluate(world, "group cutoffs on unaware, equal TPR on history", unaware, rule="tpr"),
        evaluate(world, "group cutoffs on unaware, equal TPR on outcomes", unaware, rule="tpr", val_label=val_outcome),
        evaluate(world, "audited labels, no proxies, one cutoff", audited),
        evaluate(world, "audited labels, no proxies, equal selection", audited, rule="parity"),
    ]
    table = pd.DataFrame(rows).drop(columns=["_selected", "_hist"]).set_index("approach")
    print(
        f"2. Approaches at a capacity of {CAPACITY:.0%}, on test. tpr, fpr and ppv are against the work sample, which only the generator knows for all"
    )
    print(table[["sel_A", "sel_B", "sel_C", "ratio_B", "ratio_C", "ppv_true", "ppv_hist"]].round(3).to_string())
    print()
    print(table[["tpr_A", "tpr_B", "fpr_A", "fpr_B", "ppv_A", "ppv_B"]].round(3).to_string())

    # Counted, not ppv x share: rows advance slightly different numbers of people.
    outcome = world.test["outcome"].to_numpy()
    counts = pd.DataFrame(
        {
            "advanced": {r["approach"]: int(r["_selected"].sum()) for r in rows},
            "pass_work_sample": {r["approach"]: int(outcome[r["_selected"]].sum()) for r in rows},
        }
    )
    counts["against_best"] = counts["pass_work_sample"] - counts["pass_work_sample"].max()
    print(f"\n   People advanced at a capacity of {CAPACITY:.0%}, and how many of them pass the work sample. Counts on test:")
    print(counts.to_string())
    for row in rows:
        assert abs(row["share"] - CAPACITY) < 0.02, f"{row['approach']} missed capacity: {row['share']:.3f}"
        assert max(impact_ratios(row["_selected"], world.test["group"].to_numpy()).values()) == 1.0
    parity = rows[3]
    assert parity["ratio_B"] > 0.9, "equal-selection cutoffs should close the ratio on test"
    assert rows[1]["ratio_B"] < FOUR_FIFTHS, "dropping the column should leave the gap"
    print()
    return raw, unaware, no_proxy, audited, rows


# %% 3. Proxies: removing the column does not remove the effect
def section_proxy(world, raw, unaware, no_proxy):
    train = world.train
    group_b = (train["group"] == "B").astype(int)
    from_band = fit_score(train.assign(is_b=group_b), ["band"], "is_b")
    from_all = fit_score(train.assign(is_b=group_b), UNAWARE, "is_b")
    test_b = (world.test["group"] == "B").astype(int).to_numpy()
    print("3. Can the remaining columns identify group B? AUC on test")
    print(
        f"   from postcode band alone {auc(from_band(world.test), test_b):.3f}; from every unaware column {auc(from_all(world.test), test_b):.3f}"
    )
    group, selected = world.test["group"].to_numpy(), {}
    for name, fn in [("all columns", raw), ("group and attribute dropped", unaware), ("proxies dropped too", no_proxy)]:
        cut = one_cutoff(fn(world.val))
        selected[name] = fn(world.test) >= cut
        print(
            f"   {name:<28} selection B {selection_rates(selected[name], group)['B']:.3f}, ratio {impact_ratios(selected[name], group)['B']:.3f}"
        )
    first, second = selected["all columns"], selected["group and attribute dropped"]
    print(f"   Decisions identical between the first two rows: {(first == second).mean():.1%}")
    print(
        f"   Most of that is people both reject. Of those either row advances, both do: {(first & second).sum() / (first | second).sum():.1%}\n"
    )


# %% 4. Label bias: the same score audited against two labels
def section_label_bias(world, raw, unaware):
    group = world.test["group"].to_numpy()
    history, outcome = world.test["history"].to_numpy(), world.test["outcome"].to_numpy()
    print("4. One selection, two audits, at one cutoff")
    for model, fn in [("naive", raw), ("unaware", unaware)]:
        selected = fn(world.test) >= one_cutoff(fn(world.val))
        hist, true = by_group(selected, history, group), by_group(selected, outcome, group)
        for name, res in [("against history (the logs)", hist), ("against the work sample", true)]:
            print(
                f"   {model:<8} {name:<28} TPR A {res['A']['tpr']:.3f}, B {res['B']['tpr']:.3f};"
                f"  PPV A {res['A']['ppv']:.3f}, B {res['B']['ppv']:.3f}"
            )
        if model == "naive":
            assert hist["A"]["ppv"] > hist["B"]["ppv"] and true["A"]["ppv"] < true["B"]["ppv"], (
                "the PPV gap should change sign"
            )
        else:
            assert hist["A"]["ppv"] - hist["B"]["ppv"] > abs(true["A"]["ppv"] - true["B"]["ppv"]), (
                "history should invent a gap"
            )

    score = raw(world.test)
    print("\n   The naive model, which sees group. Calibration against history: rows agree, so it looks fair")
    against_history = calibration_table(score, history, group)
    print(against_history.round(3).to_string(index=False))
    print("\n   The same score against the work sample: at the same score, B passes more often")
    against_outcome = calibration_table(score, outcome, group)
    print(against_outcome.round(3).to_string(index=False))
    history_gap = (against_history["obs_B"] - against_history["obs_A"]).abs().mean()
    outcome_gap = (against_outcome["obs_B"] - against_outcome["obs_A"]).abs().mean()
    print(
        f"   Mean gap between B and A across bins: {history_gap:.3f} against history, {outcome_gap:.3f} against the work sample"
    )
    assert history_gap < outcome_gap, "calibrating to a biased label should look fine only against that label"
    print()


# %% 5. The impossibility conflict, on a score calibrated within each group
def calibrate_within_groups(train, score_fn):
    """Refit a logistic curve per group on the score's log-odds, against outcome. This is calibration by construction."""
    curves = {}
    for g in GROUP_SHARE:
        at = train["group"] == g
        logit = np.log(np.clip(score_fn(train[at]), 1e-6, 1 - 1e-6)).reshape(-1, 1) - np.log(
            1 - np.clip(score_fn(train[at]), 1e-6, 1 - 1e-6)
        ).reshape(-1, 1)
        curves[g] = LogisticRegression(max_iter=2000).fit(logit, train.loc[at, "outcome"])

    def calibrated(df):
        out = np.zeros(len(df))
        raw = np.clip(score_fn(df), 1e-6, 1 - 1e-6)
        logit = (np.log(raw) - np.log(1 - raw)).reshape(-1, 1)
        for g, curve in curves.items():
            at = (df["group"] == g).to_numpy()
            out[at] = curve.predict_proba(logit[at])[:, 1]
        return out

    return calibrated


def chouldechova_fpr(base, ppv, fnr):
    """Chouldechova 2017, eq. 2.6: FPR = p/(1-p) * (1-PPV)/PPV * (1-FNR)."""
    return base / (1 - base) * (1 - ppv) / ppv * (1 - fnr)


def equal_ppv_cutoffs(score, group, target):
    """For each group, the lowest cutoff whose selected people pass at about `target`."""
    cuts = {}
    for g in GROUP_SHARE:
        s = np.sort(score[group == g])[::-1]
        running_ppv = np.cumsum(s) / np.arange(1, len(s) + 1)  # a calibrated score's own estimate of PPV
        cuts[g] = float(s[max(np.searchsorted(-running_ppv, -target) - 1, 0)])
    return cuts


def equalised_odds_selection(score, group, label, rng, weak="B", cutoff=0.45):
    """A derived predictor in the manner of Hardt et al. Take the weak group's ROC point at `cutoff` and draw the ray from the
    origin through it. Coin flips can move any group down its own ray, so aim for a point on that ray that every group can
    reach: each other group's ROC meets the ray once, and the lowest of those meetings is the target."""
    weak_rates = rates_against(score[group == weak] >= cutoff, label[group == weak])
    slope = weak_rates["tpr"] / max(weak_rates["fpr"], 1e-9)
    above_cutoff, reached = {weak: score >= cutoff}, {weak: weak_rates["tpr"]}
    for g in GROUP_SHARE:
        if g == weak:
            continue
        at = np.nonzero(group == g)[0]
        order = at[np.argsort(-score[at])]
        y = label[order]
        tps, fps = np.cumsum(y) / y.sum(), np.cumsum(1 - y) / (1 - y).sum()
        # The last point still above the ray, plus one. The first point below it can be one early non-passer.
        over = np.nonzero(tps > slope * fps)[0]
        k = min(int(over[-1]) + 1, len(order) - 1) if over.size else 0
        members = np.zeros(len(score), dtype=bool)
        members[order[: k + 1]] = True
        above_cutoff[g], reached[g] = members, float(tps[k])
    target = min(reached.values())
    selected = np.zeros(len(score), dtype=bool)
    for g in GROUP_SHARE:
        members = above_cutoff[g] & (group == g)
        keep = target / max(reached[g], 1e-9)
        selected[members] = keep >= 1.0 or rng.random(members.sum()) < keep
    return selected


def conflict_row(name, selected, group, outcome):
    res = by_group(selected, outcome, group)
    return {
        "rule": name,
        "sel_A": selected[group == "A"].mean(),
        "sel_B": selected[group == "B"].mean(),
        "ppv_A": res["A"]["ppv"],
        "ppv_B": res["B"]["ppv"],
        "fpr_A": res["A"]["fpr"],
        "fpr_B": res["B"]["fpr"],
        "fnr_A": res["A"]["fnr"],
        "fnr_B": res["B"]["fnr"],
    }


def section_impossibility(world, audited, world_seed=SEED):
    score_fn = calibrate_within_groups(world.val, audited)
    score = score_fn(world.test)
    group, outcome = world.test["group"].to_numpy(), world.test["outcome"].to_numpy()
    print("5. The conflict. A score trained on audited outcomes and calibrated within each group, on test")
    print(calibration_table(score, outcome, group).round(3).to_string(index=False))
    print("\n   Kleinberg et al.: mean score in each class, by group. Calibration forces (1-p)x + py = p")
    for g in ("A", "B"):
        at = group == g
        p = outcome[at].mean()
        x, y = score[at & (outcome == 0)].mean(), score[at & (outcome == 1)].mean()
        print(
            f"   {g}: base rate {p:.3f}, mean score on non-passers x {x:.3f}, on passers y {y:.3f}, (1-p)x + py = {(1 - p) * x + p * y:.3f}"
        )
        assert abs((1 - p) * x + p * y - score[at].mean()) < 1e-9
        assert abs(score[at].mean() - p) < 0.02, "a calibrated score's mean should match the base rate"

    cut = 0.45
    rows = [conflict_row(f"one cutoff at {cut}", score >= cut, group, outcome)]
    rows.append(
        conflict_row(
            "equal PPV (0.62)", apply_cutoffs(score, group, equal_ppv_cutoffs(score, group, 0.62)), group, outcome
        )
    )
    fair = apply_cutoffs(score, group, tpr_cutoffs(score, group, outcome, capacity=0.25))
    rows.append(conflict_row("equal TPR", fair, group, outcome))
    rng = np.random.default_rng(world_seed + 1)
    rows.append(
        conflict_row(
            "equal TPR and FPR (randomised)", equalised_odds_selection(score, group, outcome, rng), group, outcome
        )
    )
    table = pd.DataFrame(rows).set_index("rule")
    print("\n   What each rule equalises, and what then moves")
    print(table.round(3).to_string())
    derived = rows[-1]
    assert abs(derived["fpr_A"] - derived["fpr_B"]) < 0.02 and abs(derived["fnr_A"] - derived["fnr_B"]) < 0.02, (
        "the randomised rule should match both error rates"
    )

    # The identity holds for every row, in each group, whatever the rule.
    for row in rows:
        for g in ("A", "B"):
            p = outcome[group == g].mean()
            implied = chouldechova_fpr(p, row[f"ppv_{g}"], row[f"fnr_{g}"])
            assert abs(implied - row[f"fpr_{g}"]) < 1e-9, "Chouldechova's identity is arithmetic and must hold exactly"
    pa, pb = outcome[group == "A"].mean(), outcome[group == "B"].mean()
    print(
        f"\n   Identity check passed for every row. Base rates {pa:.3f} against {pb:.3f}. The identity holds whatever they are; unequal ones are what force a gap."
    )
    print(
        f"   With PPV 0.62 and FNR 0.40 in both groups, the identity alone gives FPR A {chouldechova_fpr(pa, 0.62, 0.40):.3f}, B {chouldechova_fpr(pb, 0.62, 0.40):.3f}\n"
    )


# %% 6. Small groups: an interval on the ratio
def group_interval_rows(selected, group):
    """One row per slice, each against the slice with the highest rate. That slice has no interval against itself."""
    rates = selection_rates(selected, group)
    top = max(rates, key=rates.get)
    k2, n2 = int(selected[group == top].sum()), int((group == top).sum())
    rows = []
    for g in sorted(rates):
        k, n = int(selected[group == g].sum()), int((group == g).sum())
        ratio, low, high = (1.0, float("nan"), float("nan")) if g == top else ratio_interval(k, n, k2, n2)
        rows.append(
            {
                "slice": g,
                "n": n,
                "selected": k,
                "rate": k / n,
                "rate_lo": wilson(k, n)[0],
                "rate_hi": wilson(k, n)[1],
                "ratio": ratio,
                "ratio_lo": low,
                "ratio_hi": high,
                "fisher_p": float("nan") if g == top else fisher_two_sided(k, n, k2, n2),
                "short_by": shortfall(k, n, k2 / n2),
            }
        )
    return pd.DataFrame(rows)


def forest(rows):
    """Intervals on a text axis from 0 to 1.6, with the 0.8 line marked. The top slice is the reference."""
    width, top = 48, 1.6

    def pos(v):
        return min(width - 1, int(min(v, top) / top * (width - 1)))

    lines = [f"{'':>6} 0{'':<{pos(0.8) - 1}}0.8{'':<{width - pos(0.8) - 6}}1.6"]
    for _, r in rows.iterrows():
        line = [" "] * width
        line[pos(0.8)] = "|"
        if r["ratio_lo"] != r["ratio_lo"]:  # NaN: the reference slice
            line[pos(1.0)] = "o"
            lines.append(f"{r['slice']:>6} {''.join(line)} 1.00 reference, n={r['n']}")
            continue
        for i in range(pos(r["ratio_lo"]), pos(r["ratio_hi"]) + 1):
            line[i] = "-" if line[i] == " " else line[i]
        line[pos(r["ratio"])] = "o"
        lines.append(
            f"{r['slice']:>6} {''.join(line)} {r['ratio']:.2f} [{r['ratio_lo']:.2f}, {r['ratio_hi']:.2f}] n={r['n']}"
        )
    return "\n".join(lines)


def section_small_groups(world, unaware):
    site = world.test.iloc[:SITE_SIZE]
    cut = one_cutoff(unaware(world.val))
    selected, group = unaware(site) >= cut, site["group"].to_numpy()
    rows = group_interval_rows(selected, group)
    print(f"6. One depot, {SITE_SIZE} applicants, the unaware model at one cutoff. Ratio against the highest group")
    print(rows.round(3).to_string(index=False))
    print(forest(rows))
    for _, r in rows.iterrows():
        assert r["rate_lo"] <= r["rate"] <= r["rate_hi"]
        assert r["ratio_lo"] != r["ratio_lo"] or r["ratio_lo"] <= r["ratio"] <= r["ratio_hi"]

    rng = np.random.default_rng(SEED + 2)
    print(
        "\n   How the four-fifths reading behaves by size. Group A has 1,000 applicants at a rate of 0.30. "
        "20,000 repeats, 3,000 for the two interval columns"
    )
    rows = []
    for n in (20, 50, 200, 1000):
        k_top = rng.binomial(1000, 0.30, 20_000)
        fair = rng.binomial(n, 0.30, 20_000)
        unfair = rng.binomial(n, 0.18, 20_000)  # a true ratio of 0.6
        false_flag = np.mean((fair / n) / (k_top / 1000) < FOUR_FIFTHS)
        missed = np.mean((unfair / n) / (k_top / 1000) >= FOUR_FIFTHS)
        covered, informative = 0, 0
        for f, t in zip(unfair[:3000], k_top[:3000]):
            _, low, high = ratio_interval(int(f), n, int(t), 1000)
            covered += low <= 0.6 <= high
            informative += high < FOUR_FIFTHS
        rows.append(
            {
                "small_group_n": n,
                "true_ratio_1.0_flagged": false_flag,
                "true_ratio_0.6_passed": missed,
                "coverage_at_0.6": covered / 3000,
                "interval_wholly_below_0.8": informative / 3000,
            }
        )
    table = pd.DataFrame(rows)
    print(table.round(3).to_string(index=False))
    assert table["true_ratio_1.0_flagged"].iloc[0] > table["true_ratio_1.0_flagged"].iloc[-1], (
        "small groups should flag more"
    )
    assert 0.9 < table["coverage_at_0.6"].iloc[-1] < 0.98, "the interval should near 95% at a reasonable size"
    # Fixed values, so a broken formula cannot pass by being self-consistent.
    assert abs(fisher_two_sided(2, 30, 64, 266) - 0.035) < 0.001
    assert all(abs(a - b) < 0.001 for a, b in zip(ratio_interval(20, 100, 300, 1000), (0.667, 0.445, 0.998)))
    assert shortfall(20, 100, 0.3) == 4
    print()


# %% 7. Intersectional slices
def slices_of(selected, test, title):
    print(f"   {title}")
    margin = group_interval_rows(selected, test["group"].to_numpy())
    attr = group_interval_rows(selected, test["attr"].to_numpy())
    both = group_interval_rows(selected, (test["group"] + "/" + test["attr"]).to_numpy())
    print(forest(pd.concat([margin, attr])))
    print(forest(both))
    return {r["slice"]: r["ratio"] for rows in (margin, attr, both) for _, r in rows.iterrows()}


def chance_false_alarms(sizes, rate, rng, repeats=20_000, z=1.96):
    """Every slice truly has the same rate. Pick the top slice from the data, as a panel does, then count the other slices
    whose 95% interval on the ratio lies wholly below 1."""
    sizes = np.array(sizes)
    k = rng.binomial(sizes, rate, (repeats, len(sizes)))
    r = k / sizes
    top = r.argmax(axis=1)
    picked = np.arange(repeats)
    k_top, n_top = k[picked, top], sizes[top]
    with np.errstate(divide="ignore"):
        se = np.sqrt(1 / k - 1 / sizes + 1 / k_top[:, None] - 1 / n_top[:, None])
        below = r / r[picked, top][:, None] * np.exp(z * se) < 1
    below[picked, top] = False
    return below.sum(axis=1).mean(), (below.sum(axis=1) > 0).mean()


def crossed_over_seeds(seeds):
    """The equal-selection fix on other draws of the same world: margins and crossings, each against its own top slice."""
    rows = []
    for seed in seeds:
        other = make_world(seed)
        fn = fit_score(other.train, UNAWARE, "history")
        test = other.test
        cuts = parity_cutoffs(fn(other.val), other.val["group"].to_numpy())
        chosen = apply_cutoffs(fn(test), test["group"].to_numpy(), cuts)
        margin = {
            **impact_ratios(chosen, test["group"].to_numpy()),
            **impact_ratios(chosen, test["attr"].to_numpy()),
        }
        crossed = impact_ratios(chosen, (test["group"] + "/" + test["attr"]).to_numpy())
        rows.append(
            {
                "B": margin["B"],
                "Y": margin["Y"],
                "worst_margin": min(margin.values()),
                "B/Y": crossed["B/Y"],
                "worst_crossed": min(crossed.values()),
            }
        )
    return pd.DataFrame(rows)


def section_intersections(world, unaware, rows):
    test = world.test
    print(f"7. Slices, on all {N_TEST:,} test applicants. Ratio against the top slice of each panel")
    slices_of(unaware(test) >= one_cutoff(unaware(world.val)), test, "Unaware model, one cutoff")
    print()
    fixed = slices_of(
        rows[3]["_selected"], test, "Unaware model, group cutoffs that equalise selection across A, B and C"
    )
    print(
        f"   After the fix: B {fixed['B']:.3f}, C {fixed['C']:.3f}, Y {fixed['Y']:.3f}. "
        f"Within them: B/Y {fixed['B/Y']:.3f}, C/Y {fixed['C/Y']:.3f}."
    )
    seeds = 30
    sweep = crossed_over_seeds(range(SEED + 300, SEED + 300 + seeds))
    print(f"\n   That reading is one draw. The same fix on {seeds} other seeds of this generator:")
    print(sweep[["B", "Y", "B/Y", "worst_crossed"]].agg(["mean", "min", "max"]).round(3).to_string())
    print(
        f"   B/Y under {FOUR_FIFTHS}: {(sweep['B/Y'] < FOUR_FIFTHS).sum()} of {seeds} seeds. "
        f"Some crossing under {FOUR_FIFTHS}: {(sweep['worst_crossed'] < FOUR_FIFTHS).sum()} of {seeds}. "
        f"Every margin over {FOUR_FIFTHS} on: {(sweep['worst_margin'] > FOUR_FIFTHS).sum()} of {seeds}."
    )
    assert (sweep["worst_crossed"] < sweep["worst_margin"]).all(), "crossings should read lower than the margins they sit in"

    sizes = test.groupby(test["group"] + "/" + test["attr"]).size().to_numpy()
    alarms, any_alarm = chance_false_alarms(sizes, CAPACITY, np.random.default_rng(SEED + 4))
    print(
        f"\n   False alarms with nothing wrong: {len(sizes)} equal slices, top slice picked from the data, 5% level. "
        f"{alarms:.2f} per audit, at least one in {any_alarm:.0%} of audits."
    )
    print(f"   The sum you might do first, {len(sizes) - 1} x 0.05 = {(len(sizes) - 1) * 0.05:.2f}, assumes a reference chosen in advance.\n")
    assert alarms > (len(sizes) - 1) * 0.05, "picking the top slice from the data should add false alarms"


# %% 8. Measuring without the column
def band_lookup(world):
    """P(group | band), which would in practice come from an outside table such as a census."""
    lookup = pd.crosstab(world.train["band"], world.train["group"], normalize="index")[list(GROUP_SHARE)]
    assert np.allclose(lookup.sum(axis=1), 1)
    return lookup


def inferred_ratios(world, selected):
    posterior = band_lookup(world).loc[world.test["band"]].to_numpy()
    hard = np.array(list(GROUP_SHARE))[posterior.argmax(axis=1)]
    hard_rates = selection_rates(selected, hard)
    soft = {g: float((posterior[:, i] * selected).sum() / posterior[:, i].sum()) for i, g in enumerate(GROUP_SHARE)}
    return hard, hard_rates, soft


def section_no_demographics(world, unaware):
    selected = unaware(world.test) >= one_cutoff(unaware(world.val))
    group = world.test["group"].to_numpy()
    true = selection_rates(selected, group)
    hard, hard_rates, soft = inferred_ratios(world, selected)
    rows = [
        {"method": "true group (held out)", "rate_A": true["A"], "rate_B": true["B"], "ratio_B": true["B"] / true["A"]},
        {
            "method": "assign each person their likeliest group",
            "rate_A": hard_rates["A"],
            "rate_B": hard_rates.get("B", float("nan")),  # with no proxy, nobody's likeliest group is B
            "ratio_B": hard_rates.get("B", float("nan")) / hard_rates["A"],
        },
        {
            "method": "weight each person by P(group | band)",
            "rate_A": soft["A"],
            "rate_B": soft["B"],
            "ratio_B": soft["B"] / soft["A"],
        },
    ]

    # Voluntary self-identification: people advanced answer more, and rejected people in group B answer least.
    # All four answer rates are assumptions, and only the planted version of this world can know them.
    rng = np.random.default_rng(SEED + 3)
    answer = np.where(group == "B", np.where(selected, 0.60, 0.20), np.where(selected, 0.75, 0.45))
    answered = rng.random(len(group)) < answer
    survey = selection_rates(selected[answered], group[answered])
    rows.append(
        {
            "method": "voluntary survey, answer rate tied to outcome and group",
            "rate_A": survey["A"],
            "rate_B": survey["B"],
            "ratio_B": survey["B"] / survey["A"],
        }
    )
    w = answered / answer
    weighted = {g: float((w * selected)[group == g].sum() / w[group == g].sum()) for g in "AB"}
    rows.append(
        {
            "method": "same survey, reweighted by the true answer rates",
            "rate_A": weighted["A"],
            "rate_B": weighted["B"],
            "ratio_B": weighted["B"] / weighted["A"],
        }
    )
    print("8. Estimating the ratio without a group column, on test")
    print(pd.DataFrame(rows).set_index("method").round(3).to_string())
    print(
        f"   Likeliest group is the true group for {(hard == group).mean():.3f} of people. "
        f"People answering the survey: {answered.mean():.3f}"
    )

    print("\n   The same estimators on other seeds, with the band table taken as correct")
    runs = []
    for seed in range(SEED + 200, SEED + 205):
        other = make_world(seed)
        fn = fit_score(other.train, UNAWARE, "history")
        chosen = fn(other.test) >= one_cutoff(fn(other.val))
        truth = selection_rates(chosen, other.test["group"].to_numpy())
        _, h, so = inferred_ratios(other, chosen)
        runs.append(
            {"seed": seed, "true": truth["B"] / truth["A"], "likeliest": h.get("B", float("nan")) / h["A"], "weighted": so["B"] / so["A"]}
        )
    runs = pd.DataFrame(runs).set_index("seed")
    print(runs.round(3).to_string())
    assert (runs["weighted"] > runs["true"]).all(), "here the weighted estimate should understate the disparity"
    print()


# %% 9. A control, and other seeds
def headline(seed, **kwargs):
    world = make_world(seed, **kwargs)
    unaware = fit_score(world.train, UNAWARE, "history")
    no_proxy = fit_score(world.train, NO_PROXY, "history")
    audited = fit_score(world.audit, NO_PROXY, "outcome")
    out = {}
    for name, fn in [("unaware", unaware), ("no_proxy", no_proxy), ("audited", audited)]:
        row = evaluate(world, name, fn)
        out[f"{name}_ratio_B"] = row["ratio_B"]
        out[f"{name}_ppv"] = row["ppv_true"]
    return out


def section_control():
    settings = [
        ("as planted", {}),
        (
            "no recruiter bias",
            {"recruiter_bias": {g: 0.0 for g in GROUP_SHARE}, "intersection_bias": 0.0, "gap_bias": 0.0},
        ),
        ("no skill gap", {"skill_gap": {g: 0.0 for g in GROUP_SHARE}}),
        (
            "neither",
            {
                "skill_gap": {g: 0.0 for g in GROUP_SHARE},
                "recruiter_bias": {g: 0.0 for g in GROUP_SHARE},
                "intersection_bias": 0.0,
                "gap_bias": 0.0,
            },
        ),
    ]
    print("9. Controls, mean of 5 seeds. Which part of the ratio comes from which planted cause?")
    rows = []
    for name, kwargs in settings:
        runs = pd.DataFrame([headline(SEED + 100 + s, **kwargs) for s in range(5)])
        rows.append({"world": name, **runs.mean().to_dict(), "unaware_ratio_B_sd": runs["unaware_ratio_B"].std()})
    table = pd.DataFrame(rows).set_index("world")
    print(table.round(3).to_string())
    control = table.loc["neither"]
    assert control["unaware_ratio_B"] > FOUR_FIFTHS, "with nothing planted, the ratio should clear the floor"
    assert table.loc["as planted", "unaware_ratio_B"] < control["unaware_ratio_B"], (
        "the planted causes should move the ratio"
    )
    print()


# %% 10. What the audit report states
def section_report(world, rows):
    unaware_row = rows[1]
    group = world.test["group"].to_numpy()
    k = {g: int(unaware_row["_selected"][group == g].sum()) for g in GROUP_SHARE}
    n = {g: int((group == g).sum()) for g in GROUP_SHARE}
    print("10. The findings part of an audit report, filled from this run")
    print(
        f"    Model: unaware, trained on recruiter decisions. Decision: top {CAPACITY:.0%} advance. Data: generated, {N_TEST:,} test applicants"
    )
    print(f"    A: {k['A']}/{n['A']} = {k['A'] / n['A']:.3f}; the reference")
    for g in ("B", "C"):
        ratio, low, high = ratio_interval(k[g], n[g], k["A"], n["A"])
        print(
            f"    {g}: {k[g]}/{n[g]} = {k[g] / n[g]:.3f}; ratio to A {ratio:.3f} (95% interval {low:.3f} to {high:.3f}); "
            f"short of 0.8 by {shortfall(k[g], n[g], k['A'] / n['A'])} people"
        )
    print(
        f"    Outcome label: recruiter decisions are a prior human judgement; {AUDIT_SIZE:,} audited work samples used as the check"
    )
    print(
        "    Not established: the cause of the gap, job-relatedness, or whether any law is met. That is for counsel.\n"
    )


# %%
def main():
    world = make_world()
    section_data(world)
    raw, unaware, no_proxy, audited, rows = section_approaches(world)
    section_proxy(world, raw, unaware, no_proxy)
    section_label_bias(world, raw, unaware)
    section_impossibility(world, audited)
    section_small_groups(world, unaware)
    section_intersections(world, unaware, rows)
    section_no_demographics(world, unaware)
    section_control()
    section_report(world, rows)
    print("All assertions passed. Every number above describes this generator and these assumptions.")


if __name__ == "__main__":
    main()
