"""Code from notes/03-distributed-compute.md. The Spark sections need a Java runtime (Java 17 was tested).

Run from any folder (it writes only to a temporary directory):
    uv run --with duckdb --with pyarrow --with numpy --with polars --with pyspark python 03_distributed_compute.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- setup ---
import numpy as np, pyarrow as pa, pyarrow.parquet as pq, duckdb, polars as pl, subprocess, zlib, os, time, random
from collections import Counter, defaultdict

def make_trips(n=1_000_000, seed=7):
    rng = np.random.default_rng(seed)
    start = np.datetime64("2026-01-01T00:00:00", "s")
    seconds = np.sort(rng.integers(0, 31 * 86_400, n))
    weights = 1 / np.arange(1, 261)
    zones = rng.choice(260, n, p=weights / weights.sum()) + 1
    miles = np.round(rng.gamma(2.0, 1.6, n), 2)
    return pa.table({
        "trip_id": np.arange(n, dtype="int64"),
        "pickup_at": pa.array(start + seconds.astype("timedelta64[s]")),
        "pickup_zone": zones.astype("int32"),
        "payment_type": pa.array(rng.choice(["card", "cash", "app"], n, p=[.7, .2, .1])),
        "passengers": rng.choice([1, 2, 3, 4], n, p=[.7, .18, .07, .05]).astype("int8"),
        "trip_miles": miles,
        "fare_usd": np.round(np.maximum(3.0, 3.0 + 2.5 * miles + rng.normal(0, 1.0, n)), 2),
    })

trips = make_trips()
pq.write_table(trips, "trips.parquet", compression="zstd")
zones = trips["pickup_zone"].to_pylist()
print("--- setup done")

# --- unix ---
with open("zones.txt", "w") as f:
    f.writelines(f"{z}\n" for z in zones[:200_000])
print(subprocess.run("sort zones.txt | uniq -c | sort -rn | head -3", shell=True, capture_output=True, text=True).stdout)
print("--- unix done")

# --- mapreduce ---
N_REDUCERS = 4

def map_task(chunk):
    for zone in chunk:
        yield zone, 1

def partition(key):
    # A stable hash: Python's hash() of strings changes per process, which would split a key.
    return zlib.crc32(str(key).encode()) % N_REDUCERS

def reduce_task(key, values):
    return key, sum(values)

splits = [zones[i:i + 250_000] for i in range(0, len(zones), 250_000)]   # four map tasks

# Map side: each task writes one sorted spill per reducer.
spills = defaultdict(list)
for chunk in splits:
    per_reducer = defaultdict(list)
    for key, value in map_task(chunk):
        per_reducer[partition(key)].append((key, value))
    for r, pairs in per_reducer.items():
        spills[r].append(sorted(pairs))

# Reduce side: merge the sorted spills, so one key's values arrive together.
from heapq import merge
from itertools import groupby
result = {}
for r in range(N_REDUCERS):
    merged = merge(*spills[r])
    for key, group in groupby(merged, key=lambda kv: kv[0]):
        k, v = reduce_task(key, (value for _, value in group))
        result[k] = v

print("reducer input sizes:", [sum(map(len, spills[r])) for r in range(N_REDUCERS)])
print("top zones:", sorted(result.items(), key=lambda kv: -kv[1])[:3])
assert result == Counter(zones)
print("--- mapreduce done")

# --- commit ---
def run_task(rows, out_path, fail_after=None):
    """Write to a temporary name and rename on success: readers never see half a file."""
    tmp = out_path + ".tmp"
    with open(tmp, "w") as f:
        for i, row in enumerate(rows):
            if fail_after is not None and i == fail_after:
                raise RuntimeError("worker preempted")
            f.write(f"{row}\n")
    os.replace(tmp, out_path)

try:
    run_task(range(1000), "part-0", fail_after=400)
except RuntimeError as exc:
    print("attempt 1:", exc, "| output exists:", os.path.exists("part-0"))
run_task(range(1000), "part-0")
print("attempt 2: output lines:", sum(1 for _ in open("part-0")))
print("--- commit done")

# --- preemption ---
hourly = 0.05
per_10_min = 1 - (1 - hourly) ** (10 / 60)
print(f"10-minute task killed: {per_10_min:.2%}")
print(f"at least one of 100 killed: {1 - (1 - per_10_min) ** 100:.0%}")
print("--- preemption done")

# --- join_cost ---
trip_bytes, zone_bytes = trips.nbytes, 260 * 64     # 64 bytes is an assumed width for a zone row
nodes = 10

sort_merge = trip_bytes * (nodes - 1) / nodes + zone_bytes * (nodes - 1) / nodes
broadcast = zone_bytes * (nodes - 1)
print(f"partitioned join moves about {sort_merge / 1e6:8.2f} MB across the network")
print(f"broadcast join moves about   {broadcast / 1e6:8.2f} MB across the network")
print("--- join_cost done")

# --- skew ---
def load(keys, reducers=8):
    counts = Counter(zlib.crc32(str(k).encode()) % reducers for k in keys)
    return [counts[r] for r in range(reducers)]

plain = load(zones)
# Salt only the known hot key: two-stage aggregation splits it across every reducer.
hot = {1}
rng = random.Random(0)
salted = load(f"{z}#{rng.randrange(8)}" if z in hot else z for z in zones)
for name, l in [("plain", plain), ("salted", salted)]:
    print(f"{name:7s} max {max(l):7d} mean {sum(l) // len(l):7d} max/mean {max(l) / (sum(l) / len(l)):.2f}")
print("--- skew done")

# --- lineage ---
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.master("local[4]").appName("trips").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
rdd = spark.sparkContext.parallelize(zones, 8).map(lambda z: (z, 1)).reduceByKey(lambda a, b: a + b, 4)
print(rdd.toDebugString().decode())
print("--- lineage done")

# --- spark ---
df = spark.read.parquet("trips.parquet")
per_zone = (df.filter(F.col("payment_type") == "card")
              .groupBy("pickup_zone")
              .agg(F.count("*").alias("trips"), F.round(F.avg("fare_usd"), 2).alias("avg_fare"))
              .orderBy(F.desc("trips")).limit(3))
per_zone.show()
per_zone.explain()
spark.stop()
print("--- spark done")

# --- one_machine ---
query = """
    SELECT pickup_zone, count(*) AS trips, round(avg(fare_usd), 2) AS avg_fare
    FROM 'trips.parquet' WHERE payment_type = 'card'
    GROUP BY pickup_zone ORDER BY trips DESC LIMIT 3
"""
print(duckdb.sql(query))

lazy = (pl.scan_parquet("trips.parquet")
        .filter(pl.col("payment_type") == "card")
        .group_by("pickup_zone")
        .agg(pl.len().alias("trips"), pl.col("fare_usd").mean().round(2).alias("avg_fare"))
        .sort("trips", descending=True)
        .limit(3))
print(lazy.collect())
print(lazy.explain())
print("--- one_machine done")

# --- larger_than_memory ---
con = duckdb.connect()
con.execute("SET memory_limit = '200MB'")
con.execute("SET temp_directory = 'spill'")
con.execute("""COPY (SELECT i AS trip_id, i % 3000000 AS rider_id, random() * 40 AS fare_usd
                     FROM range(40000000) t(i)) TO 'big.parquet' (FORMAT parquet)""")
print(f"big.parquet {os.path.getsize('big.parquet') / 1e6:.0f} MB on disk")
t0 = time.perf_counter()
print(con.sql("""SELECT count(*) AS riders, round(avg(spend), 2) AS avg_spend
                 FROM (SELECT rider_id, sum(fare_usd) AS spend FROM 'big.parquet' GROUP BY rider_id)"""))
print(f"group by 3,000,000 keys under a 200 MB limit: {time.perf_counter() - t0:.1f} s")
print("--- larger_than_memory done")
