---
title: "LC 5 — Longest Palindromic Substring"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [dynamic-programming]
source: https://leetcode.com/problems/longest-palindromic-substring/
---
## Prompt

Given a string `s`, return the longest contiguous substring of `s` that reads the
same forwards and backwards. If several have the same maximum length, any one is
acceptable. Example: `s = "babad"` -> `"bab"` (or `"aba"`); `s = "cbbd"` -> `"bb"`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Think in terms of a 2D table where entry (i, j) records whether the substring from i to j is a palindrome.

</details>

<details><summary>Hint 2</summary>

A substring is a palindrome exactly when its two ends match and the substring strictly inside them is also a palindrome. This recurrence can be filled bottom-up by increasing length.

</details>

<details><summary>Hint 3</summary>

Filling the whole table and tracking the longest span that comes out true costs O(n^2) time and space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Fill a boolean DP table `palindromes[i][j]` marking whether `s[i..j]` is a palindrome. `s[i..j]` is a palindrome when `s[i]` == `s[j]` and the inside `s[i+1..j-1]` is also a palindrome. So `palindromes[i][j]` = true if `s[i]` == `s[j]` and `palindromes[i+1][j-1]` is true (with length 1 and 2 as base cases). Fill the table and keep track of the longest span that comes out true.

```python
n = len(s)
palindromes = n x n table of false
best = s[0:1]
for i in 0..n-1:
    palindromes[i][i] = true
    for j from i-1 down to 0:
        length = i - j + 1
        ok = (s[i] == s[j])
        if length > 2:
            ok = ok and palindromes[i-1][j+1]
        palindromes[i][j] = ok
        if ok and length > len(best):
            best = s[j..i]
return best
```

**Complexity** — time O(n^2); space O(n^2)

Full Python solution: `LeetCodeCheat/longest-palindromic-substring.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Longest Palindromic Substring](https://leetcode.com/problems/longest-palindromic-substring/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/005-longest-palindromic-substring.yaml`.
