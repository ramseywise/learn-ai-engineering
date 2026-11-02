"""Transform: the runnable code of notes/01-transform.md

Run from any folder (it writes only to a temporary directory):
    uv run --with dbt-duckdb --with pyarrow --with numpy python data-engineering/03-transform-and-orchestrate/practice/01_transform.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- project ---
import json, pathlib, duckdb, numpy as np, pyarrow as pa
from dbt.cli.main import dbtRunner

def write(path, text):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)

write("dbt_project.yml", """
name: taxi
version: "1.0"
profile: taxi
models:
  taxi:
    staging: {+materialized: view}
    core:    {+materialized: table}
    marts:   {+materialized: table}
""")
write("profiles.yml", """
taxi:
  target: dev
  outputs:
    dev: {type: duckdb, path: taxi.duckdb, threads: 2}
""")

def dbt(*args):
    """Run a dbt command in this process and print one line per node."""
    res = dbtRunner().invoke([*args, "--project-dir", ".", "--profiles-dir", ".", "--quiet"])
    if res.exception:
        raise res.exception
    for r in res.result.results:
        extra = f"  ({r.failures} failing rows)" if r.failures else ""
        print(f"{r.status!s:8}{r.node.resource_type!s:9}{r.node.name}{extra}")

def sql(query):
    with duckdb.connect("taxi.duckdb") as con:
        return con.execute(query).fetchall()
print("--- project done")

# --- raw ---
def make_raw(n, seed, pickup_col):
    """Raw landed data: everything is a string, names belong to the source, some rows arrive twice."""
    rng = np.random.default_rng(seed)
    pickup = np.datetime64("2026-01-01T00:00:00") + rng.integers(0, 31 * 86400, n) * np.timedelta64(1, "s")
    t = pa.table({
        "vendorid": rng.integers(1, 3, n).astype(str),
        pickup_col: pickup.astype(str),
        "pulocationid": rng.integers(1, 266, n).astype(str),
        "total_amount": np.round(rng.gamma(2.0, 7.0, n) + 3, 2).astype(str),
        "payment_type": rng.choice(["1", "2", "3", "4", "5", "6"], n, p=[.72, .22, .02, .02, .01, .01]),
    })
    return pa.concat_tables([t, t.slice(0, 500)])          # a retried load landed 500 rows twice

green, yellow = make_raw(100_000, 1, "lpep_pickup_datetime"), make_raw(200_000, 2, "tpep_pickup_datetime")
with duckdb.connect("taxi.duckdb") as con:
    con.execute("CREATE SCHEMA raw")
    con.execute("CREATE TABLE raw.green_tripdata AS SELECT * FROM green")
    con.execute("CREATE TABLE raw.yellow_tripdata AS SELECT * FROM yellow")
    print(con.execute("SELECT count(*) FROM raw.green_tripdata").fetchall()[0][0], "green rows,",
          con.execute("SELECT count(*) FROM raw.yellow_tripdata").fetchall()[0][0], "yellow rows")
    print(con.execute("DESCRIBE raw.green_tripdata").fetchall()[3][:2])

zones = "locationid,borough,zone\n" + "".join(
    f"{i},{['Manhattan','Queens','Brooklyn','Bronx','Staten Island'][i % 5]},Zone {i}\n" for i in range(1, 261))
write("seeds/taxi_zone_lookup.csv", zones)
print("--- raw done")

# --- staging ---
write("models/staging/sources.yml", """
sources:
  - name: raw
    tables:
      - name: green_tripdata
      - name: yellow_tripdata
""")
write("macros/payment_description.sql", """
{% macro payment_description(col) -%}
    case {{ col }}
        when 1 then 'Credit card' when 2 then 'Cash' when 3 then 'No charge'
        when 4 then 'Dispute' when 5 then 'Unknown' when 6 then 'Voided trip'
        else 'EMPTY'
    end
{%- endmacro %}
""")
STAGING = """
with tripdata as (
    select *,
           row_number() over (
               partition by vendorid, PICKUP, pulocationid, total_amount
           ) as rn
    from {{ source('raw', 'TABLE') }}
    where vendorid is not null
)
select
    md5(concat_ws('|', vendorid, PICKUP, pulocationid, total_amount)) as trip_id,
    cast(vendorid as integer)         as vendor_id,
    cast(PICKUP as timestamp)         as pickup_at,
    try_cast(pulocationid as integer) as pickup_zone_id,
    try_cast(total_amount as double)  as total_amount,
    coalesce(try_cast(payment_type as integer), 0) as payment_type,
    {{ payment_description("coalesce(try_cast(payment_type as integer), 0)") }} as payment_label
from tripdata
where rn = 1
"""
write("models/staging/stg_green.sql",
      STAGING.replace("PICKUP", "lpep_pickup_datetime").replace("TABLE", "green_tripdata"))
write("models/staging/stg_yellow.sql",
      STAGING.replace("PICKUP", "tpep_pickup_datetime").replace("TABLE", "yellow_tripdata"))
print("--- staging done")

# --- core ---
write("models/core/dim_zones.sql", """
select locationid as zone_id, borough, zone from {{ ref('taxi_zone_lookup') }}
union all
select -1, 'Unknown', 'Unknown'
""")
write("models/core/fact_trips.sql", """
with unioned as (
    select *, 'green' as service from {{ ref('stg_green') }}
    union all
    select *, 'yellow' as service from {{ ref('stg_yellow') }}
)
select u.trip_id, u.service, u.pickup_at, u.total_amount, u.payment_type, u.payment_label,
       coalesce(z.zone_id, -1) as zone_id, coalesce(z.borough, 'Unknown') as borough
from unioned u
left join {{ ref('dim_zones') }} z on u.pickup_zone_id = z.zone_id
""")
write("models/marts/mart_monthly_revenue.sql", """
select borough, service, date_trunc('month', pickup_at) as revenue_month,
       round(sum(total_amount), 2) as revenue, count(*) as trips
from {{ ref('fact_trips') }}
group by all
""")
dbt("build")
print(sql("SELECT count(*) FROM main.fact_trips"))
print(sql("SELECT service, count(*), round(sum(revenue)) FROM main.mart_monthly_revenue GROUP BY 1 ORDER BY 1"))
print("--- core done")

# --- kinds ---
for row in sql("""SELECT table_type, table_name FROM information_schema.tables
                  WHERE table_schema = 'main' ORDER BY 1, 2"""):
    print(row)
print("--- kinds done")

# --- dedupe_key ---
for key in ["vendorid, lpep_pickup_datetime",
            "vendorid, lpep_pickup_datetime, pulocationid, total_amount"]:
    print(sql(f"SELECT count(*) FROM (SELECT DISTINCT {key} FROM raw.green_tripdata)")[0][0], "rows on key:", key)
print("--- dedupe_key done")

# --- dag ---
manifest = json.loads(pathlib.Path("target/manifest.json").read_text())
for node, parents in manifest["parent_map"].items():
    if node.startswith("model."):
        print(node.split(".")[-1], "<-", [p.split(".")[-1] for p in parents])
print("--- dag done")

# --- compiled ---
print(pathlib.Path("target/compiled/taxi/models/staging/stg_green.sql").read_text().strip())
print("--- compiled done")

# --- inner_join ---
print(sql("""SELECT 'left join' AS how, count(*) FROM main.fact_trips
    UNION ALL SELECT 'inner join', count(*) FROM main.fact_trips WHERE zone_id <> -1"""))
print(sql("SELECT round(sum(total_amount)) FROM main.fact_trips WHERE zone_id = -1"))
print("--- inner_join done")

# --- tests ---
write("models/core/schema.yml", """
models:
  - name: stg_green
    columns:
      - name: trip_id
        data_tests: [unique, not_null]
      - name: pickup_at
        data_tests: [not_null]
  - name: fact_trips
    columns:
      - name: trip_id
        data_tests: [unique]
      - name: zone_id
        data_tests:
          - relationships:
              arguments: {to: ref('dim_zones'), field: zone_id}
      - name: payment_type
        data_tests:
          - accepted_values:
              arguments: {values: [0, 1, 2, 3, 4, 5, 6], quote: false}
""")
dbt("build")
print("--- tests done")

# --- break ---
with duckdb.connect("taxi.duckdb") as con:
    con.execute("UPDATE raw.yellow_tripdata SET payment_type = '9' WHERE rowid % 1000 = 0")
dbt("build")
print("rows with code 9 in fact_trips:", sql("SELECT count(*) FROM main.fact_trips WHERE payment_type = 9")[0][0])
print("rows with code 9 reaching the mart: mart was skipped, still", sql("SELECT sum(trips) FROM main.mart_monthly_revenue")[0][0], "trips")
print("--- break done")

# --- select ---
with duckdb.connect("taxi.duckdb") as con:
    con.execute("UPDATE raw.yellow_tripdata SET payment_type = '1' WHERE payment_type = '9'")
dbt("build", "--select", "stg_yellow+")
print("--- select done")

# --- freshness ---
write("models/staging/sources.yml", """
sources:
  - name: raw
    freshness:
      warn_after: {count: 6, period: hour}
      error_after: {count: 24, period: hour}
    loaded_at_field: cast(lpep_pickup_datetime as timestamp)
    tables:
      - name: green_tripdata
      - name: yellow_tripdata
        loaded_at_field: cast(tpep_pickup_datetime as timestamp)
""")
dbt("source", "freshness")
print("--- freshness done")
