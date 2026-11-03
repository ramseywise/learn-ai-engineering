---
title: "LC 137 — Single Number II"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [arrays-hashing]
source: https://leetcode.com/problems/single-number-ii/
---
## Prompt

Given an integer array `nums` where every element appears exactly three times except
for one that appears once, return the single element. Example:
`nums = [2,2,3,2]` -> `3`; `nums = [0,1,0,1,0,1,99]` -> `99`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Every value except one appears exactly three times, so you need a way to detect a count that never reaches three.

</details>

<details><summary>Hint 2</summary>

A hash map counting occurrences, deleting a key as soon as it hits three, leaves only the answer behind.

</details>

<details><summary>Hint 3</summary>

For O(1) extra space instead, sum each bit position across all numbers modulo 3.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Every element appears three times except one. Count occurrences in a hash map, deleting a key as soon as its count reaches three. The single key left gives the answer. The O(1)-space method instead sums each bit position modulo 3 across all numbers.

```python
count = {}
for x in nums:
    count[x] += 1
    if count[x] == 3: delete count[x]
return the only remaining key
```

**Complexity** — time O(n); space O(n)

Full Python solution: `LeetCodeCheat/single-number-ii.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Solve it in O(1) extra space with bit counting modulo 3.
- Generalize to elements appearing k times except one.
- What changes if two numbers appear once (LeetCode 260)?

Sources:

- [LeetCode - Single Number II](https://leetcode.com/problems/single-number-ii/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/137-single-number-ii.yaml`.
