# Data Analytics

> What a data analyst has to know: get data into a frame, describe it, test a claim, model a relationship, forecast it, explain it to someone, and know when the numbers lie.

Position in the path: [programming/python](../programming/python/README.md) modules 01 to 03 come first, and [SQL](../programming/sql/README.md) helps alongside. [Data science](../data-science/README.md), [data engineering](../data-engineering/README.md) and [generative AI](../generative-ai/README.md) build on this subject.

## What it is

An analyst is handed a question and some data, and owes back an answer that somebody can act on. That takes more than statistics. The data has to be loaded and cleaned before anyone can test it, and a correct result is wasted if the person deciding cannot read the chart. The six pillars follow that order of work, from a messy export to a recommendation.

The thread through all of them is the last clause of the framing, knowing when the numbers lie. A many-to-many join inflates revenue without raising an error. A mean of rates ranks regions wrongly. A test stopped at the first small p-value finds effects that are not there. A chart with two y axes implies a relationship its author chose. None of these announce themselves, so each pillar teaches the check along with the method.

## Course outcomes

By the end of the course, you can:

1. Create a reproducible analysis-ready dataset and verify that transformations preserved its meaning.
2. Describe variation and uncertainty, select an appropriate statistical method, and qualify a quantitative claim.
3. Design and validate an experiment; distinguish association from credible causal evidence.
4. Build and diagnose Bayesian models, then make decisions with explicit uncertainty and costs.
5. Create clear, truthful visualisations and use them to make a recommendation.
6. Complete an end-to-end analysis with a baseline, validation, operational implication, and limitations.

## Before you begin

**Required:** Python fundamentals through modules 01 to 03 of [Programming: Python](../programming/python/README.md). You should be comfortable with variables, functions, collections, files, and a terminal. No pandas or statistics course is assumed. **Helpful alongside this course:** [Programming: SQL](../programming/sql/README.md). Unit 06 applies analytical SQL; the SQL track teaches the language in depth.

**Course language:** Python. The main tools are pandas, NumPy, SciPy, statsmodels, PyMC, matplotlib, seaborn, Plotly, and DuckDB. Each pillar README covers its own setup and how to run its practice.

## How to use the course

| Activity | What you do | What it shows |
|---|---|---|
| Chapters | Work through the notes and their examples in order. | You understand the concept and its worked application. |
| Deck review | Use the deck as a lecture recap and recall prompt. | You can explain the central idea without copying code. |
| Drills | Complete the chapter `Try it` exercises and interpretation checks. | You can select and apply a technique in a focused problem. |
| Labs | Create an analysis, chart, model, or decision brief. | You can combine techniques and defend a result. |
| Portfolio evidence | Save the unit's required output with assumptions and limits. | You can demonstrate analytical practice. |

## The six pillars

| Pillar | The analyst's job | What you learn | Portfolio evidence |
|---|---|---|---|
| [01 Python for data analysis](01-python-for-data-analysis/README.md) | get data into a frame | Load, clean, select, join, summarise and plot data in pandas, assuming no earlier pandas. | Cleaned dataset and validated analysis |
| [02 Probability and statistics](02-probability-and-statistics/README.md) | describe it, test a claim, model a relationship | Describe data, reason with probability, estimate with intervals, test and fit regressions, then say what a model claims. | Statistical analysis memo |
| [03 Experimentation and causality](03-experimentation-and-causality/README.md) | test a claim about a change | Run A/B tests, run them at scale, and decide when a correlation can bear a causal reading, including by matching and weighting. | Experiment brief or causal-design critique |
| [04 Bayesian analysis](04-bayesian-analysis/README.md) | decide under uncertainty | Answer the same questions with posteriors: PyMC, priors, Bayesian A/B tests, loss functions and multilevel models. | Diagnosed PyMC decision analysis |
| [05 Visualisation and storytelling](05-visualisation-and-storytelling/README.md) | explain it to someone | Choose a chart, draw it in Python and JavaScript, and use it to get a decision made. | Decision-ready visual narrative or dashboard |
| [06 Applied analyses](06-applied-analyses/README.md) | forecast it, and do the real work | End-to-end analyses: forecasting, credit scoring, cohorts, funnels, segmentation, SQL, survival, journeys, marketing measurement, operations, metric trees and surveys. | End-to-end analysis portfolio |

Read them in order the first time. Units 01 to 03 are the core sequence. Take Unit 04 after Unit 03; it revisits inference and A/B testing through a Bayesian decision framework. Take Unit 05 before or alongside Unit 06.

## Two ways to answer the same question

Pillars 02 and 03 and pillar 04 answer the same questions by different routes, and an analyst should be able to do both.

| | Frequentist (02, 03) | Bayesian (04) |
|---|---|---|
| Core question | How surprising is this data if nothing is going on? | Given the data, what should I believe and do? |
| Tools | `scipy.stats`, `statsmodels` | PyMC, ArviZ, conjugate Beta updates |
| A/B testing | [Power, sample size, z-test, peeking](03-experimentation-and-causality/notes/01-ab-testing.md) | [P(B > A), expected loss](04-bayesian-analysis/notes/04-bayesian-ab-testing.md) |
| Strength | Standard, fast, and what most teams report | Small samples, prior knowledge, decisions with asymmetric costs |

Name the distribution, fix the sample size before you look, and report effect sizes with intervals and not bare p-values.

## Units

### [01 Python for data analysis](01-python-for-data-analysis/README.md)

**Purpose:** Turn a raw export into a table you can safely analyse. Cleaning, joins, aggregation, time, and charts are correctness problems, not merely API calls ([McKinney](https://wesmckinney.com/book/); [Wickham](https://doi.org/10.18637/jss.v059.i10) on tidy shape).

**Learning objectives.** After this unit, you can:

1. Inspect a DataFrame's shape, types, labels, and missingness before using it.
2. Load a messy export into a rerunnable cleaning workflow and account for every changed or removed row.
3. Select, filter, and update data safely using label- and position-based indexing.
4. Reshape and join tables while specifying join semantics, validating cardinality, and reconciling totals.
5. Compute grouped summaries and rates correctly, including when groups or denominators are missing.
6. Work safely with time-indexed data and answer a question with an appropriate chart.

**Review and practice:** [deck](01-python-for-data-analysis/slides/python-for-data-analysis.pptx) · chapter `Try it` exercises · progressive [practice notebooks](01-python-for-data-analysis/practice/).

**Mastery lab:** From a raw retail-style export, create a documented analysis-ready table. Show a rerunnable cleaning workflow, validated join, correctly aggregated metric, and one chart with a plain-language interpretation.

**Evidence:** Preserve the cleaning function, before/after row counts, and a reconciled business total. State `how` and `validate` for the join; show the numerator and denominator for a rate.

**Key sources:** Wes McKinney, [*Python for Data Analysis*](https://wesmckinney.com/book/) · Jake VanderPlas, [*Python Data Science Handbook*](https://jakevdp.github.io/PythonDataScienceHandbook/) · Wickham, [*Tidy Data*](https://doi.org/10.18637/jss.v059.i10) · [Kaggle Learn: Pandas](https://www.kaggle.com/learn/pandas).

### [02 Probability and statistics](02-probability-and-statistics/README.md)

**Purpose:** Make claims about data you have not seen without overstating what a sample says. This is the vocabulary for later experiments, models, and evaluations.

**Learning objectives.** After this unit, you can:

1. Audit an extract's unit of observation and distribution, then choose summaries that represent it honestly.
2. Use conditional probability, expectation, and variance to reason about uncertainty and base rates.
3. Match common analytical measures to probability distributions and identify when sampling assumptions fail.
4. Estimate quantities with intervals, bootstrap procedures, and sample-size reasoning.
5. Select, run, and interpret a hypothesis test, including an appropriate multiple-comparison correction ([Wasserstein and Lazar](https://doi.org/10.1080/00031305.2016.1154108) on what a p-value does not say).
6. Fit and interpret linear, logistic, and Poisson regression models with useful uncertainty checks ([James et al.](https://www.statlearning.com/)).
7. Say what a model claims: write the data generating process you believe, and separate a better fit from better generalisation ([The data generating process](02-probability-and-statistics/notes/07-data-generating-process.md)).
8. Compare units with themselves using panel data and fixed effects, and say what that does and does not remove ([Panel data and fixed effects](02-probability-and-statistics/notes/08-panel-data-and-fixed-effects.md)).

**Review and practice:** [deck](02-probability-and-statistics/slides/probability-and-statistics.pptx) · chapter `Try it` exercises and interview checks · optional guided [statistical-analysis notebook](02-probability-and-statistics/practice/5_Statistical_Analysis.ipynb).

**Mastery lab:** Audit an unfamiliar extract, state the estimand and independent unit, report a point estimate and interval, answer one predeclared comparison, then fit and interpret a suitable regression with diagnostics.

**Evidence:** A statistical memo containing the unit of analysis, distribution or visual checks, interval, justified test or model, effect size, and limits of the conclusion.

**Key sources:** Bruce & Bruce, *Practical Statistics for Data Scientists* · Downey, [*Think Stats*](https://allendowney.github.io/ThinkStats/) · James et al., [*An Introduction to Statistical Learning with Applications in Python*](https://www.statlearning.com/) · [MIT 18.650](https://ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/) · Wasserstein and Lazar, [ASA Statement on p-Values](https://doi.org/10.1080/00031305.2016.1154108).

### [03 Experimentation and causality](03-experimentation-and-causality/README.md)

**Purpose:** Answer whether a change caused an outcome. Learn the discipline that makes an A/B result trustworthy and the assumptions required when randomisation is unavailable.

**Learning objectives.** After this unit, you can:

1. Design an A/B test: randomisation unit, estimand, MDE, sample size, stopping rule, and reporting plan ([Kohavi et al. 2009](https://doi.org/10.1007/s10618-008-0114-1)).
2. Select a north-star metric, guardrail, and diagnostic metric; interpret ratios and denominator changes correctly.
3. Validate an experiment before trusting its outcome, including SRM, balance, and unit-of-analysis checks ([Dmitriev et al.](https://doi.org/10.1145/3097983.3098024)).
4. Apply CUPED and suitable sequential testing, and explain interference and overlapping-experiment risks.
5. Draw a causal graph and distinguish confounders, mediators, and colliders.
6. Choose and qualify DiD, IV, RD, weighting, or synthetic control, naming its identifying assumption ([Cunningham](https://mixtape.scunning.com/)).
7. Build a comparison group by matching or weighting, show balance before reading the outcome, and say what a hidden confounder would have to do to undo the result ([Matching and weighting](03-experimentation-and-causality/notes/05-matching-and-weighting.md)).

**Review and practice:** [deck](03-experimentation-and-causality/slides/experimentation-and-causality.pptx) · runnable chapter examples and drills, including the Larkspur checkout experiment and causal-reasoning examples.

**Mastery lab:** Analyse a checkout experiment and write a launch/no-launch brief. For an observational question, instead submit a causal diagram, proposed design, and the assumption that makes the estimate interpretable.

**Evidence:** State the decision, OEC and guardrails, sample-size and stopping logic; validate assignment; report effect and uncertainty; and explain the recommendation or why evidence is insufficient.

**Key sources:** Kohavi, Tang, and Xu, [*Trustworthy Online Controlled Experiments*](https://experimentguide.com/) · Kohavi et al., [*Controlled Experiments on the Web*](https://doi.org/10.1007/s10618-008-0114-1) · Dmitriev et al., [*A Dirty Dozen*](https://doi.org/10.1145/3097983.3098024) · Cunningham, [*Causal Inference: The Mixtape*](https://mixtape.scunning.com/) · [Brady Neal's course](https://www.bradyneal.com/causal-inference-course).

### [04 Bayesian analysis](04-bayesian-analysis/README.md)

**Purpose:** Revisit inference as a decision problem. Use prior information, posterior uncertainty, diagnostics, and losses to answer what should be done, not only whether a null hypothesis is surprising ([Davidson-Pilon](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers)).

**Learning objectives.** After this unit, you can:

1. Express an analytical question as a generative model and compute or simulate a posterior.
2. Fit a basic Bayesian model in PyMC and interpret posterior probabilities and credible intervals.
3. Diagnose sampling quality with R-hat, ESS, traces, and divergences, then improve an ill-behaved model.
4. Select, justify, and pressure-test priors with prior-predictive simulation.
5. Compare variants in a Bayesian A/B test using probability of superiority, lift uncertainty, and expected loss.
6. Translate posterior uncertainty into a decision by defining an appropriate loss function.
7. Fit a multilevel model, choose between clustering and modelling a group, and read many segment effects with partial pooling ([Multilevel models and partial pooling](04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling.md)).

**Review and practice:** [deck](04-bayesian-analysis/slides/bayesian-analysis.pptx) · fixed-seed chapter examples · optional advanced [Bayesian ML coursework](04-bayesian-analysis/practice/BayesianML/README.md).

**Mastery lab:** Reanalyse the checkout A/B case with a PyMC model. Run prior-predictive and sampler checks, quantify posterior uncertainty, define the cost of each mistake, and make a ship/no-ship recommendation.

**Evidence:** Submit a reproducible model, diagnostic summary, posterior answer, loss-based recommendation, and a brief comparison with the fixed-horizon frequentist analysis. The advanced coursework is optional archival material, not required practice.

**Key sources:** Davidson-Pilon, [*Bayesian Methods for Hackers*](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers) · [McElreath's lectures](https://www.youtube.com/playlist?list=PLDcUM9US4XdPz-KxHM4XHt7uUVGWWVSus) · Gelman et al., [*Bayesian Data Analysis*](https://sites.stat.columbia.edu/gelman/book/) · [Aalto Bayesian Data Analysis](https://avehtari.github.io/BDA_course_Aalto/) · [PyMC examples](https://www.pymc.io/projects/examples/en/latest/gallery.html).

### [05 Visualisation and storytelling](05-visualisation-and-storytelling/README.md)

**Purpose:** Make an analytical result legible and useful. Select encodings, build static and interactive charts, and shape them into an argument without overstating what the data says.

**Learning objectives.** After this unit, you can:

1. Match a question and data type to a chart using perceptually strong encodings and honest scales ([Cleveland and McGill](https://doi.org/10.1080/01621459.1984.10478080)).
2. Build clear static charts with matplotlib and seaborn, including annotations and uncertainty where needed.
3. Design interactive charts with useful filtering, tooltips, and accessible fallbacks.
4. Explain when to use Python plotting libraries, D3, Vega-Lite, or Observable Plot, and implement a small web chart.
5. Design a dashboard and narrative that give a decision-maker context, evidence, recommendation, and limitations ([Knaflic](https://www.storytellingwithdata.com/books)).
6. Choose a dashboard stack by audience, interaction, data volume and maintainer, and get Python results to a browser without leaking or overloading ([chapter 6](05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend.md)).

**Review and practice:** [deck](05-visualisation-and-storytelling/slides/visualisation-and-storytelling.pptx) · chapter exercises · runnable [practice scripts and dashboard](05-visualisation-and-storytelling/practice/).

**Mastery lab:** Take one decision from an earlier unit and create a concise visual narrative or dashboard: audience and decision, chart choice, source and transformation notes, recommendation, and the limitation most likely to change it.

**Evidence:** A reviewer can understand the main claim without the code, trace it to a valid measure, and identify the action, uncertainty, and guardrail. Include chart source and an accessible static fallback for interactive work.

**Key sources:** Knaflic, [*Storytelling with Data*](https://www.storytellingwithdata.com/books) · Wilke, [*Fundamentals of Data Visualization*](https://clauswilke.com/dataviz/) · Munzner, [*Visualization Analysis and Design*](https://www.cs.ubc.ca/~tmm/vadbook/) · Cleveland and McGill, [*Graphical Perception*](https://doi.org/10.1080/01621459.1984.10478080) · [Kaggle Learn: Data Visualization](https://www.kaggle.com/learn/data-visualization).

### [06 Applied analyses](06-applied-analyses/README.md)

**Purpose:** Do the complete job. Each case begins with a decision and ends with a recommendation, using earlier units to establish a baseline, validate results, and make value concrete.

**Learning objectives.** After this unit, you can:

1. Frame an analytical request as a decision, metric, baseline, and validation plan.
2. Forecast demand with multiple baselines, rolling-origin backtests, and an operational recommendation ([Hyndman and Athanasopoulos](https://otexts.com/fpp3/)).
3. Build and evaluate a credit-scorecard-style analysis while distinguishing predictive performance, calibration, drift, and policy constraints.
4. Diagnose retention and conversion with cohorts and funnels, separating rate from mix and association from causation ([Fader and Hardie](https://doi.org/10.1002/dir.20074)).
5. Segment customers responsibly, validate later usefulness, and distinguish targeting from persuadability.
6. Use analytical SQL to reconcile changes in a business total and explain their drivers.
7. Model time to an event, treating customers who have not left yet as censored ([Survival and event history](06-applied-analyses/notes/07-survival-and-event-history.md)).
8. Model customers as states and sequences, and check a transition matrix on a holdout before using it to forecast ([States and sequences](06-applied-analyses/notes/08-states-and-sequences.md)).
9. Separate attribution from incrementality when you allocate a marketing budget ([Marketing measurement](06-applied-analyses/notes/09-marketing-measurement.md)).
10. Turn a forecast's error distribution into stock and staffing decisions ([Operations and supply chain](06-applied-analyses/notes/10-operations-and-supply-chain.md)).
11. Design a survey, weight it to known totals, and report what its margin of error omits ([Surveys and sampling design](06-applied-analyses/notes/12-surveys-and-sampling-design.md)).

**Review and practice:** [deck](06-applied-analyses/slides/applied-analyses.pptx) · runnable [case-study scripts](06-applied-analyses/practice/) and their generated or documented datasets.

**Mastery portfolio:** Complete at least two cases, including forecasting or credit scoring and one of cohort, funnel, segmentation, or SQL. For each: frame the decision, show a baseline, validate against something known, quantify an operational or financial implication, recommend an action, and state what could overturn it.

**Evidence:** A reproducible analysis, decision memo, and clear visual. Reconcile reported totals to the source, distinguish prediction from a causal claim, and place uncertainty beside the recommendation.

**Key sources:** Hyndman and Athanasopoulos, [*Forecasting: Principles and Practice*](https://otexts.com/fpp3/) · Grömping, [*South German Credit Data*](http://www1.beuth-hochschule.de/FB_II/reports/Report-2019-004.pdf) · Fader and Hardie, [*How to Project Customer Retention*](https://doi.org/10.1002/dir.20074) · Fader, Hardie, and Lee, [*RFM and CLV*](https://doi.org/10.1509/jmkr.2005.42.4.415) · [Mode SQL tutorial](https://mode.com/sql-tutorial/).

## Rules of thumb

| Rule | Where |
|---|---|
| State `how` and `validate` on a merge, then compare row counts and one total before and after | [01](01-python-for-data-analysis/notes/04-reshaping-and-joins.md) |
| For a group's rate, sum the numerator and the denominator and then divide; never average the rates | [01](01-python-for-data-analysis/notes/05-groupby-and-aggregation.md) |
| Make absent days visible with `asfreq`, and keep model features looking backward | [01](01-python-for-data-analysis/notes/06-time-series.md) |
| `sf(k)` is P(X > k); for "k or more" on a discrete distribution, pass k − 1 | [02](02-probability-and-statistics/notes/03-distributions-and-sampling.md) |
| The most extreme averages come from the smallest groups, so always show N | [02](02-probability-and-statistics/notes/03-distributions-and-sampling.md) |
| Default to Welch's t (`equal_var=False`) | [02](02-probability-and-statistics/notes/05-hypothesis-testing.md) |
| Twenty independent tests at α = 0.05 give a 64% chance of at least one false positive; use Holm or BH | [02](02-probability-and-statistics/notes/05-hypothesis-testing.md) |
| Halving the minimum detectable effect multiplies the sample size by about four | [03](03-experimentation-and-causality/notes/01-ab-testing.md) |
| Do not stop a fixed-horizon test the first time p < 0.05 | [03](03-experimentation-and-causality/notes/01-ab-testing.md) |
| Control for confounders, never for colliders | [03](03-experimentation-and-causality/notes/04-correlation-and-causation.md) |
| R-hat at most 1.01, no divergences and ESS in the hundreds before you trust a posterior | [04](04-bayesian-analysis/notes/02-mcmc-and-pymc.md) |
| Never put zero prior mass where the truth could be | [04](04-bayesian-analysis/notes/03-priors-and-bandits.md) |
| Ship B when the expected loss of choosing it is below the smallest difference you care about | [04](04-bayesian-analysis/notes/04-bayesian-ab-testing.md) |
| Squared loss gives the mean, absolute loss the median, zero-one loss the MAP; any other loss needs an optimiser | [04](04-bayesian-analysis/notes/05-loss-functions-and-decisions.md) |
| Beat a baseline first, and backtest over many origins because one split is one anecdote | [06](06-applied-analyses/README.md#rules-of-thumb) |
| Split a change in any aggregate into rate and mix before you explain it | [06](06-applied-analyses/README.md#rules-of-thumb) |
| Write the data generating process you believe before you fit, and simulate from it to see whether your estimator recovers it | [02](02-probability-and-statistics/notes/07-data-generating-process.md) |
| A better fit in this sample is not a better answer for the population; ask how the rows got in before you admire R² | [02](02-probability-and-statistics/notes/07-data-generating-process.md) |
| Match or weight on covariates measured before treatment, show the balance table first, and say what an unmeasured confounder would have to do to undo the result | [03](03-experimentation-and-causality/notes/05-matching-and-weighting.md) |
| Cluster when groups are a nuisance, model them when they are the question | [04](04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling.md) |
| Reading many segment effects? Partially pool them first, because the winning segment's raw estimate is exaggerated | [04](04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling.md) |
| A customer who has not churned yet is censored, not retained; never average lifetimes over the churned only | [06](06-applied-analyses/notes/07-survival-and-event-history.md) |
| A transition matrix describes the past; it forecasts only if the process is stationary, so check it on a holdout period | [06](06-applied-analyses/notes/08-states-and-sequences.md) |
| Attribution allocates credit; only an experiment or a model with a causal design measures incrementality | [06](06-applied-analyses/notes/09-marketing-measurement.md) |
| The forecast's error distribution is the input to the stock decision, not the point forecast | [06](06-applied-analyses/notes/10-operations-and-supply-chain.md) |
| A margin of error measures sampling error only: name the design, the weights and the nonresponse risk beside it | [06](06-applied-analyses/notes/12-surveys-and-sampling-design.md) |
| Before tuning, read the false positives and false negatives: what the model finds, what it misses, and whether the data could tell them apart | [DS 01](../data-science/01-classical-ml/notes/12-reading-the-errors.md) |
| Read errors on one split and score fixes on another; fix a class of error, never the rows you read | [DS 01](../data-science/01-classical-ml/notes/12-reading-the-errors.md) |
| Start from the target: it picks the model family, the loss, the metric and the baseline, in that order | [DS 01](../data-science/01-classical-ml/notes/11-choosing-a-metric.md) |

## Completion standard and next steps

You have completed the course when your portfolio demonstrates the six unit outcomes: a reproducible data-preparation analysis, a statistical memo, an experiment or causal-design brief, a diagnosed Bayesian decision analysis, a visual recommendation, and two end-to-end applied cases. Correct code alone is not enough: every piece should name its decision, unit of analysis, checks, uncertainty, and limitations.

Continue to [Data Science](../data-science/README.md) for predictive modelling and model research; [Data Engineering](../data-engineering/README.md) for pipelines and infrastructure; or [Generative AI](../generative-ai/README.md) for LLM-powered applications.

## Primary texts

- McKinney, *Python for Data Analysis*: the base text for Unit 01; its pandas advice predates pandas 3, so the notes correct it where needed
- Bruce and Bruce, *Practical Statistics for Data Scientists*: Units 02, 03 and 06
- Reinhart, *Statistics Done Wrong*: how statistical claims fail, Units 02 and 03
- Pearl, Glymour and Jewell, *Causal Inference in Statistics: A Primer*: the causal reasoning in Unit 03
- Davidson-Pilon, *Bayesian Methods for Hackers*: the spine of Unit 04
- Knaflic, *Storytelling with Data*: Unit 05
- Hyndman and Athanasopoulos, *Forecasting: Principles and Practice*: Unit 06

Everything else, including free courses and videos: [references.md](references.md). Each pillar's own `references.md` maps its sources to its chapters.
