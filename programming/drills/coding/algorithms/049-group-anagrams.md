---
title: "LC 49 — Group Anagrams"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [arrays-hashing]
source: https://leetcode.com/problems/group-anagrams/
---
## Prompt

Given an array of strings `strs`, group together the strings that are anagrams of one
another (same letters rearranged) and return the groups in any order. Example:
`["eat","tea","tan","ate","nat","bat"]` -> `[["eat","tea","ate"],["tan","nat"],["bat"]]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Two words are anagrams exactly when they share the same multiset of letters, so you need a canonical form to compare them by.

</details>

<details><summary>Hint 2</summary>

Sort the letters of each word to get a canonical key. Use a hash map from that key to the list of words sharing it.

</details>

<details><summary>Hint 3</summary>

One pass over all words, sorting each into its bucket, gives O(N * k log k) time for N words of max length k.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Two words are anagrams exactly when their sorted letters are identical, so use the sorted string as a canonical key. Scan the input, sort each word to get its key, and append the original word to a hash map bucket under that key. The map's values are the anagram groups.

```python
groups = {}                     # sorted-key -> list of words
for w in strings:
    key = sorted(w)
    groups[key].append(w)
return groups.values()
```

**Complexity** — time `O(N * k log k)` for N words of max length k; space `O(N * k)`

Full Python solution: `LeetCodeCheat/group-anagrams.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Group Anagrams](https://leetcode.com/problems/group-anagrams/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/049-group-anagrams.yaml`.
