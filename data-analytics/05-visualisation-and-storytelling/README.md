# Visualisation and storytelling

How to choose a chart, draw it well in Python and JavaScript, and use it to get a decision made.

**Why this pillar.** Most analyses that fail do not fail at the statistics. They fail in the last metre, when the finding reaches someone who has ten minutes and a chart they cannot read. A good chart is also a thinking tool: as Anscombe showed, four datasets can share every summary statistic and look nothing alike.

**The story.** Fernhill Home, a fictional online homewares retailer, cut its email budget in January 2025. Revenue kept growing, and the dashboard stayed green. We follow that one dataset through every chapter. First we learn to describe a chart as a mapping from data to marks, which tells us which chart answers which question. Then we draw it in matplotlib and seaborn until the problem is visible, make it explorable in plotly and Altair, and rebuild it at three levels of abstraction in JavaScript. Finally we build the dashboard that would have caught the fall and write the single chart and sentence that gets the budget restored. The last chapter moves to Fernhill's customer segments and asks what a dashboard should be built on: a BI tool, a Python app or a full stack, with the cost of each measured.

## Reading order

| # | Note | The question it answers |
|---|---|---|
| 1 | [Grammar of graphics and chart choice](notes/01-grammar-and-chart-choice.md) | What is a chart, and which one fits this question? |
| 2 | [Matplotlib and seaborn](notes/02-matplotlib-and-seaborn.md) | How do I get a publication-ready static chart from Python? |
| 3 | [Plotly and interactive charts](notes/03-plotly-and-interactive.md) | When does interaction earn its cost, and how do I ship it? |
| 4 | [JavaScript: D3, Vega-Lite and Observable Plot](notes/04-javascript-d3-vega-lite-observable-plot.md) | What is underneath, and when should I write it directly? |
| 5 | [Dashboards and storytelling with data](notes/05-dashboards-and-storytelling.md) | How do I monitor a number, and how do I get a decision made? |
| 6 | [Dashboard stacks: from Python results to a browser](notes/06-dashboard-stacks-from-python-to-frontend.md) | Which stack should this dashboard use, and how do results reach a browser? |

Then go on to [applied analyses](../06-applied-analyses/README.md), which use these charts on worked business questions. Readers new to pandas should start with [Python for data analysis](../01-python-for-data-analysis/README.md).

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DA 01 Python for data analysis](../01-python-for-data-analysis/README.md) | The starting point in this subject |
| [Python 02/03 Web data](../../programming/python/02-informatics/notes/03-web-data-json-xml.md) | HTTP and JSON, for how results reach a browser in chapter 6 |
| [TypeScript 01 JavaScript for Python developers](../../programming/typescript/notes/01-js-for-python-devs.md) | Optional, for reading the React front end in chapter 6 |

**Feeds into**

| Chapter | Why |
|---|---|
| [GA 06/06 Cost and latency dashboards](../../generative-ai/06-observability/notes/06-cost-and-latency-dashboards.md) | What a dashboard is for, applied to LLM traces |
| [GA 07/05 Data-analysis agent](../../generative-ai/07-agentic-applications/notes/05-data-analysis-agent.md) | An agent's charts answer to the same standards |

## Rules of thumb

- Decide what the chart must say before you choose its type. Write the finding as the title.
- Position on a common scale is the most accurate encoding. Prefer it whenever you can.
- Bars start at zero. Lines may not need to, but the axis must say so.
- Never use two y-axes. Use two panels, or index both series to a common base.
- Assign colour by job: categorical for identity, one hue for magnitude, two hues and a grey midpoint for polarity. Run the palette through a colour-vision check.
- Label lines directly, and give any chart with two or more series a legend or an equivalent.
- Start with Altair, plotly or seaborn. Reach for D3 only when the chart is worth days of work.
- Anything essential must be visible without hover.
- Pair a metric you can push by spending with a metric that shows the side effect.
- A dashboard answers "what is my number?". It does not deliver a finding. Write the sentence and send it.
- Pick the stack by the situation, take the lightest route that fits, and move up only for a requirement you can name.
- Precompute the labels and read them from a table. A filter selects rows; it never refits.
- Colour categories by name, with a second encoding, and never by a numeric id.

## Deck and practice

The deck is [`slides/visualisation-and-storytelling.pptx`](slides/visualisation-and-storytelling.pptx), with its source in [`slides/deck.yaml`](slides/deck.yaml). Rebuild it with `make slides PILLAR=data-analytics/05-visualisation-and-storytelling STRICT=1`.

The code is in [`practice/`](practice/). Every chart in the notes is generated there and saved to `data-analytics/sources/images/`. The data comes from `practice/fernhill.py`, a seeded generator, so nothing needs downloading.

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

## Primary texts

- Knaflic, *Storytelling with Data*
- VanderPlas, *Python Data Science Handbook*: background for the matplotlib chapter

Everything else: [references.md](references.md).
