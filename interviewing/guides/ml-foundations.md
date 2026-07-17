# ML Foundations (+ SQL/Analytics) — Study Guide

The classical round: still opens most MLE/DS loops, and AIE loops sanity-check it. The bar
is fluency on trade-offs and metrics, not derivations.

## 1. Supervised learning core

- **Bias–variance** — underfit vs overfit; regularization (L1 sparsity vs L2 shrinkage),
  early stopping, more data, simpler model. Diagnose with learning curves.
- **Train/val/test discipline** — leakage is the #1 practical sin: fit scalers/encoders on
  train only, split *before* any target-aware transform, time-based splits for temporal
  data. Wrap preprocessing + model in one pipeline so it can't leak.
- **Model menu with reasons**: linear/logistic (baseline, interpretable, calibrated-ish),
  tree ensembles — random forest (robust default) vs gradient boosting/LightGBM/CatBoost
  (tabular SOTA; native categorical handling), SVM (small clean data), kNN (lazy baseline),
  neural nets (unstructured data). Interview move: **always name the naive baseline first**
  (majority class / mean predictor) — improvements only mean something against it.
- **Class imbalance** — resampling, class weights, threshold moving; never report accuracy
  alone on imbalanced data.

## 2. Metrics (choose + defend)

- Classification: precision vs recall (state the business cost asymmetry), F1, ROC-AUC vs
  **PR-AUC (better under heavy imbalance)**, calibration (Brier score, reliability curves —
  probabilities that mean what they say), precision@K for ranking-ish tasks.
- Regression: MAE vs RMSE (outlier sensitivity), MAPE pitfalls near zero, R².
- Clustering: silhouette; stability across seeds.
- The pattern interviewers want: metric ← decision the system drives ("AUROC over accuracy
  because we rank-order for a capacity-limited intervention").

## 3. Deep learning basics (Ng structure)

Backprop intuition; vanishing/exploding gradients (init, norm layers, residuals);
optimization (SGD → momentum → Adam; LR schedules; batch size effects); batch norm (what it
stabilizes — and see `rethinking-batch-norm` in readings for the caveats); dropout;
CNNs (locality/weight sharing) vs RNNs → transformers for sequence (see
[llm-fundamentals](llm-fundamentals.md)). **Structuring ML Projects** (Ng course, notebooks
in repo) is interview gold: orthogonalization, single-number eval metric, human-level
performance as Bayes-error proxy, error analysis by slicing — and its two case-study quizzes
(bird detection, autonomous driving) are literally practice case interviews.

## 4. Unsupervised + embeddings

k-means (and why k is a modeling choice), GMM (soft assignments), hierarchical; PCA vs UMAP
(linear variance vs neighborhood structure — and UMAP is for looking, not for downstream
features without care); embeddings as learned representations — word2vec's
predict-your-neighbors trick generalizes to item2vec/track2vec anywhere co-occurrence
exists.

## 5. ML system hygiene (bridges to MLOps)

Reproducibility (seeds, pinned configs, logged params/metrics); "hidden technical debt in ML
systems" (NIPS 2015 — in readings; name entanglement, feedback loops, pipeline jungles);
train/serve skew; drift (covariate vs concept) with monitoring + retrain triggers;
interpretability toolbox: feature importance vs SHAP/LIME (local additive explanations —
papers in readings), and when interpretability trumps accuracy (healthcare, credit).

## 6. SQL & analytics screen (folded in)

Patterns that recur: GROUP BY + HAVING, multi-table JOINs (know LEFT vs INNER result-count
reasoning), CASE bucketing, date truncation/bucketing, **window functions** (ROW_NUMBER vs
RANK vs DENSE_RANK, LAG/LEAD, running aggregates), CTEs over nested subqueries,
dedup-latest-row idiom (ROW_NUMBER … PARTITION BY … ORDER BY ts DESC = 1). Analytics
judgment: define the metric before writing the query; know one funnel/retention/cohort query
cold. Practice substrate: `data-analytics/` notebooks; DuckDB locally.

## 7. Question bank (answer sketches)

- *"Model does great offline, poorly in prod."* — leakage, train/serve skew, drift,
  survivorship in training data, feedback loops, eval metric ≠ business metric — in that
  checking order.
- *"Explain regularization to a stakeholder."* — penalty on complexity → the model must earn
  every parameter; L1 also does feature selection.
- *"Why gradient boosting over a neural net for tabular?"* — sample efficiency, native
  missing/categorical handling, less tuning, interpretability tooling; NNs win with huge
  data or mixed modalities.
- *"Second-highest salary per department."* — window function idiom; discuss ties → RANK vs
  ROW_NUMBER choice.
- *"How do you pick K in k-means?"* — elbow/silhouette + the honest answer: K encodes the
  product decision (how many segments can ops act on?).

## Sources

- repo: `data-science/Ng's Deep Learning Nbks/` (incl. Structuring ML Projects case-study quizzes), `data-science/Ng's Machine Learning Nbks/`, `data-science/Intro to Machine Learning in Python/`, `data-science/Bayes/`, `data-analytics/` (SQL/pandas-era notebooks)
- readings: `general/` (SHAP, LIME, hidden-technical-debt, batch-norm ×2, KDD metric-interpretation pitfalls), `stats_recs/` (ISLR, Practical Statistics — also seeds the deferred stats guide)
- librarian wiki: LightGBM vs CatBoost Comparison · Track2Vec Playlist Co-Occurrence Embeddings
- global rules: `~/.claude/rules/ml.md` (personal ML practice checklist — pipelines, seeds, baselines)
