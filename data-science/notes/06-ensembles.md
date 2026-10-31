---
origin: vendored snapshot: Intro to Machine Learning in Python (kept as practice)
sources:
  - https://github.com/amueller/introduction_to_ml_with_python
  - ../practice/Intro to Machine Learning in Python/02-supervised-learning.ipynb
  - https://scikit-learn.org/stable/modules/ensemble.html
  - https://xgboost.readthedocs.io/
  - https://lightgbm.readthedocs.io/
  - https://shap.readthedocs.io/
confidence: high (sklearn sections); medium (XGBoost/LightGBM/SHAP: no notebook here)
cleaned: 2026-10-31
---
# 6 — Ensembles

> A single tree overfits; many trees combined don't. Bagging averages independent deep trees to cut variance (random forests). Boosting adds shallow trees one at a time, each fixing the last one's errors, to cut bias (gradient boosting). Together they are the default for tabular data.

---

## Why combine models

A decision tree ([02](02-supervised-learning.md#decision-trees)) has low bias and high variance: small changes in the data change the tree a lot. Averaging many models whose errors are not perfectly correlated reduces variance. If each of $B$ models has variance $\sigma^2$ and pairwise correlation $\rho$, the average has variance

$$\rho\sigma^2 + \frac{1-\rho}{B}\sigma^2$$

Adding more trees kills the second term; only *decorrelating* the trees attacks the first. That is the whole design of random forests.

| | Bagging / random forests | Boosting |
|---|---|---|
| Trees built | Independently, in parallel | Sequentially, each on the previous ensemble's errors |
| Each tree | Deep (low bias, high variance) | Shallow, depth 1–5 (high bias, low variance) |
| Reduces | Variance | Bias (and variance through shrinkage) |
| Combining | Average (or vote) | Weighted sum |
| More trees | Never hurts, only costs time | Eventually overfits without early stopping |
| Tuning effort | Low | Higher |

---

## Random forests

Two sources of randomness make the trees different:

1. **Bootstrap sample.** Each tree trains on $n$ points drawn with replacement (about 63% unique; the remaining ~37% are "out-of-bag").
2. **Random feature subset at each split.** Each node considers only `max_features` randomly chosen features.

```python
from sklearn.ensemble import RandomForestClassifier
forest = RandomForestClassifier(n_estimators=100, random_state=0, n_jobs=-1, oob_score=True)
forest.fit(X_train, y_train)
print(forest.score(X_train, y_train), forest.score(X_test, y_test))   # 1.000, 0.972 on breast cancer
print(forest.oob_score_)   # free validation estimate from the out-of-bag points
```

A single unpruned tree scored 0.937 on the same split. The forest gets 0.972 with no tuning.

| Parameter | Effect | Default advice |
|---|---|---|
| `n_estimators` | More trees: smoother, more stable; diminishing returns | As many as time and memory allow (100–500) |
| `max_features` | Low: more random, less correlated trees, each weaker. High: trees alike | `"sqrt"` for classification, `1.0` for regression (scikit-learn defaults) |
| `max_depth`, `min_samples_leaf` | Pre-pruning; rarely needed | Tune only to cut memory/time |
| `n_jobs=-1` | Train trees on all cores | Always |
| `random_state` | Results vary between seeds with few trees | Fix it for reproducibility |

**Strengths:** strong out of the box, no scaling, handles mixed feature types, parallel, OOB score for free. **Weaknesses:** poor on very high-dimensional sparse data (text: use linear models, [09](09-text-classification.md)); slow to predict with many deep trees; less interpretable than one tree; cannot extrapolate beyond the training range.

`ExtraTreesClassifier` adds a third source of randomness (random split thresholds); faster, sometimes as good.

---

## Gradient boosting

Fit a shallow tree; compute the residuals (more generally, the negative gradient of the loss with respect to the current predictions); fit the next tree to those; add it scaled by a learning rate; repeat.

$$F_m(x) = F_{m-1}(x) + \eta \, h_m(x), \qquad h_m \approx -\frac{\partial L(y, F_{m-1}(x))}{\partial F_{m-1}(x)}$$

For squared error the negative gradient *is* the residual; for log-loss it is $y - p$. Gradient boosting is gradient descent in function space.

```python
from sklearn.ensemble import GradientBoostingClassifier

gbrt = GradientBoostingClassifier(random_state=0).fit(X_train, y_train)
# train 1.000, test 0.965: overfitting

gbrt = GradientBoostingClassifier(random_state=0, max_depth=1).fit(X_train, y_train)
# train 0.991, test 0.972: stumps are enough

gbrt = GradientBoostingClassifier(random_state=0, learning_rate=0.01).fit(X_train, y_train)
# train 0.988, test 0.965
```

| Parameter | Effect |
|---|---|
| `learning_rate` ($\eta$) | Shrinks each tree's contribution. Lower needs more trees, generalises better |
| `n_estimators` | Number of boosting rounds. **Too many overfits** |
| `max_depth` | Tree size; 1–5. Depth $d$ captures interactions of up to $d$ features |
| `subsample` < 1 | Stochastic gradient boosting: each tree on a random fraction; regularises |
| `n_iter_no_change`, `validation_fraction` | Early stopping |

**The tuning recipe:** fix `n_estimators` by time budget, then search `learning_rate` and `max_depth`; or use a low learning rate with early stopping on a validation set.

Because `n_estimators` and `learning_rate` trade against each other, a grid over both is wasteful; early stopping picks `n_estimators` for you.

### HistGradientBoosting

For more than ~10k rows, use `HistGradientBoostingClassifier` / `Regressor`: features are binned into ≤255 histograms, orders of magnitude faster, native missing-value and categorical support, early stopping on by default above 10k samples. It is scikit-learn's implementation of the LightGBM approach.

```python
from sklearn.ensemble import HistGradientBoostingClassifier
hgb = HistGradientBoostingClassifier(max_iter=500, learning_rate=0.05,
                                     categorical_features="from_dtype").fit(X_train, y_train)
```

---

## Feature importance

Tree ensembles report `feature_importances_`: the total impurity decrease from splits on each feature, averaged over trees, normalised to sum to 1.

| Single tree | Random forest | Gradient boosting |
|---|---|---|
| Zero for most features: picks one of each correlated group | Non-zero for many more: random feature subsets spread the credit | Concentrated on few features; some ignored entirely |

Caveats that come up in interviews:

- **Impurity importance is biased toward high-cardinality features** (continuous, IDs) and is computed on training data, so it rewards features the model overfit on.
- **Correlated features share or steal credit.** A low importance doesn't mean a feature is useless.
- **Importance says how much, never which direction.**

Better options:

| Method | How | API |
|---|---|---|
| Permutation importance | Shuffle a feature on held-out data; measure the score drop | `sklearn.inspection.permutation_importance` |
| Partial dependence / ICE | Average prediction as one feature varies | `sklearn.inspection.PartialDependenceDisplay` |
| SHAP values | Game-theoretic per-prediction attribution; sums to prediction − baseline; `TreeExplainer` is exact and fast for trees | `shap` library |

---

## Stacking and voting

Combine different model families rather than many trees:

```python
from sklearn.ensemble import StackingClassifier, VotingClassifier
stack = StackingClassifier(
    estimators=[("rf", RandomForestClassifier()), ("svc", make_pipeline(StandardScaler(), SVC(probability=True)))],
    final_estimator=LogisticRegression(), cv=5)   # meta-model trained on out-of-fold predictions
```

Gains are usually small and the system gets harder to maintain. Kaggle uses stacking heavily (see the Kaggle NLP notebook in [09](09-text-classification.md)); production usually doesn't.

---

## The gap: XGBoost, LightGBM, CatBoost

The vendored notebooks use scikit-learn's `GradientBoostingClassifier` only. The libraries that win tabular competitions and run most tabular production models have no notebook here. This is a coverage gap, not a version issue.

| Library | Distinctive features | Docs |
|---|---|---|
| XGBoost | Second-order (Newton) boosting, explicit L1/L2 regularisation on leaf weights, sparsity-aware splits, GPU | [xgboost.readthedocs.io](https://xgboost.readthedocs.io/) |
| LightGBM | Histogram splits, leaf-wise growth (`num_leaves` is the key knob), GOSS sampling, native categoricals; fastest on large data | [lightgbm.readthedocs.io](https://lightgbm.readthedocs.io/) |
| CatBoost | Ordered target statistics for categoricals (no leakage), symmetric trees; strong defaults | [catboost.ai/docs](https://catboost.ai/docs/) |

All three expose a scikit-learn-compatible API, so they drop into the pipelines and grid searches of [03](03-feature-engineering-and-pipelines.md) and [04](04-model-evaluation.md):

```python
import lightgbm as lgb
model = lgb.LGBMClassifier(n_estimators=2000, learning_rate=0.03, num_leaves=31)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)],
          callbacks=[lgb.early_stopping(100)])     # early stopping picks n_estimators

import shap
explainer = shap.TreeExplainer(model)
shap.summary_plot(explainer.shap_values(X_val), X_val)
```

To fill the gap: a notebook comparing `GradientBoostingClassifier`, `HistGradientBoostingClassifier`, XGBoost and LightGBM on the adult census data in `../practice/Intro to Machine Learning in Python/data/`, with SHAP explanations.

---

## Rules

| Rule | Why |
|---|---|
| Random forest is the first serious model on a tabular problem | Strong with no tuning; gives a bar to beat |
| Gradient boosting (Hist/LightGBM/XGBoost) when you need the last points of accuracy | Best tabular performance; needs tuning |
| Use early stopping instead of grid-searching `n_estimators` | Learning rate and rounds trade off |
| More forest trees never overfit; more boosting rounds do | Averaging vs sequential fitting |
| Report permutation importance or SHAP, not impurity importance | Impurity importance is biased and train-set based |
| Don't use tree ensembles on sparse text features | Linear models win there |

---

## Practice

| Notebook | Covers | Runs |
|---|---|---|
| [`02-supervised-learning.ipynb`](../practice/Intro%20to%20Machine%20Learning%20in%20Python/02-supervised-learning.ipynb), section "Ensembles of Decision Trees" | Random forests, gradient boosting, feature importances on breast cancer | Offline; `scikit-learn>=1.4`, local `mglearn` |

---

→ Next: [07-neural-networks-fundamentals.md](07-neural-networks-fundamentals.md) — from the sklearn MLP to backprop by hand and the Deep Learning Specialization.
