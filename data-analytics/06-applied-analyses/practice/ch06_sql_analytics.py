# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "matplotlib", "duckdb"]
# ///
"""Chapter 6: is revenue growth coming from new customers or returning ones? Answered in SQL.

Run from this folder with: uv run ch06_sql_analytics.py
"""
import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import chartstyle as cs
from retail import load_customers, load_events, load_orders, load_sessions

cs.apply()

# %% setup
con = duckdb.connect()
customers, orders, sessions, events = load_customers(), load_orders(), load_sessions(), load_events()
# A refunds table with several lines per refunded order, for the fan-out example.
rng = np.random.default_rng(7)
refunded = orders.sample(frac=.08, random_state=7)
refunds = refunded.loc[refunded.index.repeat(rng.integers(1, 4, len(refunded)))][["order_id", "value"]]
refunds["amount"] = (refunds.pop("value") * .3).round(2)
for name, frame in {"customers": customers, "orders": orders, "sessions": sessions, "events": events, "refunds": refunds}.items():
    con.register(name, frame)
print(con.sql("SELECT count(*) AS orders, round(sum(value)) AS revenue, min(order_date)::DATE AS first, max(order_date)::DATE AS last FROM orders").df().to_string(index=False))

# %% bridge
BRIDGE = """
WITH monthly AS (                     -- one row per customer per month with an order
    SELECT customer_id,
           date_trunc('month', order_date) AS month,
           sum(value) AS revenue
    FROM orders
    GROUP BY 1, 2
),
history AS (                          -- the customer's previous active month
    SELECT *,
           lag(month) OVER (PARTITION BY customer_id ORDER BY month) AS previous_month
    FROM monthly
),
labelled AS (
    SELECT *,
           CASE WHEN previous_month IS NULL THEN 'new'
                WHEN date_diff('month', previous_month, month) <= 3 THEN 'returning'
                ELSE 'reactivated'
           END AS kind
    FROM history
)
SELECT date_trunc('quarter', month) AS quarter, kind,
       round(sum(revenue)) AS revenue,
       count(*) AS customer_months
FROM labelled
GROUP BY 1, 2
ORDER BY 1, 2
"""
bridge = con.sql(BRIDGE).df()
pivot = bridge.pivot(index="quarter", columns="kind", values="revenue")[["new", "returning", "reactivated"]]
pivot.index = pd.PeriodIndex(pivot.index, freq="Q")
print(pivot.iloc[-8:].astype(int).to_string())
yearly = pivot.groupby(pivot.index.year).sum().astype(int)
print(yearly.assign(total=yearly.sum(axis=1)).to_string())

# %% chart_bridge
fig, ax = plt.subplots()
x = np.arange(len(pivot))
bottom = np.zeros(len(pivot))
colours = {"new": cs.BLUE, "returning": cs.ORANGE, "reactivated": cs.AQUA}
for kind, colour in colours.items():
    ax.bar(x, pivot[kind] / 1000, bottom=bottom, color=colour, label=kind.capitalize(), width=.82,
           edgecolor=cs.SURFACE, linewidth=1)
    bottom += pivot[kind].to_numpy() / 1000
ax.set_xticks(x, [str(q).replace("Q", " Q") if q.quarter == 1 else f"Q{q.quarter}" for q in pivot.index], fontsize=8)
ax.set_ylabel("Revenue per quarter (£ thousand)")
ax.set_title("Growth in 2025 came from new customers, and returning revenue shrank")
ax.legend(loc="upper left", ncols=3)
cs.save(fig, "applied-sql-revenue-bridge.png")

# %% validate
in_pandas = orders.assign(month=orders.order_date.dt.to_period("M")).groupby(["customer_id", "month"]).value.sum().reset_index()
in_pandas["previous"] = in_pandas.groupby("customer_id").month.shift()
gap = (in_pandas.month.dt.year - in_pandas.previous.dt.year) * 12 + in_pandas.month.dt.month - in_pandas.previous.dt.month
in_pandas["kind"] = np.select([in_pandas.previous.isna(), gap <= 3], ["new", "returning"], "reactivated")
check = in_pandas.groupby("kind").value.sum().round()
in_sql = con.sql(BRIDGE).df().groupby("kind").revenue.sum()
print(pd.DataFrame({"pandas": check, "sql": in_sql, "diff": (check - in_sql).round()}).to_string())
print("revenue in orders:", round(orders.value.sum()), " sum of bridge:", round(in_sql.sum()))

# %% running
print(con.sql("""
WITH monthly AS (
    SELECT date_trunc('month', order_date)::DATE AS month, round(sum(value)) AS revenue
    FROM orders GROUP BY 1
)
SELECT month, revenue,
       sum(revenue) OVER (PARTITION BY year(month) ORDER BY month) AS ytd,
       round(avg(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)) AS avg_3m,
       round(100 * (revenue / lag(revenue, 12) OVER (ORDER BY month) - 1), 1) AS yoy_pct
FROM monthly
ORDER BY month DESC
LIMIT 4
""").df().to_string(index=False))

# %% topn
print(con.sql("""
SELECT year(order_date) AS year, customer_id, round(sum(value)) AS spend,
       rank() OVER (PARTITION BY year(order_date) ORDER BY sum(value) DESC) AS place
FROM orders
GROUP BY 1, 2
QUALIFY place <= 2
ORDER BY year, place
""").df().to_string(index=False))

# %% spine
print(con.sql("""
WITH weeks AS (                                  -- every week, whether or not anything sold
    SELECT unnest(generate_series(DATE '2023-01-02', DATE '2023-02-20', INTERVAL 7 DAY))::DATE AS week
),
sold AS (
    SELECT date_trunc('week', order_date)::DATE AS week, count(*) AS n
    FROM orders
    WHERE category = 'furniture' AND value > 120
    GROUP BY 1
)
SELECT w.week, coalesce(s.n, 0) AS big_furniture_orders
FROM weeks w LEFT JOIN sold s USING (week)
ORDER BY w.week
""").df().to_string(index=False))

# %% sessionise
SESSIONISE = """
WITH gaps AS (
    SELECT *, ts - lag(ts) OVER (PARTITION BY user_id ORDER BY ts) AS gap
    FROM events
),
starts AS (
    SELECT *, CASE WHEN gap IS NULL OR gap > INTERVAL 30 MINUTE THEN 1 ELSE 0 END AS is_start
    FROM gaps
)
SELECT user_id, ts, true_session,
       sum(is_start) OVER (PARTITION BY user_id ORDER BY ts) AS session_number
FROM starts
"""
print(con.sql(f"""
SELECT count(*) AS page_views,
       count(DISTINCT (user_id, session_number)) AS sessions_found,
       count(DISTINCT true_session) AS sessions_true
FROM ({SESSIONISE})
""").df().to_string(index=False))
print(con.sql(f"""
SELECT count(*) AS sessions_split_or_merged FROM (
    SELECT user_id, session_number FROM ({SESSIONISE})
    GROUP BY 1, 2 HAVING count(DISTINCT true_session) <> 1
)
""").df().to_string(index=False))

# %% islands
print(con.sql("""
WITH active AS (
    SELECT DISTINCT customer_id, date_trunc('month', order_date)::DATE AS month FROM orders
),
numbered AS (
    SELECT *,
           (year(month) * 12 + month(month))
             - row_number() OVER (PARTITION BY customer_id ORDER BY month) AS island
    FROM active
),
streaks AS (
    SELECT customer_id, island, count(*) AS months, min(month) AS started
    FROM numbered GROUP BY 1, 2
)
SELECT months AS streak_length, count(*) AS streaks
FROM streaks GROUP BY 1 ORDER BY 1 LIMIT 6
""").df().to_string(index=False))

# %% funnel
print(con.sql("""
SELECT device,
       count(*) AS sessions,
       count(*) FILTER (furthest >= 3) AS at_checkout,
       count(*) FILTER (furthest >= 4) AS reached_payment,
       round(100.0 * count(*) FILTER (furthest >= 4) / count(*) FILTER (furthest >= 3), 1) AS checkout_to_payment_pct,
       round(100.0 * avg((furthest = 5)::INT), 2) AS conversion_pct
FROM sessions
WHERE date >= DATE '2025-09-15'
GROUP BY device ORDER BY device
""").df().to_string(index=False))

# %% fanout
print(con.sql("""
SELECT round(sum(o.value)) AS revenue_wrong, round(sum(r.amount)) AS refunds
FROM orders o LEFT JOIN refunds r USING (order_id)
""").df().to_string(index=False))
print(con.sql("""
WITH per_order AS (SELECT order_id, sum(amount) AS amount FROM refunds GROUP BY 1)
SELECT round(sum(o.value)) AS revenue_right, round(sum(p.amount)) AS refunds
FROM orders o LEFT JOIN per_order p USING (order_id)
""").df().to_string(index=False))
print("true revenue", round(orders.value.sum()))
