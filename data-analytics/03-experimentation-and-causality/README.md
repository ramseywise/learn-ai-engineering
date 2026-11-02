# 03 — Experimentation and Causality

> Whether a change caused a result is the question analysts are hired to answer. This pillar is how to answer it with an experiment, and what to do when you cannot run one.
> Jump to: [Reading order](#reading-order) · [Rules of thumb](#rules-of-thumb) · [Deck and practice](#deck-and-practice) · [References](references.md)

---

## What it is

How to design and read an A/B test, choose the metric it decides on, run many tests safely on a platform, and reason about cause and effect from observational data when randomisation is not available.

## Why it matters

Most product changes do little, and a dashboard cannot separate that from the weather, the seasons or the kind of customer who opts in. A controlled experiment can, but only if the split, the unit, the metric and the stopping rule are right. Each of those fails in ways that produce confident wrong answers: a 50.4/49.6 split that signals a broken pipeline, a click-through rate that falls 40% while clicks rise 74%, a daily peek that turns 5% false positives into 25%. Many questions cannot be randomised at all, and the same care is what lets you answer them.

## The story

Larkspur, a fictional online plant shop, wants to know whether a new checkout works. You size and run the test, check the split, and report a lift with an interval ([1](notes/01-ab-testing.md)). You then find that the answer depends on what you measured: revenue per user rises while revenue per session falls, because an email changed the denominator ([2](notes/02-metrics-and-kpi-design.md)). As Larkspur runs dozens of tests at once, you cut variance with CUPED, make looking early safe, and build the checks that catch a broken test before anyone believes it ([3](notes/03-experimentation-at-scale.md)). Finally, marketing reports that loyalty-email subscribers order 1.21 more times a year, when the true effect is 0.30, and you reach for the designs that work without randomisation ([4](notes/04-correlation-and-causation.md)). [Bayesian analysis](../04-bayesian-analysis/README.md) then re-answers the checkout question in a different language.

---

## Reading order

| # | Chapter | You will be able to |
|---|---|---|
| 1 | [A/B Testing](notes/01-ab-testing.md) | Size a test, check it for sample ratio mismatch, analyse it at the right unit, and report a lift with an interval |
| 2 | [Metrics and KPI Design](notes/02-metrics-and-kpi-design.md) | Separate north star, OEC, guardrail and diagnostic, read ratio metrics correctly, and test a guardrail |
| 3 | [Experimentation at Scale](notes/03-experimentation-at-scale.md) | Apply CUPED, use sequential tests, diagnose an SRM, and handle interference and overlapping tests |
| 4 | [Correlation and Causation](notes/04-correlation-and-causation.md) | Spot confounders, mediators and colliders, and use DiD, IV, RD, weighting and synthetic control |

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

---

## Deck and practice

**Deck:** [slides/experimentation-and-causality.pptx](slides/experimentation-and-causality.pptx) ([PDF](slides/experimentation-and-causality.pdf)), built from [slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=data-analytics/03-experimentation-and-causality STRICT=1 PREVIEW=1`.

**Chapters:** every code block runs top to bottom as a notebook on synthetic data with fixed seeds:

```bash
uv run --with numpy --with pandas --with scipy --with statsmodels python
```

Add `--with dowhy` for the DoWhy block in chapter 4.

**Practice:** the coursework in [practice/](practice/) is kept as written.

| File | What it is | How to run |
|---|---|---|
| [AB-Bayes/AB_Testing_with_Python.ipynb](practice/AB-Bayes/AB_Testing_with_Python.ipynb) | Frequentist A/B analysis on the Kaggle `ab_data.csv` | Needs `ab_data.csv`, which is not in the repo, and imports for `statsmodels.stats.api` and `ceil`, which the notebook omits. [Chapter 1](notes/01-ab-testing.md) covers the same analysis on data it generates |

**Next:** [04 Bayesian Analysis](../04-bayesian-analysis/README.md). **Online evaluation of LLM features** continues in [the Eval pillar](../../generative-ai/08-eval/README.md). **References:** [references.md](references.md).
