---
title: "LC 199 — Binary Tree Right Side View"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [trees]
source: https://leetcode.com/problems/binary-tree-right-side-view/
---
## Prompt

Given the `root` of a binary tree, imagine standing to its right; return the values
of the nodes visible from top to bottom, i.e. the rightmost node at each depth.
Example: `[1,2,3,null,5,null,4]` -> `[1,3,4]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

The rightmost visible node at each depth is simply the last node encountered at that depth during a traversal.

</details>

<details><summary>Hint 2</summary>

Do a DFS visiting left before right (or a level-order traversal) while tracking depth, recording values per level.

</details>

<details><summary>Hint 3</summary>

Return the last value stored at each level, in O(n) time.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

The right-side view is the last node encountered at each depth. Traverse the tree collecting values per level (as in level-order), then take the last value of each level - the rightmost node visible from the right.

```python
levels = []
dfs(node, depth):
    if node is null: return
    if depth == len(levels): levels.append([])
    dfs(node.left, depth+1)
    levels[depth].append(node.val)
    dfs(node.right, depth+1)
dfs(root, 0)
return [level.last for level in levels]
```

**Complexity** — time O(n); space O(n)

Full Python solution: `LeetCodeCheat/binary-tree-right-side-view.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Do it with BFS, taking the last node dequeued per level.
- Return the left-side view instead.
- Reach O(h) space by visiting the right child first and recording the first node per depth.

Sources:

- [LeetCode - Binary Tree Right Side View](https://leetcode.com/problems/binary-tree-right-side-view/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/199-binary-tree-right-side-view.yaml`.
