"""Code from notes/10-choosing-a-store.md: measure the access patterns that decide which store fits.

Run from any folder (it writes only to temporary directories):
    uv run --no-project --python 3.12 --with duckdb --with numpy --with pgserver --with 'psycopg[binary]' python 10_choosing_a_store.py

Starts a private Postgres in a temporary directory. Timings depend on the machine; compare within a table.
"""
import os, sys, tempfile
os.chdir(tempfile.mkdtemp())

# --- embedded ---
import sqlite3, time, random
import duckdb, numpy as np

N = 2_000_000
rng = np.random.default_rng(10)
ids = np.arange(N)
zones = rng.integers(0, 265, N)
fares = rng.gamma(2.0, 8.0, N).round(2)

lite = sqlite3.connect("trips.sqlite")
lite.execute("CREATE TABLE trips (id INTEGER PRIMARY KEY, zone INT, fare REAL)")
lite.executemany("INSERT INTO trips VALUES (?,?,?)", zip(ids.tolist(), zones.tolist(), fares.tolist()))
lite.commit()

duck = duckdb.connect("trips.duckdb")
duck.execute("CREATE TABLE trips (id BIGINT PRIMARY KEY, zone INT, fare DOUBLE)")
duck.register("src", {"id": ids, "zone": zones, "fare": fares})
duck.execute("INSERT INTO trips SELECT * FROM src")

def timed(run, repeat):
    t = time.perf_counter()
    for _ in range(repeat):
        run()
    return (time.perf_counter() - t) / repeat * 1000

random.seed(1)
POINT = "SELECT fare FROM trips WHERE id = ?"
SCAN = "SELECT zone, avg(fare) FROM trips GROUP BY zone ORDER BY 2 DESC LIMIT 3"
print(f"{N:,} rows                       SQLite ms    DuckDB ms")
print(f"point lookup by primary key {timed(lambda: lite.execute(POINT, (random.randrange(N),)).fetchone(), 2000):11.4f} "
      f"{timed(lambda: duck.execute(POINT, (random.randrange(N),)).fetchone(), 2000):12.4f}")
print(f"group-by over every row     {timed(lambda: lite.execute(SCAN).fetchall(), 3):11.1f} "
      f"{timed(lambda: duck.execute(SCAN).fetchall(), 3):12.1f}")

# --- pg_setup ---
import subprocess, pgserver, psycopg

BIN = os.path.join(os.path.dirname(pgserver.__file__), "pginstall", "bin")
ROOT = tempfile.mkdtemp(dir="/tmp", prefix="pg")
subprocess.run([f"{BIN}/initdb", "-D", f"{ROOT}/d", "-U", "postgres", "--auth=trust", "-E", "UTF8"], check=True, capture_output=True)
with open(f"{ROOT}/d/postgresql.conf", "a") as f:
    f.write(f"listen_addresses=''\nunix_socket_directories='{ROOT}'\nport=5630\n")
subprocess.run([f"{BIN}/pg_ctl", "-w", "-D", f"{ROOT}/d", "-l", f"{ROOT}/log", "start"], check=True, capture_output=True)
pg = psycopg.connect(f"host={ROOT} port=5630 user=postgres dbname=postgres", autocommit=True)

def explain_top(sql, *params):
    plan = pg.execute("EXPLAIN (ANALYZE, TIMING OFF) " + sql, params).fetchall()
    scan = next(r[0].strip("-> ").split("  ")[0] for r in plan if "Scan" in r[0])
    runtime = [r[0] for r in plan if r[0].startswith("Execution Time")][0].split(": ")[1]
    return f"{scan[:42]:42s} {runtime}"

# --- pg_kv ---
pg.execute("CREATE TABLE kv (k text PRIMARY KEY, v jsonb)")
pg.execute("""INSERT INTO kv SELECT 'session:' || g, jsonb_build_object('user', g, 'cart', g % 7)
              FROM generate_series(1, 1000000) g""")
def rate(run, seconds=2):
    n, end = 0, time.perf_counter() + seconds
    while time.perf_counter() < end:
        run(); n += 1
    return n / seconds
print(f"reads per second, one client, over a Unix socket: "
      f"{rate(lambda: pg.execute('SELECT v FROM kv WHERE k = %s', (f'session:{random.randrange(1, 10**6)}',)).fetchone()):,.0f}")
print(f"upserts per second, one client, durable commit:   "
      f"{rate(lambda: pg.execute('INSERT INTO kv VALUES (%s, %s) ON CONFLICT (k) DO UPDATE SET v = excluded.v', (f'session:{random.randrange(1, 10**6)}', '{}'))):,.0f}")

# --- pg_document ---
pg.execute("CREATE TABLE product (id serial PRIMARY KEY, doc jsonb)")
pg.execute("""INSERT INTO product (doc)
    SELECT CASE WHEN g % 2 = 0
        THEN jsonb_build_object('kind', 'shoe', 'size', g % 15, 'color', (ARRAY['red','blue','green'])[g % 3 + 1])
        ELSE jsonb_build_object('kind', 'book', 'pages', g % 900, 'author', 'author' || g % 5000) END
    FROM generate_series(1, 1000000) g""")
Q = "SELECT count(*) FROM product WHERE doc @> %s"
print("no index  ", explain_top(Q, '{"author": "author42"}'))
pg.execute("CREATE INDEX ON product USING gin (doc jsonb_path_ops)")
pg.execute("ANALYZE product")
print("GIN index ", explain_top(Q, '{"author": "author42"}'))

# --- pg_search ---
WORDS = ("trip fare driver taxi route satisfy satisfies satisfied refund airport tip late meter zone "
         "payment rider complaint cancelled surge receipt").split()
docs = [" ".join(random.choices(WORDS, k=12)) for _ in range(300_000)]
pg.execute("CREATE TABLE ticket (id serial PRIMARY KEY, body text, tsv tsvector)")
with pg.cursor() as cur, cur.copy("COPY ticket (body) FROM STDIN") as copy:
    for d in docs:
        copy.write_row((d,))
pg.execute("UPDATE ticket SET tsv = to_tsvector('english', body)")
pg.execute("CREATE INDEX ON ticket USING gin (tsv)")
pg.execute("ANALYZE ticket")
print("LIKE 'satisfied'     matches", pg.execute("SELECT count(*) FROM ticket WHERE body LIKE '%satisfied%'").fetchone()[0])
print("tsquery 'satisfied'  matches", pg.execute(
    "SELECT count(*) FROM ticket WHERE tsv @@ to_tsquery('english', 'satisfied')").fetchone()[0], "(stems to 'satisfi')")
print("top result:", pg.execute("""SELECT body FROM ticket, to_tsquery('english', 'refund & surge') q
    WHERE tsv @@ q ORDER BY ts_rank(tsv, q) DESC LIMIT 1""").fetchone()[0][:60])

# --- pg_timeseries ---
pg.execute("CREATE TABLE metric (ts timestamptz NOT NULL, value float8) PARTITION BY RANGE (ts)")
for m in range(1, 13):
    pg.execute(f"""CREATE TABLE metric_{m:02d} PARTITION OF metric
        FOR VALUES FROM ('2026-{m:02d}-01') TO ('{"2027-01-01" if m == 12 else f"2026-{m + 1:02d}-01"}')""")
pg.execute("""INSERT INTO metric SELECT '2026-01-01'::timestamptz + (g * interval '10 seconds'), random()
              FROM generate_series(0, 3100000) g""")
pg.execute("ANALYZE metric")
rows = pg.execute("EXPLAIN SELECT avg(value) FROM metric WHERE ts >= '2026-03-01' AND ts < '2026-03-08'").fetchall()
print("partitions the plan reads for one week:", sum("Scan on metric_" in r[0] for r in rows))
t = time.perf_counter()
print("DELETE one month:", pg.execute("DELETE FROM metric WHERE ts < '2026-02-01'").rowcount, "rows", end=" ")
print(f"in {(time.perf_counter() - t) * 1000:,.0f} ms")
t = time.perf_counter()
pg.execute("DROP TABLE metric_02")
print(f"DROP one partition (a month of similar size) in {(time.perf_counter() - t) * 1000:,.1f} ms")

# --- pg_graph ---
pg.execute("CREATE TABLE edge (src int, dst int)")
edges = rng.integers(0, 100_000, (500_000, 2))
with pg.cursor() as cur, cur.copy("COPY edge FROM STDIN") as copy:
    for s, d in edges.tolist():
        copy.write_row((s, d))
pg.execute("CREATE INDEX ON edge (src)")
pg.execute("ANALYZE edge")
HOPS = """WITH RECURSIVE walk(node, depth) AS (
    SELECT %s::int, 0
  UNION
    SELECT e.dst, w.depth + 1 FROM walk w JOIN edge e ON e.src = w.node WHERE w.depth < %s
) SELECT count(DISTINCT node) FROM walk"""
print("hops  nodes reached     ms    (100,000 nodes, 500,000 edges)")
for hops in [1, 2, 3, 4, 5, 6]:
    t = time.perf_counter()
    reached = pg.execute(HOPS, (7, hops)).fetchone()[0]
    print(f"{hops:4d} {reached:14,d} {(time.perf_counter() - t) * 1000:6,.0f}")

# --- vectors_flat ---
dim = 384
print(f"exact nearest neighbours by brute force, {dim} dimensions, numpy")
for count in [10_000, 100_000, 1_000_000]:
    corpus = rng.standard_normal((count, dim), dtype=np.float32)
    corpus /= np.linalg.norm(corpus, axis=1, keepdims=True)
    query = corpus[3]
    t = time.perf_counter()
    for _ in range(5):
        np.argpartition(corpus @ query, -10)[-10:]
    print(f"{count:10,d} vectors {corpus.nbytes / 1e9:5.2f} GB  {(time.perf_counter() - t) / 5 * 1000:7.1f} ms per query")

# --- cleanup ---
pg.close()
subprocess.run([f"{BIN}/pg_ctl", "-w", "-D", f"{ROOT}/d", "-m", "fast", "stop"], capture_output=True)
