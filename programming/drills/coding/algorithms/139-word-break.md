---
title: "LC 139 — Word Break"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [dynamic-programming]
source: https://leetcode.com/problems/word-break/
---
## Prompt

Given a string `s` and a dictionary `wordDict`, return `true` if `s` can be segmented
into a sequence of one or more dictionary words. Words may be reused any number of
times. Example: `s = "leetcode"`, `wordDict = ["leet","code"]` -> `true`;
`s = "catsandog"`, `wordDict = ["cats","dog","sand","and","cat"]` -> `false`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Think of segmenting the string as making jumps from a start index whose lengths equal matching dictionary words.

</details>

<details><summary>Hint 2</summary>

Recursively try each dictionary word matching at the current start index and recurse on the remainder, memoizing start indices already known to fail.

</details>

<details><summary>Hint 3</summary>

Bucketing dictionary words by their first letter avoids checking every word at each position, keeping it close to O(n^2).

</details>

## Solution

<details><summary>Reference approach</summary>

Decide whether s can be segmented into a sequence of dictionary words. From a start index, try each dictionary word that matches at that position and recurse on the remainder. Memoize start positions already known to fail so each index is explored once. Bucketing dictionary words by their first letter prunes the candidates checked at each step.

```python
memo = set of start indices known to fail
solve(start):
    if start == len(s): return true
    if start in memo: return false
    for word in dict_by_first_letter[s[start]]:
        if s starts with word at 'start' and solve(start + len(word)):
            return true
    add start to memo; return false
return solve(0)
```

**Complexity** — time O(n^2) (times word length for matching); space O(n)

Full Python solution: [`LeetCodeCheat/word-break.py`](../../python/leetcode/LeetCodeCheat/word-break.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Return all segmentations (LeetCode 140) and explain why that can blow up.
- Rewrite it as bottom-up DP over prefix lengths.
- Use a trie to match candidate words faster.

Sources:

- [LeetCode - Word Break](https://leetcode.com/problems/word-break/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/139-word-break.yaml`.
