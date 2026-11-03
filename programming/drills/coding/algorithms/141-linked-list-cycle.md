---
title: "LC 141 — Linked List Cycle"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [linked-list]
source: https://leetcode.com/problems/linked-list-cycle/
---
## Prompt

Given the `head` of a linked list, return `true` if the list contains a cycle (some
node's `next` points back to an earlier node so traversal never ends), otherwise
`false`. Aim for O(1) extra space.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Use two pointers that move through the list at different speeds.

</details>

<details><summary>Hint 2</summary>

Advance a slow pointer one step and a fast pointer two steps each iteration. A cycle forces them to eventually collide.

</details>

<details><summary>Hint 3</summary>

This runs in O(n) time and O(1) space with no extra data structure needed.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Floyd's tortoise-and-hare advances a slow pointer one step and a fast pointer two steps at a time. If a cycle exists the fast pointer laps around and meets the slow one, otherwise fast reaches the end (null). It uses constant extra space.

```python
slow = head; fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    if slow == fast: return true
return false
```

**Complexity** — time O(n); space O(1)

Full Python solution: `LeetCodeCheat/linked-list-cycle.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Return the node where the cycle begins (LeetCode 142).
- Compute the length of the cycle.
- Why do the two pointers provably meet inside the loop?

Sources:

- [LeetCode - Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/141-linked-list-cycle.yaml`.
