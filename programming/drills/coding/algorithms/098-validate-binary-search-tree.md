---
title: "LC 98 — Validate Binary Search Tree"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [trees]
source: https://leetcode.com/problems/validate-binary-search-tree/
---
## Prompt

Given the `root` of a binary tree, return `true` if it is a valid binary search
tree. Valid means every node's entire left subtree holds strictly smaller values,
its entire right subtree holds strictly larger values, and both subtrees are
themselves valid BSTs. Example: root `[2,1,3]` -> `true`; `[5,1,4,null,null,3,6]` -> `false`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Recall that visiting a binary search tree in-order produces its values in sorted order.

</details>

<details><summary>Hint 2</summary>

Traverse the tree in-order and compare each value to the one visited right before it.

</details>

<details><summary>Hint 3</summary>

A single O(n) pass checking for strictly increasing values confirms validity.

</details>

## Solution

<details><summary>Reference approach</summary>

An in-order traversal of a binary search tree yields values in strictly increasing order. Traverse in-order collecting the values, then check that every adjacent pair is strictly increasing. Any equal-or-decreasing pair means the tree isn't a valid BST.

```python
values = []
inorder(node):
    if node is null: return
    inorder(node.left); values.append(node.val); inorder(node.right)
inorder(root)
for i in 1..len(values)-1:
    if values[i-1] >= values[i]: return false
return true
```

**Complexity** — time O(n); space O(n)

Full Python solution: [`LeetCodeCheat/validate-binary-search-tree.py`](../../python/leetcode/LeetCodeCheat/validate-binary-search-tree.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Do it in O(h) space by tracking only the previously visited value during traversal.
- Alternatively pass down (low, high) bounds to each node - how does that work?
- Handle duplicate values per the problem's chosen convention.

Sources:

- [LeetCode - Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/098-validate-binary-search-tree.yaml`.
