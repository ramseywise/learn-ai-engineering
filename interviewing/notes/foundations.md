---
origin: synthesized
sources:
  - interviewing/guides/1-foundations/interview-guide.md
  - interviewing/guides/1-foundations/00-overview.md
  - data-analytics/readings/An-Introduction-to-Statistical-Learning-with-Applications-in-Python.pdf
  - data-analytics/readings/Practical_Statistics_for_Data_Scientist.pdf
  - data-analytics/readings/Alex_Reinhart-Statistics_Done_Wrong-EN.pdf
confidence: high
cleaned: 2026-07-21
---
# Foundations — Classical ML & Model Evaluation

Pillar 1. Everything else is built on this: how models learn from data, how you know
they work, and how you choose what to measure. The interview bar is fluency on
trade-offs and metric choice, not derivations.

Core topics: bias-variance tradeoff, overfitting, regularization, cross-validation,
metric interpretation (precision/recall/F1/ROC-AUC), ISLR-to-practice bridge.

---

## Bias–variance tradeoff

**Bias** = systematic error from wrong assumptions (underfitting — model too simple).
**Variance** = sensitivity to noise in the training set (overfitting — model too complex).
They are not independent: reducing one typically increases the other.

Diagnosis tool: **learning curves** — plot training error and validation error against
training set size.

| Pattern | Diagnosis | Fix |
|---|---|---|
| Both curves high and converging | High bias (underfit) | More complexity — features, deeper model, less regularization |
| Large gap between train and val | High variance (overfit) | More data, regularization, simpler model, dropout |
| Both curves low and converging | Good fit | Done |

**Interview move:** always state the diagnosis before proposing the fix. "Learning curves
show high variance — I'd try increasing regularization strength before collecting more data
because data collection is expensive."

---

## Overfitting and regularization

Overfitting = model memorizes training data; fails to generalize. The practical test: val
loss starts increasing while train loss keeps falling.

**Regularization** adds a penalty on model complexity to force the model to *earn* every
parameter.

| Type | Penalty | Effect |
|---|---|---|
| L2 (Ridge) | sum of squared weights | Shrinks all weights toward zero; no sparsity |
| L1 (Lasso) | sum of absolute weights | Drives some weights to exactly zero → feature selection |
| Elastic net | L1 + L2 | Both effects; useful when p > n |
| Dropout (DL) | Randomly zero activations during training | Ensemble-like regularization for nets |
| Early stopping | Halt when val loss rises | Implicit regularization; keeps a checkpoint |

**Stakeholder framing:** "Regularization is a penalty on complexity — the model must justify
every parameter it uses. L1 also doubles as feature selection."

---

## Cross-validation

Purpose: estimate generalization error without touching the test set. The test set is used
**once**, at the very end.

**k-fold CV:** split training data into k folds; train on k−1, validate on the held-out fold,
rotate. Average the k validation scores. Standard: k=5 or k=10.

**Stratified k-fold:** preserve class proportions in each fold. Required for imbalanced
classification.

**Time-series splits:** no shuffling — the validation fold must always be temporally *after*
the training folds. `sklearn.model_selection.TimeSeriesSplit`.

**Data leakage — the #1 practical sin:**
- Fit scalers, encoders, imputers **on the training fold only** — then transform val/test.
- Never do target-aware transforms (target encoding, SMOTE) before the split.
- Wrap all preprocessing in a pipeline so it can't leak:

```python
from sklearn.pipeline import Pipeline
pipe = Pipeline([('scaler', StandardScaler()), ('clf', LogisticRegression())])
cross_val_score(pipe, X, y, cv=StratifiedKFold(5))
```

---

## Metric interpretation — precision, recall, F1, ROC-AUC

Never report a single metric without knowing what decision the system drives.

### Classification metrics

**Accuracy** = (TP + TN) / all. Misleading on imbalanced data (99% class A → 99% accuracy by
always predicting A). Don't use as the primary metric.

**Precision** = TP / (TP + FP) — "of all the things I flagged, how many were actually
positive?" High precision = low false alarm rate. Optimize when false positives are costly
(spam filter, fraud alert that locks accounts).

**Recall (sensitivity)** = TP / (TP + FN) — "of all actual positives, how many did I catch?"
High recall = low miss rate. Optimize when false negatives are costly (cancer screening,
fraud detection in high-value transactions).

**F1** = harmonic mean of precision and recall. Use when you need a single number that
balances both. Harmonic mean punishes extreme imbalances between the two.

**ROC-AUC** = probability that a randomly chosen positive example scores higher than a
randomly chosen negative. Threshold-agnostic. Prefer ROC-AUC for ranking problems.

**PR-AUC** = area under precision-recall curve. Better than ROC-AUC under heavy class
imbalance — ROC-AUC can look good when negatives dominate.

**Calibration** — do the probabilities mean what they say? A model predicting 70% confidence
should be right ~70% of the time. Check with Brier score or reliability (calibration) curves.
Matters when downstream decisions use the raw probability (pricing, risk scoring).

### The pattern interviewers want

> "I'd use PR-AUC rather than accuracy because we have heavy class imbalance, and because the
> system drives a ranking decision — we intervene on the top K cases per day."

Metric ← decision the system drives ← cost of false positives vs false negatives.

### Regression metrics

| Metric | Formula | When to prefer |
|---|---|---|
| MAE | mean of \|residuals\| | Robust to outliers; interpretable in target units |
| RMSE | sqrt(mean of residuals²) | Penalizes large errors; use when big misses are costly |
| MAPE | mean of \|residual/actual\| | Percentage-based; breaks near zero (avoid) |
| R² | 1 − SS_res/SS_tot | Proportion of variance explained; 0 is always-predict-mean |

---

## The ISLR-to-practice bridge

*An Introduction to Statistical Learning* (ISLR) is the theoretical anchor; the pitfall is
reading it in isolation and never closing the loop to practice.

**How to use it:** read each chapter *after* you've touched the technique in code, not before.
ISLR ch2 (statistical learning) → `Intro to ML in Python/02-supervised-learning.ipynb`. ISLR
ch5 (resampling) → `Intro to ML in Python/05-model-evaluation-and-improvement.ipynb`.

**The gap ISLR doesn't fill:** ISLR teaches what models are and why they work; it doesn't
teach production hygiene (pipelines, leakage, train/serve skew, drift). Fill that gap with:
- *Hidden Technical Debt in ML Systems* (NIPS 2015) — `ai-engineering/readings/general/` — the "why ML
  systems rot" paper. Read before pillar 8 (data eng/MLOps).
- Ng's *Structuring ML Projects* (in `Ng's Deep Learning Nbks/`) — orthogonalization,
  single-number eval metrics, human-level performance as Bayes-error proxy, error analysis by
  slicing. The two case-study quizzes (bird detection, autonomous driving) are literal practice
  case interviews.

**Statistics Done Wrong:** read in parallel with any metric interpretation work. Key pitfalls:
p-hacking, multiple comparisons without correction, stopping rules, base rate neglect. The
book is short (~170 pages); read it once, reference it when reviewing A/B test results.

---

## Sources

- Pillar guide: [`1-foundations/interview-guide.md`](../guides/1-foundations/interview-guide.md)
- Depth dir: [`data-science/`](../../data-science/CURRICULUM.md) (Layers 1–3 of the curriculum)
- Readings: `data-analytics/readings/` (ISLR, Practical Statistics, Statistics Done Wrong, Think Bayes)
- Readings: `ai-engineering/readings/general/` (SHAP, LIME, Hidden Technical Debt, KDD Metric Pitfalls)
