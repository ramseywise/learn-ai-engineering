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
| McElreath, *Statistical Rethinking* | Generative models and prior predictive simulation; in the held 2015 draft, ch. 12 (multilevel models, including 12.2 on underfitting and overfitting) and ch. 13 (varying slopes). Numbers are the draft's, and published editions may differ | [held](../sources/RM-StatRethink-Bayes.pdf) | [1](notes/01-bayesian-inference.md), [3](notes/03-priors-and-bandits.md), [6](notes/06-bayesian-machine-learning.md), [7](notes/07-multilevel-models-and-partial-pooling.md) |
| Gelman and Hill, [*Data Analysis Using Regression and Multilevel/Hierarchical Models*](https://sites.stat.columbia.edu/gelman/arm/) (Cambridge, 2007) | The standard multilevel text. Listed as further reading, and no claim in the chapter rests on it | not held | [7](notes/07-multilevel-models-and-partial-pooling.md) |
| Snijders and Bosker, *Multilevel Analysis*, 2nd ed. (SAGE, 2012) | The social-science reference. Listed as further reading; the 20-group rule in the chapter is reported through McNeish et al. | not held | [7](notes/07-multilevel-models-and-partial-pooling.md) |
| Gelman et al., [*Bayesian Data Analysis*](https://sites.stat.columbia.edu/gelman/book/) | Reference text; the eight-schools data | not held | [1](notes/01-bayesian-inference.md), [2](notes/02-mcmc-and-pymc.md), [3](notes/03-priors-and-bandits.md) |
| ★ Downey, [*Think Bayes*](https://greenteapress.com/wp/think-bayes/) (Green Tea Press, 2012; first edition, Python 2 code). Chapter PDFs in [sources/think-bayes/](../sources/think-bayes/). Folded in as: ch. 1–2 → [1](notes/01-bayesian-inference.md) (the table method, Monty Hall, the update function); ch. 3 → [1](notes/01-bayesian-inference.md), [3](notes/03-priors-and-bandits.md) (dice, locomotives, prior sensitivity); ch. 4 → [1](notes/01-bayesian-inference.md), [3](notes/03-priors-and-bandits.md) (the Euro coin, swamping, Cromwell's rule); ch. 7 → [1](notes/01-bayesian-inference.md) (the Bruins problem: posterior predictive as a mixture, and series odds of 57% against 80% under two priors, re-run); ch. 6 → [5](notes/05-loss-functions-and-decisions.md) (the Price is Right with an empirical prior and a rival; numbers are the book's, the showcase CSVs are not held); ch. 8 → [1](notes/01-bayesian-inference.md) (the Red Line: length-biased sampling, elapsed time as the latent, Poisson likelihood, rate posterior and mixture; the 5/10-minute example re-run, the collected gap data is not held, the 80% and the 30-passenger threshold are read from the book); ch. 5 → [1](notes/01-bayesian-inference.md) (odds form, Bayes factor, Oliver's blood; the sums, maxima and mixtures of dice are distribution arithmetic the chapter itself calls not specifically Bayesian, so only the mixture idea is carried on, in ch. 7). Notes cite it as `(*Think Bayes*, ch. N)` | [full text held](../sources/think_bayes.pdf) | [1](notes/01-bayesian-inference.md), [3](notes/03-priors-and-bandits.md), [5](notes/05-loss-functions-and-decisions.md) |
| Efron and Hastie, [*Computer Age Statistical Inference*](https://hastie.su.domains/CASI/) | EM, variational methods and GPs beside the frequentist toolkit | [held](../sources/computer%20age%20statistical%20inference.pdf) | [6](notes/06-bayesian-machine-learning.md) |
| Rasmussen and Williams, [*Gaussian Processes for Machine Learning*](http://gaussianprocess.org/gpml/) | GP regression, free online | not held | [6](notes/06-bayesian-machine-learning.md) |
| Silver, *The Signal and the Noise* | Weather forecasters and asymmetric loss, reached through BMH ch. 5 | not held | [5](notes/05-loss-functions-and-decisions.md) |

---

## Core papers

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| [Gelman, Jakulin, Pittau and Su, AOAS 2008](https://arxiv.org/abs/0901.4011) | Weakly informative default prior for logistic regression, and how it handles separation | [held](../sources/gelman-2009-weakly-informative-default-prior-distribution.pdf) | [3](notes/03-priors-and-bandits.md) |
| [Hoffman and Gelman, JMLR 2014](https://arxiv.org/abs/1111.4246) | NUTS, the sampler behind `pm.sample` | [held](../sources/hoffman-2011-no-u-turn-sampler.pdf) | [2](notes/02-mcmc-and-pymc.md), [6](notes/06-bayesian-machine-learning.md) |
| ★ [Blei, Kucukelbir and McAuliffe, JASA 2017](https://arxiv.org/abs/1601.00670) | Review of variational inference, the ELBO, CAVI and SVI. CAVI fit a 30-cluster mixture to 10,000 images in under a minute, orders of magnitude faster than Stan's HMC-based sampler, but VI generally underestimates variance and its accuracy relative to MCMC is left "unknown". Corrected chapter 6, which credited it with the reparameterisation trick | [held](../sources/blei-2016-variational-inference.pdf) | [2](notes/02-mcmc-and-pymc.md), [6](notes/06-bayesian-machine-learning.md) |
| [Dempster, Laird and Rubin, JRSSB 1977](https://doi.org/10.1111/j.2517-6161.1977.tb01600.x) | The original EM paper | not held | [6](notes/06-bayesian-machine-learning.md) |
| [Kingma and Welling, 2013](https://arxiv.org/abs/1312.6114) | The variational autoencoder and the reparameterisation trick | not held | [6](notes/06-bayesian-machine-learning.md) |
| [Snoek, Larochelle and Adams, NeurIPS 2012](https://proceedings.neurips.cc/paper/2012/hash/05311655a15b75fab86956663e1819cd-Abstract.html) | Bayesian optimisation for machine-learning hyperparameters | not held | [6](notes/06-bayesian-machine-learning.md) |
| [Chapelle and Li, NeurIPS 2011](https://proceedings.neurips.cc/paper/2011/hash/e53a0a2978c28872a4505bdb51db06dc-Abstract.html) | Empirical evaluation of Thompson sampling | not held (abstract read) | [3](notes/03-priors-and-bandits.md) |
| [Agrawal and Goyal, COLT 2012](https://proceedings.mlr.press/v23/agrawal12.html) | Logarithmic regret analysis of Thompson sampling | not held (abstract read) | [3](notes/03-priors-and-bandits.md) |
| [Kaufmann, Cappé and Garivier, AISTATS 2012](http://proceedings.mlr.press/v22/kaufmann12/kaufmann12.pdf) | Finite-time analysis of Thompson sampling | not held (abstract read) | [3](notes/03-priors-and-bandits.md) |
| [Lai and Robbins, Adv. Appl. Math. 1985](https://doi.org/10.1016/0196-8858(85)90002-8) | The lower bound on bandit regret | not held | [3](notes/03-priors-and-bandits.md) |
| [Warner, JASA 1965](https://doi.org/10.1080/01621459.1965.10480775) | Randomised response | not held | [1](notes/01-bayesian-inference.md) |
| [Dalal, Fowlkes and Hoadley, JASA 1989](https://doi.org/10.1080/01621459.1989.10478858) | The statistical analysis of the Challenger O-ring data | not held | [1](notes/01-bayesian-inference.md) |
| ★ [Gelman, Hill and Yajima, J. Research on Educational Effectiveness 2012](https://arxiv.org/abs/0907.2478) | Partial pooling moves estimates together where classical corrections widen intervals; the argument behind the A/B application, read with the caveat below | not held (open preprint read in full) | [7](notes/07-multilevel-models-and-partial-pooling.md) |
| [Gelman and Loken, *The garden of forking paths*, 2013](https://sites.stat.columbia.edu/gelman/research/unpublished/p_hacking.pdf) | Unpublished working paper. Multilevel modelling's practical difficulties "are not trivial", and small or highly structured problems are sensitive to assumptions: the caveat on the 2012 paper | not held (read, case studies sampled) | [7](notes/07-multilevel-models-and-partial-pooling.md) |
| ★ [McNeish, Stapleton and Silverman, Psychological Methods 2017](https://doi.org/10.1037/met0000078) | Clustered data does not by itself call for a multilevel model; clustered SEs and GEE when the groups are a nuisance | not held (read in full) | [7](notes/07-multilevel-models-and-partial-pooling.md) |
| ★ [Bell and Jones, Political Science Research and Methods 2015](https://eprints.whiterose.ac.uk/89757) | The counter-case: a within-between random-effects model does what fixed effects do, and more | not held (open access, read in full) | [7](notes/07-multilevel-models-and-partial-pooling.md) |
| [Cameron and Miller, J. Human Resources 2015](https://doi.org/10.3368/jhr.50.2.317) | Fixed effects still need clustered SEs, and how few clusters is too few. Read in the authors' draft, and only those sections | not held (partly read) | [7](notes/07-multilevel-models-and-partial-pooling.md) |
| [Evan Miller, Formulas for Bayesian A/B testing](https://www.evanmiller.org/bayesian-ab-testing.html) | Closed forms for P(B > A) | web | [4](notes/04-bayesian-ab-testing.md) |
| [Chris Stucchio, Bayesian A/B decision rule](https://www.chrisstucchio.com/blog/2014/bayesian_ab_decision_rule.html) | Expected loss as a stopping rule | web | [4](notes/04-bayesian-ab-testing.md) |
| [prasoon2211, Bayesian inference talk](https://github.com/prasoon2211/bayesian_inference_talk) | Recommended reading path and the MCMC walkthrough | web | [1](notes/01-bayesian-inference.md), [2](notes/02-mcmc-and-pymc.md) |

---

## Courses and videos

| Resource | Platform, cost | Supports | Which part |
|---|---|---|---|
| [Statistical Rethinking 2023](https://www.youtube.com/playlist?list=PLDcUM9US4XdPz-KxHM4XHt7uUVGWWVSus), McElreath; [2024 course repo](https://github.com/rmcelreath/stat_rethinking_2024) | YouTube and GitHub, free | [1](notes/01-bayesian-inference.md), [3](notes/03-priors-and-bandits.md), [6](notes/06-bayesian-machine-learning.md), [7](notes/07-multilevel-models-and-partial-pooling.md) | The full lecture series; prior predictive simulation throughout; the multilevel lectures for chapter 7 |
| [Bayesian Data Analysis](https://avehtari.github.io/BDA_course_Aalto/), Vehtari, Aalto CS-E5710 | Course site with videos, free | [2](notes/02-mcmc-and-pymc.md), [3](notes/03-priors-and-bandits.md) | Computation, MCMC diagnostics and priors |
| [Bayes' theorem](https://www.youtube.com/watch?v=HZGCoVF3YvM), 3Blue1Brown | YouTube, free | [1](notes/01-bayesian-inference.md) | The whole video, for the geometry of the update |
| [StatQuest](https://www.youtube.com/@statquest), Starmer | YouTube, free | [1](notes/01-bayesian-inference.md) | Search the channel for Bayes and for maximum likelihood |
| [Ben Lambert](https://www.youtube.com/@SpartacanUsuals), econometrics playlists | YouTube, free | [7](notes/07-multilevel-models-and-partial-pooling.md) | Panel data, and fixed against random effects. Not watched for this chapter |
| [*An Introduction to Hierarchical Modeling*](https://mfviz.com/hierarchical-models/), Freeman | Interactive page, free | [7](notes/07-multilevel-models-and-partial-pooling.md) | A scrolling picture of intercepts and slopes varying by group, on faculty salaries by department |
| [Quantitude S2E29, *Multilevel Models: The Often Unnecessary Green Monster*](https://quantitude.org/s2e29-multilevel-models-the-often-unnecessary-green-monster) | Podcast, free | [7](notes/07-multilevel-models-and-partial-pooling.md) | The McNeish argument, with McNeish as the guest. Episode description read, not the audio |

The Coursera course behind `practice/BayesianML/` (HSE, Bayesian Methods for Machine Learning) now returns a 404 at the address in that folder's README, so it has no row here.

---

## Tools

- [PyMC](https://www.pymc.io/) and its [examples gallery](https://www.pymc.io/projects/examples/en/latest/gallery.html). The chapters run on PyMC 6.4.
- [ArviZ](https://python.arviz.org/), for diagnostics and summaries. The chapters run on ArviZ 1.3.
- [bambi](https://bambinos.github.io/bambi/), a formula interface over PyMC. Linked from the chapters but not run in them.
- [statsmodels MixedLM](https://www.statsmodels.org/stable/mixed_linear.html), for random intercepts and slopes with `re_formula`, linear outcomes only, and its limits on crossed effects. Run in [chapter 7](notes/07-multilevel-models-and-partial-pooling.md).
