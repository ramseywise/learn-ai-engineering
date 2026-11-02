# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas"]
# ///
"""Chapter 11: which number should Fernhill run on, what feeds it, and what would catch it being gamed?

Run from this folder with: uv run ch11_metric_trees.py
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from retail import CHANNELS, load_customers, load_fulfilment, load_marketing_weekly, load_orders, load_sessions

pd.set_option("display.width", 130)

# %% load
orders, customers, marketing = load_orders(), load_customers(), load_marketing_weekly()
orders["year"] = orders.order_date.dt.year
print(len(orders), "orders;", len(customers), "customers;", orders.order_date.min().date(), "to", orders.order_date.max().date())


# %% tree
def tree(frame):
    """The three leaves of the revenue identity, plus the revenue they multiply to."""
    active = frame.customer_id.nunique()
    n_orders = len(frame)
    revenue = frame.value.sum()
    return pd.Series({"revenue": revenue, "active": active, "per_customer": n_orders / active,
                      "per_order": revenue / n_orders})


years = orders.groupby("year")[["customer_id", "value"]].apply(tree)
years["rebuilt"] = years.active * years.per_customer * years.per_order
print(years.round(2).to_string())
assert np.allclose(years.revenue, years.rebuilt), "the leaves must multiply back to the ledger"


# %% attribute
def attribute(before, after, leaves=("active", "per_customer", "per_order")):
    """Split a change in a product among its factors with log-mean weights, which leaves no residual."""
    weight = (after.revenue - before.revenue) / np.log(after.revenue / before.revenue)
    return pd.Series({leaf: weight * np.log(after[leaf] / before[leaf]) for leaf in leaves})


change = attribute(years.loc[2024], years.loc[2025])
print(change.round(0).to_string())
print("sum of the parts", round(change.sum()), "; change in revenue", round(years.revenue[2025] - years.revenue[2024]))

# %% naive_order
naive = years.loc[2024].copy()
naive["active"] = years.active[2025]
print("revenue if the extra customers had kept 2024's frequency:", round(naive.active * naive.per_customer * naive.per_order))

# %% north_star
orders = orders.sort_values("order_date")


def repeat_customers(frame, end, days=365):
    """Customers with two or more orders in the `days` to `end`."""
    window = frame[(frame.order_date > end - pd.Timedelta(days=days)) & (frame.order_date <= end)]
    return int((window.groupby("customer_id").size() >= 2).sum())


ends = pd.to_datetime(["2023-12-31", "2024-06-30", "2024-12-31", "2025-06-30", "2025-12-31"])
star = pd.DataFrame({"repeat_customers": [repeat_customers(orders, end) for end in ends],
                     "revenue_12m": [orders[(orders.order_date > end - pd.Timedelta(days=365))
                                            & (orders.order_date <= end)].value.sum() for end in ends]}, index=ends.date)
star["active_12m"] = [orders[(orders.order_date > end - pd.Timedelta(days=365))
                             & (orders.order_date <= end)].customer_id.nunique() for end in ends]
star["share_repeating"] = star.repeat_customers / star.active_12m
print(star.round(3).to_string())

# %% new_and_returning
first_order = orders.groupby("customer_id").order_date.min().rename("first_order")
orders = orders.join(first_order, on="customer_id")
orders["acquired_year"] = orders.first_order.dt.year
split = orders.assign(kind=np.where(orders.acquired_year == orders.year, "new", "returning"))
split = split.groupby(["year", "kind"]).agg(revenue=("value", "sum"), customers=("customer_id", "nunique"),
                                            orders=("value", "size"))
split["revenue_per_customer"] = split.revenue / split.customers
print(split.round(2).to_string())

# %% counter
customers = customers.join(first_order, on="customer_id")
ordered = orders[orders.order_date > orders.first_order].groupby("customer_id").order_date.min().rename("second_order")
customers = customers.join(ordered, on="customer_id")
customers["gap"] = (customers.second_order - customers.first_order).dt.days
LAST = orders.order_date.max()


def card(year):
    """New customers per channel in a year, with the two numbers that would catch a bad gain."""
    spend = marketing[marketing.week.dt.year == year][[f"spend_{c}" for c in CHANNELS]].sum()
    joined = customers[customers.first_order.dt.year == year]
    mature = joined[joined.first_order <= LAST - pd.Timedelta(days=90)]
    out = pd.DataFrame({"new": joined.groupby("channel").size(),
                        "repeat_90d": mature.groupby("channel").gap.apply(lambda g: (g <= 90).mean())})
    out["spend"] = [spend[f"spend_{c}"] for c in out.index]
    out["cost_per_new"] = out.spend / out.new
    out["cost_per_repeater"] = out.cost_per_new / out.repeat_90d
    return out.loc[CHANNELS]


cards = {year: card(year) for year in (2024, 2025)}
for year, table in cards.items():
    print(year, f"new {table.new.sum():,}, spend £{table.spend.sum():,.0f}, "
          f"all-channel cost per new £{table.spend.sum() / table.new.sum():.2f}, "
          f"cost per repeater £{table.spend.sum() / (table.new * table.repeat_90d).sum():.2f}")
    print(table.round(3).to_string())
extra = cards[2025].loc["paid_social"] - cards[2024].loc["paid_social"]
print("marginal paid social cost per extra customer:", round(extra.spend / extra.new, 2))

# %% scoreboard
scoreboard = pd.DataFrame({year: {"revenue": years.revenue[year],
                                  "marketing spend": cards[year].spend.sum(),
                                  "revenue less marketing": years.revenue[year] - cards[year].spend.sum()}
                           for year in (2024, 2025)})
scoreboard.loc["repeat customers, 31 December"] = [star.repeat_customers[ends[2].date()], star.repeat_customers[ends[4].date()]]
scoreboard.loc["marketing per repeat customer"] = scoreboard.loc["marketing spend"] / scoreboard.loc["repeat customers, 31 December"]
scoreboard.loc["active customers"] = years.active[[2024, 2025]].to_numpy()
scoreboard.loc["new customers"] = [cards[2024].new.sum(), cards[2025].new.sum()]
scoreboard["change"] = scoreboard[2025] / scoreboard[2024] - 1
print(scoreboard.round(3).to_string())

# %% guardrail
lead = load_fulfilment().assign(year=lambda f: f.order_date.dt.year)
print(lead[lead.year >= 2024].groupby("year").lead_time_days.agg(["mean", lambda d: d.quantile(.95)]).round(2).to_string())


# %% definitions_repeat
def repeat_rate(frame, within=None, mature_only=False):
    """Share of `frame` with a second order: ever, or within `within` days, optionally only customers we can have seen."""
    if mature_only:
        frame = frame[frame.first_order <= LAST - pd.Timedelta(days=within)]
    hit = frame.gap.notna() if within is None else frame.gap <= within
    return float(hit.mean()), len(frame)


joined_2025 = customers[customers.first_order.dt.year == 2025]
joined_2024 = customers[customers.first_order.dt.year == 2024]
for label, kwargs in {"ever": {}, "90 days, everyone": {"within": 90}, "90 days, mature": {"within": 90, "mature_only": True}}.items():
    r24, n24 = repeat_rate(joined_2024, **kwargs)
    r25, n25 = repeat_rate(joined_2025, **kwargs)
    print(f"{label:<20} 2024 {r24:.1%} of {n24:,}   2025 {r25:.1%} of {n25:,}")
late = joined_2025[joined_2025.first_order.dt.month == 12]
print(f"December 2025 joiners, 90 days, as seen on 31 December: {(late.gap <= 90).mean():.1%} of {len(late):,}")

# %% definitions_active
for days in (30, 90, 365):
    window = orders[orders.order_date > LAST - pd.Timedelta(days=days)]
    print(f"active in the last {days:>3} days: {window.customer_id.nunique():>6,}")
print("customers ever acquired:", f"{len(customers):,}")

# %% definitions_clock
fulfilment = load_fulfilment().merge(orders[["order_id", "value"]], on="order_id")
for name, column in (("order date", "order_date"), ("dispatch date", "dispatch_date"), ("delivery date", "delivered_date")):
    month = fulfilment[(fulfilment[column] >= "2025-11-01") & (fulfilment[column] < "2025-12-01")]
    print(f"November 2025 revenue by {name:<14} £{month.value.sum():>9,.0f}")
tail = fulfilment[(fulfilment.order_date >= "2025-12-01")]
print(f"December 2025 orders delivered after 31 December: {(tail.delivered_date > LAST).mean():.1%}, "
      f"£{tail[tail.delivered_date > LAST].value.sum():,.0f}")

# %% definitions_conversion
sessions = load_sessions()
sessions["bought"] = sessions.furthest == 5
by_visitor = sessions.groupby("user_id").bought.max()
print(f"per session {sessions.bought.mean():.2%}; per visitor {by_visitor.mean():.2%}")
print(f"purchases in the web log {sessions.bought.sum():,}; "
      f"orders in the ledger, same dates {((orders.order_date >= sessions.date.min())).sum():,}")


# %% spec
@dataclass(frozen=True)
class MetricSpec:
    name: str
    version: str
    question: str
    population: str
    numerator: str
    denominator: str
    clock: str
    window_days: int
    final_after_days: int
    owner: str


REPEAT_90 = MetricSpec(
    name="repeat_90d", version="1.0", question="Do the customers we acquire come back?",
    population="Customers whose first order fell in the reporting period and at least 90 days before the data ends",
    numerator="Of those, customers with a second order 1 to 90 days after the first; same-day orders do not count",
    denominator="Customers in the population",
    clock="order_date, in the ledger's own day", window_days=90, final_after_days=90, owner="Head of retention")


def repeat_90d(customer_table, start, end, as_of, spec=REPEAT_90):
    """The metric in `spec`, or None if none of the period's customers is final yet."""
    in_period = customer_table[(customer_table.first_order >= start) & (customer_table.first_order <= end)]
    population = in_period[in_period.first_order <= as_of - pd.Timedelta(days=spec.final_after_days)]
    if population.empty:
        return None
    seen = population.second_order <= as_of
    hit = seen & (population.gap >= 1) & (population.gap <= spec.window_days)
    return float(hit.mean())


toy = pd.DataFrame({
    "first_order": pd.to_datetime(["2025-01-01", "2025-01-01", "2025-01-01", "2025-01-01", "2025-11-01"]),
    "second_order": pd.to_datetime(["2025-01-01", "2025-03-01", "2025-06-01", None, "2025-11-05"])})
toy["gap"] = (toy.second_order - toy.first_order).dt.days
got = repeat_90d(toy, pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31"), pd.Timestamp("2025-12-31"))
assert got == 0.25, got  # one of the four mature rows; the same-day and day-151 repeats do not count, and November is not final
assert repeat_90d(toy, pd.Timestamp("2025-11-01"), pd.Timestamp("2025-11-30"), pd.Timestamp("2025-12-31")) is None
for year in (2024, 2025):
    value = repeat_90d(customers, pd.Timestamp(f"{year}-01-01"), pd.Timestamp(f"{year}-12-31"), LAST)
    print(year, f"{REPEAT_90.name} v{REPEAT_90.version}: {value:.1%}")

# %% gaming
END = pd.Timestamp("2025-12-31")
year_2025 = orders[(orders.order_date > END - pd.Timedelta(days=365)) & (orders.order_date <= END)]
counts = year_2025.groupby("customer_id").size()
once = year_2025[year_2025.customer_id.isin(counts[counts == 1].index)]
big = once[once.value >= once.value.quantile(.8)]
halves = pd.concat([big.assign(value=big.value / 2)] * 2)  # a hypothetical: split the largest single orders in two
gamed = pd.concat([year_2025.drop(big.index), halves])
print(f"split {len(big):,} orders: {repeat_customers(year_2025, END):,} repeat customers become {repeat_customers(gamed, END):,}")
print("revenue unchanged:", round(gamed.value.sum()) == round(year_2025.value.sum()),
      f"; value per order £{year_2025.value.mean():.2f} becomes £{gamed.value.mean():.2f}")


def repeat_customers_distinct(frame, end, days=365):
    """As repeat_customers, but two orders on one day count once."""
    window = frame[(frame.order_date > end - pd.Timedelta(days=days)) & (frame.order_date <= end)]
    return int((window.groupby("customer_id").order_date.nunique() >= 2).sum())


print(f"counting distinct days: {repeat_customers_distinct(year_2025, END):,} before, {repeat_customers_distinct(gamed, END):,} after")
print(f"distinct days, 31 December 2024: {repeat_customers_distinct(orders, pd.Timestamp('2024-12-31')):,}")

# %% diagnose
monthly = orders.assign(month=orders.order_date.dt.to_period("M")).groupby("month")[["customer_id", "value"]].apply(tree)
steps = pd.DataFrame({f"{a} to {b}": attribute(monthly.loc[a], monthly.loc[b]) for a, b in (("2024-12", "2025-01"), ("2024-11", "2025-11"))})
steps.loc["total"] = steps.sum()
print(steps.round(0).to_string())
print(monthly.loc["2024-10":"2025-03"].round(2).to_string())
