---
title: "LC 85 — Maximal Rectangle"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [stack]
source: https://leetcode.com/problems/maximal-rectangle/
---
## Prompt

Given a `rows x cols` binary matrix filled with `'0'` and `'1'` characters, find the
largest rectangle containing only `'1'`s and return its area. Example:
`[["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]]`
-> `6`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Treat each row as the baseline of a histogram formed by the run of consecutive 1s stacked above it.

</details>

<details><summary>Hint 2</summary>

For each column, track the running height plus how far left and right that height still holds, updating these bounds row by row.

</details>

<details><summary>Hint 3</summary>

Combining height times width at every cell across all rows yields an O(rows * cols) solution.

</details>

## Solution

<details><summary>Reference approach</summary>

The clean solution builds histograms row by row and uses DP with three helper arrays. For each cell, `heights[i][j]` counts the consecutive 1s stacked above (and including) cell (i,j). `left[i][j]` is the leftmost column the all-1s bar at (i,j) can extend to, and `right[i][j]` is the rightmost such column. heights updates trivially from the row above. For left, sweep the row left to right maintaining left_start (reset to j+1 on a 0), and on a 1 set left = max(left-from-row-above, left_start). right is symmetric, sweeping right to left with right_end. Compute each cell's area as heights * (right - left + 1), and take the max over all cells. Alternatively, run the histogram solution from problem 84 on the height array of each row, or grow rectangles with DFS.

```python
for each row:
    for each col:                    # heights
        height[col] = matrix[r][c]=='1' ? height[col]+1 : 0
    left_start = 0                    # left bounds, sweep left->right
    for col 0..m-1:
        if '1': left[col] = max(left[col], left_start)
        else:   left[col] = 0; left_start = col+1
    right_end = m-1                   # right bounds, sweep right->left
    for col m-1..0:
        if '1': right[col] = min(right[col], right_end)
        else:   right[col] = m-1; right_end = col-1
    for each col with '1':
        area = height[col] * (right[col] - left[col] + 1)
        best = max(best, area)
return best
```

**Complexity** — time O(rows * cols); space O(cols)

Full Python solution: [`LeetCodeCheat/maximal-rectangle.py`](../../python/leetcode/LeetCodeCheat/maximal-rectangle.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Maximal Rectangle](https://leetcode.com/problems/maximal-rectangle/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/085-maximal-rectangle.yaml`.
