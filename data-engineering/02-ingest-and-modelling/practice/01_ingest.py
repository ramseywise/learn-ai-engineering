"""Code from notes/01-ingest.md.

Run from any folder (it writes only to a temporary directory):
    uv run --with duckdb --with pyarrow --with numpy --with 'dlt[duckdb]' python 01_ingest.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- source ---
import sqlite3, duckdb, random, datetime as dt

def make_source(path="ops.sqlite", days=3, per_day=1000, seed=7):
    """An operational database: one row per trip, updated in place."""
    rng = random.Random(seed)
    db = sqlite3.connect(path)
    db.execute("DROP TABLE IF EXISTS trips")
    db.execute("""CREATE TABLE trips (
        trip_id INTEGER PRIMARY KEY, pickup_date TEXT, zone INTEGER,
        fare_usd REAL, updated_at TEXT)""")
    rows, tid = [], 0
    for d in range(days):
        day = dt.date(2026, 1, 1) + dt.timedelta(days=d)
        for _ in range(per_day):
            tid += 1
            rows.append((tid, str(day), rng.randint(1, 260),
                         round(rng.uniform(4, 60), 2), f"{day} 23:00:00"))
    db.executemany("INSERT INTO trips VALUES (?,?,?,?,?)", rows)
    db.commit()
    return db

source = make_source()
print(source.execute("SELECT count(*), sum(fare_usd) FROM trips").fetchone())
print("--- source done")

# --- append_twice ---
wh = duckdb.connect()
wh.execute("CREATE TABLE raw_trips (trip_id INT, pickup_date DATE, zone INT, fare_usd DOUBLE, updated_at TIMESTAMP)")

def load_append(day):
    rows = source.execute("SELECT * FROM trips WHERE pickup_date = ?", (day,)).fetchall()
    wh.executemany("INSERT INTO raw_trips VALUES (?,?,?,?,?)", rows)

load_append("2026-01-01")
load_append("2026-01-01")   # the scheduler retried after a timeout
print(wh.execute("SELECT count(*) AS loaded, count(DISTINCT trip_id) AS trips FROM raw_trips").fetchone())
print("--- append_twice done")

# --- idempotent ---
def load_window(day):
    """Replace one day's rows inside a transaction: running it twice changes nothing."""
    rows = source.execute("SELECT * FROM trips WHERE pickup_date = ?", (day,)).fetchall()
    wh.execute("BEGIN")
    wh.execute("DELETE FROM raw_trips WHERE pickup_date = ?", (day,))
    wh.executemany("INSERT INTO raw_trips VALUES (?,?,?,?,?)", rows)
    wh.execute("COMMIT")

load_window("2026-01-01")
load_window("2026-01-01")
print(wh.execute("SELECT count(*) AS loaded, count(DISTINCT trip_id) AS trips FROM raw_trips").fetchone())
print("--- idempotent done")

# --- watermark ---
wh.execute("DELETE FROM raw_trips")

def extract_since(mark):
    return source.execute("SELECT * FROM trips WHERE updated_at > ? ORDER BY updated_at", (mark,)).fetchall()

def upsert(rows):
    if rows:
        wh.executemany("INSERT INTO raw_trips VALUES (?,?,?,?,?)", rows)
    wh.execute("""CREATE OR REPLACE TABLE raw_trips AS
        SELECT * EXCLUDE rn FROM (SELECT *, row_number() OVER
          (PARTITION BY trip_id ORDER BY updated_at DESC) rn FROM raw_trips) WHERE rn = 1""")

rows = extract_since("1900-01-01")
upsert(rows)
mark = max(r[4] for r in rows)
print("high watermark", mark)

# A correction commits at 09:00 but its transaction began at 22:30, and stamped then.
source.execute("UPDATE trips SET fare_usd = 99.0, updated_at = '2026-01-03 22:30:00' WHERE trip_id = 42")
# A customer deletion leaves no row to find.
source.execute("DELETE FROM trips WHERE trip_id = 43")
# A normal correction after the watermark.
source.execute("UPDATE trips SET fare_usd = 11.0, updated_at = '2026-01-04 08:00:00' WHERE trip_id = 44")
source.commit()

rows = extract_since(mark)
upsert(rows)
print("extracted", len(rows), "rows, ids", [r[0] for r in rows])
print(wh.execute("SELECT trip_id, fare_usd FROM raw_trips WHERE trip_id IN (42, 43, 44) ORDER BY 1").fetchall())
print("source says:", source.execute("SELECT trip_id, fare_usd FROM trips WHERE trip_id IN (42, 43, 44) ORDER BY 1").fetchall())
print("--- watermark done")

# --- overlap ---
from datetime import datetime, timedelta

def minus_hours(ts, hours):
    return str(datetime.fromisoformat(ts) - timedelta(hours=hours))

rows = extract_since(minus_hours(mark, 2))   # re-read a two-hour overlap, and let upsert dedupe
upsert(rows)
print("extracted", len(rows), "rows")
print(wh.execute("SELECT trip_id, fare_usd FROM raw_trips WHERE trip_id IN (42, 43, 44) ORDER BY 1").fetchall())
print("--- overlap done")

# --- dual_write ---
import random
rng = random.Random(7)

def dual_write():
    """Two clients write one key to the database and to a search index, separately."""
    to_db, to_index = ["A", "B"], ["A", "B"]
    rng.shuffle(to_db); rng.shuffle(to_index)      # each write races to each system on its own
    return to_db[-1], to_index[-1]

def follow_log():
    """The database decides one order, and the index applies that same order."""
    log = ["A", "B"]; rng.shuffle(log)
    return log[-1], log[-1]

N = 100_000
for name, fn in [("dual write", dual_write), ("follow the log", follow_log)]:
    disagree = sum(db != index for db, index in (fn() for _ in range(N)))
    print(f"{name:15s} the two systems disagree in {disagree / N:6.2%} of runs")
print("--- dual_write done")

# --- cdc ---
source = make_source()
source.executescript("""
CREATE TABLE change_log (lsn INTEGER PRIMARY KEY AUTOINCREMENT, op TEXT, trip_id INT,
                         pickup_date TEXT, zone INT, fare_usd REAL, updated_at TEXT);
CREATE TRIGGER t_i AFTER INSERT ON trips BEGIN INSERT INTO change_log (op,trip_id,pickup_date,zone,fare_usd,updated_at)
  VALUES ('c',new.trip_id,new.pickup_date,new.zone,new.fare_usd,new.updated_at); END;
CREATE TRIGGER t_u AFTER UPDATE ON trips BEGIN INSERT INTO change_log (op,trip_id,pickup_date,zone,fare_usd,updated_at)
  VALUES ('u',new.trip_id,new.pickup_date,new.zone,new.fare_usd,new.updated_at); END;
CREATE TRIGGER t_d AFTER DELETE ON trips BEGIN INSERT INTO change_log (op,trip_id) VALUES ('d',old.trip_id); END;
""")
wh = duckdb.connect()
wh.execute("CREATE TABLE raw_trips (_lsn BIGINT, trip_id INT, pickup_date DATE, zone INT, fare_usd DOUBLE)")
snapshot = source.execute("SELECT trip_id, pickup_date, zone, fare_usd FROM trips").fetchall()
wh.executemany("INSERT INTO raw_trips VALUES (0,?,?,?,?)", snapshot)
print("snapshot rows", wh.execute("SELECT count(*) FROM raw_trips").fetchone()[0])

source.execute("UPDATE trips SET fare_usd = 99.0, updated_at = '2026-01-03 22:30:00' WHERE trip_id = 42")
source.execute("DELETE FROM trips WHERE trip_id = 43")
source.execute("UPDATE trips SET fare_usd = 11.0, updated_at = '2026-01-04 08:00:00' WHERE trip_id = 44")
source.commit()
for e in source.execute("SELECT lsn, op, trip_id, fare_usd FROM change_log").fetchall():
    print(e)
print("--- cdc done")

# --- apply ---
def apply_changes(after_lsn):
    """Apply changes in log order. A row stores the last position that touched it,
    and deleted keys are remembered, so replaying a change has no effect."""
    wh.execute("CREATE TABLE IF NOT EXISTS raw_trips_deleted (trip_id INT PRIMARY KEY, _lsn BIGINT)")
    events = source.execute("SELECT * FROM change_log WHERE lsn > ? ORDER BY lsn", (after_lsn,)).fetchall()
    for lsn, op, tid, day, zone, fare, _ in events:
        seen = wh.execute("SELECT max(_lsn) FROM (SELECT _lsn FROM raw_trips WHERE trip_id = ? UNION ALL "
                          "SELECT _lsn FROM raw_trips_deleted WHERE trip_id = ?)", (tid, tid)).fetchone()[0]
        if seen is not None and seen >= lsn:
            continue
        wh.execute("DELETE FROM raw_trips WHERE trip_id = ?", (tid,))
        if op == "d":
            wh.execute("INSERT OR REPLACE INTO raw_trips_deleted VALUES (?, ?)", (tid, lsn))
        else:
            wh.execute("INSERT INTO raw_trips VALUES (?,?,?,?,?)", (lsn, tid, day, zone, fare))
    return events[-1][0] if events else after_lsn

position = apply_changes(0)
position = apply_changes(0)   # a consumer crashed before saving its offset, so it replays everything
print("position", position)
print(wh.execute("SELECT trip_id, fare_usd, _lsn FROM raw_trips WHERE trip_id IN (42, 43, 44) ORDER BY 1").fetchall())
print("rows match source:", wh.execute("SELECT count(*) FROM raw_trips").fetchone()[0] == source.execute("SELECT count(*) FROM trips").fetchone()[0])
print("--- apply done")

# --- dlt ---
import dlt

def trips_resource(mark_initial="1900-01-01"):
    @dlt.resource(name="trips", primary_key="trip_id", write_disposition="merge")
    def trips(updated_at=dlt.sources.incremental("updated_at", initial_value=mark_initial)):
        db = sqlite3.connect("ops.sqlite")
        db.row_factory = sqlite3.Row
        q = "SELECT trip_id, pickup_date, zone, fare_usd, updated_at FROM trips WHERE updated_at >= ?"
        yield [dict(r) for r in db.execute(q, (updated_at.last_value,))]
    return trips

pipeline = dlt.pipeline(pipeline_name="ops_trips", destination=dlt.destinations.duckdb("lake.duckdb"),
                        dataset_name="raw", pipelines_dir="dlt_state", dev_mode=False)
print(pipeline.run(trips_resource()).has_failed_jobs)
n1 = duckdb.connect("lake.duckdb", read_only=True).execute("SELECT count(*) FROM raw.trips").fetchone()[0]
source.execute("UPDATE trips SET fare_usd = 22.0, updated_at = '2026-01-05 10:00:00' WHERE trip_id = 44")
source.commit()
print(pipeline.run(trips_resource()).has_failed_jobs)
con = duckdb.connect("lake.duckdb", read_only=True)
print("rows", n1, "->", con.execute("SELECT count(*) FROM raw.trips").fetchone()[0])
print("trip 44 fare", con.execute("SELECT fare_usd FROM raw.trips WHERE trip_id = 44").fetchone()[0])
print(sorted(r[0] for r in con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'raw'").fetchall()))
print("--- dlt done")
