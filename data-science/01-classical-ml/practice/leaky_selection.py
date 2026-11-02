# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "scikit-learn", "matplotlib"]
# ///
"""Measured figure for notes/03: selecting features before the split finds signal in pure noise.

Run from this folder:
    uv run leaky_selection.py

X and y are independent noise, 100 rows by 10,000 columns. Repeats the note's seed 42 and nine more.
Writes classical-leaky-selection.png.
"""
# %%
import numpy as np
import chartstyle as cs
import matplotlib.pyplot as plt
from sklearn.feature_selection import SelectPercentile, f_regression
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline

seeds = [42] + list(range(1, 10))
rows = []
for s in seeds:
    rnd = np.random.RandomState(s)
    X, y = rnd.normal(size=(100, 10000)), rnd.normal(size=100)
    leaky_X = SelectPercentile(f_regression, percentile=5).fit_transform(X, y)
    leaky = cross_val_score(Ridge(), leaky_X, y, cv=5).mean()
    clean = cross_val_score(make_pipeline(SelectPercentile(f_regression, percentile=5), Ridge()), X, y, cv=5).mean()
    rows.append((s, leaky, clean))
    print(f"seed {s:2d} leaky {leaky:.3f} pipeline {clean:.3f}")
r = np.array(rows)
print("mean leaky", r[:, 1].mean().round(3), "mean pipeline", r[:, 2].mean().round(3))

# %%
cs.apply()
fig, ax = plt.subplots()
ax.axhline(0, color=cs.BASELINE, lw=1)
rng = np.random.default_rng(0)
for k, (name, col, colour) in enumerate([("Select, then cross-validate", 1, cs.ORANGE), ("Selection inside the pipeline", 2, cs.BLUE)]):
    xs = k + rng.uniform(-.07, .07, len(r))
    ax.scatter(xs, r[:, col], s=50, color=colour, edgecolor=cs.SURFACE, lw=1.2, zorder=3, label=name)
    m = r[:, col].mean()
    ax.plot([k - .2, k + .2], [m, m], color=cs.INK, lw=1.5, zorder=4)
    ax.annotate(f"Mean R² {m:.2f}", (k + .22, m), va="center", color=cs.INK)
ax.set(xticks=[0, 1], xticklabels=["Select, then cross-validate", "Selection inside the pipeline"], xlim=(-.5, 1.7), ylabel="Cross-validated R²")
ax.grid(False, axis="x")
ax.set_title("X and y are pure noise: ten datasets, the same model, one line moved")
cs.save(fig, "classical-leaky-selection.png")
