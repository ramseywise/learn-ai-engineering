# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scikit-learn", "matplotlib"]
# ///
"""Measured figure for notes/02: per-genre F1 on the movie-genre task, against each genre's share.

Run from this folder:
    uv run genre_f1.py

The note's split and grid. Share is the F1 a guesser gets by predicting a genre at its own rate.
Writes nlp-genre-f1.png.
"""
# %%
import json
from pathlib import Path

import numpy as np
import pandas as pd
import chartstyle as cs
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import make_pipeline

DATA = Path(__file__).parent / "text-analytics-with-python/Ch07 - Text Similarity and Clustering/tmdb_5000_movies.csv.gz"
movies = pd.read_csv(DATA)
movies["description"] = movies["tagline"].fillna("") + " " + movies["overview"].fillna("")
movies["genre_list"] = movies["genres"].map(lambda g: [x["name"] for x in json.loads(g)])
movies = movies[movies.genre_list.str.len() > 0].copy()
movies["genre"] = movies.genre_list.str[0]
top = movies.genre.value_counts().head(6).index
data = movies[movies.genre.isin(top)]
text_train, text_test, y_train, y_test = train_test_split(data.description, data.genre, test_size=.25, random_state=0, stratify=data.genre)
pipe = make_pipeline(TfidfVectorizer(min_df=2, sublinear_tf=True), LogisticRegression(max_iter=2000))
grid = GridSearchCV(pipe, {"logisticregression__C": [.1, 1, 10, 100], "tfidfvectorizer__ngram_range": [(1, 1), (1, 2), (1, 3)]},
                    cv=5, n_jobs=4, scoring="f1_macro").fit(text_train, y_train)
pred = grid.predict(text_test)
acc, macro = accuracy_score(y_test, pred), f1_score(y_test, pred, average="macro")
print(grid.best_params_, "accuracy", round(acc, 3), "macro-F1", round(macro, 3), "majority", round((y_test == y_train.mode()[0]).mean(), 3))
labels = list(pd.Series(y_test).value_counts().index)
f1 = f1_score(y_test, pred, labels=labels, average=None)
share = pd.Series(y_test).value_counts(normalize=True)[labels].to_numpy()
for l, f, s in zip(labels, f1, share):
    print(f"{l:<10} F1 {f:.3f} share {s:.3f}")

# %%
cs.apply()
fig, ax = plt.subplots()
ypos = np.arange(len(labels))[::-1]
ax.barh(ypos, f1, height=.55, color=cs.BLUE, label="F1 of the tuned model")
ax.scatter(share, ypos, marker="|", s=420, lw=2.5, color=cs.ORANGE, zorder=3, label="Genre's share of films (chance F1)")
for y, f in zip(ypos, f1):
    ax.annotate(f"{f:.2f}", (f, y), xytext=(5, 0), textcoords="offset points", va="center")
ax.set_yticks(ypos, labels)
ax.set(xlabel="F1 on 960 test films", xlim=(0, .8))
ax.grid(False, axis="y"); ax.grid(True, axis="x"); ax.tick_params(axis="y", length=0)
ax.legend(loc="lower right")
ax.set_title(f"Accuracy {acc:.3f}, macro-F1 {macro:.3f}: the average hides which genres are learnt")
cs.save(fig, "nlp-genre-f1.png")
