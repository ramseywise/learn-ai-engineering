---
origin: synthesis
sources:
  - "McKinney, Python for Data Analysis, 2nd ed. (O'Reilly, 2017), ch. 10; 3rd ed. open access at https://wesmckinney.com/book/data-aggregation"
  - "Wickham, The Split-Apply-Combine Strategy for Data Analysis (JSS 2011), https://doi.org/10.18637/jss.v040.i01"
  - "McKinney, Data Structures for Statistical Computing in Python (SciPy 2010), https://doi.org/10.25080/Majora-92bf1922-00a"
  - "VanderPlas, Python Data Science Handbook (O'Reilly, 2016), ch. 3; https://jakevdp.github.io/PythonDataScienceHandbook/03.08-aggregation-and-grouping.html"
  - https://pandas.pydata.org/docs/user_guide/groupby.html
confidence: high
cleaned: 2026-11-01
---
# 5 — Groupby and Aggregation

Ask a shop owner what they want to know and almost every answer has the word "per" in it: revenue per region, orders per customer, average basket per month. Those are all one operation. You cut the table into groups, compute something on each, and glue the answers back together. It is the single pattern you will use most as an analyst, the heart of a SQL `GROUP BY` and of a spreadsheet pivot table alike, and pandas expresses it in one method. The method is deceptively simple. It can also return a number per group, a value per original row, or a smaller table per group, and which one you need depends on the question. This chapter works through each kind, shows how to get the totals right when ratios are involved, and ends with the pivot tables that a reader actually wants to look at.

## Split, apply, combine

Wickham named the pattern: break a big problem into pieces, work on each piece independently, then put the pieces back together. He observes that it appears at every stage of an analysis, from standardising values during preparation, to computing marginal summaries for display, to fitting a separate model for each panel ([Wickham, JSS 2011](https://doi.org/10.18637/jss.v040.i01)). Recognising the pattern is what lets you see that two questions which look different are really the same question.

```text
   SPLIT by product       APPLY sum to qty    COMBINE
  +--------+-----+
  | filter |  3  |
  | filter |  2  |  --->  filter: 15  ---+
  | filter |  4  |                        |     +---------+-----+
  | filter |  6  |                        |     | filter  |  15 |
  +--------+-----+                        +-->  | grinder |   2 |
  | grinder|  1  |  --->  grinder: 2  ---+      | kettle  |   4 |
  | grinder|  1  |                        |     | scale   |   2 |
  +--------+-----+                        |     +---------+-----+
  | kettle | ... |  --->  kettle: 4  ----+
  | scale  | ... |  --->  scale: 2  -----+
```

The frame is the same 11 orders as before, with the product table from chapter 4 merged on.

```python
import io
import numpy as np
import pandas as pd

csv = """order_id,date,customer,product,qty,unit_price,region
1001,2025-01-03,ana,kettle,1,48.0,north
1002,2025-01-03,ben,filter,3,6.5,south
1003,2025-01-05,ana,grinder,1,95.0,north
1004,2025-01-06,cara,filter,2,6.5,east
1005,2025-01-08,dev,kettle,2,48.0,unknown
1006,2025-01-09,ben,scale,1,22.0,south
1007,2025-01-11,eli,filter,4,6.5,north
1009,2025-01-14,cara,grinder,1,95.0,east
1010,2025-01-15,fay,scale,1,22.0,unknown
1011,2025-01-17,dev,filter,6,6.5,south
1012,2025-01-20,ben,kettle,1,48.0,south
"""
orders = pd.read_csv(io.StringIO(csv), parse_dates=["date"])
orders["revenue"] = orders["qty"] * orders["unit_price"]
```

```python
products = pd.DataFrame({
    "product":   ["kettle", "filter", "grinder", "scale"],
    "category":  ["brew", "consumable", "brew", "tools"],
    "unit_cost": [30.0, 2.5, 60.0, 12.0],
})
orders = orders.merge(products, on="product", how="left", validate="many_to_one")
orders["margin"] = orders["revenue"] - orders["qty"] * orders["unit_cost"]

totals = {}
for product, piece in orders.groupby("product"):
    totals[product] = int(piece["qty"].sum())
print(totals)
print(orders.groupby("product")["qty"].sum())
```

```text
{'filter': 15, 'grinder': 2, 'kettle': 4, 'scale': 2}
product
filter     15
grinder     2
kettle      4
scale       2
Name: qty, dtype: int64
```

The loop and the one-liner do the same thing. The loop also shows what a GroupBy object is: on its own it computes nothing, and iterating over it gives you pairs of a group key and the piece of the frame belonging to it. The computation only happens when you ask for an aggregation. As Wickham remarks of the alternative to loops, the reason to prefer this form is clarity of intent, since the book-keeping disappears ([Wickham, JSS 2011](https://doi.org/10.18637/jss.v040.i01)). He also marks the limit: the pattern assumes each piece is handled independently. A running mean, where each step overlaps the last, needs different tools, which chapter 6 provides.

## Keys and the first aggregations

A key can be a column name, a list of them, or any Series or array of the right length, which means you can group by something you compute on the spot. Multiple keys give you a MultiIndex, as in chapter 3. `as_index=False` keeps the keys as ordinary columns, which is often more convenient.

```python
print(orders.groupby("region")["revenue"].sum())
print(orders.groupby(["region", "category"])["revenue"].sum().head(4))
print(orders.groupby("region", as_index=False)["revenue"].sum().head(2))
print(orders.groupby(orders["date"].dt.day_name())["revenue"].sum().sort_values().tail(2))
print(orders.groupby(orders["revenue"] > 40)["qty"].mean())
```

```text
region
east       108.0
north      169.0
south      128.5
unknown    118.0
Name: revenue, dtype: float64
region  category
east    brew           95.0
        consumable     13.0
north   brew          143.0
        consumable     26.0
Name: revenue, dtype: float64
  region  revenue
0   east    108.0
1  north    169.0
date
Friday       106.5
Wednesday    118.0
Name: revenue, dtype: float64
revenue
False    2.833333
True     1.200000
Name: qty, dtype: float64
```

Two near-synonyms cause confusion. `size` counts rows in each group, including rows with missing values, and `count` counts non-missing values, column by column. They differ exactly when a column has gaps, and the difference is itself informative.

```python
g = pd.DataFrame({"region": ["n", "n", "s", "s", "s"], "rating": [5.0, None, 4.0, None, None]})
print(g.groupby("region").size())
print(g.groupby("region")["rating"].count())
print(g.groupby("region")["rating"].mean())
```

```text
region
n    2
s    3
dtype: int64
region
n    1
s    1
Name: rating, dtype: int64
region
n    5.0
s    4.0
Name: rating, dtype: float64
```

`rating` has a mean of 5.0 for the north based on one value out of two, and 4.0 for the south based on one value out of three. Without the counts next to them, those means look more solid than they are.

Aggregating a whole frame needs care in current pandas. Calling `mean` on a frame that still has text columns raises a `TypeError`, where old versions silently dropped those columns. Select the numeric columns you mean, or pass `numeric_only=True`.

```python
try:
    orders.groupby("region").mean()
except TypeError as e:
    print("TypeError:", str(e)[:50])
print(orders.groupby("region")[["qty", "revenue"]].mean())
print(orders.groupby("region").mean(numeric_only=True).columns.tolist())
```

```text
TypeError: dtype 'str' does not support operation 'mean'
          qty    revenue
region
east     1.50  54.000000
north    2.00  56.333333
south    2.75  32.125000
unknown  1.50  59.000000
['order_id', 'qty', 'unit_price', 'revenue', 'unit_cost', 'margin']
```

## agg: one row per group

An aggregation collapses each group to a single row. `agg` lets you compute several at once. The clearest form is **named aggregation**: each keyword names an output column, and takes a pair of source column and function. The output then has flat, meaningful column names that you chose, and not a two-level header to untangle.

```python
summary = orders.groupby("region").agg(
    orders=("order_id", "count"),
    customers=("customer", "nunique"),
    units=("qty", "sum"),
    revenue=("revenue", "sum"),
    biggest=("revenue", "max"),
)
print(summary.sort_values("revenue", ascending=False))
```

```text
         orders  customers  units  revenue  biggest
region
north         3          2      6    169.0     95.0
south         4          2     11    128.5     48.0
unknown       2          2      3    118.0     96.0
east          2          1      3    108.0     95.0
```

The function can be your own. It receives one group's column as a Series and returns one value. Built-in names run in fast compiled code while a Python function is called once per group, so prefer the names wherever one exists.

```python
def peak_to_peak(s):
    return s.max() - s.min()

print(orders.groupby("product").agg(price_spread=("unit_price", peak_to_peak), revenue_spread=("revenue", peak_to_peak)))
```

```text
         price_spread  revenue_spread
product
filter            0.0            26.0
grinder           0.0             0.0
kettle            0.0            48.0
scale             0.0             0.0
```

### Ratios: the mean-of-rates trap

Here is the error that most often survives into a real report. What is the margin rate of each region? It is tempting to compute a rate per order and average those rates. But that gives a 13.00 filter order the same weight as a 96.00 kettle order. The figure the business means is total margin over total revenue. Compute the numerator and the denominator per group, and only then divide.

```python
orders["rate"] = orders["margin"] / orders["revenue"]
by_region = orders.groupby("region").agg(revenue=("revenue", "sum"), margin=("margin", "sum"), mean_of_rates=("rate", "mean"))
by_region["true_rate"] = by_region["margin"] / by_region["revenue"]
print(by_region.round(3))
```

```text
         revenue  margin  mean_of_rates  true_rate
region
east       108.0    43.0          0.492      0.398
north      169.0    69.0          0.453      0.408
south      128.5    64.0          0.515      0.498
unknown    118.0    46.0          0.415      0.390
```

Read the `east` row. It has two orders: a 13.00 filter order at about 62% margin and a 95.00 grinder order at about 37%. Averaging those rates gives 0.492, while the shop in fact kept 43.0 out of 108.0, or 0.398. The two columns also rank regions differently: `east` beats `north` on the mean of rates, and `north` beats `east` on the true rate. The same trap applies to any ratio: conversion rate, average order value, cost per click.

## transform: one value per original row

Sometimes you want a group-level figure attached to each row: each order's share of its region's revenue, or how far it is from its product's average quantity. An aggregation is the wrong shape for that, since it returns one row per group. `transform` computes the group figure and broadcasts it back to the original rows, so the result lines up with the frame and can become a new column.

```python
orders["region_revenue"] = orders.groupby("region")["revenue"].transform("sum")
orders["share_of_region"] = orders["revenue"] / orders["region_revenue"]
print(orders[["order_id", "region", "revenue", "region_revenue", "share_of_region"]].head(4).round(3))
assert orders.groupby("region")["share_of_region"].sum().round(6).eq(1).all()
```

```text
   order_id region  revenue  region_revenue  share_of_region
0      1001  north     48.0           169.0            0.284
1      1002  south     19.5           128.5            0.152
2      1003  north     95.0           169.0            0.562
3      1004   east     13.0           108.0            0.120
```

McKinney's original pandas paper already has this example of subtracting group means from a dataset ([McKinney, SciPy 2010](https://doi.org/10.25080/Majora-92bf1922-00a)), and removing a group's level is one of Wickham's standard uses during preparation. It is what lets you ask "is this order large *for its product*?", a question the raw number cannot answer, as a large filter order is still cheaper than one kettle.

```python
qty_by_product = orders.groupby("product")["qty"]
orders["qty_vs_product"] = orders["qty"] - qty_by_product.transform("mean")
print(orders[["order_id", "product", "qty", "qty_vs_product"]].sort_values("qty_vs_product").tail(3).round(2))
```

```text
   order_id product  qty  qty_vs_product
6      1007  filter    4            0.25
4      1005  kettle    2            0.67
9      1011  filter    6            2.25
```

A group-wise fill is the same move. Filling a missing rating with the mean of its own region beats the global mean when regions differ, though as chapter 2 said, you should first ask why it is missing at all.

```python
g["rating_filled"] = g["rating"].fillna(g.groupby("region")["rating"].transform("mean"))
print(g)
```

```text
  region  rating  rating_filled
0      n     5.0            5.0
1      n     NaN            5.0
2      s     4.0            4.0
3      s     NaN            4.0
4      s     NaN            4.0
```

## filter and apply: keep or rebuild groups

`filter` decides for each group, by a function returning `True` or `False`, whether to keep all of its rows. To keep only the orders from repeat customers:

```python
repeat = orders.groupby("customer").filter(lambda d: len(d) >= 2)
print(sorted(repeat["customer"].unique()), len(repeat))
```

```text
['ana', 'ben', 'cara', 'dev'] 9
```

`apply` is the general escape hatch. It passes each group as a DataFrame to your function and stitches whatever comes back into a result. Use it when nothing more specific fits, such as selecting the top order per region or computing a weighted average, and reach for it last, as it is the slowest of the options.

```python
def top(d, n=1):
    return d.nlargest(n, "revenue")[["order_id", "customer", "revenue"]]

print(orders.groupby("region")[["order_id", "customer", "revenue"]].apply(top))

avg_price = orders.groupby("category")[["unit_price", "qty"]].apply(
    lambda d: np.average(d["unit_price"], weights=d["qty"])
)
print(avg_price.round(2))
```

```text
            order_id customer  revenue
region
east    7       1009     cara     95.0
north   2       1003      ana     95.0
south   10      1012      ben     48.0
unknown 4       1005      dev     96.0
category
brew          63.67
consumable     6.50
tools         22.00
dtype: float64
```

For the top row per group, a sort followed by `head` on a groupby gets you the same thing faster, and keeps the frame flat.

```python
print(orders.sort_values("revenue", ascending=False).groupby("region").head(1)[["region", "order_id", "revenue"]].sort_values("region"))
```

```text
     region  order_id  revenue
7      east      1009     95.0
2     north      1003     95.0
10    south      1012     48.0
4   unknown      1005     96.0
```

To decide among these four methods, ask what shape comes back.

| Method | Function gets | Function returns | Result has | Typical question |
|---|---|---|---|---|
| `agg` | one column of one group | a single value | one row per group | Revenue per region |
| `transform` | one column of one group | a single value, or one per row | the same rows as the input | Share of region, deviation from group mean |
| `filter` | a whole group | `True` or `False` | a subset of the input rows | Orders from repeat customers |
| `apply` | a whole group | anything | whatever you stitched together | Top order per region, weighted average |

## Groups from buckets

Chapter 2's `cut` and `qcut` produce keys ready for a groupby, which is how you get a table of behaviour by size band. Grouping by a categorical key raises a question of what to do with empty categories. Since pandas 3.0, the `observed` option defaults to `True`, so only categories present in the data appear, while `observed=False` lists all of them and is what you want for a report with a fixed row list.

```python
band = pd.cut(orders["revenue"], bins=[0, 20, 50, 100, 200], labels=["<=20", "20-50", "50-100", "100+"])
print(orders.groupby(band)["revenue"].agg(["count", "sum"]))
print(orders.groupby(band, observed=False)["revenue"].agg(["count", "sum"]))
```

```text
         count    sum
revenue
<=20         2   32.5
20-50        6  205.0
50-100       3  286.0
         count    sum
revenue
<=20         2   32.5
20-50        6  205.0
50-100       3  286.0
100+         0    0.0
```

## Missing keys vanish by default

A row whose group key is `NaN` is silently excluded from the result. If a third of your orders lack a region, your regional totals will not add up to your overall total, and nothing tells you. `dropna=False` keeps them as a group of their own. Comparing the sum of the groups with the overall total is a cheap check that catches this.

```python
k = pd.DataFrame({"region": ["n", None, "s", None], "revenue": [10.0, 20.0, 30.0, 40.0]})
print(k.groupby("region")["revenue"].sum().sum(), k["revenue"].sum())
print(k.groupby("region", dropna=False)["revenue"].sum())
```

```text
40.0 100.0
region
n      10.0
s      30.0
NaN    60.0
Name: revenue, dtype: float64
```

## Pivot tables and crosstabs

A spreadsheet pivot table is a groupby by two keys laid out as a grid. `pivot_table` does it directly, and it copes with the duplicate combinations that made `pivot` fail in chapter 4 by aggregating them. Its default `aggfunc` is the mean, which is rarely what you want for revenue, so state it. `margins=True` adds totals.

```python
pt = orders.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum", fill_value=0, margins=True, margins_name="total")
print(pt)
```

```text
category   brew  consumable  tools  total
region
east       95.0        13.0    0.0  108.0
north     143.0        26.0    0.0  169.0
south      48.0        58.5   22.0  128.5
unknown    96.0         0.0   22.0  118.0
total     382.0        97.5   44.0  523.5
```

`crosstab` is the special case of counting. `normalize` turns counts into shares of the row, the column or the whole, which is how you compare groups of different sizes.

```python
print(pd.crosstab(orders["region"], orders["category"]))
print(pd.crosstab(orders["region"], orders["category"], normalize="index").round(2))
```

```text
category  brew  consumable  tools
region
east         1           1      0
north        2           1      0
south        1           2      1
unknown      1           0      1
category  brew  consumable  tools
region
east      0.50        0.50   0.00
north     0.67        0.33   0.00
south     0.25        0.50   0.25
unknown   0.50        0.00   0.50
```

The whole chapter fits one sentence: say what one row of the output should mean, and that determines the keys and the method.

## Pitfalls

- **Averaging averages.** The mean of per-order or per-group rates weights small and large groups alike. Sum numerator and denominator, then divide.
- **Silent loss of `NaN` keys.** Check that the groups add up to the total, or use `dropna=False`.
- **`size` and `count` used interchangeably.** They differ when a column has gaps.
- **Means without counts.** A group mean built on one observation prints with the same confidence as one built on ten thousand. Always include a count.
- **Default `aggfunc`.** `pivot_table` averages unless told otherwise.
- **Old syntax.** `groupby(axis=1)` was removed in pandas 3.0, and `grouped["a", "b"]` must be a list, `grouped[["a", "b"]]`. On a frame with text columns, `grouped.mean()` now raises where old versions silently dropped them.
- **Reaching for `apply` first.** It is flexible and slow, and `agg` or `transform` usually does the job.

## Try it

1. For each customer, compute the number of orders, total revenue, and the date of the first and the last order.

<details><summary>Answer</summary>

```python
print(orders.groupby("customer").agg(
    n=("order_id", "count"), revenue=("revenue", "sum"), first=("date", "min"), last=("date", "max")
).sort_values("revenue", ascending=False))
```

```text
          n  revenue      first       last
customer
ana       2    143.0 2025-01-03 2025-01-05
dev       2    135.0 2025-01-08 2025-01-17
cara      2    108.0 2025-01-06 2025-01-14
ben       3     89.5 2025-01-03 2025-01-20
eli       1     26.0 2025-01-11 2025-01-11
fay       1     22.0 2025-01-15 2025-01-15
```

</details>

2. Add a column giving each order's rank by revenue within its region, largest first.

<details><summary>Answer</summary>

```python
orders["rank_in_region"] = orders.groupby("region")["revenue"].rank(ascending=False, method="first").astype("int64")
print(orders.sort_values(["region", "rank_in_region"])[["region", "order_id", "revenue", "rank_in_region"]].head(5))
```

```text
  region  order_id  revenue  rank_in_region
7   east      1009     95.0               1
3   east      1004     13.0               2
2  north      1003     95.0               1
0  north      1001     48.0               2
6  north      1007     26.0               3
```

</details>

3. Which category has the highest margin rate? Compute it correctly as a ratio of sums, and compare it with the mean of per-order rates.

<details><summary>Answer</summary>

```python
c = orders.groupby("category").agg(rev=("revenue", "sum"), mar=("margin", "sum"), mean_rate=("rate", "mean"))
c["rate"] = c["mar"] / c["rev"]
print(c.round(3))
```

```text
              rev    mar  mean_rate   rate
category
brew        382.0  142.0      0.372  0.372
consumable   97.5   60.0      0.615  0.615
tools        44.0   20.0      0.455  0.455
```

The two agree here, to three places, because all orders of one product share one rate and products within a category have similar rates. Regions mix very different products, which is why they diverged above.

</details>

4. In `practice/6_Aggregation.ipynb`, repeat these moves on the tips data (`data/tips.csv`, from `bash practice/fetch_data.sh`) and small synthetic frames. `practice/mckinney/ch10.ipynb` has the book's versions of group-wise fill, weighted average and the tipping pivot tables (needs `bash practice/fetch_data.sh`).

## Interview checklist

| Question | What a good answer covers |
|---|---|
| What is split-apply-combine? | Break data into groups, operate on each independently, reassemble (Wickham 2011). It is `GROUP BY` and pivot tables as one idea. |
| `size` or `count`? | `size` counts rows, `count` counts non-missing values per column. |
| What is the difference between `agg`, `transform`, `filter` and `apply`? | One row per group, same rows as the input, a subset of input rows, and anything. |
| How do you compute a group's rate? | Ratio of sums. The mean of per-row rates weights every row the same, whatever its size. |
| How would you get each row's share of its group? | `x / x.groupby(key).transform("sum")`. |
| What happens to `NaN` group keys? | They are dropped by default. Use `dropna=False`, and check that groups add up to the total. |
| How do you get the top N per group? | `sort_values` then `groupby(...).head(n)`, or `apply` with `nlargest`. |
| `pivot_table` or `crosstab`? | `pivot_table` aggregates any value and defaults to the mean. `crosstab` counts by default and can `normalize` into shares. |
| How does this map to SQL? | Keys are `GROUP BY`, aggregations are `SUM`, `COUNT`, a filter on groups is `HAVING`, and `transform` is a window function with `OVER (PARTITION BY ...)`. |

## Next

Every group so far has been a label. The most common grouping of all is by time, and time has its own rules: months have different lengths, a label can sit at either end of a period, and the order of rows carries meaning. Next: [Time series](06-time-series.md).
