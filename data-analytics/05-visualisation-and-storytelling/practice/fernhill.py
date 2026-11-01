"""Fernhill Home: a fictional online homewares shop, used by every chapter in this pillar.

Every number here is synthetic and seeded. The planted story: in January 2025
the email budget was cut from 14k to 4k a month and the money moved to paid
social. Revenue kept growing. The share of new customers who buy again within
90 days fell. Nothing reads files, so a chart can never go stale against a CSV.
"""
import numpy as np
import pandas as pd

CHANNELS = ["paid_social", "organic", "email", "referral"]
LABELS = {"paid_social": "Paid social", "organic": "Organic search",
          "email": "Email", "referral": "Referral"}
CUT = pd.Timestamp("2025-01-01")  # the month the email budget changed
MONTHS = pd.date_range("2023-01-01", "2025-12-01", freq="MS")
SEASON = np.array([.86, .82, .90, .94, .97, .95, .90, .92, .98, 1.05, 1.42, 1.29])


def load_monthly(seed=42):
    """One row per month and channel: sessions, orders, revenue, spend."""
    rng = np.random.default_rng(seed)
    rows = []
    for i, month in enumerate(MONTHS):
        after = month >= CUT
        season = SEASON[month.month - 1]
        spec = {
            "paid_social": (60_000 * (2.6 if after else 1 + i * .010), .018, 62,
                            48_000 if after else 26_000),
            "organic": (95_000 * (1 + i * .007), .026, 74, 0),
            "email": (34_000 * (.48 if after else 1 + i * .004), .046, 81,
                      4_000 if after else 14_000),
            "referral": (18_000 * (1 + i * .004), .031, 70, 0),
        }
        for channel, (base, conversion, basket, spend) in spec.items():
            sessions = int(base * season * rng.normal(1, .025))
            orders = int(rng.binomial(sessions, conversion))
            revenue = round(orders * basket * rng.normal(1, .015))
            rows.append((month, channel, sessions, orders, revenue, spend))
    return pd.DataFrame(rows, columns=["month", "channel", "sessions", "orders",
                                       "revenue", "spend"])


def load_repeat(seed=43):
    """New customers per month and channel, and how many bought again within 90 days."""
    rng = np.random.default_rng(seed)
    base_rate = {"paid_social": .24, "organic": .37, "email": .49, "referral": .36}
    drop = {"paid_social": .05, "organic": .08, "email": .10, "referral": .08}
    orders = load_monthly()
    rows = []
    for row in orders.itertuples():
        new_customers = int(row.orders * .72)
        p = base_rate[row.channel] - (drop[row.channel] if row.month >= CUT else 0)
        rows.append((row.month, row.channel, new_customers,
                     int(rng.binomial(new_customers, p))))
    return pd.DataFrame(rows, columns=["month", "channel", "new_customers", "repeat_90d"])


def load_orders(n=4_000, seed=44):
    """Order lines for looking at distributions: value by category and device."""
    rng = np.random.default_rng(seed)
    medians = {"Kitchen": 38, "Textiles": 46, "Lighting": 72, "Garden": 58, "Furniture": 165}
    category = rng.choice(list(medians), n, p=[.34, .26, .16, .14, .10])
    device = rng.choice(["mobile", "desktop"], n, p=[.64, .36])
    uplift = np.where(device == "desktop", 1.18, 1.0)
    median = np.array([medians[c] for c in category])
    value = np.round(median * uplift * rng.lognormal(0, .55, n), 2)
    return pd.DataFrame({"category": category, "device": device, "value": value})


def total_by_month():
    """Whole-shop revenue and 90-day repeat rate by month, the two lines of the story."""
    revenue = load_monthly().groupby("month")["revenue"].sum()
    repeat = load_repeat().groupby("month")[["new_customers", "repeat_90d"]].sum()
    return pd.DataFrame({"revenue": revenue,
                         "repeat_rate": repeat["repeat_90d"] / repeat["new_customers"]})
