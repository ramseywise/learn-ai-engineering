# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "scikit-learn", "torch", "matplotlib"]
# ///
"""Measured figure for notes/04: plain networks degrade with depth; residual ones do not.

Run from this folder:
    uv run depth_degradation.py

Block and deep() from the note, sklearn digits, 10 epochs, seed 0, adding depths the note does not print.
Writes dl-depth-degradation.png.
"""
# %%
import torch
import torch.nn as nn
import torch.nn.functional as F
import chartstyle as cs
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

digits = load_digits()
X_tr, X_te, y_tr, y_te = train_test_split(digits.data / 16.0, digits.target, test_size=.3, random_state=0, stratify=digits.target)
X_tr = torch.tensor(X_tr, dtype=torch.float32).reshape(-1, 1, 8, 8)
X_te = torch.tensor(X_te, dtype=torch.float32).reshape(-1, 1, 8, 8)
y_tr, y_te = torch.tensor(y_tr), torch.tensor(y_te)


def accuracy(model, X, y):
    model.eval()
    with torch.no_grad():
        return (model(X).argmax(1) == y).float().mean().item()


def run(model, epochs=10, lr=1e-3, seed=0, batch_size=32):
    torch.manual_seed(seed)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    loader = DataLoader(TensorDataset(X_tr, y_tr), batch_size=batch_size, shuffle=True, drop_last=True)
    for _ in range(epochs):
        model.train()
        for xb, yb in loader:
            loss = F.cross_entropy(model(xb), yb)
            opt.zero_grad(); loss.backward(); opt.step()
    return model


class Block(nn.Module):
    def __init__(self, c, residual):
        super().__init__()
        self.residual = residual
        self.f = nn.Sequential(nn.Conv2d(c, c, 3, padding=1), nn.BatchNorm2d(c), nn.ReLU(),
                               nn.Conv2d(c, c, 3, padding=1), nn.BatchNorm2d(c))

    def forward(self, x):
        out = self.f(x)
        return F.relu(out + x if self.residual else out)


def deep(blocks, residual, c=16):
    return nn.Sequential(nn.Conv2d(1, c, 3, padding=1), *[Block(c, residual) for _ in range(blocks)],
                         nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(c, 10))


blocks_list = [2, 5, 10, 20, 30]
curves = {False: [], True: []}
for blocks in blocks_list:
    for residual in [False, True]:
        torch.manual_seed(0)
        m = run(deep(blocks, residual))
        tr, te = accuracy(m, X_tr, y_tr), accuracy(m, X_te, y_te)
        curves[residual].append(tr)
        print(f"{2 * blocks + 2:>2} layers {'residual' if residual else 'plain   '} train {tr:.3f} test {te:.3f}", flush=True)

# %%
cs.apply()
layers = [2 * b + 2 for b in blocks_list]
fig, ax = plt.subplots()
ax.plot(layers, curves[True], color=cs.BLUE, marker="o", ms=6, label="Residual")
ax.plot(layers, curves[False], color=cs.ORANGE, marker="o", ms=6, label="Plain")
ax.annotate(f"{curves[True][-1]:.3f}", (layers[-1], curves[True][-1]), xytext=(0, -16), textcoords="offset points", ha="center")
ax.annotate(f"{curves[False][-1]:.3f}", (layers[-1], curves[False][-1]), xytext=(0, 9), textcoords="offset points", ha="center")
ax.set(xlabel="Layers", ylabel="Training accuracy after 10 epochs", ylim=(0, 1.05), xticks=layers)
ax.grid(False, axis="x")
ax.legend(loc="lower left")
ax.set_title("Deep plain networks fail on the training data itself. Digits, seed 0")
cs.save(fig, "dl-depth-degradation.png")
