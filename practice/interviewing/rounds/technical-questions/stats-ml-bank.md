# Probability, Statistics and ML Screen Bank

Short-answer questions and worked probability problems for a first-round screen on maths, probability,
statistics and basic machine learning. The one-page formulas are in [stats-ml-cheat-sheet.md](stats-ml-cheat-sheet.md).

**Three levels**: this bank is the middle one. Go through the topics once at each level.

1. Recognise: the multiple-choice sections L to S of [mcq-bank.md](mcq-bank.md).
2. Recall: this bank, answered out loud with the answer covered.
3. Calculate: [stats-ml-problems.md](stats-ml-problems.md), 38 problems with one numeric answer each.

**How to use**: cover the answer, say yours out loud, then compare. Each entry has a short **Answer** (what to
say in 30 to 60 seconds), sometimes a **Working** block (the steps to write on a whiteboard), and a **Deeper**
line that names the note to reread and the lab to run. Section P is the problem-solving set: do those with a
pen, because the interviewer grades the setup as much as the number.

| Section | Topic | Questions |
|---|---|---|
| D | Distributions and random variables | 14 |
| P | Probability problems, worked | 18 |
| S | Estimation, bias and significance | 16 |
| A | A/B testing | 13 |
| M | Machine learning models | 20 |
| B | Bayesian inference | 5 |
| C | Markov chains | 4 |
| U | Unsupervised learning | 7 |
| N | Neural networks | 9 |
| R | Retrieval, ranking and recommenders | 10 |
| T | Features, tuning and time series | 7 |
| K | Metrics and product questions | 4 |
| **Total** | | **127** |

Sections D to M are the core of a first-round screen: learn those first. Sections B to K cover the wider
reading lists that such screens point to (Bayesian inference, unsupervised learning, neural networks,
information retrieval, recommenders, time series and product metrics).

---

## D. Distributions and random variables

### D1. What is a random variable, and how do discrete and continuous ones differ?

**Answer:** A random variable is a function that assigns a number to each outcome of a random process. A discrete one takes countable values and has a probability mass function whose values sum to 1. A continuous one has a density that integrates to 1: any single point has probability 0, probabilities are areas under the curve, and the density itself can be above 1.

**Deeper:** [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md)

### D2. Give the mean and variance of a Bernoulli(p) variable. When is the variance largest?

**Answer:** Mean p, variance p(1 − p). The variance peaks at p = 0.5, where it is 0.25, and falls to 0 as p goes to 0 or 1. This is why a conversion rate near 50% needs the most data per unit of precision in absolute terms.

**Deeper:** [distributions and sampling](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md) · Lab: [distributions_and_estimators.py](../../../../data-analytics/02-probability-and-statistics/practice/distributions_and_estimators.py)

### D3. What does a Binomial(n, p) variable count, and what are its PMF, mean and variance?

**Answer:** The number of successes in n independent trials that each succeed with probability p. P(X = k) = C(n, k) p^k (1 − p)^(n − k). Mean np, variance np(1 − p). It is a sum of n independent Bernoulli(p) variables, which is where the mean and variance come from.

**Deeper:** [distributions and sampling](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md) · Lab: [distributions_and_estimators.py](../../../../data-analytics/02-probability-and-statistics/practice/distributions_and_estimators.py)

### D4. When is the Poisson distribution the right model, and what are its PMF, mean and variance?

**Answer:** For a count of events in a fixed interval when events happen independently at a constant average rate: arrivals per hour, defects per batch. P(X = k) = e^(−λ) λ^k / k!. Mean and variance are both λ. If the rate is r per unit time, the count over time t is Poisson(rt).

**Deeper:** [Poisson GLMs](../../../../data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms.md) · Lab: [distributions_and_estimators.py](../../../../data-analytics/02-probability-and-statistics/practice/distributions_and_estimators.py)

### D5. When can a Binomial be approximated by a Poisson, and when by a Normal?

**Answer:** Poisson when n is large and p is small, with λ = np (a common rule is n ≥ 20 and p ≤ 0.05). Normal when np and n(1 − p) are both at least about 10, with mean np and variance np(1 − p). Rare events go to Poisson; many trials with a moderate p go to Normal.

**Deeper:** Lab: [distributions_and_estimators.py](../../../../data-analytics/02-probability-and-statistics/practice/distributions_and_estimators.py), part 2

### D6. State the 68-95-99.7 rule and how you standardise a Normal variable.

**Answer:** For a Normal distribution about 68% of values fall within 1 standard deviation of the mean, 95% within 2 (1.96 exactly) and 99.7% within 3. Standardise with z = (x − μ) / σ, which is Normal(0, 1). A sum of independent Normals is Normal, with the means adding and the variances adding.

**Deeper:** [distributions and sampling](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md)

### D7. State the Central Limit Theorem. What does it not say?

**Answer:** The mean of n independent draws from a distribution with finite variance is approximately Normal(μ, σ²/n) for large n, whatever the shape of the original distribution. It does not say the data become Normal: the raw values stay as skewed as they were. It also fails for infinite-variance tails and converges slowly for very skewed data.

**Deeper:** [distributions and sampling](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md) · Lab: [distributions_and_estimators.py](../../../../data-analytics/02-probability-and-statistics/practice/distributions_and_estimators.py), part 3

### D8. What is the difference between the Law of Large Numbers and the Central Limit Theorem?

**Answer:** The Law of Large Numbers says the sample mean converges to the true mean as n grows. The Central Limit Theorem says how the remaining error is distributed: approximately Normal with standard deviation σ/√n. One gives the destination, the other the size and shape of the error on the way there.

**Deeper:** [distributions and sampling](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md)

### D9. Which rules for expectation and variance need independence, and which do not?

**Answer:** E[aX + bY] = aE[X] + bE[Y] always: linearity of expectation needs no independence. Var(aX + b) = a²Var(X). Var(X + Y) = Var(X) + Var(Y) + 2Cov(X, Y), so variances add only when X and Y are uncorrelated. E[XY] = E[X]E[Y] also needs independence (or at least zero correlation).

**Deeper:** [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md)

### D10. What is the difference between a standard deviation and a standard error?

**Answer:** The standard deviation describes the spread of individual data points. The standard error is the standard deviation of an estimate across repeated samples; for a mean it is σ/√n. More data leaves the standard deviation about the same and shrinks the standard error, and quadrupling n halves it.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md)

### D11. What do the Geometric and Exponential distributions model, and what property do they share?

**Answer:** Geometric(p) counts trials up to and including the first success, with mean 1/p. Exponential(λ) is the waiting time between events of a Poisson process, with mean 1/λ. Both are memoryless: having already waited tells you nothing about how much longer you will wait.

**Deeper:** Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### D12. Your count data have a variance far above the mean. What does that mean for a Poisson model?

**Answer:** The data are overdispersed, so the Poisson assumption that variance equals the mean is wrong. Standard errors will be too small and tests too confident. Use a negative binomial model, or a quasi-Poisson fit that scales the standard errors, and look for the cause: unequal rates across users or clustered events.

**Deeper:** [Poisson GLMs](../../../../data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms.md)

### D13. Are uncorrelated variables independent?

**Answer:** No. Independence implies zero correlation, but not the reverse. Correlation measures only linear association. Take X standard Normal and Y = X²: Y is fully determined by X, yet their correlation is 0. The exception is jointly Normal variables, where uncorrelated does imply independent.

**Deeper:** [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md)

### D14. Define covariance and correlation.

**Answer:** Cov(X, Y) = E[(X − μx)(Y − μy)], which is positive when the two move together and depends on their units. Correlation divides by both standard deviations, so it is unit-free and lies between −1 and 1. It captures linear association only and is sensitive to outliers.

**Deeper:** [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md)

---

## P. Probability problems, worked

### P1. A condition affects 1% of people. A test catches 95% of cases and gives a false positive for 5% of healthy people. You test positive. What is the chance you have it?

**Answer:** About 16%. Bayes' rule: 0.01 × 0.95 / (0.01 × 0.95 + 0.99 × 0.05) = 0.0095 / 0.059 = 0.161. The healthy group is 99 times larger, so its 5% of false positives outnumber the true positives five to one.

**Working:** Use counts. Of 10,000 people, 100 have it and 95 test positive. Of the 9,900 without it, 495 test positive. Positives: 590. Share that are real: 95 / 590 = 16.1%.

**Deeper:** [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md) · Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P2. 0.1% of transactions are fraud. A model flags 99% of fraud and 1% of legitimate transactions. What share of flagged transactions are fraud?

**Answer:** About 9%. 0.001 × 0.99 / (0.001 × 0.99 + 0.999 × 0.01) = 0.00099 / 0.01098 = 0.090. A model that is 99% accurate on both classes still has 9% precision at this base rate, which is why fraud models are judged on precision and recall, not accuracy.

**Working:** Of 100,000 transactions, 100 are fraud and 99 get flagged. Of the 99,900 legitimate ones, 999 get flagged. Precision: 99 / 1,098 = 9.0%.

**Deeper:** [thresholds, PR and ROC](../../../../data-science/01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration.md) · Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P3. How many flips of a fair coin do you expect before the first head? Before two heads in a row?

**Answer:** 2 for the first head (Geometric with p = 0.5, mean 1/p). 6 for two heads in a row.

**Working:** Let E be the expected flips from the start and E1 the expected flips once you hold one head. From the start: E = 1 + ½E1 + ½E. With one head: E1 = 1 + ½(0) + ½E. Substitute: E1 = 1 + E/2, so E = 1 + ½ + E/4 + E/2, which gives E = 6. The method, conditioning on the first step and writing an equation per state, is what the interviewer wants to see.

**Deeper:** Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P4. What is the probability of at least one six in four rolls of a die?

**Answer:** 1 − (5/6)⁴ = 1 − 625/1296 = 0.518. "At least one" is the cue to compute the complement: the chance of no six on every roll.

**Deeper:** Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P5. How many people do you need in a room for a better than even chance that two share a birthday?

**Answer:** 23, which gives 50.7%. Compute the complement: the chance all are different is (365/365)(364/365)…(343/365). It is low because 23 people form 253 pairs, and each pair is a chance to match.

**Working:** Approximation: P(no match) ≈ exp(−n(n − 1) / (2 × 365)). Setting that to 0.5 gives n(n − 1) ≈ 506, so n ≈ 23.

**Deeper:** Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P6. A family has two children and at least one is a boy. What is the chance both are boys? What if you are told the older one is a boy?

**Answer:** 1/3, then 1/2. The four equally likely families are BB, BG, GB, GG. "At least one boy" removes GG and leaves three, one of which is BB. "The older is a boy" leaves BB and BG, so 1/2. The answer depends on exactly what was conditioned on.

**Deeper:** [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md) · Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P7. How many rolls of a die do you expect before every face has appeared?

**Answer:** 14.7. This is the coupon collector problem: 6 × (1 + 1/2 + 1/3 + 1/4 + 1/5 + 1/6).

**Working:** Split the wait into stages. With k faces already seen, a new face appears with probability (6 − k)/6, so that stage takes 6/(6 − k) rolls on average. Add the stages: 6/6 + 6/5 + 6/4 + 6/3 + 6/2 + 6/1 = 14.7. Linearity of expectation lets you add them.

**Deeper:** Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P8. You have a coin with an unknown bias. How do you produce a fair coin flip from it?

**Answer:** Flip twice. Heads then tails counts as heads, tails then heads counts as tails, and on two equal flips you start again. Both mixed orders have probability p(1 − p), so the two outcomes are equally likely whatever p is. It takes 1 / (p(1 − p)) flips on average.

**Deeper:** Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P9. Support tickets arrive at an average of 3 an hour. What is the chance of none in the next 20 minutes? Of two or more in an hour?

**Answer:** 0.368 and 0.801. Over 20 minutes the rate is λ = 1, so P(0) = e^(−1) = 0.368. Over an hour λ = 3, so P(≥ 2) = 1 − P(0) − P(1) = 1 − e^(−3)(1 + 3) = 0.801.

**Working:** First scale the rate to the interval, then use P(k) = e^(−λ) λ^k / k!. For "at least" questions, subtract the small cases from 1.

**Deeper:** Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P10. You flip a fair coin 10 times. What is the chance of exactly 5 heads? Of 8 or more?

**Answer:** 0.246 and 0.055. Exactly 5: C(10, 5) / 2¹⁰ = 252 / 1024. Eight or more: (45 + 10 + 1) / 1024 = 56 / 1024. The most likely single outcome still happens under a quarter of the time.

**Deeper:** Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P11. A coin gives 60 heads in 100 flips. Is it fair?

**Answer:** Borderline. Under a fair coin the count has mean 50 and standard deviation √(100 × 0.5 × 0.5) = 5, so 60 is 2 standard deviations out: z = 2, two-sided p ≈ 0.046. Just significant at 5%, not at 1%. I would say the evidence is weak and ask for more flips.

**Working:** State H0: p = 0.5. Use the Normal approximation to the Binomial (np and n(1 − p) are both 50). z = (60 − 50) / 5 = 2.

**Deeper:** [hypothesis testing](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md)

### P12. In the Monty Hall game, should you switch doors?

**Answer:** Yes. Switching wins 2/3 of the time. Your first pick is right with probability 1/3. The host, who knows where the car is, always opens a goat door, so whenever your first pick was wrong (2/3 of the time) the other closed door has the car.

**Deeper:** Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P13. You draw two cards from a shuffled deck. What is the chance both are aces?

**Answer:** 4/52 × 3/51 = 1/221, about 0.45%. The draws are without replacement, so the second probability is conditional on the first: three aces left in 51 cards.

**Deeper:** [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md)

### P14. A stick is broken at a uniformly random point. What is the expected length of the longer piece?

**Answer:** 3/4 of the stick. The longer piece is max(U, 1 − U), which is uniform between 1/2 and 1, so its mean is 3/4. The shorter piece averages 1/4.

**Deeper:** Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P15. You roll a die and win its face value. You may reroll once, but must keep the second roll. What is the game worth?

**Answer:** 4.25. A reroll is worth 3.5 on average, so keep a 4, 5 or 6 and reroll a 1, 2 or 3. Value: ½ × 5 (the average of 4, 5, 6) + ½ × 3.5 = 4.25.

**Working:** Work backwards from the last decision: value the final roll first (3.5), then compare each first roll against it. With two rerolls the threshold rises: reroll anything below 4.25, so keep only 5 and 6.

**Deeper:** Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P16. For the sum of two dice, give P(sum = 7), the expected sum and the variance.

**Answer:** P(7) = 6/36 = 1/6, the most likely sum. The expected sum is 3.5 + 3.5 = 7. One die has variance 35/12, and the dice are independent, so the variance of the sum is 35/6, about 5.83.

**Deeper:** [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md)

### P17. X and Y are independent Uniform(0, 1). What is the expected value of the larger one?

**Answer:** 2/3, and the smaller one averages 1/3. P(max ≤ t) = t², so the density of the max is 2t and its mean is the integral of 2t² from 0 to 1, which is 2/3. In general the largest of n uniforms averages n / (n + 1).

**Deeper:** Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)

### P18. How many people must a poll survey for a margin of error of ±3 points at 95% confidence?

**Answer:** About 1,070. The margin is 1.96 × √(p(1 − p)/n). Use the worst case p = 0.5: n = 1.96² × 0.25 / 0.03² = 1,067. The population size does not appear, and halving the margin needs four times the sample.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md)

---

## S. Estimation, bias and significance

### S1. What does it mean for an estimator to be biased? Give an example.

**Answer:** Bias is the gap between an estimator's average over repeated samples and the true value: E[estimate] − truth. The sample variance that divides by n is biased low by the factor (n − 1)/n, because deviations are measured from the sample mean, which sits closer to the data than the true mean does. Dividing by n − 1 removes the bias.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md) · Lab: [distributions_and_estimators.py](../../../../data-analytics/02-probability-and-statistics/practice/distributions_and_estimators.py), part 4

### S2. How do the bias and variance of an estimator combine, and is an unbiased estimator always better?

**Answer:** Mean squared error = bias² + variance. An unbiased estimator is not always best: a slightly biased one with much lower variance has lower error. Ridge regression and shrinkage estimators are biased on purpose for this reason.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md) · Lab: [distributions_and_estimators.py](../../../../data-analytics/02-probability-and-statistics/practice/distributions_and_estimators.py), part 4

### S3. What is the difference between an unbiased and a consistent estimator?

**Answer:** Unbiased is a property at a fixed sample size: the average of the estimator equals the truth. Consistent is a property as n grows: the estimator converges to the truth. Variance divided by n is biased but consistent. Using only the first observation as an estimate of the mean is unbiased but not consistent.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md)

### S4. Name the main kinds of bias in how data is collected. Does more data fix them?

**Answer:** Selection bias (the sample differs from the population), survivorship bias (only those who made it through are observed), non-response bias, measurement bias and confounding. More data does not fix any of them: it shrinks variance and leaves the bias, so you get a tighter interval around the wrong number.

**Deeper:** [distributions and sampling](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md)

### S5. What is a p-value? What is it not?

**Answer:** The probability of seeing data at least as extreme as what was observed, assuming the null hypothesis is true. It is not the probability that the null is true, not the probability the result is due to chance, and it says nothing about the size of the effect.

**Deeper:** [hypothesis testing](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md)

### S6. Define Type I error, Type II error and power.

**Answer:** A Type I error rejects a true null (a false positive); its rate is α, usually 5%. A Type II error fails to reject a false null (a missed effect); its rate is β. Power is 1 − β, the chance of detecting an effect of a given size, usually planned at 80%.

**Deeper:** [hypothesis testing](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md)

### S7. What does a 95% confidence interval mean?

**Answer:** If the experiment were repeated many times, 95% of the intervals built this way would contain the true value. It is a statement about the procedure. It is not a 95% probability that the true value lies in this particular interval; that reading belongs to a Bayesian credible interval.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md)

### S8. What is the difference between statistical and practical significance?

**Answer:** Statistical significance says the effect is unlikely to be zero. Practical significance says it is large enough to matter. With millions of users a 0.01 point lift can have a tiny p-value and still not pay for the engineering. Report the effect size and its interval, and compare it with the smallest effect worth acting on.

**Deeper:** [hypothesis testing](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md)

### S9. Which test would you use to compare two means, two proportions, counts across categories, or skewed data?

**Answer:** Two means: Welch's t-test. Two proportions with large samples: a two-proportion z-test. Counts across categories: chi-square. Skewed or ordinal data with small samples: Mann-Whitney, or a bootstrap. Measurements on the same units before and after: a paired test.

**Deeper:** [hypothesis testing](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md)

### S10. You run 20 tests at α = 0.05 and all nulls are true. What is the chance of at least one false positive, and how do you control it?

**Answer:** 1 − 0.95²⁰ = 64%. Bonferroni tests each at α/m and controls the chance of any false positive, at a cost in power. Benjamini-Hochberg controls the false discovery rate instead and keeps more power when many metrics are tested.

**Deeper:** [hypothesis testing](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md)

### S11. What increases the power of a test?

**Answer:** A larger sample, a larger true effect, lower variance in the metric, and a higher α. Variance can be cut without more users by using a less noisy metric or adjusting for pre-experiment data. Power is fixed before the test: computing it afterwards from the observed effect adds nothing to the p-value.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md)

### S12. What is maximum likelihood estimation? Give the MLE for a Bernoulli, a Poisson and a Normal.

**Answer:** Choose the parameter values under which the observed data are most probable. Bernoulli: the sample proportion. Poisson: the sample mean. Normal: the sample mean, and the variance with divisor n, which is biased. In practice you maximise the log-likelihood, which turns products into sums.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md)

### S13. Two variables are strongly correlated. What could explain it other than one causing the other?

**Answer:** A confounder that drives both, reverse causation, selection in how the data was collected, or chance. Simpson's paradox is the sharp version: a trend in every subgroup can reverse in the pooled data when group sizes differ. Randomisation is what removes confounding.

**Deeper:** [correlation and causation](../../../../data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation.md)

### S14. What is the bootstrap and when would you use it?

**Answer:** Resample the data with replacement many times, recompute the statistic each time, and use the spread of those values as the sampling distribution. It gives a standard error or interval for statistics with no simple formula, such as a median or a ratio. It needs resampling at the level of the independent unit, and it fails for extremes like the maximum.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md)

### S15. Does a t-test require the data to be Normal?

**Answer:** It requires the sample mean to be approximately Normal, not the raw data. With a large sample the Central Limit Theorem delivers that even for skewed data. The test is unreliable for small samples with heavy tails or outliers, where a rank test or bootstrap is safer.

**Deeper:** [hypothesis testing](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md)

### S16. When is a one-sided test appropriate?

**Answer:** Only when an effect in the other direction would lead to the same decision as no effect, and the direction was fixed before seeing the data. It gives more power for the same α. Choosing one-sided after looking at the data halves the p-value dishonestly.

**Deeper:** [hypothesis testing](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md)

---

## A. A/B testing

### A1. Walk me through designing an A/B test.

**Answer:** State the hypothesis, one primary metric and the guardrail metrics. Pick the randomisation unit, usually the user. Set α, power and the minimum effect worth detecting, and compute the sample size and duration from them (whole weeks). Randomise, check the split, run to the planned size without stopping early, then decide from the effect and its confidence interval.

**Deeper:** [A/B testing](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md) · Lab: [ab_test_from_scratch.py](../../../../data-analytics/03-experimentation-and-causality/practice/ab_test_from_scratch.py)

### A2. The baseline conversion is 10% and you want to detect a lift of 1 point. Roughly how many users per arm?

**Answer:** About 14,400 with the shortcut n ≈ 16 p(1 − p) / δ² for α = 0.05 two-sided and 80% power: 16 × 0.09 / 0.0001. The exact formula gives 14,749.

**Working:** The 16 comes from 2 × (1.96 + 0.84)² ≈ 15.7. The 2 is there because the difference of two rates has twice the variance of one.

**Deeper:** [A/B testing](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md) · Lab: [ab_test_from_scratch.py](../../../../data-analytics/03-experimentation-and-causality/practice/ab_test_from_scratch.py), part 2

### A3. What happens to the required sample size if you halve the minimum detectable effect?

**Answer:** It quadruples, because the sample size is proportional to 1/δ². This is the main cost lever in experiment design: detecting a 0.5 point lift takes four times the traffic of a 1 point lift.

**Deeper:** [A/B testing](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md) · Lab: [ab_test_from_scratch.py](../../../../data-analytics/03-experimentation-and-causality/practice/ab_test_from_scratch.py), part 2

### A4. Control converts 1,000 of 10,000 users and treatment 1,100 of 10,000. Is the difference significant?

**Answer:** Yes at 5%: z = 2.31, p = 0.021, and the 95% interval for the lift is about 0.15 to 1.85 points. The lift is real but its size is uncertain.

**Working:** Pooled rate 2,100 / 20,000 = 0.105. Standard error = √(0.105 × 0.895 × 2 / 10,000) = 0.00434. z = 0.01 / 0.00434 = 2.31. Interval: 0.01 ± 1.96 × 0.00434.

**Deeper:** [A/B testing](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md) · Lab: [ab_test_from_scratch.py](../../../../data-analytics/03-experimentation-and-causality/practice/ab_test_from_scratch.py), part 1

### A5. Why is it a problem to check an A/B test every day and stop when it reaches significance?

**Answer:** Each look is another chance for noise to cross the threshold, so the false positive rate climbs well above 5%: about 14% with 5 looks and 25% with 20 in a simulation of tests with no true effect. Fix the sample size in advance and look once, or use a sequential design that spends α across the looks.

**Deeper:** [A/B testing](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md) · Lab: [ab_test_from_scratch.py](../../../../data-analytics/03-experimentation-and-causality/practice/ab_test_from_scratch.py), part 5

### A6. What is a sample ratio mismatch and what do you do about one?

**Answer:** The observed split between arms differs from the designed one by more than chance allows, tested with a chi-square test (p below 0.001 is the usual alarm). It means assignment or logging is broken, so the arms are no longer comparable. Do not read the metrics: find the cause and rerun.

**Deeper:** [A/B testing](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md) · Lab: [ab_test_from_scratch.py](../../../../data-analytics/03-experimentation-and-causality/practice/ab_test_from_scratch.py), part 6

### A7. Your test is not significant. What do you conclude?

**Answer:** Not that there is no effect. Look at the confidence interval. If it excludes the smallest effect worth acting on, the change does little either way. If it is wide and includes that effect, the test was underpowered and is inconclusive.

**Deeper:** [A/B testing](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md)

### A8. Users are randomised but you analyse sessions. What goes wrong?

**Answer:** Sessions from the same user are correlated, so treating them as independent understates the standard error and inflates false positives. Analyse at the randomisation unit, or correct the variance with the delta method or a bootstrap that resamples users.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md)

### A9. What are novelty and primacy effects?

**Answer:** Novelty: users engage with a change because it is new, and the lift fades. Primacy: users are slowed by a change at first, and the effect improves as they learn it. Check by plotting the effect over time and by comparing new users with existing ones, and run long enough for the effect to settle.

**Deeper:** [experimentation at scale](../../../../data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md)

### A10. When does user-level randomisation break down?

**Answer:** When one user's treatment affects another's outcome: referrals, peer-to-peer payments, marketplaces, shared inventory. The control group is contaminated and the estimate is biased. Randomise clusters instead (regions, social groups) or use switchback tests that alternate the whole market over time.

**Deeper:** [experimentation at scale](../../../../data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md)

### A11. How can you get the same power with fewer users?

**Answer:** Reduce the variance of the metric. CUPED adjusts each user's outcome by a pre-experiment covariate, usually the same metric before the test, and cuts variance by the squared correlation between the two. Stratifying, capping outliers and choosing a less noisy metric also help.

**Deeper:** [experimentation at scale](../../../../data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md)

### A12. What is a guardrail metric?

**Answer:** A metric that must not get worse while the primary metric improves: latency, error rate, refunds, complaints, unsubscribes. A test that wins on the primary metric and breaches a guardrail does not ship. Guardrails are set before the test, with thresholds.

**Deeper:** [metrics and KPI design](../../../../data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design.md)

### A13. You cannot run an A/B test. How do you estimate the effect of a change?

**Answer:** Use a quasi-experiment and state its assumption. Difference-in-differences compares the change in a treated group with the change in an untreated one and assumes parallel trends. Regression discontinuity uses a cutoff. Matching or weighting balances observed covariates and assumes no unobserved confounders.

**Deeper:** [correlation and causation](../../../../data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation.md) · [matching and weighting](../../../../data-analytics/03-experimentation-and-causality/notes/05-matching-and-weighting.md)

---

## M. Machine learning models

### M1. What are the strengths and weaknesses of linear regression?

**Answer:** Strengths: fast, interpretable coefficients, a closed-form fit, and a strong baseline. Weaknesses: it assumes a linear, additive relationship, it is sensitive to outliers, and correlated features make coefficients unstable. Inference also assumes independent errors with constant variance.

**Deeper:** [supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md)

### M2. How does logistic regression work, and when would you choose it?

**Answer:** It models the log-odds of the positive class as a linear function of the features and passes it through a sigmoid to get a probability. It is fitted by minimising log loss, which is maximum likelihood for a Bernoulli outcome. Choose it for a fast, interpretable baseline with well-calibrated probabilities. It misses interactions and non-linear effects unless you add them as features.

**Deeper:** [logistic regression](../../../../data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms.md)

### M3. How do you interpret a logistic regression coefficient?

**Answer:** A one-unit increase in the feature adds the coefficient to the log-odds, which multiplies the odds by e to the coefficient. A coefficient of 0.7 roughly doubles the odds. It is not a constant change in probability: the same shift in odds moves the probability most near 0.5 and least near 0 or 1.

**Deeper:** [logistic regression](../../../../data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms.md)

### M4. What are the strengths and weaknesses of a decision tree?

**Answer:** Strengths: readable rules, no scaling needed, handles non-linear effects and interactions, copes with mixed feature types. Weaknesses: high variance (a small change in data gives a different tree), it overfits unless depth is limited, and it cannot extrapolate beyond the training range.

**Deeper:** [supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md) · Lab: [overfit_curve.py](../../../../data-science/01-classical-ml/practice/overfit_curve.py)

### M5. Compare random forests and gradient boosting.

**Answer:** A random forest trains deep trees independently on bootstrap samples with random feature subsets and averages them, which cuts variance. Gradient boosting trains shallow trees in sequence, each fitting the errors of the ensemble so far, which cuts bias. Forests are robust with little tuning. Boosting is usually more accurate on tabular data but needs tuning of the learning rate, depth and number of trees, with early stopping.

**Deeper:** [ensembles](../../../../data-science/01-classical-ml/notes/06-ensembles.md) · Lab: [trees_vs_rounds.py](../../../../data-science/01-classical-ml/practice/trees_vs_rounds.py)

### M6. What are the strengths and weaknesses of k-nearest neighbours?

**Answer:** Strengths: no training step, no assumption about the shape of the boundary, simple to explain. Weaknesses: prediction is slow on large data, it needs scaled features, and it degrades in high dimensions where all points become roughly equally far apart. Small k gives high variance, large k gives high bias.

**Deeper:** [supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md)

### M7. Why is Naive Bayes "naive", and when does it still work?

**Answer:** It assumes features are independent given the class, which is rarely true. It still classifies well because picking the most likely class only needs the ranking of the scores to be right, not the probabilities. It is fast, works with little data and suits high-dimensional text. Its probabilities are poorly calibrated.

**Deeper:** [supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md)

### M8. What are the strengths and weaknesses of a support vector machine?

**Answer:** It finds the boundary with the largest margin, and kernels let it draw non-linear boundaries. It works well on small to medium data with many features. Weaknesses: training scales poorly beyond tens of thousands of rows, it needs scaling and tuning of C and the kernel, and it gives no probabilities without an extra calibration step.

**Deeper:** [supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md)

### M9. What is the difference between L1 and L2 regularisation?

**Answer:** Both add a penalty on coefficient size to the loss. L2 (ridge) penalises squared coefficients and shrinks them all smoothly towards zero, which handles correlated features well. L1 (lasso) penalises absolute values and sets some coefficients exactly to zero, so it also selects features. Both trade a little bias for less variance.

**Deeper:** [supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md)

### M10. Explain the bias-variance tradeoff and place common models on it.

**Answer:** Expected test error = bias² + variance + noise. Bias is error from a model too simple for the pattern; variance is error from sensitivity to the particular training set. Linear and logistic regression and Naive Bayes are high bias, low variance. Deep trees and k-nearest neighbours with small k are low bias, high variance. Bagging lowers variance, boosting lowers bias, regularisation trades variance for bias.

**Deeper:** [statistical foundations](../../../../data-science/01-classical-ml/notes/01-statistical-foundations.md) · Lab: [overfit_curve.py](../../../../data-science/01-classical-ml/practice/overfit_curve.py)

### M11. How do you detect overfitting and what do you do about it?

**Answer:** Training error is much lower than validation error, and the gap widens as the model gets more complex. Fixes: more data, a simpler model, regularisation, early stopping, fewer features, or an ensemble that averages. If both errors are high the problem is underfitting, and the fixes run the other way.

**Deeper:** [training and tuning](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md) · Lab: [overfit_curve.py](../../../../data-science/01-classical-ml/practice/overfit_curve.py)

### M12. Only 0.5% of your labels are positive, as in fraud. How do you train and evaluate?

**Answer:** Do not use accuracy: predicting "never" scores 99.5%. Evaluate with precision, recall and PR-AUC, or recall at a fixed precision set by the cost of each error. Train with class weights, and choose the decision threshold from costs instead of using 0.5. Resampling is an option but distorts the predicted probabilities. Split by time, since fraud patterns drift.

**Deeper:** [imbalance, errors and drift](../../../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md) · Lab: [credit-default-lab](../../../../data-science/01-classical-ml/practice/credit-default-lab)

### M13. Define precision, recall and ROC-AUC.

**Answer:** Precision: of the cases predicted positive, the share that are positive. Recall: of the actual positives, the share that were caught. Lowering the threshold raises recall and lowers precision. ROC-AUC is the probability that a random positive is scored above a random negative; it measures ranking, ignores the threshold, and looks flattering on heavily imbalanced data.

**Deeper:** [thresholds, PR and ROC](../../../../data-science/01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration.md)

### M14. What is cross-validation, and when is plain k-fold wrong?

**Answer:** Split the data into k folds, train on k − 1 and score on the one held out, rotate, and average. It gives a steadier estimate than one split. Plain k-fold is wrong for time series (train on the past, test on the future), for grouped data (keep each user in one fold), and when preprocessing was fitted on all the data before splitting.

**Deeper:** [model evaluation](../../../../data-science/01-classical-ml/notes/04-model-evaluation.md)

### M15. Which models need feature scaling?

**Answer:** Models based on distances or gradient descent: k-nearest neighbours, k-means, support vector machines, neural networks, and regularised linear models, where the penalty depends on coefficient size. Tree-based models do not, because a split depends only on the order of values.

**Deeper:** [feature engineering and pipelines](../../../../data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines.md)

### M16. You get a tabular classification problem. Which model do you start with and why?

**Answer:** A logistic regression baseline: it is fast, interpretable and shows whether there is signal. Then gradient-boosted trees, which usually win on tabular data because they capture non-linear effects and interactions without feature engineering. The choice also depends on data size, the need to explain decisions, and latency.

**Deeper:** [supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md) · Lab: [boosting-comparison](../../../../data-science/01-classical-ml/practice/boosting-comparison)

### M17. What is data leakage? Give two examples.

**Answer:** Information reaches the model in training that it will not have at prediction time, so validation scores are too good. Examples: a feature recorded after the outcome, such as a chargeback flag in a fraud model; fitting a scaler or selecting features on the full data before splitting; the same customer in both train and test.

**Deeper:** [feature engineering and pipelines](../../../../data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines.md) · Lab: [leaky_selection.py](../../../../data-science/01-classical-ml/practice/leaky_selection.py)

### M18. How do linear, logistic and Poisson regression relate to the Normal, Bernoulli and Poisson distributions?

**Answer:** Each is maximum likelihood under one of them. Least squares is the MLE when errors are Normal. Logistic regression is the MLE for a Bernoulli outcome, with log loss as the negative log-likelihood. Poisson regression is the MLE for counts, with a log link. They are one family, generalised linear models: pick the distribution that matches the outcome.

**Deeper:** [regression and GLMs](../../../../data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md)

### M19. How does k-means work and what are its limits?

**Answer:** Pick k centres, assign each point to the nearest, move each centre to the mean of its points, and repeat until assignments stop changing. It is fast and simple. Limits: you choose k, the result depends on the starting centres, it needs scaled numeric features, and it assumes round clusters of similar size, so it handles elongated shapes and outliers badly.

**Deeper:** [unsupervised learning](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md)

### M20. What is gradient descent, and what does the learning rate do?

**Answer:** An iterative way to minimise a loss: compute the gradient of the loss with respect to the parameters and step in the opposite direction. The learning rate is the step size. Too large and the loss oscillates or diverges; too small and training is slow. Stochastic gradient descent uses a mini-batch per step, which is cheaper and noisier.

**Deeper:** [supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md)

---

## B. Bayesian inference

### B1. State Bayes' theorem in words and name each term.

**Answer:** The posterior is proportional to the likelihood times the prior. The prior is what you believed about the parameter before the data, the likelihood is how probable the data are for each value of the parameter, and the posterior is the updated belief. The evidence, P(data), only rescales the result so that it sums to 1.

**Deeper:** [Bayesian inference](../../../../data-analytics/04-bayesian-analysis/notes/01-bayesian-inference.md)

### B2. What is a conjugate prior? Update a uniform prior on a coin's bias after 7 heads in 10 flips.

**Answer:** A conjugate prior is one whose posterior is in the same family, so the update has a closed form. The Beta is conjugate to the Binomial: a Beta(α, β) prior and n heads in N flips give a Beta(α + n, β + N − n) posterior. A uniform prior is Beta(1, 1), so 7 heads in 10 flips gives Beta(8, 4), with posterior mean 8/12 = 0.667.

**Working:**

1. Prior: Beta(1, 1), which is uniform on 0 to 1.
2. Data: n = 7 heads, N − n = 3 tails.
3. Posterior: Beta(1 + 7, 1 + 3) = Beta(8, 4).
4. Posterior mean: α / (α + β) = 8/12 = 0.667, pulled slightly from the sample proportion 0.7 towards the prior mean 0.5.

**Deeper:** [Bayesian inference](../../../../data-analytics/04-bayesian-analysis/notes/01-bayesian-inference.md)

### B3. What is the difference between the MLE, the MAP estimate and the posterior mean?

**Answer:** The maximum likelihood estimate is the parameter value that makes the data most probable. The maximum a posteriori estimate is the peak of the posterior, so it also counts the prior. The posterior mean averages over the whole posterior. Under a flat prior the MAP estimate equals the MLE.

**Deeper:** [Bayesian inference](../../../../data-analytics/04-bayesian-analysis/notes/01-bayesian-inference.md)

### B4. What is the difference between a credible interval and a confidence interval?

**Answer:** A 95% credible interval says there is a 95% probability that the parameter lies inside it, given the model and the data. A 95% confidence interval is a statement about the procedure: across repeated samples, 95% of the intervals built this way cover the true value. The credible interval is the statement most people think a confidence interval makes.

**Deeper:** [Bayesian inference](../../../../data-analytics/04-bayesian-analysis/notes/01-bayesian-inference.md)

### B5. When do Bayesian and frequentist answers agree?

**Answer:** With a large sample and a prior that does not exclude the truth, the likelihood dominates and both give nearly the same estimate. They differ most when data are scarce, because the prior then carries real weight. The prior is stated openly, can be challenged and fades as data arrive.

**Deeper:** [Bayesian inference](../../../../data-analytics/04-bayesian-analysis/notes/01-bayesian-inference.md)

---

## C. Markov chains

### C1. What is the Markov property?

**Answer:** The next state depends only on the current state, and not on the path taken to reach it. A process with this property is a Markov chain and is fully described by its transition probabilities. Check it on real data by asking whether the previous state still helps predict the next one once the current state is known.

**Deeper:** [states and sequences](../../../../data-analytics/06-applied-analyses/notes/08-states-and-sequences.md)

### C2. How do you estimate a transition matrix from data?

**Answer:** Count the observed moves from each state to each other state, then divide every row by its total. Each row is then the distribution of the next state given the current one, so each row sums to 1.

**Deeper:** [states and sequences](../../../../data-analytics/06-applied-analyses/notes/08-states-and-sequences.md)

### C3. What is an absorbing state, and how do you find the expected time to reach one?

**Answer:** An absorbing state is one the chain cannot leave, such as churned. The other states are transient. Take Q, the part of the transition matrix that moves between transient states. The fundamental matrix N = (I − Q)⁻¹ holds the expected number of visits to each transient state, and the sum of a row is the expected number of steps before absorption from that starting state.

**Deeper:** [states and sequences](../../../../data-analytics/06-applied-analyses/notes/08-states-and-sequences.md)

### C4. A walker on the points 0 to 4 starts at 2 and moves one step left or right with equal chance. The walk stops at 0 or 4. How many steps do you expect?

**Answer:** 4 steps. Write one equation per starting point by conditioning on the first step, then solve them together.

**Working:**

1. Let t(k) be the expected number of steps from point k. t(0) = t(4) = 0.
2. From 2: t(2) = 1 + ½ t(1) + ½ t(3).
3. From 1: t(1) = 1 + ½ t(0) + ½ t(2) = 1 + ½ t(2). By symmetry t(3) = t(1).
4. Substitute: t(2) = 1 + t(1) = 2 + ½ t(2), so t(2) = 4 and t(1) = t(3) = 3.

**Deeper:** [states and sequences](../../../../data-analytics/06-applied-analyses/notes/08-states-and-sequences.md)

---

## U. Unsupervised learning

### U1. What does PCA do, and why do you scale the features first?

**Answer:** Principal component analysis rotates the data so that the first axis follows the direction of greatest variance, the second the greatest variance at right angles to the first, and so on. Keeping the first few axes reduces the number of dimensions. Because it maximises variance, an unscaled feature with a large unit dominates the result, so standardise first.

**Deeper:** [unsupervised learning](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md)

### U2. When would you use PCA and when t-SNE?

**Answer:** PCA is linear, can transform new data and gives features a model can use. t-SNE preserves local neighbourhoods and is for looking at data in two dimensions. In a t-SNE plot the sizes of clusters and the distances between them mean little, and its output should not be used as model features.

**Deeper:** [unsupervised learning](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md)

### U3. How does agglomerative (hierarchical) clustering work, and what does the linkage change?

**Answer:** Start with every point as its own cluster and repeatedly merge the two most similar clusters until the wanted number remain. The merge history is a tree, drawn as a dendrogram. The linkage defines "most similar": Ward merges the pair that least increases within-cluster variance and tends to give clusters of equal size, while single linkage uses the smallest distance between two points and tends to chain into one giant cluster.

**Deeper:** [unsupervised learning](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md)

### U4. Compare k-means and DBSCAN.

**Answer:** k-means needs the number of clusters, assumes round clusters of similar size and can assign new points. DBSCAN finds the number of clusters itself, handles any shape and marks sparse points as noise, but it needs a distance threshold (eps) and cannot assign new points.

**Deeper:** [unsupervised learning](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md)

### U5. How does a Gaussian mixture model differ from k-means?

**Answer:** A Gaussian mixture models the data as several Gaussian components. It fits elliptical clusters and gives each point a probability of belonging to each cluster (a soft assignment), where k-means gives one hard label and assumes round clusters. A high membership probability is confidence inside the fitted model, not evidence that the model is right.

**Deeper:** [unsupervised learning](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md)

### U6. What does the expectation-maximisation (EM) algorithm do?

**Answer:** It fits a model with hidden variables, such as the cluster labels of a Gaussian mixture, by alternating two steps. The E-step computes each point's responsibilities: the probability that it came from each component under the current parameters. The M-step re-fits the weights, means and covariances using those responsibilities as weights. The likelihood never falls, but EM finds only a local optimum, so run several restarts and keep the best.

**Deeper:** [Bayesian machine learning](../../../../data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning.md)

### U7. How do you choose the number of clusters and judge a clustering?

**Answer:** With true labels, score agreement with the adjusted Rand index or normalised mutual information. Without labels, use the silhouette score, the BIC for a mixture model, stability across random seeds and inspection of the clusters by hand. Expect the criteria to disagree. If the final choice of k comes from a product reason, state it as one.

**Deeper:** [unsupervised learning](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md)

---

## N. Neural networks

### N1. Why does a neural network need a non-linear activation, and which do you use where?

**Answer:** Linear layers compose to a single linear layer, so without a non-linearity depth adds no expressive power. ReLU is the default for hidden layers. Use a sigmoid on a binary output layer and a softmax on a multiclass output layer.

**Deeper:** [neural network fundamentals](../../../../data-science/02-deep-learning/notes/01-neural-networks-fundamentals.md)

### N2. What is backpropagation?

**Answer:** The chain rule applied backwards from the loss to every parameter. It reuses the activations cached during the forward pass, so the whole gradient costs about one extra forward pass. Gradient descent then uses that gradient to update the weights.

**Deeper:** [neural network fundamentals](../../../../data-science/02-deep-learning/notes/01-neural-networks-fundamentals.md)

### N3. Why not initialise all the weights to zero?

**Answer:** Every unit in a layer would compute the same output and receive the same gradient, so they would stay identical and the layer would act as one unit. Random initialisation breaks this symmetry.

**Deeper:** [neural network fundamentals](../../../../data-science/02-deep-learning/notes/01-neural-networks-fundamentals.md)

### N4. What causes vanishing and exploding signals in a deep network, and how does initialisation help?

**Answer:** Each layer multiplies the scale of the activations. If the weights are too small the signal shrinks towards zero across the depth, and if too large it grows without limit. He and Glorot initialisation choose the weight variance to keep the scale about constant: He for ReLU, Glorot for tanh and sigmoid.

**Deeper:** [optimisation and regularisation](../../../../data-science/02-deep-learning/notes/02-optimisation-and-regularisation.md)

### N5. What do momentum, RMSprop and Adam add to plain gradient descent?

**Answer:** Plain gradient descent has one step size for all parameters and no memory. Momentum keeps a running average of past gradients, which smooths oscillation. RMSprop divides each step by a running average of squared gradients, which gives each parameter its own step size. Adam combines the two with a bias correction and is the usual default.

**Deeper:** [optimisation and regularisation](../../../../data-science/02-deep-learning/notes/02-optimisation-and-regularisation.md)

### N6. What does batch normalisation do, and how does it differ between training and test time?

**Answer:** It standardises each activation over the mini-batch, then applies a learned scale and shift. In training it uses the statistics of the current batch. At test time it uses running statistics collected during training, which is why forgetting to switch the model to evaluation mode silently hurts results.

**Deeper:** [optimisation and regularisation](../../../../data-science/02-deep-learning/notes/02-optimisation-and-regularisation.md)

### N7. What is dropout, and when does it hurt?

**Answer:** During training, dropout sets a random share p of units to zero and divides the survivors by 1 − p, so the expected activation matches test time, when nothing is dropped. It is a regulariser for a model that fits the training data and does not generalise. In a model that is underfitting it lowers accuracy.

**Deeper:** [optimisation and regularisation](../../../../data-science/02-deep-learning/notes/02-optimisation-and-regularisation.md)

### N8. Why are convolutions used for images, and what does pooling do?

**Answer:** A convolution shares one small set of weights across every position and connects each output to a small local patch. That needs far fewer weights than a dense layer, and a feature learned in one place applies anywhere in the image. Pooling has no parameters: it reduces the spatial size and adds some local invariance.

**Deeper:** [convolutional networks](../../../../data-science/02-deep-learning/notes/04-convolutional-networks.md)

### N9. Why do skip (residual) connections help deep networks train?

**Answer:** A skip connection adds a block's input to its output, so the block only has to learn a change from the identity. The identity becomes the easy default, so adding depth does not degrade training, and gradients have a direct path back to earlier layers.

**Deeper:** [convolutional networks](../../../../data-science/02-deep-learning/notes/04-convolutional-networks.md)

---

## R. Retrieval, ranking and recommenders

### R1. What is an inverted index?

**Answer:** A map from each term to the documents that contain it. A keyword query looks up only its own terms, so the cost depends on how many documents contain those terms and not on the size of the corpus.

**Deeper:** [keyword, semantic and hybrid search](../../../../generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search.md)

### R2. What is TF-IDF, and what does the IDF part do?

**Answer:** A score for how well a term matches a document: term frequency (how often the term appears in the document) times inverse document frequency (how rare the term is across the corpus). IDF discounts terms that appear in many documents. A term in every document contributes nothing, while a rare product code dominates.

**Deeper:** [keyword, semantic and hybrid search](../../../../generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search.md)

### R3. How does BM25 improve on TF-IDF?

**Answer:** It adds two controls. The parameter k1 saturates term frequency, so repeating a term gives diminishing returns. The parameter b sets how much long documents are penalised: 0 ignores length and 1 normalises fully.

**Deeper:** [keyword, semantic and hybrid search](../../../../generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search.md)

### R4. When does keyword search beat embedding search, and what is hybrid search?

**Answer:** Keyword search ranks by shared words, so it wins on exact identifiers, names and jargon, especially when many documents are close in meaning. Embedding (semantic) search ranks by vector distance, so it finds matches that share meaning without sharing words. Hybrid search runs both and fuses the two rankings, commonly with reciprocal rank fusion.

**Deeper:** [keyword, semantic and hybrid search](../../../../generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search.md)

### R5. A corpus has 100 documents and 5 are relevant to a query. The ranked list puts relevant ones at positions 1, 2, 8, 10 and 50. What are precision and recall at k = 10, and why not report accuracy?

**Answer:** Precision at 10 is 0.4 and recall at 10 is 0.8. Accuracy is misleading because almost every document is irrelevant: returning nothing would score 95% here.

**Working:**

1. The top 10 holds the relevant documents at positions 1, 2, 8 and 10: 4 true positives.
2. Precision at 10 = 4/10 = 0.4. Recall at 10 = 4/5 = 0.8.
3. An empty result list gets 95 of 100 documents right (all the irrelevant ones), so accuracy = 0.95 with nothing found.

**Deeper:** [choosing a metric](../../../../data-science/01-classical-ml/notes/11-choosing-a-metric.md)

### R6. What is the difference between MRR and NDCG?

**Answer:** Mean reciprocal rank averages 1/rank of the first relevant result and ignores everything after it. Normalised discounted cumulative gain counts every relevant result, discounted by its depth in the list, and can use graded relevance. Use MRR when the first good result ends the task and NDCG when several results matter.

**Deeper:** [choosing a metric](../../../../data-science/01-classical-ml/notes/11-choosing-a-metric.md)

### R7. What is collaborative filtering, and how does matrix factorisation predict a rating?

**Answer:** Collaborative filtering recommends from the pattern of who interacted with what, without using item content. Matrix factorisation learns a vector for each user and each item from the observed ratings. The prediction is the global mean, plus a user bias, plus an item bias, plus the dot product of the user and item vectors, fitted with L2 regularisation. The biases matter: much of the variance in ratings is user and item offset.

**Deeper:** [collaborative filtering and matrix factorisation](../../../../data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation.md)

### R8. What is the difference between explicit and implicit feedback?

**Answer:** Explicit feedback is a stated rating. Implicit feedback is behaviour, such as clicks, plays and purchases. Implicit data have no negative signal: an item with no interaction may be disliked or just unseen. Counts express confidence, not preference.

**Deeper:** [collaborative filtering and matrix factorisation](../../../../data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation.md)

### R9. What is the cold-start problem, and how do you handle it?

**Answer:** A new item or user has no interactions, so methods that learn only from the interaction matrix can only guess. The fix is to use features: a model that embeds an item from its attributes can place a new item straight away, provided it was trained not to rely on the item id alone.

**Deeper:** [two-tower models and evaluation](../../../../data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md)

### R10. Why do large recommenders and search systems use two stages?

**Answer:** Scoring every item with a rich model is too slow. Retrieval narrows millions of items to a few hundred cheaply and is judged on recall. Ranking then orders those candidates with richer features and is judged on the top of the list.

**Deeper:** [two-tower models and evaluation](../../../../data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md)

---

## T. Features, tuning and time series

### T1. What is the kernel trick?

**Answer:** A support vector machine with a kernel is a linear model in a richer feature space, where a curved boundary becomes a flat one. The kernel trick computes inner products in that expanded space without ever building it, which keeps the cost manageable.

**Deeper:** [supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md)

### T2. Name three ways to select features. When does feature selection help?

**Answer:** Univariate statistics test each feature against the target alone and keep the top ones. Model-based selection fits a model with importances or L1 coefficients and keeps features above a threshold. Iterative selection fits, drops the weakest feature, refits and repeats. Selection helps when many features are noise. A regularised model on clean data rarely gains. Fit the selection inside each cross-validation fold, or it leaks.

**Deeper:** [feature engineering and pipelines](../../../../data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines.md)

### T3. When do you use one-hot, ordinal and target encoding for a categorical feature?

**Answer:** One-hot for a few categories and for linear models. Ordinal when the categories have an order, or for tree models. Target encoding for high-cardinality features, computed with cross-fitting so that a row's own label does not leak into its feature.

**Deeper:** [feature engineering and pipelines](../../../../data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines.md)

### T4. What are the training, validation and test sets for? Why is the best score from a hyperparameter search optimistic?

**Answer:** The training set fits the weights, the validation set chooses models and settings, and the test set gives one final number and is read once. The winner of a search was chosen partly for luck on the validation rows, so its validation score overstates how it will do on new data. Nested cross-validation gives an honest score for the whole tuning procedure, mainly on small data.

**Deeper:** [training and tuning](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md)

### T5. Grid search or random search?

**Answer:** Random search is the usual answer. Few hyperparameters matter much, and random search tries more distinct values of each one for the same budget. Tuning usually helps less than choosing the right model family.

**Deeper:** [training and tuning](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md)

### T6. Why is plain k-fold cross-validation wrong for a time series, and what replaces it?

**Answer:** Random folds train on data from after the rows they are tested on, so the score measures filling gaps between known points and not forecasting. Use rolling-origin evaluation: train only on data before each forecast, move the origin forward and repeat.

**Deeper:** [forecasting](../../../../data-analytics/06-applied-analyses/notes/01-forecasting.md)

### T7. What is the seasonal naive forecast, and what does MASE measure?

**Answer:** The seasonal naive forecast copies the value from one season ago. It costs nothing and already knows the season, so a model that cannot beat it adds cost and no information. MASE is the model's mean absolute error divided by the in-sample mean absolute error of that naive forecast. It has no units, works when values are zero, and below 1 means better than the naive forecast.

**Deeper:** [forecasting](../../../../data-analytics/06-applied-analyses/notes/01-forecasting.md)

---

## K. Metrics and product questions

### K1. A key metric dropped this month. How do you find out why?

**Answer:** Break the metric into the factors that multiply or add up to it, such as revenue = active customers × orders per customer × value per order. Attribute the change to each factor, then go down the branch that moved. Compare with the previous period and with the same period a year ago, to separate a seasonal fall from a real change. The interviewer is checking for a structured breakdown before any guess at a cause.

**Deeper:** [metric trees](../../../../data-analytics/06-applied-analyses/notes/11-metric-trees.md)

### K2. What makes a good north star metric?

**Answer:** It tracks the value customers get, it leads revenue, and a change in it would change what someone does. It moves too slowly to decide a single launch, which is the job of the experiment's own primary metric.

**Deeper:** [metric trees](../../../../data-analytics/06-applied-analyses/notes/11-metric-trees.md)

### K3. What is the difference between a guardrail and a counter-metric?

**Answer:** A guardrail is global: a metric that no change is allowed to break. A counter-metric is paired with one target and exposes hitting that target badly. To pick one, ask how the target could be hit in the laziest way, then measure the result downstream.

**Deeper:** [metric trees](../../../../data-analytics/06-applied-analyses/notes/11-metric-trees.md)

### K4. What is Simpson's paradox? Give an example.

**Answer:** A trend in aggregated data that reverses within every subgroup. It happens when the groups differ in size and baseline. Which table to trust is a causal question: if the subgroup variable is a confounder, read the subgroup table.

**Working:**

1. Mild cases: control recovers 90 of 100 (90%), treatment 39 of 40 (97.5%). Treatment is better.
2. Severe cases: control recovers 30 of 100 (30%), treatment 80 of 160 (50%). Treatment is better.
3. Overall: control 120 of 200 (60%), treatment 119 of 200 (59.5%). Treatment looks worse.
4. The treatment arm holds far more severe cases, which recover less often in both arms.

**Deeper:** [correlation and causation](../../../../data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation.md)
