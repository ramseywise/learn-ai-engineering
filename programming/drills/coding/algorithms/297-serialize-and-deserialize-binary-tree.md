---
title: "LC 297 — Serialize and Deserialize Binary Tree"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [trees]
source: https://leetcode.com/problems/serialize-and-deserialize-binary-tree/
---
## Prompt

Design a codec for an arbitrary binary tree. Implement `serialize(root)` to encode
the tree into a single string, and `deserialize(data)` to rebuild the exact same
tree from that string. The encoding format is up to you; the only requirement is
that deserializing a serialized tree reproduces the original structure and node
values.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

A tree can be fully captured by a preorder traversal as long as you also record where children are null.

</details>

<details><summary>Hint 2</summary>

Serialize by recursively writing each node's value and its children with a sentinel marker for null. Then deserialize by parsing that same order with a position cursor.

</details>

<details><summary>Hint 3</summary>

Both directions run in O(n) time and O(n) space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Serialize with a recursive preorder that writes each node's value plus its two subtrees in parentheses, using a marker (such as 'x') for null children. This fully captures the structure. Deserialize by parsing that string left to right with a position cursor, rebuilding each node, then its left and right subtrees, recursively.

```python
serialize(node):
    if node is null: emit "x"; return
    emit node.val, "(", serialize(left), ",", serialize(right), ")"
deserialize(s):
    parse(pos):
        if s[pos] == 'x': pos++; return null
        read number val; expect '('
        node.left  = parse(pos); expect ','
        node.right = parse(pos); expect ')'
        return node
```

**Complexity** — time O(n); space O(n)

Full Python solution: `LeetCodeCheat/serialize-and-deserialize-binary-tree.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Use level-order (BFS) serialization instead of preorder.
- Serialize a BST more compactly using its ordering (LeetCode 449).
- Handle negative and multi-digit values in the parser.

Sources:

- [LeetCode - Serialize and Deserialize Binary Tree](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/297-serialize-and-deserialize-binary-tree.yaml`.
