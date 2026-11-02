# Data Analytics: curriculum

Last updated: 2026-11-02

> The sequenced path across the six pillars, with the practice for each step and how you know you are done. What each chapter covers is in the [README](README.md#syllabus). Sources are in [references.md](references.md).

## Prerequisites

| Need | Where |
|---|---|
| Python language basics | [programming/python](../programming/python/README.md), modules 01 to 03 |
| High-school probability | Pillar 02 recaps what it needs |

Pandas is not a prerequisite. Pillar 01 teaches it from the start.

## Path

| Step | Pillar | Practice | Done when you can |
|---|---|---|---|
| 1. Get data into a frame | [01](01-python-for-data-analysis/README.md) | Notebooks `1_Overview` to `4_DataFrames` | load a messy export with one rerunnable function, account for every removed row, and join tables without changing the total |
| 2. Summarise and see it | [01](01-python-for-data-analysis/README.md) | Notebooks `5_Plotting`, `6_Aggregation`, `7_Time_Series` | compute a group rate correctly, resample a daily series with gaps showing, and pick a chart from the question |
| 3. Describe it and reason about chance | [02](02-probability-and-statistics/README.md) | `practice/5_Statistical_Analysis.ipynb`, part 1 | name the distribution behind a count, rate or waiting time, and query it with `scipy.stats` |
| 4. Test a claim and model a relationship | [02](02-probability-and-statistics/README.md) | Notebook part 2; `practice/courses/` Wesleyan scripts | pick the test for two groups, k groups or a table, correct for multiple tests, and read a regression's interval |
| 5. Run an experiment | [03](03-experimentation-and-causality/README.md) | Notebook part 3 in pillar 02; `practice/AB-Bayes/` | size a test, run it, and explain why peeking inflates false positives |
| 6. Know when a correlation lies | [03](03-experimentation-and-causality/README.md) | Notebook part 4 in pillar 02 | spot a confounder or collider, and name the design that fits |
| 7. Explain it to someone | [05](05-visualisation-and-storytelling/README.md) | `practice/` scripts and `dashboard_app.py` | turn a finding into one chart and a recommendation a busy reader can act on |
| 8. Do the whole job | [06](06-applied-analyses/README.md) | Written with the pillar; no chapters yet | take a forecast, cohort, funnel or segmentation from raw data to a recommendation, with a baseline to beat |
| 9. Answer it the Bayesian way | [04](04-bayesian-analysis/README.md) | `practice/BayesianML/` week 4 (read only; legacy environment) | write a PyMC model, check its diagnostics, and re-answer the A/B question with expected loss |

Steps 1 to 6 are the critical path, because data science and data engineering assume them. Step 9 is out of numerical order on purpose. It reuses the vocabulary of steps 3 to 6 and can wait until after your first complete analysis, so read pillar 04 whenever a problem has small samples, useful prior knowledge or asymmetric costs. Bayesian machine learning, the pillar's last chapter, is optional.

## What comes next

| Goal | Next subject |
|---|---|
| Build predictive models and do ML research | [data-science](../data-science/README.md) |
| Build data pipelines and infrastructure | [data-engineering](../data-engineering/README.md) |
| Build LLM-powered applications | [generative-ai](../generative-ai/README.md), starting at 01-llm-fundamentals |
