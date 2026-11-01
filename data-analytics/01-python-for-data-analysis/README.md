# Python for data analysis

> The on-ramp to pandas. Seven chapters take you from never having seen a DataFrame to loading, cleaning, reshaping, summarising and plotting real data. Each chapter has a notebook to practise in.
>
> Jump to: [Why](#why-this-comes-first) · [Story](#the-story) · [Reading order](#reading-order) · [Rules of thumb](#rules-of-thumb) · [Deck](#deck) · [Practice](#practice) · [Sources](#sources)

---

## What this is

The working pandas, NumPy, matplotlib and seaborn you need to do analysis in Python. It assumes the Python of [`programming/python/`](../../programming/python/) modules 01 to 03 and no previous pandas. All code in the notes was run on Python 3.13, pandas 3.1.0, NumPy 2.5.4, matplotlib 3.11.2 and seaborn 0.13.2, with the output shown as it printed.

## Why this comes first

Every later pillar in [data analytics](../README.md) starts with "given a table". An analyst spends more of the job getting the table right than running any model on it, and the errors made here do not raise exceptions. A join that doubles rows, a filter that drops missing keys and an average of averages all give a clean-looking number that is wrong. So these chapters teach the checks along with the calls.

Pandas 3.0 changed enough that most tutorials and books, including McKinney's second edition, now mislead in places. The chapters use the current behaviour and say where old advice breaks.

## The story

A small online shop sells kettles, grinders, filters and scales. Its orders start as a list of dictionaries, which shows the problem a DataFrame solves (chapter 1). The real export is a messy CSV with stray capitals, duplicates and a `$` in the price column, and it becomes a clean frame of 11 orders (chapter 2). We learn to ask for exactly the rows we want (chapter 3), attach customers and products without letting a join quietly inflate revenue from 523.5 to 756.0 (chapter 4), and summarise by group, where averaging rates gives the wrong margin (chapter 5). Then the shop gets a full year of daily revenue, with an outage and a December jump, to learn the rules of time (chapter 6) and to see it all in charts (chapter 7).

## Reading order

| # | Chapter | What you can do afterwards | Practice | Go deeper |
|---|---|---|---|---|
| 1 | [Series and DataFrame](notes/01-series-and-dataframe.md) | Explain labels, alignment, dtypes and Copy-on-Write; make a first check of any frame | [1_Overview](practice/1_Overview.ipynb), a refresher on the Python involved | [umich_pandas_basics.py](practice/courses/umich_pandas_basics.py) |
| 2 | [Loading and cleaning](notes/02-loading-and-cleaning.md) | Read a messy CSV, fix text and types, decide what gaps mean, wrap it in one function | [2_Texts](practice/2_Texts.ipynb) | [mckinney/ch06](practice/mckinney/ch06.ipynb), [ch07](practice/mckinney/ch07.ipynb) |
| 3 | [Indexing and selection](notes/03-indexing-and-selection.md) | Use `loc`, `iloc` and masks without surprises, and set values safely | [3_Arrays](practice/3_Arrays.ipynb) | [wrangle_pandas.py](practice/courses/wrangle_pandas.py) |
| 4 | [Reshaping and joins](notes/04-reshaping-and-joins.md) | Merge with checks, stack tables, move between long and wide | [4_DataFrames](practice/4_DataFrames.ipynb) | [mckinney/ch08](practice/mckinney/ch08.ipynb) |
| 5 | [Groupby and aggregation](notes/05-groupby-and-aggregation.md) | Use `agg`, `transform`, `filter` and pivot tables, and compute ratios correctly | [6_Aggregation](practice/6_Aggregation.ipynb) | [mckinney/ch10](practice/mckinney/ch10.ipynb) |
| 6 | [Time series](notes/06-time-series.md) | Parse dates, resample, shift, handle time zones and use rolling windows without leakage | [7_Time_Series](practice/7_Time_Series.ipynb) | [mckinney/ch11](practice/mckinney/ch11.ipynb) |
| 7 | [Plotting](notes/07-plotting.md) | Choose a chart from the question, and draw it in matplotlib, pandas or seaborn | [5_Plotting](practice/5_Plotting.ipynb) | [mckinney/ch09](practice/mckinney/ch09.ipynb), [ch14](practice/mckinney/ch14.ipynb), [umich_visualization.py](practice/courses/umich_visualization.py) |

The notebook numbers come from their original course, so notebook 5 goes with chapter 7, and notebooks 6 and 7 with chapters 5 and 6.

## Rules of thumb

- **Run `shape`, `dtypes`, `head` and `isna().sum()` on every new frame.** They catch most problems before they spread.
- **Keep the raw file untouched.** Put every fix in one function that you can rerun.
- **To change part of a frame, use one `.loc` call.** Chained assignment now does nothing.
- **`loc` is labels, `iloc` is positions.** After a filter the two differ.
- **State `how` and `validate` on every merge,** then compare row counts and one total.
- **Print a count beside every mean.** And for a ratio, sum the top, sum the bottom, then divide.
- **Check that groups add up to the total.** Missing keys vanish from a groupby by default.
- **On time data, make gaps visible with `asfreq`,** and keep shifts and windows looking backward in anything you feed to a model.
- **Choose the chart from the question.** Bars start at zero, and there is only one y axis.

## Deck

[`slides/python-for-data-analysis.pptx`](slides/python-for-data-analysis.pptx) ([PDF](slides/python-for-data-analysis.pdf), source: [`slides/deck.yaml`](slides/deck.yaml)). To rebuild it: `make slides PILLAR=data-analytics/01-python-for-data-analysis STRICT=1 PREVIEW=1`.

## Practice

The notebooks read data that is too big to commit, so fetch it once. `fetch_data.sh` lives in `practice/` and works from any directory.

```bash
cd data-analytics/01-python-for-data-analysis/practice
bash fetch_data.sh    # about 240 MB from wesm/pydata-book into mckinney/ and data/, not committed
uv run --with jupyterlab --with pandas --with matplotlib --with seaborn --with scipy --with requests jupyter lab
```

Open the numbered notebooks from `practice/`. The `mckinney/chNN` notebooks read `examples/` and `datasets/` relative to `mckinney/`, so Jupyter's working directory must be `mckinney/` for those. Opening them from the file browser handles that.

### Numbered notebooks

All seven were patched minimally for current libraries and run cell by cell with no failures on pandas 3.1.0. The patches also fixed cells that ran out of order. Cell 18 of `2_Texts` downloads a text file from py4inf.com, so it needs a network connection. Stored cell outputs may still come from older runs, so rerun a notebook rather than trusting what it shows on opening.

| # | Notebook | Covers | Data |
|---|---|---|---|
| 1 | [Overview](practice/1_Overview.ipynb) | Expressions, conditions, iteration and data types, as a fast refresher | none |
| 2 | [Texts](practice/2_Texts.ipynb) | Text files, parsing | `mckinney/examples/segismundo.txt`, py4inf.com |
| 3 | [Arrays](practice/3_Arrays.ipynb) | NumPy arrays, indexing and slicing, sorting, broadcasting | none |
| 4 | [DataFrames](practice/4_DataFrames.ipynb) | Series and DataFrame, descriptives, indexing, subsetting, joins | none |
| 5 | [Plotting](practice/5_Plotting.ipynb) | matplotlib and seaborn basics | `macrodata`, `spx`, `tips` |
| 6 | [Aggregation](practice/6_Aggregation.ipynb) | `groupby`, grouping by dicts and index levels, quantile buckets, group-wise fill | `tips` |
| 7 | [Time series](practice/7_Time_Series.ipynb) | Datetimes, shifting, periods, resampling, rolling windows | `stock_px_2` |

### McKinney chapters

These are the book's own code from the second edition, kept unpatched as the record of the book, so some cells fail on current pandas. Chapters 2 to 5 (Python and NumPy basics) are not included. The failure counts below are from one cell-by-cell run on pandas 3.1.0, and a cell can fail because an earlier one did.

| Chapter | Topic | Code cells | Failed |
|---|---|---|---|
| [ch06](practice/mckinney/ch06.ipynb) | Loading and storing data: CSV, JSON, Excel, HDF5 | 70 | 4 |
| [ch07](practice/mckinney/ch07.ipynb) | Cleaning: missing data, duplicates, transforms, string operations | 88 | 10 |
| [ch08](practice/mckinney/ch08.ipynb) | Wrangling: hierarchical indexes, merge, concat, reshape | 70 | 12 |
| [ch09](practice/mckinney/ch09.ipynb) | Plotting and visualisation | 54 | 4 |
| [ch10](practice/mckinney/ch10.ipynb) | Aggregation and group operations | 74 | 11 |
| [ch11](practice/mckinney/ch11.ipynb) | Time series | 116 | 24 |
| [ch14](practice/mckinney/ch14.ipynb) | Worked examples: Bitly, MovieLens, baby names, USDA food, FEC donations | 114 | 12 |

When a cell fails, this table translates most of it.

| Old idiom | Current form |
|---|---|
| `df.append(other)` | `pd.concat([df, other])` |
| `df.ix[...]` | `df.loc[...]` or `df.iloc[...]` |
| `pd.unique(list)` | `pd.unique(np.array(list))`, or `list(dict.fromkeys(items))` |
| `df["a"][mask] = x` | `df.loc[mask, "a"] = x` |
| `groupby(key, axis=1)` | `df.T.groupby(key)`, then `.T` on the result |
| `grouped["a", "b"]` | `grouped[["a", "b"]]` |
| `grouped.mean()` on frames with text columns | `grouped.mean(numeric_only=True)` |
| `freq="M"`, `"Q"`, `"A"` or `"Y"` | `"ME"`, `"QE"`, `"YE"` |
| `freq="A-DEC"` on a period | `freq="Y-DEC"` |
| `freq="H"`, `"T"`, `"S"` | `"h"`, `"min"`, `"s"` |
| `resample(rule, how="mean")` | `resample(rule).mean()` |
| `df.fillna(method="ffill")` | `df.ffill()` |
| `df.applymap(f)` | `df.map(f)` |
| `sns.factorplot(...)` | `sns.catplot(..., kind=...)` |
| `sns.regplot("x", "y", data=df)` | `sns.regplot(x="x", y="y", data=df)` |
| `sns.distplot(a)` | `sns.histplot(a, kde=True)` (`distplot` still runs, with a deprecation warning) |
| `pd.rolling_mean(s, n)` | `s.rolling(n).mean()` |

### Course scripts

Scripts kept from earlier coursework, in [`courses/`](practice/courses). They are notes as code, so read them beside an open REPL rather than running them top to bottom.

| Script | From | Does it run? |
|---|---|---|
| [`wrangle_pandas.py`](practice/courses/wrangle_pandas.py) | Ben Gorman's *Data Wrangling* (pandas half) | WRANGLE_STATUS It reads its CSVs from GitHub. |
| [`umich_pandas_basics.py`](practice/courses/umich_pandas_basics.py) | Michigan, *Applied Data Science with Python* | No. It reads `cars.csv` and `census.csv` from an old Desktop path, and the course data isn't redistributable. |
| [`umich_visualization.py`](practice/courses/umich_visualization.py) | Michigan visualisation and Wesleyan *Data Analysis and Interpretation* | Partly. `iris.csv` is `sns.load_dataset("iris")`, and the NESARC survey file (`nesarc_pds.csv`) isn't included. |

## Sources

See [`references.md`](references.md) for books, papers and courses mapped to chapters. For the practice material:

| Source | License | Used for |
|---|---|---|
| Wes McKinney, [*Python for Data Analysis*](https://wesmckinney.com/book/), 2nd ed. ([code and data](https://github.com/wesm/pydata-book/tree/2nd-edition)) | Book: proprietary. Code and data: MIT | Chapter notebooks; data fetched by `fetch_data.sh` |
| University of Michigan, *Applied Data Science with Python* (Coursera) | Course materials: proprietary | Own notes in `courses/` |
| Wesleyan University, *Data Analysis and Interpretation* (Coursera) | Course materials: proprietary | Own notes in `courses/` (NESARC data not included) |
| Ben Gorman, [*DataWrangling*](https://github.com/ben519/DataWrangling) | Read online | `courses/wrangle_pandas.py` |

Next in this subject: [probability and statistics](../02-probability-and-statistics/README.md).
