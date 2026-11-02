"""Code from notes/04-schema-and-data-migrations.md: real migrations against a real Postgres under load.

Run from any folder (it writes only to temporary directories and starts a private Postgres):
    uv run --no-project --python 3.12 --with pgserver --with 'psycopg[binary]' --with alembic \
        --with sqlalchemy --with duckdb --with numpy python 04_schema_and_data_migrations.py

Timings change from machine to machine; the shape of each result is the point.
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- server ---
import shutil, subprocess, threading, time
import pgserver, psycopg

BIN = os.path.dirname(pgserver.__file__) + "/pginstall/bin"
ROOT = tempfile.mkdtemp(dir="/tmp", prefix="mig")
PORT = 5611

def tool(name, *args):
    return subprocess.run([f"{BIN}/{name}", *args], check=True, capture_output=True, text=True).stdout

tool("initdb", "-D", f"{ROOT}/d", "-U", "postgres", "--auth=trust", "-E", "UTF8")
with open(f"{ROOT}/d/postgresql.conf", "a") as f:
    f.write(f"listen_addresses=''\nunix_socket_directories='{ROOT}'\nport={PORT}\nmax_wal_size=4GB\n")
tool("pg_ctl", "-w", "-D", f"{ROOT}/d", "-l", f"{ROOT}/log", "start")

def connect():
    return psycopg.connect(f"host={ROOT} port={PORT} user=postgres dbname=postgres", autocommit=True)

db = connect()
print(db.execute("SELECT version()").fetchone()[0].split(" on ")[0])
db.execute("""CREATE TABLE orders (id bigint PRIMARY KEY, customer int NOT NULL, amount int NOT NULL, note text);
              INSERT INTO orders SELECT i, i % 50000, i % 1000, repeat('x', 60) FROM generate_series(1, 2000000) i""")
print("rows:", db.execute("SELECT count(*) FROM orders").fetchone()[0],
      "| table size:", db.execute("SELECT pg_size_pretty(pg_table_size('orders'))").fetchone()[0])

class Probe:
    """An application in miniature: reads and writes by primary key in a loop, timing each."""
    def __init__(self, sql="UPDATE orders SET amount = amount + 1 WHERE id = %s", rows=2_000_000):
        self.sql, self.rows, self.latencies, self.errors = sql, rows, [], []
        self.halt = threading.Event()
        self.thread = threading.Thread(target=self.run)
    def run(self):
        c, i = connect(), 0
        while not self.halt.is_set():
            i += 1
            t = time.perf_counter()
            try:
                c.execute(self.sql, (i % self.rows + 1,))
            except psycopg.Error as e:
                self.errors.append(type(e).__name__)
            self.latencies.append(time.perf_counter() - t)
            time.sleep(0.001)
        c.close()
    def __enter__(self):
        self.thread.start(); time.sleep(0.1); return self
    def __exit__(self, *a):
        time.sleep(0.05); self.halt.set(); self.thread.join()
    def report(self):
        return f"{len(self.latencies):5,d} queries, worst stall {max(self.latencies) * 1000:7.0f} ms, {len(self.errors)} errors"

def timed(sql, conn=None, sql_probe=None):
    """Run one statement while the probe runs, and print both timings."""
    kw = {"sql": sql_probe} if sql_probe else {}
    with Probe(**kw) as p:
        t = time.perf_counter()
        (conn or db).execute(sql)
        took = time.perf_counter() - t
    print(f"{took:6.2f} s  {sql.splitlines()[0][:58]:58s} | {p.report()}")
    return took

# --- lock_levels ---
def lock_taken(sql):
    """Run a statement in a transaction, read the lock it holds on orders, roll back."""
    with connect() as c:
        c.autocommit = False
        c.execute(sql)
        modes = c.execute("""SELECT mode FROM pg_locks WHERE relation = 'orders'::regclass
                             AND pid = pg_backend_pid()""").fetchall()
        c.rollback()
    return ", ".join(sorted(m[0] for m in modes))

db.execute("ALTER TABLE orders ADD CONSTRAINT amt_ok CHECK (amount >= 0) NOT VALID")
db.execute("CREATE TABLE parent (id int PRIMARY KEY)")
for sql in ["SELECT * FROM orders WHERE id = 1",
            "UPDATE orders SET amount = 1 WHERE id = 1",
            "ALTER TABLE orders VALIDATE CONSTRAINT amt_ok",
            "CREATE INDEX i_lock ON orders (customer)",
            "ALTER TABLE orders ADD CONSTRAINT o_fk FOREIGN KEY (customer) REFERENCES parent (id) NOT VALID",
            "ALTER TABLE orders ADD COLUMN c1 int",
            "ALTER TABLE orders RENAME COLUMN note TO note2",
            "ALTER TABLE orders DROP COLUMN note"]:
    print(f"{sql:50s} {lock_taken(sql)}")
db.execute("ALTER TABLE orders DROP CONSTRAINT amt_ok")

# --- lock_queue ---
def blocked_alter(lock_timeout):
    """A long report holds a weak lock. A one-millisecond ALTER arrives. What do other queries see?"""
    report = connect()
    report.autocommit = False
    report.execute("SELECT count(*) FROM orders WHERE id = 1")                  # holds ACCESS SHARE until it ends
    ddl = connect()
    if lock_timeout:
        ddl.execute(f"SET lock_timeout = '{lock_timeout}'")
    outcome = []
    def alter():
        t = time.perf_counter()
        try:
            ddl.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS flag1 int")
            outcome.append(f"ALTER finished after {time.perf_counter() - t:.2f} s")
        except psycopg.errors.LockNotAvailable:
            outcome.append(f"ALTER gave up after {time.perf_counter() - t:.2f} s")
    with Probe("SELECT amount FROM orders WHERE id = %s") as p:
        th = threading.Thread(target=alter)
        th.start()
        time.sleep(2)                                                           # the report runs on for 2 s
        report.rollback()
        th.join()
    report.close(); ddl.close()
    print(f"lock_timeout {lock_timeout or 'off':6s}: {outcome[0]:30s} | reads: {p.report()}")
    db.execute("ALTER TABLE orders DROP COLUMN IF EXISTS flag1")

blocked_alter(None)
blocked_alter("100ms")

# --- add_column ---
def file_of():
    return db.execute("SELECT pg_relation_filenode('orders')").fetchone()[0]
before = file_of()
timed("ALTER TABLE orders ADD COLUMN region text DEFAULT 'eu'")
print("   rewrote the table:", file_of() != before)
before = file_of()
timed("ALTER TABLE orders ADD COLUMN stamped timestamptz DEFAULT clock_timestamp()")
print("   rewrote the table:", file_of() != before)
db.execute("ALTER TABLE orders DROP COLUMN region, DROP COLUMN stamped")

# --- not_null ---
db.execute("ALTER TABLE orders ADD COLUMN source text DEFAULT 'web'")
print("naive")
timed("ALTER TABLE orders ALTER COLUMN source SET NOT NULL")
db.execute("ALTER TABLE orders ALTER COLUMN source DROP NOT NULL")
print("safe, three steps")
timed("ALTER TABLE orders ADD CONSTRAINT source_nn CHECK (source IS NOT NULL) NOT VALID")
timed("ALTER TABLE orders VALIDATE CONSTRAINT source_nn")
timed("ALTER TABLE orders ALTER COLUMN source SET NOT NULL")
db.execute("ALTER TABLE orders DROP CONSTRAINT source_nn, DROP COLUMN source")

# --- index ---
timed("CREATE INDEX i_plain ON orders (customer)")
db.execute("DROP INDEX i_plain")
timed("CREATE INDEX CONCURRENTLY i_conc ON orders (customer)")
db.execute("DROP INDEX i_conc")
db.execute("CREATE TABLE dup (k int); INSERT INTO dup VALUES (1), (1)")
try:
    db.execute("CREATE UNIQUE INDEX CONCURRENTLY dup_k ON dup (k)")
except psycopg.errors.UniqueViolation as e:
    print("unique build failed:", str(e).splitlines()[0])
print("left behind:", db.execute("""SELECT indexrelid::regclass::text, indisvalid FROM pg_index
                                    WHERE indrelid = 'dup'::regclass""").fetchall())

# --- backfill ---
db.execute("ALTER TABLE orders ADD COLUMN amount_cents bigint")
print("one statement")
timed("UPDATE orders SET amount_cents = amount * 100")
db.execute("UPDATE orders SET amount_cents = NULL")
db.execute("VACUUM orders")

def backfill(batch=10_000, pause=0.0, stop_after=None):
    """Keyed batches, one transaction each. Safe to rerun: it only touches rows still NULL."""
    done, last = 0, 0
    while True:
        rows = db.execute("""UPDATE orders SET amount_cents = amount * 100
                             WHERE id > %s AND id <= %s AND amount_cents IS NULL""", (last, last + batch))
        done += rows.rowcount
        last += batch
        if stop_after and last >= stop_after:
            return done
        if last >= 2_000_000:
            return done
        time.sleep(pause)

print("batches of 10,000")
with Probe() as p:
    t = time.perf_counter()
    first = backfill(stop_after=800_000)                                         # the job dies here
    print(f"  job dies after {first:,d} rows; missing: "
          f"{db.execute('SELECT count(*) FROM orders WHERE amount_cents IS NULL').fetchone()[0]:,d}")
    second = backfill()                                                          # rerun from the start
    took = time.perf_counter() - t
print(f"  rerun updated {second:,d} more | {took:.2f} s | {p.report()}")
WRONG = "SELECT count(*) FROM orders WHERE amount_cents IS DISTINCT FROM amount * 100"
print("  wrong after the backfill:", db.execute(WRONG).fetchone()[0])           # the application kept writing

print("with a trigger for new writes, then a repair pass")
db.execute("""CREATE FUNCTION cents() RETURNS trigger LANGUAGE plpgsql AS $$
              BEGIN NEW.amount_cents := NEW.amount * 100; RETURN NEW; END $$;
              CREATE TRIGGER cents BEFORE INSERT OR UPDATE ON orders
              FOR EACH ROW EXECUTE FUNCTION cents()""")
with Probe() as p:
    fixed = db.execute("UPDATE orders SET amount_cents = amount * 100 "
                       "WHERE amount_cents IS DISTINCT FROM amount * 100").rowcount
    time.sleep(1)
print(f"  repaired {fixed:,d} rows | {p.report()}")
print("  wrong now:", db.execute(WRONG).fetchone()[0])

# --- expand_contract ---
db.execute("""CREATE TABLE customers AS SELECT i AS id, 'u' || i || '@x.io' AS mail FROM generate_series(1, 200000) i;
              ALTER TABLE customers ADD PRIMARY KEY (id)""")
OLD_READ = "SELECT mail FROM customers WHERE id = %s"
NEW_READ = "SELECT email FROM customers WHERE id = %s"
OLD_WRITE = "UPDATE customers SET mail = 'old' || id || '@x.io' WHERE id = %s"

print("naive: rename under a running old app")
with Probe(OLD_READ, rows=200_000) as p:
    db.execute("ALTER TABLE customers RENAME COLUMN mail TO email")
    time.sleep(0.5)
print("  old app:", p.report(), set(p.errors))
db.execute("ALTER TABLE customers RENAME COLUMN email TO mail")

print("expand, migrate, contract")
app = Probe(OLD_WRITE, rows=200_000)
app.__enter__()
db.execute("ALTER TABLE customers ADD COLUMN email text")                        # 1 expand: new column, nullable
db.execute("""CREATE FUNCTION sync_email() RETURNS trigger LANGUAGE plpgsql AS $$
              BEGIN
                IF TG_OP = 'INSERT' OR NEW.mail IS DISTINCT FROM OLD.mail THEN NEW.email := NEW.mail;
                ELSIF NEW.email IS DISTINCT FROM OLD.email THEN NEW.mail := NEW.email; END IF;
                RETURN NEW;
              END $$;
              CREATE TRIGGER sync_email BEFORE INSERT OR UPDATE ON customers
              FOR EACH ROW EXECUTE FUNCTION sync_email()""")                     # 2 dual-write in the database
print("  dual write on; old app still only knows `mail`")
for low in range(0, 200000, 5000):                                               # 3 backfill in batches
    db.execute("UPDATE customers SET email = mail WHERE id > %s AND id <= %s AND email IS NULL", (low, low + 5000))
wrong = db.execute("SELECT count(*) FROM customers WHERE email IS DISTINCT FROM mail").fetchone()[0]
print("  backfilled; rows where the columns differ:", wrong)                    # 4 verify before moving reads
app.__exit__()
print("  old app during expand:", app.report())
new = Probe(NEW_READ, rows=200_000)                       # 5 deploy new code: reads `email`
new.__enter__()
time.sleep(0.3)
db.execute("SET lock_timeout = '2s'")
db.execute("""DROP TRIGGER sync_email ON customers;
              DROP FUNCTION sync_email();
              ALTER TABLE customers DROP COLUMN mail""")                         # 6 contract, only when old code is gone
time.sleep(0.3)
new.__exit__()
print("  new app through contract:", new.report())

# --- alembic_setup ---
from alembic import command
from alembic.config import Config
import sqlalchemy as sa

os.makedirs("mig/versions")
URL = f"postgresql+psycopg://postgres@/postgres?host={ROOT}&port={PORT}"
open("mig/env.py", "w").write('''
from alembic import context
import sqlalchemy as sa
url = context.config.get_main_option("sqlalchemy.url")
meta = context.config.attributes.get("target_metadata")
if context.is_offline_mode():
    context.configure(url=url, literal_binds=True, target_metadata=meta, transaction_per_migration=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    with sa.create_engine(url).connect() as conn:
        context.configure(connection=conn, target_metadata=meta, transaction_per_migration=True)
        with context.begin_transaction():
            context.run_migrations()
''')
open("mig/script.py.mako", "w").write("""from alembic import op
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
def upgrade():
    ${upgrades if upgrades else "pass"}
def downgrade():
    ${downgrades if downgrades else "pass"}
""")
# --- alembic ---
open("mig/versions/a1_add_channel.py", "w").write('''
from alembic import op
import sqlalchemy as sa
revision, down_revision = "a1", None
def upgrade():
    op.execute("SET lock_timeout = \'2s\'")
    op.add_column("customers", sa.Column("channel", sa.Text()))
def downgrade():
    op.drop_column("customers", "channel")
''')
open("mig/versions/a2_index_channel.py", "w").write('''
from alembic import op
revision, down_revision = "a2", "a1"
def upgrade():
    with op.get_context().autocommit_block():      # CONCURRENTLY cannot run inside a transaction
        op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS customers_channel ON customers (channel)")
def downgrade():
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS customers_channel")
''')
cfg = Config()
cfg.set_main_option("script_location", "mig")
cfg.set_main_option("sqlalchemy.url", URL.replace("%", "%%"))
version = lambda: db.execute("SELECT version_num FROM alembic_version").fetchall()
command.upgrade(cfg, "head")
print("after upgrade   :", version(), db.execute(
    "SELECT count(*) FROM pg_indexes WHERE indexname = 'customers_channel'").fetchone()[0], "index")
command.upgrade(cfg, "head")
print("upgrade again   :", version(), "(does nothing)")
command.downgrade(cfg, "a1")
print("after downgrade :", version())
command.upgrade(cfg, "head")

meta = sa.MetaData()
sa.Table("customers", meta, sa.Column("id", sa.Integer, primary_key=True), sa.Column("email_address", sa.Text),
         sa.Column("channel", sa.Text))
cfg.attributes["target_metadata"] = meta
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    script = command.revision(cfg, message="rename email", autogenerate=True, rev_id="a3")
print("autogenerate, told the column is now email_address, wrote this upgrade:")
body = open(script.path).read().split("def downgrade")[0]
print("\n".join("   " + l.strip() for l in body.splitlines() if "_column('customers'" in l))
os.remove(script.path)

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    command.upgrade(cfg, "a2", sql=True)
print("offline SQL for a DBA to review:")
print("\n".join("   " + l for l in buf.getvalue().splitlines()
                if l.startswith(("SET lock", "ALTER TABLE", "CREATE INDEX"))))

# --- warehouse_move ---
import duckdb
wh = duckdb.connect()
wh.execute("""CREATE TABLE trips AS SELECT i AS id, TIMESTAMP '2024-01-01' + INTERVAL (i % (366 * 24)) HOUR AS ts,
              (i * 7 % 2000) / 100.0 AS fare FROM range(1000000) t(i)""")
wh.execute("CREATE TABLE old_mart AS SELECT CAST(ts AS DATE) AS day, count(*) AS trips, round(sum(fare), 2) AS revenue FROM trips GROUP BY 1")
# The port to the new warehouse: same SQL, except the engine's session runs one hour behind UTC.
wh.execute("""CREATE TABLE new_mart AS SELECT CAST(ts - INTERVAL 1 HOUR AS DATE) AS day, count(*) AS trips,
              round(sum(fare), 2) AS revenue FROM trips GROUP BY 1""")
print("totals :", wh.execute("SELECT (SELECT sum(trips) FROM old_mart), (SELECT sum(trips) FROM new_mart), "
                             "(SELECT round(sum(revenue), 2) FROM old_mart), (SELECT round(sum(revenue), 2) FROM new_mart)").fetchall()[0])
print("by day :", wh.execute("""
  SELECT count(*) FILTER (WHERE o.trips = n.trips AND abs(o.revenue - n.revenue) < 0.01) AS matching,
         count(*) AS days,
         max(abs(o.revenue - n.revenue)) AS worst_gap
  FROM old_mart o FULL JOIN new_mart n USING (day)""").fetchall()[0])
rows = wh.execute("""
  SELECT coalesce(o.day, n.day) AS day, o.trips, n.trips FROM old_mart o FULL JOIN new_mart n USING (day)
  WHERE o.trips IS DISTINCT FROM n.trips ORDER BY 1 LIMIT 3""").fetchall()
print("first differing days:", [(str(d), a, b) for d, a, b in rows])

# --- reembed ---
import numpy as np
rng = np.random.default_rng(11)
TRUE_DIM, N, QUERIES = 256, 20_000, 200
centres = rng.normal(size=(200, TRUE_DIM))
meaning = centres[rng.integers(0, 200, N)] + rng.normal(scale=0.6, size=(N, TRUE_DIM))
ask = meaning[rng.integers(0, N, QUERIES)] + rng.normal(scale=0.3, size=(QUERIES, TRUE_DIM))

def model(seed, dim):
    """A stand-in embedding model: a fixed random projection, then unit length."""
    proj = np.random.default_rng(seed).normal(size=(TRUE_DIM, dim))
    def embed(x):
        v = x @ proj
        return v / np.linalg.norm(v, axis=1, keepdims=True)
    return embed
model_a, model_b = model(1, 128), model(2, 128)

def top10(index, query_vecs):
    return np.argsort(-(query_vecs @ index.T), axis=1)[:, :10]
truth = top10(meaning / np.linalg.norm(meaning, axis=1, keepdims=True), ask / np.linalg.norm(ask, axis=1, keepdims=True))
recall = lambda found: np.mean([len(set(f) & set(t)) / 10 for f, t in zip(found, truth)])

store = {"docs_v1": model_a(meaning)}                                            # a store with named collections
alias = {"docs": "docs_v1"}                                                      # what the application queries
print(f"model A, index A  recall@10 = {recall(top10(store[alias['docs']], model_a(ask))):.3f}")
print(f"model B, index A  recall@10 = {recall(top10(store[alias['docs']], model_b(ask))):.3f}  same shape, no error")
print(f"chance would be   recall@10 = {10 / N:.4f}")

store["docs_v2"] = np.zeros((N, 128))                                            # build a new collection on the side
updated_during_build = rng.choice(N, 500, replace=False)
store["docs_v2"][:] = model_b(meaning)                                           # the batch job, from a snapshot
changed = meaning.copy()
changed[updated_during_build] = centres[rng.integers(0, 200, 500)]               # docs edited during the build
store["docs_v1"] = model_a(changed)                                              # live writes reach the old index
stale = np.mean(np.abs(store["docs_v2"][updated_during_build] - model_b(changed)[updated_during_build]).sum(axis=1) > 1e-6)
print(f"built without dual writes: {stale:.0%} of the 500 docs edited during the build are stale in v2")
store["docs_v2"][updated_during_build] = model_b(changed)[updated_during_build]  # dual write, or replay the changes
meaning = changed
truth = top10(meaning / np.linalg.norm(meaning, axis=1, keepdims=True), ask / np.linalg.norm(ask, axis=1, keepdims=True))
gate = recall(top10(store["docs_v2"], model_b(ask)))
print(f"shadow test on v2 before cutover: recall@10 = {gate:.3f}")
alias["docs"] = "docs_v2"                                                        # one atomic pointer change
print("cutover: alias ->", alias["docs"], "| v1 kept for rollback:", "docs_v1" in store)

# --- tryit ---
db.execute("RESET lock_timeout")
report = connect()
report.autocommit = False
report.execute("SELECT count(*) FROM orders WHERE id = 1")
threading.Timer(1.0, report.rollback).start()                                    # the report ends after 1 s
ddl, attempts = connect(), 0
ddl.execute("SET lock_timeout = '100ms'")
with Probe("SELECT amount FROM orders WHERE id = %s") as p:
    while True:
        attempts += 1
        try:
            ddl.execute("ALTER TABLE orders ADD COLUMN flag2 int")
            break
        except psycopg.errors.LockNotAvailable:
            time.sleep(0.2)
print(f"retry loop: {attempts} attempts | reads: {p.report()}")
with connect() as c:
    try:
        c.autocommit = False
        c.execute("CREATE INDEX CONCURRENTLY i_tx ON orders (customer)")
    except psycopg.errors.ActiveSqlTransaction as e:
        print("in a transaction:", str(e).splitlines()[0])
db.execute("""CREATE TABLE gone AS SELECT 'a' AS v FROM generate_series(1, 1000);
              ALTER TABLE gone DROP COLUMN v; ALTER TABLE gone ADD COLUMN v text""")
print("rows with a value after drop and re-add:", db.execute("SELECT count(v) FROM gone").fetchone()[0])

# --- teardown ---
db.close()
tool("pg_ctl", "-w", "-D", f"{ROOT}/d", "-m", "fast", "stop")
shutil.rmtree(ROOT)
