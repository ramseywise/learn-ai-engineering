---
title: "LC 51 — N-Queens"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [backtracking]
source: https://leetcode.com/problems/n-queens/
---
## Prompt

Given an integer `n`, place `n` queens on an `n x n` chessboard so that no two attack
each other (no shared row, column, or diagonal). Return all distinct solutions; each
board is a list of `n` strings using `'Q'` for a queen and `'.'` for an empty cell.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Since exactly one queen goes in each row, place queens row by row while tracking which columns and diagonals are already under attack.

</details>

<details><summary>Hint 2</summary>

Backtrack at each row by trying every free column and marking the cells that queen attacks (its column and both diagonals). Recurse into the next row before undoing the choice.

</details>

<details><summary>Hint 3</summary>

Reaching row n with a valid placement means a full board is found. This exponential backtracking is bounded by the number of ways to place n non-attacking queens.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Backtrack row by row, since each row holds exactly one queen. Place a queen in some free column of the current row, mark all cells it attacks (its column and both diagonals) as taken, and recurse to the next row on a copy of that attack mask. When every free column in a row has been tried, backtrack. Reaching row n means all queens are placed, so reconstruct the board from the mask and record it as a solution.

```python
solve(row, mask, solutions):
    if row == n:
        solutions.add(board from mask); return
    for c in 0..n-1:
        if mask[row][c] is empty:
            copy = mask with queen at (row,c) and its attacks marked
            solve(row+1, copy, solutions)
```

**Complexity** — time exponential (bounded by n! placements); space O(n^2) per board mask plus recursion

Full Python solution: `LeetCodeCheat/n-queens.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — N-Queens](https://leetcode.com/problems/n-queens/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/051-n-queens.yaml`.
