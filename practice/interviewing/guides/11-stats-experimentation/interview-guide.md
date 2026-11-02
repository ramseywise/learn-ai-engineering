---
origin: synthesized
sources:
  - data-analytics/02-probability-and-statistics/notes/
  - data-analytics/03-experimentation-and-causality/notes/
  - data-analytics/04-bayesian-analysis/notes/
confidence: high
cleaned: 2026-11-02
units:
  - data-analytics/02-probability-and-statistics
  - data-analytics/03-experimentation-and-causality
  - data-analytics/04-bayesian-analysis
---
# Stats & Experimentation — Study Guide

The stats screen in analyst and DS loops, and the "how would you test this?" follow-up in product and ML rounds. Interviewers rarely
want derivations. They probe whether you know what a number claims, and whether you can design a test that would convince a sceptic.

Worked figures are from the course notes, many on Larkspur, the course's fictional shop, so treat them as examples and not as
general rules. The `16σ²/δ²` rule and the formulas are standard.

## 1. Distributions and sampling

A distribution describes how likely each value is. Know one use of each:

| Distribution | Models | Example |
|---|---|---|
| **Normal** | Sums and averages of many small effects | Measurement error, sample means |
| **Binomial** | Successes out of n tries | Conversions out of visitors |
| **Poisson** | Counts in a fixed window | Support tickets per hour |
| **Exponential** | Waiting time between events | Time to the next ticket |
| **Lognormal** | Positive and skewed, a long right tail | Spend, income |
| **Beta** | A proportion you're uncertain about | A conversion rate, in Bayes |

**Central limit theorem:** averages of independent samples with finite variance tend towards a normal distribution as n grows, with
standard error σ/√n. That's why so many tests work on non-normal data.

**Common answer:** "n ≥ 30 is enough." **Honest nuance:** it depends on the data's shape. On the course's simulated zero-inflated
lognormal spend, 95% intervals covered about 56% of the time at n = 30, and about 83% at n = 300. A large sample also doesn't fix bias.

**Small-n extremes.** Small groups fill both the top and bottom of any ranking, because variance scales with 1/n. Before saying "the
top regions are all small", check whether the bottom ones are too.

Course: [distributions and sampling](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md),
[probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md).

## 2. Confidence intervals

An interval says how far off an estimate could plausibly be. Report it with every number.

**Common answer:** "a 95% chance the true value is in this interval." **What it means:** the *procedure* captures the true value 95% of
the time across repeated samples. This one interval either contains it or doesn't. Interviewers do check this. The reading most people
want is what a Bayesian credible interval gives.

**The textbook formula can fail.** The Wald interval (p̂ ± 1.96·SE) breaks down for rare events. In the note, 0 successes in 50 gives
Wald [0, 0], against about [0, 0.07] for Wilson. At p = 0.02 and n = 50, Wald covered 63% of the time and Wilson 92%. For ratios such
as revenue per session, use the delta method or the bootstrap.

Course: [standard errors and intervals](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md#standard-errors-and-confidence-intervals),
[the bootstrap](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md#the-bootstrap).

## 3. Hypothesis tests and p-values

**Recipe:** state a null hypothesis (no difference), pick a test, compute how surprising your data would be if the null were true, and
compare with a threshold you set in advance.

**The p-value** is the probability of a result at least as extreme as yours, *if the null is true*.

| Wrong reading | Why it's wrong |
|---|---|
| "The chance the null is true" | It assumes the null; it can't give you its probability |
| "The chance this was a fluke" | The same mistake in other words |
| "1 − p is the chance the effect is real" | Needs a prior, which is the Bayesian question |
| "Small p means a big effect" | With five million per arm, a tiny lift becomes significant |
| "Not significant means no effect" | It may mean too little data; read the interval |

**Type I** is a false alarm, with rate α. **Type II** is a miss, with rate β. **Power** is 1 − β.

**Choosing a test:**

| Question | Test | Note |
|---|---|---|
| Two means | **Welch's t-test** | The default; doesn't assume equal variances |
| Same units measured twice | Paired t-test | In the note, p = 0.0004 paired against 0.33 unpaired on the same data |
| Two proportions | Chi-square or z-test | Fisher's exact when expected counts fall below about 5 |
| Skew or outliers | Mann-Whitney, permutation, bootstrap | Mann-Whitney asks about rank, not mean |

**Common answer:** "data's skewed, so use Mann-Whitney." **Honest nuance:** a rank test answers a different question from "did revenue per
user go up?" In the note's example with one huge spender, Welch's p moved from 0.165 to 0.506, and Mann-Whitney only from 0.125 to 0.163.
Robust, yes, but about a different quantity. Decide what you're asking first.

Course: [the recipe](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md#the-recipe),
[choosing the test](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md#choosing-the-test).

## 4. Power and sample size

**Power** is the chance of detecting an effect of a given size if it's there. Set the sample size before you start.

**Rule of thumb** for α = 0.05 and power 0.8: **n ≈ 16σ²/δ² per arm**, where δ is the smallest effect worth detecting (the MDE) and
σ² = p(1 − p) for a proportion.

Worked: 5% baseline, looking for 5.5%. σ² ≈ 0.0475, δ = 0.005, so n ≈ 16 × 0.0475 / 0.000025 ≈ 30,400 per arm by this rule with the
baseline variance. The exact calculation in the course gives 62,461 in total, about 31,200 per arm.

How the course's numbers move:

- Halve the MDE: 4 times the sample.
- Power from 0.8 to 0.9: 1.34 times.
- α from 0.05 to 0.01: 1.49 times.
- A 99/1 split takes about 25 times as long as 50/50.

**Rare events cost more.** In one note, the same 20% cut needed 1,284 per arm at a 22% rate and 11,452 at 3%. Count events, not rows.
**Underpowered wins exaggerate:** at 17% power in the note, significant estimates averaged 2.5 times the truth (the winner's curse).

**MDE nuance:** "the smallest effect worth detecting" should come from the business, not be reverse-engineered from the traffic you have.

Course: [how many users](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md#how-many-users),
[power, the estimation view](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md#power-and-sample-size-the-estimation-view),
[significant results exaggerate](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md#significant-results-exaggerate).

## 5. Regression and GLMs

Linear regression fits an outcome as a weighted sum of inputs. A coefficient is the change in the outcome per unit of that input,
holding the others fixed. **A t-test is a regression** on one treatment dummy, which is why adding a pre-period covariate shrinks the
standard error (0.343 to 0.287 in the note, at R² 30%).

**GLMs** keep the idea and change the link and the outcome's distribution:

| Outcome | Model | Link | Reading a coefficient |
|---|---|---|---|
| Continuous | Linear | Identity | Units of the outcome |
| Yes or no | Logistic | Logit | Multiplies the odds by e^β |
| Count | Poisson, or negative binomial if overdispersed | Log | Multiplies the rate by e^β |

A logistic coefficient of 0.4 multiplies the odds by 1.49, but that means about 1 point at a 2% base rate and about 10 points at 50%. Say
which you mean.

**Pitfalls interviewers like:**

- **Correlation isn't causation.** Regression only adjusts for what you measured, and adjusting for the wrong thing (a "bad control")
  adds bias.
- **Multicollinearity** inflates standard errors but doesn't bias estimates, so predictions can still be fine.
- **Clustered data.** If you randomised by city, cluster standard errors by city. In the note, naive errors called a null effect
  significant more than a quarter of the time. A handful of cities still isn't enough.
- **Prediction versus explanation** are different goals, with different checks.

Course: [regression and GLMs](../../../../data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md),
[logistic regression](../../../../data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md#logistic-regression),
[bad controls](../../../../data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation.md#bad-controls).

## 6. A/B test design

Randomly show two versions, so that the only systematic difference is the change. Go through these in order, and you have a strong answer
to any "how would you test this?":

1. **Decision and metric.** One primary metric, plus guardrails such as latency and refunds.
2. **MDE.** The smallest change worth shipping.
3. **Sample size and duration.** Run whole weeks, because weekdays differ.
4. **Unit of randomisation.** Usually the user. Assign by hashing with a per-experiment salt, so that a user stays in one arm and
   experiments stay independent.
5. **Unit of analysis must match.** Analysing pageviews when you randomised users roughly doubled the false positive rate in the note.
6. **Run to the planned N.** Check for **sample ratio mismatch** first. If a 50/50 test comes out at 50.4/49.6 on 2 million users, p is
   about 10⁻²⁹, and something's broken. Use a threshold of about p < 0.001, find the cause, and don't reweight.
7. **Report the interval against the MDE.** "+0.64 points, CI [+0.34, +0.95]" says more than "significant". An interval that straddles
   the MDE needs a judgment call, and not a yes or no from the p-value alone.

**Other trust checks.** An **A/A test** should give roughly uniform p-values. **Novelty and primacy effects** make an early lift or dip fade.
**Post-assignment segments** can be biased if the treatment affects who lands in the segment.

Course: [A/B testing](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md),
[checking the assignment](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md#checking-the-assignment),
[metrics and KPI design](../../../../data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design.md).

## 7. CUPED

Much of the variation between users existed before your test. CUPED removes the part you can predict from pre-experiment behaviour,
so the same traffic detects smaller effects.

Y_adj = Y − θ(X − X̄), with θ = cov(X, Y) / var(X), where X is the same metric before the experiment.

Variance falls by ρ², the squared correlation between X and Y. So ρ = 0.7 about halves it, and ρ = 0.3 removes only 9%. Deng et al. report
about 50% on Bing. It's equivalent to adding the covariate in a regression (ANCOVA).

**Pitfalls:** X must be strictly pre-exposure, or you subtract some of the treatment effect. New users have no history, so handle them
separately. CUPED reduces noise; it doesn't remove bias from a broken experiment.

Course: [variance reduction: CUPED](../../../../data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md#variance-reduction-cuped).

## 8. Cluster randomisation and design effect

Sometimes you must randomise groups: cities, stores, classrooms. Reasons include marketplace effects and spillover between users, or a
change that can only be switched on for a whole area. People in a cluster resemble each other, so they carry less information than the
headcount suggests.

**Design effect:** DE = 1 + (m − 1)ρ, where m is the cluster size and ρ is the intra-cluster correlation. Effective sample size = n / DE.

Worked: 200,000 users in 1,000 clusters gives m = 200. With ρ = 0.02, DE = 1 + 199 × 0.02 = 4.98, so about 40,000 effective users. Small
ρ, large effect, because m is big. At DE 11, a million users carry about 91,000.

**What goes wrong without it.** Interference breaks the assumption that one user's arm doesn't affect another. In the note's simulation, a
user-level test claimed +30% when the real lift was +19%. Designs include cluster randomisation, switchbacks, two-sided randomisation and
holdouts. Analyse at the level you randomised.

Course: [when users affect each other](../../../../data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md#when-users-affect-each-other).

## 9. Peeking

Checking a running test and stopping at the first p < 0.05 inflates false positives, because you get many chances for noise to cross the
line. In the course's simulations, twenty looks took the false positive rate to about 25%.

**Fixes:** commit to a fixed N, or use a method built for looking.

- **Group-sequential:** planned looks with stricter thresholds. Over five looks, Pocock's boundary is 2.42 at every look. O'Brien-Fleming is
  strict early and has a final value of 2.03, near the usual 1.96.
- **Always-valid (mSPRT):** look whenever you like, in return for less power at a fixed N.

Peeking for *harm* is fine if the stopping rule is planned. Stopping early also tends to overstate the effect.

Course: [looking early, safely](../../../../data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md#looking-early-safely),
[running the test](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md#running-the-test).

## 10. Multiple comparisons and Simpson's paradox

**Multiple comparisons.** Test 20 true nulls at 0.05, and you have a 64% chance of at least one false positive. More metrics, segments and
variants all count.

| Method | Controls | When |
|---|---|---|
| **Bonferroni** | Chance of any false positive | Few tests; simple but conservative. α/m |
| **Holm** | The same, with more power | Always prefer it over Bonferroni |
| **Benjamini-Hochberg** | Share of false discoveries among hits (FDR) | Many tests, where some false positives are acceptable |

In the note's 100-test example, no correction gave 3 false hits out of 11, Bonferroni and Holm gave 5 true and 0 false, and BH gave 7 true and
0 false. The simplest fix is one pre-registered primary metric, with the others labelled exploratory.

**Simpson's paradox.** A trend in every subgroup reverses when pooled, because group sizes differ. From the note:

| | Control | Treatment |
|---|---|---|
| Mild cases | 90/100 = 90% | 39/40 = 97.5% |
| Severe cases | 30/100 = 30% | 80/160 = 50% |
| **Overall** | **60.0%** | **59.5%** |

Treatment wins in both groups and loses overall, because it got more severe cases.

**Common answer:** "always stratify." **Honest nuance:** the causal story decides, not the arithmetic. If severity is a confounder, stratify. If
the subgroup is itself affected by the treatment, the pooled figure is the right one. In A/B tests, Simpson often appears when the traffic split
changes during a ramp, so hold the split constant or analyse by period.

Course: [multiple comparisons](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md#multiple-comparisons),
[Simpson's paradox](../../../../data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation.md#simpsons-paradox).

## 11. Partial pooling and multilevel models

Say you're estimating conversion for 500 stores, some with only a handful of visits. You could treat them all as one (**complete pooling**,
which ignores real differences) or each separately (**no pooling**, which gives wild estimates for small stores). **Partial pooling** sits
between: each store's estimate is pulled towards the overall average, and small stores are pulled more. A multilevel (hierarchical) model
estimates how strong that pull should be from the data itself, using how much stores really vary.

It's the principled version of "don't trust the small groups", and it's why such models are popular for many small segments.

**The course has no chapter on multilevel models yet**, so learn this from a textbook if a role needs it. The nearest related material is
[shrinkage on small groups](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md#the-small-n-trap) and
[shrinkage for the winner's curse](../../../../data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits.md#the-winners-curse-shrinkage-as-a-prior-on-experiments),
both of which use a fixed or simple prior rather than a full multilevel model.

## 12. Bayesian A/B testing

Start with a prior belief about each arm's rate and update it with the data. For conversions, a Beta prior and binomial data give a Beta
posterior in one line, with no sampler. You can then state directly:

- **P(B > A):** the chance B is better.
- **P(lift > x):** the chance the lift is big enough to matter.
- **Expected loss:** E[max(p_A − p_B, 0)], what you'd give up on average by shipping B if it's worse.

In the note's Larkspur test (2,079/42,141 against 2,335/41,859), P(B better) is above 0.9999, P(lift > 0.5 points) is 0.83, and the credible
interval of +0.34 to +0.95 matches the frequentist one. With plenty of data and weak priors the two usually agree. What differs is the
statement you can make.

**Common answer:** "Bayesian tests are immune to peeking." **Honest nuance:** not if you decide with a fixed P(B > A) rule. In the note's
simulation, a P(B > A) > 0.95 rule shipped a no-effect change 4.7% of the time when checked once, and 23.8% when checked daily. An expected-loss
rule behaves differently. Checked daily it shipped 59% of no-effect changes, which costs nothing by what the rule promises, but it also shipped a
harmful −0.5 point change 14.3% of the time. Waiting until day 14 before applying it cut that to 3.8%. These figures depend on the setup. Use the
same prior for both arms, and be wary of early reads: on day one, a flat prior reported a 1.77-point lift, nearly three times what the whole test found.

Course: [Bayesian A/B testing](../../../../data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing.md),
[is peeking safe?](../../../../data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing.md#is-peeking-safe),
[credible intervals](../../../../data-analytics/04-bayesian-analysis/notes/01-bayesian-inference.md#what-a-credible-interval-buys-you).

## 13. Question bank (answer sketches)

- *"Explain a p-value to a product manager."* — If the change did nothing, this is how often we'd see a difference this big by chance. It isn't
  the chance the change works.
- *"The test came back not significant. Ship or kill?"* — Read the interval against the MDE. If it excludes anything worth having, kill it. If
  it's wide, you don't know yet.
- *"Your test is significant at p = 0.04 on one of eight metrics."* — Was it the pre-registered primary? If not, correct for multiple tests and
  rerun before believing it.
- *"Treatment has 51% of users in a 50/50 test."* — Run the SRM test. If it fails, stop reading the results, and look for bugs in assignment or
  logging.
- *"PM wants to check daily."* — Show a dashboard for harm, but fix the decision rule: fixed N or a sequential design.
- *"How would you speed up experiments?"* — CUPED, a sensitive proxy metric, a 50/50 split, and fewer simultaneous variants, before asking for more
  traffic.
- *"We can't randomise users because drivers are shared."* — Cluster or switchback design, with the sample size adjusted for the design effect and
  analysis at the cluster level. See also the [quasi-experiments](../../../../data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation.md#when-you-cannot-randomise).
- *"Revenue per user is very skewed. What test?"* — Welch with a large sample, or a bootstrap; check coverage. Don't switch to Mann-Whitney unless
  rank is your question.
- *"Why might a significant win fail to replicate?"* — Low power and the winner's curse, peeking, many metrics, novelty.
- *"Frequentist or Bayesian?"* — With enough data they usually agree. Bayesian gives a statement a PM can use and a natural way to decide on loss,
  but needs a prior. Follow the team's platform and be able to read both.
- *"What's the difference between a confidence and a credible interval?"* — See [§2](#2-confidence-intervals).

For drilling, use [technical-questions](../../rounds/technical-questions/README.md) and its
[study guide](../../rounds/technical-questions/study-guide.md) for the 60-second-plus-one-level method. The ML side is in the
[foundations guide](../1-foundations/interview-guide.md), and Q14 there is the short spoken overview of this pillar.

## Sources

- Course: the notes linked in each section of [learn-ai-engineering](../../../../README.md), read November 2026, in `data-analytics/02-probability-and-statistics/`, `03-experimentation-and-causality/` and `04-bayesian-analysis/`. Worked figures belong to those notes.
- Named methods cited through those notes: Deng et al. 2013 (CUPED), Pocock and O'Brien-Fleming (group-sequential), Benjamini-Hochberg (FDR), Stucchio (expected loss).
