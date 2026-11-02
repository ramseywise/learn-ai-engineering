---
title: "LC 19 — Remove Nth Node From End of List"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [linked-list]
source: https://leetcode.com/problems/remove-nth-node-from-end-of-list/
---
## Prompt

Given the head of a singly linked list, remove the `n`-th node counting from the end
of the list and return the head of the modified list (`n` is valid, i.e. at least 1
and at most the list length). Example: `head = [1,2,3,4,5]`, `n = 2` ->
`[1,2,3,5]`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

First find the list's total length in one pass so you know exactly which position from the front needs to be removed.

</details>

<details><summary>Hint 2</summary>

The node to delete sits at position length - n. Walk to the node just before it and splice it out by pointing its next past the target.

</details>

<details><summary>Hint 3</summary>

Two passes over the list gives O(L) time and O(1) space (a single-pass two-pointer variant spaced n apart also works).

</details>

## Solution

<details><summary>Reference approach</summary>

Two passes over the singly linked list. First walk to the end to learn its length L, so the node to delete from the front sits at position L - n. If that equals the head (L == n), return head.next. Otherwise walk to the node right before the target (L - n - 1 steps) and splice it out by pointing its next past the target. A one-pass variant uses two pointers spaced n apart, but the length approach is simplest.

```python
L = length(head)
if L == n: return head.next
node = head
advance node by (L - n - 1) steps
node.next = node.next.next
return head
```

**Complexity** — time O(L); space O(1)

Full Python solution: [`LeetCodeCheat/remove-nth-node-from-end-of-list.py`](../../python/leetcode/LeetCodeCheat/remove-nth-node-from-end-of-list.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Remove Nth Node From End of List](https://leetcode.com/problems/remove-nth-node-from-end-of-list/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/019-remove-nth-node.yaml`.
