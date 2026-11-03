---
title: "LC 4 — Median of Two Sorted Arrays"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [binary-search]
source: https://leetcode.com/problems/median-of-two-sorted-arrays/
---
## Prompt

Given two sorted integer arrays `nums1` and `nums2` of sizes `m` and `n`, return
the median of the combined set of all `m + n` elements. Aim for `O(log(m+n))` time.
Example: `nums1 = [1,3]`, `nums2 = [2]` -> `2.0`; `nums1 = [1,2]`, `nums2 = [3,4]`
-> `2.5` (average of the two middle values).

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Treat the median as the k-th smallest element across both arrays (or the average of two such elements). Reframe the task as finding the k-th smallest.

</details>

<details><summary>Hint 2</summary>

Compare the m-th elements of each array, where m = k/2, to see which array's prefix can never contain the answer and discard it, shrinking k.

</details>

<details><summary>Hint 3</summary>

Discarding roughly half of the remaining elements at each step gives O(log(n+m)) instead of merging in O(n+m).

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Treat the median as the k-th smallest element of the combined arrays (or the average of the two middle ones for even total length). Reduce the problem to "find the k-th smallest across two sorted arrays" and solve that with binary search instead of merging. Compare the m-th elements of each array where m = k/2. Whichever side is smaller can't contain the k-th element in its first m entries, so discard that prefix and shrink k accordingly. Recurse until k reaches 1 or one array is empty. This gets to O(log(n+m)) rather than the O(n+m) merge.

```python
kth(a, b, k):
    if a is empty: return b[k-1]
    if b is empty: return a[k-1]
    if k == 1:     return min(a[0], b[0])
    m  = k / 2
    ia = min(len(a), m); ib = min(len(b), m)
    if a[ia-1] < b[ib-1]:
        return kth(a[ia:], b, k - ia)   # drop a's prefix
    else:
        return kth(a, b[ib:], k - ib)   # drop b's prefix

findMedian(a, b):
    total = len(a) + len(b)
    if total is odd:  return kth(a, b, total/2 + 1)
    else:             return (kth(a, b, total/2) + kth(a, b, total/2 + 1)) / 2
```

**Complexity** — time O(log(n + m)); space O(log(n + m)) recursion

Full Python solution: `LeetCodeCheat/median-of-two-sorted-arrays.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Median of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/004-median-of-two-sorted-arrays.yaml`.
