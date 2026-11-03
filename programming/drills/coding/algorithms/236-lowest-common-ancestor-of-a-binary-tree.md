---
title: "LC 236 — Lowest Common Ancestor of a Binary Tree"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [trees]
source: https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/
---
## Prompt

Given the `root` of a binary tree (not necessarily a BST) and two nodes `p` and
`q` present in it, return their lowest common ancestor: the deepest node having
both `p` and `q` as descendants, where a node may be a descendant of itself.
Example: in a tree rooted at 3, the LCA of `5` and `1` is `3`, and the LCA of `5`
and `4` (with 4 under 5) is `5`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Think recursively about which subtree(s) the two target nodes fall into.

</details>

<details><summary>Hint 2</summary>

Recurse into both children, returning the node if it equals a target. Treat a node whose two children both report a find as the split point.

</details>

<details><summary>Hint 3</summary>

Propagate whichever single non-null result bubbles up otherwise, giving O(n) time and O(h) space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Recurse down the tree. A node is the LCA when p and q lie in different subtrees beneath it, or when the node equals p or q. Return the node when it equals p or q. Otherwise recurse into both children. If both sides return non-null, this node is the split point and thus the LCA. If only one side does, propagate that result upward.

```python
lca(node):
    if node is null or node == p or node == q: return node
    left  = lca(node.left)
    right = lca(node.right)
    if left and right: return node        # p and q split here
    return left or right                  # whichever side found something
```

**Complexity** — time O(n); space O(h)

Full Python solution: `LeetCodeCheat/lowest-common-ancestor-of-a-binary-tree.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Solve it faster with BST ordering when the tree is a BST (LeetCode 235).
- Adapt it to return null if either p or q is absent.
- Find the LCA using parent pointers instead of recursion.

Sources:

- [LeetCode - Lowest Common Ancestor of a Binary Tree](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/236-lowest-common-ancestor-of-a-binary-tree.yaml`.
