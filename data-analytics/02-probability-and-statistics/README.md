# Probability and statistics

Say how far a claim about data you have not seen can be trusted. Four steps, each with the check that catches its usual mistake: look at the data and learn the rules of chance, report an estimate with an interval and test whether a difference is real, model a relationship with regression, and ask how the rows came to be in your table.

**What you should already know.** Nothing below is taught again here. Tick each line off, and go back to the chapter it links for any you cannot.

Processing data, from [module 01](../01-python-for-data-analysis/README.md):

- [ ] Load a file into a DataFrame and check its shape and column types ([loading data](../01-python-for-data-analysis/notes/02-loading-data.md))
- [ ] Filter rows with a mask and pick columns with `loc` ([indexing and selection](../01-python-for-data-analysis/notes/03-indexing-and-selection.md))
- [ ] Say why a missing value is not a zero, and fix a column's type ([cleaning](../01-python-for-data-analysis/notes/05-cleaning.md))
- [ ] Get one number per group, and print a count beside every mean ([groupby and aggregation](../01-python-for-data-analysis/notes/07-groupby-and-aggregation.md))

Python, from the [Python track](../../programming/python/README.md):

- [ ] Write a function that takes arguments and returns a value ([functions](../../programming/python/01-foundations/notes/02-functions.md))
- [ ] Loop over a sequence and keep a running result, which is how the chapters simulate ([loops](../../programming/python/01-foundations/notes/03-loops.md))

## Lecture

Start with the overview deck, [Probability and statistics](slides/probability-and-statistics.pptx) ([PDF](slides/probability-and-statistics.pdf)). It walks through the module's chapters in reading order on the same Larkspur data as the notes. There is one deck for the module, not one per step.

## The core

Every analytics decision is a claim about data you have not seen: next month's users, the other arm of an experiment, the population behind a sample. This module is how to make that claim honestly. The one question it keeps asking is: **what are we entitled to claim?**

The errors that reach a decision are rarely exotic. A mean is quoted over a column that is 95% zeros. A rare-event filter is called 99% accurate when nine in ten of its flags are false. A winning segment is one of twenty that were tested. A session-level analysis of a user-level experiment calls noise significant more than a quarter of the time. Each has a one-line fix once you can see it, and each chapter teaches you to see one. [Experimentation and causality](../03-experimentation-and-causality/README.md) and [Bayesian analysis](../04-bayesian-analysis/README.md) assume all of it.

The running example is Larkspur, a fictional online plant shop with twenty thousand users and a checkout it wants to redesign. You find that the average customer does not exist, learn the base-rate rule that makes the fraud filter wrong nine times in ten, and see why the Central Limit Theorem takes tens of thousands of users to earn its keep on revenue. You then report numbers with intervals, watch twenty tests produce a false discovery, and find that a t-test was a regression all along. You step back to ask what a model claims about the process behind the rows, and when the same stores come back week after week you compare each with itself, and a discount that looked harmful turns out to help. The new checkout then goes to a proper experiment in module 03.

## Syllabus

One row per step. **Core concepts** are the ideas that make the step go right, **Study** is what to read, **Labs** is what to run afterwards, and **Sources** is where to read more. The chapter code runs top to bottom as a notebook on synthetic data with fixed seeds, as the Practice section below explains.

| Submodule | Core concepts | Study | Labs | Sources |
|---|---|---|---|---|
| **1. Look and reason:** what the data is, and the rules for what it is not | Establish what one row is before anything else. When the mean and median disagree by a lot, the tail is running the summary. P(A given B) is not P(B given A), and the base rate sets the gap. Expectations always add, and variances add only for uncorrelated variables. The sample mean settles down only as N grows, and on zero-inflated revenue N of 30 is not enough. Small groups crowd both ends of a league table. | [1 Descriptive statistics and EDA](notes/01-descriptive-statistics-and-eda.md) · [2 Probability foundations](notes/02-probability-foundations.md) · [3 Distributions and sampling](notes/03-distributions-and-sampling.md) | [5_Statistical_Analysis](practice/5_Statistical_Analysis.ipynb), distributions and correlation against causation · [probability_puzzles.py](practice/probability_puzzles.py) · [distributions_and_estimators.py](practice/distributions_and_estimators.py) · [courses/wesleyan_data_cleaning.py](practice/courses/wesleyan_data_cleaning.py), a worked example | Bruce & Bruce ch. 1 and 2 · Downey, *Think Stats* ch. 1 to 6 · Reinhart, *Statistics Done Wrong* ch. 3 and 4 · Grinstead & Snell ch. 4 · Meng, [Statistical Paradises and Paradoxes in Big Data (I)](https://doi.org/10.1214/18-AOAS1161SF) |
| **2. Estimate and test:** a number with its interval, and a decision | Report the interval, not the point. Half the error costs four times the data. Use Wilson for small counts, and bootstrap the independent unit, which is usually the user. A test answers one question: could this pattern be noise? Default to Welch, and if you are unsure of a formula, shuffle the labels. Twenty tests of nothing have a 64% chance of a false positive, so name one primary question in advance. At low power, significant estimates are inflated. | [4 Estimation](notes/04-estimation.md) · [5 Hypothesis testing](notes/05-hypothesis-testing.md) | [5_Statistical_Analysis](practice/5_Statistical_Analysis.ipynb), hypothesis tests and A/B testing with power analysis · [distributions_and_estimators.py](practice/distributions_and_estimators.py), bias and mean squared error · [courses/wesleyan_inferential_statistics.py](practice/courses/wesleyan_inferential_statistics.py) and [courses/umich_statistical_analysis.py](practice/courses/umich_statistical_analysis.py), worked examples | Bruce & Bruce ch. 2 and 3 · Downey, *Think Stats* ch. 7 and 8 · Reinhart, *Statistics Done Wrong* ch. 1 to 6 and 9 to 12 · James et al. ch. 13 · Efron & Hastie ch. 1, 2 and 4 · Wasserstein & Lazar, [The ASA Statement on p-Values](https://doi.org/10.1080/00031305.2016.1154108) · Benjamini & Hochberg, [Controlling the False Discovery Rate](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x) |
| **3. Model a relationship:** regression with its standard error | A t-test is a regression with one binary regressor, which lets you add covariates. Pre-period covariates shrink the standard error and bias nothing. Cluster at the level of randomisation, and use robust standard errors on money. For a yes or no outcome use logistic regression, and for counts use a Poisson model with an offset for exposure. Report marginal effects rather than odds ratios, and check dispersion on every Poisson fit. | [6 Regression and GLMs](notes/06-regression-and-glms.md) · [6b Logistic regression and Poisson GLMs](notes/06b-logistic-regression-and-poisson-glms.md) | None yet | Bruce & Bruce ch. 4 and 5 · Downey, *Think Stats* ch. 9 · James et al. ch. 3, section 4.3 and section 4.6 · Reinhart, *Statistics Done Wrong* ch. 7 and 8 · McKinney ch. 13 · McElreath ch. 9 to 11 · Cameron & Miller, [A Practitioner's Guide to Cluster-Robust Inference](https://doi.org/10.3368/jhr.50.2.317) · Gelman et al., [A weakly informative default prior distribution for logistic and other regression models](https://arxiv.org/abs/0901.4011) |
| **4. Ask how the rows got there:** the process behind the table | Write the data generating process you believe, then simulate from it to see whether your estimator recovers it. A better fit in this sample is not a better answer for the population. Decide whether you are explaining or predicting first. A big sample is not a representative one. Fixed effects change the estimate, because they compare each unit with itself. They remove only what is constant within a unit, and a flat pre-period does not prove parallel trends. | [7 The data generating process](notes/07-data-generating-process.md) · [8 Panel data and fixed effects](notes/08-panel-data-and-fixed-effects.md) | [ch07_data_generating_process.py](practice/ch07_data_generating_process.py) · [ch08_panel_data.py](practice/ch08_panel_data.py) | Shmueli, [To Explain or to Predict?](https://arxiv.org/abs/1101.0891) · Breiman, [Statistical Modeling: The Two Cultures](https://doi.org/10.1214/ss/1009213726) · Efron & Hastie ch. 12 and 13 · Huntington-Klein, *The Effect* ch. 16 and 18 · Facure, *Causal Inference for the Brave and True* ch. 14 · Bell & Jones, [Explaining Fixed Effects](https://eprints.whiterose.ac.uk/89757) |

Every source and the notes it maps to: [references.md](references.md).

## Rules of thumb

**Look first** ([1](notes/01-descriptive-statistics-and-eda.md))
- **Establish what one row is before anything else.** Revenue per user, per session and per order are three different numbers.
- **When mean and median disagree by a lot, the tail is running the summary.** Look at the tail.
- **Show N next to every rate,** and count every row you remove.

**Probability** ([2](notes/02-probability-foundations.md))
- **P(A | B) is not P(B | A).** The base rate sets the gap between them.
- **Expectations always add.** Variances add only for uncorrelated variables.
- **Standard errors assume independent rows.** Sessions inside users are not independent.

**Distributions and sampling** ([3](notes/03-distributions-and-sampling.md))
- **N ≥ 30 is not a law.** On zero-inflated revenue a 95% interval can cover 56% at n = 30.
- **More rows do not fix selection bias.**
- **The extremes of a league table are usually its smallest groups,** so shrink or show N.

**Estimation** ([4](notes/04-estimation.md))
- **Report the interval, not the point.** Precision costs the square: half the error needs four times the data.
- **Use Wilson for small counts.** Use the delta method or a user-level bootstrap for ratios.
- **Bootstrap the independent unit,** which is usually the user.

**Testing** ([5](notes/05-hypothesis-testing.md))
- **Default to Welch.** If you are unsure of a formula, shuffle the labels.
- **Twenty tests of nothing have a 64% chance of a false positive.** Name one primary question in advance.
- **At low power, significant estimates are inflated.** Do not forecast from them.

**Regression** ([6](notes/06-regression-and-glms.md), [6b](notes/06b-logistic-regression-and-poisson-glms.md))
- **Add pre-period covariates to experiments.** They shrink the standard error and bias nothing.
- **Cluster at the level of randomisation.** Use robust SEs on money.
- **Report marginal effects rather than odds ratios,** and check dispersion on every Poisson fit.

**The data generating process** ([7](notes/07-data-generating-process.md))
- **Write the data generating process you believe before you fit,** and simulate from it to see whether your estimator recovers it.
- **A better fit in this sample is not a better answer for the population.** Ask how the rows got in before you admire R².
- **Decide whether you are explaining or predicting first.** Held-out error can prefer a model whose coefficient is biased.

**Panel data** ([8](notes/08-panel-data-and-fixed-effects.md))
- **Clustered errors fix the standard error and not the estimate.** Fixed effects change the estimate, because they change the comparison.
- **Fixed effects remove what is constant within a unit.** Ask what moved at the same time as the treatment, and whether the treatment responded to the outcome.
- **A flat pre-period is not a proof of parallel trends.** On a staggered rollout, do not trust the single coefficient.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| None in other subjects | Starts from [DA 01](../01-python-for-data-analysis/README.md) in this subject |

**Feeds into**

| Chapter | Why |
|---|---|
| [DS 01/01 Statistical foundations](../../data-science/01-classical-ml/notes/01-statistical-foundations.md) | Takes conditional probability, expectation and maximum likelihood as given |
| [DS 01/04 Model evaluation](../../data-science/01-classical-ml/notes/04-model-evaluation.md) | The same two error cells, and the bootstrap for a metric's interval |
| [GA 08/09 Reading results](../../generative-ai/08-eval/notes/09-reading-results.md) | Standard errors, paired tests and multiple comparisons on pass rates |
| [GA 08/15 Calibrating a judge](../../generative-ai/08-eval/notes/15-calibration-against-human-labels.md#correcting-the-pass-rate) | Correcting a judge's pass rate is the same accounting as a base-rate calculation |
| [AIE 09/03 Guardrail models](../../ai-engineering/09-safety-and-security/notes/03-guardrail-models.md) | Shows the base-rate result on a safety classifier |
| [DE 05/01 Quality dimensions and tests](../../data-engineering/05-quality-and-observability/notes/01-quality-dimensions-and-tests.md) | EDA's checks for impossible values become pipeline tests |

<a id="deck-and-practice"></a>

## Practice

Every code block in the chapters runs top to bottom as a notebook on synthetic data with fixed seeds:

```bash
uv run --with numpy --with pandas --with scipy --with statsmodels python
```

The coursework in [practice/](practice/) is kept as written. The two chapter scripts are simulations with a known truth, and write their figures to `../sources/images/`.

| File | What it is | How to run |
|---|---|---|
| [ch07_data_generating_process.py](practice/ch07_data_generating_process.py) | Chapter 7: specifications, Meng's data defect correlation, and selection into the sample | `uv run ch07_data_generating_process.py` from `practice/` |
| [ch08_panel_data.py](practice/ch08_panel_data.py) | Chapter 8: pooled OLS, fixed effects, event studies and staggered timing | `uv run ch08_panel_data.py` from `practice/` |
| [5_Statistical_Analysis.ipynb](practice/5_Statistical_Analysis.ipynb) | Distributions, tests, A/B basics, correlation and causation | `uv run --with jupyter --with numpy --with pandas --with scipy --with statsmodels --with matplotlib --with seaborn jupyter lab` |
| [courses/wesleyan_data_cleaning.py](practice/courses/wesleyan_data_cleaning.py) | Recoding survey sentinels on NESARC | Needs `nesarc_pds.csv`, which is not in the repo; read it as a worked example |
| [courses/wesleyan_inferential_statistics.py](practice/courses/wesleyan_inferential_statistics.py) | ANOVA, chi-square and Tukey via formulas on NESARC | Same data requirement |
| [courses/umich_statistical_analysis.py](practice/courses/umich_statistical_analysis.py) | Michigan coursework on statistical analysis | Read as a worked example; check its data paths first |

The deck is built from [slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=data-analytics/02-probability-and-statistics STRICT=1 PREVIEW=1`.

## Primary texts

- Bruce and Bruce, *Practical Statistics for Data Scientists*
- Reinhart, *Statistics Done Wrong*
- James et al., *An Introduction to Statistical Learning with Applications in Python*
- Huntington-Klein, *The Effect*

Everything else: [references.md](references.md).

## Next

Start with submodule 1, **Look and reason**: read [1 Descriptive statistics and EDA](notes/01-descriptive-statistics-and-eda.md), then work through its labs in the syllabus row.

After submodule 4 you can say what a number from a sample entitles you to claim, and what the model behind it assumes about how the rows got there. The next module in the core is [visualisation and storytelling](../05-visualisation-and-storytelling/README.md), which turns a result into a chart someone can act on. [Experimentation and causality](../03-experimentation-and-causality/README.md) follows it, and answers the checkout question with a proper experiment.
