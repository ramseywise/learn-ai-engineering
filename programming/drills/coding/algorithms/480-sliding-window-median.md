---
title: "LC 480 — Sliding Window Median"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [sliding-window]
source: https://leetcode.com/problems/sliding-window-median/
---
## Prompt

Given an integer array `nums` and a window size `k`, a window of `k` consecutive
elements slides from left to right one position at a time. Return an array of the
median of each window (the middle value when `k` is odd, the average of the two
middle values when `k` is even). Example: `nums = [1,3,-1,-3,5,3,6,7]`, `k = 3` ->
`[1,-1,-1,3,5,6]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

This extends the streaming two-heap median idea, but now an element must also be removed when it leaves the window.

</details>

<details><summary>Hint 2</summary>

Use two balanced multisets, not plain heaps, split around the median so the outgoing value can be removed from whichever side holds it, then rebalance.

</details>

<details><summary>Hint 3</summary>

Each slide costs O(log k), giving O(n log k) overall.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Extend the two-heap median idea to a moving window by using two balanced multisets split into a max-side and a min-side. This lets elements be removed as they leave the window. Each slide removes the outgoing value from whichever side holds it and inserts the incoming value. It then rebalances the two sides and reads the median off the boundary element(s).

```python
left (max side) and right (min side) as ordered multisets, kept balanced
init with the first k elements; balance the two sizes
for each slide:
    remove nums[i-k] from its side; add nums[i]; rebalance
    median = right.min (odd k) or avg(left.max, right.min) (even k)
```

**Complexity** — time O(n log k); space O(k)

</details>

## Notes

Follow-ups an interviewer may push on:

- Why do plain binary heaps fail here where removable multisets work?
- Use lazy deletion with two heaps and a removed-count map.
- Guard against integer overflow when averaging two large window values.

Sources:

- [LeetCode - Sliding Window Median](https://leetcode.com/problems/sliding-window-median/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/480-sliding-window-median.yaml`.
