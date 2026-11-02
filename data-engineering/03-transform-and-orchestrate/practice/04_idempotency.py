"""Idempotency and backfills: the runnable code of notes/04-idempotency-and-backfills.md

Run from any folder (it writes only to a temporary directory):
    uv run --with duckdb python data-engineering/03-transform-and-orchestrate/practice/04_idempotency.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- landing ---
import datetime as dt, hashlib, os, pathlib, shutil, duckdb
from concurrent.futures import ThreadPoolExecutor

def days(start, end):
    d, last = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    while d <= last:
        yield d.isoformat()
        d += dt.timedelta(days=1)

def land(day, extra=0):
    """Immutable raw input: one folder per day, generated deterministically from the date."""
    folder = pathlib.Path(f"landing/day={day}")
    folder.mkdir(parents=True, exist_ok=True)
    n = 1000 + int(day[-2:]) * 10 + extra
    seed = int(day.replace("-", ""))
    duckdb.sql(f"""COPY (SELECT {seed}::BIGINT * 10000 + i AS trip_id, 1 + i % 8 AS zone_id,
                                5 + (i * 37 % 400) / 10.0 AS fare
                         FROM range({n}) t(i))
                   TO '{folder}/trips.parquet' (FORMAT parquet)""")

for day in days("2026-01-10", "2026-01-20"):
    land(day)
print(duckdb.sql("""SELECT count(DISTINCT day) AS days, count(*) AS trips, round(sum(fare)) AS fares
                    FROM read_parquet('landing/*/*.parquet', hive_partitioning=1)"""))
print("--- landing done")

# --- append ---
con = duckdb.connect("warehouse.duckdb")
con.execute("CREATE TABLE daily_append (day DATE, trips BIGINT, fares DOUBLE)")

def load_append(day):
    con.execute(f"""INSERT INTO daily_append
        SELECT DATE '{day}', count(*), sum(fare) FROM 'landing/day={day}/*.parquet'""")

def total(table):
    return con.execute(f"SELECT count(*), sum(trips) FROM {table}").fetchall()[0]

load_append("2026-01-10")
print("after one run:          ", total("daily_append"))
load_append("2026-01-10")                     # a retry, a rerun, somebody being careful
print("after running it again: ", total("daily_append"))
print("--- append done")

# --- overwrite ---
con.execute("CREATE TABLE daily (day DATE, trips BIGINT, fares DOUBLE)")

def load_overwrite(day):
    con.execute("BEGIN")
    con.execute(f"DELETE FROM daily WHERE day = DATE '{day}'")
    con.execute(f"""INSERT INTO daily
        SELECT DATE '{day}', count(*), sum(fare) FROM 'landing/day={day}/*.parquet'""")
    con.execute("COMMIT")

load_overwrite("2026-01-10")
print("after one run:          ", total("daily"))
load_overwrite("2026-01-10")
print("after running it again: ", total("daily"))
print("--- overwrite done")

# --- merge_key ---
con.execute("CREATE TABLE trips_merged (trip_id BIGINT PRIMARY KEY, zone_id INT, fare DOUBLE)")

def load_merge(day):
    con.execute(f"""INSERT OR REPLACE INTO trips_merged
        SELECT trip_id, zone_id, fare FROM 'landing/day={day}/*.parquet'""")

load_merge("2026-01-10"); load_merge("2026-01-10")
print("merge, twice:", con.execute("SELECT count(*), count(DISTINCT trip_id) FROM trips_merged").fetchall()[0])
print("--- merge_key done")

# --- fingerprint ---
def fingerprint(query):
    """A hash of a result set that does not depend on row order."""
    data = sorted(map(repr, con.execute(query).fetchall()))
    return hashlib.md5("".join(data).encode()).hexdigest()[:10]

def build_clocked(day):
    con.execute(f"""CREATE OR REPLACE TABLE out_clocked AS
        SELECT DATE '{day}' AS day, count(*) AS trips, now()::TIMESTAMP AS loaded_at
        FROM 'landing/day={day}/*.parquet'""")

def build_pure(day):
    con.execute(f"""CREATE OR REPLACE TABLE out_pure AS
        SELECT DATE '{day}' AS day, count(*) AS trips
        FROM 'landing/day={day}/*.parquet'""")

for build, table in [(build_clocked, "out_clocked"), (build_pure, "out_pure")]:
    prints = set()
    for _ in range(3):
        build("2026-01-10")
        prints.add(fingerprint(f"SELECT * FROM {table}"))
    print(f"{table:12} distinct results over 3 runs: {len(prints)}")
print("--- fingerprint done")

# --- atomic ---
lake = pathlib.Path("lake/daily")

def write_in_place(day, rows, crash=False):
    path = lake / f"day={day}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for i, row in enumerate(rows):
            if crash and i == len(rows) // 2:
                raise IOError("node lost")
            f.write(f"{row}\n")

def write_atomic(day, rows, crash=False):
    path = lake / f"day={day}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        for i, row in enumerate(rows):
            if crash and i == len(rows) // 2:
                raise IOError("node lost")
            f.write(f"{row}\n")
    os.replace(tmp, path)                     # atomic on one POSIX filesystem

rows = list(range(1000))
for writer in (write_in_place, write_atomic):
    writer("2026-01-11", rows)
    try:
        writer("2026-01-11", rows, crash=True)
    except IOError:
        pass
    print(f"{writer.__name__:15} readers see", sum(1 for _ in open(lake / "day=2026-01-11.csv")), "rows after a crash")
print("--- atomic done")

# --- wap ---
for day in days("2026-01-10", "2026-01-20"):
    load_overwrite(day)

def publish(day, audit):
    """Write, audit, publish: build a staging copy, check it, then swap it in one transaction."""
    con.execute("CREATE OR REPLACE TABLE daily_staging AS SELECT * FROM daily")
    con.execute(f"DELETE FROM daily_staging WHERE day = DATE '{day}'")
    con.execute(f"""INSERT INTO daily_staging
        SELECT DATE '{day}', count(*), sum(fare) FROM 'landing/day={day}/*.parquet'""")
    bad = audit(day)
    if bad:
        print(f"{day}: audit failed ({bad}), production unchanged")
        return False
    con.execute("BEGIN")
    con.execute("DROP TABLE daily")
    con.execute("ALTER TABLE daily_staging RENAME TO daily")
    con.execute("COMMIT")
    print(f"{day}: published")
    return True

def min_trips(day):
    trips = con.execute(f"SELECT trips FROM daily_staging WHERE day = DATE '{day}'").fetchall()[0][0]
    return f"{trips} trips looks truncated" if trips < 500 else None

publish("2026-01-12", min_trips)
duckdb.sql("""COPY (SELECT * FROM 'landing/day=2026-01-13/*.parquet' LIMIT 40)
              TO 'truncated.parquet' (FORMAT parquet)""")
shutil.copy("truncated.parquet", "landing/day=2026-01-13/trips.parquet")   # a bad re-landing
publish("2026-01-13", min_trips)
print(con.execute("SELECT trips FROM daily WHERE day = '2026-01-13'").fetchall()[0][0], "trips still in production")
land("2026-01-13")                            # the source re-sends the day
print("--- wap done")

# --- late ---
print("before:", con.execute("SELECT trips, fares FROM daily WHERE day = '2026-01-14'").fetchall()[0])
land("2026-01-14", extra=50)                  # 50 more trips turn up for an old day
load_overwrite("2026-01-14")
print("after: ", con.execute("SELECT trips, fares FROM daily WHERE day = '2026-01-14'").fetchall()[0])
print("other days that moved:", con.execute("""SELECT count(*) FROM daily
    WHERE day <> DATE '2026-01-14' AND trips <> 1000 + day(day) * 10""").fetchall()[0][0])
print("--- late done")

# --- dim_type1 ---
con.execute("CREATE TABLE zones_now (zone_id INT, borough TEXT)")
con.execute("INSERT INTO zones_now SELECT i, CASE WHEN i % 2 = 0 THEN 'Queens' ELSE 'Manhattan' END FROM range(1, 9) t(i)")
con.execute("""CREATE TABLE zones_hist AS
    SELECT zone_id, borough, DATE '2025-01-01' AS valid_from, DATE '9999-12-31' AS valid_to FROM zones_now""")
# Greenpoint moves to Brooklyn on January 15th
con.execute("UPDATE zones_now SET borough = 'Brooklyn' WHERE zone_id = 6")
con.execute("UPDATE zones_hist SET valid_to = DATE '2026-01-15' WHERE zone_id = 6")
con.execute("INSERT INTO zones_hist VALUES (6, 'Brooklyn', DATE '2026-01-15', DATE '9999-12-31')")

def by_borough_current(day):
    return con.execute(f"""SELECT z.borough, count(*) FROM 'landing/day={day}/*.parquet' t
        JOIN zones_now z USING (zone_id) GROUP BY 1 ORDER BY 1""").fetchall()

def by_borough_asof(day):
    return con.execute(f"""SELECT z.borough, count(*) FROM 'landing/day={day}/*.parquet' t
        JOIN zones_hist z ON t.zone_id = z.zone_id
         AND DATE '{day}' >= z.valid_from AND DATE '{day}' < z.valid_to
        GROUP BY 1 ORDER BY 1""").fetchall()

print("Jan 10, joined to the dimension as it is today:", by_borough_current("2026-01-10"))
print("Jan 10, joined to the dimension as it was then:", by_borough_asof("2026-01-10"))
print("--- dim_type1 done")

# --- cumulative ---
def downstream_of(day, start, end, cumulative):
    """Which partitions go stale when `day` is restated?"""
    all_days = list(days(start, end))
    return [d for d in all_days if d >= day] if cumulative else [day]

def build_cumulative(order):
    con.execute("CREATE OR REPLACE TABLE cum (day DATE, total BIGINT)")
    for day in order:
        prev = con.execute(f"SELECT coalesce(max(total), 0) FROM cum WHERE day = DATE '{day}' - 1").fetchall()[0][0]
        trips = con.execute(f"SELECT trips FROM daily WHERE day = DATE '{day}'").fetchall()[0][0]
        con.execute(f"DELETE FROM cum WHERE day = DATE '{day}'")
        con.execute(f"INSERT INTO cum VALUES (DATE '{day}', {prev + trips})")
    return con.execute("SELECT max(total) FROM cum").fetchall()[0][0]

window = list(days("2026-01-10", "2026-01-20"))
print("forward: ", build_cumulative(window))
print("backward:", build_cumulative(window[::-1]))
print("a daily table, restating Jan 14:     ", downstream_of("2026-01-14", window[0], window[-1], False))
print("a cumulative table, restating Jan 14:", len(downstream_of("2026-01-14", window[0], window[-1], True)), "partitions, in order")
print("--- cumulative done")

# --- backfill ---
def backfill(start, end, workers=1):
    todo = list(days(start, end))
    def one(day):
        c = con.cursor()                      # one connection per worker
        c.execute("BEGIN")
        c.execute(f"DELETE FROM daily_bf WHERE day = DATE '{day}'")
        c.execute(f"""INSERT INTO daily_bf
            SELECT DATE '{day}', count(*), sum(fare) FROM 'landing/day={day}/*.parquet'""")
        c.execute("COMMIT")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(one, todo))

con.execute("CREATE OR REPLACE TABLE daily_bf (day DATE, trips BIGINT, fares DOUBLE)")
backfill("2026-01-10", "2026-01-14")          # stops part way: only half the range done
backfill("2026-01-10", "2026-01-20")          # rerun the whole range: nothing doubles
first = fingerprint("SELECT * FROM daily_bf")
backfill("2026-01-10", "2026-01-20", workers=4)
print("rerun over the partial run:", first, " rerun with 4 workers:", fingerprint("SELECT * FROM daily_bf"))
print("--- backfill done")

# --- reconcile ---
diff = con.execute("""
    WITH src AS (SELECT day::DATE AS day, count(*) AS trips, round(sum(fare), 2) AS fares
                 FROM read_parquet('landing/*/*.parquet', hive_partitioning=1) GROUP BY 1),
         out AS (SELECT day, trips, round(fares, 2) AS fares FROM daily_bf)
    SELECT s.day, s.trips, o.trips FROM src s FULL JOIN out o USING (day)
    WHERE s.trips IS DISTINCT FROM o.trips OR s.fares IS DISTINCT FROM o.fares""").fetchall()
print("partitions that disagree with source:", diff)
print("--- reconcile done")

# --- side_effects ---
con.execute("CREATE TABLE sent (idempotency_key TEXT PRIMARY KEY, body TEXT)")
outbox = []

def send_report(day):
    key = f"daily-report/{day}"
    fresh = con.execute("INSERT OR IGNORE INTO sent VALUES (?, ?) RETURNING 1", [key, day]).fetchall()
    if fresh:
        outbox.append(day)                    # the real send goes here

send_report("2026-01-10"); send_report("2026-01-10")
print("emails sent:", outbox)
print("--- side_effects done")
