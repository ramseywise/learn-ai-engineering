---
title: "LC 97 — Interleaving String"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [dynamic-programming]
source: https://leetcode.com/problems/interleaving-string/
---
## Prompt

Given strings `s1`, `s2`, and `s3`, return `true` if `s3` can be formed by
interleaving the characters of `s1` and `s2` while preserving the left-to-right
order within each. This requires `len(s1) + len(s2) == len(s3)`.
Example: `s1 = "aabcc"`, `s2 = "dbbca"`, `s3 = "aadbbcbcac"` -> `true`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Track how many characters have been consumed from each of the two source strings as you match against the target.

</details>

<details><summary>Hint 2</summary>

At each pair of consumption counts, the next target character can only come from one of the two strings. Build a table of reachable states.

</details>

<details><summary>Hint 3</summary>

A 2D table over prefixes of the two source strings solves it in O(n*m) time.

</details>

## Solution

<details><summary>Reference approach</summary>

Decide whether s3 is formed by interleaving s1 and s2 while preserving each string's order. Match from the front: the next character of s3 must come from s1 or s2, so recurse on both options. Memoize on the pair (i, j) of positions consumed in s1 and s2 so each state is solved once. The equivalent bottom-up form fills a DP table where `dp[i][j]` is true when `s1[:i]` and `s2[:j]` interleave to form `s3[:i+j]`. Each cell is reachable either from above (consume an s1 char) or from the left (consume an s2 char).

```python
if len(s1) + len(s2) != len(s3): return false
dp[0][0] = true
for i in 1..len(s1): dp[i][0] = dp[i-1][0] and s1[i-1] == s3[i-1]
for j in 1..len(s2): dp[0][j] = dp[0][j-1] and s2[j-1] == s3[j-1]
for i in 1..len(s1):
    for j in 1..len(s2):
        dp[i][j] = (dp[i-1][j] and s1[i-1] == s3[i+j-1])
                or (dp[i][j-1] and s2[j-1] == s3[i+j-1])
return dp[len(s1)][len(s2)]
```

**Complexity** — time O(n*m); space O(n*m)

Full Python solution: [`LeetCodeCheat/interleaving-string.py`](../../python/leetcode/LeetCodeCheat/interleaving-string.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Reduce the DP to O(min(n, m)) memory with a rolling row.
- Reconstruct one valid interleaving instead of just a yes/no answer.
- Why does a purely greedy (non-DP) match fail?

Sources:

- [LeetCode - Interleaving String](https://leetcode.com/problems/interleaving-string/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/097-interleaving-string.yaml`.
