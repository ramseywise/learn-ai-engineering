---
title: "LC 121 — Best Time to Buy and Sell Stock"
track: coding
topic: algorithms
difficulty: easy
timebox_min: 15
concepts: [dynamic-programming]
source: https://leetcode.com/problems/best-time-to-buy-and-sell-stock/
---
## Prompt

Given an array `prices` where `prices[i]` is a stock's price on day `i`, choose one
day to buy and a later day to sell to maximize profit. Return the maximum profit, or
`0` if no profitable transaction exists. Example: `prices = [7,1,5,3,6,4]` -> `5`
(buy at `1`, sell at `6`).

## Starter

Blank file in `programming/drills/coding/scratch/`. Write the signature first, then say it out loud.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Only one buy and one sell are allowed, and the buy must happen before the sell.

</details>

<details><summary>Hint 2</summary>

Track the minimum price seen so far as you scan left to right. It's always the best possible buy point for the current day's sell.

</details>

<details><summary>Hint 3</summary>

A single linear pass keeping the running minimum and best profit so far solves it in O(n) time and O(1) space.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

One buy and one sell, and the buy must come before the sell. Sweep left to right tracking the minimum price seen so far. The best profit ending on any given day is that day's price minus the running minimum. Keep the maximum such profit over all days.

```python
min_price = prices[0]; best = 0
for p in prices[1:]:
    if p < min_price: min_price = p
    else: best = max(best, p - min_price)
return best
```

**Complexity** — time O(n); space O(1)

Full Python solution: `LeetCodeCheat/best-time-to-buy-and-sell-stock.py` (local only — `programming/drills/python/leetcode/` is a gitignored nested repo).

</details>

## Notes

Follow-ups an interviewer may push on:

- Allow unlimited transactions (LeetCode 122).
- Cap the number of transactions at two (LeetCode 123).
- Add a transaction fee or a cooldown - how does the DP change?

Sources:

- [LeetCode - Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/121-best-time-to-buy-and-sell-stock.yaml`.
