"""Code from notes/02-row-and-column-stores.md.

Run from any folder (it writes only to a temporary directory):
    uv run --with duckdb --with pyarrow --with numpy python 02_row_and_column_stores.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- setup ---
import os, sqlite3, time, numpy as np, pyarrow as pa, duckdb

def make_trips(n=1_000_000, seed=7):
    """One synthetic month of taxi trips, sorted by pickup time like an append-only log."""
    rng = np.random.default_rng(seed)
    start = np.datetime64("2026-01-01T00:00:00", "s")
    seconds = np.sort(rng.integers(0, 31 * 86_400, n))
    # 260 zones with a heavy tail: a few busy zones take most pickups.
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

def best_ms(fn, repeats=5):
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter(); fn(); times.append((time.perf_counter() - t0) * 1000)
    return min(times)

trips = make_trips()

# The same rows in a row store (SQLite) and a column store (DuckDB), both on disk.
lite = sqlite3.connect("trips.sqlite")
lite.execute("""CREATE TABLE trips (trip_id INTEGER PRIMARY KEY, pickup_at TEXT, pickup_zone INT,
                payment_type TEXT, passengers INT, trip_miles REAL, fare_usd REAL)""")
lite.executemany("INSERT INTO trips VALUES (?,?,?,?,?,?,?)",
                 ((r[0], str(r[1]), *r[2:]) for r in zip(*[c.to_pylist() for c in trips.columns])))
lite.commit()
duck = duckdb.connect("trips.duckdb")
duck.execute("CREATE TABLE trips AS SELECT * FROM trips")
duck.execute("CHECKPOINT")
print(f"SQLite file {os.path.getsize('trips.sqlite')/1e6:.1f} MB, DuckDB file {os.path.getsize('trips.duckdb')/1e6:.1f} MB")
print("--- setup done")

# --- two_workloads ---
scan = "SELECT pickup_zone, sum(fare_usd) FROM trips GROUP BY pickup_zone"
point = "SELECT * FROM trips WHERE trip_id = 123456"

print(f"{'':28s}{'SQLite':>11s}{'DuckDB':>11s}")
print(f"{'analytic scan (ms)':28s}{best_ms(lambda: lite.execute(scan).fetchall()):11.2f}"
      f"{best_ms(lambda: duck.execute(scan).fetchall()):11.2f}")
print(f"{'point lookup by key (ms)':28s}{best_ms(lambda: lite.execute(point).fetchall()):11.3f}"
      f"{best_ms(lambda: duck.execute(point).fetchall()):11.3f}")
print("--- two_workloads done")

# --- layout ---
n = 1_000_000
rows = np.zeros(n, dtype=[("id", "i8"), ("at", "i8"), ("zone", "i4"), ("pay", "i4"),
                          ("pax", "i4"), ("miles", "f8"), ("fare", "f8"), ("pad", "S84")])
rows["fare"] = trips["fare_usd"].to_numpy()
fare_column = trips["fare_usd"].to_numpy().copy()

print("bytes per row in the row layout:", rows.dtype.itemsize)
print(f"sum over row layout:    {best_ms(lambda: rows['fare'].sum()):6.2f} ms")
print(f"sum over column layout: {best_ms(lambda: fare_column.sum()):6.2f} ms")
print(f"python loop, one value at a time: {best_ms(lambda: sum(fare_column[:100_000].tolist()), 3) * 10:6.2f} ms (scaled from 100k)")
print("--- layout done")

# --- rle ---
def run_length(values):
    """(value, count) pairs: the encoding a sorted column collapses into."""
    change = np.flatnonzero(values[1:] != values[:-1]) + 1
    starts = np.r_[0, change]
    return values[starts], np.diff(np.r_[starts, len(values)])

zone = trips["pickup_zone"].to_numpy()
print("arrival order:", len(run_length(zone)[0]), "runs")
print("sorted:       ", len(run_length(np.sort(zone))[0]), "runs")
print("--- rle done")

# --- bitmap ---
pay = np.array(trips["payment_type"].to_pylist())
pax = trips["passengers"].to_numpy()
is_cash, is_app = pay == "cash", pay == "app"
is_group = pax >= 3

packed = np.packbits(is_cash)
print("bitmap for payment_type='cash':", packed.nbytes, "bytes,", int(is_cash.sum()), "rows set")
print("(cash OR app) AND passengers>=3:", int(((is_cash | is_app) & is_group).sum()), "rows")
check = duck.execute("SELECT count(*) FROM trips WHERE payment_type IN ('cash','app') AND passengers >= 3").fetchone()[0]
print("same predicate in SQL:          ", check, "rows")
print("--- bitmap done")

# --- index_vs_scan ---
lite.execute("CREATE INDEX idx_zone ON trips(pickup_zone)")
rare, common = "SELECT sum(fare_usd) FROM trips WHERE pickup_zone = 250", "SELECT sum(fare_usd) FROM trips WHERE pickup_zone = 1"
for label, q in [("rare zone", rare), ("busiest zone", common)]:
    print(f"{label:13s} SQLite with index {best_ms(lambda: lite.execute(q).fetchall()):8.2f} ms   "
          f"DuckDB scan {best_ms(lambda: duck.execute(q).fetchall()):6.2f} ms   "
          f"rows {lite.execute(q.replace('sum(fare_usd)', 'count(*)')).fetchone()[0]}")
print(lite.execute("EXPLAIN QUERY PLAN " + rare).fetchall()[0][-1])
print("--- index_vs_scan done")

# --- explain ---
plan = duck.execute("EXPLAIN SELECT pickup_zone, sum(fare_usd) FROM trips WHERE pickup_zone < 5 GROUP BY pickup_zone").fetchall()[0][1]
print(plan)
print("--- explain done")

# --- cube ---
print(duck.sql("""
    SELECT date_trunc('week', pickup_at)::DATE AS week, payment_type, sum(fare_usd)::INT AS fares
    FROM trips WHERE pickup_at < DATE '2026-01-12'
    GROUP BY CUBE (week, payment_type)
    ORDER BY week NULLS LAST, payment_type NULLS LAST
"""))
print("--- cube done")

# --- matview ---
duck.execute("""CREATE OR REPLACE TABLE daily_zone AS
    SELECT pickup_at::DATE AS day, pickup_zone, count(*) AS trips, sum(fare_usd) AS fares
    FROM trips GROUP BY ALL""")
from_raw = "SELECT sum(fares) FROM (SELECT sum(fare_usd) fares FROM trips WHERE pickup_zone = 1 GROUP BY pickup_at::DATE)"
from_rollup = "SELECT sum(fares) FROM daily_zone WHERE pickup_zone = 1"
print(f"rollup rows: {duck.execute('SELECT count(*) FROM daily_zone').fetchone()[0]}")
print(f"raw {best_ms(lambda: duck.execute(from_raw).fetchall()):.2f} ms, rollup {best_ms(lambda: duck.execute(from_rollup).fetchall()):.2f} ms")
print("but share of fare from trips over 10 miles is not answerable: trip_miles is not a rollup column")
print("--- matview done")

# --- single_writes ---
def insert_loop(execute, commit, n=2_000, first=2_000_000):
    t0 = time.perf_counter()
    for i in range(first, first + n):
        execute("INSERT INTO trips VALUES (?, '2026-02-01 00:00:00', 1, 'card', 1, 1.0, 5.0)", (i,))
        commit()
    return (time.perf_counter() - t0) / n * 1000

print(f"SQLite one row per transaction: {insert_loop(lite.execute, lite.commit):6.3f} ms per row")
print(f"DuckDB one row per transaction: {insert_loop(duck.execute, lambda: None):6.3f} ms per row")
print("--- single_writes done")
