# Visualisation and storytelling

How to choose a chart, draw it well in Python and JavaScript, and use it to get a decision made. Four steps: choose and plot, draw static and interactive charts, build a dashboard and a story, and pick a dashboard stack.

**What you should already know.** Nothing below is taught again here. Tick each line off, and go back to the chapter it links for any you cannot.

Processing data, from [module 01](../01-python-for-data-analysis/README.md):

- [ ] Build and index a DataFrame, which is the table every chart here starts from ([Series and DataFrame](../01-python-for-data-analysis/notes/01-series-and-dataframe.md))
- [ ] Select rows and columns without chained indexing ([indexing and selection](../01-python-for-data-analysis/notes/03-indexing-and-selection.md))
- [ ] Join and reshape tables, and check the row counts ([reshaping and joins](../01-python-for-data-analysis/notes/04-reshaping-and-joins.md))

## Lecture

Start with the overview deck, [Visualisation and storytelling](slides/visualisation-and-storytelling.pptx), with its source in [slides/deck.yaml](slides/deck.yaml). It covers the module's chapters in reading order. There is one deck for the module, not one per step.

## The core

Most analyses that fail do not fail at the statistics. They fail in the last metre, when the finding reaches someone who has ten minutes and a chart they cannot read. A good chart is also a thinking tool: as Anscombe showed, four datasets can share every summary statistic and look nothing alike.

Fernhill Home, a fictional online homewares retailer, cut its email budget in January 2025. Revenue kept growing, and the dashboard stayed green. We follow that one dataset through every chapter. First we learn to describe a chart as a mapping from data to marks, which tells us which chart answers which question.

Then we draw it in matplotlib and seaborn until the problem is visible, make it explorable in plotly and Altair, and rebuild it at three levels of abstraction in JavaScript. Finally we build the dashboard that would have caught the fall and write the single chart and sentence that gets the budget restored. The last chapter moves to Fernhill's customer segments and asks what a dashboard should be built on: a BI tool, a Python app or a full stack, with the cost of each measured.

## Syllabus

One row per step. **Core concepts** are the ideas that make the step go right, **Study** is what to read, **Labs** is what to run afterwards, and **Sources** is where to read more. How the chapter code runs is in the Practice section below.

| Submodule | Core concepts | Study | Labs | Sources |
|---|---|---|---|---|
| **1. Choose and plot:** the grammar and your own data | Decide what the chart must say before you choose its type, and write the finding as the title. Position on a common scale is the most accurate encoding, so prefer it. Bars start at zero. Never use two y-axes: use two panels, or index both series to a common base. | [1 Grammar of graphics and chart choice](notes/01-grammar-and-chart-choice.md) · [1b Plotting your own data](notes/01b-plotting-your-own-data.md) | [ch01_grammar_and_choice.py](practice/ch01_grammar_and_choice.py) · [ch02_matplotlib_seaborn.py](practice/ch02_matplotlib_seaborn.py) | VanderPlas, *Python Data Science Handbook* ch. 4 · McKinney, *Python for Data Analysis* ch. 9 · Wilke, *Fundamentals of Data Visualization* · Munzner, *Visualization Analysis and Design* · Anscombe (1973) · Cleveland & McGill (1984) · Wickham, [A Layered Grammar of Graphics](https://vita.had.co.nz/papers/layered-grammar.html) |
| **2. Draw static and interactive charts:** matplotlib, plotly and JavaScript | Assign colour by job: categorical for identity, one hue for magnitude, two hues and a grey midpoint for polarity, and run the palette through a colour-vision check. Label lines directly, and give any chart with two or more series a legend or an equivalent. Anything essential must be visible without hover. Start with Altair, plotly or seaborn, and reach for D3 only when the chart is worth days of work. | [2 Matplotlib and seaborn](notes/02-matplotlib-and-seaborn.md) · [3 Plotly and interactive charts](notes/03-plotly-and-interactive.md) · [4 JavaScript: D3, Vega-Lite and Observable Plot](notes/04-javascript-d3-vega-lite-observable-plot.md) | [ch02_matplotlib_seaborn.py](practice/ch02_matplotlib_seaborn.py) · [ch03_plotly_interactive.py](practice/ch03_plotly_interactive.py) · [js/](practice/js) | VanderPlas ch. 4 · McKinney ch. 9 and 14 · Knaflic, *Storytelling with Data* · Shneiderman, [The Eyes Have It](https://doi.org/10.1109/VL.1996.545307) · Bostock, Ogievetsky & Heer, [D3](https://idl.uw.edu/papers/d3) · Satyanarayan et al., [Vega-Lite](https://idl.uw.edu/papers/vega-lite) · Murray, *Interactive Data Visualization for the Web* |
| **3. Dashboards and story:** monitor a number, then get a decision made | Pair a metric you can push by spending with a metric that shows the side effect. A dashboard answers "what is my number?" and does not deliver a finding, so write the sentence and send it. | [5 Dashboards and storytelling with data](notes/05-dashboards-and-storytelling.md) | [ch05_dashboards_and_story.py](practice/ch05_dashboards_and_story.py) · [dashboard_app.py](practice/dashboard_app.py) | Knaflic, *Storytelling with Data* · Few, *Information Dashboard Design* · Cairo, *The Truthful Art* · Shneiderman (1996) |
| **4. Dashboard stacks:** from Python results to a browser | Pick the stack by the situation, take the lightest route that fits, and move up only for a requirement you can name. Precompute the labels and read them from a table, because a filter selects rows and never refits. Colour categories by name, with a second encoding, and never by a numeric id. | [6 Dashboard stacks: from Python results to a browser](notes/06-dashboard-stacks-from-python-to-frontend.md) · [6b Dashboard stacks, part 2: the data path, many points, colour and the finished pages](notes/06b-dashboard-data-path-points-colour-and-worked-example.md) | [ch06_measure_api.py](practice/ch06_measure_api.py) · [ch06_stack_map.py](practice/ch06_stack_map.py) · [ch06_figure.py](practice/ch06_figure.py) · [ch06_browser.py](practice/ch06_browser.py) · [segments_dash.py](practice/segments_dash.py) · [js/](practice/js) | Wilke, on colour pitfalls and geospatial data · the tool documentation listed in references.md for FastAPI, React, Dash, Streamlit, Power BI and Datashader |

Every source and the notes it maps to: [references.md](references.md).

## Rules of thumb

- **Decide what the chart must say before you choose its type.** Write the finding as the title.
- **Position on a common scale is the most accurate encoding.** Prefer it whenever you can.
- **Bars start at zero.** Lines may not need to, but the axis must say so.
- **Never use two y-axes.** Use two panels, or index both series to a common base.
- **Assign colour by job:** categorical for identity, one hue for magnitude, two hues and a grey midpoint for polarity. Run the palette through a colour-vision check.
- **Label lines directly,** and give any chart with two or more series a legend or an equivalent.
- **Start with Altair, plotly or seaborn.** Reach for D3 only when the chart is worth days of work.
- **Anything essential must be visible without hover.**
- **Pair a metric you can push by spending with a metric that shows the side effect.**
- **A dashboard answers "what is my number?".** It does not deliver a finding. Write the sentence and send it.
- **Pick the stack by the situation,** take the lightest route that fits, and move up only for a requirement you can name.
- **Precompute the labels and read them from a table.** A filter selects rows; it never refits.
- **Colour categories by name,** with a second encoding, and never by a numeric id.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DA 01 Processing data](../01-python-for-data-analysis/README.md) | The table every chart here starts from; chapter 1b plots its orders and its year of daily revenue |
| [Python 02/03 Web data](../../programming/python/02-informatics/notes/03-web-data-json-xml.md) | HTTP and JSON, for how results reach a browser in chapter 6 |
| [TypeScript 01 JavaScript for Python developers](../../programming/typescript/notes/01-js-for-python-devs.md) | Optional, for reading the React front end in chapter 6 |

**Feeds into**

| Chapter | Why |
|---|---|
| [GA 06/06 Cost and latency dashboards](../../generative-ai/06-observability/notes/06-cost-and-latency-dashboards.md) | What a dashboard is for, applied to LLM traces |
| [GA 07/05 Data-analysis agent](../../generative-ai/07-agentic-applications/notes/05-data-analysis-agent.md) | An agent's charts answer to the same standards |

<a id="deck-and-practice"></a>

## Practice

The code is in [practice/](practice/). Every chart in the notes is generated there and saved to `data-analytics/sources/images/`. The data comes from `practice/fernhill.py`, a seeded generator, so nothing needs downloading.

```bash
cd data-analytics/05-visualisation-and-storytelling/practice
uv run ch01_grammar_and_choice.py
uv run ch02_matplotlib_seaborn.py
uv run ch03_plotly_interactive.py       # writes HTML to output/; the PNG export needs Chrome
uv run ch05_dashboards_and_story.py
uv run --with numpy --with pandas --with altair --with streamlit streamlit run dashboard_app.py
uv run ch06_measure_api.py              # the request, refit and stability tables for chapter 6
uv run ch06_stack_map.py                # versions, colour, datashader, Folium; the PNG needs Chrome
uv run ch06_figure.py                   # the download chart; run npm run sizes first
uv run ch06_browser.py                  # draw times and both dashboards' screenshots; needs Chrome
uv run segments_dash.py                 # the Dash app on localhost:8050

cd js && npm install && npm run all     # Node 22; rebuilds the three JavaScript charts
npm run sizes && npm run app            # chapter 6: bundle sizes and the React build
python3 -m http.server                  # then open localhost:8000 for the browser D3 chart
```

The deck is rebuilt with `make slides PILLAR=data-analytics/05-visualisation-and-storytelling STRICT=1`.

## Primary texts

- Knaflic, *Storytelling with Data*
- VanderPlas, *Python Data Science Handbook*: background for the matplotlib chapter

Everything else: [references.md](references.md).

## Next

Start with submodule 1, **Choose and plot**: read [1 Grammar of graphics and chart choice](notes/01-grammar-and-chart-choice.md), then the other notes in the syllabus order.

After submodule 4 you can choose a chart for a question, draw it in Python and JavaScript, build a dashboard that would have caught a fall, and write the chart and sentence that get a decision made. Go on to [experimentation and causality](../03-experimentation-and-causality/README.md), the first advanced module, and after it [applied analyses](../06-applied-analyses/README.md), which use these charts on worked business questions. Readers new to pandas should start with [processing data](../01-python-for-data-analysis/README.md).
