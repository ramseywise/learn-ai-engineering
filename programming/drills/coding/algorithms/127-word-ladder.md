---
title: "LC 127 — Word Ladder"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [graphs]
source: https://leetcode.com/problems/word-ladder/
---
## Prompt

Given `beginWord`, `endWord`, and a `wordList`, return the number of words in the
shortest transformation sequence from `beginWord` to `endWord` (counting both ends),
or `0` if none exists. Each step changes exactly one letter and every intermediate
word must be in `wordList`. Example: `beginWord = "hit"`, `endWord = "cog"`,
list `[hot,dot,dog,lot,log,cog]` -> `5`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Group words by wildcard patterns, one position replaced by a placeholder, so one-letter-apart words share a bucket and form an implicit graph.

</details>

<details><summary>Hint 2</summary>

Instead of BFS from only beginWord, grow two frontiers simultaneously from beginWord and endWord, expanding the smaller one each step.

</details>

<details><summary>Hint 3</summary>

Stop as soon as the two frontiers meet and sum their distances, for O(N * L^2) time.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Return only the shortest transformation length, using the same wildcard-pattern graph where words that differ by one letter share a bucket. Then run bidirectional BFS from both beginWord and endWord, expanding the two frontiers alternately. When they meet, the shortest ladder length is the sum of the two distances. Searching from both ends keeps each frontier small and cuts the explored space dramatically versus one-directional BFS.

```python
build wildcard groups -> graph of neighbors
frontier1 from begin (dist1), frontier2 from end (dist2)
while both frontiers non-empty:
    expand one frontier by a single BFS step
    if a newly reached node already sits in the other frontier:
        return dist1[node] + dist2[node] + boundary offset
return 0 if the frontiers never meet
```

**Complexity** — time `O(N * L^2)`; space `O(N * L)`

Full Python solution: `LeetCodeCheat/word-ladder.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Why is bidirectional BFS asymptotically better here?
- Return the actual ladder rather than its length (LeetCode 126).
- How does the wildcard index beat pairwise word comparisons?

Sources:

- [LeetCode - Word Ladder](https://leetcode.com/problems/word-ladder/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/127-word-ladder.yaml`.
