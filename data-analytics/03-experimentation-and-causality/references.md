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
| Cunningham, *Causal Inference: The Mixtape* (free online) | DAGs, potential outcomes, unconfoundedness, RD, IV, DiD, synthetic control | not held · [site](https://mixtape.scunning.com/) | [04](notes/04-correlation-and-causation.md) |

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
| Pearl, [Causal inference in statistics: An overview](https://doi.org/10.1214/09-ss057) (Statistics Surveys, 2009) | Causal graphs and how to read them for controls | not held | [04](notes/04-correlation-and-causation.md) |
| Rosenbaum & Rubin, [The central role of the propensity score](https://doi.org/10.1093/biomet/70.1.41) (Biometrika, 1983) | Propensity scores | not held | [04](notes/04-correlation-and-causation.md) |
| Angrist, Imbens, Rubin, [Identification of Causal Effects Using Instrumental Variables](https://doi.org/10.1080/01621459.1996.10476902) (JASA, 1996) | The complier interpretation of IV | not held | [04](notes/04-correlation-and-causation.md) |
| Abadie, Diamond, Hainmueller, [Synthetic Control Methods](https://doi.org/10.1198/jasa.2009.ap08746) (JASA, 2010) | Synthetic control with placebo inference | not held | [04](notes/04-correlation-and-causation.md) |

---

## Courses and videos

| Resource | Platform, cost | Supports | Which part |
|---|---|---|---|
| [A/B Testing](https://www.udacity.com/course/ab-testing--ud257) (Carrie Grimes, Caroline Buckey, Diane Tang, Google) | Udacity, free | [01](notes/01-ab-testing.md), [02](notes/02-metrics-and-kpi-design.md) | Choosing and Characterizing Metrics; Designing an Experiment; Analyzing Results |
| [Introduction to Causal Inference](https://www.bradyneal.com/causal-inference-course) (Brady Neal) | Course site with videos, free | [04](notes/04-correlation-and-causation.md) | Potential outcomes, graphs, then the quasi-experimental weeks |
| [Causal Inference: The Mixtape](https://mixtape.scunning.com/) (Scott Cunningham) | Online book, free | [04](notes/04-correlation-and-causation.md) | The chapter for whichever design you need |
| [Statistical Rethinking 2023](https://www.youtube.com/playlist?list=PLDcUM9US4XdPz-KxHM4XHt7uUVGWWVSus) (Richard McElreath) | YouTube, free | [04](notes/04-correlation-and-causation.md) | The early lectures on confounds and causal graphs |
| Evan Miller, [How Not To Run an A/B Test](https://www.evanmiller.org/how-not-to-run-an-ab-test.html) | Blog, free | [01](notes/01-ab-testing.md), [03](notes/03-experimentation-at-scale.md) | The short case against peeking |

---

## Tools

- [statsmodels power](https://www.statsmodels.org/stable/stats.html#power-and-sample-size-calculations): sample size and power.
- [DoWhy](https://www.pywhy.org/dowhy/): graph-based causal estimation and refutation.
