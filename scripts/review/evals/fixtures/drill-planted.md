---
title: Latest order per customer
track: sql
topic: window-functions
difficulty: easy
timebox_min: 15
concepts: [window-functions]
source: original
units: [programming/python]
---

## Prompt

`orders(order_id, customer_id, ordered_at)`. Return each customer's most recent order, sorted by customer.

## Starter

```sql
CREATE TABLE orders (order_id INTEGER, customer_id INTEGER, ordered_at TEXT);
INSERT INTO orders VALUES (1, 1, '2026-01-01'), (2, 1, '2026-03-01'), (3, 2, '2026-02-01'), (4, 3, '2026-01-15');
```

## Tests

Expected output:

| customer_id | order_id |
|---|---|
| 1 | 1 |
| 2 | 3 |
| 3 | 4 |

## Solution

```sql
SELECT customer_id, order_id
FROM (
  SELECT customer_id, order_id,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered_at DESC) AS rn
  FROM orders
)
WHERE rn = 1
ORDER BY customer_id;
```

## Notes

`ROW_NUMBER` picks one row per customer even when two orders share a date.
