---
title: "LC 6 — Zigzag Conversion"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [math-strings]
source: https://leetcode.com/problems/zigzag-conversion/
---
## Prompt

A string `s` is written out in a zigzag pattern across a given number of rows
`numRows` (going down the rows, then diagonally up, repeatedly), then read off row
by row to produce a new string. Return that row-by-row reading. Example:
`s = "PAYPALISHIRING"`, `numRows = 3` -> `"PAHNAPLSIIGYIR"`. When `numRows == 1`
the string is returned unchanged.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Instead of building a full 2D grid, keep one output string buffer per row of the zigzag.

</details>

<details><summary>Hint 2</summary>

Simulate the traversal by moving a row pointer down to the last row and then bouncing back up. Append each character to whichever row buffer it currently belongs to.

</details>

<details><summary>Hint 3</summary>

Concatenating the row buffers at the end gives O(n) time and space. Handle numRows == 1 as a special case that returns the string unchanged.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Simulate the zigzag path instead of building a 2D grid, keeping one string buffer per row. Iterate over the characters, appending down through the rows to the last one, then bounce back up to row 1 and repeat. Each character gets appended to the buffer of its current row. At the end, concatenate the row buffers top to bottom. The single-row case is returned unchanged.

```python
if numRows == 1: return s
rows = array of numRows empty strings
row = 0
pos = 0
while pos < len(s):
    while row < numRows and pos < len(s):     # go down
        rows[row] += s[pos]; row++; pos++
    row -= 2                                   # bounce
    while row > 0 and pos < len(s):            # go up diagonally
        rows[row] += s[pos]; row--; pos++
return concat(rows)
```

**Complexity** — time O(n); space O(n)

Full Python solution: `LeetCodeCheat/zigzag-conversion.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Zigzag Conversion](https://leetcode.com/problems/zigzag-conversion/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/006-zigzag-conversion.yaml`.
