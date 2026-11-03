---
title: "LC 307 — Range Sum Query - Mutable"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [design]
source: https://leetcode.com/problems/range-sum-query-mutable/
---
## Prompt

Design a `NumArray` initialized from an integer array `nums` that supports two
operations, both efficiently under interleaving: `update(i, val)` sets `nums[i]` to
`val`, and `sumRange(l, r)` returns the sum of the inclusive range `nums[l..r]`.
Example: after `update(1, 2)`, `sumRange(0, 2)` returns the sum of the first three
(updated) elements.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Both point updates and range-sum queries need to be faster than recomputing from scratch each time.

</details>

<details><summary>Hint 2</summary>

Store the array in a segment tree where each node holds the sum of its range. Updating a leaf then only touches its O(log n) ancestors.

</details>

<details><summary>Hint 3</summary>

A range query then combines O(log n) tree nodes, giving O(log n) update and query after an O(n) build.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Support point updates and range-sum queries efficiently by backing the array with a segment tree, where each node stores the sum of a subrange. Building is O(n), and an update fixes the O(log n) nodes on the path from a leaf to the root. A range query combines O(log n) node sums. A Fenwick (binary indexed) tree is the compact alternative.

```python
build a segment tree over nums (each node = sum of its range)
update(i, val): set leaf i, then propagate corrected sums up to the root
sumRange(l, r): combine the O(log n) tree segments that cover [l, r]
```

**Complexity** — time build O(n), update and query O(log n); space O(n)

Full Python solution: `LeetCodeCheat/range-sum-query-mutable.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Implement the same with a Fenwick (binary indexed) tree.
- Support range updates as well, using lazy propagation.
- Why is a plain prefix-sum array poor when values change often?

Sources:

- [LeetCode - Range Sum Query - Mutable](https://leetcode.com/problems/range-sum-query-mutable/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/307-range-sum-query-mutable.yaml`.
