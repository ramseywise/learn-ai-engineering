---
title: "LC 72 — Edit Distance"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [dynamic-programming]
source: https://leetcode.com/problems/edit-distance/
---
## Prompt

Given two strings `word1` and `word2`, return the minimum number of single-character
edits needed to turn `word1` into `word2`. Allowed operations are inserting a character,
deleting a character, or replacing a character. Example: `word1 = "horse"`,
`word2 = "ros"` -> `3`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Think about building a table where each cell represents the edit distance between a prefix of one string and a prefix of the other.

</details>

<details><summary>Hint 2</summary>

Each cell's value comes from the best of three neighboring cells, representing a substitution, a deletion, and an insertion.

</details>

<details><summary>Hint 3</summary>

Fill the table bottom-up in O(n1 * n2) time and space. Seed the first row and column with 0, 1, 2, ...

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Build a DP table (Levenshtein distance), where `distance[i][j]` is the edit distance between the first i characters of s1 and the first j characters of s2. Each cell is the minimum of three moves. Substitution is `distance[i-1][j-1]`, plus 1 unless `s1[i]` == `s2[j]` (in which case the characters already line up for free). Deletion is `distance[i-1][j]` + 1. Insertion is `distance[i][j-1]` + 1. Initialize the first row/column to 0,1,2,... (turning an empty string into a prefix costs one edit per character). The answer is `distance[n1][n2]`.

```python
dp[0][j] = j ; dp[i][0] = i
for i in 1..n1:
    for j in 1..n2:
        subst = dp[i-1][j-1] + (0 if s1[i-1]==s2[j-1] else 1)
        delete = dp[i-1][j] + 1
        insert = dp[i][j-1] + 1
        dp[i][j] = min(subst, delete, insert)
return dp[n1][n2]
```

**Complexity** — time `O(n1 * n2)`; space `O(n1 * n2)`

Full Python solution: `LeetCodeCheat/edit-distance.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Edit Distance](https://leetcode.com/problems/edit-distance/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/072-edit-distance.yaml`.
