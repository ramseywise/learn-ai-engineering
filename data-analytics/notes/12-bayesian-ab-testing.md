---
origin: CamDavidsonPilon-Probabilistic-Programming-and-Bayesian-Methods-for-Hackers-5b33f77
sources:
  - https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers (ch. 2 A/B testing, ch. 4 sorting Reddit comments)
  - https://www.evanmiller.org/bayesian-ab-testing.html
  - https://www.chrisstucchio.com/blog/2014/bayesian_ab_decision_rule.html (Stucchio, expected-loss decision rule)
  - ../practice/AB-Bayes/AB_Testing_with_Python.ipynb
confidence: high
cleaned: 2026-10-31
---
# 12 — Bayesian A/B Testing

> Put a Beta prior on each arm's conversion rate, update it with the counts, and answer the question stakeholders actually ask: how likely is B better than A, and how much do we lose if we pick B and are wrong? The same lower-bound idea ranks items with few ratings.

---

## The question changes

| Frequentist A/B (note 06) | Bayesian A/B |
|---|---|
| "If A and B were equal, how surprising is this data?" (p-value) | "Given the data, what is P(B > A)?" |
| fixed N set in advance | any N; unequal arms are fine |
| reject / fail to reject | a probability and an expected loss to act on |
| lift with a confidence interval | full posterior of the lift; credible interval |
| peeking invalidates the test | peeking is less damaging, but a stopping rule is still needed |

Note 06's AB notebook ([practice/AB-Bayes/AB_Testing_with_Python.ipynb](../practice/AB-Bayes/AB_Testing_with_Python.ipynb)) is, despite its folder name, entirely frequentist; a comment in it ("check out bayesian recursive learning method of adjusting proportions after establishing prior") is the pointer to this note. The code below runs on the same `successes` and `nobs` it computes.

---

## The PyMC model (BMH ch. 2)

```python
# BMH ch. 2: true p_A = 0.05, p_B = 0.04, deliberately unequal sample sizes
true_p_A, true_p_B = 0.05, 0.04
N_A, N_B = 1500, 750
observations_A = stats.bernoulli.rvs(true_p_A, size=N_A)
observations_B = stats.bernoulli.rvs(true_p_B, size=N_B)

with pm.Model():
    p_A = pm.Uniform("p_A", 0, 1)
    p_B = pm.Uniform("p_B", 0, 1)
    delta = pm.Deterministic("delta", p_A - p_B)        # the quantity we care about
    pm.Bernoulli("obs_A", p_A, observed=observations_A)
    pm.Bernoulli("obs_B", p_B, observed=observations_B)
    trace = pm.sample(20000, step=pm.Metropolis(), chains=2)

delta_samples = trace.posterior["delta"].values.flatten()
np.mean(delta_samples > 0)     # P(site A is better than site B)
np.mean(delta_samples < 0)     # P(site A is worse)
```

Reading the output:

- The posterior of p_B is wider than p_A's because B had half the traffic. The model handles unequal N without any correction.
- The posterior of delta sits mostly above zero; the fraction above zero is P(A > B).
- If N_B is increased, p_B's posterior narrows and P(A > B) firms up. More data, more certainty, no change in method.

---

## Skip the sampler: Beta closed form

Conversion data is Binomial and Beta is conjugate, so each arm's posterior is known exactly (note 09):

```
p_A | data ~ Beta(α₀ + conversions_A, β₀ + visitors_A − conversions_A)
```

Draw from both posteriors and compare. This is fast enough to run on every dashboard refresh.

```python
rng = np.random.default_rng(0)
a0, b0 = 1, 1                                # uniform prior; see "priors" below
conv_A, n_A = 120, 1000
conv_B, n_B = 140, 1000

post_A = rng.beta(a0 + conv_A, b0 + n_A - conv_A, 200_000)
post_B = rng.beta(a0 + conv_B, b0 + n_B - conv_B, 200_000)

prob_B_better   = (post_B > post_A).mean()                   # about 0.91
lift            = (post_B - post_A) / post_A
lift_ci         = np.percentile(lift, [2.5, 97.5])
loss_if_choose_B = np.maximum(post_A - post_B, 0).mean()     # about 0.0006 (0.06 pp)
loss_if_choose_A = np.maximum(post_B - post_A, 0).mean()     # about 0.021 (2.1 pp)
```

P(B > A) also has an exact closed form as a finite sum (Evan Miller), but Monte Carlo with 10⁵ draws is accurate to about 0.002 and generalises to any metric.

---

## Expected loss: the decision rule

P(B > A) = 0.91 does not say how bad the 9% case is. Expected loss does.

```
E[loss | choose B] = E[ max(p_A − p_B, 0) ]
```

the average conversion rate you give up by shipping B, counting only the worlds where A was actually better. It is a loss function in the sense of note 13.

| Rule | Ship B when |
|---|---|
| Probability threshold | P(B > A) > 0.95 |
| **Expected-loss threshold** (Stucchio / VWO) | E[loss given B] < ε, with ε the smallest difference you care about (for example 0.1 pp) |
| Credible interval | the 95% interval of the lift excludes 0 |

The expected-loss rule is the most useful in practice: it stops early when B is clearly better, stops early when the arms are so close that choosing wrong costs almost nothing, and keeps running only when the choice still matters.

### Priors for A/B tests

| Prior | Effect |
|---|---|
| Beta(1, 1) | uniform; fine once each arm has a few hundred visitors |
| Weakly informative from history, e.g. Beta(3, 97) for a ~3% baseline | stabilises the first days of a test; washes out quickly (note 11) |
| Strong prior from history, e.g. Beta(300, 9700) | demands real evidence before believing a big lift; guards against early-noise "wins" |

Use the *same* prior for both arms. The prior encodes what you knew about conversion rates before the test, not which arm you hope wins.

### Is peeking safe?

Safer, not safe. The posterior is a valid summary at any N, so looking does not invalidate it the way it invalidates a p-value. But a rule like "stop the first time P(B > A) > 0.95" still raises the rate of shipping no-difference changes. An expected-loss threshold, a minimum sample size, and running full weeks reduce the problem.

---

## Ranking with few observations (BMH ch. 4)

The same machinery fixes the small-N trap from note 02. Sorting by raw upvote ratio puts a comment with 1 upvote and 0 downvotes (100%) above one with 999 and 1 (99.9%).

![Reddit comments with very different vote counts, illustrating why raw upvote ratio misranks](../sources/images/davidson-pilon-bmh-reddit-comments-fig1.png)
*Image Source: Davidson-Pilon, Bayesian Methods for Hackers, ch. 4 (MIT)*

BMH's fix: give each comment a posterior over its true upvote ratio and sort by the **95% least plausible value**, the 5th percentile of the posterior. A comment ranks high only if we are confident its ratio is high.

```python
# BMH ch. 4: full PyMC version
def posterior_upvote_ratio(upvotes, downvotes, samples=15000):
    N = upvotes + downvotes
    with pm.Model():
        upvote_ratio = pm.Uniform("upvote_ratio", 0, 1)
        pm.Binomial("obs", N, upvote_ratio, observed=upvotes)
        trace = pm.sample(samples, step=pm.NUTS(), tune=5000, chains=1)
    return trace.posterior.upvote_ratio.data.T

# fast closed form (Normal approximation to the Beta posterior)
def lower_bound(u, d):
    a, b = 1 + u, 1 + d
    return a / (a + b) - 1.65 * np.sqrt((a * b) / ((a + b) ** 2 * (a + b + 1)))
```

| Upvotes | Downvotes | Raw ratio | Lower bound |
|---|---|---|---|
| 999 | 1 | 0.999 | 0.996 |
| 60 | 40 | 0.600 | 0.518 |
| 6 | 4 | 0.600 | 0.358 |
| 1 | 0 | 1.000 | 0.278 |

**Star ratings** work the same way: map n stars out of N to n/N, sum the scores into S over all ratings, and use a = 1 + S, b = 1 + (count − S) in the same formula.

### Where else to use it

| Ranking | Successes | Trials |
|---|---|---|
| products by rating | sum of normalised stars | number of ratings |
| sellers by on-time delivery | on-time orders | orders |
| ads by click-through | clicks | impressions |
| LLM prompts or models by eval pass rate | passes | eval cases |

Limitations from BMH ch. 6: the lower bound favours old items with many votes. Ranking by a *sample* from each item's posterior (the comment-ranking bandit in note 11) gives new items a chance to be seen.

---

→ Next: [13-loss-functions-and-decisions.md](13-loss-functions-and-decisions.md) — turning a posterior into an action by minimising expected loss: squared, absolute and asymmetric losses, and the Price is Right and stock-prediction examples.
