---
title: "LC 238 — Product of Array Except Self"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [arrays-hashing]
source: https://leetcode.com/problems/product-of-array-except-self/
---
## Prompt

Given an integer array `nums`, return an array `answer` where `answer[i]` equals
the product of every element of `nums` except `nums[i]`. Solve it without using
division and in `O(n)` time. Example: `nums = [1,2,3,4]` -> `[24,12,8,6]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Each answer is a product of everything to the left times everything to the right, so division can be avoided entirely.

</details>

<details><summary>Hint 2</summary>

Do a left-to-right pass accumulating prefix products and a right-to-left pass accumulating suffix products, multiplying them into the output.

</details>

<details><summary>Hint 3</summary>

Both passes can be folded into the output array, giving O(n) time and O(1) extra space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

For each index the answer is the product of everything to its left times everything to its right. Compute prefix products in a left-to-right pass and suffix products in a right-to-left pass, multiplying them per index - no division needed. The one-pass version fills both directions together, keeping only the output array plus two running scalars.

```python
out = array of 1s
prefix = 1
for i = 1..n-1: prefix *= nums[i-1]; out[i] *= prefix
suffix = 1
for i = n-2..0: suffix *= nums[i+1]; out[i] *= suffix
return out
```

**Complexity** — time O(n); space O(1) extra (output array aside)

Full Python solution: `LeetCodeCheat/product-of-array-except-self.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Why is division disallowed, and how would a single zero break it?
- Handle one or more zeros in the array explicitly.
- Prove the output array alone suffices for O(1) extra space.

Sources:

- [LeetCode - Product of Array Except Self](https://leetcode.com/problems/product-of-array-except-self/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/238-product-of-array-except-self.yaml`.
