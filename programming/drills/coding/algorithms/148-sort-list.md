---
title: "LC 148 — Sort List"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [linked-list]
source: https://leetcode.com/problems/sort-list/
---
## Prompt

Given the `head` of a singly linked list, sort it in ascending order and return the
new head. Aim for O(n log n) time. Example: `[4,2,1,3]` -> `[1,2,3,4]`;
`[-1,5,3,4,0]` -> `[-1,0,3,4,5]`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

A linked list has no random access, so favor a sorting method that only needs sequential traversal.

</details>

<details><summary>Hint 2</summary>

Find the middle with slow/fast pointers, split the list in half, and recursively sort each half.

</details>

<details><summary>Hint 3</summary>

Merge the two sorted parts by splicing nodes in order, giving O(n log n) time overall.

</details>

## Solution

<details><summary>Reference approach</summary>

Merge sort on a linked list, which needs no random access. Find the middle with slow/fast pointers and split it into two parts, then recursively sort each part. Merge the two sorted lists by splicing nodes in order. This gives O(n log n) time with O(log n) recursion depth.

```python
sort(head):
    if head is null or a single node: return head
    mid = split the list in half via slow/fast pointers
    left = sort(first half); right = sort(second half)
    return merge(left, right)
merge(a, b): repeatedly attach the smaller head, then append the leftover tail
```

**Complexity** — time O(n log n); space O(log n)

Full Python solution: [`LeetCodeCheat/sort-list.py`](../../python/leetcode/LeetCodeCheat/sort-list.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Make it bottom-up (iterative) for O(1) extra space.
- Why is merge sort preferred over quicksort for linked lists?
- How does merging two linked lists differ from merging arrays?

Sources:

- [LeetCode - Sort List](https://leetcode.com/problems/sort-list/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/148-sort-list.yaml`.
