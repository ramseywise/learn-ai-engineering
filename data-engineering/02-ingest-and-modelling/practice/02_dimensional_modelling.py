"""Code from notes/02-dimensional-modelling.md and notes/02b-dimensional-modelling-history-and-conformed-dimensions.md.

Run from any folder (it writes only to a temporary directory):
    uv run --with duckdb --with pyarrow --with numpy python 02_dimensional_modelling.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- setup ---
import duckdb, numpy as np, pyarrow as pa

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
print(con.execute("SELECT count(*), count(DISTINCT zone_id), max(zone_id) FROM src_trips").fetchall()[0])
print("zones in lookup:", con.execute("SELECT count(*) FROM src_zones").fetchall()[0][0])
print("--- setup done")

# --- dims ---
con.execute("""
CREATE TABLE dim_date AS
SELECT CAST(strftime(d, '%Y%m%d') AS INT) AS date_key, d::DATE AS full_date,
       year(d) AS year, month(d) AS month, dayname(d) AS day_name,
       isodow(d) >= 6 AS is_weekend
FROM generate_series(DATE '2025-01-01', DATE '2027-12-31', INTERVAL 1 DAY) t(d)""")

con.execute("CREATE SEQUENCE zone_sk START 1")
con.execute("""
CREATE TABLE dim_zone AS
SELECT nextval('zone_sk') AS zone_key, zone_id, zone_name, borough FROM src_zones ORDER BY zone_id""")
con.execute("INSERT INTO dim_zone VALUES (-1, -1, 'Unknown', 'Unknown')")   # orphans point here

con.execute("""
CREATE TABLE dim_payment AS
SELECT row_number() OVER (ORDER BY code) AS payment_key, code AS payment_code, label
FROM (VALUES ('CRD','Card'), ('CSH','Cash'), ('APP','App')) t(code, label)""")
con.execute("INSERT INTO dim_payment VALUES (-1, 'XXX', 'Unknown')")

con.execute("""
CREATE TABLE fact_trips AS
SELECT t.trip_id,                       -- degenerate dimension: no table behind it
       CAST(strftime(t.pickup_at, '%Y%m%d') AS INT) AS date_key,
       coalesce(z.zone_key, -1)    AS zone_key,
       coalesce(p.payment_key, -1) AS payment_key,
       t.trip_miles, t.fare_usd
FROM src_trips t
LEFT JOIN dim_zone z    ON t.zone_id = z.zone_id
LEFT JOIN dim_payment p ON t.payment_code = p.payment_code""")
print(con.execute("SELECT count(*) FROM dim_date").fetchall()[0][0], "dates,",
      con.execute("SELECT count(*) FROM dim_zone").fetchall()[0][0], "zones,",
      con.execute("SELECT count(*) FROM fact_trips").fetchall()[0][0], "facts")
print("orphan trips on the Unknown zone:", con.execute("SELECT count(*) FROM fact_trips WHERE zone_key = -1").fetchall()[0][0])
print("--- dims done")

# --- star_query ---
print(con.sql("""
SELECT z.borough, d.is_weekend, count(*) AS trips, round(sum(f.fare_usd)) AS fares
FROM fact_trips f
JOIN dim_zone z ON f.zone_key = z.zone_key
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_payment p ON f.payment_key = p.payment_key
WHERE p.label = 'Card' AND d.day_name = 'Friday'
GROUP BY ALL ORDER BY fares DESC LIMIT 4"""))
print("--- star_query done")

# --- fanout ---
rng = np.random.default_rng(1)
tolled = rng.choice(1_000_000, 80_000, replace=False) + 1
trip_tolls = pa.table({"trip_id": np.repeat(tolled, 2), "toll_usd": np.round(rng.uniform(2, 9, 160_000), 2)})

print("true fares      ", con.execute("SELECT round(sum(fare_usd)) FROM fact_trips").fetchall()[0][0])
print("joined to tolls ", con.execute("""SELECT round(sum(f.fare_usd)) FROM fact_trips f
    LEFT JOIN trip_tolls t USING (trip_id)""").fetchall()[0][0])
print("rolled up first ", con.execute("""SELECT round(sum(f.fare_usd)), round(sum(t.tolls)) FROM fact_trips f
    LEFT JOIN (SELECT trip_id, sum(toll_usd) AS tolls FROM trip_tolls GROUP BY 1) t USING (trip_id)""").fetchall()[0])
print("--- fanout done")

# --- additive ---
print(con.sql("""
SELECT round(sum(fare_usd) / sum(trip_miles), 2)  AS ratio_of_sums,
       round(avg(fare_usd / trip_miles), 2)       AS avg_of_ratios,
       round(sum(fare_usd / trip_miles))          AS sum_of_ratios
FROM fact_trips"""))
print("--- additive done")

# --- scd1 ---
con.execute("CREATE TABLE dim_zone_t1 AS SELECT * FROM dim_zone")
before = con.execute("""SELECT round(sum(fare_usd)) FROM fact_trips f JOIN dim_zone_t1 z USING (zone_key)
    WHERE z.borough = 'Brooklyn'""").fetchall()[0][0]
con.execute("UPDATE dim_zone_t1 SET borough = 'Brooklyn' WHERE zone_id = 6")  # the city redraws a boundary
after = con.execute("""SELECT round(sum(fare_usd)) FROM fact_trips f JOIN dim_zone_t1 z USING (zone_key)
    WHERE z.borough = 'Brooklyn'""").fetchall()[0][0]
print("Brooklyn fares for January, as reported before:", before)
print("Brooklyn fares for January, as reported after: ", after)
print("--- scd1 done")

# --- scd2 ---
con.execute("CREATE SEQUENCE zone_v_sk START 1")
con.execute("""
CREATE TABLE dim_zone_v (zone_key BIGINT, zone_id INT, zone_name VARCHAR, borough VARCHAR,
                         row_hash UBIGINT, valid_from DATE, valid_to DATE, is_current BOOLEAN)""")

def apply_scd2(source_sql, load_date):
    """Close the current row of any changed zone, then open a new one. Rerunning changes nothing."""
    con.execute(f"""CREATE OR REPLACE TEMP TABLE incoming AS
        SELECT *, hash(zone_name, borough) AS row_hash FROM ({source_sql})""")
    con.execute("""UPDATE dim_zone_v d SET valid_to = ?, is_current = false
        FROM incoming i
        WHERE d.zone_id = i.zone_id AND d.is_current AND d.row_hash <> i.row_hash""", [load_date])
    con.execute("""INSERT INTO dim_zone_v
        SELECT nextval('zone_v_sk'), i.zone_id, i.zone_name, i.borough, i.row_hash,
               ?::DATE, DATE '9999-12-31', true
        FROM incoming i
        LEFT JOIN dim_zone_v d ON d.zone_id = i.zone_id AND d.is_current
        WHERE d.zone_id IS NULL""", [load_date])

apply_scd2("SELECT * FROM src_zones", "2025-01-01")
changed = """SELECT zone_id, zone_name, CASE WHEN zone_id = 6 THEN 'Brooklyn' ELSE borough END AS borough FROM src_zones"""
apply_scd2(changed, "2026-01-15")
apply_scd2(changed, "2026-01-15")     # a retry
print(con.sql("SELECT zone_key, zone_id, borough, valid_from, valid_to, is_current FROM dim_zone_v WHERE zone_id = 6 ORDER BY 1"))
print("rows in dimension:", con.execute("SELECT count(*) FROM dim_zone_v").fetchall()[0][0])
print("--- scd2 done")

# --- scd2_facts ---
con.execute("""
CREATE TABLE fact_trips_v AS
SELECT t.trip_id, CAST(strftime(t.pickup_at, '%Y%m%d') AS INT) AS date_key,
       coalesce(z.zone_key, -1) AS zone_key, t.fare_usd
FROM src_trips t
LEFT JOIN dim_zone_v z ON t.zone_id = z.zone_id
     AND t.pickup_at::DATE >= z.valid_from AND t.pickup_at::DATE < z.valid_to""")
print("zone 6, grouped by the borough at the time of the trip")
print(con.sql("""SELECT z.borough, count(*) AS trips, min(f.date_key) AS first_day, max(f.date_key) AS last_day
    FROM fact_trips_v f JOIN dim_zone_v z USING (zone_key) WHERE z.zone_id = 6 GROUP BY 1 ORDER BY 3"""))
print("zone 6, restated to today's borough through the natural key")
print(con.sql("""SELECT cur.borough, count(*) AS trips
    FROM fact_trips_v f JOIN dim_zone_v z USING (zone_key)
    JOIN dim_zone_v cur ON cur.zone_id = z.zone_id AND cur.is_current
    WHERE z.zone_id = 6 GROUP BY 1"""))
print("--- scd2_facts done")

# --- drill ---
con.execute("""
CREATE TABLE fact_shifts AS
SELECT d.date_key, z.zone_key, (1 + (hash(d.date_key, z.zone_key) % 40))::INT AS drivers_on_shift, s.shift
FROM dim_date d CROSS JOIN dim_zone z CROSS JOIN (VALUES ('day'), ('night')) s(shift)
WHERE d.year = 2026 AND d.month = 1 AND z.zone_key > 0""")

wrong = con.execute("""SELECT round(sum(f.fare_usd)), sum(s.drivers_on_shift)
    FROM fact_trips f JOIN fact_shifts s USING (date_key, zone_key)""").fetchall()[0]
right = con.execute("""
WITH t AS (SELECT zone_key, sum(fare_usd) AS fares FROM fact_trips WHERE zone_key > 0 GROUP BY 1),
     s AS (SELECT zone_key, sum(drivers_on_shift) AS drivers FROM fact_shifts GROUP BY 1)
SELECT round(sum(t.fares)), sum(s.drivers) FROM t JOIN s USING (zone_key)""").fetchall()[0]
print("fact joined to fact:", wrong)
print("drill across:       ", right)
print("true:               ", con.execute("SELECT round(sum(fare_usd)) FROM fact_trips WHERE zone_key > 0").fetchall()[0][0],
      con.execute("SELECT sum(drivers_on_shift) FROM fact_shifts").fetchall()[0][0])
print("--- drill done")
