# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy<2", "scipy<1.14", "pandas", "gensim", "nltk", "matplotlib"]
# ///
"""Measured figure for notes/03: does coherence pick a number of topics? Three seeds per k.

Run from this folder (several minutes):
    uv run topic_coherence.py

The note's film descriptions and LDA settings, with seeds 1 and 2 added to its seed 0.
Writes nlp-topic-coherence.png.
"""
# %%
import re
from pathlib import Path

import numpy as np
import pandas as pd
import chartstyle as cs
import matplotlib.pyplot as plt
import nltk
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel, LdaModel

nltk.download("stopwords", quiet=True)
from nltk.corpus import stopwords

movies = pd.read_csv(Path(__file__).parent / "text-analytics-with-python/Ch07 - Text Similarity and Clustering/tmdb_5000_movies.csv.gz")
movies["description"] = movies["tagline"].fillna("") + " " + movies["overview"].fillna("")
movies = movies[movies.description.str.len() > 20].sort_values("popularity", ascending=False).reset_index(drop=True)
stop = set(stopwords.words("english"))


def tidy(text):
    return " ".join(w for w in re.sub(r"[^a-z\s]", " ", text.lower()).split() if w not in stop and len(w) > 2)


tokens = [d.split() for d in movies.description.map(tidy)]
dictionary = Dictionary(tokens)
dictionary.filter_extremes(no_below=5, no_above=.4)
bow = [dictionary.doc2bow(t) for t in tokens]
ks, seeds = [5, 10, 20, 40], [0, 1, 2]
res = np.zeros((len(ks), len(seeds)))
for i, k in enumerate(ks):
    for j, s in enumerate(seeds):
        model = LdaModel(corpus=bow, id2word=dictionary, num_topics=k, passes=8, random_state=s)
        res[i, j] = CoherenceModel(model=model, texts=tokens, dictionary=dictionary, coherence="c_v", processes=1).get_coherence()
        print(f"k={k} seed={s} c_v={res[i, j]:.3f}", flush=True)
print("means", dict(zip(ks, res.mean(1).round(3))))

# %%
cs.apply()
fig, ax = plt.subplots()
m = res.mean(1)
x = np.arange(len(ks))
ax.plot(x, m, color=cs.BLUE, marker="o", ms=7, label="Mean of three seeds", zorder=3)
for j in range(len(seeds)):
    ax.scatter(x, res[:, j], s=20, color=cs.MUTED, zorder=2, label="Each seed" if j == 0 else None)
for xi, v in zip(x, m):
    ax.annotate(f"{v:.3f}", (xi, v), xytext=(10, 0), textcoords="offset points", va="center")
ax.set_xticks(x, ks)
ax.set(xlabel="Number of topics", ylabel="Coherence c_v", ylim=(.25, .42), xlim=(-.3, 3.5))
ax.grid(False, axis="x")
ax.legend(loc="upper right")
ax.set_title("No knee: coherence moves about as much between seeds as between sizes")
cs.save(fig, "nlp-topic-coherence.png")
