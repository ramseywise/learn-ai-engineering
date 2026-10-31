---
origin: CamDavidsonPilon-Probabilistic-Programming-and-Bayesian-Methods-for-Hackers-5b33f77
sources:
  - https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers (ch. 6 Getting our priorities straight)
  - http://jmlr.csail.mit.edu/proceedings/papers/v22/kaufmann12/kaufmann12.pdf (Kaufmann et al., Bayes-UCB)
  - ../sources/RM-StatRethink-Bayes.pdf
confidence: high
cleaned: 2026-10-31
---
# 7 — Priors and Bandits

> How to choose a prior (objective, subjective, empirical, conjugate, Jeffreys), why the prior washes out as data grows, the regularisation-as-prior link, and Bayesian bandits: Thompson sampling as the online version of an A/B test.

---

## Kinds of prior

| Kind | What it is | Example | Caveat |
|---|---|---|---|
| Objective / flat | spread evenly over the support | Uniform(0, 1) for a rate | flat is not uninformative after a transform (see Jeffreys) |
| Weakly informative | rules out absurd values, otherwise vague | Normal(0, 10) on a log-odds coefficient | the modern default (Gelman, McElreath) |
| Subjective / informative | encodes real domain knowledge | Beta(30, 970) for a conversion rate known to be about 3% | must be defensible to a sceptic |
| Empirical Bayes | prior parameters fitted from the same data | centre the prior on the sample mean | BMH: **double-counts the data**; overconfident |
| Conjugate | prior chosen so the posterior has the same family | Beta for Binomial, Gamma for Poisson | convenience, not insight; rarely exists for big models |
| Jeffreys | invariant under reparameterisation, ∝ √(Fisher information) | Beta(½, ½) for a Bernoulli rate | can be improper |

BMH ch. 6's practical advice:

- **Gelman:** priors can and should be revised if they produce posterior predictions that look wrong. Choosing a prior is part of model checking, not a one-shot act of faith.
- **Never put zero prior mass where the truth could be.** Bounds like Uniform(0, 100) on a standard deviation are fine only if 100 is far beyond plausible.
- **Watch for priors that become informative after a transform.** A flat prior on θ ∈ [0, 1] becomes a bell shape on log(θ / (1 − θ)). That is the motivation for Jeffreys priors.

### Useful distributions for priors

| Distribution | Support | Prior for |
|---|---|---|
| Beta(α, β) | [0, 1] | rates and probabilities; α − 1 prior successes, β − 1 prior failures |
| Gamma(α, β) | (0, ∞) | positive rates and scales; Exp(β) = Gamma(1, β) |
| Half-Normal, Half-Cauchy, Exponential | (0, ∞) | standard deviations (preferred over Uniform(0, big)) |
| Normal(0, s) | ℝ | regression coefficients |
| Wishart / LKJ | positive-definite matrices | covariance matrices; prefer LKJ in PyMC 5 |

**Conjugate update for a rate:** Beta(1, 1) prior + X successes in N trials gives Beta(1 + X, 1 + N − X). This one line powers the bandit below and the Bayesian A/B test in note 08.

---

## The prior washes out

The log posterior is log-likelihood + log-prior. The log-likelihood is a sum over data points, so it grows with N; the log-prior does not. As N grows, any two priors with the same support give the same posterior.

```python
# BMH ch. 6: flat Beta(1,1) vs biased Beta(2,10), true p = 0.6
p = 0.6
beta1_params = np.array([1., 1.])
beta2_params = np.array([2, 10])
data = stats.bernoulli.rvs(p, size=500)
for N in [0, 4, 8, 32, 64, 128, 500]:
    s = data[:N].sum()
    y1 = stats.beta.pdf(x, *(beta1_params + [s, N - s]))
    y2 = stats.beta.pdf(x, *(beta2_params + [s, N - s]))
    # by N = 500 the two curves are nearly identical, centred near 0.6
```

So the prior matters most exactly when Bayesian methods matter most: small N.

---

## Regularisation is a prior

BMH ch. 6 derives the link between penalised regression and Bayesian MAP estimates.

| Frequentist | Bayesian equivalent |
|---|---|
| Ordinary least squares | maximum likelihood with Normal noise, flat prior on β |
| Ridge (L2 penalty λ‖β‖²) | MAP with a Normal(0, σ) prior on each β |
| Lasso (L1 penalty λ‖β‖₁) | MAP with a Laplace prior on each β |
| Penalty strength λ | prior precision (tighter prior = larger λ) |

One subtlety from the chapter: lasso's sparsity comes from the geometry of the L1 penalty at the MAP, not from the Laplace prior putting mass at zero. The full Laplace posterior is not sparse.

---

## Eliciting priors from experts

- **Trial roulette:** give the expert a grid of bins and twenty chips; they place chips to show where they think the value lies. Fit a distribution to the chip histogram. Works with people who would never write down a Beta.
- **BMH's stock-returns example:** expert beliefs about four stocks' daily returns become Normal priors on the means, and a Wishart prior on the covariance; posterior means and correlations then feed a mean-variance portfolio optimiser. The chapter's warning is that finance has a very low signal-to-noise ratio, and that with N assets the covariance has N(N−1)/2 unknowns, so use the sample covariance as a starting value, or drop correlations you do not need.

---

## Bayesian bandits (Thompson sampling)

The multi-armed bandit: N slot machines with unknown payout rates. Each pull earns a reward and also teaches you about that arm. Pull the best-looking arm too early and you may never discover the real best one (exploitation); keep pulling all arms equally and you waste pulls on losers (exploration). An A/B test is a bandit that explores uniformly until a fixed N and then exploits.

### The algorithm

For each round:

1. For each arm b, draw a sample X_b from its posterior Beta(1 + wins_b, 1 + losses_b).
2. Pull the arm with the largest sample.
3. Observe the reward and update that arm's posterior.

Uncertain arms produce widely spread samples, so they still win the draw sometimes: exploration happens automatically and fades as evidence accumulates. Losers are never discarded, only chosen at a decreasing rate.

```python
# BMH ch. 6, condensed
class Bandits:
    def __init__(self, p_array):
        self.p = p_array
        self.optimal = np.argmax(p_array)
    def pull(self, i):
        return np.random.rand() < self.p[i]
    def __len__(self):
        return len(self.p)

class BayesianStrategy:
    def __init__(self, bandits):
        self.bandits = bandits
        self.wins = np.zeros(len(bandits))
        self.trials = np.zeros(len(bandits))
        self.choices = []

    def sample_bandits(self, n=1):
        for _ in range(n):
            choice = np.argmax(np.random.beta(1 + self.wins,
                                              1 + self.trials - self.wins))
            result = self.bandits.pull(choice)
            self.wins[choice] += result
            self.trials[choice] += 1
            self.choices.append(choice)

bandits = Bandits(np.array([0.85, 0.60, 0.75]))
strat = BayesianStrategy(bandits)
strat.sample_bandits(1000)     # posteriors: the 0.85 arm sharp, the others wide
```

### Measuring a strategy: regret

```
R_T = Σ_{i=1..T} (w_opt − w_{B(i)})
```

where w_opt is the best arm's true rate and w_B(i) the rate of the arm chosen in round i. Zero regret means you always picked the best arm.

| Strategy | Rule | Expected regret |
|---|---|---|
| Random | pick uniformly | linear in T |
| Max mean | pick the highest posterior mean | can lock onto a wrong arm |
| Upper credible bound | pick the highest 95th percentile of the posterior | logarithmic |
| Bayes-UCB | pick the highest dynamic posterior quantile (Kaufmann et al.) | logarithmic |
| Bayesian bandit (Thompson) | sample and take the max | logarithmic |

Any strategy whose expected regret grows logarithmically "solves" the problem (it matches the lower bound). BMH estimates expected regret by repeating the simulation 500 times, the LLN again.

### Extensions from the chapter

| Extension | Change |
|---|---|
| Minimise instead (prizes are bad) | take `argmin` of the samples |
| Non-stationary arms | learning rate: `wins = rate * wins + result`, `trials = rate * trials + 1`; `rate < 1` forgets old evidence faster |
| Non-binary rewards | sample from the posterior of each arm's expected reward; needs MCMC if not conjugate |
| Comment ranking | treat each comment as an arm with Beta(1 + U, 1 + D); on each page load, sample a score per comment and sort. New comments still get seen, unlike ranking by the lower bound (note 08) |

### Bandit or A/B test?

| Use a bandit when | Use a fixed-horizon A/B test when |
|---|---|
| the cost of showing a loser is high (ads, recommendations, promotions) | you need an unbiased effect estimate to report |
| arms change over time | the decision is a one-off ship or no-ship |
| there are many arms | you need to measure guardrail and long-term metrics |

---

→ Next: [08-bayesian-ab-testing.md](08-bayesian-ab-testing.md) — the Bayesian answer to "is B better than A?": P(B > A), expected loss, and ranking by a lower credible bound.
