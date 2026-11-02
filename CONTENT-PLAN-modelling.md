# Content plan: statistical models, social-science methods and cross-subject links

Status: 2026-11-02, draft for review. Companion to [CONTENT-PLAN.md](CONTENT-PLAN.md), which set the pillar
shape, and [CURRICULUM.md](CURRICULUM.md), which froze the subjects. This file names five gaps and says how
to close them inside the existing pillars, so no freeze exception is needed.

1. **data-analytics has no chapter on models as models.** Regression is taught as a tool for
   experiments ([02/06](data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md)),
   but nothing says what a data generating process is, how model fit differs from representativeness,
   when a fitted coefficient generalises, or how to choose a specification. The social-science and
   econometric toolkit that an analyst reaches for when randomisation is impossible is thin: matching
   is one row in a table, there is no survival or event-history model, no Markov chain, no sequence
   analysis, no multilevel or panel chapter, and no marketing or operations model beyond retention
   curves and RFM.
2. **The subjects do not point at each other.** data-science links back to data-analytics in five
   places, four of them Bayesian. generative-ai links to data-science only from pillar 09 and one
   reference row. ai-engineering never names a data pillar. A learner on Path A meets TF-IDF in RAG
   without being told the NLP chapter that derives it, and reads error bars in Eval without the
   estimation chapter that explains them.
3. **Metrics are taught chapter by chapter, and nothing ties them together.** Each note covers the
   metrics of its own target well, but no page answers "my dependent variable is this, so which model,
   loss, metric and baseline do I use?" A few standard metrics are missing altogether.
4. **The confusion matrix is taught as arithmetic, and the errors themselves are rarely read.** Nothing
   teaches the descriptive habit of pulling the false positives and false negatives, seeing what the model
   is good and bad at identifying, and improving it without fitting to those particular rows. The retrieval
   and ranking chapters also never say that their precision and recall come from the same table.
5. **Judges are calibrated against humans, but heuristic checks and the judge's own reasoning are barely
   used as evidence.** Code checks only filter rows before the judge, nothing says what to do when a check
   and the judge disagree, and critiques are written without being coded, counted or tested for
   faithfulness. The fix is one section in an existing note, set out in §2.7.

---

## 1. What exists and what is missing

Measured 2026-11-02 by reading the notes, not by word count.

| Topic | Where it is now | What is missing |
|---|---|---|
| Linear, logistic, Poisson models | [02/06](data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md): OLS, logistic, Poisson and negative binomial, diagnostics, robust and clustered SEs, interactions | The *data generating process* framing; estimand vs estimator; specification (logs, polynomials, splines); model comparison (adjusted R², AIC and BIC, likelihood-ratio tests, cross-validation); explanation vs prediction as two goals |
| Fit vs representativeness | [02/03](data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md) has one section, *Big is not the same as representative* | Internal vs external validity; transportability; Meng's big-data paradox; why a well-fitting model on a self-selected sample generalises worse than a poor fit on a random one |
| Observational causal designs | [03/04](data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation.md): DAGs, bad controls, propensity *weighting*, DiD, IV, RD, synthetic control, DoWhy | Matching as a family: exact, coarsened exact (CEM), nearest-neighbour on the propensity score, entropy balancing; balance diagnostics; the backdoor criterion stated as a rule; Pearl's primer not cited |
| Multilevel models | Only pieces. Eight schools in [04/02](data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc.md) demonstrates sampler divergences, not the model. The only explicit mention is a further-reading row to McElreath at the end of [04/06](data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning.md). Intraclass correlation and the design effect are in [02/02](data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md) and [03/03](data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md), clustered SEs in [02/06](data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md), and nothing connects them | No, complete and partial pooling (the phrase appears in no note); random intercepts and slopes; `MixedLM` beside PyMC; when clustered SEs are enough; partial pooling in the A/B chapters, which use none |
| Panel data | Clustered SEs in 02/06; DiD as a design in [03/04](data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation.md) | Fixed effects and two-way fixed effects with `linearmodels`, event studies |
| A map of metrics by target | Detail in each chapter. The closest thing to "pick the model by the dependent variable" is the flowchart at the top of [02/06](data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md), which covers regression-family models only. The *Which model, when* table in [DS 01/02](data-science/01-classical-ml/notes/02-supervised-learning.md) sorts by model, not by target | One chapter organised by target; see the coverage table in §2.5 |
| Reading errors | Definitions of Type I and II in [DA 02/05](data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md). The matrix and its formulas in [DS 01/04](data-science/01-classical-ml/notes/04-model-evaluation.md). Error counts priced by threshold in [DS 01/10](data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md). One false positive explained in [DS 01/08](data-science/01-classical-ml/notes/08-model-interpretability.md). Confusion pairs counted on digits in [DS 02/03](data-science/02-deep-learning/notes/03-structuring-ml-projects.md). A confusion table read in [DS 03/02](data-science/03-nlp/notes/02-text-classification.md). Open coding of traces in [GA 08/02](generative-ai/08-eval/notes/02-defining-correct.md) | A procedure for tabular data: profile the four cells, read the rows, slice, diagnose, and confirm on data you did not read. See §2.5, note 12 |
| Judge calibration | [GA 08/05](generative-ai/08-eval/notes/05-llm-as-judge.md) calibrates against human labels and logs each prompt change with its TPR and TNR. [GA 08/04](generative-ai/08-eval/notes/04-graders.md) runs code first and stops early. [GA 06/03](generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports.md) sends flagged turns to a stronger judge and has code overrule a flag that contradicts the claim list. [AIE 01/08](ai-engineering/01-prompt-engineering/notes/08-prompt-optimization.md) turns judge feedback into prompt rewrites | Heuristics as a test of the judge; a rule for code and judge disagreeing; slicing judge errors by flag as a routine step; coding the critiques; testing whether a critique reports what drove the verdict |
| Survival and event history | [06/03](data-analytics/06-applied-analyses/notes/03-cohort-and-retention.md) fits the shifted-beta-geometric curve to aggregate retention | Individual-level time-to-event: Kaplan-Meier, log-rank, Cox proportional hazards, censoring, time-varying covariates, competing risks; `lifelines` |
| Markov chains and sequences | None (RL's MDP chapter in generative-ai is the only Markov material) | Customer-state transition matrices, absorbing states, Markov CLV (Pfeifer and Carraway); social sequence analysis and optimal matching (Abbott) for journeys and careers |
| Lifetime value | [06/03](data-analytics/06-applied-analyses/notes/03-cohort-and-retention.md) prices cohorts; BG/NBD is a pointer | Fitting BG/NBD and Gamma-Gamma with `pymc-marketing`; LTV as a Markov reward; LTV to CAC under uncertainty |
| Marketing measurement | Uplift is a pointer in [06/05](data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm.md) | Attribution, adstock and saturation, marketing mix models, geo experiments and incrementality |
| Operations and supply chain | [06/01](data-analytics/06-applied-analyses/notes/01-forecasting.md) ends at a staffing plan | Newsvendor, EOQ and safety stock from forecast error, Little's law and queues, a linear programme |

---

## 2. New chapters

All inside existing pillars. Chapter numbers continue each pillar's sequence so that no link, deck or
slide breaks. Each chapter follows the standard in [CONTENT-PLAN.md §2.2](CONTENT-PLAN.md): hook, concepts
with runnable code, a figure, pitfalls, try-it, interview checklist, next. Practice is one `# %%` script
per chapter, like pillar 06's, and Fernhill stays the running example wherever a dataset is needed.

### 2.1 data-analytics 02, probability and statistics

| # | Chapter | What it teaches | Code |
|---|---|---|---|
| 07 | **The data generating process: fit, specification and generalisation** | A model is a claim about how the rows were generated. Write the DGP, simulate from it, fit, and see which estimates recover the truth. Estimand, estimator, estimate. Specification: logs for multiplicative effects, polynomial and spline terms, when a quadratic is a story and when it is overfitting. Comparing models: adjusted R², AIC and BIC, likelihood-ratio test, and cross-validation when the goal is prediction. Shmueli's *explain or predict* as the organising question. Internal validity (did the model get the effect right in this sample) vs external validity (does it hold elsewhere). Meng's result: with self-selection, a sample of millions can carry less information than a random sample of hundreds. Transportability in one DAG | `statsmodels` (`ols`, `anova_lm`, `compare_lr_test`, `bs()` splines via patsy), `sklearn.model_selection` for the prediction half, NumPy simulation |
| 08 | **Panel data and fixed effects** | The same units measured over time: stores by week, users by month. Pooled OLS with clustered SEs (chapter 06) against fixed effects (`PanelOLS` with entity and time effects) on one simulated DGP where the unit effect is correlated with the regressor, so pooled OLS is biased and the fixed-effects estimate recovers the truth. What within-unit variation can and cannot identify. Two-way fixed effects as the regression form of DiD, and the event-study plot. Ends with a pointer to [04/07](data-analytics/04-bayesian-analysis/README.md), which holds the fixed-vs-random decision | `linearmodels.PanelOLS`, a small event-study plot |

Chapter 06's *Next* changes from pillar 03 to chapter 07. Chapter 08's *Next* points at pillar 03.

### 2.2 data-analytics 03, experimentation and causality

| # | Chapter | What it teaches | Code |
|---|---|---|---|
| 05 | **Matching and weighting** | One observational question answered six ways on the same Fernhill data, with the known truth from the generator: naive difference, regression adjustment, exact matching, coarsened exact matching, nearest-neighbour propensity matching with a caliper, propensity weighting (from chapter 04), entropy balancing. Balance tables and a Love plot before any outcome is looked at. Overlap and the common-support region. Sensitivity to an unobserved confounder (Rosenbaum bounds, or the E-value). The backdoor criterion stated as a rule, with Pearl's primer as the source | `statsmodels`, a 40-line CEM and nearest-neighbour matcher written in pandas (teaches more than a library call), `scipy.optimize` for entropy balancing weights, DoWhy's estimators as the cross-check |

Chapter 04's matching row shrinks to a pointer. Chapter 04 gains a short section on the backdoor and
front-door criteria citing Pearl, Glymour and Jewell. Pillar README's reading order becomes five.

### 2.3 data-analytics 04, Bayesian analysis

| # | Chapter | What it teaches | Code |
|---|---|---|---|
| 07 | **Multilevel models and partial pooling** | Users with repeated measures, an experiment across many markets, segment effects without chasing noise. No pooling, complete pooling and partial pooling on one simulated dataset with known truth. Random intercepts, then random slopes. Intraclass correlation as the share of variance between groups, connecting the design effect from [02/02](data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md). The same model fitted with `MixedLM` and with PyMC, and where they agree. A decision table: clustered SEs when groups are a nuisance and the effect is a population average, fixed effects when the group effect may be correlated with the regressor, multilevel when group-level estimates are the question. The A/B application: a simulated experiment across segments, comparing per-segment estimates with partially pooled ones by error against the truth and by how much the winning segment's effect is exaggerated. One line stating that "hierarchical regression" in psychology often means adding blocks of predictors in stages, which is a different thing from nested data | `statsmodels` `mixedlm` with `re_formula`, PyMC with the non-centred form from [04/02](data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc.md) |

It sits in pillar 04 and not pillar 02 because it builds on the PyMC and Bayesian A/B chapters, and that is
where partial pooling has the most to show. Three constraints to design around:

- **Binary outcomes.** `MixedLM` is linear only. Run the two-toolkit comparison on a continuous metric such
  as revenue per user, and use PyMC alone for a conversion outcome.
- **Crossed effects.** `MixedLM` handles nested groups directly, and crossed effects need the awkward
  single-group workaround its docs describe. Keep the examples nested and say so.
- **Few groups.** With a handful of segments the between-group variance is poorly estimated. Show this
  rather than promising that partial pooling always helps. Gelman has written publicly that he still worries
  about multiple comparisons despite the 2012 paper, so cite that paper with that caveat.

Pointers go in from [02/06](data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md),
[03/03](data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md) and
[04/04](data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing.md). The *Next* of 04/06 changes to 04/07.

### 2.4 data-analytics 06, applied analyses

| # | Chapter | The question | What it teaches | Code |
|---|---|---|---|---|
| 07 | **Survival and event history: when will a customer leave?** | Fernhill's subscription box: who churns, when, and does the welcome call delay it? | Censoring, and why a mean lifetime from churned customers only is wrong. Kaplan-Meier curves by channel and the log-rank test. Cox proportional hazards: hazard ratios, the proportional-hazards check, time-varying covariates (a price rise mid-life). Competing risks (cancel vs downgrade) in one paragraph. How the Cox model relates to the sBG curve in chapter 03 and to the logistic regression in chapter 02 (a discrete-time hazard is a logit on person-periods) | `lifelines` (`KaplanMeierFitter`, `CoxPHFitter`, `check_assumptions`), `statsmodels` logit on person-period rows |
| 08 | **States and sequences: Markov chains and optimal matching** | Which journeys lead to a second order, and what is a customer in each state worth? | Customer states (new, active, lapsed, churned) and the transition matrix estimated from the order log. Absorbing states and expected time to churn. Markov CLV: value of a state as discounted expected reward (Pfeifer and Carraway). Then the sociological turn: journeys as strings, edit distance and optimal matching (Abbott), clustering the dissimilarity matrix into journey types, and a typical-sequence plot. Why this is description, not prediction, and when that is the right deliverable | NumPy for the chain and its fundamental matrix, `sequenzo` (Python port of TraMineR) or a 30-line Needleman-Wunsch for optimal matching, `scipy.cluster.hierarchy` |
| 09 | **Marketing measurement: attribution, mix models and lifetime value** | Where should next quarter's budget go, and what is a new customer worth? | Last-touch and Shapley attribution on the same paths, and why both are accounting rather than causation. Adstock and saturation. A small Bayesian marketing mix model with priors from a past geo test. BG/NBD and Gamma-Gamma fitted to Fernhill's non-contractual log, closing the pointer left in chapter 03. LTV to CAC with a posterior rather than a point. Incrementality as the thing an A/B test measures and an MMM estimates | `pymc-marketing` (`BetaGeoModel`, `GammaGammaModel`, `MMM`), with a note that Meridian and Robyn do the same job at scale |
| 10 | **Operations and supply chain: stock, queues and a plan** | How much of each product should the warehouse hold, and how many packers on a Monday? | Newsvendor from the forecast distribution of chapter 01: critical fractile, cost of under and over. EOQ and safety stock, with service level as the decision. Little's law and an M/M/c queue for the packing line. A linear programme for the shift plan. Each model is run against the simulated truth from `retail.py` | NumPy and SciPy for the closed forms, `pulp` for the LP, a short simulation for the queue |

Chapter 06's *Next* changes to chapter 07, and chapter 10 ends the pillar. `retail.py` needs
subscription start and end dates with a churn reason, weekly marketing spend by channel, and per-order
pick times and lead times. Write those into the generator once, in a separate commit, before the
chapters.

### 2.5 data-science 01, classical ML

| # | Chapter | What it teaches | Code |
|---|---|---|---|
| 11 | **Choosing a metric: start from the target** | A short map, not a second copy of the detail, which stays in each chapter. The organising idea is Gneiting's: the loss decides what the model estimates (squared error the mean, absolute error the median, pinball a quantile), so the metric has to match the decision. Then one row per target, below. One worked example runs several models on the same rare-class data, so the reader watches accuracy mislead. A small ranking example shows MRR and NDCG disagreeing. Ranking metrics need results grouped by query, so that example uses its own small simulated query set | `sklearn.metrics` (`matthews_corrcoef`, `balanced_accuracy_score`, `ndcg_score`, `mean_poisson_deviance`), MRR in a few lines of NumPy, and the credit lab's data once that lab is finished |

The map the chapter is built around:

| Target | Model family | Loss | Metric | Baseline |
|---|---|---|---|---|
| Continuous | OLS, boosted regressors | Squared or absolute error | RMSE, MAE, R² out of sample, adjusted R² in sample | Predict the mean |
| Binary | Logistic, boosted trees | Log loss | PR-AUC, ROC-AUC, Brier, Matthews correlation, balanced accuracy, cost at a threshold | Base rate, majority class |
| Count | Poisson, negative binomial | Poisson deviance | Deviance, dispersion, MAE | Constant rate |
| Ranking | Two-tower, retrieval, learning to rank | Pairwise or listwise | NDCG, MRR, recall at k | Popularity |
| Clusters | k-means, hierarchical | Inertia, or none | Silhouette without labels, Adjusted Rand Index for stability or known labels | Permuted control |
| Forecast | ETS, boosting on lags | Squared error, pinball | MASE, pinball; MAPE with its warning | Seasonal naive |

What exists now, and where each missing metric goes. Metrics go in the note that owns them, and the
new chapter links to them:

| Target | Covered in | Gap | Fix |
|---|---|---|---|
| Continuous | [DS 01/04](data-science/01-classical-ml/notes/04-model-evaluation.md), [DA 02/06](data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md) | Adjusted R² and deviance appear in no note | Adjusted R² in DA 02/07 (new); deviance in DA 02/06's GLM section |
| Binary | DS 01/04 | Specificity is one table row. Matthews correlation and balanced accuracy appear in no data-science or data-analytics note | Add both to DS 01/04. [DS 01/10](data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md) is still being written, so recheck this row when it lands |
| Clusters | [DS 01/05](data-science/01-classical-ml/notes/05-unsupervised-learning.md), [DA 06/05](data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm.md) | Not compared with supervised metrics | The map chapter |
| Ranking | [DS 05/02](data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation.md), [DS 05/03](data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md), generative-ai retrieval | MRR appears only in generative-ai | Add MRR to DS 05/03 |
| Forecast | [DS 05/01](data-science/05-time-series-and-recommenders/notes/01-time-series-ml.md), [DA 06/01](data-analytics/06-applied-analyses/notes/01-forecasting.md) | Not connected to the other targets | The map chapter |

It lands as note 11 because note 10 already exists. Its *Next* and 10's are settled once 10 is finished.

| # | Chapter | What it teaches | Code |
|---|---|---|---|
| 12 | **Reading the errors: what a model finds and what it misses** | Note 11 picks the number, and this note reads what is behind it. It treats a fitted model as something to describe, using the analyst's tools. The steps below are the chapter's spine, run on one model | `sklearn.metrics.confusion_matrix`, pandas group-bys for the cell profiles and slices, Wilson intervals from [DA 02/04](data-analytics/02-probability-and-statistics/notes/04-estimation.md), Benjamini-Hochberg from [DA 02/05](data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md), and the local explanations from [DS 01/08](data-science/01-classical-ml/notes/08-model-interpretability.md) on selected errors |

The procedure:

1. **Name the errors.** State the positive class and the null, because flipping either swaps the names. Set the
   matrix at the decision threshold, not at 0.5. Say what a false positive and a false negative are in the
   domain: a good customer declined, a defaulter approved.
2. **Profile the four cells.** Compare feature distributions across true positives, false positives, false
   negatives and true negatives. False negatives against true positives shows which defaulters it misses.
   False positives against true negatives shows which good customers look risky to it.
3. **Read rows.** Take a random sample from each error cell, plus the most confident mistakes. Random comes
   first, because the confident mistakes alone give a distorted picture.
4. **Slice and count.** Compute error rates by segment with intervals, and count each group's share of all
   errors, since that share is the ceiling on what fixing it can gain ([DS 02/03](data-science/02-deep-learning/notes/03-structuring-ml-projects.md)). Slices can use columns the model
   is not allowed to see. The credit lab excludes sex, marriage and age as inputs, and that is exactly why error
   rates across them should be reported.
5. **Diagnose.** Each kind of error points to a different response, in the table below.
6. **Confirm on data you did not read.** A change counts only if it holds there.

| What the errors look like | Likely cause | Response |
|---|---|---|
| Errors look identical to correct cases on every feature | The information isn't in the data | Get a new data source, or accept the limit and say so |
| Labels look wrong when you read the rows | Label noise | Audit the labels before changing the model |
| One group's errors concentrate | The model underfits that group, or the group is small | Add a general feature or more data for that group; partial pooling for noisy estimates |
| False positives and false negatives trade off along the score | Threshold | Move the threshold from the cost ratio, and leave the model alone |
| Errors grow with time since training | Drift | See DS 01/10's drift section |

**Learning from errors without fitting to them.** This is the chapter's main argument, and it gets a runnable
demonstration:

- **Split what you read from what you score.** Ng's *Machine Learning Yearning* divides the dev set into an
  eyeball set you read and a blackbox set you only score. The test set is read by nobody and used once.
- **Fix classes of error, never rows.** Each hypothesis names a mechanism and a feature that exists at prediction
  time, written down before it is scored. A rule that matches the rows you read is memorisation.
- **Treat a slice scan as many tests.** Scan fifty slices and some look terrible by chance. Apply the correction
  from DA 02/05, confirm on the blackbox set, and use the partial pooling from [DA 04/07](data-analytics/04-bayesian-analysis/README.md) for small groups.
- **Count the rounds.** Every look at a holdout leaks a little (Dwork et al.). After several rounds of changes,
  refresh the blackbox set.
- **Watch for hindsight features.** Reading a missed defaulter suggests features known only after the outcome.
  Check each new feature's timestamp against the decision.

The demonstration adds pure-noise columns to the data, scans slices on the eyeball set, and "fixes" the worst one.
It then scores that fix and one fix from a real mechanism on the blackbox set. The chapter reports whatever the
run gives, and a noise fix that fails to overfit would be reported as such.

**Dataset.** Use the credit data at its natural 22.1% default rate. The lab's 3% version leaves too few errors
to slice: in DS 01/10's run, the test set holds only 145 defaulters. Say plainly why this differs from note 10.

### 2.6 Why not a seventh data-analytics pillar

A pillar "models of people and processes" would read well, but CURRICULUM.md froze the pillars on
2026-10-28 and the material fits the existing framings: 02 is where a model is a claim about the DGP,
03 is where a design recovers a cause, and 06 is where a question gets a priced answer. Pillar 06 grows
to ten chapters, which the deck spec allows. If the pillar reads as two stories after the chapters exist
(customers and operations), split it then, with the reason written in CURRICULUM.md.

### 2.7 Not a new chapter: checks and critiques as evidence about the judge

[GA 08/05](generative-ai/08-eval/notes/05-llm-as-judge.md) gets one new section after *Calibrate against
human labels*. The gaps come from reading the relevant sections and from keyword searches across GA 08,
GA 06 and AIE 01 on 2026-11-02, so re-check them against the full note before writing. The section teaches
four things, in this order.

**1. Run the code checks against the judge.** Where a code check tests part of the judge's criterion, the
two verdicts form a table. A citation missing from the retrieved set, for example, should fail a grounding
judge.

| | Judge passes | Judge fails |
|---|---|---|
| **Code passes** | Normal. The random human sample covers these | Either the judge caught what the check can't see, or it failed a good output. A person decides, and the answer shows which side to fix |
| **Code fails** | The judge passed an output with a checkable fault. This is its false-pass rate on faults you can prove, and the case to read first | Agreement. This gives the judge's catch rate on provable faults. They are probably its easiest cases, so don't assume the rate holds for the subjective ones |

The section has to state four limits:

- **Human labels stay the calibration.** Agreement with code tests the judge only on what code can check,
  so it says nothing about the subjective part of the criterion. It doesn't move a grader out of
  `experimental`, which keeps note 05's rule that only human labels settle which judge is right.
- **Calibration runs the judge on rows code failed.** Stopping early is right in production, as GA 08/04
  says, but it empties the bottom row of the table. Say plainly that the two modes differ.
- **The disagreement queue is not the human sample.** GA 08/04 says the 5–10% sample is "not a review
  queue", and that stays true. Keep two samples: a random one for TPR, TNR and the corrected pass rate, and
  a targeted queue for finding what to fix. Rates from the queue are biased because it was selected on
  disagreement.
- **Agreement needs independence.** A check and a judge that both react to the same surface signal, such
  as word overlap, can agree and both be wrong.

**2. Slice judge errors by flag.** Language, route, length, whether a citation is present, and the code
check's result. Report TPR and TNR for each slice on dev, using DS 01/12's procedure and GA 08/09's
multiple-comparison warning. GA 06/03 already has the example: 389 of the lenient judge's 415 false alarms
are Danish turns. That finding becomes the worked case for a routine step.

**3. Code the critiques.** Read them on every disagreement and on a sample of agreements, because a matching
verdict can still rest on a wrong reason. This extends step 4 of note 05's procedure, which sorts
disagreements by what to fix but not by what went wrong in the reasoning. Open coding from GA 08/02 applies,
so the tags below are a starting set.

| What the critique shows | Likely prompt change |
|---|---|
| Missed evidence that is in the input | Ask for the claims or evidence to be listed before any judgement |
| Cited evidence that is not in the input | Require a quote for each piece of evidence, and check the quotes in code |
| Judged a different criterion | Tighten the definitions, or split the judge in two |
| Reasoning supports one verdict, the label says the other | Compute the verdict from the listed evidence in code, like GA 06/03's override |
| Right verdict, wrong reason | Add a few-shot example from train that shows the right reason |
| Mentions something that shouldn't count, such as source, length or style | Name it as out of scope, then rerun the cue test in part 4 |

Count the tags, fix the largest class, and log the tag counts next to TPR and TNR in the calibration record.
The DS 01/12 rule applies unchanged: fix a class of error, never the rows you read, and keep test untouched.
These prompt changes are hypotheses, so each one has to win on dev before it stays.

**4. Test whether a critique reports what drove the verdict.** Coding critiques assumes they are honest, and
the evidence says that often fails. Marioriyad et al. injected cues such as source and recency, and found
strong verdict shifts with acknowledgement at or near zero. So the section adds two tests:

- **Cue test.** Add a cue that should not matter, and record both the verdict shift rate and how often the
  critique mentions the cue.
- **Edit test.** Remove the evidence the critique relies on, and see whether the verdict changes. If it
  doesn't, that critique is not a guide to what to fix.

Tapwal et al.'s evidence-first prompt, *Proof-Before-Preference*, is the mitigation to try: it locks the
evidence before scoring. Note 05's line that reasoning first "improves accuracy" has no source today, so find one
or soften it when this section goes in. Mittal and Arike add a warning: judges
often detect that a reasoning error exists but struggle to locate it, and they overestimate completeness.
Don't rely on a judge alone to grade reasoning.

**Exercise.** Parts 1 to 3 run offline on GA 06's `support_agent` package, which has planted failures. Its judges
are deterministic rules, as GA 06/03 says, so the exercise teaches the procedure and measures no real model.
Part 4 needs a real model, so it goes in as a marked online exercise, and the offline run must not be used
to claim anything about faithfulness.

**Links for the second pass (phase 14):**

| Note | Links to | What to add |
|---|---|---|
| [GA 08/04 Graders](generative-ai/08-eval/notes/04-graders.md) | GA 08/05 | One line in *Layer them, don't choose*: stop early in production, but not during calibration |
| [GA 08/02 Defining correct](generative-ai/08-eval/notes/02-defining-correct.md) | GA 08/05 | Open coding also applies to the judge's critiques |
| [GA 06/03 Judge pipelines](generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports.md) | GA 08/05 | The override and the Danish false alarms are instances of parts 2 and 3 |
| [AIE 01/08 Prompt optimization](ai-engineering/01-prompt-engineering/notes/08-prompt-optimization.md) | GA 08/05 | An optimiser fed judge feedback inherits unfaithful critiques, so test the judge first. Add to the failure-category checklist and the GEPA pitfall |
| [AIE 01/09 Evaluating prompts](ai-engineering/01-prompt-engineering/notes/09-evaluating-prompts.md) | GA 08/05 | From its judge section to this one |
| [AIE 01/03 Core techniques](ai-engineering/01-prompt-engineering/notes/03-core-techniques.md) | GA 08/05 | Its warning about rationalisation, and Turpin et al., applied to judges |

---

## 3. Cross-subject links

The rule to add to [ai-engineering/PILLAR-LAYOUT.md](ai-engineering/PILLAR-LAYOUT.md): every pillar
README has a **Builds on** table (which earlier chapters in other subjects it assumes, with one line on
why) and a **Feeds into** table (which later chapters use it). `scripts/check_chapters.py` warns when a
pillar README has neither. Chapter-level links go inline where the concept is first used, in the form
"see [chapter](path) in data analytics for the derivation".

### 3.1 data-science points back to data-analytics

| data-science note | Links to | Why |
|---|---|---|
| [01/01 Statistical foundations](data-science/01-classical-ml/notes/01-statistical-foundations.md) | DA 02/07 (DGP, new), 02/04 estimation | "A model is an estimate of f" is the DGP chapter said in ML terms; bias and variance of an estimator is the same decomposition |
| [01/02 Supervised learning](data-science/01-classical-ml/notes/02-supervised-learning.md), linear models section | DA 02/06 regression | The same `LinearRegression` and `LogisticRegression`, read for prediction here and for inference there. One sentence on why sklearn reports no standard errors |
| [01/04 Model evaluation](data-science/01-classical-ml/notes/04-model-evaluation.md) | DA 02/04 bootstrap, 02/05 multiple testing | Confidence intervals on a test score; comparing many models is many tests |
| [01/08 Interpretability](data-science/01-classical-ml/notes/08-model-interpretability.md) | DA 03/04 and 03/05 (new) | SHAP explains the model, not the world; a feature's importance is not its causal effect |
| [01/05 Unsupervised](data-science/01-classical-ml/notes/05-unsupervised-learning.md) | DA 06/05 RFM and 06/08 (new) | k-means on RFM, and clustering a sequence dissimilarity matrix |
| [03/03 Topic models](data-science/03-nlp/notes/03-topic-models-and-summarization.md) | DA 04/01, 04/02 | LDA is a Bayesian model; the inference vocabulary is there |
| [05/01 Time series ML](data-science/05-time-series-and-recommenders/notes/01-time-series-ml.md) | DA 06/01 forecasting, 06/10 (new) | The statistical baselines it must beat, and what the forecast is for |
| [05/03 Two-tower and evaluation](data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md) | DA 03/01, 03/03 | The online A/B test it ends on |
| [01/04 Model evaluation](data-science/01-classical-ml/notes/04-model-evaluation.md) and [01/02](data-science/01-classical-ml/notes/02-supervised-learning.md) | DS 01/11 (new) | The target-first map, from the two places a reader goes looking for it |
| [05/03 Two-tower and evaluation](data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md) | DS 01/11 (new), DA 04/07 (new) | Ranking in the map; segment effects read with partial pooling |
| [README](data-science/README.md) | DA README | Replace "data analytics comes first" with the Builds-on table above |

### 3.2 generative-ai points back to data-science and data-analytics

| generative-ai note | Links to | Why |
|---|---|---|
| [01 README](generative-ai/01-llm-fundamentals/README.md) and 01/01 tokens | DS 03/01 text representation, 03/04 embeddings | Word counts to word2vec to a learned embedding table is one line of descent |
| 01/02 attention, 01/06 pretraining | DS 02/01 fundamentals, 02/02 optimisation, 02/05 sequence models | Backprop, AdamW and the learning-rate sweep are assumed, not retaught |
| [02/03 Keyword, semantic and hybrid search](generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search.md) | DS 03/01, 03/02, 03/04, 03/07 | TF-IDF is derived there; the TF-IDF-beats-LSTM result is the reason BM25 is still the baseline |
| 03 agentic foundations, tool use and planning | DA 04/03 bandits | Thompson sampling is the explore-exploit idea agents inherit |
| [05 RL](generative-ai/05-RL/README.md) | DA 04/03 bandits, DA 06/08 (new) Markov chains | A Markov chain with rewards is an MDP without actions; bandits are the one-state case |
| [08/09 Reading results](generative-ai/08-eval/notes/09-reading-results.md) | DA 02/04 estimation, 02/05 testing, 03/01 A/B | Standard errors, paired tests, the bootstrap and sample-size rules are taught there with the same formulas |
| 08/11 production and A/B tests | DA 03/01, 03/03 | Peeking, SRM, CUPED |
| 06 observability dashboards | DA 05/05 dashboards | What a dashboard is for and what it hides |
| 07 data-analysis agent | DA README | The agent is doing the analyst's job; the checks it should run are the pillar's rules of thumb |
| 08/07 evaluating RAG, [02/01 RAG pipeline](generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md) | DS 01/11 (new), DS 05/03 | MRR and NDCG are defined once in data-science and used here |
| [08 eval references](generative-ai/08-eval/references.md) | DS 01/04 calibration | Already links Guo et al.'s PDF; link the chapter too |

### 3.3 ai-engineering points at the earlier subjects

| ai-engineering pillar | Links to | Why |
|---|---|---|
| README | GA 01 (model), DS 02 (training), DA 02 and 03 (measurement) | A Builds-on table at the top, since the README currently names only generative-ai eval |
| 01 prompt engineering, measurement chapter | DA 03/01, GA 08/09 | Prompt A vs prompt B is an A/B test with the same sample-size arithmetic |
| 04 loop engineering | GA 03, DA 04/03 | Loop termination and exploration budgets |
| 05 graph engineering, knowledge graphs | DS 03/05 NER | Already linked from data-science; make it two-way |
| 07 inference engineering | DS 02 (what a forward pass costs), DE 06 ml-platform (serving) | Batching and KV cache sit on the DL chapters; model registry and serving are DE's |
| 08 multimodal | DS 02/04 CNNs, DS 03/04 embeddings | Vision encoders and joint embedding spaces |
| 09 safety and security | GA 05 alignment, DA 03/02 metrics | RLHF is the alignment mechanism; guardrail metrics are the KPI chapter's idea |

### 3.4 data-engineering

| data-engineering note | Links to | Why |
|---|---|---|
| 06 ml-platform, drift | DA 06/02 credit scoring (PSI), DS 01/04 | PSI is already computed in the credit chapter; drift monitoring is the same statistic |
| 05 quality and observability | DA 01/02 loading and cleaning, DA 02/01 EDA | The checks an analyst runs by hand are the tests the pipeline automates |
| 03 transform, marts | DA 06/06 SQL for analytics | The mart's consumer |

### 3.5 Forward links from data-analytics

Each data-analytics pillar README gains a Feeds-into table: 02 to DS 01 and GA 08/09; 03 to GA 08/11
and AIE 01; 04 to DS 03/03 and GA 05; 05 to GA 06; 06 to DS 05 and DE 06.

### 3.6 Links inside data-analytics to the new chapters

| Note | Links to | Why |
|---|---|---|
| [02/06 Regression](data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md) | DS 01/11 (new), DA 04/07 (new) | The flowchart covers the regression family, and the map covers the rest. Clustered SEs lead on to multilevel |
| [02/02 Probability foundations](data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md) | DA 04/07 (new) | The intraclass correlation it introduces is a model parameter there |
| [03/02 Metrics and KPI design](data-analytics/03-experimentation-and-causality/notes/02-metrics-and-kpi-design.md) | DS 01/11 (new) | Business metrics and model metrics are different questions; say which is which |
| [03/03 Experimentation at scale](data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md), [04/04 Bayesian A/B](data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing.md) | DA 04/07 (new) | Per-segment and per-market readouts |
| [04/02 MCMC](data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc.md) | DA 04/07 (new) | Eight schools shows the sampler there, and the model is taught here |

### 3.7 One thread: the confusion matrix from data analytics to AI engineering

Every retrieval, ranking, judge and guardrail metric in the later subjects is this table with different labels.
No note says so today, so this thread gets explicit links in both directions.

| | Credit model | Retrieval and RAG | LLM judge | Guardrail |
|---|---|---|---|---|
| Positive class | Will default | Chunk is relevant | Output passes (the convention in GA 08/05) | Input is an attack |
| "Predicted positive" | Declined | Retrieved in the top k | Judge passes it | Guard blocks it |
| False positive | Good customer declined | Irrelevant chunk spends context budget | Judge passes a bad output | Benign message blocked |
| False negative | Defaulter approved | Relevant chunk missed, so the answer cannot be grounded | Judge fails a good output | Attack gets through |
| True negative | Good customer approved | The rest of the corpus, so huge that accuracy means nothing | Judge fails a bad output | Benign message allowed |
| Threshold | Score cut-off | k | Judge prompt and any score cut-off | Guard threshold |

Two points to state where the thread is taught:

- **Ranking metrics are the table swept along the list.** Precision and recall at k are one matrix at one cut-off.
  MRR and NDCG weight positions, so no single matrix gives them, and they are summaries across cut-offs.
  Manning, Raghavan and Schütze derive precision and recall from this contingency table, and they explain why
  accuracy fails for search.
- **Reading errors is the same habit at every level.** Open coding of traces in GA 08/02 is DS 01/12's procedure
  on text. Read the missed chunks and the distractors, group them, count them, and confirm on data you did not read.

| Note | Links to | What to add |
|---|---|---|
| [DA 02/05 Hypothesis testing](data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md) | DS 01/04, DS 01/12 (new) | One paragraph: Type I and II are the off-diagonal cells of the same table, with the decision rule in place of a model |
| [DA 02/02 Probability foundations](data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md) | DS 01/04, AIE 09/03 | Its base-rate calculation is why precision collapses on rare events, which is the guardrail note's result |
| [DA 06/02 Credit scoring](data-analytics/06-applied-analyses/notes/02-credit-scoring.md) | DS 01/10, DS 01/12 (new) | Cut-off choice leads on to reading who is wrongly declined |
| [DS 01/04 Model evaluation](data-science/01-classical-ml/notes/04-model-evaluation.md) | DA 02/05, DS 01/12 (new), GA 02/01 | Where the table is taught, say where it goes next, both back and forward |
| [DS 01/10 Imbalance and errors](data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md) | DS 01/12 (new) | Note 10 prices the errors, and note 12 reads them. Add once note 10 is finished |
| [DS 01/08 Interpretability](data-science/01-classical-ml/notes/08-model-interpretability.md) | DS 01/12 (new) | Its false-positive explanation is step 3 of the procedure |
| [DS 02/03 Structuring projects](data-science/02-deep-learning/notes/03-structuring-ml-projects.md), [DS 03/02 Text classification](data-science/03-nlp/notes/02-text-classification.md) | DS 01/12 (new) | The same habit on digits and on text; note 12 is the general form |
| [DS 05/03 Two-tower and evaluation](data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md) | DS 01/04, DS 01/12 (new) | Its recall-for-retrieval and precision-for-ranking split, stated as cells of the table |
| [GA 02/01 RAG pipeline](generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md), [GA 08/07 Evaluating RAG](generative-ai/08-eval/notes/07-evaluating-rag-and-grounding.md) | DS 01/04, DS 01/12 (new) | The retrieval column above, at the point recall@k is defined |
| [GA 08/02 Defining correct](generative-ai/08-eval/notes/02-defining-correct.md), [GA 08/03 Eval datasets](generative-ai/08-eval/notes/03-eval-datasets.md) | DS 01/12 (new), DS 02/03 | 08/02's error analysis descends from this procedure, and 08/03's dev and held-out split is the same answer to the overfitting question |
| [GA 08/05 LLM as judge](generative-ai/08-eval/notes/05-llm-as-judge.md) | DS 01/04, DS 01/12 (new), DA 02/02 | The judge's matrix is the same table with PASS as the positive class, and its correction formula is the base-rate argument. Coding the critiques (§2.7) is the reading-errors habit applied to the judge |
| [GA 08/09 Reading results](generative-ai/08-eval/notes/09-reading-results.md) | DS 01/12 (new), DA 02/05 | Slicing and its multiple-comparison warning are the same step |
| [AIE 01/09 Evaluating prompts](ai-engineering/01-prompt-engineering/notes/09-evaluating-prompts.md) | DS 01/12 (new) | Fix classes of failure, not the examples in the eval set |
| [AIE 02/12 Evaluating context](ai-engineering/02-context-engineering/notes/12-evaluating-context.md) | DS 01/04, DS 01/11 (new) | Its low-recall and low-precision reading is the retrieval column above |
| [AIE 09/02 Prompt injection](ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks.md), [AIE 09/03 Guardrails](ai-engineering/09-safety-and-security/notes/03-guardrail-models.md) | DS 01/04, DA 02/02 | The guardrail column above, and the base-rate source |
| [AIE 03/05 Verification loops](ai-engineering/03-harness-engineering/notes/05-verification-loops.md) | DS 01/04 | A verifier that cries wolf is a false-positive problem with a cost |

---

## 4. Sources

Books held in `data-analytics/sources/` stay there. Everything below is new. Free texts are linked, not
vendored, unless the licence allows a copy (Hernán and Robins, Grinstead and Snell, the Pearl primer
draft). Add the papers through `scripts/papers/discover/curated.jsonl` with `home: analytics` and the
note path, then `discover.py curated` and `potw.py triage`, so the ledger tracks them as it does the
rest. Books that are not held get `link-only` rows.

On the request to cite "the econometrics book from Pearl": Pearl's books are the causal-inference
canon rather than econometrics. The econometrics line is Wooldridge, Angrist and Pischke, and
Huntington-Klein. Both lines belong here, and the table says which chapter each serves.

### 4.1 Books

| Book | Free? | Chapters it serves | Role |
|---|---|---|---|
| Pearl, Glymour and Jewell, *Causal Inference in Statistics: A Primer* (Wiley, 2016). A complete draft is posted at [UCLA](https://web.cs.ucla.edu/~kaoru/primer-complete-2019.pdf); check the licence before copying it to sources/ | draft free | DA 03/04, 03/05 | ★ primary for the backdoor criterion and do-calculus in plain terms |
| Pearl, *Causality: Models, Reasoning and Inference*, 2nd ed. (Cambridge, 2009) | no | DA 03/04 | further reading; the primer is enough for the chapters |
| Pearl and Mackenzie, *The Book of Why* (Basic Books, 2018) | no | DA 03 README | the narrative version, for the pillar's story paragraph |
| Hernán and Robins, [*Causal Inference: What If*](https://miguelhernan.org/whatifbook) (Chapman and Hall/CRC; free PDF from the authors, use the latest dated version) | yes | DA 03/04, 03/05, 06/07 | ★ primary for matching, IP weighting, and the survival chapter's causal reading (Part II has survival analysis) |
| Huntington-Klein, [*The Effect: An Introduction to Research Design and Causality*](https://theeffectbook.net/) (CRC, 2022; free online, R, Stata and Python code) | yes | DA 02/08, 03/05 | ★ primary for fixed effects, event studies and matching, in a register close to this course's |
| Cunningham, [*Causal Inference: The Mixtape*](https://mixtape.scunning.com/) | yes | DA 03/05 | already listed; add the matching chapter to its row |
| Facure, [*Causal Inference for the Brave and True*](https://matheusfacure.github.io/python-causality-handbook/) (MIT licence, Python notebooks) | yes | DA 03/05, 02/08 | the Python companion to the two above; its matching and panel chapters are runnable |
| Angrist and Pischke, *Mostly Harmless Econometrics* (Princeton, 2009) and *Mastering 'Metrics* (2014) | no | DA 02/07, 02/08, 03/05 | the econometrics canon; cite for the "furious five" framing and for why OLS is the workhorse |
| Wooldridge, *Introductory Econometrics: A Modern Approach* (Cengage, 7th ed.) | no | DA 02/07, 02/08 | the undergraduate reference for specification, functional form and panel data |
| Gelman and Hill, *Data Analysis Using Regression and Multilevel/Hierarchical Models* (Cambridge, 2007) | no | DA 04/07 | ★ the multilevel text; the successor *Regression and Other Stories* is already listed and now gets a chapter to cite it |
| Snijders and Bosker, *Multilevel Analysis*, 2nd ed. (SAGE, 2012) | no | DA 04/07 | the social-science multilevel reference, including study design and survey weights |
| McElreath, *Statistical Rethinking*, multilevel chapters | draft held in sources/ | DA 04/07 | the PyMC-friendly treatment of partial pooling; check the chapter numbers in the held draft |
| Shmueli, [*To Explain or to Predict?*](https://projecteuclid.org/euclid.ss/1294167961) (Statistical Science, 2010; open access, [arXiv:1101.0891](https://arxiv.org/abs/1101.0891)) | yes | DA 02/07, DS 01/01 | ★ the paper the DGP chapter is organised around; also cited from data-science |
| Breiman, *Statistical Modeling: The Two Cultures* (Statistical Science, 2001) | yes | DA 02/07, DS 01/01 | the other half of that argument |
| Meng, [*Statistical Paradises and Paradoxes in Big Data (I)*](https://projecteuclid.org/euclid.aoas/1532743473) (Annals of Applied Statistics, 2018; [Harvard PDF](https://statistics.fas.harvard.edu/resource/statisticalparadisesandparadoxesinbigdatapdf)) | yes | DA 02/07, 02/03 | ★ the data-quality identity behind "big is not representative" |
| Kleinbaum and Klein, *Survival Analysis: A Self-Learning Text*, 3rd ed. (Springer, 2012) | no | DA 06/07 | the gentlest survival text |
| Box-Steffensmeier and Jones, *Event History Modeling: A Guide for Social Scientists* (Cambridge, 2004) | no | DA 06/07 | the social-science framing of time-to-event |
| Grinstead and Snell, [*Introduction to Probability*](https://www.stat.berkeley.edu/users/aldous/134/grinstead.pdf) (AMS, 2nd ed.; GNU FDL, chapter 11 Markov chains) | yes | DA 06/08, DA 02/02 | ★ absorbing and ergodic chains with the fundamental matrix, free to copy into sources/ |
| Cachon and Terwiesch, *Matching Supply with Demand*, 5th ed. (McGraw-Hill, 2024; chapter 14 is the newsvendor) | no | DA 06/10 | the MBA operations text; Terwiesch's Coursera course is the free lecture track |
| Hillier and Lieberman, *Introduction to Operations Research* (McGraw-Hill) | no | DA 06/10 | queueing and LP reference |
| Ng, [*Machine Learning Yearning*](https://home-wordpress.deeplearning.ai/wp-content/uploads/2022/03/andrew-ng-machine-learning-yearning.pdf) (free PDF) | yes | DS 01/12, DS 02/03 | ★ error analysis and the eyeball and blackbox dev sets |
| Manning, Raghavan and Schütze, [*Introduction to Information Retrieval*](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-unranked-retrieval-sets-1.html) (Cambridge, 2008; free online), the evaluation chapter | yes | DS 01/12, GA 02/01 | ★ precision and recall from the contingency table, and why accuracy fails for search |
| Fader, *Customer Centricity* (Wharton, 2012) and the [Fader and Hardie paper site](https://brucehardie.com/) | papers yes | DA 06/09 | already partly cited; the Gamma-Gamma note is on the site |

### 4.2 Papers

| Paper | Chapters | Why |
|---|---|---|
| Hainmueller, [*Entropy Balancing for Causal Effects*](https://www.cambridge.org/core/journals/political-analysis/article/entropy-balancing-for-causal-effects-a-multivariate-reweighting-method-to-produce-balanced-samples-in-observational-studies/220E4FC838066552B53128E647E4FAA7) (Political Analysis, 2012) | DA 03/05 | the method |
| Iacus, King and Porro, [*Causal Inference without Balance Checking: Coarsened Exact Matching*](https://gking.harvard.edu/cem/) (Political Analysis, 2012) | DA 03/05 | CEM |
| Gelman, Hill and Yajima, [*Why We (Usually) Don't Have to Worry About Multiple Comparisons*](https://arxiv.org/abs/0907.2478) (J. Research on Educational Effectiveness, 2012) | DA 04/07 | ★ partial pooling moves estimates where corrections widen intervals; the argument for the A/B application |
| McNeish, Stapleton and Silverman, *On the Unnecessary Ubiquity of Hierarchical Linear Modeling* (Psychological Methods, 2017) | DA 04/07 | the case for clustered SEs when the group effects are not the question; read the full text before citing, since search reached only a summary |
| Bell and Jones, [*Explaining Fixed Effects*](https://eprints.whiterose.ac.uk/89757) (Political Science Research and Methods, 2015; open access) | DA 04/07, 02/08 | the counter-case: a well-specified random-effects model can do what fixed effects do |
| Cameron and Miller, [*A Practitioner's Guide to Cluster-Robust Inference*](https://doi.org/10.3368/jhr.50.2.317) (J. Human Resources, 2015; paywalled) | DA 04/07, 02/06 | few clusters, multiway clustering, and fixed effects with clustering |
| Gneiting, [*Making and Evaluating Point Forecasts*](https://arxiv.org/abs/0912.0902) (JASA, 2011) | DS 01/11 | ★ why the loss has to match the quantity you want reported |
| Chicco and Jurman, [*The Advantages of the Matthews Correlation Coefficient*](https://doi.org/10.1186/s12864-019-6413-7) (BMC Genomics, 2020; open access) | DS 01/04, 01/11 | Matthews correlation against accuracy and F1; it advocates, so pair it with the cost-based view in DS 01/10 |
| Saito and Rehmsmeier, [*The Precision-Recall Plot Is More Informative than the ROC Plot*](https://doi.org/10.1371/journal.pone.0118432) (PLOS ONE, 2015; open access) | DS 01/11 | the rare-class example |
| Brodersen et al., *The Balanced Accuracy and Its Posterior Distribution* (ICPR, 2010; paywalled) | DS 01/04, 01/11 | balanced accuracy; only the citation and abstract were confirmed |
| Järvelin and Kekäläinen, [*Cumulated Gain-Based Evaluation of IR Techniques*](https://doi.org/10.1145/582415.582418) (ACM TOIS, 2002; [free preprint](https://trepo.tuni.fi/handle/10024/65718)) | DS 01/11, DS 05/03 | the source of NDCG |
| Wu, Ribeiro, Heer and Weld, [*Errudite: Scalable, Reproducible, and Testable Error Analysis*](https://aclanthology.org/P19-1073/) (ACL, 2019) | DS 01/12, GA 08/02 | ★ small hand-labelled error samples can bias conclusions, so define groups precisely and test the hypothesis |
| Chung et al., [*Slice Finder: Automated Data Slicing for Model Validation*](https://research.google/pubs/slice-finder-automated-data-slicing-for-model-validation/) (ICDE, 2019) | DS 01/12 | finding large, interpretable, problematic slices with statistical tests |
| Dwork et al., *The Reusable Holdout: Preserving Validity in Adaptive Data Analysis* (Science, 2015) | DS 01/12 | why repeated looks at a holdout stop being clean; read the full text before citing, since search confirmed only the citation and a summary of the method |
| Northcutt, Athalye and Mueller, [*Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks*](https://arxiv.org/abs/2103.14749) (NeurIPS Datasets and Benchmarks, 2021) | DS 01/12 | some "errors" are wrong labels; about 3.3% on average across 10 benchmarks |
| Ribeiro, Wu, Guestrin and Singh, [*Beyond Accuracy: Behavioral Testing of NLP Models with CheckList*](https://arxiv.org/abs/2005.04118) (ACL, 2020) | DS 01/12, AIE 01/09 | turning an error pattern into a general test instead of a patch |
| Chouldechova, [*Fair Prediction with Disparate Impact*](https://arxiv.org/abs/1703.00056) (arXiv, 2017) | DS 01/12 | when base rates differ, a calibrated score cannot also equalise false positive and false negative rates; check the journal citation before adding |
| Marioriyad et al., [*The Judge Who Never Admits: Hidden Shortcuts in LLM-based Evaluation*](https://arxiv.org/abs/2602.07996) (arXiv, 2026) | GA 08/05 | ★ six judges and six cue families: verdicts shift on cues while acknowledgement stays at or near zero. Source of the cue test |
| Tapwal, Kumar and Maple, [*Faithful or Fabricated? A Causal Framework for Rationalization Bias in LLM Judges*](https://arxiv.org/abs/2605.23970) (arXiv, 2026) | GA 08/05 | ★ tests rationale anchoring on 1,000 summaries; *Proof-Before-Preference* improves cue invariance |
| Mittal and Arike, [*C2-Faith: Benchmarking LLM Judges for Causal and Coverage Faithfulness in Chain-of-Thought Reasoning*](https://arxiv.org/abs/2603.05167) (arXiv, 2026) | GA 08/05 | judges detect reasoning errors more readily than they locate them, and overestimate completeness |
| Lanham et al., [*Measuring Faithfulness in Chain-of-Thought Reasoning*](https://arxiv.org/abs/2307.13702) (arXiv, 2023) | GA 08/05, AIE 01/03 | the intervention method behind the edit test. Its metric is contested by *Chain-of-Thought Unfaithfulness as Disguised Accuracy*, which search confirmed only as a snippet, so read and cite that too |
| Chen et al., [*Reasoning Models Don't Always Say What They Think*](https://arxiv.org/abs/2505.05410) (arXiv, 2025) | GA 08/05 | already listed in AIE 01, but not applied to judges; models that use a hint often mention it less than 20% of the time |
| Turpin et al., [*Unfaithful Explanations in Chain-of-Thought Prompting*](https://arxiv.org/abs/2305.04388) (2023) | GA 08/05 | already held and cited in AIE 01/03; a cross-citation, no new PDF |
| Shankar et al., [*Who Validates the Validators?*](https://arxiv.org/abs/2404.12272) (UIST, 2024) | GA 08/05 | code and LLM graders selected by agreement with human grades. GA 08's references map it to note 05, but the search found the citation only in note 02, so add it |
| Shankar et al., [*SPADE: Synthesizing Data Quality Assertions for LLM Pipelines*](https://arxiv.org/abs/2401.03038) (arXiv, 2024) | GA 08/04, GA 08/05 | derives code checks from a prompt's version history, so each instruction added becomes a candidate check |
| Ratner et al., [*Snorkel: Rapid Training Data Creation with Weak Supervision*](https://arxiv.org/abs/1711.10160) (VLDB, 2017) | GA 08/05, further reading | heuristics as noisy labellers whose accuracies are estimated from their agreements, and why correlated sources skew that estimate. It is about training data, so cite the idea and not a result about judges |
| Rosenbaum and Rubin (1983) | DA 03/05 | already in the ledger as link-only; it now gets a chapter |
| Cox, *Regression Models and Life-Tables* (JRSS B, 1972); Kaplan and Meier (JASA, 1958) | DA 06/07 | attribution rows |
| Abbott and Tsay, [*Sequence Analysis and Optimal Matching Methods in Sociology: Review and Prospect*](https://doi.org/10.1177/0049124100029001001) (Sociological Methods and Research, 2000), and Wu's reply in the same issue | DA 06/08 | ★ the method and the critique that it is description, not causation |
| Pfeifer and Carraway, *Modeling Customer Relationships as Markov Chains* (Journal of Interactive Marketing, 2000) | DA 06/08, 06/09 | Markov CLV; the exact title varies between citations, check the publisher record |
| Fader, Hardie and Lee, *Counting Your Customers the Easy Way* (2005), and Fader and Hardie, *The Gamma-Gamma Model of Monetary Value* (2013 note) | DA 06/09 | already cited as pointers; now fitted |
| Chan and Perry, *Challenges and Opportunities in Media Mix Modeling* (Google research, 2017); Jin et al., *Bayesian Methods for Media Mix Modeling with Carryover and Shape Effects* (Google, 2017) | DA 06/09 | adstock, saturation and the priors; not confirmed by search on 2026-11-02, so verify the links before adding |
| Gupta et al., *Modeling Customer Lifetime Value* (Journal of Service Research, 2006) | DA 06/09 | the survey of LTV model families |
| Makridakis et al., M5 (IJF, 2022) | DA 06/10 | already cited in DS 05/01; the operations chapter uses its uncertainty track |

The nine judge rows above were confirmed from arXiv records and abstracts on 2026-11-02, except Turpin et
al., which is already held, and the one snippet flagged in the Lanham row. Read each in full before citing it. The
GA and AIE papers go into the ledger under their own pillars, not `home: analytics`.

### 4.3 Courses and videos

| Course or channel | Free | Chapters | What to watch |
|---|---|---|---|
| Brady Neal, [*Introduction to Causal Inference*](https://www.bradyneal.com/causal-inference-course) (course page links the lecture videos and a free draft book) | yes | DA 03/04, 03/05 | weeks on backdoor adjustment, matching and sensitivity |
| Ben Lambert, [econometrics playlists](https://www.youtube.com/@SpartacanUsuals) (undergraduate and graduate series) | yes | DA 02/07, 02/08, 04/07 | panel data, fixed vs random effects, functional form |
| Nick Huntington-Klein, [channel](https://www.youtube.com/@NickHuntingtonKlein) | yes | DA 02/08, 03/05 | the lectures that go with *The Effect* |
| MIT 14.310x / 14.32, *Data Analysis for Social Scientists* and *Econometrics* (edX and OCW) | yes to audit | DA 02/07, 02/08 | the social-science econometrics sequence |
| Terwiesch, *Introduction to Operations Management* (Coursera, Wharton) | audit | DA 06/10 | newsvendor, queueing, process analysis weeks |
| StatQuest | yes | DA 06/07 | the survival-analysis and Cox videos in the statistics playlist already listed |
| PyMC Labs, [pymc-marketing docs](https://pymc-marketing.readthedocs.io/) | yes | DA 06/09 | the BG/NBD and MMM notebooks |
| [lifelines docs](https://lifelines.readthedocs.io/) | yes | DA 06/07 | Quickstart and Survival Regression |
| [sequenzo docs](https://pypi.org/project/sequenzo/) | yes | DA 06/08 | if it lacks optimal matching on inspection, fall back to the in-note implementation |
| [linearmodels docs](https://pypi.org/project/linearmodels/) | yes | DA 02/08 | `PanelOLS.from_formula` with `EntityEffects` |
| [statsmodels MixedLM](https://www.statsmodels.org/stable/mixed_linear.html) | yes | DA 04/07 | random intercepts and slopes with `re_formula`, and its limits on crossed effects |
| McElreath, [*Statistical Rethinking* lectures](https://www.youtube.com/playlist?list=PLDcUM9US4XdPz-KxHM4XHt7uUVGWWVSus) (already linked from DA 04/06) | yes | DA 04/07 | the multilevel lectures |
| Freeman, [*An Introduction to Hierarchical Modeling*](http://mfviz.com/hierarchical-models) (interactive) | yes | DA 04/07 | a scrolling visual of intercepts and slopes varying by group; secondary sources confirm it, so check it is still live |
| [Quantitude S2E29, *Multilevel Models: The Often Unnecessary Green Monster*](https://quantitudepod.org/s2e29-multilevel-models-the-often-unnecessary-green-monster) (podcast) | yes | DA 04/07 | the McNeish argument talked through by two psychology methodologists |
| [scikit-learn metrics guide](https://scikit-learn.org/stable/modules/model_evaluation.html) | yes | DS 01/11, 01/12 | the metric API, organised by task |
| StatQuest, *Machine Learning Fundamentals: The Confusion Matrix* and *Sensitivity and Specificity* (YouTube) | yes | DS 01/04, 01/12, DA 02/05 | titles confirmed from a listing; find the current version of each on the channel already listed |

---

## 5. Order of work

| Phase | Work | Skill | Size |
|---|---|---|---|
| 1 | Cross-links to targets that already exist (§3, every row except the ones marked new). PILLAR-LAYOUT gains the Builds-on and Feeds-into rule; `check_chapters.py` warns on their absence | by hand | one pass over 9 READMEs and about 25 notes |
| 2 | `retail.py` gains subscriptions, churn reasons, marketing spend and warehouse timings; regenerate chapters 1 to 6's outputs and confirm their numbers are unchanged (seeded) | by hand | half a day |
| 3 | DA 02/07, the DGP chapter. It is the keystone: data-science 01/01 and the Eval chapter point at it | `/chapter` with Shmueli, Meng, Huntington-Klein | one chapter |
| 4 | DA 03/05 matching and weighting; trim 04's table; add the backdoor section citing Pearl | `/chapter` | one chapter and one edit |
| 5 | DA 06/07 survival | `/chapter` with Hernán and Robins Part II, lifelines | one chapter |
| 6 | DA 06/08 states and sequences | `/chapter` with Grinstead and Snell ch. 11, Abbott and Tsay | one chapter |
| 7 | DA 02/08 panel data | `/chapter` with *The Effect*, Bell and Jones | one chapter |
| 8 | DA 04/07 multilevel models | `/chapter` with Gelman and Hill, Gelman, Hill and Yajima, McNeish et al. | one chapter and pointers from three notes |
| 9 | DA 06/09 marketing measurement | `/chapter` with pymc-marketing docs, Fader and Hardie | one chapter; the MMM section is `# illustrative` if sampling is slow |
| 10 | DA 06/10 operations | `/chapter` with Cachon and Terwiesch | one chapter |
| 11 | DS 01/11 metric map, plus the fills in DS 01/04, DS 05/03 and DA 02/06. Starts after DS 01/10 and the credit lab are finished, since it reuses both | `/chapter` with Gneiting, Chicco and Jurman | one short chapter and three small edits |
| 12 | DS 01/12 reading the errors, including the noise-fix demonstration. Also starts after DS 01/10 and the credit lab, and after phase 11 so it can link back | `/chapter` with Ng, Errudite, Slice Finder | one chapter |
| 13 | GA 08/05's new section (§2.7), and one exercise each for its offline and online parts. Links to DS 01/12, so it follows phase 12 unless the link is added later | `/papers` with Marioriyad, Tapwal, Mittal and Arike, Lanham | one section and one exercise |
| 14 | Second cross-link pass for the rows marked new, including the thread in §3.7 and the §2.7 links; READMEs, CURRICULUM.md path (new steps 4b "say what the model claims" and 8b "model an event, a state and a plan"), rules of thumb; rebuild the five decks (DA 02, 03, 04, 06 and DS 01) | `/pillar`, `/slides` | one pass |
| 15 | Ledger: curated rows for every §4 paper, route the free PDFs, mark `integrated` as each chapter lands | `/readings` | runs alongside 3 to 13 |

Phases 3 to 10 are independent of each other after phase 2, so they can be split across sessions in any order.
Phase 8 needs no new generator data, so it could start first. Phases 11 and 12 need no generator data either,
but they wait on DS 01/10 and the credit lab. Phase 1 is the cheapest and the most visible to a learner, so it comes first.

## 6. Rules of thumb these chapters add

For the data-analytics README once they exist:

- Write the data generating process you believe before you fit, and simulate from it to see whether your estimator recovers it.
- A better fit in this sample is not a better answer for the population. Ask how the rows got in before you admire R².
- Match or weight on covariates measured before treatment, show the balance table first, and say what an unmeasured confounder would have to do to undo the result.
- Cluster when groups are a nuisance, model them when they are the question.
- Reading many segment effects? Partially pool them first, because the winning segment's raw estimate is exaggerated.
- A customer who has not churned yet is censored, not retained. Never average lifetimes over the churned only.
- A transition matrix is a description of the past; it forecasts only if the process is stationary, so check it on a holdout period.
- Attribution allocates credit; only an experiment or a model with a causal design measures incrementality.
- The forecast's error distribution is the input to the stock decision, not the point forecast.
- Before tuning, read the false positives and false negatives. Ask what the model finds, what it misses, and whether the data could tell them apart.
- Read errors on one split and score fixes on another. Fix a class of error, never the rows you read.
- Start from the target: it picks the model family, the loss, the metric and the baseline, in that order.

For [GA 08/05](generative-ai/08-eval/notes/05-llm-as-judge.md) once its new section exists:

- When a code check and the judge disagree, read that row first. It shows which of them to fix.
- Run the judge on rows code already failed during calibration, and stop early only in production.
- Keep the random human sample and the disagreement queue apart. Only the random sample gives you rates.
- Read critiques on agreements as well as disagreements. A right verdict can rest on a wrong reason.
- A critique is a hypothesis about the verdict. Change the input and see whether the verdict follows.
