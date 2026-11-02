---
title: "LC 126 — Word Ladder II"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [graphs]
source: https://leetcode.com/problems/word-ladder-ii/
---
## Prompt

Given `beginWord`, `endWord`, and a `wordList`, return all shortest transformation
sequences from `beginWord` to `endWord`. Each step changes exactly one letter, and
every intermediate word must be in `wordList`. Return each sequence as a list of
words; return `[]` if none exist. Example: `beginWord = "hit"`, `endWord = "cog"`,
list `[hot,dot,dog,lot,log,cog]` -> `[[hit,hot,dot,dog,cog], [hit,hot,lot,log,cog]]`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Bucket words by wildcard patterns, replacing one position with a placeholder, so words one letter apart share a bucket and form an implicit graph.

</details>

<details><summary>Hint 2</summary>

Run BFS from beginWord but record every predecessor that reaches a word at the shortest distance, not just the first one found.

</details>

<details><summary>Hint 3</summary>

DFS backward from endWord through the recorded parent links to reconstruct all shortest paths, after an O(N * L^2) graph build.

</details>

## Solution

<details><summary>Reference approach</summary>

Return every shortest transformation sequence. Bucket words by wildcard patterns that replace one position with '_', so words that differ by one letter share a bucket. This builds an implicit graph of single-letter-change neighbors. Run BFS from beginWord recording, for each word, all predecessors that first reach it at the shortest distance. Then DFS backward from endWord through those predecessor links to reconstruct all shortest paths.

```python
build groups: for each word and each position -> pattern -> list of words
graph[w] = all words sharing any wildcard pattern with w
BFS from begin:
    dist[begin] = 0
    for neighbor 'to' of 'from':
        if unseen: dist[to] = dist[from]+1; parents[to] = [from]; enqueue
        elif dist[to] == dist[from]+1: parents[to].append(from)
DFS from end back through parents, collecting reversed shortest paths
```

**Complexity** — time `O(N * L^2)` to build the graph, plus path enumeration; space `O(N * L)`

Full Python solution: [`LeetCodeCheat/word-ladder-ii.py`](../../python/leetcode/LeetCodeCheat/word-ladder-ii.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Why record all parents at the BFS frontier instead of just one?
- How do you avoid revisiting nodes yet still capture multiple shortest parents?
- Can the number of shortest paths be exponential in the input?

Sources:

- [LeetCode - Word Ladder II](https://leetcode.com/problems/word-ladder-ii/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/126-word-ladder-ii.yaml`.
