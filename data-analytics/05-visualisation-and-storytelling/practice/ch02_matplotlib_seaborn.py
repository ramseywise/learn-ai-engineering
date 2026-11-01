# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pandas", "matplotlib", "seaborn"]
# ///
"""Chapter 2: the matplotlib object model, decluttering, and seaborn. Run: uv run ch02_matplotlib_seaborn.py"""
# %% default
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import chartstyle as cs
import fernhill

monthly = fernhill.load_monthly()
wide = monthly.pivot(index="month", columns="channel", values="revenue")[fernhill.CHANNELS] / 1000

plt.rcdefaults()                        # matplotlib's own defaults, for the "before" picture
fig, ax = plt.subplots(figsize=(8, 4))  # a Figure holding one Axes
for channel in fernhill.CHANNELS:
    ax.plot(wide.index, wide[channel], marker="o", label=channel)
ax.set_title("revenue by channel")
ax.set_xlabel("month")
ax.set_ylabel("revenue")
ax.grid(True)
ax.legend()
fig.savefig(cs.IMAGES / "viz-matplotlib-default-chart.png", dpi=150)
plt.close(fig)
print(type(fig).__name__, type(ax).__name__, len(ax.get_lines()), "Line2D artists")

# %% decluttered
cs.apply()
fig, ax = plt.subplots(figsize=(8, 4))
nudge = {"email": 5, "referral": -6}                # two line ends land close together
for channel in fernhill.CHANNELS:
    ax.plot(wide.index, wide[channel], color=cs.CHANNEL_COLOUR[channel],
            label=fernhill.LABELS[channel])
    ax.annotate(fernhill.LABELS[channel], (wide.index[-1], wide[channel].iloc[-1]),
                xytext=(6, nudge.get(channel, 0)), textcoords="offset points", va="center",
                color=cs.SECONDARY)                 # text wears ink, not the series colour
ax.set_ylim(0)
ax.margins(x=0)
cs.year_ticks(ax)
ax.set_title("Paid social overtook email in January 2025", pad=26)
ax.set_ylabel("Monthly revenue (£k)")
ax.legend(ncols=4, loc="lower left", bbox_to_anchor=(0, 1), fontsize=9, borderaxespad=0)
fig.get_layout_engine().set(rect=(0, 0, .9, 1))     # leave room for the end labels
cs.save(fig, "viz-matplotlib-decluttered-chart.png")

# %% repeat-table
repeat = fernhill.load_repeat()
repeat["period"] = np.where(repeat.month >= fernhill.CUT, "after", "before")
table = (repeat.groupby(["channel", "period"])[["repeat_90d", "new_customers"]].sum()
         .eval("rate = repeat_90d / new_customers")["rate"].unstack()[["before", "after"]])
table["change_pts"] = (table.after - table.before) * 100
print(table.loc[fernhill.CHANNELS].round(3).to_string())

# %% small-multiples
rate = repeat.assign(rate=repeat.repeat_90d / repeat.new_customers * 100)
fig, axes = plt.subplots(1, 4, figsize=(9, 2.6), sharex=True, sharey=True)
for ax, channel in zip(axes, fernhill.CHANNELS):
    for other in fernhill.CHANNELS:                 # every other channel, quietly, for context
        if other != channel:
            part = rate[rate.channel == other]
            ax.plot(part.month, part.rate, color=cs.GRID, linewidth=1)
    part = rate[rate.channel == channel]
    ax.plot(part.month, part.rate, color=cs.BLUE)
    ax.axvline(fernhill.CUT, color=cs.MUTED, linewidth=1)
    ax.set_title(fernhill.LABELS[channel])
    ax.set_ylim(0, 60)
    cs.year_ticks(ax)
    ax.tick_params(axis="x", labelsize=8)
axes[0].set_ylabel("90-day repeat rate (%)")
cs.save(fig, "viz-small-multiples-repeat-rate.png")

# %% seaborn-tips
import seaborn as sns

tips = pd.read_csv("../../01-python-for-data-analysis/practice/data/tips.csv")
print(tips.shape, list(tips.columns))
print(tips.assign(pct=tips.tip / tips.total_bill).groupby(["time", "smoker"])["pct"]
      .median().round(3).to_string())
grid = sns.relplot(data=tips, x="total_bill", y="tip", col="time", hue="smoker",
                   palette=[cs.BLUE, cs.ORANGE], s=36, height=3.4, aspect=1.15,
                   edgecolor=cs.SURFACE, linewidth=.8)
grid.set_axis_labels("Total bill ($)", "Tip ($)")
grid.set_titles("{col_name}")
grid.savefig(cs.IMAGES / "viz-seaborn-tips-facets.png")
plt.close("all")
print(type(grid).__name__, len(grid.axes.flat), "axes")

# %% seaborn-distribution
orders = fernhill.load_orders()
sorted_categories = orders.groupby("category")["value"].median().sort_values(ascending=False).index
print(orders.groupby("category")["value"].describe()[["count", "50%", "mean", "max"]]
      .loc[sorted_categories].round(1).to_string())
fig, ax = plt.subplots(figsize=(8, 3.6))
sns.boxplot(data=orders, x="value", y="category", hue="device", order=sorted_categories,
            hue_order=["mobile", "desktop"], palette=[cs.BLUE, cs.ORANGE], fliersize=1.5,
            log_scale=True, linewidth=1, gap=.15, ax=ax)
ax.set_xticks([10, 30, 100, 300, 1000], labels=["£10", "£30", "£100", "£300", "£1,000"])
ax.minorticks_off()
ax.set_xlabel("Order value (log scale)")
ax.set_ylabel(None)
ax.grid(axis="x")
ax.grid(axis="y", visible=False)
ax.set_title("Furniture baskets dwarf the rest, and desktop runs higher in every category", pad=26)
ax.legend(ncols=2, loc="lower left", bbox_to_anchor=(0, 1), borderaxespad=0, title=None)
cs.save(fig, "viz-seaborn-order-value-distribution.png")

# %% heatmap-diverging
from matplotlib.colors import LinearSegmentedColormap

m = monthly.assign(year=monthly.month.dt.year, quarter=monthly.month.dt.quarter)
by_quarter = m.groupby(["channel", "year", "quarter"])["revenue"].sum().unstack("year")
change = ((by_quarter[2025] / by_quarter[2024] - 1) * 100).unstack("quarter").loc[fernhill.CHANNELS]
change.index = [fernhill.LABELS[c] for c in change.index]
change.columns = [f"Q{q}" for q in change.columns]
print(change.round(0).to_string())
diverging = LinearSegmentedColormap.from_list("blue_red", ["#e34948", "#f0efec", "#2a78d6"])
fig, ax = plt.subplots(figsize=(6.5, 2.9))
sns.heatmap(change, annot=True, fmt="+.0f", cmap=diverging, center=0, vmin=-150, vmax=150,
            linewidths=2, linecolor=cs.SURFACE, cbar_kws={"label": "% change"}, ax=ax)
ax.tick_params(left=False, bottom=False, rotation=0)
ax.set_title("Revenue change, 2025 against 2024 (%)")
ax.grid(False)
cs.save(fig, "viz-seaborn-diverging-heatmap.png")

# %% file-formats
from pathlib import Path

Path("output").mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(wide.index, wide["email"], color=cs.AQUA)
for suffix in ("png", "svg", "pdf"):
    path = Path(f"output/format-test.{suffix}")
    fig.savefig(path)
    print(suffix, path.stat().st_size // 1024, "KB")
plt.close(fig)
