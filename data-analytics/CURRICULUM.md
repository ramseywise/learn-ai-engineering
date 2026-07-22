# Data Analytics — Curriculum

Last updated: 2026-07-22

## Purpose

Data analytics is the foundation layer before specialization. Everything here is Python-first,
dataset-level work. After completing these layers, you branch into data engineering, data science,
or generative AI — this curriculum ends with that branching decision.

## The 6 Layers

| # | Layer | What you learn | Notebooks / Material | Status |
|---|---|---|---|---|
| 1 | **Python fundamentals** | Language basics: types, control flow, functions, standard library | `../programming/Python Basics/1_Overview.ipynb`, `2_Texts.ipynb` | Present |
| 2 | **Data wrangling** | NumPy arrays, pandas DataFrames, indexing, merging, cleaning | `../programming/Python Basics/3_Arrays.ipynb`, `4_DataFrames.ipynb` | Present |
| 3 | **EDA + visualization** | Exploratory data analysis; matplotlib/seaborn plotting; aggregation; time series | `../programming/Python Basics/5_Plotting.ipynb`, `6_Aggregation.ipynb`, `7_Time_Series.ipynb` | Present |
| 4 | **Feature engineering** | Text feature representation; NLP preprocessing; TF-IDF, embeddings, classification features | `Text Analytics with Python/Ch03`, `Ch04`, `Ch05` | Present |
| 5 | **Statistical analysis** | Hypothesis testing; distributions; A/B testing; correlation vs. causation | `5_Statistical_Analysis.ipynb` | Present (partial — see Layer 5 section) |
| 6 | **Modeling + BI** | Semantic analysis; topic modeling; similarity; clustering; deep learning intro | `Text Analytics with Python/Ch06`, `Ch07`, `Ch08`, `Ch09`, `Ch10` | Present |

## Notebook Map

### `../programming/Python Basics/` (self-authored, 7 notebooks)

Sequential — each builds on the previous.

| Notebook | Layer |
|---|---|
| `1_Overview.ipynb` | 1 — Python fundamentals |
| `2_Texts.ipynb` | 1 — Python fundamentals (strings, file I/O) |
| `3_Arrays.ipynb` | 2 — Data wrangling (NumPy) |
| `4_DataFrames.ipynb` | 2 — Data wrangling (pandas) |
| `5_Plotting.ipynb` | 3 — EDA + visualization |
| `6_Aggregation.ipynb` | 3 — EDA (groupby, aggregation) |
| `7_Time_Series.ipynb` | 3 — EDA (time-indexed data) |

### `Text Analytics with Python/` (companion to Dipanjan Sarkar's book, Chapters 01–10)

| Chapter | Topic | Layer |
|---|---|---|
| Ch01 — NLP Basics | Foundations of NLP | 1 — Python fundamentals |
| Ch02 — Python for NLP | Python text tools | 1 — Python fundamentals |
| Ch03 — Processing and Understanding Text | Tokenization, normalization | 4 — Feature engineering |
| Ch04 — Feature Engineering for Text | TF-IDF, n-grams, embeddings | 4 — Feature engineering |
| Ch05 — Text Classification | Supervised classification pipeline | 4 — Feature engineering |
| Ch06 — Text Summarization + Topic Models | LDA, summarization | 6 — Modeling + BI |
| Ch07 — Text Similarity + Clustering | Cosine similarity, K-means | 6 — Modeling + BI |
| Ch08 — Semantic Analysis | Word vectors, semantic similarity | 6 — Modeling + BI |
| Ch09 — Sentiment Analysis | Lexicon and ML-based sentiment | 6 — Modeling + BI |
| Ch10 — Deep Learning | Neural text models | 6 — Modeling + BI |

**Note:** Some spaCy syntax in the Text Analytics notebooks is deprecated (spaCy 2.x → 3.x
breaking changes). The conceptual content is sound; the API calls may need updating before running.

## Layer 5 — Statistical Analysis Assessment

`5_Statistical_Analysis.ipynb` was added (2026-07-22) and covers the core curriculum. The gap
is partially closed — see below for what's present vs what remains.

### What the notebook covers

| Part | Topics | Status |
|---|---|---|
| Part 1: Probability Distributions | Normal, binomial, Poisson; PDF/CDF; sampling; Central Limit Theorem | Present — executed |
| Part 2: Hypothesis Testing | t-tests, chi-square, ANOVA, multiple comparisons (Bonferroni) | Present — executed |
| Part 3: A/B Testing | Sample-size/power calculation, peeking pitfalls, practical framework | Present — executed |
| Part 4: Correlation and Causation | Pearson vs Spearman, Simpson's paradox, confounding variables | Present — executed |

### Remaining gaps

These topics are **not** covered in the notebook and have no existing material in this repo:

| Gap | Priority | Recommendation |
|---|---|---|
| Bayesian A/B testing | High | `../data-analytics/Bayes/AB-Bayes/AB_Testing_with_Python.ipynb` partially fills this — add a cross-reference or integration section |
| Causal inference (DiD, IV, RD) | Medium | No existing notebook; add a Part 5 using `dowhy` or manual DiD examples |
| Non-parametric tests (Mann-Whitney, Kolmogorov-Smirnov) | Low | One-off add to Part 2 |
| Time-series testing (stationarity, autocorrelation) | Low | Covered better in `../programming/Python Basics/7_Time_Series.ipynb`; cross-reference sufficient |

### Readings that support this layer

All in `readings/`:

| Book | Focus |
|---|---|
| *Practical Statistics for Data Scientists* | Working-stats reference; pairs directly with Parts 1–3 |
| *Statistics Done Wrong* (Reinhart) | Inference pitfalls; pairs with Part 2–3 (multiple comparisons, peeking) |
| *An Introduction to Statistical Learning* (ISLR) | Theory for Parts 1–2; read after the notebook |
| *Think Stats* / *Think Bayes* | Alternative probabilistic lens; bridge to `Bayes/` notebooks |

### Criticality assessment

**Critical for the learning path:** statistical analysis (Layer 5) is a prerequisite for:
- Interpreting model evaluation metrics correctly (data-science Layer 3)
- A/B testing in data engineering monitoring (data-engineering Foundation 5)
- The deferred "Stats & Experimentation" interviewing pillar

The notebook fills the critical path items (distributions, hypothesis testing, A/B testing).
The remaining gaps (causal inference, Bayesian A/B) are nice-to-have for this layer — the Bayes
notebooks in `Bayes/` cover the Bayesian track separately at higher depth.

## Reference Links

- **Python reference**: [`readings/Python for Data Analysis.pdf`](readings/Python%20for%20Data%20Analysis.pdf) (Wes McKinney, O'Reilly)
- **Quick reference**: [`SimpleHacks.md`](SimpleHacks.md)
- **Stats readings**: [`readings/`](readings/)

## What Comes Next — The Branching Decision

After completing data analytics foundations (Layers 1–4), pick one path based on your goal:

| Goal | Next subject |
|---|---|
| Build data pipelines and infrastructure | **Data Engineering** → `../data-engineering/CURRICULUM.md` |
| Build predictive models and do ML research | **Data Science** → `../data-science/CURRICULUM.md` |
| Build LLM-powered applications | **Generative AI** → `../generative-ai/` (01-llm-fundamentals first) |

All three paths require the same Python + data wrangling foundation (Layers 1–3).
Feature engineering (Layer 4) is most directly useful for data science and generative AI.
