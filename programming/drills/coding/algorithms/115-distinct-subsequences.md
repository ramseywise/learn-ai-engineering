---
title: "LC 115 — Distinct Subsequences"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [dynamic-programming]
source: https://leetcode.com/problems/distinct-subsequences/
---
## Prompt

Given two strings `s` and `t`, return the number of distinct subsequences of `s`
that equal `t`. A subsequence keeps the original order but may drop characters.
Example: `s = "rabbbit"`, `t = "rabbit"` -> `3` (three different ways to pick the
matching characters).

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Think about counting matches between prefixes of the source string and prefixes of the target rather than the whole strings.

</details>

<details><summary>Hint 2</summary>

Build a table where each cell adds the ways that skip the current source character. When characters match, it also adds the ways that use it to complete the target.

</details>

<details><summary>Hint 3</summary>

Filling this 2D table bottom-up gives an O(n*m) time and space solution.

</details>

## Solution

<details><summary>Reference approach</summary>

Count how many distinct subsequences of s equal t. Fill a table `dp[i][j]` holding the number of times `t[:i]` occurs in `s[:j]`. The first row is all ones (an empty target is always matched once) and the first column below it is zero. If the characters differ, `s[j]` can't help, so `dp[i][j]` = `dp[i][j-1]` (same count as without `s[j]`). If they match, `dp[i][j]` = `dp[i][j-1] + dp[i-1][j-1]`: the ways that ignore `s[j]` plus the ways where `s[j]` completes the current target character.

```python
dp[0][*] = 1                 # empty t matched once
dp[i>0][0] = 0               # empty s can't contain non-empty t
for i in 1..len(t):
    for j in 1..len(s):
        if t[i-1] == s[j-1]:
            dp[i][j] = dp[i][j-1] + dp[i-1][j-1]
        else:
            dp[i][j] = dp[i][j-1]
return dp[len(t)][len(s)]
```

**Complexity** — time O(n*m); space O(n*m)

Full Python solution: [`LeetCodeCheat/distinct-subsequences.py`](../../python/leetcode/LeetCodeCheat/distinct-subsequences.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Reduce to O(m) memory with a rolling row over s.
- Explain the match case `dp[i][j-1] + dp[i-1][j-1]` with a small example.
- How would counts overflow, and how do you guard against it?

Sources:

- [LeetCode - Distinct Subsequences](https://leetcode.com/problems/distinct-subsequences/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/115-distinct-subsequences.yaml`.
