"""Code from notes/04-transactions-and-isolation.md.

Run from any folder (it writes only to a temporary directory):
    uv run --no-project --python 3.12 --with pgserver --with 'psycopg[binary]' python 04_transactions_and_isolation.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- atomic ---
import sqlite3

db = sqlite3.connect("wallet.db", isolation_level=None)   # we issue BEGIN ourselves
db.execute("create table wallet(owner text primary key, cents int check (cents >= 0))")

def reset():
    db.execute("delete from wallet")
    db.execute("insert into wallet values ('rider', 5000), ('driver', 0), ('platform', 0)")

def pay_trip(fare, *, crash, atomic):
    """Rider pays; the driver and the platform each get a share. Three writes, one fact."""
    if atomic:
        db.execute("begin")
    try:
        db.execute("update wallet set cents = cents - ? where owner='rider'", (fare,))
        db.execute("update wallet set cents = cents + ? where owner='driver'", (fare * 8 // 10,))
        if crash:
            raise ConnectionError("process died here")
        db.execute("update wallet set cents = cents + ? where owner='platform'", (fare * 2 // 10,))
        if atomic:
            db.execute("commit")
    except ConnectionError:
        if atomic:
            db.execute("rollback")

def show(label):
    rows = dict(db.execute("select owner, cents from wallet"))
    print(f"{label:<28} {rows}  total={sum(rows.values())}")

reset(); pay_trip(2000, crash=True, atomic=False); show("crash, no transaction")
reset(); pay_trip(2000, crash=True, atomic=True);  show("crash, in a transaction")
reset(); pay_trip(2000, crash=False, atomic=True); show("no crash")
print("--- atomic done")

# --- sqlite_serial ---
a = sqlite3.connect("serial.db", isolation_level=None, timeout=0)
b = sqlite3.connect("serial.db", isolation_level=None, timeout=0)
a.execute("pragma journal_mode=wal")
a.execute("create table driver(id int primary key, trips int)")
a.execute("insert into driver values (7, 100)")

# 1. Read-modify-write in application code, with no transaction: a lost update.
ta = a.execute("select trips from driver where id=7").fetchone()[0]
tb = b.execute("select trips from driver where id=7").fetchone()[0]
a.execute("update driver set trips=? where id=7", (ta + 1,))
b.execute("update driver set trips=? where id=7", (tb + 1,))
print("no transaction, two increments:", b.execute("select trips from driver").fetchone()[0])

# 2. Two deferred transactions: both read from a snapshot, the second writer loses.
a.execute("begin"); b.execute("begin")
ta = a.execute("select trips from driver where id=7").fetchone()[0]
tb = b.execute("select trips from driver where id=7").fetchone()[0]
a.execute("update driver set trips=? where id=7", (ta + 1,)); a.execute("commit")
try:
    b.execute("update driver set trips=? where id=7", (tb + 1,))
except sqlite3.OperationalError as e:
    print("second writer, stale snapshot:", e)
    b.execute("rollback")

# 3. BEGIN IMMEDIATE takes the single write lock up front, so writers run in series.
a.execute("begin immediate")
try:
    b.execute("begin immediate")
except sqlite3.OperationalError as e:
    print("second BEGIN IMMEDIATE:       ", e)
a.execute("commit")
print("--- sqlite_serial done")

# --- pg_setup ---
import sys, tempfile, threading, time
try:
    import pgserver, psycopg
    from psycopg import IsolationLevel as Iso, errors
except ImportError:
    sys.exit("The rest needs Postgres: run with --python 3.12 --with pgserver --with 'psycopg[binary]'")

pg = pgserver.get_server(tempfile.mkdtemp())

def connect(level=Iso.READ_COMMITTED, autocommit=False):
    conn = psycopg.connect(pg.get_uri(), autocommit=autocommit)
    conn.isolation_level = level
    return conn

def admin(sql):
    with connect(autocommit=True) as c:
        c.execute(sql)

def one(conn, sql, *args):
    return conn.execute(sql, args).fetchone()[0]

with connect() as c:
    print(one(c, "select version()").split(",")[0])
    print("default isolation:", one(c, "show transaction_isolation"))
print("--- pg_setup done")

# --- read_committed ---
admin("""drop table if exists account;
         create table account(owner text primary key, cents int);
         insert into account values ('driver', 50000), ('savings', 50000)""")

# Dirty read: asking for READ UNCOMMITTED in Postgres gets you READ COMMITTED.
w = connect(); r = connect(Iso.READ_UNCOMMITTED)
w.execute("update account set cents = cents - 10000 where owner='driver'")
print("uncommitted write, other session reads:", one(r, "select cents from account where owner='driver'"))
w.rollback(); r.rollback()

def total_seen_during_transfer(level):
    reader, writer = connect(level), connect()
    first = one(reader, "select cents from account where owner='driver'")
    writer.execute("update account set cents = cents - 10000 where owner='driver'")
    writer.execute("update account set cents = cents + 10000 where owner='savings'")
    writer.commit()
    second = one(reader, "select cents from account where owner='savings'")
    reader.rollback()
    admin("update account set cents = 50000")
    return first + second

print("true total: 100000")
print("read committed sees:  ", total_seen_during_transfer(Iso.READ_COMMITTED))
print("repeatable read sees: ", total_seen_during_transfer(Iso.REPEATABLE_READ))
print("--- read_committed done")

# --- mvcc ---
admin("""drop table if exists fare;
         create table fare(zone int primary key, cents int);
         insert into fare values (7, 1200)""")
VERSION = "select xmin::text, xmax::text, ctid::text, cents from fare where zone=7"

old_view = connect(Iso.REPEATABLE_READ); writer = connect(); other = connect()
print("before            ", old_view.execute(VERSION).fetchone())
writer.execute("update fare set cents = 1500 where zone=7")
print("writer sees       ", writer.execute(VERSION).fetchone())
print("others, uncommitted", other.execute(VERSION).fetchone()); other.rollback()
writer.commit()
print("others, committed ", other.execute(VERSION).fetchone()); other.rollback()
print("old snapshot      ", old_view.execute(VERSION).fetchone()); old_view.rollback()

# Each update writes a new row version, so the table grows until vacuum reclaims the old ones.
with connect(autocommit=True) as c:
    size = lambda: one(c, "select pg_relation_size('fare')")
    print("table bytes before updates", size())
    pin = connect(Iso.REPEATABLE_READ); one(pin, "select count(*) from fare")   # old snapshot pins versions
    for i in range(5000):
        c.execute("update fare set cents = %s where zone=7", (i,))
    print("after 5000 updates, snapshot held open", size())
    pin.rollback()
    c.execute("vacuum full fare")
    print("after vacuum full                     ", size())
print("--- mvcc done")

# --- lost_update ---
admin("""drop table if exists driver;
         create table driver(id int primary key, trips int);
         insert into driver values (7, 100)""")

def interleave(level):
    a, b = connect(level), connect(level)
    ta = one(a, "select trips from driver where id=7")
    tb = one(b, "select trips from driver where id=7")
    a.execute("update driver set trips=%s where id=7", (ta + 1,)); a.commit()
    try:
        b.execute("update driver set trips=%s where id=7", (tb + 1,)); b.commit()
        outcome = "both committed"
    except errors.SerializationFailure as e:
        b.rollback(); outcome = f"second aborted: {str(e).strip()}"
    with connect() as c:
        result = one(c, "select trips from driver where id=7")
    admin("update driver set trips = 100")
    return result, outcome

print("read committed: ", interleave(Iso.READ_COMMITTED))
print("repeatable read:", interleave(Iso.REPEATABLE_READ))
print("--- lost_update done")

# --- stress ---
def increment_rmw(c):
    t = one(c, "select trips from driver where id=7")
    c.execute("update driver set trips=%s where id=7", (t + 1,))

def increment_atomic(c):
    c.execute("update driver set trips = trips + 1 where id=7")

def increment_lock(c):
    t = one(c, "select trips from driver where id=7 for update")
    c.execute("update driver set trips=%s where id=7", (t + 1,))

def increment_cas(c):
    while True:
        t = one(c, "select trips from driver where id=7")
        if c.execute("update driver set trips=%s where id=7 and trips=%s", (t + 1, t)).rowcount == 1:
            return
        c.commit()

THREADS, EACH = 8, 150

def run(fn, level=Iso.READ_COMMITTED):
    admin("update driver set trips = 0")
    retries = [0]
    def worker():
        with connect(level) as c:
            for _ in range(EACH):
                while True:
                    try:
                        fn(c); c.commit(); break
                    except errors.SerializationFailure:
                        c.rollback(); retries[0] += 1
    t0 = time.perf_counter()
    pool = [threading.Thread(target=worker) for _ in range(THREADS)]
    [t.start() for t in pool]; [t.join() for t in pool]
    with connect() as c:
        return one(c, "select trips from driver where id=7"), retries[0], time.perf_counter() - t0

print(f"expected {THREADS * EACH}")
for name, fn, level in [("read-then-write, read committed", increment_rmw, Iso.READ_COMMITTED),
                        ("atomic update", increment_atomic, Iso.READ_COMMITTED),
                        ("select for update", increment_lock, Iso.READ_COMMITTED),
                        ("compare-and-set", increment_cas, Iso.READ_COMMITTED),
                        ("read-then-write, repeatable read", increment_rmw, Iso.REPEATABLE_READ)]:
    final, retries, secs = run(fn, level)
    print(f"{name:<34} final={final:>5}  retries={retries:>5}  {secs:5.2f} s")
print("--- stress done")

# --- write_skew ---
admin("""drop table if exists duty;
         create table duty(driver text primary key, zone int, on_duty boolean);
         insert into duty values ('Ana', 7, true), ('Ben', 7, true)""")

def sign_off(conn, name):
    """Rule: zone 7 must keep at least one driver on duty."""
    if one(conn, "select count(*) from duty where zone=7 and on_duty") >= 2:
        conn.execute("update duty set on_duty=false where driver=%s", (name,))

def both_sign_off(level):
    admin("update duty set on_duty=true")
    a, b = connect(level), connect(level)
    result = []
    sign_off(a, "Ana"); sign_off(b, "Ben")          # each sees two on duty
    for name, c in (("Ana", a), ("Ben", b)):
        try:
            c.commit(); result.append(f"{name} committed")
        except errors.SerializationFailure as e:
            result.append(f"{name} aborted: {str(e).splitlines()[0]}")
    with connect() as c:
        left = one(c, "select count(*) from duty where on_duty")
    return left, result

for name, level in [("read committed", Iso.READ_COMMITTED), ("repeatable read", Iso.REPEATABLE_READ),
                    ("serializable", Iso.SERIALIZABLE)]:
    left, result = both_sign_off(level)
    print(f"{name:<16} on duty afterwards={left}  {result}")
print("--- write_skew done")

# --- write_skew_lock ---
def sign_off_locked(name, started, results):
    with connect() as c:
        rows = c.execute("select driver from duty where zone=7 and on_duty for update").fetchall()
        started.set()
        if len(rows) >= 2:
            time.sleep(0.2)                         # hold the locks while "thinking"
            c.execute("update duty set on_duty=false where driver=%s", (name,))
            results.append(f"{name} signed off")
        else:
            results.append(f"{name} refused: only {len(rows)} on duty")

admin("update duty set on_duty=true")
started, results = threading.Event(), []
first = threading.Thread(target=sign_off_locked, args=("Ana", started, results))
first.start(); started.wait()
second = threading.Thread(target=sign_off_locked, args=("Ben", threading.Event(), results))
second.start(); first.join(); second.join()
print(results)
with connect() as c:
    print("on duty afterwards:", one(c, "select count(*) from duty where on_duty"))
print("--- write_skew_lock done")

# --- phantom ---
admin("""drop table if exists booking;
         create table booking(vehicle int, hour int, rider text)""")

def book(c, rider):
    free = not c.execute("select 1 from booking where vehicle=9 and hour=10 for update").fetchall()
    if free:
        c.execute("insert into booking values (9, 10, %s)", (rider,))

for name, level in [("read committed, for update", Iso.READ_COMMITTED),
                    ("repeatable read, for update", Iso.REPEATABLE_READ), ("serializable", Iso.SERIALIZABLE)]:
    admin("truncate booking")
    a, b = connect(level), connect(level)
    try:
        book(a, "Rae"); book(b, "Sam"); a.commit(); b.commit(); note = "both committed"
    except errors.SerializationFailure:
        a.rollback(); b.rollback(); note = "second aborted"
    with connect() as c:
        print(f"{name:<28} bookings for the slot={one(c, 'select count(*) from booking')}  {note}")

# A unique constraint turns the absence of a row into something the database can check.
admin("truncate booking; alter table booking add constraint one_per_slot unique (vehicle, hour)")
a, b = connect(), connect()
a.execute("insert into booking values (9, 10, 'Rae')"); a.commit()
try:
    b.execute("insert into booking values (9, 10, 'Sam')"); b.commit()
except errors.UniqueViolation as e:
    b.rollback(); print("unique constraint:", str(e).splitlines()[0])

# An exclusion constraint does the same for overlapping ranges.
admin("""drop table if exists booking2;
         create table booking2(vehicle int, during int4range,
             exclude using gist (during with &&) where (vehicle = 9))""")
a, b = connect(), connect()
a.execute("insert into booking2 values (9, '[10,12)')"); a.commit()
try:
    b.execute("insert into booking2 values (9, '[11,13)')"); b.commit()
except errors.ExclusionViolation as e:
    b.rollback(); print("exclusion constraint:", str(e).splitlines()[0])
print("--- phantom done")

# --- deadlock ---
admin("update driver set trips=0 where id=7; insert into driver values (8, 0) on conflict do nothing")
outcome, barrier = [], threading.Barrier(2)

def transfer(first, second):
    with connect() as c:
        try:
            c.execute("update driver set trips=trips+1 where id=%s", (first,))
            barrier.wait()                         # both now hold one row and want the other
            c.execute("update driver set trips=trips+1 where id=%s", (second,))
            c.commit(); outcome.append("committed")
        except errors.DeadlockDetected as e:
            c.rollback(); outcome.append(str(e).splitlines()[0])

t0 = time.perf_counter()
pool = [threading.Thread(target=transfer, args=args) for args in [(7, 8), (8, 7)]]
[t.start() for t in pool]; [t.join() for t in pool]
print(outcome, f"resolved after {time.perf_counter() - t0:.1f} s")
print("--- deadlock done")

# --- ssi_abort_rate ---
admin("""drop table if exists zone_count;
         create table zone_count(zone int primary key, trips int);
         insert into zone_count select g, 0 from generate_series(1, 1000) g""")

def hammer(level, zones, workers=8, each=100):
    """Read a zone, then write it. A narrow zones range means high contention."""
    admin("update zone_count set trips=0")
    aborts, commits, lock = [0], [0], threading.Lock()
    def worker(seed):
        import random
        rnd = random.Random(seed)
        with connect(level) as c:
            for _ in range(each):
                z = rnd.randrange(1, zones + 1)
                while True:
                    try:
                        t = one(c, "select trips from zone_count where zone=%s", z)
                        c.execute("update zone_count set trips=%s where zone=%s", (t + 1, z))
                        c.commit()
                        with lock: commits[0] += 1
                        break
                    except errors.SerializationFailure:
                        c.rollback()
                        with lock: aborts[0] += 1
    t0 = time.perf_counter()
    pool = [threading.Thread(target=worker, args=(i,)) for i in range(workers)]
    [t.start() for t in pool]; [t.join() for t in pool]
    return commits[0], aborts[0], time.perf_counter() - t0

for zones in (1, 10, 1000):
    commits, aborts, secs = hammer(Iso.SERIALIZABLE, zones)
    print(f"serializable, {zones:>4} hot rows: {commits} commits, {aborts:>5} aborts"
          f" ({aborts / (commits + aborts):4.0%} of attempts), {commits / secs:6.0f} commits/s")
print("--- ssi_abort_rate done")

# --- request_id ---
admin("""drop table if exists charge;
         create table charge(request_id text unique, rider text, cents int)""")

def charge(conn, request_id, cents, ack_lost):
    conn.execute("insert into charge values (%s, 'Rae', %s) on conflict (request_id) do nothing",
                 (request_id, cents))
    conn.commit()
    if ack_lost:
        raise ConnectionError("commit succeeded, reply never arrived")

def pay_with_retry(request_id_for):
    with connect() as c:
        for attempt in range(2):
            try:
                charge(c, request_id_for(attempt), 2000, ack_lost=attempt == 0)
                break
            except ConnectionError:
                pass
        total = one(c, "select sum(cents) from charge")
        c.rollback()
    admin("truncate charge")
    return total

print("new id on each retry:    charged", pay_with_retry(lambda attempt: f"req-{attempt}"))
print("same id on each retry:   charged", pay_with_retry(lambda attempt: "req-1"))
print("--- request_id done")

# --- load_swap ---
admin("""drop table if exists fct_trip;
         create table fct_trip(day date, fare int);
         insert into fct_trip select '2026-01-01', 1 from generate_series(1, 100000)""")
reader = connect(autocommit=True)
COUNT = "select count(*), sum(fare) from fct_trip where day='2026-01-01'"

# Reload the partition with a commit between delete and insert.
w = connect()
w.execute("delete from fct_trip where day='2026-01-01'"); w.commit()
print("two commits, reader sees:", reader.execute(COUNT).fetchone())
w.execute("insert into fct_trip select '2026-01-01', 2 from generate_series(1, 100000)"); w.commit()

# Reload the same partition in one transaction.
w.execute("delete from fct_trip where day='2026-01-01'")
print("one transaction, during: ", reader.execute(COUNT).fetchone())
w.execute("insert into fct_trip select '2026-01-01', 3 from generate_series(1, 100000)")
print("one transaction, still:  ", reader.execute(COUNT).fetchone())
w.commit()
print("one transaction, after:  ", reader.execute(COUNT).fetchone())
w.close(); reader.close()
pg.cleanup()
print("--- load_swap done")
