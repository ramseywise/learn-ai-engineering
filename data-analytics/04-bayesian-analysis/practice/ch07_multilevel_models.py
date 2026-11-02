# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "pymc", "arviz"]
# ///
"""Chapter 7: which segment's effect is real, and how far should you trust it?

Every dataset here is simulated, so the truth is known and the errors can be measured.
Takes about ten minutes, most of it in the PyMC cells.

Run from this folder with: uv run ch07_multilevel_models.py
"""
# %% setup
import warnings
import arviz as az, numpy as np, pandas as pd, pymc as pm
import statsmodels.api as sm, statsmodels.formula.api as smf
from scipy.special import expit, logit
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.filterwarnings("ignore", category=ConvergenceWarning)   # the replication loops hit the boundary often; counted below
warnings.filterwarnings("ignore", category=RuntimeWarning, module="statsmodels")
warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels")
pd.set_option("display.width", 120, "display.max_columns", 20)
SAMPLE = dict(chains=4, cores=1, progressbar=False, random_seed=7)

def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))

def sampler_report(idata, names):
    """The numbers you check before believing a posterior."""
    s = az.summary(idata, var_names=names)
    return (f"max r_hat {s['r_hat'].astype(float).max():.3f}, "
            f"min ess_bulk {s['ess_bulk'].astype(float).min():.0f}, "
            f"min ess_tail {s['ess_tail'].astype(float).min():.0f}, "
            f"divergences {int(idata.sample_stats['diverging'].sum())}")

# %% chart setup
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "06-applied-analyses" / "practice"))
import matplotlib.pyplot as plt
import chartstyle as cs
cs.apply()

# %% markets
def simulate_markets(seed, J=40, mu=40.0, tau=6.0, sigma=30.0):
    """Revenue per user, users nested in markets of very different sizes."""
    rng = np.random.default_rng(seed)
    n = np.clip(rng.lognormal(np.log(60), 1.1, J).astype(int), 5, 1500)
    truth = mu + tau * rng.normal(size=J)
    market = np.repeat(np.arange(J), n)
    y = truth[market] + sigma * rng.normal(size=n.sum())
    return pd.DataFrame({"market": market, "y": y}), truth, n

def three_estimates(df):
    """No pooling, complete pooling and partial pooling, one number per market."""
    fit = smf.mixedlm("y ~ 1", df, groups="market").fit(reml=True)
    groups = sorted(df["market"].unique())
    partial = np.array([fit.fe_params["Intercept"] + fit.random_effects[g].iloc[0] for g in groups])
    none = df.groupby("market")["y"].mean().to_numpy()
    complete = np.full_like(none, df["y"].mean())
    return none, complete, partial, fit

df, truth, n = simulate_markets(seed=7)
none, complete, partial, fit = three_estimates(df)
tau2, sigma2 = float(fit.cov_re.iloc[0, 0]), float(fit.scale)
print(f"{len(n)} markets, {n.sum()} users, smallest {n.min()}, median {int(np.median(n))}, largest {n.max()}")
print(f"between-market sd: true 6.0, estimated {np.sqrt(tau2):.2f}")
print(f"within-market sd:  true 30.0, estimated {np.sqrt(sigma2):.2f}")
weight = tau2 / (tau2 + sigma2 / n)      # the share of a market's own mean that survives
show = np.argsort(n)[[0, 3, 20, 36, 39]]
print(pd.DataFrame({"users": n[show], "true": truth[show], "no_pooling": none[show],
                    "partial": partial[show], "weight_on_own_mean": weight[show]}).round(2).to_string(index=False))

# %% pooling error
sizes = {"small (under 30 users)": n < 30, "middle": (n >= 30) & (n < 150), "large (150 or more)": n >= 150}
rows = [("all markets", rmse(none, truth), rmse(complete, truth), rmse(partial, truth))]
for label, mask in sizes.items():
    rows.append((f"{label}, {mask.sum()}", rmse(none[mask], truth[mask]),
                 rmse(complete[mask], truth[mask]), rmse(partial[mask], truth[mask])))
print(pd.DataFrame(rows, columns=["this dataset", "no_pooling", "complete", "partial"]).round(2).to_string(index=False))

err = []
for s in range(200):
    d, true_means, _ = simulate_markets(seed=1000 + s)
    err.append([rmse(estimate, true_means) for estimate in three_estimates(d)[:3]])
err = np.array(err)
print("\nRMSE over 200 new datasets: "
      f"no pooling {err[:, 0].mean():.2f}, complete {err[:, 1].mean():.2f}, partial {err[:, 2].mean():.2f}")
print(f"partial beat no pooling in {(err[:, 2] < err[:, 0]).mean():.0%} of datasets, "
      f"and beat complete pooling in {(err[:, 2] < err[:, 1]).mean():.0%}")

# %% icc
icc = tau2 / (tau2 + sigma2)
m_bar, m_weighted = n.mean(), (n ** 2).sum() / n.sum()
naive = smf.ols("y ~ 1", df).fit().bse["Intercept"]
clustered = smf.ols("y ~ 1", df).fit(cov_type="cluster", cov_kwds={"groups": df["market"]}).bse["Intercept"]
print(f"ICC: true {6 ** 2 / (6 ** 2 + 30 ** 2):.3f}, estimated {icc:.3f}")
print(f"design effect with the mean market size ({m_bar:.0f}): {1 + (m_bar - 1) * icc:.2f}")
print(f"design effect with the user-weighted size ({m_weighted:.0f}): {1 + (m_weighted - 1) * icc:.2f}")
print(f"SE of the mean: naive {naive:.3f}, clustered {clustered:.3f}, so (clustered/naive)^2 = {(clustered / naive) ** 2:.2f}")
N = n.sum()
exact = (6.0 ** 2 * (n ** 2).sum() / N ** 2 + 30.0 ** 2 / N) / (30.0 ** 2 / N + 6.0 ** 2 / N)
print(f"exact design effect from the true variances and these sizes: {exact:.2f}")

# %% repeated measures
def simulate_users(seed=11, users=150, weeks=6, sd_slope=2.5):
    """Weekly revenue for each user: everyone has their own level and their own trend."""
    rng = np.random.default_rng(seed)
    off_diagonal = 0.3 * 8.0 * sd_slope
    effects = rng.multivariate_normal([0, 0], [[8.0 ** 2, off_diagonal], [off_diagonal, sd_slope ** 2]], users)
    user, week = np.repeat(np.arange(users), weeks), np.tile(np.arange(weeks), users)
    y = 40 + effects[user, 0] + (1.5 + effects[user, 1]) * week + 10 * rng.normal(size=users * weeks)
    return pd.DataFrame({"user": user, "week": week, "y": y}), effects

def fit_slopes(data):
    """Random intercepts and slopes, keeping any warning statsmodels raises."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fit = smf.mixedlm("y ~ week", data, groups="user", re_formula="~week").fit(reml=True)
    return fit, sorted({str(w.message).split(".")[0][:70] for w in caught})

panel, true_effects = simulate_users()
ols = smf.ols("y ~ week", panel).fit()
intercepts = smf.mixedlm("y ~ week", panel, groups="user").fit(reml=True)
slopes, slope_warnings = fit_slopes(panel)
print(f"naive OLS:         week {ols.params['week']:.3f}, SE {ols.bse['week']:.3f}")
print(f"random intercepts: week {intercepts.fe_params['week']:.3f}, SE {intercepts.bse['week']:.3f}")
print(f"+ random slopes:   week {slopes.fe_params['week']:.3f}, SE {slopes.bse['week']:.3f}")
clustered_week = smf.ols("y ~ week", panel).fit(cov_type="cluster", cov_kwds={"groups": panel["user"]})
print(f"OLS, clustered:    week {clustered_week.params['week']:.3f}, SE {clustered_week.bse['week']:.3f}")
print("the slopes model's warnings:", slope_warnings or "none")

# %% pymc slopes
def variance_parts(fit):
    c = fit.cov_re
    sd_a, sd_b = np.sqrt(c.iloc[0, 0]), np.sqrt(c.iloc[1, 1])
    return [fit.fe_params["Intercept"], fit.fe_params["week"], sd_a, sd_b, c.iloc[0, 1] / (sd_a * sd_b), np.sqrt(fit.scale)]

def fit_pymc(data):
    """The same model with the non-centred form from chapter 2."""
    user, week = data["user"].to_numpy(), data["week"].to_numpy()
    with pm.Model():
        intercept = pm.Normal("intercept", 40, 20)
        trend = pm.Normal("trend", 0, 5)
        chol, corr, sds = pm.LKJCholeskyCov("chol", n=2, eta=2, sd_dist=pm.HalfNormal.dist(10), compute_corr=True)
        pm.Deterministic("sd_intercept", sds[0]); pm.Deterministic("sd_slope", sds[1]); pm.Deterministic("rho", corr[0, 1])
        raw = pm.Normal("raw", 0, 1, shape=(user.max() + 1, 2))
        u = pm.Deterministic("u", pm.math.dot(chol, raw.T).T)
        sigma = pm.HalfNormal("sigma", 20)
        pm.Normal("y", intercept + u[user, 0] + (trend + u[user, 1]) * week, sigma, observed=data["y"].to_numpy())
        return pm.sample(1000, tune=1000, target_accept=0.95, **SAMPLE)

def compare(data, fit, truth):
    idata = fit_pymc(data)
    names = ["intercept", "trend", "sd_intercept", "sd_slope", "rho", "sigma"]
    print(sampler_report(idata, names))
    print(pd.DataFrame({"parameter": names, "truth": truth, "MixedLM": variance_parts(fit),
                        "PyMC": [float(idata.posterior[k].mean()) for k in names]}).round(2).to_string(index=False))
    blup = np.array([fit.random_effects[g].to_numpy() for g in sorted(data["user"].unique())])
    return blup, idata.posterior["u"].mean(("chain", "draw")).to_numpy()

blup, pm_u = compare(panel, slopes, [40, 1.5, 8, 2.5, 0.3, 10])
print(f"user effects, MixedLM against PyMC: correlation {np.corrcoef(blup[:, 0], pm_u[:, 0])[0, 1]:.3f} (level), "
      f"{np.corrcoef(blup[:, 1], pm_u[:, 1])[0, 1]:.3f} (trend)")
print(f"largest gap for any user: {np.abs(blup[:, 0] - pm_u[:, 0]).max():.2f} dollars (level), {np.abs(blup[:, 1] - pm_u[:, 1]).max():.2f} dollars a week (trend)")
raw_trend = panel.groupby("user").apply(lambda g: np.polyfit(g["week"], g["y"], 1)[0], include_groups=False).to_numpy() - slopes.fe_params["week"]
print(f"each user's trend against the truth, RMSE: their own OLS line {rmse(raw_trend, true_effects[:, 1]):.2f}, "
      f"MixedLM {rmse(blup[:, 1], true_effects[:, 1]):.2f}, PyMC {rmse(pm_u[:, 1], true_effects[:, 1]):.2f}")

# %% weak slopes
weak_panel, weak_effects = simulate_users(sd_slope=1.0)
weak, weak_warnings = fit_slopes(weak_panel)
print("the slopes model's warnings:", weak_warnings or "none")
_ = compare(weak_panel, weak, [40, 1.5, 8, 1, 0.3, 10])

# %% decision table
def simulate_discount(seed, correlated, J=40, m=8):
    """x is the discount a user saw. Its true effect within a market is 2."""
    rng = np.random.default_rng(seed)
    u = rng.normal(0, 3, J)
    x_bar = 0.5 * u + rng.normal(0, 1, J) if correlated else rng.normal(0, np.sqrt(1 + 0.25 * 9), J)
    market = np.repeat(np.arange(J), m)
    x = x_bar[market] + rng.normal(0, 1, J * m)
    y = 10 + 2 * x + u[market] + 5 * rng.normal(size=J * m)
    return pd.DataFrame({"market": market, "x": x, "y": y})

def four_ways(d):
    d = d.assign(x_mean=d.groupby("market")["x"].transform("mean"))
    d["x_within"] = d["x"] - d["x_mean"]
    cl = dict(cov_type="cluster", cov_kwds={"groups": d["market"]})
    pooled = smf.ols("y ~ x", d).fit(**cl)
    fixed = smf.ols("y ~ x + C(market)", d).fit(**cl)
    random = smf.mixedlm("y ~ x", d, groups="market").fit(reml=True)
    within = smf.mixedlm("y ~ x_within + x_mean", d, groups="market").fit(reml=True)
    return ([pooled.params["x"], fixed.params["x"], random.fe_params["x"], within.fe_params["x_within"]],
            [pooled.bse["x"], fixed.bse["x"], random.bse["x"], within.bse["x_within"]])

labels = ["pooled OLS, clustered SE", "fixed effects, clustered SE", "random intercepts", "within-between random intercepts"]
for correlated in [False, True]:
    res = [four_ways(simulate_discount(s, correlated)) for s in range(400)]
    est, se = np.array([r[0] for r in res]), np.array([r[1] for r in res])
    print(f"market effect correlated with discount: {correlated} (true within-market effect 2.0)")
    print(pd.DataFrame({"estimator": labels, "mean_estimate": est.mean(0), "median_SE": np.nanmedian(se, 0),
                        "actual_sd": est.std(0), "SE_missing": np.isnan(se).sum(0)}).round(3).to_string(index=False), "\n")

# %% ab segments
def pool(y, se, prior="halfnormal", scale=2.0, X=None):
    """Exact normal-normal partial pooling: flat prior on the mean, integrate tau on a grid."""
    y, se = np.asarray(y, float), np.asarray(se, float)
    X = np.ones((len(y), 1)) if X is None else X
    taus = np.geomspace(1e-3, 40, 300)
    log_prior = -0.5 * (taus / scale) ** 2 if prior == "halfnormal" else -np.log1p((taus / scale) ** 2)
    V = se ** 2 + taus[:, None] ** 2                                   # (tau, segment)
    XtWX = np.einsum("tj,ja,jb->tab", 1 / V, X, X)
    XtWy = np.einsum("tj,ja,j->ta", 1 / V, X, y)
    cov = np.linalg.inv(XtWX)
    beta = np.einsum("tab,tb->ta", cov, XtWy)
    fitted = beta @ X.T
    log_post = log_prior + 0.5 * np.linalg.slogdet(cov)[1] - 0.5 * (np.log(V) + (y - fitted) ** 2 / V).sum(1)
    w = np.exp(log_post - log_post.max()) * np.gradient(taus)
    w /= w.sum()
    shrink = se ** 2 / V                                               # how far each segment moves
    cond_mean = shrink * fitted + (1 - shrink) * y
    cond_var = (1 - shrink) * se ** 2 + shrink ** 2 * np.einsum("ja,tab,jb->tj", X, cov, X)
    mean = w @ cond_mean
    var = w @ cond_var + w @ (cond_mean - mean) ** 2
    return mean, np.sqrt(var), taus, w

def segments(seed, J=24, mu=1.0, tau=0.5, n_scale=1.0):
    """True lift in revenue per user for each segment, and its noisy measured lift."""
    rng = np.random.default_rng(seed)
    n = np.clip(rng.lognormal(np.log(1500), 1.0, J), 100, None) * n_scale      # users per arm
    se = 30 * np.sqrt(2 / n)
    theta = mu + tau * rng.normal(size=J)
    return theta, theta + se * rng.normal(size=J), se, n

theta, y, se, n_seg = segments(seed=21)
with pm.Model():
    mu = pm.Normal("mu", 0, 10)
    tau = pm.HalfNormal("tau", 2)
    raw = pm.Normal("raw", 0, 1, shape=24)
    eff = pm.Deterministic("theta", mu + tau * raw)
    pm.Normal("y", eff, se, observed=y)
    segment_fit = pm.sample(1000, tune=1000, target_accept=0.95, **SAMPLE)
print(sampler_report(segment_fit, ["mu", "tau", "theta"]))
pm_mean = segment_fit.posterior["theta"].mean(("chain", "draw")).to_numpy()
exact, exact_sd, _, _ = pool(y, se)
print(f"PyMC against the exact grid: largest gap in a segment's mean {np.abs(pm_mean - exact).max():.3f}")
print(f"RMSE against truth: per segment {rmse(y, theta):.3f}, partially pooled {rmse(pm_mean, theta):.3f}")
win_raw, win_pool = int(np.argmax(y)), int(np.argmax(pm_mean))
print(f"raw winner: segment {win_raw}, {n_seg[win_raw]:.0f} users an arm, measured +{y[win_raw]:.2f}, pooled +{pm_mean[win_raw]:.2f}, true +{theta[win_raw]:.2f}")
print(f"pooled winner: segment {win_pool}, {n_seg[win_pool]:.0f} users an arm, measured +{y[win_pool]:.2f}, pooled +{pm_mean[win_pool]:.2f}, true +{theta[win_pool]:.2f}")
print(f"truly best: segment {int(np.argmax(theta))}, true +{theta.max():.2f}")

# %% winner
def score(theta, y, se, X=None, **prior):
    mean, sd, _, _ = pool(y, se, X=X, **prior)
    a, b = int(np.argmax(y)), int(np.argmax(mean))
    return dict(raw=rmse(y, theta), pooled=rmse(mean, theta), raw_winner_gap=y[a] - theta[a], pooled_winner_gap=mean[b] - theta[b],
                raw_winner_true=theta[a], pooled_winner_true=theta[b], best=theta.max(),
                raw_cover=np.mean(np.abs(y - theta) < 1.645 * se), pooled_cover=np.mean(np.abs(mean - theta) < 1.645 * sd))

def run(make, reps=1000, **prior):
    return pd.DataFrame([score(*make(s), **prior) for s in range(reps)]).mean()

base = run(lambda s: segments(s)[:3])
print(f"RMSE: per segment {base['raw']:.3f}, pooled {base['pooled']:.3f}")
print(f"winner's estimate minus its true lift: per segment +{base['raw_winner_gap']:.2f}, pooled +{base['pooled_winner_gap']:.2f}")
print(f"true lift of the segment you pick: per segment {base['raw_winner_true']:.2f}, pooled {base['pooled_winner_true']:.2f}, truly best {base['best']:.2f}")
print(f"90% interval coverage: per segment {base['raw_cover']:.2f}, pooled {base['pooled_cover']:.2f}")

# %% where it does not help
def lift_outlier(s, big=5.0):
    """One small segment genuinely has a far larger lift than the rest."""
    theta, y, se, n = segments(s)
    k = int(np.argmin(n))
    y, theta = y.copy(), theta.copy()
    y[k] += big - theta[k]; theta[k] = big
    return theta, y, se, k

def size_linked(s):
    """Small segments truly respond more, so the common centre is wrong for them."""
    rng = np.random.default_rng(s)
    n = np.clip(rng.lognormal(np.log(1500), 1.0, 24), 100, None)
    se = 30 * np.sqrt(2 / n)
    small = n < np.median(n)
    theta = np.where(small, 3.0, 0.5) + 0.3 * rng.normal(size=24)
    return theta, theta + se * rng.normal(size=24), se, small, np.column_stack([np.ones(24), small.astype(float)])

table = {
    "baseline: 24 noisy segments, tau 0.5": base,
    "no real differences, tau 0": run(lambda s: segments(s, tau=0.0)[:3]),
    "well measured (100x users), tau 0.5": run(lambda s: segments(s, n_scale=100.0)[:3]),
    "well measured (100x users), tau 2.0": run(lambda s: segments(s, tau=2.0, n_scale=100.0)[:3]),
    "only 4 segments, tau 0.5": run(lambda s: segments(s, J=4)[:3]),
}
scen = pd.DataFrame(table).T
scen["ratio"] = scen["pooled"] / scen["raw"]
print(scen[["raw", "pooled", "ratio", "raw_winner_gap", "pooled_winner_gap", "raw_cover", "pooled_cover"]].round(2).to_string())

out = [lift_outlier(s) for s in range(1000)]
fits = [pool(o[1], o[2]) for o in out]
raw_err = np.array([o[1][o[3]] - o[0][o[3]] for o in out])
pool_err = np.array([f[0][o[3]] - o[0][o[3]] for f, o in zip(fits, out)])
rest = np.array([[rmse(np.delete(o[1], o[3]), np.delete(o[0], o[3])), rmse(np.delete(f[0], o[3]), np.delete(o[0], o[3]))] for f, o in zip(fits, out)]).mean(0)
print(f"\none small segment truly at +5.0: per-segment mean error {raw_err.mean():+.2f}, RMSE {np.sqrt((raw_err ** 2).mean()):.2f}; "
      f"pooled mean error {pool_err.mean():+.2f}, RMSE {np.sqrt((pool_err ** 2).mean()):.2f}")
print(f"the other 23 segments: per segment {rest[0]:.3f}, pooled {rest[1]:.3f}")

linked = [size_linked(s) for s in range(1000)]
plain = [pool(l[1], l[2])[0] for l in linked]
with_x = [pool(l[1], l[2], X=l[4])[0] for l in linked]
def by_size(est):
    small = np.mean([(e[l[3]] - l[0][l[3]]).mean() for e, l in zip(est, linked)])
    return small, np.mean([rmse(e[l[3]], l[0][l[3]]) for e, l in zip(est, linked)])
print("\nsmall segments truly at +3.0, large at +0.5 (errors for the small segments):")
for label, est in [("per segment", [l[1] for l in linked]), ("pooled to one centre", plain), ("pooled, size as a predictor", with_x)]:
    bias, err_small = by_size(est)
    print(f"{label:29s} mean error {bias:+.2f}, RMSE {err_small:.2f}")

# %% few groups
rows, draws = [], {}
for J in [3, 5, 8, 20, 50]:
    fits_tau, boundary = [], 0
    for s in range(300):
        d, _, _ = simulate_markets(seed=5000 + s, J=J)
        t = np.sqrt(max(float(smf.mixedlm("y ~ 1", d, groups="market").fit(reml=True).cov_re.iloc[0, 0]), 0.0))
        fits_tau.append(t); boundary += t < 0.01
    q = np.percentile(fits_tau, [5, 50, 95])
    draws[J] = q
    rows.append(dict(markets=J, median_tau=q[1], p5=q[0], p95=q[2], share_at_zero=boundary / 300))
print("true tau is 6.0; REML estimates over 300 simulated datasets")
print(pd.DataFrame(rows).round(2).to_string(index=False))

# %% few groups priors
theta4, y4, se4, _ = segments(seed=33, J=4)
print("four segments, measured:", y4.round(2), "se:", se4.round(2), "truth:", theta4.round(2))
for label, kw in [("half-normal(0.25)", dict(scale=0.25)), ("half-normal(2)", dict(scale=2.0)),
                  ("half-Cauchy(5)", dict(prior="cauchy", scale=5.0))]:
    mean, sd, taus, w = pool(y4, se4, **kw)
    cdf = np.cumsum(w)
    print(f"{label:18s} tau 90% interval {taus[np.searchsorted(cdf, .05)]:.2f} to {taus[np.searchsorted(cdf, .95)]:.2f}, pooled estimates {mean.round(2)}")

# %% few groups error
rows = []
for tau_true in [0.5, 2.0]:
    for label, kw in [("half-normal(0.25)", dict(scale=0.25)), ("half-normal(2)", dict(scale=2.0)), ("half-Cauchy(5)", dict(prior="cauchy", scale=5.0))]:
        res = run(lambda s: segments(s, J=4, tau=tau_true)[:3], **kw)
        rows.append(dict(true_tau=tau_true, prior=label, per_segment=res["raw"], pooled=res["pooled"], ratio=res["pooled"] / res["raw"], pooled_cover=res["pooled_cover"]))
few = pd.DataFrame(rows)
print(few.round(2).to_string(index=False))

# %% few groups toolkits
small, small_truth, small_n = simulate_markets(seed=48, J=5)
fit5 = smf.mixedlm("y ~ 1", small, groups="market").fit(reml=True)
ids = small["market"].to_numpy()
with pm.Model():
    mu5 = pm.Normal("mu", 40, 20)
    tau5 = pm.HalfNormal("tau", 10)
    raw5 = pm.Normal("raw", 0, 1, shape=5)
    sigma5 = pm.HalfNormal("sigma", 40)
    pm.Normal("y", mu5 + tau5 * raw5[ids], sigma5, observed=small["y"].to_numpy())
    five = pm.sample(1000, tune=1000, target_accept=0.95, **SAMPLE)
print(sampler_report(five, ["mu", "tau", "sigma"]))
tau_draws = five.posterior["tau"].to_numpy().ravel()
print(f"five markets, sizes {sorted(small_n.tolist())}, sd of their true means {small_truth.std(ddof=1):.2f}")
print(f"tau: MixedLM {np.sqrt(fit5.cov_re.iloc[0, 0]):.2f} (a single number), "
      f"PyMC mean {tau_draws.mean():.2f}, 90% interval {np.percentile(tau_draws, 5):.2f} to {np.percentile(tau_draws, 95):.2f}")
print(f"grand mean: MixedLM {fit5.fe_params['Intercept']:.2f} (SE {fit5.bse['Intercept']:.2f}), "
      f"PyMC {float(five.posterior['mu'].mean()):.2f} (sd {float(five.posterior['mu'].std()):.2f})")

# %% conversion
rng = np.random.default_rng(101)
M = 30
users = np.clip(rng.lognormal(np.log(1200), 1.0, M), 100, None).astype(int)   # per arm
a_true, b_true = -3.0 + 0.7 * rng.normal(size=M), 0.15 + 0.15 * rng.normal(size=M)
control = rng.binomial(users, expit(a_true))
treated = rng.binomial(users, expit(a_true + b_true))
print(f"{M} markets, {users.min()} to {users.max()} users an arm; markets with zero control conversions: {(control == 0).sum()}")

with pm.Model():
    alpha = pm.Normal("alpha", -3, 1.5)
    beta = pm.Normal("beta", 0, 0.5)
    sd_alpha = pm.HalfNormal("sd_alpha", 1)
    sd_beta = pm.HalfNormal("sd_beta", 0.5)
    raw_a = pm.Normal("raw_a", 0, 1, shape=M)
    raw_b = pm.Normal("raw_b", 0, 1, shape=M)
    a = pm.Deterministic("a", alpha + sd_alpha * raw_a)
    b = pm.Deterministic("b", beta + sd_beta * raw_b)
    pm.Binomial("c", users, pm.math.invlogit(a), observed=control)
    pm.Binomial("t", users, pm.math.invlogit(a + b), observed=treated)
    conv = pm.sample(1000, tune=1000, target_accept=0.95, **SAMPLE)
print(sampler_report(conv, ["alpha", "beta", "sd_alpha", "sd_beta"]))
conv_table = az.summary(conv, var_names=["alpha", "beta", "sd_alpha", "sd_beta"])[["mean", "sd"]].astype(float).round(3)
conv_table.insert(0, "truth", [-3.0, 0.15, 0.7, 0.15])
print(conv_table.to_string())

draws_a = conv.posterior["a"].stack(s=("chain", "draw")).to_numpy()
draws_b = conv.posterior["b"].stack(s=("chain", "draw")).to_numpy()
true_rate, true_lift = expit(a_true), expit(a_true + b_true) - expit(a_true)
raw_rate, raw_lift = control / users, (treated - control) / users
pool_rate = expit(draws_a).mean(1)
pool_lift = (expit(draws_a + draws_b) - expit(draws_a)).mean(1)
print(f"\ncontrol rate RMSE, percentage points: raw {100 * rmse(raw_rate, true_rate):.2f}, pooled {100 * rmse(pool_rate, true_rate):.2f}")
print(f"lift RMSE, percentage points:         raw {100 * rmse(raw_lift, true_lift):.2f}, pooled {100 * rmse(pool_lift, true_lift):.2f}")
w_raw, w_pool = int(np.argmax(raw_lift)), int(np.argmax(pool_lift))
print(f"raw winner: {users[w_raw]} users an arm, measured {100 * raw_lift[w_raw]:+.2f} points, true {100 * true_lift[w_raw]:+.2f}")
print(f"pooled winner: {users[w_pool]} users an arm, pooled {100 * pool_lift[w_pool]:+.2f} points, true {100 * true_lift[w_pool]:+.2f}")

# %% conversion scale
long = pd.DataFrame({"market": np.tile(np.arange(M), 2), "treated": np.repeat([0, 1], M),
                     "conv": np.r_[control, treated], "users": np.r_[users, users]})
long["no"] = long["users"] - long["conv"]
pa = smf.glm("conv + no ~ treated", long, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": long["market"]})
alpha_draws = conv.posterior["alpha"].to_numpy().ravel()
sd_draws = conv.posterior["sd_alpha"].to_numpy().ravel()
print(f"invlogit(alpha), a typical market:     {100 * expit(alpha_draws).mean():.2f}%")
z = np.random.default_rng(3).normal(size=(4000, 200))
print(f"average across the market population:  {100 * expit(alpha_draws[:, None] + sd_draws[:, None] * z).mean():.2f}%")
print(f"pooled treatment log-odds, clustered SE: {pa.params['treated']:.3f} (SE {pa.bse['treated']:.3f})")
print(f"multilevel treatment log-odds, beta:     {float(conv.posterior['beta'].mean()):.3f} (sd {float(conv.posterior['beta'].std()):.3f})")
big = np.random.default_rng(4)
a_pop = -3.0 + 0.7 * big.normal(size=2_000_000)
b_pop = 0.15 + 0.15 * big.normal(size=2_000_000)
print(f"from the true parameters: cluster-specific 0.150, population-averaged {logit(expit(a_pop + b_pop).mean()) - logit(expit(a_pop).mean()):.3f}")

# %% try it
print(f"exercise 1: weight on a 20-user market's own mean {tau2 / (tau2 + sigma2 / 20):.2f}")
eight = run(lambda s: segments(s, J=8)[:3])
print(f"exercise 2: eight segments, RMSE {eight['raw']:.2f} against {eight['pooled']:.2f}, winner gap +{eight['raw_winner_gap']:.2f} against +{eight['pooled_winner_gap']:.2f}")
print(f"exercise 3: design effect, ICC 0.2, 25 users a cluster {1 + 24 * 0.2:.1f}")
strong = run(lambda s: segments(s, tau=3.0)[:3])
print(f"exercise 4: tau 3.0, RMSE {strong['raw']:.2f} against {strong['pooled']:.2f}, ratio {strong['pooled'] / strong['raw']:.2f}")

# %% figure shrinkage
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.axhline(fit.fe_params["Intercept"], color=cs.MUTED, lw=1)
ax.annotate("estimated mean across markets", (1000, fit.fe_params["Intercept"]), xytext=(0, 4),
            textcoords="offset points", ha="right", color=cs.SECONDARY, fontsize=9)
for i in range(len(n)):
    ax.plot([n[i], n[i]], [none[i], partial[i]], color=cs.GRID, lw=1.5, zorder=1)
ax.scatter(n, none, s=26, facecolor=cs.SURFACE, edgecolor=cs.ORANGE, linewidth=1.5, zorder=2, label="No pooling: the market's own mean")
ax.scatter(n, partial, s=26, color=cs.BLUE, edgecolor=cs.SURFACE, linewidth=.8, zorder=3, label="Partial pooling")
ax.set_xscale("log")
ax.set_xticks([5, 10, 30, 100, 300, 1000]); ax.set_xticklabels(["5", "10", "30", "100", "300", "1,000"])
ax.set_xlabel("Users in the market (log scale)"); ax.set_ylabel("Revenue per user ($)")
ax.set_title("Small markets move a long way towards the mean, large ones barely move")
ax.legend(loc="upper right")
cs.save(fig, "bayes-multilevel-shrinkage.png")

# %% figure scenarios
ratios = scen["ratio"].to_dict()
ratios["one small segment that truly is an outlier"] = np.sqrt((pool_err ** 2).mean()) / np.sqrt((raw_err ** 2).mean())
ratios["small segments, pooled to the wrong centre"] = by_size(plain)[1] / by_size([l[1] for l in linked])[1]
ratios["4 segments, tau 2.0, prior far too tight"] = float(few.query("true_tau == 2 and prior == 'half-normal(0.25)'")["ratio"].iloc[0])
values = pd.Series(ratios).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(8, 4.4))
ax.axvline(1, color=cs.BASELINE, lw=1.2)
ax.hlines(values.index, values, 1, color=cs.GRID, lw=2, zorder=1)
ax.scatter(values, values.index, s=60, color=cs.BLUE, zorder=2)
for label, v in values.items():
    right = v > 1
    ax.annotate(f"{v:.2f}", (v, label), xytext=(9 if right else -9, 0), textcoords="offset points",
                ha="left" if right else "right", va="center", color=cs.INK, fontsize=9)
ax.set_xlim(0, max(1.1, values.max() + .15)); ax.grid(False)
ax.set_xlabel("RMSE of pooled estimates as a share of per-segment RMSE (1.00 means no gain, above it pooling hurts)")
ax.set_title("Pooling gains most on noisy, similar segments and can lose on the wrong ones")
cs.save(fig, "bayes-multilevel-scenarios.png")

# %% figure few groups
fig, ax = plt.subplots(figsize=(8, 3.8))
xs = list(draws)
positions = np.arange(len(xs))
ax.axhline(6, color=cs.ORANGE, lw=1.5)
ax.annotate("true sd, 6", (3.5, 6), xytext=(0, 4), textcoords="offset points", ha="center", color=cs.SECONDARY, fontsize=9)
ax.vlines(positions, [draws[J][0] for J in xs], [draws[J][2] for J in xs], color=cs.BLUE, lw=3, label="5th to 95th percentile of estimates")
ax.scatter(positions, [draws[J][1] for J in xs], color=cs.INK, s=40, zorder=3, label="Median estimate")
ax.set_xticks(positions); ax.set_xticklabels([str(J) for J in xs]); ax.set_xlim(-.5, len(xs) - .5)
ax.set_xlabel("Number of markets"); ax.set_ylabel("Estimated between-market sd ($)")
ax.set_title("With a handful of groups the between-group spread is barely known")
ax.legend(loc="upper right")
cs.save(fig, "bayes-multilevel-few-groups.png")
