---
title: "LC 239 — Sliding Window Maximum"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [sliding-window]
source: https://leetcode.com/problems/sliding-window-maximum/
---
## Prompt

Given an integer array `nums` and a window size `k`, a window of `k` consecutive
elements slides from left to right one position at a time. Return an array of the
maximum value within each window position. Example: `nums = [1,3,-1,-3,5,3,6,7]`,
`k = 3` -> `[3,3,5,5,6,7]`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

You need the max of every k-sized window without rescanning the whole window on each shift.

</details>

<details><summary>Hint 2</summary>

Maintain a structure over the current window that supports fast insert, remove, and max query as the window slides.

</details>

<details><summary>Hint 3</summary>

A monotonic decreasing deque of indices achieves this in O(n) total, beating an O(n log k) ordered-set approach.

</details>

## Solution

<details><summary>Reference approach</summary>

Report the maximum of each size-k window. This solution keeps the window in an ordered multiset (a balanced tree of value -> count). Sliding one step removes the outgoing element and inserts the incoming one. The largest key gives the current maximum, so each step is O(log k). The optimal O(n) method keeps a monotonic decreasing deque of indices.

```python
window = ordered multiset
insert the first k elements; record the largest key
for i = k..n-1:
    remove nums[i-k]; insert nums[i]
    record the largest key as this window's maximum
```

**Complexity** — time O(n log k); space O(k)

Full Python solution: [`LeetCodeCheat/sliding-window-maximum.py`](../../python/leetcode/LeetCodeCheat/sliding-window-maximum.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Achieve O(n) with a monotonic decreasing deque of indices.
- Also maintain the sliding-window minimum simultaneously.
- How does the deque discard elements that can never be the max?

Sources:

- [LeetCode - Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/239-sliding-window-maximum.yaml`.
