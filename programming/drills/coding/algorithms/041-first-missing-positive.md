---
title: "LC 41 — First Missing Positive"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [arrays-hashing]
source: https://leetcode.com/problems/first-missing-positive/
---
## Prompt

Given an unsorted integer array `nums`, return the smallest positive integer
(starting from `1`) that does not appear in it. Values may be negative, zero, or
duplicated. Aim for `O(n)` time and `O(1)` extra space. Example:
`nums = [3,4,-1,1]` -> `2`; `nums = [1,2,0]` -> `3`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

The answer for an array of n elements must always lie between 1 and n+1, so only values in that range matter.

</details>

<details><summary>Hint 2</summary>

Use a boolean array of size n to mark which values from 1 to n are actually present in the input.

</details>

<details><summary>Hint 3</summary>

One pass to mark, one pass to find the first unset slot gives O(n) time and O(n) space. Think about how you could reuse the input array to get O(1) extra space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

The answer is always in the range 1..n+1, so only values in that window matter. Mark which of those are present with a boolean array of size n: for each positive value v <= n, set used[v-1]. Then scan used from the left and return the first index whose slot is unset (i+1). If all are set, the answer is n+1. (This uses O(n) extra space. The classic O(1)-space variant permutes the array in place to put each value v at index v-1, but the boolean-array version is the clearest.)

```python
used = [false] * n
for v in nums:
    if 1 <= v <= n: used[v-1] = true
for i in 0..n-1:
    if not used[i]: return i + 1
return n + 1
```

**Complexity** — time O(n); space O(n)

Full Python solution: `LeetCodeCheat/first-missing-positive.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- How would you do it in O(1) extra space by rearranging the array in place?

Sources:

- [LeetCode — First Missing Positive](https://leetcode.com/problems/first-missing-positive/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/041-first-missing-positive.yaml`.
