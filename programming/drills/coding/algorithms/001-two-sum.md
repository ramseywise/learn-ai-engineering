---
title: "LC 1 — Two Sum"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [arrays-hashing]
source: https://leetcode.com/problems/two-sum/
---
## Prompt

Given an integer array `nums` and an integer `target`, return the indices of the
two numbers that add up to `target`. Exactly one valid answer exists and you can't
reuse the same element. Example: `nums = [2,7,11,15]`, `target = 9` -> `[0,1]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

A hash map lets you check for a needed value in O(1) as you scan.

</details>

<details><summary>Hint 2</summary>

For each element a, look for its complement target - a among values seen so far.

</details>

<details><summary>Hint 3</summary>

One linear pass storing value->index gets you O(n) time, O(n) space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Scan the array once, keeping a hash map from value seen so far to its index. For each element a, the complement we need is b = target - a. If b is already in the map, we've found the pair and return the two indices. Otherwise store a with its index and continue. This trades O(n) extra space for a single linear pass instead of the O(n^2) brute-force double loop.

```python
index = {}                      # value -> position
for i, a in enumerate(nums):
    b = target - a
    if b in index:
        return [index[b], i]
    index[a] = i
```

**Complexity** — time O(n); space O(n)

Full Python solution: `LeetCodeCheat/two-sum.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Two Sum](https://leetcode.com/problems/two-sum/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/001-two-sum.yaml`.
