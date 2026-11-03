---
title: "LC 23 — Merge k Sorted Lists"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [linked-list]
source: https://leetcode.com/problems/merge-k-sorted-lists/
---
## Prompt

Given an array of `k` linked lists, each already sorted in ascending order, merge
them into a single sorted linked list and return its head. Some lists may be empty.
Example: `lists = [[1,4,5],[1,3,4],[2,6]]` -> `[1,1,2,3,4,4,5,6]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

A min-heap lets you always know which of the k list heads currently holds the smallest value.

</details>

<details><summary>Hint 2</summary>

Seed the heap with each list's head node. Repeatedly pop the smallest, append it to the output, and push its successor back into the heap if one exists.

</details>

<details><summary>Hint 3</summary>

Since the heap never holds more than k nodes at a time, this processes all N nodes in O(N log k) time.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Use a min-heap keyed on node value, seeded with the head of every non-empty list. Repeatedly pop the smallest node, append it to the output tail, and if that node has a successor push the successor back into the heap. Because the heap always holds at most k nodes, each of the N total nodes is inserted and extracted once at O(log k) cost. (The naive alternative scans all k heads on every step for O(Nk).)

```python
heap = min-heap by node.val
for list in lists:
    if list: heap.push(list)
dummy = new Node; tail = dummy
while heap not empty:
    node = heap.pop()
    if node.next: heap.push(node.next)
    tail.next = node; tail = node
return dummy.next
```

**Complexity** — time O(N log k) for N total nodes across k lists; space O(k)

Full Python solution: `LeetCodeCheat/merge-k-sorted-lists.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/023-merge-k-sorted-lists.yaml`.
