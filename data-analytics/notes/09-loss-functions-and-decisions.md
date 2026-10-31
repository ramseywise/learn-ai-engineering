---
origin: CamDavidsonPilon-Probabilistic-Programming-and-Bayesian-Methods-for-Hackers-5b33f77
sources:
  - https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers (ch. 5 Would you rather lose an arm or a leg?)
  - http://timsalimans.com/
  - Nate Silver, The Signal and the Noise (2012), weather forecasting chapter
confidence: high
cleaned: 2026-10-31
---
# 9 — Loss Functions and Bayesian Decisions

> A posterior is not a decision. Write down what a wrong answer costs, average that loss over the posterior, and pick the action that minimises it (the Bayes action). Squared loss gives the posterior mean, absolute loss the median, zero-one loss the MAP, and asymmetric losses give answers no point estimate would.

---

## Why accuracy is not enough

BMH ch. 5 opens with a meteorologist who is 95% confident the chance of a hurricane *not* striking is between 99% and 100%, and so advises no evacuation. A 1% hurricane is not a rounding error. Accuracy measures how close the estimate is; a **loss function** measures how bad acting on it would be.

```
L(θ, θ̂)  =  cost of estimating θ̂ when the truth is θ
```

---

## A catalogue of loss functions

| Loss | Formula | Behaviour | Typical use |
|---|---|---|---|
| Squared error | (θ − θ̂)² | punishes large errors heavily; outlier-sensitive | regression, most of ML |
| Asymmetric squared | (θ − θ̂)² if θ̂ < θ, else c(θ − θ̂)² with 0 < c < 1 | underestimating costs more | capacity planning: over-provisioning beats outages |
| Absolute error | \|θ − θ̂\| | linear, robust to outliers | forecasting with heavy tails |
| Zero-one | 1 if θ̂ ≠ θ | right or wrong | classification accuracy |
| Log loss | −θ log θ̂ − (1 − θ) log(1 − θ̂) | punishes confident wrong probabilities | probabilistic classifiers |
| Bounded | 1 − exp(−(θ − θ̂)²) | indifferent once far enough off | when "wrong is wrong" past a point |
| Pundit | \|θ − θ̂\| / (θ(1 − θ)) | huge near 0 and 1 | someone paid to give confident yes/no calls |
| Sign-sensitive (custom) | see the stock example below | wrong direction costs far more than wrong size | trading, any bet on a direction |

**Losses can be bent for good or ill.** Silver's *The Signal and the Noise*: The Weather Channel says 20% chance of rain when it believes 5–10%, because people punish a missed rain forecast far more than a false alarm. That is a "wet bias" chosen to minimise their loss, not yours.

---

## Expected loss and the Bayes action

We never know θ, but we have samples from its posterior. The **expected loss** (Bayesian risk) of an estimate is the average loss over the posterior:

```
l(θ̂) = E_θ[ L(θ, θ̂) ]  ≈  (1/N) Σ L(θ_i, θ̂)      θ_i ~ posterior
```

The **Bayes action** is the θ̂ that minimises it. With posterior samples this is two lines: a vectorised loss and an optimiser.

```python
import scipy.optimize as sop
expected_loss = lambda guess: loss(posterior_samples, guess).mean()
bayes_action = sop.fmin(expected_loss, x0=posterior_samples.mean(), disp=False)
```

### Closed forms worth memorising

| Loss | Bayes action |
|---|---|
| squared error | posterior **mean** |
| absolute error | posterior **median** |
| zero-one (limit) | posterior **mode** (MAP) |

This is why the mean, median and MAP are the usual summaries: each is optimal for a particular loss. When your loss is none of these, none of them is your answer.

---

## Example: The Price is Right showcase (BMH ch. 5)

You must bid on a showcase of two prizes, a snowblower and a trip to Toronto. Bid over the true total and you get nothing. Bid within $250 under and you win both showcases.

| Belief | Distribution |
|---|---|
| Historical showcase totals | true_price ~ Normal(35,000, 7,500) (prior) |
| Your guess at the snowblower | Normal(3,000, 500) |
| Your guess at the trip | Normal(12,000, 3,000) |
| How well your guesses add up to the price | Normal(prize_1 + prize_2, 3,000) |

```python
# BMH ch. 5 (PyMC 5): combine prior and guesses with a Potential
with pm.Model():
    true_price = pm.Normal("true_price", mu=35e3, sigma=75e2)
    prize_1 = pm.Normal("first_prize", mu=3e3, sigma=5e2)
    prize_2 = pm.Normal("second_prize", mu=12e3, sigma=3e3)
    price_estimate = prize_1 + prize_2
    logp = pm.logp(pm.Normal.dist(mu=price_estimate, sigma=3e3), true_price)
    pm.Potential("error", logp)            # adds an arbitrary term to the log posterior
    trace = pm.sample(50000, tune=10000, chains=1)
price_trace = trace.posterior.true_price.data.flatten()
```

The posterior mean drops to about $20,000, roughly $15,000 below the prior: the two prizes look cheap. A frequentist adding point guesses would bid $15,000 regardless of uncertainty; the naive Bayesian would bid the posterior mean. Neither accounts for the asymmetric payoff.

```python
def showdown_loss(guess, true_price, risk=80000):
    loss = np.zeros_like(true_price)
    ix = true_price < guess                         # overbid
    loss[~ix] = np.abs(guess - true_price[~ix])     # underbid: lose the gap
    close_mask = np.abs(true_price - guess) <= 250
    loss[close_mask] = -2 * true_price[close_mask]  # win both showcases: negative loss
    loss[ix] = risk                                 # overbid costs 'risk'
    return loss

for risk in np.linspace(30000, 150000, 6):
    best = sop.fmin(lambda g: showdown_loss(g, price_trace, risk).mean(),
                    15000, disp=False)
```

**Result:** the optimal bid sits well below the posterior mean and falls as `risk` rises. The more overbidding hurts, the more you shade down. `pm.Potential` is the general tool for adding any log-probability term the built-in distributions cannot express.

---

## Example: predicting stock returns with a sign-sensitive loss (BMH ch. 5)

Squared error says predicting −0.01 and predicting +0.03 for a true return of +0.01 are equally bad. A trader disagrees: the first loses money.

```python
def stock_loss(true_return, yhat, alpha=100.):
    if true_return * yhat < 0:
        # opposite signs: penalise heavily, and more so for confident wrong calls
        return alpha * yhat**2 - np.sign(true_return) * yhat + abs(true_return)
    else:
        return abs(true_return - yhat)
```

Fit a Bayesian linear regression of return on a trading signal (`beta, alpha ~ Normal(0, 100)`, `std ~ Uniform(0, 100)`), then for each signal value simulate possible returns from the posterior and minimise the expected `stock_loss`:

```python
noise = std_samples * np.random.randn(N)
possible_outcomes = lambda signal: alpha_samples + beta_samples * signal + noise
for i, s in enumerate(np.linspace(X.min(), X.max(), 50)):
    outcomes = possible_outcomes(s)
    opt_predictions[i] = sop.fmin(lambda p: stock_loss_vec(outcomes, p).mean(), 0, disp=False)
```

**Result:** near a zero signal, where returns could plausibly go either way, the optimal prediction is close to zero, meaning take no position. As the signal grows more extreme the predictions converge to the least-squares line. The model does not fit the data better than least squares; it makes better *decisions* under this loss.

---

## Example: Observing Dark Worlds (BMH ch. 5)

Tim Salimans won Kaggle's dark-matter contest with the full Bayesian workflow, which is a template for any messy prediction problem:

1. **Prior** over the unknown (halo positions).
2. **Likelihood**: a physical model of how halos distort galaxy ellipticities.
3. **Posterior** via MCMC.
4. **Bayes action**: choose predictions that minimise the expected value of the contest's own ~160-line metric over the posterior.

Step 4 is the lesson: optimise for the metric you are scored on, under uncertainty, rather than for parameter accuracy.

---

## In analytics practice

| Decision | Loss to write down | Bayes action |
|---|---|---|
| Ship B or keep A | conversion lost if wrong: max(p_A − p_B, 0) | ship if expected loss < ε (note 08) |
| Inventory or capacity forecast | stock-outs cost more than surplus | an upper quantile, not the mean |
| Fraud threshold | cost of a missed fraud vs cost of a blocked customer | threshold where expected costs balance |
| Price or bid | asymmetric payoff around a cutoff | shade toward the safe side, as in the showcase |
| Model selection | the business metric, not log-likelihood | the model minimising expected business loss |

---

→ Next: [10-bayesian-machine-learning.md](10-bayesian-machine-learning.md) — where the Bayesian track meets machine learning: EM, MCMC, variational autoencoders and Gaussian processes in the BayesianML coursework.
