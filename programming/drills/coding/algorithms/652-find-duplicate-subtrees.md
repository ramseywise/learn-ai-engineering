---
title: "LC 652 — Find Duplicate Subtrees"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [trees]
source: https://leetcode.com/problems/find-duplicate-subtrees/
---
## Prompt

Given the `root` of a binary tree, return one representative root node for each
group of duplicate subtrees. Two subtrees are duplicates when they have identical
structure and the same node values. For each set of duplicates, include only one
of their root nodes in the answer (order does not matter).

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Two subtrees are duplicates exactly when their structure and values match completely.

</details>

<details><summary>Hint 2</summary>

Give every subtree a canonical signature built from its value and its children's signatures, then group nodes by that signature.

</details>

<details><summary>Hint 3</summary>

Any group with more than one member marks a duplicate. Using assigned integer ids instead of raw strings brings the cost down from O(n^2) to O(n).

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Two subtrees are duplicates if and only if they have identical structure and values. Give each subtree a canonical signature: a serialization (or a bottom-up hash) of its value plus its children's signatures. Group nodes by signature. Any group with more than one node marks a duplicate, and one representative per such group is reported.

```python
signatures = map signature -> list of nodes
sign(node):
    if node is null: return "x"
    s = node.val + "(" + sign(left) + "," + sign(right) + ")"
    signatures[s].append(node)
    return s
sign(root)
return [group[0] for group in signatures if len(group) > 1]
```

**Complexity** — time O(n^2) with string signatures (O(n) with assigned ids); space O(n^2) / O(n)

Full Python solution: `LeetCodeCheat/find-duplicate-subtrees.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Replace string signatures with assigned integer ids to reach O(n).
- Why can naive string serialization cost O(n^2) in total?
- Guard against hash collisions if you hash subtrees.

Sources:

- [LeetCode - Find Duplicate Subtrees](https://leetcode.com/problems/find-duplicate-subtrees/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/652-find-duplicate-subtrees.yaml`.
