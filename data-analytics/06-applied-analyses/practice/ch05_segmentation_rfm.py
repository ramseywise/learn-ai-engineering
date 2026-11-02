# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "matplotlib", "scikit-learn", "scipy"]
# ///
"""Chapter 5: with money for one retention campaign, which customers should get it?

Run from this folder with: uv run ch05_segmentation_rfm.py
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

import chartstyle as cs
from retail import load_orders

cs.apply()
SEED = 20250101

# %% features
orders = load_orders()
snapshot = pd.Timestamp("2025-06-30")
past = orders[orders.order_date <= snapshot]
future = orders[orders.order_date > snapshot]
rfm = past.groupby("customer_id").agg(last=("order_date", "max"), frequency=("order_id", "count"),
                                      monetary=("value", "mean"), past_value=("value", "sum"))
rfm["recency"] = (snapshot - rfm.pop("last")).dt.days
rfm["future_value"] = future.groupby("customer_id").value.sum().reindex(rfm.index, fill_value=0)
rfm["bought_again"] = rfm.future_value > 0
print(len(rfm), "customers at the snapshot")
print(rfm[["recency", "frequency", "monetary", "future_value"]].describe().loc[["mean", "50%", "max"]].round(1).to_string())

# %% scores
def quintile(series, ascending=True):
    """Scores 1 to 5, with ties broken by rank so that heavily tied columns still split."""
    return pd.qcut(series.rank(method="first", ascending=ascending), 5, labels=False) + 1


rfm["R"] = quintile(rfm.recency, ascending=False)       # most recent = 5
rfm["F"] = quintile(rfm.frequency)
rfm["M"] = quintile(rfm.monetary)
print(rfm.frequency.value_counts(normalize=True).sort_index().head(4).round(3).to_string())


def name(row):
    if row.R >= 4 and row.F >= 4:
        return "Champions"
    if row.R <= 2 and row.F >= 4:
        return "At risk"
    if row.R >= 4 and row.F <= 2:
        return "New"
    if row.R <= 2 and row.F <= 2:
        return "Hibernating"
    return "Middle"


rfm["segment"] = rfm.apply(name, axis=1)
ORDER = ["Champions", "At risk", "Middle", "New", "Hibernating"]


def validate(frame, by):
    out = frame.groupby(by).agg(customers=("past_value", "size"), recency=("recency", "median"), frequency=("frequency", "mean"),
                                past_value=("past_value", "mean"), buy_again=("bought_again", "mean"), future_value=("future_value", "mean"))
    out["share_of_future"] = frame.groupby(by).future_value.sum() / frame.future_value.sum()
    return out


print(validate(rfm, "segment").loc[ORDER].round(2).to_string())

# %% chart_segments
table = validate(rfm, "segment").loc[ORDER]
fig, ax = plt.subplots(figsize=(8, 3.6))
bars = ax.barh(ORDER[::-1], table.future_value[::-1], height=.6, color=cs.BLUE)
ax.bar_label(bars, labels=[f"£{v:.0f} · {c:,} customers" for v, c in zip(table.future_value[::-1], table.customers[::-1])],
             padding=4, color=cs.SECONDARY)
ax.grid(False)
ax.set_xlim(0, table.future_value.max() * 1.45)
ax.set_xlabel("Mean revenue per customer in the six months after the snapshot (£)")
ax.set_title("Segments set on 30 June, judged on July to December")
cs.save(fig, "applied-rfm-segments.png")

# %% rf_grid
grid = rfm.assign(rec=pd.cut(rfm.recency, [-1, 60, 180, 365, 10_000], labels=["0-60", "61-180", "181-365", "366+"]),
                  freq=pd.cut(rfm.frequency, [0, 1, 2, 4, 1_000], labels=["1", "2", "3-4", "5+"]))
print(grid.pivot_table(index="rec", columns="freq", values="future_value", aggfunc="mean", observed=True).round(0).to_string())
print(grid.pivot_table(index="rec", columns="freq", values="future_value", aggfunc="size", observed=True).to_string())

# %% kmeans
features = np.column_stack([np.log1p(rfm.recency), np.log(rfm.frequency), np.log(rfm.monetary)])
X = StandardScaler().fit_transform(features)
sample = np.random.default_rng(SEED).choice(len(X), 5000, replace=False)
for k in range(2, 8):
    labels = KMeans(k, n_init=10, random_state=SEED).fit_predict(X)
    print(k, round(silhouette_score(X[sample], labels[sample]), 3))

km = KMeans(4, n_init=10, random_state=SEED).fit(X)
rfm["cluster"] = km.labels_
ordered = validate(rfm, "cluster").sort_values("future_value", ascending=False)
print(ordered.join(rfm.groupby("cluster").monetary.mean().rename("order_value")).round(2).to_string())
print("largest overlap of each cluster with the named segments")
print(pd.crosstab(rfm.cluster, rfm.segment, normalize="index").loc[ordered.index, ORDER].round(2).to_string())

# %% concentration
ranked = rfm.sort_values("past_value", ascending=False)
top = len(ranked) // 10
past_top = ranked.past_value.iloc[:top].sum() / ranked.past_value.sum()
future_top = ranked.future_value.iloc[:top].sum() / ranked.future_value.sum()
best_future = rfm.future_value.sort_values(ascending=False).iloc[:top].sum() / rfm.future_value.sum()
print(f"top decile by past value holds {past_top:.1%} of past value and {future_top:.1%} of future value")
print(f"the top decile by future value itself holds {best_future:.1%} of future value")
print(f"Spearman, past value vs future value: {spearmanr(rfm.past_value, rfm.future_value)[0]:.3f}")
two = rfm[rfm.bought_again]
later = future.groupby("customer_id").value.mean().reindex(two.index)
print(f"customers who buy in both periods, {len(two)}: Spearman of past and future order value {spearmanr(two.monetary, later)[0]:.3f}")

# %% chart_concentration
fig, ax = plt.subplots()
x = np.arange(1, len(ranked) + 1) / len(ranked) * 100
ax.plot(x, ranked.past_value.cumsum() / ranked.past_value.sum() * 100, color=cs.BLUE, label="Past value (what the ranking was built on)")
ax.plot(x, ranked.future_value.cumsum() / ranked.future_value.sum() * 100, color=cs.ORANGE, label="Future value of the same customers")
ax.plot([0, 100], [0, 100], color=cs.BASELINE, lw=1, label="No concentration")
ax.axvline(10, color=cs.BASELINE, lw=1)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_xlabel("Customers, ranked by value up to 30 June (%)")
ax.set_ylabel("Cumulative share of value (%)")
ax.set_title("The top tenth by past value still brings 44% of future value")
ax.legend(loc="lower right")
cs.save(fig, "applied-rfm-concentration.png")

# %% campaign
MARGIN, COST = .35, 1.50
aov = past.value.mean()
print(f"average order £{aov:.2f}, margin per extra order £{aov * MARGIN:.2f}, cost per contact £{COST:.2f}")
print(f"breakeven: {COST / (aov * MARGIN):.1%} extra customers ordering once")
lift = COST / (aov * MARGIN)
lapsing = rfm[rfm.recency.between(61, 180) & (rfm.frequency >= 3)]
groups = {"At risk (R 1-2, F 4-5)": rfm[rfm.segment == "At risk"], "Hibernating": rfm[rfm.segment == "Hibernating"],
          "Lapsing (61-180 days, 3+ orders)": lapsing}
for label, group in groups.items():
    base = group.bought_again.mean()
    n = (norm.ppf(.975) + norm.ppf(.8)) ** 2 * (base * (1 - base) + (base + lift) * (1 - base - lift)) / lift ** 2
    print(f"{label:34s} {len(group):5,} customers, buy again {base:5.1%}, breakeven needs {(base + lift) / base:4.1f}x, n per arm {n:,.0f}")
print(f"cost to contact the lapsing group £{len(lapsing) * COST:,.0f}")
