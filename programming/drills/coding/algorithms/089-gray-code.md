---
title: "LC 89 — Gray Code"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [math-strings]
source: https://leetcode.com/problems/gray-code/
---
## Prompt

Given an integer `n`, return any valid `n`-bit Gray code sequence: a list of the
`2^n` integers from `0` to `2^n - 1` where every consecutive pair (and the first
and last) differ in exactly one bit. The sequence must start with `0`.
Example: `n = 2` -> `[0, 1, 3, 2]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Reflecting an existing list of codes and adding a new high bit preserves the property that consecutive codes differ by one bit.

</details>

<details><summary>Hint 2</summary>

Build the sequence bit by bit, appending the current list in reverse order with the new bit set on each copy.

</details>

<details><summary>Hint 3</summary>

This doubles the list every round, producing all 2^n codes in O(2^n) time.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Build the sequence iteratively by reflection, starting with [0]. For each bit i from 0 to n-1, take the current list. Walking it in reverse order, set bit i on each existing code and append the result. Reflecting the list and prefixing the new high bit guarantees consecutive codes differ by exactly one bit. The list doubles each round until it holds all 2^n codes.

```python
result = [0]
for i in 0..n-1:
    for k from len(result)-1 down to 0:
        result.append(result[k] | (1 << i))
return result
```

**Complexity** — time O(2^n); space O(2^n)

Full Python solution: `LeetCodeCheat/gray-code.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Prove that each adjacent pair differs by exactly one bit.
- Produce the i-th Gray code directly with the formula g = i XOR (i >> 1).
- Convert a Gray code back to its binary index.

Sources:

- [LeetCode - Gray Code](https://leetcode.com/problems/gray-code/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/089-gray-code.yaml`.
