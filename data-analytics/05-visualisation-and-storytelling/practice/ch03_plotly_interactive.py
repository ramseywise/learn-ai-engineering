# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pandas", "plotly", "kaleido", "altair", "matplotlib"]
# ///
"""Chapter 3: interactive charts with plotly and Altair. Run: uv run ch03_plotly_interactive.py
Writes HTML to practice/output/ and a static PNG to sources/images/. The PNG needs Chrome for kaleido."""
# %% px-line
from pathlib import Path

import pandas as pd
import plotly.express as px
import chartstyle as cs
import fernhill

Path("output").mkdir(exist_ok=True)
monthly = fernhill.load_monthly().assign(channel=lambda d: d.channel.map(fernhill.LABELS))
colours = {fernhill.LABELS[c]: v for c, v in cs.CHANNEL_COLOUR.items()}
fig = px.line(monthly, x="month", y="revenue", color="channel",
              color_discrete_map=colours, labels={"revenue": "Revenue (£)", "month": ""},
              custom_data=["sessions", "orders"],
              title="Monthly revenue by channel")
print(type(fig).__name__, len(fig.data), "traces,", fig.data[0].mode, "mode")
print(fig.data[0].hovertemplate)

# %% polish
fig.update_traces(line_width=2, hovertemplate=(
    "%{x|%b %Y}<br><b>£%{y:,.0f}</b><br>%{customdata[0]:,} sessions, "
    "%{customdata[1]:,} orders<extra>%{fullData.name}</extra>"))
fig.update_layout(template="none", title_x=0.02, paper_bgcolor=cs.SURFACE, plot_bgcolor=cs.SURFACE,
                  font=dict(family="Helvetica Neue, Arial, sans-serif", color=cs.SECONDARY),
                  hovermode="closest", legend=dict(orientation="h", y=1.08, title=None),
                  margin=dict(l=70, r=20, t=90, b=40), width=960, height=480)
fig.update_xaxes(showgrid=False, linecolor=cs.BASELINE, rangeslider_visible=True)
fig.update_yaxes(gridcolor=cs.GRID, zeroline=False, rangemode="tozero", tickformat=",.0f")
fig.add_shape(type="line", x0=fernhill.CUT, x1=fernhill.CUT, yref="paper", y0=0, y1=1,
              line=dict(color=cs.MUTED, width=1))
fig.add_annotation(x=fernhill.CUT, yref="paper", y=1, text="Email budget cut", showarrow=False,
                   xanchor="left", font=dict(color=cs.SECONDARY))
print(sorted(fig.to_dict()), [t["name"] for t in fig.to_dict()["data"]])

# %% export
inline, cdn = Path("output/revenue_inline.html"), Path("output/revenue_cdn.html")
fig.write_html(inline, include_plotlyjs=True)
fig.write_html(cdn, include_plotlyjs="cdn")
for path in (inline, cdn):
    print(path.name, f"{path.stat().st_size / 1024:,.0f} KB")
fig.write_image(cs.IMAGES / "viz-plotly-revenue-by-channel.png", scale=1.25)
print("static copy written")

# %% dropdown
import plotly.graph_objects as go

wide = monthly.pivot(index="month", columns="channel", values="revenue")
choice = go.Figure()
names = [fernhill.LABELS[c] for c in fernhill.CHANNELS]
for name in names:
    choice.add_trace(go.Scatter(x=wide.index, y=wide[name], name=name, line_color=colours[name],
                                visible=name == names[0]))
buttons = [dict(label=name, method="update", args=[{"visible": [n == name for n in names]}])
           for name in names]
choice.update_layout(updatemenus=[dict(buttons=buttons, x=0, y=1.15, xanchor="left")],
                     template="none", yaxis_rangemode="tozero")
choice.write_html("output/revenue_dropdown.html", include_plotlyjs="cdn")
print(buttons[2]["label"], buttons[2]["args"][0]["visible"])

# %% altair-brush
import altair as alt

story = fernhill.total_by_month().reset_index()
story["rate_pct"] = story.repeat_rate * 100
brush = alt.selection_interval(encodings=["x"])
overview = (alt.Chart(story).mark_line(strokeWidth=2, color=cs.BLUE)
            .encode(x=alt.X("month:T", title=None), y=alt.Y("revenue:Q", title="Revenue (£)"))
            .properties(width=640, height=90).add_params(brush))
detail = (alt.Chart(story).mark_line(strokeWidth=2, color=cs.ORANGE, point=True)
          .encode(x=alt.X("month:T", title=None, scale=alt.Scale(domain=brush)),
                  y=alt.Y("rate_pct:Q", title="90-day repeat rate (%)",
                          scale=alt.Scale(domain=[0, 45])),
                  tooltip=[alt.Tooltip("month:T", format="%b %Y"),
                           alt.Tooltip("rate_pct:Q", format=".1f")])
          .properties(width=640, height=220))
linked = alt.vconcat(overview, detail)
linked.save("output/linked_brush.html")
spec = linked.to_dict()
print(spec["params"][0]["select"], Path("output/linked_brush.html").stat().st_size, "bytes")
