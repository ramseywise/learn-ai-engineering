---
origin: synthesis
sources:
  - https://about.gitlab.com/blog/2017/02/10/postmortem-of-database-outage-of-january-31/
  - https://sre.google/sre-book/data-integrity/
  - https://www.postgresql.org/docs/current/backup.html
  - https://www.postgresql.org/docs/current/backup-dump.html
  - https://www.postgresql.org/docs/current/continuous-archiving.html
  - https://www.postgresql.org/docs/current/backup-file.html
  - https://www.postgresql.org/docs/current/runtime-config-connection.html
  - https://www.postgresql.org/docs/current/connect-estab.html
  - https://www.pgbouncer.org/features.html
  - https://www.pgbouncer.org/usage.html
  - https://www.postgresql.org/docs/current/routine-vacuuming.html
  - https://www.postgresql.org/docs/current/monitoring-stats.html
  - https://www.postgresql.org/docs/current/warm-standby.html
  - https://www.postgresql.org/docs/current/hot-standby.html
  - https://www.postgresql.org/docs/current/upgrading.html
  - https://www.postgresql.org/docs/current/ddl-partitioning.html
confidence: medium
cleaned: 2026-11-02
---
# Operating data stores

On 31 January 2017 an engineer at GitLab wiped the data directory of the wrong server. [GitLab's postmortem](https://about.gitlab.com/blog/2017/02/10/postmortem-of-database-outage-of-january-31/) is the best short course in this chapter's subject, because nearly every topic here failed that night: replica lag started it, connection settings slowed it, and the backups turned out not to exist. This chapter runs each of those on real servers: a restore drill, a recovery to a chosen moment, connection exhaustion, vacuum and bloat, replica lag, capacity and upgrades.

The confidence is medium. Everything ran on Postgres 16.2 on a laptop with small tables and local sockets, while the docs cited describe the current release. PgBouncer and `pg_upgrade` were read about and not run, and are marked where they appear. Terms for failures and durability come from [persistence](../../01-storage-and-compute-foundations/notes/09-persistence.md), and replication's theory from [partitioning and replication](../../01-storage-and-compute-foundations/notes/05-partitioning-and-replication.md); this chapter is the daily work.

## The bench

One primary, with WAL archiving on and at most 30 connections. Autovacuum is off so that the vacuum section is deterministic. Never do that in production.

```python
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
```

```text
16.2 | max_connections 30
```

## Backups: only a restore proves one

GitLab's account of the night runs like this. Load made the replica fall behind, and the WAL it needed had already been removed from the primary, so an engineer started to re-sync it. While fighting `pg_basebackup`, they ran the wipe on the primary instead, and around 300 GB was gone in a second or two. Then they went to the backups:

- **`pg_dump`:** the S3 bucket was empty. The job used `pg_dump` 9.2 against a 9.6 server, so it failed every time, and the failure emails were rejected by the receiver because of DMARC, so nobody knew.
- **Disk snapshots:** turned on for the file servers, not the database, as the team assumed the others were enough.
- **Replica:** already wiped for the re-sync.
- **LVM snapshot for staging:** the one thing that worked. It was six hours old, and copying it took around 18 hours over disks throttled to about 60 Mbps.

They estimated losing at least 5,000 projects, 5,000 comments and 700 users. [Google's SRE book on data integrity](https://sre.google/sre-book/data-integrity/) makes the general point: "No one really wants to make backups; what people really want are restores." It also says that replication and redundancy are not recoverability, and [persistence](../../01-storage-and-compute-foundations/notes/09-persistence.md) measured why: a bad `DELETE` reached the standby in 34 ms.

So make the restore the scheduled job, and let its success be what alerts. [`pg_dump`](https://www.postgresql.org/docs/current/backup-dump.html) takes a consistent snapshot without blocking normal reads and writes. Here it runs while transfers are moving money between accounts, and the drill checks that the total stayed exact:

```python
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
```

```text
pg_dump under write load: 0.32 s, 2.3 MB
real dump : ok in 0.40 s, invariant = 1,000,000,000
empty file: FAILED: pg_restore: error: input file is too short (read 0, expected 5)
```

The invariant is the important line. Each account starts at 1,000 and each transfer balances, so 1,000,000,000 shows the dump saw one consistent moment despite the writes. A check that the job exited zero, or that a file exists, proves neither. The second call is the GitLab failure at small scale: the job left nothing usable and the drill said so, on a day when it could still be fixed.

A real drill adds three things: run it on a schedule on other hardware, record how long it took (that is your measured recovery time, not the estimate), and page someone if it doesn't report success. A job that stops running must look like a failure, which is why the alert should fire on missing success. [The docs](https://www.postgresql.org/docs/current/backup.html) group Postgres backups into three kinds, and the difference matters:

| Method | What you get | Can do | Can't do |
|---|---|---|---|
| SQL dump (`pg_dump`, `pg_dumpall`) | A logical copy at one moment | Move between major versions; restore one table | Anything after the dump; `pg_dump` alone omits roles and tablespaces |
| [File system backup](https://www.postgresql.org/docs/current/backup-file.html) | The data directory | Copy a whole cluster | Move across major versions; restore one table. It needs the server shut down or an atomic snapshot |
| Base backup plus archived WAL | A physical copy plus every change since | Restore to any moment | Move across major versions |

Keep the [SRE book's defence in depth](https://sre.google/sre-book/data-integrity/) in mind as well. Its first layer is soft deletion, since in Google's experience bugs in applications cause most data loss, and its third is regular validation, because low-grade corruption can go unnoticed for weeks. A study of 19 recovery efforts there found the hardest cases were those discovered long after they began, which is what retention has to allow for: you need a copy from before the problem started.

## Point-in-time recovery: a real drill

A nightly dump loses a day's data. With a base backup and [archived WAL](https://www.postgresql.org/docs/current/continuous-archiving.html), you can recover to a moment of your choice. Here is the case that replication can't help with, on a real server: 5,000 orders arrive after the backup, a bad `DELETE` removes 4,000, and we recover to just before it.

```python
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
```

```text
base backup: 106 MB
orders after the bad DELETE: 1000
WAL segments archived: 13 | last: 00000001000000000000000C.00000028.backup
restored to 21:33:01.812161 in 0.17 s: orders = 5000
recovery stopping before commit of transaction 1895, time 2026-11-02 21:33:03.018791+01
selected new timeline ID: 2
the nightly dump, taken before these orders existed, has none of them
```

The log line shows the server stopping just before the commit of the bad transaction, and the 5,000 orders are back. Some details:

- The recovered server starts a **new timeline**, so its WAL can't be confused with the original's. The original is still around, which means you can copy out the good rows and keep what was written after the mistake. That manual merge is usually the hard part of the night.
- Recovery on a different server, as here, also leaves the damaged one for investigation.
- The docs warn that `archive_command` must return zero only on success, and the `test ! -f` here refuses to overwrite an existing file. A broken archive command is silent until a restore needs it, so watch `pg_stat_archiver`.
- Time to recover grows with the WAL to replay, so frequent base backups reduce it. The 0.17 s here reflects a few hundred MB on a laptop.

Dedicated backup tools wrap this procedure for production use; none was used here.

## Connections: why you pool

Each Postgres connection is [a server process](https://www.postgresql.org/docs/current/connect-estab.html), and [`max_connections`](https://www.postgresql.org/docs/current/runtime-config-connection.html) is fixed at server start and sizes shared memory, so it isn't a value to raise freely. GitLab's was 8,000; their postmortem calls that way too high, and it stopped the server restarting mid-incident with a semaphore error. Three slots stay reserved for superusers by default, which is how you get in during an exhaustion incident.

```python
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
```

```text
new connection each query: 1.27 ms | held connection: 0.02 ms
no pool   : 0.40 s, slowest 99 ms, 349 of 500 failed
    {'sorry, too many clients already': 298, '4kh7df/.s.PGSQL.5621" failed: Connection refused': 51}
pool of 10: 2.58 s, slowest 521 ms, 0 of 500 failed
```

Without a pool, 100 clients at once asked for more than 30 connections, and 70% of requests failed. With ten connections shared, all 500 succeeded, at the cost of some queueing: 2.58 s of total time is close to 500 × 50 ms ÷ 10, which is the capacity the pool exposes. **That's the point of a pool:** it turns failure into waiting. It also makes the bottleneck visible, because the slowest request tells you the queue length. Connecting cost 1.27 ms against 0.02 ms for reuse, and that is on a local socket with trust auth and no TLS, so the real gap is larger.

The in-process `psycopg_pool` above serves one application. With many application instances, each with its own pool, the sum can still exceed `max_connections`, and that's the job of a proxy such as [PgBouncer](https://www.pgbouncer.org/features.html), which was not run here. Its [modes](https://www.pgbouncer.org/usage.html) differ in when a server connection goes back:

| Mode | Server connection is held | Breaks |
|---|---|---|
| Session | Until the client disconnects | Nothing, but saves little |
| Transaction | For each transaction | `SET`, `LISTEN`, session advisory locks, `PREPARE`, `WITH HOLD` cursors, `PRESERVE ROWS` temp tables |
| Statement | For each query | Multi-statement transactions too |

The transaction-mode list bites migrations in particular. `SET lock_timeout` from [the migrations chapter](04-schema-and-data-migrations.md) is session state, so run migrations on a direct connection.

## VACUUM and bloat

Postgres updates create a new row version and leave the old one in place for transactions that may still see it ([isolation](../../01-storage-and-compute-foundations/notes/04-transactions-and-isolation.md) covers why). Dead versions take space until [VACUUM](https://www.postgresql.org/docs/current/routine-vacuuming.html) removes them.

```python
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
```

```text
fresh table                              16.9 MB  dead rows         0
3 full updates, no vacuum                67.6 MB  dead rows   600,000
VACUUM                                   67.6 MB  dead rows         0
1 more update reuses the space           67.6 MB  dead rows   200,000
VACUUM FULL (0.34 s, exclusive)          16.9 MB  dead rows         0
-- a forgotten session
update while the session sits idle       33.8 MB  dead rows   200,000
VACUUM cannot remove them                33.8 MB  dead rows   200,000
[('idle in transaction', 1, 1)]
session gone, VACUUM works               33.8 MB  dead rows         0
oldest unfrozen XID age: 1182 of about 2 billion
```

Each line teaches one thing:

- **Three full updates took the table from 16.9 to 67.6 MB.** The table is now four times the size with the same data.
- **`VACUUM` frees the space for reuse, not for the OS.** The size stays at 67.6 MB, and the next update fits inside. The docs describe this as the goal: a steady state, not a minimal table.
- **`VACUUM FULL` gets the 16.9 MB back** by rewriting the table, under `ACCESS EXCLUSIVE`, needing extra disk for the copy. It stops the application like the rewrite in [the migrations chapter](04-schema-and-data-migrations.md#adding-a-column-and-the-default-that-rewrites-the-table). The docs say the aim of routine vacuuming is to avoid ever needing it.
- **A forgotten session stops everything.** One idle transaction holding a snapshot kept 200,000 dead rows that `VACUUM` could not remove. It held a snapshot and was doing nothing. This is the usual bloat incident, and the query against [`pg_stat_activity`](https://www.postgresql.org/docs/current/monitoring-stats.html) is how to find the culprit. `idle_in_transaction_session_timeout` is the guard.

Autovacuum does this in production, and you tune it per table rather than switching it off. For a table with big periodic deletes, the docs suggest `TRUNCATE` over `DELETE` and `VACUUM`, and [dropping a partition](https://www.postgresql.org/docs/current/ddl-partitioning.html) does the same job for time-based data.

**Wraparound** is the failure to know by name. Transaction IDs are finite, and the docs set the limit at two billion transactions since a table's last aggressive vacuum. Autovacuum normally handles this with no attention. If it can't, the server warns as it nears the limit and eventually stops assigning new transaction IDs to avoid data loss. The docs' recovery list starts with ending long-running transactions and dropping old replication slots, the same things that block ordinary vacuum. So alert on `age(datfrozenxid)` long before it matters. This run printed a few thousand.

## Replica lag

Reading from a standby is the first scaling step for many teams, and its cost is that reads can be stale. Replication's guarantee was covered in [partitioning and replication](../../01-storage-and-compute-foundations/notes/05-partitioning-and-replication.md); here is its size on a real pair:

```python
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
```

```text
idle, read straight after write: 194 of 200 stale
during a bulk write: 199 of 200 stale | peak replay gap 17.2 MB, replay_lag 0.137 s
-- a long query on the standby
SerializationFailure: terminating connection due to conflict with recovery
```

Even on an idle pair on one machine, a read straight after a write was stale 194 times in 200. The lag was tiny, but the read was faster. So never route a read-your-own-write through a replica without a check, whichever metric looks good. Under bulk writes the [gap measured in `pg_stat_replication`](https://www.postgresql.org/docs/current/warm-standby.html) grew to 17 MB. This is the view to alert on, and it should act as the brake on backfills. Its `replay_lag` column is a time, and the byte gap comes from comparing LSNs; alert on whichever matches what you promise your readers.

Then there's the other direction. [On a hot standby](https://www.postgresql.org/docs/current/hot-standby.html), applying WAL can conflict with a running query, as when a vacuum removes rows the query can still see. Replication must go on, so after `max_standby_streaming_delay` the server cancels the query or, as here, ends the session. An analyst running long reports on a replica gets this error at random. The options all cost something: a higher delay means more lag, `hot_standby_feedback` means bloat on the primary (the fourth exercise), and a dedicated replica for reports is more hardware.

## Capacity

Disk is the failure you can see coming, so see it coming. Three numbers from the run explain most surprises:

```python
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
```

```text
updating 1,000,000 rows wrote 278 MB of WAL (table size 73 MB)
-- a replication slot with nobody reading it
  WAL held for the slot:    460 MB
  WAL held for the slot:    724 MB
  WAL held for the slot:    978 MB
used 410 GB of 1 TB, growing 3 GB a day: 130 days to the 80% alarm
the same, with a 300 GB rewrite planned: 30 days
```

- **WAL is bigger than the data.** Updating every row of a 73 MB table wrote 278 MB of WAL, nearly four times the table. Backfills fill the WAL disk and the archive, and they push the replicas behind.
- **A replication slot with nobody reading it holds WAL forever.** [Slots](https://www.postgresql.org/docs/current/warm-standby.html) ensure WAL stays until a consumer receives it, and that's their purpose. If the consumer dies, a full disk stops the primary. GitLab's incident started from the opposite problem, WAL removed with no archive to fall back on. Slots fix that and bring this one. Alert on the retained amount, and consider [`max_slot_wal_keep_size`](https://www.postgresql.org/docs/current/warm-standby.html), which limits it.
- **Plan headroom for operations, not for data alone.** The two forecasts use made-up inputs, and the point is the gap: a rewrite that needs a table's size again cuts 130 days to 30. `VACUUM FULL`, a type change and a concurrent reindex all need that room.

A short list to graph, and alert on the trend rather than the instant: disk used and days left; WAL per hour; connections against the limit; replication lag; age of the oldest transaction; `n_dead_tup` per table; `age(datfrozenxid)`; `pg_stat_archiver` failures; and the time of the last successful restore drill.

## Upgrades

[The docs](https://www.postgresql.org/docs/current/upgrading.html) draw the line clearly. Minor releases never change the storage format, so you replace the binaries and restart; do that promptly. Major releases can change the format, and there are three ways over:

| Method | Downtime | Note |
|---|---|---|
| `pg_dumpall` and restore | Longest, grows with data | Simple; use the newer version's tools |
| `pg_upgrade` | The docs say minutes, particularly with `--link` | In place, so take a backup first and test it |
| Logical replication to the new version | The docs say several seconds at the switch | Most moving parts; lets you roll back while the old side is alive |

None of these ran here, as the bench has one Postgres version. The procedure is the same as [expand, migrate, contract](04-schema-and-data-migrations.md): stand up the new, keep them in sync, verify, switch and keep the old until you're sure. The docs ask you to read the "Migration" section of every release's notes in between and to test client applications against the new version, and GitLab's failure gives one more item for the list: check the version of every tool that talks to the server, your backup job above all.

## Pitfalls

- **Monitoring the backup job instead of the restore.** An exit code is not evidence. Run a drill and check an invariant.
- **Alerts that go through something that can silently fail.** GitLab's backup failure emails were being rejected. Alert on the absence of success.
- **Counting the replica as the backup.** It replays your mistake within milliseconds.
- **Raising `max_connections` to fix a connection storm.** More processes contending for the same CPU and disk rarely help. Pool, and queue in front.
- **`pg_restore -t` for one table.** It restores the table without its primary key or indexes; the second exercise showed that.
- **Disabling autovacuum because it was slow.** Tune it instead.
- **Forgotten slots, sessions and replicas.** Each of these holds back cleanup and fills a disk, slowly and without alarm. Add alerts for all three.
- **Runbook steps with no checking.** GitLab's engineer was on the wrong host. Make the host obvious in the prompt, and let a second person read destructive commands.

## Try it

Run `05_operating_data_stores.py` first. Its final section runs the checks behind these answers.

1. Recover from the same backup without `recovery_target_time`. How many orders come back, and why?
2. Restore only `accounts` from `nightly.dump` with `pg_restore -t`. Is the primary key there?
3. Set `idle_in_transaction_session_timeout` to 300 ms on a session, start a transaction, wait and try again. What does the client see?
4. Turn on `hot_standby_feedback` on the standby and repeat the long-query experiment. What happens on both sides?

<details>
<summary>Answers</summary>

1. It returned 1,000 orders. Without a target, recovery replays all available WAL, so it faithfully replays the mistake. This is the default, and the target is what makes it point-in-time.
2. No. It printed 1,000,000 rows and `primary key kept: False`. Table restore here brings the table and its data, so restore or recreate indexes and constraints with it, or restore to a scratch database and copy rows across.
3. `IdleInTransactionSessionTimeout: terminating connection due to idle-in-transaction timeout`. The server ended the session, so its snapshot no longer holds back vacuum. Applications should handle the error.
4. The standby's query finished with 200,000 rows and no error. On the primary, `events` reached 169 MB with 200,000 dead rows that `VACUUM` had left. Feedback moved the cost from the standby's query to bloat on the primary, so a stuck reader on a replica can now bloat the primary.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| How do you know a backup works? | Restore it on a schedule to separate hardware, check an invariant in the data, measure the time, and alert on missing success. |
| Why isn't a replica a backup? | It replays mistakes quickly. It protects against losing a machine, not against a bad `DELETE`. |
| What does point-in-time recovery need? | A base backup, every archived WAL segment since, a `restore_command` and a target. It starts a new timeline. |
| Dump or physical backup? | Dump for logical copies, one table or a version move. Physical plus WAL for any point in time and a large database. Many teams run both. |
| What happens at `max_connections`? | New clients get an error. Fix it with pooling, which turns errors into queueing. Raising the limit allocates more resources and adds contention. |
| What does transaction pooling break? | Session state: `SET`, `LISTEN`, session advisory locks and `PREPARE`. Migrations should use a direct connection. |
| Why does a Postgres table grow with no new rows? | Updates leave dead row versions until vacuum. Plain `VACUUM` reuses space and `VACUUM FULL` returns it, under an exclusive lock. |
| What stops vacuum from working? | The oldest open transaction or snapshot, old replication slots, or `hot_standby_feedback` from a standby. |
| What is wraparound? | Transaction IDs are finite. If autovacuum can't freeze rows, Postgres eventually refuses new transaction IDs. Alert on `age(datfrozenxid)`. |
| How do you measure replica lag? | `pg_stat_replication`: LSN differences in bytes, and the `write_lag`, `flush_lag` and `replay_lag` times. |
| Why was a standby query cancelled? | A conflict with WAL replay, typically from a vacuum on the primary, past `max_standby_streaming_delay`. |
| What fills a Postgres disk unexpectedly? | WAL from bulk writes, a slot with no consumer, bloat, and rewrites needing a second copy. |
| How do you do a major upgrade? | `pg_upgrade`, dump and restore, or logical replication. Read every release's migration notes and test clients first. |

## Next

[DataOps](06-dataops.md) puts these operations into environments, CI, service levels and on-call. For the incident itself, [the playbooks](03-incident-playbooks.md) give the shape of the response.
