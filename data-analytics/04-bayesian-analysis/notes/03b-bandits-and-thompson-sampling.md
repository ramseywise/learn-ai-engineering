---
origin: synthesis  # split from 03-priors-and-bandits.md (2026-11-08) so each part stays under the chapter length cap
sources:
  - https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers (ch. 6 Getting our priorities straight)
  - http://proceedings.mlr.press/v22/kaufmann12/kaufmann12.pdf (Kaufmann et al., Bayes-UCB, AISTATS 2012)
  - https://doi.org/10.1016/0196-8858(85)90002-8
  - "Sutton and Barto, Reinforcement Learning: An Introduction, 2nd ed. (MIT Press, 2018), ch. 2"
  - Lattimore and Szepesvári, Bandit Algorithms (Cambridge University Press, 2020), ch. 34 to 36
confidence: high
cleaned: 2026-11-08
---
# 3b — Bandits and Thompson Sampling

> The second half of chapter 3. [3](03-priors-and-bandits.md) covered choosing and checking priors, ridge as a prior and empirical Bayes. Here the same Beta posterior decides which option to try next: Thompson sampling, regret, and when a bandit beats an A/B test.

```python
import numpy as np
from scipy import stats
```

## Bayesian bandits (Thompson sampling)

The multi-armed bandit: N slot machines with unknown payout rates. Each pull earns a reward and also teaches you about that arm. Pull the best-looking arm too early and you may never discover the real best one. Keep pulling all arms equally and you waste pulls on losers. An A/B test is a bandit that explores uniformly until a fixed N and then exploits.

### Conjugate updates

Thompson sampling is cheap because the posterior update is arithmetic. Two cases cover most arms (*Bandit Algorithms*, ch. 34):

- **Bernoulli reward, Beta prior.** Beta(α, β) becomes Beta(α + x, β + 1 − x) after a reward x in {0, 1}, so after t pulls with S_t successes it is Beta(α + S_t, β + t − S_t). The predictive success probability is the posterior mean (α + S_t)/(α + β + t). From Beta(1, 1), 3 successes in 10 pulls gives Beta(4, 8) with mean 1/3.
- **Gaussian reward, Gaussian prior.** With a N(μ, σ²) prior on the arm's mean and unit-variance noise, the posterior after t pulls with reward sum S_t is N(μ_t, σ_t²), where μ_t = (μ/σ² + S_t)/(1/σ² + t) and σ_t² = (1/σ² + t)⁻¹. It is a precision-weighted average of the prior mean and the data, and the variance does not depend on what was observed. A N(0, 1) prior with S_4 = 2 gives mean 0.4 and variance 0.2.

The book's reading of the prior is a pseudo-count: for exponential-family likelihoods a conjugate prior behaves like n₀ earlier observations with average x₀, which is the "imagined data" view of [3](03-priors-and-bandits.md). Pick a prior you can update or sample cheaply, not only one that encodes belief; a non-conjugate arm needs MCMC each round.

### The algorithm

For each round:

1. For each arm b, draw a sample X_b from its posterior Beta(1 + wins_b, 1 + losses_b).
2. Pull the arm with the largest sample.
3. Observe the reward and update that arm's posterior.

```mermaid
flowchart LR
    A["Posterior for each arm"] --> B["Draw one sample per arm"]
    B --> C["Pull the arm with the largest draw"]
    C --> D["Observe reward"]
    D --> E["Update that arm's Beta"]
    E --> A
```

Uncertain arms produce widely spread samples, so they still win the draw sometimes. Exploration happens automatically and fades as evidence accumulates. Losers are never discarded, only chosen at a decreasing rate. The rule is due to Thompson in 1933, and it spent decades in the shade until empirical work such as [Chapelle and Li (NeurIPS, 2011)](https://proceedings.neurips.cc/paper/2011/hash/e53a0a2978c28872a4505bdb51db06dc-Abstract.html) found it highly competitive and argued it should be a standard baseline.

```python
rng = np.random.default_rng(5)
class Bandits:
    def __init__(self, p_array):
        self.p = np.asarray(p_array)
    def pull(self, i):
        return rng.random() < self.p[i]
    def __len__(self):
        return len(self.p)

class BayesianStrategy:
    def __init__(self, bandits):
        self.bandits = bandits
        self.wins = np.zeros(len(bandits))
        self.trials = np.zeros(len(bandits))
    def sample_bandits(self, n=1):
        for _ in range(n):
            draw = rng.beta(1 + self.wins, 1 + self.trials - self.wins)
            choice = np.argmax(draw)
            self.wins[choice] += self.bandits.pull(choice)
            self.trials[choice] += 1

strat = BayesianStrategy(Bandits([0.85, 0.60, 0.75]))
strat.sample_bandits(1000)
print("pulls   ", strat.trials.astype(int))
print("post sd ", np.round(stats.beta(1 + strat.wins, 1 + strat.trials - strat.wins).std(), 3))
```

```text
pulls    [926  26  48]
post sd  [0.011 0.091 0.061]
```

After 1,000 pulls the 0.85 arm has 926 of them and a tight posterior. The others have wide posteriors, which is correct: the strategy has learned just enough about them to stop paying for more.

### Measuring a strategy: regret

```text
R_T = Σ_{i=1..T} (w_opt − w_{B(i)})
```

Here w_opt is the best arm's true rate and w_B(i) the rate of the arm chosen in round i. Zero regret means you always picked the best arm. [Lai and Robbins (*Advances in Applied Mathematics*, 1985)](https://doi.org/10.1016/0196-8858(85)90002-8) proved that any good strategy's regret must grow at least logarithmically in T, so a strategy matching that rate has "solved" the problem in BMH's phrase. Thompson sampling was shown to be logarithmic by [Agrawal and Goyal (COLT, 2012)](https://proceedings.mlr.press/v23/agrawal12.html), and [Bayes-UCB](http://proceedings.mlr.press/v22/kaufmann12/kaufmann12.pdf) has finite-time bounds that imply asymptotic optimality for binary rewards (Kaufmann, Cappé and Garivier, AISTATS 2012).

| Strategy | Rule | Expected regret |
|---|---|---|
| Random | pick uniformly | linear in T |
| Max mean | pick the highest posterior mean | can lock onto a wrong arm |
| Upper credible bound | pick the highest 95th percentile of the posterior | fixed quantile: no guarantee claimed here, measured below |
| Bayes-UCB | pick the highest posterior quantile, with the level rising over time | logarithmic, optimal for binary rewards |
| Thompson | sample and take the max | logarithmic |

BMH estimates expected regret by repeating the simulation 500 times, the Law of Large Numbers again. Here are 300 runs on low rates more like a checkout than a slot machine:

```python
def run(rule, p, T, rng):
    wins, trials = np.zeros(len(p)), np.zeros(len(p))
    regret = np.empty(T)
    for t in range(T):
        i = rule(wins, trials, t, rng)
        wins[i] += rng.random() < p[i]
        trials[i] += 1
        regret[t] = p.max() - p[i]
    return regret.cumsum()

rules = {
    "random": lambda w, n, t, r: r.integers(len(w)),
    "max mean": lambda w, n, t, r: np.argmax((1 + w) / (2 + n)),
    "95% upper bound": lambda w, n, t, r: np.argmax(stats.beta.ppf(0.95, 1 + w, 1 + n - w)),
    "Thompson": lambda w, n, t, r: np.argmax(r.beta(1 + w, 1 + n - w)),
}
p = np.array([0.15, 0.20, 0.10])                           # checkout-style low rates
rng = np.random.default_rng(6)
for name, rule in rules.items():
    runs = np.array([run(rule, p, 2000, rng)[[99, 499, 1999]] for _ in range(300)])
    print(f"{name:16s} regret at 100 {runs[:, 0].mean():5.1f}   500 {runs[:, 1].mean():6.1f}   2000 {runs[:, 2].mean():6.1f}")
```

```text
random           regret at 100   5.0   500   24.9   2000  100.0
max mean         regret at 100   2.9   500    8.8   2000   28.3
95% upper bound  regret at 100   3.3   500    8.6   2000   14.6
Thompson         regret at 100   3.8   500   12.4   2000   22.8
```

Random pays at a constant rate. Thompson's regret climbs from 12 to 23 while pulls quadruple. In this setup, over this horizon, the plain 95% bound beats it, at 14.6, and at 500 pulls max mean is level with the bound. Do not read this as a ranking, because the ordering depends on the gaps and the horizon, and with 300 runs the means still carry noise. Run your own simulation with your rates and horizon before you commit to a rule. Thompson's appeal is that it has no quantile to choose and extends directly to the cases below.

### What the guarantees say

Three results sharpen the regret table above (*Bandit Algorithms*, ch. 34 and 36; the theory itself is in the [RL pillar's bandit note](../../../generative-ai/05-RL/notes/01c-bandit-algorithms.md)):

- **Bayesian regret is an average over the prior.** It integrates the regret over environments drawn from your prior, so a bound on it does not generally bound the regret on any one instance, while a pointwise bound R_n(ν) ≤ f(ν) does give a Bayesian one, E[f(ν)]. The book's advice is to analyse the frequentist regret of Bayesian algorithms. Even the Bayes-optimal policy can have positive Bayesian regret, because it cannot know the best arm in round one.
- **Thompson sampling's bounds.** For k arms, any prior, and rewards that are 1-subgaussian after centring with mean in [0, 1], Bayesian regret is at most C√(kn log n) for a universal constant C (Thm 36.1), and the log factor can be removed (an exercise in the book, after Bubeck and Liu). For unit-variance Gaussian arms, the limit of Thompson sampling as the prior mean and variance go to infinity (posterior N(μ̂, 1/t)) is asymptotically optimal, with R_n/log n tending to Σ 2/Δᵢ over suboptimal arms as n grows (Thm 36.3), and a worst-case regret of C√(nk log n). The book notes it is not minimax optimal for Gaussian noise.
- **Experiment 36.1: not the winner.** On a two-armed Gaussian bandit with means (1/5, 0), unit variance, horizon n = 2,000 and 100,000 runs, expected regret was 29.9 for that Thompson sampler against 23.8 for AdaUCB, a more refined UCB variant, and its regret had a much larger variance. It still beat the plain UCB of the book's chapter 7. This matches the Bernoulli table above: Thompson is a good default, and a tuned bound can beat it at a given horizon.

**A misspecified prior does not wash out.** In ordinary Bayesian analysis data overrules a bad prior (see "The prior washes out" in [3](03-priors-and-bandits.md)). In a bandit it may not: if the prior underestimates an arm, Thompson sampling may rarely or never play it, so no data arrives to correct the belief (*Bandit Algorithms*, ch. 36, Note 5). The book leaves an exercise on this (means (0, 1/10), n = 1,000). When the prior is shaky, check the arm counts, not only the posterior means.

### Extensions from BMH

| Extension | Change |
|---|---|
| Minimise instead (prizes are bad) | take `argmin` of the samples |
| Non-stationary arms | learning rate: `wins = rate * wins + result`, `trials = rate * trials + 1`; `rate < 1` forgets old evidence faster |
| Non-binary rewards | sample from the posterior of each arm's expected reward; needs MCMC if not conjugate |
| Comment ranking | treat each comment as an arm with Beta(1 + U, 1 + D); on each page load, sample a score per comment and sort. New comments still get seen, unlike ranking by the lower bound ([chapter 4](04-bayesian-ab-testing.md)) |

The non-stationary row is one line of change, and it pays when the world moves. Two arms swap their rates halfway through 4,000 pulls:

```python
rng = np.random.default_rng(8)
def forget(rate, T=4000):
    w, n, reward = np.zeros(2), np.zeros(2), 0
    for t in range(T):
        p = np.array([0.20, 0.10]) if t < T // 2 else np.array([0.10, 0.20])   # arms swap
        i = np.argmax(rng.beta(1 + w, 1 + n - w))
        r = rng.random() < p[i]
        w, n = rate * w, rate * n
        w[i] += r
        n[i] += 1
        reward += r
    return reward / T
for rate in (1.0, 0.99):
    print(f"rate {rate}: mean reward per pull {np.mean([forget(rate) for _ in range(100)]):.3f}")
```

```text
rate 1.0: mean reward per pull 0.162
rate 0.99: mean reward per pull 0.179
```

The forgetful strategy reacts to the swap and earns about 10% more per pull. On a stationary problem it would cost a little, because forgetting throws away evidence.

### Sutton and Barto's testbed, and the exact Bayesian answer

The standard benchmark is the 10-armed testbed: 2,000 random bandits, each arm's true value drawn from Normal(0, 1), each reward Normal(true value, 1), 1,000 steps per run, sample-average estimates starting at 0 (*Reinforcement Learning: An Introduction*, ch. 2). A purely greedy learner levelled off near 1 reward per step against about 1.54 for always pulling the best arm, and found the best arm in only about a third of the runs: in the rest, disappointing early draws from the best arm sent it elsewhere for good. Epsilon-greedy at 0.1 found the best arm sooner but never chose it more than 91% of the time, and 0.01 improves more slowly but is expected to end higher, which the authors state and the 1,000 plotted steps do not show.

Thompson sampling above is the posterior-sampling version of the same trade. Two points from the chapter sharpen it:

- **Non-stationarity.** Sample averages assume arms do not change. If they drift, a constant step size weights recent rewards more, which is the "forgetful strategy" above, and the authors note that effectively non-stationary problems are the most common in reinforcement learning.
- **The exact answer is intractable.** Treating the posterior as the problem's information state gives the Bayes-optimal exploration, but even with two actions and two rewards a 1,000-step horizon has 2^2000 leaves in its tree. Thompson sampling and UCB are the feasible stand-ins, which is why the chapter's "Bayesian" bandit is an approximation.

### The Gittins index

Is there an exact answer that is not 2^2000 leaves? Sometimes. For one Bernoulli arm against a known payoff, the Bayes-optimal policy is a retirement rule found by backwards induction over (round, successes so far). It costs O(n²) against O(n) for a frequentist stopping rule. In the book's Experiment 35.1 (n = 500, known arm 1/2, Beta(1, 1) prior, regret plotted against the unknown arm's mean) the Bayes-optimal rule has lower prior-averaged regret, while the frequentist rule is very good when the arm beats 1/2 and poor when it does not; the regrets appear only in a figure (*Bandit Algorithms*, ch. 35).

For k arms, Gittins showed that if the objective is discounted infinite-horizon reward, with geometric discounting and independent arms, the Bayes-optimal policy is an index policy: play the arm with the highest index, the smallest per-round charge that makes you indifferent between retiring and playing it. It fails outside those assumptions: with non-geometric discounting an arm's index can change while you play another, with multiple plays per round the theorem breaks, and for a finite undiscounted horizon the optimal policy is not an index policy. Using the index for the remaining horizon is then only a heuristic that "performs well in practice". Its optimality is for the discounted objective, and it carries no regret guarantee.

### Bandit or A/B test?

| Use a bandit when | Use a fixed-horizon A/B test when |
|---|---|
| the cost of showing a loser is high (ads, recommendations, promotions) | you need an unbiased effect estimate to report |
| arms change over time | the decision is a one-off ship or no-ship |
| there are many arms | you need to measure guardrail and long-term metrics |

Allocation that responds to outcomes is why the left column cannot report a clean effect. The arm that looked bad early stops getting traffic, so its estimate stays noisy and tends to stay low. Larkspur would not have used a bandit for checkout: it wanted a number to report and guardrail metrics it could read at the end.

## Pitfalls

| Pitfall | What goes wrong | Fix |
|---|---|---|
| Reporting a bandit's arm means as an effect | Adaptive allocation biases them | Run a fixed split, or a holdout, for the number you report |
| Trusting a published regret ranking | The order depends on gaps and horizon | Simulate with your own rates |

---

## Try it

1. A Thompson bandit runs a week on a price test where weekend buyers convert differently. What goes wrong, and which row of the extensions table helps?

<details>
<summary>Answers</summary>

1. The early arm's data comes from a different mix of days, so the posterior reflects timing as well as price, and it shifts traffic on that basis. The learning rate helps it recover, but the honest answer for a price decision is usually a fixed split across whole weeks.

</details>

---

## Interview checklist

| Prompt | Answer |
|---|---|
| How does Thompson sampling work? | Draw from each arm's posterior, pull the highest draw, and update. Uncertainty drives exploration |
| What is regret, and what is the bound? | The cumulative gap to the best arm. Lai and Robbins' lower bound is logarithmic in T |
| Why not always use a bandit? | Adaptive allocation biases effect estimates, and it is poorly suited to long-term and guardrail metrics |

---

## Further reading

- BMH ch. 6 for more bandit extensions and the stock example.
- [Bandit and regret theory](../../../generative-ai/05-RL/notes/01c-bandit-algorithms.md) in the RL pillar.

---

## Next

[Chapter 4: Bayesian A/B Testing](04-bayesian-ab-testing.md) takes the Beta posterior back to Larkspur's checkout: P(B > A), expected loss, what peeking does and does not cost, and ranking by a lower credible bound.
