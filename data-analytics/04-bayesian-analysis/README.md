# 04 — Bayesian Analysis

> Treat unknowns as distributions, update them with data, and choose the action with the lowest expected cost.
> Jump to: [Reading order](#reading-order) · [Rules of thumb](#rules-of-thumb) · [Deck and practice](#deck-and-practice) · [References](references.md)

---

## What it is

Bayesian analysis writes down how the data could have been generated, puts a prior on the unknowns, and computes the posterior: what is plausible once the data is in. When the posterior has no closed form, MCMC or variational inference approximates it. The result is a distribution you can ask direct questions of and feed into a decision.

## Why it matters

Stakeholders ask how likely B is to be better and how much it could cost to be wrong. A p-value answers neither. A posterior answers both, carries prior knowledge into small samples, and makes the cost of a mistake part of the calculation. The same machinery sits under bandits, Bayesian optimisation and VAEs. It also has failure modes: a sampler that has not converged, a prior nobody checked, and peeking that a Bayesian label does not make safe.

## The story

Larkspur's checkout test from the previous pillar gets a new question. [Chapter 1](notes/01-bayesian-inference.md) builds the update and the habit of telling a generative story, on coins, Challenger and German tanks. [Chapter 2](notes/02-mcmc-and-pymc.md) opens the sampler, because a posterior you cannot trust is worse than none. [Chapter 3](notes/03-priors-and-bandits.md) tests priors before fitting and turns posteriors into traffic allocation with Thompson sampling. [Chapter 4](notes/04-bayesian-ab-testing.md) answers Larkspur: P(B > A) of 0.99999, a lift between +0.34 and +0.95 points, and a measured answer to whether peeking is safe. [Chapter 5](notes/05-loss-functions-and-decisions.md) turns that posterior into a ship decision in dollars. [Chapter 6](notes/06-bayesian-machine-learning.md) carries the same ideas into EM, variational inference, VAEs and Gaussian processes. [Chapter 7](notes/07-multilevel-models-and-partial-pooling.md) reads the test across many markets, and measures how partial pooling cuts the winning segment's exaggeration and where it doesn't help. [Chapter 7b](notes/07b-varying-slopes-measurement-error-and-missing-data.md) adds correlated varying slopes, effective parameters, and what to do with noisy and missing predictors.

---

## Reading order

| # | Chapter | You will be able to |
|---|---|---|
| 1 | [Bayesian inference](notes/01-bayesian-inference.md) | Write a generative model, compute a Beta-Binomial posterior by hand and fit the same model in PyMC |
| 1b | [Grids, hypotheses and simulation](notes/01b-grids-hypotheses-and-simulation.md) | Read two-parameter posteriors through marginals and conditionals, compute a Bayes factor and say what it hinges on, and simulate a joint distribution |
| 2 | [MCMC and PyMC](notes/02-mcmc-and-pymc.md) | Explain one Metropolis step, read r_hat, ESS and divergences, and fix a sampler by reparameterising |
| 3 | [Priors and bandits](notes/03-priors-and-bandits.md) | Run a prior predictive check, pick a default prior for logistic regression, and implement Thompson sampling |
| 4 | [Bayesian A/B testing](notes/04-bayesian-ab-testing.md) | Report P(B > A), a lift interval and expected loss, and say what peeking does to each |
| 5 | [Loss functions and decisions](notes/05-loss-functions-and-decisions.md) | Choose the action that minimises expected loss, and price a ship decision |
| 6 | [Bayesian machine learning](notes/06-bayesian-machine-learning.md) | Derive EM and the ELBO, see where ADVI underestimates uncertainty, and run a GP with Bayesian optimisation |
| 7 | [Multilevel models and partial pooling](notes/07-multilevel-models-and-partial-pooling.md) | Fit random intercepts and slopes in `MixedLM` and PyMC, choose between clustered SEs, fixed effects and a multilevel model, and say when partial pooling does not help |
| 7b | [Varying slopes, measurement error and missing data](notes/07b-varying-slopes-measurement-error-and-missing-data.md) | Count effective parameters, fit correlated varying slopes with a non-centred form, and model measurement error and missing predictors instead of ignoring them |

Read 1 to 5 in order (1b follows 1 and can wait until after 2). Chapter 6 needs 1 and 2, and is the map for the [BayesianML coursework](practice/BayesianML). Chapter 7b follows 7. Chapter 7 needs 2 and 4, plus clustered SEs from [regression](../02-probability-and-statistics/notes/06-regression-and-glms.md) and the design effect from [probability foundations](../02-probability-and-statistics/notes/02-probability-foundations.md). Earlier pillars: [probability and statistics](../02-probability-and-statistics/README.md) and [experimentation](../03-experimentation-and-causality/README.md), whose Larkspur test chapter 4 reuses.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| None in other subjects | Starts from [DA 02](../02-probability-and-statistics/README.md) in this subject |

**Feeds into**

| Chapter | Why |
|---|---|
| [DS 03/03 Topic models and summarization](../../data-science/03-nlp/notes/03-topic-models-and-summarization.md) | LDA is Bayesian inference with conjugate priors |
| [GA 05/01 RL foundations](../../generative-ai/05-RL/notes/01-rl-foundations.md) | Bandits lead into contextual bandits and RL |
| [AIE 04/08 Self-improving loops](../../ai-engineering/04-loop-engineering/notes/08-self-improving-loops.md) | A Bayesian bandit shifts live traffic between candidates |
| [DS 05/03 Two-tower and evaluation](../../data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md) | Segment effects read with partial pooling (the pointer back from that chapter is still to come) |

---

## Rules of thumb

**Inference** ([1](notes/01-bayesian-inference.md))
- Write the generative story first. The model is that story in code.
- Use a closed form when one exists, and use it to check the sampler.
- Report an interval and a probability about the question asked, never a posterior mean alone.

**Sampling** ([2](notes/02-mcmc-and-pymc.md))
- A high acceptance rate is not health. At a step size of 0.002, Metropolis accepted 98.7% and kept an ESS of 11 from 19,000 draws.
- Look at r_hat, ESS and divergences before you look at any result.
- When a sampler struggles, change the model: standardise, marginalise or use a non-centred form.

**Priors and bandits** ([3](notes/03-priors-and-bandits.md))
- Simulate from the prior before you fit. A wide prior on the logit scale is not uninformative.
- Priors matter most when data is thin, and wash out as it grows.
- Shrink lifts picked as winners. Selection alone inflates them.

**A/B testing** ([4](notes/04-bayesian-ab-testing.md))
- P(B > A) says nothing about size. Report the lift interval beside it.
- Peeking is not free: stopping daily on P(B > A) shipped 24% of no-effect tests in the chapter's simulation, against 5% at the last look alone.
- Set the stopping rule and its threshold before the test starts.

**Decisions** ([5](notes/05-loss-functions-and-decisions.md))
- Pick the point estimate from the loss. The mean, median and mode each answer a different loss.
- Put the decision in the business's own units, with the cost of being wrong.

**Bayesian ML** ([6](notes/06-bayesian-machine-learning.md))
- Restart EM. It finds local optima, and a single run cannot tell you which one you got.
- Mean-field ADVI is fast and understates correlated uncertainty. Check it against NUTS on a small version.

**Multilevel models** ([7](notes/07-multilevel-models-and-partial-pooling.md))
- Cluster when groups are a nuisance, model them when they are the question.
- Reading many segment effects? Partially pool them first. The raw winner overstated its true lift by 2.93 in the chapter's simulation, and the pooled winner by 0.09.
- With a handful of groups the between-group spread is barely known, so run several priors and report the range.

---

## Deck and practice

**Deck:** [slides/bayesian-analysis.pptx](slides/bayesian-analysis.pptx) ([PDF](slides/bayesian-analysis.pdf)), built from [slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=data-analytics/04-bayesian-analysis STRICT=1 PREVIEW=1`.

**Chapters:** every code block runs top to bottom as a notebook, on PyMC 6.4 and ArviZ 1.3 with fixed seeds:

```bash
uv run --with pymc --with arviz --with scipy --with scikit-learn python
```

Three legacy blocks in chapter 6 are marked `# illustrative`, because they show the coursework's PyMC3, GPy and GPyOpt code and need its pinned environment. Chapter 7 shows the core of each simulation, and its runnable form is [practice/ch07_multilevel_models.py](practice/ch07_multilevel_models.py): run `uv run ch07_multilevel_models.py` from that folder. It also needs `statsmodels` and the chart helpers in [06/practice](../06-applied-analyses/practice/chartstyle.py).

**Practice:** the coursework in [practice/BayesianML/](practice/BayesianML) is kept as written, with no saved outputs. It targets Python 3.7, TensorFlow 1.15, Keras 2.3.1, `pymc3==3.11.4` and `theano-pymc==1.1.2`, set up with [bayesian.yml](practice/BayesianML/bayesian.yml). The course grader is not included, and these notebooks are not run by the repo checks.

| Folder | What it is | How to run |
|---|---|---|
| [week_2](practice/BayesianML/week_2) | EM for a Gaussian mixture | Notebook, in the pinned environment |
| [week_4](practice/BayesianML/week_4) | MCMC and Bayesian logistic regression in PyMC3 | Notebook, in the pinned environment |
| [week_5](practice/BayesianML/week_5) | Variational autoencoder on MNIST | Notebook, in the pinned environment |
| [week_6](practice/BayesianML/week_6) | Gaussian processes and Bayesian optimisation | Also needs GPy, GPyOpt and xgboost, installed with pip |
| [final_assignment](practice/BayesianML/final_assignment) | "Finding the suspect": a VAE with Bayesian optimisation | Notebook with `utils.py`, in the pinned environment |

## Primary texts

- Davidson-Pilon, *Bayesian Methods for Hackers*: the spine of this pillar
- McElreath, *Statistical Rethinking*
- Gelman and Hill, *Data Analysis Using Regression and Multilevel/Hierarchical Models*: further reading
- Downey, *Think Bayes*

Everything else: [references.md](references.md).

**Next:** [05 Visualisation and Storytelling](../05-visualisation-and-storytelling/README.md), for putting these answers in front of people. **References:** [references.md](references.md).
