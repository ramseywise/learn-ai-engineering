---
title: "LC 30 — Substring with Concatenation of All Words"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [sliding-window]
source: https://leetcode.com/problems/substring-with-concatenation-of-all-words/
---
## Prompt

Given a string `s` and an array `words` of strings that all have the same length,
return the starting indices of every substring of `s` that is a concatenation of all
the words in `words` exactly once, in any order and with no characters in between.
Example: `s = "barfoothefoobarman"`, `words = ["foo","bar"]` -> `[0,9]` (`"barfoo"`
at index 0 and `"foobar"` at index 9).

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Since every word has the same fixed length, precompute for each position in the string which of the words, if any, starts there.

</details>

<details><summary>Hint 2</summary>

For each candidate start index, try to greedily consume the required words with backtracking. Track how many of each distinct word are still needed, undoing a choice when it leads nowhere.

</details>

<details><summary>Hint 3</summary>

Restricting attempts to starts whose total span fits, and stopping early at positions with no matching word, keeps this close to O(n * total words) in typical cases.

</details>

## Solution

<details><summary>Reference approach</summary>

All words have the same length, and we want every start index where some permutation of all the words appears back to back. Precompute, for each position i in s, which words match starting at i (a small candidate list per position). Also count how many times each distinct word must be used. Then, for each viable start (one whose total span fits), try to consume the words greedily with backtracking. At the current position pick an unused matching word, decrement its remaining count, jump forward by its length, and recurse until all words are consumed, undoing on failure. Record starts that succeed.

```python
L = word length; total = number of words
counts = required count per distinct word
matches[i] = list of words that equal s[i : i+L]
for start in 0 .. len(s) - total*L:
    if can_consume(start, matches, counts_copy, total):
        output start

can_consume(pos, matches, counts, remaining):
    if remaining == 0: return true
    for w in matches[pos] with counts[w] > 0:
        counts[w]--
        if can_consume(pos + L, matches, counts, remaining - 1): return true
        counts[w]++
    return false
```

**Complexity** — time roughly O(n * total) in the good cases; backtracking worst case is higher; space O(n + total)

Full Python solution: [`LeetCodeCheat/substring-with-concatenation-of-all-words.py`](../../python/leetcode/LeetCodeCheat/substring-with-concatenation-of-all-words.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Substring with Concatenation of All Words](https://leetcode.com/problems/substring-with-concatenation-of-all-words/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/030-substring-concatenation.yaml`.
