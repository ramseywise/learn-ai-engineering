---
title: "LC 234 — Palindrome Linked List"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [linked-list]
source: https://leetcode.com/problems/palindrome-linked-list/
---
## Prompt

Given the `head` of a singly linked list, return `true` if the sequence of values
reads the same forward and backward, `false` otherwise. Example:
`1 -> 2 -> 2 -> 1` -> `true`; `1 -> 2` -> `false`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

A palindrome check just means comparing the list to its own reverse.

</details>

<details><summary>Hint 2</summary>

Copy the list in reverse, or find the midpoint and reverse the second half, then walk both parts in lockstep comparing values.

</details>

<details><summary>Hint 3</summary>

The midpoint-reverse approach reaches O(n) time with O(1) extra space.

</details>

## Solution

<details><summary>Reference approach</summary>

Build a reversed copy of the list, then walk the original and the reversed copy in lockstep comparing values. If every value matches, the list is a palindrome. The O(1)-space variant instead finds the middle, reverses the second half in place, and compares the two parts.

```python
reversed = a new list with the nodes copied in reverse order
walk original and reversed together:
    if any pair of values differs: return false
return true
```

**Complexity** — time O(n); space O(n)

Full Python solution: [`LeetCodeCheat/palindrome-linked-list.py`](../../python/leetcode/LeetCodeCheat/palindrome-linked-list.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Do it in O(1) space by reversing the second half in place.
- Restore the original list after an in-place reversal.
- Use fast/slow pointers to locate the midpoint.

Sources:

- [LeetCode - Palindrome Linked List](https://leetcode.com/problems/palindrome-linked-list/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/234-palindrome-linked-list.yaml`.
