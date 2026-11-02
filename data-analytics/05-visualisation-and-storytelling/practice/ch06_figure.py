# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pandas", "matplotlib"]
# ///
"""Chapter 6's one chart: what the browser downloads. Run after ch06_measure_api.py and `npm run sizes`."""
import json

import matplotlib.pyplot as plt
import pandas as pd

import chartstyle as cs
import segments

api = json.loads((segments.OUTPUT / "api_measurements.json").read_text())
code = {r["name"]: r["gzip_kb"] for r in json.loads((segments.OUTPUT / "bundle_sizes.json").read_text())}
rows = [
    ("Data: every customer, every column", api["naive: every customer, every column"]["gzip_kb"], cs.ORANGE),
    ("Data: grid of counts for the map", api["map: grid of counts, cell 0.25"]["gzip_kb"], cs.ORANGE),
    ("Data: one row per segment", api["summary: one row per segment"]["gzip_kb"], cs.ORANGE),
    ("Code: plotly.js, every chart type", code["plotly.js-dist-min (every chart type)"], cs.BLUE),
    ("Code: plotly.js basic", code["plotly.js-basic-dist-min (bar, pie, scatter)"], cs.BLUE),
    ("Code: ECharts, everything", code["echarts, everything"], cs.BLUE),
    ("Code: vega-embed, Vega, Vega-Lite", code["vega-embed + vega + vega-lite"], cs.BLUE),
    ("Code: ECharts, scatter only", code["echarts, scatter only"], cs.BLUE),
    ("Code: Recharts scatter with React", code["recharts scatter + react"], cs.BLUE),
    ("Code: D3, everything", code["d3, everything"], cs.BLUE),
    ("Code: Leaflet", code["leaflet"], cs.BLUE),
]
frame = pd.DataFrame(rows, columns=["what", "kb", "colour"]).iloc[::-1]
cs.apply()
fig, ax = plt.subplots(figsize=(8, 4.4))
ax.barh(frame.what, frame.kb, color=frame.colour, height=.68)
for i, value in enumerate(frame.kb):
    ax.text(value + 15, i, f"{value:,.1f} KB" if value < 10 else f"{value:,.0f} KB", va="center", color=cs.SECONDARY)
ax.set_xlim(0, frame.kb.max() * 1.14)
ax.grid(False)
ax.set_xticks([])
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(True)
ax.tick_params(left=False)
ax.set_title("Sending every customer costs as much as the largest chart library; a summary costs almost nothing",
             fontsize=10)
ax.set_xlabel("Gzipped download, 50,000 synthetic customers", color=cs.SECONDARY)
cs.save(fig, "viz-segments-what-the-browser-downloads.png")
