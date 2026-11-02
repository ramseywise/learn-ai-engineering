# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["numpy", "pandas", "pyarrow", "scikit-learn", "fastapi", "plotly", "dash"]
# ///
"""The same segments page as a Dash app: no JavaScript, one Python file. Run: uv run segments_dash.py
Dash starts on localhost:8050. It imports the helpers the API uses, so both routes show the same numbers."""
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dash_table, dcc, html

import segments
import segments_api as api

if not segments.TABLE.exists():
    segments.build_table()
TABLE = pd.read_parquet(segments.TABLE)  # read-only in every worker, which is what Dash asks for
COLOURS = dict(zip(segments.NAMES, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]))
SYMBOLS = dict(zip(segments.NAMES, ["circle", "square", "triangle-up", "diamond"]))

app = Dash(__name__, title="Fernhill customer segments")
app.layout = html.Main([
    html.H1("Fernhill customer segments"),
    dcc.Dropdown(sorted(TABLE.region.unique()), id="region", placeholder="All regions"),
    dcc.Graph(id="map"),
    dash_table.DataTable(id="summary"),
])


@callback(Output("map", "figure"), Output("summary", "data"), Input("region", "value"))
def update(region):
    """Runs on the server every time the dropdown changes. Reads the labels, never refits."""
    rows = TABLE if region is None else TABLE[TABLE.region == region]
    bins = pd.DataFrame(api.bin_map(rows))
    figure = px.scatter(bins, x="x", y="y", size="customers", color="segment", symbol="segment",
                        category_orders={"segment": segments.NAMES},
                        color_discrete_map=COLOURS, symbol_map=SYMBOLS, template="none",
                        labels={"x": "Coordinate 1", "y": "Coordinate 2", "segment": ""})
    return figure, api.summarise(rows)


if __name__ == "__main__":
    app.run(debug=False)
