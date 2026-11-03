---
title: "LC 17 — Letter Combinations of a Phone Number"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [backtracking]
source: https://leetcode.com/problems/letter-combinations-of-a-phone-number/
---
## Prompt

Given a string `digits` containing digits `2`-`9`, return all letter combinations
the number could spell, using the classic phone keypad mapping (`2` -> `abc`,
`3` -> `def`, ..., `9` -> `wxyz`). The order of the combinations doesn't matter.
An empty input returns an empty list. Example: `digits = "23"` ->
`["ad","ae","af","bd","be","bf","cd","ce","cf"]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Map each digit to its phone-keypad letters and think of building each combination one digit at a time.

</details>

<details><summary>Hint 2</summary>

Backtrack by recursing on the remaining digits. Try each letter of the current digit, appending it to the prefix built so far before recursing further.

</details>

<details><summary>Hint 3</summary>

Emitting the prefix once no digits remain explores all O(4^n) combinations with only O(n) recursion depth.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Backtrack over the digits, mapping each digit to its phone-keypad letters. Recurse one digit at a time, passing along the prefix built so far. For the current digit try each of its letters, appending it to the prefix and recursing on the remaining digits. When there are no digits left, the prefix is a complete combination, so emit it. Empty input yields no combinations.

```python
pad = {'2':"abc", '3':"def", ..., '9':"wxyz"}
generate(prefix, digits):
    if digits empty:
        output prefix; return
    for ch in pad[digits[0]]:
        generate(prefix + ch, digits[1:])
```

**Complexity** — time O(4^n) combinations for n digits; space O(n) recursion depth

Full Python solution: `LeetCodeCheat/letter-combinations-of-a-phone-number.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Letter Combinations of a Phone Number](https://leetcode.com/problems/letter-combinations-of-a-phone-number/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/017-letter-combinations.yaml`.
