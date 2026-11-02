"""Code from notes/09-persistence.md: real crash tests of each rung of the persistence ladder.

Run from any folder (it writes only to temporary directories):
    uv run --no-project --python 3.12 --with pgserver --with 'psycopg[binary]' python 09_persistence.py

The Postgres sections SIGKILL a private server started in a temporary directory, never any other server.
Timings change from machine to machine; the counts of what survived are the point.
"""
import os, sys, tempfile
os.chdir(tempfile.mkdtemp())

# --- ladder ---
import signal, subprocess, random, time

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
    p = subprocess.Popen([sys.executable, "writer.py", mode, "log.txt"], stdout=subprocess.PIPE, text=True)
    time.sleep(0.05 + random.random() / 10)
    p.send_signal(signal.SIGKILL)
    acked = p.stdout.read().count("\n")
    p.wait()
    with open("log.txt") as f:
        saved = sum(1 for line in f if len(line) == 16)        # 16 bytes is one complete record
    return acked, max(acked - saved, 0)

random.seed(9)
print(f"{'stops at':10s} {'trials':>6s} {'acknowledged':>13s} {'lost':>7s}")
for mode in ["memory", "flush", "fsync"]:
    results = [crash_writer(mode) for _ in range(20)]
    print(f"{mode:10s} {len(results):6d} {sum(a for a, _ in results):13,d} {sum(l for _, l in results):7,d}")

# --- fsync_cost ---
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

# --- power_model ---
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

# --- wal ---
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

# --- replace ---
ATOMIC = """
import os, sys
mode, path, text = sys.argv[1], sys.argv[2], sys.argv[3]
body = text.encode() * 20000
if mode == "in_place":
    with open(path, "wb") as f:                 # truncates first: the old version is gone at once
        for i in range(0, len(body), 4096):
            f.write(body[i:i + 4096]); f.flush()
else:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        for i in range(0, len(body), 4096):
            f.write(body[i:i + 4096]); f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)                       # atomic on POSIX: readers see old or new
    d = os.open(os.path.dirname(path) or ".", os.O_RDONLY)
    os.fsync(d); os.close(d)                    # make the rename itself durable
"""
open("atomic.py", "w").write(ATOMIC)
SIZE = 20000 * 8

def replace_trials(mode, n=40):
    outcome = {"old": 0, "new": 0, "corrupt": 0}
    for _ in range(n):
        with open("config.bin", "wb") as f:
            f.write(b"old-old-" * 20000)
        p = subprocess.Popen([sys.executable, "atomic.py", mode, "config.bin", "new-new-"])
        time.sleep(0.015 + random.random() * 0.03)
        p.send_signal(signal.SIGKILL); p.wait()
        data = open("config.bin", "rb").read()
        outcome["old" if data == b"old-old-" * 20000 else "new" if data == b"new-new-" * 20000 else "corrupt"] += 1
    return outcome

random.seed(3)
for mode in ["in_place", "rename"]:
    print(f"{mode:9s} {replace_trials(mode)}")

# --- pg_setup ---
try:
    import pgserver, psycopg
except ImportError:
    sys.exit("The rest needs Postgres: run with --python 3.12 --with pgserver --with 'psycopg[binary]'")
import threading, shutil

BIN = os.path.join(os.path.dirname(pgserver.__file__), "pginstall", "bin")
ROOT = tempfile.mkdtemp(dir="/tmp", prefix="pg")     # short path: Unix sockets have a length limit

def tool(name, *args):
    return subprocess.run([f"{BIN}/{name}", *args], check=True, capture_output=True, text=True).stdout

class Server:
    """One private Postgres server in a temporary directory, with a real kill -9."""
    def __init__(self, name, port, conf=""):
        self.dir, self.port = f"{ROOT}/{name}", port
        self.conf = f"listen_addresses=''\nunix_socket_directories='{ROOT}'\nport={port}\n{conf}\n"
    def init(self):
        tool("initdb", "-D", self.dir, "-U", "postgres", "--auth=trust", "-E", "UTF8")
        self.configure()
        return self
    def configure(self):
        with open(f"{self.dir}/postgresql.conf", "a") as f:
            f.write(self.conf)
    def start(self):
        t = time.perf_counter()
        tool("pg_ctl", "-w", "-t", "120", "-D", self.dir, "-l", f"{self.dir}/server.log", "start")
        return time.perf_counter() - t
    def connect(self):
        return psycopg.connect(f"host={ROOT} port={self.port} user=postgres dbname=postgres", autocommit=True)
    def kill9(self):
        with open(f"{self.dir}/postmaster.pid") as f:
            pid = int(f.readline())
        kids = subprocess.run(["pgrep", "-P", str(pid)], capture_output=True, text=True).stdout.split()
        for p in [pid, *map(int, kids)]:
            try:
                os.kill(p, signal.SIGKILL)
            except ProcessLookupError:
                pass
        time.sleep(0.2)
        if os.path.exists(f"{self.dir}/postmaster.pid"):
            os.remove(f"{self.dir}/postmaster.pid")
    def stop(self):
        subprocess.run([f"{BIN}/pg_ctl", "-w", "-D", self.dir, "-m", "fast", "stop"], capture_output=True)

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

# --- pg_crash ---
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

# --- pg_recovery_rto ---
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

# --- pg_replica ---
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
    conf = "wal_level=replica\nmax_wal_senders=5\n" + ("synchronous_standby_names='*'\n" if sync else "")
    primary = Server(name, 5610).init()
    primary.start()
    primary.connect().execute("CREATE TABLE trips (id bigint PRIMARY KEY)")
    with open(f"{primary.dir}/postgresql.conf", "a") as f:
        f.write("wal_level=replica\nmax_wal_senders=5\n")
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
    receiver = None
    if freeze:                    # a stalled network: pause the standby's WAL receiver for the last second
        with standby.connect() as c:
            receiver = c.execute("SELECT pid FROM pg_stat_activity WHERE backend_type='walreceiver'").fetchone()[0]
        os.kill(receiver, signal.SIGSTOP)
        time.sleep(1.0)
    primary.kill9()
    if receiver:
        os.kill(receiver, signal.SIGCONT)
    stop.set()
    t.join()
    time.sleep(0.5)
    tool("pg_ctl", "-w", "-D", standby.dir, "promote")
    with standby.connect() as c:
        present = {r[0] for r in c.execute("SELECT id FROM trips")}
    standby.stop()
    return len(acked), sum(i not in present for i in acked)

print(f"{'replication':34s} {'acknowledged':>13s} {'lost after failover':>20s}")
for label, sync, freeze in [("asynchronous", False, False),
                            ("asynchronous, standby stalled 1 s", False, True),
                            ("synchronous", True, False)]:
    a, lost = failover_trial(sync, freeze)
    print(f"{label:34s} {a:13,d} {lost:20,d}")

# --- pg_bad_delete ---
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

# --- cache ---
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
