---
origin: curated
sources:
  - ../sources/
  - ../references.md
confidence: high
cleaned: 2026-11-01
---
# Experimentation and Causality — References

> The sources behind the chapters in [notes/](notes/), mapped to what they support. PDFs live in the shared [sources/](../sources/) folder. Course index: [README](README.md). ★ marks reading that changed a claim in a note.

---

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| Bruce & Bruce, *Practical Statistics for Data Scientists* (O'Reilly, 2017) | ch. 3 Statistical Experiments and Significance Testing | [PDF](../sources/Practical_Statistics_for_Data_Scientist.pdf) | [01](notes/01-ab-testing.md), [04](notes/04-correlation-and-causation.md) |
| Reinhart, *Statistics Done Wrong* (No Starch, 2015) | ch. 2 Power; ch. 3 Pseudoreplication | [PDF](../sources/Alex_Reinhart-Statistics_Done_Wrong-EN.pdf) | [01](notes/01-ab-testing.md) |
| Kohavi, Tang & Xu, *Trustworthy Online Controlled Experiments* (Cambridge, 2020) | Further reading; no chapter claims are made from it | not held · [site](https://experimentguide.com/) | [03](notes/03-experimentation-at-scale.md) |
| Cunningham, *Causal Inference: The Mixtape* (free online) | DAGs, potential outcomes, unconfoundedness, RD, IV, DiD, synthetic control; the matching and subclassification chapter for 05. Further reading; no claims taken from it | not held · [site](https://mixtape.scunning.com/) | [04](notes/04-correlation-and-causation.md), [05](notes/05-matching-and-weighting.md) |
| ★ Pearl, Glymour & Jewell, *Causal Inference in Statistics: A Primer* (Wiley, 2016) | §3.3 backdoor, §3.4 front-door and part of §3.6 read in full; not the rest. The draft asks not to be redistributed, so link only | not held · [draft](https://web.cs.ucla.edu/~kaoru/primer-complete-2019.pdf) | [04](notes/04-correlation-and-causation.md), [05](notes/05-matching-and-weighting.md) |
| Pearl, *Causality*, 2nd ed. (Cambridge, 2009) | Further reading; not read for this course, no claims taken from it | not held · [site](https://bayes.cs.ucla.edu/BOOK-2K/) | [04](notes/04-correlation-and-causation.md) |
| Pearl & Mackenzie, *The Book of Why* (Basic Books, 2018) | The narrative version, for the pillar's story. Not read; no claims taken from it | not held · [site](http://bayes.cs.ucla.edu/WHY/) | [README](README.md) |
| Hernán & Robins, *Causal Inference: What If* (Chapman and Hall/CRC; free PDF from the authors, all rights reserved) | ch. 7 Confounding; §6.4 positivity; ch. 12 IP weighting; ch. 13 standardisation; ch. 15 outcome regression and propensity scores, with §15.4 on propensity matching. These read in full in the 19 August 2026 PDF, not the rest of the book; §7.4 cited in 04 and §15.4 in 05 | not held · [site](https://miguelhernan.org/whatifbook) | [04](notes/04-correlation-and-causation.md), [05](notes/05-matching-and-weighting.md) |
| Huntington-Klein, *The Effect* (CRC, 2022; free online) | ch. 14 Matching, read in part: calipers, extreme weights and trimming, the data appetite of CEM, entropy balancing | not held · [ch. 14](https://theeffectbook.net/ch-Matching.html) | [05](notes/05-matching-and-weighting.md) |
| Facure, *Causal Inference for the Brave and True* (MIT licence) | ch. 10 Matching and ch. 11 Propensity Score, read in part. The runnable Python companion | not held · [ch. 10](https://matheusfacure.github.io/python-causality-handbook/10-Matching.html) | [05](notes/05-matching-and-weighting.md) |
| Angrist & Pischke, *Mostly Harmless Econometrics* (Princeton, 2009) | Further reading, the econometrics canon. Not reached; no claims taken from it | not held | [05](notes/05-matching-and-weighting.md) |

---

## Core papers

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| ★ Kohavi, Longbotham, Sommerfield, Henne, [Controlled experiments on the web: survey and practical guide](https://doi.org/10.1007/s10618-008-0114-1) (DMKD, 2009) | Sample size rule, OEC, A/A tests, ramp-up, hash tests, the 99/1 cost, the eBay interference case | [PDF](../sources/kohavi-2008-controlled-experiments-web.pdf) | [01](notes/01-ab-testing.md), [02](notes/02-metrics-and-kpi-design.md), [03](notes/03-experimentation-at-scale.md) |
| ★ Dmitriev, Gupta, Kim, Vaz, [A Dirty Dozen: Twelve Common Metric Interpretation Pitfalls in Online Controlled Experiments](https://doi.org/10.1145/3097983.3098024) (KDD, 2017) | The metric taxonomy and twelve real failures, each mapped to a check | [PDF](../sources/2017-08-kddmetricinterpretationpitfalls.pdf) | [02](notes/02-metrics-and-kpi-design.md), [03](notes/03-experimentation-at-scale.md) |
| Deng, Knoblich, Lu, [Applying the Delta Method in Metric Analytics](https://doi.org/10.1145/3219819.3219919) (KDD, 2018) | Variance of ratio metrics. Not held; cited for the method | not held | [02](notes/02-metrics-and-kpi-design.md) |
| Hohnhold, O'Brien, Tang, [Focusing on the Long-term](https://doi.org/10.1145/2783258.2788583) (KDD, 2015) | Long-running experiments that measure user learning. Not held; no numbers quoted | not held | [02](notes/02-metrics-and-kpi-design.md), [03](notes/03-experimentation-at-scale.md) |
| Deng, Xu, Kohavi, Walker, [Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data](https://doi.org/10.1145/2433396.2433413) (WSDM, 2013) | CUPED. Not held; the 50% figure comes from the abstract | not held | [03](notes/03-experimentation-at-scale.md) |
| Johari, Pekelis, Walsh, [Always Valid Inference](https://arxiv.org/abs/1512.04922) (arXiv, 2015) | Always-valid p-values with the mixture SPRT. Not held; cited for the method | not held | [01](notes/01-ab-testing.md), [03](notes/03-experimentation-at-scale.md) |
| Johari, Koomen, Pekelis, Walsh, [Peeking at A/B Tests](https://doi.org/10.1145/3097983.3097992) (KDD, 2017) | The deployed version of the same idea. Not held | not held | [03](notes/03-experimentation-at-scale.md) |
| Fabijan et al., [Diagnosing Sample Ratio Mismatch in Online Controlled Experiments](https://doi.org/10.1145/3292500.3330722) (KDD, 2019) | Taxonomy of SRM causes. Not held; cited for the approach | not held | [03](notes/03-experimentation-at-scale.md) |
| Tang, Agarwal, O'Brien, Meyer, [Overlapping Experiment Infrastructure](https://doi.org/10.1145/1835804.1835810) (KDD, 2010) | Layered assignment. Not held | not held | [03](notes/03-experimentation-at-scale.md) |
| Pocock, [Group sequential methods](https://doi.org/10.1093/biomet/64.2.191) (Biometrika, 1977) | Constant sequential boundary | not held | [03](notes/03-experimentation-at-scale.md) |
| O'Brien & Fleming, [A multiple testing procedure for clinical trials](https://doi.org/10.2307/2530245) (Biometrics, 1979) | Sequential boundary strict early and lenient late | not held | [03](notes/03-experimentation-at-scale.md) |
| Anscombe, [Graphs in Statistical Analysis](https://doi.org/10.1080/00031305.1973.10478966) (The American Statistician, 1973) | The quartet | not held | [04](notes/04-correlation-and-causation.md) |
| Bickel, Hammel, O'Connell, [Sex Bias in Graduate Admissions](https://doi.org/10.1126/science.187.4175.398) (Science, 1975) | The classic Simpson's paradox case | not held | [04](notes/04-correlation-and-causation.md) |
| Rubin, [Estimating causal effects of treatments](https://doi.org/10.1037/h0037350) (J. Educational Psychology, 1974) | Potential outcomes | not held | [04](notes/04-correlation-and-causation.md) |
| Pearl, [Causal inference in statistics: An overview](https://doi.org/10.1214/09-ss057) (Statistics Surveys, 2009) | Causal graphs and how to read them for controls. Not read for the backdoor section, which uses the primer | not held | [04](notes/04-correlation-and-causation.md) |
| Rosenbaum & Rubin, [The central role of the propensity score](https://doi.org/10.1093/biomet/70.1.41) (Biometrika, 1983) | Propensity scores: the coarsest balancing score, removing bias due to observed covariates only. Summary and §1 read (pp. 41-42) | not held · [copy](https://www.stat.cmu.edu/~ryantibs/journalclub/rosenbaum_1983.pdf) | [04](notes/04-correlation-and-causation.md), [05](notes/05-matching-and-weighting.md) |
| ★ Iacus, King, Porro, [Causal Inference without Balance Checking: Coarsened Exact Matching](https://gking.harvard.edu/files/political_analysis-2011-iacus-pan_mpr013.pdf) (Political Analysis, 2012) | CEM, its weights, local SATT when treated units are pruned, and what it cannot rescue. Read except part of §5.3-5.7 | not held | [05](notes/05-matching-and-weighting.md) |
| ★ Hainmueller, [Entropy Balancing for Causal Effects](https://www.mit.edu/~jhainm/Paper/eb.pdf) (Political Analysis, 2012) | The dual used in the script, and the warning on limited overlap. Pp. 25-44 read | not held | [05](notes/05-matching-and-weighting.md) |
| Stuart, [Matching Methods for Causal Inference: A Review and a Look Forward](https://pmc.ncbi.nlm.nih.gov/articles/PMC2943670/) (Statistical Science, 2010) | Standardised differences, plots of them, and Rubin's (2001) 0.25 and 0.5-2 guideline as she reports it. Balance sections read | not held | [05](notes/05-matching-and-weighting.md) |
| ★ Ding & VanderWeele, [Sensitivity Analysis Without Assumptions](https://pmc.ncbi.nlm.nih.gov/articles/PMC4820664/) (Epidemiology, 2016) | The bounding factor behind the E-value, and its use for non-negative outcomes such as spend. Read in part | not held | [05](notes/05-matching-and-weighting.md) |
| Mathur, Ding, Riddell, VanderWeele, [Web Site and R Package for Computing E-values](https://pmc.ncbi.nlm.nih.gov/articles/PMC6066405/) (Epidemiology, 2018) | The E-value definition and formula, as restated by its authors. Read in full | not held | [05](notes/05-matching-and-weighting.md) |
| VanderWeele & Ding, [Sensitivity Analysis in Observational Research: Introducing the E-Value](https://doi.org/10.7326/M16-2607) (Annals of Internal Medicine, 2017) | Origin of the E-value. Abstract only; full text not reached | not held | [05](notes/05-matching-and-weighting.md) |
| Liu, Kuramoto, Stuart, [An Introduction to Sensitivity Analysis for Unobserved Confounding in Nonexperimental Prevention Research](https://pmc.ncbi.nlm.nih.gov/articles/PMC3800481/) (Prevention Science, 2013) | Rosenbaum bounds, and the fact that the simple form sets the confounder-outcome link at infinity. Rosenbaum section read | not held | [05](notes/05-matching-and-weighting.md) |
| Angrist, Imbens, Rubin, [Identification of Causal Effects Using Instrumental Variables](https://doi.org/10.1080/01621459.1996.10476902) (JASA, 1996) | The complier interpretation of IV | not held | [04](notes/04-correlation-and-causation.md) |
| Abadie, Diamond, Hainmueller, [Synthetic Control Methods](https://doi.org/10.1198/jasa.2009.ap08746) (JASA, 2010) | Synthetic control with placebo inference | not held | [04](notes/04-correlation-and-causation.md) |

---

## Courses and videos

| Resource | Platform, cost | Supports | Which part |
|---|---|---|---|
| [A/B Testing](https://www.udacity.com/course/ab-testing--ud257) (Carrie Grimes, Caroline Buckey, Diane Tang, Google) | Udacity, free | [01](notes/01-ab-testing.md), [02](notes/02-metrics-and-kpi-design.md) | Choosing and Characterizing Metrics; Designing an Experiment; Analyzing Results |
| [Introduction to Causal Inference](https://www.bradyneal.com/causal-inference-course) (Brady Neal) | Course site with videos, free | [04](notes/04-correlation-and-causation.md), [05](notes/05-matching-and-weighting.md) | Potential outcomes, graphs, then the quasi-experimental weeks; for 05, the backdoor adjustment and sensitivity weeks |
| [Causal Inference: The Mixtape](https://mixtape.scunning.com/) (Scott Cunningham) | Online book, free | [04](notes/04-correlation-and-causation.md), [05](notes/05-matching-and-weighting.md) | The chapter for whichever design you need |
| [Nick Huntington-Klein's channel](https://www.youtube.com/@NickHuntingtonKlein) | YouTube, free | [05](notes/05-matching-and-weighting.md) | The lectures that go with *The Effect*. Listed from the content plan; not watched |
| [Statistical Rethinking 2023](https://www.youtube.com/playlist?list=PLDcUM9US4XdPz-KxHM4XHt7uUVGWWVSus) (Richard McElreath) | YouTube, free | [04](notes/04-correlation-and-causation.md) | The early lectures on confounds and causal graphs |
| Evan Miller, [How Not To Run an A/B Test](https://www.evanmiller.org/how-not-to-run-an-ab-test.html) | Blog, free | [01](notes/01-ab-testing.md), [03](notes/03-experimentation-at-scale.md) | The short case against peeking |

---

## Tools

- [statsmodels power](https://www.statsmodels.org/stable/stats.html#power-and-sample-size-calculations): sample size and power.
- [DoWhy](https://www.pywhy.org/dowhy/): graph-based causal estimation and refutation. Chapter 5 records how its defaults behave, from version 0.14's source and output: scores clipped to 0.05-0.95, and the clipped score written back to the model's data.
- [rbounds](https://cran.r-project.org/package=rbounds): Rosenbaum bounds in R, with `psens` for continuous outcomes. Package listing and function list only; chapter 5 writes the Wilcoxon bound itself.
