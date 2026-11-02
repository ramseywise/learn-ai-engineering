"""Chapter 5: the taxi pipeline in Airflow 3, including a real backfill (starts airflow standalone).

Run from any folder (it writes only to a temporary directory):
    uv run --python 3.12 --with apache-airflow --with duckdb python 05_airflow.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- shared_af ---
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
print("--- shared_af done")

# --- airflow_setup ---
import json, os, subprocess
pathlib.Path("dags").mkdir(exist_ok=True)
env = {**os.environ,
       "AIRFLOW_HOME": os.path.abspath("airflow_home"),
       "AIRFLOW__CORE__LOAD_EXAMPLES": "False",
       "AIRFLOW__CORE__DAGS_FOLDER": os.path.abspath("dags"),
       "AIRFLOW__LOGGING__LOGGING_LEVEL": "ERROR",
       "PYTHONPATH": os.path.abspath("dags")}

def airflow(*args):
    """Run the Airflow CLI against a throwaway home with a SQLite metadata database."""
    out = subprocess.run([sys.executable, "-m", "airflow", *args], capture_output=True, text=True, env=env)
    return out.returncode, out.stdout, out.stderr

print("migrate exit code:", airflow("db", "migrate")[0])
print("--- airflow_setup done")

# --- timetables ---
import datetime as dt
from airflow.timetables.base import TimeRestriction
from airflow.timetables.interval import CronDataIntervalTimetable
from airflow.timetables.trigger import CronTriggerTimetable
restriction = TimeRestriction(earliest=dt.datetime(2026, 1, 14, tzinfo=dt.timezone.utc), latest=None, catchup=True)
for table in (CronTriggerTimetable("0 3 * * *", timezone="UTC"), CronDataIntervalTimetable("0 3 * * *", timezone="UTC")):
    info = table.next_dagrun_info(last_automated_data_interval=None, restriction=restriction)
    print(f"{type(table).__name__:26} fires {info.run_after:%Y-%m-%d %H:%M}, logical date {info.logical_date:%Y-%m-%d %H:%M}")
print("--- timetables done")

# --- airflow_lib ---
import shutil
shutil.copy("taxi_lib.py", "dags/taxi_lib.py")   # the same functions Dagster imported
print("--- airflow_lib done")

# --- taskflow ---
pathlib.Path("dags/taxi_daily.py").write_text(r'''
import datetime as dt, pathlib
import duckdb
from airflow.sdk import dag, task
from airflow.timetables.interval import CronDataIntervalTimetable
from taxi_lib import land, build_daily, build_report

@dag(dag_id="taxi_daily", schedule=CronDataIntervalTimetable("0 3 * * *", timezone="UTC"), start_date=dt.datetime(2026, 1, 10),
     end_date=dt.datetime(2026, 1, 21), catchup=False, max_active_runs=1)
def taxi_daily():
    @task
    def raw_trips(ds=None):                   # ds is the logical date, YYYY-MM-DD
        poisoned = pathlib.Path("poisoned.txt")
        land(ds, sign=-1 if poisoned.exists() and ds in poisoned.read_text() else 1)

    @task(retries=2, retry_delay=dt.timedelta(seconds=0))
    def daily_revenue(ds=None):
        outages = pathlib.Path("outages.txt")
        if outages.exists() and int(outages.read_text()) > 0:
            outages.write_text(str(int(outages.read_text()) - 1))
            raise ConnectionError("warehouse unreachable")
        return int(build_daily(ds))

    @task
    def fares_positive():
        with duckdb.connect("warehouse.duckdb") as con:
            bad = con.execute("SELECT count(*) FROM daily_revenue WHERE fares <= 0").fetchall()[0][0]
        assert bad == 0, f"{bad} rows with no revenue"

    @task
    def zone_report():
        return build_report()

    raw_trips() >> daily_revenue() >> fares_positive() >> zone_report()

taxi_daily()
''')
code, out, err = airflow("dags", "reserialize")
print("reserialize exit code:", code, err[-300:])
code, out, err = airflow("dags", "list", "-o", "json")
print([(d["dag_id"], d["is_paused"]) for d in json.loads(out)])
print("--- taskflow done")

# --- test_run ---
def states(day):
    code, out, err = airflow("tasks", "states-for-dag-run", "taxi_daily", run_ids[day], "-o", "json")
    return {row["task_id"]: row["state"] for row in json.loads(out)}

run_ids = {}
def run_day(day):
    code, out, err = airflow("dags", "test", "taxi_daily", day)
    runs = json.loads(airflow("dags", "list-runs", "taxi_daily", "-o", "json")[1])
    run_ids[day] = next(r["run_id"] for r in runs if r["logical_date"].startswith(day))
    print(day, "exit", code, states(day))

run_day("2026-01-12")
with duckdb.connect("warehouse.duckdb", read_only=True) as con:
    print(con.execute("SELECT count(*), sum(trips) FROM daily_revenue").fetchall())
print("--- test_run done")

# --- af_retry ---
pathlib.Path("outages.txt").write_text("2")
run_day("2026-01-13")
print("outages left:", pathlib.Path("outages.txt").read_text())
print("--- af_retry done")

# --- af_check ---
pathlib.Path("poisoned.txt").write_text("2026-01-14")
run_day("2026-01-14")
print("--- af_check done")

# --- repair ---
pathlib.Path("poisoned.txt").unlink()
run_day("2026-01-14")
with duckdb.connect("warehouse.duckdb", read_only=True) as con:
    print(con.execute("SELECT count(*) FROM daily_revenue WHERE fares <= 0").fetchall())
print("--- repair done")

# --- backfill_dry ---
code, out, err = airflow("backfill", "create", "--dag-id", "taxi_daily", "--from-date", "2026-01-15", "--to-date", "2026-01-18", "--dry-run")
print(out[out.index("Runs to be attempted"):])
print("--- backfill_dry done")

# --- backfill_real ---
import atexit, signal, time
airflow("dags", "unpause", "taxi_daily", "-y")
print("create exit code:", airflow("backfill", "create", "--dag-id", "taxi_daily", "--from-date", "2026-01-15",
                                   "--to-date", "2026-01-18", "--reprocess-behavior", "none", "--max-active-runs", "1")[0])

server = subprocess.Popen([sys.executable, "-m", "airflow", "standalone"], env=env, start_new_session=True,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)   # scheduler, API server, Dag processor, triggerer
atexit.register(lambda: os.killpg(server.pid, signal.SIGTERM))

def runs(dag_id="taxi_daily"):
    listed = json.loads(airflow("dags", "list-runs", dag_id, "-o", "json")[1] or "[]")
    return {r["run_id"].split("__")[0] + " " + (r["logical_date"] or "")[:16]: r["state"] for r in listed}

def wait_for(check, seconds=150):
    deadline = time.time() + seconds
    while time.time() < deadline and not check():
        time.sleep(3)

wait_for(lambda: sum(state == "success" for state in runs().values()) == 6)
for run_id, state in sorted(runs().items()):
    print(run_id, state)
with duckdb.connect("warehouse.duckdb", read_only=True) as con:
    print(con.execute("SELECT min(day), max(day), sum(trips) FROM daily_revenue").fetchall())
    print(con.execute("SELECT sum(trips) FROM zone_report").fetchall())
print("--- backfill_real done")

# --- asset_style ---
pathlib.Path("dags/taxi_assets.py").write_text(r'''
import duckdb
from airflow.sdk import asset

@asset(schedule=None)
def daily_counts():
    with duckdb.connect("warehouse.duckdb") as con:
        con.execute("CREATE OR REPLACE TABLE daily_counts AS SELECT day, sum(trips) AS trips FROM daily_revenue GROUP BY 1")

@asset(schedule=daily_counts)                 # runs when daily_counts has a new event
def best_day():
    with duckdb.connect("warehouse.duckdb") as con:
        con.execute("CREATE OR REPLACE TABLE best_day AS SELECT * FROM daily_counts ORDER BY trips DESC LIMIT 1")
''')
print("reserialize exit code:", airflow("dags", "reserialize")[0])
for dag_id in ("daily_counts", "best_day"):
    airflow("dags", "unpause", dag_id, "-y")
airflow("dags", "trigger", "daily_counts")
wait_for(lambda: "success" in runs("best_day").values(), 90)
print("daily_counts:", list(runs("daily_counts").values()), "best_day:", list(runs("best_day").values()))
with duckdb.connect("warehouse.duckdb", read_only=True) as con:
    print(con.execute("SELECT * FROM best_day").fetchall())
print("--- asset_style done")
