---
title: "LC 160 — Intersection of Two Linked Lists"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [linked-list]
source: https://leetcode.com/problems/intersection-of-two-linked-lists/
---
## Prompt

Given the heads of two singly linked lists `headA` and `headB`, return the node where
they first intersect (share the same node by reference, so the two lists merge into
one tail from there). Return `null` if they never intersect. Aim for O(1) extra space.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

If two lists intersect, they share the exact same tail from the intersection node onward.

</details>

<details><summary>Hint 2</summary>

Measure both lengths, then advance the longer list's pointer by the difference so both pointers are equally far from the end.

</details>

<details><summary>Hint 3</summary>

Move both pointers together one step at a time. They meet exactly at the intersection node in O(n+m) time, O(1) space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Two lists that intersect share the same tail from the intersection node onward. Measure both lengths (and confirm they end at the same last node, otherwise there's no intersection). Advance the longer list's pointer by the length difference so both pointers are equidistant from the end. Then move them together until they meet at the intersection node.

```python
len1, len2 = lengths of A and B
if last node of A != last node of B: return null
advance the longer head by |len1 - len2|
move both pointers together until they are equal
return that node
```

**Complexity** — time O(n+m); space O(1)

Full Python solution: `LeetCodeCheat/intersection-of-two-linked-lists.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Solve it without computing lengths using the two-pointer swap.
- Detect intersection when the lists might also contain cycles.
- Why does aligning by the length difference guarantee they meet?

Sources:

- [LeetCode - Intersection of Two Linked Lists](https://leetcode.com/problems/intersection-of-two-linked-lists/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/160-intersection-of-two-linked-lists.yaml`.
