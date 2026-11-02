# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "matplotlib", "statsmodels", "prophet"]
# ///
"""Chapter 1: how many units must the warehouse be staffed for over the next 13 weeks?

Run from this folder with: uv run ch01_forecasting.py
"""
import logging
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from prophet import Prophet
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from statsmodels.tsa.forecasting.stl import STLForecast
from statsmodels.tsa.statespace.sarimax import SARIMAX

import chartstyle as cs
from retail import load_weekly_units

warnings.filterwarnings("ignore")
logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
logging.getLogger("prophet").setLevel(logging.ERROR)
cs.apply()

# %% load
units = load_weekly_units()
print(units.tail(3).to_string())
print(f"{len(units)} weeks, mean {units.mean():.0f}, max {units.max()} in week of {units.idxmax().date()}")
by_year = units.groupby(units.index.year).sum()
print("growth by year:", (by_year.pct_change().dropna() * 100).round(1).to_dict())

# %% chart_series
fig, ax = plt.subplots()
ax.plot(units.index, units, color=cs.BLUE, lw=1.4)
ax.set_title("Weekly units have a trend, a season and a one-week hole")
ax.set_ylabel("Units shipped per week")
ax.set_ylim(0)
cs.year_ticks(ax)
outage = pd.Timestamp("2023-06-12")
ax.annotate("Warehouse outage", (outage, units[outage]), (pd.Timestamp("2023-08-20"), 700),
            color=cs.SECONDARY, arrowprops=dict(arrowstyle="-", color=cs.MUTED))
cs.save(fig, "applied-forecast-weekly-units.png")

# %% baselines
H, SEASON = 13, 52


def mean_method(train, h=H):
    return np.repeat(train.mean(), h)


def naive(train, h=H):
    return np.repeat(train.iloc[-1], h)


def seasonal_naive(train, h=H):
    return train.iloc[-SEASON:-SEASON + h].to_numpy()


def drift(train, h=H):
    slope = (train.iloc[-1] - train.iloc[0]) / (len(train) - 1)
    return train.iloc[-1] + slope * np.arange(1, h + 1)


train = units.iloc[:-H]
print("first three forecast weeks")
for f in (mean_method, naive, seasonal_naive, drift):
    print(f"{f.__name__:15s}", np.round(f(train)[:3]).astype(int))

# %% models
def stl_ets(train, h=H):
    """STL removes the season, ETS forecasts what is left: FPP3's first suggestion for weekly data."""
    model = STLForecast(np.log(train).asfreq("W-MON"), ETSModel, period=SEASON, robust=True,
                        model_kwargs=dict(error="add", trend="add", damped_trend=True)).fit()
    frame = model.get_prediction(start=len(train), end=len(train) + h - 1).summary_frame(alpha=.2)
    return np.exp(frame["mean"]).to_numpy(), np.exp(frame["mean_ci_lower"]).to_numpy(), np.exp(frame["mean_ci_upper"]).to_numpy()


def black_friday_weeks(index):
    """1 for the week holding the fourth Friday of November, else 0."""
    flags = []
    for week in index:
        nov1 = pd.Timestamp(week.year, 11, 1)
        friday = nov1 + pd.Timedelta(days=(4 - nov1.dayofweek) % 7 + 21)
        flags.append(int(week <= friday < week + pd.Timedelta(days=7)))
    return np.array(flags)


def harmonic_exog(index, K):
    """Fourier terms at the true period of 52.18 weeks, a trend, and the moving Black Friday."""
    t = (index - pd.Timestamp("2021-01-04")).days.to_numpy() / 7
    terms = {"trend": t / 52.18, "black_friday": black_friday_weeks(index)}
    for k in range(1, K + 1):
        terms[f"sin{k}"] = np.sin(2 * np.pi * k * t / 52.18)
        terms[f"cos{k}"] = np.cos(2 * np.pi * k * t / 52.18)
    return pd.DataFrame(terms, index=index)


def dhr_fit(train, K):
    return SARIMAX(np.log(train).asfreq("W-MON"), exog=harmonic_exog(train.index, K),
                   order=(1, 0, 0), trend="c").fit(disp=False, maxiter=200)


def aicc(res):
    n, k = res.nobs, len(res.params)
    return res.aic + 2 * k * (k + 1) / (n - k - 1)


def best_K(train, candidates=(2, 4, 6, 8, 10, 12)):
    """FPP3 picks the number of Fourier pairs by AICc, so each origin picks its own."""
    return min(candidates, key=lambda K: aicc(dhr_fit(train, K)))


def dhr(train, h=H):
    K = best_K(train)
    future = pd.date_range(train.index[-1] + pd.Timedelta(weeks=1), periods=h, freq="W-MON")
    frame = dhr_fit(train, K).get_forecast(h, exog=harmonic_exog(future, K)).summary_frame(alpha=.2)
    return (np.exp(frame["mean"]).to_numpy(), np.exp(frame["mean_ci_lower"]).to_numpy(),
            np.exp(frame["mean_ci_upper"]).to_numpy())


def prophet(train, h=H):
    days = pd.date_range("2021-01-01", "2026-12-31")
    fridays = days[(days.month == 11) & (days.dayofweek == 4) & (days.day >= 22) & (days.day <= 28)]
    # A weekly series is stamped on Mondays, so the event sits on the Monday of the Friday's week.
    mondays = fridays - pd.Timedelta(days=4)
    events = pd.DataFrame({"holiday": "black_friday", "ds": mondays})
    model = Prophet(seasonality_mode="multiplicative", weekly_seasonality=False, daily_seasonality=False,
                    yearly_seasonality=10, holidays=events, interval_width=.8, uncertainty_samples=300)
    model.fit(pd.DataFrame({"ds": train.index, "y": train.to_numpy()}))
    future = pd.DataFrame({"ds": pd.date_range(train.index[-1] + pd.Timedelta(weeks=1), periods=h, freq="W-MON")})
    out = model.predict(future)
    return out["yhat"].to_numpy(), out["yhat_lower"].to_numpy(), out["yhat_upper"].to_numpy()


print("AICc picks K =", best_K(units.iloc[:-H]), "on everything before the last 13 weeks")

# %% backtest
METHODS = {"Mean": mean_method, "Naive": naive, "Drift": drift, "Seasonal naive": seasonal_naive,
           "STL + ETS": stl_ets, "Harmonic regression": dhr, "Prophet": prophet}
origins = [len(units) - H * i for i in range(12, 0, -1)]      # train lengths, each 13 weeks apart
rows = []
for n_train in origins:
    train, test = units.iloc[:n_train], units.iloc[n_train:n_train + H]
    # MASE scale: the in-sample seasonal naive MAE, which each origin computes from its own past.
    scale = train.diff(SEASON).abs().mean()
    for name, method in METHODS.items():
        out = method(train)
        point, low, high = out if isinstance(out, tuple) else (out, np.nan, np.nan)
        rows.append(pd.DataFrame({"origin": train.index[-1], "week": test.index, "step": np.arange(1, H + 1),
                                  "model": name, "actual": test.to_numpy(), "forecast": point,
                                  "low": low, "high": high, "scale": scale}))
backtest = pd.concat(rows, ignore_index=True)
backtest["error"] = backtest["actual"] - backtest["forecast"]
print(f"{len(origins)} origins, from {backtest.origin.min().date()} to {backtest.origin.max().date()}")

# %% score
def score(frame):
    return pd.Series({"MAE": frame.error.abs().mean(), "RMSE": np.sqrt((frame.error ** 2).mean()),
                      "MASE": (frame.error.abs() / frame.scale).mean(),
                      "Bias": frame.error.mean()})


exam_origin = backtest.origin.max()
select = backtest[backtest.origin < exam_origin]       # 11 origins to choose a model
exam = backtest[backtest.origin == exam_origin]        # the last 13 weeks, touched once
order = list(METHODS)
table = select.groupby("model").apply(score, include_groups=False).loc[order]
print(table.round(2).to_string())

# %% chart_mase
ranked = table["MASE"].sort_values(ascending=False)
baselines = {"Mean", "Naive", "Drift", "Seasonal naive"}
fig, ax = plt.subplots(figsize=(8, 3.8))
colours = [cs.MUTED if m in baselines else cs.BLUE for m in ranked.index]
bars = ax.barh(ranked.index, ranked, color=colours, height=.6)
ax.bar_label(bars, fmt="%.2f", padding=4, color=cs.SECONDARY, backgroundcolor=cs.SURFACE)
ax.axvline(1, color=cs.BASELINE, lw=1, zorder=0)
ax.grid(False)
ax.set_xticks([0, 1, 2])
ax.set_xlabel("MASE over 11 rolling origins, 13 weeks ahead (1 = in-sample seasonal naive error)")
ax.set_title("Beat the seasonal naive before you trust a model")
ax.bar(0, 0, color=cs.MUTED, label="Baseline")
ax.bar(0, 0, color=cs.BLUE, label="Model")
ax.legend(loc="upper right")
cs.save(fig, "applied-forecast-backtest-mase.png")

# %% coverage
with_pi = select.dropna(subset=["low"])
coverage = with_pi.assign(inside=lambda d: d.actual.between(d.low, d.high)).groupby("model")["inside"].mean()
print("share of actuals inside the nominal 80% interval, 11 origins")
print((coverage * 100).round(1).to_string())

# %% plan
best = table["MASE"].idxmin()
print("selected on 11 origins:", best)
ratio = select[select.model == best].eval("actual / forecast")
cost_short, cost_over = 12.0, 4.0
target = cost_short / (cost_short + cost_over)
buffer = ratio.quantile(target)
print(f"critical ratio {target:.2f}, buffer {buffer:.3f} times the forecast")

def plan_cost(plan, actual):
    short = np.maximum(actual - plan, 0)
    over = np.maximum(plan - actual, 0)
    return (cost_short * short + cost_over * over).sum()


pick = exam[exam.model == best].set_index("week")
snaive = exam[exam.model == "Seasonal naive"].set_index("week")
plans = {"Seasonal naive, no buffer": snaive.forecast, f"{best}, no buffer": pick.forecast,
         f"{best}, buffered": pick.forecast * buffer}
for name, plan in plans.items():
    print(f"{name:34s} cost £{plan_cost(plan, pick.actual):>8,.0f}")
print(exam.groupby("model").apply(score, include_groups=False).loc[order].round(2).to_string())

# %% chart_plan
fig, ax = plt.subplots()
recent = units["2025-03-01":]
ax.plot(recent.index, recent, color=cs.INK, lw=1.6, label="Actual units")
ax.plot(pick.index, pick.forecast, color=cs.BLUE, label=f"{best} forecast")
ax.plot(pick.index, pick.forecast * buffer, color=cs.ORANGE, label="Staffing plan (forecast × buffer)")
ax.axvline(exam_origin, color=cs.BASELINE, lw=1)
ax.text(exam_origin, 400, " Forecast made here", color=cs.SECONDARY)
ax.set_ylim(0)
ax.set_ylabel("Units per week")
ax.set_title("The Q4 plan, set in September, against what happened")
ax.legend(loc="upper left")
cs.save(fig, "applied-forecast-q4-plan.png")
