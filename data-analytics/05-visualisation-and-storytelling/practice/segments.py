"""Fernhill's customer segments: the batch job behind chapter 6's dashboard.

Every number is synthetic and seeded. `fernhill.py` is monthly by channel and has
no customer rows, so this file builds its own 50,000 customers and does not touch
that generator. The labels are the input to the dashboard: how to choose a
clustering is in the applied-analyses segmentation chapter, not here.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

OUTPUT = Path(__file__).resolve().parent / "output"
TABLE = OUTPUT / "customer_segments.parquet"
FEATURES = ["orders_12m", "spend_12m", "days_since_order", "email_open_rate", "discount_share"]
REGIONS = {  # name: (share of customers, latitude, longitude of a large city in the region)
    "London": (.19, 51.51, -0.13), "South East": (.16, 51.45, -0.97), "North West": (.12, 53.48, -2.24),
    "East": (.10, 52.20, 0.12), "West Midlands": (.09, 52.49, -1.89), "South West": (.09, 51.45, -2.59),
    "Yorkshire": (.08, 53.80, -1.55), "Scotland": (.07, 55.95, -3.19), "East Midlands": (.06, 52.95, -1.15),
    "Wales": (.04, 51.48, -3.18),
}
# Planted groups: share, then the centre of orders, spend, days since order, open rate, discount share.
PLANTED = [(.22, 9, 620, 30, .55, .10), (.28, 5, 210, 70, .25, .70),
           (.20, 2, 150, 200, .60, .25), (.30, 1, 55, 300, .10, .35)]
# Named after the model has run, by the rank of the centroid's spend and open rate. See name_clusters.
NAMES = ["Loyal regulars", "Discount hunters", "Lapsed email readers", "One and done"]


def make_customers(n=50_000, seed=7, spread=1.0):
    """One row per customer: an id, an email address (personal data, on purpose), a region, the features.

    `spread` widens the noise around each planted group. At 1 the groups barely touch, which is
    kinder than real customers; 2.5 makes them overlap, and chapter 6 measures both.
    """
    rng = np.random.default_rng(seed)
    group = rng.choice(len(PLANTED), n, p=[g[0] for g in PLANTED])
    centres = np.array([g[1:] for g in PLANTED])[group]
    frame = pd.DataFrame({
        "customer_id": np.arange(1, n + 1),
        "orders_12m": rng.poisson(centres[:, 0]) + 1,
        "spend_12m": np.round(centres[:, 1] * rng.lognormal(0, .35 * spread, n), 2),
        "days_since_order": np.clip(rng.normal(centres[:, 2], 45 * spread), 0, 365).round().astype(int),
        "email_open_rate": np.clip(rng.normal(centres[:, 3], .12 * spread), 0, 1).round(3),
        "discount_share": np.clip(rng.normal(centres[:, 4], .15 * spread), 0, 1).round(3),
    })
    frame["email"] = [f"customer{i}@example.com" for i in frame.customer_id]
    shares = np.array([v[0] for v in REGIONS.values()])
    frame["region"] = rng.choice(list(REGIONS), n, p=shares / shares.sum())
    return frame


def fit(frame, seed=0):
    """Scale, cluster and project. Returns integer cluster ids and two display coordinates."""
    scaled = StandardScaler().fit_transform(frame[FEATURES])
    cluster = KMeans(n_clusters=4, n_init=10, random_state=seed).fit_predict(scaled)
    x, y = PCA(n_components=2, random_state=seed).fit_transform(scaled).T
    return cluster, x, y


def name_clusters(frame, cluster):
    """Cluster ids are arbitrary, so name them from what the customers in them do, once."""
    means = frame[FEATURES].groupby(cluster).mean()
    loyal = means.spend_12m.idxmax()
    hunters = means.drop(loyal).discount_share.idxmax()
    rest = means.drop([loyal, hunters])
    readers = rest.email_open_rate.idxmax()
    gone = rest.drop(readers).index[0]
    return {loyal: NAMES[0], hunters: NAMES[1], readers: NAMES[2], gone: NAMES[3]}


def build_table(n=50_000, seed=7, path=TABLE):
    """The nightly job: fit once, write one table the app only ever reads."""
    frame = make_customers(n, seed)
    cluster, x, y = fit(frame)
    frame["segment"] = pd.Series(cluster).map(name_clusters(frame, cluster)).values
    frame["x"], frame["y"] = x.round(3), y.round(3)
    path.parent.mkdir(exist_ok=True)
    frame.to_parquet(path, index=False)
    return frame


if __name__ == "__main__":
    table = build_table()
    print(table.segment.value_counts().to_string())
    print(table.groupby("segment")[FEATURES].mean().round(2).to_string())
