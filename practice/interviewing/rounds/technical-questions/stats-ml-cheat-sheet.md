# Probability, Statistics and ML Cheat Sheet

The formulas and comparisons a first-round screen on maths, probability, statistics and basic machine learning
expects from memory. Drill them in [stats-ml-bank.md](stats-ml-bank.md) (short answer and worked problems) and
sections L, M and N of [mcq-bank.md](mcq-bank.md). Each section names the note that carries the full treatment.

## 1. Distributions

| Distribution | Models | PMF or PDF | Mean | Variance |
|---|---|---|---|---|
| Bernoulli(p) | one yes/no trial | P(1) = p, P(0) = 1 − p | p | p(1 − p) |
| Binomial(n, p) | successes in n independent trials | C(n, k) p^k (1 − p)^(n − k) | np | np(1 − p) |
| Geometric(p) | trials up to the first success | (1 − p)^(k − 1) p | 1/p | (1 − p)/p² |
| Poisson(λ) | events in a fixed interval at a constant rate | e^(−λ) λ^k / k! | λ | λ |
| Exponential(λ) | waiting time between Poisson events | λ e^(−λx) | 1/λ | 1/λ² |
| Uniform(a, b) | equally likely on an interval | 1/(b − a) | (a + b)/2 | (b − a)²/12 |
| Normal(μ, σ²) | sums and averages of many small effects | bell curve | μ | σ² |

How they connect:

- A Binomial is a sum of n independent Bernoullis.
- Binomial → Poisson(np) when n is large and p is small.
- Binomial → Normal(np, np(1 − p)) when np and n(1 − p) are both at least about 10.
- Poisson(λ) → Normal(λ, λ) when λ is large.
- Geometric and Exponential are memoryless.
- Normal: 68% within 1σ, 95% within 1.96σ, 99.7% within 3σ. z = (x − μ)/σ.

Notes: [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md),
[distributions and sampling](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md).
Lab: [distributions_and_estimators.py](../../../../data-analytics/02-probability-and-statistics/practice/distributions_and_estimators.py).

## 2. Probability rules

| Rule | Formula |
|---|---|
| Complement | P(not A) = 1 − P(A). Use it for "at least one". |
| Addition | P(A or B) = P(A) + P(B) − P(A and B) |
| Conditional | P(A given B) = P(A and B) / P(B) |
| Independence | P(A and B) = P(A) P(B) |
| Total probability | P(B) = Σ P(B given Aᵢ) P(Aᵢ) |
| Bayes | P(A given B) = P(B given A) P(A) / P(B) |
| Linearity | E[aX + bY] = aE[X] + bE[Y], with or without independence |
| Variance | Var(X) = E[X²] − E[X]². Var(aX + b) = a²Var(X) |
| Variance of a sum | Var(X + Y) = Var(X) + Var(Y) + 2Cov(X, Y) |
| Total expectation | E[X] = E[E[X given Y]] |
| Counting | n! orderings. C(n, k) = n! / (k!(n − k)!) ways to choose k of n |

Problem-solving moves, in the order to try them:

1. Define the event or random variable out loud before computing.
2. "At least one": compute the complement.
3. A rare condition and a test: Bayes with counts out of 10,000.
4. "Expected number of trials until": condition on the first step and write one equation per state.
5. A sum of pieces: linearity of expectation, even when the pieces are dependent.
6. Sanity-check the answer against an extreme case (p = 0, p = 1, n = 1).

Lab: [probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py).

## 3. Sampling and estimation

- **Law of Large Numbers**: the sample mean converges to μ.
- **Central Limit Theorem**: the sample mean is approximately Normal(μ, σ²/n) for large n. The raw data do not become Normal.
- **Standard error** of a mean: σ/√n. Of a proportion: √(p(1 − p)/n). Four times the data halves it.
- **95% confidence interval**: estimate ± 1.96 × standard error. 95% of intervals built this way cover the truth.
- **Bias** of an estimator: E[estimate] − truth. **MSE** = bias² + variance.
- **Unbiased**: right on average at this n. **Consistent**: converges to the truth as n grows.
- Sample variance: divide by n − 1 for unbiased. The divisor n is the maximum likelihood estimate and is biased low.
- **MLE**: Bernoulli → sample proportion. Poisson → sample mean. Normal → sample mean and the divisor-n variance.
- Bias in data collection (selection, survivorship, non-response, measurement, confounding) is not reduced by more data.

Note: [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md).

## 4. Hypothesis testing

| Term | Meaning |
|---|---|
| p-value | P(data at least this extreme, given H0 is true). Not P(H0 is true). |
| α | Type I error rate: rejecting a true H0. Usually 0.05. |
| β | Type II error rate: missing a real effect. |
| Power | 1 − β. Usually planned at 0.8. Rises with n, effect size and α; falls with variance. |
| Two-sided z | 1.645 for 90%, 1.96 for 95%, 2.576 for 99% |

| Comparing | Test |
|---|---|
| Two means | Welch's t-test |
| Two proportions, large n | Two-proportion z-test |
| Counts across categories | Chi-square |
| Before and after on the same units | Paired t-test |
| Skewed or ordinal, small n | Mann-Whitney or bootstrap |
| Three or more means | ANOVA, then pairwise with a correction |

Multiple comparisons: with m tests at α the chance of at least one false positive is 1 − (1 − α)^m, 64% for 20 tests.
Bonferroni uses α/m. Benjamini-Hochberg controls the false discovery rate.

Note: [hypothesis testing](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md).

## 5. A/B testing

The steps: hypothesis and primary metric → guardrails → randomisation unit → α, power, minimum detectable effect →
sample size and duration → randomise → check the split → run to the planned size → decide from the interval.

- **Two-proportion z-test**: z = (p_t − p_c) / √(p̄(1 − p̄)(1/n_c + 1/n_t)), with p̄ the pooled rate.
- **Sample size per arm** (α = 0.05 two-sided, power 0.8): n ≈ 16 p(1 − p) / δ². Half the effect needs four times the users.
- **Worked numbers**: 10.0% against 11.0% with 10,000 per arm gives z = 2.31, p = 0.021, interval 0.15 to 1.85 points.
  Detecting that 1 point lift at 80% power needs about 14,700 per arm.

| Pitfall | What happens | Fix |
|---|---|---|
| Peeking | False positives rise from 5% to about 25% with 20 looks | Fixed horizon, or a sequential design |
| Sample ratio mismatch | The split differs from the design; arms are not comparable | Chi-square on the counts; fix before reading metrics |
| Many metrics or segments | Some will be significant by chance | One primary metric; correct the rest |
| Unit mismatch | Sessions analysed, users randomised: standard errors too small | Analyse by user, delta method or user-level bootstrap |
| Novelty or primacy | The effect changes as users adapt | Run longer; compare new and existing users |
| Interference | Treated users affect control users | Cluster or switchback randomisation |
| Underpowered test | "Not significant" is read as "no effect" | Read the interval against the minimum effect |

Notes: [A/B testing](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md),
[experimentation at scale](../../../../data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md).
Lab: [ab_test_from_scratch.py](../../../../data-analytics/03-experimentation-and-causality/practice/ab_test_from_scratch.py).

## 6. Machine learning models

| Model | Strengths | Weaknesses | Scale features? |
|---|---|---|---|
| Linear regression | Fast, interpretable, strong baseline | Linear and additive only; sensitive to outliers and correlated features | For regularised versions |
| Logistic regression | Calibrated probabilities, interpretable odds, fast | Linear boundary; needs hand-built interactions | For regularised versions |
| Naive Bayes | Very fast, little data needed, good on text | Independence assumption; poor probabilities | No |
| k-nearest neighbours | No training, any boundary shape | Slow prediction; fails in high dimensions | Yes |
| Decision tree | Readable rules, non-linear, mixed feature types | High variance, overfits, cannot extrapolate | No |
| Random forest | Robust, little tuning, lowers variance | Larger and slower, less interpretable | No |
| Gradient boosting | Usually the most accurate on tabular data | Needs tuning; overfits without early stopping | No |
| Support vector machine | Strong on small data with many features; kernels | Slow on large data; no probabilities; needs tuning | Yes |
| Neural network | Learns features from images, text, audio | Needs much data and compute; hard to interpret | Yes |
| k-means | Fast, simple clustering | Choose k; round clusters only; sensitive to start and outliers | Yes |

- **Bias-variance**: test error = bias² + variance + noise. High bias: linear models, Naive Bayes. High variance: deep trees, small-k nearest neighbours.
- **Bagging** (random forest) averages independent trees and lowers variance. **Boosting** adds trees in sequence and lowers bias.
- **Regularisation**: L2 shrinks all coefficients. L1 sets some to zero and so selects features.
- **Overfitting**: training error far below validation error. Underfitting: both high.
- **Metrics**: precision = TP/(TP + FP). Recall = TP/(TP + FN). F1 is their harmonic mean. ROC-AUC is P(a random positive outranks a random negative). Use PR-AUC when positives are rare.
- **Likelihood link**: least squares is MLE under Normal errors, logistic regression under Bernoulli, Poisson regression for counts.
- **Leakage**: a feature unavailable at prediction time, or preprocessing fitted before the split.

Notes: [statistical foundations](../../../../data-science/01-classical-ml/notes/01-statistical-foundations.md),
[supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md),
[ensembles](../../../../data-science/01-classical-ml/notes/06-ensembles.md),
[model evaluation](../../../../data-science/01-classical-ml/notes/04-model-evaluation.md).
Labs: [overfit_curve.py](../../../../data-science/01-classical-ml/practice/overfit_curve.py),
[trees_vs_rounds.py](../../../../data-science/01-classical-ml/practice/trees_vs_rounds.py).
