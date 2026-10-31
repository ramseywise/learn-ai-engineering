---
origin: own coursework
sources:
  - ../practice/5_Statistical_Analysis.ipynb
  - ../sources/Practical_Statistics_for_Data_Scientist.pdf
  - https://www.pywhy.org/dowhy/
  - https://mixtape.scunning.com/
confidence: medium
cleaned: 2026-10-31
---
# 8 — Correlation, Confounding and Causation

> Pearson vs Spearman, how a confounder manufactures correlation, how Simpson's paradox flips a result, partial correlation as the simplest control, and the quasi-experimental methods (DiD, IV, RD) you reach for when you cannot run an A/B test.

---

## Measuring association

| Coefficient | Measures | Sensitive to outliers | Use when |
|---|---|---|---|
| Pearson r | linear association | very | both variables roughly Normal, relationship linear |
| Spearman ρ | monotonic association (Pearson on ranks) | no | ordinal data, skew, outliers, curved but monotonic |
| Kendall τ | concordant vs discordant pairs | no | small samples, many ties |
| Point-biserial | one binary, one continuous | | equivalent to a t-test |
| Cramér's V | two categorical | | derived from chi-square (note 04) |

```python
# practice/5_Statistical_Analysis.ipynb, Part 4: one outlier
x = np.linspace(1, 10, 30)
y_clean = x + np.random.normal(0, 0.5, 30)
y_outlier = y_clean.copy(); y_outlier[-1] = 50

stats.pearsonr(x, y_clean)     # r near 0.99
stats.pearsonr(x, y_outlier)   # r drops sharply: one point moved it
stats.spearmanr(x, y_outlier)  # rho barely moves: the outlier is still the largest rank
```

Always plot before you correlate. Anscombe's quartet is four datasets with the same r = 0.82 and completely different shapes.

`sns.heatmap(df.corr(), annot=True, center=0)` is the fastest EDA view of a feature table. In the notebook's synthetic table, age drives income and income drives spend, so age and spend correlate even though neither touches the other directly. That chain is the start of the confounding story.

---

## Confounding

> A confounder Z causes both X and Y. X and Y then correlate even if neither causes the other.

```
      temperature
       /       \
      v         v
 ice cream    drownings
```

```python
# practice/5_Statistical_Analysis.ipynb
temperature = np.random.normal(20, 8, 365)
ice_cream = 100 + 3 * temperature + np.random.normal(0, 10, 365)
drownings = 2 + 0.1 * temperature + np.random.normal(0, 1, 365)

stats.pearsonr(ice_cream, drownings)     # strong, "significant", meaningless
```

### Partial correlation

Control for Z by regressing it out of both variables and correlating what is left.

```python
def residuals(y, x):
    slope, intercept, *_ = stats.linregress(x, y)
    return y - (slope * x + intercept)

stats.pearsonr(residuals(ice_cream, temperature),
               residuals(drownings, temperature))   # near zero
```

Multiple regression does the same thing in one step: the coefficient on X in `y ~ x + z` is the effect of X holding Z fixed. Both only remove confounders you measured. An unmeasured confounder is untouched, which is why randomisation (note 06) is the gold standard: it breaks the arrow from every confounder into treatment, measured or not.

### Bad controls

Controlling for the wrong variable creates bias rather than removing it.

| Variable type | Path | Control for it? |
|---|---|---|
| Confounder | Z → X, Z → Y | yes |
| Mediator | X → M → Y | no, if you want the total effect of X |
| Collider | X → C ← Y | **no**: conditioning on it creates a spurious X–Y link |

Collider example: among people admitted to a selective programme, test scores and interview scores look negatively correlated, because admission required a high sum of the two. Selecting on the outcome is conditioning on a collider.

---

## Simpson's paradox

> A trend in aggregated data reverses within every subgroup, because the subgroups have different sizes and different baselines.

The notebook's synthetic example: treatment looks worse overall but is better for both mild and severe patients, because treatment was given mostly to severe cases.

| | Control | Treatment |
|---|---|---|
| Mild | 90 / 100 = 90.0% | 39 / 40 = 97.5% |
| Severe | 30 / 100 = 30.0% | 80 / 160 = 50.0% |
| **Overall** | 120 / 200 = **60.0%** | 119 / 200 = **59.5%** |

```python
data.groupby("treatment")["recovered"].mean()                        # misleading
data.groupby(["treatment", "subgroup"])["recovered"].mean().unstack()  # true picture
```

Which table is right depends on the causal story, not the arithmetic. Here severity affects both who got treated and who recovered, so it is a confounder and you stratify. The classic real case is UC Berkeley 1973 admissions: women were admitted less often overall, but at equal or higher rates within most departments, because they applied more to competitive departments.

In A/B tests Simpson's paradox appears when the traffic mix shifts during the test (for example a marketing push that sends a different segment to one arm on one day). Check arm balance by segment and by day.

---

## When you cannot randomise

These are the causal-inference methods this repo has no notebook for yet. The table is the map; Cunningham's *Causal Inference: The Mixtape* (free online) and the `dowhy` docs are the next step.

| Method | Idea | Key assumption | Analytics example |
|---|---|---|---|
| **Difference-in-differences (DiD)** | compare the before/after change in a treated group with the change in an untreated group | parallel trends: without treatment both groups would have moved together | a feature launched in one country but not another |
| **Instrumental variables (IV)** | find Z that moves X but affects Y only through X | exclusion restriction (untestable) | distance to a store as an instrument for store visits |
| **Regression discontinuity (RD)** | units just above and just below a cutoff are comparable | no manipulation of the running variable at the cutoff | a loyalty tier at 1,000 points; a credit score threshold |
| **Propensity score matching / weighting** | model P(treated given X), compare treated and untreated with similar scores | no unmeasured confounders | users who opted into a feature |
| **Synthetic control** | build a weighted combination of untreated units that tracks the treated one before treatment | the pre-period fit carries forward | one city gets a policy change |

```python
# minimal DiD as a regression: the interaction coefficient is the effect
import statsmodels.formula.api as smf
# df columns: y, treated (0/1 group), post (0/1 period)
smf.ols("y ~ treated * post", data=df).fit().params["treated:post"]

# dowhy: state the graph, then identify and estimate
# import dowhy
# model = dowhy.CausalModel(data=df, treatment="x", outcome="y", common_causes=["z"])
# estimand = model.identify_effect()
# model.estimate_effect(estimand, method_name="backdoor.propensity_score_matching")
```

### Choosing

| Situation | First choice |
|---|---|
| You control assignment | A/B test (note 06) |
| A rollout hit some units and not others, with pre-period data | DiD; plot the pre-trends |
| Treatment assigned by a threshold | RD |
| Self-selected treatment, rich covariates | propensity weighting, plus a sensitivity analysis |
| One treated unit, many controls | synthetic control |

---

## Regression as the bridge

Regression is where this note hands off to data-science. A coefficient is a conditional association: the change in Y per unit of X *holding the other regressors fixed*. It becomes a causal effect only with one of the designs above, or when X was randomised. BMH ch. 6 (note 11) shows that ridge and lasso are Bayesian regression with Normal and Laplace priors, which is the bridge from this note to the Bayesian track.

---

→ Next: [09-bayesian-inference.md](09-bayesian-inference.md) — the other way to answer "what do the data say": probability as belief, priors and posteriors, and the first PyMC models.
