"""Walk-forward forecasting of weekly net cash flow, by customer and by segment.

Issue time: Monday morning, every four weeks. Horizon: the next four weeks. Information set: every
transaction before the issue time, so every lag is at least four weeks. Same discipline, same level
trick and same MASE as `notes/01-time-series-ml.md`, with weeks in place of hours.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from generator import N_WEEKS, START

H = 4                                        # weeks ahead
M = 52                                       # the season used to scale MASE
ORIGINS = list(range(N_WEEKS - 32, N_WEEKS, H))   # eight issue dates, the last 32 weeks of the data
FIRST_ISSUE = START + pd.Timedelta(weeks=ORIGINS[0])
LAGS = (4, 5, 6, 8, 12, 26, 52)


def weekly_panel(tx, n_customers):
    """Weeks in rows, customers in columns, signed net cash in each cell."""
    week = (tx.date - START).dt.days // 7
    y = tx.groupby([week, "customer_id"]).amount.sum().unstack(fill_value=0.0)
    return y.reindex(index=range(N_WEEKS), columns=range(n_customers), fill_value=0.0)


def mase(y_true, y_pred, y_train, m=M):
    scale = np.mean(np.abs(y_train[m:] - y_train[:-m]))
    return float(np.mean(np.abs(y_true - y_pred)) / max(scale, 1e-8))


def smape(y_true, y_pred):
    """As in atlas's grader. Bounded at 200, and undefined-looking when the actual is near zero."""
    return float(100 * np.mean(np.abs(y_true - y_pred) / np.maximum((np.abs(y_true) + np.abs(y_pred)) / 2, 1e-8)))


def directional(y_true, y_pred):
    """As in atlas's grader: % of steps where the forecast moved the same way as the actual."""
    return float(100 * np.mean(np.sign(np.diff(y_true)) == np.sign(np.diff(y_pred))))


def long_table(y):
    """One row per customer-week, every input at least H weeks old and divided by a known level."""
    level = y.abs().rolling(26).mean().shift(H) + 1.0
    columns = {f"lag_{lag}": (y.shift(lag) / level).stack() for lag in LAGS}
    columns["mean_13"] = (y.rolling(13).mean().shift(H) / level).stack()
    columns["std_13"] = (y.rolling(13).std().shift(H) / level).stack()
    out = pd.DataFrame(columns)
    out["target"] = (y / level).stack()
    out["level"] = level.stack()
    out["actual"] = y.stack()
    out.index.names = ["week", "customer"]
    out = out.reset_index()
    out["week_of_year"] = (START + pd.to_timedelta(out.week * 7, unit="D")).dt.isocalendar().week.astype(int)
    return out.dropna()


INPUTS = [f"lag_{lag}" for lag in LAGS] + ["mean_13", "std_13", "week_of_year"]


def fit_predict(table, origin, inputs=INPUTS, categorical=None):
    """Train on weeks before the issue date, predict the next H. Trees see a clipped ratio; output is in money."""
    train = table[table.week < origin]
    test = table[(table.week >= origin) & (table.week < origin + H)]
    model = HistGradientBoostingRegressor(max_iter=100, learning_rate=0.1, random_state=0,
                                          categorical_features=categorical)
    model.fit(train[inputs], train.target.clip(-20, 20))
    return test.assign(pred=model.predict(test[inputs]) * test.level)[["week", "customer", "pred"]]


def global_forecast(table, labels=None):
    """One model for every customer. With labels, the segment is one more input."""
    inputs, categorical = INPUTS, None
    if labels is not None:
        table = table.assign(segment=np.asarray(labels)[table.customer] + 1)      # noise (-1) becomes category 0
        inputs, categorical = INPUTS + ["segment"], ["segment"]
    return _to_wide(pd.concat(fit_predict(table, o, inputs, categorical) for o in ORIGINS))


def per_segment_forecast(table, labels):
    """One model per segment, each trained only on that segment's customers."""
    labels = np.asarray(labels)
    parts = [fit_predict(table[labels[table.customer] == s], o) for o in ORIGINS for s in np.unique(labels)]
    return _to_wide(pd.concat(parts))


def _to_wide(long):
    return long.pivot(index="week", columns="customer", values="pred")


def seasonal_naive(y, lag):
    """Same week `lag` weeks ago. Legal at every horizon because lag >= H."""
    test = [w for o in ORIGINS for w in range(o, o + H)]
    return y.shift(lag).loc[test]


def customer_score(y, pred):
    """Mean over customers of each one's MASE across all test weeks, each scaled on data before the first issue."""
    train = y.loc[: ORIGINS[0] - 1].to_numpy()
    return float(np.mean([mase(y[c].loc[pred.index].to_numpy(), pred[c].to_numpy(), train[:, c]) for c in y.columns]))


def segment_scores(y, pred, labels):
    """One row per fold and segment: MASE, SMAPE and direction on the segment's total."""
    labels = np.asarray(labels)
    rows = []
    for o in ORIGINS:
        weeks = list(range(o, o + H))
        for s in np.unique(labels):
            cols = y.columns[labels == s]
            total, forecast = y[cols].sum(axis=1), pred[cols].sum(axis=1)
            rows.append(dict(fold=o, segment=s, mase=mase(total.loc[weeks].to_numpy(), forecast.loc[weeks].to_numpy(), total.loc[: o - 1].to_numpy()),
                             smape=smape(total.loc[weeks].to_numpy(), forecast.loc[weeks].to_numpy()),
                             direction=directional(total.loc[weeks].to_numpy(), forecast.loc[weeks].to_numpy())))
    return pd.DataFrame(rows)


def local_total_forecast(y, labels):
    """statsforecast's MSTL fitted to each segment's total: the classical per-segment model. Optional dependency."""
    from statsforecast import StatsForecast
    from statsforecast.models import MSTL, AutoETS
    labels = np.asarray(labels)
    out = []
    for o in ORIGINS:
        frames = [pd.DataFrame({"unique_id": str(s), "ds": y.index[:o], "y": y[y.columns[labels == s]].sum(axis=1).to_numpy()[:o]})
                  for s in np.unique(labels)]
        sf = StatsForecast(models=[MSTL(season_length=[4, 52], trend_forecaster=AutoETS(model="ZZN"))], freq=1)
        fc = sf.forecast(df=pd.concat(frames), h=H)
        fc = fc.assign(week=o + fc.groupby("unique_id").cumcount()).rename(columns={"MSTL": "pred"})
        out.append(fc[["unique_id", "week", "pred"]])
    return pd.concat(out)
