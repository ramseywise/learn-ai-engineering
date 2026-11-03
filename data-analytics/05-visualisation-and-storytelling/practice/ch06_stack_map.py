# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["numpy", "pandas", "pyarrow", "scikit-learn", "plotly", "kaleido", "altair", "bokeh", "folium", "holoviews", "datashader", "matplotlib"]
# ///
"""Chapter 6: which JavaScript each Python library sends, what a figure weighs, and colour for categories.
Run: uv run ch06_stack_map.py   The PNG export needs Chrome for kaleido."""
# %% python-to-javascript
import gzip
import json
import time

import altair as alt
import bokeh
import bokeh.resources
import folium
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import chartstyle as cs
import segments

table = segments.build_table()
print("plotly.py", plotly.__version__, "-> plotly.js", plotly.offline.get_plotlyjs_version())
print("altair", alt.__version__, "-> vega-lite", alt.VEGALITE_VERSION, "vega", alt.VEGA_VERSION, "vega-embed", alt.VEGAEMBED_VERSION)
print("bokeh", bokeh.__version__, "->", [u.rsplit("/", 1)[-1] for u in bokeh.resources.CDN.js_files[:1]])
print("folium", folium.__version__, "->", [u for name, u in folium.Map.default_js if name == "leaflet"])

import holoviews as hv  # noqa: E402

hv.extension("bokeh", "matplotlib", "plotly", logo=False)
print("holoviews", hv.__version__, "-> backends it loaded:", sorted(hv.Store.renderers))

# %% figure-weight
xy = table[["x", "y"]]
fig = go.Figure(go.Scattergl(x=xy.x.values, y=xy.y.values, mode="markers"))
as_arrays = fig.to_json()
as_lists = go.Figure(go.Scattergl(x=xy.x.tolist(), y=xy.y.tolist(), mode="markers")).to_json()
for name, text in [("numpy arrays", as_arrays), ("python lists", as_lists)]:
    print(f"plotly figure, 50,000 points, {name}: {len(text) / 1024:,.0f} KB, gzip {len(gzip.compress(text.encode(), 6)) / 1024:,.0f} KB")

# %% datashader
import datashader as ds  # noqa: E402

rng = np.random.default_rng(1)
for points in (50_000, 50_000, 5_000_000):  # the first call compiles, so the 50,000 runs twice
    idx = rng.integers(0, len(table), points)
    cloud = pd.DataFrame({"x": table.x.values[idx] + rng.normal(0, .05, points),
                          "y": table.y.values[idx] + rng.normal(0, .05, points),
                          "segment": pd.Categorical(table.segment.values[idx], categories=segments.NAMES)})
    start = time.perf_counter()
    canvas = ds.Canvas(plot_width=800, plot_height=500)
    aggregate = canvas.points(cloud, "x", "y", ds.count_cat("segment"))
    image = ds.tf.shade(aggregate, color_key=dict(zip(segments.NAMES, cs.CATEGORICAL)), min_alpha=80).to_pil()
    elapsed = (time.perf_counter() - start) * 1000
    path = segments.OUTPUT / f"datashader_{points}.png"
    image.save(path)
    print(f"datashader {points:>9,} points: {elapsed:6,.0f} ms, PNG {path.stat().st_size / 1024:,.0f} KB, image is {image.size}")
    if points == 5_000_000:
        image.save(cs.IMAGES / "viz-segments-datashader.png")

# %% colour-for-categories
table["cluster"] = table.segment.map({n: i for i, n in enumerate(segments.NAMES)})
sample = table.sample(3_000, random_state=0)
numeric = px.scatter(sample, x="x", y="y", color="cluster")
print("numeric ids:", len(numeric.data), "trace, colour bar titled", repr(numeric.layout.coloraxis.colorbar.title.text),
      "| colours are", numeric.layout.coloraxis.colorscale[0][1], "...", numeric.layout.coloraxis.colorscale[-1][1])
COLOURS = dict(zip(segments.NAMES, cs.CATEGORICAL))
named = px.scatter(sample, x="x", y="y", color="segment", symbol="segment",
                   category_orders={"segment": segments.NAMES}, color_discrete_map=COLOURS)
print("names:", len(named.data), "traces:", [t.name for t in named.data])

whole = px.scatter(sample, x="x", y="y", color="segment")
filtered = px.scatter(sample[sample.segment != whole.data[0].name], x="x", y="y", color="segment")
print("no colour map, whole table:     ", {t.name: t.marker.color for t in whole.data})
print("no colour map, one segment gone:", {t.name: t.marker.color for t in filtered.data})

both = make_subplots(cols=2, horizontal_spacing=.2, subplot_titles=(
    "Numeric ids: a colour scale implies 3 is more than 0", "Names: four categories, each with a shape and a legend"))
for trace in numeric.data:
    both.add_trace(trace, row=1, col=1)
for trace in named.data:
    trace.legendgroup = None
    both.add_trace(trace.update(marker_size=5), row=1, col=2)
both.update_layout(coloraxis=numeric.layout.coloraxis, template="none", width=1100, height=430,
                   paper_bgcolor=cs.SURFACE, plot_bgcolor=cs.SURFACE, font=dict(color=cs.SECONDARY),
                   legend=dict(x=.55, y=-.13, orientation="h"), margin=dict(l=60, r=20, t=50, b=70))
both.update_layout(coloraxis_colorbar=dict(x=.41, len=.9, thickness=14, title="cluster"))
both.update_xaxes(showticklabels=False, showgrid=False, title="Coordinate 1", linecolor=cs.BASELINE)
both.update_yaxes(showticklabels=False, showgrid=False, title="Coordinate 2", linecolor=cs.BASELINE)
both.write_image(cs.IMAGES / "viz-segments-numeric-vs-categorical.png", scale=1.5)
print("saved viz-segments-numeric-vs-categorical.png")

# %% maps
regional = table.groupby(["region", "segment"]).size().unstack()
shares = regional.div(regional.sum(axis=1), axis=0)
UK = folium.Map(location=[53.5, -2], zoom_start=6, tiles="OpenStreetMap")
for region, (_, lat, lon) in segments.REGIONS.items():
    folium.CircleMarker([lat, lon], radius=(regional.loc[region].sum() ** .5) / 8, weight=1, fill=True,
                        tooltip=f"{region}: {regional.loc[region].sum():,} customers, "
                                f"{shares.loc[region, 'Loyal regulars']:.0%} loyal regulars").add_to(UK)
UK.save(segments.OUTPUT / "segments_regions.html")
everyone = folium.Map(location=[53.5, -2], zoom_start=6)
for row in table.head(5_000).itertuples():
    lat, lon = segments.REGIONS[row.region][1:]
    folium.CircleMarker([lat + rng.normal(0, .3), lon + rng.normal(0, .3)], radius=2).add_to(everyone)
everyone.save(segments.OUTPUT / "segments_everyone.html")
for name in ("segments_regions.html", "segments_everyone.html"):
    print(f"{name}: {(segments.OUTPUT / name).stat().st_size / 1024:,.0f} KB")
