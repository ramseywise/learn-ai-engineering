---
origin: curated
sources:
  - ../sources/
  - ../references.md
confidence: high
cleaned: 2026-11-02
---
# Probability and Statistics — References

> The sources behind the chapters in [notes/](notes/), mapped to what they support. PDFs live in the shared [sources/](../sources/) folder. Course index: [README](README.md). ★ marks reading that changed a claim in a note.

---

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| ★ Bruce & Bruce, *Practical Statistics for Data Scientists* (O'Reilly, 2017) | ch. 1 EDA; ch. 2 Sampling; ch. 3 Experiments; ch. 4 Regression; ch. 5 Classification | [PDF](../sources/Practical_Statistics_for_Data_Scientist.pdf) | [01](notes/01-descriptive-statistics-and-eda.md), [03](notes/03-distributions-and-sampling.md), [04](notes/04-estimation.md), [05](notes/05-hypothesis-testing.md), [06](notes/06-regression-and-glms.md) |
| Downey, *Think Stats* (Green Tea Press; CC BY-NC) | Chapter PDFs in [sources/think-stats/](../sources/think-stats/). Folded in as: ch. 1 → [01](notes/01-descriptive-statistics-and-eda.md), [05](notes/05-hypothesis-testing.md); ch. 2-3 → [01](notes/01-descriptive-statistics-and-eda.md), [03](notes/03-distributions-and-sampling.md); ch. 4 → [03](notes/03-distributions-and-sampling.md); ch. 5 → [02](notes/02-probability-foundations.md); ch. 6 → [03](notes/03-distributions-and-sampling.md); ch. 7 → [05](notes/05-hypothesis-testing.md); ch. 8 → [04](notes/04-estimation.md); ch. 9 → [01](notes/01-descriptive-statistics-and-eda.md), [06](notes/06-regression-and-glms.md). Notes cite it as `(*Think Stats*, ch. N)`. Errata found: ch. 4 prints 1.5 for the 95th percentile of an exponential with median 1 (it is about 4.3); ch. 8 prints the unbiased locomotive multiplier as 2N/(N-1) (it is 2N/(N+1)); ch. 9 types Pearson's denominator as a product of sums, not the square root | [PDF](../sources/thinkstats.pdf) · [3rd ed. online](https://allendowney.github.io/ThinkStats/) | 01, 02, 03, 04, 05, 06 |
| ★ Reinhart, *Statistics Done Wrong* (No Starch, 2015) | ch. 2 Power; ch. 3 Pseudoreplication; ch. 4 Base rate; ch. 5 Significance; ch. 9 Researcher freedom | [PDF](../sources/Alex_Reinhart-Statistics_Done_Wrong-EN.pdf) | [01](notes/01-descriptive-statistics-and-eda.md), [02](notes/02-probability-foundations.md), [05](notes/05-hypothesis-testing.md), [06](notes/06-regression-and-glms.md) |
| ★ James, Witten, Hastie, Tibshirani, Taylor, *An Introduction to Statistical Learning, with Applications in Python* (Springer, 2023) | §3.1-3.3 linear regression and its problems; §4.3 logistic; §4.6 GLMs | [PDF](../sources/An-Introduction-to-Statistical-Learning-with-Applications-in-Python.pdf) · [site](https://www.statlearning.com/) | [06](notes/06-regression-and-glms.md) |
| Efron & Hastie, *Computer Age Statistical Inference* (Cambridge, 2016) | ch. 3-4 Bayesian and Fisherian inference; ch. 6-7 empirical Bayes, James-Stein; ch. 8 GLMs, §8.2 deviance; ch. 10-11 bootstrap; ch. 15 FDR | [PDF](../sources/computer%20age%20statistical%20inference.pdf) | [03](notes/03-distributions-and-sampling.md), [04](notes/04-estimation.md), [05](notes/05-hypothesis-testing.md), [06](notes/06-regression-and-glms.md) |
| Davidson-Pilon, *Bayesian Methods for Hackers* (MIT licence) | ch. 1 and 4 (LLN, the small-N trap, ranking) | [PDF](../sources/bayes_for_hackers.pdf) · [repo](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers) | [03](notes/03-distributions-and-sampling.md) |
| ★ Huntington-Klein, [*The Effect*](https://theeffectbook.net/) (CRC, 2022; free online) | [ch. 16 Fixed Effects](https://theeffectbook.net/ch-FixedEffects.html), read to the start of §16.3.2; [ch. 18 Difference-in-Differences](https://theeffectbook.net/ch-DifferenceinDifference.html), §§18.2.1-18.2.3, long-term effects, §18.2.6 and the start of §18.3.1. The estimators it names for rollouts are cited through it | online | [08](notes/08-panel-data-and-fixed-effects.md) |
| Facure, [*Causal Inference for the Brave and True*](https://matheusfacure.github.io/python-causality-handbook/14-Panel-Data-and-Fixed-Effects.html) (MIT licence) | ch. 14, the opening and "When Panel Data Won't Help You" | online | [08](notes/08-panel-data-and-fixed-effects.md) |
| Angrist & Pischke, *Mostly Harmless Econometrics* (Princeton, 2009) and *Mastering 'Metrics* (2014) (not held) | Further reading for the econometrics canon; no chapter claims are made from them | not held | [07](notes/07-data-generating-process.md), [08](notes/08-panel-data-and-fixed-effects.md) |
| Wooldridge, *Introductory Econometrics: A Modern Approach* (Cengage, 7th ed.) (not held) | Further reading on specification, functional form and panel data; no chapter claims are made from it | not held | [07](notes/07-data-generating-process.md), [08](notes/08-panel-data-and-fixed-effects.md) |
| Blitzstein & Hwang, *Introduction to Probability* (not held) | Further reading for the full treatment; no chapter claims are made from it | not held | [02](notes/02-probability-foundations.md) |
| Grinstead & Snell, [*Introduction to Probability*](https://www.stat.berkeley.edu/users/aldous/134/grinstead.pdf) (2nd ed., AMS; GNU FDL) | ch. 4 Conditional Probability read in full, including the cancer-test example on small priors; not the rest | not held | [02](notes/02-probability-foundations.md) |

---

## Core papers

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| ★ Kohavi, Longbotham, Sommerfield, Henne, [Controlled experiments on the web: survey and practical guide](https://doi.org/10.1007/s10618-008-0114-1) (DMKD, 2009) | The 16σ²/δ² rule and its worked revenue vs conversion example; hash-based randomisation tests | [PDF](../sources/kohavi-2008-controlled-experiments-web.pdf) | [02](notes/02-probability-foundations.md), [04](notes/04-estimation.md) |
| Efron, [Bootstrap Methods: Another Look at the Jackknife](https://doi.org/10.1214/aos/1176344552) (Annals of Statistics, 1979) | Origin of the bootstrap. Not held; cited for the method | not held | [04](notes/04-estimation.md) |
| Wasserstein & Lazar, [The ASA Statement on p-Values](https://doi.org/10.1080/00031305.2016.1154108) (The American Statistician, 2016) | The official statement of what a p-value is not | not held | [05](notes/05-hypothesis-testing.md) |
| Benjamini & Hochberg, [Controlling the False Discovery Rate](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x) (JRSS B, 1995) | Origin of FDR control. Not held; cited for the procedure | not held | [05](notes/05-hypothesis-testing.md) |
| Ioannidis, [Why Most Published Research Findings Are False](https://doi.org/10.1371/journal.pmed.0020124) (PLOS Medicine, 2005) | The base-rate argument applied to whole fields. Not held | not held | [02](notes/02-probability-foundations.md) |
| ★ Shmueli, [To Explain or to Predict?](https://arxiv.org/abs/1101.0891) (Statistical Science, 2010; [DOI](https://doi.org/10.1214/10-STS330)) | Explanatory and predictive modelling are different goals, and the best model for one can be wrong for the other. Read in full | not held | [07](notes/07-data-generating-process.md) |
| ★ Meng, [Statistical Paradises and Paradoxes in Big Data (I)](https://doi.org/10.1214/18-AOAS1161SF) (Annals of Applied Statistics, 2018) | The data defect correlation: a small selection effect leaves a huge sample worth a few hundred random rows. Main text read in full; no licence found, so link only | not held | [03](notes/03-distributions-and-sampling.md), [07](notes/07-data-generating-process.md) |
| Breiman, [Statistical Modeling: The Two Cultures](https://doi.org/10.1214/ss/1009213726) (Statistical Science, 2001) | Against assuming the data model before looking at predictive accuracy. §§1-9.1 and §12 read, §§9.2-11 in part, discussion read | not held | [07](notes/07-data-generating-process.md) |
| Cameron & Miller, [A Practitioner's Guide to Cluster-Robust Inference](https://doi.org/10.3368/jhr.50.2.317) (J. Human Resources, 2015) | What to cluster over, why fixed effects do not remove the need, and how few clusters is too few. Read in full in the authors' February 2015 draft, not the published text | not held | [06](notes/06-regression-and-glms.md) |
| Pearl & Bareinboim, [External Validity: From Do-Calculus to Transportability Across Populations](https://arxiv.org/abs/1503.01603) (Statistical Science, 2014) | Selection diagrams, for when a result carries to another population. §§1-3 and the start of §4.1 read | not held | [07](notes/07-data-generating-process.md) |
| ★ Bell & Jones, [Explaining Fixed Effects](https://eprints.whiterose.ac.uk/89757) (Political Science Research and Methods, 2015; [DOI](https://doi.org/10.1017/psrm.2014.7)) | The within-between model: its within coefficient matches fixed effects, and it also gives the between effect. Main text read; online appendix not | not held | [08](notes/08-panel-data-and-fixed-effects.md) |
| ★ Gelman, Jakulin, Pittau, Su, [A weakly informative default prior distribution for logistic and other regression models](https://arxiv.org/abs/0901.4011) (Annals of Applied Statistics, 2008) | Stable logistic fits under separation with a Cauchy(0, 2.5) prior on standardised inputs | [PDF](../sources/gelman-2009-weakly-informative-default-prior-distribution.pdf) | [06](notes/06-regression-and-glms.md) |

---

## Courses and videos

| Resource | Platform, cost | Supports | Which part |
|---|---|---|---|
| [Statistics 110: Probability](https://www.youtube.com/playlist?list=PL2SOU6wwxB0uwwH80KTQ6ht66KWxbzTIo) (Joe Blitzstein, Harvard) | YouTube, free | [02](notes/02-probability-foundations.md), [03](notes/03-distributions-and-sampling.md) | Full playlist; conditional probability and expectation lectures first |
| [HarvardX Introduction to Probability](https://www.edx.org/learn/probability/harvard-university-introduction-to-probability) | edX, free to audit | [02](notes/02-probability-foundations.md) | The same material, structured with exercises |
| [MIT 18.650 Statistics for Applications, Fall 2016](https://ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/) (Philippe Rigollet); [playlist](https://www.youtube.com/playlist?list=PLUl4u3cNGP60uVBMaoNERc6knT_MgPKS0) | MIT OCW and YouTube, free | [04](notes/04-estimation.md), [05](notes/05-hypothesis-testing.md), [06](notes/06-regression-and-glms.md) | Maximum likelihood, testing, linear regression, GLMs |
| [StatQuest: Statistics Fundamentals](https://www.youtube.com/playlist?list=PLblh5JKOoLUK0FLuzwntyYI10UQFUhsY9) (Josh Starmer) | YouTube, free | [01](notes/01-descriptive-statistics-and-eda.md), [03](notes/03-distributions-and-sampling.md), [04](notes/04-estimation.md), [05](notes/05-hypothesis-testing.md) | Short refreshers on p-values, intervals and the bootstrap |
| 3Blue1Brown, [Bayes' theorem](https://www.youtube.com/watch?v=HZGCoVF3YvM) and [central limit theorem](https://www.youtube.com/watch?v=zeJD6dqJ5lo) | YouTube, free | [02](notes/02-probability-foundations.md), [03](notes/03-distributions-and-sampling.md) | The geometric picture of each |
| Cassie Kozyrkov, [Making Friends with AI](https://www.youtube.com/playlist?list=PLRKtJ4IpxJpDxl0NTvNYQWKCYzHNuy2xG) | YouTube, free | [05](notes/05-hypothesis-testing.md) | Decision-focused view of testing |
| [Think Stats, 3rd edition](https://allendowney.github.io/ThinkStats/) (Allen Downey) | Online book with notebooks, free | [01](notes/01-descriptive-statistics-and-eda.md), [03](notes/03-distributions-and-sampling.md) | Runnable chapters on distributions and CDFs |
| Ben Lambert, [econometrics playlists](https://www.youtube.com/@SpartacanUsuals) | YouTube, free | [07](notes/07-data-generating-process.md), [08](notes/08-panel-data-and-fixed-effects.md) | Panel data, fixed against random effects, functional form |
| Nick Huntington-Klein, [channel](https://www.youtube.com/@NickHuntingtonKlein) | YouTube, free | [08](notes/08-panel-data-and-fixed-effects.md) | The lectures that go with *The Effect* |
| MIT 14.310x and 14.32, *Data Analysis for Social Scientists* and *Econometrics* | edX and MIT OCW, free to audit | [07](notes/07-data-generating-process.md), [08](notes/08-panel-data-and-fixed-effects.md) | The social-science econometrics sequence |

---

## Tools

- [scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html): distributions, tests and `bootstrap`.
- [statsmodels](https://www.statsmodels.org/stable/index.html): OLS, GLMs, robust and clustered SEs, multiple-testing corrections.
- [linearmodels](https://pypi.org/project/linearmodels/): `PanelOLS` with entity and time effects, `drop_absorbed`.
- [patsy](https://patsy.readthedocs.io/): `bs()` splines and formula terms.
- [sklearn.model_selection](https://scikit-learn.org/stable/modules/cross_validation.html): cross-validated error for comparing specifications.
