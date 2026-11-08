---
origin: curated
sources:
  - data-analytics/sources/Python for Data Analysis 2nd edition.pdf
  - data-analytics/sources/Python_Datascience.pdf
confidence: high
cleaned: 2026-11-01
---
# Python for data analysis: references

Every source behind the notes in this pillar. Books shared with other pillars are listed with all their mappings in the [subject library](../references.md).

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| Wes McKinney, *Python for Data Analysis*, 2nd ed. (O'Reilly, 2017). The base text. Its pandas advice predates pandas 3, so the notes correct it where needed. The [3rd edition](https://wesmckinney.com/book/) is open access online and updated for pandas 2.0. | 5 | [PDF](../sources/Python%20for%20Data%20Analysis%202nd%20edition.pdf) | [01](notes/01-series-and-dataframe.md) |
| McKinney, same book: per-chapter PDFs. Notes cite them as `(*Python for Data Analysis*, ch. N)`. Folded in as: ch. 1 → [01](notes/01-series-and-dataframe.md) (labeled-axes motivation, name origins); ch. 2 and 3 → no pillar note: Python basics, IPython and built-in data structures are taught in [`programming/python/`](../../programming/python/), and the chapters add nothing new there for this lane (sharpens only; 2017 text with `str.format` and Python 3.6); ch. 4 → [03](notes/03-indexing-and-selection.md) (views vs copies, fancy indexing, vectorisation timing); ch. 5 → [01](notes/01-series-and-dataframe.md), [03](notes/03-indexing-and-selection.md) (alignment with `fill_value`, inclusive label slices); ch. 6 → [02](notes/02-loading-and-cleaning.md) (chunked `value_counts` with `fill_value=0`, HDF5 write-once caveat, 50+ `read_csv` options; Parquet is not covered by the 2017 text); ch. 7 → [02](notes/02-loading-and-cleaning.md) (`qcut` equal bins, `dropna(thresh=)`); ch. 8 → [04](notes/04-reshaping-and-joins.md) (many-to-many product, `join` vs `merge`, `pivot` = `set_index` + `unstack`, `stack` drops NaN, sorted MultiIndex); ch. 9 → [07](notes/07-plotting.md) (`pairplot`, barplot 95% CI, `bbox_inches`; the chapter's matplotlib walk-through adds nothing the note lacks); ch. 10 → [05](notes/05-groupby-and-aggregation.md) (`qcut` vs `cut` buckets, crosstab margins, custom-function slowness); ch. 11 → [06](notes/06-time-series.md) (right-closed 5-min bins 0/15/40/11, `Q-JAN` fiscal periods, UTC storage under `tz_convert`, rolling `min_periods` and `20D`, `rolling().corr`); ch. 12 → [01](notes/01-series-and-dataframe.md), [05](notes/05-groupby-and-aggregation.md) (categorical memory 80,000,080 vs 10,000,272 bytes, `transform` vs `apply`, `Grouper` per key; method chaining and `pipe` taught only as style, not added); ch. 13 → [01](notes/01-series-and-dataframe.md) (`.values` on mixed frames, names back onto coefficients, Patsy design matrices, train-only imputation; the statsmodels OLS/AR and scikit-learn Titanic parts are dropped here as off-lane, see data-analytics/02 and data-science/01); ch. 14 → [05](notes/05-groupby-and-aggregation.md) (min-count filter, `transform('sum')` shares, `searchsorted` diversity; the other examples repeat techniques already in notes 04, 05 and 07: sharpens only). Dated: `ix`, `applymap`, `fillna(method=)`, `sum(level=)`, `sns.factorplot`/`distplot`, object-dtype strings and view-based column access, `pd.TimeGrouper`, `resample(loffset=)`, old aliases `M`/`Q`/`A-DEC`/`H`/`T`, `PeriodIndex(year=, quarter=)`, `pd.value_counts`, `.values`, `sm.tsa.AR`, `rename(copy=False)`, `read_table(sep='::')` without `engine='python'`, chained assignment on slices | 1 to 14 | [PDFs](../sources/python-for-data-analysis/) | [01](notes/01-series-and-dataframe.md), [02](notes/02-loading-and-cleaning.md), [03](notes/03-indexing-and-selection.md), [04](notes/04-reshaping-and-joins.md), [05](notes/05-groupby-and-aggregation.md), [07](notes/07-plotting.md) |
| | 6, 7 | | [02](notes/02-loading-and-cleaning.md) |
| | 4, 5, 8.1 | | [03](notes/03-indexing-and-selection.md) |
| | 8 | | [04](notes/04-reshaping-and-joins.md) |
| | 10 | | [05](notes/05-groupby-and-aggregation.md) |
| | 11 | | [06](notes/06-time-series.md) |
| | 9 | | [07](notes/07-plotting.md) |
| | 14 | | Capstone exercise in [07](notes/07-plotting.md) |
| Wes McKinney, *Python for Data Analysis*, 1st ed. (O'Reilly, 2012). Superseded; kept for reference. | all | [PDF](../sources/Python%20for%20Data%20Analysis.pdf) | none directly |
| Jake VanderPlas, *Python Data Science Handbook* (O'Reilly, 2016; 1st ed., inferred from the IPython 4.0.1, NumPy 1.11 and pandas 0.18.1 output, as the chapter PDFs print no year). A second explanation of each topic, [free online](https://jakevdp.github.io/PythonDataScienceHandbook/). Chapter PDFs in [sources/python-data-science-handbook/](../sources/python-data-science-handbook/). Notes cite it as `(*Python Data Science Handbook*, ch. N)`. Folded in as: ch. 1 → [01](notes/01-series-and-dataframe.md) (`%timeit` vs `%time` on `sort`, profiling order; the same tools inside IPython are in [`programming/software-design/notes/06-debugging-and-profiling.md`](../../programming/software-design/notes/06-debugging-and-profiling.md), "The same tools inside IPython"); ch. 2 → [03](notes/03-indexing-and-selection.md) (broadcasting is in [`programming/computer-science/notes/04-numbers-and-memory.md`](../../programming/computer-science/notes/04-numbers-and-memory.md); `np.add.at` for repeated indices, loop vs vectorised and `sum` vs `np.sum` timings, hand-rolled histogram crossover); ch. 3 → [01](notes/01-series-and-dataframe.md) (object-dtype and loop timings, `eval` caveat), [02](notes/02-loading-and-cleaning.md) (IQR 5-sigma clipping), [04](notes/04-reshaping-and-joins.md) (isnull audit after a merge, state densities), [05](notes/05-groupby-and-aggregation.md) (Titanic survival by sex and class), [06](notes/06-time-series.md) (nanosecond range 1678 to 2262); ch. 4 → [07](notes/07-plotting.md) (luminance of `jet` vs `viridis`, `clim` with `extend`, `plot` vs `scatter`, check group size before a violin); ch. 5 → no note here: machine learning belongs to `data-science/01-classical-ml` (Estimator API, validation and grid search, PCA, k-means, GMM, KDE; nothing in this lane's notes needs it). Dated: `%timeit` "best of 3" output, `ix`, `Panel`, `DataFrame.append`, `concat(join_axes=)`, `mean(level=)`, `tshift`, `pd.datetime`, `pd.rolling_mean`, `resample(how=)`, `fillna(method=)`, old aliases `H`/`T`/`S`/`L`/`BA`, `np.float_` and `np.complex_` (removed in NumPy 2), `np.random.seed` (use `default_rng`), `hist(normed=)`, `axisbg=`, `sns.distplot`/`factorplot`/`pairplot(size=)`, `jet` as default colormap, Basemap, seaborn style names without `v0_8`. | 1 to 5 | [PDFs](../sources/python-data-science-handbook/) | [01](notes/01-series-and-dataframe.md), [02](notes/02-loading-and-cleaning.md), [03](notes/03-indexing-and-selection.md), [04](notes/04-reshaping-and-joins.md), [05](notes/05-groupby-and-aggregation.md), [06](notes/06-time-series.md), [07](notes/07-plotting.md) |
| Same book, original whole-book PDF. | 3: introducing pandas objects, operating on data | [PDF](../sources/Python_Datascience.pdf) | [01](notes/01-series-and-dataframe.md) |
| | 3: handling missing data | | [02](notes/02-loading-and-cleaning.md) |
| | 2 and 3: NumPy indexing, data selection, hierarchical indexing | | [03](notes/03-indexing-and-selection.md) |
| | 3: combining datasets, merge and join, pivot tables | | [04](notes/04-reshaping-and-joins.md) |
| | 3: aggregation and grouping | | [05](notes/05-groupby-and-aggregation.md) |
| | 3: working with time series | | [06](notes/06-time-series.md) |
| | 4: visualization with matplotlib and seaborn | | [07](notes/07-plotting.md) |

## Core papers

| Paper | What it adds | Maps to |
|---|---|---|
| McKinney, [Data Structures for Statistical Computing in Python](https://doi.org/10.25080/Majora-92bf1922-00a), SciPy 2010 | Why pandas exists: labelled arrays and built-in alignment | [01](notes/01-series-and-dataframe.md) |
| Harris et al., [Array programming with NumPy](https://doi.org/10.1038/s41586-020-2649-2), Nature 2020 | The array as a pointer with data type, shape and strides | [03](notes/03-indexing-and-selection.md) |
| Wickham, [Tidy Data](https://doi.org/10.18637/jss.v059.i10), JSS 2014 | One variable per column, one observation per row | [04](notes/04-reshaping-and-joins.md), [07](notes/07-plotting.md) |
| Wickham, [The Split-Apply-Combine Strategy for Data Analysis](https://doi.org/10.18637/jss.v040.i01), JSS 2011 | The model behind `groupby`, and what falls outside it | [05](notes/05-groupby-and-aggregation.md), [06](notes/06-time-series.md) |
| Hunter, [Matplotlib: A 2D Graphics Environment](https://doi.org/10.1109/MCSE.2007.55), CiSE 2007 | What matplotlib set out to do | [07](notes/07-plotting.md) |
| Waskom, [seaborn: statistical data visualization](https://doi.org/10.21105/joss.03021), JOSS 2021 | Plots specified from a table's columns | [07](notes/07-plotting.md) |
| Cleveland & McGill, [Graphical Perception](https://doi.org/10.1080/01621459.1984.10478080), JASA 1984 | People judge length more accurately than angle | [07](notes/07-plotting.md) |

## Courses and videos

| Course or video | Platform | Cost | Which parts | Maps to |
|---|---|---|---|---|
| [Kaggle Learn: Pandas](https://www.kaggle.com/learn/pandas) | Kaggle | Free | The whole short course | [01](notes/01-series-and-dataframe.md), [03](notes/03-indexing-and-selection.md), [05](notes/05-groupby-and-aggregation.md) |
| [Kaggle Learn: Data Cleaning](https://www.kaggle.com/learn/data-cleaning) | Kaggle | Free | The whole short course | [02](notes/02-loading-and-cleaning.md) |
| [Kaggle Learn: Time Series](https://www.kaggle.com/learn/time-series) | Kaggle | Free | The whole short course; continues into forecasting | [06](notes/06-time-series.md) |
| [Kaggle Learn: Data Visualization](https://www.kaggle.com/learn/data-visualization) | Kaggle | Free | The whole short course (seaborn) | [07](notes/07-plotting.md) |
| [Applied Data Science with Python](https://www.coursera.org/specializations/data-science-python), University of Michigan | Coursera | Paid; own notes in `practice/courses/` | Pandas and plotting courses | [01](notes/01-series-and-dataframe.md), [07](notes/07-plotting.md) |
| [Data Analysis and Interpretation](https://www.coursera.org/specializations/data-analysis), Wesleyan University | Coursera | Paid; own notes in `practice/courses/` | Visualisation material | [07](notes/07-plotting.md) |
| Ben Gorman, [DataWrangling](https://github.com/ben519/DataWrangling) | GitHub | Free | The pandas half; own notes in `practice/courses/wrangle_pandas.py` | [03](notes/03-indexing-and-selection.md), [04](notes/04-reshaping-and-joins.md) |

## Documentation

| Page | Maps to |
|---|---|
| [pandas 3.0 release notes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html), [3.1 release notes](https://pandas.pydata.org/docs/whatsnew/v3.1.0.html) and the [migration guide](https://pandas.pydata.org/docs/user_guide/migration.html) | All notes; the source for every "changed in pandas 3" claim |
| pandas user guide: [indexing](https://pandas.pydata.org/docs/user_guide/indexing.html), [missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html), [IO](https://pandas.pydata.org/docs/user_guide/io.html), [merging](https://pandas.pydata.org/docs/user_guide/merging.html), [reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html), [groupby](https://pandas.pydata.org/docs/user_guide/groupby.html), [time series](https://pandas.pydata.org/docs/user_guide/timeseries.html), [windowing](https://pandas.pydata.org/docs/user_guide/window.html) | [02](notes/02-loading-and-cleaning.md) to [06](notes/06-time-series.md) |
| [matplotlib application interfaces](https://matplotlib.org/stable/users/explain/figure/api_interfaces.html), [seaborn function overview](https://seaborn.pydata.org/tutorial/function_overview.html), [seaborn 0.12 release notes](https://seaborn.pydata.org/whatsnew/v0.12.0.html) | [07](notes/07-plotting.md) |
