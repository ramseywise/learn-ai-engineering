# Visualisation and storytelling

How to choose a chart, draw it well in Python and JavaScript, and use it to get a decision made.

**Why this pillar.** Most analyses that fail do not fail at the statistics. They fail in the last metre, when the finding reaches someone who has ten minutes and a chart they cannot read. A good chart is also a thinking tool: as Anscombe showed, four datasets can share every summary statistic and look nothing alike.

**The story.** Fernhill Home, a fictional online homewares retailer, cut its email budget in January 2025. Revenue kept growing, and the dashboard stayed green. We follow that one dataset through every chapter. First we learn to describe a chart as a mapping from data to marks, which tells us which chart answers which question. Then we draw it in matplotlib and seaborn until the problem is visible, make it explorable in plotly and Altair, and rebuild it at three levels of abstraction in JavaScript. Finally we build the dashboard that would have caught the fall and write the single chart and sentence that gets the budget restored.

## Reading order

| # | Note | The question it answers |
|---|---|---|
| 1 | [Grammar of graphics and chart choice](notes/01-grammar-and-chart-choice.md) | What is a chart, and which one fits this question? |
| 2 | [Matplotlib and seaborn](notes/02-matplotlib-and-seaborn.md) | How do I get a publication-ready static chart from Python? |
| 3 | [Plotly and interactive charts](notes/03-plotly-and-interactive.md) | When does interaction earn its cost, and how do I ship it? |
| 4 | [JavaScript: D3, Vega-Lite and Observable Plot](notes/04-javascript-d3-vega-lite-observable-plot.md) | What is underneath, and when should I write it directly? |
| 5 | [Dashboards and storytelling with data](notes/05-dashboards-and-storytelling.md) | How do I monitor a number, and how do I get a decision made? |

Then go on to [applied analyses](../06-applied-analyses/README.md), which use these charts on six business questions. Readers new to pandas should start with [Python for data analysis](../01-python-for-data-analysis/README.md).

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

cd js && npm install && npm run all     # Node 22; rebuilds the three JavaScript charts
python3 -m http.server                  # then open localhost:8000 for the browser D3 chart
```
