---
title: "LC 10 — Regular Expression Matching"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [dynamic-programming]
source: https://leetcode.com/problems/regular-expression-matching/
---
## Prompt

Given an input string `s` and a pattern `p`, return whether `p` matches the entire
string `s`. In the pattern, `.` matches any single character and `*` matches zero or
more of the element immediately preceding it. The match must cover all of `s`, not
just a prefix. Example: `s = "aa"`, `p = "a*"` -> `true`; `s = "ab"`, `p = ".*"` ->
`true`; `s = "mississippi"`, `p = "mis*is*p*."` -> `false`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Solve match(s, p) recursively, treating '.' as any single character and '*' as zero-or-more copies of the element before it.

</details>

<details><summary>Hint 2</summary>

When the regex's second character is '*', branch into two cases: skip the starred element entirely (zero occurrences), or consume one matching character from s and retry with the same regex (one-or-more).

</details>

<details><summary>Hint 3</summary>

Plain recursion is exponential in the worst case. Memoizing on the (s, p) positions brings it down to an O(n*m) DP.

</details>

## Solution

<details><summary>Reference approach</summary>

Solve it with recursion on match(s, p), where '.' matches any single character and '*' matches zero or more of the preceding element. If both s and p are empty, return true. If s is empty but p isn't, it only matches when the next regex element is starred (skip it: match("", p[2:])). When the second regex char is '*' the current element is optional, so handle the '.' case and the specific-char case: consume as many matching characters from s as possible and try continuing with p[2:], and also try the zero-match branch. Otherwise, if the first characters match ('.' or equal), recurse on match(s[1:], p[1:]). Otherwise return false.

```python
match(s, p):
    if p empty:                return s empty
    if s empty:
        return len(p) >= 2 and p[1]=='*' and match(s, p[2:])
    starred = len(p) > 1 and p[1] == '*'
    if starred:
        # zero occurrences
        if match(s, p[2:]): return true
        # one-or-more: first char must match
        if p[0]=='.' or p[0]==s[0]:
            return match(s[1:], p)
        return false
    if p[0]=='.' or p[0]==s[0]:
        return match(s[1:], p[1:])
    return false
```

**Complexity** — time exponential without memoization (O(n*m) with a DP table); space O(n + m) recursion (O(n*m) memoized)

Full Python solution: [`LeetCodeCheat/regular-expression-matching.py`](../../python/leetcode/LeetCodeCheat/regular-expression-matching.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Sources:

- [LeetCode — Regular Expression Matching](https://leetcode.com/problems/regular-expression-matching/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/010-regular-expression-matching.yaml`.
