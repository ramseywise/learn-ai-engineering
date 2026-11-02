---
title: "LC 37 — Sudoku Solver"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [backtracking]
source: https://leetcode.com/problems/sudoku-solver/
---
## Prompt

Given a `9x9` Sudoku board with some cells filled with digits `1`-`9` and the rest
marked `.` (empty), fill in every empty cell so the finished board is valid: each
row, each column, and each of the nine `3x3` sub-boxes contains the digits `1`-`9`
exactly once. A unique solution is guaranteed; modify the board in place.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

For every empty cell, precompute the set of candidate digits allowed by its row, column, and box. Also list the other empty cells sharing a unit with it.

</details>

<details><summary>Hint 2</summary>

Backtrack by always filling the empty cell with the fewest remaining candidates first. Propagate each placement by removing it from peers' candidate sets, and prune if any peer hits zero candidates.

</details>

<details><summary>Hint 3</summary>

This constraint-propagation plus most-constrained-cell backtracking is exponential worst case but fast in practice. Undo placements and candidate removals on failure.

</details>

## Solution

<details><summary>Reference approach</summary>

Backtracking with constraint propagation and a most-constrained-cell heuristic. For each empty cell, precompute its candidate digits (those not already used in its row, column, or box) and the list of "peer" empty cells that share a unit with it. Then solve recursively: always pick the empty cell with the fewest remaining candidates (fail fast). Try each candidate by placing it, removing it from all peers' candidate sets, and recursing. If a peer would be left with zero candidates, prune that branch immediately. On failure, restore the digit and the peers' candidates and try the next. When no empty cells remain, the board is solved.

```python
build candidate sets and peer lists for all empty cells
solve():
    c = empty cell with fewest candidates
    if none: return true          # solved
    for d in c.candidates:
        if placing d leaves some peer with 0 candidates: continue
        place d; remove d from peers' candidates
        if solve(): return true
        undo: restore d and peers' candidates
    return false
```

**Complexity** — time exponential worst case (constraint pruning makes it fast in practice); space O(1) for the fixed 9x9 board plus recursion

Full Python solution: [`LeetCodeCheat/sudoku-solver.py`](../../python/leetcode/LeetCodeCheat/sudoku-solver.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Sudoku Solver](https://leetcode.com/problems/sudoku-solver/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/037-sudoku-solver.yaml`.
