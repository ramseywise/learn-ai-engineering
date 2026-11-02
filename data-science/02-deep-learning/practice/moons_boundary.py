# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "scikit-learn", "matplotlib"]
# ///
"""Measured figure for notes/01: the same data, with and without a hidden layer.

Run from this folder:
    uv run moons_boundary.py

NumPy backprop from the note: make_moons(600, noise=0.2, random_state=0), the first 400 points train,
init seed 0, 3000 steps at rate 0.5. Writes dl-moons-boundary.png.
"""
# %%
import numpy as np
import chartstyle as cs
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.datasets import make_moons


def layer_forward(A_prev, W, b, activation):
    Z = W @ A_prev + b
    A = np.maximum(0, Z) if activation == "relu" else 1 / (1 + np.exp(-Z))
    return A, (A_prev, W, b, Z)


def layer_backward(dA, cache, activation):
    A_prev, W, b, Z = cache
    m = A_prev.shape[1]
    if activation == "relu":
        dZ = dA * (Z > 0)
    else:
        s = 1 / (1 + np.exp(-Z)); dZ = dA * s * (1 - s)
    return W.T @ dZ, dZ @ A_prev.T / m, dZ.sum(axis=1, keepdims=True) / m


def init(sizes, seed=0):
    rng = np.random.default_rng(seed)
    p = {}
    for l in range(1, len(sizes)):
        p[f"W{l}"] = rng.standard_normal((sizes[l], sizes[l-1])) * np.sqrt(2 / sizes[l-1])
        p[f"b{l}"] = np.zeros((sizes[l], 1))
    return p


def forward(X, p):
    L, A, caches = len(p) // 2, X, []
    for l in range(1, L + 1):
        A, c = layer_forward(A, p[f"W{l}"], p[f"b{l}"], "sigmoid" if l == L else "relu")
        caches.append(c)
    return A, caches


def backward(A, Y, caches):
    L, grads = len(caches), {}
    A = np.clip(A, 1e-9, 1 - 1e-9)
    dA = (A - Y) / (A * (1 - A))
    for l in range(L, 0, -1):
        dA, grads[f"dW{l}"], grads[f"db{l}"] = layer_backward(dA, caches[l-1], "sigmoid" if l == L else "relu")
    return grads


Xm, ym = make_moons(600, noise=0.2, random_state=0)
X, Y = Xm[:400].T, ym[:400].reshape(1, -1)
X_te, Y_te = Xm[400:].T, ym[400:].reshape(1, -1)


def fit(sizes, steps=3000, lr=.5):
    p = init(sizes)
    for _ in range(steps):
        A, caches = forward(X, p)
        g = backward(A, Y, caches)
        for l in range(1, len(p) // 2 + 1):
            p[f"W{l}"] -= lr * g[f"dW{l}"]
            p[f"b{l}"] -= lr * g[f"db{l}"]
    return p


# %%
cs.apply()
fig, axes = plt.subplots(1, 2, sharex=True, sharey=True)
gx, gy = np.meshgrid(np.linspace(-2, 3, 300), np.linspace(-1.5, 2, 220))
grid = np.c_[gx.ravel(), gy.ravel()].T
for ax, sizes, name in [(axes[0], [2, 1], "No hidden layer"), (axes[1], [2, 8, 1], "One hidden layer of 8")]:
    p = fit(sizes)
    acc = ((forward(X_te, p)[0] > .5) == Y_te).mean()
    print(sizes, "test accuracy", round(float(acc), 3))
    z = (forward(grid, p)[0] > .5).reshape(gx.shape)
    ax.contourf(gx, gy, z, levels=[-.5, .5, 1.5], cmap=ListedColormap(["#fbe3da", "#d9e8fa"]))
    ax.contour(gx, gy, z, levels=[.5], colors=cs.SECONDARY, linewidths=1)
    for k, colour in [(0, cs.ORANGE), (1, cs.BLUE)]:
        s = Y_te[0] == k
        ax.scatter(X_te[0][s], X_te[1][s], s=16, color=colour, edgecolor=cs.SURFACE, lw=.5, label=f"Class {k}")
    ax.set_title(f"{name}: test accuracy {acc:.3f}", fontsize=11)
    ax.grid(False)
    ax.set(xticks=[], yticks=[])
    for sp in ax.spines.values():
        sp.set_visible(False)
axes[1].legend(loc="lower right", ncol=2, frameon=True, facecolor=cs.SURFACE, edgecolor="none")
fig.suptitle("A straight boundary is the ceiling; a hidden layer removes it. 200 held-out points", x=.01, ha="left", fontweight="bold", fontsize=12)
cs.save(fig, "dl-moons-boundary.png")
