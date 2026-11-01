---
origin: synthesis
sources:
  - https://avehtari.github.io/ROS-Examples/ (Gelman, Hill & Vehtari, Regression and Other Stories, free PDF; not yet held)
  - ../sources/An-Introduction-to-Statistical-Learning-with-Applications-in-Python.pdf (ch. 3–4)
  - ../sources/Practical_Statistics_for_Data_Scientist.pdf (ch. 4, Regression and Prediction)
confidence: low
cleaned: 2026-10-31
---
# 5 — Regression and GLMs

> Regression as the analyst uses it: fitting and reading an OLS model, checking its assumptions, and the two GLMs that cover most product data, logistic for yes/no outcomes and Poisson for counts.

> **Status: skeleton (2026-10-31).** Section plan only. Fill with `/chapter` (ISLP ch. 3–4, Bruce & Bruce ch. 4, Gelman, Hill & Vehtari ch. 6–15) and `/papers analytics`.

---

## Why this note

A t-test (note 04) is a regression with one binary regressor. Seeing it that way lets you add covariates, which is what CUPED (note 07) and every adjustment in note 08 do. data-science treats regression as a predictor; this note treats it as an estimate with a standard error.

---

## OLS in `statsmodels`

- `smf.ols("y ~ treatment + x", df).fit().summary()`, read line by line.
- Coefficients as conditional differences; dummy coding; interactions.
- The t-test and ANOVA from note 04, reproduced as regressions.

## Diagnostics

- Residual plots, leverage and influence, heteroskedasticity; robust (HC) standard errors.
- Multicollinearity and why it inflates SEs without biasing coefficients.
- Clustered standard errors when users repeat (note 07).

## Logistic regression

- Log-odds, odds ratios, marginal effects; reading a coefficient as a percentage-point change.
- Separation and why the fit fails; regularisation as a fix (note 11 reads it as a prior).

## Poisson and other GLMs

- Link functions; Poisson for counts with an exposure offset; overdispersion and negative binomial.

## Prediction vs explanation

- Where this note stops and [data-science](../../data-science/README.md) starts: held-out error vs coefficient SEs.

---

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| Interpret a logistic coefficient of 0.4. | to be written |
| Why add pre-period covariates to an A/B regression? | to be written |
| When do you need robust or clustered SEs? | to be written |

---

→ Next: [06-ab-testing.md](06-ab-testing.md) — hypothesis testing applied to product experiments: power, sample size, the two-proportion z-test and peeking.
