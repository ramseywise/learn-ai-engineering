---
origin: own coursework
sources:
  - ../practice/5_Statistical_Analysis.ipynb
  - ../practice/courses/wesleyan_inferential_statistics.py
  - ../practice/courses/umich_statistical_analysis.py
  - ../../sources/Alex_Reinhart-Statistics_Done_Wrong-EN.pdf
  - ../../sources/Practical_Statistics_for_Data_Scientist.pdf
  - https://docs.scipy.org/doc/scipy/reference/stats.html
confidence: high
cleaned: 2026-10-31
---
# 4 — Hypothesis Testing

> The null-hypothesis recipe, which test fits which data, what a p-value does and does not say, the non-parametric fallbacks, and why running twenty tests guarantees a false positive.

---

## The recipe

1. **H₀ (null):** the default. No effect, no difference, independence.
2. **H₁ (alternative):** the effect you want to detect. Decide one- or two-sided *before* looking.
3. **α:** the false-positive rate you accept, usually 0.05.
4. **Test statistic:** a number whose distribution under H₀ is known (t, χ², F, z).
5. **p-value:** the probability, *assuming H₀ is true*, of a statistic at least as extreme as the one observed.
6. **Decision:** reject H₀ if p < α. Otherwise "fail to reject", which is not "accept".

| Term | Plain meaning |
|---|---|
| Type I error (α) | false positive: you reject a true H₀ |
| Type II error (β) | false negative: you miss a real effect |
| Power (1 − β) | chance of detecting an effect of a given size; note 06 |
| Effect size | how big the difference is, independent of N (Cohen's d, h, lift) |

### What a p-value is not

Reinhart's *Statistics Done Wrong* lists these; each is a common interview trap.

| Wrong reading | Why it is wrong |
|---|---|
| "p = 0.03 means a 3% chance H₀ is true" | p assumes H₀ is true; it cannot be the probability of H₀. That needs a prior (note 09). |
| "p = 0.2 means there is no effect" | the test may simply be underpowered |
| "p = 0.0001 means a big effect" | with N in the millions, trivially small effects are significant; report the effect size and CI |
| "p < 0.05 in one study, p > 0.05 in another, so they disagree" | the difference between significant and not significant is not itself significant |

---

## Choosing the test

| Question | Data | Parametric test | `scipy.stats` | Non-parametric fallback |
|---|---|---|---|---|
| Is this mean different from a known value? | one continuous sample | one-sample t | `ttest_1samp(x, mu0)` | Wilcoxon signed-rank on x − mu0 |
| Do two independent groups differ? | two continuous samples | two-sample t (Welch) | `ttest_ind(a, b, equal_var=False)` | Mann-Whitney U `mannwhitneyu(a, b)` |
| Before vs after on the same units? | paired continuous | paired t | `ttest_rel(before, after)` | Wilcoxon `wilcoxon(before, after)` |
| Do 3+ groups differ? | k continuous samples | one-way ANOVA | `f_oneway(a, b, c)` | Kruskal-Wallis `kruskal(a, b, c)` |
| Are two categorical variables independent? | contingency table | chi-square | `chi2_contingency(table)` | Fisher's exact `fisher_exact(2x2)` when any expected count < 5 |
| Do two samples come from the same distribution? | two continuous samples | none | | Kolmogorov-Smirnov `ks_2samp(a, b)` |
| Do two proportions differ? | counts and totals | two-proportion z | `statsmodels proportions_ztest` | chi-square on the 2×2, or Fisher |

Default to Welch's t (`equal_var=False`). It loses almost nothing when variances are equal and protects you when they are not.

---

## The parametric tests in code

```python
# from practice/5_Statistical_Analysis.ipynb, Part 2

# one-sample t: is the average height 170 cm?
sample = np.random.normal(loc=173, scale=8, size=50)
t_stat, p_value = stats.ttest_1samp(sample, 170)

# two-sample t: does a new study method raise scores?
control   = np.random.normal(72, 10, 40)
treatment = np.random.normal(76, 10, 40)
t_stat, p_value = stats.ttest_ind(control, treatment)

# chi-square: does product preference depend on age group?
observed = np.array([[30, 20],    # under 30: prefer A, prefer B
                     [15, 35]])   # over 30
chi2, p_value, dof, expected = stats.chi2_contingency(observed)
# 'expected' is the table you would see under independence; compare it to 'observed'

# ANOVA: do three teaching methods differ?
f_stat, p_value = stats.f_oneway(method_a, method_b, method_c)
# a significant F says "some mean differs", not which one: follow with Tukey HSD
# from statsmodels.stats.multicomp import pairwise_tukeyhsd
```

The Wesleyan coursework script ([practice/courses/wesleyan_inferential_statistics.py](../practice/courses/wesleyan_inferential_statistics.py)) runs the same tests on the NESARC survey through the formula route, which is what you want when the groups live in a DataFrame column: `smf.ols` for the F-test, then Tukey HSD for the pairwise follow-up.

```python
# condensed from the Wesleyan script
import statsmodels.formula.api as smf
import statsmodels.stats.multicomp as multi
results = smf.ols("NUMCIGMO_EST ~ C(MAJORDEPLIFE)", data=sub2).fit()
print(results.summary())                         # F-statistic and its p-value
mc = multi.MultiComparison(sub2["NUMCIGMO_EST"], sub2["ETHRACE2A"])
print(mc.tukeyhsd().summary())                   # which pairs differ
```

---

## Non-parametric tests

Use them when the data are ordinal, heavily skewed, or have outliers you cannot justify removing. They test ranks rather than raw values, so one extreme point cannot dominate.

| Test | Tests | Assumes | Cost |
|---|---|---|---|
| Mann-Whitney U | whether one group tends to have larger values than the other | independent samples, similar shapes if you want to read it as a median test | slightly less power than t on Normal data (about 95% efficiency) |
| Wilcoxon signed-rank | whether paired differences are centred on zero | symmetric differences | same |
| Kruskal-Wallis | Mann-Whitney for 3+ groups | as above | follow with Dunn's test |
| Kolmogorov-Smirnov | whether two whole distributions differ (shape, spread, location) | continuous data | low power for differences only in the tails |

```python
# revenue per user: skewed, with a few whales
from scipy.stats import mannwhitneyu, ks_2samp, wilcoxon
u, p = mannwhitneyu(rev_a, rev_b, alternative="two-sided")
d, p = ks_2samp(rev_a, rev_b)
w, p = wilcoxon(before, after)
```

A bootstrap is the other general fallback: resample each group with replacement, recompute the difference, and read the 2.5th and 97.5th percentiles. It works for medians, ratios and anything else without a textbook test.

```python
diffs = [np.median(np.random.choice(b, len(b))) - np.median(np.random.choice(a, len(a)))
         for _ in range(10_000)]
np.percentile(diffs, [2.5, 97.5])
```

---

## Multiple comparisons

> At α = 0.05, twenty independent tests of true nulls produce at least one false positive with probability 1 − 0.95²⁰ ≈ 64%.

The notebook simulates exactly this: twenty t-tests on pairs of samples drawn from the *same* distribution.

```python
n_tests, alpha = 20, 0.05
p_values = [stats.ttest_ind(np.random.normal(0, 1, 30),
                            np.random.normal(0, 1, 30)).pvalue
            for _ in range(n_tests)]
uncorrected = sum(p < alpha for p in p_values)            # usually 1, sometimes 2-3
corrected   = sum(p < alpha / n_tests for p in p_values)  # Bonferroni: usually 0
```

| Correction | Controls | Rule | When |
|---|---|---|---|
| Bonferroni | family-wise error rate (any false positive) | reject if p < α/m | few tests, any false positive is costly |
| Holm | family-wise error rate | step-down Bonferroni; uniformly more powerful | always prefer over plain Bonferroni |
| Benjamini-Hochberg | false discovery rate (share of rejections that are false) | sort p, reject p₍ᵢ₎ ≤ (i/m)·α | many tests (metrics dashboards, genes, feature screens) |

```python
from statsmodels.stats.multitest import multipletests
reject, p_adj, _, _ = multipletests(p_values, alpha=0.05, method="holm")      # or "fdr_bh"
```

### Where multiplicity hides

- **Many metrics** on one A/B test. Pick one primary metric in advance; treat the rest as exploratory.
- **Many segments** ("it worked for Android users in Germany"). Each segment is a test. Also the small-N trap from note 02.
- **Many looks** at the same test over time. That is peeking, note 06.
- **Data dredging.** The Michigan coursework script ([practice/courses/umich_statistical_analysis.py](../practice/courses/umich_statistical_analysis.py), week 4) lists three remedies: Bonferroni, holding out data to confirm what you found, and pre-registering what you expect and why.
- **The garden of forking paths:** choices about outliers, transforms and subsets made after seeing the data. Reinhart's fix is to write the analysis plan first.

---

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| t-test vs z-test? | z when σ is known or N is large (proportions); t when σ is estimated from a small sample |
| Why Welch? | does not assume equal variances, costs almost nothing |
| Chi-square vs Fisher? | Fisher when any expected cell count is below 5 |
| Data are skewed with outliers? | Mann-Whitney, or bootstrap the statistic you care about |
| 30 metrics, 3 significant? | expect about 1.5 by chance; correct (Holm or BH) and replicate |

---

→ Next: [05-regression-and-glms.md](05-regression-and-glms.md) — the t-test as a regression: OLS, diagnostics, and logistic and Poisson GLMs.
