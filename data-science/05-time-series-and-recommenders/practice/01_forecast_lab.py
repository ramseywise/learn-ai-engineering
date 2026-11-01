#!/usr/bin/env python3
"""Backtest lab for notes/01-time-series-ml.md, using the UCI Bike Sharing data.

Run from the pillar folder:
    uv run --with scikit-learn --with pandas python practice/01_forecast_lab.py

Every experiment is one call to `run`. Change the features, the horizon or the training
window and read the result against the seasonal naive row. A feature is legal only if its
value is known `min_lag` hours before the target.
"""
import urllib.request, zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

CACHE = Path.home() / ".cache" / "learn-ai-engineering"
URL = "https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip"


def load():
    """Return the hourly frame on a complete calendar grid. Missing hours count as zero rentals."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "bike-sharing.zip"
    if not path.exists():
        path.write_bytes(urllib.request.urlopen(URL, timeout=60).read())
    with zipfile.ZipFile(path) as z:
        raw = pd.read_csv(z.open("hour.csv"), parse_dates=["dteday"])
    raw["ts"] = raw["dteday"] + pd.to_timedelta(raw["hr"], unit="h")
    grid = pd.date_range(raw["ts"].min(), raw["ts"].max(), freq="h")
    df = raw.set_index("ts").reindex(grid)
    df["cnt"] = df["cnt"].fillna(0.0)
    return df


df = load()
y = df["cnt"]
TEST_STARTS = pd.date_range("2012-07-01", periods=6, freq="MS")


def calendar():
    X = pd.DataFrame(index=y.index)
    X["hour"] = y.index.hour
    X["dow"] = y.index.dayofweek
    X["month"] = y.index.month
    X["holiday"] = df["holiday"].ffill().fillna(0).values
    X["workingday"] = df["workingday"].ffill().fillna(0).values
    return X


def level(min_lag):
    return y.shift(min_lag).rolling(168).mean() + 1


def lag_features(lags, min_lag):
    """Lags relative to a level that is itself min_lag hours old. Rejects illegal lags."""
    assert min(lags) >= min_lag, "a lag inside the horizon is a leak"
    lv = level(min_lag)
    return pd.DataFrame({f"lag_{k}": y.shift(k) / lv for k in lags})


def score(pred, idx, train_end, m=24):
    tr = y[y.index < train_end].to_numpy()
    scale = np.mean(np.abs(tr[m:] - tr[:-m]))
    mae = np.mean(np.abs(y[idx].to_numpy() - pred))
    return mae, mae / scale


def run(name, X, min_lag=24, train_days=None):
    """Expanding-window backtest (or trailing, with train_days). Prints mean MAE and MASE."""
    lv = level(min_lag)
    rows = []
    for s in TEST_STARTS:
        idx = y.index[(y.index >= s) & (y.index < s + pd.offsets.MonthBegin(1))]
        tr = (X.index < s - pd.Timedelta(hours=min_lag - 24)) & X.notna().all(axis=1) & lv.notna()
        if train_days:
            tr &= X.index >= s - pd.Timedelta(days=train_days)
        m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, loss="poisson", random_state=0)
        m.fit(X[tr], (y / lv)[tr])
        rows.append(score(m.predict(X.loc[idx]) * lv[idx].to_numpy(), idx, s))
    mae, mase = np.mean(rows, axis=0)
    print(f"{name:42s} MAE {mae:6.2f}  MASE {mase:.3f}")
    return rows


def naive(name, lag):
    rows = [score(y.shift(lag).reindex(idx).to_numpy(), idx, s) for s in TEST_STARTS
            for idx in [y.index[(y.index >= s) & (y.index < s + pd.offsets.MonthBegin(1))]]]
    mae, mase = np.mean(rows, axis=0)
    print(f"{name:42s} MAE {mae:6.2f}  MASE {mase:.3f}")


if __name__ == "__main__":
    day = calendar().join(lag_features((24, 48, 168, 336), 24))

    print("-- baselines and the chapter's model")
    naive("same hour last week", 168)
    base = run("gbm relative, horizon 24h", day)

    print("\n-- exercise 1: same-hour mean over four weeks")
    same_hour = sum(y.shift(24 * 7 * k) for k in (1, 2, 3, 4)) / 4 / level(24)
    run("plus 4-week same-hour mean", day.assign(same_hour=same_hour))

    print("\n-- exercise 2: plan a week ahead, every input at least 168 hours old")
    week = calendar().join(lag_features((168, 336, 504, 672), 168))
    run("gbm relative, horizon one week", week, min_lag=168)

    print("\n-- exercise 3: forget old data")
    run("trailing 365 days", day, train_days=365)
    run("trailing 180 days", day, train_days=180)

    print("\n-- the bad month, without the storm days")
    oct_days = y["2012-10-25":"2012-11-02"].resample("D").sum()
    print(oct_days.astype(int).to_string())
