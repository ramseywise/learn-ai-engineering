---
title: "LC 36 — Valid Sudoku"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [arrays-hashing]
source: https://leetcode.com/problems/valid-sudoku/
---
## Prompt

Given a partially filled `9x9` Sudoku board (cells hold digits `1`-`9` or `.` for
empty), determine whether the current filled cells are valid: no digit repeats within
any row, any column, or any of the nine `3x3` sub-boxes. Only the filled cells are
checked; the board need not be solvable. Return `true` if valid, `false` otherwise.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Validity only requires checking three independent kinds of groups: rows, columns, and 3x3 boxes.

</details>

<details><summary>Hint 2</summary>

For each group, use a small seen-array or set of size 9 and fail as soon as a digit repeats, skipping empty cells.

</details>

<details><summary>Hint 3</summary>

Checking all rows, columns, and boxes this way takes only O(1) time and space on the fixed 9x9 board.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Independently check that no digit repeats within any row, any column, or any 3x3 box. For each of the nine rows scan its cells with a seen-array of size 9 and fail on a repeat. Do the same for each column, then for each of the nine boxes scan its 3x3 cells with a fresh seen-array. Empty cells ('.') are skipped. If none of the checks finds a duplicate, the board is valid.

```python
for each row:      used = [false]*9; for each cell d: if used[d] return false; used[d]=true
for each col:      used = [false]*9; for each cell d: if used[d] return false; used[d]=true
for each 3x3 box:  used = [false]*9; for each cell d: if used[d] return false; used[d]=true
return true
```

**Complexity** — time O(1) — fixed 9x9 board (O(n^2) for an n x n board); space O(1)

Full Python solution: `LeetCodeCheat/valid-sudoku.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Valid Sudoku](https://leetcode.com/problems/valid-sudoku/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/036-valid-sudoku.yaml`.
