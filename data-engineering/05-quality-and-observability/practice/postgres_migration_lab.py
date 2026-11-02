"""Postgres migration lab for notes/04-schema-and-data-migrations.md.

A small application reads and writes a table while you change that table's schema.
The lab scores each migration on what the application saw and on what the data ended up as.

Goal state for `accounts`:
  - `cust_email` is now `email`, NOT NULL and indexed
  - `amount` (whole units, int) is now `amount_cents` (bigint)
  - no leftover triggers or old columns

Run from any folder (it starts a private Postgres in a temporary directory):
    uv run --no-project --python 3.12 --with pgserver --with 'psycopg[binary]' python postgres_migration_lab.py

Options:
    --exercise     score your own your_migration() instead of the built-in safe one
    --no-trigger   run the safe migration without dual writes
    --one-batch    run the safe migration with one huge backfill statement

Exercises:
  1. Run the lab and read the scorecard. Which phase caused the naive migration's errors?
  2. Run --no-trigger. Errors stay at zero and the data is wrong. Why does nothing report it?
  3. Run --one-batch. Why does a backfill stall a table with no schema change at all?
  4. Write your_migration() and run --exercise. Your target: zero errors, zero wrong rows,
     every goal met, worst stall under 250 ms on an otherwise quiet machine.
"""
import collections, os, random, shutil, subprocess, sys, tempfile, threading, time
import pgserver, psycopg

BIN = os.path.dirname(pgserver.__file__) + "/pginstall/bin"
ROOT = tempfile.mkdtemp(dir="/tmp", prefix="lab")
PORT, ROWS, DEPLOY_SECONDS = 5612, 500_000, 1.0
STALL_LIMIT_MS = 250


def tool(name, *args):
    return subprocess.run([f"{BIN}/{name}", *args], check=True, capture_output=True, text=True).stdout


def connect():
    return psycopg.connect(f"host={ROOT} port={PORT} user=postgres dbname=postgres", autocommit=True)


class App:
    """Reads and writes in a loop. `version` is what is deployed: old, mixed (mid-rollout) or new."""
    OLD = {"read": "SELECT cust_email, amount FROM accounts WHERE id = %s",
           "write": "UPDATE accounts SET amount = amount + 1 WHERE id = %s"}
    NEW = {"read": "SELECT email, amount_cents FROM accounts WHERE id = %s",
           "write": "UPDATE accounts SET amount_cents = amount_cents + 100 WHERE id = %s"}

    def __init__(self):
        self.version, self.halt = "old", threading.Event()
        self.errors, self.worst, self.queries = collections.Counter(), 0.0, 0
        self.applied = collections.Counter()                  # successful writes per id: the truth
        self.threads = [threading.Thread(target=self.loop, args=(kind,)) for kind in ("read", "write")]

    def code(self):
        version = random.choice(["old", "new"]) if self.version == "mixed" else self.version
        return self.OLD if version == "old" else self.NEW

    def loop(self, kind):
        conn = connect()
        rng = random.Random(kind)
        while not self.halt.is_set():
            key, sql = rng.randint(1, ROWS), self.code()[kind]
            start = time.perf_counter()
            try:
                conn.execute(sql, (key,))
                if kind == "write":
                    self.applied[key] += 1
            except psycopg.Error as e:
                self.errors[f"{kind}: {type(e).__name__}"] += 1
            self.worst = max(self.worst, time.perf_counter() - start)
            self.queries += 1
            time.sleep(0.001)
        conn.close()

    def __enter__(self):
        for t in self.threads:
            t.start()
        time.sleep(0.2)
        return self

    def __exit__(self, *a):
        self.halt.set()
        for t in self.threads:
            t.join()


def reset(db):
    db.execute(f"""DROP TABLE IF EXISTS accounts;
                  DROP FUNCTION IF EXISTS sync_accounts();
                  CREATE TABLE accounts (id bigint PRIMARY KEY, cust_email text, amount int NOT NULL);
                  INSERT INTO accounts SELECT i, 'u' || i || '@x.io', i % 1000 FROM generate_series(1, {ROWS}) i""")


def unmet_goals(db):
    """What in the goal state is not true of the table now."""
    columns = dict(db.execute("""SELECT column_name, is_nullable FROM information_schema.columns
                                 WHERE table_name = 'accounts'""").fetchall())
    missing = []
    if columns.get("email") != "NO":
        missing.append("email missing or nullable")
    if "amount_cents" not in columns:
        missing.append("amount_cents missing")
    if {"cust_email", "amount"} & set(columns):
        missing.append("old columns still there")
    if db.execute("SELECT count(*) FROM pg_trigger WHERE tgrelid = 'accounts'::regclass AND NOT tgisinternal").fetchone()[0]:
        missing.append("trigger left behind")
    valid = db.execute("""SELECT count(*) FROM pg_index i JOIN pg_attribute a
                          ON a.attrelid = i.indrelid AND a.attnum = i.indkey[0]
                          WHERE i.indrelid = 'accounts'::regclass AND a.attname = 'email' AND i.indisvalid""").fetchone()[0]
    if not valid:
        missing.append("no valid index on email")
    return missing


def wrong_rows(db, app):
    """Compare every row against the start value plus the writes the application saw succeed."""
    columns = {r[0] for r in db.execute("""SELECT column_name FROM information_schema.columns
                                           WHERE table_name = 'accounts'""").fetchall()}
    if "amount_cents" not in columns:
        return ROWS
    rows = db.execute("SELECT id, amount_cents FROM accounts").fetchall()
    return sum(cents != (key % 1000 + app.applied[key]) * 100 for key, cents in rows)


def ddl_with_retry(conn, sql, timeout="200ms", pause=0.3):
    """Never queue for long behind a long reader: give up the lock attempt and try again."""
    conn.execute(f"SET lock_timeout = '{timeout}'")
    while True:
        try:
            return conn.execute(sql)
        except psycopg.errors.LockNotAvailable:
            time.sleep(pause)


def naive_migration(app, db):
    """The change as a developer first writes it: one transaction, then deploy."""
    with db.transaction():
        db.execute("ALTER TABLE accounts RENAME COLUMN cust_email TO email")
        db.execute("ALTER TABLE accounts ALTER COLUMN amount TYPE bigint USING amount * 100")
        db.execute("ALTER TABLE accounts RENAME COLUMN amount TO amount_cents")
        db.execute("CREATE INDEX accounts_email ON accounts (email)")
        db.execute("ALTER TABLE accounts ALTER COLUMN email SET NOT NULL")
    app.version = "mixed"
    time.sleep(DEPLOY_SECONDS)
    app.version = "new"


def safe_migration(app, db, trigger=True, batch=5_000):
    """Expand, migrate, contract. Each step is short, and old and new code both work until the end."""
    # expand
    ddl_with_retry(db, "ALTER TABLE accounts ADD COLUMN email text, ADD COLUMN amount_cents bigint")
    db.execute("""CREATE FUNCTION sync_accounts() RETURNS trigger LANGUAGE plpgsql AS $$
                  BEGIN
                    IF TG_OP = 'INSERT' OR NEW.cust_email IS DISTINCT FROM OLD.cust_email THEN
                      NEW.email := NEW.cust_email;
                    ELSIF NEW.email IS DISTINCT FROM OLD.email THEN
                      NEW.cust_email := NEW.email;
                    END IF;
                    IF TG_OP = 'INSERT' OR NEW.amount IS DISTINCT FROM OLD.amount THEN
                      NEW.amount_cents := NEW.amount * 100;
                    ELSIF NEW.amount_cents IS DISTINCT FROM OLD.amount_cents THEN
                      NEW.amount := NEW.amount_cents / 100;
                    END IF;
                    RETURN NEW;
                  END $$""")
    if trigger:
        ddl_with_retry(db, """CREATE TRIGGER sync_accounts BEFORE INSERT OR UPDATE ON accounts
                              FOR EACH ROW EXECUTE FUNCTION sync_accounts()""")
    # backfill: short keyed transactions, restartable because it only touches unfilled rows
    for low in range(0, ROWS, batch):
        db.execute("""UPDATE accounts SET email = cust_email, amount_cents = amount * 100
                      WHERE id > %s AND id <= %s AND (email IS NULL OR amount_cents IS NULL)""", (low, low + batch))
    # verify before anything reads the new columns
    if trigger:
        differ = db.execute("""SELECT count(*) FROM accounts WHERE email IS DISTINCT FROM cust_email
                               OR amount_cents IS DISTINCT FROM amount * 100""").fetchone()[0]
        assert differ == 0, f"{differ} rows differ; do not deploy"
    # constraints and indexes that do not block the application
    ddl_with_retry(db, "ALTER TABLE accounts ADD CONSTRAINT email_nn CHECK (email IS NOT NULL) NOT VALID")
    db.execute("ALTER TABLE accounts VALIDATE CONSTRAINT email_nn")
    ddl_with_retry(db, "ALTER TABLE accounts ALTER COLUMN email SET NOT NULL")
    ddl_with_retry(db, "ALTER TABLE accounts DROP CONSTRAINT email_nn")
    db.execute("CREATE INDEX CONCURRENTLY accounts_email ON accounts (email)")
    # deploy: old and new code run side by side
    app.version = "mixed"
    time.sleep(DEPLOY_SECONDS)
    app.version = "new"
    time.sleep(0.2)                                            # the last old instance has drained
    # contract
    ddl_with_retry(db, "DROP TRIGGER IF EXISTS sync_accounts ON accounts")
    ddl_with_retry(db, "ALTER TABLE accounts DROP COLUMN cust_email, DROP COLUMN amount")
    db.execute("DROP FUNCTION sync_accounts()")
    db.execute("RESET lock_timeout")


def your_migration(app, db):
    """Exercise 4: replace this body. Flip app.version to "mixed", then "new", when your schema allows."""
    raise NotImplementedError("write your migration here, then run --exercise")


def run(name, migration):
    db = connect()
    reset(db)
    with App() as app:
        start = time.perf_counter()
        migration(app, db)
        took = time.perf_counter() - start
        time.sleep(0.2)
    wrong, goals = wrong_rows(db, app), unmet_goals(db)
    errors = sum(app.errors.values())
    passed = not errors and not wrong and not goals and app.worst * 1000 < STALL_LIMIT_MS
    print(f"{name:18s} {took:5.1f} s | {app.queries:6,d} queries | {errors:5,d} errors | "
          f"worst stall {app.worst * 1000:6.0f} ms | {wrong:5,d} wrong rows | {'PASS' if passed else 'FAIL'}")
    for kind, n in sorted(app.errors.items()):
        print(f"{'':18s} {n:5,d} {kind}")
    for goal in goals:
        print(f"{'':18s} unmet: {goal}")
    db.close()
    return errors, wrong, goals, app.worst * 1000


def main():
    tool("initdb", "-D", f"{ROOT}/d", "-U", "postgres", "--auth=trust", "-E", "UTF8")
    with open(f"{ROOT}/d/postgresql.conf", "a") as f:
        f.write(f"listen_addresses=''\nunix_socket_directories='{ROOT}'\nport={PORT}\nmax_wal_size=4GB\n")
    tool("pg_ctl", "-w", "-D", f"{ROOT}/d", "-l", f"{ROOT}/log", "start")
    try:
        if "--exercise" in sys.argv:
            run("yours", your_migration)
        elif "--no-trigger" in sys.argv:
            run("no dual write", lambda a, d: safe_migration(a, d, trigger=False))
        elif "--one-batch" in sys.argv:
            run("one big backfill", lambda a, d: safe_migration(a, d, batch=ROWS))
        else:
            n_errors, _, n_goals, _ = run("naive", naive_migration)
            s_errors, s_wrong, s_goals, _ = run("expand-contract", safe_migration)
            assert n_errors > 0 and not n_goals, "naive should reach the goal but hurt the application"
            assert s_errors == 0 and s_wrong == 0 and not s_goals, "safe migration must be clean"
            print("checks passed: naive reached the goal and broke the application; expand-contract did neither")
    finally:
        subprocess.run([f"{BIN}/pg_ctl", "-w", "-D", f"{ROOT}/d", "-m", "immediate", "stop"], capture_output=True)
        shutil.rmtree(ROOT, ignore_errors=True)


if __name__ == "__main__":
    main()
