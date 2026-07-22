# Data Analytics — Curriculum

Last updated: 2026-07-21

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
| 5 | **Statistical analysis** | Hypothesis testing; distributions; A/B testing; correlation vs. causation | — | **MISSING** |
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

## Layer 5 Gap — Statistical Analysis

Layer 5 (statistical analysis) is the critical missing piece. No notebooks cover:
- Hypothesis testing (t-tests, chi-square, ANOVA)
- Distributions and probability
- A/B testing and experimental design
- Correlation vs. causation

Until this gap is filled, students should supplement with the readings in
`0-cross-stats/` (*Practical Statistics for Data Scientists*, *Statistics Done Wrong*).

## Reference Links

- **Python reference**: [`readings/Python for Data Analysis.pdf`](readings/Python%20for%20Data%20Analysis.pdf) (Wes McKinney, O'Reilly)
- **Quick reference**: [`SimpleHacks.md`](SimpleHacks.md)
- **Stats readings**: [`0-cross-stats/`](0-cross-stats/)

## What Comes Next — The Branching Decision

After completing data analytics foundations (Layers 1–4), pick one path based on your goal:

| Goal | Next subject |
|---|---|
| Build data pipelines and infrastructure | **Data Engineering** → `../data-engineering/CURRICULUM.md` |
| Build predictive models and do ML research | **Data Science** → `../data-science/CURRICULUM.md` |
| Build LLM-powered applications | **Generative AI** → `../generative-ai/` (01-llm-fundamentals first) |

All three paths require the same Python + data wrangling foundation (Layers 1–3).
Feature engineering (Layer 4) is most directly useful for data science and generative AI.
