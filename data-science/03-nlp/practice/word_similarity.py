# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy<2", "scipy<1.14", "gensim", "matplotlib"]
# ///
"""Measured figure for notes/04: cosine between word pairs in GloVe. One-hot vectors give 0 for all of them.

Run from this folder:
    uv run word_similarity.py

Uses the 50-dimensional GloVe vectors, fetched once to ~/.cache/learn-ai-engineering, as in the note.
Writes nlp-word-similarity.png.
"""
# %%
import urllib.request
from pathlib import Path

import numpy as np
import chartstyle as cs
import matplotlib.pyplot as plt
from gensim.models import KeyedVectors

CACHE = Path.home() / ".cache/learn-ai-engineering"
CACHE.mkdir(parents=True, exist_ok=True)
path = CACHE / "glove-wiki-gigaword-50.gz"
if not path.exists():
    urllib.request.urlretrieve("https://github.com/RaRe-Technologies/gensim-data/releases/download/glove-wiki-gigaword-50/glove-wiki-gigaword-50.gz", path)
glove = KeyedVectors.load_word2vec_format(path, binary=False, limit=100_000)


def cos(a, b):
    u, v = glove[a], glove[b]
    return float(u @ v / (np.linalg.norm(u) * np.linalg.norm(v)))


pairs = [("hotel", "motel"), ("good", "bad"), ("king", "queen"), ("car", "truck"), ("hotel", "banana"), ("king", "banana")]
vals = [(f"{a} / {b}", cos(a, b)) for a, b in pairs]
vals.sort(key=lambda t: t[1])
for n, v in vals:
    print(f"{n:<18} {v:.3f}")

# %%
cs.apply()
fig, ax = plt.subplots()
ax.barh([n for n, _ in vals], [v for _, v in vals], height=.55, color=cs.BLUE, label="GloVe 50-d")
ax.scatter([0] * len(vals), range(len(vals)), s=40, color=cs.ORANGE, edgecolor=cs.SURFACE, lw=1, zorder=3, label="One-hot: 0 for every pair")
for i, (_, v) in enumerate(vals):
    ax.annotate(f"{v:.2f}", (v, i), xytext=(5, 0), textcoords="offset points", va="center")
ax.axvline(0, color=cs.BASELINE, lw=1)
ax.set(xlabel="Cosine similarity", xlim=(min(0, min(v for _, v in vals)) - .05, 1.05))
ax.grid(False, axis="y"); ax.grid(True, axis="x"); ax.tick_params(axis="y", length=0)
ax.legend(loc="lower right")
ax.set_title("One-hot rates every pair 0. GloVe separates them, and puts good near bad")
cs.save(fig, "nlp-word-similarity.png")
