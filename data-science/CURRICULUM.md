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

**Staleness note (resolved — #35):** Notebooks were authored against sklearn 0.20 and have been updated for
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

**Staleness note — PyMC migration status (#37):**

CamDavidsonPilon repo ships both `_PyMC3` and `_PyMC_current` variants per chapter — the `_current`
variants use `import pymc as pm` (PyMC 5.x). Simple-tier notebooks already migrated:
- `../data-analytics/Bayes/bayesian_inference_talk-main/Calculate_Posterior_Prob_with_PyMC.ipynb` — uses `import pymc as pm` (done)
- `../data-analytics/Bayes/bayesian_inference_talk-main/German_Tank_Problem.ipynb` — uses `import pymc as pm` (done)
- `../data-analytics/CamDavidsonPilon-.../Chapter1_Introduction/Ch1_Introduction_PyMC3.ipynb` — uses `import pymc as pm` (done despite `_PyMC3` filename)
- `../data-analytics/CamDavidsonPilon-.../Chapter2_MorePyMC/Ch2_MorePyMC_PyMC_current.ipynb` — PyMC5 variant exists (use this)
- `../data-analytics/CamDavidsonPilon-.../Chapter3_MCMC/Ch3_IntroMCMC_PyMC_current.ipynb` — PyMC5 variant exists (use this)
- `../data-analytics/CamDavidsonPilon-.../Chapter4_TheGreatestTheoremNeverTold/Ch4_LawOfLargeNumbers_PyMC_current.ipynb` — PyMC5 variant exists (use this)
- `../data-analytics/CamDavidsonPilon-.../Chapter5_LossFunctions/Ch5_LossFunctions_PyMC_current.ipynb` — uses `import pymc3` still (stale despite name — needs import swap)
- `../data-analytics/CamDavidsonPilon-.../Chapter6_Priorities/Ch6_Priors_PyMC_current.ipynb` — PyMC5 variant exists (verify import)

Still on **PyMC3** (breaking at v4), no `_current` equivalent:
- `../data-analytics/Bayes/BayesianML-master/week_4/Week4. Practical Assignment. MCMC.ipynb` — `import pymc3 as pm`; requires full port or pin `pymc3==3.11.4` + `theano-pymc`

Phase 2 work (medium/hard tiers) requires: `pm.traceplot` → `az.plot_trace`, `pm.summary` → `az.summary`,
and any custom Theano ops → PyTensor equivalents.

---

## Dependency Staleness Audit (#33, #35, #36, #37)

Full audit run 2026-07-22. Bayesian notebooks live in `../data-analytics/` (moved from `data-science/`).

### scikit-learn: 0.20 → 1.4+ (#35) — **Resolved**

| Notebook | Status | Notes |
|---|---|---|
| `Intro to ML in Python/02-supervised-learning.ipynb` | Updated | `LogisticRegression(max_iter=1000)`, `DummyClassifier(strategy="stratified")` |
| `Intro to ML in Python/04-representing-data-feature-engineering.ipynb` | Updated | `OneHotEncoder(sparse_output=False)` |
| `Intro to ML in Python/05-model-evaluation-and-improvement.ipynb` | Updated | No stale module imports; uses `mglearn` helpers |
| `Intro to ML in Python/01,03,06,07,08` | Clean | No stale API patterns |
| `intro-to-nlp/` notebooks | Clean | `sklearn.manifold.TSNE`, `cosine_similarity`, `LogisticRegression`, `SVC` — all stable across 1.x |
| `Ng's Machine Learning Nbks/` | Clean | No sklearn imports |
| `Text Analytics with Python/` | Clean | Uses `sklearn.pipeline.Pipeline` / `make_pipeline` — stable |

No version pinning required. `sklearn.cross_validation` (removed in 0.20) is not present anywhere —
occurrences of `cross_validation` in `Ch06b` are LDA topic words in notebook output, not imports.

**Migration map (for reference):**
- `sklearn.cross_validation` → `sklearn.model_selection` (removed in 0.20, already absent)
- `sklearn.grid_search` → `sklearn.model_selection` (removed in 0.20, already absent)
- `DummyClassifier(strategy="warn")` → `strategy="stratified"` (default changed in 1.1)
- `OneHotEncoder(sparse=True)` → `sparse_output=False` (parameter renamed in 1.2)

### TensorFlow: 1.x → 2.x (#36) — **Phase 1 complete, Phase 2 required for 2 notebooks**

**Decision: `tf.compat.v1` bridge (Phase 1) for most; full Keras rewrite (Phase 2) for tf.contrib notebooks.**

| Notebook | Status | Blocker |
|---|---|---|
| `Ng's Deep Learning Nbks/.../Tensorflow Tutorial.ipynb` | Phase 1 done (`tf.compat.v1` + `disable_v2_behavior`) | `tf.contrib.layers.xavier_initializer` — **Phase 2 required** |
| `Ng's Deep Learning Nbks/CNN/Week1/Convolution model - Application.ipynb` | Phase 1 done | `tf.contrib.layers.flatten`, `tf.contrib.layers.fully_connected`, `tf.contrib.layers.xavier_initializer` — **Phase 2 required** |
| `Ng's Deep Learning Nbks/CNN/Week2/ResNets/Residual Networks.ipynb` | Phase 1 done | `tf.Session` / `tf.placeholder` via compat.v1 — runs on TF 2.x |
| `Ng's Deep Learning Nbks/CNN/Week3/Car detection.../Autonomous driving application.ipynb` | Phase 1 done | No tf.contrib — runs on TF 2.x via compat.v1 |
| `Ng's Deep Learning Nbks/CNN/Week4/Face Recognition for the Happy House.ipynb` | Phase 1 done | No tf.contrib — runs on TF 2.x via compat.v1 |
| `Ng's Deep Learning Nbks/CNN/Week4/Art Generation with Neural Style Transfer.ipynb` | Phase 1 done | No tf.contrib — runs on TF 2.x via compat.v1 |
| `intro-to-nlp/tensorFlow/` (all 10 notebooks) | TF 2.x native | Use `tensorflow` / `tensorflow.keras` directly — no compat.v1 needed |
| `Text Analytics with Python/Ch10a` | Stale | `with tf.Session() as session` — no compat shim; needs `tf.compat.v1.Session` or Keras rewrite |

**Phase 2 migration map for tf.contrib (Tensorflow Tutorial + Convolution model):**
- `tf.contrib.layers.xavier_initializer(seed=N)` → `tf.keras.initializers.glorot_uniform(seed=N)`
- `tf.contrib.layers.flatten(P)` → `tf.keras.layers.Flatten()(P)` or `tf.reshape(P, [tf.shape(P)[0], -1])`
- `tf.contrib.layers.fully_connected(F, n, activation_fn=None)` → `tf.keras.layers.Dense(n, activation=None)(F)`
- `tf.get_variable(name, shape, initializer=...)` → `tf.Variable(initializer(shape=shape))`
- `tf.placeholder(dtype, shape)` → function argument / `tf.keras.Input`
- `with tf.Session() as sess: sess.run(op)` → `op.numpy()` or direct eager execution

### PyMC3 → PyMC 5 (#37) — **Partial; data-analytics/ not data-science/**

Note: all Bayesian notebooks are in `../data-analytics/`, not `data-science/`. CURRICULUM.md Layer 6
cross-references them correctly.

| Notebook | Status | Action |
|---|---|---|
| `data-analytics/Bayes/bayesian_inference_talk-main/Calculate_Posterior_Prob_with_PyMC.ipynb` | Done — `import pymc as pm` | — |
| `data-analytics/Bayes/bayesian_inference_talk-main/German_Tank_Problem.ipynb` | Done — `import pymc as pm` | — |
| `data-analytics/CamDavidsonPilon-.../Ch1_Introduction_PyMC3.ipynb` | Done — uses `import pymc as pm` despite filename | — |
| `data-analytics/CamDavidsonPilon-.../Ch2_MorePyMC_PyMC_current.ipynb` | Available — use this variant | Verify no `pymc3` remnants |
| `data-analytics/CamDavidsonPilon-.../Ch3_IntroMCMC_PyMC_current.ipynb` | Available — use this variant | Verify |
| `data-analytics/CamDavidsonPilon-.../Ch4_LawOfLargeNumbers_PyMC_current.ipynb` | Available — use this variant | Verify |
| `data-analytics/CamDavidsonPilon-.../Ch5_LossFunctions_PyMC_current.ipynb` | Stale — still `import pymc3 as pm` | Swap: `import pymc3` → `import pymc`; `pm.traceplot` → `az.plot_trace` |
| `data-analytics/CamDavidsonPilon-.../Ch6_Priors_PyMC_current.ipynb` | Likely done | Verify import |
| `data-analytics/CamDavidsonPilon-.../Chapter2–6 _PyMC3 variants` | Legacy — do not use | Pin `pymc3==3.11.4` + `theano-pymc` if must run |
| `data-analytics/Bayes/BayesianML-master/week_4/Week4. Practical Assignment. MCMC.ipynb` | Stale — `import pymc3 as pm` | Port or pin; no `_current` variant exists |
| `data-analytics/CamDavidsonPilon-.../sandbox/`, `Chapter7_BayesianMachineLearning/` | Stale — various pymc imports | Low priority; not in curriculum path |

**PyMC3 → PyMC 5 migration map:**
- `import pymc3 as pm` → `import pymc as pm`
- `pm.traceplot(trace)` → `import arviz as az; az.plot_trace(trace)`
- `pm.summary(trace)` → `az.summary(trace)`
- `pm.plot_posterior(trace)` → `az.plot_posterior(trace)`
- `pm.sample(draws, tune=N)` — signature largely unchanged; `return_inferencedata=True` is now default in PyMC 5
- Theano custom ops → PyTensor equivalents (advanced; only in BayesianML week_4)

---

## Interview crosswalk

- **Pillar 1 — Foundations:** [interviewing/guides/1-foundations/](../interviewing/guides/1-foundations/00-overview.md)
  (covers Layers 1–5 content: bias-variance, metrics, supervised learning, unsupervised, ensembles)
- **Cleaned notes:** `interviewing/notes/foundations.md` (Pillar 1 summary — bias-variance, metrics, CV)
- **Readings cross-cut:** `../data-analytics/readings/` maps to Layers 1–3
