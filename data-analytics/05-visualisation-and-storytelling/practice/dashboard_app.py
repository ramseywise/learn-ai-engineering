# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pandas", "streamlit", "altair"]
# ///
"""Fernhill weekly dashboard. Run: uv run --with numpy --with pandas --with streamlit streamlit run dashboard_app.py"""
import altair as alt
import pandas as pd
import streamlit as st

import fernhill


@st.cache_data
def load():
    """Runs once per session; every widget interaction after that reuses the result."""
    monthly = fernhill.load_monthly().merge(fernhill.load_repeat(), on=["month", "channel"])
    monthly["channel"] = monthly.channel.map(fernhill.LABELS)
    return monthly


st.set_page_config(page_title="Fernhill", layout="wide")
data = load()
st.title("Fernhill Home: are we buying customers or keeping them?")

names = list(fernhill.LABELS.values())
left, right = st.columns([2, 1])
chosen = left.multiselect("Channel", names, default=names)
year = right.selectbox("Year", [2025, 2024, 2023])
view = data[data.channel.isin(chosen) & (data.month.dt.year == year)]
previous = data[data.channel.isin(chosen) & (data.month.dt.year == year - 1)]


def rate(frame):
    return frame.repeat_90d.sum() / max(frame.new_customers.sum(), 1)


tiles = st.columns(3)
tiles[0].metric("Revenue", f"£{view.revenue.sum() / 1e6:.2f}m",
                f"{view.revenue.sum() / max(previous.revenue.sum(), 1) - 1:+.1%} on last year"
                if len(previous) else None)
tiles[1].metric("90-day repeat rate", f"{rate(view):.1%}",
                f"{(rate(view) - rate(previous)) * 100:+.1f} pts" if len(previous) else None)
tiles[2].metric("Marketing spend", f"£{view.spend.sum() / 1000:,.0f}k")

palette = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
colour = alt.Color("channel:N", title=None, legend=alt.Legend(orient="top"),
                   scale=alt.Scale(domain=names, range=palette))
chart = (alt.Chart(view.assign(rate=view.repeat_90d / view.new_customers * 100))
         .mark_line(strokeWidth=2, point=alt.OverlayMarkDef(size=30))
         .encode(x=alt.X("month:T", title=None, axis=alt.Axis(format="%b", tickCount="month")),
                 y=alt.Y("rate:Q", title="90-day repeat rate (%)", scale=alt.Scale(domain=[0, 60])),
                 color=colour, tooltip=["channel", "month:T", alt.Tooltip("rate:Q", format=".1f")])
         .properties(height=300))
st.altair_chart(chart, width="stretch")

with st.expander("Table view"):
    st.dataframe(view[["month", "channel", "revenue", "spend", "new_customers", "repeat_90d"]])
