# Practice: Python for data analysis

The labs for [working with data](../README.md). Its syllabus says which notebook goes with which step.

## Setup

The notebooks read data that is too big to commit, so fetch it once. `fetch_data.sh` lives in `practice/` and works from any directory.

```bash
cd data-analytics/01-python-for-data-analysis/practice
bash fetch_data.sh    # about 240 MB from wesm/pydata-book into mckinney/ and data/, not committed
uv run --with jupyterlab --with pandas --with matplotlib --with seaborn --with scipy --with requests jupyter lab
```

Open the numbered notebooks from this folder. The `mckinney/chNN` notebooks read `examples/` and `datasets/` relative to `mckinney/`, so Jupyter's working directory must be `mckinney/` for those. Opening them from the file browser handles that.

## Numbered notebooks

All seven were patched minimally for current libraries and run cell by cell with no failures on pandas 3.1.0. The patches also fixed cells that ran out of order. Cell 18 of `2_Texts` downloads a text file from py4inf.com, so it needs a network connection. Stored cell outputs may still come from older runs, so rerun a notebook rather than trusting what it shows on opening.

| # | Notebook | Covers | Data |
|---|---|---|---|
| 1 | [Overview](1_Overview.ipynb) | Expressions, conditions, iteration and data types, as a fast refresher | none |
| 2 | [Texts](2_Texts.ipynb) | Text files, parsing | `mckinney/examples/segismundo.txt`, py4inf.com |
| 3 | [Arrays](3_Arrays.ipynb) | NumPy arrays, indexing and slicing, sorting, broadcasting | none |
| 4 | [DataFrames](4_DataFrames.ipynb) | Series and DataFrame, descriptives, indexing, subsetting, joins | none |
| 5 | [Plotting](5_Plotting.ipynb) | matplotlib and seaborn basics | `macrodata`, `spx`, `tips` |
| 6 | [Aggregation](6_Aggregation.ipynb) | `groupby`, grouping by dicts and index levels, quantile buckets, group-wise fill | `tips` |
| 7 | [Time series](7_Time_Series.ipynb) | Datetimes, shifting, periods, resampling, rolling windows | `stock_px_2` |

## McKinney chapters

These are the book's own code from the second edition, kept unpatched as the record of the book, so some cells fail on current pandas. Chapters 2 to 5 (Python and NumPy basics) are not included. The failure counts below are from one cell-by-cell run on pandas 3.1.0, and a cell can fail because an earlier one did.

| Chapter | Topic | Code cells | Failed |
|---|---|---|---|
| [ch06](mckinney/ch06.ipynb) | Loading and storing data: CSV, JSON, Excel, HDF5 | 70 | 4 |
| [ch07](mckinney/ch07.ipynb) | Cleaning: missing data, duplicates, transforms, string operations | 88 | 10 |
| [ch08](mckinney/ch08.ipynb) | Wrangling: hierarchical indexes, merge, concat, reshape | 70 | 12 |
| [ch09](mckinney/ch09.ipynb) | Plotting and visualisation | 54 | 4 |
| [ch10](mckinney/ch10.ipynb) | Aggregation and group operations | 74 | 11 |
| [ch11](mckinney/ch11.ipynb) | Time series | 116 | 24 |
| [ch14](mckinney/ch14.ipynb) | Worked examples: Bitly, MovieLens, baby names, USDA food, FEC donations | 114 | 12 |

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

## Course scripts

Scripts kept from earlier coursework, in [`courses/`](courses/). They are notes as code, so read them beside an open REPL rather than running them top to bottom.

| Script | From | Does it run? |
|---|---|---|
| [`wrangle_pandas.py`](courses/wrangle_pandas.py) | Ben Gorman's *Data Wrangling* (pandas half) | Partly. It reads its CSVs from GitHub, then stops at `transactions[[1]]`, a lookup by position that raises `KeyError` on pandas 3.1. |
| [`umich_pandas_basics.py`](courses/umich_pandas_basics.py) | Michigan, *Applied Data Science with Python* | No. It reads `cars.csv` and `census.csv` from an old Desktop path, and the course data isn't redistributable. |
| [`umich_visualization.py`](courses/umich_visualization.py) | Michigan visualisation and Wesleyan *Data Analysis and Interpretation* | Partly. `iris.csv` is `sns.load_dataset("iris")`, and the NESARC survey file (`nesarc_pds.csv`) isn't included. |

## Licences

| Source | License | Used for |
|---|---|---|
| Wes McKinney, [*Python for Data Analysis*](https://wesmckinney.com/book/), 2nd ed. ([code and data](https://github.com/wesm/pydata-book/tree/2nd-edition)) | Book: proprietary. Code and data: MIT | Chapter notebooks; data fetched by `fetch_data.sh` |
| University of Michigan, *Applied Data Science with Python* (Coursera) | Course materials: proprietary | Own notes in `courses/` |
| Wesleyan University, *Data Analysis and Interpretation* (Coursera) | Course materials: proprietary | Own notes in `courses/` (NESARC data not included) |
| Ben Gorman, [*DataWrangling*](https://github.com/ben519/DataWrangling) | Read online | `courses/wrangle_pandas.py` |
