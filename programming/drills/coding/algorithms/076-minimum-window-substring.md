---
title: "LC 76 — Minimum Window Substring"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [sliding-window]
source: https://leetcode.com/problems/minimum-window-substring/
---
## Prompt

Given two strings `s` and `t`, return the shortest substring of `s` that contains every
character of `t` including duplicates (counting multiplicity). If no such window exists,
return the empty string `""`. The answer is guaranteed unique when it exists. Example:
`s = "ADOBECODEBANC"`, `t = "ABC"` -> `"BANC"`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

A sliding window paired with a frequency count of the target characters tells you how much of the target is still missing.

</details>

<details><summary>Hint 2</summary>

Expand the window's right edge until it covers every needed character, then shrink from the left while it stays valid.

</details>

<details><summary>Hint 3</summary>

One pass with two pointers and running counts achieves O(n + m) time.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Sliding window with character counts. Count how many of each character t requires and track total_count, the number of still-needed characters. Expand the right edge over s, decrementing counts and total_count whenever the added character was actually needed. Whenever total_count hits 0 the window covers t, so try to shrink from the left. Record the window if it's the smallest so far, then remove the left character (bumping its count and total_count back if it was required) and advance left. Continue until the right edge reaches the end. Return the smallest recorded window.

```python
need = count of each char in t
total = len(t)
left = 0; best = none
for right in 0..len(s)-1:
    if need[s[right]] > 0: total--
    need[s[right]]--
    while total == 0:                 # window valid, shrink
        update best with [left, right]
        need[s[left]]++
        if need[s[left]] > 0: total++
        left++
return best window or ""
```

**Complexity** — time O(n + m); space O(alphabet)

Full Python solution: `LeetCodeCheat/minimum-window-substring.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/076-minimum-window-substring.yaml`.
