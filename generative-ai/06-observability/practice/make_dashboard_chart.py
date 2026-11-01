"""Render the fortnight's dashboard to sources/images/ as three panels on one time axis."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from support_agent import PRICES_AS_OF, generate_traces
from support_agent.frames import traces_frame

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, SURFACE, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e7e6e2"
OUT = Path(__file__).parent.parent / "sources" / "images" / "support-agent-dashboard.png"

df = traces_frame(generate_traces())
df["day"] = pd.to_datetime(df["day"])
df["group"] = df["route"].where(df["route"] == "billing", "other routes")

daily = df.groupby("day").agg(cost=("cost_usd", "sum"), resolved=("outcome", lambda s: (s == "resolved").sum()))
daily["per_resolved"] = daily["cost"] / daily["resolved"]
p95 = df.groupby(["day", "group"])["latency_ms"].quantile(0.95).unstack() / 1000

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": GRID})
fig, axes = plt.subplots(3, 1, figsize=(9, 7.4), sharex=True, facecolor=SURFACE, constrained_layout=True)
last = daily.index[-1]


def panel(ax, title):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold", color=INK)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    ax.set_ylim(bottom=0)
    ax.axvspan(pd.Timestamp("2026-10-13 12:00"), pd.Timestamp("2026-10-16 12:00"), color="#ecebe7", zorder=0)


axes[0].plot(daily.index, daily["cost"], color=BLUE, linewidth=2)
panel(axes[0], "Model spend per day, USD (100 synthetic turns a day)")
axes[0].annotate("v2.0 shipped: timestamp in system prompt,\ncache writes on every call", xy=(pd.Timestamp("2026-10-15"), daily["cost"].max()),
                 xytext=(pd.Timestamp("2026-10-08"), daily["cost"].max() * 0.72), fontsize=9, color=MUTED)

axes[1].plot(daily.index, daily["per_resolved"], color=BLUE, linewidth=2)
panel(axes[1], "Model spend per resolved ticket, USD")
axes[1].annotate("v2.1 restores the cache. Nothing on this panel\nshows the quality regression still live", xy=(pd.Timestamp("2026-10-17"), daily["per_resolved"].iloc[-2]),
                 xytext=(pd.Timestamp("2026-10-05"), daily["per_resolved"].max() * 0.72), fontsize=9, color=MUTED)

for name, color in (("billing", ORANGE), ("other routes", BLUE)):
    axes[2].plot(p95.index, p95[name], color=color, linewidth=2, label=name)
    axes[2].annotate(name, xy=(last, p95[name].iloc[-1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=9, color=INK)
panel(axes[2], "p95 turn latency, seconds, by route")
axes[2].legend(loc="upper left", frameon=False, ncols=2, fontsize=9)
axes[2].annotate("get_invoice vendor stalls from 11 Oct", xy=(pd.Timestamp("2026-10-11"), p95["billing"].loc["2026-10-11"]),
                 xytext=(pd.Timestamp("2026-10-05 12:00"), p95["billing"].max() * 0.62), fontsize=9, color=MUTED)
axes[2].set_xlim(daily.index[0], last + pd.Timedelta(days=1.1))
axes[2].xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%-d %b"))
axes[2].xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=2))
fig.text(0.01, -0.012, f"Synthetic traces from practice/support_agent. Priced at Anthropic list prices read {PRICES_AS_OF}. Shaded: release v2.0.", fontsize=8, color=MUTED)
fig.savefig(OUT, dpi=130, bbox_inches="tight", facecolor=SURFACE)
print(OUT.name)
