# Pillar 1 — Foundations (classical ML, stats, SQL)

Everything else in AI is built on this: how models learn from data, how you know they
work, and how you query the data in the first place. If you're starting from zero, this
pillar is where terms like "overfitting", "precision/recall", and "train/test split" stop
being jargon and become tools you reach for.

## Learning path

1. **Python + data handling first** — work through `programming/Python Basics/` and
   *Python for Data Analysis* (readings) until pandas feels boring.
2. **Core ML by doing** — `data-science/Intro to Machine Learning in Python/` notebooks:
   fit your first models, break them, plot learning curves.
3. **Theory to anchor it** — *An Introduction to Statistical Learning* (ISLR, readings):
   read each chapter *after* you've touched the technique in code, not before.
4. **Ng's courses for the discipline** — `data-science/Ng's Machine Learning Nbks/` and
   the Structuring ML Projects material in `Ng's Deep Learning Nbks/` (error analysis,
   single-number metrics — the habits that survive into every later pillar).
5. **Stats honesty** — *Statistics Done Wrong* + *Practical Statistics for Data
   Scientists* (readings): what p-values and metrics actually claim.
6. **Bayes as a second lens** — `data-analytics/Bayes/` + *Bayesian Methods for Hackers*
   (code copy in `data-analytics/`, PDF in readings).

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| Python Basics · Text Analytics | code | `data-analytics/` | pandas/SQL-era analytics, NLP basics |
| Intro to ML in Python | code | `data-science/Intro to Machine Learning in Python/` | hands-on scikit-learn fundamentals |
| Ng ML + DL notebooks | code | `data-science/Ng's Machine Learning Nbks/`, `Ng's Deep Learning Nbks/` | course discipline; Structuring ML Projects = case-study practice |
| ISLR (Python ed.) | pdf | `data-analytics/readings/` | the standard ML theory text |
| Practical Statistics for Data Scientists | pdf | `data-analytics/readings/` | working-stats reference |
| Statistics Done Wrong (Reinhart) | pdf | `data-analytics/readings/` | inference pitfalls |
| Think Stats · Think Bayes · Statistical Rethinking · Computer Age Statistical Inference | pdf | `data-analytics/readings/` | deeper/alternative stats tracks |
| Python for Data Analysis (McKinney) | pdf | `data-analytics/readings/` | pandas from its author |
| Storytelling with Data (Knaflic) | pdf | `data-analytics/readings/` | communicating results (feeds pillar 10) |
| SHAP (1705.07874) · LIME (1602.04938) | pdf | `data-science/` | model explanation methods |
| Hidden Technical Debt in ML (NIPS 2015) | pdf | `data-science/` | why ML systems rot — read before pillar 8 |
| KDD Metric Interpretation Pitfalls | pdf | `data-science/` | metric misreads in practice |
| LightGBM vs CatBoost · Track2Vec | wiki | librarian | applied tabular + embedding case studies |

## Test yourself
[interview-guide.md](interview-guide.md) (the exam-prep summary) · rounds:
[technical-questions](../../rounds/technical-questions/README.md),
[coding-challenge](../../rounds/coding-challenge/README.md) (SQL screens),
[case-study](../../rounds/case-study/README.md) (ML cases).

*Detailed notes (`01-…`) land here pillar-by-pillar; stats/experimentation will grow into
its own pillar from `data-analytics/readings/`.*
