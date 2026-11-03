# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["numpy", "pandas", "pyarrow", "scikit-learn", "fastapi", "httpx2", "uvicorn", "scipy"]
# ///
"""Chapter 6: what one dashboard request costs. Run: uv run ch06_measure_api.py
Writes practice/output/api_measurements.json. In-process TestClient, so no network and no TLS."""
# %% setup
import gzip
import json
import platform
import statistics
import time
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

import segments
import segments_api as api

KEY = {"X-API-Key": "demo-analyst-key"}
CRM = {"X-API-Key": "demo-crm-key"}


def timed(call, repeats):
    """Median and worst of `repeats` calls, in milliseconds, after one warm-up call."""
    call()
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = call()
        times.append((time.perf_counter() - start) * 1000)
    return statistics.median(times), max(times), result


start = time.perf_counter()
table = segments.build_table()
print(f"batch job: {time.perf_counter() - start:.1f} s for {len(table):,} customers, "
      f"{segments.TABLE.stat().st_size / 1e6:.1f} MB parquet")
good, naive = TestClient(api.build_app(table)), TestClient(api.build_naive_app(table))
print(f"{platform.machine()} {platform.system()}, python {platform.python_version()}")
results = {}

# %% endpoints
requests = [
    ("naive: every customer, every column", naive, "/segments", {}, 7),
    ("summary: one row per segment", good, "/v1/segments", KEY, 51),
    ("summary, one region", good, "/v1/segments?region=Wales", KEY, 51),
    ("map: grid of counts, cell 0.25", good, "/v1/segments/map", KEY, 21),
    ("one page of 100 customers", good, "/v1/customers?segment=Loyal%20regulars", CRM, 51),
]
print(f"{'request':38}{'rows':>8}{'JSON KB':>10}{'gzip KB':>10}{'median ms':>11}{'worst ms':>10}")
for name, client, url, headers, repeats in requests:
    median, worst, response = timed(lambda: client.get(url, headers=headers), repeats)
    response.raise_for_status()
    body = response.content
    data = response.json()
    rows = len(data["rows"]) if isinstance(data, dict) else len(data)
    packed = len(gzip.compress(body, 6))
    results[name] = dict(rows=rows, json_kb=len(body) / 1024, gzip_kb=packed / 1024, median_ms=median, worst_ms=worst)
    print(f"{name:38}{rows:>8,}{len(body) / 1024:>10,.1f}{packed / 1024:>10,.1f}{median:>11,.1f}{worst:>10,.1f}")

# %% refusals
print("no key:", good.get("/v1/segments").status_code,
      "| analyst asking for customers:", good.get("/v1/customers?segment=One%20and%20done", headers=KEY).status_code,
      "| limit=50000:", good.get("/v1/customers?segment=One%20and%20done&limit=50000", headers=CRM).status_code)
page = good.get("/v1/customers?segment=One%20and%20done&limit=2", headers=CRM).json()
print(page)
leak = naive.get("/segments").json()[0]
print("naive first row keys:", sorted(leak))

# %% serialisation
records = table.to_dict("records")
print(f"to_dict + json.dumps: {timed(lambda: json.dumps(records), 3)[0]:,.0f} ms, "
      f"{len(json.dumps(records, separators=(",", ":"))) / 1024:,.0f} KB")
slim = table[["x", "y", "segment"]]
as_records = slim.to_json(orient="records")
as_columns = json.dumps({c: slim[c].tolist() for c in slim}, separators=(",", ":"))
print(f"three columns, records {len(as_records) / 1024:,.0f} KB (gzip {len(gzip.compress(as_records.encode(), 6)) / 1024:,.0f}), "
      f"columnar {len(as_columns) / 1024:,.0f} KB (gzip {len(gzip.compress(as_columns.encode(), 6)) / 1024:,.0f})")

# %% refit-versus-read
refit_ms, refit_worst, answer = timed(lambda: naive.get("/segments/refit"), 5)
answer.raise_for_status()
refit_region_ms, _, answer = timed(lambda: naive.get("/segments/refit?region=Wales"), 5)
answer.raise_for_status()
read_ms = timed(lambda: api.summarise(pd.read_parquet(segments.TABLE)), 15)[0]
memory_ms = timed(lambda: api.summarise(table), 51)[0]
results["costs"] = dict(refit_ms=refit_ms, refit_worst_ms=refit_worst, refit_region_ms=refit_region_ms,
                        read_ms=read_ms, memory_ms=memory_ms)
print(f"refit everyone per request     {refit_ms:9,.1f} ms (worst {refit_worst:,.0f})")
print(f"refit one region per request   {refit_region_ms:9,.1f} ms")
print(f"read parquet, then aggregate   {read_ms:9,.1f} ms")
print(f"aggregate the table in memory  {memory_ms:9,.1f} ms")


# %% refit-changes-the-answer
def moved_after_matching(first, second):
    """Share of customers in a different segment, after renaming ids to overlap as far as possible."""
    overlap = pd.crosstab(first, second).values
    rows, cols = linear_sum_assignment(-overlap)
    return 1 - overlap[rows, cols].sum() / len(first)


def stability(frame, label):
    """Fit once as the published labels, then ask what a new seed and two filters would do to them."""
    start = time.perf_counter()
    published, _, _ = segments.fit(frame, seed=0)
    fit_ms = (time.perf_counter() - start) * 1000
    other, _, _ = segments.fit(frame, seed=1)
    print(f"{label}: one fit {fit_ms:,.0f} ms")
    print(f"  new seed: same id for {(published == other).mean():.1%}, "
          f"ARI {adjusted_rand_score(published, other):.3f}, moved {moved_after_matching(published, other):.1%}")
    for name, mask in [("one region", frame.region == "Wales"),
                       ("spend above median", frame.spend_12m > frame.spend_12m.median())]:
        part, _, _ = segments.fit(frame[mask])
        print(f"  refit on {name} ({mask.sum():,}): ARI {adjusted_rand_score(published[mask], part):.3f}, "
              f"moved {moved_after_matching(published[mask], part):.1%}")


stability(table, "groups barely touch (spread 1)")
stability(segments.make_customers(spread=2.5), "groups overlap (spread 2.5)")

# %% real-model-job
scaled = StandardScaler().fit_transform(table[segments.FEATURES])
start = time.perf_counter()
scores = {k: silhouette_score(scaled, KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(scaled),
                              sample_size=10_000, random_state=0) for k in range(2, 9)}
print(f"choosing k from 2 to 8 with a silhouette on a 10,000 sample: {time.perf_counter() - start:.1f} s, "
      f"best k = {max(scores, key=scores.get)}")

Path(segments.OUTPUT / "api_measurements.json").write_text(json.dumps(results, indent=1))
