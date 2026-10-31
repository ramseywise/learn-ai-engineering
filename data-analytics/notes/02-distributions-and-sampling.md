---
origin: own coursework
sources:
  - ../practice/5_Statistical_Analysis.ipynb
  - https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers (ch. 4, The Greatest Theorem Never Told)
  - ../sources/Practical_Statistics_for_Data_Scientist.pdf
  - ../sources/thinkstats.pdf
confidence: high
cleaned: 2026-10-31
---
# 2 — Distributions and Sampling

> The four distributions that cover most analytics work, how `scipy.stats` exposes them, and why sample means behave (Law of Large Numbers, Central Limit Theorem) until N gets small.

---

## Why start here

Every test in notes 04–08 and every model in 09–13 is a statement about a distribution. A t-test assumes the sampling distribution of a mean is roughly Normal. A conversion rate is a Binomial proportion. Error counts per hour are Poisson. A Bayesian prior is a distribution over a parameter. If you can name the distribution behind the data, you can usually name the test.

| Data you have | Distribution | Parameters | Mean | Typical question |
|---|---|---|---|---|
| Continuous measurement (height, latency, revenue per user) | Normal | μ, σ | μ | Is the mean different from X? |
| Count of successes in n yes/no trials (conversions, clicks) | Binomial | n, p | np | Is p higher in B than in A? |
| Count of events in a fixed window (errors/hour, texts/day) | Poisson | λ | λ | Did the rate change? |
| Waiting time between Poisson events | Exponential | λ | 1/λ | How long until the next event? |
| A probability itself (a rate you are unsure of) | Beta | α, β | α/(α+β) | What do I believe p is? (note 09) |

Poisson and Exponential are two views of the same process: if events arrive at rate λ per unit time, the count in one unit is Poisson(λ) and the gap between events is Exponential(λ). BMH ch. 1 uses Exponential priors on Poisson rates for exactly this reason (note 09).

---

## The `scipy.stats` interface

Every distribution object has the same methods. Learn them once.

| Method | Meaning | Discrete or continuous |
|---|---|---|
| `.pdf(x)` / `.pmf(k)` | density / probability at a point | pdf continuous, pmf discrete |
| `.cdf(x)` | P(X ≤ x) | both |
| `.sf(x)` | survival function, P(X > x) = 1 − cdf | both |
| `.ppf(q)` | inverse cdf: the x with cdf(x) = q (critical values) | both |
| `.rvs(size=n)` | draw random samples | both |
| `.mean()`, `.std()`, `.interval(0.95)` | moments and central interval | both |

```python
# from practice/5_Statistical_Analysis.ipynb, Part 1
from scipy import stats

# Normal: P(-1 < X < 1) for a standard normal
stats.norm.cdf(1) - stats.norm.cdf(-1)        # 0.6827, the "68" of 68-95-99.7

# Binomial: 20 fair coin flips
stats.binom.pmf(10, 20, 0.5)                   # P(exactly 10 heads)
stats.binom.sf(9, 20, 0.5)                     # P(10 or more heads) = 0.588

# Poisson: a server averages 3 errors/hour; P(more than 5 in an hour)?
stats.poisson.sf(5, 3)                         # 0.084

# critical value for a two-sided 95% test
stats.norm.ppf(0.975)                          # 1.96
```

`sf(k)` is P(X > k), not P(X ≥ k). For "10 or more" on a discrete distribution you pass 9. This off-by-one is the most common bug in hand-rolled tests.

### Sampling check

Draw samples and overlay the theoretical density. If the histogram does not sit on the curve, either the sample is too small or the model is wrong.

```python
samples = np.random.normal(0, 1, 1000)
plt.hist(samples, bins=40, density=True, alpha=0.7)
plt.plot(x, stats.norm.pdf(x), "r-")
samples.mean(), samples.std()   # close to 0 and 1, not equal
```

The same "simulate and compare" habit returns in note 09 as the posterior predictive check.

---

## Law of Large Numbers

> The average of N independent draws from the same distribution converges to the expected value as N grows.

Two consequences from BMH ch. 4 that the rest of this course relies on:

1. **Probability is a mean.** P(A) = E[1_A], the expected value of an indicator. So the fraction of samples where a condition holds estimates its probability. Every `np.mean(samples > 0)` in notes 09–13 is the LLN at work.
2. **Expectations from samples.** E[f(Z)] ≈ (1/N) Σ f(Z_i). This is how posterior expected loss is computed in note 13: average the loss over posterior samples.

### How fast it converges

The error of a sample mean shrinks like

```
error ≈ sqrt(Var(Z)) / sqrt(N)
```

| N | Relative error (σ = 1) |
|---|---|
| 100 | 0.10 |
| 10,000 | 0.01 |
| 1,000,000 | 0.001 |

Halving the error costs four times the data. Note 06 turns the same arithmetic into a sample-size formula.

---

## Central Limit Theorem

> Sums and means of many independent draws are approximately Normal, whatever the shape of the original distribution, with standard error σ/√N.

This is why t-tests and z-tests work on conversion rates, revenue and other non-Normal data: the test is about the *mean*, and the mean is approximately Normal once N is moderate.

| Condition | CLT approximation |
|---|---|
| Symmetric, light tails, N ≥ 30 | good |
| Proportions with np and n(1−p) both ≥ 10 | good (z-test for proportions) |
| Heavy tails (revenue, session length) | slow; needs large N, or use a non-parametric test (note 04) or bootstrap |
| N < 30 and unknown σ | use the t distribution, not Normal |

---

## The small-N trap

BMH ch. 4's warning, worth more than any formula on this page:

> **The LLN holds only for large N. For small N, sample averages are noisy, and the most extreme averages come from the smallest groups.**

### County heights

Simulate 5,000 counties whose populations range from 100 to 1,500. Every person's height is drawn from the *same* distribution, so there is no real difference between counties. Plot average height against population and you get a triangle: the tallest and shortest counties are all small ones. Large counties sit near the true mean.

```python
# BMH ch. 4, condensed
std_height, mean_height = 15, 150
n_counties = 5000
pop_generator = np.random.randint
norm = np.random.normal

population = pop_generator(100, 1500, n_counties)
average_across_county = np.zeros(n_counties)
for i in range(n_counties):
    average_across_county[i] = norm(mean_height, 1. / std_height,
                                     population[i]).mean()

i_min = np.argsort(average_across_county)[:10]
i_max = np.argsort(-average_across_county)[:10]
population[i_min], population[i_max]   # both lists are dominated by small counties
```

The same shape shows up in real US census data (mail-back response rate against block-group population) and in Wainer's *The Most Dangerous Equation*: the Gates Foundation funded small schools because the best-performing schools were small, but the worst-performing schools were small too. Small samples are high-variance, not high-quality.

### Where this bites in analytics

| Setting | Small-N symptom | Fix |
|---|---|---|
| Ranking products by average rating | a 1-review 5-star item tops the list | rank by a lower credible bound (note 12) |
| Comparing regions, stores, cohorts | the best and worst segments are the smallest | show N next to every rate; shrink toward the overall mean |
| A/B test read early | huge lift on day one | fix the sample size in advance (note 06) |
| Model leaderboards on small eval sets | rank flips between runs | report a confidence interval, not a point |

Andrew Gelman's line, quoted in BMH ch. 1, frames the Bayesian half of this course: *"Sample sizes are never large. If N is too small to get a sufficiently-precise estimate, you need to get more data (or make more assumptions). But once N is 'large enough,' you can start subdividing the data to learn more."* There is always a subgroup small enough to be noisy.

---

## Exercises (from BMH ch. 4)

1. Estimate E[cos X] for X ~ Exp(4) by averaging samples. How many samples until the third decimal stops moving?
2. Ranking NFL field-goal kickers by success rate: why does a kicker with 2 of 2 rank above one with 95 of 100, and what should you rank by instead?
3. A chart shows "average programmer income by language" with the top languages all being rare ones. What is going on?

---

→ Next: [03-estimation.md](03-estimation.md) — from a sample to a reported number: maximum likelihood, standard errors, confidence intervals and the bootstrap.
