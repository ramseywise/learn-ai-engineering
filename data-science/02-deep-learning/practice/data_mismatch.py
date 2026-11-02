# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "scikit-learn", "torch", "matplotlib"]
# ///
"""Measured figure for notes/03: the four-error diagnostic when deployment data differs from training.

Run from this folder:
    uv run data_mismatch.py

Clean digits for training, shifted and noisy digits as dev and test, as in the note, plus the same
experiment with training-side corruption added. Writes dl-data-mismatch.png.
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
X_all, X_hold, y_all, y_hold = train_test_split(d.data / 16.0, d.target, test_size=.3, random_state=0, stratify=d.target)
X_all = torch.tensor(X_all, dtype=torch.float32); y_all = torch.tensor(y_all)
X_hold = torch.tensor(X_hold, dtype=torch.float32); y_hold = torch.tensor(y_hold)


def run(model, X, y, epochs=30, lr=1e-3, seed=0, batch_size=32):
    torch.manual_seed(seed)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    loader = DataLoader(TensorDataset(X, y), batch_size=batch_size, shuffle=True, drop_last=len(X) > batch_size)
    for _ in range(epochs):
        model.train()
        for xb, yb in loader:
            loss = F.cross_entropy(model(xb), yb)
            opt.zero_grad(); loss.backward(); opt.step()
    return model


def mlp(h=64):
    return nn.Sequential(nn.Linear(64, h), nn.ReLU(), nn.Linear(h, 10))


def error(model, X, y):
    model.eval()
    with torch.no_grad():
        return 100 * (model(X).argmax(1) != y).float().mean().item()


def corrupt(X, seed=0):
    g = torch.Generator().manual_seed(seed)
    imgs = X.reshape(-1, 8, 8)
    imgs = torch.roll(imgs, shifts=1, dims=2)
    imgs = (imgs + .25 * torch.randn(imgs.shape, generator=g)).clamp(0, 1)
    return imgs.reshape(-1, 64)


perm = torch.randperm(len(X_all), generator=torch.Generator().manual_seed(0))
X_train, y_train = X_all[perm[:1000]], y_all[perm[:1000]]
X_tdev, y_tdev = X_all[perm[1000:]], y_all[perm[1000:]]
X_dev, y_dev = corrupt(X_hold[:270]), y_hold[:270]
X_test, y_test = corrupt(X_hold[270:], seed=1), y_hold[270:]


def report(name, m):
    e = [error(m, X_train, y_train), error(m, X_tdev, y_tdev), error(m, X_dev, y_dev), error(m, X_test, y_test)]
    print(f"{name:<26}", " ".join(f"{v:5.2f}" for v in e))
    return e


torch.manual_seed(0)
clean = report("clean training only", run(mlp(), X_train, y_train))
X_aug = torch.cat([X_train, corrupt(X_train, seed=2)])
y_aug = torch.cat([y_train, y_train])
torch.manual_seed(0)
aug = report("plus synthetic corruption", run(mlp(), X_aug, y_aug))

# %%
cs.apply()
fig, ax = plt.subplots()
names = ["Train", "Train-dev", "Dev", "Test"]
ax.plot(names, clean, color=cs.ORANGE, marker="o", ms=7, label="Clean training only")
ax.plot(names, aug, color=cs.BLUE, marker="o", ms=7, label="Plus synthetic corruption")
for j, (a, b) in enumerate(zip(clean, aug)):
    if j >= 2:
        ax.annotate(f"{a:.1f}%", (j, a), xytext=(0, 9), textcoords="offset points", ha="center")
        ax.annotate(f"{b:.1f}%", (j, b), xytext=(0, 9), textcoords="offset points", ha="center")
ax.set(ylabel="Error (%)", ylim=(0, 75))
ax.grid(False, axis="x")
ax.legend(loc="upper left")
ax.set_title("The jump sits between train-dev and dev: that is mismatch, not variance")
cs.save(fig, "dl-data-mismatch.png")
