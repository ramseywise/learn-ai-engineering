---
title: "LC 460 — LFU Cache"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [design]
source: https://leetcode.com/problems/lfu-cache/
---
## Prompt

Design a Least Frequently Used (LFU) cache with a fixed `capacity`. `get(key)`
returns the value if present (else -1), and `put(key, value)` inserts or updates.
When the cache is full, evict the key used the fewest times; break ties by
evicting the least recently used among them. Both `get` and `put` count as a use
and bump the key's frequency. Aim for `O(1)` average time per operation.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Eviction needs both a frequency ordering and a recency tiebreaker among equally-frequent entries.

</details>

<details><summary>Hint 2</summary>

Keep a hash map from key to node plus a structure ordering nodes by (frequency, last-used time). Update it on each get and put by reinserting the touched node.

</details>

<details><summary>Hint 3</summary>

An ordered-set version costs O(log n) per operation. The true O(1) design instead chains a doubly linked list per frequency bucket.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Evict the least-frequently-used entry, breaking ties by least-recently-used. This design keeps a hash map key -> node plus an ordered set of nodes sorted by (frequency, last-use timestamp). Both get and put bump a node's frequency and timestamp, then remove and reinsert it. Eviction removes the set's first (smallest) node, at O(log n) per operation. The O(1) design instead chains a doubly linked list per frequency bucket.

```python
nodes: key -> node(freq, last_used, value)
sorted set of nodes ordered by (freq, last_used)
get/put on existing key: erase from set; freq++; last_used = tick++; reinsert
put new key when full: evict set.begin() (lowest freq, oldest); insert node freq=1
```

**Complexity** — time O(log n) per operation; space O(capacity)

The prompt asks for O(1), which needs a bucket of keys per frequency, each ordered by last use, plus the current minimum frequency:

```python
from collections import OrderedDict, defaultdict

class LFUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.entries = {}                          # key -> [value, freq]
        self.buckets = defaultdict(OrderedDict)    # freq -> keys, oldest use first
        self.min_freq = 0

    def _touch(self, key):
        entry = self.entries[key]
        freq = entry[1]
        del self.buckets[freq][key]
        if not self.buckets[freq]:
            del self.buckets[freq]
            if self.min_freq == freq:
                self.min_freq = freq + 1           # the key moves to freq + 1, so that bucket exists
        entry[1] = freq + 1
        self.buckets[freq + 1][key] = None

    def get(self, key):
        if key not in self.entries:
            return -1
        self._touch(key)
        return self.entries[key][0]

    def put(self, key, value):
        if self.capacity == 0:
            return
        if key in self.entries:
            self.entries[key][0] = value
            self._touch(key)
            return
        if len(self.entries) == self.capacity:
            oldest, _ = self.buckets[self.min_freq].popitem(last=False)
            if not self.buckets[self.min_freq]:
                del self.buckets[self.min_freq]
            del self.entries[oldest]
        self.entries[key] = [value, 1]
        self.buckets[1][key] = None
        self.min_freq = 1
```

**Complexity** — average O(1) time per operation; space O(capacity)

Full Python solution: `LeetCodeCheat/lfu-cache.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Design the true O(1) version with per-frequency linked lists.
- How does LFU differ from LRU under a scan-heavy workload?
- Handle capacity zero and frequency ties precisely.

Sources:

- [LeetCode - LFU Cache](https://leetcode.com/problems/lfu-cache/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/460-lfu-cache.yaml`.
