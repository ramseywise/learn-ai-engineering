"""The transactional outbox, and a consumer that tolerates redelivery. Chapter 3."""
import json
import sqlite3
from typing import Callable


def connect() -> sqlite3.Connection:
    """An in-memory database with autocommit, so transactions are explicit."""
    db = sqlite3.connect(":memory:", isolation_level=None)
    db.executescript("""
        create table orders(id integer primary key, item text);
        create table outbox(id integer primary key autoincrement, body text, sent int default 0);
        create table processed(message_id integer primary key);
        create table shipments(order_id integer);
    """)
    return db


def place_order(db: sqlite3.Connection, item: str, fail: bool = False) -> int:
    """Insert the order and its outbox message in one transaction; return the id.

    `fail=True` simulates a crash just before commit: neither row may survive,
    and the exception (RuntimeError) reaches the caller.
    """
    db.execute("begin")
    try:
        order_id = db.execute("insert into orders(item) values (?)", (item,)).lastrowid
        db.execute("insert into outbox(body) values (?)", (json.dumps({"order_id": order_id}),))
        if fail:
            raise RuntimeError("crash before commit")
        db.execute("commit")
    except BaseException:
        db.execute("rollback")
        raise
    return order_id


def relay(db: sqlite3.Connection, publish: Callable[[int, dict], None]) -> int:
    """Publish unsent messages in id order, marking each sent after it's published.

    If publish raises, stop and leave that message unsent. Return how many went.
    Publishing before marking means a crash between them sends twice, never zero.
    """
    count = 0
    rows = db.execute("select id, body from outbox where sent = 0 order by id").fetchall()
    for message_id, body in rows:
        publish(message_id, json.loads(body))
        db.execute("update outbox set sent = 1 where id = ?", (message_id,))
        count += 1
    return count


def consume(db: sqlite3.Connection, message_id: int, body: dict) -> bool:
    """Apply a message once. Return False for a redelivery.

    The processed row and the shipment commit in one transaction.
    """
    db.execute("begin")
    try:
        db.execute("insert into processed values (?)", (message_id,))
    except sqlite3.IntegrityError:
        db.execute("rollback")
        return False
    db.execute("insert into shipments values (?)", (body["order_id"],))
    db.execute("commit")
    return True
