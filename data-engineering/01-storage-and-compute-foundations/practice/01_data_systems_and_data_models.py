"""Code from notes/01-data-systems-and-data-models.md.

Run from any folder (it writes only to a temporary directory):
    uv run --with numpy python 01_data_systems_and_data_models.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- disks ---
disks = 10_000
for mttf_years in (10, 30, 50):
    per_day = disks / (mttf_years * 365)
    print(f"MTTF {mttf_years:>2} years: {per_day:4.2f} failed disks per day, one every {1/per_day:4.1f} days")
print("--- disks done")

# --- fanout ---
import numpy as np
rng = np.random.default_rng(11)

# Followers are heavy-tailed: most have few, a handful have millions.
users = 1_000_000
followers = rng.pareto(1.1, users) * 8
followers = np.minimum(followers, 30_000_000)
posts_per_s = 4_600

print(f"mean followers  {followers.mean():>12,.0f}")
print(f"median          {np.median(followers):>12,.0f}")
print(f"largest         {followers.max():>12,.0f}")

# Pick who posts uniformly. Timeline writes per second on fan-out-on-write:
print(f"fan-out writes/s, all users      {posts_per_s * followers.mean():>14,.0f}")

# Hybrid: accounts above a threshold are read at query time instead.
for threshold in (1_000_000, 100_000, 10_000):
    kept = followers[followers < threshold]
    share_of_writes = kept.sum() / followers.sum()
    print(f"excluding >={threshold:>9,} followers: {(followers >= threshold).sum():>6,} accounts,"
          f" writes fall to {share_of_writes:6.1%}")
print("--- fanout done")

# --- percentiles ---
rng = np.random.default_rng(3)
n = 1_000_000
fast = rng.lognormal(mean=np.log(40), sigma=0.4, size=n)         # ms
slow = rng.random(n) < 0.015                                     # GC, a cache miss, a page fault
latency = fast + slow * rng.exponential(800, n)

print(f"mean {latency.mean():7.1f} ms")
for p in (50, 95, 99, 99.9):
    print(f"p{p:<5} {np.percentile(latency, p):7.1f} ms")
print(f"requests slower than the mean: {(latency > latency.mean()).mean():.1%}")
print("--- percentiles done")

# --- averaging ---
# Ten servers. Nine are healthy; one is slow and, because it sits behind a sticky
# load balancer, takes 30% of the traffic.
rng = np.random.default_rng(4)
shuffled = rng.permutation(latency)
bad, rest = shuffled[:300_000] * 4, shuffled[300_000:]
parts = [bad] + list(np.array_split(rest, 9))

avg_of_p99 = np.mean([np.percentile(p, 99) for p in parts])
true_p99 = np.percentile(np.concatenate(parts), 99)
print(f"average of ten servers' p99 {avg_of_p99:7.1f} ms")
print(f"p99 of all requests         {true_p99:7.1f} ms")

# The correct way to combine: keep histograms and add them.
edges = np.logspace(0, 5, 400)
hist = sum(np.histogram(p, edges)[0] for p in parts)
merged_p99 = edges[np.searchsorted(hist.cumsum(), 0.99 * hist.sum())]
print(f"p99 from merged histograms  {merged_p99:7.1f} ms")
print("--- averaging done")

# --- amplification ---
for fanout in (1, 5, 10, 50, 100):
    print(f"{fanout:>3} backend calls: {1 - 0.99**fanout:6.1%} of requests hit a call slower than its p99")
print("--- amplification done")

# --- omission ---
SERVICE, STALL_START, STALL_END = 0.005, 50.0, 52.0

def finish(start):
    """When a request that starts at `start` completes; the server freezes for 2 s."""
    if STALL_START <= start < STALL_END:
        start = STALL_END
    return start + SERVICE

# Open loop: a request every 10 ms whatever happens, as real users behave.
open_loop, free = [], 0.0
for t in np.arange(0, 100, 0.01):
    free = finish(max(t, free))
    open_loop.append(free - t)

# Closed loop: one client sends the next request only after the last reply.
closed_loop, t = [], 0.0
while t < 100:
    done = finish(t)
    closed_loop.append(done - t)
    t = done + 0.005                          # same 10 ms pacing when healthy

for name, lat in (("open loop", open_loop), ("closed loop", closed_loop)):
    lat = np.array(lat)
    print(f"{name:<12} n={len(lat):>6}  p50={np.percentile(lat, 50)*1000:7.1f} ms"
          f"  p99={np.percentile(lat, 99)*1000:7.1f} ms  max={lat.max()*1000:7.1f} ms")
print("--- omission done")

# --- models ---
import sqlite3, json, time
db = sqlite3.connect(":memory:")
rng = np.random.default_rng(7)
trips = 200_000
drivers = 2_000
driver_of = rng.integers(0, drivers, trips).tolist()
fares = np.round(rng.gamma(2.2, 7.0, trips), 2).tolist()

# Relational: the driver's name is stored once, and trips point to it.
db.executescript("""
create table driver(driver_id integer primary key, name text);
create table trip(trip_id integer primary key, driver_id integer references driver, fare real);
create index trip_driver on trip(driver_id);
create table trip_doc(trip_id integer primary key, doc text);
create index doc_driver on trip_doc(json_extract(doc, '$.driver.id'));
""")
db.executemany("insert into driver values (?,?)", [(i, f"Driver {i}") for i in range(drivers)])
db.executemany("insert into trip values (?,?,?)", zip(range(trips), driver_of, fares))

# Document: each trip carries its driver with it.
docs = ((i, json.dumps({"fare": fares[i], "driver": {"id": driver_of[i], "name": f"Driver {driver_of[i]}"}}))
        for i in range(trips))
db.executemany("insert into trip_doc values (?,?)", docs)

def timed(label, sql, *args):
    t = time.perf_counter(); cur = db.execute(sql, args); rows = cur.fetchall()
    print(f"{label:<34} {(time.perf_counter()-t)*1000:8.2f} ms   rows touched {max(cur.rowcount, len(rows)):>4}")

timed("rename, relational", "update driver set name='Ana M.' where driver_id=7")
timed("rename, document", "update trip_doc set doc=json_set(doc,'$.driver.name','Ana M.') "
      "where json_extract(doc,'$.driver.id')=7")
timed("read one trip, relational (join)", "select t.fare, d.name from trip t join driver d using(driver_id) where trip_id=4242")
timed("read one trip, document", "select doc from trip_doc where trip_id=4242")
print("--- models done")

# --- schema ---
db.execute("insert into trip_doc values (900001, ?)", (json.dumps({"fare": 11.0, "driver_name": "Old Format"}),))
db.execute("insert into trip_doc values (900002, ?)", (json.dumps({"fare": 12.0, "driver": {"id": 3, "name": "New Format"}}),))

# Schema-on-read: the reader carries the history of every shape ever written.
def driver_name(doc):
    d = json.loads(doc)
    if "driver" in d:
        return d["driver"]["name"]
    return d.get("driver_name", "unknown")

for tid in (900001, 900002):
    print(driver_name(db.execute("select doc from trip_doc where trip_id=?", (tid,)).fetchone()[0]))

# Schema-on-write: the shape is enforced, and changing it is an explicit event.
t = time.perf_counter()
db.execute("alter table trip add column tip real default 0")
print(f"alter table on {trips:,} rows: {(time.perf_counter()-t)*1000:.2f} ms")
t = time.perf_counter()
db.execute("update trip set tip = round(fare*0.1, 2)")
print(f"backfill the new column:      {(time.perf_counter()-t)*1000:.2f} ms")
try:
    db.execute("insert into trip(trip_id, driver_id, fare) values (1, 1, 2.0)")
except sqlite3.IntegrityError as e:
    print("rejected on write:", e)
print("--- schema done")

# --- declarative ---
query = "select count(*), avg(fare) from trip where fare > 100"
def plan(sql):
    return " | ".join(r[3] for r in db.execute("explain query plan " + sql))

t = time.perf_counter(); print(db.execute(query).fetchone()); a = time.perf_counter() - t
print(f"{a*1000:7.2f} ms   {plan(query)}")
db.execute("create index trip_fare on trip(fare)")
t = time.perf_counter(); print(db.execute(query).fetchone()); b = time.perf_counter() - t
print(f"{b*1000:7.2f} ms   {plan(query)}")
print("--- declarative done")

# --- graph ---
db.executescript("""
create table zone(zone text primary key);
create table adjacent(a text, b text);
""")
edges = [("Airport","Harbour"),("Harbour","Old Town"),("Old Town","Station"),("Station","Uni"),
         ("Uni","Hospital"),("Harbour","Docks"),("Docks","Stadium"),("Stadium","Hospital"),
         ("Old Town","Market"),("Market","Uni")]
db.executemany("insert into adjacent values (?,?)", edges + [(b, a) for a, b in edges])

# Reachable within any number of hops: no fixed number of joins can say this.
rows = db.execute("""
with recursive reach(zone, hops, path) as (
    select 'Airport', 0, 'Airport'
    union
    select a.b, r.hops + 1, r.path || ' > ' || a.b
    from reach r join adjacent a on a.a = r.zone
    where r.hops < 6 and instr(r.path, a.b) = 0
)
select zone, min(hops), path from reach group by zone order by 2, 1
""").fetchall()
for r in rows:
    print(f"{r[1]} hops  {r[0]:<10} {r[2]}")
print("--- graph done")
