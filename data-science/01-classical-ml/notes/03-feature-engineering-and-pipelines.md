---
origin: vendored snapshot: Intro to Machine Learning in Python (kept as practice)
sources:
  - https://github.com/amueller/introduction_to_ml_with_python
  - ../practice/Intro to Machine Learning in Python/04-representing-data-feature-engineering.ipynb
  - ../practice/Intro to Machine Learning in Python/06-algorithm-chains-and-pipelines.ipynb
  - ../sources/mueller-guido-introduction-to-ml-with-python.pdf
confidence: high
cleaned: 2026-10-31
---
# 3 — Feature Engineering and Pipelines

> How you represent the data usually matters more than which model you pick. Encode categoricals, bin or expand numeric features for linear models, select what helps, add what a domain expert knows, and wrap every fitted transformation in a `Pipeline` so cross-validation never sees the test fold.

---

## Why representation matters

[02](02-supervised-learning.md) assumed a clean matrix of continuous numbers. Real tables have categories ("workclass = Private"), dates, counts and text. The best representation depends on the model:

| Model family | Wants |
|---|---|
| Linear models, SVMs, MLPs | Scaled numeric features; expanded features (bins, interactions, polynomials) to fit non-linear shapes |
| Trees and ensembles | Raw features; no scaling; they find interactions themselves |
| kNN | Scaled features, few of them |

---

## Categorical variables

The adult census dataset (M&G ch. 4, `data/adult.data`) predicts income > $50k from age, workclass, education, gender, hours-per-week and occupation. Four of the six columns are strings.

### One-hot encoding

Replace a column with $k$ categories by $k$ binary columns.

```python
import pandas as pd
data = pd.read_csv("data/adult.data", header=None, index_col=False, names=[...])
print(data.gender.value_counts())   # always check for typos: " Male" vs "male" become separate categories

dummies = pd.get_dummies(data)       # encodes every object/category column
```

**Encode train and test together, or with a fitted encoder.** `get_dummies` on train and test separately can produce different columns when a category appears in only one of them.

**Integers can be categories.** A survey answer coded 1–5 or a zip code is categorical even though it looks numeric. `get_dummies` will not encode it unless you convert it to string first.

### OneHotEncoder and ColumnTransformer

The scikit-learn way: a fitted transformer that remembers the categories from training, applied per column.

```python
from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ct = ColumnTransformer([
    ("scaling", StandardScaler(), ["age", "hours-per-week"]),
    ("onehot", OneHotEncoder(sparse_output=False, handle_unknown="ignore"),
               ["workclass", "education", "gender", "occupation"]),
])
X_train_trans = ct.fit_transform(X_train)   # fit categories and scaling on train only
X_test_trans = ct.transform(X_test)          # unseen category -> all zeros (handle_unknown)
```

`sparse=` was renamed `sparse_output=` in scikit-learn 1.2 and the old name removed in 1.4; see the migration map in [04](04-model-evaluation.md#scikit-learn-migration-map-020--14).

| Encoding | When |
|---|---|
| One-hot | Few categories; linear models |
| Ordinal (`OrdinalEncoder`) | Categories with an order; tree models |
| Target / frequency encoding | Very many categories (IDs, zip codes); needs cross-fitting to avoid leakage |
| Native categorical support | `HistGradientBoostingClassifier(categorical_features=...)`, LightGBM |

---

## Binning, interactions and polynomials

A linear model on one feature fits a line. Three ways to give it more shape:

**Binning** cuts a continuous feature into intervals and one-hot encodes them; the model learns a constant per bin, i.e. a step function.

```python
from sklearn.preprocessing import KBinsDiscretizer
kb = KBinsDiscretizer(n_bins=10, strategy="uniform", encode="onehot-dense")
X_binned = kb.fit_transform(X)
```

On the `make_wave` data, a linear model and a decision tree on binned features make *identical* predictions: binning gives the linear model the tree's flexibility and does nothing for the tree.

**Interactions** add the product of the bin indicators with the original feature, so each bin gets its own slope.

**Polynomials** add $x^2, x^3, \ldots$ and cross-products:

```python
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, include_bias=False)   # 13 Boston features -> 104
```

On the Boston data, ridge improves from 0.62 to 0.75 test $R^2$ with degree-2 features; a random forest gets *worse* with them (0.80 → 0.77). Expanded features help linear models and are noise to trees.

| Technique | Helps | Cost |
|---|---|---|
| Binning | Linear models on low-dim data | Loses within-bin information |
| Interactions | Linear models where effects combine | Feature count grows quadratically |
| Polynomials | Smooth non-linear trends | Extreme values at the edges with high degree; overfitting |

---

## Univariate non-linear transforms

Count data (visits, purchases, word counts) is usually heavily skewed: many small values, a few huge ones. Linear models and neural networks prefer roughly Gaussian features.

```python
X_train_log = np.log1p(X_train)    # log(x + 1): handles zeros
# M&G's Poisson count example: Ridge R^2 0.62 -> 0.875 after log transform
```

Other options: `np.sqrt`, `PowerTransformer` (Box-Cox, Yeo-Johnson), `QuantileTransformer`. Transforming the *target* also helps regression on skewed targets (`TransformedTargetRegressor`). Trees ignore monotone transforms of features entirely.

---

## Automatic feature selection

Fewer features means simpler, faster and sometimes more general models. Three strategies, cheapest first:

| Strategy | Class | How |
|---|---|---|
| Univariate statistics | `SelectKBest`, `SelectPercentile` (`f_classif`, `f_regression`, `chi2`, `mutual_info_*`) | Test each feature against the target alone; keep the top |
| Model-based | `SelectFromModel(RandomForestClassifier(), threshold="median")` | Fit a model with importances or L1 coefficients; keep features above a threshold |
| Iterative | `RFE(estimator, n_features_to_select=40)`, `SequentialFeatureSelector` | Fit, drop the weakest feature, refit, repeat |

M&G's experiment: add 50 noise features to the 30 breast-cancer features. Univariate selection at 50% recovers most of the real ones (test score 0.930 → 0.940); model-based and RFE do better (0.951). Selection only pays off when you suspect many features are noise; with a regularised model on clean data it rarely helps.

Feature selection is a fitted step. Selecting on all data and then cross-validating is the leakage bug below.

---

## Expert knowledge

The Citi Bike rental series (M&G ch. 4, `data/citibike.csv`) shows the value of domain features. Predicting the number of rentals per 3-hour slot from the raw POSIX timestamp:

| Features | Model | Test $R^2$ |
|---|---|---|
| POSIX time | Random forest | −0.04 (trees can't extrapolate; see [02](02-supervised-learning.md#decision-trees)) |
| Hour of day | Random forest | 0.60 |
| Hour + day of week | Random forest | 0.84 |
| Hour + day of week, one-hot | Linear regression | 0.62 |
| One-hot hour × day interactions | Ridge | 0.85 |

A person who knows bikes are rented on commutes and weekends writes `X_hour_week` in one line; no model discovers it from the raw timestamp. The final ridge model is also readable: one coefficient per hour-of-day-and-weekday cell.

---

## Leakage and why pipelines exist

The classic bug (M&G ch. 6):

```python
scaler = MinMaxScaler().fit(X_train)          # fit on ALL training data
X_train_scaled = scaler.transform(X_train)
grid = GridSearchCV(SVC(), param_grid, cv=5).fit(X_train_scaled, y_train)   # wrong
```

Inside each CV split, the validation fold was already used to fit the scaler. The CV score is optimistic because the "unseen" data shaped the preprocessing. With scaling the bias is small. With feature selection it is enormous: M&G select the top 5% of 10,000 *pure-noise* features against random targets, then cross-validate ridge.

| Procedure | CV $R^2$ on pure noise |
|---|---|
| `SelectPercentile` on all data, then `cross_val_score(Ridge())` | 0.91 |
| `cross_val_score(Pipeline([select, ridge]))` | −0.25 (correct: there is no signal) |

**Rule:** any step with a `fit` (scaling, imputation, encoding, selection, PCA, target encoding, vectorising text) must be refit inside each fold. A `Pipeline` does that for you.

---

## Pipelines

A pipeline chains transformers and a final estimator into one estimator, so `fit`, `predict`, `score` and cross-validation treat the whole chain as one model.

![Overview of the training and prediction process in a pipeline](../sources/images/mueller-guido-pipeline.png)
*Image source: Müller & Guido, Introduction to Machine Learning with Python, companion repo `images/pipeline.png`*

```python
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.model_selection import GridSearchCV

pipe = Pipeline([("scaler", MinMaxScaler()), ("svm", SVC())])
param_grid = {"svm__C": [0.001, 0.01, 0.1, 1, 10, 100],      # <step name>__<parameter>
              "svm__gamma": [0.001, 0.01, 0.1, 1, 10, 100]}
grid = GridSearchCV(pipe, param_grid, cv=5).fit(X_train, y_train)
print(grid.best_score_, grid.score(X_test, y_test))

# make_pipeline names steps automatically: "minmaxscaler", "svc"
pipe_short = make_pipeline(MinMaxScaler(), SVC(C=100))
```

**Accessing steps.** `pipe.named_steps["logisticregression"].coef_`; inside a grid search, `grid.best_estimator_.named_steps[...]`.

### Grid-searching the preprocessing too

The preprocessing has hyperparameters as well, and you can search them jointly with the model's:

```python
pipe = make_pipeline(StandardScaler(), PolynomialFeatures(), Ridge())
param_grid = {"polynomialfeatures__degree": [1, 2, 3],
              "ridge__alpha": [0.001, 0.01, 0.1, 1, 10, 100]}
# best: degree=2, alpha=10 on Boston
```

You can even search *which* steps to use by treating a step as a parameter:

```python
pipe = Pipeline([("preprocessing", StandardScaler()), ("classifier", SVC())])
param_grid = [
    {"classifier": [SVC()], "preprocessing": [StandardScaler(), None],
     "classifier__gamma": [0.001, 0.01, 0.1, 1, 10, 100],
     "classifier__C": [0.001, 0.01, 0.1, 1, 10, 100]},
    {"classifier": [RandomForestClassifier(n_estimators=100)],
     "preprocessing": [None], "classifier__max_features": [1, 2, 3]},
]
```

`Pipeline(memory="cache_dir")` caches fitted transformers so a grid search doesn't refit an expensive step for every model parameter.

### The general interface

Every step except the last must have `fit` and `transform`. The last needs `fit` and, depending on use, `predict`, `score` or `transform`. Internally, `pipeline.fit` calls `fit_transform` on each step in turn and passes the output on; `predict` calls `transform` on each step and `predict` on the last.

---

## Rules

| Rule | Why |
|---|---|
| Put every fitted preprocessing step in a pipeline | Leakage, and the pipeline is what you deploy |
| Use `ColumnTransformer` for mixed-type tables | One object holds the per-column logic |
| `handle_unknown="ignore"` in production encoders | New categories appear after deployment |
| Expand features for linear models, not for trees | Trees find interactions; extra features are noise to them |
| Log-transform skewed counts | Linear models and NNs assume roughly symmetric inputs |
| Try a domain feature before a bigger model | Citi Bike: hour + weekday beat every model on the timestamp |

---

## Practice

| Notebook | Covers | Runs |
|---|---|---|
| [`04-representing-data-feature-engineering.ipynb`](../practice/Intro%20to%20Machine%20Learning%20in%20Python/04-representing-data-feature-engineering.ipynb) | Encoding, binning, polynomials, transforms, selection, Citi Bike | Offline; `scikit-learn>=1.4`, local `mglearn`; data in `data/` |
| [`06-algorithm-chains-and-pipelines.ipynb`](../practice/Intro%20to%20Machine%20Learning%20in%20Python/06-algorithm-chains-and-pipelines.ipynb) | Leakage, pipelines, grid search over pipelines | Offline; same |

---

→ Next: [04-model-evaluation.md](04-model-evaluation.md) — cross-validation, grid search and metrics that match the business question.
