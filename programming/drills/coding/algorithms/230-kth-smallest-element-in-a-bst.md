---
title: "LC 230 — Kth Smallest Element in a BST"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [trees]
source: https://leetcode.com/problems/kth-smallest-element-in-a-bst/
---
## Prompt

Given the `root` of a binary search tree and an integer `k` (1-indexed), return
the value of the `k`-th smallest element among all node values. Example: for a
BST containing `1, 2, 3, 4` with `k = 1` -> `1`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

In-order traversal of a BST visits nodes in ascending sorted order.

</details>

<details><summary>Hint 2</summary>

Walk the tree in-order while keeping a counter, and stop as soon as the counter reaches k.

</details>

<details><summary>Hint 3</summary>

This reaches O(h + k) time using O(h) space, with no need to build the full sorted list.

</details>

## Solution

<details><summary>Reference approach</summary>

An in-order traversal of a BST visits values in ascending order, so the k-th node visited is the k-th smallest. Traverse in-order with a counter and stop as soon as the counter reaches k, returning that node's value without visiting the rest of the tree.

```python
count = 0; answer = null
inorder(node):
    if node is null or answer is found: return
    inorder(node.left)
    count += 1
    if count == k: answer = node.val; return
    inorder(node.right)
inorder(root)
return answer
```

**Complexity** — time O(h + k); space O(h)

Full Python solution: [`LeetCodeCheat/kth-smallest-element-in-a-bst.py`](../../python/leetcode/LeetCodeCheat/kth-smallest-element-in-a-bst.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Augment each node with its subtree size for O(h) queries under frequent modification.
- Find the k-th largest element instead.
- Why does in-order traversal produce sorted order for a BST?

Sources:

- [LeetCode - Kth Smallest Element in a BST](https://leetcode.com/problems/kth-smallest-element-in-a-bst/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/230-kth-smallest-element-in-a-bst.yaml`.
