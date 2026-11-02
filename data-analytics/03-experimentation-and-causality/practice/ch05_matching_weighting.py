# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "dowhy"]
# ///
"""Chapter 5: one observational question, answered six ways, on Fernhill's loyalty club.

Run from anywhere with: uv run ch05_matching_weighting.py   (about two minutes; the first run installs DoWhy)

The table comes from the shared retail generator in 06-applied-analyses/practice. The columns that
start with true_ are hidden truth. The estimators never see them. They appear only in the sections
that score the estimators, and those sections are marked SCORING.
"""
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "06-applied-analyses" / "practice"))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.optimize import minimize
from scipy.stats import norm, rankdata

import chartstyle as cs
from retail import CLUB_DGP, load_club

warnings.filterwarnings("ignore")
cs.apply()
pd.set_option("display.width", 130)
SEED = 20250101

# %% the design table: everything measured before the club launched, and nothing else
def design_matrix(d):
    """Pre-treatment covariates, standardised. No outcome and no true_ column gets in."""
    x = pd.DataFrame({"log_orders": np.log1p(d.prior_orders), "log_spend": np.log1p(d.prior_spend),
                      "recency": d.recency_days.astype(float), "tenure": d.tenure_days.astype(float)})
    x["log_orders_sq"] = x.log_orders ** 2
    x["log_spend_sq"] = x.log_spend ** 2
    x["recency_sq"] = x.recency ** 2
    for c in ["paid_social", "email", "referral"]:
        x[f"ch_{c}"] = (d.channel == c).astype(float)
    return (x - x.mean()) / x.std()


club = load_club()
D = club.club.to_numpy()
X = design_matrix(club)
print(f"customers {len(club)}, joined {D.sum()} ({D.mean():.1%})")


# %% balance: the check that needs no outcome
def smd(X, D, w, sd=None):
    """Standardised mean difference: weighted treated mean minus weighted control mean, over the raw treated SD."""
    sd = X[D == 1].std() if sd is None else sd
    t = np.average(X[D == 1], axis=0, weights=w[D == 1])
    c = np.average(X[D == 0], axis=0, weights=w[D == 0])
    return pd.Series((t - c) / sd, index=X.columns)


RAW_SD = X[D == 1].std()
one = np.ones(len(X))
balance = pd.DataFrame({"treated": X[D == 1].mean(), "control": X[D == 0].mean(), "smd": smd(X, D, one),
                        "var_ratio": X[D == 1].var() / X[D == 0].var()})
print("\nBalance before any adjustment (standardised units):")
print(balance.round(2).to_string())


# %% the propensity score and common support
def propensity(X, D):
    return sm.Logit(D, sm.add_constant(X)).fit(disp=0).predict(sm.add_constant(X)).to_numpy()


p = propensity(X, D)
lp = np.log(p / (1 - p))
lo, hi = p[D == 1].min(), p[D == 0].max()
print(f"\nEstimated propensity: treated {p[D == 1].min():.3f} to {p[D == 1].max():.3f}, "
      f"control {p[D == 0].min():.3f} to {p[D == 0].max():.3f}")
print(f"Treated above the highest control score: {(p[D == 1] > p[D == 0].max()).sum()}; "
      f"controls with score over 0.9: {((p > .9) & (D == 0)).sum()}; treated with score over 0.9: {((p > .9) & (D == 1)).sum()}")

fig, ax = cs.plt.subplots()
bins = np.linspace(lp.min(), lp.max(), 40)
ax.hist(lp[D == 1], bins=bins, color=cs.BLUE, alpha=.75, label="Joined the club", edgecolor=cs.SURFACE, linewidth=.5)
ax.hist(lp[D == 0], bins=bins, color=cs.ORANGE, alpha=.6, label="Did not join", edgecolor=cs.SURFACE, linewidth=.5)
ax.set_xlabel("Estimated log odds of joining")
ax.set_ylabel("Customers")
ax.set_title("Joiners and non-joiners overlap, but thin out at the top")
ax.legend(frameon=False, loc="upper left")
cs.save(fig, "causal-club-overlap.png")


# %% the designs: each returns weights that make the two groups comparable. Still no outcome
def stratum_weights(strata, D):
    """Exact matching on a stratum label, weighted as in Iacus, King and Porro (2012), equation 6."""
    s = pd.DataFrame({"s": strata, "D": D})
    n = s.groupby("s").D.agg(["sum", "count"])
    n["ctrl"] = n["count"] - n["sum"]
    n = n[(n["sum"] > 0) & (n.ctrl > 0)]
    mT, mC = n["sum"].sum(), n.ctrl.sum()
    keep = s.s.isin(n.index).to_numpy()
    w = np.zeros(len(s))
    w[keep & (D == 1)] = 1
    ratio = (mC / mT) * (n["sum"] / n.ctrl)
    w[keep & (D == 0)] = s.s[keep & (D == 0)].map(ratio).to_numpy()
    return w


def cem_strata(d):
    """Coarsen by choices a retailer could defend, then glue the bins into one label."""
    orders = pd.cut(d.prior_orders, [0, 1, 2, 3, 5, 9, np.inf], labels=False)
    spend = pd.cut(d.prior_spend, [-1, 25, 50, 75, 100, 150, 200, 300, 500, np.inf], labels=False)
    recency = pd.cut(d.recency_days, [-1, 30, 60, 90, 180, 270, np.inf], labels=False)
    tenure = pd.cut(d.tenure_days, [-1, 90, 180, 365, np.inf], labels=False)
    return (d.channel.astype(str) + "|" + orders.astype(str) + "|" + spend.astype(str) + "|"
            + recency.astype(str) + "|" + tenure.astype(str)).to_numpy()


def nearest_neighbour(lp, D, caliper, replace, seed=SEED):
    """1:1 nearest neighbour on the log odds. Returns weights and the matched pairs."""
    t, c = np.flatnonzero(D == 1), np.flatnonzero(D == 0)
    w, pairs = np.zeros(len(D)), []
    if replace:
        c = c[np.argsort(lp[c])]
        hi_i = np.searchsorted(lp[c], lp[t]).clip(1, len(c) - 1)
        nearest = np.where(np.abs(lp[c][hi_i - 1] - lp[t]) <= np.abs(lp[c][hi_i] - lp[t]), hi_i - 1, hi_i)
        ok = np.abs(lp[c][nearest] - lp[t]) <= caliper
        w[t[ok]] = 1
        np.add.at(w, c[nearest[ok]], 1)
        return w, np.c_[t[ok], c[nearest[ok]]]
    free = np.ones(len(c), bool)
    for i in np.random.default_rng(seed).permutation(t):
        gaps = np.abs(lp[c] - lp[i])
        gaps[~free] = np.inf
        j = gaps.argmin()
        if gaps[j] <= caliper:
            free[j] = False
            w[i], w[c[j]] = 1, 1
            pairs.append((i, c[j]))
    return w, np.array(pairs)


def entropy_balance(C, target):
    """Hainmueller's dual: find the weights nearest to uniform whose moments hit the target exactly."""
    C = C - target
    f = lambda z: np.log(np.exp(-C @ z).sum())
    def grad(z):
        w = np.exp(-C @ z)
        return -(C.T @ (w / w.sum()))
    fit = minimize(f, np.zeros(C.shape[1]), jac=grad, method="BFGS", options={"gtol": 1e-8, "maxiter": 5000})
    w = np.exp(-C @ fit.x)
    return w / w.sum()


def designs(d, X, D, p):
    """The ATT designs: weights on treated and control. Nothing here reads an outcome."""
    lp = np.log(p / (1 - p))
    caliper = .2 * lp.std()
    w = {}
    w["Exact: every covariate"] = stratum_weights((d.channel.astype(str) + "|" + d.prior_orders.astype(str) + "|"
                                                   + d.prior_spend.astype(str) + "|" + d.recency_days.astype(str) + "|"
                                                   + d.tenure_days.astype(str)).to_numpy(), D)
    w["Exact: channel and orders"] = stratum_weights((d.channel.astype(str) + "|" + d.prior_orders.astype(str)).to_numpy(), D)
    w["CEM"] = stratum_weights(cem_strata(d), D)
    w["PS match, with replacement"] = nearest_neighbour(lp, D, caliper, True)[0]
    w["PS match, no replacement"] = nearest_neighbour(lp, D, caliper, False)[0]
    wipw = np.where(D == 1, 1.0, p / (1 - p))
    w["Propensity weights"] = wipw
    xv = X.to_numpy()
    eb = np.ones(len(D))
    eb[D == 0] = entropy_balance(xv[D == 0], xv[D == 1].mean(0)) * (D == 1).sum()
    w["Entropy balancing"] = eb
    return w


W = designs(club, X, D, p)


def effective_n(w):
    return w.sum() ** 2 / (w ** 2).sum() if w.sum() else 0


rows = []
for name, w in W.items():
    b = smd(X, D, w, RAW_SD) if w[D == 1].sum() else pd.Series(np.nan, index=X.columns)
    rows.append({"design": name, "treated_kept": int((w[D == 1] > 0).sum()), "controls_used": int((w[D == 0] > 0).sum()),
                 "control_eff_n": round(effective_n(w[D == 0])), "max_control_wt_share": round(w[D == 0].max() / max(w[D == 0].sum(), 1e-9), 3),
                 "max_abs_smd": round(b.abs().max(), 3), "n_over_.1": int((b.abs() > .1).sum())})
print("\nDesigns, judged before any outcome is read:")
print(pd.DataFrame(rows).set_index("design").to_string())
print(f"\nSMD on all {X.shape[1]} covariates for each design:")
love = pd.DataFrame({"Before": smd(X, D, one, RAW_SD), **{k: smd(X, D, W[k], RAW_SD) for k in
                     ["Exact: channel and orders", "CEM", "PS match, with replacement", "Propensity weights", "Entropy balancing"]}})
print(love.round(3).to_string())

# %% Love plot
order = love.Before.abs().sort_values().index
yy = np.arange(len(order))
fig, ax = cs.plt.subplots(figsize=(8, 5))
ax.grid(axis="y", visible=False)
ax.grid(axis="x", color=cs.GRID)
ax.axvline(0, color=cs.BASELINE, lw=1)
ax.axvline(.1, color=cs.MUTED, lw=1, ls="--")
ax.axvline(-.1, color=cs.MUTED, lw=1, ls="--")
for name, col, mk in [("Before", cs.ORANGE, "o"), ("PS match, with replacement", cs.YELLOW, "s"), ("CEM", cs.AQUA, "D"), ("Entropy balancing", cs.BLUE, "o")]:
    ax.scatter(love.loc[order, name], yy, color=col, marker=mk, s=42, label=name, edgecolor=cs.SURFACE, linewidth=1, zorder=3)
ax.set_yticks(yy, [c.replace("ch_", "channel: ").replace("_", " ") for c in order])
ax.set_xlabel("Standardised difference, joiners minus comparison group (dashed lines at 0.1)")
ax.set_title("The designs close the gaps before any outcome is read")
ax.legend(frameon=False, loc="lower right")
cs.save(fig, "causal-club-love-plot.png")

# %% only now read the outcome
y = club.spend_next_6m.to_numpy()


def att(y, D, w):
    return np.average(y[D == 1], weights=w[D == 1]) - np.average(y[D == 0], weights=w[D == 0])


def arm_models(y, D, X):
    """Regression adjustment with a separate model per arm, so the effect may vary with X."""
    Xc = sm.add_constant(X)
    te = sm.OLS(y[D == 1], Xc[D == 1]).fit().predict(Xc) - sm.OLS(y[D == 0], Xc[D == 0]).fit().predict(Xc)
    return te.mean(), te[D == 1].mean()


def estimate_all(d, X, D, p, y, w=None):
    w = designs(d, X, D, p) if w is None else w
    xv = X.to_numpy()
    reg_ate, reg_att = arm_models(y, D, X)
    const = sm.OLS(y, sm.add_constant(X.assign(D=D))).fit().params["D"]
    cem_reg = sm.WLS(y, sm.add_constant(X.assign(D=D)), weights=w["CEM"]).fit().params["D"]
    a1 = entropy_balance(xv[D == 1], xv.mean(0)); a0 = entropy_balance(xv[D == 0], xv.mean(0))
    ipw_ate = np.average(y[D == 1], weights=1 / p[D == 1]) - np.average(y[D == 0], weights=1 / (1 - p[D == 0]))
    tp = np.where(D == 1, 1.0, p / (1 - p))
    trim = (p > .05) & (p < .95)
    est = {
        "Naive difference": ("ATT", y[D == 1].mean() - y[D == 0].mean(), one_(D)),
        "Regression, one coefficient": ("none", const, one_(D)),
        "Regression, by arm (ATE)": ("ATE", reg_ate, None),
        "Regression, by arm (ATT)": ("ATT", reg_att, one_(D)),
        "Exact: channel and orders": ("local ATT", att(y, D, w["Exact: channel and orders"]), w["Exact: channel and orders"]),
        "CEM": ("local ATT", att(y, D, w["CEM"]), w["CEM"]),
        "CEM + regression": ("local ATT", cem_reg, w["CEM"]),
        "PS match, with replacement": ("local ATT", att(y, D, w["PS match, with replacement"]), w["PS match, with replacement"]),
        "PS match, no replacement": ("local ATT", att(y, D, w["PS match, no replacement"]), w["PS match, no replacement"]),
        "Propensity weights (ATE)": ("ATE", ipw_ate, None),
        "Propensity weights (ATT)": ("ATT", att(y, D, tp), one_(D)),
        "Propensity weights, 0.05-0.95 (ATT)": ("local ATT", att(y, D, tp * trim), tp * trim),
        "Entropy balancing (ATE)": ("ATE", (a1 * y[D == 1]).sum() - (a0 * y[D == 0]).sum(), None),
        "Entropy balancing (ATT)": ("ATT", att(y, D, w["Entropy balancing"]), one_(D)),
    }
    return est


def one_(D):
    return np.ones(len(D))


EST = estimate_all(club, X, D, p, y, W)
print("\nOne dataset, every estimator (pounds over six months):")
print(pd.DataFrame({k: {"targets": v[0], "estimate": round(v[1], 2)} for k, v in EST.items()}).T.to_string())

# %% SCORING: compare with the truth the generator kept back
te = (club.true_y1 - club.true_y0).to_numpy()
true_ate, true_att = te.mean(), te[D == 1].mean()
print(f"\nSCORING. True ATE {true_ate:.2f}, true ATT {true_att:.2f}, true ATC {te[D == 0].mean():.2f}")


def truth_for(target, w, te, D):
    if target == "ATE" or target == "none":
        return te.mean()
    return np.average(te[D == 1], weights=w[D == 1])


score = pd.DataFrame({k: {"targets": v[0], "estimate": round(v[1], 2), "truth": round(truth_for(v[0], v[2], te, D), 2),
                          "gap": round(v[1] - truth_for(v[0], v[2], te, D), 2)} for k, v in EST.items()}).T
print(score.to_string())


# %% SCORING: one dataset is one draw. Twenty fresh customer bases give the spread
def fit_all(s):
    d = load_club(seed=s)
    D_, X_ = d.club.to_numpy(), design_matrix(d)
    p_ = propensity(X_, D_)
    e = estimate_all(d, X_, D_, p_, d.spend_next_6m.to_numpy())
    te_ = (d.true_y1 - d.true_y0).to_numpy()
    return {k: v[1] - truth_for(v[0], v[2], te_, D_) for k, v in e.items()}


SEEDS = [SEED] + list(range(1, 20))
runs = pd.DataFrame([fit_all(s) for s in SEEDS])
mc = pd.DataFrame({"mean_gap": runs.mean(), "se_of_mean": runs.std() / np.sqrt(len(runs)), "sd_across_runs": runs.std(), "rmse": np.sqrt((runs ** 2).mean())})
print(f"\nSCORING. Gap from the truth for each estimator's own target, over {len(SEEDS)} generated datasets:")
print(mc.round(2).to_string())

fig, ax = cs.plt.subplots(figsize=(8, 5))
ax.grid(axis="y", visible=False)
ax.grid(axis="x", color=cs.GRID)
show = ["Regression, by arm (ATT)", "CEM", "CEM + regression", "PS match, with replacement", "PS match, no replacement", "Propensity weights (ATT)", "Propensity weights, 0.05-0.95 (ATT)", "Entropy balancing (ATT)"]
yy = np.arange(len(show))[::-1]
ax.axvline(0, color=cs.INK, lw=1)
ax.hlines(yy, runs[show].min(), runs[show].max(), color=cs.BASELINE, lw=2, label="Range over 20 datasets")
ax.scatter(runs[show].mean(), yy, color=cs.BLUE, s=48, zorder=3, edgecolor=cs.SURFACE, label="Average gap")
ax.set_yticks(yy, show)
ax.set_xlabel("Estimate minus truth for the customers each method keeps (pounds)")
ax.set_title("Every ATT design lands above the truth on average")
ax.legend(frameon=False, loc="lower right")
cs.save(fig, "causal-club-estimates.png")


# %% SCORING: the unobserved confounder, and the zero floor on spend
def rebuild_y0_no_floor(d, rng):
    """Redraw Y0 from the generator's published equation, with and without its clip at zero."""
    g = CLUB_DGP["y0"]
    z = lambda v: (v - v.mean()) / v.std()
    zo, zs, zr = z(np.log1p(d.prior_orders)), z(np.log1p(d.prior_spend)), z(d.recency_days)
    mu = (g["const"] + g["z_log_prior_orders"] * zo + g["z_log_prior_spend"] * zs + g["z_log_prior_spend_squared"] * zs ** 2
          + g["z_recency"] * zr + d.channel.map(CLUB_DGP["y0_channel"]) + g["unobserved_engagement"] * d.true_engagement)
    return (mu + rng.normal(0, g["noise_sd"], len(d))).to_numpy()


def eb_att(y, D, X):
    xv = X.to_numpy()
    return y[D == 1].mean() - (entropy_balance(xv[D == 0], xv[D == 1].mean(0)) * y[D == 0]).sum()


floor = []
for s in SEEDS:
    d = load_club(seed=s)
    D_ = d.club.to_numpy()
    te_ = (d.true_y1 - d.true_y0).to_numpy()
    X_, XU = design_matrix(d), design_matrix(d).assign(engagement=(d.true_engagement - d.true_engagement.mean()) / d.true_engagement.std())
    y0 = rebuild_y0_no_floor(d, np.random.default_rng(s + 999))
    worlds = {"generator's table": d.spend_next_6m.to_numpy(), "redrawn, with floor": y0.clip(0) + te_ * D_, "redrawn, no floor": y0 + te_ * D_}
    for world, yy_ in worlds.items():
        for adj, XX in [("observed", X_), ("observed + engagement", XU)]:
            floor.append({"world": world, "adjust": adj, "seed": s, "regression": arm_models(yy_, D_, XX)[1] - te_[D_ == 1].mean(),
                          "entropy": eb_att(yy_, D_, XX) - te_[D_ == 1].mean(),
                          "weights": att(yy_, D_, np.where(D_ == 1, 1.0, (q := propensity(XX, D_)) / (1 - q))) - te_[D_ == 1].mean()})
floor = pd.DataFrame(floor)
print("\nSCORING. ATT gap by world and adjustment set, mean over 20 datasets (standard error of the mean in brackets):")
ft = floor.groupby(["world", "adjust"], sort=False)[["regression", "entropy", "weights"]]
print((ft.mean().round(2).astype(str) + " (" + ft.sem().round(2).astype(str) + ")").to_string())

# %% SCORING: the bad control
post = X.assign(sessions=(club.sessions_next_6m - club.sessions_next_6m.mean()) / club.sessions_next_6m.std())
print(f"\nSCORING. Bad control. Regression ATT without sessions_next_6m {arm_models(y, D, X)[1]:.2f}, with it {arm_models(y, D, post)[1]:.2f}; truth {true_att:.2f}")
print(f"One-coefficient regression without it {sm.OLS(y, sm.add_constant(X.assign(D=D))).fit().params['D']:.2f}, with it {sm.OLS(y, sm.add_constant(post.assign(D=D))).fit().params['D']:.2f}; true ATE {true_ate:.2f}")
print(f"Entropy balancing ATT without it {eb_att(y, D, X):.2f}, with it {eb_att(y, D, post):.2f}")
gaps = []
for s in SEEDS:
    d = load_club(seed=s)
    D_ = d.club.to_numpy()
    X_ = design_matrix(d)
    Xp = X_.assign(sessions=(d.sessions_next_6m - d.sessions_next_6m.mean()) / d.sessions_next_6m.std())
    gaps.append({"without": arm_models(d.spend_next_6m.to_numpy(), D_, X_)[1] - (d.true_y1 - d.true_y0)[D_ == 1].mean(),
                 "with": arm_models(d.spend_next_6m.to_numpy(), D_, Xp)[1] - (d.true_y1 - d.true_y0)[D_ == 1].mean()})
print("Regression ATT gap over 20 datasets:", pd.DataFrame(gaps).mean().round(2).to_dict())

# %% DoWhy as the cross-check
import dowhy

frame = X.assign(club=D.astype(bool), spend=y)
model = dowhy.CausalModel(data=frame, treatment="club", outcome="spend", common_causes=list(X.columns))
estimand = model.identify_effect(proceed_when_unidentifiable=True)
print(f"\nDoWhy {dowhy.__version__}. Backdoor set: {len(estimand.get_backdoor_variables())} variables")
for method, target in [("backdoor.linear_regression", "ate"), ("backdoor.propensity_score_weighting", "ate"), ("backdoor.propensity_score_weighting", "att"),
                       ("backdoor.propensity_score_matching", "att"), ("backdoor.propensity_score_stratification", "att")]:
    try:
        e = model.estimate_effect(estimand, method_name=method, target_units=target, test_significance=False)
        print(f"  {method:45s} {target}  {e.value:8.2f}")
    except Exception as ex:
        print(f"  {method:45s} {target}  FAILED: {type(ex).__name__}: {ex}")
base = model.estimate_effect(estimand, method_name="backdoor.linear_regression", test_significance=False)
ref = model.refute_estimate(estimand, base, method_name="random_common_cause", num_simulations=10, random_seed=SEED)
print(f"  random common cause refuter: {ref.estimated_effect:.2f} becomes {ref.new_effect:.2f}")
ref = model.refute_estimate(estimand, base, method_name="placebo_treatment_refuter", placebo_type="permute", num_simulations=10, random_seed=SEED)
print(f"  placebo treatment refuter: {ref.estimated_effect:.2f} becomes {ref.new_effect:.2f}")


# %% sensitivity 1: the E-value, on the ratio of means
def e_value(rr):
    rr = max(rr, 1 / rr)
    return rr + np.sqrt(rr * (rr - 1))


rng = np.random.default_rng(SEED)
tw = W["Entropy balancing"]
y1_mean, y0_mean = y[D == 1].mean(), np.average(y[D == 0], weights=tw[D == 0])
boot_ratio, boot_att = [], []
xv = X.to_numpy()
for _ in range(300):
    i = rng.integers(0, len(y), len(y))
    Db, yb, xb = D[i], y[i], xv[i]
    wb = entropy_balance(xb[Db == 0], xb[Db == 1].mean(0))
    boot_ratio.append(yb[Db == 1].mean() / (wb * yb[Db == 0]).sum())
    boot_att.append(yb[Db == 1].mean() - (wb * yb[Db == 0]).sum())
ratio = y1_mean / y0_mean
lo_r = np.percentile(boot_ratio, 2.5)
print(f"\nEntropy balancing ATT {y1_mean - y0_mean:.2f}, bootstrap 95% interval {np.percentile(boot_att, 2.5):.2f} to {np.percentile(boot_att, 97.5):.2f}")
print(f"Ratio of means {y1_mean:.2f} / {y0_mean:.2f} = {ratio:.3f}, bootstrap lower limit {lo_r:.3f}")
print(f"E-value for the estimate {e_value(ratio):.2f}, for the interval's lower limit {e_value(lo_r):.2f}")

# %% sensitivity 2: Rosenbaum bounds on the matched pairs
_, pairs = nearest_neighbour(lp, D, .2 * lp.std(), False)
diff = y[pairs[:, 0]] - y[pairs[:, 1]]


def wilcoxon_upper_p(diff, gamma):
    """Upper bound on the one-sided signed-rank p value when hidden bias can tilt each pair's odds by gamma."""
    diff = diff[diff != 0]
    r = rankdata(np.abs(diff))
    stat = r[diff > 0].sum()
    pplus = gamma / (1 + gamma)
    return norm.sf((stat - pplus * r.sum()) / np.sqrt(pplus * (1 - pplus) * (r ** 2).sum()))


grid = np.round(np.arange(1, 4.01, .05), 2)
print(f"\nRosenbaum bounds on {len(pairs)} matched pairs (treated minus control, mean {diff.mean():.2f}, median {np.median(diff):.2f}):")
print(pd.Series({g: wilcoxon_upper_p(diff, g) for g in [1, 1.25, 1.5, 1.75, 2, 2.5, 3]}, name="upper p").round(4).to_string())
g_star = next((g for g in grid if wilcoxon_upper_p(diff, g) > .05), None)
print(f"Smallest gamma with upper p above 0.05: {g_star}")

# %% sensitivity 3: the arithmetic an analyst can do, and how the planted confounder scores
print("\nATT if a hidden trait moves spend by gamma pounds per SD and stays delta SD out of balance after weighting:")
grid_t = pd.DataFrame({f"delta {dl}": {f"gamma {g}": round(y1_mean - y0_mean - g * dl, 1) for g in [5, 10, 20, 30]} for dl in [.1, .25, .5, 1]})
print(grid_t.to_string())
Xz = X.copy()
coef = sm.OLS(y[D == 0], sm.add_constant(Xz[D == 0])).fit().params
print("\nBenchmarks from what is observed, control-group spend per SD of each covariate, and its imbalance before weighting:")
print(pd.DataFrame({"pounds_per_sd": coef.drop("const"), "smd_before": smd(X, D, one, RAW_SD)}).round(2).to_string())

# SCORING
u = ((club.true_engagement - club.true_engagement.mean()) / club.true_engagement.std()).to_numpy()
delta_before = u[D == 1].mean() - u[D == 0].mean()
delta_after = u[D == 1].mean() - np.average(u[D == 0], weights=tw[D == 0])
gamma_true = CLUB_DGP["y0"]["unobserved_engagement"]
gap_eb = y1_mean - y0_mean - true_att
print(f"\nSCORING. Engagement imbalance in SD: before {delta_before:.2f}, after entropy balancing {delta_after:.2f}")
print(f"Planted gamma {gamma_true} times remaining delta {delta_after:.2f} = {gamma_true * delta_after:.2f}; actual gap {gap_eb:.2f}")
true_ratio = y1_mean / (y1_mean - true_att)
print(f"True ratio of means {true_ratio:.3f}. E-value to move the estimate to the null {e_value(ratio):.2f}, to the truth {e_value(ratio / true_ratio):.2f}")
odds = np.exp(CLUB_DGP["logit_join"]["unobserved_engagement"] * np.abs(u[pairs[:, 0]] - u[pairs[:, 1]]))
print(f"Hidden odds ratio inside matched pairs from engagement: median {np.median(odds):.2f}, 90th percentile {np.percentile(odds, 90):.2f}, 99th {np.percentile(odds, 99):.2f}")
