from collections import Counter

import pytest

from hash_ring import HashRing, stable_hash

KEYS = [f"key-{i}" for i in range(10_000)]
NODES = [f"node-{i}" for i in range(10)]


def test_stable_hash_is_fixed_across_processes():
    assert stable_hash("abc") == int("ba7816bf8f01cfea", 16)  # first 8 bytes of SHA-256


def test_adding_a_node_moves_about_one_share_only_onto_it():
    before = HashRing(NODES)
    after = HashRing(NODES + ["node-new"])
    moved = [k for k in KEYS if before.owner(k) != after.owner(k)]
    assert all(after.owner(k) == "node-new" for k in moved)
    assert 0.05 < len(moved) / len(KEYS) < 0.15


def test_removing_a_node_moves_only_its_keys():
    ring = HashRing(NODES)
    owners = {k: ring.owner(k) for k in KEYS}
    ring.remove("node-3")
    for k in KEYS:
        if owners[k] != "node-3":
            assert ring.owner(k) == owners[k]
        else:
            assert ring.owner(k) != "node-3"


def test_virtual_nodes_even_out_the_load():
    few = Counter(HashRing(NODES, vnodes=1).owner(k) for k in KEYS)
    many = Counter(HashRing(NODES, vnodes=200).owner(k) for k in KEYS)
    assert max(many.values()) < max(few.values())
    assert max(many.values()) < 1.5 * len(KEYS) / len(NODES)


def test_replicas_are_distinct_and_start_with_the_owner():
    ring = HashRing(NODES)
    for k in KEYS[:200]:
        r = ring.replicas(k, 3)
        assert len(set(r)) == 3 and r[0] == ring.owner(k)


def test_more_replicas_than_nodes_returns_all():
    assert sorted(HashRing(["a", "b"]).replicas("k", 5)) == ["a", "b"]


def test_empty_ring():
    with pytest.raises(LookupError):
        HashRing([]).owner("k")
