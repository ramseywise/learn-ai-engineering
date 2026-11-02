# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "scikit-learn", "torch", "matplotlib"]
# ///
"""Measured figure for notes/02: sweep the learning rate by factors of ten.

Run from this folder:
    uv run lr_sweep.py

MLP on sklearn digits, Adam, 10 epochs, seeds 0 to 2, as in the note. Writes dl-lr-sweep.png.
"""
# %%
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import chartstyle as cs
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

d = load_digits()
X_tr, X_te, y_tr, y_te = train_test_split(d.data / 16.0, d.target, test_size=.3, random_state=0, stratify=d.target)
X_tr, X_te = torch.tensor(X_tr, dtype=torch.float32), torch.tensor(X_te, dtype=torch.float32)
y_tr, y_te = torch.tensor(y_tr), torch.tensor(y_te)


def accuracy(model, X, y):
    model.eval()
    with torch.no_grad():
        return (model(X).argmax(1) == y).float().mean().item()


def run(model, lr, epochs=10, batch_size=32, seed=0):
    torch.manual_seed(seed)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loader = DataLoader(TensorDataset(X_tr, y_tr), batch_size=batch_size, shuffle=True, drop_last=True)
    for _ in range(epochs):
        model.train()
        for xb, yb in loader:
            loss = F.cross_entropy(model(xb), yb)
            opt.zero_grad(); loss.backward(); opt.step()
    return model


def mlp(hidden=64, depth=2):
    layers, n = [], 64
    for _ in range(depth):
        layers += [nn.Linear(n, hidden), nn.ReLU()]
        n = hidden
    return nn.Sequential(*layers, nn.Linear(n, 10))


lrs = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0]
torch.manual_seed(0)  # run() reseeds after each model is built, so only the first model needs this
res = np.array([[accuracy(run(mlp(), lr, seed=s), X_te, y_te) for s in range(3)] for lr in lrs])
for lr, r in zip(lrs, res):
    print(f"lr {lr:<7} mean {r.mean():.3f} seeds {np.round(r, 3)}")

# %%
cs.apply()
fig, ax = plt.subplots()
m = res.mean(1)
ax.plot(lrs, m, color=cs.BLUE, marker="o", ms=6, zorder=3)
for j in range(3):
    ax.scatter(lrs, res[:, j], s=14, color=cs.MUTED, zorder=2, label="Each seed" if j == 0 else None)
ax.set_xscale("log")
ax.set(xlabel="Learning rate (log scale)", ylabel="Test accuracy after 10 epochs", ylim=(0, 1.05), xticks=lrs, xticklabels=["0.00001", "0.0001", "0.001", "0.01", "0.1", "1"])
ax.minorticks_off()
offs = [(10, 0, "left"), (10, -2, "left"), (0, 10, "center"), (0, 10, "center"), (10, 4, "left"), (-10, 4, "right")]
for x, y, (dx, dy, ha) in zip(lrs, m, offs):
    ax.annotate(f"{y:.3f}", (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center" if dy in (0, -2, 4) else "bottom")
ax.legend(loc="upper left")
ax.set_title("Too low has not finished; too high never settles. Digits, three seeds")
cs.save(fig, "dl-lr-sweep.png")
