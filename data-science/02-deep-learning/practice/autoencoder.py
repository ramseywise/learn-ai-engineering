# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "scikit-learn", "torch", "matplotlib"]
# ///
"""Numbers and figure for notes/05: an autoencoder's bottleneck, denoising, and reconstruction error as an anomaly score.

Run from this folder (a minute or two):
    uv run autoencoder.py

Data: scikit-learn's bundled digits, 1,797 images of 8 by 8 pixels. Writes dl-autoencoder-bottleneck.png.
"""
# %%
import chartstyle as cs
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.metrics import roc_auc_score

torch.set_num_threads(4)
digits = load_digits()
X_all, y_all = (digits.data / 16).astype("float32"), digits.target
SEEDS = range(5)


def split(seed, hold=None):
    """A fixed-size test set. With hold set, that digit never reaches training and becomes the anomaly."""
    r = np.random.default_rng(seed)
    p = r.permutation(len(X_all))
    te, tr = p[:500], p[500:]
    if hold is not None:
        tr = tr[y_all[tr] != hold]
    return X_all[tr], X_all[te], y_all[te]


def make_ae(code, hidden=128):
    return nn.Sequential(nn.Linear(64, hidden), nn.ReLU(), nn.Linear(hidden, code), nn.ReLU(),
                         nn.Linear(code, hidden), nn.ReLU(), nn.Linear(hidden, 64), nn.Sigmoid())


def corrupt(x, nu, gen):
    """Vincent et al.'s corruption: set a random fraction nu of the inputs to zero."""
    return x * (torch.rand(x.shape, generator=gen) >= nu).float()


def fit(X, net, nu=0.0, epochs=300, seed=0, lr=2e-3):
    torch.manual_seed(seed)
    gen = torch.Generator().manual_seed(seed)
    for m in net:
        if hasattr(m, "reset_parameters"):
            m.reset_parameters()
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    x = torch.tensor(X)
    for _ in range(epochs):
        for b in torch.randperm(len(x), generator=gen).split(64):
            target = x[b]
            inp = corrupt(target, nu, gen) if nu else target
            loss = nn.functional.mse_loss(net(inp), target)
            opt.zero_grad(); loss.backward(); opt.step()
    return net.eval()


def recon(net, X):
    with torch.no_grad():
        return net(torch.tensor(X)).numpy()


def mse_per_image(a, b):
    return ((a - b) ** 2).sum(1)


# %% Bottleneck against PCA, squared error per image on held-out data
codes = [2, 4, 8, 16, 32]
table = {c: dict(ae=[], pca=[]) for c in codes}
for s in SEEDS:
    tr, te, _ = split(s)
    for c in codes:
        table[c]["ae"].append(mse_per_image(recon(fit(tr, make_ae(c), seed=s), te), te).mean())
        p = PCA(c, random_state=s).fit(tr)
        table[c]["pca"].append(mse_per_image(p.inverse_transform(p.transform(te)), te).mean())
print("held-out squared error per image, mean (sd) over five splits; pixels scaled 0 to 1, 64 pixels")
for c in codes:
    print(f"code {c:<3} autoencoder {np.mean(table[c]['ae']):.3f} ({np.std(table[c]['ae']):.3f})   PCA {np.mean(table[c]['pca']):.3f} ({np.std(table[c]['pca']):.3f})")


# %% Denoising: an overcomplete code, with and without corruption in training
def wide():
    """A hidden layer wider than the input: without noise, nothing stops it from copying."""
    return nn.Sequential(nn.Linear(64, 256), nn.ReLU(), nn.Linear(256, 64), nn.Sigmoid())


print("\nwide network with 256 hidden units, test images with 30% of pixels zeroed; error measured against the clean image")
res = {n: dict(clean=[], noisy=[], copy=[]) for n in ("Plain, trained on clean input", "Denoising, trained with 30% zeroed")}
for s in SEEDS:
    tr, te, _ = split(s)
    gen = torch.Generator().manual_seed(1000 + s)
    te_noisy = corrupt(torch.tensor(te), .3, gen).numpy()
    for name, nu in (("Plain, trained on clean input", 0.0), ("Denoising, trained with 30% zeroed", .3)):
        net = fit(tr, wide(), nu=nu, seed=s)
        res[name]["clean"].append(mse_per_image(recon(net, te), te).mean())
        out = recon(net, te_noisy)
        res[name]["noisy"].append(mse_per_image(out, te).mean())
        res[name]["copy"].append(mse_per_image(out, te_noisy).mean())
base = np.mean([mse_per_image(corrupt(torch.tensor(split(s)[1]), .3, torch.Generator().manual_seed(1000 + s)).numpy(), split(s)[1]).mean() for s in SEEDS])
print(f"doing nothing (the corrupted image as the answer): error {base:.3f}")
for k, v in res.items():
    print(f"{k:<36} clean input {np.mean(v['clean']):.3f}   corrupted input {np.mean(v['noisy']):.3f}   distance from the corrupted input {np.mean(v['copy']):.3f}")


# %% Reconstruction error as an anomaly score: hold each digit out in turn
print("\nAUC for spotting a digit never seen in training, mean over all ten digits, five splits each")
auc = {c: dict(ae=[], pca=[]) for c in codes}
per_digit = {}
for s in SEEDS:
    for hold in range(10):
        tr, te, yte = split(s, hold)
        y = (yte == hold).astype(int)
        for c in codes:
            e_ae = mse_per_image(recon(fit(tr, make_ae(c), seed=s, epochs=150), te), te)
            p = PCA(c, random_state=s).fit(tr)
            e_pca = mse_per_image(p.inverse_transform(p.transform(te)), te)
            auc[c]["ae"].append(roc_auc_score(y, e_ae))
            auc[c]["pca"].append(roc_auc_score(y, e_pca))
            if c == 16:
                per_digit.setdefault(hold, []).append(roc_auc_score(y, e_ae))
    print("split", s, "done", flush=True)
for c in codes:
    print(f"code {c:<3} autoencoder {np.mean(auc[c]['ae']):.3f} (sd over runs {np.std(auc[c]['ae']):.3f})   PCA {np.mean(auc[c]['pca']):.3f} (sd {np.std(auc[c]['pca']):.3f})")
print("by held-out digit at code 16, autoencoder:", {d: round(float(np.mean(v)), 3) for d, v in sorted(per_digit.items())})

# %% Figure
cs.apply()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4))
x = range(len(codes))
a1.plot(x, [np.mean(table[c]["ae"]) for c in codes], color=cs.BLUE, marker="o", ms=6, label="Autoencoder")
a1.plot(x, [np.mean(table[c]["pca"]) for c in codes], color=cs.ORANGE, marker="o", ms=6, label="PCA")
a1.set_xticks(list(x), codes)
a1.set(xlabel="Size of the code", ylabel="Squared error per image", title="A wider code reconstructs better", ylim=(0, None))
a1.legend(loc="upper right")
a1.grid(False, axis="x")
a2.plot(x, [np.mean(auc[c]["ae"]) for c in codes], color=cs.BLUE, marker="o", ms=6)
a2.plot(x, [np.mean(auc[c]["pca"]) for c in codes], color=cs.ORANGE, marker="o", ms=6)
a2.set_xticks(list(x), codes)
a2.set(xlabel="Size of the code", ylabel="AUC for an unseen digit", title="Spotting what it never saw", ylim=(.5, 1))
a2.grid(False, axis="x")
cs.save(fig, "dl-autoencoder-bottleneck.png")
