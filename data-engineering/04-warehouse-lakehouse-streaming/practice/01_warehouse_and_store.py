"""Code from notes/01-warehouse-and-store.md: layout, shared storage, distribution and billing arithmetic.

Run from any folder (it writes only to a temporary directory):
    uv run --no-project --python 3.12 --with duckdb --with pyarrow --with numpy python 01_warehouse_and_store.py

BigQuery, Snowflake, Redshift, ClickHouse and Spark are not needed and are not run here.
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- rowcol ---
import duckdb, pyarrow as pa, pyarrow.parquet as pq, numpy as np, os, glob
rng = np.random.default_rng(7)
n = 3_000_000
start = np.datetime64('2024-01-01T00:00:00')
secs = rng.integers(0, 366 * 86400, n)                       # one leap year of pickups
trips = pa.table({
    'pickup': pa.array(start + secs.astype('timedelta64[s]')),
    'vendor_id': pa.array(rng.choice([1, 2], n, p=[.3, .7]).astype('int32')),
    'pu_zone': pa.array(rng.integers(1, 266, n).astype('int32')),
    'do_zone': pa.array(rng.integers(1, 266, n).astype('int32')),
    'distance': pa.array(np.round(rng.exponential(3.0, n), 2)),
    'fare': pa.array(np.round(3 + rng.exponential(14.0, n), 2)),
    'total': pa.array(np.round(4 + rng.exponential(19.0, n), 2)),
    'note': pa.array(rng.integers(0, 2**62, n).astype(str)),  # a wide column nobody queries
})
os.makedirs('lake', exist_ok=True)
pq.write_table(trips, 'lake/flat.parquet', row_group_size=100_000)
print(f"{n:,} rows, {os.path.getsize('lake/flat.parquet') / 1e6:.0f} MB on disk")

# --- column_bytes ---
def column_bytes(paths):
    """Compressed bytes per column, summed from Parquet footers. No data is read."""
    out = {}
    for path in paths:
        md = pq.ParquetFile(path).metadata
        for rg in range(md.num_row_groups):
            for c in range(md.num_columns):
                col = md.row_group(rg).column(c)
                out[col.path_in_schema] = out.get(col.path_in_schema, 0) + col.total_compressed_size
    return out

sizes = column_bytes(['lake/flat.parquet'])
total = sum(sizes.values())
for name, b in sorted(sizes.items(), key=lambda kv: -kv[1]):
    print(f"{name:10s} {b / 1e6:7.1f} MB  {b / total:5.1%}")
q = sizes['pickup'] + sizes['total']
print(f"SELECT *               reads {total / 1e6:6.1f} MB")
print(f"SELECT pickup, total   reads {q / 1e6:6.1f} MB  ({total / q:.1f}x less)")

# --- by_day ---
con = duckdb.connect()
con.execute("""
  COPY (SELECT *, CAST(pickup AS DATE) AS pickup_date FROM 'lake/flat.parquet')
  TO 'lake/by_day' (FORMAT parquet, PARTITION_BY (pickup_date), OVERWRITE_OR_IGNORE)
""")
days = sorted(glob.glob('lake/by_day/pickup_date=*'))
june = [d for d in days if '=2024-06' in d]
files = lambda dirs: [f for d in dirs for f in glob.glob(d + '/*.parquet')]
all_b, june_b = column_bytes(files(days)), column_bytes(files(june))
print(f"{len(days)} day partitions; June is {len(june)} of them")
print(f"vendor_id bytes, whole year : {all_b['vendor_id'] / 1e3:8.0f} KB")
print(f"vendor_id bytes, June only  : {june_b['vendor_id'] / 1e3:8.0f} KB "
      f"({all_b['vendor_id'] / june_b['vendor_id']:.1f}x less)")
print(con.sql("""
  SELECT DISTINCT vendor_id FROM read_parquet('lake/by_day/*/*.parquet', hive_partitioning = true)
  WHERE pickup_date BETWEEN '2024-06-01' AND '2024-06-30' ORDER BY 1
""").fetchall())

# --- cluster ---
def skipped(path, column, value):
    """How many row groups can min/max statistics rule out for column = value?"""
    md = pq.ParquetFile(path).metadata
    idx = md.schema.names.index(column)
    hit = sum(md.row_group(i).column(idx).statistics.min <= value <= md.row_group(i).column(idx).statistics.max
              for i in range(md.num_row_groups))
    return md.num_row_groups - hit, md.num_row_groups

con.execute("COPY (SELECT * FROM 'lake/flat.parquet') TO 'lake/unsorted.parquet' (FORMAT parquet, ROW_GROUP_SIZE 100000)")
con.execute("COPY (SELECT * FROM 'lake/flat.parquet' ORDER BY pu_zone) TO 'lake/sorted.parquet' (FORMAT parquet, ROW_GROUP_SIZE 100000)")
for f in ['unsorted', 'sorted']:
    s, t = skipped(f'lake/{f}.parquet', 'pu_zone', 132)
    print(f"{f:9s} pu_zone = 132: can skip {s:2d} of {t} row groups")

# --- shared_storage ---
import subprocess, sys, time
READER = """
import duckdb, sys, time
t = time.perf_counter()
n, s = duckdb.sql(sys.argv[1]).fetchall()[0]
print(f"{n:,} rows, {s:,.0f} total, {time.perf_counter() - t:.2f} s")
"""
JOBS = {"dashboard": "SELECT count(*), sum(total) FROM 'lake/flat.parquet' WHERE pu_zone = 132",
        "finance":   "SELECT count(*), sum(fare) FROM 'lake/flat.parquet'",
        "ml export": "SELECT count(*), sum(distance) FROM 'lake/flat.parquet' WHERE vendor_id = 2"}
procs = {name: subprocess.Popen([sys.executable, "-c", READER, sql], stdout=subprocess.PIPE, text=True)
         for name, sql in JOBS.items()}                    # three separate engines, started together
for name, p in procs.items():
    print(f"{name:10s} {p.communicate()[0].strip()}")

# --- dist_style ---
# Arithmetic on keys, not a Redshift run: where rows sit in a four-node cluster for a fact-dimension join.
fact_zone = rng.integers(1, 266, 1_000_000)                    # one million trips, joined on pickup zone
fact_vendor = rng.choice([1, 2], 1_000_000, p=[.3, .7])
fact_even = np.arange(1_000_000) % 4                           # DISTSTYLE EVEN: round robin
fact_key = fact_zone % 4                                       # DISTKEY (pu_zone): same value, same node
print("rows moved to run the join:")
print(f"  EVEN fact, EVEN dimension  {(fact_even != fact_key).sum():>9,d} fact rows are redistributed by key")
print(f"  KEY on the join column     {(fact_key != fact_zone % 4).sum():>9,d}")
print(f"  EVEN fact, ALL dimension   {0:>9,d} but 265 x 4 = {265 * 4:,} dimension rows stored")
for label, placed in [("DISTKEY (pu_zone)", fact_zone % 4), ("DISTKEY (vendor_id)", fact_vendor % 4)]:
    print(f"{label:20s} rows per node {np.bincount(placed, minlength=4).tolist()}")

# --- billing ---
TIB, GIB = 2**40, 2**30
on_demand = 6.25                                               # USD per TiB, BigQuery on-demand list price
def query_cost(gb):
    return gb * GIB / TIB * on_demand
print("BigQuery on-demand, per query at 1,000 runs a month")
for label, gb in [("unpartitioned", 1.6), ("partitioned", 0.106)]:
    print(f"  {label:14s} {gb:6.3f} GiB  ${query_cost(gb):.5f} per run  ${query_cost(gb) * 1000:6.2f} per month")

def credits(size_per_hour, seconds, starts):
    """Snowflake: per-second billing with a 60-second minimum each time the warehouse starts."""
    return size_per_hour / 3600 * sum(max(seconds / starts, 60) for _ in range(starts))
print("Snowflake Gen1 Small (2 credits an hour), 100 one-second queries a day")
print(f"  each wakes the warehouse:   {credits(2, 100, 100):5.2f} credits a day")
print(f"  batched in one session:     {credits(2, 100, 1):5.2f} credits a day")

# --- portable_mart ---
print(con.sql("""
  SELECT pu_zone AS revenue_zone, date_trunc('month', pickup) AS revenue_month,
         round(sum(total), 2) AS revenue, round(avg(distance), 2) AS avg_distance
  FROM 'lake/flat.parquet'
  GROUP BY 1, 2 ORDER BY revenue DESC LIMIT 3
"""))

# --- shuffle ---
# What a groupBy pays for: count the rows that must cross the network in a four-executor cluster.
rows = 1_000_000
keys = rng.integers(0, 265, rows)                              # 265 pickup zones
home = rng.integers(0, 4, rows)                                # the executor each row starts on
dest = keys % 4                                                # the executor that owns its key after a hash shuffle
print(f"Without partial aggregation: {(home != dest).sum():,} rows cross the network")
pairs = len(set(zip(home.tolist(), keys.tolist())))            # one partial sum per (executor, key)
moved = sum(1 for h, k in set(zip(home.tolist(), keys.tolist())) if h != k % 4)
print(f"With partial aggregation   : {moved:,} partial sums cross the network (of {pairs:,})")
