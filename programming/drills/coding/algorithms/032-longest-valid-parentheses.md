---
title: "LC 32 — Longest Valid Parentheses"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [stack]
source: https://leetcode.com/problems/longest-valid-parentheses/
---
## Prompt

Given a string `s` containing only `(` and `)`, return the length of the longest
contiguous substring that is well-formed (properly matched) parentheses. Example:
`s = "(()"` -> `2` (the substring `"()"`); `s = ")()())"` -> `4` (the substring
`"()()"`); `s = ""` -> `0`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Think about tracking, for each opening bracket, the index where its matching closing bracket occurs, using a stack of indices.

</details>

<details><summary>Hint 2</summary>

After recording all matches with a single left-to-right stack pass, chain together consecutive matched pairs starting from each position to measure contiguous valid runs.

</details>

<details><summary>Hint 3</summary>

A single O(n) pass with a stack and an array of match endpoints gets you the answer in O(n) time and O(n) space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Match parentheses with a stack of indices, then measure runs. Scan left to right, pushing the index of each '('. On a ')', if the stack is non-empty, pop the matching '(' index and record that it closes at the current position (end_ptr[open] = i). This gives, for every opening bracket that's part of a valid pair, where its pair ends. Then sweep the string: whenever a position has a recorded end, chain forward through consecutive matched segments to accumulate the length of a contiguous valid run, keeping the maximum.

```python
end_ptr = array of -1
stack = []
for i, c in s:
    if c == '(': stack.push(i)
    else if stack not empty:
        open = stack.pop(); end_ptr[open] = i
best = 0; i = 0
while i < n:
    length = 0
    while end_ptr[i] != -1:
        length += end_ptr[i] - i + 1
        i = end_ptr[i] + 1
    best = max(best, length)
    i++
return best
```

**Complexity** — time O(n); space O(n)

Full Python solution: `LeetCodeCheat/longest-valid-parentheses.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Longest Valid Parentheses](https://leetcode.com/problems/longest-valid-parentheses/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/032-longest-valid-parentheses.yaml`.
