# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["numpy", "pandas", "matplotlib", "scipy", "statsmodels", "lifelines"]
# ///
"""Chapter 7: when will a subscriber leave, and does the welcome call delay it?

Run from this folder with: uv run ch07_survival.py
"""
import contextlib
import io
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from lifelines import AalenJohansenFitter, CoxPHFitter, CoxTimeVaryingFitter, KaplanMeierFitter
from lifelines.statistics import multivariate_logrank_test
from lifelines.utils import restricted_mean_survival_time
from scipy.optimize import minimize
from scipy.special import betaln

import chartstyle as cs
from retail import CHANNELS, PLANS, SEED, load_subscription_periods, load_subscriptions, load_truth

cs.apply()

# %% load
subs, periods, truth = load_subscriptions(), load_subscription_periods(), load_truth("subscriptions")
print(len(subs), "subscriptions,", len(periods), "person-periods")
print(subs[["subscription_id", "channel", "plan", "welcome_call", "start_date", "event_type", "duration_days"]].head(3).to_string(index=False))
print(subs.event_type.fillna("still subscribed").value_counts().to_string())
print(subs.groupby("channel").welcome_call.mean().loc[CHANNELS].round(3).to_string())

# %% censoring
print(f"mean days, churned only:           {subs[subs.event == 1].duration_days.mean():.1f}")
print(f"mean days, censored counted as end: {subs.duration_days.mean():.1f}")
km_all = KaplanMeierFitter().fit(subs.duration_days, subs.event)
HORIZON = 1080
capped_truth = subs.true_duration_days.clip(upper=HORIZON).mean()
print(f"Kaplan-Meier median:               {km_all.median_survival_time_:.0f}   truth {subs.true_duration_days.median():.0f}")
print(f"Kaplan-Meier mean to day {HORIZON}:      {restricted_mean_survival_time(km_all, t=HORIZON):.1f}   truth {capped_truth:.1f}")
print(f"truth, uncapped mean:              {subs.true_duration_days.mean():.1f}   (longest {subs.true_duration_days.max()} days; the data stop at {subs.duration_days.max()})")

# %% km_channel
fig, ax = plt.subplots()
for channel in CHANNELS:
    part = subs[subs.channel == channel]
    km = KaplanMeierFitter().fit(part.duration_days, part.event)
    curve = km.survival_function_.iloc[:, 0] * 100
    ax.step(curve.index, curve, where="post", color=cs.CHANNEL_COLOUR[channel])
    band = km.confidence_interval_ * 100
    ax.fill_between(band.index, band.iloc[:, 0], band.iloc[:, 1], step="post", color=cs.CHANNEL_COLOUR[channel], alpha=.15, lw=0)
    at_360 = km.predict(360)
    print(f"{channel:12s} n {len(part):5d}  median {km.median_survival_time_:6.0f}  still subscribed at 360 days {at_360:.1%}")
    last = curve.loc[:HORIZON].iloc[-1]
    ax.text(HORIZON + 8, last + {"organic": 1.5, "referral": -1.5}.get(channel, 0), channel.replace("_", " "), color=cs.SECONDARY, va="center")
ax.set_xlim(0, HORIZON + 130)
ax.set_ylim(0, 100)
ax.set_xticks(range(0, HORIZON + 1, 180))
ax.set_xlabel("Days since the box started")
ax.set_ylabel("Still subscribed (%)")
ax.set_title("Paid social subscribers leave first and email subscribers last")
cs.save(fig, "applied-survival-km-channel.png")

test = multivariate_logrank_test(subs.duration_days, subs.channel, subs.event)
print(f"log-rank across four channels: chi2 {test.test_statistic:.1f} on {test.degrees_of_freedom} df, p = {test.p_value:.1e}")

# %% cox_single
# From here the event is a cancel, and a downgrade ends a subscriber's time at risk, because the question is about cancels.
subs["cancel"] = (subs.event_type == "cancel").astype(int)
for channel in ("paid_social", "email", "referral"):
    subs[channel] = (subs.channel == channel).astype(int)
subs["large"] = (subs.plan == "large").astype(int)
CONFOUNDERS = ["paid_social", "email", "referral", "large"]

alone = CoxPHFitter().fit(subs[["welcome_call", "duration_days", "cancel"]], "duration_days", "cancel")
single = CoxPHFitter().fit(subs[["welcome_call", *CONFOUNDERS, "duration_days", "cancel"]], "duration_days", "cancel")
print(f"welcome call HR, nothing adjusted:    {alone.hazard_ratios_['welcome_call']:.3f}")
print(f"welcome call HR, channel and plan:    {single.hazard_ratios_['welcome_call']:.3f}")
print(single.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%"]].round(3).to_string())

# check_assumptions prints a long report: keep its table and the advice line for the failing covariate.
report = io.StringIO()
with contextlib.redirect_stdout(report), warnings.catch_warnings():
    warnings.simplefilter("ignore")
    single.check_assumptions(subs[["welcome_call", *CONFOUNDERS, "duration_days", "cancel"]], p_value_threshold=.01, show_plots=False)
lines = report.getvalue().splitlines()
print("\n".join(line for line in lines if line.strip().startswith(("welcome_call", "1. Variable", "test_name", "paid_social", "email", "referral", "large"))))


# %% wear_off
def episodes(frame, cuts=(90,)):
    """Long form for CoxTimeVaryingFitter: split each subscriber at the given days and at their own price rise."""
    rows = []
    for r in frame.itertuples():
        marks = {c for c in cuts if 0 < c < r.duration_days}
        if r.price_rise_day == r.price_rise_day and 0 < r.price_rise_day < r.duration_days:
            marks.add(r.price_rise_day)
        points = [0, *sorted(marks), r.duration_days]
        for a, b in zip(points[:-1], points[1:]):
            rows.append((r.subscription_id, a, b, int(b == r.duration_days and r.cancel), r.welcome_call,
                         int(r.price_rise_day == r.price_rise_day and a >= r.price_rise_day),
                         r.paid_social, r.email, r.referral, r.large))
    return pd.DataFrame(rows, columns=["id", "start", "stop", "cancel", "call", "rise", *CONFOUNDERS])


def fit_tv(long, covariates):
    fitter = CoxTimeVaryingFitter()
    fitter.fit(long[["id", "start", "stop", "cancel", *covariates]], id_col="id", event_col="cancel", start_col="start", stop_col="stop")
    return fitter


BANDS = [(0, 90), (90, 180), (180, 360), (360, 100000)]
long = episodes(subs, cuts=[b[0] for b in BANDS[1:]])
names = []
for low, high in BANDS:
    name = f"call_{low}_{high}"
    long[name] = long.call * ((long.start >= low) & (long.start < high)).astype(int)
    names.append(name)
bands = fit_tv(long, [*names, "rise", *CONFOUNDERS]).summary.loc[names, ["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%"]]
bands.columns = ["hr", "low", "high"]
bands.index = ["0-90", "90-180", "180-360", "360+"]
print(bands.round(3).to_string())

fig, ax = plt.subplots(figsize=(8, 3.6))
y = np.arange(len(bands))[::-1]
ax.hlines(y, bands.low, bands.high, color=cs.BLUE, lw=2)
ax.plot(bands.hr, y, "o", color=cs.BLUE, ms=7)
ax.axvline(1, color=cs.BASELINE, lw=1)
ax.axvline(single.hazard_ratios_["welcome_call"], color=cs.ORANGE, lw=1.5)
ax.text(single.hazard_ratios_["welcome_call"] - .012, -.42, "single HR", color=cs.ORANGE, ha="right", va="center")
ax.set_yticks(y, [f"Days {b}" for b in bands.index])
ax.set_ylim(-.65, len(bands) - .5)
ax.grid(False)
ax.grid(True, axis="x")
ax.set_xlabel("Hazard ratio, welcome call against no call, with 95% interval")
ax.set_title("The call works for three months, then stops: one number hides that")
cs.save(fig, "applied-survival-wear-off.png")

# %% cox_timevarying
long = episodes(subs)
long["call_early"] = long.call * (long.start < 90).astype(int)
long["call_late"] = long.call * (long.start >= 90).astype(int)
tv = fit_tv(long, ["call_early", "call_late", "rise", *CONFOUNDERS])
table = tv.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%"]].copy()
table.columns = ["estimate", "low", "high"]
table["truth"] = [truth["hr_welcome_early"], truth["hr_welcome_late"], truth["hr_price_rise"],
                  truth["hr_channel"]["paid_social"], truth["hr_channel"]["email"], truth["hr_channel"]["referral"], truth["hr_plan"]["large"]]
print(len(long), "episodes")
print(table.round(3).to_string())


# %% seeds
def early_late(seed):
    frame = load_subscriptions(seed)
    frame["cancel"] = (frame.event_type == "cancel").astype(int)
    for channel in ("paid_social", "email", "referral"):
        frame[channel] = (frame.channel == channel).astype(int)
    frame["large"] = (frame.plan == "large").astype(int)
    ep = episodes(frame)
    ep["call_early"] = ep.call * (ep.start < 90).astype(int)
    ep["call_late"] = ep.call * (ep.start >= 90).astype(int)
    return fit_tv(ep, ["call_early", "call_late", "rise", *CONFOUNDERS]).hazard_ratios_


runs = pd.DataFrame([early_late(SEED + i) for i in range(1, 21)])
check = pd.DataFrame({"mean of 20 seeds": runs.mean(), "lowest": runs.min(), "highest": runs.max()})
print(check.loc[["call_early", "call_late", "rise"]].round(3).to_string())

# %% discrete_time
periods["paid_social"] = (periods.channel == "paid_social").astype(int)
periods["email"] = (periods.channel == "email").astype(int)
periods["referral"] = (periods.channel == "referral").astype(int)
periods["large"] = (periods.plan == "large").astype(int)
periods["welcome_late"] = periods.welcome_call - periods.welcome_early
periods["log_month"] = np.log(periods.tenure_month)
FORMULA = "cancel ~ log_month + welcome_early + welcome_late + price_rise_active + paid_social + email + referral + large"
logit = smf.logit(FORMULA, periods).fit(disp=0)
print(f"mean monthly cancel hazard {periods.cancel.mean():.3f}")
compare = pd.DataFrame({"logit odds ratio": np.exp(logit.params)}).drop(["Intercept", "log_month"])
compare["Cox hazard ratio"] = tv.hazard_ratios_.rename({"call_early": "welcome_early", "call_late": "welcome_late", "rise": "price_rise_active"})
print(compare.round(3).to_string())
print(f"coefficient on log(tenure month) {logit.params['log_month']:.3f}; a Weibull of shape .75 implies about {.75 - 1:.2f}")


# %% competing
rows = []
for plan in PLANS:
    part = subs[subs.plan == plan]
    coded = part.event_type.map({"cancel": 1, "downgrade": 2}).fillna(0).astype(int)
    for code, label in ((1, "cancel"), (2, "downgrade")):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            aj = AalenJohansenFitter(calculate_variance=False).fit(part.duration_days, coded, event_of_interest=code)
        rows.append({"plan": plan, "event": label, "by_day_720": aj.predict(720)})
    km = KaplanMeierFitter().fit(part.duration_days, coded == 1)
    rows.append({"plan": plan, "event": "cancel, 1 - KM with downgrades censored", "by_day_720": 1 - km.predict(720)})
print(pd.DataFrame(rows).round(3).to_string(index=False))


# %% sbg
def sbg_survival(a, b, t):
    """Shifted-beta-geometric survivor function, as in chapter 3."""
    t = np.asarray(t, dtype=float)
    return np.exp(betaln(a, b + t) - betaln(a, b))


def sbg_fit(survival):
    survival = np.asarray(survival, dtype=float)
    n = len(survival) - 1
    died = -np.diff(survival)

    def negative_ll(log_params):
        a, b = np.exp(log_params)
        s = sbg_survival(a, b, np.arange(n + 1))
        return -(died * np.log(-np.diff(s))).sum() - survival[n] * np.log(s[n])

    return np.exp(minimize(negative_ll, [0, 0], method="Nelder-Mead", options=dict(xatol=1e-5, fatol=1e-8)).x)


months = np.arange(37)
actual = km_all.predict(months * 30).to_numpy()
calibrate = 13
a, b = sbg_fit(actual[:calibrate])
forecast = sbg_survival(a, b, months)
print(f"sBG on months 0 to {calibrate - 1}: alpha {a:.3f}, beta {b:.3f}")
for t in (12, 18, 24, 30, 36):
    print(f"month {t:2d}  Kaplan-Meier {actual[t]:.3f}  sBG forecast {forecast[t]:.3f}")

# %% standardise
HOLD = 24


def standardised(model, frame):
    """Average predicted survival over the subscribers we have, with everyone called and with nobody called."""
    mix = frame.groupby(["paid_social", "email", "referral", "large"]).size().rename("n").reset_index()
    mix["n"] = mix.n / mix.n.sum()
    grid = mix.merge(pd.DataFrame({"tenure_month": np.arange(1, 37)}), how="cross")
    grid["log_month"] = np.log(grid.tenure_month)
    grid["price_rise_active"] = 0
    out = {}
    for call in (0, 1):
        g = grid.assign(welcome_early=call * (grid.tenure_month <= 3).astype(int), welcome_late=call * (grid.tenure_month > 3).astype(int))
        g["survive"] = 1 - model.predict(g)
        g["s"] = g.groupby(["paid_social", "email", "referral", "large"]).survive.cumprod()
        out[call] = g.groupby("tenure_month").apply(lambda x: (x.s * x.n).sum(), include_groups=False).to_numpy()
    return out[0], out[1]


def true_curves(frame):
    """The same two curves from the generator's parameters: no price rise, no downgrades."""
    k, scale = truth["weibull_shape"], truth["weibull_scale_days"]
    days = np.arange(1, 37) * 30
    H0 = (days / scale) ** k
    H90 = (90 / scale) ** k
    called = np.where(days <= 90, truth["hr_welcome_early"] * H0, truth["hr_welcome_early"] * H90 + (H0 - H90))
    base = frame.channel.map(truth["hr_channel"]).to_numpy() * frame.plan.map(truth["hr_plan"]).to_numpy()
    return np.exp(-np.outer(base, H0)).mean(axis=0), np.exp(-np.outer(base, called)).mean(axis=0)


unit = periods.drop(columns=["channel", "plan"]).merge(subs[["subscription_id"]], on="subscription_id")
none, called = standardised(logit, subs.assign(**{c: subs[c] for c in CONFOUNDERS}))
true_none, true_called = true_curves(subs)
months_gained = lambda s0, s1, h: (s1[:h] - s0[:h]).sum()      # survival summed over months = months subscribed

rng = np.random.default_rng(SEED)
by_id = {i: g for i, g in periods.groupby("subscription_id").indices.items()}
ids = np.array(list(by_id))
boot = []
for _ in range(200):
    pick = rng.choice(ids, len(ids))
    rows = periods.iloc[np.concatenate([by_id[i] for i in pick])]
    s0, s1 = standardised(smf.logit(FORMULA, rows).fit(disp=0), subs.set_index("subscription_id").loc[pick].reset_index())
    boot.append((s1[11] - s0[11], s1[HOLD - 1] - s0[HOLD - 1], months_gained(s0, s1, HOLD)))
low, high = np.percentile(boot, [2.5, 97.5], axis=0)
print(f"{'':28s}{'estimate':>9s}{'95% interval':>18s}{'truth':>8s}")
print(f"{'gain in survival, month 12':28s}{called[11] - none[11]:9.3f}{low[0]:10.3f} to{high[0]:6.3f}{true_called[11] - true_none[11]:8.3f}")
print(f"{'gain in survival, month 24':28s}{called[23] - none[23]:9.3f}{low[1]:10.3f} to{high[1]:6.3f}{true_called[23] - true_none[23]:8.3f}")
gain = months_gained(none, called, HOLD)
print(f"{'box-months gained in 24':28s}{gain:9.2f}{low[2]:10.2f} to{high[2]:6.2f}{months_gained(true_none, true_called, HOLD):8.2f}")
crude = {c: KaplanMeierFitter().fit(g.duration_days, g.cancel).predict(360) for c, g in subs.groupby("welcome_call")}
print(f"crude gap at day 360, no adjustment: {crude[1] - crude[0]:.3f}")

fig, ax = plt.subplots()
x = np.arange(1, 37)
ax.plot(x, called * 100, color=cs.BLUE)
ax.plot(x, none * 100, color=cs.ORANGE)
ax.plot(x, true_called * 100, color=cs.BLUE, lw=1, ls=":")
ax.plot(x, true_none * 100, color=cs.ORANGE, lw=1, ls=":")
ax.axvline(3, color=cs.BASELINE, lw=1)
ax.text(3.3, 8, "The call stops working at 90 days", color=cs.SECONDARY)
ax.text(36.3, called[-1] * 100 + .8, "everyone called", color=cs.BLUE, va="center")
ax.text(36.3, none[-1] * 100 - .8, "nobody called", color=cs.ORANGE, va="center")
ax.set_xlim(0, 44)
ax.set_ylim(0, 100)
ax.set_xticks(range(0, 37, 6))
ax.set_xlabel("Months since the box started (dotted: the generator's true curves)")
ax.set_ylabel("Not yet cancelled (%)")
ax.set_title("The effect is short but the gap it opens stays open")
cs.save(fig, "applied-survival-standardised.png")

# %% price_call
MARGIN = .35                            # as in chapter 3, assumed
CALL_COST = 4.0                         # assumed: fifteen minutes of a loaded agent, pounds per call reached
mean_price = subs.plan.map({p: v[0] for p, v in PLANS.items()}).mean()
print(f"margin per box-month at pre-rise prices £{mean_price * MARGIN:.2f}; gain per call reached £{gain * mean_price * MARGIN:.2f}, assumed cost £{CALL_COST:.2f}")
print(f"at the interval's ends: £{low[2] * mean_price * MARGIN:.2f} to £{high[2] * mean_price * MARGIN:.2f}")
uncalled = subs[subs.welcome_call == 0].channel.value_counts().loc[CHANNELS]
print(uncalled.to_string())

# %% price_rise
reason = subs[subs.event_type == "cancel"].copy()
reason["after"] = reason.price_rise_day.notna() & (reason.duration_days > reason.price_rise_day)
share = reason.groupby("after").churn_reason.apply(lambda x: (x == "price").mean())
print(f"cancels giving price as the reason: {share[False]:.1%} before the rise, {share[True]:.1%} after")
print(f"HR implied by the reason codes alone: {(1 - share[False]) / (1 - share[True]):.2f}")

at_rise = subs[subs.price_rise_day.notna() & (subs.duration_days > subs.price_rise_day)]
print(len(at_rise), "subscribers on the books on the day of the rise")
rows = []
for h in (6, 12, 24):
    totals = {0: 0.0, 1: 0.0}
    for r in at_rise.itertuples():
        start = int(r.price_rise_day // 30) + 1
        future = pd.DataFrame({"tenure_month": np.arange(start, start + h)})
        future["log_month"] = np.log(future.tenure_month)
        future = future.assign(paid_social=r.paid_social, email=r.email, referral=r.referral, large=r.large, welcome_early=0, welcome_late=r.welcome_call)
        old, new = PLANS[r.plan]
        for rise, price in ((0, old), (1, new)):
            s = (1 - logit.predict(future.assign(price_rise_active=rise))).cumprod().to_numpy()
            totals[rise] += (s * (price - old * (1 - MARGIN))).sum()
    rows.append({"months": h, "margin_no_rise": totals[0] / len(at_rise), "margin_rise": totals[1] / len(at_rise)})
print(pd.DataFrame(rows).round(2).to_string(index=False))
