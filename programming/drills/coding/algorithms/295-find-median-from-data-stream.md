---
title: "LC 295 — Find Median from Data Stream"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [heap]
source: https://leetcode.com/problems/find-median-from-data-stream/
---
## Prompt

Design a `MedianFinder` that supports two operations on a growing stream of
numbers: `addNum(x)` inserts `x`, and `findMedian()` returns the median of all
values seen so far. The median is the middle value when the count is odd, or the
average of the two middle values when it is even. Example: after adding `1` and
`2`, `findMedian()` -> `1.5`; after adding `3`, `findMedian()` -> `2`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

The median only depends on the boundary between the lower and upper parts of the data.

</details>

<details><summary>Hint 2</summary>

Keep a max-heap for the smaller half and a min-heap for the larger half. Rebalance after each insert so the sizes differ by at most one.

</details>

<details><summary>Hint 3</summary>

This gives O(log n) inserts and O(1) median lookup from the two heap tops.

</details>

## Solution

<details><summary>Reference approach</summary>

Keep the stream split into two parts: a max-heap holding the smaller half and a min-heap holding the larger half, kept balanced in size. On each insert, push into one heap and rebalance so the two sizes differ by at most one. The median is then the top of the larger heap (odd count) or the average of the two tops (even count). Both heaps expose the boundary elements around the median in O(1), with O(log n) inserts.

```python
add(x):
    push x into right_min heap
    move right_min.top into left_max heap
    if left_max is larger than right_min: move left_max.top back to right_min
median():
    if the heaps are equal size: return (left_max.top + right_min.top) / 2
    else: return the top of the larger heap
```

**Complexity** — time O(log n) per add, O(1) per median; space O(n)

Full Python solution: [`LeetCodeCheat/find-median-from-data-stream.py`](../../python/leetcode/LeetCodeCheat/find-median-from-data-stream.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- How would a fixed integer range let you use a simpler structure?
- Support removing an element to get a sliding-window median (LeetCode 480).
- Why keep the two heaps within one element of each other?

Sources:

- [LeetCode - Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/295-find-median-from-data-stream.yaml`.
