---
title: "LC 3 — Longest Substring Without Repeating Characters"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [sliding-window]
source: https://leetcode.com/problems/longest-substring-without-repeating-characters/
---
## Prompt

Given a string `s`, return the length of the longest contiguous substring that
contains no repeated characters. Example: for `s = "abcabcbb"` the answer is `3`
(the substring `"abc"`); for `s = "bbbbb"` it is `1`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Track a sliding window over the string along with a map from character to the last index at which it appeared.

</details>

<details><summary>Hint 2</summary>

When you hit a character already seen inside the current window, jump the window's start to just after that previous occurrence. This avoids restarting the scan.

</details>

<details><summary>Hint 3</summary>

One left-to-right pass updating the start and the best length as you go gives O(n) time.

</details>

## Solution

<details><summary>Reference approach</summary>

As you scan, keep start, the index where the current substring (the one ending at i) begins, and a map char -> the index where that char was seen previously (-1 if not seen). To advance to i+1: let c = str[i+1] and m = map[c], where we saw c last. If m is before the current start, start stays put. Otherwise move start to m+1: if c was seen after the current start, jump start to just after that previous occurrence. Record the char's new position and track the max length i - start + 1 along the way.

```python
seen = {}                       # char -> last index, default -1
start = 0
best = 0
for i, c in enumerate(s):
    if seen[c] + 1 > start:
        start = seen[c] + 1     # jump past previous occurrence
    seen[c] = i
    best = max(best, i - start + 1)
return best
```

**Complexity** — time O(n); space O(1) for a fixed alphabet (O(k) in general)

Full Python solution: [`LeetCodeCheat/longest-substring-without-repeating-characters.py`](../../python/leetcode/LeetCodeCheat/longest-substring-without-repeating-characters.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/003-longest-substring.yaml`.
