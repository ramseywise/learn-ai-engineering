---
title: "LC 45 — Jump Game II"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [greedy-intervals]
source: https://leetcode.com/problems/jump-game-ii/
---
## Prompt

Given a 0-indexed array `nums` where `nums[i]` is the maximum forward jump length from
index `i`, return the minimum number of jumps needed to reach the last index. You start
at index `0`, and the input guarantees the end is always reachable. Example:
`nums = [2,3,1,1,4]` -> `2` (jump `0 -> 1 -> 4`).

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Picture each index as reachable from any earlier index whose jump range covers it. Think of the minimum jumps as a shortest path in this implicit graph.

</details>

<details><summary>Hint 2</summary>

Process indices level by level as in BFS, where each level corresponds to one additional jump. Mark each index's distance the first time it becomes reachable.

</details>

<details><summary>Hint 3</summary>

This BFS-by-levels (equivalently, greedily extending the current reach) gives the minimum jump count in O(n) time and O(n) space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Treat indices as nodes: from index i you can reach any index up to i + nums[i], so the minimum number of jumps to the end is the shortest path in this graph. A BFS by levels finds it, one jump per level. Process indices in FIFO order, marking newly reachable indices with their distance (parent distance + 1). The first time you can reach or pass the last index, that distance + 1 is the answer. (Equivalently this is the greedy "extend the current reach as far as possible, then take a jump" idea.)

```python
dist = [-1]*n; dist[0] = 0
queue = [0]
while queue:
    i = queue.pop_front()
    if i + nums[i] >= n-1: return dist[i] + 1
    for j from i + nums[i] down to i+1:
        if not visited[j]:
            dist[j] = dist[i] + 1; visited[j] = true; queue.push(j)
return dist[n-1]
```

**Complexity** — time O(n); space O(n)

Full Python solution: `LeetCodeCheat/jump-game-ii.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Jump Game II](https://leetcode.com/problems/jump-game-ii/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/045-jump-game-ii.yaml`.
