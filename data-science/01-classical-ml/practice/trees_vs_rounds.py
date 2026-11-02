# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scikit-learn", "lightgbm", "matplotlib"]
# ///
"""Measured figure for notes/06: forest and boosting as trees are added, on census income.

Run from this folder:
    uv run trees_vs_rounds.py

Adult, 80/20 stratified split with random_state=0, as in the note. Writes classical-trees-vs-rounds.png.
"""
# %%
from pathlib import Path

import numpy as np
import pandas as pd
import chartstyle as cs
import matplotlib.pyplot as plt
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

cols = ["age", "workclass", "fnlwgt", "education", "education_num", "marital", "occupation", "relationship", "race",
        "sex", "capital_gain", "capital_loss", "hours", "country", "income"]
adult = pd.read_csv(Path(__file__).parent / "intro-to-ml-in-python/data/adult.data", header=None, names=cols,
                    skipinitialspace=True, na_values="?")
y = (adult.income == ">50K").astype(int)
X = adult.drop(columns=["income", "fnlwgt", "education"])
for c in X.select_dtypes(exclude="number"):
    X[c] = X[c].astype("category")
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, stratify=y, random_state=0)
# Forests in scikit-learn need numbers: ordinal-coded categories, -1 for missing.
Xtr_n, Xte_n = Xtr.copy(), Xte.copy()
for c in Xtr.select_dtypes("category"):
    Xtr_n[c], Xte_n[c] = Xtr[c].cat.codes, Xte[c].cat.codes

rounds = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000]
gb = LGBMClassifier(n_estimators=max(rounds), learning_rate=.05, verbose=-1, n_jobs=4, random_state=0).fit(Xtr, ytr)
gb_auc = [roc_auc_score(yte, gb.predict_proba(Xte, num_iteration=n)[:, 1]) for n in rounds]
trees = [n for n in rounds if n <= 500]
rf_auc = []
rf = RandomForestClassifier(n_estimators=0, warm_start=True, n_jobs=4, random_state=0)
for n in trees:
    rf.n_estimators = n
    rf.fit(Xtr_n, ytr)
    rf_auc.append(roc_auc_score(yte, rf.predict_proba(Xte_n)[:, 1]))
for n, a in zip(rounds, gb_auc):
    print(f"boosting {n:5d} AUC {a:.4f}")
for n, a in zip(trees, rf_auc):
    print(f"forest   {n:5d} AUC {a:.4f}")
best = int(np.argmax(gb_auc))

# %%
cs.apply()
fig, ax = plt.subplots()
ax.plot(rounds, gb_auc, color=cs.BLUE, marker="o", ms=5, label="Boosting (LightGBM, rate 0.05)")
ax.plot(trees, rf_auc, color=cs.ORANGE, marker="o", ms=5, label="Random forest")
ax.set_xscale("log")
ax.set(xlabel="Trees (log scale)", ylabel="Test AUC", xticks=rounds, xticklabels=rounds, ylim=(.70, .94))
ax.minorticks_off()
ax.annotate(f"Boosting peaks at {gb_auc[best]:.3f} with {rounds[best]} trees", (rounds[best], gb_auc[best]), xytext=(0, 10), textcoords="offset points", ha="center")
ax.annotate(f"Boosting at 2000: {gb_auc[-1]:.3f}", (rounds[-1], gb_auc[-1]), xytext=(0, -16), textcoords="offset points", ha="right")
ax.annotate(f"Forest at 500: {rf_auc[-1]:.3f}", (trees[-1], rf_auc[-1]), xytext=(0, -16), textcoords="offset points", ha="center")
ax.legend(loc="lower right")
ax.set_title("A forest averages to a plateau; boosting climbs, then slips. Census income")
cs.save(fig, "classical-trees-vs-rounds.png")
