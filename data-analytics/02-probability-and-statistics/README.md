# 02 — Probability and Statistics

> Every analytics decision is a claim about data you have not seen. This pillar is how to make that claim honestly.
> Jump to: [Reading order](#reading-order) · [Rules of thumb](#rules-of-thumb) · [Deck and practice](#deck-and-practice) · [References](references.md)

---

## What it is

The statistics an analyst uses in practice: looking at data before summarising it, the rules of probability, the distributions behind common metrics, estimates with intervals, hypothesis tests, and regression as an estimate with a standard error.

## Why it matters

The errors that reach a decision are rarely exotic. A mean is quoted over a column that is 95% zeros. A rare-event filter is called 99% accurate when nine in ten of its flags are false. A winning segment is one of twenty that were tested. A session-level analysis of a user-level experiment calls noise significant more than a quarter of the time. Each of these has a one-line fix once you can see it, and this pillar teaches you to see it. Everything in [experimentation and causality](../03-experimentation-and-causality/README.md) and [Bayesian analysis](../04-bayesian-analysis/README.md) assumes it.

## The story

Larkspur, a fictional online plant shop, hands you twenty thousand users and asks about the average customer. You look first and find that the average customer does not exist ([1](notes/01-descriptive-statistics-and-eda.md)). You learn the rules for reasoning about data you do not have, including the base-rate rule that makes the fraud filter wrong nine times in ten ([2](notes/02-probability-foundations.md)), then the shapes that recur and why the Central Limit Theorem takes tens of thousands of users to earn its keep on revenue ([3](notes/03-distributions-and-sampling.md)). You report numbers with intervals, by formula and by bootstrap ([4](notes/04-estimation.md)), turn intervals into decisions and watch twenty tests produce a false discovery ([5](notes/05-hypothesis-testing.md)), and finally see that a t-test was a regression all along, which lets you add covariates, fix standard errors and model conversions and counts ([6](notes/06-regression-and-glms.md)). The new checkout you have been testing then goes to a proper experiment in pillar 03.

---

## Reading order

| # | Chapter | You will be able to |
|---|---|---|
| 1 | [Descriptive Statistics and EDA](notes/01-descriptive-statistics-and-eda.md) | Audit a new extract, choose summaries the shape allows, and write the finding down |
| 2 | [Probability Foundations](notes/02-probability-foundations.md) | Invert a conditional with Bayes, use linearity, and say when variances add |
| 3 | [Distributions and Sampling](notes/03-distributions-and-sampling.md) | Name the distribution behind a metric, and know when LLN and CLT fail you |
| 4 | [Estimation](notes/04-estimation.md) | Fit by maximum likelihood, read a confidence interval, bootstrap, plan sample size |
| 5 | [Hypothesis Testing](notes/05-hypothesis-testing.md) | Pick a test, read a p-value correctly, and correct for many comparisons |
| 6 | [Regression and GLMs](notes/06-regression-and-glms.md) | Read OLS output, check it, cluster its errors, and fit logistic and Poisson models |

---

## Rules of thumb

**Look first** ([1](notes/01-descriptive-statistics-and-eda.md))
- Establish what one row is before anything else. Revenue per user, per session and per order are three different numbers.
- When mean and median disagree by a lot, the tail is running the summary. Look at the tail.
- Show N next to every rate, and count every row you remove.

**Probability** ([2](notes/02-probability-foundations.md))
- P(A | B) is not P(B | A). The base rate sets the gap between them.
- Expectations always add. Variances add only for uncorrelated variables.
- Standard errors assume independent rows. Sessions inside users are not independent.

**Distributions and sampling** ([3](notes/03-distributions-and-sampling.md))
- N ≥ 30 is not a law. On zero-inflated revenue a 95% interval can cover 56% at n = 30.
- More rows do not fix selection bias.
- The extremes of a league table are usually its smallest groups, so shrink or show N.

**Estimation** ([4](notes/04-estimation.md))
- Report the interval, not the point. Precision costs the square: half the error needs four times the data.
- Use Wilson for small counts. Use the delta method or a user-level bootstrap for ratios.
- Bootstrap the independent unit, which is usually the user.

**Testing** ([5](notes/05-hypothesis-testing.md))
- Default to Welch. If you are unsure of a formula, shuffle the labels.
- Twenty tests of nothing have a 64% chance of a false positive. Name one primary question in advance.
- At low power, significant estimates are inflated. Do not forecast from them.

**Regression** ([6](notes/06-regression-and-glms.md))
- Add pre-period covariates to experiments. They shrink the standard error and bias nothing.
- Cluster at the level of randomisation. Use robust SEs on money.
- Report marginal effects rather than odds ratios, and check dispersion on every Poisson fit.

---

## Deck and practice

**Deck:** [slides/probability-and-statistics.pptx](slides/probability-and-statistics.pptx) ([PDF](slides/probability-and-statistics.pdf)), built from [slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=data-analytics/02-probability-and-statistics STRICT=1 PREVIEW=1`.

**Chapters:** every code block runs top to bottom as a notebook on synthetic data with fixed seeds:

```bash
uv run --with numpy --with pandas --with scipy --with statsmodels python
```

**Practice:** the coursework in [practice/](practice/) is kept as written.

| File | What it is | How to run |
|---|---|---|
| [5_Statistical_Analysis.ipynb](practice/5_Statistical_Analysis.ipynb) | Distributions, tests, A/B basics, correlation and causation | `uv run --with jupyter --with numpy --with pandas --with scipy --with statsmodels --with matplotlib --with seaborn jupyter lab` |
| [courses/wesleyan_data_cleaning.py](practice/courses/wesleyan_data_cleaning.py) | Recoding survey sentinels on NESARC | Needs `nesarc_pds.csv`, which is not in the repo; read it as a worked example |
| [courses/wesleyan_inferential_statistics.py](practice/courses/wesleyan_inferential_statistics.py) | ANOVA, chi-square and Tukey via formulas on NESARC | Same data requirement |
| [courses/umich_statistical_analysis.py](practice/courses/umich_statistical_analysis.py) | Michigan coursework on statistical analysis | Read as a worked example; check its data paths first |

**Next:** [03 Experimentation and Causality](../03-experimentation-and-causality/README.md). **References:** [references.md](references.md).
