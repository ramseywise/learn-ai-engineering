# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "matplotlib", "scipy"]
# ///
"""Chapter 3: are the new customers worse, or is everyone worse?

Run from this folder with: uv run ch03_cohort_retention.py
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import betaln

import chartstyle as cs
from retail import CHANNELS, load_customers, load_orders

cs.apply()

# %% load
customers, orders = load_customers(), load_orders()
print(len(customers), "customers,", len(orders), "orders,", f"£{orders.value.sum():,.0f} revenue")
customers["cohort"] = customers.acquired.dt.to_period("M")
tagged = orders.merge(customers[["customer_id", "cohort", "channel"]], on="customer_id")
tagged["month"] = tagged.order_date.dt.to_period("M")
tagged["age"] = (tagged.month.dt.year - tagged.cohort.dt.year) * 12 + tagged.month.dt.month - tagged.cohort.dt.month
print(tagged[["customer_id", "cohort", "month", "age", "value"]].head(3).to_string(index=False))

# %% triangle
LAST = pd.Period("2025-12", "M")
sizes = customers.groupby("cohort").size()
active = tagged.groupby(["cohort", "age"]).customer_id.nunique().unstack("age")
retention = active.div(sizes, axis=0)
# Quarterly cohorts are easier to read: pool the monthly triangle by acquisition quarter.
customers["quarter"] = customers.acquired.dt.to_period("Q")
tagged = tagged.merge(customers[["customer_id", "quarter"]], on="customer_id")
quarter_sizes = customers.groupby("quarter").size()
q_active = tagged.groupby(["quarter", "age"]).customer_id.nunique().unstack("age")
q_ret = q_active.div(quarter_sizes, axis=0)
# An age is only complete for a quarter if its youngest customers have reached it.
for q in q_ret.index:
    q_ret.loc[q, q_ret.columns > (LAST - q.asfreq("M", "end")).n] = np.nan
print((q_ret[[1, 2, 3, 6, 12]] * 100).round(1).to_string())

# %% chart_heatmap
from matplotlib.colors import LinearSegmentedColormap

ramp = LinearSegmentedColormap.from_list("blue", cs.SEQUENTIAL)
ramp.set_bad(cs.SURFACE)
show = q_ret.loc[:, 1:18].dropna(how="all") * 100
fig, ax = plt.subplots(figsize=(8.5, 4.6))
im = ax.imshow(np.ma.masked_invalid(show.to_numpy()), aspect="auto", cmap=ramp, vmin=0, vmax=20)
ax.set_xticks(range(0, 18, 2), [str(a) for a in show.columns[::2]])
ax.set_yticks(range(len(show)), [str(q) for q in show.index])
ax.grid(False)
ax.tick_params(length=0)
ax.set_xlabel("Months since first order")
ax.set_title("Share of each acquisition quarter ordering that month (%)")
fig.colorbar(im, ax=ax, shrink=.8, label="Active customers (%)").outline.set_visible(False)
cs.save(fig, "applied-cohort-heatmap.png")

# %% mix
c25 = customers[customers.acquired >= "2025-01-01"].channel.value_counts(normalize=True)
c24 = customers[customers.acquired.dt.year == 2024].channel.value_counts(normalize=True)
print(pd.DataFrame({"2024": c24, "2025": c25}).loc[CHANNELS].round(3).to_string())

# Repeat within 90 days: comparable across cohorts, and needs only 90 days of history per customer.
firsts = customers.set_index("customer_id").acquired
gap = (orders.order_date - orders.customer_id.map(firsts)).dt.days
repeaters = orders[(gap > 0) & (gap <= 90)].customer_id.unique()
customers["repeat_90"] = customers.customer_id.isin(repeaters)
complete = customers[customers.acquired <= "2025-10-02"].copy()
complete["period"] = np.select([complete.acquired < "2024-10-03", complete.acquired < "2025-01-01"],
                               ["2024 (to Oct 2)", "exposed"], "2025")
compare = complete[complete.period != "exposed"]
by_channel = compare.groupby(["period", "channel"]).repeat_90.mean().unstack("period").loc[CHANNELS]
print((by_channel * 100).round(1).to_string())

base_period, new_period = "2024 (to Oct 2)", "2025"
mix = compare.groupby("period").channel.value_counts(normalize=True).unstack("period").loc[CHANNELS]
total_old = (by_channel[base_period] * mix[base_period]).sum()
total_new = (by_channel[new_period] * mix[new_period]).sum()
new_rates_old_mix = (by_channel[new_period] * mix[base_period]).sum()
print(f"90-day repeat: {total_old:.1%} -> {total_new:.1%}, change {100 * (total_new - total_old):+.1f} points")
print(f"  everyone got worse (rates change, 2024 mix): {100 * (new_rates_old_mix - total_old):+.1f} points")
print(f"  mix moved to paid social (mix change, 2025 rates): {100 * (total_new - new_rates_old_mix):+.1f} points")

# %% chart_curves
def cumulative_rev(frame, members, horizon=12):
    """Mean cumulative revenue per customer by age."""
    by_age = frame[frame.customer_id.isin(members) & (frame.age <= horizon)].groupby("age").value.sum()
    return by_age.reindex(range(horizon + 1), fill_value=0).cumsum() / len(members)


pre = customers[(customers.acquired >= "2023-01-01") & (customers.acquired < "2024-01-01")]
fig, ax = plt.subplots()
ltv = {}
for channel in CHANNELS:
    members = pre[pre.channel == channel].customer_id
    curve = cumulative_rev(tagged, members)
    ltv[channel] = curve
    ax.plot(curve.index, curve, color=cs.CHANNEL_COLOUR[channel], label=channel.replace("_", " "))
    nudge = {"organic": 4, "referral": -4}.get(channel, 0)    # these two nearly coincide
    ax.text(12.15, curve[12] + nudge, channel.replace("_", " "), color=cs.SECONDARY, va="center")
ax.set_xlim(0, 14.2)
ax.set_ylim(0)
ax.set_xticks(range(0, 13, 3))
ax.set_xlabel("Months since first order")
ax.set_ylabel("Cumulative revenue per customer (£)")
ax.set_title("2023 customers: the first order is similar, the next twelve months are not")
ax.legend(loc="upper left")
cs.save(fig, "applied-cohort-ltv-channel.png")

# %% ltv
MARGIN = .35
CAC = {"paid_social": 32, "organic": 6, "email": 9, "referral": 14}    # assumed, in pounds
rows = []
for channel in CHANNELS:
    members = pre[pre.channel == channel].customer_id
    m24 = cumulative_rev(tagged, members, 24)[24] * MARGIN
    rows.append({"channel": channel, "customers": len(members), "margin_12m": ltv[channel][12] * MARGIN,
                 "margin_24m": m24, "cac": CAC[channel], "ltv_24m_to_cac": m24 / CAC[channel]})
print(pd.DataFrame(rows).round(2).to_string(index=False))

# %% sbg_replicate
def sbg_survival(a, b, t):
    """Shifted-beta-geometric survivor function S(t) = B(a, b + t) / B(a, b)."""
    t = np.asarray(t, dtype=float)
    return np.exp(betaln(a, b + t) - betaln(a, b))


def sbg_fit(survival):
    """Maximum likelihood from an aggregate survival curve S(0)=1, S(1), ..., S(n)."""
    survival = np.asarray(survival, dtype=float)
    n = len(survival) - 1
    died = -np.diff(survival)

    def negative_ll(log_params):
        a, b = np.exp(log_params)
        s = sbg_survival(a, b, np.arange(n + 1))
        return -(died * np.log(-np.diff(s))).sum() - survival[n] * np.log(s[n])

    res = minimize(negative_ll, [0, 0], method="Nelder-Mead", options=dict(xatol=1e-5, fatol=1e-8))
    return np.exp(res.x)


# Table 1 of Fader and Hardie (2007): % surviving, years 0 to 12.
high_end = np.array([100, 86.9, 74.3, 65.3, 59.3, 55.1, 51.7, 49.1, 46.8, 44.5, 42.7, 40.9, 39.4]) / 100
regular = np.array([100, 63.1, 46.8, 38.2, 32.6, 28.9, 26.2, 24.1, 22.3, 20.7, 19.4, 18.3, 17.3]) / 100
for name, curve in {"High End": high_end, "Regular": regular}.items():
    a, b = sbg_fit(curve[:8])
    s12 = sbg_survival(a, b, 12)
    print(f"{name:9s} alpha {a:.3f}  beta {b:.3f}  year 12 forecast {s12:.1%}  actual {curve[12]:.1%}  error {s12 / curve[12] - 1:+.1%}")

# The PDF prints alpha = 0.688 for High End; compare the two values at the printed beta.
def sbg_ll(a, b, survival):
    s = sbg_survival(a, b, np.arange(len(survival)))
    return (-np.diff(survival) * np.log(-np.diff(s))).sum() + survival[-1] * np.log(s[-1])


print(f"High End log likelihood per customer: {sbg_ll(.668, 3.806, high_end[:8]):.5f} at 0.668, {sbg_ll(.688, 3.806, high_end[:8]):.5f} at 0.688")

# %% sbg_fernhill
# The generator's true lifetimes stand in for what a subscription firm would see. Fernhill cannot.
early = customers[customers.acquired < "2023-07-01"]
months = np.arange(25)
empirical = np.array([(early.true_lifetime_months > t).mean() for t in months])
calibrate = 7
a, b = sbg_fit(empirical[:calibrate])
forecast = sbg_survival(a, b, months)
slope, intercept = np.polyfit(months[1:calibrate], np.log(empirical[1:calibrate]), 1)
exponential = np.exp(intercept + slope * months)
print(f"{len(early)} customers, calibrated on months 0 to {calibrate - 1}; alpha {a:.3f}, beta {b:.3f}")
for t in (6, 12, 18, 24):
    print(f"month {t:2d}  actual {empirical[t]:.3f}  sBG {forecast[t]:.3f}  exponential {exponential[t]:.3f}")
r = (b + months[1:13] - 1) / (a + b + months[1:13] - 1)
print("model retention rate at month 1, 6, 12:", r[[0, 5, 11]].round(3))

# %% chart_sbg
fig, ax = plt.subplots()
ax.plot(months, empirical * 100, color=cs.INK, label="Actual")
ax.plot(months, forecast * 100, color=cs.BLUE, label="sBG forecast")
ax.plot(months, exponential * 100, color=cs.ORANGE, label="Exponential curve fit")
ax.axvline(calibrate - 1, color=cs.BASELINE, lw=1)
ax.text(calibrate - .7, 92, "Calibration ends", color=cs.SECONDARY)
ax.set_ylim(0, 100)
ax.set_xlabel("Months since first order")
ax.set_ylabel("Customers still alive (%)")
ax.set_title("Heterogeneous churn flattens a curve that an exponential cannot")
ax.legend(loc="upper right")
cs.save(fig, "applied-cohort-sbg.png")
