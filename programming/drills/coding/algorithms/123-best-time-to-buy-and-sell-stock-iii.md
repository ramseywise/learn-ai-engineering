---
title: "LC 123 — Best Time to Buy and Sell Stock III"
track: coding
topic: algorithms
difficulty: hard
timebox_min: 40
concepts: [dynamic-programming]
source: https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/
---
## Prompt

Given an array `prices` where `prices[i]` is a stock's price on day `i`, find the
maximum profit achievable with at most two transactions. You must sell before buying
again (no overlapping trades). Return the best total profit, or `0` if none is
positive. Example: `prices = [3,3,5,0,0,3,1,4]` -> `6`.

## Starter

Blank file in `drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

With at most two transactions, think about splitting the timeline into an independent left part and right part.

</details>

<details><summary>Hint 2</summary>

For every possible split point, solve the single-transaction problem on each side and combine the two profits.

</details>

<details><summary>Hint 3</summary>

This gives O(n^2) directly, and is refinable to O(n) by precomputing best-profit-so-far arrays from both ends.

</details>

## Solution

<details><summary>Reference approach</summary>

At most two transactions. Split the timeline at every index into a left and a right part, then solve the single-transaction problem (problem 121) independently on each side. Take the split that maximizes the sum of the two best profits. This split approach costs O(n^2), but an O(n) DP refines it by tracking four running states for the two buys and two sells.

```python
best121(a, lo, hi): one-pass max single-transaction profit within a[lo:hi]
answer = best121(prices, 0, n)
for i in 2..n-1:
    answer = max(answer, best121(prices, 0, i) + best121(prices, i, n))
return answer
```

**Complexity** — time O(n^2); space O(1)

Full Python solution: [`LeetCodeCheat/best-time-to-buy-and-sell-stock-iii.py`](../../python/leetcode/LeetCodeCheat/best-time-to-buy-and-sell-stock-iii.py) (local only — `drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Reduce to O(n) using precomputed left[i] and right[i] best-profit arrays.
- Generalize to at most k transactions (LeetCode 188).
- Track the four-state DP: buy1, sell1, buy2, sell2.

Sources:

- [LeetCode - Best Time to Buy and Sell Stock III](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/123-best-time-to-buy-and-sell-stock-iii.yaml`.
