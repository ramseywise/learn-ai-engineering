---
title: "LC 8 — String to Integer (atoi)"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [math-strings]
source: https://leetcode.com/problems/string-to-integer-atoi/
---
## Prompt

Implement `atoi`: convert a string `s` to a 32-bit signed integer. Skip leading
spaces, read an optional `+`/`-` sign, then consume consecutive digits, stopping at
the first non-digit character. Ignore any trailing characters. If no digits were
read, return `0`. Clamp the result to the 32-bit signed range `[-2^31, 2^31 - 1]`.
Example: `"   -42abc"` -> `-42`; `"4193 with words"` -> `4193`; `"words 99"` -> `0`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Scan the string as a small state machine: first skip leading spaces, then read an optional sign character.

</details>

<details><summary>Hint 2</summary>

Consume digits while building result = result * 10 + digit, stopping as soon as you hit a non-digit character.

</details>

<details><summary>Hint 3</summary>

Detect 32-bit overflow immediately after each multiply-and-add and clamp to INT_MAX or INT_MIN based on the sign, giving an O(n) single pass.

</details>

## Solution

<details><summary>Reference approach</summary>

Scan the characters as a careful state machine: first skip leading spaces and read an optional +/- sign. Then consume digits, building the result as result * 10 + digit, stopping at the first non-digit. The tricky part is 32-bit overflow: after each multiply-and-add, detect that the accumulation wrapped and clamp to INT_MAX or INT_MIN according to the sign. Anything that isn't a valid prefix yields 0.

```python
skip leading spaces
read optional '+' / '-' -> sign
result = 0
while next char c is a digit:
    d = c - '0'
    result = result * 10 + d
    if overflow detected:
        return sign > 0 ? INT_MAX : INT_MIN
return sign * result
```

**Complexity** — time O(n); space O(1)

Full Python solution: [`LeetCodeCheat/string-to-integer-atoi.py`](../../python/leetcode/LeetCodeCheat/string-to-integer-atoi.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — String to Integer (atoi)](https://leetcode.com/problems/string-to-integer-atoi/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/008-string-to-integer.yaml`.
