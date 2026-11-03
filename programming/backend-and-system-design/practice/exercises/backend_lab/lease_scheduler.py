"""A job scheduler with leases and fencing tokens, on SQLite. Chapter 8."""
import sqlite3

class LeaseScheduler:

    def __init__(self) -> None:
        self.db = sqlite3.connect(':memory:', isolation_level=None)
        self.db.executescript("\n            CREATE TABLE runs (\n                job TEXT, due REAL, state TEXT DEFAULT 'pending', owner TEXT, lease_until REAL,\n                token INTEGER DEFAULT 0, attempts INTEGER DEFAULT 0, PRIMARY KEY (job, due));\n            CREATE TABLE effects (job TEXT, due REAL, token INTEGER, what TEXT);\n        ")

    def add(self, job: str, due: float) -> None:
        """Record one run. The same (job, due) added twice makes one run."""
        raise NotImplementedError()

    def claim(self, worker: str, now: float, lease: float=30.0, max_attempts: int=3) -> tuple | None:
        """Atomically take the oldest due run, or an expired one; return (job, due, token).

        The token goes up on every claim. A run whose lease has expired with
        max_attempts used is marked 'failed' and never handed out again.
        """
        raise NotImplementedError()

    def heartbeat(self, job: str, due: float, token: int, now: float, lease: float=30.0) -> bool:
        """Extend the lease if this token still holds it. False means stop working."""
        raise NotImplementedError()

    def finish(self, job: str, due: float, token: int, what: str) -> bool:
        """Record the result and mark done, atomically, only for the current token."""
        raise NotImplementedError()

    def state(self, job: str, due: float) -> str:
        """The run's state: pending, running, done or failed."""
        return self.db.execute('SELECT state FROM runs WHERE job=? AND due=?', (job, due)).fetchone()[0]

    def effects(self) -> list[tuple]:
        """Every accepted result, as (job, token, what)."""
        return self.db.execute('SELECT job, token, what FROM effects').fetchall()
