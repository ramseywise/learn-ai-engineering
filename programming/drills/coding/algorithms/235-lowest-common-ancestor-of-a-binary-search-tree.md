---
title: "LC 235 — Lowest Common Ancestor of a Binary Search Tree"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [trees]
source: https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/
---
## Prompt

Given the `root` of a binary search tree and two nodes `p` and `q` present in it,
return their lowest common ancestor: the deepest node that has both `p` and `q` as
descendants (a node may be a descendant of itself). Example: in a BST rooted at 6,
the LCA of `2` and `8` is `6`, and the LCA of `2` and `4` is `2`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

BST ordering tells you which subtree both target nodes must lie in at each step.

</details>

<details><summary>Hint 2</summary>

Starting at the root, move left if both values are smaller and right if both are larger. Stop where they diverge or one matches the current node.

</details>

<details><summary>Hint 3</summary>

That first split point gives the LCA in O(h) time and O(1) space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Use the BST ordering, walking down from the root. Go left if both p and q are smaller than the current node, and go right if both are larger. The first node where they split is the lowest common ancestor, as is any node that equals p or q. The implementation traces the root-to-p and root-to-q paths and returns their last common node.

```python
node = root
loop:
    if p.val < node.val and q.val < node.val: node = node.left
    elif p.val > node.val and q.val > node.val: node = node.right
    else: return node        # split point, or node equals p or q
```

**Complexity** — time O(h); space O(1)

Full Python solution: `LeetCodeCheat/lowest-common-ancestor-of-a-binary-search-tree.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Solve the general (non-BST) tree version (LeetCode 236).
- Why is the first split point guaranteed to be the LCA?
- Handle the case where one node is an ancestor of the other.

Sources:

- [LeetCode - Lowest Common Ancestor of a Binary Search Tree](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/235-lowest-common-ancestor-of-a-binary-search-tree.yaml`.
