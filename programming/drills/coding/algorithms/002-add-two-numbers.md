---
title: "LC 2 — Add Two Numbers"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [linked-list]
source: https://leetcode.com/problems/add-two-numbers/
---
## Prompt

You're given two non-empty singly linked lists representing two non-negative
integers, with the digits stored in reverse order (least-significant digit first)
and one digit per node. Add the two numbers and return the sum as a linked list in
the same reversed-digit form. The lists may differ in length. Example:
`[2,4,3] + [5,6,4]` represents `342 + 465 = 807` -> `[7,0,8]`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

The digits are stored least-significant-first, so you can add the two lists the same way you add numbers by hand, one position at a time.

</details>

<details><summary>Hint 2</summary>

At each position add the two current digits plus the incoming carry. Keep the units digit for a new node and pass the rest forward as the next carry.

</details>

<details><summary>Hint 3</summary>

Treat a missing node as digit 0 so lists of different lengths work. Emit one final node if a carry remains at the end, for O(max(n, m)) time and space.

</details>

## Solution

<details><summary>Reference approach</summary>

The digits are stored least-significant first, so add them the way you add by hand in school. Scan both lists in lockstep, adding the two current digits plus the incoming carry. Keep the units digit in a new node and pass the carry (0 or 1) forward. When both lists are exhausted, emit one final node if a carry remains. Treat a missing node as the digit 0 so lists of different lengths work.

```python
add(l1, l2, carry):
    if l1 is null and l2 is null:
        return new Node(carry) if carry > 0 else null
    sum = val(l1) + val(l2) + carry        # val(null) = 0
    node = new Node(sum % 10)
    node.next = add(next(l1), next(l2), sum / 10)
    return node
```

**Complexity** — time O(max(n, m)); space O(max(n, m))

Full Python solution: [`LeetCodeCheat/add-two-numbers.py`](../../python/leetcode/LeetCodeCheat/add-two-numbers.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Add Two Numbers](https://leetcode.com/problems/add-two-numbers/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/002-add-two-numbers.yaml`.
