---
title: "Primes from 0 to 100"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [math-strings]
source: https://github.com/alexeygrigorev/ai-engineering-gym
---
## Prompt

Print all prime numbers between 0 and 100 (reported warm-up in a GenAI engineer
interview). Explain your approach and its complexity, then generalize to primes up
to n.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

For a single number, only test divisors up to sqrt(m). A larger factor always pairs with a smaller one. Handle 0, 1, and 2 as special cases.

</details>

<details><summary>Hint 2</summary>

For all primes up to n, the Sieve of Eratosthenes beats testing each number: mark multiples as composite.

</details>

<details><summary>Hint 3</summary>

In the sieve you can start striking multiples of p at p*p (smaller multiples were already struck by smaller primes).

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Two standard answers, and interviewers like to hear you compare them. Trial division: for each candidate m, test divisibility only up to sqrt(m). If no divisor is found, m is prime. The sqrt bound works because any factor larger than sqrt(m) pairs with one smaller than sqrt(m), and you only need to test odd divisors after 2. Sieve of Eratosthenes: mark a boolean array [2..n] all prime, then for each still-prime p, strike out its multiples starting at p*p. Whatever stays marked is prime. For a small fixed bound like 100 either is instant, but the sieve is the better answer for "all primes up to n" and shows you know the classic. Mention the edge cases: 0 and 1 aren't prime, 2 is the only even prime.

```python
# Trial division
def is_prime(m):
    if m < 2: return False
    if m == 2: return True
    if m % 2 == 0: return False
    for d in range(3, int(m**0.5) + 1, 2):
        if m % d == 0: return False
    return True
primes = [m for m in range(0, 101) if is_prime(m)]

# Sieve of Eratosthenes (better for all primes up to n)
def sieve(n):
    is_p = [False, False] + [True] * (n - 1)   # indices 0..n
    for p in range(2, int(n**0.5) + 1):
        if is_p[p]:
            for j in range(p*p, n + 1, p):
                is_p[j] = False
    return [i for i, v in enumerate(is_p) if v]
```

**Complexity** — time Trial division O(n * sqrt(n)); sieve O(n log log n); space O(1) for trial division; O(n) for the sieve's boolean array

Full Python solution: `LeetCodeCheat/count-primes.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Why can you stop trial division at sqrt(m)?
- Why does the sieve start crossing out at p*p rather than 2*p?
- How would you reduce the sieve's memory for large n (segmented sieve, odds-only)?
- How does trial division's O(n*sqrt(n)) compare to the sieve as n grows large?

Sources:

- [GeeksforGeeks — Sieve of Eratosthenes](https://www.geeksforgeeks.org/dsa/sieve-of-eratosthenes/)
- [Medium (Khushal Kumar) — My Generative AI Engineer Interview Experience](https://kaysnotes.medium.com/my-generative-ai-engineer-interview-experience-got-hired-6b3f1affc4e9)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-primes-0-100.yaml`.
