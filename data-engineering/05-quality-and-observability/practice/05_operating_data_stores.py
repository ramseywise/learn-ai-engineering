"""Code from notes/05-operating-data-stores.md: restores, connections, vacuum and lag on real Postgres servers.

Run from any folder (it writes only to temporary directories and starts private Postgres servers):
    uv run --no-project --python 3.12 --with pgserver --with 'psycopg[binary,pool]' python 05_operating_data_stores.py

Timings change from machine to machine; the shape of each result is the point.
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- server ---
import shutil, subprocess, threading, time
import pgserver, psycopg

BIN = os.path.dirname(pgserver.__file__) + "/pginstall/bin"
ROOT = tempfile.mkdtemp(dir="/tmp", prefix="ops")

def tool(name, *args):
    return subprocess.run([f"{BIN}/{name}", *args], check=True, capture_output=True, text=True).stdout

class Server:
    def __init__(self, name, port, conf=""):
        self.dir, self.port = f"{ROOT}/{name}", port
        self.conf = f"listen_addresses=''\nunix_socket_directories='{ROOT}'\nport={port}\n{conf}\n"
    def init(self):
        tool("initdb", "-D", self.dir, "-U", "postgres", "--auth=trust", "-E", "UTF8")
        return self.configure()
    def configure(self):
        with open(f"{self.dir}/postgresql.conf", "a") as f:
            f.write(self.conf)
        return self
    def start(self):
        tool("pg_ctl", "-w", "-t", "120", "-D", self.dir, "-l", f"{self.dir}/server.log", "start")
        return self
    def connect(self, dbname="postgres"):
        return psycopg.connect(f"host={ROOT} port={self.port} user=postgres dbname={dbname}", autocommit=True)
    def stop(self):
        subprocess.run([f"{BIN}/pg_ctl", "-w", "-D", self.dir, "-m", "fast", "stop"], capture_output=True)

os.makedirs(f"{ROOT}/archive")
primary = Server("primary", 5621, f"""wal_level=replica
archive_mode=on
archive_command='test ! -f {ROOT}/archive/%f && cp %p {ROOT}/archive/%f'
max_connections=30
autovacuum=off""").init().start()
db = primary.connect()
print(db.execute("SHOW server_version").fetchone()[0], "| max_connections", db.execute("SHOW max_connections").fetchone()[0])

# --- dump_restore ---
db.execute("""CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL);
              INSERT INTO accounts SELECT i, 1000 FROM generate_series(1, 1000000) i""")
halt = threading.Event()
def transfers():
    """Move money between accounts, in transactions, so the total never changes."""
    c, i = primary.connect(), 0
    while not halt.is_set():
        i += 1
        with c.transaction():
            c.execute("UPDATE accounts SET balance = balance - 1 WHERE id = %s", (i % 1000000 + 1,))
            c.execute("UPDATE accounts SET balance = balance + 1 WHERE id = %s", ((i * 7) % 1000000 + 1,))
    c.close()
writer = threading.Thread(target=transfers); writer.start()
t = time.perf_counter()
tool("pg_dump", "-h", ROOT, "-p", "5621", "-U", "postgres", "-Fc", "-f", f"{ROOT}/nightly.dump", "postgres")
print(f"pg_dump under write load: {time.perf_counter() - t:.2f} s, {os.path.getsize(f'{ROOT}/nightly.dump') / 1e6:.1f} MB")
halt.set(); writer.join()

def restore_drill(dump_path, expected_tables, invariant):
    """A backup you have not restored is a hope. Restore to a scratch database and check the data."""
    db.execute("DROP DATABASE IF EXISTS drill"); db.execute("CREATE DATABASE drill")
    t = time.perf_counter()
    try:
        tool("pg_restore", "-h", ROOT, "-p", "5621", "-U", "postgres", "-d", "drill", dump_path)
    except subprocess.CalledProcessError as e:
        return f"FAILED: {e.stderr.strip().splitlines()[-1]}"
    took = time.perf_counter() - t
    with primary.connect("drill") as c:
        tables = {r[0] for r in c.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'").fetchall()}
        if tables != expected_tables:
            return f"FAILED: tables {tables}"
        value = c.execute(invariant).fetchone()[0]
    return f"ok in {took:.2f} s, invariant = {value:,d}"

print("real dump :", restore_drill(f"{ROOT}/nightly.dump", {"accounts"}, "SELECT sum(balance) FROM accounts"))
open(f"{ROOT}/silent_failure.dump", "w").close()                                 # a job that wrote nothing
print("empty file:", restore_drill(f"{ROOT}/silent_failure.dump", {"accounts"}, "SELECT sum(balance) FROM accounts"))

# --- pitr ---
tool("pg_basebackup", "-h", ROOT, "-p", "5621", "-U", "postgres", "-D", f"{ROOT}/base", "-X", "stream", "-c", "fast")
print(f"base backup: {sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(f'{ROOT}/base') for f in fs) / 1e6:.0f} MB")

db.execute("CREATE TABLE orders (id int PRIMARY KEY, placed timestamptz DEFAULT now())")
db.execute("INSERT INTO orders (id) SELECT generate_series(1, 5000)")            # work after the backup
time.sleep(1.2)
target = db.execute("SELECT now()").fetchone()[0]                                # the last good moment
time.sleep(1.2)
db.execute("DELETE FROM orders WHERE id > 1000")                                 # the mistake: WHERE was wrong
print("orders after the bad DELETE:", db.execute("SELECT count(*) FROM orders").fetchone()[0])
db.execute("SELECT pg_switch_wal()")                                             # ship the current WAL segment
last = db.execute("SELECT last_archived_wal FROM pg_stat_archiver").fetchone()[0]
print("WAL segments archived:", len(os.listdir(f"{ROOT}/archive")), "| last:", last)

shutil.copytree(f"{ROOT}/base", f"{ROOT}/restored")
open(f"{ROOT}/restored/recovery.signal", "w").close()
restored = Server("restored", 5622, f"""archive_mode=off
restore_command='cp {ROOT}/archive/%f %p'
recovery_target_time='{target}'
recovery_target_action='promote'""").configure()
t = time.perf_counter(); restored.start()
with restored.connect() as c:
    while c.execute("SELECT pg_is_in_recovery()").fetchone()[0]:
        time.sleep(0.05)
    print(f"restored to {target:%H:%M:%S.%f} in {time.perf_counter() - t:.2f} s: orders =",
          c.execute("SELECT count(*) FROM orders").fetchone()[0])
restored.stop()
with open(f"{restored.dir}/server.log") as f:
    print("\n".join(l.split("LOG:")[1].strip() for l in f if "recovery stopping" in l or "selected new timeline" in l))
try:
    with primary.connect("drill") as c:
        c.execute("SELECT count(*) FROM orders")
except psycopg.errors.UndefinedTable:
    print("the nightly dump, taken before these orders existed, has none of them")

# --- connections ---
import collections
def per_request(n):
    t = time.perf_counter()
    for _ in range(n):
        c = primary.connect(); c.execute("SELECT 1"); c.close()
    return (time.perf_counter() - t) / n * 1000
held = primary.connect()
t = time.perf_counter()
for _ in range(500):
    held.execute("SELECT 1")
reuse = (time.perf_counter() - t) / 500 * 1000
print(f"new connection each query: {per_request(500):.2f} ms | held connection: {reuse:.2f} ms")

def traffic(handle, clients=100, requests=5):
    """100 clients each make 5 requests, and each request does 50 ms of database work."""
    errors, slowest = collections.Counter(), [0.0]
    def client(i):
        time.sleep(i * 0.001)
        for _ in range(requests):
            t = time.perf_counter()
            try:
                handle()
            except psycopg.OperationalError as e:
                errors[str(e).split("FATAL:")[-1].strip().splitlines()[0][-48:]] += 1
            slowest[0] = max(slowest[0], time.perf_counter() - t)
    threads = [threading.Thread(target=client, args=(i,)) for i in range(clients)]
    t = time.perf_counter()
    for th in threads: th.start()
    for th in threads: th.join()
    return time.perf_counter() - t, errors, slowest[0]

def no_pool():
    with primary.connect() as c:
        c.execute("SELECT pg_sleep(0.05)")
took, errors, slow = traffic(no_pool)
print(f"no pool   : {took:.2f} s, slowest {slow * 1000:.0f} ms, {sum(errors.values())} of 500 failed")
print("   ", dict(errors))

from psycopg_pool import ConnectionPool
pool = ConnectionPool(f"host={ROOT} port=5621 user=postgres dbname=postgres", min_size=10, max_size=10,
                      kwargs={"autocommit": True}, open=True)
pool.wait()
def pooled():
    with pool.connection() as c:
        c.execute("SELECT pg_sleep(0.05)")
took, errors, slow = traffic(pooled)
print(f"pool of 10: {took:.2f} s, slowest {slow * 1000:.0f} ms, {sum(errors.values())} of 500 failed")
pool.close()

# --- vacuum ---
def state(label):
    size, dead = db.execute("""SELECT pg_table_size('events'), n_dead_tup FROM pg_stat_user_tables
                               WHERE relname = 'events'""").fetchone()
    print(f"{label:38s} {size / 1e6:6.1f} MB  dead rows {dead:9,d}")
def settle():
    db.execute("SELECT pg_stat_force_next_flush()"); time.sleep(0.2)

db.execute("""CREATE TABLE events (id int PRIMARY KEY, v int, pad text);
              INSERT INTO events SELECT i, 0, repeat('x', 40) FROM generate_series(1, 200000) i""")
db.execute("ANALYZE events"); settle(); state("fresh table")
for _ in range(3):
    db.execute("UPDATE events SET v = v + 1")
settle(); state("3 full updates, no vacuum")
db.execute("VACUUM events"); settle(); state("VACUUM")
db.execute("UPDATE events SET v = v + 1"); settle(); state("1 more update reuses the space")
db.execute("VACUUM events")
t = time.perf_counter(); db.execute("VACUUM FULL events"); settle(); state(f"VACUUM FULL ({time.perf_counter() - t:.2f} s, exclusive)")

print("-- a forgotten session")
idle = primary.connect()
idle.autocommit = False
idle.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
idle.execute("SELECT count(*) FROM accounts")                                    # now idle in transaction, holding a snapshot
db.execute("UPDATE events SET v = v + 1"); settle(); state("update while the session sits idle")
db.execute("VACUUM events"); settle(); state("VACUUM cannot remove them")
print(db.execute("""SELECT state, age(backend_xmin), round(extract(epoch FROM now() - xact_start))::int AS seconds
                    FROM pg_stat_activity WHERE backend_xmin IS NOT NULL AND pid <> pg_backend_pid()""").fetchall())
idle.rollback(); idle.close()
db.execute("VACUUM events"); settle(); state("session gone, VACUUM works")
print("oldest unfrozen XID age:", db.execute("SELECT max(age(datfrozenxid)) FROM pg_database").fetchone()[0], "of about 2 billion")

# --- replica_lag ---
tool("pg_basebackup", "-h", ROOT, "-p", "5621", "-U", "postgres", "-D", f"{ROOT}/standby", "-R", "-X", "stream", "-c", "fast")
standby = Server("standby", 5623, "archive_mode=off\nhot_standby=on\nmax_standby_streaming_delay=200ms").configure().start()
replica = standby.connect()
def wait_streaming():
    while not db.execute("SELECT count(*) FROM pg_stat_replication WHERE state = 'streaming'").fetchone()[0]:
        time.sleep(0.05)
wait_streaming()

db.execute("CREATE TABLE profile (id int PRIMARY KEY, name text); INSERT INTO profile VALUES (1, 'v0')")
def read_your_write(trials=200):
    time.sleep(0.5)
    stale = 0
    for i in range(1, trials + 1):
        db.execute("UPDATE profile SET name = %s WHERE id = 1", (f"v{i}",))
        if replica.execute("SELECT name FROM profile WHERE id = 1").fetchone()[0] != f"v{i}":
            stale += 1
    return stale
print(f"idle, read straight after write: {read_your_write()} of 200 stale")

stop = threading.Event()
def burst():
    c = primary.connect()
    while not stop.is_set():
        c.execute("UPDATE events SET v = v + 1")                                 # a backfill-sized write
c = threading.Thread(target=burst); c.start()
peak_lag, peak_bytes = 0.0, 0
for _ in range(20):
    time.sleep(0.25)
    row = db.execute("""SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn),
                               extract(epoch FROM replay_lag) FROM pg_stat_replication""").fetchone()
    peak_bytes = max(peak_bytes, int(row[0] or 0)); peak_lag = max(peak_lag, float(row[1] or 0))
print(f"during a bulk write: {read_your_write()} of 200 stale | peak replay gap {peak_bytes / 1e6:.1f} MB, replay_lag {peak_lag:.3f} s")
stop.set(); c.join()

print("-- a long query on the standby")
reader = standby.connect()
reader.autocommit = False
reader.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
reader.execute("SELECT count(*) FROM events")                                    # analyst holds a snapshot
db.execute("UPDATE events SET v = v + 1"); db.execute("VACUUM events")           # removes rows it can still see
time.sleep(1.5)
try:
    reader.execute("SELECT count(*) FROM events")
    print("still running")
except psycopg.Error as e:
    print(type(e).__name__ + ":", str(e).splitlines()[0])
reader.close()

# --- capacity ---
def wal_of(sql):
    a = db.execute("SELECT pg_current_wal_lsn()").fetchone()[0]
    db.execute(sql)
    b = db.execute("SELECT pg_current_wal_lsn()").fetchone()[0]
    return float(db.execute("SELECT pg_wal_lsn_diff(%s, %s)", (b, a)).fetchone()[0])
wal = wal_of("UPDATE accounts SET balance = balance + 1")
size = db.execute("SELECT pg_table_size('accounts')").fetchone()[0]
print(f"updating {1_000_000:,d} rows wrote {wal / 1e6:.0f} MB of WAL (table size {size / 1e6:.0f} MB)")

print("-- a replication slot with nobody reading it")
db.execute("SELECT pg_create_physical_replication_slot('forgotten', true)")
def slot_retained():
    return float(db.execute("""SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) FROM pg_replication_slots
                               WHERE slot_name = 'forgotten'""").fetchone()[0])
for _ in range(3):
    db.execute("UPDATE accounts SET balance = balance + 1")
    print(f"  WAL held for the slot: {slot_retained() / 1e6:6.0f} MB")
db.execute("SELECT pg_drop_replication_slot('forgotten')")

def days_left(used_gb, disk_gb, gb_per_day, alarm=0.8):
    return (disk_gb * alarm - used_gb) / gb_per_day
print(f"used 410 GB of 1 TB, growing 3 GB a day: {days_left(410, 1000, 3):.0f} days to the 80% alarm")
print(f"the same, with a 300 GB rewrite planned: {days_left(410 + 300, 1000, 3):.0f} days")

# --- tryit ---
# Answer 1: recover to a moment after the mistake instead.
shutil.copytree(f"{ROOT}/base", f"{ROOT}/late")
open(f"{ROOT}/late/recovery.signal", "w").close()
late = Server("late", 5624, f"archive_mode=off\nrestore_command='cp {ROOT}/archive/%f %p'\nrecovery_target_action='promote'").configure().start()
with late.connect() as c:
    while c.execute("SELECT pg_is_in_recovery()").fetchone()[0]:
        time.sleep(0.05)
    print("recovered to the end of the WAL: orders =", c.execute("SELECT count(*) FROM orders").fetchone()[0])
late.stop()

# Answer 2: one table out of a custom-format dump.
db.execute("CREATE DATABASE one_table")
tool("pg_restore", "-h", ROOT, "-p", "5621", "-U", "postgres", "-d", "one_table", "-t", "accounts", f"{ROOT}/nightly.dump")
with primary.connect("one_table") as c:
    print("restored one table:", c.execute("SELECT count(*) FROM accounts").fetchone()[0], "rows, tables:",
          c.execute("SELECT count(*) FROM pg_tables WHERE schemaname = 'public'").fetchone()[0],
          "| primary key kept:", c.execute("SELECT count(*) FROM pg_indexes WHERE tablename = 'accounts'").fetchone()[0] > 0)

# Answer 3: a server-side limit on forgotten sessions.
idle = primary.connect()
idle.execute("SET idle_in_transaction_session_timeout = '300ms'")
idle.autocommit = False
idle.execute("SELECT 1")
time.sleep(0.8)
try:
    idle.execute("SELECT 1")
except psycopg.Error as e:
    print(type(e).__name__ + ":", str(e).splitlines()[0])

# Answer 4: hot_standby_feedback stops the standby query being cancelled, and costs the primary.
replica.execute("ALTER SYSTEM SET hot_standby_feedback = on"); replica.execute("SELECT pg_reload_conf()")
time.sleep(1)
reader = standby.connect()
reader.autocommit = False
reader.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
reader.execute("SELECT count(*) FROM events")
time.sleep(1)
db.execute("UPDATE events SET v = v + 1"); db.execute("VACUUM events")
time.sleep(1.5)
print("standby query after VACUUM:", reader.execute("SELECT count(*) FROM events").fetchone()[0], "rows")
settle(); state("primary's table while the standby reads")
reader.close()

# --- teardown ---
db.close(); held.close(); replica.close()
standby.stop(); primary.stop()
shutil.rmtree(ROOT, ignore_errors=True)
