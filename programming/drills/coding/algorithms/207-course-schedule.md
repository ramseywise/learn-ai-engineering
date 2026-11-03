---
title: "LC 207 — Course Schedule"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [graphs]
source: https://leetcode.com/problems/course-schedule/
---
## Prompt

You must take `numCourses` courses labeled `0` to `numCourses - 1`. You are given
a list `prerequisites` where `[a, b]` means you must take course `b` before course
`a`. Return `true` if it is possible to finish all courses, `false` otherwise
(i.e., whether the dependency graph is free of cycles). Example:
`numCourses = 2`, `prerequisites = [[1,0],[0,1]]` -> `false`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Model prerequisites as a directed graph and ask whether that graph contains a cycle.

</details>

<details><summary>Hint 2</summary>

Run DFS marking nodes as currently being visited versus fully finished. Reaching a node still marked as being visited means you found a back edge.

</details>

<details><summary>Hint 3</summary>

Detecting any such cycle runs in O(V + E) time and means the schedule is infeasible.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Courses and their prerequisites form a directed graph. The schedule is feasible if and only if the graph has no cycle. Run DFS marking each node VISITING when entered and VISITED when finished. Reaching a node still marked VISITING means a back edge and thus a cycle, so it's infeasible. Translating the recursion to an explicit stack means pushing each node twice. Push once to open it (mark VISITING), and once with a counter to close it (mark VISITED).

```python
build adjacency list: edge prereq -> course
for each unvisited node: if not DFS(node): return false

DFS(start):
    stack = [(start, 0)]
    while stack:
        (n, cnt) = pop
        if cnt == 0 and status[n] == VISITING: return false     # cycle
        if cnt > 0: status[n] = VISITED; continue
        status[n] = VISITING; push (n, 1)
        for m in graph[n]: if status[m] != VISITED: push (m, 0)
    return true
```

**Complexity** — time O(V + E); space O(V + E)

Full Python solution: `LeetCodeCheat/course-schedule.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Return a valid course ordering, not just yes/no (LeetCode 210).
- Solve it with Kahn's algorithm using in-degrees and a queue.
- How does the two-push counter emulate the recursive call stack?

Sources:

- [LeetCode - Course Schedule](https://leetcode.com/problems/course-schedule/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/207-course-schedule.yaml`.
