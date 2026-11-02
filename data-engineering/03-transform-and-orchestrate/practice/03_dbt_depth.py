"""dbt depth: the runnable code of notes/03-dbt-tests-snapshots-incremental.md

Run from any folder (it writes only to a temporary directory):
    uv run --with dbt-duckdb python data-engineering/03-transform-and-orchestrate/practice/03_dbt_depth.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- project ---
import pathlib, duckdb
from dbt.cli.main import dbtRunner

def write(path, text):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)

write("dbt_project.yml", 'name: taxi\nversion: "1.0"\nprofile: taxi\n')
write("profiles.yml", "taxi:\n  target: dev\n  outputs:\n    dev: {type: duckdb, path: taxi.duckdb}\n")

def dbt(*args):
    res = dbtRunner().invoke([*args, "--project-dir", ".", "--profiles-dir", ".", "--quiet"])
    if res.exception:
        raise res.exception
    for r in res.result.results:
        extra = f"  ({r.failures} failing)" if r.failures else ""
        print(f"{r.status!s:8}{r.node.resource_type!s:9}{r.node.name[:58]}{extra}")

def sql(query):
    with duckdb.connect("taxi.duckdb") as con:
        return con.execute(query).fetchall()

def run(statement):
    with duckdb.connect("taxi.duckdb") as con:
        con.execute(statement)

run("CREATE SCHEMA raw")
run("""CREATE TABLE raw.trips AS
       SELECT i AS trip_id, 1 + i % 8 AS zone_id,
              TIMESTAMP '2026-01-01' + INTERVAL (i * 7) MINUTE AS pickup_at,
              round(5 + (i * 37 % 400) / 10.0, 2) AS fare
       FROM range(1000) t(i)""")
run("""CREATE TABLE raw.zones (zone_id INT, zone TEXT, borough TEXT, updated_at TIMESTAMP)""")
run("""INSERT INTO raw.zones VALUES (1,'Astoria','Queens','2025-01-01'), (2,'Bushwick','Brooklyn','2025-01-01'),
       (3,'Harlem','Manhattan','2025-01-01'), (4,'Midtown','Manhattan','2025-01-01'),
       (5,'Flushing','Queens','2025-01-01'), (6,'Greenpoint','Queens','2025-01-01'),
       (7,'Red Hook','Brooklyn','2025-01-01'), (8,'Chelsea','Manhattan','2025-01-01')""")
write("models/sources.yml", "sources:\n  - name: raw\n    tables:\n      - name: trips\n      - name: zones\n")
write("models/dim_zones.sql", "select zone_id, zone, borough from {{ source('raw', 'zones') }}")
write("models/fact_trips.sql", """
select t.trip_id, t.pickup_at, t.fare, z.zone, z.borough
from {{ source('raw', 'trips') }} t
left join {{ ref('dim_zones') }} z using (zone_id)
""")
dbt("run")
print(sql("SELECT count(*), round(sum(fare)) FROM main.fact_trips"))
print("--- project done")

# --- singular ---
write("tests/assert_fact_reconciles.sql", """
with src as (select count(*) as n, sum(fare) as fare from {{ source('raw', 'trips') }}),
     fct as (select count(*) as n, sum(fare) as fare from {{ ref('fact_trips') }})
select src.n as source_rows, fct.n as fact_rows, src.fare as source_fare, fct.fare as fact_fare
from src, fct
where src.n <> fct.n or abs(src.fare - fct.fare) > 0.01
""")
dbt("test")
print("--- singular done")

# --- fanout ---
run("INSERT INTO raw.zones VALUES (3,'Harlem','Manhattan','2025-06-01')")     # a second row for zone 3
dbt("build")
print(sql("SELECT source_rows, fact_rows, round(source_fare), round(fact_fare) FROM (" +
          pathlib.Path("target/compiled/taxi/tests/assert_fact_reconciles.sql").read_text() + ")"))
print("--- fanout done")

# --- generic ---
write("tests/generic/test_positive.sql", """
{% test positive(model, column_name) %}
select {{ column_name }} from {{ model }} where {{ column_name }} <= 0
{% endtest %}
""")
write("models/schema.yml", """
models:
  - name: dim_zones
    columns:
      - name: zone_id
        data_tests: [unique, not_null]
  - name: fact_trips
    columns:
      - name: trip_id
        data_tests: [unique]
      - name: fare
        data_tests: [positive]
""")
dbt("test")
print("--- generic done")

# --- grain ---
run("DELETE FROM raw.zones WHERE updated_at = '2025-06-01'")     # the source removes its duplicate
dbt("build")
print("--- grain done")

# --- thresholds ---
run("UPDATE raw.trips SET fare = -1 WHERE trip_id < 12")
write("models/schema.yml", """
models:
  - name: dim_zones
    columns:
      - name: zone_id
        data_tests: [unique, not_null]
  - name: fact_trips
    columns:
      - name: trip_id
        data_tests: [unique]
      - name: fare
        data_tests:
          - positive:
              config:
                severity: error
                warn_if: ">0"
                error_if: ">50"
                store_failures: true
""")
dbt("build", "--select", "fact_trips")
print(sql("SELECT fare, count(*) FROM main_dbt_test__audit.positive_fact_trips_fare GROUP BY 1"))
run("UPDATE raw.trips SET fare = 7 WHERE trip_id < 12")
print("--- thresholds done")

# --- unit ---
write("models/fare_bands.sql", """
select trip_id, fare,
       case when fare < 10 then 'low' when fare < 30 then 'mid' else 'high' end as band
from {{ ref('fact_trips') }}
""")
write("models/unit.yml", """
unit_tests:
  - name: band_boundaries
    model: fare_bands
    given:
      - input: ref('fact_trips')
        rows:
          - {trip_id: 1, fare: 9.99}
          - {trip_id: 2, fare: 10.00}
          - {trip_id: 3, fare: 30.00}
    expect:
      rows:
        - {trip_id: 1, fare: 9.99,  band: low}
        - {trip_id: 2, fare: 10.00, band: mid}
        - {trip_id: 3, fare: 30.00, band: high}
""")
dbt("build", "--select", "fare_bands")
print("--- unit done")

# --- unit_fail ---
good = pathlib.Path("models/fare_bands.sql").read_text()
write("models/fare_bands.sql", good.replace("fare < 10 ", "fare <= 10 "))
dbt("build", "--select", "fare_bands")
write("models/fare_bands.sql", good)
print("--- unit_fail done")

# --- snapshot ---
write("snapshots/zones.yml", """
snapshots:
  - name: zones_snapshot
    relation: source('raw', 'zones')
    config:
      schema: snapshots
      unique_key: zone_id
      strategy: timestamp
      updated_at: updated_at
      dbt_valid_to_current: "cast('9999-12-31' as timestamp)"
""")
dbt("snapshot")
run("UPDATE raw.zones SET borough = 'Brooklyn', updated_at = '2026-01-15' WHERE zone_id = 6")
dbt("snapshot")
HIST = """SELECT zone_id, borough, dbt_valid_from::DATE, dbt_valid_to::DATE
          FROM main_snapshots.zones_snapshot WHERE zone_id = 6 ORDER BY dbt_valid_from"""
for row in sql(HIST):
    print(row)
print("--- snapshot done")

# --- snapshot_gap ---
run("UPDATE raw.zones SET borough = 'Queens',    updated_at = '2026-02-01' WHERE zone_id = 7")
run("UPDATE raw.zones SET borough = 'Manhattan', updated_at = '2026-02-02' WHERE zone_id = 7")
dbt("snapshot")
for row in sql(HIST.replace("zone_id = 6", "zone_id = 7")):
    print(row)
print("--- snapshot_gap done")

# --- snapshot_check ---
write("snapshots/zones_check.yml", """
snapshots:
  - name: zones_check
    relation: source('raw', 'zones')
    config:
      schema: snapshots
      unique_key: zone_id
      strategy: check
      check_cols: [borough]
""")
dbt("snapshot", "--select", "zones_check")
run("UPDATE raw.zones SET zone = 'Greenpoint North', updated_at = '2026-03-01' WHERE zone_id = 6")
dbt("snapshot", "--select", "zones_check")
dbt("snapshot", "--select", "zones_snapshot")
print("rows for zone 6, check_cols=[borough]:", sql("SELECT count(*) FROM main_snapshots.zones_check WHERE zone_id = 6")[0][0])
print("rows for zone 6, timestamp strategy:  ", sql("SELECT count(*) FROM main_snapshots.zones_snapshot WHERE zone_id = 6")[0][0])
print("--- snapshot_check done")

# --- snapshot_delete ---
write("snapshots/zones_check.yml", pathlib.Path("snapshots/zones_check.yml").read_text() + "      hard_deletes: invalidate\n")
run("DELETE FROM raw.zones WHERE zone_id = 8")
dbt("snapshot", "--select", "zones_check")
print(sql("SELECT zone_id, dbt_valid_to IS NULL AS still_current FROM main_snapshots.zones_check WHERE zone_id = 8"))
print("--- snapshot_delete done")

# --- incr_append ---
write("models/fct_append.sql", """
{{ config(materialized='incremental') }}
select trip_id, pickup_at, fare from {{ source('raw', 'trips') }}
{% if is_incremental() %}
where pickup_at >= (select max(pickup_at) from {{ this }})
{% endif %}
""")
dbt("run", "--select", "fct_append")
dbt("run", "--select", "fct_append")
print(sql("SELECT count(*), count(DISTINCT trip_id) FROM main.fct_append"))
print("--- incr_append done")

# --- incr_key ---
write("models/fct_merge.sql", """
{{ config(materialized='incremental', unique_key='trip_id', incremental_strategy='delete+insert') }}
select trip_id, pickup_at, fare from {{ source('raw', 'trips') }}
{% if is_incremental() %}
where pickup_at > (select max(pickup_at) from {{ this }})
{% endif %}
""")
dbt("run", "--select", "fct_merge")
dbt("run", "--select", "fct_merge")
print(sql("SELECT count(*), count(DISTINCT trip_id) FROM main.fct_merge"))
print("--- incr_key done")

# --- incr_late ---
run("""INSERT INTO raw.trips VALUES (1000, 1, TIMESTAMP '2026-01-02 08:00', 50.0),
                                    (1001, 1, TIMESTAMP '2026-01-06 00:00', 50.0)""")
dbt("run", "--select", "fct_merge")
print("late row  1000 present:", sql("SELECT count(*) FROM main.fct_merge WHERE trip_id = 1000")[0][0])
print("fresh row 1001 present:", sql("SELECT count(*) FROM main.fct_merge WHERE trip_id = 1001")[0][0])
print("--- incr_late done")

# --- incr_lookback ---
write("models/fct_merge.sql", """
{{ config(materialized='incremental', unique_key='trip_id', incremental_strategy='delete+insert') }}
select trip_id, pickup_at, fare from {{ source('raw', 'trips') }}
{% if is_incremental() %}
where pickup_at > (select max(pickup_at) - interval 3 day from {{ this }})
{% endif %}
""")
run("INSERT INTO raw.trips VALUES (1002, 1, TIMESTAMP '2026-01-04 09:00', 50.0)")
dbt("run", "--select", "fct_merge")
print("row 1002, 2 days behind the newest: present", sql("SELECT count(*) FROM main.fct_merge WHERE trip_id = 1002")[0][0])
print("row 1000, 4 days behind the newest: present", sql("SELECT count(*) FROM main.fct_merge WHERE trip_id = 1000")[0][0])
print("rows:", sql("SELECT count(*) FROM main.fct_merge")[0][0], "source:", sql("SELECT count(*) FROM raw.trips")[0][0])
print("--- incr_lookback done")

# --- full_refresh ---
dbt("run", "--select", "fct_merge", "--full-refresh")
print("rows:", sql("SELECT count(*) FROM main.fct_merge")[0][0], "late row present:",
      sql("SELECT count(*) FROM main.fct_merge WHERE trip_id = 1000")[0][0])
print("--- full_refresh done")

# --- schema_change ---
BODY = """
{{ config(materialized='incremental', unique_key='trip_id', on_schema_change='MODE') }}
select trip_id, pickup_at, fare COLS from {{ source('raw', 'trips') }}
{% if is_incremental() %} where pickup_at > (select max(pickup_at) from {{ this }}) {% endif %}
"""
def fct_schema(mode, cols=""):
    write("models/fct_schema.sql", BODY.replace("MODE", mode).replace("COLS", cols))
    dbt("run", "--select", "fct_schema")
    print(mode, [c[0] for c in sql("DESCRIBE main.fct_schema")])

fct_schema("ignore")
fct_schema("ignore", ", fare * 0.2 as tip_estimate")
run("INSERT INTO raw.trips VALUES (1003, 1, TIMESTAMP '2026-01-07', 20.0)")
fct_schema("append_new_columns", ", fare * 0.2 as tip_estimate")
print(sql("SELECT count(*), count(tip_estimate) FROM main.fct_schema"))
print("--- schema_change done")

# --- microbatch ---
write("models/sources.yml", """
sources:
  - name: raw
    tables:
      - name: trips
        config: {event_time: pickup_at}
      - name: zones
""")
write("models/daily_revenue.sql", """
{{ config(materialized='incremental', incremental_strategy='microbatch',
          event_time='pickup_at', batch_size='day', begin='2026-01-01') }}
select trip_id, pickup_at, fare from {{ source('raw', 'trips') }}
""")
dbt("run", "--select", "daily_revenue", "--event-time-start", "2026-01-01", "--event-time-end", "2026-01-04")
print(sql("SELECT pickup_at::DATE, count(*), round(sum(fare)) FROM main.daily_revenue GROUP BY 1 ORDER BY 1"))
run("UPDATE raw.trips SET fare = fare + 100 WHERE pickup_at::DATE = '2026-01-02'")
dbt("run", "--select", "daily_revenue", "--event-time-start", "2026-01-02", "--event-time-end", "2026-01-03")
print(sql("SELECT pickup_at::DATE, count(*), round(sum(fare)) FROM main.daily_revenue GROUP BY 1 ORDER BY 1"))
print("--- microbatch done")
