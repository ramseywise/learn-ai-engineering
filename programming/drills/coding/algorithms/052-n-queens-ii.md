---
title: "LC 52 — N-Queens II"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [backtracking]
source: https://leetcode.com/problems/n-queens-ii/
---
## Prompt

Given an integer `n`, return the number of distinct ways to place `n` queens on an
`n x n` chessboard so that no two attack each other (no shared row, column, or
diagonal). Only the count is required, not the boards. Example: `n = 4` -> `2`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

This is the same row-by-row placement problem as N-Queens, but you never need to materialize a board.

</details>

<details><summary>Hint 2</summary>

Backtrack by placing one queen per row in a free column. Mark its column and diagonals as attacked, and recurse on a copy of that attack state.

</details>

<details><summary>Hint 3</summary>

Instead of recording boards, increment a counter whenever a placement reaches row n. The search is still exponential but touches only masks, not full boards.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Identical backtracking to N-Queens, but we only need the count of solutions, not the boards. Place one queen per row in a free column, mark its column and diagonals as attacked, and recurse on a copy of the mask. When row n is reached, increment a counter instead of reconstructing a board.

```python
solve(row, mask, count):
    if row == n:
        count += 1; return
    for c in 0..n-1:
        if mask[row][c] is empty:
            copy = mask with queen at (row,c) and its attacks marked
            solve(row+1, copy, count)
```

**Complexity** — time exponential (bounded by n! placements); space O(n^2) per mask plus recursion

Full Python solution: `LeetCodeCheat/n-queens-ii.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — N-Queens II](https://leetcode.com/problems/n-queens-ii/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/052-n-queens-ii.yaml`.
