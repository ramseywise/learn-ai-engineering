# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "matplotlib", "statsmodels", "linearmodels"]
# ///
"""Chapter 8: panel data and fixed effects.

One simulated store-by-week panel with a known effect, so we can see which
estimators recover it and which do not.

Run from this folder with: uv run ch08_panel_data.py
"""
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS

import chartstyle as cs

cs.apply()
warnings.filterwarnings("ignore")
pd.set_option("display.width", 130, "display.max_columns", 20)

# %% write the DGP
TRUE_BETA = 0.5  # one extra point of discount adds 0.5 units a week, in every store


def simulate(stores=100, weeks=52, seed=0, beta=TRUE_BETA, within_sd=2.0, confound=0.5):
    r = np.random.default_rng(seed)
    alpha = r.normal(0, 6, stores)  # store quality: fixed, and we never observe it
    season = 3 * np.sin(2 * np.pi * np.arange(weeks) / 52)  # week effects that everyone shares
    e = np.zeros((stores, weeks))  # errors that persist from week to week
    shocks = r.normal(0, 3, (stores, weeks))
    e[:, 0] = shocks[:, 0]
    for t in range(1, weeks):
        e[:, t] = 0.5 * e[:, t - 1] + shocks[:, t]
    # Weak stores discount harder, and everyone discounts harder in the slack season.
    x = 10 - confound * alpha[:, None] - 0.6 * season + r.normal(0, within_sd, (stores, weeks))
    y = 50 + alpha[:, None] + season + beta * x + e
    return pd.DataFrame({"store": np.repeat(np.arange(stores), weeks), "week": np.tile(np.arange(weeks), stores),
                         "discount": x.ravel(), "sales": y.ravel(), "quality": np.repeat(alpha, weeks)})


df = simulate(seed=8)
print(df.head(3).round(2).to_string(index=False))
print(f"rows {len(df):,}, stores {df.store.nunique()}, weeks {df.week.nunique()}, true effect {TRUE_BETA}")
print(f"corr(store quality, store's mean discount) {df.groupby('store').quality.first().corr(df.groupby('store').discount.mean()):.3f}")

# %% between and within variation
between = df.groupby("store").discount.transform("mean")
print(f"variance of discount {df.discount.var():.2f}: between stores {between.var():.2f}, within stores {(df.discount - between).var():.2f}")
means = df.groupby("store")[["sales", "discount"]].mean()
print(f"regression on store means (between only): slope {smf.ols('sales ~ discount', means).fit().params['discount']:.3f}")

# %% pooled OLS, with and without clustered SEs
naive = smf.ols("sales ~ discount", df).fit()
clus = smf.ols("sales ~ discount", df).fit(cov_type="cluster", cov_kwds={"groups": df.store})
print(f"pooled OLS {naive.params['discount']:.3f}, naive SE {naive.bse['discount']:.3f}, clustered SE {clus.bse['discount']:.3f}")

# %% fixed effects with PanelOLS
panel = df.set_index(["store", "week"])


def fe(data, entity=True, time=True, formula="sales ~ discount"):
    term = formula + (" + EntityEffects" if entity else "") + (" + TimeEffects" if time else "")
    return PanelOLS.from_formula(term, data).fit(cov_type="clustered", cluster_entity=True)


m_e = fe(panel, time=False)
m_et = fe(panel)
print(f"store effects only   {m_e.params['discount']:.3f}, clustered SE {m_e.std_errors['discount']:.3f}")
print(f"store + week effects {m_et.params['discount']:.3f}, clustered SE {m_et.std_errors['discount']:.3f}")

# %% what PanelOLS does, by hand
def two_way_demean(s, data):
    return s - s.groupby(data.store).transform("mean") - s.groupby(data.week).transform("mean") + s.mean()


yy, xx = two_way_demean(df.sales, df), two_way_demean(df.discount, df)
print(f"two-way demeaned by hand: {(xx @ yy) / (xx @ xx):.6f}; PanelOLS: {m_et.params['discount']:.6f}")

# %% over many panels
def run_many(reps=300):
    rows = []
    for s in range(reps):
        d = simulate(seed=1000 + s)
        p = d.set_index(["store", "week"])
        a = smf.ols("sales ~ discount", d).fit()
        b = a.get_robustcov_results("cluster", groups=d.store)
        for name, est, se in [("pooled, naive SE", a.params["discount"], a.bse["discount"]),
                              ("pooled, clustered SE", b.params[1], b.bse[1])]:
            rows.append((name, est, se))
        for name, kw in [("store effects, clustered", dict(time=False)), ("store + week effects, clustered", {})]:
            m = fe(p, **kw)
            rows.append((name, m.params["discount"], m.std_errors["discount"]))
        m = PanelOLS.from_formula("sales ~ discount + EntityEffects + TimeEffects", p).fit()
        rows.append(("store + week effects, unadjusted SE", m.params["discount"], m.std_errors["discount"]))
    r = pd.DataFrame(rows, columns=["estimator", "est", "se"])
    r["hit"] = (r.est - 1.96 * r.se <= TRUE_BETA) & (TRUE_BETA <= r.est + 1.96 * r.se)
    return r.groupby("estimator", sort=False).agg(mean=("est", "mean"), sd=("est", "std"), mean_se=("se", "mean"), coverage=("hit", "mean")).round(3)


print(run_many().to_string())

# %% when clustering earns its keep: a regressor that persists
def persistent(seed, stores=100, weeks=52):
    """The discount a store runs now is close to the one it ran last week, and shocks persist too."""
    r = np.random.default_rng(seed)
    alpha = r.normal(0, 6, stores)
    x, e = np.zeros((stores, weeks)), np.zeros((stores, weeks))
    x[:, 0], e[:, 0] = r.normal(0, 2, stores), r.normal(0, 3, stores)
    for t in range(1, weeks):
        x[:, t] = 0.9 * x[:, t - 1] + r.normal(0, 2 * np.sqrt(1 - 0.81), stores)
        e[:, t] = 0.7 * e[:, t - 1] + r.normal(0, 3, stores)
    y = 50 + alpha[:, None] + TRUE_BETA * x + e
    return pd.DataFrame({"store": np.repeat(np.arange(stores), weeks), "week": np.tile(np.arange(weeks), stores),
                         "discount": x.ravel(), "sales": y.ravel()}).set_index(["store", "week"])


rows = []
for s in range(300):
    p_ = persistent(1500 + s)
    formula = "sales ~ discount + EntityEffects + TimeEffects"
    for name, m in [("unadjusted", PanelOLS.from_formula(formula, p_).fit()), ("clustered", fe(p_))]:
        est, se = m.params["discount"], m.std_errors["discount"]
        rows.append((name, est, se, abs(est - TRUE_BETA) <= 1.96 * se))
print(pd.DataFrame(rows, columns=["se_type", "est", "se", "hit"]).groupby("se_type", sort=False)
      .agg(mean=("est", "mean"), sd=("est", "std"), mean_se=("se", "mean"), coverage=("hit", "mean")).round(3).to_string())

# %% figure: pooled slope against within-store slopes
# Five stores from across the quality range, with the shared week effects taken out of both axes.
fig_d = df.copy()
for c in ("sales", "discount"):
    fig_d[c] = fig_d[c] - fig_d.groupby("week")[c].transform("mean") + fig_d[c].mean()
ranked = fig_d.groupby("store").quality.first().sort_values().index
sel = fig_d[fig_d.store.isin(ranked[[4, 28, 50, 72, 95]])]
fig, ax = cs.plt.subplots(figsize=(8, 4.5))
for i, (_, g) in enumerate(sel.groupby("store")):
    ax.scatter(g.discount, g.sales, s=9, color=cs.MUTED, alpha=0.5, linewidths=0)
    b = np.polyfit(g.discount, g.sales, 1)
    xs = np.array([g.discount.min(), g.discount.max()])
    ax.plot(xs, np.polyval(b, xs), color=cs.BLUE, lw=2, label="Within one store" if i == 0 else None)
b = np.polyfit(sel.discount, sel.sales, 1)
xs = np.array([sel.discount.min(), sel.discount.max()])
ax.plot(xs, np.polyval(b, xs), color=cs.ORANGE, lw=2, label="Pooled across these stores")
ax.set_xlabel("Discount depth (points), week effects removed")
ax.set_ylabel("Weekly sales (units), week effects removed")
ax.legend(loc="upper right")
cs.save(fig, "stats-panel-pooled-vs-within.png")

# %% what within variation cannot do: a store attribute that never changes
panel2 = panel.assign(urban=(panel.quality > 0).astype(float))
try:
    fe(panel2, formula="sales ~ discount + urban")
except Exception as err:
    print(type(err).__name__, "-", " ".join(str(err).split())[:70])
m = PanelOLS.from_formula("sales ~ discount + urban + EntityEffects + TimeEffects", panel2, drop_absorbed=True).fit()
print("with drop_absorbed=True, coefficients kept:", list(m.params.index))

# %% what within variation cannot do: confounders that move over time
def time_varying(seed, stores=100, weeks=52):
    """A competitor opens near some stores part-way through: sales fall and discounts rise."""
    r = np.random.default_rng(seed)
    d = simulate(stores, weeks, seed)
    open_week = r.integers(10, 45, stores)
    has = r.random(stores) < 0.4
    comp = (has[d.store] & (d.week.to_numpy() >= open_week[d.store])).astype(float)
    d["discount"] += 4 * comp
    d["sales"] += TRUE_BETA * 4 * comp - 6 * comp
    d["competitor"] = comp
    return d


def reverse(seed, stores=100, weeks=52):
    """Managers discount after a bad week, so last week's shock moves this week's discount."""
    r = np.random.default_rng(seed)
    season = 3 * np.sin(2 * np.pi * np.arange(weeks) / 52)
    alpha = r.normal(0, 6, stores)
    y, x = np.zeros((stores, weeks)), np.zeros((stores, weeks))
    e = np.zeros(stores)
    for t in range(weeks):
        prev = (y[:, t - 1] - (50 + alpha + season[t - 1] + TRUE_BETA * x[:, t - 1])) if t else np.zeros(stores)
        x[:, t] = 10 - 0.5 * alpha - 0.6 * season[t] - 0.4 * prev + r.normal(0, 2, stores)
        e = 0.5 * e + r.normal(0, 3, stores)
        y[:, t] = 50 + alpha + season[t] + TRUE_BETA * x[:, t] + e
    return pd.DataFrame({"store": np.repeat(np.arange(stores), weeks), "week": np.tile(np.arange(weeks), stores),
                         "discount": x.ravel(), "sales": y.ravel()})


rows = []
for s in range(100):
    d = time_varying(2000 + s).set_index(["store", "week"])
    rows.append(("competitor unmeasured", fe(d).params["discount"]))
    rows.append(("competitor controlled", fe(d, formula="sales ~ discount + competitor").params["discount"]))
    rows.append(("discount reacts to last week's shock", fe(reverse(3000 + s).set_index(["store", "week"])).params["discount"]))
print(pd.DataFrame(rows, columns=["scenario", "est"]).groupby("scenario", sort=False).est.agg(["mean", "std"]).round(3).to_string())

# %% what within variation cannot do: precision when little changes
rows = []
for sd in (2.0, 0.5, 0.1):
    m = fe(simulate(seed=8, within_sd=sd).set_index(["store", "week"]))
    rows.append(dict(within_sd=sd, estimate=m.params["discount"], clustered_se=m.std_errors["discount"]))
print(pd.DataFrame(rows).round(3).to_string(index=False))

# %% whose effect does fixed effects report?
def heterogeneous(seed, stores=100, weeks=52):
    r = np.random.default_rng(seed)
    alpha = r.normal(0, 6, stores)
    movers = np.arange(stores) < stores // 2
    beta = np.where(movers, 1.0, 0.0)  # half the stores respond, half do not: the average is 0.5
    wsd = np.where(movers, 3.0, 1.0)  # the ones that respond also vary their discounts more
    x = 10 - 0.5 * alpha[:, None] + r.normal(0, 1, (stores, weeks)) * wsd[:, None]
    y = 50 + alpha[:, None] + beta[:, None] * x + r.normal(0, 3, (stores, weeks))
    return pd.DataFrame({"store": np.repeat(np.arange(stores), weeks), "week": np.tile(np.arange(weeks), stores),
                         "discount": x.ravel(), "sales": y.ravel()}).set_index(["store", "week"])


ests = [fe(heterogeneous(4000 + s)).params["discount"] for s in range(100)]
print(f"average effect across stores 0.500; two-way FE {np.mean(ests):.3f} (variance-weighted expectation {(9 * 1 + 1 * 0) / 10:.3f})")

# %% difference-in-differences as two-way fixed effects
def did_panel(seed=12, stores=100, weeks=52, start=26, tilt=0.0):
    """Better stores get a new display in week 26. The effect builds up, then holds at 4."""
    r = np.random.default_rng(seed)
    alpha = r.normal(0, 6, stores)
    treated = (alpha + r.normal(0, 6, stores)) > 0  # not random: stronger stores are likelier
    season = 3 * np.sin(2 * np.pi * np.arange(weeks) / 52)
    k = np.arange(weeks) - start  # weeks since the change; 0 is the first treated week
    path = np.clip(1 + 0.5 * k, 0, 4) * (k >= 0)
    trend = tilt * (np.arange(weeks) - start)  # tilt > 0 means treated stores were already pulling ahead
    y = 50 + alpha[:, None] + season + treated[:, None] * (path + trend) + r.normal(0, 3, (stores, weeks))
    return pd.DataFrame({"store": np.repeat(np.arange(stores), weeks), "week": np.tile(np.arange(weeks), stores),
                         "sales": y.ravel(), "group": np.repeat(treated, weeks).astype(int),
                         "k": np.tile(k, stores)}), path


did, path = did_panel()
did["post"] = (did.k >= 0).astype(int)
did["treated_now"] = did.group * did.post
cells = did.groupby(["group", "post"]).sales.mean().unstack()
print(cells.round(3).to_string())
by_hand = (cells.loc[1, 1] - cells.loc[1, 0]) - (cells.loc[0, 1] - cells.loc[0, 0])
twfe = fe(did.set_index(["store", "week"]), formula="sales ~ treated_now")
print(f"difference of differences {by_hand:.6f}; two-way FE {twfe.params['treated_now']:.6f}, clustered SE {twfe.std_errors['treated_now']:.3f}")
print(f"true average effect over treated weeks {path[26:].mean():.3f}")
print(f"raw gap in post period, ignoring the pre-period {cells.loc[1, 1] - cells.loc[0, 1]:.3f}")

# %% the event study
def event_study(d, lo=-8, hi=12, omit=-1):
    d = d.copy()
    names = {}
    for k in range(lo, hi + 1):
        if k == omit:
            continue
        col = f"k_m{-k}" if k < 0 else f"k_p{k}"
        names[col] = k
        ends = (d.k <= k) if k == lo else (d.k >= k) if k == hi else (d.k == k)  # bin the far tails
        d[col] = (d.group * ends).astype(float)
    m = fe(d.set_index(["store", "week"]), formula="sales ~ " + " + ".join(names))
    return pd.DataFrame({"k": list(names.values()), "est": m.params[list(names)].to_numpy(),
                         "se": m.std_errors[list(names)].to_numpy()})


es_good = event_study(did)
tilted, _ = did_panel(tilt=0.15)
es_bad = event_study(tilted)
print(es_good[es_good.k.between(-4, 8)].round(2).to_string(index=False))
for name, es in [("parallel", es_good), ("tilted", es_bad)]:
    pre = es[es.k < -1]
    print(f"{name}: pre-period coefficients range {pre.est.min():.2f} to {pre.est.max():.2f}; "
          f"{(abs(pre.est) > 1.96 * pre.se).sum()} of {len(pre)} outside their 95% interval")
tilted["post"] = (tilted.k >= 0).astype(int)
tilted["treated_now"] = tilted.group * tilted.post
print(f"tilted panel: two-way FE {fe(tilted.set_index(['store', 'week']), formula='sales ~ treated_now').params['treated_now']:.3f} against a true {path[26:].mean():.3f}")

fig, axes = cs.plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, es, title in [(axes[0], es_good, "Parallel before the change"), (axes[1], es_bad, "Already pulling ahead")]:
    ax.axhline(0, color=cs.BASELINE, lw=1)
    ax.axvline(-0.5, color=cs.MUTED, lw=1, ls=":")
    ax.vlines(es.k, es.est - 1.96 * es.se, es.est + 1.96 * es.se, color=cs.BLUE, lw=1.5)
    ax.plot(es.k, es.est, "o", color=cs.BLUE, ms=5, label="Estimate, 95% interval")
    ks = np.arange(-8, 13)
    ax.plot(ks, np.clip(1 + 0.5 * ks, 0, 4) * (ks >= 0), color=cs.ORANGE, lw=2, label="True effect")
    ax.set_title(title)
    ax.set_xticks(range(-8, 13, 4))
    ax.set_xlabel("Weeks since the change")
axes[0].set_ylabel("Effect on weekly sales, relative to week -1")
axes[0].legend(loc="upper left")
cs.save(fig, "stats-panel-event-study.png")

# %% staggered timing: where the one-coefficient form breaks
def staggered(seed, stores=120, weeks=60, never=0.0, dynamic=True):
    """Three cohorts adopt at different weeks. The effect is flat, or it grows with time since adoption."""
    r = np.random.default_rng(seed)
    n_never = int(never * stores)
    starts = np.full(stores, 10_000)
    rest = stores - n_never
    starts[:rest] = np.repeat([15, 30, 45], rest // 3 + 1)[:rest]
    alpha = r.normal(0, 6, stores)
    week = np.tile(np.arange(weeks), stores)
    start = np.repeat(starts, weeks)
    since = week - start
    tau = np.where(since >= 0, 0.25 * (since + 1) if dynamic else 4.5, 0.0)
    y = 50 + np.repeat(alpha, weeks) + tau + r.normal(0, 3, stores * weeks)
    return pd.DataFrame({"store": np.repeat(np.arange(stores), weeks), "week": week, "sales": y, "start": start,
                         "treated_now": (since >= 0).astype(float), "tau": tau})


def clean_comparisons(d):
    """Each cohort against the never-treated stores only, weighted by its treated rows."""
    never = d[d.start == 10_000]
    if never.empty:
        return np.nan
    ests, weights = [], []
    for g, c in d[d.start < 10_000].groupby("start"):
        post = lambda x: x[x.week >= g].sales.mean() - x[x.week < g].sales.mean()
        ests.append(post(c) - post(never))
        weights.append((c.week >= g).sum())
    return np.average(ests, weights=weights)


rows = []
for dynamic, never in [(False, 0.0), (True, 0.0), (True, 0.5)]:
    ests, truth, clean = [], [], []
    for s in range(100):
        d = staggered(5000 + s, never=never, dynamic=dynamic)
        ests.append(fe(d.set_index(["store", "week"]), formula="sales ~ treated_now").params["treated_now"])
        truth.append(d.tau[d.treated_now == 1].mean())
        clean.append(clean_comparisons(d))
    rows.append(dict(effect="grows" if dynamic else "flat", never_treated=never, true_att=np.mean(truth),
                     twfe_mean=np.mean(ests), twfe_sd=np.std(ests), clean_2x2=np.mean(clean)))
print(pd.DataFrame(rows).round(3).to_string(index=False))

# %% Bell and Jones's counter-case: the within-between random-effects model
d = df.copy()
for c in ("sales", "discount"):  # take out week means, because this model has no week effects of its own
    d[c] = d[c] - d.groupby("week")[c].transform("mean")
d["x_mean"] = d.groupby("store").discount.transform("mean")
d["x_within"] = d.discount - d.x_mean
rewb = smf.mixedlm("sales ~ x_within + x_mean", d, groups=d.store).fit()
print(f"within effect {rewb.params['x_within']:.4f} (se {rewb.bse['x_within']:.4f}); between effect {rewb.params['x_mean']:.4f} (se {rewb.bse['x_mean']:.4f})")
print(f"two-way FE {m_et.params['discount']:.4f}; between-store variance {float(rewb.cov_re.iloc[0, 0]):.2f}; within-store variance {rewb.scale:.2f}")

# %% Try it: answers
# 1. Take away the store confounding, and keep the seasonal one.
rows = []
for s in range(200):
    d = simulate(seed=6000 + s, confound=0.0)
    a = smf.ols("sales ~ discount", d).fit(cov_type="cluster", cov_kwds={"groups": d.store})
    w = smf.ols("sales ~ discount + C(week)", d).fit(cov_type="cluster", cov_kwds={"groups": d.store})
    m = fe(d.set_index(["store", "week"]))
    rows.append((a.params["discount"], w.params["discount"], w.bse["discount"], m.params["discount"], m.std_errors["discount"]))
names = ["pooled", "pooled_with_week_effects", "its_se", "store_and_week_fe", "fe_se"]
print("no store confounding:", {k: float(round(v, 3)) for k, v in zip(names, np.mean(rows, axis=0))})

# 2. A gentler tilt in the pre-period: does the event study still flag it?
for tilt in (0.05, 0.15):
    flagged, bias = [], []
    for s in range(100):
        t_, p_ = did_panel(seed=7000 + s, tilt=tilt)
        es = event_study(t_)
        pre = es[es.k < -1]
        flagged.append((abs(pre.est) > 1.96 * pre.se).any())
        t_["treated_now"] = t_.group * (t_.k >= 0).astype(int)
        bias.append(fe(t_.set_index(["store", "week"]), formula="sales ~ treated_now").params["treated_now"] - p_[26:].mean())
    print(f"tilt {tilt}: any pre-period coefficient outside its interval in {np.mean(flagged):.0%} of panels; mean bias {np.mean(bias):.2f}")
flagged = [(lambda e: (abs(e.est) > 1.96 * e.se).any())(event_study(did_panel(seed=7000 + s)[0]).query("k < -1")) for s in range(100)]
print(f"tilt 0.0: any pre-period coefficient outside its interval in {np.mean(flagged):.0%} of panels")
