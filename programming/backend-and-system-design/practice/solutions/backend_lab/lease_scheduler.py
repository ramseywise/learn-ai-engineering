"""A job scheduler with leases and fencing tokens, on SQLite. Chapter 8."""
import sqlite3


class LeaseScheduler:
    def __init__(self) -> None:
        self.db = sqlite3.connect(":memory:", isolation_level=None)
        self.db.executescript("""
            CREATE TABLE runs (
                job TEXT, due REAL, state TEXT DEFAULT 'pending', owner TEXT, lease_until REAL,
                token INTEGER DEFAULT 0, attempts INTEGER DEFAULT 0, PRIMARY KEY (job, due));
            CREATE TABLE effects (job TEXT, due REAL, token INTEGER, what TEXT);
        """)

    def add(self, job: str, due: float) -> None:
        """Record one run. The same (job, due) added twice makes one run."""
        self.db.execute("INSERT OR IGNORE INTO runs (job, due) VALUES (?, ?)", (job, due))

    def claim(self, worker: str, now: float, lease: float = 30.0, max_attempts: int = 3) -> tuple | None:
        """Atomically take the oldest due run, or an expired one; return (job, due, token).

        The token goes up on every claim. A run whose lease has expired with
        max_attempts used is marked 'failed' and never handed out again.
        """
        self.db.execute("BEGIN IMMEDIATE")
        self.db.execute("""UPDATE runs SET state='failed'
                            WHERE state='running' AND lease_until <= ? AND attempts >= ?""", (now, max_attempts))
        row = self.db.execute("""
            SELECT job, due, token FROM runs
             WHERE due <= ? AND attempts < ?
               AND (state = 'pending' OR (state = 'running' AND lease_until <= ?))
             ORDER BY due LIMIT 1""", (now, max_attempts, now)).fetchone()
        if row is None:
            self.db.execute("COMMIT")
            return None
        job, due, token = row
        self.db.execute("""UPDATE runs SET state='running', owner=?, lease_until=?, token=?, attempts=attempts+1
                            WHERE job=? AND due=?""", (worker, now + lease, token + 1, job, due))
        self.db.execute("COMMIT")
        return job, due, token + 1

    def heartbeat(self, job: str, due: float, token: int, now: float, lease: float = 30.0) -> bool:
        """Extend the lease if this token still holds it. False means stop working."""
        cur = self.db.execute("UPDATE runs SET lease_until=? WHERE job=? AND due=? AND token=? AND state='running'",
                              (now + lease, job, due, token))
        return cur.rowcount == 1

    def finish(self, job: str, due: float, token: int, what: str) -> bool:
        """Record the result and mark done, atomically, only for the current token."""
        self.db.execute("BEGIN IMMEDIATE")
        cur = self.db.execute("UPDATE runs SET state='done' WHERE job=? AND due=? AND token=? AND state='running'",
                              (job, due, token))
        accepted = cur.rowcount == 1
        if accepted:
            self.db.execute("INSERT INTO effects VALUES (?, ?, ?, ?)", (job, due, token, what))
        self.db.execute("COMMIT")
        return accepted

    def state(self, job: str, due: float) -> str:
        """The run's state: pending, running, done or failed."""
        return self.db.execute("SELECT state FROM runs WHERE job=? AND due=?", (job, due)).fetchone()[0]

    def effects(self) -> list[tuple]:
        """Every accepted result, as (job, token, what)."""
        return self.db.execute("SELECT job, token, what FROM effects").fetchall()
