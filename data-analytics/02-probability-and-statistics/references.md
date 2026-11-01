---
origin: curated
sources:
  - ../sources/
  - ../references.md
confidence: high
cleaned: 2026-11-01
---
# Probability and Statistics — References

> The sources behind the chapters in [notes/](notes/), mapped to what they support. PDFs live in the shared [sources/](../sources/) folder. Course index: [README](README.md). ★ marks reading that changed a claim in a note.

---

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| ★ Bruce & Bruce, *Practical Statistics for Data Scientists* (O'Reilly, 2017) | ch. 1 EDA; ch. 2 Sampling; ch. 3 Experiments; ch. 4 Regression; ch. 5 Classification | [PDF](../sources/Practical_Statistics_for_Data_Scientist.pdf) | [01](notes/01-descriptive-statistics-and-eda.md), [03](notes/03-distributions-and-sampling.md), [04](notes/04-estimation.md), [05](notes/05-hypothesis-testing.md), [06](notes/06-regression-and-glms.md) |
| Downey, *Think Stats* (Green Tea Press; CC BY-NC) | ch. 2-3 descriptive statistics and the class size paradox; ch. 4 continuous; ch. 5 probability; ch. 6 operations; ch. 7 tests | [PDF](../sources/thinkstats.pdf) · [3rd ed. online](https://allendowney.github.io/ThinkStats/) | [01](notes/01-descriptive-statistics-and-eda.md), [02](notes/02-probability-foundations.md), [03](notes/03-distributions-and-sampling.md), [05](notes/05-hypothesis-testing.md) |
| ★ Reinhart, *Statistics Done Wrong* (No Starch, 2015) | ch. 2 Power; ch. 3 Pseudoreplication; ch. 4 Base rate; ch. 5 Significance; ch. 9 Researcher freedom | [PDF](../sources/Alex_Reinhart-Statistics_Done_Wrong-EN.pdf) | [01](notes/01-descriptive-statistics-and-eda.md), [02](notes/02-probability-foundations.md), [05](notes/05-hypothesis-testing.md), [06](notes/06-regression-and-glms.md) |
| ★ James, Witten, Hastie, Tibshirani, Taylor, *An Introduction to Statistical Learning, with Applications in Python* (Springer, 2023) | §3.1-3.3 linear regression and its problems; §4.3 logistic; §4.6 GLMs | [PDF](../sources/An-Introduction-to-Statistical-Learning-with-Applications-in-Python.pdf) · [site](https://www.statlearning.com/) | [06](notes/06-regression-and-glms.md) |
| Efron & Hastie, *Computer Age Statistical Inference* (Cambridge, 2016) | ch. 3-4 Bayesian and Fisherian inference; ch. 6-7 empirical Bayes, James-Stein; ch. 8 GLMs; ch. 10-11 bootstrap; ch. 15 FDR | [PDF](../sources/computer%20age%20statistical%20inference.pdf) | [03](notes/03-distributions-and-sampling.md), [04](notes/04-estimation.md), [05](notes/05-hypothesis-testing.md), [06](notes/06-regression-and-glms.md) |
| Davidson-Pilon, *Bayesian Methods for Hackers* (MIT licence) | ch. 1 and 4 (LLN, the small-N trap, ranking) | [PDF](../sources/bayes_for_hackers.pdf) · [repo](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers) | [03](notes/03-distributions-and-sampling.md) |
| Blitzstein & Hwang, *Introduction to Probability* (not held) | Further reading for the full treatment; no chapter claims are made from it | not held | [02](notes/02-probability-foundations.md) |

---

## Core papers

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| ★ Kohavi, Longbotham, Sommerfield, Henne, [Controlled experiments on the web: survey and practical guide](https://doi.org/10.1007/s10618-008-0114-1) (DMKD, 2009) | The 16σ²/δ² rule and its worked revenue vs conversion example; hash-based randomisation tests | [PDF](../sources/kohavi-2008-controlled-experiments-web.pdf) | [02](notes/02-probability-foundations.md), [04](notes/04-estimation.md) |
| Efron, [Bootstrap Methods: Another Look at the Jackknife](https://doi.org/10.1214/aos/1176344552) (Annals of Statistics, 1979) | Origin of the bootstrap. Not held; cited for the method | not held | [04](notes/04-estimation.md) |
| Wasserstein & Lazar, [The ASA Statement on p-Values](https://doi.org/10.1080/00031305.2016.1154108) (The American Statistician, 2016) | The official statement of what a p-value is not | not held | [05](notes/05-hypothesis-testing.md) |
| Benjamini & Hochberg, [Controlling the False Discovery Rate](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x) (JRSS B, 1995) | Origin of FDR control. Not held; cited for the procedure | not held | [05](notes/05-hypothesis-testing.md) |
| Ioannidis, [Why Most Published Research Findings Are False](https://doi.org/10.1371/journal.pmed.0020124) (PLOS Medicine, 2005) | The base-rate argument applied to whole fields. Not held | not held | [02](notes/02-probability-foundations.md) |
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

---

## Tools

- [scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html): distributions, tests and `bootstrap`.
- [statsmodels](https://www.statsmodels.org/stable/index.html): OLS, GLMs, robust and clustered SEs, multiple-testing corrections.
