# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "scipy", "scikit-learn", "torch", "sentence-transformers>=6,<7"]
# ///
"""The Try it numbers in notes/05: the same training at three temperatures. Run with `uv run 05_similarity_tryit.py`, about four minutes on an Apple M4 Pro GPU."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from parts_catalogue import make_catalogue
from similarity_train import SEEDS, encode, evaluate, labelled_pairs, train

rows = []
for seed in SEEDS:
    train_records, _ = make_catalogue(seed)
    test_records, test_parts = make_catalogue(seed + 1000)
    pairs, groups = labelled_pairs(train_records, 1000, np.random.default_rng(seed))
    for temperature in (.05, .2, 1.0):
        model, _ = train(train_records, pairs, groups, seed, temperature=temperature)
        rows.append(dict(seed=seed, temperature=temperature, **evaluate(encode(model, test_records.text), test_records, test_parts)))
        del model
print("1000 pairs, in-batch, mean and standard deviation over three seeds, new catalogue")
print(pd.DataFrame(rows).groupby("temperature")[["recall", "unsafe_in_top"]].agg(["mean", "std"]).round(3).to_string())
