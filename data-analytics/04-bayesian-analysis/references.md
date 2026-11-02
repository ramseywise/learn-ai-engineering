---
origin: curated
sources:
  - ../sources/
  - ../references.md
confidence: high
cleaned: 2026-11-01
---
# Bayesian Analysis — References

> The sources behind the chapters in [notes/](notes/), mapped to what they support. PDFs live in the shared [sources/](../sources/) folder. Course index: [README](README.md). ★ marks reading that changed a claim in a note.

---

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| ★ Davidson-Pilon, [*Bayesian Methods for Hackers*](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers) | Ch. 1 to 6, the spine of this pillar. Reading it corrected several attributions, such as the text-message data being one user's | [sample](../sources/bayes_for_hackers.pdf) | [1](notes/01-bayesian-inference.md) to [6](notes/06-bayesian-machine-learning.md) |
| McElreath, *Statistical Rethinking* | Generative models and prior predictive simulation | [held](../sources/RM-StatRethink-Bayes.pdf) | [1](notes/01-bayesian-inference.md), [3](notes/03-priors-and-bandits.md), [6](notes/06-bayesian-machine-learning.md) |
| Gelman et al., [*Bayesian Data Analysis*](https://sites.stat.columbia.edu/gelman/book/) | Reference text; the eight-schools data | not held | [1](notes/01-bayesian-inference.md), [2](notes/02-mcmc-and-pymc.md), [3](notes/03-priors-and-bandits.md) |
| Downey, [*Think Bayes*](https://greenteapress.com/wp/think-bayes/) | The same ideas in plain Python | [held](../sources/think_bayes.pdf) | [1](notes/01-bayesian-inference.md) |
| Efron and Hastie, [*Computer Age Statistical Inference*](https://hastie.su.domains/CASI/) | EM, variational methods and GPs beside the frequentist toolkit | [held](../sources/computer%20age%20statistical%20inference.pdf) | [6](notes/06-bayesian-machine-learning.md) |
| Rasmussen and Williams, [*Gaussian Processes for Machine Learning*](http://gaussianprocess.org/gpml/) | GP regression, free online | not held | [6](notes/06-bayesian-machine-learning.md) |
| Silver, *The Signal and the Noise* | Weather forecasters and asymmetric loss, reached through BMH ch. 5 | not held | [5](notes/05-loss-functions-and-decisions.md) |

---

## Core papers

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| [Gelman, Jakulin, Pittau and Su, AOAS 2008](https://arxiv.org/abs/0901.4011) | Weakly informative default prior for logistic regression, and how it handles separation | [held](../sources/gelman-2009-weakly-informative-default-prior-distribution.pdf) | [3](notes/03-priors-and-bandits.md) |
| [Hoffman and Gelman, JMLR 2014](https://arxiv.org/abs/1111.4246) | NUTS, the sampler behind `pm.sample` | [held](../sources/hoffman-2011-no-u-turn-sampler.pdf) | [2](notes/02-mcmc-and-pymc.md), [6](notes/06-bayesian-machine-learning.md) |
| [Blei, Kucukelbir and McAuliffe, JASA 2017](https://arxiv.org/abs/1601.00670) | Review of variational inference and the ELBO | [held](../sources/blei-2016-variational-inference.pdf) | [6](notes/06-bayesian-machine-learning.md) |
| [Dempster, Laird and Rubin, JRSSB 1977](https://doi.org/10.1111/j.2517-6161.1977.tb01600.x) | The original EM paper | not held | [6](notes/06-bayesian-machine-learning.md) |
| [Kingma and Welling, 2013](https://arxiv.org/abs/1312.6114) | The variational autoencoder and the reparameterisation trick | not held | [6](notes/06-bayesian-machine-learning.md) |
| [Snoek, Larochelle and Adams, NeurIPS 2012](https://proceedings.neurips.cc/paper/2012/hash/05311655a15b75fab86956663e1819cd-Abstract.html) | Bayesian optimisation for machine-learning hyperparameters | not held | [6](notes/06-bayesian-machine-learning.md) |
| [Chapelle and Li, NeurIPS 2011](https://proceedings.neurips.cc/paper/2011/hash/e53a0a2978c28872a4505bdb51db06dc-Abstract.html) | Empirical evaluation of Thompson sampling | not held (abstract read) | [3](notes/03-priors-and-bandits.md) |
| [Agrawal and Goyal, COLT 2012](https://proceedings.mlr.press/v23/agrawal12.html) | Logarithmic regret analysis of Thompson sampling | not held (abstract read) | [3](notes/03-priors-and-bandits.md) |
| [Kaufmann, Cappé and Garivier, AISTATS 2012](http://proceedings.mlr.press/v22/kaufmann12/kaufmann12.pdf) | Finite-time analysis of Thompson sampling | not held (abstract read) | [3](notes/03-priors-and-bandits.md) |
| [Lai and Robbins, Adv. Appl. Math. 1985](https://doi.org/10.1016/0196-8858(85)90002-8) | The lower bound on bandit regret | not held | [3](notes/03-priors-and-bandits.md) |
| [Warner, JASA 1965](https://doi.org/10.1080/01621459.1965.10480775) | Randomised response | not held | [1](notes/01-bayesian-inference.md) |
| [Dalal, Fowlkes and Hoadley, JASA 1989](https://doi.org/10.1080/01621459.1989.10478858) | The statistical analysis of the Challenger O-ring data | not held | [1](notes/01-bayesian-inference.md) |
| [Evan Miller, Formulas for Bayesian A/B testing](https://www.evanmiller.org/bayesian-ab-testing.html) | Closed forms for P(B > A) | web | [4](notes/04-bayesian-ab-testing.md) |
| [Chris Stucchio, Bayesian A/B decision rule](https://www.chrisstucchio.com/blog/2014/bayesian_ab_decision_rule.html) | Expected loss as a stopping rule | web | [4](notes/04-bayesian-ab-testing.md) |
| [prasoon2211, Bayesian inference talk](https://github.com/prasoon2211/bayesian_inference_talk) | Recommended reading path and the MCMC walkthrough | web | [1](notes/01-bayesian-inference.md), [2](notes/02-mcmc-and-pymc.md) |

---

## Courses and videos

| Resource | Platform, cost | Supports | Which part |
|---|---|---|---|
| [Statistical Rethinking 2023](https://www.youtube.com/playlist?list=PLDcUM9US4XdPz-KxHM4XHt7uUVGWWVSus), McElreath; [2024 course repo](https://github.com/rmcelreath/stat_rethinking_2024) | YouTube and GitHub, free | [1](notes/01-bayesian-inference.md), [3](notes/03-priors-and-bandits.md), [6](notes/06-bayesian-machine-learning.md) | The full lecture series; prior predictive simulation throughout |
| [Bayesian Data Analysis](https://avehtari.github.io/BDA_course_Aalto/), Vehtari, Aalto CS-E5710 | Course site with videos, free | [2](notes/02-mcmc-and-pymc.md), [3](notes/03-priors-and-bandits.md) | Computation, MCMC diagnostics and priors |
| [Bayes' theorem](https://www.youtube.com/watch?v=HZGCoVF3YvM), 3Blue1Brown | YouTube, free | [1](notes/01-bayesian-inference.md) | The whole video, for the geometry of the update |
| [StatQuest](https://www.youtube.com/@statquest), Starmer | YouTube, free | [1](notes/01-bayesian-inference.md) | Search the channel for Bayes and for maximum likelihood |

The Coursera course behind `practice/BayesianML/` (HSE, Bayesian Methods for Machine Learning) now returns a 404 at the address in that folder's README, so it has no row here.

---

## Tools

- [PyMC](https://www.pymc.io/) and its [examples gallery](https://www.pymc.io/projects/examples/en/latest/gallery.html). The chapters run on PyMC 6.4.
- [ArviZ](https://python.arviz.org/), for diagnostics and summaries. The chapters run on ArviZ 1.3.
- [bambi](https://bambinos.github.io/bambi/), a formula interface over PyMC. Linked from the chapters but not run in them.
