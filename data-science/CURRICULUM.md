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
| An Introduction to Statistical Learning (ISLR, Python ed.) | `readings/0-cross-stats/An-Introduction-to-Statistical-Learning-with-Applications-in-Python.pdf` | canonical ML theory text; read chapters alongside Layer 2 code |
| Practical Statistics for Data Scientists | `readings/0-cross-stats/Practical_Statistics_for_Data_Scientist.pdf` | working-stats reference; chapter-level |
| Statistics Done Wrong (Reinhart) | `readings/0-cross-stats/Alex_Reinhart-Statistics_Done_Wrong-EN.pdf` | inference pitfalls — read before any metric interpretation |
| Think Bayes | `readings/0-cross-stats/think_bayes.pdf` | gateway to Layer 6 |
| Statistical Rethinking (McElreath) | `readings/0-cross-stats/RM-StatRethink-Bayes.pdf` | deep Bayesian intuition |
| Computer Age Statistical Inference | `readings/0-cross-stats/computer age statistical inference.pdf` | frequentist-to-Bayes bridge |

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
| ISLR ch2-4 | `readings/0-cross-stats/` | linear methods theory |

**Staleness note:** Notebooks were authored against sklearn 0.20 (current: 1.4+). The API
is largely compatible but some pipeline and preprocessing patterns have changed. Pin
`scikit-learn==0.20` if running as-is, or update imports to sklearn 1.x conventions.

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
| ISLR ch5 | `readings/0-cross-stats/` | resampling methods |

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
| ISLR ch10, ch12 | `readings/0-cross-stats/` | PCA, clustering theory |

---

## Layer 5 — Ensemble Methods

**What:** Random forests, gradient boosting, stacking. How combining weak learners beats
any single model on tabular data.

**Source material:**

| Resource | Location | Covers |
|---|---|---|
| Intro to ML in Python — ch02 (trees + ensembles section) | `data-science/Intro to Machine Learning in Python/02-supervised-learning.ipynb` | decision trees, random forests, gradient boosting |
| ISLR ch8 | `readings/0-cross-stats/` | tree methods theory |

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
| Bayes/AB-Bayes | `data-science/Bayes/AB-Bayes/` | Bayesian A/B testing — executed notebook |
| Bayes/bayesian_inference_talk-main | `data-science/Bayes/bayesian_inference_talk-main/` | slides + 3 executed notebooks from a real talk |
| Bayes/BayesianML-master | `data-science/Bayes/BayesianML-master/` | Coursera "Bayesian Methods for ML" — weeks 2/4/5/6 + final |
| Bayesian Methods for Hackers (vendored) | `data-science/CamDavidsonPilon-Probabilistic-Programming-and-Bayesian-Methods-for-Hackers-5b33f77/` | chapters 1–7 with PyMC3 code |
| Bayesian Methods for Hackers (PDF) | `readings/0-cross-stats/bayes_for_hackers.pdf` | reference copy |

**Staleness note:** All Bayes notebooks use **PyMC3** (current: PyMC 5.x — breaking API change
at v4). Do not run without either pinning `pymc3==3.11.4` with its `theano-pymc` dependency or
porting to PyMC 5 syntax (`pm.Data`, `pm.draw`, autodiff backend changed from Theano to PyTensor).

---

## Dependency Pinning Summary

| Library | Notebooks authored against | Current | Risk |
|---|---|---|---|
| scikit-learn | 0.20 | 1.4+ | Medium — mostly API-compatible; some pipeline changes |
| PyMC3 | 3.x | 5.x (breaking at 4.0) | High — must pin or port |
| TensorFlow | 1.x (Ng DL notebooks) | 2.x (breaking) | High — must pin `tensorflow==1.x` or use compat mode |

---

## Interview crosswalk

- **Pillar 1 — Foundations:** [interviewing/guides/1-foundations/](../interviewing/guides/1-foundations/00-overview.md)
  (covers Layers 1–5 content: bias-variance, metrics, supervised learning, unsupervised, ensembles)
- **Cleaned notes:** `interviewing/notes/foundations.md` (Pillar 1 summary — bias-variance, metrics, CV)
- **Readings cross-cut:** `readings/0-cross-stats/` maps to Layers 1–3; `readings/general/` has SHAP/LIME
  papers and Hidden Technical Debt (bridge from Layer 3 to MLOps)
