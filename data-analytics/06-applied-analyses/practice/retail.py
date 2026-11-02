"""Fernhill Home, a fictional online homewares retailer: the seeded data behind this pillar.

Same plot as the visualisation pillar: email budget cut in January 2025, paid social scaled
to 2.6 times its old size. This generator is new and works at customer level, so its totals
are not calibrated to the pillar 05 charts. Nothing is read from disk, and every call with
the default seed returns the same rows.

The first five tables feed chapters 1 to 6 and are frozen: their numbers are quoted in the notes.
The rest are overlays for later chapters. They share customer ids and channels with load_customers,
draw from their own streams (STREAMS) and never feed back, so a club member's extra spend, say, is
not in load_orders. Columns starting `true_` are what no analyst would see. load_truth(table) gives
that table's parameters and realised true effects as a dict; the *_DGP constants hold the parameters.

load_subscriptions (truth "subscriptions", 06/07): subscription_id, customer_id, channel, plan,
    monthly_price, welcome_call, start_date, end_date, event, event_type (cancel, downgrade),
    churn_reason, duration_days, price_rise_day, true_duration_days, true_event_type.
    Cancel hazard is Weibull with HRs by channel and plan. The welcome call has HR .60 for 90 days,
    then 1.0, so a single HR breaks proportional hazards; who gets a call is confounded by channel and
    plan. The price rise has HR 1.5 from 2025-03-01 for those already subscribed. Downgrade is a
    competing risk. The HRs are for cancels, treating downgrades as censored.
load_subscription_periods (same truth): subscription_id, customer_id, channel, plan, welcome_call,
    tenure_month, start_day, stop_day, cancel, downgrade, welcome_early, price_rise_active. One row per
    30 days at risk. price_rise_active is 1 if the rise came by start_day; use price_rise_day for exact timing.
load_club (truth "club", 03/05): customer_id, channel, prior_orders, prior_spend, recency_days,
    tenure_days, club, spend_next_6m, sessions_next_6m (post-treatment), true_engagement (the unobserved
    confounder), true_propensity, true_y0, true_y1. true_ate, true_att and true_atc differ on purpose.
load_journeys (truth "journeys", 06/08): customer_id, channel, month_index, month, state (new, active,
    lapsed, churned), orders, revenue, true_journey_type. Four planted types, each a Markov chain, so a
    single pooled chain misprices a new customer.
load_marketing_weekly (truth "marketing", 06/09): week, revenue, spend_<channel>, new_customers_<channel>,
    true_baseline, true_contribution_<channel>. Geometric adstock and Hill saturation per channel; spend
    follows the January 2025 cut and rises before Christmas with sales. Revenue is not reconciled to load_orders.
load_geo_test (truth "geo_test", 06/09): geo, pair, week, holdout, post, spend_paid_social, revenue,
    true_paid_social_contribution, true_counterfactual_revenue. Randomised paid social holdout on
    the same response curve as load_marketing_weekly, giving true_iroas.
load_touch_paths (truth "touch_paths", 06/09): path_id, path, n_touches, converted, value, true_intent,
    true_p_convert. Paid social retargets people already likely to buy, so last touch overcredits it
    against true_incremental_share.
load_repeat_log (truth "repeat_log", 06/09): customer_id, order_date, value, true_alive_at_end,
    true_rate_per_week, true_dropout_p. Drawn from BG/NBD and Gamma-Gamma exactly (r, alpha, a, b, p, q, v).
load_fulfilment (truth "fulfilment", 06/10): order_id, customer_id, order_date, category, pick_minutes,
    pack_minutes, dispatch_date, delivered_date, lead_time_days. One row per order in load_orders.
    Furniture is slow, November and December slower, and the June 2023 outage delays dispatch.
load_packing_line (truth "packing_line", 06/10): parcel_id, date, weekday, packer, arrived, pack_start,
    pack_end, wait_minutes, pack_minutes. Simulated M/M/c, with erlang_c() and its results as the truth.
load_products, load_product_demand, load_purchase_orders (truth "products", 06/10): sku, category,
    unit_cost, unit_price, salvage_value, holding_cost_per_year, order_cost, christmas_only; week, sku,
    units; po_id, sku, ordered, lead_time_days, received. Truth by_sku holds each newsvendor_q, eoq and safety_stock.
"""
from copy import deepcopy
from functools import lru_cache
from statistics import NormalDist

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


# ---------------------------------------------------------------------------------------------
# Tables added for chapters 03/05 and 06/07 to 06/10. See the module docstring. Each table has its
# own random stream, so nothing here can move a number in the tables above. Add a stream, don't share one.
# ---------------------------------------------------------------------------------------------
STREAMS = {"subscriptions": 101, "club": 102, "journeys": 103, "marketing": 104, "geo_test": 105,
           "touch_paths": 106, "repeat_log": 107, "fulfilment": 108, "packing_line": 109, "products": 110}


def _stream(name, seed):
    """A generator keyed on [seed, id], which never overlaps the seed, seed + 1, ... streams above."""
    return np.random.default_rng([seed, STREAMS[name]])


def _z(x):
    return (x - x.mean()) / x.std()


CLUB_DATE = pd.Timestamp("2024-07-01")      # Fernhill Club opens; customers choose whether to join
PRICE_RISE = pd.Timestamp("2025-03-01")     # subscription box price rise, existing subscribers included
PLANS = {"standard": (24.0, 28.0), "large": (39.0, 45.0)}   # monthly price before and after the rise

SUBSCRIPTION_DGP = {
    "p_subscribe": {"paid_social": .15, "organic": .20, "email": .30, "referral": .20},
    "p_large": .30,
    # Who gets through on the welcome call: a confounder, because these groups also churn differently.
    "p_call": {"paid_social": .35, "organic": .55, "email": .75, "referral": .55},
    "p_call_large_extra": .10,
    # Cancel hazard, per day: Weibull baseline (organic, standard, no call, before the rise) times the HRs.
    "weibull_shape": .75,
    "weibull_scale_days": 420.0,
    "hr_channel": {"paid_social": 1.6, "organic": 1.0, "email": .7, "referral": .9},
    "hr_plan": {"standard": 1.0, "large": .8},
    "hr_welcome_early": .60,        # the call delays: this HR holds for the first welcome_early_days ...
    "welcome_early_days": 90,
    "hr_welcome_late": 1.0,         # ... and then it wears off, so a single-HR Cox model breaks PH on purpose
    "hr_price_rise": 1.5,           # from PRICE_RISE on, for people subscribed before it; joiners after it are exempt
    "price_rise_date": PRICE_RISE,
    # Competing risk: a constant downgrade hazard, no covariate but plan.
    "downgrade_rate_per_30d": {"standard": .006, "large": .020},
    "cancel_reason_mix": {"price": .20, "no_longer_needed": .40, "quality": .20, "moved_or_other": .20},
    "downgrade_reason_mix": {"price": .30, "too_much_product": .70},
}


def _cancel_days(exposure, base, call, rise_day, d):
    """Invert the piecewise Weibull cumulative hazard: the day each subscriber's exposure runs out."""
    k, scale = d["weibull_shape"], d["weibull_scale_days"]
    H0 = lambda t: (t / scale) ** k
    out = np.empty(len(exposure))
    for i in range(len(exposure)):
        cuts = sorted(c for c in (d["welcome_early_days"] if call[i] else np.nan, rise_day[i]) if c == c) + [np.inf]
        t0, used = 0.0, 0.0
        for cut in cuts:
            m = base[i]
            if call[i]:
                m *= d["hr_welcome_early"] if t0 < d["welcome_early_days"] else d["hr_welcome_late"]
            if rise_day[i] == rise_day[i] and t0 >= rise_day[i]:
                m *= d["hr_price_rise"]
            step = m * (H0(cut) - H0(t0))
            if used + step >= exposure[i]:
                out[i] = scale * ((exposure[i] - used) / m + H0(t0)) ** (1 / k)
                break
            t0, used = cut, used + step
    return out


@lru_cache(maxsize=1)
def _subscriptions(seed=SEED):
    d = SUBSCRIPTION_DGP
    rng = _stream("subscriptions", seed)
    frame = load_customers(seed)[["customer_id", "channel", "acquired"]]
    frame = frame[rng.uniform(size=len(frame)) < frame["channel"].map(d["p_subscribe"]).to_numpy()]
    frame = frame.assign(start_date=frame["acquired"] + pd.to_timedelta(rng.integers(0, 31, len(frame)), "D"))
    frame = frame[frame["start_date"] < END].drop(columns="acquired").reset_index(drop=True)
    n = len(frame)
    frame["plan"] = rng.choice(list(PLANS), n, p=[1 - d["p_large"], d["p_large"]])
    large = (frame["plan"] == "large").to_numpy()
    p_call = frame["channel"].map(d["p_call"]).to_numpy() + d["p_call_large_extra"] * large
    frame["welcome_call"] = (rng.uniform(size=n) < p_call).astype(int)
    frame["monthly_price"] = [PLANS[p][int(s >= PRICE_RISE)] for p, s in zip(frame["plan"], frame["start_date"])]
    rise = (PRICE_RISE - frame["start_date"]).dt.days.to_numpy(dtype=float)
    rise[rise <= 0] = np.nan                # joined after the rise: this price is the only one they know
    frame["price_rise_day"] = rise

    base = frame["channel"].map(d["hr_channel"]).to_numpy() * frame["plan"].map(d["hr_plan"]).to_numpy()
    cancel = _cancel_days(rng.exponential(1, n), base, frame["welcome_call"].to_numpy(), rise, d)
    downgrade = rng.exponential(30 / frame["plan"].map(d["downgrade_rate_per_30d"]).to_numpy())
    true_days = np.maximum(np.ceil(np.minimum(cancel, downgrade)), 1).astype(int)
    true_type = np.where(cancel <= downgrade, "cancel", "downgrade")
    censor = (END - frame["start_date"]).dt.days.to_numpy()
    observed = true_days <= censor

    reason = np.empty(n, dtype=object)
    risen = np.nan_to_num(rise, nan=np.inf) <= cancel
    mix = d["cancel_reason_mix"]
    extra = d["hr_price_rise"] - 1          # the extra hazard after the rise is all price cancels
    after = {r: (p + extra * (r == "price")) / d["hr_price_rise"] for r, p in mix.items()}
    for mask, shares in (((true_type == "cancel") & ~risen, mix), ((true_type == "cancel") & risen, after),
                         (true_type == "downgrade", d["downgrade_reason_mix"])):
        reason[mask] = rng.choice(list(shares), mask.sum(), p=list(shares.values()))

    frame["event"] = observed.astype(int)
    frame["event_type"] = pd.Series(true_type).where(observed, None)
    frame["churn_reason"] = pd.Series(reason).where(observed, None)
    frame["duration_days"] = np.minimum(true_days, censor)
    frame["end_date"] = frame["start_date"] + pd.to_timedelta(np.where(observed, true_days, np.nan), "D")
    frame["true_duration_days"] = true_days
    frame["true_event_type"] = true_type
    frame = frame.sort_values(["start_date", "customer_id"], ignore_index=True)
    frame.insert(0, "subscription_id", np.arange(1, n + 1))
    frame = frame[["subscription_id", "customer_id", "channel", "plan", "monthly_price", "welcome_call", "start_date",
                   "end_date", "event", "event_type", "churn_reason", "duration_days", "price_rise_day",
                   "true_duration_days", "true_event_type"]]
    truth = {**d, "n": n, "censored_share": 1 - observed.mean(),
             "mean_days_churned_only": frame.loc[frame["event"] == 1, "duration_days"].mean(),
             "true_mean_days": true_days.mean(), "true_median_days": float(np.median(true_days)),
             "call_rate_by_channel": frame.groupby("channel")["welcome_call"].mean().to_dict(),
             "reason_mix_after_rise": after}
    return frame, truth


def load_subscriptions(seed=SEED):
    """One row per subscription box, started January 2023 to December 2025, censored at END."""
    return _subscriptions(seed)[0].copy()


def load_subscription_periods(seed=SEED):
    """Person-period form of load_subscriptions: one row per 30 days at risk, for a discrete-time hazard."""
    s = _subscriptions(seed)[0]
    periods = np.ceil(s["duration_days"] / 30).astype(int).to_numpy()
    i = np.repeat(np.arange(len(s)), periods)
    frame = s.iloc[i][["subscription_id", "customer_id", "channel", "plan", "welcome_call"]].reset_index(drop=True)
    frame["tenure_month"] = np.concatenate([np.arange(1, p + 1) for p in periods])
    frame["start_day"] = (frame["tenure_month"] - 1) * 30
    frame["stop_day"] = np.minimum(frame["tenure_month"] * 30, s["duration_days"].to_numpy()[i])
    last = frame["tenure_month"].to_numpy() == periods[i]
    kind = s["event_type"].to_numpy()[i]
    frame["cancel"] = (last & (kind == "cancel")).astype(int)
    frame["downgrade"] = (last & (kind == "downgrade")).astype(int)
    frame["welcome_early"] = ((frame["welcome_call"] == 1)
                              & (frame["start_day"] < SUBSCRIPTION_DGP["welcome_early_days"])).astype(int)
    frame["price_rise_active"] = (s["price_rise_day"].to_numpy()[i] <= frame["start_day"].to_numpy()).astype(int)
    return frame


CLUB_DGP = {
    # P(join): logit on standardised covariates. Y(0): £ in the next six months, with a curve in prior spend.
    "logit_join": {"const": -.40, "z_log_prior_orders": 1.10, "z_log_prior_spend": .70, "z_recency": -.50,
                   "unobserved_engagement": .50},
    "logit_join_channel": {"paid_social": -.70, "organic": 0.0, "email": .60, "referral": .20},
    "y0": {"const": 55.0, "z_log_prior_orders": 28.0, "z_log_prior_spend": 22.0, "z_log_prior_spend_squared": 12.0,
           "z_recency": -15.0, "unobserved_engagement": 8.0, "noise_sd": 30.0},
    "y0_channel": {"paid_social": -8.0, "organic": 0.0, "email": 6.0, "referral": 2.0},
    # Y(1) - Y(0) grows with prior orders, so the effect on joiners exceeds the effect on everyone.
    "effect": {"const": 15.0, "z_log_prior_orders": 10.0, "email_extra": 5.0},
    "unobserved_odds_ratio_per_sd": float(np.exp(.50)),
    "backdoor_observed": ["channel", "prior_orders", "prior_spend", "recency_days", "tenure_days"],
    "not_observed": "true_engagement",
    "post_treatment": "sessions_next_6m",
}


@lru_cache(maxsize=1)
def _club(seed=SEED):
    d = CLUB_DGP
    rng = _stream("club", seed)
    orders = load_orders(seed)
    prior = (orders[orders["order_date"] < CLUB_DATE].groupby("customer_id")
             .agg(prior_orders=("order_id", "size"), prior_spend=("value", "sum"), last=("order_date", "max")))
    frame = load_customers(seed)[["customer_id", "channel", "acquired"]].merge(prior, left_on="customer_id", right_index=True)
    frame["recency_days"] = (CLUB_DATE - frame["last"]).dt.days
    frame["tenure_days"] = (CLUB_DATE - frame["acquired"]).dt.days
    frame = frame[frame["recency_days"] <= 365].drop(columns=["last", "acquired"]).reset_index(drop=True)
    frame["prior_spend"] = frame["prior_spend"].round(2)
    n = len(frame)
    zo, zs, zr = _z(np.log1p(frame["prior_orders"])), _z(np.log1p(frame["prior_spend"])), _z(frame["recency_days"])
    u = rng.normal(size=n)
    lj, y = d["logit_join"], d["y0"]
    logit = (lj["const"] + lj["z_log_prior_orders"] * zo + lj["z_log_prior_spend"] * zs + lj["z_recency"] * zr
             + frame["channel"].map(d["logit_join_channel"]) + lj["unobserved_engagement"] * u)
    p = 1 / (1 + np.exp(-logit))
    frame["club"] = (rng.uniform(size=n) < p).astype(int)
    noise = rng.normal(0, y["noise_sd"], n)
    y0 = (y["const"] + y["z_log_prior_orders"] * zo + y["z_log_prior_spend"] * zs
          + y["z_log_prior_spend_squared"] * zs ** 2 + y["z_recency"] * zr
          + frame["channel"].map(d["y0_channel"]) + y["unobserved_engagement"] * u + noise).clip(lower=0).round(2)
    e = d["effect"]
    y1 = (y0 + e["const"] + e["z_log_prior_orders"] * zo + e["email_extra"] * (frame["channel"] == "email")).clip(lower=0).round(2)
    joined = frame["club"] == 1
    frame["spend_next_6m"] = y1.where(joined, y0)
    frame["sessions_next_6m"] = rng.poisson(np.exp(1.2 + .15 * zo + .35 * frame["club"] + .2 * u))
    frame["true_engagement"] = u
    frame["true_propensity"] = p
    frame["true_y0"] = y0
    frame["true_y1"] = y1
    effect = y1 - y0
    truth = {**d, "n": n, "club_date": CLUB_DATE, "treated_share": joined.mean(), "true_ate": effect.mean(),
             "true_att": effect[joined].mean(), "true_atc": effect[~joined].mean(),
             "naive_difference": frame.loc[joined, "spend_next_6m"].mean() - frame.loc[~joined, "spend_next_6m"].mean(),
             "selection_bias": y0[joined].mean() - y0[~joined].mean()}
    return frame, truth


def load_club(seed=SEED):
    """One row per recently active customer at CLUB_DATE: did they join, and what did they spend next?"""
    return _club(seed)[0].copy()


JOURNEY_STATES = ["new", "active", "lapsed", "churned"]
JOURNEY_MONTHS = 18
JOURNEY_DGP = {
    # Each row of a matrix is a state in JOURNEY_STATES order. "churned" absorbs.
    "transition": {
        "steady": [[0, .85, .15, 0], [0, .85, .13, .02], [0, .50, .42, .08], [0, 0, 0, 1]],
        "drifter": [[0, .60, .35, .05], [0, .60, .33, .07], [0, .20, .60, .20], [0, 0, 0, 1]],
        "one_and_done": [[0, .05, .25, .70], [0, .20, .30, .50], [0, .05, .35, .60], [0, 0, 0, 1]],
        "comeback": [[0, .35, .60, .05], [0, .30, .65, .05], [0, .45, .50, .05], [0, 0, 0, 1]],
    },
    "type_mix": {
        "paid_social": {"steady": .10, "drifter": .25, "one_and_done": .55, "comeback": .10},
        "organic": {"steady": .25, "drifter": .30, "one_and_done": .25, "comeback": .20},
        "email": {"steady": .40, "drifter": .25, "one_and_done": .10, "comeback": .25},
        "referral": {"steady": .25, "drifter": .30, "one_and_done": .25, "comeback": .20},
    },
    "extra_orders_when_active": {"steady": .5, "drifter": .2, "one_and_done": .05, "comeback": .3},
    "mean_order_value": 42 * float(np.exp(.55 ** 2 / 2)),
    "monthly_discount": .01,
}


def _chain_values(P, reward, discount):
    """Expected months to churn and discounted value per state, from the fundamental matrix."""
    P = np.asarray(P, dtype=float)
    N = np.linalg.inv(np.eye(3) - P[:3, :3])
    value = np.linalg.solve(np.eye(4) - P / (1 + discount), reward)
    return N.sum(axis=1), value


@lru_cache(maxsize=2)
def _journeys(n_customers=4000, seed=SEED):
    d = JOURNEY_DGP
    rng = _stream("journeys", seed)
    customers = load_customers(seed)
    customers = customers[customers["acquired"] < "2024-07-01"]     # every journey is seen for all 18 months
    picked = np.sort(rng.choice(len(customers), n_customers, replace=False))
    customers = customers.iloc[picked].reset_index(drop=True)
    types = list(d["transition"])
    tensor = np.array([d["transition"][t] for t in types], dtype=float).cumsum(axis=2)
    who = np.array([rng.choice(4, p=[d["type_mix"][c][t] for t in types]) for c in customers["channel"]])
    states = np.zeros((n_customers, JOURNEY_MONTHS), dtype=int)
    for m in range(1, JOURNEY_MONTHS):
        draws = rng.uniform(size=n_customers)
        states[:, m] = (draws[:, None] > tensor[who, states[:, m - 1]]).sum(axis=1).clip(max=3)
    extra = np.array([d["extra_orders_when_active"][t] for t in types])[who]
    n_orders = np.where(states == 0, 1, 0) + (states == 1) * (1 + rng.poisson(extra[:, None], states.shape))
    # Same order value as load_orders: lognormal around £42.
    revenue = np.array([rng.lognormal(np.log(42), .55, x).sum() for x in n_orders.ravel()]).reshape(states.shape)
    k = np.tile(np.arange(JOURNEY_MONTHS), n_customers)
    i = np.repeat(np.arange(n_customers), JOURNEY_MONTHS)
    months = customers["acquired"].dt.year.to_numpy()[i] * 12 + customers["acquired"].dt.month.to_numpy()[i] - 1 + k
    frame = pd.DataFrame({
        "customer_id": customers["customer_id"].to_numpy()[i], "channel": customers["channel"].to_numpy()[i],
        "month_index": k, "month": pd.to_datetime({"year": months // 12, "month": months % 12 + 1, "day": 1}),
        "state": np.array(JOURNEY_STATES)[states.ravel()], "orders": n_orders.ravel(),
        "revenue": revenue.ravel().round(2), "true_journey_type": np.array(types)[who[i]],
    })
    # The truth: per type, and the mixture a pooled chain is estimating.
    by_type, counts = {}, np.zeros((4, 4))
    for t_i, t in enumerate(types):
        P = np.array(d["transition"][t], dtype=float)
        reward = d["mean_order_value"] * np.array([1, 1 + d["extra_orders_when_active"][t], 0, 0])
        months_left, value = _chain_values(P, reward, d["monthly_discount"])
        by_type[t] = {"months_to_churn": dict(zip(JOURNEY_STATES, months_left)),
                      "value": dict(zip(JOURNEY_STATES, value)), "monthly_reward": dict(zip(JOURNEY_STATES, reward)),
                      "p_second_order": P[0, 1] + P[0, 2] * P[2, 1] / (1 - P[2, 2])}
    np.add.at(counts, (states[:, :-1].ravel(), states[:, 1:].ravel()), 1)
    pooled = counts / counts.sum(axis=1, keepdims=True).clip(min=1)
    pooled[3] = [0, 0, 0, 1]
    share = np.bincount(who, minlength=4) / n_customers
    truth = {**d, "n": n_customers, "states": JOURNEY_STATES, "months": JOURNEY_MONTHS, "by_type": by_type,
             "realised_type_share": dict(zip(types, share)),
             "realised_pooled_transition": pooled,
             # The trap: a single chain averages the types and misprices a new customer.
             "true_value_of_new_customer": sum(share[i] * by_type[t]["value"]["new"] for i, t in enumerate(types))}
    return frame, truth


def load_journeys(n_customers=4000, seed=SEED):
    """One row per customer per month for 18 months: a planted state and what they bought in it."""
    return _journeys(n_customers, seed)[0].copy()


MARKETING_START = "2023-01-02"
MARKETING_DGP = {
    # Revenue = baseline + sum over channels of beta * Hill(adstock(spend)), plus noise.
    "weekly_spend_before_cut": {"paid_social": 2500.0, "organic": 800.0, "email": 1200.0, "referral": 600.0},
    "weekly_spend_after_cut": {"paid_social": 6500.0, "organic": 800.0, "email": 400.0, "referral": 600.0},
    "spend_noise_sigma": .20,
    "spend_seasonal_lift": .25,     # budgets rise before Christmas, when baseline sales rise anyway: a confounder
    "adstock_alpha": {"paid_social": .30, "organic": .60, "email": .15, "referral": .40},
    "adstock_l_max": 8,             # geometric weights over 0..7 lags, normalised to sum to one
    "hill_K": {"paid_social": 5000.0, "organic": 1000.0, "email": 900.0, "referral": 500.0},
    "hill_slope": {"paid_social": 1.5, "organic": 1.0, "email": 1.2, "referral": 1.0},
    "beta": {"paid_social": 15000.0, "organic": 3000.0, "email": 6000.0, "referral": 2000.0},
    "baseline_level": 12000.0, "baseline_trend_per_week": 15.0, "baseline_xmas_lift": .30, "revenue_noise_sd": 900.0,
}


def _adstock(x, alpha, l_max):
    """Geometric carryover. Weights sum to one, so the result stays on the spend scale."""
    w = alpha ** np.arange(l_max)
    w = w / w.sum()
    padded = np.concatenate([np.full(l_max - 1, x[0]), x])
    return np.convolve(padded, w, mode="valid")


def _hill(x, K, slope):
    return x ** slope / (x ** slope + K ** slope)


def _xmas_weight(weeks):
    """Smooth pre-Christmas bump, 0 to 1, peaking in the third week of December."""
    return np.exp(-(((weeks.dayofyear.to_numpy() - 352) / 21.0) ** 2))


@lru_cache(maxsize=1)
def _marketing(seed=SEED):
    d = MARKETING_DGP
    rng = _stream("marketing", seed)
    weeks = pd.date_range(MARKETING_START, END, freq="W-MON")
    t, season = np.arange(len(weeks)), _xmas_weight(weeks)
    after = weeks >= CUT
    frame = pd.DataFrame({"week": weeks})
    baseline = d["baseline_level"] + d["baseline_trend_per_week"] * t
    baseline = baseline * (1 + d["baseline_xmas_lift"] * season)
    frame["true_baseline"] = baseline
    revenue = baseline + rng.normal(0, d["revenue_noise_sd"], len(t))
    contribution_total, truth_roas, truth_marginal = 0, {}, {}
    for c in CHANNELS:
        plan = np.where(after, d["weekly_spend_after_cut"][c], d["weekly_spend_before_cut"][c])
        burst = 1 + .5 * (rng.uniform(size=len(t)) < .12)       # flights, so the channels don't move together
        spend = plan * burst * (1 + d["spend_seasonal_lift"] * season) * rng.lognormal(0, d["spend_noise_sigma"], len(t))
        ad = _adstock(spend, d["adstock_alpha"][c], d["adstock_l_max"])
        part = d["beta"][c] * _hill(ad, d["hill_K"][c], d["hill_slope"][c])
        frame[f"spend_{c}"] = spend.round(2)
        frame[f"true_contribution_{c}"] = part
        contribution_total = contribution_total + part
        truth_roas[c] = {"before_cut": part[~after].sum() / spend[~after].sum(), "after_cut": part[after].sum() / spend[after].sum()}
        x = ad[after].mean()
        truth_marginal[c] = d["beta"][c] * (_hill(x + 1, d["hill_K"][c], d["hill_slope"][c]) - _hill(x, d["hill_K"][c], d["hill_slope"][c]))
    frame["revenue"] = (revenue + contribution_total).round(2)
    customers = load_customers(seed)
    bucket = customers["acquired"].dt.to_period("W-SUN").dt.start_time
    counts = customers.groupby([bucket, "channel"]).size().unstack(fill_value=0)
    for c in CHANNELS:
        frame[f"new_customers_{c}"] = frame["week"].map(counts[c]).fillna(0).astype(int)
    order = ["week", "revenue"] + [f"spend_{c}" for c in CHANNELS] + [f"new_customers_{c}" for c in CHANNELS]
    frame = frame[order + ["true_baseline"] + [f"true_contribution_{c}" for c in CHANNELS]]
    truth = {**d, "true_roas": truth_roas, "true_marginal_roas_after_cut": truth_marginal,
             "true_baseline_share": frame["true_baseline"].sum() / frame["revenue"].sum()}
    return frame, truth


def load_marketing_weekly(seed=SEED):
    """One row per week, 2023 to 2025: revenue, spend by channel, and new customers from load_customers."""
    return _marketing(seed)[0].copy()


GEO_TEST_DGP = {"n_geos": 20, "start": "2024-09-02", "pre_weeks": 12, "test_weeks": 8, "noise_sd_share": .03,
                "channel": "paid_social", "holdout": "paid_social spend goes to zero in half of the geos"}


@lru_cache(maxsize=1)
def _geo_test(seed=SEED):
    d, m = GEO_TEST_DGP, MARKETING_DGP
    rng = _stream("geo_test", seed)
    national = _marketing(seed)[0].set_index("week")
    start = pd.Timestamp(d["start"])
    weeks = pd.date_range(start - pd.Timedelta(weeks=d["pre_weeks"]), periods=d["pre_weeks"] + d["test_weeks"], freq="W-MON")
    share = np.sort(rng.dirichlet(np.full(d["n_geos"], 8.0)))
    # Pair geos of similar size, then flip a coin in each pair.
    holdout = np.array([x for _ in range(d["n_geos"] // 2) for x in rng.permutation([0, 1])])
    effect_alpha, K, slope, beta = m["adstock_alpha"]["paid_social"], m["hill_K"]["paid_social"], m["hill_slope"]["paid_social"], m["beta"]["paid_social"]
    other = (national["revenue"] - national["true_contribution_paid_social"]).loc[weeks].to_numpy()
    plan = national["spend_paid_social"].loc[weeks].to_numpy()
    post = (weeks >= start).astype(int)
    frames, lost, saved = [], 0.0, 0.0
    for g in range(d["n_geos"]):
        spend = share[g] * plan * rng.lognormal(0, .10, len(weeks))
        actual = np.where(holdout[g] & (post == 1), 0.0, spend)
        with_ads = share[g] * beta * _hill(_adstock(spend / share[g], effect_alpha, m["adstock_l_max"]), K, slope)
        got = share[g] * beta * _hill(_adstock(actual / share[g], effect_alpha, m["adstock_l_max"]), K, slope)
        rest = share[g] * other * rng.lognormal(0, d["noise_sd_share"], len(weeks))
        frames.append(pd.DataFrame({
            "geo": f"G{g + 1:02d}", "pair": g // 2 + 1, "week": weeks, "holdout": int(holdout[g]), "post": post,
            "spend_paid_social": actual.round(2), "revenue": (rest + got).round(2),
            "true_paid_social_contribution": got, "true_counterfactual_revenue": rest + with_ads,
        }))
        if holdout[g]:
            test = post == 1
            lost += (with_ads - got)[test].sum()
            saved += spend[test].sum()
    frame = pd.concat(frames, ignore_index=True)
    return frame, {**d, "geo_share": share, "true_iroas": lost / saved, "true_revenue_lost": lost, "spend_saved": saved}


def load_geo_test(seed=SEED):
    """One row per geo per week: a randomised paid social holdout, on the same response curve as the MMM data."""
    return _geo_test(seed)[0].copy()


TOUCH_DGP = {
    "n_paths": 8000,
    # Noisy-or: P(convert) = 1 - (1 - baseline(intent)) * product over touches of (1 - lift of that channel).
    "lift_per_touch": {"paid_social": .01, "organic": .02, "email": .05, "referral": .06},
    "baseline_conversion": "0.02 + 0.25 * intent ** 2",
    "intent": "Beta(1.5, 3)",
    "mean_extra_touches": 1.5,
    "channel_weights_low_intent": {"paid_social": .45, "organic": .35, "email": .10, "referral": .10},
    "channel_weights_high_intent": {"paid_social": .30, "organic": .25, "email": .25, "referral": .20},
    "retarget_intent_above": .55,   # paid social chases people who were going to buy, and touches them last
    "retarget_probability": .70,
}


@lru_cache(maxsize=1)
def _touch_paths(seed=SEED):
    d = TOUCH_DGP
    rng = _stream("touch_paths", seed)
    n = d["n_paths"]
    intent = rng.beta(1.5, 3, n)
    n_touches = 1 + rng.poisson(d["mean_extra_touches"], n)
    low = np.array([d["channel_weights_low_intent"][c] for c in CHANNELS])
    high = np.array([d["channel_weights_high_intent"][c] for c in CHANNELS])
    retarget = (intent > d["retarget_intent_above"]) & (rng.uniform(size=n) < d["retarget_probability"])
    paths = []
    for i in range(n):
        weights = low + (high - low) * intent[i]
        path = list(rng.choice(CHANNELS, n_touches[i], p=weights / weights.sum()))
        paths.append(path + ["paid_social"] * int(retarget[i]))
    lift = d["lift_per_touch"]
    baseline = .02 + .25 * intent ** 2
    survive = np.array([np.prod([1 - lift[c] for c in p]) for p in paths])
    p_convert = 1 - (1 - baseline) * survive
    incremental = {}
    for c in CHANNELS:
        without = np.array([np.prod([1 - lift[x] for x in p if x != c]) for p in paths])
        incremental[c] = float((p_convert - (1 - (1 - baseline) * without)).sum())
    converted = rng.uniform(size=n) < p_convert
    value = rng.lognormal(np.log(42), .55, n)
    frame = pd.DataFrame({"path_id": np.arange(1, n + 1), "path": [">".join(p) for p in paths],
                          "n_touches": [len(p) for p in paths], "converted": converted.astype(int),
                          "value": np.where(converted, value.round(2), 0.0),
                          "true_intent": intent, "true_p_convert": p_convert})
    total = sum(incremental.values())
    truth = {**d, "true_incremental_conversions": incremental,
             "true_incremental_share": {c: v / total for c, v in incremental.items()},
             "conversions_without_any_touch": float(baseline.sum()), "expected_conversions": float(p_convert.sum())}
    return frame, truth


def load_touch_paths(seed=SEED):
    """One row per path to purchase or not: the channels in order, joined with ">"."""
    return _touch_paths(seed)[0].copy()


REPEAT_LOG_DGP = {
    # Exactly BG/NBD and Gamma-Gamma, in the parameters pymc-marketing reports. Time is in weeks.
    "r": .50, "alpha": 8.0, "a": .70, "b": 2.50,        # purchase rate ~ Gamma(r, alpha); dropout ~ Beta(a, b)
    "p": 6.0, "q": 4.0, "v": 25.0,                      # order value ~ Gamma(p, nu); nu ~ Gamma(q, v)
    "n_customers": 3000, "cohort_start": "2024-01-01", "cohort_end": "2024-06-30",
}


@lru_cache(maxsize=1)
def _repeat_log(seed=SEED):
    d = REPEAT_LOG_DGP
    rng = _stream("repeat_log", seed)
    n = d["n_customers"]
    span = (pd.Timestamp(d["cohort_end"]) - pd.Timestamp(d["cohort_start"])).days + 1
    first = pd.Timestamp(d["cohort_start"]) + pd.to_timedelta(rng.integers(0, span, n), "D")
    rate = rng.gamma(d["r"], 1 / d["alpha"], n)         # numpy takes a scale, the model states a rate
    dropout = rng.beta(d["a"], d["b"], n)
    nu = rng.gamma(d["q"], 1 / d["v"], n)
    horizon = (END - first).days.to_numpy() / 7
    rows, alive = [], np.ones(n, dtype=bool)
    for i in range(n):
        rows.append((i, 0.0))
        t = 0.0
        while True:
            t += rng.exponential(1 / rate[i])
            if t > horizon[i]:
                break
            rows.append((i, t))
            if rng.uniform() < dropout[i]:      # dropout only ever follows a repeat purchase
                alive[i] = False
                break
    log = pd.DataFrame(rows, columns=["i", "week"])
    log["customer_id"] = log["i"] + 1
    log["order_date"] = first[log["i"]] + pd.to_timedelta(np.floor(log["week"] * 7), "D")
    log["value"] = rng.gamma(d["p"], 1 / nu[log["i"]]).round(2).clip(min=.01)
    log["true_alive_at_end"] = alive[log["i"]].astype(int)
    log["true_rate_per_week"] = rate[log["i"]]
    log["true_dropout_p"] = dropout[log["i"]]
    log = log.sort_values(["order_date", "customer_id"], ignore_index=True)
    frame = log[["customer_id", "order_date", "value", "true_alive_at_end", "true_rate_per_week", "true_dropout_p"]]
    truth = {**d, "observation_end": END, "time_unit": "weeks", "realised_alive_share": alive.mean(),
             "true_mean_order_value": d["p"] * d["v"] / (d["q"] - 1)}
    return frame, truth


def load_repeat_log(seed=SEED):
    """A non-contractual order log with exact BG/NBD and Gamma-Gamma truth, for chapter 9."""
    return _repeat_log(seed)[0].copy()


FULFILMENT_DGP = {
    # Lognormal around these means; sigma 0.4. Peak is 1 November to 31 December.
    "mean_pick_minutes": {"kitchen": 4.0, "textiles": 3.0, "lighting": 5.0, "furniture": 14.0},
    "mean_pack_minutes": {"kitchen": 3.0, "textiles": 2.0, "lighting": 4.0, "furniture": 9.0},
    "peak_pick_multiplier": 1.30,
    "time_sigma": .40,
    # Days from order to dispatch ~ Poisson; from dispatch to delivery = 1 + Poisson(mean - 1).
    "mean_dispatch_days": .60, "peak_extra_dispatch_days": 1.0,
    "outage_start": "2023-06-12", "outage_end": "2023-06-18", "outage_extra_dispatch_days": 4.0,
    "mean_transit_days": {"kitchen": 2.0, "textiles": 2.0, "lighting": 2.0, "furniture": 6.0},
}


@lru_cache(maxsize=1)
def _fulfilment(seed=SEED):
    d = FULFILMENT_DGP
    rng = _stream("fulfilment", seed)
    frame = load_orders(seed)[["order_id", "customer_id", "order_date", "category"]]
    n = len(frame)
    peak = frame["order_date"].dt.month.isin([11, 12]).to_numpy()
    outage = frame["order_date"].between(d["outage_start"], d["outage_end"]).to_numpy()
    shrink = d["time_sigma"] ** 2 / 2       # so the stated numbers are means, not medians
    pick = frame["category"].map(d["mean_pick_minutes"]).to_numpy() * np.where(peak, d["peak_pick_multiplier"], 1)
    frame["pick_minutes"] = (pick * rng.lognormal(-shrink, d["time_sigma"], n)).round(2)
    pack = frame["category"].map(d["mean_pack_minutes"]).to_numpy()
    frame["pack_minutes"] = (pack * rng.lognormal(-shrink, d["time_sigma"], n)).round(2)
    lag = rng.poisson(d["mean_dispatch_days"] + d["peak_extra_dispatch_days"] * peak + d["outage_extra_dispatch_days"] * outage)
    transit = 1 + rng.poisson(frame["category"].map(d["mean_transit_days"]).to_numpy() - 1)
    frame["dispatch_date"] = frame["order_date"] + pd.to_timedelta(lag, "D")
    frame["delivered_date"] = frame["dispatch_date"] + pd.to_timedelta(transit, "D")
    frame["lead_time_days"] = lag + transit
    return frame, dict(d)


def load_fulfilment(seed=SEED):
    """One row per order in load_orders: minutes to pick and pack, days to dispatch and deliver."""
    return _fulfilment(seed)[0].copy()


PACKING_DGP = {
    # M/M/c on one line, 08:00 to 16:00. Every day starts empty, so waits run a little under steady state.
    "arrivals_per_hour": {"Monday": 62.0, "Tuesday": 44.0, "Wednesday": 40.0, "Thursday": 38.0, "Friday": 34.0},
    "packers": {"Monday": 6, "Tuesday": 5, "Wednesday": 4, "Thursday": 4, "Friday": 4},
    "service_rate_per_hour": 12.0,
    "open_hour": 8, "shift_hours": 8, "start": "2025-09-29", "weeks": 13, "wage_per_hour": 14.0,
}


def erlang_c(arrivals, service, c):
    """M/M/c steady state: P(wait), mean wait, and mean in the system. Same time unit as the rates."""
    a, rho = arrivals / service, arrivals / (service * c)
    if rho >= 1:
        return {"rho": rho, "p_wait": 1.0, "mean_wait": float("inf"), "mean_in_system": float("inf")}
    term, total = 1.0, 1.0
    for k in range(1, c):
        term *= a / k
        total += term
    last = term * a / c / (1 - rho)
    p_wait = last / (total + last)
    wait = p_wait / (c * service - arrivals)
    return {"rho": rho, "p_wait": p_wait, "mean_wait": wait, "mean_in_system": arrivals * (wait + 1 / service)}


@lru_cache(maxsize=1)
def _packing_line(seed=SEED):
    d = PACKING_DGP
    rng = _stream("packing_line", seed)
    rows, ref = [], 0
    for day in pd.date_range(d["start"], periods=d["weeks"] * 7, freq="D"):
        name = day.day_name()
        if name not in d["arrivals_per_hour"]:
            continue
        rate, c = d["arrivals_per_hour"][name], d["packers"][name]
        n = rng.poisson(rate * d["shift_hours"])
        arrivals = np.sort(rng.uniform(0, d["shift_hours"] * 60, n))
        service = rng.exponential(60 / d["service_rate_per_hour"], n)
        free = np.zeros(c)
        opening = day + pd.Timedelta(hours=d["open_hour"])
        for arrive, minutes in zip(arrivals, service):
            ref += 1
            packer = int(np.argmin(free))
            begin = max(arrive, free[packer])
            free[packer] = begin + minutes
            rows.append((ref, opening, name, packer + 1, arrive, begin, begin + minutes))
    frame = pd.DataFrame(rows, columns=["parcel_id", "opening", "weekday", "packer", "a", "b", "e"])
    for col, source in (("arrived", "a"), ("pack_start", "b"), ("pack_end", "e")):
        frame[col] = frame["opening"] + pd.to_timedelta(frame[source], "m")
    frame["wait_minutes"] = (frame["b"] - frame["a"]).round(3)
    frame["pack_minutes"] = (frame["e"] - frame["b"]).round(3)
    frame["date"] = frame["opening"].dt.normalize()
    frame = frame[["parcel_id", "date", "weekday", "packer", "arrived", "pack_start", "pack_end", "wait_minutes", "pack_minutes"]]
    # Truth in minutes.
    theory = {}
    for name, rate in d["arrivals_per_hour"].items():
        q = erlang_c(rate, d["service_rate_per_hour"], d["packers"][name])
        q["mean_wait_minutes"] = q.pop("mean_wait") * 60
        theory[name] = q
    return frame, {**d, "erlang_c": theory, "realised_mean_wait_minutes": frame.groupby("weekday")["wait_minutes"].mean().to_dict()}


def load_packing_line(seed=SEED):
    """One row per parcel over 13 weeks of weekdays: arrival, start and end of packing, and who packed it."""
    return _packing_line(seed)[0].copy()


# sku: category, unit cost, unit price, salvage, weekly demand level, christmas-only line, order cost, lead-time days
PRODUCT_DGP = {
    "KIT-01": ("kitchen", 18.0, 42.0, 9.0, 60.0, False, 40.0, 21.0),
    "KIT-02": ("kitchen", 6.0, 16.0, 3.0, 110.0, False, 40.0, 14.0),
    "KIT-03": ("kitchen", 12.0, 34.0, 4.0, 90.0, True, 60.0, 35.0),
    "TEX-01": ("textiles", 9.0, 26.0, 4.0, 85.0, False, 35.0, 28.0),
    "TEX-02": ("textiles", 21.0, 58.0, 10.0, 35.0, False, 35.0, 28.0),
    "TEX-03": ("textiles", 8.0, 24.0, 2.0, 140.0, True, 60.0, 42.0),
    "LGT-01": ("lighting", 14.0, 39.0, 6.0, 45.0, False, 45.0, 35.0),
    "LGT-02": ("lighting", 28.0, 72.0, 12.0, 20.0, False, 45.0, 35.0),
    "LGT-03": ("lighting", 10.0, 30.0, 3.0, 120.0, True, 60.0, 49.0),
    "FUR-01": ("furniture", 85.0, 190.0, 45.0, 8.0, False, 120.0, 56.0),
    "FUR-02": ("furniture", 140.0, 320.0, 80.0, 4.0, False, 120.0, 63.0),
    "FUR-03": ("furniture", 60.0, 150.0, 30.0, 12.0, False, 120.0, 49.0),
}
INVENTORY_DGP = {"demand_dispersion_k": 8.0, "season_weeks": 8, "staple_season_lift": .60, "holding_rate_per_year": .25,
                 "lead_time_sigma": .25, "service_level": .95, "po_interval_weeks": 8}


def _season_mask(weeks, n_weeks):
    """Weeks in the selling season: the n_weeks Mondays ending at Christmas."""
    xmas = pd.to_datetime({"year": weeks.year, "month": 12, "day": 25}).to_numpy()
    days = (xmas - weeks.to_numpy()) / np.timedelta64(1, "D")
    return (days >= 0) & (days < n_weeks * 7)


@lru_cache(maxsize=1)
def _products(seed=SEED):
    d = INVENTORY_DGP
    rng = _stream("products", seed)
    weeks = pd.date_range(MARKETING_START, END, freq="W-MON")
    season = _season_mask(weeks, d["season_weeks"])
    products, demand, purchases, truth_sku = [], [], [], {}
    normal = NormalDist()
    z_service = normal.inv_cdf(d["service_level"])
    for sku, (category, cost, price, salvage, level, christmas, order_cost, lead_days) in PRODUCT_DGP.items():
        mean = level * season if christmas else level * (1 + d["staple_season_lift"] * season)
        k = d["demand_dispersion_k"]
        # Gamma-Poisson draw, written so that a zero mean is simply zero.
        units = rng.poisson(rng.gamma(k, np.where(mean > 0, mean / k, 0)))
        demand.append(pd.DataFrame({"week": weeks, "sku": sku, "units": units}))
        holding = cost * d["holding_rate_per_year"]
        products.append((sku, category, cost, price, salvage, holding, order_cost, christmas))

        po_weeks = pd.date_range(MARKETING_START, END, freq=f"{d['po_interval_weeks']}W-MON")
        shrink = d["lead_time_sigma"] ** 2 / 2
        lead = np.maximum(np.round(lead_days * rng.lognormal(-shrink, d["lead_time_sigma"], len(po_weeks))), 1).astype(int)
        purchases.append(pd.DataFrame({"sku": sku, "ordered": po_weeks, "lead_time_days": lead}))

        var = mean + mean ** 2 / k
        season_mean, season_sd = mean[season][:d["season_weeks"]].sum(), var[season][:d["season_weeks"]].sum() ** .5
        cu, co = price - cost, cost - salvage
        fractile = cu / (cu + co)
        one_year = weeks.year == 2025
        annual, weekly_var = mean[one_year].sum(), var[one_year].mean()
        weekly_mean = annual / one_year.sum()
        lead_weeks = lead_days / 7
        lead_sd_weeks = lead_weeks * (np.exp(d["lead_time_sigma"] ** 2) - 1) ** .5
        truth_sku[sku] = {"weekly_level": level, "christmas_only": christmas, "season_mean": season_mean, "season_sd": season_sd,
                          "critical_fractile": fractile,
                          "newsvendor_q": NormalDist(season_mean, season_sd).inv_cdf(fractile),
                          "annual_demand_2025": annual, "eoq": (2 * annual * order_cost / holding) ** .5,
                          "mean_lead_time_days": lead_days,
                          "safety_stock": z_service * (lead_weeks * weekly_var + weekly_mean ** 2 * lead_sd_weeks ** 2) ** .5}
    products = pd.DataFrame(products, columns=["sku", "category", "unit_cost", "unit_price", "salvage_value",
                                               "holding_cost_per_year", "order_cost", "christmas_only"])
    demand = pd.concat(demand, ignore_index=True)
    purchases = pd.concat(purchases, ignore_index=True)
    purchases["received"] = purchases["ordered"] + pd.to_timedelta(purchases["lead_time_days"], "D")
    purchases = purchases.sort_values(["ordered", "sku"], ignore_index=True)
    purchases.insert(0, "po_id", np.arange(1, len(purchases) + 1))
    return (products, demand, purchases), {**d, "by_sku": truth_sku}


def load_products(seed=SEED):
    """One row per SKU: costs and prices, for newsvendor and EOQ."""
    return _products(seed)[0][0].copy()


def load_product_demand(seed=SEED):
    """One row per SKU per week, 2023 to 2025: units demanded."""
    return _products(seed)[0][1].copy()


def load_purchase_orders(seed=SEED):
    """One row per supplier order: when ordered, when received, and the lead time."""
    return _products(seed)[0][2].copy()


_TRUTH = {"subscriptions": _subscriptions, "club": _club, "marketing": _marketing, "geo_test": _geo_test,
          "touch_paths": _touch_paths, "repeat_log": _repeat_log, "fulfilment": _fulfilment,
          "packing_line": _packing_line, "products": _products}


def load_truth(table, seed=SEED):
    """The DGP's parameters and realised true effects for a table, as a dict. Tables: TRUTH_TABLES."""
    if table == "journeys":
        return deepcopy(_journeys(4000, seed)[1])
    return deepcopy(_TRUTH[table](seed)[1])


TRUTH_TABLES = sorted([*_TRUTH, "journeys"])


if __name__ == "__main__":
    print(len(load_customers()), "customers,", len(load_orders()), "orders,", len(load_sessions()), "sessions")
    print(load_weekly_units().describe().round(0).to_string())
