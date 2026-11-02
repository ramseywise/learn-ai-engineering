---
title: "LC 83 — Remove Duplicates from Sorted List"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [linked-list]
source: https://leetcode.com/problems/remove-duplicates-from-sorted-list/
---
## Prompt

Given the head of a sorted linked list, remove duplicate nodes so each value appears
only once (keeping the first occurrence), and return the head of the modified list.
Example: `1 -> 1 -> 2 -> 3 -> 3` -> `1 -> 2 -> 3`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

In a sorted list, equal values sit right next to each other, so duplicates can be spotted locally.

</details>

<details><summary>Hint 2</summary>

Keep a pointer at the last kept node and unlink any following node whose value matches it.

</details>

<details><summary>Hint 3</summary>

One linear, in-place pass gives O(n) time and O(1) space.

</details>

## Solution

<details><summary>Reference approach</summary>

The list is sorted, so equal values are adjacent. Keep the first occurrence of each value and drop the rest. Walk with a prev pointer at the last kept node. If the current node equals prev's value, unlink it (prev.next = node.next). Otherwise advance prev to the current node. One linear pass, in place.

```python
prev = head
node = head.next
while node:
    if node.val == prev.val:
        prev.next = node.next        # skip duplicate
    else:
        prev = node
    node = node.next
return head
```

**Complexity** — time O(n); space O(1)

Full Python solution: [`LeetCodeCheat/remove-duplicates-from-sorted-list.py`](../../python/leetcode/LeetCodeCheat/remove-duplicates-from-sorted-list.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Remove Duplicates from Sorted List](https://leetcode.com/problems/remove-duplicates-from-sorted-list/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/083-remove-duplicates-sorted-list.yaml`.
