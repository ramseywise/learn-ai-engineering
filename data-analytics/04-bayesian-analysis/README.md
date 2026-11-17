# Bayesian analysis

Treat unknowns as distributions, update them with data, and choose the action with the lowest expected cost. Five steps: infer a posterior, compute it and check the computation, turn it into a decision, carry the ideas into machine learning, and read the same test across many groups.

**What you should already know.** Nothing below is taught again here. Tick each line off, and go back to the chapter it links for any you cannot.

Probability and statistics, from [module 02](../02-probability-and-statistics/README.md):

- [ ] Use conditional probability and Bayes' rule on a small table ([probability foundations](../02-probability-and-statistics/notes/02-probability-foundations.md))
- [ ] Describe a distribution by its shape, and know the binomial, normal and Poisson ([distributions and sampling](../02-probability-and-statistics/notes/03-distributions-and-sampling.md))
- [ ] Say what a likelihood is and what an interval claims ([estimation](../02-probability-and-statistics/notes/04-estimation.md))
- [ ] Read regression output and clustered standard errors ([regression and GLMs](../02-probability-and-statistics/notes/06-regression-and-glms.md))

Experimentation, from [module 03](../03-experimentation-and-causality/README.md):

- [ ] Size, run and read the Larkspur checkout A/B test, which chapter 4 here reuses ([A/B testing](../03-experimentation-and-causality/notes/01-ab-testing.md))

## Lecture

Start with the overview deck, [Bayesian analysis](slides/bayesian-analysis.pptx) ([PDF](slides/bayesian-analysis.pdf)). It covers the module's chapters in reading order. There is one deck for the module, not one per step.

## The core

Bayesian analysis writes down how the data could have been generated, puts a prior on the unknowns, and computes the posterior: what is plausible once the data is in. When the posterior has no closed form, MCMC or variational inference approximates it. The result is a distribution you can ask direct questions of and feed into a decision.

Stakeholders ask how likely B is to be better and how much it could cost to be wrong. A p-value answers neither. A posterior answers both, carries prior knowledge into small samples, and makes the cost of a mistake part of the calculation. The same machinery sits under bandits, Bayesian optimisation and VAEs. It also has failure modes: a sampler that has not converged, a prior nobody checked, and peeking that a Bayesian label does not make safe.

Larkspur's checkout test from module 03 gets a new question. You build the update and the habit of telling a generative story on coins, Challenger and German tanks, then open the sampler, because a posterior you cannot trust is worse than none. You test priors before fitting, and turn posteriors into traffic allocation with Thompson sampling. Then you answer Larkspur: P(B > A) of 0.99999, a lift between +0.34 and +0.95 points, and a measured answer to whether peeking is safe. That posterior becomes a ship decision in dollars.

The last steps widen the frame. The same ideas carry into EM, variational inference, VAEs and Gaussian processes. They then read the test across many markets, which measures how partial pooling cuts the winning segment's exaggeration and where it does not help.

## Syllabus

One row per step. **Core concepts** are the ideas that make the step go right, **Study** is what to read, **Labs** is what to run afterwards, and **Sources** is where to read more. Read the notes in the order shown: 1b follows 1 and can wait until after 2, and 3b follows 3. Note 6 needs 1 and 2. Note 7 needs 2 and 4, plus clustered SEs from [regression](../02-probability-and-statistics/notes/06-regression-and-glms.md) and the design effect from [probability foundations](../02-probability-and-statistics/notes/02-probability-foundations.md). Note 7b follows 7. How the chapter code runs is in the Practice section below.

| Submodule | Core concepts | Study | Labs | Sources |
|---|---|---|---|---|
| **1. Infer:** the generative story and the posterior | Write the generative story first, because the model is that story in code. Use a closed form when one exists, and use it to check the sampler. Read two-parameter posteriors through marginals and conditionals, and compute a Bayes factor while knowing what it hinges on. Report an interval and a probability about the question asked, never a posterior mean alone. | [1 Bayesian inference](notes/01-bayesian-inference.md) · [1b Grids, hypotheses and simulation](notes/01b-grids-hypotheses-and-simulation.md) | None yet | Davidson-Pilon, *Bayesian Methods for Hackers* ch. 1 to 4 · McElreath, *Statistical Rethinking* ch. 1 to 3 · Downey, *Think Bayes* ch. 1 to 4, 7 and 8 · Downey, *Think Stats* ch. 8 · Gelman et al., *Bayesian Data Analysis* |
| **2. Compute and check:** MCMC, priors and empirical Bayes | A high acceptance rate is not health: at a step size of 0.002, Metropolis accepted 98.7% and kept an ESS of 11 from 19,000 draws. Look at r_hat, ESS and divergences before any result, and when a sampler struggles change the model. Simulate from the prior before you fit, because a wide prior on the logit scale is not uninformative. Priors matter most when data is thin. Shrink lifts picked as winners, since selection alone inflates them. | [2 MCMC and PyMC](notes/02-mcmc-and-pymc.md) · [3 Priors and empirical Bayes](notes/03-priors-and-bandits.md) | [BayesianML/week_4](practice/BayesianML/week_4), MCMC and Bayesian logistic regression in PyMC3 | Hoffman & Gelman, [NUTS](https://arxiv.org/abs/1111.4246) · Gelman et al., [weakly informative default prior](https://arxiv.org/abs/0901.4011) · Bishop, *PRML* ch. 11 · McElreath ch. 4 to 6 · Efron & Hastie ch. 3 and 6 · James et al., *ISLP* ch. 6 |
| **3. Decide:** bandits, A/B tests and loss | Thompson sampling draws once per arm posterior and plays the highest, so exploration fades as evidence grows. A bandit saves traffic but biases arm means, so run a fixed split for the effect you report. P(B > A) says nothing about size, so report the lift interval beside it. Peeking is not free: stopping daily on P(B > A) shipped 24% of no-effect tests against 5% at the last look alone. Pick the point estimate from the loss, and put the decision in the business's own units. | [3b Bandits and Thompson sampling](notes/03b-bandits-and-thompson-sampling.md) · [4 Bayesian A/B testing](notes/04-bayesian-ab-testing.md) · [5 Loss functions and decisions](notes/05-loss-functions-and-decisions.md) | None yet | Davidson-Pilon ch. 5 · Sutton & Barto ch. 2 · Lattimore & Szepesvári ch. 34 to 36 · Downey, *Think Bayes* ch. 6 · Efron & Hastie ch. 3 · Evan Miller, [Formulas for Bayesian A/B testing](https://www.evanmiller.org/bayesian-ab-testing.html) · Stucchio, [Bayesian A/B decision rule](https://www.chrisstucchio.com/blog/2014/bayesian_ab_decision_rule.html) |
| **4. Bayesian machine learning:** EM, variational inference and GPs | Restart EM, because it finds local optima and one run cannot tell you which you got. Mean-field ADVI is fast and understates correlated uncertainty, so check it against NUTS on a small version. | [6 Bayesian machine learning](notes/06-bayesian-machine-learning.md) | [BayesianML/week_2](practice/BayesianML/week_2), EM for a Gaussian mixture · [BayesianML/week_5](practice/BayesianML/week_5), a VAE on MNIST · [BayesianML/week_6](practice/BayesianML/week_6), Gaussian processes and Bayesian optimisation · [BayesianML/final_assignment](practice/BayesianML/final_assignment), a VAE with Bayesian optimisation | Bishop, *PRML* ch. 9 to 11 · Efron & Hastie · Blei et al., [Variational Inference: A Review](https://arxiv.org/abs/1601.00670) · Kingma & Welling, [Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) · Rasmussen & Williams, *Gaussian Processes for Machine Learning* · Dempster, Laird & Rubin (1977) |
| **5. Many groups:** multilevel models and partial pooling | Cluster when groups are a nuisance, and model them when they are the question. Partially pool many segment effects first: the raw winner overstated its true lift by 2.93 in the chapter's simulation, and the pooled winner by 0.09. With a handful of groups the between-group spread is barely known, so run several priors and report the range. | [7 Multilevel models and partial pooling](notes/07-multilevel-models-and-partial-pooling.md) · [7b Varying slopes, measurement error and missing data](notes/07b-varying-slopes-measurement-error-and-missing-data.md) | [ch07_multilevel_models.py](practice/ch07_multilevel_models.py), the chapter 7 simulations | McElreath, *Statistical Rethinking* (2015 draft) ch. 12 and 13 · Gelman, Hill & Yajima, [multiple comparisons and partial pooling](https://arxiv.org/abs/0907.2478) · McNeish, Stapleton & Silverman (2017) · Bell & Jones (2015) · Gelman & Hill, *Data Analysis Using Regression and Multilevel/Hierarchical Models* |

Every source and the notes it maps to: [references.md](references.md).

## Rules of thumb

**Inference** ([1](notes/01-bayesian-inference.md))
- **Write the generative story first.** The model is that story in code.
- **Use a closed form when one exists,** and use it to check the sampler.
- **Report an interval and a probability about the question asked,** never a posterior mean alone.

**Sampling** ([2](notes/02-mcmc-and-pymc.md))
- **A high acceptance rate is not health.** At a step size of 0.002, Metropolis accepted 98.7% and kept an ESS of 11 from 19,000 draws.
- **Look at r_hat, ESS and divergences before you look at any result.**
- **When a sampler struggles, change the model:** standardise, marginalise or use a non-centred form.

**Priors** ([3](notes/03-priors-and-bandits.md))
- **Simulate from the prior before you fit.** A wide prior on the logit scale is not uninformative.
- **Priors matter most when data is thin,** and wash out as it grows.
- **Shrink lifts picked as winners.** Selection alone inflates them.

**Bandits** ([3b](notes/03b-bandits-and-thompson-sampling.md))
- **Thompson sampling draws once per arm posterior and plays the highest,** so exploration fades as evidence grows.
- **A bandit saves traffic but biases arm means,** so run a fixed split for the effect you report.

**A/B testing** ([4](notes/04-bayesian-ab-testing.md))
- **P(B > A) says nothing about size.** Report the lift interval beside it.
- **Peeking is not free.** Stopping daily on P(B > A) shipped 24% of no-effect tests in the chapter's simulation, against 5% at the last look alone.
- **Set the stopping rule and its threshold before the test starts.**

**Decisions** ([5](notes/05-loss-functions-and-decisions.md))
- **Pick the point estimate from the loss.** The mean, median and mode each answer a different loss.
- **Put the decision in the business's own units,** with the cost of being wrong.

**Bayesian ML** ([6](notes/06-bayesian-machine-learning.md))
- **Restart EM.** It finds local optima, and a single run cannot tell you which one you got.
- **Mean-field ADVI is fast and understates correlated uncertainty.** Check it against NUTS on a small version.

**Multilevel models** ([7](notes/07-multilevel-models-and-partial-pooling.md))
- **Cluster when groups are a nuisance, model them when they are the question.**
- **Reading many segment effects? Partially pool them first.** The raw winner overstated its true lift by 2.93 in the chapter's simulation, and the pooled winner by 0.09.
- **With a handful of groups the between-group spread is barely known,** so run several priors and report the range.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| None in other subjects | Starts from [DA 02](../02-probability-and-statistics/README.md) in this subject |

**Feeds into**

| Chapter | Why |
|---|---|
| [DS 03/03 Topic models and summarization](../../data-science/03-nlp/notes/03-topic-models-and-summarization.md) | LDA is Bayesian inference with conjugate priors |
| [GA 05/01c Bandits](../../generative-ai/05-RL/notes/01c-bandit-algorithms.md) | Bandits lead into regret bounds, contextual bandits and RL ([01 RL foundations](../../generative-ai/05-RL/notes/01-rl-foundations.md)) |
| [AIE 04/08 Self-improving loops](../../ai-engineering/04-loop-engineering/notes/08-self-improving-loops.md) | A Bayesian bandit shifts live traffic between candidates |
| [DS 05/03 Two-tower and evaluation](../../data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md) | Segment effects read with partial pooling (the pointer back from that chapter is still to come) |

<a id="deck-and-practice"></a>

## Practice

Every code block in the chapters runs top to bottom as a notebook, on PyMC 6.4 and ArviZ 1.3 with fixed seeds:

```bash
uv run --with pymc --with arviz --with scipy --with scikit-learn python
```

Three legacy blocks in chapter 6 are marked `# illustrative`, because they show the coursework's PyMC3, GPy and GPyOpt code and need its pinned environment. Chapter 7 shows the core of each simulation, and its runnable form is [practice/ch07_multilevel_models.py](practice/ch07_multilevel_models.py): run `uv run ch07_multilevel_models.py` from that folder. It also needs `statsmodels` and the chart helpers in [06/practice](../06-applied-analyses/practice/chartstyle.py).

The coursework in [practice/BayesianML/](practice/BayesianML) is kept as written, with no saved outputs. It targets Python 3.7, TensorFlow 1.15, Keras 2.3.1, `pymc3==3.11.4` and `theano-pymc==1.1.2`, set up with [bayesian.yml](practice/BayesianML/bayesian.yml). The course grader is not included, and these notebooks are not run by the repo checks.

| Folder | What it is | How to run |
|---|---|---|
| [week_2](practice/BayesianML/week_2) | EM for a Gaussian mixture | Notebook, in the pinned environment |
| [week_4](practice/BayesianML/week_4) | MCMC and Bayesian logistic regression in PyMC3 | Notebook, in the pinned environment |
| [week_5](practice/BayesianML/week_5) | Variational autoencoder on MNIST | Notebook, in the pinned environment |
| [week_6](practice/BayesianML/week_6) | Gaussian processes and Bayesian optimisation | Also needs GPy, GPyOpt and xgboost, installed with pip |
| [final_assignment](practice/BayesianML/final_assignment) | "Finding the suspect": a VAE with Bayesian optimisation | Notebook with `utils.py`, in the pinned environment |

The deck is built from [slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=data-analytics/04-bayesian-analysis STRICT=1 PREVIEW=1`.

## Primary texts

- Davidson-Pilon, *Bayesian Methods for Hackers*: the spine of this module
- McElreath, *Statistical Rethinking*
- Gelman and Hill, *Data Analysis Using Regression and Multilevel/Hierarchical Models*: further reading
- Downey, *Think Bayes*

Everything else: [references.md](references.md).

## Next

Start with submodule 1, **Infer**: read [1 Bayesian inference](notes/01-bayesian-inference.md), then the other notes in the syllabus order.

After submodule 5 you can write a generative model, fit it and check the sampler, turn a posterior into a decision priced in business units, and read many segment effects with partial pooling. This is the last module of [data analytics](../README.md#completion-standard-and-next-steps).
