# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["numpy", "pandas", "matplotlib", "scipy", "pymc-marketing==1.3.0", "nutpie"]
# ///
"""Chapter 9: where should next quarter's budget go, and what is a new customer worth?

Run from this folder with: uv run ch09_marketing_measurement.py
Takes about five minutes, nearly all of it the three MMM fits. Add --seeds for the extra-seed checks quoted in the note.
"""
import itertools
import logging
import math
import sys
import warnings

import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pymc_extras.prior import Prior
from pymc_marketing.clv import BetaGeoModel, GammaGammaModel
from pymc_marketing.mmm import MMM, GeometricAdstock, HillSaturation
from scipy.optimize import minimize
from scipy.special import betaln, gammaln, hyp2f1
from scipy.stats import mannwhitneyu

import chartstyle as cs
from retail import (CHANNELS, CUT, END, load_geo_test, load_marketing_weekly, load_product_demand, load_products,
                    load_repeat_log, load_touch_paths, load_truth)

cs.apply()
pd.set_option("display.width", 130)
warnings.filterwarnings("ignore")
logging.getLogger("pymc").setLevel(logging.ERROR)
SEED = 9
rng = np.random.default_rng(SEED)

# %% load
paths, touch_truth = load_touch_paths(), load_truth("touch_paths")
print(len(paths), "paths,", paths.converted.sum(), "conversions, conversion rate", round(paths.converted.mean(), 4))
print(paths[["path_id", "path", "n_touches", "converted", "value"]].head(4).to_string(index=False))


# %% last_touch
touches = paths.path.str.split(">")
converted = paths.converted == 1
last_touch = touches.str[-1][converted].value_counts(normalize=True).reindex(CHANNELS)
true_share = pd.Series(touch_truth["true_incremental_share"]).reindex(CHANNELS)
print(pd.DataFrame({"last_touch": last_touch, "true_incremental": true_share}).round(3).to_string())
by_last = paths.groupby(touches.str[-1]).agg(paths=("converted", "size"), conversion=("converted", "mean"),
                                             mean_intent=("true_intent", "mean"))
print(by_last.reindex(CHANNELS).round(3).to_string())


# %% shapley
def shapley_credit(channel_sets, outcome):
    """Shapley credit by channel. v(S) is the conversion rate of paths whose channel set is exactly S; v(empty) = 0."""
    groups = pd.DataFrame({"s": channel_sets, "y": outcome}).groupby("s").y.agg(["mean", "size"])
    value, size = groups["mean"].to_dict(), groups["size"].to_dict()
    credit = dict.fromkeys(CHANNELS, 0.0)
    for full, n in size.items():
        for k in full:
            rest = [c for c in full if c != k]
            for r in range(len(rest) + 1):
                for subset in itertools.combinations(rest, r):
                    s = frozenset(subset)
                    weight = math.factorial(len(s)) * math.factorial(len(full) - len(s) - 1) / math.factorial(len(full))
                    credit[k] += n * weight * (value.get(s | {k}, value.get(s, 0.0)) - value.get(s, 0.0))
    return pd.Series(credit)


channel_sets = touches.map(frozenset)
shapley = shapley_credit(channel_sets, paths.converted)
print("distinct channel sets:", channel_sets.nunique(), "| credit handed out:", round(shapley.sum(), 1))
decile = pd.qcut(paths.true_intent, 10, labels=False)
shapley_intent = sum(shapley_credit(channel_sets[decile == d], paths.converted[decile == d]) for d in range(10))
table = pd.DataFrame({"last_touch": last_touch, "shapley": shapley / shapley.sum(),
                      "shapley_within_intent": shapley_intent / shapley_intent.sum(), "true_incremental": true_share})
print(table.round(3).to_string())
print("true conversions from any touch:", round(sum(touch_truth["true_incremental_conversions"].values()), 1),
      "| would have converted untouched:", round(touch_truth["conversions_without_any_touch"], 1))


# %% causal_model
def fit_noisy_or(frame, use_intent):
    """Fit the generator's own form by maximum likelihood: P(convert) = 1 - (1 - baseline) * product of (1 - lift)."""
    counts = np.array([[p.count(c) for c in CHANNELS] for p in frame.path.str.split(">")], float)
    intent2 = frame.true_intent.to_numpy() ** 2 if use_intent else np.zeros(len(frame))
    y = frame.converted.to_numpy()

    def parts(theta):
        base = np.clip(np.exp(theta[0]) + np.exp(theta[1]) * intent2, 1e-6, .999)
        lift = 1 / (1 + np.exp(-theta[2:]))
        return base, lift, (1 - lift) ** counts

    def nll(theta):
        base, _, keep = parts(theta)
        p = np.clip(1 - (1 - base) * keep.prod(axis=1), 1e-9, 1 - 1e-9)
        return -(y * np.log(p) + (1 - y) * np.log(1 - p)).sum()

    theta = minimize(nll, [-3.5, -1.5, -3.5, -3.5, -3.5, -3.5], method="L-BFGS-B").x
    base, lift, keep = parts(theta)
    with_all = (1 - base) * keep.prod(axis=1)
    gained = np.array([((1 - base) * np.delete(keep, j, axis=1).prod(axis=1) - with_all).sum() for j in range(4)])
    return pd.Series(lift, CHANNELS), pd.Series(gained, CHANNELS)


lift_intent, gained_intent = fit_noisy_or(paths, use_intent=True)
lift_blind, gained_blind = fit_noisy_or(paths, use_intent=False)
print(pd.DataFrame({"true_lift": pd.Series(touch_truth["lift_per_touch"]), "lift_with_intent": lift_intent, "lift_no_intent": lift_blind,
                    "share_with_intent": gained_intent / gained_intent.sum(), "share_no_intent": gained_blind / gained_blind.sum(),
                    "true_share": true_share}).round(3).to_string())

# %% attribution_chart
fig, ax = plt.subplots(figsize=(8.5, 4))
series = [("Last touch", last_touch, cs.ORANGE, "o"), ("Shapley", shapley / shapley.sum(), cs.YELLOW, "s"),
          ("Noisy-or with intent", gained_intent / gained_intent.sum(), cs.AQUA, "^"), ("True incremental", true_share, cs.BLUE, "D")]
for i, c in enumerate(CHANNELS):
    ax.plot([0, .55], [i, i], color=cs.GRID, lw=.8, zorder=0)
    for name, values, colour, marker in series:
        ax.scatter(values[c], i, color=colour, marker=marker, s=70, zorder=3, label=name if i == 0 else None)
ax.set_yticks(range(4), [c.replace("_", " ").capitalize() for c in CHANNELS])
ax.invert_yaxis()
ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
ax.set_xlabel("Share of credit")
ax.set_title("Last touch gives paid social nearly half the credit; it earned about a sixth", loc="left")
ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(.5, -.18))
cs.save(fig, "applied-attribution-vs-truth.png")

# %% geo_test
geo, geo_truth = load_geo_test(), load_truth("geo_test")
print(geo.week.min().date(), "to", geo.week.max().date(), "| test starts", geo_truth["start"], "| geos", geo.geo.nunique(), "| cut", CUT.date())


def geo_lift(frame):
    """Pair by pair: holdout's pre-period, grown by its control's post/pre ratio, is what it would have done."""
    sums = frame.groupby(["pair", "holdout", "post"]).agg(revenue=("revenue", "sum"), spend=("spend_paid_social", "sum")).unstack("post")
    hold, ctrl = sums.xs(1, level="holdout"), sums.xs(0, level="holdout")
    lost = hold[("revenue", 0)] * ctrl[("revenue", 1)] / ctrl[("revenue", 0)] - hold[("revenue", 1)]
    saved = hold[("spend", 0)] * ctrl[("spend", 1)] / ctrl[("spend", 0)]     # holdout spend is zero, so we estimate it
    return lost, saved


lost, saved = geo_lift(geo)
iroas = lost.sum() / saved.sum()
pick = rng.integers(0, 10, (4000, 10))
boot = lost.to_numpy()[pick].sum(axis=1) / saved.to_numpy()[pick].sum(axis=1)
iroas_se = boot.std()
print(f"revenue lost {lost.sum():,.0f} (true {geo_truth['true_revenue_lost']:,.0f}) | spend saved {saved.sum():,.0f} (true {geo_truth['spend_saved']:,.0f})")
print(f"iROAS {iroas:.3f}, pair bootstrap 95% [{np.percentile(boot, 2.5):.2f}, {np.percentile(boot, 97.5):.2f}], true {geo_truth['true_iroas']:.3f}")
print("by pair:", (lost / saved).round(2).to_list())
naive = geo[(geo.post == 1) & (geo.holdout == 0)].revenue.sum() - geo[(geo.post == 1) & (geo.holdout == 1)].revenue.sum()
print(f"post-period control minus holdout, ignoring the pre-period: {naive:,.0f} of 'lost revenue'")

# %% transforms
weekly, marketing_truth = load_marketing_weekly(), load_truth("marketing")
SPEND = [f"spend_{c}" for c in CHANNELS]
after = (weekly.week >= CUT).to_numpy()


def adstock(x, alpha, l_max=8):
    """Geometric carryover, weights normalised to one, so the result stays on the spend scale."""
    weights = alpha ** np.arange(l_max)
    weights = weights / weights.sum()
    return np.convolve(np.concatenate([np.full(l_max - 1, x[0]), x]), weights, mode="valid")


def hill(x, K, slope, beta):
    """S-shaped saturation: beta is the ceiling, K the spend at half of it, slope how sharp the bend is."""
    return beta * x ** slope / (x ** slope + K ** slope)


pulse = np.r_[np.zeros(3), 1000.0, np.zeros(6)]
print("adstock of a single £1,000 week, alpha 0.30:", adstock(pulse, .30).round(0).tolist())
print("adstock of the same week, alpha 0.60:      ", adstock(pulse, .60).round(0).tolist())
paid = {k: marketing_truth[f"hill_{k}"]["paid_social"] for k in ("K", "slope")} | {"beta": marketing_truth["beta"]["paid_social"]}
for x in (1000, 2500, 5000, 7300, 13000):
    print(f"paid social at £{x:>6,}/wk: true response £{hill(x, **paid):>6,.0f}, average ROAS {hill(x, **paid) / x:.2f}, "
          f"marginal ROAS {hill(x + 1, **paid) - hill(x, **paid):.2f}")
print(weekly[SPEND].corr().round(2).loc["spend_paid_social"].to_string())
print(pd.DataFrame({"before": weekly[~after][SPEND].mean(), "after": weekly[after][SPEND].mean(),
                    "min": weekly[SPEND].min(), "max": weekly[SPEND].max()}).round(0).to_string())

# %% naive_regression
design = np.column_stack([np.ones(len(weekly)), weekly[SPEND].to_numpy()])
ols = pd.Series(np.linalg.lstsq(design, weekly.revenue.to_numpy(), rcond=None)[0][1:], CHANNELS)
true_avg = {c: weekly[f"true_contribution_{c}"].sum() / weekly[f"spend_{c}"].sum() for c in CHANNELS}
print(pd.DataFrame({"ols_coefficient": ols, "true_average_roas": true_avg}).round(2).to_string())

# %% mmm
JIN_SATURATION = {"slope": Prior("Gamma", alpha=3, beta=1, dims="channel"), "kappa": Prior("Beta", alpha=2, beta=2, dims="channel"),
                  "beta": Prior("HalfNormal", sigma=1, dims="channel")}
JIN_ADSTOCK = {"alpha": Prior("Beta", alpha=3, beta=3, dims="channel")}


def fit_mmm(frame, lift_test=None, jin_priors=True, seed=SEED, target_accept=.99):
    X = frame[["week"] + SPEND].assign(t=np.arange(len(frame)))
    model = MMM(date_column="week", channel_columns=SPEND, target_column="revenue", control_columns=["t"], yearly_seasonality=6,
                adstock=GeometricAdstock(l_max=8, priors=JIN_ADSTOCK if jin_priors else None),
                saturation=HillSaturation(priors=JIN_SATURATION if jin_priors else None))
    model.build_model(X, frame.revenue)
    if lift_test is not None:
        model.add_lift_test_measurements(lift_test)
    model.fit(X, frame.revenue, chains=4, tune=3000, draws=2000, target_accept=target_accept, random_seed=seed, progressbar=False)
    return model


def curves(model):
    """Posterior draws of each channel's parameters, back on the scale of pounds."""
    post, scales = model.idata.posterior, model.get_scales_as_xarray()
    get = lambda name: post[name].stack(s=("chain", "draw")).transpose("s", "channel").to_numpy()
    return {"alpha": get("adstock_alpha"), "slope": get("saturation_slope"),
            "K": get("saturation_kappa") * scales["channel_scale"].to_numpy(),
            "beta": get("saturation_beta") * float(scales["target_scale"])}


def recovery(draws, frame, every=8):
    """Average ROAS after the cut and marginal ROAS at after-cut adstock, per kept draw and channel."""
    use = np.arange(0, draws["alpha"].shape[0], every)
    avg, marginal = np.zeros((len(use), 4)), np.zeros((len(use), 4))
    late = (frame.week >= CUT).to_numpy()
    for j, c in enumerate(CHANNELS):
        x = frame[f"spend_{c}"].to_numpy()
        for row, i in enumerate(use):
            K, s, b = draws["K"][i, j], draws["slope"][i, j], draws["beta"][i, j]
            ad = adstock(x, draws["alpha"][i, j])
            avg[row, j] = hill(ad, K, s, b)[late].sum() / x[late].sum()
            level = ad[late].mean()
            marginal[row, j] = hill(level + 1, K, s, b) - hill(level, K, s, b)
    return avg, marginal


def report(draws, avg, marginal, truth):
    rows = {}
    for j, c in enumerate(CHANNELS):
        rows[c] = {"roas": f"{np.median(avg[:, j]):.2f} [{np.percentile(avg[:, j], 5):.2f}, {np.percentile(avg[:, j], 95):.2f}]",
                   "true": round(truth["true_roas"][c]["after_cut"], 2),
                   "marginal": f"{np.median(marginal[:, j]):.2f} [{np.percentile(marginal[:, j], 5):.2f}, {np.percentile(marginal[:, j], 95):.2f}]",
                   "true_m": round(truth["true_marginal_roas_after_cut"][c], 2)}
    return pd.DataFrame(rows).T


def diagnostics(model):
    params = ["adstock_alpha", "saturation_slope", "saturation_kappa", "saturation_beta"]
    rhat = az.summary(model.idata.posterior, var_names=params)["r_hat"].astype(float)
    return (f"divergences {int(model.idata.sample_stats.diverging.sum())} of 8000, largest R-hat {rhat.max():.3f} on {rhat.idxmax()}, "
            f"largest for paid social {rhat[rhat.index.str.contains('paid_social')].max():.3f}")


default_fit = fit_mmm(weekly, jin_priors=False)
print("default priors:", diagnostics(default_fit))
default_draws = curves(default_fit)
default_avg, default_marginal = recovery(default_draws, weekly)
print(report(default_draws, default_avg, default_marginal, marketing_truth).to_string())

plain_fit = fit_mmm(weekly)
print("Jin priors:", diagnostics(plain_fit))
plain_draws = curves(plain_fit)
plain_avg, plain_marginal = recovery(plain_draws, weekly)
print(report(plain_draws, plain_avg, plain_marginal, marketing_truth).to_string())

# %% mmm_with_geo
test_weeks = weekly.week.between(geo.week[geo.post == 1].min(), geo.week.max())
test_spend = weekly.loc[test_weeks, "spend_paid_social"].mean()
lift_test = pd.DataFrame({"channel": ["spend_paid_social"], "x": [test_spend], "delta_x": [-test_spend],
                          "delta_y": [-iroas * test_spend], "sigma": [iroas_se * test_spend]})
print(lift_test.round(1).to_string(index=False))
geo_fit = fit_mmm(weekly, lift_test=lift_test)
print("Jin priors and geo test:", diagnostics(geo_fit))
geo_draws = curves(geo_fit)
geo_avg, geo_marginal = recovery(geo_draws, weekly)
print(report(geo_draws, geo_avg, geo_marginal, marketing_truth).to_string())
contrib = geo_fit.idata.posterior["channel_contribution"].isel(chain=0, draw=0).to_numpy() * float(geo_fit.get_scales_as_xarray()["target_scale"])
mine = np.column_stack([hill(adstock(weekly[f"spend_{c}"].to_numpy(), geo_draws["alpha"][0, j]), geo_draws["K"][0, j], geo_draws["slope"][0, j], geo_draws["beta"][0, j])
                        for j, c in enumerate(CHANNELS)])
print("our curve against the library's contribution, largest gap after week 8: £", round(float(np.abs(contrib - mine)[8:].max()), 2))
parameters = pd.DataFrame({
    "true": [marketing_truth["hill_K"]["paid_social"], marketing_truth["hill_slope"]["paid_social"], marketing_truth["beta"]["paid_social"], marketing_truth["adstock_alpha"]["paid_social"]],
    "no_geo": [np.median(plain_draws[k][:, 0]) for k in ("K", "slope", "beta", "alpha")],
    "with_geo": [np.median(geo_draws[k][:, 0]) for k in ("K", "slope", "beta", "alpha")]}, index=["K", "slope", "beta", "alpha"])
print(parameters.round(2).to_string())

# %% budget
after_ad = {c: adstock(weekly[f"spend_{c}"].to_numpy(), marketing_truth["adstock_alpha"][c])[after].mean() for c in CHANNELS}
true_curve = {c: {"K": marketing_truth["hill_K"][c], "slope": marketing_truth["hill_slope"][c], "beta": marketing_truth["beta"][c]} for c in CHANNELS}


def move_gain(draws, amount):
    """Weekly revenue change, per kept draw, of moving £amount from paid social to email at after-cut levels."""
    out = []
    for i in range(0, draws["alpha"].shape[0], 8):
        p_level = adstock(weekly["spend_paid_social"].to_numpy(), draws["alpha"][i, 0])[after].mean()
        e_level = adstock(weekly["spend_email"].to_numpy(), draws["alpha"][i, 2])[after].mean()
        drop = hill(p_level, draws["K"][i, 0], draws["slope"][i, 0], draws["beta"][i, 0]) - hill(p_level - amount, draws["K"][i, 0], draws["slope"][i, 0], draws["beta"][i, 0])
        rise = hill(e_level + amount, draws["K"][i, 2], draws["slope"][i, 2], draws["beta"][i, 2]) - hill(e_level, draws["K"][i, 2], draws["slope"][i, 2], draws["beta"][i, 2])
        out.append(rise - drop)
    return np.array(out)


rows = []
for amount in (250, 500, 1000, 2000, 4000):
    true_gain = (hill(after_ad["email"] + amount, **true_curve["email"]) - hill(after_ad["email"], **true_curve["email"])
                 - hill(after_ad["paid_social"], **true_curve["paid_social"]) + hill(after_ad["paid_social"] - amount, **true_curve["paid_social"]))
    gain = move_gain(geo_draws, amount)
    rows.append({"moved_per_week": amount, "true_gain": round(true_gain), "posterior_median": round(np.median(gain)),
                 "p5": round(np.percentile(gain, 5)), "p95": round(np.percentile(gain, 95)), "p_gain_positive": round((gain > 0).mean(), 3)})
print(pd.DataFrame(rows).to_string(index=False))
print("P(email marginal ROAS > paid social marginal ROAS):", round((geo_marginal[:, 2] > geo_marginal[:, 0]).mean(), 3))
total = sum(after_ad.values())


def true_revenue(x):
    return sum(hill(x[j], **true_curve[c]) for j, c in enumerate(CHANNELS))


now = np.array([after_ad[c] for c in CHANNELS])
best = minimize(lambda x: -true_revenue(x), now, bounds=[(1, total)] * 4, constraints={"type": "eq", "fun": lambda x: x.sum() - total}, method="SLSQP")
print("after-cut mean adstocked spend by channel:", pd.Series(now, CHANNELS).round(0).to_dict())
print("truth's best split of the same total:     ", pd.Series(best.x, CHANNELS).round(0).to_dict())
print(f"weekly revenue from media now £{true_revenue(now):,.0f}, at truth's best £{true_revenue(best.x):,.0f}")
products, demand = load_products().set_index("sku"), load_product_demand()
units = demand[demand.week.dt.year == 2025].groupby("sku").units.sum()
margin = ((products.unit_price - products.unit_cost) * units).sum() / (products.unit_price * units).sum()
break_even = 1 / margin
print(f"gross margin, 2025 demand at list prices {margin:.3f}, so an extra £1 pays back its margin at revenue ROAS {break_even:.2f}")
levels = np.linspace(1, 15000, 15000)
for c in CHANNELS:
    slope = np.diff(hill(levels, **true_curve[c]))
    print(f"  {c}: true marginal ROAS now {marketing_truth['true_marginal_roas_after_cut'][c]:.2f}, spend where it equals break-even £{levels[np.where(slope >= break_even)[0].max()]:,.0f}, spend now £{after_ad[c]:,.0f}")

# %% mmm_charts
fig, ax = plt.subplots(figsize=(8.5, 4.5))
grid = np.linspace(1, 14000, 200)


def band(draws, colour, label):
    curve = np.array([hill(grid, draws["K"][i, 0], draws["slope"][i, 0], draws["beta"][i, 0]) for i in range(0, draws["K"].shape[0], 8)])
    ax.fill_between(grid, *np.percentile(curve, [5, 95], axis=0), color=colour, alpha=.22, lw=0)
    ax.text(grid[-1] + 150, np.median(curve[:, -1]), label, color=colour, va="center")


band(plain_draws, cs.ORANGE, "Without geo test")
band(geo_draws, cs.AQUA, "With geo test")
ax.plot(grid, hill(grid, **true_curve["paid_social"]), color=cs.INK, lw=2)
ax.text(grid[-1] + 150, hill(grid[-1], **true_curve["paid_social"]) - 900, "True curve", color=cs.INK, va="center")
ax.plot([0, test_spend], [0, hill(test_spend, **true_curve["paid_social"])], color=cs.BLUE, lw=1.4, ls="--")
ax.text(test_spend + 250, 1900, "Holdout measures this\nchord, about £1.50 per £1", color=cs.BLUE, ha="left")
tangent = after_ad["paid_social"]
ax.scatter([tangent], [hill(tangent, **true_curve["paid_social"])], color=cs.INK, zorder=4)
ax.annotate("After the cut each extra\n£1 brings back about £0.70", (tangent, hill(tangent, **true_curve["paid_social"])), (tangent + 500, 6300), color=cs.SECONDARY)
ax.set_xlim(0, 17500)
ax.set_xlabel("Paid social, adstocked £ per week")
ax.set_ylabel("Weekly revenue from the channel (£)")
ax.set_title("A holdout pins down the average return; the budget turns on the slope further up", loc="left")
cs.save(fig, "applied-mmm-response-paid-social.png")

fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
fits = [("Without geo test", plain_avg, plain_marginal, cs.ORANGE, .14), ("With geo test", geo_avg, geo_marginal, cs.AQUA, -.14)]
for ax, kind, key in ((axes[0], "Average ROAS after the cut", 1), (axes[1], "Marginal ROAS after the cut", 2)):
    for j, c in enumerate(CHANNELS):
        true_value = marketing_truth["true_roas"][c]["after_cut"] if key == 1 else marketing_truth["true_marginal_roas_after_cut"][c]
        ax.scatter(true_value, j, color=cs.INK, marker="D", s=40, zorder=4, label="Truth" if j == 0 else None)
        for name, avg, marginal, colour, shift in fits:
            values = (avg if key == 1 else marginal)[:, j]
            ax.plot(np.percentile(values, [5, 95]), [j + shift] * 2, color=colour, lw=2)
            ax.scatter(np.median(values), j + shift, color=colour, s=30, zorder=3, label=name if j == 0 else None)
    ax.set_xscale("log")
    ax.set_title(kind, loc="left")
    ax.set_xlabel("£ of revenue per £ of spend, log scale")
axes[0].set_yticks(range(4), [c.replace("_", " ").capitalize() for c in CHANNELS])
axes[0].invert_yaxis()
axes[1].legend(frameon=False, loc="upper left")
fig.suptitle("The geo test narrows only the channel it tested", x=.02, ha="left", fontweight="bold")
cs.save(fig, "applied-mmm-roas-recovery.png")

# %% rfm
log, repeat_truth = load_repeat_log(), load_truth("repeat_log")
print(len(log), "orders,", log.customer_id.nunique(), "customers, mean value", round(log.value.mean(), 2))


def rfm_table(frame, end):
    """frequency = repeat orders; recency = weeks from first to last order; T = weeks from first order to end."""
    frame = frame[frame.order_date <= end]
    d = frame.groupby("customer_id").order_date.agg(["min", "max", "count"])
    return pd.DataFrame({"customer_id": d.index, "frequency": d["count"] - 1, "recency": (d["max"] - d["min"]).dt.days / 7,
                         "T": (end - d["min"]).dt.days / 7}).reset_index(drop=True)


rfm = rfm_table(log, END)
print(rfm.head(3).round(2).to_string(index=False))
print("no repeat order at all:", round((rfm.frequency == 0).mean(), 3), "| mean repeats", round(rfm.frequency.mean(), 2))


# %% bgnbd_mle
def bgnbd_nll(log_params, x, t_x, T):
    """Negative log likelihood of BG/NBD, Fader, Hardie and Lee (2005), equation 6, on the log scale."""
    r, alpha, a, b = np.exp(log_params)
    ln_a1 = gammaln(r + x) - gammaln(r) + r * np.log(alpha)
    ln_a2 = betaln(a, b + x) - betaln(a, b)
    ln_a3 = -(r + x) * np.log(alpha + T)
    ln_a4 = np.where(x > 0, np.log(a) - np.log(np.maximum(b + x - 1, 1e-12)) - (r + x) * np.log(alpha + t_x), -np.inf)
    return -(ln_a1 + ln_a2 + np.logaddexp(ln_a3, ln_a4)).sum()


def bgnbd_mle(table):
    fit = minimize(bgnbd_nll, np.log([.5, 5, 1, 2]), args=(table.frequency.to_numpy(), table.recency.to_numpy(), table["T"].to_numpy()), method="L-BFGS-B")
    return dict(zip(["r", "alpha", "a", "b"], np.exp(fit.x))), -fit.fun


mle, ll = bgnbd_mle(rfm)
print("maximum likelihood:", {k: round(v, 3) for k, v in mle.items()}, "| log likelihood", round(ll, 1))
print("truth:             ", {k: repeat_truth[k] for k in ("r", "alpha", "a", "b")})

# %% bgnbd_pymc
bg = BetaGeoModel()
bg.fit(rfm, chains=4, tune=1000, draws=1000, random_seed=SEED, progressbar=False)
print(az.summary(bg.idata.posterior, var_names=["r", "alpha", "a", "b"], ci_prob=.9)[["mean", "sd", "eti90_lb", "eti90_ub", "r_hat"]].to_string())
alive = bg.expected_probability_alive(rfm).mean(("chain", "draw")).to_numpy()
true_alive = log.groupby("customer_id").true_alive_at_end.first().reindex(rfm.customer_id).to_numpy()
u = mannwhitneyu(alive[true_alive == 1], alive[true_alive == 0]).statistic
print(f"mean P(alive) {alive.mean():.3f}, realised {repeat_truth['realised_alive_share']:.3f}, AUC {u / ((true_alive == 1).sum() * (true_alive == 0).sum()):.3f}")
for low, high in ((0, .25), (.25, .5), (.5, .75), (.75, .95), (.95, 1.01)):
    m = (alive >= low) & (alive < high)
    print(f"  P(alive) {low:.2f}-{min(high, 1):.2f}: {m.sum():>5} customers, truly alive {true_alive[m].mean():.3f}")

# %% holdout
SPLIT = pd.Timestamp("2025-06-30")
calibration = rfm_table(log, SPLIT)
fit_cal, _ = bgnbd_mle(calibration)
print("calibration fit to", SPLIT.date(), {k: round(v, 3) for k, v in fit_cal.items()})


def expected_future(params, table, t):
    """Fader, Hardie and Lee (2005), equation 10: expected repeat orders in the next t weeks for one customer."""
    r, alpha, a, b = params["r"], params["alpha"], params["a"], params["b"]
    x, t_x, T = table.frequency.to_numpy(), table.recency.to_numpy(), table["T"].to_numpy()
    top = (a + b + x - 1) / (a - 1) * (1 - ((alpha + T) / (alpha + T + t)) ** (r + x) * hyp2f1(r + x, b + x, a + b + x - 1, t / (alpha + T + t)))
    return top / (1 + (x > 0) * a / (b + x - 1) * ((alpha + T) / (alpha + t_x)) ** (r + x))


later = log[log.order_date > SPLIT]
horizon = (END - SPLIT).days / 7
expected = expected_future(fit_cal, calibration, horizon)
print(f"orders in holdout, {horizon:.1f} weeks: actual {len(later)}, forecast {expected.sum():.0f}, error {expected.sum() / len(later) - 1:+.1%}")
actual_by_customer = later.groupby("customer_id").size().reindex(calibration.customer_id).fillna(0).to_numpy()
print("correlation of customer forecasts with actual:", round(np.corrcoef(expected, actual_by_customer)[0, 1], 3))
groups = pd.DataFrame({"x": np.minimum(calibration.frequency, 7), "forecast": expected, "actual": actual_by_customer}).groupby("x").agg(customers=("actual", "size"), actual=("actual", "mean"), forecast=("forecast", "mean"))
print(groups.round(2).to_string())


def simulate_counts(params, T, generator, draws=20):
    """Repeat orders by customer, simulated from a fitted BG/NBD with the observed T values."""
    n = len(T) * draws
    T = np.repeat(T, draws)
    lam, p = generator.gamma(params["r"], 1 / params["alpha"], n), generator.beta(params["a"], params["b"], n)
    counts = generator.poisson(lam * T)
    survive = np.minimum(generator.geometric(p), 10 ** 6)     # orders until dropout, dropout follows an order
    return np.minimum(counts, survive)


sim = simulate_counts(mle, rfm["T"].to_numpy(), rng)
compare = pd.DataFrame({"actual": np.bincount(np.minimum(rfm.frequency, 7), minlength=8) / len(rfm), "fitted": np.bincount(np.minimum(sim, 7), minlength=8) / len(sim)})
print(compare.round(3).T.to_string())

weeks_grid = pd.date_range(SPLIT, END, freq="W-MON")
cum_actual = [(later.order_date <= d).sum() for d in weeks_grid]
cum_forecast = [expected_future(fit_cal, calibration, (d - SPLIT).days / 7).sum() for d in weeks_grid]
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(weeks_grid, cum_actual, color=cs.INK, lw=2)
ax.plot(weeks_grid, cum_forecast, color=cs.AQUA, lw=2, ls="--")
ax.text(weeks_grid[-1], cum_actual[-1] * 1.03, "Actual", color=cs.INK, ha="right")
ax.text(weeks_grid[-1], cum_forecast[-1] * .76, "BG/NBD forecast", color=cs.AQUA, ha="right")
ax.set_ylabel("Cumulative orders from these customers")
ax.set_title("Fitted to June 2025, BG/NBD forecasts the next six months of orders", loc="left")
cs.save(fig, "applied-bgnbd-holdout.png")

# %% gamma_gamma
repeat_only = log.sort_values("order_date").groupby("customer_id").apply(lambda d: d.value.iloc[1:].mean() if len(d) > 1 else np.nan, include_groups=False)
money = rfm.assign(monetary_value=rfm.customer_id.map(repeat_only)).query("frequency > 0")[["customer_id", "frequency", "monetary_value"]]
print(len(money), "customers with a repeat order; corr(frequency, monetary value):", round(money.frequency.corr(money.monetary_value), 3))
gg = GammaGammaModel()
gg.fit(money, chains=4, tune=1000, draws=1000, random_seed=SEED, progressbar=False)
print(az.summary(gg.idata.posterior, var_names=["p", "q", "v"], ci_prob=.9)[["mean", "sd", "eti90_lb", "eti90_ub", "r_hat"]].to_string())
print("truth:", {k: repeat_truth[k] for k in "pqv"}, "| true mean order value", repeat_truth["true_mean_order_value"])


def gamma_gamma_mle(table):
    """Fader and Hardie (2013), equation 1a, by maximum likelihood on customers with a repeat order."""
    x, z = table.frequency.to_numpy(), table.monetary_value.to_numpy()

    def nll(log_params):
        p, q, v = np.exp(log_params)
        return -(gammaln(p * x + q) - gammaln(p * x) - gammaln(q) + (p * x - 1) * np.log(z) + p * x * np.log(x) + q * np.log(v) - (p * x + q) * np.log(v + x * z)).sum()

    return dict(zip("pqv", np.exp(minimize(nll, np.log([1, 1, 10]), method="L-BFGS-B").x)))


gg_mle = gamma_gamma_mle(money)
print("maximum likelihood:", {k: round(v, 2) for k, v in gg_mle.items()}, "| implied mean", round(gg_mle["p"] * gg_mle["v"] / (gg_mle["q"] - 1), 2))
mean_value = (gg.idata.posterior["p"] * gg.idata.posterior["v"] / (gg.idata.posterior["q"] - 1)).stack(s=("chain", "draw")).to_numpy()
print(f"population mean order value: {np.median(mean_value):.2f} [{np.percentile(mean_value, 5):.2f}, {np.percentile(mean_value, 95):.2f}]; raw mean of all orders {log.value.mean():.2f}")
shrunk = gg.expected_customer_spend(money).mean(("chain", "draw")).to_numpy()
one = money.frequency == 1
print(f"one repeat order: raw sd {money.monetary_value[one].std():.1f} -> shrunk sd {shrunk[one.to_numpy()].std():.1f}")


# %% ltv
def expected_repeats_new(r, alpha, a, b, t):
    """Fader, Hardie and Lee (2005), equation 9: expected repeat orders for a new customer in t weeks."""
    return (a + b - 1) / (a - 1) * (1 - (alpha / (alpha + t)) ** r * hyp2f1(r, b, a + b - 1, t / (alpha + t)))


TRUE_DISCOUNT = load_truth("journeys")["monthly_discount"]
WEEKS_PER_MONTH = 52.18 / 12


def discounted_orders(r, alpha, a, b, months=60, discount=TRUE_DISCOUNT):
    grid = np.arange(0, months + 1) * WEEKS_PER_MONTH
    cumulative = np.array([expected_repeats_new(r, alpha, a, b, t) for t in grid])
    return 1 + (np.diff(cumulative, axis=0) / (1 + discount) ** np.arange(1, months + 1).reshape((-1,) + (1,) * (cumulative.ndim - 1))).sum(axis=0)


true_orders = discounted_orders(repeat_truth["r"], repeat_truth["alpha"], repeat_truth["a"], repeat_truth["b"])
long_orders = discounted_orders(repeat_truth["r"], repeat_truth["alpha"], repeat_truth["a"], repeat_truth["b"], months=1200)
print(f"truth at {TRUE_DISCOUNT:.0%} a month: over 60 months {true_orders:.2f} orders, £{true_orders * repeat_truth['true_mean_order_value']:.0f} revenue; "
      f"over 100 years {long_orders:.2f} orders, £{long_orders * repeat_truth['true_mean_order_value']:.0f} revenue")
for years in (1, 3, 5, 10, 25, 50):
    undiscounted = expected_repeats_new(repeat_truth["r"], repeat_truth["alpha"], repeat_truth["a"], repeat_truth["b"], years * 52.18)
    print(f"  at the true parameters, repeat orders by year {years:>2}: {undiscounted:.2f}, undiscounted")
poster = bg.idata.posterior
keep = {k: poster[k].stack(s=("chain", "draw")).to_numpy() for k in ("r", "alpha", "a", "b")}
orders = discounted_orders(keep["r"], keep["alpha"], keep["a"], keep["b"])
library = bg.expected_purchases_new_customer(pd.DataFrame({"customer_id": [0], "t": [52.18]})).mean().item()
print(f"library's mean repeat orders in year one {library:.3f}; our closed form {expected_repeats_new(keep['r'], keep['alpha'], keep['a'], keep['b'], 52.18).mean():.3f}")
revenue_ltv = orders * mean_value
ltv = revenue_ltv * margin
print(f"revenue value £{np.median(revenue_ltv):.0f} [{np.percentile(revenue_ltv, 5):.0f}, {np.percentile(revenue_ltv, 95):.0f}] | margin value £{np.median(ltv):.0f} [{np.percentile(ltv, 5):.0f}, {np.percentile(ltv, 95):.0f}] | true margin value £{true_orders * repeat_truth['true_mean_order_value'] * margin:.0f}")

plug_in = discounted_orders(*[mle[k] for k in ("r", "alpha", "a", "b")]) * gg_mle["p"] * gg_mle["v"] / (gg_mle["q"] - 1)
print(f"plugging in maximum likelihood instead of posterior draws: revenue value £{plug_in:.0f}; parts: orders {np.median(orders):.2f} posterior, {discounted_orders(*[mle[k] for k in ('r', 'alpha', 'a', 'b')]):.2f} plug-in")

# %% cac
rows = {}
for c in CHANNELS:
    rows[c] = {"spend_per_week_before": weekly[~after][f"spend_{c}"].mean(), "spend_per_week_after": weekly[after][f"spend_{c}"].mean(),
               "new_per_week_before": weekly[~after][f"new_customers_{c}"].mean(), "new_per_week_after": weekly[after][f"new_customers_{c}"].mean(),
               "cac_before": weekly[~after][f"spend_{c}"].sum() / weekly[~after][f"new_customers_{c}"].sum(),
               "cac_after": weekly[after][f"spend_{c}"].sum() / weekly[after][f"new_customers_{c}"].sum()}
cac = pd.DataFrame(rows).T
print(cac.round(1).to_string())
ratio = {c: ltv / cac.loc[c, "cac_after"] for c in CHANNELS}
print(pd.DataFrame({c: {"cac": cac.loc[c, "cac_after"], "median_ltv_to_cac": np.median(r), "p5": np.percentile(r, 5), "p95": np.percentile(r, 95),
                        "p_above_1": (r > 1).mean(), "p_above_3": (r > 3).mean()} for c, r in ratio.items()}).T.round(2).to_string())

attributed = touches.str[-1][converted].value_counts().reindex(CHANNELS)
caused = pd.Series(touch_truth["true_incremental_conversions"]).reindex(CHANNELS)
what_if = pd.DataFrame({"last_touch_conversions": attributed, "true_incremental": caused, "caused_per_credited": caused / attributed})
what_if["incremental_cac"] = cac.cac_after / what_if.caused_per_credited
what_if["ltv_to_incremental_cac"] = np.median(ltv) / what_if.incremental_cac
print(what_if.round(2).to_string())

fig, ax = plt.subplots(figsize=(8.5, 4))
ax.hist(ltv, bins=40, color=cs.SEQUENTIAL[1])
top = ax.get_ylim()[1]
for c in CHANNELS:
    ax.axvline(cac.loc[c, "cac_after"], color=cs.CHANNEL_COLOUR[c], lw=2)
    ax.text(cac.loc[c, "cac_after"] + 1, top * .92, f"{c.replace('_', ' ').capitalize()}\nCAC £{cac.loc[c, 'cac_after']:.0f}", color=cs.CHANNEL_COLOUR[c], va="top")
ax.axvline(true_orders * repeat_truth["true_mean_order_value"] * margin, color=cs.INK, lw=1.4, ls="--")
ax.text(true_orders * repeat_truth["true_mean_order_value"] * margin - 1, top * .92, f"True value\n£{true_orders * repeat_truth['true_mean_order_value'] * margin:.0f}", color=cs.INK, va="top", ha="right")
ax.set_xlabel("Margin value of a new customer over five years, discounted (£)")
ax.set_ylabel("Posterior draws")
ax.set_title("A new customer's value is a range; each channel's average CAC sits below it", loc="left")
cs.save(fig, "applied-ltv-cac-posterior.png")

# %% try_it
print("Try it 1: first touch against last touch")
first_touch = touches.str[0][converted].value_counts(normalize=True).reindex(CHANNELS)
print(pd.DataFrame({"first_touch": first_touch, "last_touch": last_touch, "true_incremental": true_share}).round(3).to_string())
print("Try it 2: the same budget move without the geo test")
for amount in (500, 1000, 2000):
    no_geo, with_geo = move_gain(plain_draws, amount), move_gain(geo_draws, amount)
    print(f"  move £{amount:>5,}: no geo test {np.median(no_geo):>6,.0f} [{np.percentile(no_geo, 5):,.0f}, {np.percentile(no_geo, 95):,.0f}]; with it {np.median(with_geo):>6,.0f} [{np.percentile(with_geo, 5):,.0f}, {np.percentile(with_geo, 95):,.0f}]")
print("Try it 3: Gamma-Gamma with priors wide enough to stay out of the way")
wide = GammaGammaModel(model_config={"p": Prior("HalfNormal", sigma=50), "q": Prior("HalfNormal", sigma=50), "v": Prior("HalfNormal", sigma=200)})
wide.fit(money, chains=4, tune=1000, draws=1000, random_seed=SEED, progressbar=False)
print(az.summary(wide.idata.posterior, var_names=["p", "q", "v"], ci_prob=.9)[["mean", "eti90_lb", "eti90_ub", "r_hat"]].to_string())
print("Try it 4: how the value moves with horizon and discount rate, at the true parameters and £50 an order")
truth_params = [repeat_truth[k] for k in ("r", "alpha", "a", "b")]
for months, monthly in ((36, .01), (60, .01), (120, .01), (60, .005), (60, .02), (60, 0.0)):
    n = discounted_orders(*truth_params, months=months, discount=monthly)
    print(f"  {months:>3} months at {monthly:.1%} a month: {n:.2f} orders, revenue £{n * 50:.0f}, margin £{n * 50 * margin:.0f}")

# %% extra_seeds
if "--seeds" in sys.argv:
    rows = []
    for s in range(100, 112):
        p, t = load_touch_paths(seed=s), load_truth("touch_paths", seed=s)
        split = p.path.str.split(">")
        lt = split.str[-1][p.converted == 1].value_counts(normalize=True)
        sh = shapley_credit(split.map(frozenset), p.converted)
        _, gained = fit_noisy_or(p, use_intent=True)
        g_lost, g_saved = geo_lift(load_geo_test(seed=s))
        log_s = load_repeat_log(seed=s)
        rfm_s = rfm_table(log_s, END)
        fit_s, _ = bgnbd_mle(rfm_s)
        means = log_s.sort_values("order_date").groupby("customer_id").value.apply(lambda v: v.iloc[1:].mean() if len(v) > 1 else np.nan)
        gg_s = gamma_gamma_mle(rfm_s.assign(monetary_value=rfm_s.customer_id.map(means)).query("frequency > 0"))
        rows.append({"seed": s, "last": lt["paid_social"], "shapley": sh["paid_social"] / sh.sum(), "noisy_or": gained["paid_social"] / gained.sum(),
                     "true": t["true_incremental_share"]["paid_social"], "iroas": g_lost.sum() / g_saved.sum(), "true_iroas": load_truth("geo_test", seed=s)["true_iroas"],
                     **{k: fit_s[k] for k in ("r", "alpha", "a", "b")}, **gg_s,
                     "revenue_ltv": discounted_orders(*[fit_s[k] for k in ("r", "alpha", "a", "b")]) * gg_s["p"] * gg_s["v"] / (gg_s["q"] - 1)})
    seeds = pd.DataFrame(rows)
    print(seeds.round(3).to_string(index=False))
    print(seeds.drop(columns="seed").mean().round(3).to_string())
    print("iROAS error sd:", round((seeds.iroas - seeds.true_iroas).std(), 3), "mean:", round((seeds.iroas - seeds.true_iroas).mean(), 3))
    mmm_rows = []
    for s in range(100, 104):
        w = load_marketing_weekly(seed=s)
        g_lost, g_saved = geo_lift(load_geo_test(seed=s))
        g_iroas = g_lost.sum() / g_saved.sum()
        tw = w.week.between(load_geo_test(seed=s).week[load_geo_test(seed=s).post == 1].min(), load_geo_test(seed=s).week.max())
        x = w.loc[tw, "spend_paid_social"].mean()
        lt = pd.DataFrame({"channel": ["spend_paid_social"], "x": [x], "delta_x": [-x], "delta_y": [-g_iroas * x], "sigma": [.04 * x]})
        draws = curves(fit_mmm(w, lift_test=lt, seed=s))
        a_, m_ = recovery(draws, w)
        t = load_truth("marketing", seed=s)
        mmm_rows.append({"seed": s, "roas_paid": np.median(a_[:, 0]), "true": t["true_roas"]["paid_social"]["after_cut"],
                         "m_paid": np.median(m_[:, 0]), "true_m_paid": t["true_marginal_roas_after_cut"]["paid_social"],
                         "m_email": np.median(m_[:, 2]), "true_m_email": t["true_marginal_roas_after_cut"]["email"]})
    print(pd.DataFrame(mmm_rows).round(2).to_string(index=False))
