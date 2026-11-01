# Boosting comparison

Trains four gradient-boosting libraries and two baselines on the adult census data, with the same split, learning rate (0.05) and early-stopping patience (50 rounds) where the library supports it. It repeats over five seeds, so you can see how much of any gap between libraries is noise.

```bash
cd data-science/01-classical-ml/practice/boosting-comparison
uv run --python 3.12 --with scikit-learn --with xgboost --with lightgbm \
    --with catboost --with pandas python compare_boosters.py
```

It takes a few minutes and writes [`results.csv`](results.csv), one row per model and seed. The data comes from [`../intro-to-ml-in-python/data/adult.data`](../intro-to-ml-in-python/data/adult.data), so nothing is downloaded beyond the packages. Timings are from a laptop that was busy with other work, so read them as rough ratios.

The discussion and the table of results are in [`notes/07-boosting-in-practice.md`](../../notes/07-boosting-in-practice.md).
