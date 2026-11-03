---
title: "LRU Cache"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [design]
source: https://leetcode.com/problems/lru-cache/
---
## Prompt

Design a data structure for a Least Recently Used (LRU) cache with a fixed
capacity. Support get(key) — return the value if present, else -1 — and
put(key, value) — insert or update. Both operations must run in O(1) average
time. When capacity is exceeded, evict the least recently used entry. Both get
and put count as "using" a key.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

You need O(1) lookup by key together with O(1) reordering by recency, which no single structure provides alone.

</details>

<details><summary>Hint 2</summary>

Combine a hash map from key to node with a doubly linked list ordered by recency, moving a node to the front on every access.

</details>

<details><summary>Hint 3</summary>

Use dummy head and tail sentinels to avoid null checks. Evict the node before the tail sentinel when over capacity, for true O(1) get and put.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Combine a hash map with a doubly linked list. The hash map maps key -> node, giving O(1) lookup of any entry. The doubly linked list stores nodes in recency order: most-recently-used near the head, least-recently-used near the tail. A doubly linked list (not singly) is required so any node can be unlinked in O(1), because you have direct pointers to its neighbors. On every get and put, move the touched node to the head to mark it most-recently used. On put past capacity, evict the tail node (LRU) and delete its key from the map. Use dummy head and tail sentinel nodes so insertion and removal never need null checks.

```python
class Node: key, val, prev, next
map: key -> Node
head, tail = sentinel dummies; head.next = tail; tail.prev = head

remove(node):        # unlink from list, O(1)
  node.prev.next = node.next
  node.next.prev = node.prev

add_front(node):     # insert right after head (most recent)
  node.next = head.next; node.prev = head
  head.next.prev = node; head.next = node

get(k):
  if k not in map: return -1
  node = map[k]
  remove(node); add_front(node)   # mark most-recently used
  return node.val

put(k, v):
  if k in map:
    node = map[k]; node.val = v
    remove(node); add_front(node)
  else:
    if len(map) == capacity:
      lru = tail.prev
      remove(lru); del map[lru.key]   # evict least recently used
    node = Node(k, v)
    map[k] = node; add_front(node)
```

**Complexity** — time O(1) average per get and put (hash map lookup + constant linked-list pointer updates); space O(capacity) for the map plus one node per stored entry

Full Python solution: `LeetCodeCheat/lru-cache.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- How would you make it thread-safe under concurrent get/put?
- How does Python's collections.OrderedDict (or functools.lru_cache) implement this?
- How would you extend it to LFU (least frequently used) eviction?
- What changes for a TTL / time-based expiry cache?
- How would you shard this to a distributed cache across many machines?

Sources:

- [LeetCode 146 — LRU Cache Solution & Explanation (NeetCode)](https://neetcode.io/solutions/lru-cache)
- [LeetCode — 146. LRU Cache (problem statement)](https://leetcode.com/problems/lru-cache/)
- [algo.monster — 146. LRU Cache In-Depth Explanation](https://algo.monster/liteproblems/146)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/lru-cache.yaml`.
