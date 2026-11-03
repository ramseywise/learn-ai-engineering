---
title: "LC 815 — Bus Routes"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [graphs]
source: https://leetcode.com/problems/bus-routes/
---
## Prompt

You are given `routes`, where `routes[i]` is the list of stops served by bus `i` on
a repeating loop, plus a `source` stop and a `target` stop. Starting at `source`,
return the fewest number of buses you must ride to reach `target`, or `-1` if it is
impossible. You may only travel between stops by boarding buses. Example:
`routes = [[1,2,7],[3,6,7]]`, `source = 1`, `target = 6` -> `2`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Think of buses, not stops, as the nodes of the graph you should search over.

</details>

<details><summary>Hint 2</summary>

Build an index from stop to buses, and connect any two buses that share a stop. Then add artificial start and end nodes linked to the buses serving S and T.

</details>

<details><summary>Hint 3</summary>

A BFS over this bus graph gives the minimum number of buses as the path length minus the two artificial nodes.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Model routes as a graph over buses, not over stops. Build an inverted index stop -> buses, then connect two buses whenever they share a stop. Add artificial start and end nodes linked to the buses that serve S and T. A BFS from the start node gives the fewest buses (edges) needed to reach T. Each edge crossed is one bus change.

```python
index[stop] = list of buses serving it
for each stop served by >= 2 buses: connect all those buses pairwise
start node -> buses at S; buses at T -> end node
BFS from start to end
answer = (path length in nodes) - 2      # exclude the two artificial nodes
return -1 if T is unreachable
```

**Complexity** — time O(sum of route lengths + B^2) worst case for graph build; space O(B^2)

Full Python solution: `LeetCodeCheat/bus-routes.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Why build the graph over buses rather than over stops?
- How do the two artificial nodes simplify the BFS?
- Bound the graph size when many buses share the same stops.

Sources:

- [LeetCode - Bus Routes](https://leetcode.com/problems/bus-routes/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/815-bus-routes.yaml`.
