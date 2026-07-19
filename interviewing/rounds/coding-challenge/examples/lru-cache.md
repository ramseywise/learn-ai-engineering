# LRU Cache — Live Coding Walkthrough

**Prompt**: "Implement an LRU (Least Recently Used) cache with `get(key)` and `put(key, value)` operations. Both should run in O(1) time."

**Time budget**: 20–25 minutes

---

## Step 1: Clarify (before touching the keyboard)

[NARRATE: "Before I start, a few quick questions. What should `get` return on a cache miss — None, or raise a KeyError? And is the capacity guaranteed to be a positive integer, or do I need to handle zero or negative?"]

*Interviewer*: Return -1 on miss. Capacity is always >= 1.

[NARRATE: "Got it. And I'll assume single-threaded — no thread safety needed unless you tell me otherwise."]

---

## Step 2: State the approach

[NARRATE: "The O(1) constraint is the key signal here. A plain dict gives me O(1) lookup, but I'd need O(n) to find the least-recently-used entry for eviction. Python's `collections.OrderedDict` gives me O(1) for both — it maintains insertion order and has a `move_to_end` method that lets me promote recently used keys. I'll use that rather than building a doubly-linked list from scratch."]

[NARRATE: "The invariant I'll maintain: the front of the OrderedDict is the least recently used; the back is the most recently used. On `get`, I move the key to the end. On `put`, I add to the end and evict from the front if over capacity."]

---

## Step 3: Write the interface first

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.cache: OrderedDict[int, int] = OrderedDict()

    def get(self, key: int) -> int:
        ...

    def put(self, key: int, value: int) -> None:
        ...
```

[NARRATE: "I'm typing the class skeleton first so we both know what we're building before I fill in the logic."]

---

## Step 4: Implement `get`

```python
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)  # mark as recently used
        return self.cache[key]
```

[NARRATE: "`move_to_end` with no argument moves to the end — the 'most recently used' position. O(1) because it's a doubly-linked list under the hood. The not-found path returns -1 as specified."]

---

## Step 5: Implement `put`

```python
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)  # evict LRU (front)
            self.cache[key] = value
```

[NARRATE: "Two cases: if the key already exists, I update the value and promote it. If it's new, I check capacity first — `popitem(last=False)` removes from the front, which is the least recently used entry. Then I insert the new key at the back."]

---

## Step 6: Trace a known example

[NARRATE: "Let me trace through the LeetCode example before I declare this done."]

```
LRUCache(2)
put(1, 1)   → cache: {1:1}
put(2, 2)   → cache: {1:1, 2:2}
get(1)      → 1; promotes 1 → cache: {2:2, 1:1}
put(3, 3)   → capacity hit; evict LRU = 2 → cache: {1:1, 3:3}
get(2)      → -1 (evicted) ✓
put(4, 4)   → capacity hit; evict LRU = 1 → cache: {3:3, 4:4}
get(1)      → -1 ✓
get(3)      → 3 ✓
get(4)      → 4 ✓
```

[NARRATE: "Traces correctly."]

---

## Step 7: Check edge cases

[NARRATE: "Edge cases I want to call out: capacity=1 — only ever holds one item; every `put` of a new key evicts. Already-covered by the logic. What about `put` with the same key twice? The `key in self.cache` branch handles that — updates value, promotes position. And `get` on an empty cache — falls through to `return -1`. I think we're good."]

---

## Step 8: Quick test

```python
def test_lru_cache():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1
    c.put(3, 3)          # evicts key 2
    assert c.get(2) == -1
    c.put(4, 4)          # evicts key 1
    assert c.get(1) == -1
    assert c.get(3) == 3
    assert c.get(4) == 4
    print("all assertions passed")

test_lru_cache()
```

---

## Complexity summary

[NARRATE: "Time complexity: O(1) for both `get` and `put` — hash map lookup plus doubly-linked list pointer updates, all constant. Space: O(capacity) — we never hold more than `capacity` entries."]

---

## What signals this answer

- Named `OrderedDict` before writing a line of code, and explained why
- Stated the invariant (front = LRU, back = MRU) before implementing
- Handled the "update existing key" case in `put` (many candidates miss this)
- Traced a concrete example before declaring done
- Complexity stated unprompted
- Wrote a verifying test at the end
