---
origin: synthesis
sources:
  - "McKinney, Python for Data Analysis, 2nd ed. (O'Reilly, 2017), ch. 5; 3rd ed. open access at https://wesmckinney.com/book/pandas-basics"
  - "VanderPlas, Python Data Science Handbook (O'Reilly, 2016), ch. 3; https://jakevdp.github.io/PythonDataScienceHandbook/03.00-introduction-to-pandas.html"
  - "McKinney, Data Structures for Statistical Computing in Python (SciPy 2010), https://doi.org/10.25080/Majora-92bf1922-00a"
  - https://pandas.pydata.org/docs/whatsnew/v3.0.0.html
  - https://pandas.pydata.org/docs/user_guide/migration.html
confidence: high
cleaned: 2026-11-01
---
# 1 — Series and DataFrame

Most of the data an analyst touches arrives as a table: a row per order, a column per fact about the order. Python's own lists and dictionaries can hold such a table, but every question you ask of it turns into a loop, and every loop is a place to get the bookkeeping wrong. pandas gives you two objects that hold the table directly, the Series for one column and the DataFrame for many, and lets you ask the question in one line. This chapter builds both from nothing, using the orders of a small online shop that sells coffee gear. The same shop runs through all seven chapters of this pillar. By the end you can build a frame, read what it tells you about itself, compute a new column, and explain why two Series with different labels add up the way they do.

Everything here was run on pandas 3.1.0 with Python 3.13. That matters more than usual, because pandas 3.0 changed behaviour that older books and most blog posts still describe. The chapter points those places out as they come up.

## The problem a DataFrame solves

Start without pandas. The shop's first six orders fit naturally into a list of dictionaries, one dictionary per order. This is the Python you practised in `practice/1_Overview.ipynb`.

```python
rows = [
    {"order_id": 1001, "customer": "ana",  "product": "kettle",  "qty": 1, "unit_price": 48.0},
    {"order_id": 1002, "customer": "ben",  "product": "filter",  "qty": 3, "unit_price": 6.5},
    {"order_id": 1003, "customer": "ana",  "product": "grinder", "qty": 1, "unit_price": 95.0},
    {"order_id": 1004, "customer": "cara", "product": "filter",  "qty": 2, "unit_price": 6.5},
    {"order_id": 1005, "customer": "dev",  "product": "kettle",  "qty": 2, "unit_price": 48.0},
    {"order_id": 1006, "customer": "ben",  "product": "scale",   "qty": 1, "unit_price": 22.0},
]

spend = {}
for r in rows:
    spend[r["customer"]] = spend.get(r["customer"], 0) + r["qty"] * r["unit_price"]
print(spend)
```

```text
{'ana': 143.0, 'ben': 41.5, 'cara': 13.0, 'dev': 96.0}
```

That works, and for six rows it is fine. Look at what the loop makes you manage, though. You name the accumulator, you handle the first time a customer appears, and you spell out the arithmetic per row. The intent, "total spend by customer", is buried in the book-keeping. Wickham makes this argument about loops in general: the objection is seldom speed, it is that loops do not express intent, since the important details are mixed in with the unimportant ones ([Wickham, JSS 2011](https://doi.org/10.18637/jss.v040.i01)).

Here is the same question asked of a DataFrame. Do not worry about the syntax yet; chapter 5 is devoted to it.

```python
import pandas as pd

orders = pd.DataFrame(rows)
orders["revenue"] = orders["qty"] * orders["unit_price"]
print(orders.groupby("customer")["revenue"].sum())
```

```text
customer
ana     143.0
ben      41.5
cara     13.0
dev      96.0
Name: revenue, dtype: float64
```

Three lines, and each one says what it means. The shape of this saving is the reason pandas exists. McKinney built it because statistical data tends to arrive as a two-dimensional list of observations with named fields, and the structures Python offered at the time did not make that convenient compared with R's `data.frame` ([McKinney, SciPy 2010](https://doi.org/10.25080/Majora-92bf1922-00a)). The rest of this chapter takes the DataFrame apart so that none of it is magic.

## A Series is a column with labels

The smaller object first. A Series holds a sequence of values of one type, plus a label for each value. You can think of it as a NumPy array that knows the name of every position, or as a dictionary whose values are stored efficiently and keep their order. Both pictures are useful.

```python
import pandas as pd

qty = pd.Series([1, 3, 1, 2], index=["ana", "ben", "cara", "dev"], name="qty")
print(qty)
print("values:", qty.to_numpy())
print("index: ", list(qty.index))
print("dtype: ", qty.dtype)
```

```text
ana     1
ben     3
cara    1
dev     2
Name: qty, dtype: int64
values: [1 3 1 2]
index:  ['ana', 'ben', 'cara', 'dev']
dtype:  int64
```

The printout shows the two parts side by side: labels on the left, values on the right, with the type of the values underneath. The labels are called the **index**. If you do not supply one, pandas numbers the rows from 0.

```text
   index     values
  +------+  +------+
  | ana  |  |   1  |
  | ben  |  |   3  |     dtype: int64
  | cara |  |   1  |     name:  qty
  | dev  |  |   2  |
  +------+  +------+
```

Two habits follow from having labels. You look values up by label, and you do arithmetic on the whole column at once without writing a loop. The second is called **vectorisation**, and it is both shorter and much faster, since the loop runs in compiled code inside NumPy.

```python
print(qty["ben"])                # look up by label
print(qty * 48.0)                # arithmetic applies to every value
print(qty[qty >= 2])             # a boolean test selects values
print(qty.sum(), qty.mean())     # summaries ignore the labels
```

```text
3
ana      48.0
ben     144.0
cara     48.0
dev      96.0
Name: qty, dtype: float64
ben    3
dev    2
Name: qty, dtype: int64
7 1.75
```

A Series can also be built from a dictionary, which is often the most readable way to write a small one. The keys become the labels. If you also pass an index, pandas lines the dictionary up against it, and a label with no matching key gets `NaN`, the marker pandas uses for a missing number.

```python
stock = pd.Series({"kettle": 12, "filter": 240, "grinder": 3})
print(stock)
print(pd.Series({"kettle": 12, "filter": 240}, index=["filter", "kettle", "scale"]))
```

```text
kettle      12
filter     240
grinder      3
dtype: int64
filter    240.0
kettle     12.0
scale       NaN
dtype: float64
```

Notice the second result's dtype. Twelve and 240 were integers, but the Series came back as `float64`. `NaN` is a floating-point value, so a column that needs to hold one gets promoted to float. McKinney names this as the known cost of his original design: `NaN` was chosen for speed and because it propagates naturally through arithmetic, at the price of not fitting in integer arrays ([McKinney, SciPy 2010](https://doi.org/10.25080/Majora-92bf1922-00a)). You will meet this whenever a column of whole numbers mysteriously prints with `.0` on the end. It usually means there is a missing value somewhere in it.

## Alignment: the idea that makes it pandas

If labels were only a lookup convenience, pandas would be a thin wrapper over NumPy. What sets it apart is that operations between two objects match values **by label, not by position**. McKinney calls this built-in data alignment and singles it out as the main enhancement over R's data frame at the time ([McKinney, SciPy 2010](https://doi.org/10.25080/Majora-92bf1922-00a)).

Say the shop has two weeks of units sold per product, but the products do not line up. The first week sold no scales; the second week sold no grinders. And the two Series are in different orders.

```python
week1 = pd.Series({"kettle": 4, "filter": 30, "grinder": 2})
week2 = pd.Series({"filter": 25, "scale": 6, "kettle": 5})
print(week1 + week2)
```

```text
filter     55.0
grinder     NaN
kettle      9.0
scale       NaN
dtype: float64
```

Each product was matched with itself, whatever its position. The result carries the union of the labels, so nothing is lost, and a label present on only one side comes out `NaN`, because pandas will not pretend it knows what `2 + nothing` is. Compare the same numbers as bare NumPy arrays, where position is all there is:

```python
import numpy as np

print(np.array([4, 30, 2]) + np.array([25, 6, 5]))
```

```text
[29 36  7]
```

That result is wrong, and silently so: it adds 4 kettles to 25 filters. Alignment removes that whole class of mistake. It does introduce a smaller trap, the `NaN`s, but those are visible. If you know that a missing label means zero sales, say so with `add` and a fill value:

```python
print(week1.add(week2, fill_value=0))
```

```text
filter     55.0
grinder     2.0
kettle      9.0
scale       6.0
dtype: float64
```

Whether a gap means zero or means unknown is a question about the data and not about the code, and pandas leaves that decision with you. Chapter 2 returns to it.

## A DataFrame is a dictionary of aligned columns

A DataFrame is a set of Series that share one index, one per column. Each column has a single dtype, but different columns can have different dtypes, which is exactly what a real table needs and what a NumPy array does not offer.

```text
              columns (an Index too)
              order_id  customer  product   qty  unit_price
             +--------+---------+---------+----+----------+
  index  0   |  1001  |  ana    | kettle  |  1 |   48.0   |
         1   |  1002  |  ben    | filter  |  3 |    6.5   |  <- one row
         2   |  1003  |  ana    | grinder |  1 |   95.0   |
             +--------+---------+---------+----+----------+
               int64     str       str     int64  float64
                 ^
                 each column is a Series with the same index
```

There are several ways to build one. A dictionary of equal-length lists mirrors the structure directly, and it is the form you will see throughout this pillar. A list of row dictionaries, as earlier, works too.

```python
orders = pd.DataFrame({
    "order_id":   [1001, 1002, 1003, 1004, 1005, 1006],
    "customer":   ["ana", "ben", "ana", "cara", "dev", "ben"],
    "product":    ["kettle", "filter", "grinder", "filter", "kettle", "scale"],
    "qty":        [1, 3, 1, 2, 2, 1],
    "unit_price": [48.0, 6.5, 95.0, 6.5, 48.0, 22.0],
})
print(orders)
```

```text
   order_id customer  product  qty  unit_price
0      1001      ana   kettle    1        48.0
1      1002      ben   filter    3         6.5
2      1003      ana  grinder    1        95.0
3      1004     cara   filter    2         6.5
4      1005      dev   kettle    2        48.0
5      1006      ben    scale    1        22.0
```

Taking one column out gives you a Series with the same index. A single row comes back as a Series too, indexed by the column names. Chapter 3 covers selection in depth; for now, the square-bracket form picks columns.

```python
print(orders["product"])
print(type(orders["product"]).__name__, type(orders).__name__)
```

```text
0     kettle
1     filter
2    grinder
3     filter
4     kettle
5      scale
Name: product, dtype: str
Series DataFrame
```

## First look: what to run on a new frame

When a frame lands in front of you, run the same handful of commands before you believe anything about it. They answer: how big is it, what types did pandas assign, how much is missing, and what do the values look like.

```python
print(orders.shape)        # (rows, columns)
print(orders.head(2))      # first rows; tail() for the last
print(orders.dtypes)       # the type of every column
orders.info()              # dtypes, non-null counts, memory
```

```text
(6, 5)
   order_id customer product  qty  unit_price
0      1001      ana  kettle    1        48.0
1      1002      ben  filter    3         6.5
order_id        int64
customer          str
product           str
qty             int64
unit_price    float64
dtype: object
<class 'pandas.DataFrame'>
RangeIndex: 6 entries, 0 to 5
Data columns (total 5 columns):
 #   Column      Non-Null Count  Dtype
---  ------      --------------  -----
 0   order_id    6 non-null      int64
 1   customer    6 non-null      str
 2   product     6 non-null      str
 3   qty         6 non-null      int64
 4   unit_price  6 non-null      float64
dtypes: float64(1), int64(2), str(2)
memory usage: 427.0 bytes
```

`describe` summarises the numeric columns and `value_counts` tallies a categorical one. These two commands catch a surprising share of data problems early: an impossible maximum, a category spelled two ways.

```python
print(orders[["qty", "unit_price"]].describe())
print(orders["product"].value_counts())
```

```text
            qty  unit_price
count  6.000000    6.000000
mean   1.666667   37.666667
std    0.816497   33.730797
min    1.000000    6.500000
25%    1.000000   10.375000
50%    1.500000   35.000000
75%    2.000000   48.000000
max    3.000000   95.000000
product
kettle     2
filter     2
grinder    1
scale      1
Name: count, dtype: int64
```

Read the first table with some care. `count` is the number of non-missing values, so a count below the row total is your first sign of gaps. `50%` is the median. For `unit_price` the mean (37.67) sits above the median (35.00), pulled up by the one 95.00 grinder. The next pillar explains why that gap matters; it is worth noticing already.

## Dtypes decide what an operation means

A column's dtype determines what `+` and `sum` do to it. The most common failure in real data is a numeric column that arrived as text, because a single stray value such as `"n/a"` forces pandas to read the whole column as strings. The arithmetic then either fails or does something quite different.

```python
as_text = pd.Series(["3", "12", "5"])
print(as_text.dtype)
print(as_text.sum())                 # strings concatenate
print(pd.to_numeric(as_text).sum())  # after conversion, numbers add
```

```text
str
3125
20
```

The string dtype in that output is new. Since pandas 3.0, text columns get a dedicated `str` dtype by default, where earlier versions used the catch-all `object` ([pandas 3.0 release notes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)). A `str` column can only hold strings or missing values, with `NaN` as the missing marker. Older tutorials that check `dtype == object` to find text columns no longer work on such frames.

The table below covers the dtypes you will use in this pillar.

| dtype | Holds | Missing marker | Typical source of trouble |
|---|---|---|---|
| `int64` | whole numbers | cannot hold a missing value | one gap promotes the column to `float64` |
| `float64` | real numbers | `NaN` | rounding error when summing money |
| `str` | text | `NaN` | numbers and dates read as text |
| `bool` | True and False | cannot hold a missing value | a gap makes it `object` |
| `datetime64` | moments in time | `NaT` | dates left as text; chapter 6 |
| `category` | a small set of repeated labels | `NaN` | a value outside the declared categories turns into `NaN` |

Convert deliberately with `astype` when you know the type, and with `pd.to_numeric` or `pd.to_datetime` when the data may be dirty.

```python
orders["product"] = orders["product"].astype("category")
print(orders["product"].dtype)
print(orders["product"].cat.categories.tolist())
orders["product"] = orders["product"].astype("str")
```

```text
category
['filter', 'grinder', 'kettle', 'scale']
```

## Making new columns

Assigning to a column name that does not exist creates it. Arithmetic between columns is aligned on the index and vectorised, so a new column is usually one line. A boolean condition inside the square brackets keeps the rows where it is true, and `sort_values` reorders rows.

```python
orders["revenue"] = orders["qty"] * orders["unit_price"]
orders["is_bulk"] = orders["qty"] >= 2
print(orders)
print(orders[orders["is_bulk"]].sort_values("revenue", ascending=False))
```

```text
   order_id customer  product  qty  unit_price  revenue  is_bulk
0      1001      ana   kettle    1        48.0     48.0    False
1      1002      ben   filter    3         6.5     19.5     True
2      1003      ana  grinder    1        95.0     95.0    False
3      1004     cara   filter    2         6.5     13.0     True
4      1005      dev   kettle    2        48.0     96.0     True
5      1006      ben    scale    1        22.0     22.0    False
   order_id customer product  qty  unit_price  revenue  is_bulk
4      1005      dev  kettle    2        48.0     96.0     True
1      1002      ben  filter    3         6.5     19.5     True
3      1004     cara  filter    2         6.5     13.0     True
```

Removing a column uses `drop`, which returns a new frame rather than changing the old one. Most pandas methods behave this way: they hand you a result and leave the original alone. That is why you will so often see the pattern `orders = orders.something(...)`, and it allows the method chaining you will see in later chapters.

```python
slim = orders.drop(columns=["is_bulk"])
print(list(slim.columns))
print(list(orders.columns))
```

```text
['order_id', 'customer', 'product', 'qty', 'unit_price', 'revenue']
['order_id', 'customer', 'product', 'qty', 'unit_price', 'revenue', 'is_bulk']
```

## Copy-on-Write: the rule that changed in pandas 3

This is the one section where older material will actively mislead you, so it deserves care. McKinney's second edition warns that a column you pull out of a frame is a view on the underlying data, so that changing it changes the frame, and that you should call `.copy()` to avoid this. For years, learners also met the `SettingWithCopyWarning`, which meant "pandas cannot tell whether this write reaches the original".

Pandas 3.0 replaced all of that with one rule, called Copy-on-Write: the result of any indexing operation or method **behaves as if it were a copy** ([pandas 3.0 release notes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)). Pandas still avoids copying data until it has to, which is where the name comes from, but you cannot see that from outside. Changing one object never changes another. The migration guide states the consequence plainly: one statement cannot update more than one object ([pandas migration guide](https://pandas.pydata.org/docs/user_guide/migration.html)).

```python
col = orders["qty"]
col.iloc[0] = 99
print(col.iloc[0], orders["qty"].iloc[0])
```

```text
99 1
```

The write changed `col` and left `orders` untouched. In pandas 2 and earlier this could have changed both. The flip side is **chained assignment**, the old idiom of selecting and then assigning in two steps on one line. Each step produces a separate object, so the assignment lands on a temporary that is immediately thrown away.

```python
fixed = orders.copy()
fixed["qty"][fixed["customer"] == "ana"] = 0     # chained: does nothing
print(fixed.loc[fixed["customer"] == "ana", "qty"].tolist())

fixed.loc[fixed["customer"] == "ana", "qty"] = 0  # one .loc call: works
print(fixed.loc[fixed["customer"] == "ana", "qty"].tolist())
```

```text
ChainedAssignmentError: A value is being set on a copy of a DataFrame or Series through chained assignment.
[1, 1]
[0, 0]
```

The first attempt changed nothing and pandas warned about it. The second made the selection and the assignment in a single `.loc` call, so it reached the frame. That is the one pattern to remember: **to change part of a frame, use a single `.loc`**. The defensive `.copy()` calls that older code sprinkled around to silence the warning are no longer needed, and the warning itself is gone ([pandas 3.0 release notes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)). A related edge: the array you get back from `to_numpy()` may be a read-only view of the frame's data, and writing to it raises an error ([pandas migration guide](https://pandas.pydata.org/docs/user_guide/migration.html)). Copy it first if you want to modify it.

## Pitfalls

- **Iterating a frame row by row.** `for` loops and `iterrows` work, but they are slow and hide intent. If you are writing one, look first for a vectorised column expression, or wait until chapter 5 and use `groupby`.
- **Reading `.0` as harmless.** A column of whole numbers printing as floats usually means a missing value is hiding in it. Check `isna().sum()`.
- **Trusting the dtype without looking.** A numeric column with one bad value reads as `str`, and `sum` then concatenates rather than adds. Always run `dtypes` on a new frame.
- **Comparing with `NaN` using `==`.** `NaN == NaN` is false by the floating-point standard. Use `isna()`.
- **Following pre-3.0 advice on views and copies.** `df["a"][mask] = x` no longer does anything to `df`. Use `df.loc[mask, "a"] = x`.
- **Forgetting that methods return new objects.** `orders.drop(columns=["qty"])` on its own line changes nothing that you kept. Assign the result.

## Try it

1. Build a Series of units in stock for `kettle`, `filter` and `scale`, and another of units on order for `filter`, `scale` and `grinder`. Add them so that a product missing from one side counts as zero.

<details><summary>Answer</summary>

```python
in_stock = pd.Series({"kettle": 12, "filter": 240, "scale": 7})
on_order = pd.Series({"filter": 100, "scale": 5, "grinder": 4})
print(in_stock.add(on_order, fill_value=0))
```

```text
filter     340.0
grinder      4.0
kettle      12.0
scale       12.0
dtype: float64
```

The label order is sorted because the labels are not the same on both sides, so pandas forms a sorted union.

</details>

2. Using `orders`, add a `revenue` column and find which orders are worth more than the mean order value.

<details><summary>Answer</summary>

```python
orders["revenue"] = orders["qty"] * orders["unit_price"]
print(orders[orders["revenue"] > orders["revenue"].mean()][["order_id", "revenue"]])
```

```text
   order_id  revenue
2      1003     95.0
4      1005     96.0
```

</details>

3. Without running it, say what this prints, then check: `s = pd.Series([1, 2], index=["a", "b"]); u = s[s > 1]; u.iloc[0] = 50; print(s["b"])`.

<details><summary>Answer</summary>

It prints 2. `u` behaves as a copy under Copy-on-Write, so writing to it does not reach `s`.

</details>

4. Open `practice/1_Overview.ipynb`. It drills lists, tuples, dictionaries and comprehensions, the Python this chapter relies on. Then read `practice/courses/umich_pandas_basics.py` and rewrite one of its Series examples with your own labels.

## Interview checklist

| Question | What a good answer covers |
|---|---|
| What is the difference between a Series and a DataFrame? | A Series is one labelled column of one dtype. A DataFrame is a set of Series sharing an index, one per column, so dtypes can differ across columns. |
| What is the index for? | Labels for lookup and, more importantly, for alignment: operations between objects match on label, not on position. |
| What happens when you add two Series with different labels? | The result has the union of the labels. A label on only one side gives `NaN`, unless you use `add(..., fill_value=0)`. |
| Why did my integer column become float? | `NaN` is a float, so a missing value promotes the column to `float64`. |
| How do you see what a new frame contains? | `shape`, `head`, `dtypes`, `info`, `describe`, and `value_counts` on categorical columns. |
| What is the default string dtype in pandas 3? | The `str` dtype replaced `object` for inferred text. It holds only strings and missing values, with `NaN` as the marker. |
| What is Copy-on-Write and what did it change? | Every indexing result and method result behaves as a copy, so one statement cannot update two objects. Chained assignment stops working, and `SettingWithCopyWarning` is gone. |
| How do you update part of a frame safely? | One `.loc` call with both the row selection and the column: `df.loc[mask, "col"] = value`. |
| Why prefer vectorised operations over loops? | They state intent, and the loop runs in compiled code, so they are much faster. |

## Next

The frames here were typed in by hand, and real ones never are. Real data comes from files, and files are messy. Next: [Loading and cleaning](02-loading-and-cleaning.md).
