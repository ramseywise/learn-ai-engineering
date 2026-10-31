# Data Science — Curriculum

> The order to work through the notes, and what each stage needs first. Contents and run labels are in [README.md](README.md); sources are in [references.md](references.md).

## Prerequisites

- Python and NumPy fluency. Vectorised array code is assumed from note 02 onwards.
- From [data-analytics](../data-analytics/README.md): distributions, hypothesis tests and the idea of a likelihood. Bayesian modelling stays there and is not repeated here.
- Calculus up to the chain rule and matrix products, for 07 and 15–17.

## Path

The path is a tree, not a line. After the core, the three arcs are independent.

```
Core (classical ML)
  01 statistical foundations
   └─ 02 supervised learning
        ├─ 03 features and pipelines ─┐
        │                             ├─ 04 model evaluation ─ 06 ensembles
        └─ 05 unsupervised learning ──┘
              │
   ┌──────────┼─────────────────────────────┐
   ▼          ▼                             ▼
NLP arc      Neural-network arc            From-scratch arc
08 → 09      07 (Ng DL courses)            15 micrograd
 → 10 → 11    │                             → 16 makemore
 → 12 → 13    └──── 14 neural text ◄──────── → 17 nanoGPT
               (needs 07 and 11)
```

| Stage | Notes | Depends on | Notes on order |
|---|---|---|---|
| Core | 01 → 02 → 03, 05 → 04 → 06 | data-analytics | 05 needs only 02. Read 04 before trusting any score in 06 |
| NLP arc | 08 → 09 → 10 → 11 → 12 → 13, then 18 | 02, 03, 04; 05 and 14 for 18 | 10 and 11 can swap. 12 is optional for interviews. 18 (planned) closes the arc: the methods of 05, 09 and 10 rerun on LLM embeddings |
| Neural-network arc | 07 → 14 | 02, 04; 11 for 14 | Learn backprop once in 07 or 15, then use the other as a check |
| From-scratch arc | 15 → 16 → 17 | 02 (logistic regression, softmax) | Strictly sequential. Each part reuses the previous code. 16 part 3 is the most interview-relevant |

When 17 is done, continue to [generative-ai / 01 LLM fundamentals](../generative-ai/01-llm-fundamentals/README.md).

## Known gaps

- There is no hands-on comparison of sklearn gradient boosting, XGBoost and LightGBM with SHAP on a real dataset. Note 06 covers the APIs, but no notebook exercises them.
- Note 18 (LLM embeddings as features) is planned, not written. Notes 05 and 11 cover anomaly detection, clustering and recommenders on classical features; nothing yet repeats them on sentence embeddings.
- There are no notebooks for note 01. It is readings-only (ISLR ch. 2, *Statistics Done Wrong*).
