---
title: "LC 211 — Design Add and Search Words Data Structure"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [tries]
source: https://leetcode.com/problems/design-add-and-search-words-data-structure/
---
## Prompt

Design a `WordDictionary` supporting two operations: `addWord(word)` stores a
word, and `search(word)` returns `true` if any stored word matches. The search
string may contain the wildcard `.`, which matches any single letter. Example:
after adding `"bad"`, `"dad"`, `"mad"`, `search("b..")` -> `true` and
`search("pad")` -> `false`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Store all words in a trie so common prefixes are shared and lookups walk letter by letter.

</details>

<details><summary>Hint 2</summary>

To add a word, descend the trie creating child nodes as needed and mark the final node as an end of word.

</details>

<details><summary>Hint 3</summary>

To search with wildcard dots, recurse into every child at that position instead of following a single path.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Store words in a trie (26-way children plus a flag marking word ends). addWord walks and creates nodes letter by letter. search walks the trie too, but on a '.' wildcard it recurses into every child and succeeds if any branch matches the rest of the pattern.

```python
node: children[26], is_word
add(word): descend creating nodes; mark the last node is_word
search(node, pattern):
    for each char c in pattern:
        if c == '.': return any child matches search(child, rest of pattern)
        else: node = node.children[c]; if null return false
    return node.is_word
```

**Complexity** — time add O(L); search O(L) typical, up to O(26^d) with d wildcards; space O(total characters stored)

Full Python solution: `LeetCodeCheat/add-and-search-word-data-structure-design.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Bound the worst-case wildcard search cost with many dots.
- Compress the trie into a radix/Patricia tree to save memory.
- Support deletion of words.

Sources:

- [LeetCode - Design Add and Search Words Data Structure](https://leetcode.com/problems/design-add-and-search-words-data-structure/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/211-design-add-and-search-words-data-structure.yaml`.
