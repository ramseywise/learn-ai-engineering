# 03 — Experimentation and Causality

> Whether a change caused a result is the question analysts are hired to answer. This pillar is how to answer it with an experiment, and what to do when you cannot run one.
> Jump to: [Reading order](#reading-order) · [Rules of thumb](#rules-of-thumb) · [Deck and practice](#deck-and-practice) · [References](references.md)

---

## What it is

How to design and read an A/B test, choose the metric it decides on, run many tests safely on a platform, and reason about cause and effect from observational data when randomisation is not available.

## Why it matters

Most product changes do little, and a dashboard cannot separate that from the weather, the seasons or the kind of customer who opts in. A controlled experiment can, but only if the split, the unit, the metric and the stopping rule are right. Each of those fails in ways that produce confident wrong answers: a 50.4/49.6 split that signals a broken pipeline, a click-through rate that falls 40% while clicks rise 74%, a daily peek that turns 5% false positives into 25%. Many questions cannot be randomised at all, and the same care is what lets you answer them.

## The story

Larkspur, a fictional online plant shop, wants to know whether a new checkout works. You size and run the test, check the split, and report a lift with an interval ([1](notes/01-ab-testing.md)). You then find that the answer depends on what you measured: revenue per user rises while revenue per session falls, because an email changed the denominator ([2](notes/02-metrics-and-kpi-design.md)). As Larkspur runs dozens of tests at once, you cut variance with CUPED, make looking early safe, and build the checks that catch a broken test before anyone believes it ([3](notes/03-experimentation-at-scale.md)). Finally, marketing reports that loyalty-email subscribers order 1.21 more times a year, when the true effect is 0.30, and you reach for the designs that work without randomisation ([4](notes/04-correlation-and-causation.md)). Fernhill Home, the retailer from [Applied Analyses](../06-applied-analyses/README.md), then asks whether its loyalty club works: members spent £95.54 more, the true effect is £23.38, and six ways of building a comparison group each land about £3 to £4 above it, because of a trait nobody logged ([5](notes/05-matching-and-weighting.md)). [Bayesian analysis](../04-bayesian-analysis/README.md) then re-answers the checkout question in a different language. For the long view of why graphs came into this subject, Pearl and Mackenzie's *The Book of Why* is the narrative version.

---

## Reading order

| # | Chapter | You will be able to |
|---|---|---|
| 1 | [A/B Testing](notes/01-ab-testing.md) | Size a test, check it for sample ratio mismatch, analyse it at the right unit, and report a lift with an interval |
| 2 | [Metrics and KPI Design](notes/02-metrics-and-kpi-design.md) | Separate north star, OEC, guardrail and diagnostic, read ratio metrics correctly, and test a guardrail |
| 3 | [Experimentation at Scale](notes/03-experimentation-at-scale.md) | Apply CUPED, use sequential tests, diagnose an SRM, and handle interference and overlapping tests |
| 4 | [Correlation and Causation](notes/04-correlation-and-causation.md) | Spot confounders, mediators and colliders, apply the backdoor and front-door criteria, and use DiD, IV, RD, weighting and synthetic control |
| 5 | [Matching and Weighting](notes/05-matching-and-weighting.md) | Check balance and overlap before reading the outcome, build a comparison group by matching or weighting, say which customers the estimate covers, and state what a sensitivity check does and doesn't rule out |

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
| [AIE 01/09 Evaluating prompts](../../ai-engineering/01-prompt-engineering/notes/09-evaluating-prompts.md) | Prompt A against prompt B online is an A/B test |
| [AIE 09/02 Prompt injection and jailbreaks](../../ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks.md) | Utility without attack works as a guardrail metric |
| [DS 05/03 Two-tower and evaluation](../../data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md) | Online evaluation of a recommender is an A/B test |

---

## Rules of thumb

**A/B tests** ([1](notes/01-ab-testing.md))
- Size the test before it starts: halving the minimum detectable effect costs about four times the users.
- Run the SRM check before you look at the outcome.
- Analyse at the unit you randomised. Pageview-level analysis of a user-level test took the false positive rate from 5% to about 11% in our simulation.

**Metrics** ([2](notes/02-metrics-and-kpi-design.md))
- Never report a ratio without its numerator and denominator.
- Agree one OEC in advance, and give each guardrail a margin and a one-sided test.
- Apply Twyman's law: a result that looks too good is usually a bug.

**At scale** ([3](notes/03-experimentation-at-scale.md))
- CUPED removes ρ² of the variance for free. The covariate must predate exposure.
- If people will look, use sequential boundaries or always-valid p-values.
- Treat an SRM as a stopped test. Adding up reported lifts overstates what shipped.

**Causality** ([4](notes/04-correlation-and-causation.md))
- Draw the graph before you pick controls. Control for confounders, not for mediators or colliders.
- Plot the pre-trends before you trust a DiD.
- Every method without randomisation has an assumption that the data cannot prove. Say what it is.

**Matching and weighting** ([5](notes/05-matching-and-weighting.md))
- Match or weight on covariates measured before treatment, show the balance table first, and say what an unmeasured confounder would have to do to undo the result.
- Report who was kept. An estimate on 53% of the treated answers a different question.
- Report the effective sample and the largest weight. In our data, 5,710 weighted controls were worth 107.

---

## Deck and practice

**Deck:** [slides/experimentation-and-causality.pptx](slides/experimentation-and-causality.pptx) ([PDF](slides/experimentation-and-causality.pdf)), built from [slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=data-analytics/03-experimentation-and-causality STRICT=1 PREVIEW=1`.

**Chapters:** every code block runs top to bottom as a notebook on synthetic data with fixed seeds:

```bash
uv run --with numpy --with pandas --with scipy --with statsmodels python
```

Add `--with dowhy` for the DoWhy block in chapter 4. Chapter 5 is the exception: its code lives in a script, listed below.

**Practice:** the coursework in [practice/](practice/) is kept as written, and the chapter 5 script is new.

| File | What it is | How to run |
|---|---|---|
| [AB-Bayes/AB_Testing_with_Python.ipynb](practice/AB-Bayes/AB_Testing_with_Python.ipynb) | Frequentist A/B analysis on the Kaggle `ab_data.csv` | Needs `ab_data.csv`, which is not in the repo, and imports for `statsmodels.stats.api` and `ceil`, which the notebook omits. [Chapter 1](notes/01-ab-testing.md) covers the same analysis on data it generates |
| [ch05_matching_weighting.py](practice/ch05_matching_weighting.py) | Every table and figure in [chapter 5](notes/05-matching-and-weighting.md), on the club table from the shared retail generator | `uv run practice/ch05_matching_weighting.py` from this folder; the script finds its data from any directory. Under a minute; the first run also installs DoWhy |

## Primary texts

- Pearl, Glymour and Jewell, *Causal Inference in Statistics: A Primer*
- Kohavi et al., *Controlled experiments on the web: survey and practical guide*
- Cunningham, *Causal Inference: The Mixtape*
- Bruce and Bruce, *Practical Statistics for Data Scientists*, ch. 3

Everything else: [references.md](references.md).

**Next:** [04 Bayesian Analysis](../04-bayesian-analysis/README.md). **Online evaluation of LLM features** continues in [the Eval pillar](../../generative-ai/08-eval/README.md). **References:** [references.md](references.md).
