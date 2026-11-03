---
title: "LC 82 — Remove Duplicates from Sorted List II"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [linked-list]
source: https://leetcode.com/problems/remove-duplicates-from-sorted-list-ii/
---
## Prompt

Given the head of a sorted linked list, delete every node that has a duplicate value,
leaving only values that appear exactly once, and return the head of the modified list.
Example: `1 -> 2 -> 3 -> 3 -> 4 -> 4 -> 5` -> `1 -> 2 -> 5`;
`1 -> 1 -> 1 -> 2 -> 3` -> `2 -> 3`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Because the list is sorted, any duplicated value forms a contiguous run of nodes.

</details>

<details><summary>Hint 2</summary>

When you spot a repeated value, skip the entire run rather than a single node, keeping only values that appear exactly once.

</details>

<details><summary>Hint 3</summary>

A single recursive or iterative pass handles this in O(n) time.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Because the list is sorted, any duplicated value forms a contiguous run. Here we must drop such runs entirely, leaving only values that appear exactly once. Process recursively: if the head's value repeats into the next node, skip the whole run of that value and recurse on the first node past it. Otherwise the head is unique, so keep it and recurse on the rest, linking it to the cleaned tail.

```python
dedup(head):
    if head is null or head.next is null: return head
    if head.val == head.next.val:
        v = head.val
        skip all nodes equal to v -> node
        return dedup(node)              # drop the whole run
    head.next = dedup(head.next)        # head is unique, keep it
    return head
```

**Complexity** — time O(n); space O(n) recursion (O(1) if written iteratively)

Full Python solution: `LeetCodeCheat/remove-duplicates-from-sorted-list-ii.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Remove Duplicates from Sorted List II](https://leetcode.com/problems/remove-duplicates-from-sorted-list-ii/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/082-remove-duplicates-sorted-list-ii.yaml`.
