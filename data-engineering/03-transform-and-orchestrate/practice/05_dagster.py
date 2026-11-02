"""Chapter 5: the taxi pipeline in Dagster.

Run from any folder (it writes only to a temporary directory):
    uv run --with dagster --with duckdb python 05_dagster.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- shared ---
import pathlib, sys
pathlib.Path("taxi_lib.py").write_text(r'''
import pathlib, duckdb

def land(day, sign=1):
    """The input both orchestrators read: one file per day of landed trips."""
    pathlib.Path("landing").mkdir(exist_ok=True)
    n = 1000 + int(day[-2:]) * 10
    duckdb.sql(f"""COPY (SELECT DATE '{day}' AS day, 1 + i % 8 AS zone_id, {sign} * (5 + (i * 37 % 400) / 10.0) AS fare
                         FROM range({n}) t(i)) TO 'landing/{day}.parquet' (FORMAT parquet)""")

def build_daily(day):
    """Idempotent: replaces one day of the output, as in the previous chapter."""
    with duckdb.connect("warehouse.duckdb") as con:
        con.execute("CREATE TABLE IF NOT EXISTS daily_revenue (day DATE, zone_id INT, trips BIGINT, fares DOUBLE)")
        con.execute("BEGIN")
        con.execute(f"DELETE FROM daily_revenue WHERE day = DATE '{day}'")
        con.execute(f"""INSERT INTO daily_revenue SELECT day, zone_id, count(*), sum(fare)
                        FROM 'landing/{day}.parquet' GROUP BY 1, 2""")
        con.execute("COMMIT")
        return con.execute(f"SELECT sum(trips) FROM daily_revenue WHERE day = DATE '{day}'").fetchall()[0][0]

def build_report():
    with duckdb.connect("warehouse.duckdb") as con:
        con.execute("""CREATE OR REPLACE TABLE zone_report AS
                       SELECT zone_id, sum(trips) AS trips, round(sum(fares), 2) AS fares
                       FROM daily_revenue GROUP BY 1""")
        return con.execute("SELECT count(*), sum(trips) FROM zone_report").fetchall()[0]
''')
sys.path.insert(0, ".")
import duckdb
from taxi_lib import land, build_daily, build_report
print("--- shared done")

# --- assets ---
import dagster as dg

daily = dg.DailyPartitionsDefinition(start_date="2026-01-10", end_date="2026-01-21")
poisoned, outages = set(), {"left": 0}        # failure injection for the demos below

@dg.asset(partitions_def=daily)
def raw_trips(context: dg.AssetExecutionContext) -> None:
    day = context.partition_key               # the logical date
    land(day, sign=-1 if day in poisoned else 1)

@dg.asset(partitions_def=daily, deps=[raw_trips], retry_policy=dg.RetryPolicy(max_retries=2))
def daily_revenue(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    if outages["left"] > 0:
        outages["left"] -= 1
        raise ConnectionError("warehouse unreachable")
    trips = build_daily(context.partition_key)
    return dg.MaterializeResult(metadata={"trips": int(trips)})

@dg.asset_check(asset=daily_revenue, blocking=True)
def fares_positive() -> dg.AssetCheckResult:
    with duckdb.connect("warehouse.duckdb") as con:
        bad = con.execute("SELECT count(*) FROM daily_revenue WHERE fares <= 0").fetchall()[0][0]
    return dg.AssetCheckResult(passed=bad == 0, metadata={"bad_rows": bad})

@dg.asset(partitions_def=daily, deps=[daily_revenue])
def zone_report() -> dg.MaterializeResult:
    zones, trips = build_report()
    return dg.MaterializeResult(metadata={"zones": zones, "trips": int(trips)})

pipeline = [raw_trips, daily_revenue, fares_positive, zone_report]
defs = dg.Definitions(assets=[raw_trips, daily_revenue, zone_report], asset_checks=[fares_positive])
graph = defs.resolve_asset_graph()
for asset_key in graph.get_all_asset_keys():
    print(asset_key.to_user_string(), "<-", sorted(k.to_user_string() for k in graph.get(asset_key).parent_keys))
print("--- assets done")

# --- run_one ---
instance = dg.DagsterInstance.ephemeral()

def run_day(day):
    result = dg.materialize(pipeline, partition_key=day, instance=instance, raise_on_error=False)
    for event in result.all_events:
        if event.event_type_value in ("STEP_SUCCESS", "STEP_FAILURE", "STEP_UP_FOR_RETRY", "STEP_SKIPPED"):
            print(f"{day} {event.step_key:32} {event.event_type_value}")
    return result

r = run_day("2026-01-12")
print("trips:", r.asset_materializations_for_node("daily_revenue")[0].metadata["trips"].value)
print("--- run_one done")

# --- retry ---
outages["left"] = 2
run_day("2026-01-13").success
print("--- retry done")

# --- check_fail ---
poisoned.add("2026-01-14")
print("success:", run_day("2026-01-14").success)
poisoned.clear()
print("repaired:", dg.materialize(pipeline, partition_key="2026-01-14", instance=instance, raise_on_error=False).success)
print("--- check_fail done")

# --- missing ---
report = dg.AssetKey("zone_report")
def missing():
    done = instance.get_materialized_partitions(report)
    return [p for p in daily.get_partition_keys() if p not in done]
print("done:   ", sorted(instance.get_materialized_partitions(report)))
print("missing:", missing())
print("--- missing done")

# --- backfill ---
for day in missing():
    assert dg.materialize(pipeline, partition_key=day, instance=instance, raise_on_error=False).success
print("missing after backfill:", missing())
with duckdb.connect("warehouse.duckdb") as con:
    print(con.execute("SELECT sum(trips), round(sum(fares)) FROM zone_report").fetchall())
print("--- backfill done")

# --- rerun ---
dg.materialize(pipeline, partition_key="2026-01-14", instance=instance, raise_on_error=False)
with duckdb.connect("warehouse.duckdb") as con:
    print("after running Jan 14 again:", con.execute("SELECT sum(trips), round(sum(fares)) FROM zone_report").fetchall())
print("--- rerun done")

# --- schedule ---
job = dg.define_asset_job("taxi_daily", selection=[raw_trips, daily_revenue, zone_report])
schedule = dg.build_schedule_from_partitioned_job(job, hour_of_day=3)
defs = dg.Definitions(assets=[raw_trips, daily_revenue, zone_report], asset_checks=[fares_positive],
                      jobs=[job], schedules=[schedule])
resolved = defs.resolve_schedule_def(schedule.name)
print(resolved.name, repr(resolved.cron_schedule), resolved.job_name)
print("--- schedule done")

# --- tick ---
import datetime as dt
tick = dg.build_schedule_context(scheduled_execution_time=dt.datetime(2026, 1, 14, 3, tzinfo=dt.timezone.utc))
print("fires 2026-01-14 03:00, builds partition:", [r.partition_key for r in resolved.evaluate_tick(tick).run_requests])
print("--- tick done")

# --- argument_style ---
@dg.asset(partitions_def=dg.MonthlyPartitionsDefinition(start_date="2026-01-01", end_date="2026-03-01"))
def monthly_fares(context: dg.AssetExecutionContext) -> list[float]:
    month = context.partition_key                 # the logical date, again
    return [12.5, 8.0] if month == "2026-01-01" else [20.0]

@dg.asset(partitions_def=monthly_fares.partitions_def)
def monthly_total(monthly_fares: list[float]) -> float:   # the argument is the dependency
    return sum(monthly_fares)

result = dg.materialize([monthly_fares, monthly_total], partition_key="2026-01-01", instance=dg.DagsterInstance.ephemeral())
print(result.output_for_node("monthly_total"))
print("--- argument_style done")
