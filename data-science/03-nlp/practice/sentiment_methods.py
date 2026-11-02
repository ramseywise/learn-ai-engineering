# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "pyarrow", "scikit-learn", "nltk", "afinn", "textblob", "matplotlib"]
# ///
"""Measured figure for notes/06: lexicons against a supervised baseline, on the same 1,500 IMDb reviews.

Run from this folder (about three minutes):
    uv run sentiment_methods.py

Thresholds tuned on 1,500 training reviews (seed 1), test sample seed 0, as in the note. Writes nlp-sentiment-methods.png.
"""
# %%
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import chartstyle as cs
import matplotlib.pyplot as plt
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline

for pkg in ["vader_lexicon", "sentiwordnet", "wordnet", "punkt", "punkt_tab", "averaged_perceptron_tagger_eng"]:
    nltk.download(pkg, quiet=True)
from afinn import Afinn
from nltk.corpus import sentiwordnet as swn
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob

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
sample = test_df.sample(5000, random_state=0)
tune = train_df.sample(1500, random_state=1)
afn, vader = Afinn(emoticons=True), SentimentIntensityAnalyzer()


def swn_score(text):
    pos = neg = n = 0
    for word, tag in nltk.pos_tag(nltk.word_tokenize(text[:1500])):
        wn_pos = {"NN": "n", "VB": "v", "JJ": "a", "RB": "r"}.get(tag[:2])
        synsets = list(swn.senti_synsets(word, wn_pos)) if wn_pos else []
        if synsets:
            pos += synsets[0].pos_score(); neg += synsets[0].neg_score(); n += 1
    return (pos - neg) / max(n, 1)


scorers = {"AFINN": afn.score, "VADER": lambda t: vader.polarity_scores(t)["compound"],
           "TextBlob": lambda t: TextBlob(t).sentiment.polarity, "SentiWordNet": swn_score}
y = sample.label.iloc[:1500]
results = {}
for name, score in scorers.items():
    s, t = sample.text.iloc[:1500].map(score), tune.text.map(score)
    grid = np.quantile(t, np.linspace(.1, .9, 33))
    best = grid[np.argmax([((t >= g) == tune.label).mean() for g in grid])]
    results[name] = accuracy_score(y, s >= best)
    print(f"{name:<13} tuned threshold {best:6.2f} accuracy {results[name]:.3f}", flush=True)
pipe = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True), LogisticRegression(C=10, max_iter=1000)).fit(train_df.text, train_df.label)
full = accuracy_score(test_df.label, pipe.predict(test_df.text))
results["TF-IDF + logistic (25,000 labels)"] = accuracy_score(y, pipe.predict(sample.text.iloc[:1500]))
print("TF-IDF accuracy on the 1,500:", round(results["TF-IDF + logistic (25,000 labels)"], 3), "on all 25,000 test:", round(full, 3))

# %%
cs.apply()
fig, ax = plt.subplots()
items = sorted(results.items(), key=lambda kv: kv[1])
colours = [cs.BLUE if k.startswith("TF-IDF") else cs.MUTED for k, _ in items]
ax.barh([k for k, _ in items], [v for _, v in items], height=.55, color=colours)
ax.axvline(.5, color=cs.SECONDARY, lw=1, ls="--")
ax.annotate("Coin flip", (.5, 4.42), xytext=(4, 0), textcoords="offset points", color=cs.SECONDARY, va="center")
for i, (_, v) in enumerate(items):
    ax.annotate(f"{v:.3f}", (v, i), xytext=(5, 0), textcoords="offset points", va="center")
ax.set(xlabel="Accuracy on the same 1,500 test reviews", xlim=(0, 1))
ax.grid(False, axis="y"); ax.grid(True, axis="x"); ax.tick_params(axis="y", length=0)
ax.set_title("Dictionaries beat a coin with no labels; labels buy about 15 points more")
cs.save(fig, "nlp-sentiment-methods.png")
