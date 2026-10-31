---
origin: own coursework
sources:
  - ../practice/BayesianML/
  - https://www.coursera.org/learn/bayesian-methods-in-machine-learning (HSE, Bayesian Methods for Machine Learning)
  - https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers (ch. 7 Bayesian Machine Learning, unfinished outline)
  - ../sources/computer age statistical inference.pdf
confidence: medium
cleaned: 2026-10-31
---
# 14 — Bayesian Machine Learning

> Where the Bayesian track meets machine learning: latent-variable models fitted with EM, Bayesian logistic regression by MCMC, variational autoencoders, and Gaussian processes driving Bayesian optimisation. A map of the BayesianML coursework, with the ideas you need to read it.

---

## Where this sits

Notes 09–13 use Bayesian inference to estimate a handful of parameters and make decisions. Machine learning applies the same ideas at scale: thousands of parameters, latent variables per data point, and posteriors too large for MCMC. The BayesianML coursework (HSE's *Bayesian Methods for Machine Learning* on Coursera) covers that ground. BMH's own ch. 7 was never finished; its outline (Bayesian answers to overfitting, Salimans' *Don't Overfit* Kaggle solution, predictive distributions, model fitting with BIC, Gaussian processes) is essentially the syllabus below.

| Coursework | Topic | Inference method | Key idea |
|---|---|---|---|
| [week_2](../practice/BayesianML/week_2/) | Gaussian mixture model | Expectation-maximisation | latent cluster labels, soft assignments |
| [week_4](../practice/BayesianML/week_4/) | Markov chains, Bayesian logistic regression | MCMC (Metropolis, NUTS) in PyMC3 | odds ratio with a credible interval |
| [week_5](../practice/BayesianML/week_5/) | Variational autoencoder on MNIST | variational inference (ELBO) | amortised posterior via an encoder network |
| [week_6](../practice/BayesianML/week_6/) | Gaussian processes, Bayesian optimisation | exact GP posterior, acquisition functions | tune hyperparameters with few evaluations |
| [final_assignment](../practice/BayesianML/final_assignment/) | "Finding the suspect": VAE + Bayesian optimisation | both | search a VAE's latent space with human feedback |

**Runnability:** legacy. The environment in `bayesian.yml` pins Python 3.7, TensorFlow 1.15, Keras 2.3.1, `pymc3==3.11.4` and `theano-pymc==1.1.2`; week 6 adds GPy, GPyOpt and xgboost by pip. Every notebook imports the Coursera `grader` module, which is not included, and none has saved outputs. Read them for the method; port to PyMC 5 with note 10's map before running.

---

## EM for Gaussian mixtures (week 2)

The mixture model from note 10, fitted by optimisation instead of sampling. Each point x_i has a hidden label t_i ∈ {1..C}; the parameters are mixture weights π, means μ_c and covariances Σ_c.

| Step | Computes | Formula |
|---|---|---|
| E-step | responsibilities γ_ic = P(t_i = c given x_i) | γ_ic ∝ π_c · N(x_i; μ_c, Σ_c), normalised over c |
| M-step | parameters given responsibilities | π_c = mean of γ_·c; μ_c = Σ γ_ic x_i / Σ γ_ic; Σ_c the γ-weighted covariance |
| Loss | variational lower bound on the log-likelihood | rises monotonically; stop when it plateaus |

```python
# week_2 structure (numpy only)
def E_step(X, pi, mu, sigma):
    # gamma[i, c] = pi[c] * N(X[i] | mu[c], sigma[c]), normalised per row
    # compute in log space (slogdet, solve) to avoid underflow
    ...
def M_step(X, gamma):
    # weighted means, covariances and weights from gamma
    ...
def train_EM(X, C, rtol=1e-3, max_iter=100, restarts=10):
    # EM finds a local optimum: run several random restarts, keep the best lower bound
    ...
```

EM vs MCMC on the same model:

| | EM | MCMC (note 10) |
|---|---|---|
| Output | a point estimate (MAP or MLE) of the parameters | samples from the full posterior |
| Speed | fast, deterministic per restart | slower |
| Uncertainty | none on the parameters | full |
| Failure | local optima, collapsing covariances | slow mixing, label switching |

---

## MCMC and Bayesian logistic regression (week 4)

**Task 1, Alice and Bob.** Two sellers set prices from each other's last price plus Gaussian noise. Simulating it, discarding a burn-in, and checking that the joint distribution is the same for any seed or start point is a hands-on Markov chain: a stationary distribution that does not depend on where you start is exactly what makes MCMC valid.

**Task 2, logistic regression on US census income** (`adult_us_postprocessed.csv`, not included): does sex affect P(income > $50K), controlling for age, age², education and hours?

```python
# week_4 (PyMC3, pinned); the PyMC 5 equivalent uses bambi or explicit priors
with pm.Model() as logistic_model:
    pm.glm.GLM.from_formula(
        "income_more_50K ~ sex + age + age_squared + educ + hours",
        data, family=pm.glm.families.Binomial())
    trace = pm.sample(4000)                      # NUTS chosen automatically

# odds ratio for sex = exp(coefficient); credible interval from the samples
b = trace["sex[T. Male]"][100:]                # short burn-in: sampling started at the MAP
lb, ub = np.percentile(b, 2.5), np.percentile(b, 97.5)
np.exp(lb), np.exp(ub)
```

The exercise compares Metropolis-Hastings (needs many samples, highly autocorrelated) with NUTS (fewer, nearly independent samples), and ends on the point note 09 makes: a credible interval can be read the way people wish they could read a confidence interval.

```python
# PyMC 5 port of the same model
import bambi as bmb
model = bmb.Model("income_more_50K ~ sex + age + age_squared + educ + hours",
                  data, family="bernoulli")
idata = model.fit(draws=4000)
```

---

## Variational inference and the VAE (week 5)

When the posterior is too big to sample, approximate it with a simpler distribution q and make q as close as possible by maximising the **evidence lower bound (ELBO)**:

```
log p(x) ≥ E_q[ log p(x | z) ] − KL( q(z | x) ‖ p(z) )
          reconstruction        regulariser
```

A variational autoencoder learns both halves with neural networks:

| Part | Role |
|---|---|
| Encoder | outputs the mean and log-variance of q(z given x): an amortised posterior |
| Reparameterisation | z = μ + σ ⊙ ε with ε ~ N(0, I), so gradients flow through the sampling |
| Decoder | p(x given z); Bernoulli per pixel for binarised MNIST |
| Prior | p(z) = N(0, I); sampling from it and decoding "hallucinates" new digits |
| Conditional VAE | condition encoder and decoder on the label to generate a chosen digit |

PyMC's `pm.fit(method="advi")` is the same idea without the encoder: one variational distribution per model rather than per data point. BMH ch. 5 uses it to initialise NUTS.

---

## Gaussian processes and Bayesian optimisation (week 6)

A **Gaussian process** is a prior over functions: any finite set of function values is jointly Normal, with covariance given by a kernel such as the RBF, k(x, x') = σ² exp(−‖x − x'‖² / 2ℓ²). Conditioning on observed points gives a posterior mean and a variance at every x: a prediction with an error bar.

```python
# week_6 (GPy)
import GPy
kernel = GPy.kern.RBF(input_dim=1, variance=1.5, lengthscale=2.)
model = GPy.models.GPRegression(X, y, kernel)
model.optimize()                      # fit kernel hyperparameters by marginal likelihood
mean, var = model.predict(X_new)
# sparse GPs (inducing points) cut the O(n^3) cost for large n
```

**Bayesian optimisation** uses the GP as a cheap surrogate for an expensive black-box function (a model's validation score as a function of its hyperparameters) and picks the next point to evaluate with an acquisition function that trades off exploration and exploitation, the same trade-off as the bandits in note 11.

| Acquisition | Picks the point with |
|---|---|
| Expected improvement | the largest expected gain over the best value so far |
| Upper confidence bound | the highest mean + κ · standard deviation |
| Probability of improvement | the highest chance of beating the best so far (GPyOpt's `MPI`, used in week 6) |

```python
# week_6 (GPyOpt): tune XGBoost hyperparameters (the notebook repeats it for an SVR)
import GPyOpt
bounds = [  # continuous variables first, then discrete
    {"name": "learning_rate", "type": "continuous", "domain": (0, 1)},
    {"name": "gamma", "type": "continuous", "domain": (0, 5)},
    {"name": "max_depth", "type": "discrete", "domain": (1, 50)},
    {"name": "n_estimators", "type": "discrete", "domain": (1, 300)},
    {"name": "min_child_weight", "type": "discrete", "domain": (1, 10)},
]
optimizer = GPyOpt.methods.BayesianOptimization(
    f=f, domain=bounds, acquisition_type="MPI", acquisition_par=0.1, exact_eval=True)
optimizer.run_optimization(max_iter=50)
```

The final project combines both: train a VAE on faces, then use Bayesian optimisation over its latent space, with a human rating each generated face, to converge on a target face (darkest hair, widest smile, a specific person) in a few dozen evaluations.

---

## Further reading

| Topic | Source |
|---|---|
| EM, VI and GPs alongside the frequentist toolkit | Efron & Hastie, *Computer Age Statistical Inference* ([sources/](../sources/computer%20age%20statistical%20inference.pdf)) |
| Bayesian regression and multilevel models in depth | McElreath, *Statistical Rethinking* ([sources/](../sources/RM-StatRethink-Bayes.pdf)) |
| Learning-focused statistics in Python | James et al., *ISLP* ([sources/](../sources/An-Introduction-to-Statistical-Learning-with-Applications-in-Python.pdf)) |
| Modern PyMC | [pymc.io examples gallery](https://www.pymc.io/projects/examples/en/latest/gallery.html), bambi |

---

→ Next: leave the statistics layer. Model building continues in [data-science](../../data-science/README.md); pipelines in [data-engineering](../../data-engineering/README.md); LLM applications in [generative-ai](../../generative-ai/README.md).
