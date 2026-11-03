---
title: "LC 206 — Reverse Linked List"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [linked-list]
source: https://leetcode.com/problems/reverse-linked-list/
---
## Prompt

Given the `head` of a singly linked list, reverse the list and return the new
head. Example: `1 -> 2 -> 3 -> 4 -> 5` becomes `5 -> 4 -> 3 -> 2 -> 1`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Reversing means flipping each node's next pointer to point backward instead of forward.

</details>

<details><summary>Hint 2</summary>

Traverse the list with a prev pointer, saving each node's next before overwriting node.next to point at prev.

</details>

<details><summary>Hint 3</summary>

One pass with O(n) time and O(1) space. prev becomes the new head once the cursor runs off the end.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Reverse the pointers in a single pass, traversing the list with a prev pointer. For each node, save its next, point the node back to prev, then advance prev and the cursor. When the cursor runs off the end, prev is the new head.

```python
prev = null; node = head
while node:
    next = node.next
    node.next = prev
    prev = node
    node = next
return prev
```

**Complexity** — time O(n); space O(1)

Full Python solution: `LeetCodeCheat/reverse-linked-list.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Write the recursive version and state its stack cost.
- Reverse only nodes m..n in place (LeetCode 92).
- Reverse the list in groups of k (LeetCode 25).

Sources:

- [LeetCode - Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/206-reverse-linked-list.yaml`.
