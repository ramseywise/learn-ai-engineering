import pytest

from outbox import connect, consume, place_order, relay


def count(db, table):
    return db.execute(f"select count(*) from {table}").fetchone()[0]


def test_both_rows_or_neither():
    db = connect()
    place_order(db, "book")
    assert count(db, "orders") == count(db, "outbox") == 1
    with pytest.raises(RuntimeError):
        place_order(db, "lamp", fail=True)
    assert count(db, "orders") == count(db, "outbox") == 1


def test_relay_sends_each_once_in_order():
    db = connect()
    for item in "abc":
        place_order(db, item)
    sent = []
    assert relay(db, lambda mid, body: sent.append(mid)) == 3
    assert sent == [1, 2, 3]
    assert relay(db, lambda mid, body: sent.append(mid)) == 0


def test_broker_down_keeps_the_message():
    db = connect()
    place_order(db, "a")
    place_order(db, "b")
    sent = []

    def flaky(mid, body):
        if mid == 2:
            raise ConnectionError
        sent.append(mid)

    with pytest.raises(ConnectionError):
        relay(db, flaky)
    assert sent == [1]
    relay(db, lambda mid, body: sent.append(mid))
    assert sent == [1, 2]


def test_consumer_applies_a_redelivery_once():
    db = connect()
    assert consume(db, 7, {"order_id": 1}) is True
    assert consume(db, 7, {"order_id": 1}) is False
    assert count(db, "shipments") == 1
    assert consume(db, 8, {"order_id": 2}) is True
    assert count(db, "shipments") == 2
