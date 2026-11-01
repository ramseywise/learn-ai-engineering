---
origin: synthesis
sources:
  - "McKinney, Python for Data Analysis, 2nd ed. (O'Reilly, 2017), ch. 4-5, 8.1; 3rd ed. open access at https://wesmckinney.com/book/pandas-basics"
  - "VanderPlas, Python Data Science Handbook (O'Reilly, 2016), ch. 2-3; https://jakevdp.github.io/PythonDataScienceHandbook/03.02-data-indexing-and-selection.html"
  - "Harris et al., Array programming with NumPy (Nature 2020), https://doi.org/10.1038/s41586-020-2649-2"
  - https://pandas.pydata.org/docs/user_guide/indexing.html
confidence: high
cleaned: 2026-11-01
---
# 3 — Indexing and Selection

Nearly everything you do to a frame starts with saying which part of it you mean: January's orders, the revenue column, the top row of each product. Pandas gives you several ways to say this, and the differences between them are the source of more confusion for newcomers than anything else in the library. They look alike, they often give the same answer on small examples, and then one day your rows get filtered and the same code returns the wrong row without complaint. This chapter makes the rules explicit. It starts with the NumPy array underneath, since positions and masks work the same way there, and then adds labels. By the end, `loc` and `iloc` should feel like two clear questions, "which label?" and "which position?", and you will know when each one is the right question to ask.

## Underneath: the NumPy array

Every numeric pandas column is stored in an array, so NumPy's model of selection is worth learning directly. `practice/3_Arrays.ipynb` is the drill for this section. An array is a block of same-typed values in contiguous memory, with a shape. Harris and colleagues describe the design: the array stores a data pointer, a dtype, a shape and strides, and that layout is what lets whole-array operations run in compiled code ([Harris et al., Nature 2020](https://doi.org/10.1038/s41586-020-2649-2)). Selection comes in three forms, which you will see again in pandas.

```python
import numpy as np

qty = np.array([1, 3, 1, 2, 2, 1])
print(qty[0], qty[-1])        # one position
print(qty[1:4])               # a slice: start included, stop excluded
print(qty[qty >= 2])          # a boolean mask
print(qty[[0, 2, 5]])         # a list of positions
```

```text
1 1
[3 1 2]
[3 2 2]
[1 1 1]
```

The mask deserves a second look, because it is the single most used selection tool in analysis. `qty >= 2` is itself an array of `True` and `False`, one per element, and using it as an index keeps the `True` positions. Vectorised comparison plus mask replaces the loop-with-an-if that you would write in plain Python.

A two-dimensional array takes one selector per axis, with a comma between. **Axis 0** runs down the rows and **axis 1** runs across the columns. Summing along an axis collapses that axis.

```python
daily = np.array([[4, 30, 2],
                  [5, 25, 0],
                  [3, 41, 1]])   # rows are days, columns are products
print(daily.shape)
print(daily[1, 2], daily[:, 0], daily[0, :])
print(daily.sum(axis=0))         # total per product (collapses the rows)
print(daily.sum(axis=1))         # total per day (collapses the columns)
print(daily * 2)                 # arithmetic is element-wise
```

```text
(3, 3)
0 [4 5 3] [ 4 30  2]
[12 96  3]
[36 30 45]
[[ 8 60  4]
 [10 50  0]
 [ 6 82  2]]
```

`np.where` is the vectorised if-else: it takes a condition and two values, and you will use it for conditional columns later in this chapter.

```python
print(np.where(qty >= 2, "bulk", "single"))
```

```text
['single' 'bulk' 'single' 'bulk' 'bulk' 'single']
```

An array has no idea that column 1 means filters. Getting that wrong is a silent bug, and labels are the fix.

## The orders frame

The rest of the chapter uses the 11 clean orders that chapter 2 produced. Each later chapter starts from this same block, so you can run any one of them alone.

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
print(orders)
```

```text
    order_id       date customer  product  qty  unit_price   region  revenue
0       1001 2025-01-03      ana   kettle    1        48.0    north     48.0
1       1002 2025-01-03      ben   filter    3         6.5    south     19.5
2       1003 2025-01-05      ana  grinder    1        95.0    north     95.0
3       1004 2025-01-06     cara   filter    2         6.5     east     13.0
4       1005 2025-01-08      dev   kettle    2        48.0  unknown     96.0
5       1006 2025-01-09      ben    scale    1        22.0    south     22.0
6       1007 2025-01-11      eli   filter    4         6.5    north     26.0
7       1009 2025-01-14     cara  grinder    1        95.0     east     95.0
8       1010 2025-01-15      fay    scale    1        22.0  unknown     22.0
9       1011 2025-01-17      dev   filter    6         6.5    south     39.0
10      1012 2025-01-20      ben   kettle    1        48.0    south     48.0
```

## Three selectors: `[]`, `loc` and `iloc`

The plain square bracket is a convenience with a mixed job. Given a column name, or a list of names, it selects columns. Given a boolean Series, it filters rows. Learn those two uses and stop there. For anything else, ask the precise question with one of two accessors:

- **`.loc`** selects by **label**: `df.loc[row_labels, column_labels]`.
- **`.iloc`** selects by integer **position**: `df.iloc[row_positions, column_positions]`.

```python
print(orders["product"].head(2))             # one name: a Series
print(orders[["product", "qty"]].head(2))    # a list of names: a DataFrame
print(orders[orders["qty"] >= 4])            # a boolean Series: filter rows
```

```text
0    kettle
1    filter
Name: product, dtype: str
  product  qty
0  kettle    1
1  filter    3
   order_id       date customer product  qty  unit_price region  revenue
6      1007 2025-01-11      eli  filter    4         6.5  north     26.0
9      1011 2025-01-17      dev  filter    6         6.5  south     39.0
```

```python
print(orders.loc[2, "product"])              # row label 2, column label "product"
print(orders.iloc[2, 3])                     # third row, fourth column
print(orders.loc[0:2, ["customer", "qty"]])  # labels 0 to 2 INCLUDED
print(orders.iloc[0:2, [2, 4]])              # positions 0 and 1; 2 is EXCLUDED
```

```text
grinder
grinder
  customer  qty
0      ana    1
1      ben    3
2      ana    1
  customer  qty
0      ana    1
1      ben    3
```

Look at the last two results. They use what appears to be the same slice, `0:2`, and return three rows and two rows. A position slice excludes its end, like all of Python. A label slice includes its end, because labels have no natural "one past the last": if you ask for `"filter":"kettle"` in a sorted index you want kettle in the result, and you may not know which label follows it.

```text
             labels   positions         .loc[0:2]    .iloc[0:2]
  row 1001     0         0              included     included
  row 1002     1         1              included     included
  row 1003     2         2              included     excluded
  row 1004     3         3
```

Here the labels happen to equal the positions, which is exactly what makes the difference easy to miss. It stops being true the moment you filter.

## The integer index trap

Filtering keeps the original labels, so the labels of a filtered frame have gaps. Now `loc` and `iloc` give different answers to what looks like the same question, and neither one complains.

```python
filters = orders[orders["product"] == "filter"]
print(filters[["order_id", "customer"]])
print("iloc[1]:", filters.iloc[1]["order_id"])
print("loc[3]: ", filters.loc[3]["order_id"])
try:
    filters.loc[0]
except KeyError as e:
    print("loc[0]: KeyError", e)
```

```text
   order_id customer
1      1002      ben
3      1004     cara
6      1007      eli
9      1011      dev
iloc[1]: 1004
loc[3]:  1004
loc[0]: KeyError 0
```

Position 1 is the second row, whose label happens to be 3. Label 0 no longer exists because order 1001 was a kettle. This is why you should reset the index after a filter when you plan to work with positions, or just never rely on a default integer label meaning anything.

```python
print(filters.reset_index(drop=True)[["order_id", "customer"]])
```

```text
   order_id customer
0      1002      ben
1      1004     cara
2      1007      eli
3      1011      dev
```

`s[0]` on a Series is the most treacherous form of all. In pandas 3 a bare integer in square brackets on a Series always means a label, while older versions would fall back to position when the index held no integers. With a text index it now fails, which is an improvement. Use `iloc[0]` for the first value.

```python
revenue = orders.set_index("product")["revenue"]
print(revenue.iloc[0])
try:
    revenue[0]
except KeyError as e:
    print("KeyError:", e)
```

```text
48.0
KeyError: 0
```

## Boolean masks, in full

A real filter usually has several conditions. Combine them with `&` for and, `|` for or, `~` for not, and put each condition in parentheses because those operators bind more tightly than comparisons. Python's `and` and `or` cannot be used here, as they try to reduce a whole Series to a single truth value.

```python
mask = (orders["region"] == "south") & (orders["revenue"] > 30)
print(orders.loc[mask, ["order_id", "region", "revenue"]])

try:
    orders[(orders["region"] == "south") and (orders["revenue"] > 30)]
except ValueError as e:
    print("ValueError:", str(e)[:60])
```

```text
    order_id region  revenue
9       1011  south     39.0
10      1012  south     48.0
ValueError: The truth value of a Series is ambiguous. Use a.empty, a.ite
```

Three helpers make common masks shorter: `isin` for membership, `between` for ranges with both ends included by default, and the `.str` methods for text. `query` lets you write the condition as a string, which can read better when several conditions pile up.

```python
print(orders[orders["product"].isin(["kettle", "scale"])]["order_id"].tolist())
print(orders[orders["date"].between("2025-01-05", "2025-01-09")]["order_id"].tolist())
print(orders[orders["customer"].str.startswith("c")]["order_id"].tolist())
print(orders.query("region == 'north' and qty > 1")["order_id"].tolist())
print(orders.nlargest(2, "revenue")[["order_id", "revenue"]])
```

```text
[1001, 1005, 1006, 1010, 1012]
[1003, 1004, 1005, 1006]
[1004, 1009]
[1007]
   order_id  revenue
4      1005     96.0
2      1003     95.0
```

A mask is also a number. Since `True` counts as 1, the `sum` of a mask is how many rows match and the `mean` is the share that match. It is a small trick you will use constantly.

```python
print((orders["qty"] > 1).sum(), round((orders["qty"] > 1).mean(), 3))
```

```text
5 0.455
```

## Setting values

As chapter 1 explained, Copy-on-Write means an assignment must go through one accessor call in one step. Put the row selection and the column into the same `.loc`. To build a new column from a condition, use `np.where` for two outcomes and `np.select` or `pd.cut` for more than two.

```python
orders.loc[orders["region"] == "unknown", "region"] = "unassigned"
orders["size"] = np.where(orders["revenue"] >= 50, "large", "small")
print(orders[["order_id", "region", "revenue", "size"]].head(5))
orders.loc[orders["region"] == "unassigned", "region"] = "unknown"
```

```text
   order_id      region  revenue   size
0      1001       north     48.0  small
1      1002       south     19.5  small
2      1003       north     95.0  large
3      1004        east     13.0  small
4      1005  unassigned     96.0  large
```

## Choosing an index

So far the index has been a meaningless row number. When a column really does identify rows, make it the index with `set_index`, and lookups read as what they are. `reset_index` is the reverse: it moves the index back to being a column.

```python
by_id = orders.set_index("order_id")
print(by_id.loc[1007, "customer"])
print(by_id.loc[[1001, 1012], ["customer", "revenue"]])
print(by_id.reset_index().columns.tolist()[:3])
```

```text
eli
         customer  revenue
order_id
1001          ana     48.0
1012          ben     48.0
['order_id', 'date', 'customer']
```

An index need not be unique, and that catches people out. `by_customer.loc["ana"]` returns two rows because she placed two orders, while `by_customer.loc["eli"]` returns a single row as a Series, with a different type and shape. Pass a list to always get a DataFrame back.

```python
by_customer = orders.set_index("customer")
print(by_customer.index.is_unique)
print(type(by_customer.loc["ana"]).__name__, by_customer.loc["ana"].shape)
print(type(by_customer.loc["eli"]).__name__, by_customer.loc["eli"].shape)
print(type(by_customer.loc[["eli"]]).__name__, by_customer.loc[["eli"]].shape)
```

```text
False
DataFrame (2, 8)
Series (8,)
DataFrame (1, 8)
```

`reindex` is the other useful tool here. It conforms an object to a list of labels you specify, inserting `NaN` for new labels. A report needs every product listed, in a fixed order, including one with no sales this month.

```python
sold = orders.groupby("product")["qty"].sum()
print(sold.reindex(["kettle", "grinder", "filter", "scale", "descaler"], fill_value=0))
```

```text
product
kettle       4
grinder      2
filter      15
scale        2
descaler     0
Name: qty, dtype: int64
```

## Two-level labels: the MultiIndex

Group by two columns and pandas gives you an index with two levels. McKinney calls this hierarchical indexing, and describes it as a way to work with higher-dimensional data in a lower-dimensional form ([McKinney, *Python for Data Analysis*, ch. 8](https://wesmckinney.com/book/data-wrangling)). You need just enough of it to read such results.

```python
sales = orders.groupby(["region", "product"])["qty"].sum()
print(sales)
print(sales.index.nlevels)
```

```text
region   product
east     filter     2
         grinder    1
north    filter     4
         grinder    1
         kettle     1
south    filter     9
         kettle     1
         scale      1
unknown  kettle     2
         scale      1
Name: qty, dtype: int64
2
```

Select with a tuple for one exact combination, a single value for everything under an outer level, and `xs` to cut across on an inner level. Slicing a MultiIndex needs it to be sorted, as a `groupby` result already is, and `sort_index` fixes one that is not.

```python
print(sales.loc[("south", "filter")])
print(sales.loc["north"])
print(sales.xs("filter", level="product"))
print(sales.reset_index().head(3))
```

```text
9
product
filter     4
grinder    1
kettle     1
Name: qty, dtype: int64
region
east     2
north    4
south    9
Name: qty, dtype: int64
  region  product  qty
0   east   filter    2
1   east  grinder    1
2  north   filter    4
```

When in doubt, `reset_index()` flattens levels back to ordinary columns, and you are on familiar ground. Plenty of analysts work that way on purpose. Chapter 4 shows the other route out, `unstack`, which turns one level into columns.

## Pitfalls

- **Assuming labels are positions.** They match only until the first filter or sort. Use `iloc` for "the first row" and `loc` for "the row labelled this".
- **Forgetting that `.loc` slices include the end.** `df.loc[0:2]` has three rows and `df.iloc[0:2]` has two.
- **`and` and `or` in a mask.** Use `&` and `|` with parentheses around each condition.
- **Chained selection on assignment.** `df[mask]["a"] = 1` does nothing. Use `df.loc[mask, "a"] = 1`.
- **A non-unique index.** `loc` can return a Series or a DataFrame depending on the data. Check `index.is_unique`, or pass a list.
- **Reading old code with `.ix`.** It has been gone for years. Decide whether you meant a label or a position, then use `loc` or `iloc`.
- **Slicing an unsorted MultiIndex.** Call `sort_index()` first.

## Try it

1. Select the customer and revenue of every order placed in the north or east with revenue above 25.

<details><summary>Answer</summary>

```python
m = orders["region"].isin(["north", "east"]) & (orders["revenue"] > 25)
print(orders.loc[m, ["customer", "revenue"]])
```

```text
  customer  revenue
0      ana     48.0
2      ana     95.0
6      eli     26.0
7     cara     95.0
```

</details>

2. What share of orders contains a filter, and what share of revenue do those orders bring in?

<details><summary>Answer</summary>

```python
is_filter = orders["product"] == "filter"
print(round(is_filter.mean(), 3), round(orders.loc[is_filter, "revenue"].sum() / orders["revenue"].sum(), 3))
```

```text
0.364 0.186
```

Filters are over a third of orders and under a fifth of revenue, which is why a report should not stop at counting.

</details>

3. Sort `orders` by revenue, descending. Then get the first row by position and the row with label 0. Are they the same? Why?

<details><summary>Answer</summary>

```python
ranked = orders.sort_values("revenue", ascending=False)
print(ranked.iloc[0]["order_id"], ranked.loc[0]["order_id"])
```

```text
1005 1001
```

They differ. `iloc[0]` is the top-revenue order, while `loc[0]` finds whichever row kept label 0 from before the sort.

</details>

4. Work through `practice/3_Arrays.ipynb` for NumPy indexing, masks and `np.where`. `practice/courses/wrangle_pandas.py` holds a set of selection, sorting and joining recipes (it reads small CSVs from GitHub, so it needs a network connection); rewrite three of them without looking.

## Interview checklist

| Question | What a good answer covers |
|---|---|
| `loc` or `iloc`? | `loc` selects by label, `iloc` by integer position. |
| Does a slice include its end? | `.iloc` excludes it like Python, `.loc` includes it, as labels have no natural next value. |
| Why do `df.loc[0]` and `df.iloc[0]` disagree? | After a filter or sort, labels no longer equal positions. Use `reset_index(drop=True)` if you need them aligned. |
| How do you combine conditions? | `&`, `\|` and `~` with each condition in parentheses; `and` and `or` raise a `ValueError` on a Series. |
| How do you set a value on filtered rows? | One call: `df.loc[mask, "col"] = value`. Chained forms write to a temporary under Copy-on-Write. |
| What does `(s > 0).mean()` give? | The share of values above 0, as `True` counts as 1. |
| What is the difference between axis 0 and axis 1? | Axis 0 runs down the rows, axis 1 across the columns. `sum(axis=0)` collapses rows and gives one value per column. |
| What is a MultiIndex for? | Several levels of labels, usually out of a multi-key groupby. Select by tuple, by outer level, or with `xs`, or flatten with `reset_index`. |
| What does `reindex` do? | Conforms an object to a given list of labels, adding `NaN` or a fill value for new ones and dropping others. |

## Next

You can pick out any part of one table. The answers you need usually live across several tables, or in a table with the wrong shape. Next: [Reshaping and joins](04-reshaping-and-joins.md).
