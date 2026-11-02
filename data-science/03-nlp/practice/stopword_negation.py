# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "pyarrow", "scikit-learn", "matplotlib"]
# ///
"""Measured figure for notes/06: what a stop-word list does to negation.

Run from this folder (about two minutes):
    uv run stopword_negation.py

IMDb, 25,000 train and 25,000 test, fetched once to ~/.cache/learn-ai-engineering, the note's bigram
TF-IDF and logistic regression with and without stop_words="english". Writes nlp-stopword-negation.png.
"""
# %%
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import chartstyle as cs
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline

CACHE = Path.home() / ".cache/learn-ai-engineering"
CACHE.mkdir(parents=True, exist_ok=True)
BASE = "https://huggingface.co/datasets/stanfordnlp/imdb/resolve/main/plain_text/"


def load(split):
    path = CACHE / f"imdb-{split}.parquet"
    if not path.exists():
        urllib.request.urlretrieve(f"{BASE}{split}-00000-of-00001.parquet", path)
    df = pd.read_parquet(path)
    df["text"] = df.text.str.replace("<br />", " ", regex=False)
    return df


train_df, test_df = load("train"), load("test")
y_train, y_test = train_df.label.to_numpy(), test_df.label.to_numpy()
tests = ["not good", "this film is not good", "not a good film"]
out = {}
for name, kw in [("kept", {}), ("removed", {"stop_words": "english"})]:
    pipe = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, **kw), LogisticRegression(C=10, max_iter=1000)).fit(train_df.text, y_train)
    acc = accuracy_score(y_test, pipe.predict(test_df.text))
    p = pipe.predict_proba(tests)[:, 1]
    out[name] = (acc, p)
    print(name, "accuracy", round(acc, 3), "probabilities", p.round(2), "'not good' in vocab:", "not good" in pipe[0].vocabulary_, flush=True)

# %%
cs.apply()
fig, ax = plt.subplots()
ypos = np.arange(len(tests))[::-1]
for k, (name, colour, label) in enumerate([("kept", cs.BLUE, "Stop words kept"), ("removed", cs.ORANGE, "Stop words removed")]):
    acc, p = out[name]
    ax.barh(ypos + (.19 if k == 0 else -.19), p, height=.34, color=colour, label=f"{label} (test accuracy {acc:.3f})")
    for y, v in zip(ypos, p):
        ax.annotate(f"{v:.2f}", (v, y + (.19 if k == 0 else -.19)), xytext=(4, 0), textcoords="offset points", va="center")
ax.axvline(.5, color=cs.BASELINE, lw=1)
ax.set_yticks(ypos, [f'"{t}"' for t in tests])
ax.set(xlabel="Predicted probability the text is positive", xlim=(0, 1.08))
ax.grid(False, axis="y"); ax.grid(True, axis="x"); ax.tick_params(axis="y", length=0)
ax.legend(loc="upper center", bbox_to_anchor=(.5, -.14), ncol=2)
ax.set_title("Remove stop words and \"not good\" becomes good. Accuracy barely shows it")
cs.save(fig, "nlp-stopword-negation.png")
