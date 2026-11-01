---
origin: own coursework
sources:
  - ../practice/5_Statistical_Analysis.ipynb
  - https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers (ch. 4, The Greatest Theorem Never Told)
  - ../../sources/Practical_Statistics_for_Data_Scientist.pdf (ch. 2, Data and Sampling Distributions)
  - ../../sources/thinkstats.pdf (ch. 4, Continuous distributions; ch. 6, Operations on distributions)
confidence: high
cleaned: 2026-11-01
---
# 3 — Distributions and Sampling

A foundation gives a pile of money to small schools because the top of the league table is full of them. Then someone looks at the bottom of the table, and that is full of small schools too. Nothing about being small made those schools good or bad; small groups have noisy averages, so they crowd both ends of any ranking. This chapter covers the handful of distributions that describe most analytics data, the two theorems that make sample means behave, and the conditions under which they stop behaving, which are the conditions Larkspur's revenue data lives in.

## Why start here

Every test in [chapter 5](05-hypothesis-testing.md) and every model in [the Bayesian pillar](../../04-bayesian-analysis/README.md) is a statement about a distribution. A t-test assumes the sampling distribution of a mean is roughly Normal. A conversion rate is a Binomial proportion. Error counts per hour are Poisson. A Bayesian prior is a distribution over a parameter. If you can name the distribution behind the data, you can usually name the test.

| Data you have | Distribution | Parameters | Mean | Typical question |
|---|---|---|---|---|
| Continuous measurement (height, latency, log-revenue) | Normal | μ, σ | μ | Is the mean different from X? |
| Count of successes in n yes/no trials (conversions, clicks) | Binomial | n, p | np | Is p higher in B than in A? |
| Count of events in a fixed window (errors/hour, texts/day) | Poisson | λ | λ | Did the rate change? |
| Waiting time between Poisson events | Exponential | λ | 1/λ | How long until the next event? |
| Positive and multiplicative (order value, income) | Lognormal | μ, σ on the log scale | exp(μ + σ²/2) | What is the typical order, and how heavy is the tail? |
| A probability itself (a rate you are unsure of) | Beta | α, β | α/(α+β) | What do I believe p is? ([Bayesian inference](../../04-bayesian-analysis/notes/01-bayesian-inference.md)) |

Poisson and Exponential are two views of the same process: if events arrive at rate λ per unit time, the count in one unit is Poisson(λ) and the gap between events is Exponential(λ). BMH ch. 1 uses Exponential priors on Poisson rates for exactly this reason, and [Bayesian inference](../../04-bayesian-analysis/notes/01-bayesian-inference.md) picks that up. The lognormal row is the shape chapter 1 found in Larkspur's order values. Its mean formula shows the tail at work: the mean grows with σ even when the median, exp(μ), stays still (Downey, *Think Stats*, ch. 4; Bruce & Bruce, 2017, ch. 2).

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

The block below is adapted from Part 1 of the [practice notebook](../practice/5_Statistical_Analysis.ipynb).

```python
from scipy import stats

print(round(stats.norm.cdf(1) - stats.norm.cdf(-1), 4))    # P(-1 < X < 1), standard normal
print(round(stats.binom.pmf(10, 20, 0.5), 4))              # P(exactly 10 heads in 20)
print(round(stats.binom.sf(9, 20, 0.5), 4))                # P(10 or more heads)
print(round(stats.poisson.sf(5, 3), 4))                    # 3 errors/hour: P(more than 5)
print(round(stats.norm.ppf(0.975), 4))                     # two-sided 95% critical value
```

```text
0.6827
0.1762
0.5881
0.0839
1.96
```

`sf(k)` is P(X > k), not P(X ≥ k). For "10 or more" on a discrete distribution you pass 9. This off-by-one is the most common bug in hand-rolled tests.

The claim that Poisson and Exponential are one process is easy to check. Generate exponential gaps, count how many fall in each hour, and compare.

```python
import numpy as np

rng = np.random.default_rng(0)
gaps = rng.exponential(1 / 3, 200_000)           # rate 3 per hour
counts = np.bincount(np.floor(np.cumsum(gaps)).astype(int))[:-1]
print(f"mean gap {gaps.mean():.3f} (1/3 = 0.333)")
print(f"count per hour: mean {counts.mean():.3f}, var {counts.var():.3f}")
print(f"P(count > 5) {np.mean(counts > 5):.3f}, Poisson sf {stats.poisson.sf(5, 3):.3f}")
```

```text
mean gap 0.333 (1/3 = 0.333)
count per hour: mean 3.004, var 3.037
P(count > 5) 0.085, Poisson sf 0.084
```

### Sampling check

Draw samples and compare them with the theoretical distribution. If they disagree, either the sample is too small or the model is wrong. Plotting is the usual way, and the Kolmogorov-Smirnov test puts a number on the gap.

```python
rng = np.random.default_rng(1)
samples = rng.normal(0, 1, 1000)
print(f"mean {samples.mean():+.3f}, sd {samples.std():.3f}")
print(f"KS against N(0,1): p = {stats.kstest(samples, 'norm').pvalue:.2f}")
skewed = np.exp(samples)                 # same draws, wrong shape for a Normal model
fit = stats.norm(skewed.mean(), skewed.std())
print(f"KS of skewed data against a fitted Normal: p = {stats.kstest(skewed, fit.cdf).pvalue:.1e}")
```

```text
mean -0.054, sd 0.986
KS against N(0,1): p = 0.10
KS of skewed data against a fitted Normal: p = 1.5e-56
```

The Normal draws are consistent with N(0,1). Their exponentials, which are what a lognormal is, are decisively not Normal, even with the mean and spread fitted. The same "simulate and compare" habit returns as the [posterior predictive check](../../04-bayesian-analysis/notes/01-bayesian-inference.md). With a large enough sample a goodness-of-fit test will reject any model at all, so treat it as a description of size of disagreement and look at the plot.

## From population to sample

A *population* is what you want to know about. A *sample* is what you have. A *statistic* is a number computed from the sample. The *sampling distribution* is what that statistic would do if you repeated the sampling, and it is the central idea of this chapter: the data have one distribution, and the statistic has another, usually much narrower and better behaved (Bruce & Bruce, 2017, ch. 2).

## Law of Large Numbers

The average of N independent draws from the same distribution converges to the expected value as N grows. Two consequences from BMH ch. 4 that the rest of this course relies on:

1. **Probability is a mean.** P(A) = E[1_A], the expected value of an indicator. So the fraction of samples where a condition holds estimates its probability. Every `np.mean(samples > 0)` in [the Bayesian pillar](../../04-bayesian-analysis/README.md) is the LLN at work.
2. **Expectations from samples.** E[f(Z)] ≈ (1/N) Σ f(Zᵢ). This is how posterior expected loss is computed in [decision-making](../../04-bayesian-analysis/notes/05-loss-functions-and-decisions.md): average the loss over posterior samples.

```python
rng = np.random.default_rng(2)
z = rng.exponential(1.0, 1_000_000)
print("n          running mean   |error|   1/sqrt(n)")
for n in [100, 10_000, 1_000_000]:
    print(f"{n:<10} {z[:n].mean():.4f}         {abs(z[:n].mean() - 1):.4f}    {1 / n**0.5:.4f}")
print("P(z>2) as a mean of an indicator:", round(np.mean(z > 2), 4), "exact", round(np.exp(-2), 4))
print("E[cos z]:", round(np.cos(z).mean(), 4), "exact", 0.5)
```

```text
n          running mean   |error|   1/sqrt(n)
100        0.9303         0.0697    0.1000
10000      0.9758         0.0242    0.0100
1000000    1.0010         0.0010    0.0010
P(z>2) as a mean of an indicator: 0.1353 exact 0.1353
E[cos z]: 0.4998 exact 0.5
```

### How fast it converges

The error of a sample mean shrinks like

```text
error ≈ sqrt(Var(Z)) / sqrt(N)
```

| N | Relative error (σ = 1) |
|---|---|
| 100 | 0.10 |
| 10,000 | 0.01 |
| 1,000,000 | 0.001 |

The error column above tracks that rule, though a single run can land on either side of it. Halving the error costs four times the data. [Experimentation at scale](../../03-experimentation-and-causality/notes/03-experimentation-at-scale.md) turns the same arithmetic into a sample-size formula.

## Central Limit Theorem

Sums and means of many independent draws are approximately Normal, whatever the shape of the original distribution, with standard error σ/√N. This is why t-tests and z-tests work on conversion rates, revenue and other non-Normal data: the test is about the *mean*, and the mean is approximately Normal once N is moderate.

The sticking point is "moderate". Rules of thumb such as N ≥ 30 come from fairly well-behaved data. Larkspur's revenue per user is about as badly behaved as data gets: mostly zeros, then a lognormal tail. The simulation below draws repeated samples of each size and asks how often the usual 95% Normal interval contains the true mean.

```python
rng = np.random.default_rng(3)
def spend(size):
    buy = rng.random(size) < 0.047
    return np.where(buy, rng.lognormal(3.6, 1.1, size), 0.0)

print("n        skew of mean   95% normal CI covers true mean")
pop = spend(5_000_000); true = pop.mean()
for n in [30, 300, 3_000, 30_000]:
    means, cover = [], 0
    for _ in range(3000):
        s = spend(n); m, se = s.mean(), s.std(ddof=1) / n**0.5
        means.append(m); cover += abs(m - true) < 1.96 * se
    print(f"{n:<8} {stats.skew(means):>6.2f}         {cover / 3000:.3f}")
```

```text
n        skew of mean   95% normal CI covers true mean
30         4.68         0.563
300        1.34         0.832
3000       0.46         0.928
30000      0.22         0.948
```

At n = 30 the "95%" interval covers the truth about 56% of the time. It takes tens of thousands of users to earn the label. And the failure is not symmetric. Most small samples contain few whales, so they underestimate both the mean and the spread and sit too confidently below the truth. This is what the skew column reports. The formula never warned you, because the standard error it uses is itself estimated from the same sample.

| Condition | CLT approximation |
|---|---|
| Symmetric, light tails, N ≥ 30 | good |
| Proportions with np and n(1−p) both ≥ 10 | good (z-test for proportions) |
| Heavy tails (revenue, session length) | slow; needs large N, or use a non-parametric test ([chapter 5](05-hypothesis-testing.md)) or the [bootstrap](04-estimation.md) |
| N < 30 and unknown σ | use the t distribution, not Normal |

The theorem also needs independence and finite variance. Rows from the same user break the first, as [chapter 2](02-probability-foundations.md) showed. Some extreme heavy-tailed distributions break the second, and for those a mean never settles at all. For a visual treatment, see 3Blue1Brown's [central limit theorem video](https://www.youtube.com/watch?v=zeJD6dqJ5lo).

### Big is not the same as representative

The CLT describes sampling error. It says nothing about bias in how you selected the rows, and having more of them does not reduce that.

```python
rng = np.random.default_rng(6)
pop = spend(1_000_000)
print(f"population mean {pop.mean():.3f}")
resp = rng.random(len(pop)) < np.where(pop > 0, 0.20, 0.05)   # buyers answer surveys more
print(f"survey of responders: {pop[resp].mean():.3f} from {resp.sum():,} rows")
rnd = rng.choice(pop, 5_000, replace=False)
print(f"simple random sample: {rnd.mean():.3f} from {len(rnd):,} rows")
```

```text
population mean 3.123
survey of responders: 11.062 from 57,152 rows
simple random sample: 3.001 from 5,000 rows
```

Larkspur emails a spend survey to everyone and buyers are four times likelier to reply. The result has 57,000 rows and is more than three times too high. A simple random sample of 5,000 is within about 4% of the truth. Sampling error shrinks with n. Selection bias does not. Before admiring a large N, ask how the rows got into the table.

## The small-N trap

BMH ch. 4's warning is worth more than any formula on this page: the LLN holds only for large N. For small N, sample averages are noisy, and the most extreme averages come from the smallest groups.

### County heights

Simulate 5,000 counties whose populations range from 100 to 1,500. Every person's height is drawn from the *same* distribution, so there is no real difference between counties.

```python
rng = np.random.default_rng(4)
n_counties = 5000
population = rng.integers(100, 1500, n_counties)
heights = np.array([rng.normal(150, 15, p).mean() for p in population])

order = np.argsort(heights)
print("mean height, all counties:", heights.mean().round(2))
print("population of 10 shortest:", np.sort(population[order[:10]]))
print("population of 10 tallest: ", np.sort(population[order[-10:]]))
print("median population overall:", int(np.median(population)))
```

```text
mean height, all counties: 150.0
population of 10 shortest: [103 108 110 113 135 159 161 164 217 291]
population of 10 tallest:  [104 117 127 128 141 143 174 180 265 290]
median population overall: 808
```

Every one of the ten tallest and ten shortest counties has fewer than 300 people, though the median county has 808. Plot average height against population and you get a triangle, wide at the small end and narrow at the large end.

```text
average
height
  ^     .
  |    . .
  |   . . . .
  |  ......:::::::::::::::    all counties share one true mean
  |   . . . .
  |    . .
  |     .
  +------------------------> population
     small             large
```

The same shape shows up in real US census data in BMH ch. 4 (mail-back response rate against block-group population), and in Wainer's *The Most Dangerous Equation* (as discussed in BMH ch. 4): the Gates Foundation funded small schools because the best-performing schools were small, but the worst-performing schools were small too. Small samples are high-variance, not high-quality.

### Shrinkage: the fix in a line

If a raw rate is unreliable because its N is small, pull it toward what you know about the group. A simple way is to add pseudo-observations at the overall rate. The formula looks ad hoc, but it is exactly the Beta-Binomial posterior mean of the [Bayesian pillar](../../04-bayesian-analysis/notes/01-bayesian-inference.md).

```python
rng = np.random.default_rng(5)
trials = np.array([2, 5, 20, 100, 1000])
hits = np.array([2, 5, 18, 92, 905])
raw = hits / trials
prior_mean, prior_n = 0.9, 40
shrunk = (hits + prior_mean * prior_n) / (trials + prior_n)
for t, h, r, s in zip(trials, hits, raw, shrunk):
    print(f"{h:>4}/{t:<5} raw {r:.3f}  shrunk {s:.3f}")
```

```text
   2/2     raw 1.000  shrunk 0.905
   5/5     raw 1.000  shrunk 0.911
  18/20    raw 0.900  shrunk 0.900
  92/100   raw 0.920  shrunk 0.914
 905/1000  raw 0.905  shrunk 0.905
```

The 2/2 kicker drops below the 92/100 kicker, and the 905/1000 estimate does not change. The estimate moves only when N is too small to speak for itself. Efron and Hastie treat this as empirical Bayes and the James-Stein estimator (*Computer Age Statistical Inference*, ch. 6 and 7), where the amount of shrinkage is itself estimated from the data.

### Where this bites in analytics

| Setting | Small-N symptom | Fix |
|---|---|---|
| Ranking products by average rating | a 1-review 5-star item tops the list | rank by a lower credible bound ([Bayesian decision-making](../../04-bayesian-analysis/notes/05-loss-functions-and-decisions.md)) |
| Comparing regions, stores, cohorts | the best and worst segments are the smallest | show N next to every rate; shrink toward the overall mean |
| A/B test read early | huge lift on day one | fix the sample size in advance ([experimentation at scale](../../03-experimentation-and-causality/notes/03-experimentation-at-scale.md)) |
| Model leaderboards on small eval sets | rank flips between runs | report a confidence interval, not a point |

Andrew Gelman's line, quoted in BMH ch. 1, frames the Bayesian half of this course: *"Sample sizes are never large. If N is too small to get a sufficiently-precise estimate, you need to get more data (or make more assumptions). But once N is 'large enough,' you can start subdividing the data to learn more."* There is always a subgroup small enough to be noisy.

---

## Pitfalls

- **Off-by-one on discrete tails.** `sf(9)` is P(X ≥ 10). Passing 10 gives a different answer, silently.
- **Treating N ≥ 30 as a law.** It came from fairly well-behaved data. For zero-inflated revenue, N = 300 still gives an interval that covers about 83% of the time here.
- **Mistaking volume for representativeness.** Fifty-seven thousand self-selected rows lose to five thousand random ones.
- **Confusing the data's distribution with the statistic's.** Revenue is not Normal and never will be. The question is whether the mean of revenue is.
- **Ranking raw rates.** The top and bottom of any league table are dominated by small groups. Show N or shrink.
- **Overusing goodness-of-fit tests.** They reject every model given enough rows and pass most models given few. Look at the plot and ask whether the misfit matters for your decision.
- **Assuming independence.** The CLT's σ/√N requires independent rows. Pseudoreplicated data gives a beautifully Normal mean with a standard error that is simply wrong.

---

## Try it

The first three exercises are adapted from BMH ch. 4.

1. Estimate E[cos X] for X ~ Exp(1) by averaging samples. How many samples until the third decimal stops moving?
2. Ranking NFL field-goal kickers by success rate: why does a kicker with 2 of 2 rank above one with 95 of 100, and what should you rank by instead?
3. A chart shows "average programmer income by language" with the top languages all being rare ones. What is going on?
4. Change the `spend` function in the `clt` block so that 30% of users buy. How does coverage at n = 300 change, and why?

<details>
<summary>Answers</summary>

1. The exact value is 1/2. Error shrinks with 1/√N and Var(cos X) = 0.6 − 0.25 = 0.35, so sd is about 0.59, and an error under 0.0005 needs about (0.59/0.0005)², or 1.4 million samples. The `lln` block printed 0.4998 at one million.
2. The raw rate has no notion of N. The lower 95% Wilson bound is a better ranking, and gives the output below, so the 95/100 kicker wins easily. A shrunken rate gives a similar order.
3. Rare languages have few respondents, so their averages are noisy and fill the extremes. Add a lower bound or filter by N, and most of the effect should disappear.
4. Coverage rises, because far fewer samples are mostly zeros, so the mean's skew falls. The heavy tail still costs something: the lognormal part has not changed.

```python
print(f"2/2 lower 95% Wilson: {stats.binomtest(2, 2).proportion_ci(method='wilson').low:.3f}")
print(f"95/100 lower 95% Wilson: {stats.binomtest(95, 100).proportion_ci(method='wilson').low:.3f}")
```

```text
2/2 lower 95% Wilson: 0.342
95/100 lower 95% Wilson: 0.888
```

</details>

---

## Interview checklist

| Prompt | Answer |
|---|---|
| Which distribution for clicks out of impressions, and errors per hour? | Binomial for a count out of n trials. Poisson for a count in a window with no fixed ceiling. |
| What does the CLT actually say, and what does it require? | Means of many independent draws are approximately Normal with SE σ/√N. It needs independence, finite variance, and more N the heavier the tail. |
| Is N = 30 enough for a t-test on revenue? | Usually not. Simulations on zero-inflated lognormal spend show 95% intervals covering about 56% at n = 30 and about 83% at n = 300. Use more data or a bootstrap, and check by simulation. |
| Why are the best and worst schools (or stores) so often small? | Variance of a mean scales as 1/N, so small groups produce extremes in both directions without any real difference. |
| LLN or CLT: which tells you how wrong your mean is? | LLN says it converges. CLT describes the distribution of the error, giving the interval. |
| How would you rank items with few ratings? | Use a lower confidence or credible bound, or shrink toward the overall mean with a Beta prior. |
| Can a larger sample fix a biased sample? | No. It gives a more precise estimate of the wrong number. |

---

## Next

[Chapter 4: Estimation](04-estimation.md) goes from a sample to a reported number: maximum likelihood, standard errors, confidence intervals and the bootstrap, including the interval that holds up on Larkspur's revenue.
