# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scikit-learn", "lightgbm"]
# ///
"""The measured answers to the Try it section of notes/04. Run from this folder: uv run 04_matching_tryit.py"""
# %%
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lightgbm as lgb
import numpy as np
import pandas as pd

from matching import FEATURES, add_features, block, make_ledger, ndcg_at, top1

GBM = dict(num_leaves=15, learning_rate=.05, min_data_in_leaf=20, verbosity=-1, deterministic=True, force_row_wise=True,
           num_threads=4, objective="lambdarank", label_gain=[0, 1, 3])
DROPS = {"all features": [],
         "no reference": ["ref_digits"],
         "no name": ["name_sim", "name_rank"],
         "no amount": ["amount_rel_diff", "amount_exact", "amount_near", "amount_rank"],
         "no date": ["days_since_issue", "days_from_due"]}

# %% What each kind of evidence is worth
rows = []
for seed in range(5):
    inv, ln, lk = make_ledger(seed)
    p = add_features(block(inv, ln), inv, ln, lk)
    a, b = ln.day.quantile([.6, .8])
    tr = p[p.line.isin(ln[ln.day <= a].line)]
    te = p[p.line.isin(ln[ln.day > b].line)]
    tr = tr[tr.groupby("line").linked.transform("max") == 1].sort_values(["line", "invoice"])
    te = te[te.groupby("line").linked.transform("max") == 1]
    for name, drop in DROPS.items():
        cols = [f for f in FEATURES if f not in drop]
        ds = lgb.Dataset(tr[cols].to_numpy(float), label=tr.grade, group=tr.groupby("line", sort=False).size().to_numpy())
        model = lgb.train(dict(GBM, seed=seed), ds, 200)
        s = model.predict(te[cols].to_numpy(float))
        rows.append(dict(seed=seed, features=name, ndcg5=ndcg_at(te.grade.to_numpy(), s, te.line.to_numpy()),
                         top1=top1(te.linked.to_numpy(), s, te.line.to_numpy())))
tab = pd.DataFrame(rows).groupby("features", sort=False)[["ndcg5", "top1"]].mean()
print("LambdaMART with one kind of evidence removed, mean over five ledgers")
print(tab.round(4).to_string())

# %% How narrow can the date window go
inv, ln, lk = make_ledger(0)
print("\ndate window in days, candidates per line, recall of true links, seed 0")
for window in (30, 60, 90, 120, 180):
    p = block(inv, ln, window=window)
    kept = lk.merge(p[["line", "invoice"]], on=["line", "invoice"])
    print(f"{window:4d}  {len(p) / len(ln):6.1f}  {len(kept) / len(lk):.4f}")
