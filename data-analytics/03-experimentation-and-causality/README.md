# Experimentation and causality

Answer whether a change caused a result, with an experiment when you can run one and with a design you can defend when you cannot. Three steps: design and read one A/B test and the metric it decides on, run many tests safely on a platform, and reason about cause and effect from observational data.

**What you should already know.** Nothing below is taught again here. Tick each line off, and go back to the chapter it links for any you cannot.

Probability and statistics, from [module 02](../02-probability-and-statistics/README.md):

- [ ] Report an estimate with a confidence interval, and bootstrap it ([estimation](../02-probability-and-statistics/notes/04-estimation.md))
- [ ] Pick a test, read a p-value correctly, and say why twenty tests find a false positive ([hypothesis testing](../02-probability-and-statistics/notes/05-hypothesis-testing.md))
- [ ] Read OLS output, add a covariate, and say what clustered errors fix and what they do not ([regression and GLMs](../02-probability-and-statistics/notes/06-regression-and-glms.md))
- [ ] Say what fixed effects remove, and what they cannot fix ([panel data and fixed effects](../02-probability-and-statistics/notes/08-panel-data-and-fixed-effects.md))

Processing data, from [module 01](../01-python-for-data-analysis/README.md):

- [ ] Get one number per group and check that the groups add up to the total ([groupby and aggregation](../01-python-for-data-analysis/notes/07-groupby-and-aggregation.md))
- [ ] State what a join should do and count rows before and after ([reshaping and joins](../01-python-for-data-analysis/notes/04-reshaping-and-joins.md))

## Lecture

Start with the overview deck, [Experiments and causality](slides/experimentation-and-causality.pptx) ([PDF](slides/experimentation-and-causality.pdf)). It walks through the module's chapters in reading order on the Larkspur checkout test. There is one deck for the module, not one per step.

## The core

Whether a change caused a result is the question analysts are hired to answer, and the one this module keeps asking is: **did the change cause the result?**

Most product changes do little, and a dashboard cannot separate that from the weather, the seasons or the kind of customer who opts in. A controlled experiment can, but only if the split, the unit, the metric and the stopping rule are right. Each of those fails in ways that produce confident wrong answers: a 50.4/49.6 split that signals a broken pipeline, a click-through rate that falls 40% while clicks rise 74%, a daily peek that turns 5% false positives into 25%. Many questions cannot be randomised at all, and the same care is what lets you answer them.

Larkspur, a fictional online plant shop, wants to know whether a new checkout works. You size and run the test, check the split, and report a lift with an interval. You find that the answer depends on what you measured, because an email changed the denominator. As Larkspur runs dozens of tests at once you cut variance with CUPED, make looking early safe, and build the checks that catch a broken test. Then marketing reports that loyalty-email subscribers order 1.21 more times a year, when the true effect is 0.30, and you reach for the designs that work without randomisation. Fernhill Home, the retailer from [Applied Analyses](../06-applied-analyses/README.md), asks whether its loyalty club works: members spent £95.54 more, the true effect is £23.38, and six ways of building a comparison group each land about £3 to £4 above it, because of a trait nobody logged. [Bayesian analysis](../04-bayesian-analysis/README.md) then re-answers the checkout question in a different language. For the long view of why graphs came into this subject, Pearl and Mackenzie's *The Book of Why* is the narrative version.

## Syllabus

One row per step. **Core concepts** are the ideas that make the step go right, **Study** is what to read, **Labs** is what to run afterwards, and **Sources** is where to read more. How the chapter code runs is in the Practice section below.

| Submodule | Core concepts | Study | Labs | Sources |
|---|---|---|---|---|
| **1. Design and read one test:** the split, the unit and the metric | Size the test before it starts: halving the minimum detectable effect costs about four times the users. Check the sample ratio before you look at the outcome. Analyse at the unit you randomised, because a pageview-level analysis of a user-level test raised the false positive rate from 5% to about 11%. Never report a ratio without its numerator and denominator. Agree one overall evaluation criterion in advance, and give each guardrail a margin and a one-sided test. A result that looks too good is usually a bug. | [1 A/B testing](notes/01-ab-testing.md) · [2 Metrics and KPI design](notes/02-metrics-and-kpi-design.md) | [ab_test_from_scratch.py](practice/ab_test_from_scratch.py), the two-proportion test, sample size and a sample ratio check · [AB-Bayes/AB_Testing_with_Python.ipynb](practice/AB-Bayes/AB_Testing_with_Python.ipynb), which needs a data file that is not in the repo | Bruce & Bruce ch. 3 · Reinhart, *Statistics Done Wrong* ch. 2, 3 and 6 · McElreath ch. 15 · Kohavi et al., [Controlled experiments on the web](https://doi.org/10.1007/s10618-008-0114-1) · Dmitriev et al., [A Dirty Dozen](https://doi.org/10.1145/3097983.3098024) · Udacity, [A/B Testing](https://www.udacity.com/course/ab-testing--ud257) |
| **2. Run many tests safely:** variance, peeking and trust checks | CUPED removes ρ² of the variance for free, if the covariate predates exposure. If people will look early, use sequential boundaries or always-valid p-values. Treat a sample ratio mismatch as a stopped test. Users can affect each other, and overlapping tests can interfere. Adding up reported lifts overstates what shipped. | [3 Experimentation at scale](notes/03-experimentation-at-scale.md) | [ab_test_from_scratch.py](practice/ab_test_from_scratch.py), the cost of peeking and a sample ratio check | Kohavi, Tang & Xu, [*Trustworthy Online Controlled Experiments*](https://experimentguide.com/) · Efron & Hastie ch. 3, 15 and 20 · Lattimore & Szepesvári ch. 33 · Deng et al., [CUPED](https://doi.org/10.1145/2433396.2433413) · Johari et al., [Always Valid Inference](https://arxiv.org/abs/1512.04922) · Fabijan et al., [Diagnosing Sample Ratio Mismatch](https://doi.org/10.1145/3292500.3330722) |
| **3. When you cannot randomise:** confounding, matching and weighting | Draw the graph before you pick controls, and control for confounders, not for mediators or colliders. Plot the pre-trends before you trust a difference-in-differences. Every method without randomisation has an assumption the data cannot prove, so say what it is. Check balance and overlap before you read the outcome. Report who was kept, and report the effective sample and the largest weight. Say what an unmeasured confounder would have to do to undo the result. | [4 Correlation and causation](notes/04-correlation-and-causation.md) · [5 Matching and weighting](notes/05-matching-and-weighting.md) | [ch05_matching_weighting.py](practice/ch05_matching_weighting.py), the Fernhill loyalty club answered six ways | Pearl, Glymour & Jewell sections 3.3 and 3.4 · Hernán & Robins ch. 7, 12, 13 and 15 · Cunningham, [*Causal Inference: The Mixtape*](https://mixtape.scunning.com/) · Huntington-Klein, *The Effect* ch. 14 · Facure ch. 10 and 11 · McElreath ch. 10 · Reinhart, *Statistics Done Wrong* ch. 8 · Rosenbaum & Rubin, [The central role of the propensity score](https://doi.org/10.1093/biomet/70.1.41) · Brady Neal, [Introduction to Causal Inference](https://www.bradyneal.com/causal-inference-course) |

Every source and the notes it maps to: [references.md](references.md).

## Rules of thumb

**A/B tests** ([1](notes/01-ab-testing.md))
- **Size the test before it starts:** halving the minimum detectable effect costs about four times the users.
- **Run the SRM check before you look at the outcome.**
- **Analyse at the unit you randomised.** Pageview-level analysis of a user-level test took the false positive rate from 5% to about 11% in our simulation.

**Metrics** ([2](notes/02-metrics-and-kpi-design.md))
- **Never report a ratio without its numerator and denominator.**
- **Agree one OEC in advance,** and give each guardrail a margin and a one-sided test.
- **Apply Twyman's law:** a result that looks too good is usually a bug.

**At scale** ([3](notes/03-experimentation-at-scale.md))
- **CUPED removes ρ² of the variance for free.** The covariate must predate exposure.
- **If people will look, use sequential boundaries or always-valid p-values.**
- **Treat an SRM as a stopped test.** Adding up reported lifts overstates what shipped.

**Causality** ([4](notes/04-correlation-and-causation.md))
- **Draw the graph before you pick controls.** Control for confounders, not for mediators or colliders.
- **Plot the pre-trends before you trust a DiD.**
- **Every method without randomisation has an assumption that the data cannot prove.** Say what it is.

**Matching and weighting** ([5](notes/05-matching-and-weighting.md))
- **Match or weight on covariates measured before treatment,** show the balance table first, and say what an unmeasured confounder would have to do to undo the result.
- **Report who was kept.** An estimate on 53% of the treated answers a different question.
- **Report the effective sample and the largest weight.** In our data, 5,710 weighted controls were worth 107.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| None in other subjects | Starts from [DA 02](../02-probability-and-statistics/README.md) in this subject |

**Feeds into**

| Chapter | Why |
|---|---|
| [GA 08/11 Production and the maturity ladder](../../generative-ai/08-eval/notes/11-production-and-the-maturity-ladder.md) | A/B tests of LLM features, with peeking, SRM and CUPED taught here |
| [GA 08/09 Reading results](../../generative-ai/08-eval/notes/09-reading-results.md) | The sample-size question for two versions |
| [AIE 01/08 Evaluating prompts](../../ai-engineering/01-prompt-engineering/notes/08-evaluating-prompts.md) | Prompt A against prompt B online is an A/B test |
| [AIE 09/02 Prompt injection and jailbreaks](../../ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks.md) | Utility without attack works as a guardrail metric |
| [DS 05/03 Two-tower and evaluation](../../data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md) | Online evaluation of a recommender is an A/B test |

<a id="deck-and-practice"></a>

## Practice

Every code block in the chapters runs top to bottom as a notebook on synthetic data with fixed seeds:

```bash
uv run --with numpy --with pandas --with scipy --with statsmodels python
```

Add `--with dowhy` for the DoWhy block in chapter 4. Chapter 5 is the exception: its code lives in a script, listed below.

The coursework in [practice/](practice/) is kept as written, and the chapter 5 script is new.

| File | What it is | How to run |
|---|---|---|
| [AB-Bayes/AB_Testing_with_Python.ipynb](practice/AB-Bayes/AB_Testing_with_Python.ipynb) | Frequentist A/B analysis on the Kaggle `ab_data.csv` | Needs `ab_data.csv`, which is not in the repo, and imports for `statsmodels.stats.api` and `ceil`, which the notebook omits. [Chapter 1](notes/01-ab-testing.md) covers the same analysis on data it generates |
| [ab_test_from_scratch.py](practice/ab_test_from_scratch.py) | A conversion-rate A/B test by hand: the two-proportion z-test, sample size, simulated false positive rate and power, the cost of peeking, and a sample ratio mismatch check | `uv run ab_test_from_scratch.py` from `practice/` |
| [ch05_matching_weighting.py](practice/ch05_matching_weighting.py) | Every table and figure in [chapter 5](notes/05-matching-and-weighting.md), on the club table from the shared retail generator | `uv run practice/ch05_matching_weighting.py` from this folder; the script finds its data from any directory. Under a minute; the first run also installs DoWhy |

The deck is built from [slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=data-analytics/03-experimentation-and-causality STRICT=1 PREVIEW=1`.

## Primary texts

- Pearl, Glymour and Jewell, *Causal Inference in Statistics: A Primer*
- Kohavi et al., *Controlled experiments on the web: survey and practical guide*
- Cunningham, *Causal Inference: The Mixtape*
- Bruce and Bruce, *Practical Statistics for Data Scientists*, ch. 3

Everything else: [references.md](references.md).

## Next

Start with submodule 1, **Design and read one test**: read [1 A/B testing](notes/01-ab-testing.md), then work through its labs in the syllabus row.

After submodule 3 you can size and read an experiment, run many of them without fooling yourself, and say what a comparison without randomisation does and does not establish. The next module is [applied analyses](../06-applied-analyses/README.md), which puts these methods to work on business questions, and after it [Bayesian analysis](../04-bayesian-analysis/README.md), which answers this module's checkout test again with posteriors. Online evaluation of LLM features continues in [the Eval pillar](../../generative-ai/08-eval/README.md).
