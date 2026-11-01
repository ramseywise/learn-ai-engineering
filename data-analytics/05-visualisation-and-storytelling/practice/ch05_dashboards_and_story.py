# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pandas", "matplotlib", "streamlit", "altair"]
# ///
"""Chapter 5: test the dashboard, size the decision, draw the explanatory chart. Run: uv run ch05_dashboards_and_story.py"""
# %% apptest
from streamlit.testing.v1 import AppTest

app = AppTest.from_file("dashboard_app.py", default_timeout=30).run()
assert not app.exception
print([(m.label, m.value) for m in app.metric])
app.multiselect[0].set_value(["Email"]).run()
print([(m.label, m.value) for m in app.metric])
app.selectbox[0].set_value(2023).run()
print([(m.label, m.value, m.delta) for m in app.metric])

# %% decision-rates
import numpy as np
import pandas as pd
import fernhill

monthly = fernhill.load_monthly()
repeat = fernhill.load_repeat()
y24, y25 = (repeat[repeat.month.dt.year == y] for y in (2024, 2025))
rates24 = y24.groupby("channel")[["repeat_90d", "new_customers"]].sum().eval("repeat_90d / new_customers")
rates25 = y25.groupby("channel")[["repeat_90d", "new_customers"]].sum().eval("repeat_90d / new_customers")
mix25 = y25.groupby("channel")["new_customers"].sum()
actual = (rates25 * mix25).sum() / mix25.sum()
at_old_rates = (rates24 * mix25).sum() / mix25.sum()
overall24 = y24.repeat_90d.sum() / y24.new_customers.sum()
print(f"2024 overall {overall24:.1%}, 2025 overall {actual:.1%}")
print(f"2025 mix at 2024 channel rates {at_old_rates:.1%}")
print(f"mix effect {(at_old_rates - overall24) * 100:+.1f} pts, within-channel effect {(actual - at_old_rates) * 100:+.1f} pts")

# %% decision-value
MARGIN = 0.40             # assumption: gross margin
REPEAT_REVENUE = 110      # assumption: revenue from a repeat customer in the following year
RESTORE_COST = (14_000 - 4_000) * 12

lost_repeaters = (at_old_rates - actual) * mix25.sum()
repeat_margin = lost_repeaters * REPEAT_REVENUE * MARGIN

email = monthly[monthly.channel == "email"].assign(year=lambda d: d.month.dt.year)
email_revenue = email.groupby("year")["revenue"].sum()
email_margin = (email_revenue[2024] - email_revenue[2025]) * MARGIN
print(f"new customers 2025: {mix25.sum():,}; repeat customers lost: {lost_repeaters:,.0f}")
print(f"margin on lost repeat revenue: £{repeat_margin:,.0f}")
print(f"email revenue 2024 £{email_revenue[2024]:,}, 2025 £{email_revenue[2025]:,}")
print(f"margin on lost email revenue:  £{email_margin:,.0f}")
print(f"budget saved by the cut:       £{RESTORE_COST:,}")
print(f"margin lost per pound saved:   {(repeat_margin + email_margin) / RESTORE_COST:.1f}")
lost_revenue = lost_repeaters * REPEAT_REVENUE + email_revenue[2024] - email_revenue[2025]
print(f"break-even gross margin:       {RESTORE_COST / lost_revenue:.1%}")

# %% story-chart
import matplotlib.pyplot as plt
import chartstyle as cs

cs.apply()
story = fernhill.total_by_month()
before = story.repeat_rate[story.index < fernhill.CUT].mean() * 100
after = story.repeat_rate[story.index >= fernhill.CUT].mean() * 100
print(f"average before {before:.1f}%, after {after:.1f}%")
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(story.index, story.repeat_rate * 100, color=cs.BLUE, marker="o", markersize=4)
ax.set_ylim(0, 50)
ax.margins(x=.02)
cs.year_ticks(ax)
ax.axvline(fernhill.CUT, color=cs.MUTED, linewidth=1)
ax.annotate("January 2025: email budget cut\nfrom £14k to £4k a month", (fernhill.CUT, 44),
            xytext=(8, 0), textcoords="offset points", va="center", color=cs.SECONDARY)
ax.text(pd.Timestamp("2023-02-01"), before + 2.5, f"{before:.0f}% buy again within 90 days",
        color=cs.INK, fontweight="bold")
ax.text(pd.Timestamp("2025-02-15"), after - 5.5, f"{after:.0f}%", color=cs.INK, fontweight="bold")
ax.set_ylabel("90-day repeat rate (%)")
ax.set_title("Since we cut email, repeat buying has fallen from 38% to 26% of new customers",
             fontsize=11)
cs.save(fig, "viz-story-explanatory-repeat-rate.png")

# %% cost-benefit
parts = pd.Series({"Budget saved by the cut": RESTORE_COST,
                   "Margin lost on email orders": email_margin,
                   "Margin lost on repeat customers": repeat_margin})
fig, ax = plt.subplots(figsize=(8, 2.6))
colours = [cs.BASELINE, cs.BLUE, cs.BLUE]
ax.barh(parts.index[::-1], parts.values[::-1] / 1000, color=colours[::-1], height=.6)
for i, value in enumerate(parts.values[::-1] / 1000):
    ax.text(value + 5, i, f"£{value:,.0f}k", va="center", color=cs.SECONDARY)
ax.set_xlim(0, parts.max() / 1000 * 1.15)
ax.grid(False)
ax.set_xticks([])
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(True)
ax.tick_params(left=False)
ax.set_title("The cut saved £120k a year and gave up about £550k of margin", fontsize=11)
cs.save(fig, "viz-story-saved-vs-lost.png")
