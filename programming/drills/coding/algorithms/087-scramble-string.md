---
title: "LC 87 — Scramble String"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [dynamic-programming]
source: https://leetcode.com/problems/scramble-string/
---
## Prompt

A scramble of a string is formed by recursively splitting it into two non-empty
substrings and optionally swapping the two halves at each node. Given two strings
`s1` and `s2` of equal length, return `true` if `s2` is a scramble of `s1`.
Example: `s1 = "great"`, `s2 = "rgeat"` -> `true` (swap the split `gr | eat`).

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

A scramble is built by recursively splitting a string into two children that may or may not swap places.

</details>

<details><summary>Hint 2</summary>

Try every split point of the first string and check both the no-swap and swap alignments against the second string. Prune first with an anagram check.

</details>

<details><summary>Hint 3</summary>

Memoizing on the pair of substrings turns the exponential recursion into a polynomial-time solution.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Solve it with recursion. First, if s1 and s2 aren't anagrams, s2 can't be a scramble of s1. If they're already equal, return true. Otherwise try splitting s1 at every position i (1..n-1). Each split explores the ways of building the scramble tree. s1[:i] is the left child and s1[i:] the right. For each split, s2 could correspond in two ways. Without a swap at this node, s2 splits at i too, so check s1[:i] vs s2[:i] and s1[i:] vs s2[i:]. With a swap, s2's matching pieces are the last i and first n-i characters, so check s1[:i] vs s2[n-i:] and s1[i:] vs s2[:n-i]. If any split works, return true. Otherwise return false. The anagram check at the top prunes most branches.

```python
isScramble(s1, s2):
    if s1 == s2: return true
    if not anagram(s1, s2): return false
    n = len(s1)
    for i in 1..n-1:
        # no swap
        if isScramble(s1[:i], s2[:i]) and isScramble(s1[i:], s2[i:]): return true
        # swap
        if isScramble(s1[:i], s2[n-i:]) and isScramble(s1[i:], s2[:n-i]): return true
    return false
```

**Complexity** — time exponential without memoization (memoize on (s1,s2) substrings to make it polynomial); space O(n) recursion (more with memoization)

Full Python solution: `LeetCodeCheat/scramble-string.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Scramble String](https://leetcode.com/problems/scramble-string/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/087-scramble-string.yaml`.
