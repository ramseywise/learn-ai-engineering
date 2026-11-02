---
title: "LC 81 — Search in Rotated Sorted Array II"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [binary-search]
source: https://leetcode.com/problems/search-in-rotated-sorted-array-ii/
---
## Prompt

Given an integer array `nums` that was sorted in non-decreasing order (and may contain
duplicates) then rotated at some unknown pivot, plus a `target`, return `true` if
`target` is present and `false` otherwise. Try to keep the search close to `O(log n)`,
though duplicates can force `O(n)` in the worst case. Example:
`nums = [2,5,6,0,0,1,2]`, `target = 0` -> `true`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

The array is still two sorted parts around a rotation point, like the version without duplicates, but duplicates can hide which part is actually sorted.

</details>

<details><summary>Hint 2</summary>

When the boundary values are equal, shrink the search window from one side until they differ, then run the usual rotated binary search.

</details>

<details><summary>Hint 3</summary>

This handles duplicates correctly but degrades to O(n) time in the worst case.

</details>

## Solution

<details><summary>Reference approach</summary>

Same as problem 33 (Search in Rotated Sorted Array), but the array may contain duplicates, which needs one adjustment. The trouble is when A[start] == A[end]: you can't tell which half is sorted. Fix it by shrinking the window. Move end left until A[start] != A[end], then run the ordinary rotated binary search unchanged. The duplicate-skipping is what pushes the worst case to O(n).

```python
search(A, t, start, end):
    while A[start] == A[end] and end >= start: end--
    if start > end: return false
    m = start + (end - start) / 2
    if t in {A[start], A[m], A[end]}: return true
    if A[start] <= t and t < A[m]: return search(A, t, start, m-1)   # left sorted
    if A[m] < t and t <= A[end]:   return search(A, t, m+1, end)     # right sorted
    if A[m] > A[end]:              return search(A, t, m+1, end)     # pivot right
    if A[m] < A[start]:            return search(A, t, start, m-1)   # pivot left
    return false
```

**Complexity** — time O(log n) average, O(n) worst case with many duplicates; space O(log n) recursion

Full Python solution: [`LeetCodeCheat/search-in-rotated-sorted-array-ii.py`](../../python/leetcode/LeetCodeCheat/search-in-rotated-sorted-array-ii.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Search in Rotated Sorted Array II](https://leetcode.com/problems/search-in-rotated-sorted-array-ii/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/081-search-in-rotated-sorted-array-ii.yaml`.
