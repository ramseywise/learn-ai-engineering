import pytest

from mini_kv import MiniKV


@pytest.fixture
def store(tmp_path):
    s = MiniKV(tmp_path, memtable_limit=4)
    yield s
    s.close()


def fill(s, n, prefix="k", value="v"):
    for i in range(n):
        s.put(f"{prefix}{i}", f"{value}{i}")


def test_put_get_across_a_flush(store):
    fill(store, 10)
    assert len(store.tables) == 2 and store.get("k0") == "v0" and store.get("k9") == "v9"
    assert store.get("missing") is None


def test_newest_table_wins(store):
    for round_ in ("old", "new"):
        for i in range(4):
            store.put(f"k{i}", f"{round_}{i}")
    assert len(store.tables) == 2 and store.get("k1") == "new1"


def test_tombstone_survives_a_flush(store):
    fill(store, 4)
    store.delete("k1")
    fill(store, 3, prefix="x")
    assert len(store.tables) == 2 and store.memtable == {}
    assert store.get("k1") is None and store.get("k2") == "v2"


def test_recovery_from_the_log(tmp_path):
    s = MiniKV(tmp_path, memtable_limit=100)
    s.put("a", "1")
    s.delete("a")
    s.put("b", "2")
    s.close()
    again = MiniKV(tmp_path, memtable_limit=100)
    assert again.get("a") is None and again.get("b") == "2"
    again.close()


def test_recovery_ignores_a_torn_last_line(tmp_path):
    s = MiniKV(tmp_path, memtable_limit=100)
    s.put("a", "1")
    s.close()
    with open(tmp_path / "wal.log", "a") as f:
        f.write('["b", "tor')
    again = MiniKV(tmp_path, memtable_limit=100)
    assert again.get("a") == "1" and again.get("b") is None
    again.close()


def test_tables_are_reloaded_and_flush_truncates_the_log(tmp_path):
    s = MiniKV(tmp_path, memtable_limit=2)
    fill(s, 2)
    assert (tmp_path / "wal.log").read_text() == ""
    s.put("z", "9")
    s.close()
    again = MiniKV(tmp_path, memtable_limit=2)
    assert again.get("k0") == "v0" and again.get("z") == "9"
    again.close()


def test_table_numbers_keep_rising_after_reopen(tmp_path):
    s = MiniKV(tmp_path, memtable_limit=1)
    s.put("a", "old")
    s.close()
    again = MiniKV(tmp_path, memtable_limit=1)
    again.put("a", "new")
    assert again.get("a") == "new"
    again.close()
    third = MiniKV(tmp_path, memtable_limit=1)
    assert third.get("a") == "new"
    third.close()


def test_compaction_merges_and_drops_tombstones(store, tmp_path):
    fill(store, 4)
    for i in range(4):
        store.put(f"k{i}", f"new{i}")
    store.delete("k3")
    fill(store, 3, prefix="x")
    assert len(store.tables) == 3
    store.compact()
    assert len(store.tables) == 1 and len(list(tmp_path.glob("table-*.json"))) == 1
    assert store.get("k0") == "new0" and store.get("k3") is None and store.get("x2") == "v2"
    assert "k3" not in store.tables[0][0]


def test_compaction_survives_reopen(tmp_path):
    s = MiniKV(tmp_path, memtable_limit=2)
    fill(s, 6)
    s.compact()
    s.close()
    again = MiniKV(tmp_path, memtable_limit=2)
    assert again.get("k5") == "v5"
    again.close()
