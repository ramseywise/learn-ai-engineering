---
title: "LC 42 — Trapping Rain Water"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [two-pointers]
source: https://leetcode.com/problems/trapping-rain-water/
---
## Prompt

Given `n` non-negative integers `height` representing an elevation map where each bar
has width `1`, compute how much rainwater is trapped between the bars after raining.
Example: `height = [0,1,0,2,1,0,1,3,2,1,2,1]` -> `6`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

The water trapped above any bar depends only on the tallest bar to its left and the tallest bar to its right.

</details>

<details><summary>Hint 2</summary>

Sweep inward from both ends toward the position of the global maximum, tracking a running left_max and right_max as you go.

</details>

<details><summary>Hint 3</summary>

This two-pointer sweep computes the total trapped water in a single O(n) time, O(1) space pass.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Water above a bar is bounded by the tallest bar to its left and the tallest to its right. The trapped amount at that bar is min(left_max, right_max) - height. Sweep from both ends toward the global maximum: from the left, track the running left_max and add left_max - height wherever the current bar is lower. Do the same symmetrically from the right with right_max. The two sweeps meet at the tallest bar, which correctly bounds both sides. Every position is counted once in a single O(n) pass with O(1) space.

```python
m = index/height of global max
left_max = h[0]
for left from 0 while h[left] < m:
    if h[left] <= left_max: water += left_max - h[left]
    else:                   left_max = h[left]
right_max = h[last]
for right from last while h[right] < m:
    if h[right] <= right_max: water += right_max - h[right]
    else:                     right_max = h[right]
return water
```

**Complexity** — time O(n); space O(1)

Full Python solution: `LeetCodeCheat/trapping-rain-water.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/042-trapping-rain-water.yaml`.
