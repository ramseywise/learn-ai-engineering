---
origin: CamDavidsonPilon-Probabilistic-Programming-and-Bayesian-Methods-for-Hackers-5b33f77; bayesian_inference_talk-main
sources:
  - https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers (ch. 1 Introduction, ch. 2 A little more on PyMC)
  - https://github.com/prasoon2211/bayesian_inference_talk (DataTalks.Club talk, Introduction to Bayesian Inference for Parameter Estimation)
  - https://www.eadan.net/blog/german-tank-problem/
  - ../sources/bayes_for_hackers.pdf
  - ../sources/think_bayes.pdf
confidence: high
cleaned: 2026-10-31
---
# 9 — Bayesian Inference

> Probability as a degree of belief. Start from a prior, update on data with Bayes' theorem, and keep the whole posterior distribution instead of a point estimate. Worked through four models: a coin, a texting-habit switchpoint, a privacy-preserving survey and the German tank problem.

---

## Two views of probability

| | Frequentist (notes 02–08) | Bayesian (notes 09–13) |
|---|---|---|
| Probability is | long-run frequency of an event | degree of belief in an event |
| Parameters are | fixed, unknown constants | random variables with distributions |
| Output | point estimate + confidence interval, p-value | posterior distribution, credible interval |
| A 95% interval means | 95% of intervals built this way contain the true value | 95% probability the value is in this interval, given model and data |
| Prior knowledge | not formally used | encoded as the prior |
| Small N | wide intervals, unstable tests | prior regularises; posterior stays honest about uncertainty |
| Large N | | converges to the frequentist answer: the likelihood swamps the prior |

BMH ch. 1's framing: the frequentist asks "how often would I see data like this if the null were true?"; the Bayesian asks "given the data, what should I believe?". Both are useful. Bayesian methods earn their extra machinery when N is small, when you have real prior knowledge, or when the decision needs a probability ("how likely is B better than A?", note 12).

---

## Bayes' theorem

```
P(A | X) = P(X | A) · P(A) / P(X)

posterior ∝ likelihood × prior
```

### The bug example (BMH ch. 1)

Your code passes all its tests (X). What is the probability it has no bugs (A)? Let p = P(A) be your prior.

- P(X | A) = 1: bug-free code passes every test.
- P(X | ¬A) = 0.5: buggy code still passes the tests half the time.
- P(X) = 1·p + 0.5·(1 − p) = 0.5(1 + p).

```
P(A | X) = p / (0.5(1 + p)) = 2p / (1 + p)
```

| Prior p | Posterior P(A given X) |
|---|---|
| 0.20 | 0.33 |
| 0.50 | 0.67 |
| 0.80 | 0.89 |

Passing the tests raises your belief, but how far depends on where you started. That is the whole method in one line.

---

## The coin: Beta-Binomial

The cleanest Bayesian model, and the one under every Bayesian A/B test (note 12).

| Piece | Choice |
|---|---|
| Unknown | θ = P(heads) |
| Prior | θ ~ Beta(α, β); Beta(1, 1) is uniform |
| Likelihood | n heads in N flips ~ Binomial(N, θ) |
| Posterior | θ given data ~ Beta(α + n, β + N − n) |

The Beta prior is **conjugate** to the Binomial: the posterior is another Beta, so no sampling is needed.

```python
# BMH ch. 1: watch the posterior sharpen as flips arrive
dist = stats.beta
n_trials = [0, 1, 2, 3, 4, 5, 8, 15, 50, 500]
data = stats.bernoulli.rvs(0.5, size=n_trials[-1])
x = np.linspace(0, 1, 100)
for N in n_trials:
    heads = data[:N].sum()
    y = dist.pdf(x, 1 + heads, 1 + N - heads)   # uniform prior
```

The talk repeats this with a Beta(4, 4) prior (mild belief the coin is fair) and N = 50 flips, n = 32 heads. The analytic posterior is Beta(36, 22), mean 0.62, pulled slightly toward 0.5 from the raw 32/50 = 0.64. It then fits the same model in PyMC two ways and gets the same curve, which is the point: MCMC reproduces the closed form when one exists.

```python
# talk: Calculate_Posterior_Prob_with_PyMC.ipynb (PyMC 5)
data = [1] * 32 + [0] * 18
with pm.Model():
    p = pm.Beta("p", 4, 4)
    pm.Bernoulli("y", p=p, observed=data)
    trace1 = pm.sample(5000, tune=1500)

with pm.Model():                       # Binomial version, with hyperpriors on the Beta
    a = pm.Uniform("a", 1, 100)
    b = pm.Uniform("b", 1, 100)
    p = pm.Beta("p", a, b)
    pm.Binomial("y", p=p, n=50, observed=[32])
    trace2 = pm.sample(5000, tune=1500)
az.plot_trace(trace1)
```

With a flat prior, the posterior mode (MAP) equals the maximum-likelihood estimate.

---

## Thinking in generative stories

BMH ch. 2's method for building any model: write the story of how the data could have been generated, from the top down, then translate each line into a distribution. If you can simulate fake data from the story, you can fit it.

### Texting habits: a switchpoint model (BMH ch. 1)

Daily counts of text messages over 74 days. Did the rate change at some point?

| Story | Distribution |
|---|---|
| Texts on day i | C_i ~ Poisson(λ_i) |
| Rate before day τ is λ₁, after is λ₂ | λ_i = λ₁ if i < τ else λ₂ |
| Rates are positive, near the observed mean | λ₁, λ₂ ~ Exponential(1 / mean(counts)) |
| The switch could be any day | τ ~ DiscreteUniform(0, n_days − 1) |

![Graph of the switchpoint model: tau and two lambdas feed a deterministic lambda that parameterises the observed Poisson counts](../sources/images/davidson-pilon-bmh-sms-model-fig1.png)
*Image Source: Davidson-Pilon, Bayesian Methods for Hackers, ch. 2 (MIT)*

```python
# BMH ch. 1 (PyMC 5 port)
count_data = np.loadtxt("data/txtdata.csv")
n_count_data = len(count_data)
alpha = 1.0 / count_data.mean()

with pm.Model() as model:
    lambda_1 = pm.Exponential("lambda_1", alpha)
    lambda_2 = pm.Exponential("lambda_2", alpha)
    tau = pm.DiscreteUniform("tau", lower=0, upper=n_count_data - 1)
    idx = np.arange(n_count_data)
    lambda_ = pm.math.switch(tau > idx, lambda_1, lambda_2)
    observation = pm.Poisson("obs", lambda_, observed=count_data)
    trace = pm.sample(10000, tune=5000, step=pm.Metropolis())

lambda_1_samples = trace.posterior["lambda_1"].values.flatten()
tau_samples = trace.posterior["tau"].values.flatten()
```

**Result:** λ₁ ≈ 18 texts/day, λ₂ ≈ 23, and τ concentrated around day 45, with almost all posterior mass on three or four days. The posterior answers questions a point estimate cannot: P(λ₂ > λ₁) is the fraction of samples where it holds (essentially 1), and the expected count on any day is the average of λ₁ or λ₂ over samples, chosen per sample by whether that day falls before that sample's τ.

---

## PyMC building blocks (BMH ch. 2)

| Concept | PyMC 5 | Note |
|---|---|---|
| Model context | `with pm.Model() as model:` | every variable declared inside belongs to it |
| Stochastic variable | `pm.Normal("x", mu, sigma)` | random even if parents are known |
| Deterministic variable | `pm.Deterministic("d", a - b)` | a function of parents; stored in the trace |
| Vector of variables | `pm.Normal("x", 0, 1, shape=N)` | one call, N independent variables |
| Starting value | `initval=...` | was `testval` in PyMC3 |
| Observed data | `observed=data` | turns a prior into a likelihood |
| Prior draws | `pm.draw(x, draws=1000)` | simulate from the prior before fitting |
| Lazy maths | `pm.math`, `pytensor.tensor as pt` | builds a compiled graph, not NumPy values |
| Stack scalars | `pt.stack([p1, 1 - p1])` | needed for Categorical probabilities |

---

## Cheating survey: Binomial with a privacy mechanism (BMH ch. 2)

You want the share of students who cheat, but nobody will admit it. Each student privately flips a coin. Heads: answer honestly. Tails: flip again and say "yes" on heads, "no" on tails. The interviewer cannot tell who cheated, but

```
P("yes") = 0.5 · p_cheat + 0.5 · 0.5 = 0.5 p + 0.25
```

With 100 students and 35 "yes" answers:

```python
with pm.Model():
    p = pm.Uniform("freq_cheating", 0, 1)
    p_skewed = pm.Deterministic("p_skewed", 0.5 * p + 0.25)
    yes_responses = pm.Binomial("number_cheaters", 100, p_skewed, observed=35)
    trace = pm.sample(25000, tune=2500)
```

The posterior for p spreads roughly from 0.05 to 0.35. The privacy mechanism costs precision (the noise is deliberate) but still rules out "nobody cheats" and "most people cheat". This is the randomised-response technique used in real sensitive surveys.

---

## Challenger: logistic regression with uncertainty (BMH ch. 2)

23 shuttle launches before 1986, each with a temperature and whether an O-ring failed. The night before Challenger the forecast was 31°F.

```python
# p(t) = 1 / (1 + exp(beta * t + alpha))
with pm.Model():
    beta  = pm.Normal("beta", mu=0, tau=0.001, initval=0)
    alpha = pm.Normal("alpha", mu=0, tau=0.001, initval=0)
    p = pm.Deterministic("p", 1.0 / (1.0 + pm.math.exp(beta * temperature + alpha)))
    pm.Bernoulli("obs", p, observed=D)
    start = pm.find_MAP()
    trace = pm.sample(120000, step=pm.Metropolis(), initvals=start)
```

| Output | Reading |
|---|---|
| Posterior of β | entirely positive: colder means more likely to fail |
| 95% credible band of p(t) | from `mquantiles(p_t, [0.025, 0.975], axis=0)` over samples |
| P(defect at 31°F) | posterior concentrated near 1 |

### Is the model any good? Posterior predictive checks

Simulate datasets from the posterior and compare with the real one. BMH's **separation plot** sorts launches by predicted probability and marks the ones that actually failed; a good model puts the failures on the right. Comparing it with a perfect model, a random model and a constant 7/23 model shows the logistic model is useful but not sharp.

---

## German tank problem (talk)

Captured tanks carry serial numbers 1…N. From 15 captured serials, estimate N.

| Estimator | Formula | Property |
|---|---|---|
| Max seen | m | biased low: always ≤ N |
| Max plus average gap | m + m/k − 1 | unbiased; the minimum-variance unbiased estimator; higher variance than m |
| Bayesian | posterior over N | full distribution, honest about uncertainty |

```python
# talk: German_Tank_Problem.ipynb
captured = [499, 505, 190, 427, 185, 572, 818, 721, 912, 302, 765, 231, 547, 410, 884]
max(captured) + max(captured) / len(captured) - 1     # 971.8

with pm.Model():
    num_tanks = pm.DiscreteUniform("num_tanks", lower=max(captured), upper=2000)
    pm.DiscreteUniform("observed", lower=1, upper=num_tanks, observed=captured)
    posterior = pm.sample(10000, tune=1000)
az.plot_posterior(posterior)    # 94% HDI roughly 912 to 1112; true N = 1000
```

The simulation in the talk also shows the bias-variance trade-off: the unbiased estimator is centred on 1,000 but spreads wider than the biased max.

---

## Where to go next

| Want | Read |
|---|---|
| more PyMC mechanics | note 10 |
| the talk's recommended path | BMH (this note), then McElreath's *Statistical Rethinking* ([sources/RM-StatRethink-Bayes.pdf](../sources/RM-StatRethink-Bayes.pdf)), then Gelman et al. *BDA3* |
| Bayesian estimation as a t-test replacement | Kruschke, *Bayesian Estimation Supersedes the t Test* (BEST) |
| the same ideas in plain Python | Downey, *Think Bayes* ([sources/think_bayes.pdf](../sources/think_bayes.pdf)) |

---

→ Next: [10-mcmc-and-pymc.md](10-mcmc-and-pymc.md) — what `pm.sample` is actually doing, how to tell whether it worked, and how to port PyMC3 code to PyMC 5.
