---
title: Top orders per user, with a running total
track: sql
topic: window-functions
difficulty: medium
timebox_min: 20
concepts: [window-functions, partitioning, ranking]
source: original
units: [programming/sql, data-analytics/06-applied-analyses/notes/06-sql-for-analytics.md]
---

## Prompt

`orders(order_id, user_id, ordered_at, amount)`. For each user, return their **two largest
orders by amount**, and for each returned row the user's **running total of spend up to and
including that order** (by date, then `order_id`). Ties on amount both count as the same
rank, so a user can get more than two rows. Sort by user, then rank, then date.

Ask before you write: what happens with ties? Is the running total over all orders or only
the returned ones? (All orders: filter after the window, not before.)

## Starter

Seed schema: [`top-orders-per-user.sql`](top-orders-per-user.sql).

```bash
sqlite3 :memory: '.read top-orders-per-user.sql' '<your query>'
```

## Tests

Expected output:

| user_id | order_id | ordered_at | amount | amount_rank | running_total |
|---|---|---|---|---|---|
| 1 | 4 | 2026-02-14 | 90 | 1 | 185 |
| 1 | 1 | 2026-01-03 | 40 | 2 | 40 |
| 1 | 3 | 2026-02-01 | 40 | 2 | 95 |
| 2 | 5 | 2026-01-05 | 20 | 1 | 20 |
| 2 | 6 | 2026-03-01 | 20 | 1 | 40 |
| 3 | 7 | 2026-01-20 | 70 | 1 | 70 |
| 3 | 9 | 2026-02-02 | 55 | 2 | 135 |

<details>
<summary>Solution</summary>

```sql
WITH ranked AS (
  SELECT
    user_id, order_id, ordered_at, amount,
    DENSE_RANK() OVER (PARTITION BY user_id ORDER BY amount DESC) AS amount_rank,
    SUM(amount) OVER (
      PARTITION BY user_id ORDER BY ordered_at, order_id
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
  FROM orders
)
SELECT user_id, order_id, ordered_at, amount, amount_rank, running_total
FROM ranked
WHERE amount_rank <= 2
ORDER BY user_id, amount_rank, ordered_at;
```

</details>

## Notes

- **Window functions can't go in `WHERE`** — they run after it. Rank in a CTE, filter outside.
- **`ROW_NUMBER` vs `RANK` vs `DENSE_RANK`**: user 2's tie is the whole question. `ROW_NUMBER`
  drops one tied row; `RANK` would skip rank 2 after a tie; `DENSE_RANK` doesn't.
- **Frame clause**: with `ORDER BY` and no frame, the default is `RANGE ... CURRENT ROW`,
  which lumps rows with the same `ordered_at` together. `ROWS` plus a tiebreaker makes the
  total deterministic.
- **Follow-ups**: top N as a parameter; percent of user total (`amount / SUM(amount) OVER
  (PARTITION BY user_id)`); gap since the previous order (`LAG(ordered_at)`).
