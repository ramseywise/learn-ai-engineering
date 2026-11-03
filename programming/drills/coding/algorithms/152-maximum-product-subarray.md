---
title: "LC 152 — Maximum Product Subarray"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [dynamic-programming]
source: https://leetcode.com/problems/maximum-product-subarray/
---
## Prompt

Given an integer array `nums`, find the contiguous non-empty subarray with the
largest product and return that product. The array may contain negative numbers and
zeros. Example: `nums = [2,3,-2,4]` -> `6` (from `[2,3]`);
`nums = [-2,0,-1]` -> `0`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Negative numbers mean the maximum product ending at a position might actually come from the smallest product at the previous position.

</details>

<details><summary>Hint 2</summary>

Track both a running maximum and a running minimum product ending at each index, updating both with the current element.

</details>

<details><summary>Hint 3</summary>

Combine the current element with the previous max and min to get the next max and min in O(n) time, O(1) space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

A DP that tracks both the running maximum and running minimum product ending at each index. Because multiplying by a negative flips largest and smallest, the current minimum can become the maximum. At each step: cur_max = max(A[i], min_prev*A[i], max_prev*A[i]) and cur_min = min of the same three. Return the largest cur_max seen over all indices.

```python
max_prev = min_prev = answer = nums[0]
for x in nums[1:]:
    candidates = [x, x*max_prev, x*min_prev]
    cur_max = max(candidates); cur_min = min(candidates)
    answer = max(answer, cur_max)
    max_prev, min_prev = cur_max, cur_min
return answer
```

**Complexity** — time O(n); space O(1)

Full Python solution: `LeetCodeCheat/maximum-product-subarray.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Why must you track the running minimum, not just the maximum?
- How do zeros in the array reset the running products?
- Contrast this with maximum subarray sum (LeetCode 53).

Sources:

- [LeetCode - Maximum Product Subarray](https://leetcode.com/problems/maximum-product-subarray/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/152-maximum-product-subarray.yaml`.
