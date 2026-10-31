---
origin: curated
sources:
  - https://www.statlearning.com/
  - https://github.com/amueller/introduction_to_ml_with_python
  - ../practice/Intro to Machine Learning in Python/01-introduction.ipynb
  - ../sources/mueller-guido-introduction-to-ml-with-python.pdf
confidence: high
cleaned: 2026-10-31
---
# 1 — Statistical Foundations

> The vocabulary every later note assumes: what a model is estimating, why it fails on new data, how to split data so you can tell, and the four-line scikit-learn loop that every classical model shares.

---

## Why a readings layer comes first

Classical machine learning is applied statistics with a compute budget. Every technique in notes 02–06 answers the same question, *how do I estimate a function from samples so that it holds on samples I haven't seen?*, and every failure is a failure to answer it: overfitting, leakage, a metric that rewards the wrong thing, a test set you peeked at.

This layer is mostly reading. The code starts in [02](02-supervised-learning.md). What this note does is fix the terms, show the one API shape you will use everywhere, and say which book chapter to read alongside which later note.

> **A model is an estimate of $f$ in $y = f(x) + \varepsilon$. Learning is choosing $\hat f$ from a family of functions. Generalisation is how close $\hat f$ stays to $f$ on new $x$.**

The rest of this note is about that last sentence.

---

## The problem setting

| Term | Meaning | Where it shows up |
|---|---|---|
| Sample, data point | One row $x_i$ with features $x_{i1..p}$ | Everywhere |
| Feature | One column; numeric, categorical, text, image | [03](03-feature-engineering-and-pipelines.md), [08](08-text-representation.md) |
| Target, label | The $y$ you want to predict | Supervised learning only |
| Supervised | Learn $x \to y$ from labelled pairs | [02](02-supervised-learning.md), [06](06-ensembles.md) |
| Unsupervised | Find structure in $x$ alone | [05](05-unsupervised-learning.md) |
| Classification | $y$ is a class from a finite set | [02](02-supervised-learning.md), [09](09-text-classification.md) |
| Regression | $y$ is a real number | [02](02-supervised-learning.md) |
| Generalisation | Performance on data not used to fit | [04](04-model-evaluation.md) |

Two questions come before any model, and Müller & Guido open with them (*Introduction to ML with Python*, ch. 1, "Knowing your task and knowing your data"):

- What question am I answering, and is the data I have able to answer it?
- How will I measure success, and what does a wrong answer cost?

Most failed projects fail here, not in model choice.

---

## Bias, variance and model complexity

The expected squared error of a regression model at a point decomposes into three parts:

$$
\mathbb{E}\big[(y - \hat f(x))^2\big] = \underbrace{\big(\mathbb{E}[\hat f(x)] - f(x)\big)^2}_{\text{bias}^2} + \underbrace{\mathrm{Var}\big[\hat f(x)\big]}_{\text{variance}} + \underbrace{\sigma^2_\varepsilon}_{\text{irreducible}}
$$

- **Bias** is error from the model family being too simple: a straight line fit to a curve.
- **Variance** is error from the fit depending too much on which samples you happened to draw: a degree-15 polynomial through 20 points.
- **Irreducible error** is the noise in $y$ itself. No model removes it.

Raising model complexity trades bias for variance. The test-error curve is U-shaped: falls while bias drops, rises once variance dominates. The sweet spot is the model you want.

![Training and test accuracy against model complexity: underfitting on the left, overfitting on the right, the sweet spot in between](../sources/images/mueller-guido-overfitting-underfitting-cartoon.png)
*Image source: Müller & Guido, Introduction to Machine Learning with Python, ch. 2 (companion repo `images/`)*

| Symptom | Training score | Test score | Diagnosis | Fix |
|---|---|---|---|---|
| Underfitting | Low | Low, close to train | High bias | More features, more flexible model, less regularisation |
| Overfitting | High | Much lower | High variance | More data, simpler model, more regularisation, early stopping |
| Good fit | High | Close to train | — | Stop tuning; check the test set once |

**Complexity relative to data size.** The right complexity depends on how much data you have: more varied data supports a more complex model without overfitting (*Introduction to ML with Python*, ch. 2, "Relation of model complexity to dataset size"). Collecting more data is often a better fix than a cleverer model. Ng's ex5 makes this measurable with learning curves ([04](04-model-evaluation.md#learning-curves-and-bias-variance-diagnosis)).

**Regularisation** is the general name for any constraint that pulls the fit toward simplicity: an L2 penalty on weights (ridge), an L1 penalty (lasso, which also zeros features), a maximum tree depth, a minimum number of neighbours. Every model in [02](02-supervised-learning.md) has one main complexity knob, and its strengths-and-weaknesses table names it.

---

## Probability as ML uses it

You need far less probability theory to *use* these models than the textbooks cover, but four ideas recur:

| Idea | Used in | One line |
|---|---|---|
| Likelihood | Logistic regression, naive Bayes, language models ([16](16-makemore.md)) | How probable the observed data is under the model's parameters; training maximises it |
| Negative log-likelihood | Cross-entropy loss everywhere, from [02](02-supervised-learning.md) to [17](17-nanogpt.md) | $-\frac1n \sum \log p_\theta(y_i \mid x_i)$; minimising it is maximum likelihood |
| Gaussian | Anomaly detection ([05](05-unsupervised-learning.md)), weight initialisation ([16](16-makemore.md)) | Mean and variance describe it fully; sums of many small effects tend toward it |
| Conditional independence | Naive Bayes ([02](02-supervised-learning.md), [09](09-text-classification.md)) | Assume features are independent given the class; wrong, but the classifier is often still good |

The Bayesian reading of the same models (priors as regularisers, posteriors instead of point estimates, MCMC) lives in the data-analytics subject: [`../../data-analytics/notes/`](../../data-analytics/notes/). Ridge regression is the MAP estimate under a Gaussian prior on the weights; lasso is the MAP estimate under a Laplace prior. That is the bridge between the two subjects.

---

## Train, validation, test

The one discipline that separates a real result from a fooled one:

> **The test set is touched once, at the end. Everything you tune is tuned on data the test set never saw.**

| Split | Used for | Typical share |
|---|---|---|
| Training | Fitting parameters | 60–80% |
| Validation (or CV folds) | Choosing hyperparameters, features, model family | 10–20%, or k-fold over the training part |
| Test | One final estimate of generalisation | 10–20% |

`train_test_split` shuffles and holds out 25% by default. Fix `random_state` so the split is reproducible, and pass `stratify=y` for classification so the class balance matches.

Two ways to break this, both covered in [04](04-model-evaluation.md):

- **Tuning on the test set**: choosing $C$ for an SVM by test score turns the test set into a validation set, and the reported score is optimistic.
- **Leakage**: fitting a scaler or feature selector on all the data before splitting. The model has then seen statistics of the test rows ([03](03-feature-engineering-and-pipelines.md#leakage-and-why-pipelines-exist)).

---

## The scikit-learn API in four lines

Müller & Guido's first application, classifying iris species with k-nearest neighbours, shows the shape every estimator shares (*Introduction to ML with Python*, ch. 1, "A first application").

![Iris flower with petal and sepal labelled](../sources/images/mueller-guido-iris-petal-sepal.png)
*Image source: Müller & Guido, Introduction to Machine Learning with Python, ch. 1*

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

iris = load_iris()                      # a Bunch: .data (150, 4), .target (150,), .feature_names
X_train, X_test, y_train, y_test = train_test_split(
    iris["data"], iris["target"], random_state=0)   # 112 train, 38 test

knn = KNeighborsClassifier(n_neighbors=1)  # 1. instantiate with hyperparameters
knn.fit(X_train, y_train)                  # 2. fit on training data (learned state ends in _)
y_pred = knn.predict(X_test)               # 3. predict
print(knn.score(X_test, y_test))           # 4. score: accuracy for classifiers, R^2 for regressors -> 0.97
```

Before fitting, **look at the data**. A scatter matrix (`pd.plotting.scatter_matrix(df, c=y_train)`) shows whether the classes separate on the raw features at all, and catches unit errors and outliers before they cost you a day.

| Method | On | Returns |
|---|---|---|
| `fit(X, y)` | Every estimator | `self`, with learned attributes ending in `_` (`coef_`, `cluster_centers_`) |
| `predict(X)` | Supervised models, some clusterers | Labels or values |
| `predict_proba(X)` / `decision_function(X)` | Most classifiers | Class probabilities / signed margins ([02](02-supervised-learning.md#uncertainty-estimates)) |
| `transform(X)` | Preprocessors, PCA, vectorisers | A new feature matrix |
| `fit_transform(X)` | Transformers | Fit then transform, sometimes faster |
| `score(X, y)` | Supervised models | Default metric |

![scikit-learn API summary: which estimators have fit, predict, transform, score](../sources/images/mueller-guido-api-table.png)
*Image source: Müller & Guido, Introduction to Machine Learning with Python, ch. 8*

Because every estimator has this shape, you can chain them ([03 — pipelines](03-feature-engineering-and-pipelines.md)) and search over them ([04 — grid search](04-model-evaluation.md)). Writing your own estimator means subclassing `BaseEstimator` (and `TransformerMixin` or `ClassifierMixin`), taking every hyperparameter in `__init__` without logic, and returning `self` from `fit` (*Introduction to ML with Python*, ch. 8).

---

## The shape of this subject

The classical-ML part is a tree, not a line: after supervised learning you can go to evaluation or to unsupervised learning in either order.

```
01 Statistical foundations (readings)
 ├── 02 Supervised ── 03 Features and pipelines ── 04 Evaluation
 ├── 05 Unsupervised            (independent of 04)
 ├── 06 Ensembles               (after 02)
 └── 07 Neural networks         (after 02)
       ├── 08–14 NLP arc        (text as features, then neural text models)
       └── 15–17 micrograd → makemore → nanoGPT   (→ generative-ai 01)
```

| Layer | Notes | Depends on |
|---|---|---|
| Foundations | 01 | — |
| Supervised | 02, 03 | 01 |
| Evaluation | 04 | 02 |
| Unsupervised | 05 | 01 (02 helps) |
| Ensembles | 06 | 02 |
| Neural networks | 07 | 02 |
| NLP | 08–14 | 02, 04; 07 for 13–14 |
| From scratch to GPT | 15–17 | 07 |
| Bayesian methods | [data-analytics](../../data-analytics/notes/) | 01 |

---

## Reading map

These books live in data-analytics' [`sources/`](../../data-analytics/sources/) (shared with the stats course), apart from Müller & Guido which is [here](../sources/mueller-guido-introduction-to-ml-with-python.pdf).

| Book | Read with | Focus |
|---|---|---|
| James, Witten, Hastie, Tibshirani, Taylor, *An Introduction to Statistical Learning* (Python ed.) | ch. 2 → 01; ch. 3–4 → 02; ch. 5 → 04; ch. 6 → 03; ch. 8 → 06; ch. 10 → 07; ch. 12 → 05 | The canonical theory text; free at [statlearning.com](https://www.statlearning.com/) |
| Müller & Guido, *Introduction to Machine Learning with Python* | ch. 1–8 → 01–06, 08 | The code-first companion; notebooks in [practice](../practice/Intro%20to%20Machine%20Learning%20in%20Python/) |
| Bruce, Bruce & Gedeck, *Practical Statistics for Data Scientists* | ch. 1–3 before 04 | Working statistics, chapter-level |
| Reinhart, *Statistics Done Wrong* | Before reading any metric in 04 | Inference pitfalls |
| Efron & Hastie, *Computer Age Statistical Inference* | After 06 | Frequentist-to-Bayes bridge, bootstrap, boosting theory |
| Downey, *Think Bayes*; McElreath, *Statistical Rethinking* | With the data-analytics Bayesian notes | Bayesian intuition |

Return to these after each later note: a technique you have just used makes the chapter that explains it readable.

---

## Practice

- [`01-introduction.ipynb`](../practice/Intro%20to%20Machine%20Learning%20in%20Python/01-introduction.ipynb) — NumPy, SciPy sparse matrices, pandas, the iris kNN. Runs offline; needs `scikit-learn>=1.4` and the local `mglearn` package (run from the notebook's folder).
- [`practice/udacity_mlnd_python_practice.ipynb`](../practice/udacity_mlnd_python_practice.ipynb) — own Udacity MLND Connect Intensive exercise: pandas and seaborn plots (histogram, scatter, bar) of the iris data, the "look at your data" step above. Needs `seaborn` and a `data/iris.txt` that is not in the repo (substitute `sns.load_dataset("iris")`).

---

→ Next: [02-supervised-learning.md](02-supervised-learning.md) — the model families, each with its complexity knob, strengths and failure mode.
