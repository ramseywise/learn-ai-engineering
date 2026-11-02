---
title: "LC 69 — Sqrt(x)"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [binary-search]
source: https://leetcode.com/problems/sqrtx/
---
## Prompt

Given a non-negative integer `x`, return the integer square root of `x`, i.e. `sqrt(x)`
rounded down to the nearest integer. Do not use any built-in exponent/sqrt function.
Example: `x = 8` -> `2` (since `2.828...` truncates to `2`); `x = 4` -> `2`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

The function g -> g*g is monotonic over non-negative g, which means you can bracket the true root instead of testing every candidate.

</details>

<details><summary>Hint 2</summary>

Binary search over the range from 1 to x, narrowing the bounds based on whether the midpoint squared is smaller or larger than x.

</details>

<details><summary>Hint 3</summary>

Stop once the guess is close enough and take the floor of it, giving O(log x) time and O(1) space.

</details>

## Solution

<details><summary>Reference approach</summary>

Binary search for the square root. The root of x lies in [1, x]. Repeatedly take the midpoint g and compare g*g against x, moving the low bound up when g*g is too small and the high bound down when it's too big, until the guess is close enough. Since the problem wants the integer part, round the converged guess down (with a small epsilon to decide whether to round the boundary case). Bracketing on a monotonic function is the core idea. (0 and 1 are returned directly.)

```python
if x <= 1: return x
lo = 1; hi = x
loop:
    g = (lo + hi) / 2
    if |g*g - x| small enough: break
    if g*g < x: lo = g else hi = g
return floor(g)     # integer part
```

**Complexity** — time O(log x); space O(1)

Full Python solution: [`LeetCodeCheat/sqrtx.py`](../../python/leetcode/LeetCodeCheat/sqrtx.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Sqrt(x)](https://leetcode.com/problems/sqrtx/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/069-sqrtx.yaml`.
