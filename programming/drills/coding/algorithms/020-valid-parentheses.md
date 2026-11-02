---
title: "LC 20 — Valid Parentheses"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [stack]
source: https://leetcode.com/problems/valid-parentheses/
---
## Prompt

Given a string `s` containing only the characters `()[]{}`, determine whether it is
valid: every opening bracket is closed by the matching type of bracket, and brackets
are closed in the correct order. Example: `"()[]{}"` -> `true`; `"(]"` -> `false`;
`"([)]"` -> `false`; `"{[]}"` -> `true`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

A stack naturally tracks which opening brackets are still waiting to be closed.

</details>

<details><summary>Hint 2</summary>

Push every opening bracket, and on a closing bracket check the stack's top is the matching opener and pop it, failing immediately if the stack is empty or the pair doesn't match.

</details>

<details><summary>Hint 3</summary>

One linear pass with this stack is valid only if the stack ends up empty at the end, giving O(n) time and O(n) space.

</details>

## Solution

<details><summary>Reference approach</summary>

Use a stack and push every opening bracket. On a closing bracket, the stack must be non-empty and its top must be the matching opener. Pop it and check the pair matches. If the stack is empty or the pair is wrong, the string is invalid. After scanning everything, the string is valid only if the stack is empty (no unclosed openers).

```python
stack = []
for c in s:
    if c in "([{":
        stack.push(c)
    else if c in ")]}":
        if stack empty: return false
        if not matches(stack.pop(), c): return false
return stack is empty
```

**Complexity** — time O(n); space O(n)

Full Python solution: [`LeetCodeCheat/valid-parentheses.py`](../../python/leetcode/LeetCodeCheat/valid-parentheses.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Valid Parentheses](https://leetcode.com/problems/valid-parentheses/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/020-valid-parentheses.yaml`.
