---
title: "LC 138 — Copy List with Random Pointer"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [linked-list]
source: https://leetcode.com/problems/copy-list-with-random-pointer/
---
## Prompt

Given a linked list where each node has a `next` pointer and a `random` pointer that
may point to any node in the list or be `null`, return a deep copy. Each node in the
copy must be a brand-new node with the same value, and its `next`/`random` must point
to nodes within the copied list (never the original).

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

The random pointer can point to any node in the list. You need a fast way to look up the clone of a given original node.

</details>

<details><summary>Hint 2</summary>

Build a hash map from each original node to its newly created clone in a first pass over the list.

</details>

<details><summary>Hint 3</summary>

A second pass wires each clone's next and random by looking them up in the map, giving O(n) time and space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Deep-copy a list whose nodes have an extra random pointer. Keep a hash map from each original node to its clone. A first pass creates every clone and records the mapping. A second pass wires each clone's next and random by looking up the clone of the original's next and random. The map resolves random pointers that may point anywhere in the list.

```python
map = {}
for node in list: map[node] = new Node(node.val)
for node in list:
    map[node].next   = map[node.next]
    map[node].random = map[node.random]
return map[head]
```

**Complexity** — time O(n); space O(n)

Full Python solution: `LeetCodeCheat/copy-list-with-random-pointer.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Do it with O(1) extra space by interleaving cloned nodes between originals.
- How would a recursive clone-and-memoize version look?
- Handle random pointers that are null or self-referential.

Sources:

- [LeetCode - Copy List with Random Pointer](https://leetcode.com/problems/copy-list-with-random-pointer/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/138-copy-list-with-random-pointer.yaml`.
