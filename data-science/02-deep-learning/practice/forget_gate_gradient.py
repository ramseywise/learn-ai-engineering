# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "scikit-learn", "torch", "matplotlib"]
# ///
"""Measured figure for notes/05: gradient from each input step back through 50 steps, before training.

Run from this folder:
    uv run forget_gate_gradient.py

Reader and memory_net from the note, seed 0. Writes dl-forget-gate-gradient.png.
"""
# %%
import numpy as np
import torch
import torch.nn as nn
import chartstyle as cs
import matplotlib.pyplot as plt


class Reader(nn.Module):
    def __init__(self, cell, inp=8, hidden=64, classes=10):
        super().__init__()
        self.rnn = {"rnn": nn.RNN, "gru": nn.GRU, "lstm": nn.LSTM}[cell](inp, hidden, batch_first=True)
        self.out = nn.Linear(hidden, classes)

    def forward(self, x):
        outputs, _ = self.rnn(x)
        return self.out(outputs[:, -1])


def memory_net(cell, forget_bias=0.0, h=32):
    m = Reader(cell, inp=1, hidden=h, classes=2)
    if forget_bias:
        for name, q in m.rnn.named_parameters():
            if "bias" in name:
                nn.init.zeros_(q)
            if name == "bias_hh_l0":
                q.data[h:2 * h] = forget_bias
    return m


variants = [("rnn", 0.0, "Plain RNN", cs.MUTED), ("lstm", 0.0, "LSTM, forget bias 0", cs.ORANGE),
            ("lstm", 1.0, "LSTM, forget bias 1", cs.AQUA), ("lstm", 2.0, "LSTM, forget bias 2", cs.BLUE)]
cs.apply()
fig, ax = plt.subplots()
for cell, fb, name, colour in variants:
    torch.manual_seed(0)
    m = memory_net(cell, fb)
    x = torch.randn(1, 50, 1, requires_grad=True)
    m(x)[0, 0].backward()
    g = x.grad.abs().flatten().numpy()
    print(f"{name:<22} t=49 {g[49]:.1e} t=25 {g[25]:.1e} t=0 {g[0]:.1e}")
    ax.plot(np.arange(50), g, color=colour, label=f"{name}: {g[0]:.0e} at step 0".replace("e-0", "e-").replace("e+0", "e+"))
ax.set_yscale("log")
ax.set(xlabel="Input step t (the output reads step 49)", ylabel="|d output / d x_t| (log scale)", xlim=(0, 49))
ax.minorticks_off()
ax.grid(False, axis="x")
ax.legend(loc="lower right")
ax.set_title("Before training, only a forget bias keeps the first step reachable")
cs.save(fig, "dl-forget-gate-gradient.png")
