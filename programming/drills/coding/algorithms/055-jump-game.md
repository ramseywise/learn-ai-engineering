---
title: "LC 55 — Jump Game"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [greedy-intervals]
source: https://leetcode.com/problems/jump-game/
---
## Prompt

Given an array `nums` where `nums[i]` is the maximum forward jump length from index `i`,
determine whether you can reach the last index starting from index `0`. Return `true` or
`false`. Example: `nums = [2,3,1,1,4]` -> `true`; `nums = [3,2,1,0,4]` -> `false`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

You don't need to track every possible jump sequence, just the farthest index reachable so far.

</details>

<details><summary>Hint 2</summary>

Scan the array left to right, updating the farthest reachable index at each step. Do this only while the current index is still within that reachable range.

</details>

<details><summary>Hint 3</summary>

This greedy single pass tells you in O(n) time and O(1) space whether the last index can ever be reached.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Greedy single pass tracking the farthest index reachable so far. Scan left to right, but only through positions you can actually reach (i <= max_index). At each i update max_index = max(max_index, i + nums[i]). If you can reach the last index, return true. If the loop stalls because i outran max_index, return false.

```python
max_index = 0
for i in 0..n-1:
    if i > max_index: return false      # can't reach here
    max_index = max(max_index, i + nums[i])
return max_index >= n - 1
```

**Complexity** — time O(n); space O(1)

Full Python solution: `LeetCodeCheat/jump-game.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Jump Game](https://leetcode.com/problems/jump-game/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/055-jump-game.yaml`.
