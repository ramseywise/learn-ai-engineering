---
origin: vendored snapshot, Intro to Machine Learning in Python (kept as practice), plus own coursework (Ng ML ex1 to ex4, ex6)
sources:
  - https://github.com/amueller/introduction_to_ml_with_python
  - ../practice/intro-to-ml-in-python/02-supervised-learning.ipynb
  - https://www.coursera.org/specializations/machine-learning-introduction
  - ../practice/ng-machine-learning/ex1/ex1.ipynb
  - ../practice/ng-machine-learning/ex2/ex2.ipynb
  - ../practice/ng-machine-learning/ex3/ex3.ipynb
  - ../practice/ng-machine-learning/ex6/ex6.ipynb
  - ../../sources/cortes-1995-support-vector-networks.pdf
  - ../../sources/pedregosa-2012-scikit-learn.pdf
confidence: high
cleaned: 2026-11-01
---
# Supervised Learning

> You have a table and a target. Which model do you try first, and how do you know whether it is too simple or too flexible? This note walks the classical families (nearest neighbours, linear models, naive Bayes, trees, kernel SVMs, small neural networks), each with the one knob that controls its complexity, what it is good at and how it fails, plus the from-scratch versions from Ng's exercises.

Blocks run top to bottom from this `notes/` folder, on the breast-cancer data that ships with scikit-learn, so the numbers below are this split's. Figures attributed to M&G come from the book's own examples.

---

## The two tasks

| | Classification | Regression |
|---|---|---|
| Target | A class label from a fixed set | A continuous number |
| Example (M&G ch. 2) | Breast-cancer benign/malignant; `make_forge` two-class toy | House prices (M&G's Boston data, removed from scikit-learn 1.2); `make_wave` 1-D toy |
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
    print(k, round(clf.score(X_train, y_train), 3), round(clf.score(X_test, y_test), 3))
```

```text
1 1.0 0.902
2 0.977 0.888
3 0.958 0.923
4 0.955 0.923
5 0.948 0.923
6 0.946 0.937
7 0.944 0.93
8 0.941 0.93
9 0.934 0.916
10 0.939 0.916
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

M&G show the effect on their extended Boston data (104 features): OLS scores 0.95 on train and 0.61 on test; ridge at `alpha=1` gets 0.89 / 0.75; lasso at `alpha=0.01` uses 33 of the 104 features and generalises about as well. That dataset has since been removed from scikit-learn, so here is the same experiment on the diabetes data, expanded to squares and products of its features so that OLS has room to overfit:

```python
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures

d = load_diabetes()
Xd = PolynomialFeatures(degree=3, include_bias=False).fit_transform(d.data)
Xd_train, Xd_test, yd_train, yd_test = train_test_split(Xd, d.target, random_state=0)
print("features:", Xd.shape[1], "rows in train:", Xd_train.shape[0])

for name, model in [("OLS", LinearRegression()),
                    ("Ridge a=0.1", Ridge(alpha=0.1)),
                    ("Lasso a=0.1", Lasso(alpha=0.1, max_iter=100_000))]:
    model.fit(Xd_train, yd_train)
    print(f"{name:12} train {model.score(Xd_train, yd_train):.2f}  test {model.score(Xd_test, yd_test):.2f}"
          f"  nonzero {(np.abs(model.coef_) > 1e-8).sum()}")
```

```text
features: 285 rows in train: 331
OLS          train 0.90  test -9.32  nonzero 285
Ridge a=0.1  train 0.55  test 0.37  nonzero 285
Lasso a=0.1  train 0.55  test 0.36  nonzero 7
```

With 285 features and 331 rows OLS memorises the training set, and its test R² of -9.32 is far worse than predicting the mean. Both penalties rescue it at the cost of train score. Ridge keeps all 285 weights small; lasso matches it with 7. That is why you try lasso when you suspect only a few features matter.

The penalties have a pedigree worth citing: the L1 penalty and its property of setting weights exactly to zero come from the lasso paper ([doi:10.1111/j.2517-6161.1996.tb02080.x](https://doi.org/10.1111/j.2517-6161.1996.tb02080.x), Tibshirani, JRSS-B 1996).

**Ridge vs lasso.** Default to ridge. Use lasso when you expect only a few features to matter, or need a model you can read.

**Learning curves for ridge** show the data-size effect from [01](01-statistical-foundations.md): with enough data, regularisation matters less and OLS catches up.

### Classification: logistic regression and linear SVM

Both draw a hyperplane. They differ in loss (log-loss vs hinge), not in the shape of the boundary.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

# sklearn >= 1.4: lbfgs needs more iterations on unscaled data (fix applied in this repo's copy)
logreg = LogisticRegression(C=1, max_iter=10000).fit(X_train, y_train)
svm = LinearSVC(C=1, max_iter=20000).fit(X_train, y_train)
print("logreg", round(logreg.score(X_test, y_test), 3), "linear svm", round(svm.score(X_test, y_test), 3))
```

```text
logreg 0.944 linear svm 0.944
```

The knob is **`C`, the inverse of regularisation strength**: high `C` fits each training point harder (complex); low `C` keeps weights small (simple). Note the inversion against `alpha` above. `penalty="l1"` gives sparse coefficients, as lasso does.

**Multiclass.** Linear classifiers are binary by nature. One-vs-rest trains one classifier per class and predicts the class with the highest score. `LogisticRegression` uses a true multinomial (softmax) loss by default.

| | |
|---|---|
| Knob | `alpha` (regression), `C` (classification) |
| Good at | Very many features; sparse data (text, [NLP text classification](../../03-nlp/notes/02-text-classification.md)); huge datasets (`SGDClassifier`, `solver="sag"`); fast to train and predict; coefficients readable |
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

Knob: `alpha` (additive smoothing: pretends every feature was seen `alpha` extra times in every class). Naive Bayes is the classic fast text baseline ([NLP text classification](../../03-nlp/notes/02-text-classification.md)); usually slightly worse than a linear model, trained much faster.

---

## Decision trees

A tree asks a sequence of if/else questions ("is feature 3 ≤ 0.8?"), each chosen to make the resulting groups as pure as possible. A leaf predicts the majority class (or mean value) of its training points.

```python
from sklearn.tree import DecisionTreeClassifier

full = DecisionTreeClassifier(random_state=0).fit(X_train, y_train)
tree = DecisionTreeClassifier(max_depth=4, random_state=0).fit(X_train, y_train)
print("unpruned ", round(full.score(X_train, y_train), 3), round(full.score(X_test, y_test), 3))
print("max_depth", round(tree.score(X_train, y_train), 3), round(tree.score(X_test, y_test), 3))
print("features used:", (tree.feature_importances_ > 0).sum(), "of", X_train.shape[1])  # zero means unused, not "unimportant"
```

```text
unpruned  1.0 0.895
max_depth 0.988 0.902
features used: 10 of 30
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

Only the training points on the margin, the **support vectors**, define the boundary. The soft-margin formulation, where `C` prices each margin violation so that non-separable data still has a solution, is the contribution of the original paper, which combined ten degree-4 polynomial classifiers to reach 1.1% test error on the NIST digit benchmark ([doi:10.1007/bf00994018](https://doi.org/10.1007/bf00994018), Cortes and Vapnik, Machine Learning 1995).

```python
from sklearn.svm import SVC
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler().fit(X_train)           # fit on train only (see 03)
svc = SVC(kernel="rbf", C=1000, gamma="scale").fit(scaler.transform(X_train), y_train)
raw = SVC(kernel="rbf", C=1000, gamma=1.0).fit(X_train, y_train)   # unscaled: distances are dominated by the largest-valued features
print("unscaled", round(raw.score(X_test, y_test), 3))
print("scaled  ", round(svc.score(scaler.transform(X_test), y_test), 3))
```

```text
unscaled 0.629
scaled   0.972
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

Ng's ex6 implements the Gaussian kernel by hand and uses `sklearn.svm.SVC` on three 2-D datasets, then builds a **spam classifier**: email preprocessing (lower-case, strip HTML, normalise URLs, numbers and addresses, Porter stemming), a 1,899-word vocabulary, binary word-presence features, a linear SVM. That is the bag-of-words pipeline of [NLP text representation](../../03-nlp/notes/01-text-representation.md) written out by hand.

```python
# Ng ex6: the Gaussian kernel, from scratch
def gauss_kernel(x1, x2, sigma):
    return np.exp(-np.sum((x1 - x2) ** 2) / (2.0 * sigma ** 2))   # gamma = 1 / (2 sigma^2)

print(round(gauss_kernel(np.array([1., 2, 1]), np.array([0., 4, -1]), 2.0), 6))
```

```text
0.324652
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
print(round(mlp.score(StandardScaler().fit(X_train).transform(X_test), y_test), 3))
```

```text
0.951
```

| Knob | Effect |
|---|---|
| `hidden_layer_sizes` | Width and depth: capacity |
| `alpha` | L2 penalty on weights |
| `activation` | `relu` (default) or `tanh` |
| `random_state` | Different seeds give visibly different boundaries on small data |

The tuning recipe from M&G: first build a network big enough to overfit, then shrink it or raise `alpha` until test performance is best. Scaling to mean 0 and variance 1 is required. Neural networks need more data, more tuning and more care than the other models here; for tabular data, gradient-boosted trees usually win ([06](06-ensembles.md)). [neural network basics](../../02-deep-learning/notes/01-neural-networks-fundamentals.md) builds them from scratch.

---

## Uncertainty estimates

Most classifiers can say *how sure* they are, not only which class:

| Method | Range | Meaning |
|---|---|---|
| `decision_function(X)` | Any real number; sign = class (binary) | Margin from the boundary; scale is model-specific |
| `predict_proba(X)` | [0, 1], rows sum to 1 | Estimated class probabilities |

```python
from sklearn.ensemble import GradientBoostingClassifier

y_train_named = cancer.target_names[y_train]         # labels as strings, to show classes_
gbrt = GradientBoostingClassifier(random_state=0).fit(X_train, y_train_named)
print(gbrt.classes_)
print(gbrt.decision_function(X_test)[:4].round(2))   # signed margin; positive means classes_[1]
print(gbrt.predict_proba(X_test)[:4].round(3))       # probability of each class in classes_ order
agree = gbrt.classes_[(gbrt.decision_function(X_test) > 0).astype(int)] == gbrt.predict(X_test)
print(agree.all())
```

```text
['benign' 'malignant']
[-8.69 -8.75 -8.32 -8.77]
[[1. 0.]
 [1. 0.]
 [1. 0.]
 [1. 0.]]
True
```

A probability is only as good as the model's **calibration**: an overfit model reports 1.0 on points it gets wrong. You need these scores to move the decision threshold, which [04](04-model-evaluation.md#threshold-precision-recall-and-roc) does, and [04](04-model-evaluation.md#calibration-is-a-08-really-80) shows how to check them. Niculescu-Mizil and Caruana compared ten learners' probabilities and found boosted trees and SVMs distort them in a sigmoid shape while logistic regression does not ([doi:10.1145/1102351.1102430](https://doi.org/10.1145/1102351.1102430), ICML 2005).

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
| Gradient boosting | `learning_rate`, `n_estimators`, `max_depth` | No | Best tabular accuracy ([07](07-boosting-in-practice.md)) | You can't afford tuning |
| Kernel SVM | `C`, `gamma` | Yes | Medium data, similar-scale features | Large n |
| MLP | layers, `alpha` | Yes | Large data, time to tune | Small tabular data |

M&G's advice when faced with a new dataset: start with a simple model (linear, naive Bayes or kNN) to learn what the data is like, then move to random forests, gradient boosting, SVMs or neural networks. All of them sit behind the same API, which is the reason a sweep across families costs a few lines ([arXiv:1201.0490](https://arxiv.org/abs/1201.0490), Pedregosa et al., JMLR 2011).

---

## The same models, from scratch: Ng's exercises

Your own Coursera work implements the maths that scikit-learn hides. Each is the counterpart of a section above.

| Exercise | Implements | Key function |
|---|---|---|
| ex1 | Linear regression, one and many variables; batch gradient descent; feature normalisation; the normal equation | `computeCost`, `descendGradient`, `normEqtn` |
| ex2 | Logistic regression; regularised logistic regression on polynomial features (`mapFeature` to degree 6); decision boundary | `computeCost`, `optimizeTheta` (via `scipy.optimize`) |
| ex3 | Vectorised one-vs-all logistic regression on 5,000 handwritten digits; feed-forward with given NN weights | `predictOneVsAll`, `propagateForward` |
| ex4 | NN training: backpropagation, gradient checking, random initialisation | Taken up in [neural network basics](../../02-deep-learning/notes/01-neural-networks-fundamentals.md) |
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

# Ng ex1: profit of a food truck against city population
data = np.loadtxt("../practice/ng-machine-learning/ex1/data/ex1data1.txt", delimiter=",")
X1 = np.c_[np.ones(len(data)), data[:, 0]]
y1 = data[:, 1]
print("cost at zero   ", round(cost_linear(np.zeros(2), X1, y1), 2))
print("grad descent   ", gradient_descent(X1, y1, np.zeros(2)).round(3))
print("normal equation", normal_equation(X1, y1).round(3))
```

```text
cost at zero    32.07
grad descent    [-3.63   1.166]
normal equation [-3.896  1.193]
```

After 1,500 iterations gradient descent has not quite reached the closed-form answer, so running longer closes the gap. Three things these make concrete that the library hides: gradient descent diverges if the learning rate is too high (plot $J$ per iteration, ex1); features on different scales slow it badly (normalise first); and the regularisation term skips the bias weight.

---

## Practice

| Notebook | Covers | Runs |
|---|---|---|
| [`02-supervised-learning.ipynb`](../practice/intro-to-ml-in-python/02-supervised-learning.ipynb) | Everything above except the Ng section | Offline; `scikit-learn>=1.4`, local `mglearn`; `graphviz` for tree plots |
| [`ex1`](../practice/ng-machine-learning/ex1/ex1.ipynb), [`ex2`](../practice/ng-machine-learning/ex2/ex2.ipynb), [`ex3`](../practice/ng-machine-learning/ex3/ex3.ipynb), [`ex6`](../practice/ng-machine-learning/ex6/ex6.ipynb) | From-scratch linear/logistic regression, one-vs-all, SVMs, spam | Legacy: Python 2.7 kernels (`print` statements); ex3 uses `scipy.misc.toimage`, removed in SciPy 1.2. Data in each `data/` folder |

---

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Unscaled features for a distance or margin model | kNN or SVC scores near the dummy rate, and scaling jumps it | Put a scaler in a pipeline ([03](03-feature-engineering-and-pipelines.md)) |
| Confusing `C` and `alpha` | Raising `C` makes the fit tighter, raising `alpha` makes it looser | Remember `C` is the inverse of regularisation strength |
| Reading coefficients as causes | A correlated feature flips sign between fits | Check stability across resamples; see [interpretability](08-model-interpretability.md) |
| A convergence warning ignored | Coefficients differ with solver or seed | Scale first, or raise `max_iter` until the warning goes |
| Trees on trending time data | Forecast flatlines at the last training value | Model the trend with a linear part, or difference the target |
| Trusting `predict_proba` from an overfit model | Probabilities of 1.0 on wrong answers | Check calibration ([04](04-model-evaluation.md#calibration-is-a-08-really-80)) |

## Try it

1. Sweep `C` over `[0.001, 0.01, 0.1, 1, 10, 100]` for `LogisticRegression` on the scaled breast-cancer split. Find where train and test scores part.
2. Fit `DecisionTreeClassifier` with `max_depth` from 1 to 10. Which depth does the test score peak at on this split?
3. Run `gradient_descent` on `X1, y1` with `alpha=0.03`. What happens to the cost, and why?
4. Extend `cost_logistic` to return its gradient and fit it on ex2's `data/ex2data1.txt` with `scipy.optimize.minimize`. Solutions are in [`ex2.ipynb`](../practice/ng-machine-learning/ex2/ex2.ipynb).

<details>
<summary>Answers</summary>

1. Very small `C` underfits, with both scores lower. From about `C=1` the train score reaches its ceiling while the test score flattens or drops, which is where more flexibility stops paying.
2. Print the sweep. The peak is usually at a small depth, and the unpruned tree is not the best one; the exact depth depends on the split, so rerun with a different `random_state` to see how unstable a single tree's choice is.
3. It diverges to infinity: the feature (city population in tens of thousands) has a large range, so a step of 0.03 overshoots and the cost grows every iteration. Normalising the feature first fixes it, which is the point ex1 makes.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What controls complexity in kNN, linear models, trees, RBF SVMs? | `n_neighbors`; `alpha` or `C`; `max_depth`; `C` with `gamma` |
| Ridge vs lasso? | Ridge shrinks all weights. Lasso sets some to exactly zero, so it selects features |
| Logistic regression vs linear SVM? | The same hyperplane shape with different losses: log-loss vs hinge. Logistic gives probabilities directly |
| Why do trees not need scaling? | Each split compares one feature to a threshold, so only the order of its values matters |
| Why can't trees or forests extrapolate? | Predictions are means of training leaves, so they never leave the training range |
| What is the kernel trick? | Computing inner products in an expanded feature space without building that space |
| What are support vectors? | The training points on or inside the margin, the only ones that define the boundary |
| Why is naive Bayes fast and often fine? | One pass of per-class statistics. Its independence assumption is wrong but the ranking is often good |
| Which model first on a new table? | A linear model or kNN to learn the data, then a forest or boosting |
| Gradient descent vs normal equation? | Iterative with a learning rate, vs closed form at about cubic cost in features |

## Next

[Feature engineering and pipelines](03-feature-engineering-and-pipelines.md): the features matter more than the model, and pipelines keep preprocessing honest.
