---
title: "LC 79 — Subsets"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [backtracking]
source: https://leetcode.com/problems/subsets/
---
## Prompt

Given an integer array `nums` of unique elements, return all possible subsets (the power
set). The result must not contain duplicate subsets and may be returned in any order.
Example: `nums = [1,2,3]` -> `[[],[1],[2],[3],[1,2],[1,3],[2,3],[1,2,3]]`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Each subset corresponds to a unique choice of include or exclude for every element.

</details>

<details><summary>Hint 2</summary>

Represent that choice as an n-bit number and enumerate every value from 0 to 2^n - 1.

</details>

<details><summary>Hint 3</summary>

For each mask, build the subset from the set bits, giving an O(n * 2^n) solution.

</details>

## Solution

<details><summary>Reference approach</summary>

There are 2^n subsets of n elements, and each corresponds to an n-bit mask where bit j says whether nums[j] is included. So enumerate all masks 0 .. 2^n - 1 and, for each, collect the elements whose bit is set. (An equivalent formulation is recursive include/exclude backtracking. Another starts with the empty set and, for each new element, appends copies of all existing subsets extended by it.)

```python
result = []
for mask in 0 .. 2^n - 1:
    subset = [nums[j] for j in 0..n-1 if mask has bit j set]
    result.append(subset)
return result
```

**Complexity** — time `O(n * 2^n)`; space `O(n * 2^n)` for the output

Full Python solution: [`LeetCodeCheat/subsets.py`](../../python/leetcode/LeetCodeCheat/subsets.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Subsets](https://leetcode.com/problems/subsets/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/079-subsets.yaml`.
