import threading

import pytest

from single_flight import SingleFlight


def run_many(fn, n):
    results, errors = [], []
    start = threading.Barrier(n)

    def work():
        start.wait()
        try:
            results.append(fn())
        except Exception as err:
            errors.append(err)

    threads = [threading.Thread(target=work) for _ in range(n)]
    for t in threads:
        t.start()
    return threads, results, errors


def test_many_callers_one_load():
    flight, calls, release = SingleFlight(), [], threading.Event()
    started = threading.Event()

    def load():
        calls.append(1)
        started.set()
        release.wait(5)
        return "value"

    threads, results, errors = run_many(lambda: flight.do("k", load), 16)
    started.wait(1)
    threading.Event().wait(0.05)  # let the others reach the wait
    release.set()
    for t in threads:
        t.join(5)
    assert results == ["value"] * 16 and not errors and len(calls) == 1


def test_leader_failure_reaches_every_waiter():
    flight, calls, release = SingleFlight(), [], threading.Event()
    started = threading.Event()

    def load():
        calls.append(1)
        started.set()
        release.wait(5)
        raise RuntimeError("backend down")

    threads, results, errors = run_many(lambda: flight.do("k", load), 8)
    started.wait(1)
    threading.Event().wait(0.05)
    release.set()
    for t in threads:
        t.join(5)
    assert not any(t.is_alive() for t in threads)
    assert len(errors) == 8 and all(str(e) == "backend down" for e in errors) and len(calls) == 1


def test_later_call_loads_again_after_failure_and_success():
    flight = SingleFlight()

    def bad():
        raise RuntimeError("no")

    with pytest.raises(RuntimeError):
        flight.do("k", bad)
    assert flight.do("k", lambda: 1) == 1
    assert flight.do("k", lambda: 2) == 2


def test_keys_do_not_block_each_other():
    flight = SingleFlight()
    inner = []

    def outer():
        inner.append(flight.do("b", lambda: "b"))
        return "a"

    assert flight.do("a", outer) == "a" and inner == ["b"]
