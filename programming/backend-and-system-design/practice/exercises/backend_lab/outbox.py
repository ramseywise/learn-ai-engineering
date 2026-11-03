"""The transactional outbox, and a consumer that tolerates redelivery. Chapter 3."""
import json
import sqlite3
from typing import Callable

def connect() -> sqlite3.Connection:
    """An in-memory database with autocommit, so transactions are explicit."""
    db = sqlite3.connect(':memory:', isolation_level=None)
    db.executescript('\n        create table orders(id integer primary key, item text);\n        create table outbox(id integer primary key autoincrement, body text, sent int default 0);\n        create table processed(message_id integer primary key);\n        create table shipments(order_id integer);\n    ')
    return db

def place_order(db: sqlite3.Connection, item: str, fail: bool=False) -> int:
    """Insert the order and its outbox message in one transaction; return the id.

    `fail=True` simulates a crash just before commit: neither row may survive,
    and the exception (RuntimeError) reaches the caller.
    """
    raise NotImplementedError()

def relay(db: sqlite3.Connection, publish: Callable[[int, dict], None]) -> int:
    """Publish unsent messages in id order, marking each sent after it's published.

    If publish raises, stop and leave that message unsent. Return how many went.
    Publishing before marking means a crash between them sends twice, never zero.
    """
    raise NotImplementedError()

def consume(db: sqlite3.Connection, message_id: int, body: dict) -> bool:
    """Apply a message once. Return False for a redelivery.

    The processed row and the shipment commit in one transaction.
    """
    raise NotImplementedError()
