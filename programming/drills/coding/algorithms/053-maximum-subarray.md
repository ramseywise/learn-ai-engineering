---
title: "LC 53 — Maximum Subarray"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [dynamic-programming]
source: https://leetcode.com/problems/maximum-subarray/
---
## Prompt

Given an integer array `nums`, find the contiguous subarray (at least one element) with
the largest sum and return that sum. Example: `nums = [-2,1,-3,4,-1,2,1,-5,4]` -> `6`
(the subarray `[4,-1,2,1]`).

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Think about the best subarray sum ending exactly at each index, and how that value relates to the one ending at the previous index.

</details>

<details><summary>Hint 2</summary>

If the best sum ending at the previous index is negative, it can only drag down the current element. So it's better to restart the running sum at the current element, otherwise keep extending it.

</details>

<details><summary>Hint 3</summary>

This is Kadane's algorithm: track a running current sum and a global best in a single O(n) time, O(1) space pass.

</details>

## Solution

<details><summary>Reference approach</summary>

Apply Kadane's algorithm: keep sum[i], the maximum sum of a subarray ending at i (not necessarily starting at 0). To extend: if sum[i] + arr[i+1] > arr[i+1] then sum[i+1] = sum[i] + arr[i+1], otherwise sum[i+1] = arr[i+1]. In other words, if the running sum has gone negative it can only hurt, so reset to the new element. Otherwise keep accumulating. Report the maximum over all sum[i].

```python
current = nums[0]
best = nums[0]
for i in 1..n-1:
    current = max(nums[i], current + nums[i])
    best = max(best, current)
return best
```

**Complexity** — time O(n); space O(1)

Full Python solution: [`LeetCodeCheat/maximum-subarray.py`](../../python/leetcode/LeetCodeCheat/maximum-subarray.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Maximum Subarray](https://leetcode.com/problems/maximum-subarray/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/053-maximum-subarray.yaml`.
