---
title: "LC 16 — 3Sum Closest"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [two-pointers]
source: https://leetcode.com/problems/3sum-closest/
---
## Prompt

Given an integer array `nums` and an integer `target`, pick three elements whose sum
is as close to `target` as possible, and return that sum. Exactly one such closest
sum exists. Example: `nums = [-1,2,1,-4]`, `target = 1` -> `2` (from `-1 + 2 + 1`).

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

This has the same structure as 3Sum: sort the array, then fix one element and sweep the remaining suffix with two pointers.

</details>

<details><summary>Hint 2</summary>

At each step compare the current triplet sum's distance from the target against the best distance found so far. Move whichever pointer moves the sum toward the target.

</details>

<details><summary>Hint 3</summary>

This gives O(n^2) time overall. An exact match (distance zero) can return immediately without finishing the sweep.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

This has the same structure as 3Sum. Sort the array, fix each element a, and sweep the rest with two pointers. For every triplet track the sum whose absolute distance to the target is smallest so far. If the current sum exceeds the target move the right pointer left, otherwise move the left pointer right. An exact hit (distance 0) returns immediately.

```python
sort(nums)
best = infinity distance
for i in 0..n-3:
    j = i+1; k = n-1
    while j < k:
        sum = nums[i] + nums[j] + nums[k]
        if abs(sum - target) < best_distance:
            best = sum
        if sum == target: return sum
        if sum > target:  k--
        else:             j++
return best
```

**Complexity** — time O(n^2); space O(1) (excluding sort)

Full Python solution: `LeetCodeCheat/3sum-closest.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — 3Sum Closest](https://leetcode.com/problems/3sum-closest/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/016-3sum-closest.yaml`.
