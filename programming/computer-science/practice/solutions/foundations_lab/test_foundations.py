import random
import socket
import threading

import pytest

from dynamic_array import DynamicArray
from framing import FrameDecoder, encode_frame
from hash_table import CompactDict
from lru_cache import LRUCache
from rto import RtoEstimator
from summation import neumaier_sum


# Dynamic array
def test_array_keeps_values_in_order():
    a = DynamicArray()
    for i in range(1_000):
        a.append(i)
    assert len(a) == 1_000
    assert [a[i] for i in (0, 1, 999)] == [0, 1, 999]
    with pytest.raises(IndexError):
        a[1_000]


def test_doubling_copies_are_linear():
    a = DynamicArray()
    for i in range(2**16):
        a.append(i)
    assert a.resizes == 16
    assert a.copies == 2**16 - 1


def test_constant_increment_copies_are_quadratic():
    a = DynamicArray(grow=lambda c: c + 100)
    n = 20_000
    for i in range(n):
        a.append(i)
    assert a.copies / n > 50


def test_pop_returns_last_and_shrinks_with_hysteresis():
    a = DynamicArray()
    for i in range(1_024):
        a.append(i)
    assert a.pop() == 1_023
    before = a.resizes
    a.append(1_023)
    a.pop()
    a.append(1_023)
    assert a.resizes == before, "an append/pop pair at the boundary must not keep resizing"
    while len(a):
        a.pop()
    assert a.capacity <= 2
    with pytest.raises(IndexError):
        a.pop()


# Hash table
def test_table_behaves_like_dict_under_random_operations():
    rng = random.Random(1)
    ours, real = CompactDict(), {}
    for _ in range(20_000):
        k = rng.randrange(500)
        action = rng.random()
        if action < 0.6:
            ours[k] = real[k] = rng.random()
        elif k in real:
            assert ours[k] == real[k]
            if action > 0.8:
                del ours[k], real[k]
        else:
            assert k not in ours
            with pytest.raises(KeyError):
                ours[k]
        assert len(ours) == len(real)
    assert list(ours) == list(real)


def test_table_iterates_in_insertion_order():
    t = CompactDict()
    for word in ["prompt", "tokens", "model", "cost"]:
        t[word] = len(word)
    del t["tokens"]
    t["tokens"] = 6
    t["prompt"] = 0
    assert list(t) == ["prompt", "model", "cost", "tokens"]


def test_delete_keeps_later_keys_reachable():
    t = CompactDict(hash_fn=lambda k: 0)  # everything collides
    for k in "abcd":
        t[k] = k
    del t["b"]
    assert t["c"] == "c" and t["d"] == "d"
    assert "b" not in t


def test_table_handles_negative_hashes():
    t = CompactDict(hash_fn=lambda k: -k - 2)
    for k in range(100):
        t[k] = k * 2
    assert all(t[k] == k * 2 for k in range(100))


def test_high_bits_reach_the_probe_sequence():
    keys = [i << 16 for i in range(5_000)]
    t = CompactDict()
    for k in keys:
        t[k] = True
    assert t.probes / len(keys) < 12, "low bits alone would give thousands of probes per key"


def test_rebuild_reclaims_deleted_space():
    t = CompactDict()
    for k in range(10_000):
        t[k] = k
    for k in range(9_990):
        del t[k]
    t[-1] = 0  # may not resize at once; keep inserting until it does
    for k in range(20_000, 20_000 + 20_000):
        t[k] = k
        if len(t._entries) == len(t):
            break
    assert len(t._entries) == len(t), "a rebuild drops deleted entries"


# LRU
def test_lru_evicts_least_recently_used():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1
    c.put("c", 3)
    assert c.get("b") is None
    assert c.keys_newest_first() == ["c", "a"]
    assert c.evictions == 1


def test_lru_put_refreshes_recency_without_evicting():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("a", 10)
    assert c.evictions == 0 and c.get("a") == 10
    c.put("c", 3)
    assert c.get("b") is None


def test_lru_counts_and_capacity_of_one():
    c = LRUCache(1)
    c.put("a", 1)
    c.put("b", 2)
    assert len(c) == 1
    assert (c.get("a"), c.get("b")) == (None, 2)
    assert (c.hits, c.misses) == (1, 1)
    with pytest.raises(ValueError):
        LRUCache(0)


def test_lru_stays_correct_against_a_model():
    rng = random.Random(3)
    c, model = LRUCache(16), {}
    for _ in range(20_000):
        k = rng.randrange(40)
        if rng.random() < 0.5:
            c.put(k, k)
            model.pop(k, None)
            model[k] = k
            if len(model) > 16:
                del model[next(iter(model))]
        else:
            expected = model.get(k)
            assert c.get(k) == expected
            if expected is not None:
                model[k] = model.pop(k)
    assert c.keys_newest_first() == list(reversed(model))


# Summation
def test_compensated_sum_handles_large_cancelling_terms():
    assert neumaier_sum([1e16, 1.0, -1e16, 1.0] * 1000) == 2000.0


def test_compensated_sum_handles_an_addend_bigger_than_the_total():
    assert neumaier_sum([1.0, 1e100, 1.0, -1e100]) == 2.0


def test_compensated_sum_of_tenths():
    assert neumaier_sum([0.1] * 10) == 1.0
    assert neumaier_sum([]) == 0.0


# Framing
def test_frames_survive_any_cut():
    stream = b"".join(encode_frame(m) for m in [b"first", b"", b"third" * 100])
    for cut in range(1, 12):
        d = FrameDecoder()
        out = []
        for i in range(0, len(stream), cut):
            out += d.feed(stream[i:i + cut])
        assert out == [b"first", b"", b"third" * 100]
        assert d.pending == 0


def test_decoder_rejects_oversized_header_before_buffering():
    d = FrameDecoder(max_size=10)
    with pytest.raises(ValueError):
        d.feed((1 << 31).to_bytes(4, "big"))
    with pytest.raises(ValueError):
        encode_frame(b"x" * 11, max_size=10)


def test_frames_over_a_real_socket():
    listener = socket.create_server(("127.0.0.1", 0))
    messages = [bytes([i]) * (i * 997) for i in range(1, 60)]

    def send():
        with socket.create_connection(listener.getsockname()) as s:
            for m in messages:
                s.sendall(encode_frame(m))

    threading.Thread(target=send, daemon=True).start()
    conn, _ = listener.accept()
    conn.settimeout(5)
    d, got = FrameDecoder(), []
    with conn, listener:
        while data := conn.recv(4096):
            got += d.feed(data)
    assert got == messages


# RTO, with values worked by hand from RFC 6298 section 2
def test_rto_first_sample():
    e = RtoEstimator(minimum=0.0)
    assert e.rto == 1.0
    e.sample(0.1)
    assert e.srtt == pytest.approx(0.1)
    assert e.rttvar == pytest.approx(0.05)
    assert e.rto == pytest.approx(0.3)


def test_rto_second_sample_updates_rttvar_from_old_srtt():
    e = RtoEstimator(minimum=0.0)
    e.sample(0.1)
    e.sample(0.5)
    assert e.rttvar == pytest.approx(0.75 * 0.05 + 0.25 * 0.4)
    assert e.srtt == pytest.approx(0.875 * 0.1 + 0.125 * 0.5)


def test_rto_floor_backoff_and_ceiling():
    e = RtoEstimator()
    assert e.sample(0.01) == 1.0
    assert e.on_timeout() == 2.0
    for _ in range(10):
        e.on_timeout()
    assert e.rto == 60.0


def test_rto_uses_granularity_when_variance_is_zero():
    e = RtoEstimator(granularity=0.5, minimum=0.0)
    for _ in range(100):
        e.sample(1.0)
    assert e.rto == pytest.approx(e.srtt + 0.5, abs=1e-3)
