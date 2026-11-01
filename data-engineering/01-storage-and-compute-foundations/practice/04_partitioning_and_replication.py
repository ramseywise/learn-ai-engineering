"""Code from notes/04-partitioning-and-replication.md.

Run from any folder (it writes only to a temporary directory):
    uv run --with duckdb --with numpy python 04_partitioning_and_replication.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- setup ---
import zlib, random, itertools, sqlite3, os, time, numpy as np
from collections import Counter

def h(key):
    """A hash that is stable across processes."""
    return zlib.crc32(str(key).encode())
print("--- setup done")

# --- range_vs_hash ---
rng = np.random.default_rng(7)
days = np.sort(rng.integers(0, 31, 1_000_000))
ids = np.arange(len(days))

# Today's writes: the rows for the last day of the month.
today = ids[days == 30]
range_partitions = 31                       # one per day
hash_partitions = np.array([h(i) for i in today[:50_000]]) % 31
print("writes today by range-on-date: 1 of", range_partitions, "partitions takes", len(today), "rows")
print("writes today by hash: busiest partition takes",
      f"{Counter(hash_partitions.tolist()).most_common(1)[0][1] / 50_000:.1%} of them")

def partitions_for_week(kind):
    if kind == "range":
        return len(set(range(7, 14)))
    return 31          # a hash has destroyed the order, so ask every partition

print("query one week: range touches", partitions_for_week("range"), "| hash touches", partitions_for_week("hash"))
print("--- range_vs_hash done")

# --- compound ---
rows = [{"zone": int(z), "day": int(d)} for z, d in zip(rng.integers(1, 261, 200_000), rng.integers(0, 31, 200_000))]
store = {}
for row in rows:
    store.setdefault(h(row["zone"]) % 16, []).append((row["zone"], row["day"]))
for part in store.values():
    part.sort()

target = h(42) % 16
hits = [r for r in store[target] if r[0] == 42 and 7 <= r[1] < 14]
print(f"zone 42, days 7-13: read 1 of 16 partitions, {len(hits)} rows, rows sorted by day inside the zone")
print("--- compound done")

# --- hot_key ---
keys_stream = ["celebrity"] * 300_000 + [f"user{i}" for i in range(700_000)]
def busiest(stream, n=100):
    c = Counter(h(k) % n for k in stream)
    return c.most_common(1)[0][1]

salt = random.Random(0)
print("no salt, busiest partition:", busiest(keys_stream))
print("salted,  busiest partition:", busiest(f"{k}{salt.randrange(100):02d}" if k == "celebrity" else k for k in keys_stream))
print("--- hot_key done")

# --- scatter ---
lat = random.Random(1)
def one_shard():
    return lat.lognormvariate(1.6, 0.5)      # a median near 5 ms, invented for the demo

def scatter_gather(n):
    return max(one_shard() for _ in range(n))

for n in [1, 4, 16, 64]:
    sample = sorted(scatter_gather(n) for _ in range(20_000))
    print(f"{n:3d} shards: median {sample[10_000]:6.1f} ms   p99 {sample[19_800]:6.1f} ms")
print("--- scatter done")

# --- hash_mod ---
keys = range(1_000_000)
moved_mod = sum(h(k) % 10 != h(k) % 11 for k in keys) / len(keys)
print(f"hash mod N, 10 -> 11 nodes: {moved_mod:.1%} of keys move")

# Fixed partitions: 1,024 partitions never change; only ownership of some moves.
PARTITIONS = 1024
owners = {p: p % 10 for p in range(PARTITIONS)}
new_owners = dict(owners)
for node in range(10):                         # the new node takes a fair share from each node
    take = [p for p, o in owners.items() if o == node][: PARTITIONS // 11 // 10 + 1]
    for p in take:
        new_owners[p] = 10
moved_fixed = sum(new_owners[h(k) % PARTITIONS] != owners[h(k) % PARTITIONS] for k in keys) / len(keys)
print(f"fixed partitions, 10 -> 11 nodes: {moved_fixed:.1%} of keys move")
print("load after rebalance:", sorted(Counter(new_owners.values()).values()))
print("--- hash_mod done")

# --- hive ---
import duckdb

con = duckdb.connect()
con.execute("""CREATE TABLE trips AS
    SELECT i AS trip_id, TIMESTAMP '2026-01-01' + INTERVAL (i * 2.6784) SECOND AS pickup_at,
           (hash(i) % 260 + 1)::INT AS pickup_zone, round(3 + random() * 40, 2) AS fare_usd
    FROM range(1000000) t(i)""")
con.execute("""COPY (SELECT *, pickup_at::DATE AS day FROM trips)
               TO 'lake' (FORMAT parquet, PARTITION_BY (day))""")
files = [os.path.join(d, f) for d, _, fs in os.walk("lake") for f in fs]
print(len(files), "files, e.g.", sorted(files)[0])
print(f"average file {sum(map(os.path.getsize, files)) / len(files) / 1e3:.0f} KB")

q = "SELECT sum(fare_usd) FROM read_parquet('lake/*/*.parquet', hive_partitioning=true) WHERE day = DATE '2026-01-15'"
plan = con.sql("EXPLAIN ANALYZE " + q).fetchall()[0][1]
print([line.strip(" │") for line in plan.splitlines() if "File Filters" in line or "Scanning Files" in line or "Files" in line][:3])
print(con.sql(q).fetchall())
print("--- hive done")

# --- small_files ---
con.execute("""COPY (SELECT *, pickup_at::DATE AS day FROM trips)
               TO 'too_fine' (FORMAT parquet, PARTITION_BY (day, pickup_zone))""")
fine = [os.path.join(d, f) for d, _, fs in os.walk("too_fine") for f in fs]
print(f"{len(fine)} files, average {sum(map(os.path.getsize, fine)) / len(fine) / 1e3:.1f} KB")
print(f"footer overhead reading all: {sum(os.path.getsize(f) for f in fine) / 1e6:.1f} MB vs "
      f"{sum(os.path.getsize(f) for f in files) / 1e6:.1f} MB by day")
def t(path):
    t0 = time.perf_counter(); con.sql(f"SELECT sum(fare_usd) FROM read_parquet('{path}', hive_partitioning=true)").fetchall()
    return (time.perf_counter() - t0) * 1000
print(f"full scan by day {min(t('lake/*/*.parquet') for _ in range(3)):.1f} ms, by day and zone {min(t('too_fine/*/*/*.parquet') for _ in range(3)):.1f} ms")
print("--- small_files done")

# --- statement_vs_row ---
def replica():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE trips (id INT PRIMARY KEY, audit REAL)")
    db.executemany("INSERT INTO trips VALUES (?, 0)", [(1,), (2,)])
    return db

leader, follower_stmt, follower_row = replica(), replica(), replica()
statement = "UPDATE trips SET audit = random()"
leader.execute(statement)
follower_stmt.execute(statement)                                     # replay the statement
for row in leader.execute("SELECT audit, id FROM trips"):            # or ship the resulting rows
    follower_row.execute("UPDATE trips SET audit = ? WHERE id = ?", row)

state = lambda db: db.execute("SELECT * FROM trips ORDER BY id").fetchall()
print("statement replica matches leader:", state(follower_stmt) == state(leader))
print("row replica matches leader:      ", state(follower_row) == state(leader))
print("--- statement_vs_row done")

# --- replication ---
class Node:
    def __init__(self, name):
        self.name, self.log, self.applied = name, [], 0
    def apply(self, entry):
        self.log.append(entry); self.applied += 1

class Cluster:
    """Single leader with asynchronous followers: a write is acknowledged before it replicates."""
    def __init__(self, followers=2):
        self.leader = Node("leader")
        self.followers = [Node(f"f{i}") for i in range(followers)]
        self.next_id = 1
    def write(self, value):
        entry = (self.next_id, value)
        self.next_id += 1
        self.leader.apply(entry)
        return entry[0]                              # acknowledged here
    def replicate(self, follower, upto):
        for entry in self.leader.log[follower.applied:upto]:
            follower.apply(entry)
    def failover(self):
        self.followers.sort(key=lambda n: n.applied, reverse=True)
        self.leader = self.followers.pop(0)
        self.next_id = self.leader.applied + 1       # autoincrement from what the new leader knows

c = Cluster()
for rider in ["ana", "bo", "cy", "di"]:
    c.write(f"receipt for {rider}")
old_log = list(c.leader.log)
c.replicate(c.followers[0], 3)
c.replicate(c.followers[1], 2)
print("acknowledged to clients:", old_log)

print("read from f1 now:", c.followers[1].log[-1], "(lagging: read-your-writes fails for cy, di)")
c.failover()
print("new leader log:", c.leader.log)
print("lost acknowledged write:", [e for e in old_log if e not in c.leader.log])
new_id = c.write("receipt for eve")
print("new write reused id", new_id, "- the old id", new_id, "belonged to:", dict(old_log)[new_id])
print("--- replication done")

# --- monotonic ---
replica_lag = {"f0": 3, "f1": 1}          # how many writes behind each follower is
history = [f"comment{i}" for i in range(1, 11)]
def read_from(replica):
    return history[: len(history) - replica_lag[replica]]

print("random replica reads:", len(read_from("f1")), "then", len(read_from("f0")), "comments: time went backwards")
pick = lambda user: "f" + str(zlib.crc32(user.encode()) % 2)
print("pinned by hash of user id:", {u: pick(u) for u in ["ana", "bo", "cy"]})
print("--- monotonic done")

# --- quorum ---
def always_overlap(n, w, r):
    nodes = range(n)
    return all(set(a) & set(b) for a in itertools.combinations(nodes, w)
                                for b in itertools.combinations(nodes, r))

print(f"{'n':>2} {'w':>2} {'r':>2}  overlap  tolerates down (write / read)")
for n, w, r in [(3, 2, 2), (3, 1, 1), (3, 3, 1), (5, 3, 3), (5, 2, 2)]:
    print(f"{n:2d} {w:2d} {r:2d}  {str(always_overlap(n, w, r)):7s}  {n - w} / {n - r}")
print("--- quorum done")
