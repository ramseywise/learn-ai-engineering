# Data analytics: course curriculum

> Learn to turn imperfect data into an honest, decision-ready recommendation: from a messy export, through uncertainty and causal evidence, to a clear action.

This is the learner-facing syllabus for Data Analytics. Study each unit's chapters, use its deck to review, complete its drills and lab, and retain the stated evidence of mastery in a portfolio. Pillar READMEs explain how to run practice; their `references.md` files contain complete source mappings.

## Course outcomes

By the end of the course, you can:

1. Create a reproducible analysis-ready dataset and verify that transformations preserved its meaning.
2. Describe variation and uncertainty, select an appropriate statistical method, and qualify a quantitative claim.
3. Design and validate an experiment; distinguish association from credible causal evidence.
4. Build and diagnose Bayesian models, then make decisions with explicit uncertainty and costs.
5. Create clear, truthful visualisations and use them to make a recommendation.
6. Complete an end-to-end analysis with a baseline, validation, operational implication, and limitations.

## Before you begin

**Required:** Python fundamentals through modules 01–03 of [Programming: Python](../programming/python/README.md). You should be comfortable with variables, functions, collections, files, and a terminal. No pandas or statistics course is assumed.

**Helpful alongside this course:** [Programming: SQL](../programming/sql/README.md). Unit 06 applies analytical SQL; the SQL module teaches the language in depth.

**Course language:** Python. The main tools are pandas, NumPy, SciPy, statsmodels, PyMC, matplotlib, seaborn, Plotly, and DuckDB. Environment setup belongs in each pillar README, not this syllabus.

## How to use the course

| Activity | What you do | What it shows |
|---|---|---|
| Chapters | Work through the notes and their examples in order. | You understand the concept and its worked application. |
| Deck review | Use the deck as a lecture recap and recall prompt. | You can explain the central idea without copying code. |
| Drills | Complete the chapter `Try it` exercises and interpretation checks. | You can select and apply a technique in a focused problem. |
| Labs | Create an analysis, chart, model, or decision brief. | You can combine techniques and defend a result. |
| Portfolio evidence | Save the unit's required output with assumptions and limits. | You can demonstrate analytical practice. |

## Course map

| Unit | Focus | Chapters | Portfolio evidence |
|---|---|---:|---|
| [01 Python for data analysis](#unit-01--python-for-data-analysis) | Make trustworthy tables | 7 | Cleaned dataset and validated analysis |
| [02 Probability and statistics](#unit-02--probability-and-statistics) | Quantify uncertainty | 8 | Statistical analysis memo |
| [03 Experimentation and causality](#unit-03--experimentation-and-causality) | Establish whether change caused an outcome | 5 | Experiment brief or causal-design critique |
| [04 Bayesian analysis](#unit-04--bayesian-analysis) | Decide under uncertainty | 7 | Diagnosed PyMC decision analysis |
| [05 Visualisation and storytelling](#unit-05--visualisation-and-storytelling) | Make evidence understandable | 5 | Decision-ready visual narrative or dashboard |
| [06 Applied analyses](#unit-06--applied-analyses) | Integrate the workflow | 10 | End-to-end analysis portfolio |

Units 01–03 are the core sequence. Take Unit 04 after Unit 03; it revisits inference and A/B testing through a Bayesian decision framework. Take Unit 05 before or alongside Unit 06.

Two steps cut across the units:

- **Step 4b, say what the model claims.** Once you can fit a regression, read [the data generating process](02-probability-and-statistics/notes/07-data-generating-process.md) and [panel data and fixed effects](02-probability-and-statistics/notes/08-panel-data-and-fixed-effects.md). Then, after the causal chapter, [matching and weighting](03-experimentation-and-causality/notes/05-matching-and-weighting.md), and after MCMC, [multilevel models and partial pooling](04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling.md). The test is whether you can say what your model assumes about how the rows came to exist, and what it would take to be wrong.
- **Step 8b, model an event, a state and a plan.** After the first six applied cases, take [survival and event history](06-applied-analyses/notes/07-survival-and-event-history.md) for the event, [states and sequences](06-applied-analyses/notes/08-states-and-sequences.md) for the state, then [marketing measurement](06-applied-analyses/notes/09-marketing-measurement.md) and [operations and supply chain](06-applied-analyses/notes/10-operations-and-supply-chain.md) for the plan. The test is whether you can pick the model from the decision, and name the assumption that would change it.

---

## Unit 01 — Python for data analysis

**Purpose:** Turn a raw export into a table you can safely analyse. Cleaning, joins, aggregation, time, and charts are correctness problems—not merely API calls.

**Learning objectives**

After this unit, you can:

1. Inspect a DataFrame's shape, types, labels, and missingness before using it.
2. Load a messy export into a rerunnable cleaning workflow and account for every changed or removed row.
3. Select, filter, and update data safely using label- and position-based indexing.
4. Reshape and join tables while specifying join semantics, validating cardinality, and reconciling totals.
5. Compute grouped summaries and rates correctly, including when groups or denominators are missing.
6. Work safely with time-indexed data and answer a question with an appropriate chart.

**Chapters:** [Series and DataFrame](01-python-for-data-analysis/notes/01-series-and-dataframe.md) · [Loading and cleaning](01-python-for-data-analysis/notes/02-loading-and-cleaning.md) · [Indexing and selection](01-python-for-data-analysis/notes/03-indexing-and-selection.md) · [Reshaping and joins](01-python-for-data-analysis/notes/04-reshaping-and-joins.md) · [Groupby and aggregation](01-python-for-data-analysis/notes/05-groupby-and-aggregation.md) · [Time series](01-python-for-data-analysis/notes/06-time-series.md) · [Plotting](01-python-for-data-analysis/notes/07-plotting.md)

**Review and practice:** [deck](01-python-for-data-analysis/slides/python-for-data-analysis.pptx) · chapter `Try it` exercises · seven progressive [practice notebooks](01-python-for-data-analysis/practice/).

**Mastery lab:** From a raw retail-style export, create a documented analysis-ready table. Show a rerunnable cleaning workflow, validated join, correctly aggregated metric, and one chart with a plain-language interpretation.

**Evidence:** Preserve the cleaning function, before/after row counts, and a reconciled business total. State `how` and `validate` for the join; show the numerator and denominator for a rate.

**Key sources:** Wes McKinney, [*Python for Data Analysis*](https://wesmckinney.com/book/) · Jake VanderPlas, [*Python Data Science Handbook*](https://jakevdp.github.io/PythonDataScienceHandbook/) · Wickham, [*Tidy Data*](https://doi.org/10.18637/jss.v059.i10) · [Kaggle Learn: Pandas](https://www.kaggle.com/learn/pandas).

---

## Unit 02 — Probability and statistics

**Purpose:** Make claims about data you have not seen without overstating what a sample says. This is the vocabulary for later experiments, models, and evaluations.

**Learning objectives**

After this unit, you can:

1. Audit an extract's unit of observation and distribution, then choose summaries that represent it honestly.
2. Use conditional probability, expectation, and variance to reason about uncertainty and base rates.
3. Match common analytical measures to probability distributions and identify when sampling assumptions fail.
4. Estimate quantities with intervals, bootstrap procedures, and sample-size reasoning.
5. Select, run, and interpret a hypothesis test, including an appropriate multiple-comparison correction.
6. Fit and interpret linear, logistic, and Poisson regression models with useful uncertainty checks.
7. Say what a model claims: write the data generating process you believe, and separate a better fit from better generalisation ([The data generating process](02-probability-and-statistics/notes/07-data-generating-process.md)).
8. Compare units with themselves using panel data and fixed effects, and say what that does and does not remove ([Panel data and fixed effects](02-probability-and-statistics/notes/08-panel-data-and-fixed-effects.md)).

**Chapters:** [Descriptive statistics and EDA](02-probability-and-statistics/notes/01-descriptive-statistics-and-eda.md) · [Probability foundations](02-probability-and-statistics/notes/02-probability-foundations.md) · [Distributions and sampling](02-probability-and-statistics/notes/03-distributions-and-sampling.md) · [Estimation](02-probability-and-statistics/notes/04-estimation.md) · [Hypothesis testing](02-probability-and-statistics/notes/05-hypothesis-testing.md) · [Regression and GLMs](02-probability-and-statistics/notes/06-regression-and-glms.md) · [The data generating process](02-probability-and-statistics/notes/07-data-generating-process.md) · [Panel data and fixed effects](02-probability-and-statistics/notes/08-panel-data-and-fixed-effects.md)

**Review and practice:** [deck](02-probability-and-statistics/slides/probability-and-statistics.pptx) · chapter `Try it` exercises and interview checks · optional guided [statistical-analysis notebook](02-probability-and-statistics/practice/5_Statistical_Analysis.ipynb).

**Mastery lab:** Audit an unfamiliar extract, state the estimand and independent unit, report a point estimate and interval, answer one predeclared comparison, then fit and interpret a suitable regression with diagnostics.

**Evidence:** A statistical memo containing the unit of analysis, distribution or visual checks, interval, justified test or model, effect size, and limits of the conclusion.

**Key sources:** Bruce & Bruce, *Practical Statistics for Data Scientists* · Downey, [*Think Stats*](https://allendowney.github.io/ThinkStats/) · James et al., [*An Introduction to Statistical Learning with Applications in Python*](https://www.statlearning.com/) · [MIT 18.650](https://ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/) · Wasserstein and Lazar, [ASA Statement on p-Values](https://doi.org/10.1080/00031305.2016.1154108).

---

## Unit 03 — Experimentation and causality

**Purpose:** Answer whether a change caused an outcome. Learn the discipline that makes an A/B result trustworthy and the assumptions required when randomisation is unavailable.

**Learning objectives**

After this unit, you can:

1. Design an A/B test: randomisation unit, estimand, MDE, sample size, stopping rule, and reporting plan.
2. Select a north-star metric, guardrail, and diagnostic metric; interpret ratios and denominator changes correctly.
3. Validate an experiment before trusting its outcome, including SRM, balance, and unit-of-analysis checks.
4. Apply CUPED and suitable sequential testing, and explain interference and overlapping-experiment risks.
5. Draw a causal graph and distinguish confounders, mediators, and colliders.
6. Choose and qualify DiD, IV, RD, weighting, or synthetic control, naming its identifying assumption.
7. Build a comparison group by matching or weighting, show balance before reading the outcome, and say what a hidden confounder would have to do to undo the result ([Matching and weighting](03-experimentation-and-causality/notes/05-matching-and-weighting.md)).

**Chapters:** [A/B testing](03-experimentation-and-causality/notes/01-ab-testing.md) · [Metrics and KPI design](03-experimentation-and-causality/notes/02-metrics-and-kpi-design.md) · [Experimentation at scale](03-experimentation-and-causality/notes/03-experimentation-at-scale.md) · [Correlation, confounding and causation](03-experimentation-and-causality/notes/04-correlation-and-causation.md) · [Matching and weighting](03-experimentation-and-causality/notes/05-matching-and-weighting.md)

**Review and practice:** [deck](03-experimentation-and-causality/slides/experimentation-and-causality.pptx) · runnable chapter examples and drills, including the Larkspur checkout experiment and causal-reasoning examples.

**Mastery lab:** Analyse a checkout experiment and write a launch/no-launch brief. For an observational question, instead submit a causal diagram, proposed design, and the assumption that makes the estimate interpretable.

**Evidence:** State the decision, OEC and guardrails, sample-size and stopping logic; validate assignment; report effect and uncertainty; and explain the recommendation or why evidence is insufficient.

**Key sources:** Kohavi, Tang, and Xu, [*Trustworthy Online Controlled Experiments*](https://experimentguide.com/) · Kohavi et al., [*Controlled Experiments on the Web*](https://doi.org/10.1007/s10618-008-0114-1) · Dmitriev et al., [*A Dirty Dozen*](https://doi.org/10.1145/3097983.3098024) · Cunningham, [*Causal Inference: The Mixtape*](https://mixtape.scunning.com/) · [Brady Neal's course](https://www.bradyneal.com/causal-inference-course).

---

## Unit 04 — Bayesian analysis

**Purpose:** Revisit inference as a decision problem. Use prior information, posterior uncertainty, diagnostics, and losses to answer what should be done—not only whether a null hypothesis is surprising.

**Learning objectives**

After this unit, you can:

1. Express an analytical question as a generative model and compute or simulate a posterior.
2. Fit a basic Bayesian model in PyMC and interpret posterior probabilities and credible intervals.
3. Diagnose sampling quality with R-hat, ESS, traces, and divergences, then improve an ill-behaved model.
4. Select, justify, and pressure-test priors with prior-predictive simulation.
5. Compare variants in a Bayesian A/B test using probability of superiority, lift uncertainty, and expected loss.
6. Translate posterior uncertainty into a decision by defining an appropriate loss function.
7. Fit a multilevel model, choose between clustering and modelling a group, and read many segment effects with partial pooling ([Multilevel models and partial pooling](04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling.md)).

**Chapters:** [Bayesian inference](04-bayesian-analysis/notes/01-bayesian-inference.md) · [MCMC and PyMC](04-bayesian-analysis/notes/02-mcmc-and-pymc.md) · [Priors and bandits](04-bayesian-analysis/notes/03-priors-and-bandits.md) · [Bayesian A/B testing](04-bayesian-analysis/notes/04-bayesian-ab-testing.md) · [Loss functions and Bayesian decisions](04-bayesian-analysis/notes/05-loss-functions-and-decisions.md) · [Bayesian machine learning](04-bayesian-analysis/notes/06-bayesian-machine-learning.md) · [Multilevel models and partial pooling](04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling.md)

**Review and practice:** [deck](04-bayesian-analysis/slides/bayesian-analysis.pptx) · fixed-seed chapter examples · optional advanced [Bayesian ML coursework](04-bayesian-analysis/practice/BayesianML/README.md).

**Mastery lab:** Reanalyse the checkout A/B case with a PyMC model. Run prior-predictive and sampler checks, quantify posterior uncertainty, define the cost of each mistake, and make a ship/no-ship recommendation.

**Evidence:** Submit a reproducible model, diagnostic summary, posterior answer, loss-based recommendation, and a brief comparison with the fixed-horizon frequentist analysis. The advanced coursework is optional archival material, not required practice.

**Key sources:** Davidson-Pilon, [*Bayesian Methods for Hackers*](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers) · [McElreath's lectures](https://www.youtube.com/playlist?list=PLDcUM9US4XdPz-KxHM4XHt7uUVGWWVSus) · Gelman et al., [*Bayesian Data Analysis*](https://sites.stat.columbia.edu/gelman/book/) · [Aalto Bayesian Data Analysis](https://avehtari.github.io/BDA_course_Aalto/) · [PyMC examples](https://www.pymc.io/projects/examples/en/latest/gallery.html).

---

## Unit 05 — Visualisation and storytelling

**Purpose:** Make an analytical result legible and useful. Select encodings, build static and interactive charts, and shape them into an argument without overstating what the data says.

**Learning objectives**

After this unit, you can:

1. Match a question and data type to a chart using perceptually strong encodings and honest scales.
2. Build clear static charts with matplotlib and seaborn, including annotations and uncertainty where needed.
3. Design interactive charts with useful filtering, tooltips, and accessible fallbacks.
4. Explain when to use Python plotting libraries, D3, Vega-Lite, or Observable Plot, and implement a small web chart.
5. Design a dashboard and narrative that give a decision-maker context, evidence, recommendation, and limitations.

**Chapters:** [Grammar of graphics and chart choice](05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice.md) · [Matplotlib and seaborn](05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn.md) · [Plotly and interactive charts](05-visualisation-and-storytelling/notes/03-plotly-and-interactive.md) · [JavaScript: D3, Vega-Lite and Observable Plot](05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot.md) · [Dashboards and storytelling with data](05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling.md)

**Review and practice:** [deck](05-visualisation-and-storytelling/slides/visualisation-and-storytelling.pptx) · chapter exercises · runnable [practice scripts and dashboard](05-visualisation-and-storytelling/practice/).

**Mastery lab:** Take one decision from an earlier unit and create a concise visual narrative or dashboard: audience and decision, chart choice, source and transformation notes, recommendation, and the limitation most likely to change it.

**Evidence:** A reviewer can understand the main claim without the code, trace it to a valid measure, and identify the action, uncertainty, and guardrail. Include chart source and an accessible static fallback for interactive work.

**Key sources:** Knaflic, [*Storytelling with Data*](https://www.storytellingwithdata.com/books) · Wilke, [*Fundamentals of Data Visualization*](https://clauswilke.com/dataviz/) · Munzner, [*Visualization Analysis and Design*](https://www.cs.ubc.ca/~tmm/vadbook/) · Cleveland and McGill, [*Graphical Perception*](https://doi.org/10.1080/01621459.1984.10478080) · [Kaggle Learn: Data Visualization](https://www.kaggle.com/learn/data-visualization).

---

## Unit 06 — Applied analyses

**Purpose:** Do the complete job. Each case begins with a decision and ends with a recommendation, using earlier units to establish a baseline, validate results, and make value concrete.

**Learning objectives**

After this unit, you can:

1. Frame an analytical request as a decision, metric, baseline, and validation plan.
2. Forecast demand with multiple baselines, rolling-origin backtests, and an operational recommendation.
3. Build and evaluate a credit-scorecard-style analysis while distinguishing predictive performance, calibration, drift, and policy constraints.
4. Diagnose retention and conversion with cohorts and funnels, separating rate from mix and association from causation.
5. Segment customers responsibly, validate later usefulness, and distinguish targeting from persuadability.
6. Use analytical SQL to reconcile changes in a business total and explain their drivers.
7. Model time to an event, treating customers who have not left yet as censored ([Survival and event history](06-applied-analyses/notes/07-survival-and-event-history.md)).
8. Model customers as states and sequences, and check a transition matrix on a holdout before using it to forecast ([States and sequences](06-applied-analyses/notes/08-states-and-sequences.md)).
9. Separate attribution from incrementality when you allocate a marketing budget ([Marketing measurement](06-applied-analyses/notes/09-marketing-measurement.md)).
10. Turn a forecast's error distribution into stock and staffing decisions ([Operations and supply chain](06-applied-analyses/notes/10-operations-and-supply-chain.md)).

**Chapters:** [Forecasting](06-applied-analyses/notes/01-forecasting.md) · [Credit scoring](06-applied-analyses/notes/02-credit-scoring.md) · [Cohort and retention](06-applied-analyses/notes/03-cohort-and-retention.md) · [Funnel and conversion](06-applied-analyses/notes/04-funnel-and-conversion.md) · [Segmentation and RFM](06-applied-analyses/notes/05-segmentation-and-rfm.md) · [SQL for analytics](06-applied-analyses/notes/06-sql-for-analytics.md) · [Survival and event history](06-applied-analyses/notes/07-survival-and-event-history.md) · [States and sequences](06-applied-analyses/notes/08-states-and-sequences.md) · [Marketing measurement](06-applied-analyses/notes/09-marketing-measurement.md) · [Operations and supply chain](06-applied-analyses/notes/10-operations-and-supply-chain.md)

**Review and practice:** [deck](06-applied-analyses/slides/applied-analyses.pptx) · six runnable [case-study scripts](06-applied-analyses/practice/) and their generated or documented datasets.

**Mastery portfolio:** Complete at least two cases, including forecasting or credit scoring and one of cohort, funnel, segmentation, or SQL. For each: frame the decision, show a baseline, validate against something known, quantify an operational or financial implication, recommend an action, and state what could overturn it.

**Evidence:** A reproducible analysis, decision memo, and clear visual. Reconcile reported totals to the source, distinguish prediction from a causal claim, and place uncertainty beside the recommendation.

**Key sources:** Hyndman and Athanasopoulos, [*Forecasting: Principles and Practice*](https://otexts.com/fpp3/) · Grömping, [*South German Credit Data*](http://www1.beuth-hochschule.de/FB_II/reports/Report-2019-004.pdf) · Fader and Hardie, [*How to Project Customer Retention*](https://doi.org/10.1002/dir.20074) · Fader, Hardie, and Lee, [*RFM and CLV*](https://doi.org/10.1509/jmkr.2005.42.4.415) · [Mode SQL tutorial](https://mode.com/sql-tutorial/).

---

## Completion standard and next steps

You have completed the course when your portfolio demonstrates the six unit outcomes: a reproducible data-preparation analysis, a statistical memo, an experiment or causal-design brief, a diagnosed Bayesian decision analysis, a visual recommendation, and two end-to-end applied cases. Correct code alone is not enough: every piece should name its decision, unit of analysis, checks, uncertainty, and limitations.

Continue to [Data Science](../data-science/README.md) for predictive modelling and model research; [Data Engineering](../data-engineering/README.md) for pipelines and infrastructure; or [Generative AI](../generative-ai/README.md) for LLM-powered applications.

## Complete references

Each unit's complete, chapter-level source map is maintained separately:

- [01 Python for data analysis](01-python-for-data-analysis/references.md)
- [02 Probability and statistics](02-probability-and-statistics/references.md)
- [03 Experimentation and causality](03-experimentation-and-causality/references.md)
- [04 Bayesian analysis](04-bayesian-analysis/references.md)
- [05 Visualisation and storytelling](05-visualisation-and-storytelling/references.md)
- [06 Applied analyses](06-applied-analyses/references.md)
