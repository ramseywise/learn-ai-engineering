# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "scikit-learn", "matplotlib"]
# ///
"""Measured figure for notes/06: how a decision tree's gap between train and test opens with depth.

Run from this folder:
    uv run overfit_curve.py

Breast cancer data, 20 stratified splits (seeds 0 to 19). Writes classical-overfit-curve.png.
"""
# %%
import numpy as np
import chartstyle as cs
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
depths = list(range(1, 11))
train, test = np.zeros((20, len(depths))), np.zeros((20, len(depths)))
for s in range(20):
    Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=s)
    for j, d in enumerate(depths):
        m = DecisionTreeClassifier(max_depth=d, random_state=0).fit(Xtr, ytr)
        train[s, j], test[s, j] = m.score(Xtr, ytr), m.score(Xte, yte)
trm, tem, tes = train.mean(0), test.mean(0), test.std(0)
for d, a, b, sd in zip(depths, trm, tem, tes):
    print(f"depth {d:2d} train {a:.3f} test {b:.3f} (sd {sd:.3f}) gap {a-b:.3f}")

# The note's split, unstratified in the note's own phrasing, for comparison with 0.881.
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
m = DecisionTreeClassifier(random_state=0).fit(Xtr, ytr)
print("note split, unlimited depth:", round(m.score(Xtr, ytr), 3), round(m.score(Xte, yte), 3))

# %%
cs.apply()
fig, ax = plt.subplots()
ax.plot(depths, trm, color=cs.BLUE, marker="o", ms=5, label="Train")
ax.plot(depths, tem, color=cs.ORANGE, marker="o", ms=5, label="Test")
ax.fill_between(depths, tem - tes, tem + tes, color=cs.ORANGE, alpha=.15, lw=0)
best = int(np.argmax(tem))
ax.annotate(f"{trm[-1]:.3f} train", (depths[-1], trm[-1]), xytext=(-4, -14), textcoords="offset points", ha="right", color=cs.INK)
ax.annotate(f"{tem[-1]:.3f} test", (depths[-1], tem[-1]), xytext=(-4, -16), textcoords="offset points", ha="right", color=cs.INK)
ax.annotate(f"Best test {tem[best]:.3f} at depth {depths[best]}", (depths[best], tem[best]), xytext=(0, -30), textcoords="offset points", ha="center", color=cs.INK,
            arrowprops=dict(arrowstyle="-", color=cs.MUTED, lw=.7))
ax.set(xlabel="Maximum tree depth", ylabel="Accuracy", xticks=depths, ylim=(.88, 1.01))
ax.legend(loc="lower right", ncol=2)
ax.set_title("Train keeps improving; test stops. Tree on breast cancer, 20 splits (band: ±1 sd)")
cs.save(fig, "classical-overfit-curve.png")
