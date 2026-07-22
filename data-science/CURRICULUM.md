# Data Science — Curriculum

> **Structure:** tree-shaped, not linear. Layers 2 and 4 are independent branches — you can do
> unsupervised learning without touching model evaluation. Layer 3 depends on Layer 2 only.
> Layer 1 (statistical foundations) is readings-only — it grounds the vocabulary but has no
> hands-on notebooks here; code comes in Layer 2.

```
Layer 1: Statistical Foundations  (readings-only)
    │
    ├── Layer 2: Supervised Learning ──── Layer 3: Model Evaluation
    │                                          (depends on Layer 2)
    │
    └── Layer 4: Unsupervised Learning  (independent of Layer 3)
         │
         └── Layer 5: Ensemble Methods
                  │
                  └── Layer 6: Bayesian Methods
```

---

## Layer 1 — Statistical Foundations

**What:** Vocabulary and statistical intuition before touching code. Bias-variance,
probability, distributions, inference, and Bayesian thinking as a second lens on
everything that follows.

**Source material (readings-only):**

| Resource | Location | Focus |
|---|---|---|
| An Introduction to Statistical Learning (ISLR, Python ed.) | `../data-analytics/readings/An-Introduction-to-Statistical-Learning-with-Applications-in-Python.pdf` | canonical ML theory text; read chapters alongside Layer 2 code |
| Practical Statistics for Data Scientists | `../data-analytics/readings/Practical_Statistics_for_Data_Scientist.pdf` | working-stats reference; chapter-level |
| Statistics Done Wrong (Reinhart) | `../data-analytics/readings/Alex_Reinhart-Statistics_Done_Wrong-EN.pdf` | inference pitfalls — read before any metric interpretation |
| Think Bayes | `../data-analytics/readings/think_bayes.pdf` | gateway to Layer 6 |
| Statistical Rethinking (McElreath) | `../data-analytics/readings/RM-StatRethink-Bayes.pdf` | deep Bayesian intuition |
| Computer Age Statistical Inference | `../data-analytics/readings/computer age statistical inference.pdf` | frequentist-to-Bayes bridge |

**No hands-on here.** This is the grounding layer — return to these after each later layer
solidifies a technique.

---

## Layer 2 — Supervised Learning

**What:** Hands-on classical ML. Fit models, break them, diagnose with learning curves.
Linear/logistic regression, classification, SVMs, neural net basics. Independent of Layer 4.

**Source material:**

| Resource | Location | Covers |
|---|---|---|
| Intro to ML in Python — ch01, ch02 | `data-science/Intro to Machine Learning in Python/01-introduction.ipynb`, `02-supervised-learning.ipynb` | supervised learning foundations, scikit-learn API |
| Ng ML Notebooks — ex1, ex2, ex3 | `data-science/Ng's Machine Learning Nbks/ex1/`, `ex2/`, `ex3/` | linear regression, logistic regression, multi-class classification |
| ISLR ch2-4 | `../data-analytics/readings/` | linear methods theory |

**Staleness note:** Notebooks were authored against sklearn 0.20 and have been updated for
sklearn 1.4+ compatibility (notebooks 02, 04, 05). The API is largely compatible; changes
were: `LogisticRegression(max_iter=1000)`, `DummyClassifier(strategy="stratified")`,
`OneHotEncoder(sparse_output=False)`. No version pinning required for these notebooks.

**Prerequisite:** Layer 1 vocabulary (bias-variance, distributions). No prior code requirement
beyond Python basics.

---

## Layer 3 — Model Evaluation

**What:** How you know whether your model works. Cross-validation, metric selection
(precision/recall/F1/ROC-AUC), learning curves, bias-variance diagnosis, train/val/test
discipline. **Depends on Layer 2** (assumes you've fit at least one supervised model).

**Source material:**

| Resource | Location | Covers |
|---|---|---|
| Intro to ML in Python — ch05 | `data-science/Intro to Machine Learning in Python/05-model-evaluation-and-improvement.ipynb` | cross-validation, grid search, metrics |
| Ng ML Notebooks — ex5 | `data-science/Ng's Machine Learning Nbks/ex5/` | bias-variance diagnosis, learning curves |
| ISLR ch5 | `../data-analytics/readings/` | resampling methods |

**Interview crosswalk:** Layer 3 is the core of pillar [1-foundations](../interviewing/guides/1-foundations/interview-guide.md) —
metric interpretation, train/test discipline, and leakage are the most common interview
failure modes.

---

## Layer 4 — Unsupervised Learning

**What:** Clustering, dimensionality reduction, embeddings. Independent of Layer 3 — you
can tackle this directly after Layer 2 without completing evaluation.

**Source material:**

| Resource | Location | Covers |
|---|---|---|
| Intro to ML in Python — ch03 | `data-science/Intro to Machine Learning in Python/03-unsupervised-learning.ipynb` | k-means, DBSCAN, PCA, NMF, manifold learning |
| Ng ML Notebooks — ex7, ex8 | `data-science/Ng's Machine Learning Nbks/ex7/`, `ex8/` | k-means + PCA, anomaly detection, recommender systems |
| ISLR ch10, ch12 | `../data-analytics/readings/` | PCA, clustering theory |

---

## Layer 5 — Ensemble Methods

**What:** Random forests, gradient boosting, stacking. How combining weak learners beats
any single model on tabular data.

**Source material:**

| Resource | Location | Covers |
|---|---|---|
| Intro to ML in Python — ch02 (trees + ensembles section) | `data-science/Intro to Machine Learning in Python/02-supervised-learning.ipynb` | decision trees, random forests, gradient boosting |
| ISLR ch8 | `../data-analytics/readings/` | tree methods theory |

**Gap — no XGBoost/LightGBM hands-on.** The notebooks use scikit-learn's GradientBoostingClassifier
(sklearn 0.20); LightGBM and XGBoost — the actual tabular SOTA — have no dedicated notebooks
here. This is a staleness/coverage gap, not just a version issue. To fill: add a standalone
notebook comparing sklearn GB vs XGBoost vs LightGBM on a real dataset with SHAP explanations.

---

## Layer 6 — Bayesian Methods

**What:** Probabilistic programming, MCMC, Bayesian inference in practice. Builds on Layer 1
(statistical foundations) and Layer 2 (model intuition).

**Source material:**

| Resource | Location | Covers |
|---|---|---|
| Bayes/AB-Bayes | `../data-analytics/Bayes/AB-Bayes/` | Bayesian A/B testing — executed notebook |
| Bayes/bayesian_inference_talk-main | `../data-analytics/Bayes/bayesian_inference_talk-main/` | slides + 3 executed notebooks from a real talk |
| Bayes/BayesianML-master | `../data-analytics/Bayes/BayesianML-master/` | Coursera "Bayesian Methods for ML" — weeks 2/4/5/6 + final |
| Bayesian Methods for Hackers (vendored) | `../data-analytics/CamDavidsonPilon-Probabilistic-Programming-and-Bayesian-Methods-for-Hackers-5b33f77/` | chapters 1–7 with PyMC3 code |
| Bayesian Methods for Hackers (PDF) | `../data-analytics/readings/bayes_for_hackers.pdf` | reference copy |

**Staleness note (partial migration — 2026-07-22):** Simple-tier notebooks migrated to PyMC 5.x:
- `../data-analytics/Bayes/bayesian_inference_talk-main/Calculate_Posterior_Prob_with_PyMC.ipynb` — import swap + `az.plot_trace`
- `../data-analytics/Bayes/bayesian_inference_talk-main/German_Tank_Problem.ipynb` — import swap
- `../data-analytics/CamDavidsonPilon-.../Chapter1_Introduction/Ch1_Introduction_PyMC3.ipynb` — import swap

Remaining notebooks still use **PyMC3** (breaking at v4). Do not run without pinning `pymc3==3.11.4`
with its `theano-pymc` dependency, or completing Phase 2 porting (medium/hard tiers: `../data-analytics/Bayes/BayesianML-master/week_4/`,
CamDavidsonPilon chapters 2–6 in `../data-analytics/CamDavidsonPilon-.../`). Phase 2 notebooks
require custom Theano→PyTensor op rewrites and `pm.traceplot`/`pm.summary` API updates.

---

## Dependency Pinning Summary

| Library | Notebooks authored against | Current | Risk |
|---|---|---|---|
| scikit-learn | 0.20 → updated to 1.4+ | 1.4+ | Low — notebooks 02/04/05 updated; no pinning needed |
| PyMC3 | 3.x | 5.x (breaking at 4.0) | Partial — 3 simple-tier notebooks ported (2026-07-22); remaining must pin or port |
| TensorFlow | 1.x (Ng DL notebooks) | 2.x (breaking) | Phase 1 complete — 5 notebooks updated to `tf.compat.v1` + `disable_v2_behavior`. 2 notebooks (`Tensorflow Tutorial`, `Convolution model - Application`) still use `tf.contrib` (removed in TF2, not restored by compat.v1) — Phase 2 rewrite required for those. |

---

## Interview crosswalk

- **Pillar 1 — Foundations:** [interviewing/guides/1-foundations/](../interviewing/guides/1-foundations/00-overview.md)
  (covers Layers 1–5 content: bias-variance, metrics, supervised learning, unsupervised, ensembles)
- **Cleaned notes:** `interviewing/notes/foundations.md` (Pillar 1 summary — bias-variance, metrics, CV)
- **Readings cross-cut:** `../data-analytics/readings/` maps to Layers 1–3
