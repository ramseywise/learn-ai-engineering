---
origin: synthesis
sources:
  - James, Witten, Hastie, Tibshirani & Taylor, An Introduction to Statistical Learning with Applications in Python (Springer, 2023), https://www.statlearning.com/ (ch. 3, Linear Regression)
  - Bruce & Bruce, Practical Statistics for Data Scientists (O'Reilly, 2017) (ch. 4, Regression and Prediction)
  - Efron & Hastie, Computer Age Statistical Inference (Cambridge, 2016), https://hastie.su.domains/CASI/ (ch. 7, ridge; ch. 16-18, lasso, boosting and neural networks as GLM relatives)
  - https://www.statsmodels.org/stable/index.html
  - https://doi.org/10.3368/jhr.50.2.317 (Cameron and Miller, J. Human Resources, 2015; authors' draft read)
  - Downey, Think Stats (Green Tea Press, 2011), https://allendowney.github.io/ThinkStats/ (ch. 9, Correlation)
  - Reinhart, Statistics Done Wrong (No Starch, 2015) (ch. 7, Continuity Errors; ch. 8, Model Abuse)
confidence: high
cleaned: 2026-11-08
---
# 6 — Regression and GLMs

Larkspur's A/B test has 20,000 users and an effect that a t-test finds at p = 0.0001. Add one line to the analysis, the amount each user spent the month before, and the standard error falls by about 16% with no extra traffic. That line turns the t-test into a regression, and regression is what makes it possible. It holds other things fixed, it reports what a covariate is worth, and with a small change it handles conversions and counts as well. This chapter treats regression as the analyst uses it, an estimate with a standard error, whereas [data science](../../../data-science/README.md) treats it as a predictor. The two uses need different checks.

## Why this chapter

A t-test ([chapter 5](05-hypothesis-testing.md)) is a regression with one binary regressor. Seeing it that way lets you add covariates, and that is what [CUPED](../../03-experimentation-and-causality/notes/03-experimentation-at-scale.md) and every adjustment in [causal inference](../../03-experimentation-and-causality/notes/04-correlation-and-causation.md) do. Here is the map of the chapter, in the form of the decision you make first.

```mermaid
flowchart TD
    A{Outcome?} -->|Continuous| B[OLS]
    A -->|Yes or no| C[Logistic: log-odds link]
    A -->|Count, exposure varies| D[Poisson with offset: log link]
    D --> E{Variance much larger than mean?}
    E -->|Yes| F[Negative binomial, or robust SEs]
    B --> G[Diagnostics: residuals, leverage, collinearity]
    C --> G
    F --> G
    G --> H{Rows from one user repeat?}
    H -->|Yes| I[Cluster the standard errors]
```

## OLS in `statsmodels`

Ordinary least squares picks the coefficients that minimise the sum of squared residuals (*An Introduction to Statistical Learning*, §3.1-3.2; Bruce & Bruce, 2017, ch. 4). Here is a Larkspur experiment: spend in the month after a new checkout was randomised, alongside pre-period spend and device. The true effect is 1.5.

```python
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm

rng = np.random.default_rng(42)
n = 20_000
pre = rng.gamma(2.0, 15.0, n)                    # spend in the 30 days before
new_checkout = rng.integers(0, 2, n)
device = rng.choice(["mobile", "desktop", "tablet"], n, p=[.62, .31, .07])
noise = rng.normal(0, 8 + 0.35 * pre)            # louder for heavy spenders
spend = 6 + 1.5 * new_checkout + 0.6 * pre + 3.0 * (device == "desktop") + noise
df = pd.DataFrame(dict(spend=spend, new_checkout=new_checkout, pre=pre, device=device))
print(df.head(3).round(2).to_string())
```

```text
   spend  new_checkout    pre  device
0  37.16             0  31.38  mobile
1  48.40             0  42.53  mobile
2  19.03             0  27.56  mobile
```

### The t-test is a regression

```python
from scipy import stats

m0 = smf.ols("spend ~ new_checkout", df).fit()
a, b = df.spend[df.new_checkout == 0], df.spend[df.new_checkout == 1]
t = stats.ttest_ind(b, a)
print(f"difference in means {b.mean() - a.mean():.3f}   t-test t={t.statistic:.3f} p={t.pvalue:.4f}")
print(f"OLS coefficient     {m0.params['new_checkout']:.3f}   OLS    t={m0.tvalues['new_checkout']:.3f} p={m0.pvalues['new_checkout']:.4f}")
```

```text
difference in means 1.350   t-test t=3.942 p=0.0001
OLS coefficient     1.350   OLS    t=3.942 p=0.0001
```

The coefficient on a 0/1 variable is the difference in group means, and its t-statistic is the pooled t-test's. Nothing here is a coincidence. The one-way ANOVA in chapter 5 matched `smf.ols` exactly for the same reason.

### Reading the summary

```python
m1 = smf.ols("spend ~ new_checkout + pre + C(device)", df).fit()
print(m1.summary(slim=True))
```

```text
                            OLS Regression Results
==============================================================================
Dep. Variable:                  spend   R-squared:                       0.299
Model:                            OLS   Adj. R-squared:                  0.299
No. Observations:               20000   F-statistic:                     2137.
Covariance Type:            nonrobust   Prob (F-statistic):               0.00
=======================================================================================
                          coef    std err          t      P>|t|      [0.025      0.975]
---------------------------------------------------------------------------------------
Intercept               8.5986      0.357     24.055      0.000       7.898       9.299
C(device)[T.mobile]    -2.9948      0.315     -9.519      0.000      -3.611      -2.378
C(device)[T.tablet]    -3.1347      0.602     -5.211      0.000      -4.314      -1.956
new_checkout            1.4392      0.287      5.017      0.000       0.877       2.002
pre                     0.6118      0.007     91.701      0.000       0.599       0.625
=======================================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
```

Read it from the left. Each `coef` is a *conditional* difference: `new_checkout` at 1.44 means, comparing users with the same pre-period spend and device, the new checkout's group spends 1.44 more. `Intercept` is the prediction when all regressors are zero: a desktop user (the baseline level of the dummy coding) with no prior spend, on the old checkout. `C(device)[T.mobile]` at −2.99 is mobile compared with desktop, and it is *not* a statement about mobile in general. `pre` at 0.61 says one extra unit of spend before goes with 0.61 more after.

`std err` is the coefficient's sampling standard deviation, and `t` is the ratio of the two. `[0.025, 0.975]` is the 95% confidence interval, which is what you should report. R² at 0.30 tells you the share of variance explained. It is low, and that is fine for inference. Whether the effect estimate is unbiased depends on the randomisation and has nothing to do with R².

A prediction needs a different interval. The confidence interval covers the average outcome for everyone with those inputs, and the prediction interval covers one new person, adding the irreducible error. The book's advertising fit gives a 95% confidence interval of 10,985 to 11,528 around 11,256 units of sales and a prediction interval of 7,930 to 14,580 around the same centre (*ISLP*, ch. 3). Report the first for an effect or an average, the second for a single user's spend.

### Why add pre-period covariates

```python
for name, m in [("no covariate", m0), ("with pre-period", m1)]:
    print(f"{name:<16} effect {m.params['new_checkout']:.3f}  SE {m.bse['new_checkout']:.3f}  R2 {m.rsquared:.3f}")
print(f"variance removed: {1 - (m1.bse['new_checkout'] / m0.bse['new_checkout'])**2:.0%}")
```

```text
no covariate     effect 1.350  SE 0.343  R2 0.001
with pre-period  effect 1.439  SE 0.287  R2 0.299
variance removed: 30%
```

Randomisation guarantees the effect estimate is unbiased either way. What the covariate buys is precision: pre-period spend explains 30% of the outcome variance, so that share of the noise vanishes from the error term, and the standard error falls from 0.343 to 0.287. The relation is direct: variance removed is about the R² gained. That equals running the experiment with about 30% fewer users for the same precision, and it is exactly what [CUPED](../../03-experimentation-and-causality/notes/03-experimentation-at-scale.md) does. Only adjust for variables measured *before* assignment. A post-treatment covariate can absorb the treatment effect, or manufacture one.

### Conditional differences only help if you measured the cause

Outside randomised data, the coefficient is causal only if you have adjusted for what matters.

```python
rng2 = np.random.default_rng(1)
loyal = rng2.normal(0, 1, n)
email = (loyal + rng2.normal(0, 1, n) > 0).astype(int)     # loyal users open the email
y = 10 + 0.0 * email + 5 * loyal + rng2.normal(0, 3, n)
d2 = pd.DataFrame(dict(y=y, email=email, loyal=loyal))
print(f"y ~ email          coef {smf.ols('y ~ email', d2).fit().params['email']:.2f}")
print(f"y ~ email + loyal  coef {smf.ols('y ~ email + loyal', d2).fit().params['email']:.2f}   (truth 0)")
```

```text
y ~ email          coef 5.69
y ~ email + loyal  coef 0.08   (truth 0)
```

Here the email has no effect, but loyal users are the ones who open it, so a regression without loyalty finds 5.69. Add loyalty and the coefficient falls to about zero. In observational work you rarely have the `loyal` column. [Correlation and causation](../../03-experimentation-and-causality/notes/04-correlation-and-causation.md) picks up from here.

### Interactions

Interactions ask if an effect differs across groups. `new_checkout * C(device)` fits a separate effect per device.

```python
m2 = smf.ols("spend ~ new_checkout * C(device) + pre", df).fit()
print(m2.params.filter(like="new_checkout").round(3).to_string())
print(f"joint p for the interactions: {m2.f_test('new_checkout:C(device)[T.mobile] = 0, new_checkout:C(device)[T.tablet] = 0').pvalue:.3f}")
```

```text
new_checkout                        0.873
new_checkout:C(device)[T.mobile]    0.793
new_checkout:C(device)[T.tablet]    1.108
joint p for the interactions: 0.396
```

The effect on desktop (the baseline) is 0.87, on mobile 0.87 + 0.79 and on tablet 0.87 + 1.11. They look different, yet the joint test gives p = 0.40, so the data do not distinguish them. Test the interaction, as opposed to noticing that one segment is significant and another is not. The same book shows an interaction that is large: price per extra square foot is $177 in the cheapest zip-code group and $447 in the dearest, a factor of almost 2.7, and the dearest group alone adds almost $340,000 as a main effect (*Practical Statistics*, ch. 4). Interaction estimates also have larger standard errors than main effects, so experiments rarely have the power to detect them.

The simple-regression algebra behind this table is short, and *Think Stats* gives it in one place (ch. 9). With one predictor the least-squares slope is β = Cov(X, Y) / Var(X) and the intercept is α = ȳ − β·x̄. R² equals ρ², the square of Pearson's correlation, and it is 1 − Var(residual) / Var(Y): the share of the mean squared error removed compared with always guessing ȳ. So R² = 0.64 means the model cuts squared prediction error by 64%, a more careful wording than "explains 64% of the variability". The book notes least squares is the maximum likelihood fit when residuals are independent of x, normal, mean zero and of constant variance, and argues that computational convenience is no longer a reason to prefer squared loss over a cost function that matches the problem.

## Diagnostics

Regression's assumptions, in the order they usually matter for an analyst: the sample represents what you claim; errors are independent; the relationship is additive and linear in what you modelled; error variance is constant; errors are Normal (rarely important with large n). ISLP §3.3.3 lists the practical problems as non-linearity, correlated errors, non-constant variance, outliers, high-leverage points and collinearity. The next few sections work through the ones that bite.

### Residuals and heteroskedasticity

A residual plot shows residuals against fitted values. You want a shapeless band. A funnel means the noise grows with the prediction, which is *heteroskedasticity*, and it is the rule for money. Spend residuals in Larkspur's data get louder as predicted spend increases.

```text
residual
   ^                      :
   |                  : . : .
   |            . : . : . : :
   |  . . : . : : : : : : : :     funnel: spread grows with fitted value
   |            ' : ' : ' : :
   |                  : ' : '
   |                      :
   +-----------------------------> fitted
```

```python
resid, fitted = m1.resid, m1.fittedvalues
q = pd.qcut(fitted, 5, labels=False)
print("residual sd by fitted quintile:", resid.groupby(q).std().round(1).tolist())
bp = sm.stats.diagnostic.het_breuschpagan(resid, m1.model.exog)
print(f"Breusch-Pagan p = {bp[1]:.1e}")
```

```text
residual sd by fitted quintile: [11.0, 13.9, 16.8, 21.1, 31.8]
Breusch-Pagan p = 0.0e+00
```

The p-value underflows to zero because n is large and the funnel is plain. The sd by quintile, 11 rising to 32, is the more useful reading. The coefficients are still unbiased under heteroskedasticity. It is the standard errors that go wrong, since the textbook formula assumes one variance for everyone.

### Robust standard errors

Robust (Huber-White, or HC) standard errors estimate the variance without that assumption. In `statsmodels` you ask for `cov_type="HC3"`.

```python
hc = smf.ols("spend ~ new_checkout + pre + C(device)", df).fit(cov_type="HC3")
print(f"pre coefficient {m1.params['pre']:.3f}  classical SE {m1.bse['pre']:.4f}  HC3 SE {hc.bse['pre']:.4f}")
print(f"new_checkout    {m1.params['new_checkout']:.3f}  classical SE {m1.bse['new_checkout']:.4f}  HC3 SE {hc.bse['new_checkout']:.4f}")
```

```text
pre coefficient 0.612  classical SE 0.0067  HC3 SE 0.0112
new_checkout    1.439  classical SE 0.2869  HC3 SE 0.2871
```

The coefficient does not change at all, and that is the point: only the uncertainty does. For `pre`, whose values line up with the noise, the classical SE is 40% too small. For the randomised `new_checkout`, which is unrelated to who is noisy, the two agree. Robust SEs cost little, so with large samples and skewed outcomes, report them by default.

### Leverage and influence

A point matters when it is both far out in x (high *leverage*) and off the line (large residual). Cook's distance combines the two into an estimate of how much the fit changes if the point is removed.

```python
rng3 = np.random.default_rng(2)
x = rng3.normal(0, 1, 200); y3 = 2 * x + rng3.normal(0, 1, 200)
x_bad, y_bad = np.r_[x, 15.0], np.r_[y3, -30.0]
fit_good = sm.OLS(y3, sm.add_constant(x)).fit()
fit_bad = sm.OLS(y_bad, sm.add_constant(x_bad)).fit()
infl = fit_bad.get_influence()
print(f"slope without point {fit_good.params[1]:.2f}, with one high-leverage point {fit_bad.params[1]:.2f}")
print(f"leverage of that point {infl.hat_matrix_diag[-1]:.2f} (average {2 / 201:.3f}), "
      f"Cook's D {infl.cooks_distance[0][-1]:.1f}")
```

```text
slope without point 2.02, with one high-leverage point -0.18
leverage of that point 0.55 (average 0.010), Cook's D 107.0
```

One row of 201 changed a slope of 2.02 to −0.18. It has 55 times the average leverage, and the average is always (p + 1)/n for p predictors (*ISLP*, ch. 3). The same chapter flags studentized residuals beyond 3 in absolute value as outliers, and its worst case is a point that is both: high leverage with a large residual. The book's version is a house regression where the largest standardized residual (-4.33) is a partial-interest sale priced $757,753 off, and dropping the influential rows moves the Bathrooms coefficient from 2,282 to -16,132 (*Practical Statistics*, ch. 4). Extrapolation fails quietly too: the same fit prices a 5,000 sq ft empty lot at -$522,202 because every training row has a building. Always look at the top few rows by Cook's distance, and go back to the question from chapter 1: what is this row? Then decide.

### Multicollinearity

When predictors move together, the model cannot tell them apart.

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor as vif

rng4 = np.random.default_rng(3)
x1 = rng4.normal(0, 1, 500)
x2 = x1 + rng4.normal(0, 0.05, 500)
y4 = 1 + x1 + x2 + rng4.normal(0, 1, 500)
X = sm.add_constant(np.c_[x1, x2])
fit = sm.OLS(y4, X).fit()
solo = sm.OLS(y4, sm.add_constant(x1)).fit()
print(f"VIF {vif(X, 1):.0f}")
print(f"both in: coefs {fit.params[1:].round(2)}, SEs {fit.bse[1:].round(2)}")
print(f"x1 alone: coef {solo.params[1]:.2f}, SE {solo.bse[1]:.3f}")
print(f"prediction RMSE both {np.sqrt(fit.mse_resid):.3f}, x1 alone {np.sqrt(solo.mse_resid):.3f}")
```

```text
VIF 391
both in: coefs [1.51 0.54], SEs [0.81 0.82]
x1 alone: coef 2.05, SE 0.041
prediction RMSE both 0.920, x1 alone 0.920
```

The variance inflation factor (VIF) is how much a coefficient's variance is inflated by correlation with the other predictors: 1 / (1 − R²ⱼ), where R²ⱼ comes from regressing predictor *j* on all the others. Here that is 391, so R²ⱼ is 0.997. The rule of thumb is that 5 or 10 is a problem (*ISLP*, ch. 3). The two coefficients sum to the right total but their split is arbitrary: their standard errors are 20 times larger than the solo fit's. The predictions, however, are just as good. So collinearity is a problem for *explanation* and mostly not for prediction. It biases nothing, but it inflates the SEs. In the book's King County house-price model (R² = 0.5407, in-sample), the bedroom coefficient is negative once square feet and bathrooms are in, because bedrooms and size move together; take size out and it flips to +$27,657 (*Practical Statistics*, ch. 4). Drop or combine predictors if you need to interpret them. In the book's Credit data, credit limit and rating have VIFs of 160.67 and 160.59, and the limit coefficient's standard error grows 12-fold once rating is in. Dropping rating takes R² from 0.754 to 0.75 and the VIFs close to 1. In the right-hand panel below, the least-squares fit sits at the end of a long thin valley of near-equal fits, so a small change in the data moves the pair along it.

![Contour plots of the residual sum of squares: a closed ellipse for limit and age, a long narrow valley for limit and rating](../../sources/images/islp-ch03-linear-regression-fig3-15.png)

*Image Source: James et al., *An Introduction to Statistical Learning with Applications in Python* (Springer, 2023), Fig. 3.15. Credit data, balance regressions.* For a randomised treatment, collinearity with covariates is not a concern, because assignment is independent of them by construction.

### Clustered standard errors

Rows from the same user are correlated, as you saw in [chapter 2](02-probability-foundations.md). ISLP §3.3.3 gives the extreme version: double your data by duplicating every row and the intervals narrow by √2, despite no new information. In this example, treatment is assigned per user, with 6 sessions each, and the true effect is zero.

```python
rng5 = np.random.default_rng(4)
users = 800
per_user = 6
uid = np.repeat(np.arange(users), per_user)
treat_u = rng5.integers(0, 2, users)
y5 = 1.0 + 0.0 * treat_u[uid] + rng5.normal(0, 1, users)[uid] + rng5.normal(0, 1, users * per_user)
d5 = pd.DataFrame(dict(y=y5, treat=treat_u[uid], uid=uid))
naive = smf.ols("y ~ treat", d5).fit()
clus = smf.ols("y ~ treat", d5).fit(cov_type="cluster", cov_kwds={"groups": d5.uid})
print(f"coef {naive.params['treat']:.3f}, naive SE {naive.bse['treat']:.4f}, clustered SE {clus.bse['treat']:.4f}")
```

```text
coef 0.033, naive SE 0.0411, clustered SE 0.0781
```

```python
def fp(reps=400):
    r = np.random.default_rng(5); naive = clustered = 0
    for _ in range(reps):
        tu = r.integers(0, 2, users)
        yy = r.normal(0, 1, users)[uid] + r.normal(0, 1, users * per_user)
        d = pd.DataFrame(dict(y=yy, treat=tu[uid], uid=uid))
        f = sm.OLS(d.y, sm.add_constant(d.treat)).fit()
        naive += f.pvalues["treat"] < .05
        clustered += f.get_robustcov_results("cluster", groups=d.uid).pvalues[1] < .05
    return naive / reps, clustered / reps

print("false positive rate at nominal .05 (naive, clustered): %.3f, %.3f" % fp())
```

```text
false positive rate at nominal .05 (naive, clustered): 0.278, 0.035
```

The naive analysis calls a null experiment significant more than a quarter of the time at a nominal 5%. Clustering on the user brings it back to about the nominal rate. Reinhart's pseudoreplication chapter is this exact problem (*Statistics Done Wrong*, ch. 3). The rule: cluster at the level of randomisation. An experiment randomised by user and analysed by session must cluster on user. Randomised by city, cluster on city, and note that with few cities even this is not enough. [Cameron and Miller (J. Human Resources, 2015)](https://doi.org/10.3368/jhr.50.2.317), read in the authors' draft, show how far off it gets: in simulations they report, a nominal 5% test using clustered errors and the usual 1.96 rejected about 21% of the time with five clusters, and they give no clear cut-off for "few", which may range from under 20 to under 50 when clusters are balanced.

Clustered errors treat the groups as a nuisance: the coefficient stays where it was, and only its standard error changes. If the group effect may be correlated with the predictor, you need [fixed effects](08-panel-data-and-fixed-effects.md). If the group-level estimates are themselves the question, you need a multilevel model. The [decision table in the multilevel chapter](../../04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling.md#which-tool-the-decision-table) sets the three side by side.

## Logistic regression and Poisson models

Binary outcomes and counts are in [6b — Logistic regression and Poisson GLMs](06b-logistic-regression-and-poisson-glms.md): the log-odds link, odds ratios against marginal effects, separation, the link-function table, the offset for exposure, deviance and overdispersion. The map above shows where they sit: the same linear predictor, with a different outcome distribution and link.

## Choosing variables without fooling yourself

Two habits turn regression into a false-positive machine. The first is splitting a continuous predictor into high and low. Reinhart reports that picking the cutoff with the smallest p-value raises the false-positive rate by up to a factor of 10, and that dichotomising costs about as much power as discarding a third of the data (*Statistics Done Wrong*, ch. 7, as reported; early-1990s breast-cancer studies that used 'optimal' cutoffs, none of which survived multiplicity correction). The bigger harm is confounding. Here `x2` is correlated with a true cause `x1` and has no effect of its own:

```python
rng = np.random.default_rng(21)
hits_split = hits_cont = 0
for _ in range(1000):
    x1 = rng.normal(size=200)
    x2 = x1 + rng.normal(scale=0.6, size=200)
    y = x1 + rng.normal(size=200)
    d = pd.DataFrame({"y": y, "x1": x1, "x2": x2})
    d["h1"], d["h2"] = (d.x1 > d.x1.median()).astype(int), (d.x2 > d.x2.median()).astype(int)
    hits_split += smf.ols("y ~ h1 + h2", d).fit().pvalues["h2"] < .05
    hits_cont += smf.ols("y ~ x1 + x2", d).fit().pvalues["x2"] < .05
print(f"flagged at p<.05: median split {hits_split / 1000:.2f}, continuous {hits_cont / 1000:.2f}")
```

```text
flagged at p<.05: median split 0.75, continuous 0.04
```

Splitting at the median leaves the high half of `x1` mixed into both halves of `x2`, so `x2` soaks up the residual signal; the continuous model controls `x1` properly and holds the nominal 5%. The second habit is automatic variable selection. Reinhart's watermelon example: a cited study with 43 melons and 1,600 acoustic predictors claimed 99.9% of ripeness variance, and his own stepwise regression on pure noise reproduced 99.9% (ch. 8). The mechanism is visible with a few lines: keep the five of 1,600 noise predictors most correlated with `y` in 43 rows.

```python
n, k = 43, 1600
X, y = rng.normal(size=(n, k)), rng.normal(size=n)
Xt, yt = rng.normal(size=(n, k)), rng.normal(size=n)
top = np.argsort(-np.abs([np.corrcoef(X[:, j], y)[0, 1] for j in range(k)]))[:5]
beta = np.linalg.lstsq(np.c_[np.ones(n), X[:, top]], y, rcond=None)[0]
def r2(A, b):
    p = np.c_[np.ones(len(b)), A[:, top]] @ beta
    return 1 - ((b - p) ** 2).sum() / ((b - b.mean()) ** 2).sum()
print(f"in-sample R2 {r2(X, y):.2f}, fresh-data R2 {r2(Xt, yt):.2f}")
```

```text
in-sample R2 0.55, fresh-data R2 -0.50
```

An in-sample R² of 0.55 on pure noise, and worse than predicting the mean on fresh data. Reinhart's rules: evaluate on separate data or by cross-validation, prefer the lasso or no selection to stepwise, remember that a non-significant variable is not a zero effect, and note that a coefficient is not an intervention (nobody gains a pound 'holding everything else fixed'). The other trap in observational regressions is Simpson's paradox, with real numbers in [correlation and causation](../../03-experimentation-and-causality/notes/04-correlation-and-causation.md#simpsons-paradox).

Efron and Hastie give the advice to prefer the lasso to stepwise a measured form on the spam data (4,601 emails; 3,065 for training, 1,536 for test). With 3,061 candidate predictors including pairwise interactions, the lasso logistic regression reaches a test error of 0.057, stepwise logistic 0.064, and the lasso on main effects only 0.071. Stepwise fitting stalled at 134 variables on convergence problems, where the lasso's active set grew to 682 (*Computer Age*, ch. 16). On main effects alone, stepwise logistic matches the lasso with about half as many terms, so stepwise is not hopeless as a screen; its weakness is that nothing makes the greedy path optimal and that it charges more degrees of freedom than it appears to for searching. The same chapter's HIV example, where the lasso picks 7 of 30 mutation sites, shows the inference problem: naive intervals make three sites significant, and selection-adjusted ones leave one (*Computer Age*, ch. 16). Two further links to the models in this chapter. A neural network without its hidden nonlinearity is a GLM, and dropout on a linear model is a generalised ridge that equals ridge when the variables are standardised (*Computer Age*, ch. 18). Boosting and random forests are the usual benchmark for a GLM: if a forest does much better than your parametric model, "you probably have some work to do, by including some important interactions and the like" (*Computer Age*, ch. 17). On the spam data one pruned tree gets 9.3% test error against the lasso's 7.1%, so the benchmark is a tree ensemble and not a single tree.

---

## Prediction vs explanation

This chapter judged every model by its coefficients and their standard errors. [Data science](../../../data-science/01-classical-ml/README.md) judges models by error on data they have not seen, and that can lead to opposite conclusions.

```python
idx = np.arange(n) < n // 2
tr, te = df[idx], df[~idx]
for f in ["spend ~ new_checkout", "spend ~ pre + C(device)"]:
    fit = smf.ols(f, tr).fit()
    print(f"{f:<26} held-out RMSE {np.sqrt(((te.spend - fit.predict(te))**2).mean()):.2f}")
```

```text
spend ~ new_checkout       held-out RMSE 24.17
spend ~ pre + C(device)    held-out RMSE 20.16
```

The first model is the *right* one for the question "did the checkout work?", and it predicts poorly. The second has no checkout term and predicts better. A model with low R² can estimate an effect precisely, and a model with excellent held-out error can have uninterpretable coefficients, as in the collinearity example. Decide which question you are answering, and judge by the matching test.

---

## Pitfalls

- **Reading a coefficient as causal.** It is a conditional association unless randomisation or a defensible design says otherwise. The email example made 5.69 out of nothing.
- **Adjusting for post-treatment variables.** They can absorb the effect or create a false one. Use variables measured before assignment.
- **Using the wrong unit of analysis.** Sessions within users without clustering gave a 28% false-positive rate at a nominal 5%.
- **Judging an explanatory model by R².** A low R² does not bias a randomised effect. Equally, a high R² does not make a coefficient causal.
- **Dropping a collinear predictor without thinking.** Doing so can change what the remaining coefficient means, because it now absorbs part of what you removed.

---

## Try it

1. In the `gen` data, regress `spend` on `new_checkout` with `C(device)` only. How much does the standard error shrink, compared with using `pre`? Why the difference?
2. In the `cluster_fp` block, set `per_user = 20`, and predict what happens to the two false-positive rates before you run it.

<details>
<summary>Answers</summary>

1. `smf.ols("spend ~ new_checkout + C(device)", df).fit().bse["new_checkout"]` is about 0.342, barely below the unadjusted 0.343, against 0.287 with `pre`. Device explains about 0.5% of the outcome variance, so adjusting for it removes almost nothing. A covariate helps only in proportion to what it explains.
2. The naive rate climbs, to about 0.54 in a 200-repeat run, because the formula sees 16,000 rows with only 800 independent users. The clustered rate stays near the nominal level, about 0.055 in the same run. More rows per user make the naive analysis more wrong.

</details>

---

## Interview checklist

| Prompt | Answer |
|---|---|
| Why add pre-period covariates to an A/B regression? | They do not change the expected effect under randomisation. They explain outcome variance, so the standard error shrinks and power rises. |
| When do you need robust or clustered SEs? | Robust when variance is non-constant, typical of money. Clustered when rows repeat within a unit or the randomisation unit is coarser than the row. |
| Show that a t-test is a regression. | Regress the outcome on a 0/1 group. The coefficient is the difference in means, and its t matches the pooled t-test. |
| What does multicollinearity do? | Inflates coefficient SEs and makes individual coefficients unstable. It does not bias them and rarely hurts prediction. |

---

## Next

[6b — Logistic regression and Poisson GLMs](06b-logistic-regression-and-poisson-glms.md): the same machinery for a yes/no outcome, a count with exposure and an ordered rating, with deviance and overdispersion. [Chapter 7](07-data-generating-process.md) then steps back from fitting to ask what a model is a claim about.
