---
title: "LC 204 — Count Primes"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [math-strings]
source: https://leetcode.com/problems/count-primes/
---
## Prompt

Given an integer `n`, return the number of prime numbers that are strictly less
than `n`. A prime is an integer greater than 1 with no positive divisors other
than 1 and itself. Example: `n = 10` -> `4` (the primes below 10 are 2, 3, 5, 7).

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Instead of testing each number for primality individually, mark composite numbers in bulk.

</details>

<details><summary>Hint 2</summary>

Use the Sieve of Eratosthenes: walk upward, and whenever a number is still marked prime, cross out all of its multiples as composite.

</details>

<details><summary>Hint 3</summary>

Striking multiples rather than checking each number individually gives O(n log log n) time.

</details>

## Solution

<details><summary>Reference approach</summary>

Count primes below n with the Sieve of Eratosthenes, marking all numbers prime initially. Walking the odd numbers upward, count each one that's still marked prime and strike out all of its multiples as composite. Striking multiples is far cheaper than testing each number individually for primality.

```python
is_prime[2..n-1] = true
count = 1                       # account for 2
for i = 3, 5, 7, ... < n:
    if not is_prime[i]: continue
    count += 1
    for j = 2i, 3i, ... < n: is_prime[j] = false
return count
```

**Complexity** — time O(n log log n); space O(n)

Full Python solution: [`LeetCodeCheat/count-primes.py`](../../python/leetcode/LeetCodeCheat/count-primes.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Why can you start striking multiples from i*i rather than 2*i?
- Reduce memory with a segmented sieve.
- Compare against trial-division primality testing per number.

Sources:

- [LeetCode - Count Primes](https://leetcode.com/problems/count-primes/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/204-count-primes.yaml`.
