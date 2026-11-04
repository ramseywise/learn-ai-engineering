---
origin: synthesis
sources:
  - "Kleppmann, Designing Data-Intensive Applications (O'Reilly, 2017), the sidebar 'Replication and Durability' in ch. 7 and the introduction to Part III"
  - https://www.usenix.org/conference/atc20/presentation/rebello
  - https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai
  - https://www.postgresql.org/docs/current/wal-intro.html
  - https://www.postgresql.org/docs/current/wal-reliability.html
  - https://www.postgresql.org/docs/current/wal-async-commit.html
  - https://www.postgresql.org/docs/current/runtime-config-wal.html
  - https://www.postgresql.org/docs/current/warm-standby.html
  - https://www.postgresql.org/docs/current/continuous-archiving.html
  - https://wiki.postgresql.org/wiki/Fsync_Errors
  - https://man7.org/linux/man-pages/man2/fsync.2.html
  - https://www.sqlite.org/howtocorrupt.html
  - https://docs.aws.amazon.com/AmazonS3/latest/userguide/DataDurability.html
  - https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/business-continuity-plan-bcp.html
  - https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/
confidence: high
cleaned: 2026-11-02
---
# 9 — Persistence: what "saved" means

An API returns 200 and the row is "saved". Saved where? In a Python buffer, a process dies and it is gone. In the operating system's page cache, a power cut takes it. On a disk, the disk can fail, and on a replica, your own bad `DELETE` follows it across in milliseconds. "Saved" is not one state but a ladder, and each rung survives a different failure and costs a different amount. This chapter climbs the ladder by crashing things on purpose and counting what was lost. All the code is in [`practice/09_persistence.py`](../practice/09_persistence.py) and uses a private Postgres 16.2 in a temporary directory, so it runs with nothing installed.

```mermaid
flowchart LR
  A[Process memory] -->|flush| B[OS page cache]
  B -->|fsync| C[Device]
  C -->|log first| D[WAL]
  D -->|stream| E[Replica]
  E -->|archive| F[Object store]
  F -->|retain and restore| G[Backup you have tested]
```

The test for every rung is the same question from a client's point of view: of the writes you acknowledged, how many are still there after this failure? Acknowledgement is what matters. Losing a write nobody was told about is a failed request. Losing one you confirmed is a broken promise.

Two numbers describe the answer. AWS's [disaster recovery guidance](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/business-continuity-plan-bcp.html) defines the recovery point objective (RPO) as the longest acceptable time since the last recovery point, and the recovery time objective (RTO) as the longest acceptable delay before service returns. RPO is how much you lose. RTO is how long you are down.

## Memory and the page cache: what a process crash takes

A write in Python passes through two caches before any device sees it. `f.write` puts bytes in a buffer inside the process. `f.flush` hands them to the operating system, which holds them in its page cache and returns at once. `os.fsync` asks the OS to push them to the device and waits.

So here is a writer that acknowledges each record to its client after one of those three steps. The parent `SIGKILL`s it at a random moment, 20 times per setting. `SIGKILL` cannot be caught, so nothing gets a chance to tidy up.

```python
import signal, subprocess, sys, random, time

WRITER = """
import os, sys
mode, path = sys.argv[1], sys.argv[2]
f = open(path, "w", buffering=8192)
i = 0
while True:
    f.write(f"record {i:08d}\\n")           # into this process's memory
    if mode in ("flush", "fsync"):
        f.flush()                           # into the operating system's page cache
    if mode == "fsync":
        os.fsync(f.fileno())                # asks the OS to push it to the device
    sys.stdout.write(f"{i}\\n"); sys.stdout.flush()   # tell the client it is saved
    i += 1
"""
open("writer.py", "w").write(WRITER)

def crash_writer(mode):
    """Start a writer, SIGKILL it at a random moment, compare what it acknowledged with the file."""
    with open("acks.txt", "w") as acks:                # a file, not a pipe: a full pipe would stall the writer
        p = subprocess.Popen([sys.executable, "writer.py", mode, "log.txt"], stdout=acks)
        time.sleep(0.05 + random.random() / 10)
        p.send_signal(signal.SIGKILL)
        p.wait()
    with open("acks.txt") as f:
        acked = f.read().count("\n")
    with open("log.txt") as f:
        saved = sum(1 for line in f if len(line) == 16)        # 16 bytes is one complete record
    return acked, max(acked - saved, 0)

random.seed(9)
print(f"{'stops at':10s} {'trials':>6s} {'acknowledged':>13s} {'lost':>7s}")
for mode in ["memory", "flush", "fsync"]:
    results = [crash_writer(mode) for _ in range(20)]
    print(f"{mode:10s} {len(results):6d} {sum(a for a, _ in results):13,d} {sum(l for _, l in results):7,d}")
```

```text
stops at   trials  acknowledged    lost
memory         20       991,331   4,707
flush          20       543,470       0
fsync          20        63,756       0
```

The `memory` writer told its client about 4,700 records that were never in the file: about 235 per crash, which fits a buffer of 8 KB at 16 bytes per record, or 512 records, caught on average half full. The counts vary by machine and run. One `flush` per record closes the gap entirely, for this failure.

Now the honest catch: **this test cannot tell `flush` from `fsync`.** A killed process does not take the page cache with it. The kernel still holds those pages and writes them later, so both show zero. If you stop here you would conclude `fsync` buys nothing, and that is wrong. What it buys only shows when the machine itself goes down.

## fsync: what a power cut takes, and what it costs

I did not cut the power to this laptop, and no result in this chapter comes from a physical power loss. A fair test needs fault injection at the block layer, which is what [Rebello et al. (USENIX ATC 2020)](https://www.usenix.org/conference/atc20/presentation/rebello) built for their study. What follows for this rung is a model, labelled as one, plus what the sources say.

The model is a volatile cache and a durable store. Writes land in the cache; `fsync` moves them across; a power cut keeps a random half of whatever had not moved, since the kernel and drive may write pages in any order.

```python
class ToyDisk:
    """A SIMULATION of power loss. A kill does not empty the page cache, so a real kill cannot show this.
    Writes sit in a volatile cache; fsync makes them durable; a power cut keeps a random subset of the rest."""
    def __init__(self, rng):
        self.durable, self.cache, self.rng = {}, {}, rng
    def write(self, pos, data):
        self.cache[pos] = data
    def fsync(self):
        self.durable.update(self.cache)
        self.cache.clear()
    def power_cut(self):
        survivors = {p: d for p, d in self.cache.items() if self.rng.random() < 0.5}
        return {**self.durable, **survivors}

def run(rng, sync_every):
    d = ToyDisk(rng)
    for i in range(100):
        d.write(i, f"rec{i}")
        if sync_every and (i + 1) % sync_every == 0:
            d.fsync()
    state = d.power_cut()
    prefix = next((i for i in range(100) if i not in state), 100)
    return prefix, len(state), len(state) > prefix            # holes: later records survive past a lost one

rng = random.Random(4)
print("simulated power cut, 100 writes, 1,000 trials")
for label, every in [("no fsync", 0), ("fsync every 10", 10), ("fsync every write", 1)]:
    runs = [run(rng, every) for _ in range(1000)]
    print(f"  {label:18s} mean records in order {sum(r[0] for r in runs) / 1000:6.1f}   "
          f"trials with holes {sum(r[2] for r in runs) / 10:5.1f}%")
```

```text
simulated power cut, 100 writes, 1,000 trials
  no fsync           mean records in order    1.0   trials with holes 100.0%
  fsync every 10     mean records in order  100.0   trials with holes   0.0%
  fsync every write  mean records in order  100.0   trials with holes   0.0%
```

The "holes" column is the part worth noticing. Without `fsync` the loss is not just a missing tail: later records survive while earlier ones vanish, so the file does not match any moment in the program's history. Ordering is what a barrier gives you. SQLite's [How To Corrupt](https://www.sqlite.org/howtocorrupt.html) page says the same: as long as writes before a sync complete before writes after it, a crash may lose recent transactions but will not corrupt the database. "Fsync every 10" shows 100 records only because the 100th write happened to trigger a sync; stop at 95 and the last five are at risk.

Then the cost, measured on this machine.

```python
import fcntl

fd = os.open("cost.bin", os.O_CREAT | os.O_WRONLY | os.O_APPEND)
block = b"x" * 4096

def per_write(sync, n):
    t = time.perf_counter()
    for _ in range(n):
        os.write(fd, block)
        sync()
    return (time.perf_counter() - t) / n * 1e6

print(f"write only             {per_write(lambda: None, 20000):9.1f} us per 4 KiB write")
print(f"write + fsync          {per_write(lambda: os.fsync(fd), 2000):9.1f} us")
if hasattr(fcntl, "F_FULLFSYNC"):    # macOS: fsync stops at the drive; this asks the drive to flush its cache
    print(f"write + F_FULLFSYNC    {per_write(lambda: fcntl.fcntl(fd, fcntl.F_FULLFSYNC), 300):9.1f} us")
os.close(fd)
```

```text
write only                   3.4 us per 4 KiB write
write + fsync               55.3 us
write + F_FULLFSYNC       3825.5 us
```

The last line is the surprise, and it is specific to the platform. On Linux, [`fsync(2)`](https://man7.org/linux/man-pages/man2/fsync.2.html) says it includes flushing the disk cache where one is present. The macOS `fsync(2)` man page (read locally with `man 2 fsync`) warns that the drive may hold data for some time and write it out of order, and offers the `F_FULLFSYNC` fcntl, which "asks the drive to flush all buffered data to permanent storage". That is why a plain `fsync` on this Mac costs tens of microseconds and a true flush costs nearly 4 ms. Do not read the 55 µs as the price of durability. It is the price of stopping short of it.

Three further traps sit below your code, and each one has a source to read:

- **Drives can lie.** The [Postgres reliability docs](https://www.postgresql.org/docs/current/wal-reliability.html) warn that many SSDs have volatile write-back caches and that many do not honour cache flush commands by default. SQLite puts it more bluntly: "most consumer-grade mass storage devices lie about syncing".
- **fsync can fail, and retrying can lie.** Postgres assumed a failed `fsync` could be retried. It cannot, because on Linux the failed pages get marked clean, so the retry reports success with the data gone. Since the 2018 ["fsyncgate"](https://wiki.postgresql.org/wiki/Fsync_Errors) fix Postgres panics and recovers from the WAL instead. Rebello et al. tested ext4, XFS and Btrfs against PostgreSQL, LMDB, LevelDB, SQLite and Redis and found the techniques in use for handling fsync failure are, in their words, none sufficient.
- **The file is not its directory entry.** The Linux man page notes that `fsync` on a file does not necessarily make its directory entry durable, and that you need a second `fsync` on the directory. New files and renames can vanish without it. [Pillai et al. (OSDI 2014)](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai) checked eleven widely used systems for code relying on properties the file system did not promise, and found 60 such crash vulnerabilities across them.

## The write-ahead log: making a crash boring

If every commit had to `fsync` every changed page at random places on disk, databases would be unusably slow, and a crash midway through would leave a table half updated. The [write-ahead log](https://www.postgresql.org/docs/current/wal-intro.html) solves both: append a description of the change to one sequential file, sync that, and only then tell the client. Data pages can follow lazily, because after a crash the log can replay them. One sync of the log can also commit many transactions at once.

Here is the whole idea in a few lines: a record is length, checksum and payload, and recovery replays until the first record that does not check out.

```python
import struct, zlib

HEADER = struct.Struct("<II")                     # payload length, CRC-32 of payload

def append(fd, key, value):
    payload = f"{key}={value}".encode()
    os.write(fd, HEADER.pack(len(payload), zlib.crc32(payload)) + payload)
    os.fsync(fd)                                  # commit point: only now may the client be told

def recover(path):
    """Replay records until the first one that is short or fails its checksum, then cut the file there."""
    state, pos = {}, 0
    with open(path, "rb") as f:
        raw = f.read()
    while pos + HEADER.size <= len(raw):
        length, crc = HEADER.unpack_from(raw, pos)
        payload = raw[pos + HEADER.size:pos + HEADER.size + length]
        if len(payload) < length or zlib.crc32(payload) != crc:
            break
        key, value = payload.decode().split("=")
        state[key] = value
        pos += HEADER.size + length
    os.truncate(path, pos)
    return state

fd = os.open("toy.wal", os.O_CREAT | os.O_WRONLY | os.O_TRUNC | os.O_APPEND)
for i in range(50):
    append(fd, f"k{i % 7}", i)
os.close(fd)
whole = open("toy.wal", "rb").read()
expected_states = []
pos = 0
while pos < len(whole):                           # the state after each whole record
    length, _ = HEADER.unpack_from(whole, pos)
    pos += HEADER.size + length
    expected_states.append(pos)

bad = 0
for cut in range(len(whole) + 1):                 # tear the log at every possible byte
    with open("torn.wal", "wb") as f:
        f.write(whole[:cut])
    state = recover("torn.wal")
    kept = os.path.getsize("torn.wal")
    if kept > cut or (kept and kept not in expected_states) or (cut in expected_states and kept != cut):
        bad += 1
print(f"tore the log at each of {len(whole) + 1:,} byte positions: {bad} bad recoveries")

flip = bytearray(whole)
flip[len(whole) // 2] ^= 0x01                     # one flipped bit in the middle of the log
with open("flipped.wal", "wb") as f:
    f.write(flip)
state = recover("flipped.wal")
print(f"one bit flipped mid-log: kept {os.path.getsize('flipped.wal'):,} of {len(whole):,} bytes, "
      f"state k6 = {state['k6']}")
```

```text
tore the log at each of 641 byte positions: 0 bad recoveries
one bit flipped mid-log: kept 315 of 640 bytes, state k6 = 20
```

The first line tears the log at every possible byte, the same result a crash mid-append could leave, and recovery always lands on a clean record boundary. The second flips one bit in the middle of the log. Recovery stops there and keeps the prefix: 315 bytes out of 640, with `k6` at an older value. That is the right behaviour for a log, since replaying past a damaged record could produce a state that never existed. The checksum is not decoration: Postgres [does the same with CRC-32C on WAL records](https://www.postgresql.org/docs/current/wal-reliability.html).

The same discipline applies to whole files, and you will use this one yourself. Pipeline checkpoints and config files get replaced, and replacing a file in place is unsafe, because opening it for writing empties it. The safe pattern is to write a temporary file, sync it, rename it over the old one, and sync the directory.

```python
ATOMIC = """
import os, sys, time
mode, path = sys.argv[1], sys.argv[2]
print("go", flush=True)
target = path if mode == "in_place" else path + ".tmp"
with open(target, "wb") as f:                   # in place: opening truncates, the old version is gone at once
    for _ in range(40):
        f.write(b"new-" * 1024); f.flush()
        time.sleep(0.001)                       # stands in for a file too big to write in one go
    os.fsync(f.fileno())
if mode == "rename":
    os.replace(target, path)                    # atomic on POSIX: a reader sees old or new, never a mix
    d = os.open(os.path.dirname(path) or ".", os.O_RDONLY)
    os.fsync(d); os.close(d)                    # make the rename itself durable
"""
open("atomic.py", "w").write(ATOMIC)
OLD, NEW = b"old-" * 1024 * 40, b"new-" * 1024 * 40

def replace_trials(mode, n=40):
    outcome = {"old": 0, "new": 0, "corrupt": 0}
    for _ in range(n):
        with open("config.bin", "wb") as f:
            f.write(OLD)
        p = subprocess.Popen([sys.executable, "atomic.py", mode, "config.bin"], stdout=subprocess.PIPE)
        p.stdout.readline()                     # the child is about to start writing
        time.sleep(random.random() * 0.06)
        p.send_signal(signal.SIGKILL); p.wait()
        data = open("config.bin", "rb").read()
        outcome["old" if data == OLD else "new" if data == NEW else "corrupt"] += 1
    return outcome

random.seed(3)
for mode in ["in_place", "rename"]:
    print(f"{mode:9s} {replace_trials(mode)}")
```

```text
in_place  {'old': 0, 'new': 12, 'corrupt': 28}
rename    {'old': 28, 'new': 12, 'corrupt': 0}
```

Kill it partway and in-place writing leaves a corrupt mix in 28 of 40 trials. Rename gives the old version or the new one, never anything else. `SIGKILL` proves atomicity here, not durability across a power cut; for that you depend on the two `fsync` calls, for the reasons above.

## Real Postgres: what `synchronous_commit` trades

The toy log shows the mechanism. Now a real server. The practice file has a small `Server` class around `initdb` and `pg_ctl`, whose `kill9` sends `SIGKILL` to the postmaster and every child. This loop inserts rows one at a time and notes each id only after the commit returns.

```python
ids = iter(range(1, 10**12))

def hammer(server, commit_mode, acked, stop):
    """Insert rows one at a time, noting each id only after COMMIT has returned."""
    try:
        with server.connect() as c:
            c.execute(f"SET synchronous_commit = {commit_mode}")
            while not stop.is_set():
                i = next(ids)
                c.execute("INSERT INTO trips VALUES (%s)", (i,))
                acked.append(i)
    except psycopg.Error:
        pass                                         # the crash, seen from the client

def crash_during_load(server, commit_mode, seconds=0.8, clients=1):
    acked, stop = [], threading.Event()
    threads = [threading.Thread(target=hammer, args=(server, commit_mode, acked, stop)) for _ in range(clients)]
    for t in threads:
        t.start()
    time.sleep(seconds)
    server.kill9()
    stop.set()
    for t in threads:
        t.join()
    return acked
```

```python
main = Server("main", 5601).init()
main.start()
main.connect().execute("CREATE TABLE trips (id bigint PRIMARY KEY)")
print("kill -9 every Postgres process during a single-row insert loop")
print(f"{'synchronous_commit':20s} {'trial':>5s} {'acknowledged':>13s} {'lost':>5s} {'restart s':>10s}")
for mode in ["on", "off"]:
    for trial in range(5):
        acked = crash_during_load(main, mode)
        recovery = main.start()
        c = main.connect()
        present = {r[0] for r in c.execute("SELECT id FROM trips")}
        print(f"{mode:20s} {trial:5d} {len(acked):13,d} {sum(i not in present for i in acked):5d} {recovery:10.2f}")
        c.execute("TRUNCATE trips")
        c.close()
```

```text
kill -9 every Postgres process during a single-row insert loop
synchronous_commit   trial  acknowledged  lost  restart s
on                       0        12,046     0       0.11
on                       1        12,445     0       0.11
on                       2        10,143     0       0.11
on                       3        10,757     0       0.11
on                       4        12,960     0       0.12
off                      0        22,659    30       0.12
off                      1        23,840    29       0.11
off                      2        22,611     5       0.12
off                      3        22,401    36       0.12
off                      4        21,938     9       0.11
```

With `synchronous_commit = on`, five crashes lost nothing out of about 58,000 acknowledged commits. With `off`, about twice as many commits got through and every crash lost some: 5 to 36 rows that the client had been told were safe. Yet the database came back consistent each time. That matches the [asynchronous commit docs](https://www.postgresql.org/docs/current/wal-async-commit.html): the risk is losing recent transactions, not corruption, because replay stops cleanly at a commit boundary. The docs bound the window at three times `wal_writer_delay` (200 ms by default), and give the right way to decide: bank transfers no, event logging quite possibly.

Do not confuse this with `fsync = off`. That setting can corrupt the database, because the server no longer controls write ordering. `synchronous_commit = off` trades a little recent data for speed; `fsync = off` risks the whole cluster.

A `SIGKILL` of Postgres leaves the kernel's page cache intact, so `off` losses here come from WAL that had not yet been written to the OS. On a power cut, `on` still relies on the sync reaching stable media. Which brings back the Mac:

```python
def commits_per_second(commit_mode, seconds=3):
    acked, stop = [], threading.Event()
    t = threading.Thread(target=hammer, args=(main, commit_mode, acked, stop))
    t.start()
    time.sleep(seconds)
    stop.set()
    t.join()
    return len(acked) / seconds

for label, mode, method in [("off", "off", "fsync"), ("on, fsync", "on", "fsync"),
                            ("on, fsync_writethrough", "on", "fsync_writethrough")]:
    with main.connect() as c:
        try:
            c.execute(f"ALTER SYSTEM SET wal_sync_method = {method}")
        except psycopg.Error:
            print(f"{label:24s} not available on this platform")
            continue
        c.execute("SELECT pg_reload_conf()")
    time.sleep(0.3)
    print(f"{label:24s} {commits_per_second(mode):9,.0f} commits per second")
with main.connect() as c:
    c.execute("ALTER SYSTEM RESET wal_sync_method")
    c.execute("SELECT pg_reload_conf()")
```

```text
off                         27,037 commits per second
on, fsync                   14,737 commits per second
on, fsync_writethrough         296 commits per second
```

The default `wal_sync_method` on macOS shows 14,737 commits per second because it does not flush the drive. Asking for write-through drops that to 296, about 50 times slower, and that's the honest speed of durable commits on this drive with one client. If a benchmark shows a suspiciously fast fsync, this is usually why. The [reliability docs](https://www.postgresql.org/docs/current/wal-reliability.html) tell macOS users to set `fsync_writethrough`, and the machine was busy with other work during these runs, so take the ratios rather than the absolute figures.

The WAL also sets your crash RTO. Everything since the last checkpoint must be replayed on restart.

```python
def recovery_time(seconds):
    """Write for a while with checkpoints held off, crash, time the restart: the WAL replay is the RTO."""
    c = main.connect()
    c.execute("TRUNCATE trips")
    c.execute("CHECKPOINT")
    lsn0 = c.execute("SELECT pg_current_wal_lsn()").fetchone()[0]
    stop = threading.Event()
    def load():
        try:
            with main.connect() as w:
                w.execute("SET synchronous_commit = off")
                while not stop.is_set():
                    w.execute("INSERT INTO trips SELECT nextval('rto') FROM generate_series(1, 5000)")
        except psycopg.Error:
            pass
    threads = [threading.Thread(target=load) for _ in range(4)]
    for t in threads:
        t.start()
    time.sleep(seconds)
    wal = c.execute("SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), %s)", (lsn0,)).fetchone()[0]
    c.close()
    main.kill9()
    stop.set()
    for t in threads:
        t.join()
    return float(wal) / 1e6, main.start()

c = main.connect()
c.execute("CREATE SEQUENCE IF NOT EXISTS rto")
c.execute("ALTER SYSTEM SET max_wal_size = '32GB'")
c.execute("ALTER SYSTEM SET checkpoint_timeout = '1h'")
c.close()
tool("pg_ctl", "-w", "-D", main.dir, "restart", "-l", f"{main.dir}/server.log")
print(f"{'WAL since checkpoint':>22s} {'restart after crash':>21s}")
for seconds in [1, 5, 15]:
    mb, secs = recovery_time(seconds)
    print(f"{mb:19,.0f} MB {secs:19.2f} s")
c = main.connect(); c.execute("TRUNCATE trips"); c.execute("ALTER SYSTEM RESET ALL"); c.execute("CHECKPOINT"); c.close()
main.stop()
```

```text
  WAL since checkpoint   restart after crash
                131 MB                0.43 s
                690 MB                1.79 s
              2,099 MB                6.03 s
```

Restart time grows about linearly with WAL volume: 6 seconds for 2.1 GB here. The same arithmetic holds on a busier server with more WAL pending. `checkpoint_timeout` and `max_wal_size` are therefore RTO settings as much as performance settings.

## Replicas: surviving the machine, not your mistakes

Everything so far dies with the machine. A replica keeps the WAL stream on another one. How replication works, and what lag looks like to a reader, is in [partitioning and replication](05-partitioning-and-replication.md), and failure detection is in [when distributed systems fail](06-when-distributed-systems-fail.md). The question here is narrower: what does failover lose? This builds a real standby with `pg_basebackup`, kills the primary under load, promotes the standby and counts. In the stalled cases the standby's WAL receiver is paused with `SIGSTOP` for a second first, as a stuck network would.

```python
def make_standby(primary, name, port):
    tool("pg_basebackup", "-h", ROOT, "-p", str(primary.port), "-U", "postgres", "-D", f"{ROOT}/{name}", "-R", "-X", "stream")
    s = Server(name, port)
    s.configure()
    s.start()
    return s

def wait_streaming(primary):
    with primary.connect() as c:
        while not c.execute("SELECT count(*) FROM pg_stat_replication WHERE state='streaming'").fetchone()[0]:
            time.sleep(0.05)

def failover_trial(sync, freeze):
    """Primary dies during load. The standby is promoted. Which acknowledged writes does it still have?"""
    name = f"p{int(sync)}{int(freeze)}"
    primary = Server(name, 5610).init()
    primary.start()
    primary.connect().execute("CREATE TABLE trips (id bigint PRIMARY KEY)")
    standby = make_standby(primary, name + "s", 5611)
    wait_streaming(primary)
    if sync:
        c = primary.connect()
        c.execute("ALTER SYSTEM SET synchronous_standby_names = '*'")
        c.execute("SELECT pg_reload_conf()")
        time.sleep(0.5)
        c.close()
    acked, stop = [], threading.Event()
    t = threading.Thread(target=hammer, args=(primary, "on", acked, stop))
    t.start()
    time.sleep(0.5)
    receiver, during_stall = None, 0
    if freeze:                    # a stalled network: pause the standby's WAL receiver for the last second
        with standby.connect() as c:
            receiver = c.execute("SELECT pid FROM pg_stat_activity WHERE backend_type='walreceiver'").fetchone()[0]
        os.kill(receiver, signal.SIGSTOP)
        before = len(acked)
        time.sleep(1.0)
        during_stall = len(acked) - before
    primary.kill9()
    if receiver:
        os.kill(receiver, signal.SIGCONT)
    stop.set()
    t.join()
    time.sleep(0.5)
    t0 = time.perf_counter()
    tool("pg_ctl", "-w", "-D", standby.dir, "promote")
    promote = time.perf_counter() - t0
    with standby.connect() as c:
        present = {r[0] for r in c.execute("SELECT id FROM trips")}
    standby.stop()
    return len(acked), during_stall, sum(i not in present for i in acked), promote

print(f"{'replication':34s} {'acknowledged':>13s} {'in the stall':>13s} {'lost after failover':>20s} {'promote s':>10s}")
for label, sync, freeze in [("asynchronous", False, False),
                            ("asynchronous, standby stalled 1 s", False, True),
                            ("synchronous", True, False),
                            ("synchronous, standby stalled 1 s", True, True)]:
    a, stalled, lost, promote = failover_trial(sync, freeze)
    print(f"{label:34s} {a:13,d} {stalled:13,d} {lost:20,d} {promote:10.2f}")
```

```text
replication                         acknowledged  in the stall  lost after failover  promote s
asynchronous                               7,315             0                    0       0.11
asynchronous, standby stalled 1 s         21,878        15,432               15,620       0.11
synchronous                                4,059             0                    0       0.11
synchronous, standby stalled 1 s           3,915             0                    0       0.21
```

Read the table from the top. Asynchronous replication lost nothing when the network was healthy, which is what makes it dangerous: most days it looks like a free lunch. Once the standby was stalled for a second the primary kept acknowledging commits, 15,432 of them, and failover lost 15,620. The [Postgres docs](https://www.postgresql.org/docs/current/warm-standby.html) state it directly: the amount lost is proportional to replication delay at failover. One run per row, so read this as a demonstration and not a rate.

Synchronous replication lost nothing in either case. The price is in the "in the stall" column: during that second the primary acknowledged nothing at all, because each commit waits for the standby. You have turned a replica problem into a primary outage. RPO zero costs availability, and that is the choice you are making, not a detail of the setup.

Promotion itself took about a tenth of a second here. That is not the RTO, since detecting the failure and deciding to fail over usually dominate; the detection problem is in [chapter 6](06-when-distributed-systems-fail.md).

A replica also copies your mistakes, faithfully and quickly.

```python
primary = Server("pd", 5620).init()
primary.start()
c = primary.connect()
c.execute("CREATE TABLE trips AS SELECT g AS id FROM generate_series(1, 100000) g")
standby = make_standby(primary, "pds", 5621)
wait_streaming(primary)
r = standby.connect()
print("standby rows before:", r.execute("SELECT count(*) FROM trips").fetchone()[0])
c.execute("DELETE FROM trips")                       # the bad deploy
t = time.perf_counter()
while r.execute("SELECT count(*) FROM trips").fetchone()[0]:
    time.sleep(0.001)
print(f"standby rows after the bad DELETE: 0, within {(time.perf_counter() - t) * 1000:.0f} ms")
standby.stop(); primary.stop()
```

```text
standby rows before: 100000
standby rows after the bad DELETE: 0, within 34 ms
```

## Object store and backup: surviving yourself

Kleppmann's sidebar on [replication and durability](https://dataintensive.net/) (*DDIA*, ch. 7) says no single technique is absolute: faults correlate, SSDs can violate their guarantees on power loss, and 30 to 80% of SSDs develop at least one bad block in their first four years. Disks, replicas and backups each fail differently, and he says to use them together.

The rungs left are copies outside the system that can be damaged. S3 is [designed for 99.999999999% durability](https://docs.aws.amazon.com/AmazonS3/latest/userguide/DataDurability.html) across at least three availability zones (One Zone-IA is the exception). Be careful what that number covers. It describes S3 losing an object, not you overwriting one. The same page points to versioning for recovering from "unintended user actions and application failures", and to Object Lock. Eleven nines of durability will preserve your bad `DELETE` perfectly.

For a database, the copy is a base backup plus archived WAL, which allows [point-in-time recovery](https://www.postgresql.org/docs/current/continuous-archiving.html) to just before the mistake. The bad-delete problem above is exactly what this solves and a replica does not. RPO becomes the age of the newest archived WAL, and since only completed segments get archived, `archive_timeout` is what caps it on a quiet server. RTO becomes restore time plus replay time, which you can only know by doing it. The drill, including a real recovery to a target time, is in [Operating data stores](../../05-quality-and-observability/notes/05-operating-data-stores.md). A backup never restored is a hope, not a rung.

## The ladder as a table

| Rung | Survives | Does not survive | RPO | RTO | Evidence |
|---|---|---|---|---|---|
| Process memory | nothing | process crash | all unflushed, up to 512 records per crash in the test above | none needed | measured |
| Page cache | process crash | OS crash, power cut | since the last OS writeback; [Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) say about 30 s on Linux | reboot | measured for process crash, cited otherwise |
| `fsync` to device | power cut, if the device honours flushes | disk failure, lying drive | 0 if honest | restart | modelled, not physically tested |
| WAL, `synchronous_commit=off` | server crash, without corruption | last few hundred ms of commits | 5 to 36 rows in our runs; bounded at 3 x `wal_writer_delay` | 0.1 s to replay | measured and cited |
| WAL, `on` | server crash | disk failure | 0 | grows with WAL: 6 s for 2.1 GB | measured |
| Async replica | machine loss | your mistakes; loses the lag | replication lag: 0 to 15,620 rows | detection plus promotion (0.1 s) | measured, one run each |
| Sync replica | machine loss with no acked loss | your mistakes; stalls if the standby does | 0 | as above, plus outage during a stall | measured, one run each |
| Object store with versioning | zone loss, overwrites and deletes | account compromise without Object Lock | upload interval | re-download | cited |
| Tested backup with WAL archive | your own bad deploy | whatever you never restored | newest archived WAL | restore plus replay | [measured in 05/05](../../05-quality-and-observability/notes/05-operating-data-stores.md) |

Note who decides. Not the engineer: the cost of being wrong. AWS's guidance says recovery should not cost more than the loss it prevents, so a clickstream on async commit can be right, and a payments ledger on the same setting is a serious mistake.

## Cache versus source of truth

Kleppmann's framing at the start of *DDIA* Part III is the one to keep: a **system of record** holds the authoritative version of the data, and **derived data** can be rebuilt from it, with a cache as the classic example. Losing derived data costs time. Losing the system of record costs the data. Ask of every store you run: if this were deleted, could I rebuild it, and from what?

Trouble starts when a cache silently becomes the system of record. The usual way is write-behind: acknowledge in the cache and write to the database later. Here both policies use a real SQLite file underneath and a dict that disappears on restart.

```python
import sqlite3

class Store:
    """A real SQLite file as the source of truth, and a dict as the cache that dies with the process."""
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS fare (trip INT PRIMARY KEY, cents INT)")
        self.cache, self.dirty = {}, []
    def write_through(self, trip, cents):
        self.db.execute("INSERT OR REPLACE INTO fare VALUES (?, ?)", (trip, cents))
        self.db.commit()                              # saved first
        self.cache.pop(trip, None)                    # then invalidate
    def write_behind(self, trip, cents):
        self.cache[trip] = cents                      # acknowledged here
        self.dirty.append((trip, cents))
    def flush(self):
        self.db.executemany("INSERT OR REPLACE INTO fare VALUES (?, ?)", self.dirty)
        self.db.commit()
        self.dirty.clear()
    def read(self, trip):
        if trip not in self.cache:
            row = self.db.execute("SELECT cents FROM fare WHERE trip = ?", (trip,)).fetchone()
            if row:
                self.cache[trip] = row[0]
        return self.cache.get(trip)

for policy in ["write_through", "write_behind"]:
    path = f"{policy}.db"
    s = Store(path)
    for trip in range(1000):
        getattr(s, policy)(trip, trip * 10)
        if policy == "write_behind" and trip % 300 == 299:
            s.flush()
    del s                                             # the cache process restarts, memory gone
    s = Store(path)
    found = sum(s.read(t) is not None for t in range(1000))
    print(f"{policy:14s} acknowledged 1000, readable after restart {found}")
```

```text
write_through  acknowledged 1000, readable after restart 1000
write_behind   acknowledged 1000, readable after restart 900
```

Write-through lost nothing because the database got the write before the client heard anything. Write-behind lost 100 acknowledged writes: the ones since the last flush. Its RPO is its flush interval, and it has quietly turned the cache into the source of truth for that window.

Redis shows the same thing as configuration. Its [persistence docs](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) describe RDB snapshots, which can lose the minutes since the last save, and an append-only file with three settings: `appendfsync always` (very slow, very safe), `everysec` (the default, can lose one second) and `no` (leaves it to the OS). That's the ladder again, with the same names. A Redis used as a cache needs none of it. A Redis holding the only copy of carts or sessions needs you to have chosen.

The test is to do it: delete the cache in staging and check what happens. If the answer is "the app rebuilds it and gets slower for a while", it is a cache. If the answer is that someone has to explain to customers, it was your database all along.

## Pitfalls

- **Testing durability with `kill -9` alone.** It proves process-crash safety and says nothing about power loss, because the page cache survives. Say which failure you tested.
- **Trusting a fast fsync.** Tens of microseconds on an SSD usually means a volatile cache is taking the write. Check with `pg_test_fsync` on the real hardware and read the drive's spec for power-loss protection.
- **Retrying a failed fsync.** The second call may succeed with the data already gone. Treat the failure as a crash and recover from the log.
- **Forgetting the directory.** A renamed or new file needs an `fsync` on its directory to survive a crash.
- **Calling a replica a backup.** The bad `DELETE` reached the standby in about 30 ms. Replicas cover hardware; backups cover people.
- **Reading eleven nines as data safety.** Durability figures describe the provider losing objects. Your deletes and overwrites are outside them unless you turn on versioning.
- **Setting `fsync = off` for a load and forgetting it.** It is not the same as `synchronous_commit = off`. One loses a little recent data; the other can corrupt the cluster.
- **Sync replication with one standby and no plan.** A stalled standby stalled every commit in our run. Decide in advance who gets paged and what happens.

## Try it

1. Change the writer to `buffering=1`, which makes Python line-buffer its file. What happens to the `memory` row, and why does this not make it durable?
2. In the toy WAL, remove the CRC check from `recover` and rerun the flipped-bit test. What does recovery do now?
3. Set `max_wal_size = '256MB'` in `pg_recovery_rto` instead of 32 GB and rerun. What happens to restart time, and what does it cost?
4. A pipeline writes a watermark file after each batch and restarts from it. Which of this chapter's failures could it hit, and what is the smallest correct way to write it?

<details><summary>Answers</summary>

1. Losses fall to about zero because each record now reaches the page cache before the acknowledgement, so the row looks like `flush`. It survives a process crash and nothing more: there is still no `fsync`.
2. Recovery replays past the damage. A flip in a payload gives a wrong value with no error, and a flip in the length field misreads everything after it. This is why the checksum sits in the format.
3. Checkpoints run more often, so less WAL is pending and restart gets faster. The cost is more write work during normal running, because pages are written and full-page images logged more frequently. You are trading throughput for RTO.
4. A torn write (use a temporary file and `os.replace`, as in the `rename` test), a lost rename or lost contents on power loss (`fsync` the file, then the directory), and a watermark ahead of the data it describes. Sync the data first, and make the batch [idempotent](../../03-transform-and-orchestrate/notes/04-idempotency-and-backfills.md) so replaying after a crash is harmless.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| A write returned success. Where is the data? | It depends on the rung: process buffer, page cache, device, replica, or backup. Each survives a different failure, so ask which failure you must survive. |
| Difference between `flush` and `fsync`? | `flush` moves data from the process to the OS and survives a process crash. `fsync` asks the OS to push it to the device, which is what a power cut requires, assuming the drive honours it. |
| RPO versus RTO? | RPO is how much data you can lose, measured in time. RTO is how long you can be down. They are set by business cost and bought separately. |
| Why does a WAL make commits faster? | One sequential append and sync replaces many random page writes. Pages follow later, and replay rebuilds them after a crash. One sync can also commit many transactions. |
| `synchronous_commit = off` versus `fsync = off`? | The first can lose recent commits but stays consistent. The second can corrupt the database and is only for data you can rebuild. |
| Async or sync replication? | Async can lose the lag on failover. Sync loses nothing acknowledged, but commits stop if the standby stalls. It's a choice between RPO and availability. |
| Is a replica a backup? | No. It copies deletes in milliseconds. You need point-in-time recovery from a retained backup. |
| What does eleven nines cover? | The provider losing your object, not you overwriting it. Versioning and Object Lock cover that. |
| What makes something a cache rather than a source of truth? | You can delete it and rebuild it from elsewhere. Write-behind breaks that for its flush window. |

## Next

With durability settled, the next question is which kind of store fits the access pattern: [Choosing a store](10-choosing-a-store.md).
