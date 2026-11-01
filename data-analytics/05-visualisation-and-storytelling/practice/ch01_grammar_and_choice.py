# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pandas", "matplotlib", "altair", "vl-convert-python"]
# ///
"""Chapter 1: why we plot, the grammar of a chart, and choosing a form. Run: uv run ch01_grammar_and_choice.py"""
# %% anscombe-stats
import numpy as np
import pandas as pd

# The four datasets exactly as published in Anscombe (1973).
x123 = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
x4 = [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8]
quartet = {
    "I": (x123, [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]),
    "II": (x123, [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]),
    "III": (x123, [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]),
    "IV": (x4, [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]),
}
rows = []
for name, (x, y) in quartet.items():
    slope, intercept = np.polyfit(x, y, 1)
    rows.append({"set": name, "mean_x": np.mean(x), "mean_y": np.mean(y),
                 "var_y": np.var(y, ddof=1), "corr": np.corrcoef(x, y)[0, 1],
                 "slope": slope, "intercept": intercept})
print(pd.DataFrame(rows).round(2).to_string(index=False))

# %% anscombe-plot
import matplotlib.pyplot as plt
import chartstyle as cs

cs.apply()
fig, axes = plt.subplots(1, 4, figsize=(9, 2.8), sharex=True, sharey=True)
for ax, (name, (x, y)) in zip(axes, quartet.items()):
    slope, intercept = np.polyfit(x, y, 1)
    line_x = np.array([3, 20])
    ax.plot(line_x, slope * line_x + intercept, color=cs.BASELINE, linewidth=1.5)
    ax.scatter(x, y, s=34, color=cs.BLUE, edgecolor=cs.SURFACE, linewidth=1, zorder=3)
    ax.set_title(f"Set {name}")
    ax.set_xlabel("x")
axes[0].set_ylabel("y")
fig.suptitle("Same means, variance, correlation and fitted line. Four different stories.",
             x=0.01, ha="left", fontsize=12, fontweight="bold")
cs.save(fig, "viz-anscombe-quartet.png")

# %% load-fernhill
import fernhill

monthly = fernhill.load_monthly()
print(monthly.head(4).to_string(index=False))
print(len(monthly), "rows")
yearly = monthly.assign(year=monthly.month.dt.year).groupby("year")[["revenue", "spend"]].sum()
print(yearly)
print(fernhill.total_by_month().assign(year=lambda d: d.index.year)
      .groupby("year")["repeat_rate"].mean().round(3))

# %% grammar
import altair as alt

data = monthly.assign(channel=monthly.channel.map(fernhill.LABELS))
order = [fernhill.LABELS[c] for c in fernhill.CHANNELS]
colour = alt.Color("channel:N", sort=order, title="Channel",
                   scale=alt.Scale(domain=order, range=cs.CATEGORICAL))
x = alt.X("yearmonth(month):T", title=None, axis=alt.Axis(format="%Y", tickCount="year"))
y = alt.Y("sum(revenue):Q", title="Revenue (£)")

base = alt.Chart(data).properties(width=250, height=190)          # data
lines = base.mark_line(strokeWidth=2).encode(x=x, y=y, color=colour)  # geom + aesthetics
areas = base.mark_area().encode(x=x, y=y, color=colour)           # change only the mark
small = (base.properties(width=112, height=78).mark_line(strokeWidth=2)
         .encode(x=x, y=alt.Y("sum(revenue):Q", title=None), color=colour)
         .facet(facet=alt.Facet("channel:N", sort=order, title=None), columns=2))  # add a facet
grammar = (alt.hconcat(lines, areas, small).resolve_scale(color="shared")
           .configure_view(stroke=None).configure_axis(gridColor=cs.GRID, domainColor=cs.BASELINE)
           .configure(background=cs.SURFACE, font="Helvetica Neue"))
grammar.save(cs.IMAGES / "viz-grammar-one-spec-three-marks.png", scale_factor=1.5)
print(sorted(lines.to_dict()["encoding"]), lines.to_dict()["mark"]["type"])

# %% share-exhibit
share = (monthly[monthly.month.dt.year == 2025].groupby("channel")["revenue"].sum()
         .sort_values(ascending=False))
share = share / share.sum()
print(share.round(3).to_string())

fig, (left, right) = plt.subplots(1, 2, figsize=(8, 3.3))
colours = [cs.CHANNEL_COLOUR[c] for c in share.index]
names = [fernhill.LABELS[c] for c in share.index]
left.pie(share, colors=colours, startangle=90, counterclock=False,
         wedgeprops={"edgecolor": cs.SURFACE, "linewidth": 2})
left.set_title("Counter-example: which slice is second?")
right.barh(names[::-1], share.values[::-1] * 100, color=cs.BLUE, height=.6)
for i, value in enumerate(share.values[::-1] * 100):
    right.text(value + .8, i, f"{value:.0f}%", va="center", color=cs.SECONDARY)
right.set_title("Sorted bars: position on a common scale")
right.grid(False)
right.set_xticks([])
right.spines["bottom"].set_visible(False)
right.spines["left"].set_visible(True)
right.tick_params(left=False)
cs.save(fig, "viz-pie-vs-sorted-bars.png")

# %% dual-axis
story = fernhill.total_by_month()


def dual(ax, revenue_limits, rate_limits, title):
    """A deliberately bad chart: two y scales the author can slide independently."""
    ax.plot(story.index, story.revenue / 1000, color=cs.BLUE, label="Revenue")
    ax.set_ylim(revenue_limits)
    ax.set_ylabel("Revenue (£k)")
    twin = ax.twinx()
    twin.plot(story.index, story.repeat_rate * 100, color=cs.ORANGE, label="Repeat rate")
    twin.set_ylim(rate_limits)
    twin.set_ylabel("90-day repeat rate (%)")
    twin.grid(False)
    ax.set_title(title)
    cs.year_ticks(ax)
    ax.figure.legend(handles=[*ax.get_lines(), *twin.get_lines()], loc="outside lower center",
                     ncols=2) if ax is a else None


fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.4))
dual(a, (0, 1600), (0, 100), "Counter-example: nothing much happens")
dual(b, (300, 800), (24, 40), "Same data: a collapse crossing a surge")
cs.save(fig, "viz-dual-axis-two-stories.png")

# %% two-panels
fig, (top, bottom) = plt.subplots(2, 1, figsize=(8, 4.2), sharex=True, height_ratios=[1, 1])
top.plot(story.index, story.revenue / 1000, color=cs.BLUE)
top.set_ylim(0)
top.set_title("Monthly revenue (£k) keeps growing")
bottom.plot(story.index, story.repeat_rate * 100, color=cs.ORANGE)
bottom.set_ylim(0, 40)
bottom.set_title("Share of new customers buying again within 90 days (%) steps down")
for ax in (top, bottom):
    ax.axvline(fernhill.CUT, color=cs.MUTED, linewidth=1)
cs.year_ticks(bottom)
bottom.annotate("Email budget cut", (fernhill.CUT, 6), xytext=(6, 0),
                textcoords="offset points", color=cs.SECONDARY)
cs.save(fig, "viz-two-panels-instead-of-dual-axis.png")

# %% baseline
quarter = (story.revenue[story.index.year == 2025].groupby(lambda d: d.quarter).sum() / 1000)
print(quarter.round(0).to_string())
q = quarter.iloc[:3]  # Q4 is the Christmas peak, so compare the three ordinary quarters
fig, (a, b) = plt.subplots(1, 2, figsize=(8, 3))
for ax, bottom_limit, title in ((a, 1100, "Counter-example: y axis starts at £1.1m"),
                                (b, 0, "Bars start at zero")):
    ax.bar([f"Q{i}" for i in q.index], q.values, color=cs.BLUE, width=.6)
    ax.set_ylim(bottom_limit, q.max() * 1.06)
    ax.set_title(title)
    ax.set_ylabel("Revenue (£k)")
print(f"real Q3 vs Q1: {q.iloc[2] / q.iloc[0] - 1:+.0%}, "
      f"bar heights on the left: {(q.iloc[2] - 1100) / (q.iloc[0] - 1100) - 1:+.0%}")
cs.save(fig, "viz-bar-baseline-truncated-vs-zero.png")
