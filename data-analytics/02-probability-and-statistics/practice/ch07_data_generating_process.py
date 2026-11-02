# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "matplotlib", "statsmodels", "patsy", "scikit-learn"]
# ///
"""Chapter 7: the data generating process. Fit, specification and generalisation.

Every dataset here is simulated, because the point is to know the truth and see
which estimates recover it.

Run from this folder with: uv run ch07_data_generating_process.py
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from patsy import dmatrix
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_score
from statsmodels.stats.anova import anova_lm

import chartstyle as cs

cs.apply()
pd.set_option("display.width", 130, "display.max_columns", 20)

# %% write the DGP
# A model is a claim about how the rows were generated. Here is the claim, as code.
TRUE_COUPON = 0.20  # coupon multiplies spend by exp(0.20)


def simulate(n, rng):
    """One Larkspur customer per row: tenure, a targeted coupon, annual spend."""
    tenure = rng.uniform(1, 60, n)
    # Marketing aims coupons at mid-tenure customers, who also spend the most.
    p_coupon = 0.15 + 0.60 * np.exp(-(((tenure - 30) / 15) ** 2))
    coupon = rng.binomial(1, p_coupon)
    log_spend = 2.6 + TRUE_COUPON * coupon + 0.14 * tenure - 0.0024 * tenure**2 + rng.normal(0, 0.5, n)
    return pd.DataFrame({"tenure": tenure, "coupon": coupon, "spend": np.exp(log_spend), "log_spend": log_spend})


rng = np.random.default_rng(7)
df = simulate(800, rng)
print(df.head(3).round(2).to_string(index=False))
print(f"true effect on log spend {TRUE_COUPON}, so a lift of {np.exp(TRUE_COUPON) - 1:.1%}")

# %% the same estimand in pounds, by brute force
big = simulate(2_000_000, np.random.default_rng(1))
no_coupon = np.exp(big.log_spend - TRUE_COUPON * big.coupon)
true_gbp = ((np.exp(TRUE_COUPON) - 1) * no_coupon).mean()
true_gbp_att = ((np.exp(TRUE_COUPON) - 1) * no_coupon)[big.coupon == 1].mean()
print(f"true average effect in pounds: all customers {true_gbp:.2f}, customers who got a coupon {true_gbp_att:.2f}")

# %% one dataset, four estimators
FORMULAS = {
    "difference in means": "log_spend ~ coupon",
    "linear tenure": "log_spend ~ coupon + tenure",
    "quadratic tenure (true form)": "log_spend ~ coupon + tenure + I(tenure**2)",
    "spline tenure, df=5": "log_spend ~ coupon + bs(tenure, df=5)",
}
for name, f in FORMULAS.items():
    m = smf.ols(f, df).fit()
    print(f"{name:30s} coupon {m.params['coupon']:6.3f}  se {m.bse['coupon']:.3f}  R2 {m.rsquared:.3f}")

# %% does the estimator recover the truth, over many datasets?
def recovery(reps=1000, n=800, seed=11):
    r = np.random.default_rng(seed)
    rows = {k: [] for k in [*FORMULAS, "pounds, quadratic in levels"]}
    for _ in range(reps):
        d = simulate(n, r)
        for name, f in FORMULAS.items():
            m = smf.ols(f, d).fit()
            lo, hi = m.conf_int().loc["coupon"]
            rows[name].append((m.params["coupon"], lo <= TRUE_COUPON <= hi))
        m = smf.ols("spend ~ coupon + tenure + I(tenure**2)", d).fit(cov_type="HC3")
        lo, hi = m.conf_int().loc["coupon"]
        rows["pounds, quadratic in levels"].append((m.params["coupon"], lo <= true_gbp <= hi))
    out = []
    for name, v in rows.items():
        est, hit = map(np.array, zip(*v))
        truth = true_gbp if name.startswith("pounds") else TRUE_COUPON
        out.append(dict(estimator=name, truth=truth, mean=est.mean(), bias=est.mean() - truth,
                        sd=est.std(ddof=1), coverage=hit.mean()))
    return pd.DataFrame(out).round(3)


print(recovery().to_string(index=False))

# %% compare specifications: fit statistics on one dataset
DEGREES = {"linear": 1, "quadratic": 2, "cubic": 3, "degree 6": 6, "degree 10": 10}
d300 = simulate(300, np.random.default_rng(21))
d300["z"] = (d300.tenure - 30) / 30  # rescale so high powers stay well conditioned


def poly(k):
    return " + ".join(f"I(z**{j})" for j in range(1, k + 1))


specs = {name: f"log_spend ~ coupon + {poly(k)}" for name, k in DEGREES.items()}
specs |= {"spline df=5": "log_spend ~ coupon + bs(z, df=5)", "spline df=15": "log_spend ~ coupon + bs(z, df=15)"}


def cv_rmse(formula, data, seed=0):
    X = np.asarray(dmatrix(formula.split("~")[1], data))
    scores = cross_val_score(LinearRegression(fit_intercept=False), X, data.log_spend,
                             cv=KFold(10, shuffle=True, random_state=seed),
                             scoring="neg_root_mean_squared_error")
    return -scores.mean()


fits = {name: smf.ols(f, d300).fit() for name, f in specs.items()}
table = pd.DataFrame([dict(model=n, params=int(m.df_model) + 1, R2=m.rsquared, adj_R2=m.rsquared_adj, AIC=m.aic,
                           BIC=m.bic, cv_rmse=cv_rmse(specs[n], d300), coupon=m.params["coupon"])
                      for n, m in fits.items()])
print(table.round(3).to_string(index=False))

# %% likelihood-ratio and F tests, which need nested models
print(anova_lm(fits["linear"], fits["quadratic"], fits["cubic"], fits["degree 6"]).round(4).to_string())
for small, large in [("linear", "quadratic"), ("quadratic", "cubic"), ("quadratic", "degree 6")]:
    lr, p, df_diff = fits[large].compare_lr_test(fits[small])
    print(f"LR test {small} vs {large}: chi2 {lr:.2f}, df {df_diff:.0f}, p {p:.4f}")

# %% how often does each rule choose the true form?
def selection(n, reps=300, seed=31):
    r = np.random.default_rng(seed)
    tally = {rule: {k: 0 for k in DEGREES} for rule in ["R2", "adj_R2", "AIC", "BIC", "CV"]}
    for _ in range(reps):
        d = simulate(n, r)
        z = ((d.tenure - 30) / 30).to_numpy()
        res = {}
        for name, k in DEGREES.items():
            X = sm.add_constant(np.column_stack([d.coupon] + [z**j for j in range(1, k + 1)]))
            m = sm.OLS(d.log_spend.to_numpy(), X).fit()
            folds = KFold(5, shuffle=True, random_state=0)
            cv = -cross_val_score(LinearRegression(fit_intercept=False), X, d.log_spend, cv=folds,
                                  scoring="neg_root_mean_squared_error").mean()
            res[name] = dict(R2=-m.rsquared, adj_R2=-m.rsquared_adj, AIC=m.aic, BIC=m.bic, CV=cv)
        for rule in tally:
            tally[rule][min(res, key=lambda name: res[name][rule])] += 1
    return (pd.DataFrame(tally).T / reps).round(2)


for n in (100, 800):
    print(f"share of {300} datasets picking each form, n={n}")
    print(selection(n).to_string())

# %% when a quadratic is a story, and when it is overfitting
r = np.random.default_rng(41)
t = r.uniform(1, 60, 800)
truths = {"Truth rises then falls": lambda x: 0.14 * x - 0.0024 * x**2,
          "Truth rises then flattens": lambda x: 2.0 * (1 - np.exp(-x / 15))}
grid = pd.DataFrame({"t": np.linspace(t.min(), t.max(), 200)})  # patsy's bs() will not extrapolate past its knots
curves = {}
for label, f in truths.items():
    d = pd.DataFrame({"t": t, "y": f(t) + r.normal(0, 0.5, t.size)})
    q = smf.ols("y ~ t + I(t**2)", d).fit()
    s = smf.ols("y ~ bs(t, df=6, include_intercept=False)", d).fit()
    b1, b2 = q.params["t"], q.params["I(t ** 2)"]
    peak = -b1 / (2 * b2)
    # bootstrap the turning point
    boots = []
    for _ in range(500):
        bd = d.sample(len(d), replace=True, random_state=int(r.integers(1e9)))
        bm = smf.ols("y ~ t + I(t**2)", bd).fit()
        boots.append(-bm.params["t"] / (2 * bm.params["I(t ** 2)"]))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    fall_q = q.predict(pd.DataFrame({"t": [60.0]})).iloc[0] - q.predict(pd.DataFrame({"t": [min(peak, 60.0)]})).iloc[0]
    print(f"{label}: t^2 coef {b2:.5f} (p {q.pvalues['I(t ** 2)']:.1e}); quadratic peak at {peak:.1f} "
          f"[{lo:.1f}, {hi:.1f}]; quadratic says peak-to-60 change {fall_q:.2f}, truth {f(60.0) - f(min(peak, 60.0)):.2f}; "
          f"R2 quad {q.rsquared:.3f}, spline {s.rsquared:.3f}")
    curves[label] = (d, q.predict(grid), s.predict(grid), f(grid.t), peak)

fig, axes = cs.plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, (label, (d, qf, sf, tf, peak)) in zip(axes, curves.items()):
    ax.scatter(d.t, d.y, s=6, color=cs.MUTED, alpha=0.35, linewidths=0)
    ax.plot(grid.t, tf, color=cs.INK, lw=2, label="True curve")
    ax.plot(grid.t, qf, color=cs.ORANGE, lw=2, label="Quadratic fit")
    ax.plot(grid.t, sf, color=cs.BLUE, lw=2, label="Spline fit (df=6)")
    ax.axvline(peak, color=cs.ORANGE, lw=1, ls=":")
    ax.set_title(label)
    ax.set_xlabel("Tenure (months)")
axes[0].set_ylabel("Outcome (log scale)")
axes[0].legend(frameon=False, loc="lower center")
cs.save(fig, "stats-dgp-quadratic-story.png")

# %% explain or predict: the true model is not always the best predictor
def explain_vs_predict(n, reps=2000, b1=1.0, b2=0.2, rho=0.9, sigma=2.0, seed=51):
    r = np.random.default_rng(seed)
    cov = [[1, rho], [rho, 1]]
    est_full, est_short, mse_full, mse_short = [], [], [], []
    for _ in range(reps):
        X = r.multivariate_normal([0, 0], cov, n)
        y = b1 * X[:, 0] + b2 * X[:, 1] + r.normal(0, sigma, n)
        full = np.linalg.lstsq(sm.add_constant(X), y, rcond=None)[0]
        short = np.linalg.lstsq(sm.add_constant(X[:, 0]), y, rcond=None)[0]
        Xt = r.multivariate_normal([0, 0], cov, 2000)
        yt = b1 * Xt[:, 0] + b2 * Xt[:, 1] + r.normal(0, sigma, 2000)
        mse_full.append(np.mean((yt - sm.add_constant(Xt) @ full) ** 2))
        mse_short.append(np.mean((yt - sm.add_constant(Xt[:, 0]) @ short) ** 2))
        est_full.append(full[1])
        est_short.append(short[1])
    return dict(n=n, b1_true_form=np.mean(est_full), sd_true_form=np.std(est_full), b1_short=np.mean(est_short),
                sd_short=np.std(est_short), test_rmse_true_form=np.sqrt(np.mean(mse_full)),
                test_rmse_short=np.sqrt(np.mean(mse_short)), short_wins=np.mean(np.array(mse_short) < np.array(mse_full)))


print(pd.DataFrame([explain_vs_predict(n) for n in (30, 300, 3000)]).round(3).to_string(index=False))

# %% internal and external validity: a clean experiment on the wrong people
POP = 2_000_000
r = np.random.default_rng(61)
pop = pd.DataFrame({"tenure": r.uniform(1, 60, POP), "keen": r.binomial(1, 0.3, POP)})
pop["new"] = (pop.tenure < 12).astype(int)
# The coupon works better on new customers and on keen gardeners.
pop["effect"] = 0.05 + 0.25 * pop.new + 0.20 * pop.keen
print(f"population average effect {pop.effect.mean():.3f}")


def experiment(sample, seed=0, label=""):
    """Randomise inside the sample. Report sample truth, estimate, and reweighted estimate."""
    rr = np.random.default_rng(seed)
    d = sample.copy()
    d["t"] = rr.binomial(1, 0.5, len(d))
    d["y"] = 3 + 0.01 * d.tenure + d.effect * d.t + rr.normal(0, 0.5, len(d))
    m = smf.ols("y ~ t", d).fit()
    by = {g: smf.ols("y ~ t", x).fit().params["t"] for g, x in d.groupby("new")}
    weights = pop.new.value_counts(normalize=True)
    reweighted = sum(by[g] * weights[g] for g in by)
    return dict(sample=label, n=len(d), share_new=d.new.mean(), share_keen=d.keen.mean(),
                sample_truth=d.effect.mean(), estimate=m.params["t"], se=m.bse["t"], reweighted_on_new=reweighted)


opt_tenure = pop[r.random(POP) < np.where(pop.new == 1, 0.002, 0.03)]  # panel volunteers skew long-tenure
opt_keen = pop[r.random(POP) < np.where(pop.keen == 1, 0.05, 0.003)]  # volunteers skew keen, which we do not record
rand = pop.sample(20000, random_state=3)
print(pd.DataFrame([experiment(rand, 1, "random"), experiment(opt_tenure, 2, "selected on tenure"),
                    experiment(opt_keen, 3, "selected on keenness")]).round(3).to_string(index=False))

# %% Meng: the identity holds to machine precision
def population(N, seed=71, prevalence=0.30):
    return np.random.default_rng(seed).binomial(1, prevalence, N).astype(float)


def self_select(G, f, rho, rng):
    """Recording indicator R with target response rate f and target correlation rho with G."""
    p = G.mean()
    gap = rho * np.sqrt(f * (1 - f) / (p * (1 - p)))
    p0 = f - p * gap
    return rng.random(G.size) < np.where(G == 1, p0 + gap, p0)


N = 10_000_000
G = population(N)
R = self_select(G, 0.10, 0.02, np.random.default_rng(72))
n = R.sum()
f = n / N
rho_hat = np.corrcoef(R, G)[0, 1]
lhs = G[R].mean() - G.mean()
rhs = rho_hat * np.sqrt((1 - f) / f) * G.std()
print(f"N {N:,}, n {n:,}, f {f:.4f}, rho {rho_hat:.5f}, population mean {G.mean():.5f}, sample mean {G[R].mean():.5f}")
print(f"response rate with the trait {R[G == 1].mean():.4f}, without it {R[G == 0].mean():.4f}")
print(f"actual error {lhs:.10f}; rho x sqrt((1-f)/f) x sigma {rhs:.10f}; difference {lhs - rhs:.1e}")

# %% effective sample size: what is that big sample worth?
def n_eff(f, rho, N):
    star = f / (1 - f) / rho**2
    return star / (1 + (star - 1) / N)


sigma = G.std()
rows = []
for f_ in (0.001, 0.01, 0.10, 0.50):
    for rho_ in (0.005, 0.02):
        Rx = self_select(G, f_, rho_, np.random.default_rng(73))
        err = G[Rx].mean() - G.mean()
        se = np.sqrt(G[Rx].var(ddof=1) / Rx.sum())
        rows.append(dict(f=f_, rho=rho_, n=int(Rx.sum()), error=err, naive_se=se, z=err / se, n_eff=n_eff(f_, rho_, N)))
print(pd.DataFrame(rows).round({"error": 4, "naive_se": 5, "z": 1, "n_eff": 0}).to_string(index=False))

# %% the big sample against a small random one
ne = int(round(n_eff(0.10, 0.02, N)))
rng2 = np.random.default_rng(74)
srs = np.array([rng2.choice(G, ne, replace=False).mean() for _ in range(2000)]) - G.mean()
sel = np.array([G[self_select(G, 0.10, 0.02, rng2)].mean() for _ in range(50)]) - G.mean()
sel_se = np.sqrt(G.mean() * (1 - G.mean()) / (0.10 * N))
srs_cover = np.mean(np.abs(srs) <= 1.96 * np.sqrt(G.mean() * (1 - G.mean()) / ne))
print(f"random sample of {ne}: RMSE {np.sqrt((srs**2).mean()):.4f}, 95% interval covers truth {srs_cover:.1%}")
print(f"self-selected ~{int(0.10 * N):,}: RMSE {np.sqrt((sel**2).mean()):.4f}, naive SE {sel_se:.5f}, "
      f"interval covers truth {np.mean(np.abs(sel) <= 1.96 * sel_se):.1%} of {sel.size} draws")

# %% growing the population makes it worse, not better
rows = []
for N_ in (100_000, 1_000_000, 10_000_000):
    Gx = population(N_, seed=75)
    Rx = self_select(Gx, 0.10, 0.02, np.random.default_rng(76))
    err = Gx[Rx].mean() - Gx.mean()
    se = np.sqrt(Gx[Rx].var(ddof=1) / Rx.sum())
    rows.append(dict(N=N_, n=int(Rx.sum()), error=err, naive_se=se, error_in_ses=err / se, n_eff=n_eff(0.10, 0.02, N_)))
print(pd.DataFrame(rows).round({"error": 4, "naive_se": 5, "error_in_ses": 1, "n_eff": 0}).to_string(index=False))

# %% figure: the narrow interval in the wrong place
est_sel = G.mean() + sel[0]
ex = rng2.choice(G, ne, replace=False).mean()
ex_se = np.sqrt(ex * (1 - ex) / ne)
fig, ax = cs.plt.subplots(figsize=(8, 2.8))
labels = [f"Random sample, n = {ne:,}", "Self-selected sample, n = 1,000,000"]
for y, (e, s, c) in enumerate([(ex, ex_se, cs.BLUE), (est_sel, sel_se, cs.ORANGE)]):
    ax.plot([e - 1.96 * s, e + 1.96 * s], [y, y], color=c, lw=2)
    ax.plot(e, y, "o", color=c, ms=8)
ax.axvline(G.mean(), color=cs.INK, lw=1.5)
ax.annotate("Population truth", (G.mean(), 1.42), xytext=(6, 0), textcoords="offset points", ha="left", color=cs.INK, fontsize=10)
ax.set_yticks([0, 1], labels)
ax.set_ylim(-0.5, 1.7)
ax.set_xlabel("Estimated share, with 95% interval")
cs.save(fig, "stats-dgp-meng-interval.png")

# %% does a better fit generalise? Three ways into the sample
def segment_population(N, seed=81):
    r = np.random.default_rng(seed)
    x = r.normal(0, 1, N)
    keen = r.random(N) < 0.2
    # Keen customers respond strongly and predictably. Everyone else barely responds.
    y = np.where(keen, 1 + 2.0 * x + r.normal(0, 0.5, N), 0.2 * x + r.normal(0, 2.0, N))
    return x, y, keen


x, y, keen = segment_population(1_000_000)
r = np.random.default_rng(82)
samples = {"random, n=500": r.choice(x.size, 500, replace=False),
           "opt-in on x, n~100k": np.flatnonzero(r.random(x.size) < 0.2 * (x > 0)),
           "opt-in on segment, n~100k": np.flatnonzero(r.random(x.size) < np.where(keen, 0.45, 0.012))}
pop_fit = sm.OLS(y, sm.add_constant(x)).fit()
print(f"best linear fit on the whole population: slope {pop_fit.params[1]:.3f}, R2 {pop_fit.rsquared:.3f}, "
      f"RMSE {np.sqrt(pop_fit.mse_resid):.3f}")
rows = []
for label, idx in samples.items():
    m = sm.OLS(y[idx], sm.add_constant(x[idx])).fit()
    pred = m.params[0] + m.params[1] * x
    rows.append(dict(sample=label, n=idx.size, share_keen=keen[idx].mean(), slope=m.params[1], sample_R2=m.rsquared,
                     sample_rmse=np.sqrt(m.mse_resid), population_rmse=np.sqrt(np.mean((y - pred) ** 2))))
print(pd.DataFrame(rows).round(3).to_string(index=False))

# %% Try it: answers
# 1. Set the coupon's true effect to zero. What does each estimator now report?
r = np.random.default_rng(91)
placebo = {k: [] for k in ["log_spend ~ coupon + tenure", "log_spend ~ coupon + tenure + I(tenure**2)"]}
for _ in range(300):
    d = simulate(800, r)
    d["log_spend"] -= TRUE_COUPON * d.coupon
    for f in placebo:
        m = smf.ols(f, d).fit()
        placebo[f].append((m.params["coupon"], m.pvalues["coupon"] < 0.05))
for f, v in placebo.items():
    est, sig = zip(*v)
    print(f"{f}: mean coupon {np.mean(est):.3f}, significant at 5% in {np.mean(sig):.1%} of datasets")

# 2. Meng's two worked numbers, from the formula.
print(f"f=0.5, rho=0.05, N=230m: n_eff {n_eff(0.5, 0.05, 230_000_000):.0f}")
print(f"f=0.01, rho=0.005, N=231,557,000: n_eff {n_eff(0.01, 0.005, 231_557_000):.0f}, "
      f"Z {np.sqrt(231_557_000 * 0.01) * np.sqrt(99 * 0.005**2 / (1 - 99 * 0.005**2)):.2f}")

# 3. Uncorrelated predictors: the short model is no longer biased in b1.
print(pd.DataFrame([explain_vs_predict(n, rho=0.0, reps=1000) for n in (30, 300)]).round(3).to_string(index=False))
