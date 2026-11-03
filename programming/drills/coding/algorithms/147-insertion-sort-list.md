---
title: "LC 147 — Insertion Sort List"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [linked-list]
source: https://leetcode.com/problems/insertion-sort-list/
---
## Prompt

Given the `head` of a singly linked list, sort it in ascending order and return the
new head. Example: `[4,2,1,3]` -> `[1,2,3,4]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Build the sorted result incrementally, keeping in mind a linked list can't be indexed like an array.

</details>

<details><summary>Hint 2</summary>

Repeatedly scan the unsorted remainder for the current minimum, unlink it, and attach it to the front of the growing sorted portion.

</details>

<details><summary>Hint 3</summary>

This selection-sort-over-a-list approach runs in O(n^2) time and O(1) extra space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Sort a linked list by repeatedly selecting the minimum. Scan the unsorted remainder to find the minimum node, unlink it, and place it at the front of the growing sorted result. That's a selection sort over the list. Classic insertion sort instead walks the sorted prefix to find each node's insertion point.

```python
sorted = empty
while list not empty:
    find node with the minimum value (track its predecessor)
    unlink it from the list
    attach it into the sorted portion in order
return sorted
```

**Complexity** — time O(n^2); space O(1)

Full Python solution: `LeetCodeCheat/insertion-sort-list.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Implement true insertion sort with a dummy head and per-node insertion.
- When would you prefer merge sort on a list (LeetCode 148)?
- Is the selection variant stable - does it preserve equal-key order?

Sources:

- [LeetCode - Insertion Sort List](https://leetcode.com/problems/insertion-sort-list/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/147-insertion-sort-list.yaml`.
