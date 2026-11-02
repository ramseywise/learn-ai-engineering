---
title: "Reverse a linked list"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [linked-list]
source: https://leetcode.com/problems/reverse-linked-list/
---
## Prompt

Reverse a singly linked list in place. This was reported in an AI-assisted coding
round (Microsoft Applied AI/ML): you may use an LLM, but the interviewer modifies
the constraints mid-problem and watches how you re-prompt and verify. Give the
iterative and recursive solutions and the constraint variants.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Track a prev pointer (start null). For each node: save next, repoint node.next to prev, then advance prev and the cursor.

</details>

<details><summary>Hint 2</summary>

The invariant is that everything up to prev is already reversed. When the cursor is null, prev is the new head.

</details>

<details><summary>Hint 3</summary>

In an AI-assisted round, verify the model's code on a 2-3 node example. Re-prompt precisely when the interviewer adds a constraint (O(1) space, reverse m..n, groups of k).

</details>

## Solution

<details><summary>Reference approach</summary>

Reverse the pointers in a single pass, keeping a prev pointer that starts at null. For each node, save its next, point the node back to prev, then advance both prev and the cursor. When the cursor runs off the end, prev is the new head. This is O(n) time, O(1) space, and doesn't allocate new nodes. The recursive version reverses the tail first and then flips the link between the current node and its successor, at O(n) stack cost. In an AI-assisted round the code is easy. The signal is how you work: state the invariant (everything before prev is already reversed) and verify the LLM's output against a tiny example. When the interviewer adds a constraint ("O(1) space", "reverse only nodes m..n", "in groups of k"), re-prompt precisely and check edge cases (empty list, single node) rather than pasting blindly.

```python
# iterative, O(1) space
def reverse(head):
    prev, node = None, head
    while node:
        nxt = node.next
        node.next = prev
        prev = node
        node = nxt
    return prev

# recursive, O(n) stack
def reverse_rec(node, prev=None):
    if node is None: return prev
    nxt = node.next
    node.next = prev
    return reverse_rec(nxt, node)
```

**Complexity** — time O(n); space O(1) iterative; O(n) recursion stack

Full Python solution: [`LeetCodeCheat/reverse-linked-list.py`](../../python/leetcode/LeetCodeCheat/reverse-linked-list.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Reverse only nodes between positions m and n in one pass (LeetCode 92).
- Reverse the list in groups of k (LeetCode 25).
- State the recursion's stack cost and when it would overflow.
- In an AI-assisted round, how do you show the interviewer you understand the generated code rather than pasting it?
- How would you test your reversal, and what edge cases must the tests cover?

Sources:

- [LeetCode — 206. Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/)
- [Reddit — Microsoft SWE Applied AI/ML Summer 2026 (r/csMajors)](https://www.reddit.com/r/csMajors/comments/1nqfzhq/microsoft_swe_applied_aiml_summer_2026_redmond)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-reverse-linked-list.yaml`.
