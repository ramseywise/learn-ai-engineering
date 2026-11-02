# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "matplotlib", "scipy"]
# ///
"""Chapter 4: overall conversion is flat, so is the new mobile checkout page fine?

Run from this folder with: uv run ch04_funnel.py
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

import chartstyle as cs
from retail import REDESIGN, STEPS, load_orders, load_sessions

cs.apply()

# %% load
sessions = load_sessions()
sessions["period"] = np.where(sessions.date >= REDESIGN, "after", "before")
sessions["purchased"] = sessions.furthest == 5
print(len(sessions), "sessions,", sessions.user_id.nunique(), "users")
print(sessions.head(3).to_string(index=False))
print((sessions.groupby("period").purchased.mean().loc[["before", "after"]] * 100).round(2).to_string())

# %% steps
def funnel(frame):
    """Sessions reaching each step, and the conditional rate from the step before."""
    reached = [(frame.furthest >= i).sum() for i in range(len(STEPS))]
    rate = [np.nan] + [reached[i] / reached[i - 1] for i in range(1, len(STEPS))]
    return pd.DataFrame({"reached": reached, "rate": rate}, index=STEPS)


rates = pd.DataFrame({(device, period): funnel(sessions[(sessions.device == device) & (sessions.period == period)]).rate
                      for device in ("mobile", "desktop") for period in ("before", "after")})
print((rates.iloc[1:] * 100).round(1).to_string())

# %% chart_steps
fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
y = np.arange(5)
for ax, device in zip(axes, ("mobile", "desktop")):
    before, after = rates[(device, "before")].iloc[1:] * 100, rates[(device, "after")].iloc[1:] * 100
    ax.barh(y + .19, before, height=.34, color=cs.MUTED, label="Before 15 Sep")
    ax.barh(y - .19, after, height=.34, color=cs.BLUE, label="After 15 Sep")
    for i, (b, a) in enumerate(zip(before, after)):
        ax.text(a + 1, i - .19, f"{a:.0f}", va="center", color=cs.SECONDARY)
        ax.text(b + 1, i + .19, f"{b:.0f}", va="center", color=cs.SECONDARY)
    ax.set_title(device.capitalize())
    ax.set_xlim(0, 108)
    ax.grid(False)
    ax.set_xlabel("Sessions passing the step (%)")
axes[0].set_yticks(y, [f"{STEPS[i]} to {STEPS[i + 1]}" for i in range(5)])
axes[0].invert_yaxis()
axes[0].legend(loc="upper right")
cs.save(fig, "applied-funnel-steps.png")

# %% simpson
share = sessions.groupby(["period", "device"]).size().unstack("device")
share = share.div(share.sum(axis=1), axis=0).loc[["before", "after"]]
conversion = sessions.groupby(["period", "device"]).purchased.mean().unstack("device").loc[["before", "after"]]
print("mobile share of sessions", (share["mobile"] * 100).round(1).to_dict())
print((conversion * 100).round(2).to_string())

# %% chart_simpson
weekly = sessions.assign(week=sessions.date.dt.to_period("W").dt.start_time)
weekly = weekly[(weekly.week >= "2025-03-03") & (weekly.week < "2025-12-29")]
overall = weekly.groupby("week").purchased.mean() * 100
by_device = weekly.groupby(["week", "device"]).purchased.mean().unstack() * 100
fig, ax = plt.subplots()
ax.plot(overall.index, overall, color=cs.INK, label="All sessions")
ax.plot(by_device.index, by_device["desktop"], color=cs.BLUE, label="Desktop")
ax.plot(by_device.index, by_device["mobile"], color=cs.ORANGE, label="Mobile")
for name, series in {"Desktop": by_device["desktop"], "All sessions": overall, "Mobile": by_device["mobile"]}.items():
    ax.text(series.index[-1] + pd.Timedelta(days=4), series.iloc[-1], name, va="center", color=cs.SECONDARY)
ax.axvline(REDESIGN, color=cs.BASELINE, lw=1)
ax.text(REDESIGN - pd.Timedelta(days=3), 13.2, "Checkout redesign", ha="right", color=cs.SECONDARY)
ax.set_xlim(overall.index[0], overall.index[-1] + pd.Timedelta(days=45))
ax.set_ylim(0, 14)
ax.set_ylabel("Sessions ending in a purchase (%)")
ax.set_title("The headline holds still while the two devices part")
ax.legend(loc="upper left")
cs.save(fig, "applied-funnel-simpson.png")

# %% test
def payment_counts(device, period):
    at = sessions[(sessions.device == device) & (sessions.period == period) & (sessions.furthest >= 3)]
    return (at.furthest >= 4).sum(), len(at)


def difference(a, b):
    """Difference in proportions (a minus b) with its standard error, from (passed, n) pairs."""
    pa, pb = a[0] / a[1], b[0] / b[1]
    return pa - pb, np.sqrt(pa * (1 - pa) / a[1] + pb * (1 - pb) / b[1])


z = norm.ppf(.975)
mobile = difference(payment_counts("mobile", "after"), payment_counts("mobile", "before"))
desktop = difference(payment_counts("desktop", "after"), payment_counts("desktop", "before"))
did, did_se = mobile[0] - desktop[0], np.hypot(mobile[1], desktop[1])
print(f"mobile checkout-to-payment   {mobile[0] * 100:+.1f} points, 95% CI {100 * (mobile[0] - z * mobile[1]):+.1f} to {100 * (mobile[0] + z * mobile[1]):+.1f}")
print(f"desktop checkout-to-payment {desktop[0] * 100:+.1f} points, 95% CI {100 * (desktop[0] - z * desktop[1]):+.1f} to {100 * (desktop[0] + z * desktop[1]):+.1f}")
print(f"difference in differences    {did * 100:+.1f} points, 95% CI {100 * (did - z * did_se):+.1f} to {100 * (did + z * did_se):+.1f}")
print("n at step, mobile after:", payment_counts("mobile", "after")[1])

# %% users
pre = sessions[sessions.period == "before"]
post = sessions[sessions.period == "after"]
for label, frame in {"before": pre, "after": post}.items():
    print(f"{label:6s} per session {frame.purchased.mean():.2%}, per user {frame.groupby('user_id').purchased.max().mean():.2%}, "
          f"sessions per user {len(frame) / frame.user_id.nunique():.2f}, days {frame.date.nunique()}")

# %% value
orders = load_orders()
aov = orders.value.mean()
MARGIN = .35
at_step = payment_counts("mobile", "after")[1]
purchase_after_pay = (post[post.device == "mobile"].furthest == 5).sum() / (post[post.device == "mobile"].furthest >= 4).sum()
lost_low, lost_mid, lost_high = [-x * at_step * purchase_after_pay for x in (did + z * did_se, did, did - z * did_se)]
print(f"average order £{aov:.2f}, purchase given payment passed {purchase_after_pay:.3f}")
for label, lost in {"low": lost_low, "mid": lost_mid, "high": lost_high}.items():
    print(f"{label:4s} lost orders {lost:6.0f}  revenue £{lost * aov:9,.0f}  margin £{lost * aov * MARGIN:8,.0f}")
per_week = lost_mid * aov * MARGIN / (post.date.nunique() / 7)
print(f"margin lost per week of delay £{per_week:,.0f}")

# %% experiment
per_day = at_step / post.date.nunique()
for p0, delta in ((.68, .02), (.68, .05), (.68, .10)):
    p1 = p0 + delta
    n = (norm.ppf(.975) + norm.ppf(.8)) ** 2 * (p0 * (1 - p0) + p1 * (1 - p1)) / delta ** 2
    print(f"to detect +{delta:.0%} on a {p0:.0%} step at 80% power: {n:,.0f} per arm, {2 * n / per_day:.0f} days at 50/50 ({per_day:.0f} sessions a day reach the step)")
