---
origin: own coursework
sources:
  - ../practice/5_Statistical_Analysis.ipynb
  - ../practice/AB-Bayes/AB_Testing_with_Python.ipynb
  - https://www.kaggle.com/datasets/zhangluyuan/ab-testing (ab_data.csv, not included)
  - https://www.statsmodels.org/stable/stats.html#power-and-sample-size-calculations
  - ../sources/Alex_Reinhart-Statistics_Done_Wrong-EN.pdf
confidence: high
cleaned: 2026-10-31
---
# 3 — Frequentist A/B Testing

> An A/B test is a two-sample hypothesis test with a sample size fixed in advance. Size it with a power calculation, randomise cleanly, test once with a two-proportion z-test, and report the lift with a confidence interval.

---

## The pipeline

| Step | Decision | Failure if skipped |
|---|---|---|
| 1. Metric | one primary metric (conversion, revenue per user), plus guardrails | twenty metrics, one "wins" by chance (note 02) |
| 2. Minimum detectable effect (MDE) | the smallest lift worth shipping | test runs forever or is underpowered |
| 3. Sample size | power analysis from baseline, MDE, α, power | peeking, or stopping too early |
| 4. Randomisation unit | user, not session or pageview | the same user sees both arms |
| 5. Run to N | no decisions before N | inflated false-positive rate |
| 6. Test | two-proportion z (or Welch t for means) | |
| 7. Report | lift, 95% CI, p-value, sample ratio check | "significant" with no effect size |

---

## Sample size from first principles

For two proportions with equal group sizes, the per-group N is

```
n = ((z_{1-α/2} + z_{1-β}) / h)²
```

where h is a standardised effect size. The notebook uses the pooled-SD version:

```python
# practice/5_Statistical_Analysis.ipynb, Part 3
from scipy.stats import norm
p_control, p_treatment = 0.05, 0.06        # baseline 5%, detect +1 pp
alpha, power = 0.05, 0.80

p_pooled = (p_control + p_treatment) / 2
effect_size = abs(p_treatment - p_control) / np.sqrt(p_pooled * (1 - p_pooled))

z_alpha = norm.ppf(1 - alpha / 2)          # 1.96
z_beta  = norm.ppf(power)                  # 0.84
n = ((z_alpha + z_beta) / effect_size) ** 2
int(np.ceil(n))                            # 4080 per group
```

The `statsmodels` route uses Cohen's h (an arcsine transform), which is what the AB notebook does:

```python
# practice/AB-Bayes/AB_Testing_with_Python.ipynb
import statsmodels.stats.api as sms        # missing from the notebook: add this import
from math import ceil                      # also missing

effect_size = sms.proportion_effectsize(0.13, 0.15)   # baseline 13%, target 15%
required_n = sms.NormalIndPower().solve_power(
    effect_size, power=0.8, alpha=0.05, ratio=1)
required_n = ceil(required_n)              # about 2360 per group
```

### What moves N

| Change | Effect on N |
|---|---|
| halve the MDE | ×4 |
| power 0.8 → 0.9 | ×1.34 |
| α 0.05 → 0.01 | ×1.49 |
| baseline closer to 50% | larger (variance p(1−p) peaks at 0.5) for the same absolute lift |
| unequal split (ratio ≠ 1) | larger total N for the same power |

The square in the formula is the LLN error rate from note 01: precision costs data quadratically.

---

## Cleaning the assignment

The AB notebook's dataset (`ab_data.csv`, about 290k rows of `user_id`, `group`, `landing_page`, `converted`) has users who appear in both arms. Cross-tab before anything else.

```python
pd.crosstab(df["group"], df["landing_page"])   # off-diagonal cells = mis-assigned rows

# drop every user seen more than once
session_counts = df["user_id"].value_counts()
duplicates = session_counts[session_counts > 1].index
df = df[~df["user_id"].isin(duplicates)]

# sample the required N from each arm
control   = df[df.group == "control"].sample(n=required_n, random_state=1)
treatment = df[df.group == "treatment"].sample(n=required_n, random_state=1)
ab_test = pd.concat([control, treatment], ignore_index=True)
ab_test["group"].value_counts()               # should be exactly 50/50
```

**Sample ratio mismatch (SRM).** In a live test the split is never exactly 50/50, but it should be close. A chi-square goodness-of-fit test on the arm counts with p < 0.001 means the randomisation or logging is broken, and the result cannot be trusted whatever it says.

---

## Running the test

```python
# practice/5_Statistical_Analysis.ipynb, Part 3 (simulated) and the AB notebook (real data)
from statsmodels.stats.proportion import proportions_ztest, proportion_confint

successes = [control.converted.sum(), treatment.converted.sum()]
nobs      = [len(control), len(treatment)]

z_stat, p_value = proportions_ztest(successes, nobs)
(lo_c, lo_t), (hi_c, hi_t) = proportion_confint(successes, nobs, alpha=0.05)

# 95% CI for the difference (unpooled SE)
rate_a, rate_b = successes[0] / nobs[0], successes[1] / nobs[1]
se = np.sqrt(rate_a * (1 - rate_a) / nobs[0] + rate_b * (1 - rate_b) / nobs[1])
diff = rate_b - rate_a
ci = (diff - 1.96 * se, diff + 1.96 * se)
```

The AB notebook also runs `ttest_ind` on the 0/1 outcomes and a hand-computed chi-square on the 2×2 table. On large samples all three give the same answer; that agreement is a sanity check, not three independent pieces of evidence.

| Test on conversion data | When it is the right one |
|---|---|
| two-proportion z | the default for large N |
| chi-square on the 2×2 | identical to z (χ² = z²); generalises to more than two arms |
| Fisher's exact | small N, any expected count < 5 |
| Welch t on 0/1 outcomes | fine at large N; mostly useful when the metric is a mean, not a rate |

### Reporting

Report the lift and its CI before the p-value. "Treatment converts at 12.3% vs 12.0%, lift +0.3 pp, 95% CI [−0.4, +1.0] pp, p = 0.41" tells the reader both that the test is inconclusive and how large an effect is still plausible. "Not significant" alone does not.

---

## Peeking

> The p-value is valid only at the sample size you planned. Checking it repeatedly and stopping the first time it dips below 0.05 inflates the false-positive rate far above 5%.

```python
# practice/5_Statistical_Analysis.ipynb: both arms have the same true rate (H0 true)
np.random.seed(7)
a = np.random.binomial(1, 0.10, 500)
b = np.random.binomial(1, 0.10, 500)
pvs = [proportions_ztest([a[:i].sum(), b[:i].sum()], [i, i])[1]
       for i in range(20, 501, 10)]
sum(pv < 0.05 for pv in pvs)   # several crossings; stopping at the first is a false positive
```

| If you need to look early | Method |
|---|---|
| a few planned interim looks | group-sequential design with O'Brien-Fleming or Pocock boundaries |
| continuous monitoring | always-valid p-values / mSPRT (Optimizely, Eppo) |
| you want a probability, not a test | Bayesian A/B, note 08 (peeking is less damaging, not free) |
| you want to stop sending traffic to losers | a bandit, note 07 |

---

## Other pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Novelty / primacy effect | lift fades after week one | run at least one full business cycle; look at lift by days since exposure |
| Network effects | treatment users affect control users (marketplaces, social) | cluster randomisation by region or graph component |
| Multiple metrics | a secondary metric "wins" | one primary metric, correct the rest (note 02) |
| Segment fishing | "it worked on iOS" | pre-register segments; treat others as hypotheses for the next test |
| Simpson's paradox | arm mix differs across segments | stratify, note 04 |
| Variance too high | revenue tests never conclude | CUPED: regress out a pre-period covariate to cut variance |

---

→ Next: [04-correlation-and-causation.md](04-correlation-and-causation.md) — what to do when you cannot randomise: confounding, Simpson's paradox, partial correlation and the quasi-experimental toolkit.
