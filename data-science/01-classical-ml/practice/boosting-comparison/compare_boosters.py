"""Compare four gradient-boosting libraries, and two baselines, on adult census.

Run from this folder:
    uv run --python 3.12 --with scikit-learn --with xgboost --with lightgbm \
        --with catboost --with pandas python compare_boosters.py

Every model is trained on the same split, stops early on the same validation
set where it can, and is scored on the same test set. Repeating over several
seeds shows how much of any gap between libraries is noise. Results are printed
and saved to results.csv. Takes a few minutes on a laptop.
"""

import time
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier, early_stopping
from sklearn.compose import make_column_transformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import (
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

HERE = Path(__file__).parent
DATA = HERE.parent / "intro-to-ml-in-python" / "data" / "adult.data"
COLS = ["age", "workclass", "fnlwgt", "education", "education-num", "marital-status",
        "occupation", "relationship", "race", "gender", "capital-gain", "capital-loss",
        "hours-per-week", "native-country", "income"]
SEEDS = [0, 1, 2, 3, 4]
LR, MAX_ROUNDS, PATIENCE = 0.05, 2000, 50
THREADS = 4


def load():
    df = pd.read_csv(DATA, header=None, names=COLS, skipinitialspace=True, na_values="?")
    y = (df.pop("income") == ">50K").astype(int)
    df = df.drop(columns=["fnlwgt", "education"])  # a sampling weight, and a copy of education-num
    cats = list(df.select_dtypes(exclude="number").columns)
    for c in cats:
        df[c] = df[c].astype("category")
    return df, y, cats


def one_hot(cats):
    # Older libraries and the forest need numbers; missing becomes its own category.
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    return make_column_transformer((encoder, cats), remainder="passthrough")


def score(name, seed, y_test, proba, seconds, rounds):
    return dict(model=name, seed=seed, auc=roc_auc_score(y_test, proba),
                logloss=log_loss(y_test, proba),
                accuracy=accuracy_score(y_test, proba > 0.5),
                seconds=seconds, rounds=rounds)


def run_seed(X, y, cats, seed):
    X_rest, X_test, y_rest, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=seed)
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_rest, y_rest, test_size=0.2, stratify=y_rest, random_state=seed)
    rows = []

    def timed(fit):
        t0 = time.perf_counter()
        model = fit()
        return model, time.perf_counter() - t0

    # Baselines: the majority class, and a forest with no tuning.
    m, s = timed(lambda: DummyClassifier(strategy="prior").fit(_impute(X_tr), y_tr))
    rows.append(score("Dummy (majority)", seed, y_test, m.predict_proba(_impute(X_test))[:, 1], s, 0))

    m, s = timed(lambda: _fit_forest(X_tr, y_tr, cats, seed))
    rows.append(score("Random forest", seed, y_test, m.predict_proba(_impute(X_test))[:, 1], s, 300))

    # The classic scikit-learn booster: exact splits, no native categoricals or NaN.
    m, s = timed(lambda: make_pipeline(one_hot(cats), GradientBoostingClassifier(
        learning_rate=LR, n_estimators=MAX_ROUNDS, n_iter_no_change=PATIENCE,
        validation_fraction=0.2, max_depth=3, random_state=seed)).fit(_impute(X_rest), y_rest))
    rows.append(score("sklearn GradientBoosting", seed, y_test, m.predict_proba(_impute(X_test))[:, 1],
                      s, m[-1].n_estimators_))

    # Histogram boosting in scikit-learn.
    m, s = timed(lambda: HistGradientBoostingClassifier(
        learning_rate=LR, max_iter=MAX_ROUNDS, early_stopping=True, n_iter_no_change=PATIENCE,
        validation_fraction=0.2, categorical_features="from_dtype", random_state=seed
    ).fit(X_rest, y_rest))
    rows.append(score("sklearn HistGradientBoosting", seed, y_test, m.predict_proba(X_test)[:, 1],
                      s, m.n_iter_))

    m, s = timed(lambda: XGBClassifier(
        learning_rate=LR, n_estimators=MAX_ROUNDS, early_stopping_rounds=PATIENCE,
        tree_method="hist", enable_categorical=True, n_jobs=THREADS, random_state=seed
    ).fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False))
    rows.append(score("XGBoost", seed, y_test, m.predict_proba(X_test)[:, 1], s, m.best_iteration + 1))

    m, s = timed(lambda: LGBMClassifier(
        learning_rate=LR, n_estimators=MAX_ROUNDS, n_jobs=THREADS, random_state=seed, verbose=-1
    ).fit(X_tr, y_tr, eval_set=[(X_val, y_val)],
          callbacks=[early_stopping(PATIENCE, verbose=False)]))
    rows.append(score("LightGBM", seed, y_test, m.predict_proba(X_test)[:, 1], s, m.best_iteration_))

    # CatBoost takes strings and needs missing categories spelled out.
    fill = lambda d: d.assign(**{c: d[c].astype(object).where(d[c].notna(), "missing").astype(str)
                                 for c in cats})
    m, s = timed(lambda: CatBoostClassifier(
        learning_rate=LR, iterations=MAX_ROUNDS, early_stopping_rounds=PATIENCE, thread_count=THREADS,
        cat_features=cats, random_seed=seed, verbose=False, allow_writing_files=False
    ).fit(fill(X_tr), y_tr, eval_set=(fill(X_val), y_val)))
    rows.append(score("CatBoost", seed, y_test, m.predict_proba(fill(X_test))[:, 1], s, m.tree_count_))
    return rows


def _impute(d):
    return d.assign(**{c: d[c].astype(object).where(d[c].notna(), "missing").astype(str)
                       for c in d.select_dtypes(exclude="number").columns})


def _fit_forest(X_tr, y_tr, cats, seed):
    return make_pipeline(one_hot(cats), RandomForestClassifier(
        n_estimators=300, n_jobs=THREADS, random_state=seed)).fit(_impute(X_tr), y_tr)


def main():
    X, y, cats = load()
    rows = [row for seed in SEEDS for row in run_seed(X, y, cats, seed)]
    res = pd.DataFrame(rows)
    res.to_csv(HERE / "results.csv", index=False, float_format="%.5f")
    table = res.groupby("model", sort=False).agg(
        auc=("auc", "mean"), auc_sd=("auc", "std"), logloss=("logloss", "mean"),
        accuracy=("accuracy", "mean"), seconds=("seconds", "mean"), rounds=("rounds", "mean"))
    pd.set_option("display.width", 120)
    print(f"Adult census, {len(X)} rows, mean of {len(SEEDS)} seeds, {THREADS} threads")
    print(table.round({"auc": 4, "auc_sd": 4, "logloss": 4, "accuracy": 4, "seconds": 1, "rounds": 0}))


if __name__ == "__main__":
    main()
