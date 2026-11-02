# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scikit-learn", "lightgbm", "matplotlib"]
# ///
"""Measured figure for notes/08: gain credits a useless ID; permutation on held-out data does not.

Run from this folder:
    uv run importance_noise.py

Adult with two planted columns of noise, seeds and split as in the note. Writes classical-importance-noise.png.
"""
# %%
from pathlib import Path

import numpy as np
import pandas as pd
import chartstyle as cs
import matplotlib.pyplot as plt
from lightgbm import LGBMClassifier, early_stopping
from sklearn.inspection import permutation_importance
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
rng = np.random.default_rng(0)
X["noise"] = rng.normal(size=len(X))
X["noisy_id"] = rng.integers(0, 5000, len(X)).astype(float)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, stratify=y, random_state=0)
X_tr, X_val, y_tr, y_val = train_test_split(X_train, y_train, test_size=.2, stratify=y_train, random_state=0)
model = LGBMClassifier(learning_rate=.05, n_estimators=2000, verbose=-1, n_jobs=4, random_state=0)
model.fit(X_tr, y_tr, eval_X=X_val, eval_y=y_val, callbacks=[early_stopping(50, verbose=False)])
print("rounds", model.best_iteration_, "test AUC", round(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]), 4))

gain = model.booster_.feature_importance("gain")
gain = pd.Series(gain / gain.sum(), index=X.columns)
perm = permutation_importance(model, X_test.iloc[:3000], y_test.iloc[:3000], scoring="roc_auc", n_repeats=5, random_state=0)
perm = pd.Series(perm.importances_mean, index=X.columns)
table = pd.DataFrame({"gain": gain, "perm": perm}).sort_values("gain", ascending=False)
print(table.round(4))

# %%
cs.apply()
show = table.head(6).index.tolist()
show += [c for c in ["noisy_id", "noise"] if c not in show]
t = table.loc[show[::-1]]
labels = {"noisy_id": "noisy_id (planted)", "noise": "noise (planted)"}
fig, axes = plt.subplots(1, 2, sharey=True)
for ax, col, name, colour in [(axes[0], "gain", "Share of split gain (training data)", cs.ORANGE),
                              (axes[1], "perm", "Permutation AUC drop (held-out data)", cs.BLUE)]:
    ax.barh([labels.get(i, i) for i in t.index], t[col], color=colour, height=.6)
    ax.set_title(name, fontsize=10)
    ax.grid(False, axis="y"); ax.grid(True, axis="x"); ax.tick_params(axis="y", length=0)
    for lab in ["noisy_id", "noise"]:
        v = table.loc[lab, col]
        ax.annotate(f"{v:.3f}" if col == "gain" else f"{v:.4f}", (max(v, 0), labels[lab]), xytext=(4, 0), textcoords="offset points", va="center")
fig.suptitle("Gain credits columns that cannot matter; permutation on held-out data does not", x=0.01, ha="left", fontweight="bold", fontsize=12)
cs.save(fig, "classical-importance-noise.png")
