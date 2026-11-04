# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scipy", "scikit-learn", "lightgbm"]
# ///
"""Capstone: find interchangeable parts from raw catalogue text, with each record's family given, and decide what may merge without a person.

Four stages, each from an earlier chapter: read the attributes (rules), retrieve candidates (character TF-IDF), score
pairs (gradient boosting on similarity features), then gate (merge, review or leave, by cost). It trains on one generated
catalogue, sets thresholds on a second and reports on a third, each from its own seed. Nothing here is real
data, and the prices are assumptions: change them at the top and see the gate move.

Run from this folder, about five minutes on a laptop CPU:
    uv run 06_parts_capstone_lab.py
"""
# %%
import functools
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from parts_catalogue import CODE, VENDOR, candidates, components, extract, label_pairs, make_catalogue

warnings.filterwarnings("ignore")
pd.set_option("display.width", 170)
SEEDS = range(5)
WRONG_MERGE, REVIEW, MISSED = 200.0, 3.0, 5.0  # euros: a wrong part on a work order, a person's check, a duplicate left in stock
GBM = dict(objective="binary", num_leaves=31, learning_rate=.05, min_data_in_leaf=10, verbosity=-1, deterministic=True, force_row_wise=True, num_threads=4)


def features(records, pairs, read_rules=True):
    """How alike two records are, and what the rules read from each. Which code it is never gets through, only whether codes agree."""
    X = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True).fit_transform(records.text)
    cos = np.asarray(X[pairs.left.values].multiply(X[pairs.right.values]).sum(1)).ravel()
    texts, fams, rows = records.text.str.lower().values, records.family.values, []
    for l, r in zip(pairs.left.values, pairs.right.values):
        a, b = set(texts[l].split()), set(texts[r].split())
        codes_l, codes_r, vend_l, vend_r = set(CODE.findall(texts[l])), set(CODE.findall(texts[r])), set(VENDOR.findall(texts[l])), set(VENDOR.findall(texts[r]))
        ea, eb = extract(texts[l], fams[l]), extract(texts[r], fams[r]) if fams[l] == fams[r] else {}
        known = [k for k in ea if ea[k] and eb.get(k)]
        agree, clash = sum(ea[k] == eb[k] for k in known), sum(ea[k] != eb[k] for k in known)
        rows.append((len(a & b) / max(len(a | b), 1), fams[l] == fams[r], agree if read_rules else 0, clash if read_rules else 0, bool(codes_l & codes_r),
                     bool(codes_l and codes_r and not codes_l & codes_r), bool(vend_l & vend_r), clash))
    rows = np.array(rows, float)
    return np.column_stack([cos, rows[:, :-1]]), rows[:, -1] > 0  # features, and whether the rules see a stated conflict


def build(seed, k=10, n_specs=800):
    records, parts = make_catalogue(seed, n_specs=n_specs)
    pairs = label_pairs(records, parts, candidates(records, k))
    return records, pairs, pairs.relation.isin(["same_part", "equivalent"]).values


@functools.cache
def prepared(seed, k, n_specs, read_rules):
    """Building a catalogue and its features is the slow part, and many arms share them."""
    records, pairs, good = build(seed, k, n_specs)
    return (records, pairs, good, *features(records, pairs, read_rules))


@functools.cache
def trained(seed, k, read_rules):
    _, _, good, X, _ = prepared(seed, k, 800, read_rules)
    return lgb.train(GBM, lgb.Dataset(X, good), 200)


def all_true_pairs(records):
    n = records.groupby("spec").size().values
    return int((n * (n - 1) // 2).sum())


def route(s, clash, hi, lo, stop_on_conflict):
    """Merge above hi. Review between lo and hi, plus any high scorer whose stated attributes conflict, if that stop is on."""
    stopped = stop_on_conflict & clash & (s >= hi)
    return (s >= hi) & ~stopped, ((s >= lo) & (s < hi)) | stopped


def euros(good, merge, review, unoffered, missed):
    """A review settles its pair correctly. A true pair retrieval never offered costs the same as one the gate left."""
    wrong = int((merge & ~good).sum())
    left = int((~merge & ~review & good).sum()) + unoffered
    return wrong * WRONG_MERGE + review.sum() * REVIEW + left * missed, wrong, left


def choose(s, good, clash, stop_on_conflict, missed, reviews=True, points=40):
    """The thresholds that cost least on a labelled catalogue the model didn't train on. `points` is how finely hi is searched."""
    lows, best = np.quantile(s, np.linspace(.5, .999, 40)), (np.inf, 1.0, 1.0)
    for hi in np.quantile(s, np.linspace(.5, .999, points)):
        for lo in lows[lows <= hi] if reviews else [hi]:
            cost = euros(good, *route(s, clash, hi, lo, stop_on_conflict), 0, missed)[0]
            if cost < best[0]:
                best = (cost, hi, lo)
    return best[1:]


def closure(n, pairs, keep, records):
    """Join kept pairs into groups. Returns the implied pairs that are true and those that are wrong."""
    groups = components(n, pairs.left.values[keep], pairs.right.values[keep])
    table = pd.crosstab(groups, records.spec.values).values
    sizes = table.sum(1)
    implied, right = int((sizes * (sizes - 1) // 2).sum()), int((table * (table - 1) // 2).sum())
    return right, implied - right


def run(seed, k=10, read_rules=True, stop_on_conflict=True, reviews=True, tune_specs=800, missed=MISSED, tune_draw=500, points=40):
    """Train on one catalogue, set thresholds on a second, report on a third, each from its own seed."""
    model = trained(seed, k, read_rules)
    _, _, good, X, clash = prepared(seed + tune_draw, k, tune_specs, read_rules)
    hi, lo = choose(model.predict(X), good, clash, stop_on_conflict, missed, reviews, points)
    records, pairs, good, X, clash = prepared(seed + 1000, k, 800, read_rules)
    merge, review = route(model.predict(X), clash, hi, lo, stop_on_conflict)
    total = all_true_pairs(records)
    cost, wrong, left = euros(good, merge, review, total - int(good.sum()), missed)
    right, wrong_closed = closure(len(records), pairs, merge, records)
    offered_right, _ = closure(len(records), pairs, good, records)
    reviewed_right, reviewed_wrong = closure(len(records), pairs, merge | (review & good), records)  # a review settles its pair correctly
    in_pile = (model.predict(X) >= hi) & clash
    return dict(records=len(records), true_pairs=total, offered=good.sum() / total, candidates=len(pairs), merged=int(merge.sum()), wrong_merges=wrong, reviews=int(review.sum()), still_unfound=left, hi=hi, pile_clashes=int(in_pile.sum()), pile_clashes_wrong=int((in_pile & ~good).sum()), offered_closed=offered_right / total, merged_reviewed_closed=reviewed_right / total, wrong_merged_reviewed_closed=reviewed_wrong,
                euros_per_record=cost / len(records), pairs_after_closure=right + wrong_closed, wrong_after_closure=wrong_closed)


# %%
records, pairs, good = build(0)
print("--- read: share of attributes the rules can read, 2,000 records, seed 0")
read = pd.DataFrame([{k: v is not None for k, v in extract(t, f).items()} for t, f in zip(records.text.head(2000), records.family.head(2000))])
print(read.mean().round(3).to_string())

# %%
print(f"\n--- retrieve, score, gate. Reported on a new catalogue, mean of {len(SEEDS)} seeds. Prices: wrong merge {WRONG_MERGE:.0f}, review {REVIEW:.0f}, missed {MISSED:.0f}")
ARMS = [("full pipeline, k=10", {}),
        ("no stop on stated conflict", dict(stop_on_conflict=False)),
        ("rules hidden from model and gate", dict(read_rules=False, stop_on_conflict=False)),
        ("no review band", dict(reviews=False)),
        ("thresholds set on 200 specs", dict(tune_specs=200)),
        ("200 specs, a second draw", dict(tune_specs=200, tune_draw=600)),
        ("200 specs, a third draw", dict(tune_specs=200, tune_draw=700)),
        ("800 specs, a second draw", dict(tune_draw=600)),
        ("800 specs, a third draw", dict(tune_draw=700)),
        ("retrieve only k=3", dict(k=3)),
        ("retrieve k=30", dict(k=30)),
        ("missed pair costs 20, not 5", dict(missed=20.0))]
rows = [dict(arm=name, seed=seed, **run(seed, **kw)) for name, kw in ARMS for seed in SEEDS]
res = pd.DataFrame(rows)
print(res.groupby("arm", sort=False)[["offered", "candidates", "merged", "wrong_merges", "reviews", "still_unfound", "euros_per_record", "pairs_after_closure", "wrong_after_closure"]].mean().round(3).to_string())
print("\nwhat closure can recover, and the stated clashes above the merge threshold")
print(res.groupby("arm", sort=False)[["offered_closed", "merged_reviewed_closed", "wrong_merged_reviewed_closed", "pile_clashes", "pile_clashes_wrong"]].mean().round(3).to_string())
print("\nsd over seeds")
print(res.groupby("arm", sort=False)[["wrong_merges", "reviews", "euros_per_record", "hi"]].std().round(3).to_string())
base = res[res.arm == ARMS[0][0]].set_index("seed").euros_per_record
print("\neuros per record against the full pipeline, paired by seed: mean difference, and seeds where the arm cost less")
for name, _ in ARMS[1:-1]:
    d = res[res.arm == name].set_index("seed").euros_per_record - base
    print(f"  {name:<34} {d.mean():+.3f}  {(d < 0).sum()} of {len(d)}")

# %%
print("\n--- how far the threshold search itself moves the answer: wrong merges and euros per record, mean of 5 seeds, by tuning draw and points searched for hi")
sweep = pd.DataFrame([dict(setup=name, draw=draw, points=points, seed=seed, **run(seed, tune_draw=draw, points=points, **kw))
                      for name, kw in [("k=10, 800 specs", {}), ("k=10, 200 specs", dict(tune_specs=200)), ("k=30, 800 specs", dict(k=30))]
                      for draw in (500, 600, 700) for points in (40, 80, 200) for seed in SEEDS])
print(sweep.pivot_table(index=["setup", "draw"], columns="points", values=["wrong_merges", "euros_per_record"], sort=False).round(3).to_string())
wide = sweep.pivot_table(index=["draw", "points", "seed"], columns="setup", values="euros_per_record")
diff = wide["k=30, 800 specs"] - wide["k=10, 800 specs"]
print("\nk=30 minus k=10, euros per record: mean difference by draw and points, then seeds of 5 where k=30 cost less")
print(diff.groupby(["draw", "points"]).mean().unstack().round(3).to_string())
print((diff < 0).groupby(["draw", "points"]).sum().unstack().to_string())
print(f"\nrecords {res.records.mean():.0f}, true interchangeable pairs {res.true_pairs.mean():.0f}")
