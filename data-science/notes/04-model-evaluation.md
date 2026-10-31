---
origin: vendored snapshot: Intro to Machine Learning in Python (kept as practice) + own coursework (Ng ML ex5)
sources:
  - https://github.com/amueller/introduction_to_ml_with_python
  - ../practice/Intro to Machine Learning in Python/05-model-evaluation-and-improvement.ipynb
  - ../Ng's Machine Learning Nbks/ex5/ex5.ipynb
  - ../sources/mueller-guido-introduction-to-ml-with-python.pdf
confidence: high
cleaned: 2026-10-31
---
# 4 — Model Evaluation

> Cross-validation instead of one split, grid search with a held-out test set (or nested CV), a metric chosen from the business consequence of each error type, thresholds read off precision–recall and ROC curves, and learning curves to decide whether you need more data or a different model.

This is the layer interviews probe hardest: metric interpretation, train/test discipline and leakage are the most common failure modes. See the interviewing guide linked from the [README](../README.md).

---

## Cross-validation

A single `train_test_split` gives a score that depends on which points landed in the test set. **k-fold cross-validation** splits the data into $k$ folds, trains $k$ models each holding out one fold, and reports $k$ scores.

```python
from sklearn.model_selection import cross_val_score, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris

iris = load_iris()
logreg = LogisticRegression(max_iter=1000)
scores = cross_val_score(logreg, iris.data, iris.target, cv=5)
print(scores, scores.mean())          # [0.967 1.    0.933 0.967 1.   ] 0.973

res = cross_validate(logreg, iris.data, iris.target, cv=5, return_train_score=True)
```

What CV buys:

- Every point is in a test fold exactly once, so the estimate doesn't depend on a lucky split.
- The **spread** of fold scores says how sensitive the model is to the training data. A range of 0.90–1.00 means "about 95%, give or take."
- More data is used for training: 80% per model at `cv=5` vs 75% for the default split.

What it doesn't do: return a model. `cross_val_score` evaluates a *procedure*; refit on all the data for the final model.

### Splitters

| Splitter | When | Note |
|---|---|---|
| `KFold(n_splits, shuffle=True)` | Regression; data in random order | Without `shuffle`, ordered data (iris is sorted by class) gives 0% folds |
| `StratifiedKFold` | Classification (the default for classifiers) | Keeps class proportions in each fold |
| `LeaveOneOut` | Very small data | $n$ fits; high-variance estimate |
| `ShuffleSplit`, `StratifiedShuffleSplit` | Control train/test sizes and repeats independently; subsample large data | |
| `GroupKFold` | Several rows per subject (patient, user, speaker) | The same group is never in train and test; otherwise you measure memorisation of the person |
| `TimeSeriesSplit` | Temporal data | Always train on the past, test on the future |
| `RepeatedStratifiedKFold` | Small data; want a tighter estimate | |

**The groups rule generalises:** the split must mirror how the model meets new data in production. New users → split by user. Next month → split by time.

---

## Grid search

Hyperparameters (`C`, `gamma`, `max_depth`) are not learned by `fit`. Search them, but the score you used to pick them is no longer an honest estimate.

![Overview of the parameter selection and model evaluation process with GridSearchCV](../sources/images/mueller-guido-gridsearch-overview.png)
*Image source: Müller & Guido, Introduction to Machine Learning with Python, companion repo `images/`*

The three-way split from [01](01-statistical-foundations.md): pick parameters on validation, report on test once.

```python
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.svm import SVC

X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, random_state=0)
param_grid = {"C": [0.001, 0.01, 0.1, 1, 10, 100],
              "gamma": [0.001, 0.01, 0.1, 1, 10, 100]}
grid = GridSearchCV(SVC(), param_grid, cv=5, return_train_score=True)
grid.fit(X_train, y_train)               # CV on train only; then refits best on all of train

print(grid.best_params_)                 # {'C': 10, 'gamma': 0.1}
print(grid.best_score_)                  # 0.97  mean CV score: optimistic, used for selection
print(grid.score(X_test, y_test))        # 0.97  the honest number
```

### Reading the results

`pd.DataFrame(grid.cv_results_)` has one row per parameter combination. Pivot the mean test score into a $C \times \gamma$ heatmap:

| Heatmap shows | Meaning | Action |
|---|---|---|
| Best values in the interior | Range is right | Refine around the best |
| Best values on an edge | The optimum may be outside | Extend the range |
| Flat, no change | Parameter doesn't matter, or the scale is wrong | Change scale (log), or drop it |

Search parameters on a **log scale** (0.001, 0.01, …). A list of dicts lets you search conditional spaces, e.g. `gamma` only for `kernel="rbf"`.

```python
param_grid = [{"kernel": ["rbf"], "C": [0.01, 0.1, 1, 10, 100], "gamma": [0.01, 0.1, 1, 10]},
              {"kernel": ["linear"], "C": [0.01, 0.1, 1, 10, 100]}]
```

`RandomizedSearchCV` samples from distributions (`scipy.stats.loguniform`) instead of a grid; with many parameters it finds good regions in far fewer fits. `HalvingGridSearchCV` (experimental) discards poor candidates early.

### Nested cross-validation

When you have no separate test set, wrap the grid search in an outer CV:

```python
scores = cross_val_score(GridSearchCV(SVC(), param_grid, cv=5), iris.data, iris.target, cv=5)
print(scores.mean())   # 0.98: an estimate of how well "grid search over SVC" generalises
```

5 × 5 × 36 = 900 fits. It evaluates the model *selection procedure*, not one model. `n_jobs=-1` parallelises.

---

## Metrics: keep the end goal in mind

Accuracy treats every mistake the same. Business consequences rarely do.

| Error | Also called | Cancer screening | Spam filter |
|---|---|---|---|
| False positive | Type I | Healthy patient sent for more tests (cost, stress) | Real email lost in spam (bad) |
| False negative | Type II | Cancer missed (very bad) | Spam in the inbox (annoying) |

### Imbalanced data and the dummy baseline

On the digits dataset relabelled "is it a 9?" (10% positives), a classifier that always says "not 9" scores 90% accuracy.

```python
from sklearn.dummy import DummyClassifier
dummy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)   # 0.90
dummy = DummyClassifier(strategy="stratified").fit(X_train, y_train)      # ~0.80, random by class rate
# A tree scores 0.92 and logistic regression 0.98: only the last is clearly useful.
```

Always compare against a dummy. If accuracy barely beats it, accuracy is the wrong metric.

### Confusion matrix, precision, recall, F1

```python
from sklearn.metrics import confusion_matrix, classification_report
confusion_matrix(y_test, pred)
# [[TN FP]
#  [FN TP]]
print(classification_report(y_test, pred, target_names=["not nine", "nine"]))
```

| Metric | Formula | Answers | Optimise when |
|---|---|---|---|
| Accuracy | $(TP+TN)/n$ | Fraction right | Balanced classes, symmetric costs |
| Precision (PPV) | $TP/(TP+FP)$ | Of those flagged, how many are real? | False positives are costly (drug trials, spam) |
| Recall (sensitivity, TPR) | $TP/(TP+FN)$ | Of the real ones, how many did we catch? | False negatives are costly (cancer, fraud) |
| Specificity | $TN/(TN+FP)$ | Of the negatives, how many did we leave alone? | |
| FPR | $FP/(FP+TN)$ | | The x-axis of ROC |
| F1 | $2PR/(P+R)$ | Harmonic mean of P and R | One number for an imbalanced positive class |
| $F_\beta$ | weights recall $\beta$ times | | Asymmetric preference |

The dummy "always not-nine" has accuracy 0.90 and F1 0.00 on the positive class. F1 exposes it.

---

## Threshold, precision–recall and ROC

`predict` thresholds `decision_function` at 0 or `predict_proba` at 0.5 ([02](02-supervised-learning.md#uncertainty-estimates)). Moving the threshold trades precision for recall without retraining.

```python
y_pred_lower = svc.decision_function(X_test) > -0.8   # catch more positives: recall up, precision down
```

**Never pick the threshold on the test set.** Use a validation set or CV; `TunedThresholdClassifierCV` (scikit-learn 1.5) does this for you.

### Precision–recall curve

```python
from sklearn.metrics import precision_recall_curve, average_precision_score
precision, recall, thresholds = precision_recall_curve(y_test, svc.decision_function(X_test))
ap = average_precision_score(y_test, rf.predict_proba(X_test)[:, 1])   # area under the PR curve
```

The closer the curve hugs the top right, the better. Average precision summarises it; with heavy imbalance it is more informative than ROC AUC, because it ignores the large pool of true negatives.

### ROC curve and AUC

```python
from sklearn.metrics import roc_curve, roc_auc_score
fpr, tpr, thresholds = roc_curve(y_test, svc.decision_function(X_test))
auc = roc_auc_score(y_test, rf.predict_proba(X_test)[:, 1])
```

ROC plots TPR against FPR over all thresholds. **AUC** is the probability that a random positive gets a higher score than a random negative: 0.5 is chance, 1.0 is perfect ranking. A random predictor always scores 0.5 regardless of class balance, which makes AUC a better model-selection metric than accuracy on imbalanced data.

On M&G's digits "is it a 9?" example, SVMs with `gamma` 1, 0.1 and 0.01 all have accuracy 0.90 (the dummy rate), but AUC 0.50, 0.90 and 1.00. The model with `gamma=0.01` ranks perfectly; only the default threshold is wrong.

| Curve | Axes | Use when |
|---|---|---|
| Precision–recall | P vs R | Positive class rare; you care about the flagged set |
| ROC | TPR vs FPR | Ranking quality overall; balanced-ish data |

---

## Multiclass and regression metrics

**Multiclass.** The confusion matrix is $K \times K$; read the off-diagonals for which classes are confused. F1 per class, averaged:

| Average | Weights | Use when |
|---|---|---|
| `macro` | Every class equally | Small classes matter as much as large |
| `weighted` | By class support | Default in `classification_report` |
| `micro` | Every sample equally (= accuracy for single-label) | Each sample matters equally |

**Regression.** $R^2$ (default `score`) is fine for model comparison. For reporting, use a unit the business understands: MAE (robust to outliers), RMSE (penalises big misses), MAPE (relative error; undefined at zero).

---

## Using a metric in model selection

Pass `scoring` to CV and grid search; the default is accuracy (classifiers) or $R^2$ (regressors).

```python
grid = GridSearchCV(SVC(), {"gamma": [0.0001, 0.01, 0.1, 1, 10]}, scoring="roc_auc").fit(X_train, y_train)
# Selecting by accuracy picks gamma=0.0001 (test AUC 0.92); by AUC picks gamma=0.01 (test AUC 1.00)

from sklearn.metrics import get_scorer_names
sorted(get_scorer_names())   # "accuracy", "roc_auc", "average_precision", "f1_macro", "neg_mean_squared_error", ...
```

Error metrics are negated (`neg_mean_absolute_error`) because scikit-learn always maximises.

---

## Learning curves and bias-variance diagnosis

Ng's ex5 makes the diagnosis from [01](01-statistical-foundations.md#bias-variance-and-model-complexity) operational. Fit regularised linear regression on the water-level/dam-outflow data with an increasing number of training examples; plot training error and cross-validation error against $m$.

```python
# Ng ex5, vectorised: regularised linear regression cost and learning curve
def compute_cost(theta, X, y, lam=0.0):
    m = len(y)
    err = X @ theta - y
    return (err @ err) / (2 * m) + lam / (2 * m) * (theta[1:] @ theta[1:])

def learning_curve(X, y, Xval, yval, lam=0.0):
    train_err, val_err = [], []
    for i in range(1, len(y) + 1):
        theta = fit(X[:i], y[:i], lam)                     # scipy.optimize on the first i points
        train_err.append(compute_cost(theta, X[:i], y[:i], 0.0))   # report errors WITHOUT the penalty
        val_err.append(compute_cost(theta, Xval, yval, 0.0))
    return train_err, val_err
```

| Curve shape | Diagnosis | More data helps? | Fix |
|---|---|---|---|
| Train and val error both high, converge quickly | High bias (underfit): ex5's straight line | No | More features (ex5: degree-8 polynomial), less regularisation, bigger model |
| Train error low, large gap to val error | High variance (overfit): ex5's polynomial with $\lambda = 0$ | Yes | More data, more regularisation, fewer features |
| Both low, small gap | Good fit | Marginal | Ship it |

Ex5 then selects $\lambda$ on the validation set: sweep $\lambda \in \{0, 0.001, \ldots, 10\}$, pick the one with lowest validation error ($\lambda \approx 3$), report test error once. That is grid search written out by hand.

scikit-learn's version:

```python
from sklearn.model_selection import learning_curve, validation_curve
sizes, train_scores, val_scores = learning_curve(Ridge(alpha=1), X, y, cv=5,
                                                 train_sizes=np.linspace(0.1, 1.0, 10))
# validation_curve sweeps one hyperparameter instead of training size
```

---

## Rules

| Rule | Why |
|---|---|
| Report a test score exactly once, after all choices | Every look at it is a choice that leaks |
| Split the way production meets data (groups, time) | Otherwise CV measures memorisation |
| Compare against `DummyClassifier` first | 90% accuracy can be zero skill |
| Choose the metric from the cost of each error type | Accuracy assumes FP and FN cost the same |
| Use AUC or average precision for model selection on imbalanced data; tune the threshold separately | Ranking quality and operating point are separate decisions |
| Plot a learning curve before collecting more data | It tells you whether more data can help |
| Search hyperparameters on a log scale, check the best isn't on an edge | |

---

## scikit-learn migration map (0.20 → 1.4)

The vendored M&G notebooks were written against scikit-learn 0.20. This repo's copies were updated for 1.4+ (#35) and `environment.yml` pins `scikit-learn>=1.4`.

| Old API | New API | Changed in |
|---|---|---|
| `from sklearn.cross_validation import ...` | `from sklearn.model_selection import ...` | Removed 0.20 |
| `from sklearn.grid_search import GridSearchCV` | `from sklearn.model_selection import GridSearchCV` | Removed 0.20 |
| `DummyClassifier()` (default `strategy="warn"`) | `DummyClassifier(strategy="stratified")` or `"prior"` explicitly | Default changed 0.24/1.1 |
| `OneHotEncoder(sparse=False)` | `OneHotEncoder(sparse_output=False)` | Renamed 1.2, old name removed 1.4 |
| `GridSearchCV(..., iid=True)` | Drop `iid` | Removed 1.0 (0.24 deprecation) |
| `LogisticRegression()` (convergence warnings on unscaled data) | `LogisticRegression(max_iter=1000)` or scale first | Default solver `lbfgs` since 0.22 |
| `load_boston()` | `fetch_california_housing()` or `mglearn.datasets.load_extended_boston()` | Removed 1.2 |

Where the fixes landed:

| Notebook | Change |
|---|---|
| `02-supervised-learning.ipynb` | `LogisticRegression(max_iter=1000)`, `DummyClassifier(strategy="stratified")` |
| `04-representing-data-feature-engineering.ipynb` | `OneHotEncoder(sparse_output=False)` in cells 18, 21, 26 |
| `05-model-evaluation-and-improvement.ipynb` | No stale imports (uses `mglearn` helpers) |
| `01`, `03`, `06`, `07`, `08` | Clean |
| `../practice/approaching-almost-any-nlp-problem-on-kaggle.ipynb` | `iid=True` removed from `GridSearchCV` (cells 41, 43) |
| Sarkar *Text Analytics*, Ng ML exercises | Clean (Sarkar uses `Pipeline` only; Ng uses no sklearn) |

`cross_validation` appearing in Sarkar's `Ch06b` is an LDA topic word in a notebook output, not an import.

---

## Practice

| Notebook | Covers | Runs |
|---|---|---|
| [`05-model-evaluation-and-improvement.ipynb`](../practice/Intro%20to%20Machine%20Learning%20in%20Python/05-model-evaluation-and-improvement.ipynb) | Everything above except ex5 | Offline; `scikit-learn>=1.4`, local `mglearn` |
| [`ex5.ipynb`](../Ng's%20Machine%20Learning%20Nbks/ex5/ex5.ipynb) | Regularised linear regression, learning curves, polynomial features, selecting $\lambda$ | Legacy: Python 2.7 kernel; `scipy.io.loadmat` data in `ex5/data/` |

---

→ Next: [05-unsupervised-learning.md](05-unsupervised-learning.md) — no labels: scaling, PCA, NMF, t-SNE, clustering, anomaly detection and recommenders.
