---
title: "LC 102 — Binary Tree Level Order Traversal"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [trees]
source: https://leetcode.com/problems/binary-tree-level-order-traversal/
---
## Prompt

Given the `root` of a binary tree, return its level-order traversal: a list of
lists where each inner list holds the node values at one depth, read left to right,
ordered from the root level downward. Example: `[3,9,20,null,null,15,7]` ->
`[[3], [9,20], [15,7]]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Each node belongs to a specific depth, so group node values by their level.

</details>

<details><summary>Hint 2</summary>

Traverse the tree while tracking the current depth, appending each node's value into that level's bucket.

</details>

<details><summary>Hint 3</summary>

One O(n) traversal, starting a new bucket the first time a depth is reached, produces the level-order lists.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Group node values by depth with a DFS that tracks the current level. The first time a level is seen, start a new bucket, then append each node's value to its level's bucket. Visiting the left child before the right keeps left-to-right order within each level. A BFS that processes the queue one level at a time is the equivalent iterative approach.

```python
result = []
dfs(node, level):
    if node is null: return
    if level == len(result): result.append([])
    dfs(node.left, level+1)
    result[level].append(node.val)
    dfs(node.right, level+1)
dfs(root, 0)
return result
```

**Complexity** — time O(n); space O(n)

Full Python solution: `LeetCodeCheat/binary-tree-level-order-traversal.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Do it iteratively with a queue, one level per outer loop.
- Return the levels bottom-up (LeetCode 107).
- Return a zigzag level order (LeetCode 103).

Sources:

- [LeetCode - Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/102-binary-tree-level-order-traversal.yaml`.
