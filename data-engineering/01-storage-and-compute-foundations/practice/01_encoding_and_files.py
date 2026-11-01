"""Code from notes/01-encoding-and-files.md.

Run from any folder (it writes only to a temporary directory):
    uv run --with duckdb --with pyarrow --with numpy --with polars --with fastavro python 01_encoding_and_files.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- make_trips ---
import numpy as np, pyarrow as pa

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

trips = make_trips()
print(trips.schema)
print(trips.num_rows, "rows,", round(trips.nbytes / 1e6, 1), "MB in Arrow memory")
print("--- make_trips done")

# --- sizes ---
import os, pyarrow.csv as pcsv, pyarrow.parquet as pq, pyarrow.json, gzip, shutil, time

pcsv.write_csv(trips, "trips.csv")
with open("trips.csv", "rb") as src, gzip.open("trips.csv.gz", "wb") as dst:
    shutil.copyfileobj(src, dst)
pq.write_table(trips, "trips_snappy.parquet", compression="snappy")
pq.write_table(trips, "trips_zstd.parquet", compression="zstd")

for path in ["trips.csv", "trips.csv.gz", "trips_snappy.parquet", "trips_zstd.parquet"]:
    print(f"{path:24s} {os.path.getsize(path) / 1e6:7.1f} MB")
print("--- sizes done")

# --- csv_traps ---
import io, pyarrow.csv as pcsv

raw = b'zip,amount,note\n02134,12,"plain"\n10001,007,"has, a comma"\n'
table = pcsv.read_csv(io.BytesIO(raw))
print(table.schema)
print(table.to_pylist())

# Same bytes, with the schema stated rather than guessed.
typed = pcsv.read_csv(io.BytesIO(raw), convert_options=pcsv.ConvertOptions(
    column_types={"zip": pa.string(), "amount": pa.string()}))
print(typed.to_pylist())

# A JSON number read as a double cannot hold every 64-bit id.
tweet_id = 2**53 + 1
print(tweet_id, "->", int(float(tweet_id)))
print("--- csv_traps done")

# --- encodings_compared ---
import json, fastavro

schema_v1 = {"type": "record", "name": "Person", "fields": [
    {"name": "userName", "type": "string"},
    {"name": "favoriteNumber", "type": ["null", "long"], "default": None},
    {"name": "interests", "type": {"type": "array", "items": "string"}},
]}
person = {"userName": "Martin", "favoriteNumber": 1337, "interests": ["daydreaming", "hacking"]}

as_json = json.dumps(person, separators=(",", ":")).encode()
buf = io.BytesIO()
fastavro.schemaless_writer(buf, fastavro.parse_schema(schema_v1), person)
print("JSON bytes:", len(as_json))
print("Avro bytes:", len(buf.getvalue()))
print(buf.getvalue())
print("--- encodings_compared done")

# --- avro_evolution ---
# The reader knows a newer schema: one added field with a default, one removed.
schema_v2 = {"type": "record", "name": "Person", "fields": [
    {"name": "userName", "type": "string"},
    {"name": "interests", "type": {"type": "array", "items": "string"}},
    {"name": "city", "type": "string", "default": "unknown"},
]}
buf.seek(0)
print(fastavro.schemaless_reader(buf, fastavro.parse_schema(schema_v1), fastavro.parse_schema(schema_v2)))

# A field with no default cannot be resolved against old data.
schema_bad = {"type": "record", "name": "Person", "fields": [
    {"name": "userName", "type": "string"},
    {"name": "city", "type": "string"},
]}
buf.seek(0)
try:
    fastavro.schemaless_reader(buf, fastavro.parse_schema(schema_v1), fastavro.parse_schema(schema_bad))
except Exception as exc:
    print(type(exc).__name__, "-", exc)
print("--- avro_evolution done")

# --- parquet_anatomy ---
meta = pq.ParquetFile("trips_zstd.parquet").metadata
print("rows", meta.num_rows, "| row groups", meta.num_row_groups, "| columns", meta.num_columns,
      "| footer bytes", meta.serialized_size)
rg = meta.row_group(0)
print("row group 0:", rg.num_rows, "rows,", round(rg.total_byte_size / 1e6, 1), "MB uncompressed")
for i in range(rg.num_columns):
    c = rg.column(i)
    st = c.statistics
    print(f"{c.path_in_schema:13s} {c.total_compressed_size / 1e6:6.2f} MB "
          f"ratio {c.total_uncompressed_size / c.total_compressed_size:5.1f}  "
          f"min {st.min!s:.19} max {st.max!s:.19}  {sorted(set(c.encodings))}")
print("--- parquet_anatomy done")

# --- pruning ---
pq.write_table(trips, "small_groups.parquet", row_group_size=50_000, compression="zstd")

def groups_touching(path, column, lo, hi):
    pf = pq.ParquetFile(path)
    idx = pf.schema_arrow.get_field_index(column)
    return sum(
        1 for g in range(pf.num_row_groups)
        if pf.metadata.row_group(g).column(idx).statistics.max >= lo
        and pf.metadata.row_group(g).column(idx).statistics.min <= hi
    ), pf.num_row_groups

print("trip_id 500000..500010 ->", groups_touching("small_groups.parquet", "trip_id", 500_000, 500_010))
print("fare 40..41            ->", groups_touching("small_groups.parquet", "fare_usd", 40, 41))

def best_ms(fn, repeats=5):
    """Best of a few runs, because a shared laptop is a noisy lab."""
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter(); fn(); times.append((time.perf_counter() - t0) * 1000)
    return min(times)

print(f"read all 7 columns:  {best_ms(lambda: pq.read_table('small_groups.parquet')):6.1f} ms")
print(f"read fare_usd only:  {best_ms(lambda: pq.read_table('small_groups.parquet', columns=['fare_usd'])):6.1f} ms")
print("--- pruning done")

# --- sort_effect ---
by_zone = trips.sort_by([("pickup_zone", "ascending"), ("payment_type", "ascending")])
pq.write_table(by_zone, "sorted_zone.parquet", compression="zstd")
for path in ["trips_zstd.parquet", "sorted_zone.parquet"]:
    m = pq.ParquetFile(path).metadata
    idx = pq.ParquetFile(path).schema_arrow.names
    sizes = {idx[i]: sum(m.row_group(g).column(i).total_compressed_size for g in range(m.num_row_groups))
             for i in range(m.num_columns)}
    print(f"{path:22s} total {os.path.getsize(path)/1e6:5.1f} MB  "
          f"pickup_zone {sizes['pickup_zone']/1e3:7.1f} KB  payment_type {sizes['payment_type']/1e3:7.1f} KB  "
          f"pickup_at {sizes['pickup_at']/1e3:8.1f} KB")
print("--- sort_effect done")

# --- arrow_memory ---
import pyarrow.ipc as ipc, pyarrow.compute as pc

fares = trips["fare_usd"].combine_chunks()
validity, values = fares.buffers()
print("fare_usd:", fares.type, "| validity buffer:", validity, "| values buffer bytes:", values.size)

as_numpy = fares.to_numpy(zero_copy_only=True)
print("numpy shares Arrow's memory:", as_numpy.ctypes.data == values.address)

with ipc.new_file("trips.arrow", trips.schema) as w:
    w.write_table(trips)
def from_arrow_file():
    return ipc.open_file(pa.memory_map("trips.arrow")).read_all()

print(f"trips.arrow        {os.path.getsize('trips.arrow')/1e6:5.1f} MB, open all columns: {best_ms(from_arrow_file):7.2f} ms")
print(f"trips_zstd.parquet {os.path.getsize('trips_zstd.parquet')/1e6:5.1f} MB, open all columns: "
      f"{best_ms(lambda: pq.read_table('trips_zstd.parquet')):7.2f} ms")
print("--- arrow_memory done")

# --- arrow_interchange ---
import duckdb, polars as pl

con = duckdb.connect()

# DuckDB scans the Arrow table from the Python variable name, no export step.
top = con.sql("""
    SELECT pickup_zone, count(*) AS trips, round(avg(fare_usd), 2) AS avg_fare
    FROM trips GROUP BY pickup_zone ORDER BY trips DESC LIMIT 3
""").to_arrow_table()
print(type(top).__name__, top.to_pylist()[0])
# Polars wraps the same columnar layout.
print(pl.from_arrow(top))
print("--- arrow_interchange done")

# --- parquet_evolution ---
jan = pa.table({"trip_id": [1, 2], "fare_usd": [12.5, 9.0]})
feb = pa.table({"trip_id": [3], "fare_usd": [20.0], "tip_usd": [4.0]})
pq.write_table(jan, "jan.parquet"); pq.write_table(feb, "feb.parquet")

print(con.sql("SELECT * FROM read_parquet(['jan.parquet','feb.parquet'], union_by_name=true) ORDER BY trip_id"))
# Without union_by_name the schema of the first file wins, and tip_usd disappears without an error.
print(con.sql("SELECT * FROM read_parquet(['jan.parquet','feb.parquet'])").columns)
print("--- parquet_evolution done")
