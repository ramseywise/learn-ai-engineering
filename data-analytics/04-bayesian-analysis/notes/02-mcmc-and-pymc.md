---
origin: CamDavidsonPilon-Probabilistic-Programming-and-Bayesian-Methods-for-Hackers-5b33f77
sources:
  - https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers (ch. 3 Opening the Black Box of MCMC)
  - https://www.pymc.io/projects/docs/en/stable/guides/Gotchas.html
  - https://python.arviz.org/
  - ../practice/BayesianML/week_4/
confidence: high
cleaned: 2026-10-31
---
# 10 — MCMC and PyMC

> Why we sample instead of computing the posterior, what Markov chain Monte Carlo does at each step, how to read traces and diagnostics, a full mixture model, and the map from PyMC3 code to PyMC 5.

---

## Why sample at all

With one or two conjugate parameters (note 09's coin) the posterior has a formula. With more, the posterior is a surface over N dimensions, and computing it on a grid costs k^N evaluations. BMH ch. 3's picture: the prior is a landscape over parameter space; the likelihood warps it, pulling up the regions consistent with the data. We need to explore the warped landscape without mapping all of it.

> **MCMC returns samples from the posterior, not the posterior itself.** Every summary (mean, interval, P(B > A), expected loss) is then an average over samples, by the Law of Large Numbers (note 02).

Two consequences BMH stresses:

- **A prior of zero stays zero.** If the prior assigns no mass to a region, no amount of data can move the posterior there. Choose supports generously (note 11).
- **Thousands of samples, not tens.** Summaries are Monte Carlo estimates; their error shrinks like 1/√(effective samples).

---

## What one MCMC step does

1. Start at the current position (a vector of parameter values).
2. **Propose** a nearby position.
3. **Accept** it with a probability that depends on how much higher (or lower) the posterior density is there. Always accept uphill; sometimes accept downhill.
4. Record the position (the new one if accepted, the old one if not) and repeat.

The chain is *memoryless*: the next step depends only on the current position. After a warm-up, the positions are distributed like the posterior. Rejected proposals are not wasted: staying put is how the chain spends more time in high-density regions.

| Sampler | PyMC 5 | Good for |
|---|---|---|
| NUTS (Hamiltonian Monte Carlo) | default for continuous variables | almost everything continuous; uses gradients to make long, well-directed moves |
| Metropolis | `pm.Metropolis()` | discrete variables, quick experiments; BMH uses it heavily |
| CategoricalGibbsMetropolis | `pm.CategoricalGibbsMetropolis()` | Categorical assignments (replaced `ElemwiseCategorical`) |
| Compound | `step=[step1, step2]` | NUTS or Metropolis for continuous, a discrete sampler for the rest |

Alternatives to MCMC mentioned in ch. 3: the **Laplace approximation** (fit a Normal at the MAP) and **variational inference** (`pm.fit(method="advi")`), both faster and less exact. BMH ch. 5 uses ADVI to initialise NUTS.

---

## Worked example: a two-cluster mixture (BMH ch. 3)

300 values that look bimodal. Model them as a mixture of two Normals.

| Story | Distribution |
|---|---|
| Each point belongs to cluster 0 with probability p | p ~ Uniform(0, 1) |
| Its cluster label | assignment_i ~ Categorical([p, 1 − p]) |
| Each cluster has a centre and a spread | centers ~ Normal([120, 190], σ = 10); sds ~ Uniform(0, 100), shape 2 |
| The observed value | x_i ~ Normal(centers[assignment_i], sds[assignment_i]) |

```python
# BMH ch. 3 (PyMC 5 port)
import pytensor.tensor as pt
data = np.loadtxt("data/mixture_data.csv", delimiter=",")

with pm.Model() as model:
    p1 = pm.Uniform("p", 0, 1)
    p2 = 1 - p1
    p = pt.stack([p1, p2])
    assignment = pm.Categorical("assignment", p, shape=data.shape[0],
                                initval=np.random.randint(0, 2, data.shape[0]))
    sds = pm.Uniform("sds", 0, 100, shape=2)
    centers = pm.Normal("centers", mu=np.array([120, 190]), sigma=np.array([10, 10]), shape=2)
    center_i = pm.Deterministic("center_i", centers[assignment])
    sd_i = pm.Deterministic("sd_i", sds[assignment])
    observations = pm.Normal("obs", mu=center_i, sigma=sd_i, observed=data)

    step1 = pm.Metropolis(vars=[p1, sds, centers])
    step2 = pm.CategoricalGibbsMetropolis(vars=[assignment])
    trace = pm.sample(25000, step=[step1, step2], tune=5000)
```

**Result:** the posterior puts the two centres near 120 and 200, with different standard deviations for the two clusters, as the histogram suggested. A less likely but still consistent explanation (one wide cluster, one narrow) also has posterior mass, which is why the next rule matters.

### Using the posterior

To classify a new point x = 175, compare the posterior-averaged likelihood under each cluster, weighted by the cluster probability, sample by sample:

```python
# P(x in cluster 1) ∝ p · N(x; center_1, sd_1), averaged over posterior samples
# compare P(x | L=1) P(L=1) with P(x | L=0) P(L=0); P(x) cancels
v = (p_trace * norm_pdf(x, loc=center_trace[:, 0], scale=std_trace[:, 0])
     > (1 - p_trace) * norm_pdf(x, loc=center_trace[:, 1], scale=std_trace[:, 1]))
v.mean()      # probability x = 175 belongs to cluster 0

# assigning to the nearer centre would ignore that the clusters have different spreads
```

> **Do not mix posterior samples across indices.** Each sample is a joint draw. If x + y = 10 is a constraint, pairing x from sample 3 with y from sample 900 breaks it. Compute derived quantities within a sample, then summarise.

### Label switching

In mixtures, "cluster 0" and "cluster 1" can swap meaning between chains or mid-chain. Informative priors on the centres (120 vs 190 above) or an ordering constraint stop it.

---

## Is the sampler working? Diagnostics

| Check | Tool | Healthy |
|---|---|---|
| Trace plot | `az.plot_trace(idata)` | "fuzzy caterpillar": no trends, chains overlap |
| R-hat | `az.summary(idata)["r_hat"]` | ≤ 1.01 |
| Effective sample size | `ess_bulk`, `ess_tail` in `az.summary` | hundreds or more per parameter |
| Autocorrelation | `az.plot_autocorr(idata)` | drops to near zero within a few lags |
| Divergences (NUTS) | `idata.sample_stats.diverging.sum()` | zero; otherwise reparameterise |
| Posterior | `az.plot_posterior(idata, hdi_prob=0.95)` | shows mean and HDI |

**Burn-in.** Early samples reflect the starting point, not the posterior. PyMC 5 handles this with `tune=` and discards tuning draws by default (`discard_tuned_samples=True`). PyMC3-era code sliced `trace[1000:]` by hand.

**Autocorrelation and thinning.** Metropolis chains move in small steps, so consecutive samples are correlated and carry less information than their count suggests. Thinning (keep every k-th sample) reduces storage; BMH notes k ≤ 10 is usually enough. It does not add information: ESS is what matters.

**HDI vs confidence interval.** The 95% highest-density interval is the narrowest interval containing 95% of posterior mass. Unlike a confidence interval it is a direct probability statement about the parameter.

---

## Making MCMC converge (BMH ch. 3 tips)

| Tip | How |
|---|---|
| Start in a sensible place | `initvals=pm.find_MAP()` (was `start=` in PyMC3) or the data's sample statistics |
| Use priors that rule out nonsense | bounded supports, weakly informative scales |
| Run several chains | `chains=4`; disagreement reveals multimodality |
| Prefer NUTS | let PyMC choose unless you have discrete variables |
| When it will not converge | reconsider the model |

> **The Folk Theorem of statistical computing (Gelman): "If you are having computational problems, probably your model is wrong."**

---

## PyMC3 to PyMC 5 migration map

BMH, the talk and most blog posts before 2022 use PyMC3 (Theano backend). The vendored BMH snapshot was already ported to PyMC 5; the BayesianML week 4 coursework was not, and is pinned at `pymc3==3.11.4 theano-pymc==1.1.2` (see [practice/BayesianML/](../practice/BayesianML)).

| PyMC3 | PyMC 5 |
|---|---|
| `import pymc3 as pm` | `import pymc as pm` |
| `import theano.tensor as tt` | `import pytensor.tensor as pt` |
| `sd=` | `sigma=` |
| `testval=` | `initval=` |
| `start=` / `init='MAP'` | `initvals=pm.find_MAP()` |
| `pm.traceplot`, `pm.summary`, `pm.plot_posterior` | `az.plot_trace`, `az.summary`, `az.plot_posterior` |
| `trace["x"]` (MultiTrace) | `idata.posterior["x"]` (InferenceData; `return_inferencedata=True` is now the default) |
| `trace.varnames` | `list(idata.posterior.data_vars)` |
| `trace[1000:]` for burn-in | `tune=1000` (tuned draws discarded) |
| `pm.ElemwiseCategorical` | `pm.CategoricalGibbsMetropolis` |
| `pm.glm.GLM.from_formula` | `bambi` |
| `pm.iter_sample` | removed |
| `pm.sample_posterior_predictive(trace, samples=n)` | `pm.sample_posterior_predictive(idata)`, then `idata.posterior_predictive` |

Shape gotcha: PyMC 5 samples have dimensions `(chain, draw, ...)`. Flatten with `.values.flatten()` or `az.extract(idata)` before NumPy maths written for PyMC3's flat arrays.

---

→ Next: [11-priors-and-bandits.md](03-priors-and-bandits.md) — choosing priors, why the prior stops mattering at large N, and Thompson sampling for multi-armed bandits.
