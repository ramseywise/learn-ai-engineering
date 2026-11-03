---
title: "Excel column name"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [math-strings]
source: https://leetcode.com/problems/excel-sheet-column-title/
---
## Prompt

Given a positive integer, return its Excel column name (1 -> "A", 26 -> "Z",
27 -> "AA", 702 -> "ZZ", 703 -> "AAA"). Reported in a Microsoft Applied AI/ML round.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Think base-26, but with no zero digit: A is 1, not 0. That's why plain n % 26 fails at 26, 52, 702, ...

</details>

<details><summary>Hint 2</summary>

Fix it by decrementing n by 1 at the start of each loop iteration before taking n % 26, then divide n by 26.

</details>

<details><summary>Hint 3</summary>

You produce the least-significant letter first, so build the string in reverse (or prepend).

</details>

## Solution

<details><summary>Solution: reference approach</summary>

This is base-26 conversion, but bijective: letters A-Z map to 1-26, so there's no digit zero. The whole problem comes down to that off-by-one. In ordinary base-26 you'd take n % 26. Here you must subtract 1 first at each step so that a multiple of 26 (like 26 -> "Z") maps to the last letter rather than rolling over to a zero. Loop: decrement n by 1, take remainder = n % 26 to pick the letter chr(ord('A') + remainder), then n //= 26. Prepend letters because you generate the least-significant one first. The (n-1) adjustment is what makes 26 give "Z" and 27 give "AA" instead of the naive "A0"/"BA".

```python
def to_column(n):
    out = []
    while n > 0:
        n -= 1                         # shift to 0-based for the bijective system
        out.append(chr(ord('A') + n % 26))
        n //= 26
    return "".join(reversed(out))
```

**Complexity** — time O(log_26 n) — one iteration per output letter; space O(log_26 n) for the result string

Full Python solution: `LeetCodeCheat/excel-sheet-column-title.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Why is the (n-1) adjustment needed, and what breaks without it (test n = 26, 52, 702)?
- Write the inverse: convert a column name like 'AAA' back to its number.
- How does this bijective base-26 differ from a standard positional base-26 with a zero?
- How would you handle large column numbers that overflow a fixed-width integer?

Sources:

- [LeetCode — 168. Excel Sheet Column Title](https://leetcode.com/problems/excel-sheet-column-title/)
- [algo.monster — 168. Excel Sheet Column Title In-Depth Explanation](https://algo.monster/liteproblems/168)
- [Reddit — Microsoft SWE Applied AI/ML Summer 2026 (r/csMajors)](https://www.reddit.com/r/csMajors/comments/1nqfzhq/microsoft_swe_applied_aiml_summer_2026_redmond)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-excel-column-name.yaml`.
