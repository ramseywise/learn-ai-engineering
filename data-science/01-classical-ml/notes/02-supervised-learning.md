---
origin: vendored snapshot: Intro to Machine Learning in Python (kept as practice) + own coursework (Ng ML ex1–ex4, ex6)
sources:
  - https://github.com/amueller/introduction_to_ml_with_python
  - ../practice/Intro to Machine Learning in Python/02-supervised-learning.ipynb
  - https://www.coursera.org/learn/machine-learning
  - ../Ng's Machine Learning Nbks/ex1/ex1.ipynb
  - ../Ng's Machine Learning Nbks/ex2/ex2.ipynb
  - ../Ng's Machine Learning Nbks/ex3/ex3.ipynb
  - ../Ng's Machine Learning Nbks/ex6/ex6.ipynb
confidence: high
cleaned: 2026-10-31
---
# 2 — Supervised Learning

> The classical model families — nearest neighbours, linear models, naive Bayes, trees, kernel SVMs, small neural networks — each with the one knob that controls its complexity, what it is good at, and how it fails; plus the from-scratch versions from Ng's exercises.

---

## The two tasks

| | Classification | Regression |
|---|---|---|
| Target | A class label from a fixed set | A continuous number |
| Example (M&G ch. 2) | Breast-cancer benign/malignant; `make_forge` two-class toy | Boston-style house prices; `make_wave` 1-D toy |
| Default `score` | Accuracy | $R^2$ |
| Loss in training | Log-loss (logistic), hinge (SVM), Gini/entropy (trees) | Squared error |

The test for which one you have: *is there continuity between possible outputs?* Income in dollars is regression; the language of a website is classification.

Every model below has a **complexity knob**. Turning it trades the bias and variance of [01](01-statistical-foundations.md#bias-variance-and-model-complexity), and the first thing to do with any new model is to sweep that knob and plot train and test score against it.

---

## k-nearest neighbours

The simplest model: memorise the training set; predict by looking at the $k$ closest training points (majority vote for classification, mean for regression).

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

cancer = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    cancer.data, cancer.target, stratify=cancer.target, random_state=66)

# Sweep the complexity knob: small k = complex (jagged boundary), large k = simple
for k in range(1, 11):
    clf = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train)
    print(k, clf.score(X_train, y_train), clf.score(X_test, y_test))
# k=1: train 1.00, test ~0.90; best test near k=6; large k: both fall (underfit)
```

The single-neighbour model gets every training point right and is the worst on test. That is overfitting made visible.

| | |
|---|---|
| Knob | `n_neighbors` (and the distance metric) |
| Good at | A baseline in minutes; small, low-dimensional data |
| Fails on | Many features (distances stop meaning anything); sparse data; large training sets (prediction is slow) |
| Needs | Feature scaling: distances are dominated by the largest-range feature |

---

## Linear models

Predict with a weighted sum: $\hat y = w \cdot x + b$. For classification, threshold it at zero.

### Regression: OLS, ridge, lasso

| Model | Objective | Effect | Knob |
|---|---|---|---|
| `LinearRegression` (OLS) | $\min \lVert y - Xw \rVert^2$ | No complexity control; overfits with many features | — |
| `Ridge` | $+\ \alpha \lVert w \rVert_2^2$ | Shrinks all weights toward 0 | `alpha` (higher = simpler) |
| `Lasso` | $+\ \alpha \lVert w \rVert_1$ | Sets some weights exactly to 0: built-in feature selection | `alpha`; raise `max_iter` when small |
| `ElasticNet` | Both penalties | Lasso's sparsity with ridge's stability | `alpha`, `l1_ratio` |

On the extended Boston data (104 features, M&G ch. 2), OLS scores 0.95 on train and 0.61 on test: it overfits. Ridge at `alpha=1` gets 0.89 / 0.75. Lasso at `alpha=0.01` uses 33 of the 104 features and generalises about as well.

```python
from sklearn.linear_model import Ridge, Lasso
ridge = Ridge(alpha=1.0).fit(X_train, y_train)
lasso = Lasso(alpha=0.01, max_iter=100_000).fit(X_train, y_train)  # small alpha needs more iterations
print((lasso.coef_ != 0).sum(), "features used")
```

**Ridge vs lasso.** Default to ridge. Use lasso when you expect only a few features to matter, or need a model you can read.

**Learning curves for ridge** show the data-size effect from [01](01-statistical-foundations.md): with enough data, regularisation matters less and OLS catches up.

### Classification: logistic regression and linear SVM

Both draw a hyperplane. They differ in loss (log-loss vs hinge), not in the shape of the boundary.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

# sklearn >= 1.4: lbfgs needs more iterations on unscaled data (fix applied in this repo's copy)
logreg = LogisticRegression(C=1, max_iter=1000).fit(X_train, y_train)
svm = LinearSVC(C=1).fit(X_train, y_train)
```

The knob is **`C`, the inverse of regularisation strength**: high `C` fits each training point harder (complex); low `C` keeps weights small (simple). Note the inversion against `alpha` above. `penalty="l1"` gives sparse coefficients, as lasso does.

**Multiclass.** Linear classifiers are binary by nature. One-vs-rest trains one classifier per class and predicts the class with the highest score. `LogisticRegression` uses a true multinomial (softmax) loss by default.

| | |
|---|---|
| Knob | `alpha` (regression), `C` (classification) |
| Good at | Very many features; sparse data (text, [09](../../03-nlp/notes/02-text-classification.md)); huge datasets (`SGDClassifier`, `solver="sag"`); fast to train and predict; coefficients readable |
| Fails on | Low-dimensional data with non-linear boundaries, unless you add features ([03](03-feature-engineering-and-pipelines.md)) |
| Caution | Coefficients of correlated features can flip sign; don't over-read them |

---

## Naive Bayes

Fit per-class statistics of each feature independently and apply Bayes' rule. Training is a single pass over the data.

| Variant | Data | Statistic per class |
|---|---|---|
| `GaussianNB` | Continuous | Mean and std per feature |
| `BernoulliNB` | Binary | Count of non-zero per feature |
| `MultinomialNB` | Counts (word counts) | Mean count per feature |

Knob: `alpha` (additive smoothing: pretends every feature was seen `alpha` extra times in every class). Naive Bayes is the classic fast text baseline ([09](../../03-nlp/notes/02-text-classification.md)); usually slightly worse than a linear model, trained much faster.

---

## Decision trees

A tree asks a sequence of if/else questions ("is feature 3 ≤ 0.8?"), each chosen to make the resulting groups as pure as possible. A leaf predicts the majority class (or mean value) of its training points.

```python
from sklearn.tree import DecisionTreeClassifier, export_graphviz
tree = DecisionTreeClassifier(max_depth=4, random_state=0).fit(X_train, y_train)
# Unpruned: train 1.000, test 0.937.  max_depth=4: train 0.988, test 0.951
print(tree.feature_importances_)   # sums to 1; zero means unused, not "unimportant"
```

A tree grown until every leaf is pure memorises the training set. Control it with **pre-pruning**: `max_depth`, `max_leaf_nodes`, or `min_samples_leaf`. scikit-learn also has cost-complexity post-pruning (`ccp_alpha`).

**Two quirks to remember:**

- **No scaling needed.** Each split looks at one feature at a time.
- **Trees can't extrapolate.** On the RAM-price time series (M&G ch. 2), a tree predicts the last known price forever after the training range, while a linear model on log-price continues the trend.

A single tree is rarely the best model. Its value is as the building block of [06 — ensembles](06-ensembles.md), where random forests and gradient boosting fix its variance.

---

## Kernelized support vector machines

A linear model in a richer feature space. Adding $x_1^2$ as a feature turns a curved boundary into a plane in 3-D. The **kernel trick** computes inner products in that expanded space without building it.

| Kernel | Implicit features |
|---|---|
| Polynomial | All products of features up to a degree |
| RBF (Gaussian) | Infinite-dimensional; similarity decays with distance: $k(x, x') = \exp(-\gamma \lVert x - x' \rVert^2)$ |

Only the training points on the margin, the **support vectors**, define the boundary.

```python
from sklearn.svm import SVC
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler().fit(X_train)           # fit on train only (see 03)
svc = SVC(kernel="rbf", C=1000, gamma="scale").fit(scaler.transform(X_train), y_train)
# Unscaled breast-cancer data: test 0.63. Scaled to [0,1], C=1000: test 0.97
```

| Knob | Small value | Large value |
|---|---|---|
| `gamma` | Wide kernel, smooth boundary | Narrow kernel, every point its own island |
| `C` | Heavy regularisation | Fit every training point |

Tune them **together** ([04 — grid search](04-model-evaluation.md#grid-search)).

| | |
|---|---|
| Good at | Small and medium data (up to ~10k samples) with features on similar scales; complex boundaries in few dimensions |
| Fails on | 100k+ samples (memory and time); unscaled features; interpretation |

Ng's ex6 implements the Gaussian kernel by hand and uses `sklearn.svm.SVC` on three 2-D datasets, then builds a **spam classifier**: email preprocessing (lower-case, strip HTML, normalise URLs, numbers and addresses, Porter stemming), a 1,899-word vocabulary, binary word-presence features, a linear SVM. That is the bag-of-words pipeline of [08](../../03-nlp/notes/01-text-representation.md) written out by hand.

```python
# Ng ex6: the Gaussian kernel, from scratch
def gauss_kernel(x1, x2, sigma):
    return np.exp(-np.sum((x1 - x2) ** 2) / (2.0 * sigma ** 2))   # gamma = 1 / (2 sigma^2)
```

---

## Neural networks (multilayer perceptrons)

A stack of linear models with a non-linearity between them: $h = \tanh(W_1 x + b_1)$, $\hat y = W_2 h + b_2$. Without the non-linearity, the stack collapses to one linear model.

```python
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

Xs_train = StandardScaler().fit(X_train).transform(X_train)
mlp = MLPClassifier(hidden_layer_sizes=[10, 10], alpha=1.0,
                    max_iter=1000, random_state=0).fit(Xs_train, y_train)
```

| Knob | Effect |
|---|---|
| `hidden_layer_sizes` | Width and depth: capacity |
| `alpha` | L2 penalty on weights |
| `activation` | `relu` (default) or `tanh` |
| `random_state` | Different seeds give visibly different boundaries on small data |

The tuning recipe from M&G: first build a network big enough to overfit, then shrink it or raise `alpha` until test performance is best. Scaling to mean 0 and variance 1 is required. Neural networks need more data, more tuning and more care than the other models here; for tabular data, gradient-boosted trees usually win ([06](06-ensembles.md)). [07](../../02-deep-learning/notes/01-neural-networks-fundamentals.md) builds them from scratch.

---

## Uncertainty estimates

Most classifiers can say *how sure* they are, not only which class:

| Method | Range | Meaning |
|---|---|---|
| `decision_function(X)` | Any real number; sign = class (binary) | Margin from the boundary; scale is model-specific |
| `predict_proba(X)` | [0, 1], rows sum to 1 | Estimated class probabilities |

```python
gbrt = GradientBoostingClassifier(random_state=0).fit(X_train, y_train_named)
gbrt.decision_function(X_test)[:6]   # e.g. [ 4.14 -1.68 -3.95 -3.62  4.29  3.66]
gbrt.predict_proba(X_test)[:6]       # probability of each class in classes_ order
gbrt.classes_[(gbrt.decision_function(X_test) > 0).astype(int)]  # == gbrt.predict(X_test)
```

A probability is only as good as the model's **calibration**: an overfit model reports 1.0 on points it gets wrong. You need these scores to move the decision threshold, which [04](04-model-evaluation.md#threshold-precision-recall-and-roc) does.

---

## Which model, when

![Decision boundaries of ten classifiers on three toy datasets](../../sources/images/mueller-guido-classifier-comparison.png)
*Image source: Müller & Guido, Introduction to Machine Learning with Python, companion repo `images/` (after scikit-learn's classifier comparison)*

| Model | Knob | Scale features? | Good for | Avoid when |
|---|---|---|---|---|
| kNN | `n_neighbors` | Yes | Small data, baseline, explanation by example | Many features, large n |
| Linear | `alpha` / `C` | Yes (for solvers and penalty) | High-dimensional, sparse, large data | Low-dim non-linear structure |
| Naive Bayes | `alpha` | No | Very fast text baselines | When accuracy matters most |
| Decision tree | `max_depth` | No | Explaining a model to people | Accuracy (use an ensemble) |
| Random forest | `max_features` | No | Strong default for tabular | Very sparse high-dim data |
| Gradient boosting | `learning_rate`, `n_estimators`, `max_depth` | No | Best tabular accuracy | You can't afford tuning |
| Kernel SVM | `C`, `gamma` | Yes | Medium data, similar-scale features | Large n |
| MLP | layers, `alpha` | Yes | Large data, time to tune | Small tabular data |

M&G's advice when faced with a new dataset: start with a simple model (linear, naive Bayes or kNN) to learn what the data is like, then move to random forests, gradient boosting, SVMs or neural networks.

---

## The same models, from scratch: Ng's exercises

Your own Coursera work implements the maths that scikit-learn hides. Each is the counterpart of a section above.

| Exercise | Implements | Key function |
|---|---|---|
| ex1 | Linear regression, one and many variables; batch gradient descent; feature normalisation; the normal equation | `computeCost`, `descendGradient`, `normEqtn` |
| ex2 | Logistic regression; regularised logistic regression on polynomial features (`mapFeature` to degree 6); decision boundary | `computeCost`, `optimizeTheta` (via `scipy.optimize`) |
| ex3 | Vectorised one-vs-all logistic regression on 5,000 handwritten digits; feed-forward with given NN weights | `predictOneVsAll`, `propagateForward` |
| ex4 | NN training: backpropagation, gradient checking, random initialisation | Taken up in [07](../../02-deep-learning/notes/01-neural-networks-fundamentals.md) |
| ex6 | Gaussian-kernel SVM; spam classifier | See [above](#kernelized-support-vector-machines) |

The core of ex1 and ex2, vectorised:

```python
import numpy as np
from scipy.special import expit   # sigmoid

def h_linear(theta, X):           # X has a leading column of ones
    return X @ theta

def cost_linear(theta, X, y):
    m = len(y)
    return ((h_linear(theta, X) - y) ** 2).sum() / (2 * m)

def gradient_descent(X, y, theta, alpha=0.01, iters=1500):
    m = len(y)
    for _ in range(iters):
        theta = theta - (alpha / m) * X.T @ (h_linear(theta, X) - y)   # simultaneous update
    return theta

def normal_equation(X, y):        # closed form, no learning rate, O(n^3) in features
    return np.linalg.pinv(X.T @ X) @ X.T @ y

def cost_logistic(theta, X, y, lam=0.0):
    m = len(y)
    h = expit(X @ theta)
    reg = lam / (2 * m) * (theta[1:] ** 2).sum()                       # never penalise the bias
    return -(y @ np.log(h) + (1 - y) @ np.log(1 - h)) / m + reg
```

Three things these make concrete that the library hides: gradient descent diverges if the learning rate is too high (plot $J$ per iteration, ex1); features on different scales slow it badly (normalise first); and the regularisation term skips the bias weight.

---

## Practice

| Notebook | Covers | Runs |
|---|---|---|
| [`02-supervised-learning.ipynb`](../practice/intro-to-ml-in-python/02-supervised-learning.ipynb) | Everything above except the Ng section | Offline; `scikit-learn>=1.4`, local `mglearn`; `graphviz` for tree plots |
| [`ex1`](../practice/ng-machine-learning/ex1/ex1.ipynb), [`ex2`](../practice/ng-machine-learning/ex2/ex2.ipynb), [`ex3`](../practice/ng-machine-learning/ex3/ex3.ipynb), [`ex6`](../practice/ng-machine-learning/ex6/ex6.ipynb) | From-scratch linear/logistic regression, one-vs-all, SVMs, spam | Legacy: Python 2.7 kernels (`print` statements); ex3 uses `scipy.misc.toimage`, removed in SciPy 1.2. Data in each `data/` folder |

---

→ Next: [03-feature-engineering-and-pipelines.md](03-feature-engineering-and-pipelines.md) — the features matter more than the model, and pipelines keep preprocessing honest.
