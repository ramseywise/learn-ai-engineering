---
title: "LC 84 — Largest Rectangle in Histogram"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [stack]
source: https://leetcode.com/problems/largest-rectangle-in-histogram/
---
## Prompt

Given an array `heights` where each element is the height of a bar of width `1` in a
histogram, return the area of the largest rectangle that fits entirely within the
histogram. Example: `heights = [2,1,5,6,2,3]` -> `10` (bars of height `5` and `6` span
width `2`).

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

For each bar, the widest rectangle of its height is limited by the nearest shorter bar on either side.

</details>

<details><summary>Hint 2</summary>

A stack of indices kept in non-decreasing height order lets you discover the nearest shorter bar to the left and right of each bar as you scan.

</details>

<details><summary>Hint 3</summary>

Popping the stack whenever a shorter bar arrives computes every bar's rectangle in a single O(n) pass.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Solve it with a monotonic stack. The idea mirrors the naive approach, where for each bar you consider how far a rectangle of its height extends left through bars that are at least as tall. The stack finds those boundaries efficiently. Scan the bars keeping a stack of indices with non-decreasing heights: if the current bar is taller than (or equal to) the top, push it. Otherwise pop the top bar j. Its height is hist[j], the tallest currently on the stack and taller than the current bar. Its rectangle's width runs from the bar after the new stack top up to i-1 (width = i - 1 - stack.top, or i if the stack is empty). Compute that area and keep the max. Drain the stack the same way at the end. (A divide-and-conquer variant recurses on the min-height index, found fast with a segment tree.)

```python
stack = []; i = 0; best = 0
while i < n:
    if stack empty or hist[i] >= hist[stack.top]:
        stack.push(i); i++
    else:
        j = stack.pop(); h = hist[j]
        w = (stack empty) ? i : i - 1 - stack.top
        best = max(best, h * w)
# drain remaining bars with the same width rule
return best
```

**Complexity** — time O(n); space O(n)

Full Python solution: `LeetCodeCheat/largest-rectangle-in-histogram.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/084-largest-rectangle-in-histogram.yaml`.
