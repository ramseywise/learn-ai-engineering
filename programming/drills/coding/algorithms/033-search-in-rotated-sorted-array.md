---
title: "LC 33 — Search in Rotated Sorted Array"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [binary-search]
source: https://leetcode.com/problems/search-in-rotated-sorted-array/
---
## Prompt

An ascending sorted array of distinct integers has been rotated at some unknown
pivot (e.g. `[0,1,2,4,5,6,7]` might become `[4,5,6,7,0,1,2]`). Given the rotated
array `nums` and a `target`, return the index of `target`, or `-1` if it is absent.
Aim for `O(log n)` time. Example: `nums = [4,5,6,7,0,1,2]`, `target = 0` -> `4`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Even after rotation, at least one half of any subarray you look at is still sorted.

</details>

<details><summary>Hint 2</summary>

At each step figure out which half (left or right of the midpoint) is sorted. Then check whether the target falls inside that sorted half to decide which side to search.

</details>

<details><summary>Hint 3</summary>

A modified binary search that discards half the range each step gives O(log n) time.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

The array was sorted and then rotated by an unknown amount. There's one "pivot" where the order breaks, and no duplicates. Do a modified binary search on [l, r]. Take the middle m and look at A[l], A[m], A[r]. If the target equals any of these, return that index. If start <= target < mid, the left half is sorted and the target must be there, so recurse left. If mid < target <= end, the right half is sorted and holds the target, so recurse right. If neither ordinary case fires, the order breaks in this window, so find which side the pivot is on. If mid > right the pivot is on the right, so go right. If mid < left the pivot is on the left, so go left. (Duplicates need the extra handling in problem 81.)

```python
search(A, t, l, r):
    if l > r: return -1
    m = l + (r - l) / 2
    if A[m] == t: return m
    if A[l] <= t and t < A[m]: return search(A, t, l, m-1)   # left sorted
    if A[m] < t and t <= A[r]: return search(A, t, m+1, r)   # right sorted
    if A[m] > A[r]:            return search(A, t, m+1, r)   # pivot on right
    if A[m] < A[l]:            return search(A, t, l, m-1)   # pivot on left
    return -1
```

**Complexity** — time O(log n); space O(log n) recursion

Full Python solution: `LeetCodeCheat/search-in-rotated-sorted-array.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/033-search-in-rotated-sorted-array.yaml`.
