---
title: "LC 25 — Reverse Nodes in k-Group"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [linked-list]
source: https://leetcode.com/problems/reverse-nodes-in-k-group/
---
## Prompt

Given the head of a linked list, reverse the nodes `k` at a time and return the
modified list. Process the list in consecutive groups of `k`; if the final group has
fewer than `k` nodes, leave it in its original order. Node values are not changed,
only the links. Example: `head = [1,2,3,4,5]`, `k = 2` -> `[2,1,4,3,5]`; with
`k = 3` -> `[3,2,1,4,5]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Process the list one group of k nodes at a time rather than reversing the whole list in one go.

</details>

<details><summary>Hint 2</summary>

For each group, first confirm k nodes actually remain. Then reverse just those k nodes in place and reconnect the previous group's tail to the new group's head.

</details>

<details><summary>Hint 3</summary>

Remember the node right after the group before reversing so you can continue correctly. Use a dummy head to simplify stitching the first group. This runs in O(n) time and O(1) space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Process the list group by group. For each group of k nodes, first check there are k nodes left by advancing to the group end. If fewer than k remain, leave that tail as-is and stop. Otherwise remember the node after the group and reverse the k nodes in place. Connect the previous group's tail to the new head (the old group end) while the old group start becomes the new tail. Continue from the saved next node. A dummy head simplifies stitching the first group.

```python
dummy -> head; prev = dummy
group_start = head
while group_start:
    group_end = advance k-1 from group_start (null if < k remain)
    if group_end is null:
        prev.next = group_start; break
    next = group_end.next
    reverse nodes from group_start to group_end
    prev.next = group_end        # reversed head
    prev = group_start           # reversed tail
    group_start = next
return dummy.next
```

**Complexity** — time O(n); space O(1)

Full Python solution: `LeetCodeCheat/reverse-nodes-in-k-group.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Reverse Nodes in k-Group](https://leetcode.com/problems/reverse-nodes-in-k-group/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/025-reverse-nodes-in-k-group.yaml`.
