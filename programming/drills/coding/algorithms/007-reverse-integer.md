---
title: "LC 7 — Reverse Integer"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [math-strings]
source: https://leetcode.com/problems/reverse-integer/
---
## Prompt

Given a signed 32-bit integer `x`, return `x` with its digits reversed, keeping the
sign. If the reversed value falls outside the 32-bit signed range
`[-2^31, 2^31 - 1]`, return `0`. Example: `x = 123` -> `321`; `x = -123` -> `-321`;
`x = 120` -> `21`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Work on the absolute value and peel off digits one at a time using mod and integer division by 10.

</details>

<details><summary>Hint 2</summary>

Rebuild the reversed number by repeatedly multiplying the accumulator by 10 and adding the next digit, then restore the original sign at the end.

</details>

<details><summary>Hint 3</summary>

Guard against 32-bit overflow by checking after each step that dividing the accumulator back by the same power of ten still returns the digit you added. Return 0 if not.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Pull digits off the number one at a time with mod/divide by 10. Rebuild the reversed value by multiplying the accumulator by 10 and adding each digit. Handle the sign separately by working on the absolute value. The one subtlety is 32-bit overflow: after each step check that dividing the accumulator back by the current power of ten still yields the digit you added. If it doesn't, the value overflowed, so return 0.

```python
sign = sign(x); x = abs(x)
digits = []
while x != 0: digits.push(x % 10); x /= 10
result = 0; pow = 1
for d in digits (most significant first):
    result += pow * d
    if result / pow != d: return 0     # overflow
    pow *= 10
return sign * result
```

**Complexity** — time O(log10(x)) — number of digits; space O(log10(x))

Full Python solution: `LeetCodeCheat/reverse-integer.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Reverse Integer](https://leetcode.com/problems/reverse-integer/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/007-reverse-integer.yaml`.
