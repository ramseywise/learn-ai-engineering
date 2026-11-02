---
title: "LC 99 — Recover Binary Search Tree"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [trees]
source: https://leetcode.com/problems/recover-binary-search-tree/
---
## Prompt

You are given the `root` of a binary search tree in which exactly two nodes had
their values swapped by mistake. Recover the tree by fixing those two values,
without changing its structure. Example: `[1,3,null,null,2]` (nodes `3` and `2`
swapped) becomes `[3,1,null,null,2]`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Two nodes were swapped, so an in-order traversal is sorted everywhere except near the swap points.

</details>

<details><summary>Hint 2</summary>

Scan the in-order sequence for the first place the order breaks and the last place it breaks - those two nodes were swapped.

</details>

<details><summary>Hint 3</summary>

Swap their values back in a single O(n) traversal (O(1) extra space is possible with Morris traversal).

</details>

## Solution

<details><summary>Reference approach</summary>

Two nodes of a BST were swapped, so an in-order traversal is sorted except at the swap points. Collect the nodes in-order. Scan left-to-right for the first place the order breaks (the larger misplaced node), and scan right-to-left for the last break (the smaller misplaced node). Then swap those two nodes' values to restore the tree.

```python
nodes = inorder(root)                    # list of nodes
left  = first i where nodes[i].val > nodes[i+1].val
right = last  i where nodes[i].val < nodes[i-1].val
swap nodes[left].val and nodes[right].val
```

**Complexity** — time O(n); space O(n)

Full Python solution: [`LeetCodeCheat/recover-binary-search-tree.py`](../../python/leetcode/LeetCodeCheat/recover-binary-search-tree.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Achieve O(1) extra space with Morris in-order traversal.
- Why are two separate scans (from each end) needed?
- What changes when the two swapped nodes are adjacent in-order?

Sources:

- [LeetCode - Recover Binary Search Tree](https://leetcode.com/problems/recover-binary-search-tree/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/099-recover-binary-search-tree.yaml`.
