---
title: "LC 56 — Merge Intervals"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [greedy-intervals]
source: https://leetcode.com/problems/merge-intervals/
---
## Prompt

Given an array of intervals where `intervals[i] = [start, end]`, merge all overlapping
intervals and return the resulting non-overlapping intervals covering the same ranges.
Example: `[[1,3],[2,6],[8,10],[15,18]]` -> `[[1,6],[8,10],[15,18]]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

If the intervals are sorted by their start, any interval that could merge with the current one is guaranteed to appear right after it.

</details>

<details><summary>Hint 2</summary>

Sort by start, then scan the intervals keeping a running result list. Extend the last result interval's end when the next interval overlaps it, otherwise start a new interval.

</details>

<details><summary>Hint 3</summary>

This single pass after sorting gives O(n log n) time overall (dominated by the sort) and O(n) space for the result.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Sort the intervals by start. Scan them in order, keeping a result list seeded with the first interval. For each next interval, if its start is within the current last result interval (start <= last.end) the two overlap, so extend last.end to the larger of the two ends. Otherwise there's a gap, so append it as a new interval. Sorting guarantees any interval that could merge with the current one comes right after it.

```python
sort intervals by start
result = [intervals[0]]
for iv in intervals[1:]:
    if iv.start <= result.last.end:
        result.last.end = max(result.last.end, iv.end)
    else:
        result.append(iv)
return result
```

**Complexity** — time O(n log n); space O(n)

Full Python solution: `LeetCodeCheat/merge-intervals.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Merge Intervals](https://leetcode.com/problems/merge-intervals/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/056-merge-intervals.yaml`.
