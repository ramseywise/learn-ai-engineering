---
title: "LC 479 — Largest Palindrome Product"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [math-strings]
source: https://leetcode.com/problems/largest-palindrome-product/
---
## Prompt

Given an integer `n`, find the largest integer palindrome that can be written as a
product of two `n`-digit numbers, and return it modulo `1337`. Example: `n = 2` ->
`987` (since `99 * 91 = 9009` is the largest such palindrome, and `9009 % 1337 = 987`).

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

You're looking for the largest product of two n-digit numbers that happens to be a palindrome, so the order you search in matters.

</details>

<details><summary>Hint 2</summary>

Iterate candidate factors from the largest n-digit numbers downward, pruning combinations that can't produce the needed trailing digits.

</details>

<details><summary>Hint 3</summary>

Return the first palindrome found, modulo 1337, since a top-down search finds the largest one first.

</details>

## Solution

<details><summary>Reference approach</summary>

Find the largest palindrome that's a product of two n-digit numbers, returned modulo 1337. Search factor pairs from the top of the n-digit range downward. Prune pairs whose last digits can't make the product end in 9, skip factors ending in 5, and return the first product that reads as a palindrome. The bounded ordered search reaches the largest palindrome quickly.

```python
max = 10^n - 1; min = 10^(n-1)
for k from max down to min:
    for i from k up to max:
        if the last digits can't yield a product ending in 9: skip
        cand = i * k
        if is_palindrome(cand): return cand % 1337
```

**Complexity** — time O((10^n)^2) worst case, heavily pruned in practice; space O(number of digits)

Full Python solution: [`LeetCodeCheat/largest-palindrome-product.py`](../../python/leetcode/LeetCodeCheat/largest-palindrome-product.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Build palindromes top-down and test factorability instead of scanning products.
- Why can the largest such product be forced to end in the digit 9?
- Handle the special small-n edge cases.

Sources:

- [LeetCode - Largest Palindrome Product](https://leetcode.com/problems/largest-palindrome-product/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/479-largest-palindrome-product.yaml`.
