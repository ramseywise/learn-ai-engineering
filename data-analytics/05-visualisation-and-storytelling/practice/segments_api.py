"""Chapter 6's API, in two versions: the one a first draft tends to produce and the one to ship.

Run the good one: uv run --with fastapi --with uvicorn --with pandas --with pyarrow --with scikit-learn uvicorn segments_api:app
Build the table first with `segments.py`. The key below is a stand-in so the example runs:
a real deployment validates a signed token from your single sign-on provider.
"""
import secrets

import pandas as pd
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import segments

KEYS = {"demo-analyst-key": "analyst", "demo-crm-key": "crm"}  # stand-ins for real tokens
MIN_CELL = 5  # a map bin with fewer customers than this is dropped, not shown
DIST = segments.OUTPUT.parent / "js" / "segments_app" / "dist"


class SegmentSummary(BaseModel):
    segment: str
    customers: int
    avg_spend: float
    avg_days_since_order: float
    avg_open_rate: float


class MapBin(BaseModel):
    segment: str
    x: float
    y: float
    customers: int


class CustomerRow(BaseModel):
    """What the CRM list needs. No email address, so it cannot leave by accident."""
    customer_id: int
    segment: str
    region: str
    spend_12m: float


class CustomerPage(BaseModel):
    rows: list[CustomerRow]
    next_after: int | None


def role_of(x_api_key: str = Header(default="")) -> str:
    """Who is calling. Compare keys in constant time, and refuse anything unknown."""
    for key, role in KEYS.items():
        if secrets.compare_digest(x_api_key, key):
            return role
    raise HTTPException(status_code=401, detail="Unknown API key")


def require_crm(role: str = Depends(role_of)) -> str:
    """Seeing a segment and seeing a customer are different permissions."""
    if role != "crm":
        raise HTTPException(status_code=403, detail="Customer rows need the CRM role")
    return role


def summarise(table: pd.DataFrame) -> list[dict]:
    named = table.groupby("segment", sort=True).agg(
        customers=("customer_id", "size"), avg_spend=("spend_12m", "mean"),
        avg_days_since_order=("days_since_order", "mean"), avg_open_rate=("email_open_rate", "mean"))
    return named.round(3).reset_index().to_dict("records")


def bin_map(table: pd.DataFrame, cell: float = .25) -> list[dict]:
    """Count customers per segment on a fixed grid over the two coordinates, so no mark is one person."""
    frame = pd.DataFrame({"segment": table.segment.values,
                          "x": ((table.x // cell) * cell + cell / 2).round(3).values,
                          "y": ((table.y // cell) * cell + cell / 2).round(3).values})
    counted = frame.groupby(["segment", "x", "y"]).size().rename("customers").reset_index()
    return counted[counted.customers >= MIN_CELL].to_dict("records")


def build_app(table: pd.DataFrame, gzip: bool = False) -> FastAPI:
    """The app reads the table the nightly job wrote. It never imports a model."""
    app = FastAPI(title="Fernhill segments")
    if gzip:
        app.add_middleware(GZipMiddleware, minimum_size=1000)
    table = table.sort_values("customer_id")

    @app.get("/v1/regions", response_model=list[str])
    def regions(_: str = Depends(role_of)):
        return sorted(table.region.unique())

    @app.get("/v1/segments", response_model=list[SegmentSummary])
    def segment_summary(region: str | None = None, _: str = Depends(role_of)):
        rows = table if region is None else table[table.region == region]
        return summarise(rows)

    @app.get("/v1/segments/map", response_model=list[MapBin])
    def segment_map(cell: float = Query(.25, ge=.05, le=2), region: str | None = None,
                    _: str = Depends(role_of)):
        rows = table if region is None else table[table.region == region]
        return bin_map(rows, cell)

    @app.get("/v1/customers", response_model=CustomerPage)
    def customers(segment: str, after: int = 0, limit: int = Query(100, ge=1, le=500),
                  _: str = Depends(require_crm)):
        """Keyset pagination: `after` is the last id you saw, so the server never counts past rows."""
        rows = table[(table.segment == segment) & (table.customer_id > after)].head(limit)
        last = int(rows.customer_id.iloc[-1]) if len(rows) == limit else None
        return {"rows": rows[list(CustomerRow.model_fields)].to_dict("records"), "next_after": last}

    return app


def build_naive_app(table: pd.DataFrame) -> FastAPI:
    """The first draft, kept to measure and to learn from. Do not deploy this.

    No key, every customer, every column including the email address, no limit, and a
    refit whenever anyone touches a filter.
    """
    app = FastAPI(title="Do not deploy")

    @app.get("/segments")
    def all_rows():
        return table.to_dict("records")

    @app.get("/segments/refit")
    def refit(region: str | None = None):
        rows = table if region is None else table[table.region == region]
        cluster, _, _ = segments.fit(rows)
        return pd.Series(cluster).value_counts().sort_index().to_dict()

    return app


def app_from_disk() -> FastAPI:
    if not segments.TABLE.exists():
        segments.build_table()
    app = build_app(pd.read_parquet(segments.TABLE), gzip=True)
    if DIST.exists():  # the built React app, on the same origin, so no cross-origin setup is needed
        app.mount("/", StaticFiles(directory=DIST, html=True), name="site")
    return app


def __getattr__(name):  # `uvicorn segments_api:app` loads the table; importing this file does not
    if name == "app":
        return app_from_disk()
    raise AttributeError(name)
