"""Fernhill Home, a fictional online homewares retailer: the seeded data behind this pillar.

Same plot as the visualisation pillar: email budget cut in January 2025, paid social scaled
to 2.6 times its old size. This generator is new and works at customer level, so its totals
are not calibrated to the pillar 05 charts. Nothing is read from disk, and every call with
the default seed returns the same rows.
"""
from functools import lru_cache

import numpy as np
import pandas as pd

SEED = 20250101
CUT = pd.Timestamp("2025-01-01")          # email budget cut
REDESIGN = pd.Timestamp("2025-09-15")     # new mobile checkout page ships
END = pd.Timestamp("2025-12-31")
CHANNELS = ["paid_social", "organic", "email", "referral"]
STEPS = ["visit", "product", "basket", "checkout", "payment", "purchase"]

# Customers acquired per month, before and after the cut.
ACQ_BEFORE = {"paid_social": 180, "organic": 260, "email": 120, "referral": 100}
ACQ_AFTER = {"paid_social": 468, "organic": 260, "email": 40, "referral": 100}
ORDERS_PER_MONTH = {"paid_social": .10, "organic": .22, "email": .35, "referral": .20}
# Monthly churn varies across customers: Beta(a, b), means .25, .12, .08, .12.
CHURN_BETA = {"paid_social": (1.0, 3.0), "organic": (.9, 6.6), "email": (.8, 9.2), "referral": (.9, 6.6)}


@lru_cache(maxsize=1)
def _customers_and_orders(seed=SEED):
    rng = np.random.default_rng(seed)
    rows = []
    for month in pd.date_range("2023-01-01", "2025-12-01", freq="MS"):
        plan = ACQ_AFTER if month >= CUT else ACQ_BEFORE
        for channel in CHANNELS:
            n = rng.poisson(plan[channel])
            days = rng.integers(0, month.days_in_month, n)
            rows.append(pd.DataFrame({"acquired": month + pd.to_timedelta(days, "D"), "channel": channel}))
    customers = pd.concat(rows, ignore_index=True).sort_values("acquired", ignore_index=True)
    customers.insert(0, "customer_id", np.arange(1, len(customers) + 1))

    n = len(customers)
    a = customers["channel"].map(lambda c: CHURN_BETA[c][0]).to_numpy()
    b = customers["channel"].map(lambda c: CHURN_BETA[c][1]).to_numpy()
    churn = rng.beta(a, b)
    # Ground truth a real non-contractual retailer never sees: months until the customer lapses.
    lifetime = rng.geometric(np.clip(churn, 1e-4, 1))
    customers["true_lifetime_months"] = lifetime
    base = customers["channel"].map(ORDERS_PER_MONTH).to_numpy()
    rate = rng.gamma(.7, base / .7)                     # long-tailed order rate, mean = base
    spend = rng.lognormal(0, .35, n)                    # some customers always spend more

    repeats = rng.poisson(rate * lifetime)
    idx = np.repeat(np.arange(n), repeats)
    acquired = customers["acquired"].to_numpy()
    offset = rng.uniform(0, 1, len(idx)) * lifetime[idx] * 30.44
    when = acquired[idx] + pd.to_timedelta(np.round(offset), "D").to_numpy()
    first = pd.DataFrame({"i": np.arange(n), "order_date": acquired})
    later = pd.DataFrame({"i": idx, "order_date": when})
    # The cut removes the reminder that drove repeat orders, for everyone and most for email customers.
    after = later["order_date"] >= CUT
    keep = np.where(customers["channel"].to_numpy()[later["i"]] == "email", .65, .70)
    later = later[~after | (rng.uniform(size=len(later)) < keep)]
    orders = pd.concat([first, later], ignore_index=True)
    orders = orders[orders["order_date"] <= END]
    orders["customer_id"] = orders["i"] + 1
    orders["value"] = np.round(rng.lognormal(np.log(42), .55, len(orders)) * spend[orders["i"]], 2)
    orders["category"] = rng.choice(["kitchen", "textiles", "lighting", "furniture"], len(orders), p=[.4, .3, .2, .1])
    orders = orders.sort_values(["order_date", "customer_id"], ignore_index=True)
    orders.insert(0, "order_id", np.arange(1, len(orders) + 1))
    return customers, orders[["order_id", "customer_id", "order_date", "value", "category"]]


def load_customers(seed=SEED):
    """One row per customer: id, acquisition date and channel, and the true lifetime."""
    return _customers_and_orders(seed)[0].copy()


def load_orders(seed=SEED):
    """One row per order, from January 2023 to December 2025."""
    return _customers_and_orders(seed)[1].copy()


@lru_cache(maxsize=1)
def _weekly(seed=SEED):
    rng = np.random.default_rng(seed + 1)
    weeks = pd.date_range("2021-01-04", "2025-12-29", freq="W-MON")
    t = np.arange(len(weeks))
    level = 1800 + 3.6 * t
    doy = weeks.dayofyear.to_numpy()
    season = 1 + .16 * np.cos(2 * np.pi * (doy - 340) / 365.25) + .04 * np.cos(4 * np.pi * (doy - 100) / 365.25)
    y = level * season
    for i, week in enumerate(weeks):
        # Black Friday moves: the day after the fourth Thursday of November.
        nov1 = pd.Timestamp(week.year, 11, 1)
        black_friday = nov1 + pd.Timedelta(days=(3 - nov1.dayofweek) % 7 + 22)
        if week <= black_friday < week + pd.Timedelta(days=7):
            y[i] *= 1.45
        days_to_xmas = (pd.Timestamp(week.year, 12, 25) - week).days
        if 0 <= days_to_xmas < 7:
            y[i] *= .95
        elif 7 <= days_to_xmas < 28:
            y[i] *= 1.28
    noise = np.zeros(len(t))
    for i in range(1, len(t)):
        noise[i] = .45 * noise[i - 1] + rng.normal(0, .045)
    y = y * np.exp(noise)
    y[weeks.get_loc(pd.Timestamp("2023-06-12"))] *= .45     # one-week warehouse outage
    return pd.Series(np.round(y).astype(int), index=pd.DatetimeIndex(weeks, name="week"), name="units")


def load_weekly_units(seed=SEED):
    """Units shipped per week, Mondays from January 2021 to December 2025."""
    return _weekly(seed).copy()


@lru_cache(maxsize=1)
def _sessions(seed=SEED):
    rng = np.random.default_rng(seed + 2)
    days = pd.date_range("2025-03-01", END, freq="D")
    frames = []
    for day in days:
        traffic = 1500 * (1.25 if day.month >= 11 else 1) * (1.1 if day.dayofweek >= 5 else 1)
        n = rng.poisson(traffic)
        position = (day - days[0]).days / (len(days) - 1)
        mobile = rng.uniform(size=n) < .58 + .08 * position
        # Autumn gift shopping lifts intent upstream of payment, on every device.
        intent = 1 + .16 * np.clip((day - pd.Timestamp("2025-09-01")).days / 30, 0, 1)
        pay_mobile = .68 if day >= REDESIGN else .82
        probs = np.where(mobile[:, None],
                         [.55, .22 * intent, .62, pay_mobile, .93],
                         [.62, .30 * intent, .68, .84, .95])
        passed = rng.uniform(size=(n, 5)) < probs
        frames.append(pd.DataFrame({
            "date": day,
            "device": np.where(mobile, "mobile", "desktop"),
            "channel": rng.choice(CHANNELS, n, p=[.40, .33, .12, .15]),
            "furthest": np.cumprod(passed, axis=1).sum(axis=1),
        }))
    sessions = pd.concat(frames, ignore_index=True)
    sessions.insert(0, "session_id", np.arange(1, len(sessions) + 1))
    n_users = int(len(sessions) / 1.6)
    sessions.insert(1, "user_id", rng.integers(1, n_users + 1, len(sessions)))
    return sessions


def load_sessions(seed=SEED):
    """One row per web session, March to December 2025.

    `furthest` is the last step reached, as an index into STEPS (0 visit, 5 purchase).
    """
    return _sessions(seed).copy()


def load_events(n_users=2000, seed=SEED):
    """Timestamped page views with a known session count, for testing sessionisation.

    Page views inside a session are under 30 minutes apart and sessions are over 30 minutes
    apart, so `true_session` is what a correct 30-minute rule must recover.
    """
    rng = np.random.default_rng(seed + 3)
    rows, session_id = [], 0
    start = pd.Timestamp("2025-11-01")
    for user in range(1, n_users + 1):
        clock = start + pd.Timedelta(minutes=float(rng.uniform(0, 20000)))
        for _ in range(1 + rng.poisson(2)):
            session_id += 1
            for _ in range(1 + rng.poisson(4)):
                rows.append((user, clock, session_id))
                clock += pd.Timedelta(minutes=float(min(rng.exponential(3), 29)))
            clock += pd.Timedelta(minutes=float(31 + rng.exponential(1500)))
    return pd.DataFrame(rows, columns=["user_id", "ts", "true_session"])


if __name__ == "__main__":
    print(len(load_customers()), "customers,", len(load_orders()), "orders,", len(load_sessions()), "sessions")
    print(load_weekly_units().describe().round(0).to_string())
