---
title: "LC 347 — Top K Frequent Elements"
track: coding
topic: algorithms
difficulty: medium
timebox_min: 25
concepts: [arrays-hashing]
source: https://leetcode.com/problems/top-k-frequent-elements/
---
## Prompt

Given an integer array `nums` and an integer `k`, return the `k` most frequently
occurring elements. The answer may be returned in any order and is guaranteed to
be unique. Example: `nums = [1,1,1,2,2,3]`, `k = 2` -> `[1,2]`.

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Frequencies only range from 1 to n, which suggests indexing by count instead of sorting elements.

</details>

<details><summary>Hint 2</summary>

Bucket each element by its frequency into an array indexed by count, then read the buckets off from the highest frequency downward.

</details>

<details><summary>Hint 3</summary>

Collecting elements until you have k gives O(n) overall time, beating a full sort or heap.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Count occurrences in a hash map, then bucket elements by frequency into an array indexed by count (the maximum possible count is n). Walk the buckets from highest frequency down, collecting elements until k are gathered - linear time, avoiding a full sort or a heap.

```python
count = frequency map of nums
buckets[f] = list of elements whose frequency is f   # index 0..n
result = []
for f from n down to 1:
    for el in buckets[f]:
        result.append(el)
        if len(result) == k: return result
```

**Complexity** — time O(n); space O(n)

Full Python solution: `LeetCodeCheat/top-k-frequent-elements.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Use a size-k heap for O(n log k) with less memory.
- Break ties deterministically among elements of equal frequency.
- Apply the same bucket idea to sort characters by frequency (LeetCode 451).

Sources:

- [LeetCode - Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/347-top-k-frequent-elements.yaml`.
