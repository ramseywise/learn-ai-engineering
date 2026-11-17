# Processing data

Turn a raw export into a table you can trust. Three steps, each with the check that catches its usual mistake: extract the rows you need, clean them until every column is the type it claims to be, and summarise them.

**What you should already know.** Nothing below is taught again here. Tick each line off, and go back to the chapter it links for any you cannot.

Python, from the [Python track](../../programming/python/README.md):

- [ ] Tell an `int`, a `float`, a `str`, a `bool` and `None` apart, and convert between them ([values and types](../../programming/python/01-foundations/notes/01-values-and-conditionals.md))
- [ ] Write a function that takes arguments and returns a value ([functions](../../programming/python/01-foundations/notes/02-functions.md))
- [ ] Loop over a sequence and keep a running result ([loops](../../programming/python/01-foundations/notes/03-loops.md))
- [ ] Open a text file, and split, strip and compare strings ([strings and files](../../programming/python/01-foundations/notes/04-strings-and-files.md))
- [ ] Hold records in lists, dictionaries and tuples ([collections](../../programming/python/01-foundations/notes/05-collections.md))

Relational tables, from the [SQL track](../../programming/sql/README.md). These help but are not required, because each idea returns here on a table in memory:

- [ ] Pick columns and filter rows with `SELECT … WHERE` ([selecting and filtering](../../programming/sql/notes/01-select-and-filter.md))
- [ ] Say why a missing value is not a zero ([missing data](../../programming/sql/notes/02-nulls-and-expressions.md))
- [ ] Get one row per group with `GROUP BY` ([aggregation](../../programming/sql/notes/03-aggregation.md))
- [ ] Match two tables on a key, and say what a left join keeps ([joins](../../programming/sql/notes/04-joins.md))

## Lecture

Start with the overview lecture, [Processing data](slides/lectures/00-overview.yaml): the one question the module keeps asking, the three steps and which tool to reach for. Then there is one lecture per step, on the same shop data as the notes: [Extract](slides/lectures/01-extract.yaml) (chapters 1 to 4), [Clean](slides/lectures/02-clean.yaml) (chapters 5 and 6) and [Summarise](slides/lectures/03-summarise.yaml) (chapters 7 and 8). A shorter single deck over all eight chapters is [Python for Data Analysis](slides/python-for-data-analysis.pptx) ([PDF](slides/python-for-data-analysis.pdf)).

## The core

This module is about the data, not about Python. Every later module in [data analytics](../README.md) starts with "given a table", and an analyst spends more of the job getting that table right than running any model on it. The mistakes made here do not raise exceptions. A join that doubles rows, a price column that is still text and an average of averages all give a clean-looking number that is wrong. So the one question this module keeps asking is: **is this number the one you meant?**

There are three steps between an export and a number, and each has a mistake to learn to catch. Analysis and charts come after them, in the modules that follow.

The steps are the same in any tool. The notes use pandas, and the choice between tools is mostly about where the data lives and how big it is:

| Tool | Reach for it when | Where the course says so |
|---|---|---|
| SQL | The data lives in a database. Filter and aggregate there, so the database reads less and sends back less. | [SQL 09](../../programming/sql/notes/09-sql-from-python.md) |
| pandas | The result fits in memory and you need to clean, reshape and look at it. | This module |
| Polars | The files are large but still fit on one machine. A lazy scan pushes the filter and the column choice into the read. | [DE 01/08](../../data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute.md) |

## Syllabus

One row per step. **Core concepts** are the ideas that make the step go right in any tool, **Study** is what to read, **Labs** is the notebook to work through afterwards, and **Sources** is where to read more. How to run the labs: [practice/README.md](practice/README.md).

| Submodule | Core concepts | Study | Labs | Sources |
|---|---|---|---|---|
| **1. Extract:** the rows and columns you need | Know what one row means before you touch it. Labels and positions are different things, and they come apart after a filter. A filter is a mask of true and false. A join can multiply rows, so state what it should do and count before and after. | [1 Series and DataFrame](notes/01-series-and-dataframe.md) · [2 Loading data](notes/02-loading-data.md) · [3 Indexing and selection](notes/03-indexing-and-selection.md) · [4 Reshaping and joins](notes/04-reshaping-and-joins.md) | [1_Overview](practice/1_Overview.ipynb), a refresher on the Python involved · [3_Arrays](practice/3_Arrays.ipynb) · [4_DataFrames](practice/4_DataFrames.ipynb) · book code: [ch06](practice/mckinney/ch06.ipynb), [ch08](practice/mckinney/ch08.ipynb) · [wrangle_pandas.py](practice/courses/wrangle_pandas.py) | McKinney ch. 4 to 6 and 8 · VanderPlas ch. 2 and 3 (pandas objects, indexing, merge and join) · Wickham, [Tidy Data](https://doi.org/10.18637/jss.v059.i10) |
| **2. Clean:** every column the type it claims | The type of a column decides what an operation on it means. A gap is a decision, and missing is not zero. A date is a type, not text, and it carries a time zone and a period. Keep the raw file untouched and put every fix in one function you can rerun. | [5 Cleaning](notes/05-cleaning.md) · [6 Dates and times](notes/06-dates-and-times.md) | [2_Texts](practice/2_Texts.ipynb) · [7_Time_Series](practice/7_Time_Series.ipynb), Datetime Basics and Periods · book code: [ch07](practice/mckinney/ch07.ipynb), [ch11](practice/mckinney/ch11.ipynb) | McKinney ch. 7 and 11 · VanderPlas ch. 3 (missing data, time series) · [Kaggle Learn: Data Cleaning](https://www.kaggle.com/learn/data-cleaning) |
| **3. Summarise:** one number per group | Split, apply, combine. Print a count beside every mean. For a rate, sum the top, sum the bottom, then divide. The groups must add back up to the total. Time is one more group key, and a window that feeds a model must look backward. | [7 Groupby and aggregation](notes/07-groupby-and-aggregation.md) · [8 Time series](notes/08-time-series.md) | [6_Aggregation](practice/6_Aggregation.ipynb) · [7_Time_Series](practice/7_Time_Series.ipynb), from Shifting onward · book code: [ch10](practice/mckinney/ch10.ipynb) | McKinney ch. 10 and 11 · VanderPlas ch. 3 (aggregation and grouping) · Wickham, [The Split-Apply-Combine Strategy](https://doi.org/10.18637/jss.v040.i01) |

The chapters are numbered in reading order, and each belongs to one step. Every source and the notes it maps to: [references.md](references.md).

Charts come later, in [visualisation and storytelling](../05-visualisation-and-storytelling/README.md). Its chapter [Plotting your own data](../05-visualisation-and-storytelling/notes/01b-plotting-your-own-data.md) gives you the calls to look at your own table. The plotting labs stay in this module's practice folder, beside the data they use: [5_Plotting](practice/5_Plotting.ipynb), the book code [ch09](practice/mckinney/ch09.ipynb) and [ch14](practice/mckinney/ch14.ipynb), and [umich_visualization.py](practice/courses/umich_visualization.py).

## Rules of thumb

- **Run `shape`, `dtypes`, `head` and `isna().sum()` on every new frame.** They catch most problems before they spread.
- **Keep the raw file untouched.** Put every fix in one function that you can rerun.
- **To change part of a frame, use one `.loc` call.** Chained assignment now does nothing.
- **`loc` is labels, `iloc` is positions.** After a filter the two differ.
- **State `how` and `validate` on every merge,** then compare row counts and one total.
- **Print a count beside every mean.** And for a ratio, sum the top, sum the bottom, then divide.
- **Check that groups add up to the total.** Missing keys vanish from a groupby by default.
- **On time data, make gaps visible with `asfreq`,** and keep shifts and windows looking backward in anything you feed to a model.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [Python track](../../programming/python/README.md) | Assumes modules 01 to 03; the checklist at the top names the chapters |
| [SQL track](../../programming/sql/README.md) | Helpful, not required: selecting, grouping and joining return here on a table in memory |

**Feeds into**

| Chapter | Why |
|---|---|
| [GA 07/05 Data-analysis agent](../../generative-ai/07-agentic-applications/notes/05-data-analysis-agent.md) | Its cleaning and group-by checks are this pillar's |
| [DE 05/01 Quality dimensions and tests](../../data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests.md) | Automates the checks an analyst runs by hand here |
| [DS 05/01 Time-series ML](../../data-science/05-time-series-and-recommenders/notes/01-time-series-ml.md) | Takes resampling and shifting as given |

## Primary texts

- McKinney, *Python for Data Analysis*: the base text
- VanderPlas, *Python Data Science Handbook*

All code in the notes was run on Python 3.13, pandas 3.1.0, NumPy 2.5.4, with the output shown as it printed. Pandas 3.0 changed enough that most tutorials and books, including McKinney's second edition, now mislead in places. The notes use the current behaviour and say where old advice breaks.

Everything else: [references.md](references.md). The lectures are built from [`slides/lectures/`](slides/lectures/) with `make slides PILLAR=data-analytics/01-python-for-data-analysis LECTURE=01-extract STRICT=1 PREVIEW=1`, and the single deck from [`slides/deck.yaml`](slides/deck.yaml) with the same command without `LECTURE=`.

## Next

Start with submodule 1, **Extract**: read [1 Series and DataFrame](notes/01-series-and-dataframe.md), then work through its labs in the syllabus row.

After submodule 3 you can get data into a table and say how you know a number is the one you meant. What you cannot yet say is whether a difference in that table is real or luck. That is the next module, [probability and statistics](../02-probability-and-statistics/README.md).
