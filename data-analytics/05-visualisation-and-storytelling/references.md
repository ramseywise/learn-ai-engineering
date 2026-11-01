---
origin: curated
sources:
  - "Books, papers and documentation listed below"
confidence: high
cleaned: 2026-11-01
---

# Visualisation and storytelling: references

Reading for this pillar. ★ marks a reading that changed a claim in the notes. Each row says how far it was read, because not every book was to hand.

## Books

None of the seven core books on this list is specifically a Python book, so the Python section adds the two standard references that do teach these libraries. Wilke and Healy show R code or figures, but the ideas transfer directly.

### Python

| Book | Why read it | Notes | How it was used |
|---|---|---|---|
| VanderPlas, *Python Data Science Handbook* (O'Reilly, 2017, ISBN 9781491912058). [Free online](https://jakevdp.github.io/PythonDataScienceHandbook/), [local copy](../sources/Python_Datascience.pdf) | The matplotlib chapter explains figure and axes clearly, then seaborn | 02 | Local copy held; used as background, not read in full |
| McKinney, *Python for Data Analysis*. [Free online](https://wesmckinney.com/book/), [local copy](../sources/Python%20for%20Data%20Analysis.pdf) | Its plotting chapter shows how pandas, matplotlib and seaborn fit together | 02 | Local copy held; used as background, not read in full |

### JavaScript

| Book | Why read it | Notes | How it was used |
|---|---|---|---|
| Murray, *Interactive Data Visualization for the Web*, 2nd ed. ([O'Reilly, 2017](https://alignedleft.com/work/d3-book-2e)) | The gentlest route into D3, written for people new to web work: from a blank page to the data join | 04 | Publisher and author pages checked; not read in full |
| Meeks & Dufour, [*D3.js in Action*, 3rd ed.](https://www.manning.com/books/d3js-in-action-third-edition) (Manning, 2024, ISBN 9781633439177) | Goes deeper than Murray and covers D3 v7, layouts, performance and using D3 inside frameworks | 04 | Publisher page checked; not read in full |

### Language-neutral

| Book | Why read it | Notes | How it was used |
|---|---|---|---|
| ★ Knaflic, [*Storytelling with Data*](https://www.storytellingwithdata.com/books) (Wiley, 2015, ISBN 9781119002253). [Local copy](../sources/Knaflic-storytelling-data.pdf) | The practical reference for explanatory charts: context, declutter, focus, story. Framing for who, what and how, the Big Idea, horizontal logic | 01, 02, 03, 05 | Read in full from the local copy |
| Wilke, [*Fundamentals of Data Visualization*](https://clauswilke.com/dataviz/) (O'Reilly, 2019, ISBN 9781492031086), free online | Chart choice organised by the question, and clear reasons why a figure is good, bad or ugly. The directory of visualisations and proportional ink chapter back note 01 | 01, 02 | Relevant chapters read online; code-free text, figures made in R |
| Healy, [*Data Visualization: A Practical Introduction*](https://socviz.co/) (Princeton University Press, 2018, ISBN 9780691181615), free online | Best bridge from perception to code. Teaches ggplot2 layer by layer, so the grammar in note 01 is shown in practice | 01 | Site checked, used as background; code is in R |
| Munzner, [*Visualization Analysis and Design*](https://www.cs.ubc.ca/~tmm/vadbook/) (A K Peters/CRC Press, 2014, ISBN 9781466508910) | The academic framework: what, why and how; marks and channels; manipulating views. Read it when you want the theory behind rules of thumb | 01, 03 | Table of contents checked; book not held, so claims are limited to its structure |
| Cairo, [*The Truthful Art*](https://oreilly.com/library/view/the-truthful-art/9780133440492) (New Riders, 2016, ISBN 9780321934079) | Data visualisation from a journalism perspective, including how charts mislead and five qualities of a good one | 05 | Secondary accounts only; book not held |
| Few, *Information Dashboard Design* (O'Reilly, 2006, ISBN 9780596100162) | The reference on dashboards as a form, and the one-screen definition | 05 | Secondary account only, via this [review](https://uxmatters.com/mt/archives/2007/04/book-review-information-dashboard-design.php); book not held |
| Wilkinson, [*The Grammar of Graphics*](https://link.springer.com/book/10.1007/0-387-28695-0) (Springer, 2nd ed., 2005) | The source of the grammar, for readers who want the formal treatment | 01 | Publisher page checked; cited via Wickham's paper |
| Wickham, Navarro & Pedersen, [*ggplot2: Elegant Graphics for Data Analysis*](https://ggplot2-book.org/), 3rd ed., free online | The layered grammar as a working system | 01 | Site checked; reference only |

## Core papers

| Paper | Why read it | Notes |
|---|---|---|
| Anscombe, ["Graphs in Statistical Analysis"](https://www.jstor.org/stable/2682899), *The American Statistician*, 1973 | Four datasets, same summary statistics, different stories. The original case for plotting | 01 |
| Cleveland & McGill, ["Graphical Perception"](https://doi.org/10.1080/01621459.1984.10478080), *JASA* 79(387), 1984 | The experiments behind the ranking of encodings: position beats length beats angle and area | 01 |
| Heer & Bostock, ["Crowdsourcing Graphical Perception"](https://idl.uw.edu/papers/crowdsourcing-graphical-perception), CHI 2010 | Replicates the spatial encoding results online and adds rectangular area, chart size and gridline spacing | 01 |
| Wickham, ["A Layered Grammar of Graphics"](https://vita.had.co.nz/papers/layered-grammar.html), *JCGS* 19(1), 2010 | The grammar as used by ggplot2 and in spirit by seaborn, plotly express and Altair | 01 |
| Shneiderman, ["The Eyes Have It"](https://doi.org/10.1109/VL.1996.545307), IEEE Symposium on Visual Languages, 1996 | Overview first, zoom and filter, then details on demand | 03, 05 |
| Bostock, Ogievetsky & Heer, ["D3: Data-Driven Documents"](https://idl.uw.edu/papers/d3), IEEE TVCG, 2011 | Why D3 works on the document directly | 04 |
| Satyanarayan, Moritz, Wongsuphasawat & Heer, ["Vega-Lite"](https://idl.uw.edu/papers/vega-lite), IEEE TVCG, 2017 | Interaction as part of a declarative grammar, the idea behind Altair's selections | 03, 04 |
| Wigdor & Balakrishnan, on reading rotated text, 2005 | Why rotated labels are slow to read. Cited as reported in Knaflic; paper not read | 02 |

## Courses and videos

| Course | Platform | Cost | Notes supported | Which parts |
|---|---|---|---|---|
| [Data Visualization](https://www.kaggle.com/learn/data-visualization) | Kaggle Learn | Free | 02 | All; short seaborn exercises |
| [Data Visualization with Python](https://www.coursera.org/learn/python-for-data-visualization) | Coursera | Paid; check for free audit | 02, 03, 05 | Matplotlib, seaborn, plotly and dashboard modules |
| [CPSC 547 Information Visualization](https://www.cs.ubc.ca/~tmm/courses/547-22/) | UBC, Munzner's course site | Free | 01, 03 | Reading schedule for the book, with her lecture materials |
| [storytelling with data](https://www.youtube.com/@storytellingwithdata) | YouTube | Free | 05 | Pick by topic; complements the book |

## Tool documentation

| Tool | Notes | Link |
|---|---|---|
| Matplotlib, seaborn | 02 | [Quick start](https://matplotlib.org/stable/users/explain/quick_start.html), [seaborn function overview](https://seaborn.pydata.org/tutorial/function_overview.html) |
| Plotly, Altair | 03 | [Plotly hover text](https://plotly.com/python/hover-text-and-formatting/), [Altair interactions](https://altair-viz.github.io/user_guide/interactions/index.html) |
| D3, Vega-Lite, Observable Plot | 04 | [D3 getting started](https://d3js.org/getting-started), [Vega-Lite compile](https://vega.github.io/vega-lite/usage/compile.html), [Plot source](https://github.com/observablehq/plot) |
| Streamlit, Metabase, Looker Studio | 05 | [Streamlit main concepts](https://docs.streamlit.io/get-started/fundamentals/main-concepts), [Metabase SQL parameters](https://www.metabase.com/docs/latest/questions/native-editor/sql-parameters), [Looker Studio docs](https://cloud.google.com/looker/docs/studio) |

Observable Plot's documentation site rate-limited the check, so this links to the source repository, which is the same project.
