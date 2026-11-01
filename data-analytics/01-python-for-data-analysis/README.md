# Python 04 — Python for data

> NumPy, pandas, plotting, group-bys and time series. Two layers: seven compact course notebooks
> (`1_` … `7_`) that teach each topic once, and McKinney's chapter notebooks that go deeper.
> Jump to: [Setup](#setup) · [Notebooks](#notebooks) · [McKinney chapters](#mckinney-chapters) · [Course scripts](#course-scripts) · [Sources](#sources)

---

## Setup

```bash
cd programming/python/04-python-for-data
bash fetch_data.sh                       # ~240 MB from wesm/pydata-book into mckinney/ and data/; not committed
uv run --with jupyterlab --with pandas --with matplotlib --with seaborn --with scipy jupyter lab
```

Open `1_` … `7_` from this folder. The `mckinney/chNN` notebooks read `examples/…` and
`datasets/…` relative to `mckinney/`, so Jupyter's working directory must be `mckinney/` for those
(opening them from the file browser handles that).

---

## Notebooks

| # | Notebook | Covers | Data | Go deeper |
|---|---|---|---|---|
| 1 | [Overview](practice/1_Overview.ipynb) | Expressions, conditions, iteration, data types: a fast refresher | — | [Python 01](../../programming/python/01-foundations) |
| 2 | [Texts](practice/2_Texts.ipynb) | Text files, the OS, parsing | `data/tmp.txt` | [Python 01 · 04](../../programming/python/01-foundations/notes/04-strings-and-files.md) |
| 3 | [Arrays](practice/3_Arrays.ipynb) | NumPy arrays, indexing and slicing, sorting, broadcasting | — | ch04 (not included) |
| 4 | [DataFrames](practice/4_DataFrames.ipynb) | Series vs DataFrame, descriptives, indexing, subsetting, joins | — | [ch07](practice/mckinney/ch07.ipynb), [ch08](practice/mckinney/ch08.ipynb) |
| 5 | [Plotting](practice/5_Plotting.ipynb) | matplotlib and seaborn basics | `macrodata`, `spx`, `tips` | [ch09](practice/mckinney/ch09.ipynb) |
| 6 | [Aggregation](practice/6_Aggregation.ipynb) | `groupby`, grouping by dicts and index levels, quantile buckets, group-wise fill | `tips` | [ch10](practice/mckinney/ch10.ipynb) |
| 7 | [Time series](practice/7_Time_Series.ipynb) | Datetimes, shifting, periods, resampling and interpolation | `stock_px_2` | [ch11](practice/mckinney/ch11.ipynb) |

## McKinney chapters

From *Python for Data Analysis*, 2nd edition, with the book's code. Chapters 2–5 (Python and
NumPy basics) are covered by Python 01–03 and notebook 3, so they're not included.

| Chapter | Topic |
|---|---|
| [ch06](practice/mckinney/ch06.ipynb) | Loading and storing data: CSV, JSON, Excel, HDF5 |
| [ch07](practice/mckinney/ch07.ipynb) | Cleaning and preparation: missing data, duplicates, transforms, string ops |
| [ch08](practice/mckinney/ch08.ipynb) | Wrangling: hierarchical indexes, merge, concat, reshape |
| [ch09](practice/mckinney/ch09.ipynb) | Plotting and visualisation |
| [ch10](practice/mckinney/ch10.ipynb) | Aggregation and group operations |
| [ch11](practice/mckinney/ch11.ipynb) | Time series |
| [ch14](practice/mckinney/ch14.ipynb) | Worked examples: Bitly, MovieLens, baby names, USDA food, FEC donations |

## Course scripts

Scripts kept from earlier coursework, in [`courses/`](practice/courses). They are notes-as-code, so read them
alongside an open REPL rather than running them top to bottom.

| Script | From | Runs as-is? |
|---|---|---|
| [`wrangle_pandas.py`](practice/courses/wrangle_pandas.py) | Ben Gorman's *Data Wrangling* (pandas half) | Yes. It reads its CSVs from GitHub |
| [`umich_pandas_basics.py`](practice/courses/umich_pandas_basics.py) | Michigan, *Applied Data Science with Python* | No. It reads `cars.csv` and `census.csv` from an old Desktop path; the course data isn't redistributable |
| [`umich_visualization.py`](practice/courses/umich_visualization.py) | Michigan visualisation + Wesleyan *Data Analysis and Interpretation* | Partly. `iris.csv` is `sns.load_dataset("iris")`; the NESARC survey file (`nesarc_pds.csv`) isn't included |

---

## Sources

| Source | License | Used for |
|---|---|---|
| Wes McKinney, [*Python for Data Analysis*](https://wesmckinney.com/book/), 2nd ed. ([code and data](https://github.com/wesm/pydata-book/tree/2nd-edition)) | Book: proprietary. Code and data: MIT | Chapter notebooks; data fetched by `fetch_data.sh` |
| University of Michigan, *Applied Data Science with Python* (Coursera) | Course materials: proprietary | Own notes in `courses/` |
| Wesleyan University, *Data Analysis and Interpretation* (Coursera) | Course materials: proprietary | Own notes in `courses/` (NESARC data not included) |
| Ben Gorman, [*DataWrangling*](https://github.com/ben519/DataWrangling) | Read online | `courses/wrangle_pandas.py` |

The [data-analytics](../README.md) pillar picks up from here: statistics, experiments and analysis practice.
