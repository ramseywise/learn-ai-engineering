---
title: "LC 215 — Kth Largest Element in an Array"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [heap]
source: https://leetcode.com/problems/kth-largest-element-in-an-array/
---
## Prompt

Given an integer array `nums` and an integer `k`, return the `k`-th largest
element in the array. This is the element at sorted position `k` from the end,
not the `k`-th distinct value (duplicates count). Example:
`nums = [3,2,1,5,6,4]`, `k = 2` -> `5`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

The kth largest element has a fixed final index once the array is sorted, so you don't need to fully sort it.

</details>

<details><summary>Hint 2</summary>

Use quickselect by partitioning around a pivot, then recursing only into the side of the partition containing the target index.

</details>

<details><summary>Hint 3</summary>

Shuffle the array first to avoid worst-case behavior, giving O(n) average time versus O(n log n) for full sorting.

</details>

## Solution

<details><summary>Reference approach</summary>

Quickselect works because the k-th largest element sits at index n-k in sorted order. Partition the array (Hoare partition) around a pivot and recurse only into the side that contains that target index, ignoring the other half. This averages O(n). A random shuffle first guards against adversarial worst-case inputs.

```python
target = n - k
select(lo, hi):
    if lo >= hi: return
    p = partition(a, lo, hi)
    if target <= p: select(lo, p)
    else: select(p+1, hi)
shuffle(a); select(0, n-1); return a[target]
```

**Complexity** — time O(n) average, O(n^2) worst; space O(1)

Full Python solution: [`LeetCodeCheat/kth-largest-element-in-an-array.py`](../../python/leetcode/LeetCodeCheat/kth-largest-element-in-an-array.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Use a size-k min-heap for a streaming O(n log k) alternative.
- How does median-of-medians give worst-case linear time?
- Why does shuffling protect Hoare partition from sorted-input blowup?

Sources:

- [LeetCode - Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/215-kth-largest-element-in-an-array.yaml`.
