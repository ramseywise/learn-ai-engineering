"""LRU Cache — live coding, 20-25 min.

PROMPT
    Implement an LRU (Least Recently Used) cache with `get(key)` and
    `put(key, value)` operations. Both should run in O(1) time.

The interviewer answered your clarifying questions as follows -- but ask them
anyway before you look:
    - `get` returns -1 on a miss.
    - Capacity is always >= 1.
    - Single-threaded; no thread safety needed.

Run this file to check the smoke test. Edge cases are yours to find.
"""


class LRUCache:
    def __init__(self, capacity: int) -> None:
        raise NotImplementedError

    def get(self, key: int) -> int:
        raise NotImplementedError

    def put(self, key: int, value: int) -> None:
        raise NotImplementedError


if __name__ == "__main__":
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    cache.put(3, 3)  # evicts key 2 (least recently used)
    assert cache.get(2) == -1
    print("smoke test passed")

    # your edge cases here
