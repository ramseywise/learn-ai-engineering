---
title: "LC 57 — Insert Interval"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [greedy-intervals]
source: https://leetcode.com/problems/insert-interval/
---
## Prompt

Given a list of sorted, non-overlapping `intervals` (`[start, end]`) and a `newInterval`,
insert the new interval so the result stays sorted and non-overlapping, merging any
intervals it overlaps. Example: `intervals = [[1,3],[6,9]]`, `newInterval = [2,5]` ->
`[[1,5],[6,9]]`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Because the existing intervals are already sorted and non-overlapping, you can process them in one left-to-right pass relative to the new interval.

</details>

<details><summary>Hint 2</summary>

Copy over intervals ending before the new one starts. Then merge the new interval with every following interval it overlaps by extending its end, and copy the remaining intervals unchanged.

</details>

<details><summary>Hint 3</summary>

This single linear scan inserts and merges the new interval in O(n) time and O(n) space.

</details>

## Solution

<details><summary>Reference approach</summary>

The existing intervals are already sorted and non-overlapping, so process them in one pass around the new interval. Copy over every interval that ends before the new one starts. Then merge the new interval with any it overlaps by extending its end while the next interval's start is within reach. Finally copy the remaining intervals that come entirely after. This inserts and merges in a single linear scan.

```python
result = []
i = 0
while intervals[i].start < new.start:
    result.append(intervals[i]); i++
# place / merge new interval with the last copied one if they overlap
merge new into result (extend ends as needed)
while i < len and result.last.end >= intervals[i].start:
    result.last.end = max(result.last.end, intervals[i].end); i++
append the rest of intervals
return result
```

**Complexity** — time O(n); space O(n)

Full Python solution: [`LeetCodeCheat/insert-interval.py`](../../python/leetcode/LeetCodeCheat/insert-interval.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Insert Interval](https://leetcode.com/problems/insert-interval/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/057-insert-interval.yaml`.
