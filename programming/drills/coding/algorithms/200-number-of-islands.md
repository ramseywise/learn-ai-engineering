---
title: "LC 200 — Number of Islands"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [graphs]
source: https://leetcode.com/problems/number-of-islands/
---
## Prompt

Given an `m x n` grid of `'1'` (land) and `'0'` (water) characters, return the number
of islands. An island is a group of land cells connected horizontally or vertically,
and the grid's edges are surrounded by water. Example: a grid whose only land forms
one connected blob -> `1`; three separate blobs -> `3`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Think of each island as a connected component of land cells in the grid.

</details>

<details><summary>Hint 2</summary>

Scan every cell, and when you find an unvisited land cell, flood-fill outward over its four neighbors marking all connected land visited.

</details>

<details><summary>Hint 3</summary>

Increment the island count once per flood-fill. Each cell is visited only once, giving O(rows * cols) time.

</details>

## Solution

<details><summary>Reference approach</summary>

Count the connected components of '1' (land) cells in the grid. Scan every cell, and flood-fill from each unvisited land cell (DFS or BFS over its four-directional neighbors), marking all reachable land as visited. Then increment the island count. Each cell is visited once.

```python
count = 0
for each cell (i, j):
    if grid[i][j] == '1' and not visited:
        flood_fill(i, j)          # DFS/BFS marking connected land visited
        count += 1
return count
```

**Complexity** — time `O(rows * cols)`; space `O(rows * cols)`

Full Python solution: [`LeetCodeCheat/number-of-islands.py`](../../python/leetcode/LeetCodeCheat/number-of-islands.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Use union-find (disjoint set) instead of flood fill.
- Count islands as the grid is updated online (LeetCode 305).
- How do you avoid recursion-depth overflow on large grids?

Sources:

- [LeetCode - Number of Islands](https://leetcode.com/problems/number-of-islands/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/200-number-of-islands.yaml`.
