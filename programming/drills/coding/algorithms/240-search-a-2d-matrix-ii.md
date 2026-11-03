---
title: "LC 240 — Search a 2D Matrix II"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [binary-search]
source: https://leetcode.com/problems/search-a-2d-matrix-ii/
---
## Prompt

Given an `m x n` integer `matrix` in which every row is sorted ascending left to
right and every column is sorted ascending top to bottom, and a `target` value,
return `true` if `target` appears in the matrix, `false` otherwise. Example:
searching for `5` in such a matrix -> `true`; searching for `20` -> `false`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Rows and columns are each sorted, so a full scan of every cell is wasteful.

</details>

<details><summary>Hint 2</summary>

Narrow down to candidate rows whose value range could contain the target, then search within a row.

</details>

<details><summary>Hint 3</summary>

Starting from the top-right corner and stepping left or down based on the comparison reaches O(m+n) time.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Each row and each column is sorted ascending. This solution skips leading rows whose last element is below the target and trailing rows whose first element is above it. It then binary-searches each remaining candidate row. The elegant O(m+n) alternative starts at the top-right corner and moves left on a too-big value or down on a too-small one.

```python
trim: advance the top row while its last value < target
      retreat the bottom row while its first value > target
for each row in [top .. bottom]:
    if binary_search(row, target): return true
return false
```

**Complexity** — time O(m log n) (top-right staircase alternative is O(m+n)); space O(1)

Full Python solution: `LeetCodeCheat/search-a-2d-matrix-ii.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Implement the O(m+n) top-right staircase walk.
- Why does the staircase walk never need to backtrack?
- Extend it to count how many cells equal the target.

Sources:

- [LeetCode - Search a 2D Matrix II](https://leetcode.com/problems/search-a-2d-matrix-ii/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/240-search-a-2d-matrix-ii.yaml`.
