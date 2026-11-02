---
title: "LC 48 — Rotate Image"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [math-strings]
source: https://leetcode.com/problems/rotate-image/
---
## Prompt

Given an `n x n` 2D matrix representing an image, rotate it by 90 degrees clockwise.
You must modify the matrix in place, without allocating another 2D array. Example:
`[[1,2,3],[4,5,6],[7,8,9]]` -> `[[7,4,1],[8,5,2],[9,6,3]]`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

A 90-degree clockwise rotation of a matrix can be decomposed into two simpler, well-known operations.

</details>

<details><summary>Hint 2</summary>

First transpose the matrix in place by swapping across the diagonal, then reverse each row.

</details>

<details><summary>Hint 3</summary>

This composition of transpose and row-reversal rotates the matrix in O(n^2) time and O(1) extra space.

</details>

## Solution

<details><summary>Reference approach</summary>

Rotating an n x n matrix 90 degrees clockwise in place is transpose-then-reverse. First transpose the matrix (swap `m[i][j]` with `m[j][i]`, touching only one triangle so each pair swaps once), then reverse each row. The composition of those two O(n^2) passes is exactly the clockwise rotation, and it needs no extra matrix.

```python
# transpose
for i in 1..n-1:
    for j in 0..i-1:
        swap(m[i][j], m[j][i])
# reverse each row
for each row:
    reverse(row)
```

**Complexity** — time O(n^2); space O(1)

Full Python solution: [`LeetCodeCheat/rotate-image.py`](../../python/leetcode/LeetCodeCheat/rotate-image.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Rotate Image](https://leetcode.com/problems/rotate-image/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/048-rotate-image.yaml`.
