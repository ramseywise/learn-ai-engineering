"""Orchestrate: the runnable code of notes/02-orchestrate.md

Run from any folder (it writes only to a temporary directory):
    uv run --with duckdb --with prefect python data-engineering/03-transform-and-orchestrate/practice/02_orchestrate.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- orchestrator ---
import graphlib, time, datetime as dt, duckdb, pathlib, itertools

class Pipeline:
    """A toy orchestrator: dependencies, retries, a logical date, run history."""
    def __init__(self, name):
        self.name, self.tasks, self.deps, self.retries, self.history = name, {}, {}, {}, {}

    def task(self, *, needs=(), retries=0):
        def register(fn):
            self.tasks[fn.__name__] = fn
            self.deps[fn.__name__] = set(needs)
            self.retries[fn.__name__] = retries
            return fn
        return register

    def run(self, logical_date, verbose=True):
        state = {}
        for name in graphlib.TopologicalSorter(self.deps).static_order():
            if any(state[d] != "success" for d in self.deps[name]):
                state[name] = "skipped"
            else:
                state[name] = self._attempt(name, logical_date)
            if verbose:
                print(f"{logical_date} {name:12} {state[name]}")
        self.history[logical_date] = "success" if set(state.values()) == {"success"} else "failed"
        return state

    def _attempt(self, name, logical_date):
        for attempt in range(self.retries[name] + 1):
            try:
                self.tasks[name](logical_date)
                return "success"
            except Exception as e:
                print(f"{logical_date} {name:12} attempt {attempt + 1} failed: {e}")
                time.sleep(0.01 * 2 ** attempt)      # backoff, shortened for the demo
        return "failed"
print("--- orchestrator done")

# --- pipeline ---
pipe = Pipeline("daily_revenue")
pathlib.Path("lake").mkdir(exist_ok=True)
outages = {}                                  # task -> failures still to inject

def maybe_fail(name):
    if outages.get(name, 0) > 0:
        outages[name] -= 1
        raise ConnectionError("warehouse unreachable")

@pipe.task(retries=2)
def extract(day):
    maybe_fail("extract")
    n = 1000 + int(day[-2:]) * 10          # deterministic per day
    duckdb.sql(f"""COPY (SELECT DATE '{day}' AS day, 5 + i % 40 AS fare FROM range({n}) t(i))
                   TO 'lake/raw_{day}.parquet'""")

@pipe.task(needs=["extract"])
def transform(day):
    maybe_fail("transform")
    duckdb.sql(f"""COPY (SELECT day, count(*) AS trips, sum(fare) AS revenue
                         FROM 'lake/raw_{day}.parquet' GROUP BY day)
                   TO 'lake/revenue_{day}.parquet'""")

@pipe.task(needs=["transform"])
def test_revenue(day):
    bad = duckdb.sql(f"SELECT count(*) FROM 'lake/revenue_{day}.parquet' WHERE revenue <= 0").fetchall()[0][0]
    assert bad == 0, f"{bad} days with no revenue"

@pipe.task(needs=["test_revenue"])
def publish(day):
    print(f"           published {day}")

pipe.run("2026-01-05")
print("--- pipeline done")

# --- retry ---
outages["extract"] = 2                        # fails twice, succeeds on the third attempt
pipe.run("2026-01-06")
print("--- retry done")

# --- stop ---
outages["extract"] = 3                        # more failures than retries
pipe.run("2026-01-07")
print("--- stop done")

# --- clock_bug ---
def naive_extract():
    """Reads the date from the clock. Re-running it writes today's partition, never the one that failed."""
    return dt.date.today().isoformat()

print("rerun 2026-01-07 with the clock writes to:", "raw_" + naive_extract() + ".parquet", "(not raw_2026-01-07)")
pipe.run("2026-01-07", verbose=False)
print("rerun 2026-01-07 with a logical date:", sorted(p.name for p in pathlib.Path("lake").glob("*07*")))
print("--- clock_bug done")

# --- catchup ---
def schedule(start, end):
    d = dt.date.fromisoformat(start)
    while d <= dt.date.fromisoformat(end):
        yield d.isoformat()
        d += dt.timedelta(days=1)

def missing_runs(start, end):
    return [d for d in schedule(start, end) if pipe.history.get(d) != "success"]

print("history:", pipe.history)
todo = missing_runs("2026-01-03", "2026-01-08")
print("to run:", todo)
for day in todo:
    pipe.run(day, verbose=False)
print("still missing:", missing_runs("2026-01-03", "2026-01-08"))
print(duckdb.sql("SELECT day, trips, revenue FROM 'lake/revenue_*.parquet' ORDER BY day"))
print("--- catchup done")

# --- sensor ---
def sensor(path, timeout_ticks=5):
    """Poll for a file. A sensor is a task whose only job is to wait for the world."""
    for tick in itertools.count():
        if pathlib.Path(path).exists():
            return tick
        if tick == timeout_ticks:
            raise TimeoutError(path)
        if tick == 2:                     # the vendor's file lands while we poll
            pathlib.Path(path).touch()
        time.sleep(0.01)

print("file seen after", sensor("lake/_SUCCESS_vendor"), "polls")
print("--- sensor done")

# --- prefect ---
import os
os.environ["PREFECT_LOGGING_LEVEL"] = "CRITICAL"
from prefect import flow, task
from prefect.testing.utilities import prefect_test_harness

calls = {"n": 0}

@task(retries=2, retry_delay_seconds=0)
def extract_task(day: str) -> int:
    calls["n"] += 1
    if calls["n"] < 3:
        raise ConnectionError("warehouse unreachable")
    return 1000

@task
def transform_task(day: str, rows: int) -> dict:
    return {"day": day, "trips": rows}

@flow
def daily_revenue(day: str) -> dict:
    rows = extract_task(day)
    return transform_task(day, rows)

with prefect_test_harness():
    print(daily_revenue("2026-01-05"), "after", calls["n"], "attempts of extract")
    print([daily_revenue(d)["day"] for d in ["2026-01-06", "2026-01-07"]])
print("--- prefect done")
