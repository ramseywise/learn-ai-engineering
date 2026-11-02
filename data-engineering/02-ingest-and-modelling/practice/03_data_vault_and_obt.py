"""Code from notes/03-data-vault-and-obt.md.

Run from any folder (it writes only to a temporary directory):
    uv run --with duckdb --with pyarrow --with numpy python 03_data_vault_and_obt.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- setup ---
import os, time, duckdb, numpy as np, pyarrow as pa

def make_ops(n=1_000_000, seed=7):
    """The operational source: one row per trip, plus a zone lookup with a borough."""
    rng = np.random.default_rng(seed)
    zones = rng.zipf(1.3, n * 2)
    zones = zones[zones <= 260][:n]
    miles = np.round(rng.gamma(2.0, 1.6, n) + 0.1, 2)
    trips = pa.table({
        "trip_id": np.arange(1, n + 1),
        "pickup_at": pa.array((np.datetime64("2026-01-01") + rng.integers(0, 31 * 86400, n) * np.timedelta64(1, "s")).astype("datetime64[s]")),
        "zone_id": zones.astype("int32"),
        "payment_code": rng.choice(np.array(["CRD", "CSH", "APP", "XXX"]), n, p=[.7, .2, .0995, .0005]),
        "trip_miles": miles,
        "fare_usd": np.round(3 + miles * 2.5 + rng.normal(0, 1, n).clip(-2, 8), 2),
    })
    return trips

con = duckdb.connect()
src_trips = make_ops()
boroughs = ["Manhattan", "Queens", "Brooklyn", "Bronx", "Staten Island"]
con.execute("CREATE TABLE src_zones AS SELECT z AS zone_id, 'Zone ' || z AS zone_name, "
            "['Manhattan','Queens','Brooklyn','Bronx','Staten Island'][1 + z % 5] AS borough FROM range(1, 251) t(z)")

con.execute("""CREATE TABLE dim_zone AS SELECT zone_id AS zone_key, zone_id, zone_name, borough FROM src_zones""")
con.execute("INSERT INTO dim_zone VALUES (-1, -1, 'Unknown', 'Unknown')")
con.execute("""CREATE TABLE dim_date AS SELECT CAST(strftime(d, '%Y%m%d') AS INT) AS date_key, d::DATE AS full_date,
    dayname(d) AS day_name, isodow(d) >= 6 AS is_weekend, month(d) AS month
    FROM generate_series(DATE '2026-01-01', DATE '2026-12-31', INTERVAL 1 DAY) t(d)""")
con.execute("""CREATE TABLE fact_trips AS SELECT trip_id, CAST(strftime(pickup_at, '%Y%m%d') AS INT) AS date_key,
    coalesce(z.zone_key, -1) AS zone_key, payment_code, trip_miles, fare_usd
    FROM src_trips t LEFT JOIN dim_zone z USING (zone_id)""")
print(con.execute("SELECT count(*) FROM fact_trips").fetchall()[0])
print("--- setup done")

# --- vault_tables ---
con.execute("""
CREATE TABLE hub_zone (zone_hk UBIGINT PRIMARY KEY, zone_id INT, load_ts TIMESTAMP, record_source VARCHAR);
CREATE TABLE hub_trip (trip_hk UBIGINT PRIMARY KEY, trip_id BIGINT, load_ts TIMESTAMP, record_source VARCHAR);
CREATE TABLE link_trip_zone (link_hk UBIGINT PRIMARY KEY, trip_hk UBIGINT, zone_hk UBIGINT, load_ts TIMESTAMP, record_source VARCHAR);
CREATE TABLE sat_zone (zone_hk UBIGINT, load_ts TIMESTAMP, hash_diff UBIGINT, zone_name VARCHAR, borough VARCHAR,
                       record_source VARCHAR, PRIMARY KEY (zone_hk, load_ts));
CREATE TABLE sat_trip (trip_hk UBIGINT, load_ts TIMESTAMP, hash_diff UBIGINT, pickup_at TIMESTAMP, payment_code VARCHAR,
                       trip_miles DOUBLE, fare_usd DOUBLE, record_source VARCHAR);
""")
print("--- vault_tables done")

# --- vault_load ---
def load_vault(zones_sql, load_ts, source="ops"):
    """Insert-only. Hubs and links add unseen keys; satellites add a row when attributes change."""
    con.execute(f"""INSERT INTO hub_zone
        SELECT DISTINCT hash(zone_id), zone_id, TIMESTAMP '{load_ts}', '{source}' FROM ({zones_sql}) s
        WHERE hash(zone_id) NOT IN (SELECT zone_hk FROM hub_zone)""")
    con.execute(f"""INSERT INTO sat_zone
        WITH latest AS (SELECT zone_hk, arg_max(hash_diff, load_ts) AS hash_diff FROM sat_zone GROUP BY 1)
        SELECT hash(s.zone_id), TIMESTAMP '{load_ts}', hash(s.zone_name, s.borough), s.zone_name, s.borough, '{source}'
        FROM ({zones_sql}) s LEFT JOIN latest l ON l.zone_hk = hash(s.zone_id)
        WHERE l.hash_diff IS NULL OR l.hash_diff <> hash(s.zone_name, s.borough)""")

load_vault("SELECT * FROM src_zones", "2026-01-01 00:00:00")
con.execute(f"""INSERT INTO hub_trip SELECT hash(trip_id), trip_id, TIMESTAMP '2026-02-01', 'ops' FROM src_trips""")
con.execute(f"""INSERT INTO link_trip_zone SELECT hash(trip_id, zone_id), hash(trip_id), hash(zone_id), TIMESTAMP '2026-02-01', 'ops' FROM src_trips""")
con.execute(f"""INSERT INTO sat_trip SELECT hash(trip_id), TIMESTAMP '2026-02-01', hash(fare_usd, trip_miles), pickup_at, payment_code,
    trip_miles, fare_usd, 'ops' FROM src_trips""")

changed = "SELECT zone_id, zone_name, CASE WHEN zone_id = 6 THEN 'Brooklyn' ELSE borough END AS borough FROM src_zones"
load_vault(changed, "2026-01-15 00:00:00")
load_vault(changed, "2026-01-15 00:00:00")   # a retry adds nothing
print(con.sql("SELECT h.zone_id, s.borough, s.load_ts FROM hub_zone h JOIN sat_zone s USING (zone_hk) WHERE h.zone_id = 6 ORDER BY 3"))
print("hub, satellite rows:", con.execute("SELECT (SELECT count(*) FROM hub_zone), (SELECT count(*) FROM sat_zone)").fetchall()[0])
print("--- vault_load done")

# --- vault_query ---
vault_sql = """
WITH z AS (SELECT zone_hk, arg_max(borough, load_ts) AS borough FROM sat_zone GROUP BY 1)
SELECT z.borough, count(*) AS trips, round(sum(st.fare_usd)) AS fares
FROM hub_trip ht
JOIN sat_trip st ON st.trip_hk = ht.trip_hk
JOIN link_trip_zone l ON l.trip_hk = ht.trip_hk
JOIN z ON z.zone_hk = l.zone_hk
GROUP BY 1 ORDER BY fares DESC LIMIT 3"""
star_sql = """
SELECT CASE WHEN z.zone_id = 6 THEN 'Brooklyn' ELSE z.borough END AS borough, count(*) AS trips, round(sum(f.fare_usd)) AS fares
FROM fact_trips f JOIN dim_zone z USING (zone_key)
WHERE z.zone_key > 0
GROUP BY 1 ORDER BY fares DESC LIMIT 3"""
def best_ms(sql, n=5):
    out = []
    for _ in range(n):
        t0 = time.perf_counter(); con.execute(sql).fetchall(); out.append((time.perf_counter() - t0) * 1000)
    return min(out)
print(con.sql(vault_sql))
print(con.sql(star_sql))
print(f"vault {best_ms(vault_sql):.0f} ms over 3 joins, star {best_ms(star_sql):.0f} ms over 1 join")
print("--- vault_query done")

# --- obt_build ---
con.execute("""
CREATE TABLE obt_trips AS
SELECT f.trip_id, f.trip_miles, f.fare_usd, f.payment_code, d.full_date, d.day_name, d.is_weekend, d.month,
       z.zone_id, z.zone_name, z.borough
FROM fact_trips f JOIN dim_date d USING (date_key) JOIN dim_zone z USING (zone_key)""")
con.execute("COPY fact_trips TO 'fact.parquet' (FORMAT parquet, COMPRESSION zstd)")
con.execute("COPY dim_date TO 'dim_date.parquet' (FORMAT parquet, COMPRESSION zstd)")
con.execute("COPY dim_zone TO 'dim_zone.parquet' (FORMAT parquet, COMPRESSION zstd)")
con.execute("COPY obt_trips TO 'obt.parquet' (FORMAT parquet, COMPRESSION zstd)")
star_mb = sum(os.path.getsize(f) for f in ["fact.parquet", "dim_date.parquet", "dim_zone.parquet"]) / 1e6
print(f"star {star_mb:.1f} MB, one big table {os.path.getsize('obt.parquet') / 1e6:.1f} MB")
print("--- obt_build done")

# --- obt_query ---
q_star = """SELECT z.borough, d.is_weekend, round(sum(f.fare_usd)) FROM 'fact.parquet' f
    JOIN 'dim_zone.parquet' z USING (zone_key) JOIN 'dim_date.parquet' d USING (date_key)
    WHERE d.month = 1 AND f.payment_code = 'CRD' GROUP BY ALL"""
q_obt = """SELECT borough, is_weekend, round(sum(fare_usd)) FROM 'obt.parquet'
    WHERE month = 1 AND payment_code = 'CRD' GROUP BY ALL"""
print("same answer:", sorted(con.execute(q_star).fetchall()) == sorted(con.execute(q_obt).fetchall()))
print(f"star {best_ms(q_star):.1f} ms, one big table {best_ms(q_obt):.1f} ms")
print("--- obt_query done")

# --- obt_restate ---
t0 = time.perf_counter()
con.execute("UPDATE dim_zone SET borough = 'Brooklyn' WHERE zone_id = 6")
star_ms = (time.perf_counter() - t0) * 1000
t0 = time.perf_counter()
n = con.execute("UPDATE obt_trips SET borough = 'Brooklyn' WHERE zone_id = 6").fetchall()[0][0]
obt_ms = (time.perf_counter() - t0) * 1000
print(f"star: 1 row, {star_ms:.1f} ms. One big table: {n} rows, {obt_ms:.1f} ms")
print("and a file on the lake has to be rewritten whole:")
t0 = time.perf_counter()
con.execute("""COPY (SELECT * REPLACE (CASE WHEN zone_id = 6 THEN 'Brooklyn' ELSE borough END AS borough)
    FROM 'obt.parquet') TO 'obt2.parquet' (FORMAT parquet, COMPRESSION zstd)""")
print(f"rewrite of obt.parquet {(time.perf_counter() - t0) * 1000:.0f} ms")
print("--- obt_restate done")
