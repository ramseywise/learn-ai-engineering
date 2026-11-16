# Probability, Statistics and ML Screen: Worked Problems

Problems with a number for an answer, to do with a pen and a calculator. They are the third pass over the
topics of [stats-ml-bank.md](stats-ml-bank.md): recognise the answer in [mcq-bank.md](mcq-bank.md) (sections L
to S), recall it from the bank, then calculate it here. Each section letter matches the bank's.

**How to use**: write the setup before any arithmetic, because the interviewer grades the setup as much as the
number. Give the answer to the precision the question asks for, then read the **Working** even when you were
right. The **Deeper** line names the note that teaches the method.

| Section | Topic | Problems |
|---|---|---|
| P | Probability | 7 |
| S | Estimation and testing | 6 |
| A | A/B testing | 2 |
| M | Machine learning models | 7 |
| B and C | Bayesian inference and Markov chains | 3 |
| U and N | Unsupervised learning and neural networks | 5 |
| R | Retrieval and ranking | 5 |
| T and K | Time series and metrics | 3 |
| **Total** | | **38** |

---

## P. Probability

### W1. A condition affects 2% of people. A test catches 90% of cases and gives a false positive for 8% of healthy people. You test positive. What is the chance you have it, as a percentage to 1 decimal place?

**Answer:** 18.7

**Working:** Bayes' rule: P(condition | positive) = 0.02 × 0.90 / (0.02 × 0.90 + 0.98 × 0.08) = 0.018 / 0.0964 = 0.187. Of 10,000 people, 180 true positives and 784 false positives test positive, and 180 / 964 = 18.7%.

**Deeper:** [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md)

### W2. You roll a fair die and win its face value. You may reroll up to twice, but must keep the last roll you make. What is the game worth, to 2 decimal places?

**Answer:** 4.67

**Working:** Work backwards. The last roll is worth 3.5. With one reroll left, keep 4, 5 or 6: (4 + 5 + 6)/6 + (3/6) × 3.5 = 4.25. With two rerolls left, keep only a roll above 4.25, so 5 or 6: (5 + 6)/6 + (4/6) × 4.25 = 1.833 + 2.833 = 4.67.

**Deeper:** [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md)

### W3. A user converts with probability 0.3, independently of the others. What is the probability that exactly 2 of 5 users convert, to 3 decimal places?

**Answer:** 0.309

**Working:** Binomial: C(5, 2) × 0.3² × 0.7³ = 10 × 0.09 × 0.343 = 0.3087.

**Deeper:** [distributions and sampling](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md)

### W4. Support tickets arrive at an average of 4 an hour, independently. What is the probability of none in the next 30 minutes, to 3 decimal places?

**Answer:** 0.135

**Working:** The rate for 30 minutes is 4 × 0.5 = 2. Poisson: P(0) = e^(−2) = 0.1353.

**Deeper:** [distributions and sampling](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md)

### W5. Each email is opened with probability 0.05, independently. What is the probability that at least one of 10 emails is opened, to 3 decimal places?

**Answer:** 0.401

**Working:** Take the complement: 1 − P(none) = 1 − 0.95¹⁰ = 1 − 0.5987 = 0.4013.

**Deeper:** [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md)

### W6. X is Binomial with n = 400 and p = 0.2. What is its standard deviation?

**Answer:** 8

**Working:** Variance is np(1 − p) = 400 × 0.2 × 0.8 = 64, and the standard deviation is √64 = 8.

**Deeper:** [distributions and sampling](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md)

### W7. X has variance 4, Y has variance 9, and their correlation is 0.5. What is the variance of X + Y?

**Answer:** 19

**Working:** Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X, Y). The covariance is correlation × sd(X) × sd(Y) = 0.5 × 2 × 3 = 3, so the variance is 4 + 9 + 2 × 3 = 19.

**Deeper:** [probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md)

---

## S. Estimation and testing

### W8. A sample of 144 orders has a mean of 50 and a standard deviation of 12. What is the upper limit of the 95% confidence interval for the mean, using z = 1.96, to 2 decimal places?

**Answer:** 51.96

**Working:** The standard error is 12 / √144 = 1. The interval is 50 ± 1.96 × 1, so the upper limit is 51.96.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md)

### W9. 120 of 400 surveyed users say yes. What is the 95% margin of error on that proportion, using z = 1.96, to 3 decimal places?

**Answer:** 0.045

**Working:** The proportion is 0.30. Standard error: √(0.3 × 0.7 / 400) = √0.000525 = 0.0229. Margin: 1.96 × 0.0229 = 0.0449.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md)

### W10. A coin gives 540 heads in 1,000 flips. What is the z statistic for the test that the coin is fair, to 2 decimal places?

**Answer:** 2.53

**Working:** Under the null the standard error is √(0.5 × 0.5 / 1000) = 0.01581. z = (0.54 − 0.50) / 0.01581 = 2.53, beyond 1.96, so the result is significant at 5%.

**Deeper:** [hypothesis testing](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md)

### W11. 36 customers change their spend by a mean of 2.4, with a standard deviation of 6. What is the t statistic for the test that the mean change is zero?

**Answer:** 2.4

**Working:** The standard error is 6 / √36 = 1, so t = 2.4 / 1 = 2.4 with 35 degrees of freedom.

**Deeper:** [hypothesis testing](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md)

### W12. How many respondents does a survey need for a 95% margin of error of 3 percentage points on a proportion, in the worst case p = 0.5, using z = 1.96? Round up to a whole person.

**Answer:** 1068

**Tolerance:** 1

**Working:** n = z² p(1 − p) / margin² = 1.96² × 0.25 / 0.03² = 0.9604 / 0.0009 = 1,067.1, which rounds up to 1,068.

**Deeper:** [estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md)

### W13. You run 20 independent tests at a significance level of 0.05 and every null hypothesis is true. What is the probability of at least one false positive, to 3 decimal places?

**Answer:** 0.642

**Working:** 1 − P(no false positive) = 1 − 0.95²⁰ = 1 − 0.3585 = 0.6415. A Bonferroni correction would test each at 0.05 / 20 = 0.0025.

**Deeper:** [experimentation at scale](../../../../data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md)

---

## A. A/B testing

### W14. Control converts 200 of 2,000 users and treatment 250 of 2,000. What is the z statistic of the two-proportion test with a pooled standard error, to 2 decimal places?

**Answer:** 2.50

**Working:** Rates are 0.100 and 0.125, pooled 450 / 4,000 = 0.1125. Standard error: √(0.1125 × 0.8875 × (1/2000 + 1/2000)) = 0.00999. z = 0.025 / 0.00999 = 2.50, significant at 5%.

**Deeper:** [A/B testing](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md)

### W15. The baseline conversion is 20% and you want to detect an absolute lift of 2 points at 5% significance and 80% power. Using the rule of thumb n = 16 p(1 − p) / δ², how many users does each arm need?

**Answer:** 6400

**Working:** n = 16 × 0.2 × 0.8 / 0.02² = 2.56 / 0.0004 = 6,400 per arm, so 12,800 in total.

**Deeper:** [A/B testing](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md)

---

## M. Machine learning models

### W16. Fit a least-squares line to the points (1, 2), (2, 3), (3, 5) and (4, 6). What is the slope?

**Answer:** 1.4

**Working:** The means are x̄ = 2.5 and ȳ = 4. Sum of (x − x̄)(y − ȳ) = 3 + 0.5 + 0.5 + 3 = 7. Sum of (x − x̄)² = 2.25 + 0.25 + 0.25 + 2.25 = 5. Slope = 7 / 5 = 1.4.

**Deeper:** [regression and GLMs](../../../../data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md)

### W17. A regression has a residual sum of squares of 20 and a total sum of squares of 80. What is R²?

**Answer:** 0.75

**Working:** R² = 1 − SS_res / SS_tot = 1 − 20 / 80 = 0.75: the model explains 75% of the variance.

**Deeper:** [regression and GLMs](../../../../data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md)

### W18. A logistic regression has log-odds −2 + 0.5x. What probability does it predict at x = 6, to 3 decimal places?

**Answer:** 0.731

**Working:** The log-odds are −2 + 0.5 × 6 = 1. The probability is 1 / (1 + e^(−1)) = 1 / 1.3679 = 0.7311.

**Deeper:** [logistic regression](../../../../data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms.md)

### W19. A logistic regression coefficient is 0.4. By what factor do the odds multiply for a one-unit increase in that feature, to 2 decimal places?

**Answer:** 1.49

**Working:** A coefficient is a change in log-odds, so the odds multiply by e^0.4 = 1.4918.

**Deeper:** [logistic regression](../../../../data-analytics/02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms.md)

### W20. A classifier has 40 true positives, 10 false positives, 20 false negatives and 930 true negatives. What is its F1 score, to 3 decimal places?

**Answer:** 0.727

**Working:** Precision = 40 / 50 = 0.8. Recall = 40 / 60 = 0.667. F1 = 2 × 0.8 × 0.667 / (0.8 + 0.667) = 0.7273. Accuracy would be 97%, which hides the 20 missed positives.

**Deeper:** [thresholds, PR and ROC](../../../../data-science/01-classical-ml/notes/04b-thresholds-pr-roc-and-calibration.md)

### W21. A decision-tree node holds 30 positive and 10 negative examples. What is its Gini impurity?

**Answer:** 0.375

**Working:** Gini = 1 − (p₊² + p₋²) = 1 − (0.75² + 0.25²) = 1 − 0.625 = 0.375.

**Deeper:** [supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md)

### W22. You minimise f(w) = w² by gradient descent from w = 3 with a learning rate of 0.1. What is w after one step?

**Answer:** 2.4

**Working:** The gradient is 2w = 6. The update is w − rate × gradient = 3 − 0.1 × 6 = 2.4.

**Deeper:** [optimisation and regularisation](../../../../data-science/02-deep-learning/notes/02-optimisation-and-regularisation.md)

---

## B and C. Bayesian inference and Markov chains

### W23. Your prior on a conversion rate is Beta(2, 2). You then see 12 conversions and 8 non-conversions. What is the posterior mean, to 3 decimal places?

**Answer:** 0.583

**Working:** The Beta prior is conjugate to the Binomial: add successes to the first parameter and failures to the second, giving Beta(14, 10). Its mean is 14 / 24 = 0.5833. The data alone give 12 / 20 = 0.6, and the prior pulls that towards 0.5.

**Deeper:** [Bayesian inference](../../../../data-analytics/04-bayesian-analysis/notes/01-bayesian-inference.md)

### W24. A user is active or lapsed each month. An active user stays active with probability 0.9, and a lapsed user returns with probability 0.5. A user is active now. What is the probability they are active two months from now?

**Answer:** 0.86

**Working:** Sum over the middle month: active then active is 0.9 × 0.9 = 0.81, lapsed then back is 0.1 × 0.5 = 0.05. Total 0.86, which is the active-to-active entry of the transition matrix squared.

**Deeper:** [states and sequences](../../../../data-analytics/06-applied-analyses/notes/08-states-and-sequences.md)

### W25. A walker on the points 0 to 6 starts at 3 and moves one step left or right with equal chance. The walk stops at 0 or 6. How many steps do you expect?

**Answer:** 9

**Working:** Let t(k) be the expected steps from k, with t(0) = t(6) = 0 and t(k) = 1 + ½t(k − 1) + ½t(k + 1). The solution is t(k) = k(6 − k), so t(3) = 3 × 3 = 9.

**Deeper:** [states and sequences](../../../../data-analytics/06-applied-analyses/notes/08-states-and-sequences.md)

---

## U and N. Unsupervised learning and neural networks

### W26. A PCA on four standardised features gives eigenvalues 4, 2, 1 and 1. What percentage of the variance do the first two components explain?

**Answer:** 75

**Working:** Each eigenvalue is the variance along its component. The first two hold (4 + 2) / (4 + 2 + 1 + 1) = 6 / 8 = 75%.

**Deeper:** [unsupervised learning](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md)

### W27. A convolution with a 3 × 3 filter, stride 2 and padding 1 is applied to a 64 × 64 image. What is the width of the output?

**Answer:** 32

**Working:** Output size = floor((n + 2p − f) / s) + 1 = floor((64 + 2 − 3) / 2) + 1 = 31 + 1 = 32.

**Deeper:** [convolutional networks](../../../../data-science/02-deep-learning/notes/04-convolutional-networks.md)

### W28. A fully connected network has 100 inputs, one hidden layer of 50 units and 10 outputs, with a bias on every unit. How many parameters does it have?

**Answer:** 5560

**Working:** First layer: 100 × 50 weights + 50 biases = 5,050. Second layer: 50 × 10 weights + 10 biases = 510. Total 5,560.

**Deeper:** [neural network fundamentals](../../../../data-science/02-deep-learning/notes/01-neural-networks-fundamentals.md)

### W29. A classifier outputs the logits 2, 1 and 0. What probability does softmax give the first class, to 3 decimal places?

**Answer:** 0.665

**Working:** Softmax: e² / (e² + e¹ + e⁰) = 7.389 / (7.389 + 2.718 + 1) = 7.389 / 11.107 = 0.6652.

**Deeper:** [neural network fundamentals](../../../../data-science/02-deep-learning/notes/01-neural-networks-fundamentals.md)

### W30. A model gives the true class a probability of 0.25. What is the cross-entropy loss for that example, using the natural log, to 3 decimal places?

**Answer:** 1.386

**Working:** The loss is −ln(probability of the true class) = −ln(0.25) = 1.3863. A probability of 1 would give a loss of 0.

**Deeper:** [neural network fundamentals](../../../../data-science/02-deep-learning/notes/01-neural-networks-fundamentals.md)

---

## R. Retrieval and ranking

### W31. Across four queries the first relevant result is at rank 1, rank 3, not returned at all, and rank 2. What is the mean reciprocal rank, to 3 decimal places?

**Answer:** 0.458

**Working:** Reciprocal ranks are 1, 1/3, 0 and 1/2. Their mean is 1.8333 / 4 = 0.4583.

**Deeper:** [two-tower models and evaluation](../../../../data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md)

### W32. A ranked list has graded relevances 3, 2, 0, 1 from the top. With gain equal to the relevance and a discount of log2(rank + 1), what is NDCG at 4, to 3 decimal places?

**Answer:** 0.985

**Working:** DCG = 3/log2(2) + 2/log2(3) + 0/log2(4) + 1/log2(5) = 3 + 1.262 + 0 + 0.431 = 4.693. The ideal order 3, 2, 1, 0 gives 3 + 1.262 + 0.5 + 0 = 4.762. NDCG = 4.693 / 4.762 = 0.9854.

**Deeper:** [two-tower models and evaluation](../../../../data-science/05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md)

### W33. A term appears 3 times in a document and in 10 of the 1,000 documents in the corpus. With TF-IDF = count × log10(N / df), what is its score in that document?

**Answer:** 6

**Working:** IDF = log10(1000 / 10) = 2, so TF-IDF = 3 × 2 = 6. A term in every document would score 0.

**Deeper:** [keyword, semantic and hybrid search](../../../../generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search.md)

### W34. A document is ranked 1st by keyword search and 4th by vector search. What is its reciprocal rank fusion score with k = 60, to 3 decimal places?

**Answer:** 0.032

**Working:** RRF sums 1 / (k + rank) over the lists: 1/61 + 1/64 = 0.01639 + 0.01563 = 0.0320. Only ranks enter, so the two score scales never need reconciling.

**Deeper:** [the RAG pipeline](../../../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md)

### W35. What is the cosine similarity of the vectors (1, 2, 2) and (2, 0, 1), to 3 decimal places?

**Answer:** 0.596

**Working:** Dot product: 2 + 0 + 2 = 4. Lengths: √9 = 3 and √5 = 2.236. Cosine = 4 / (3 × 2.236) = 0.5963.

**Deeper:** [keyword, semantic and hybrid search](../../../../generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search.md)

---

## T and K. Time series and metrics

### W36. A forecast has a mean absolute error of 8 on the test period. The seasonal naive forecast has an in-sample mean absolute error of 10. What is the MASE?

**Answer:** 0.8

**Working:** MASE = model MAE / naive in-sample MAE = 8 / 10 = 0.8. Below 1 means the model beats the naive forecast.

**Deeper:** [forecasting](../../../../data-analytics/06-applied-analyses/notes/01-forecasting.md)

### W37. Segment A has 1,000 users converting at 10% and segment B has 3,000 users converting at 2%. What is the overall conversion rate, as a percentage?

**Answer:** 4

**Working:** Conversions: 100 + 60 = 160 of 4,000 users, which is 4%. The overall rate is a weighted mean, so a shift in mix towards B lowers it even when neither segment changes, the mechanism behind Simpson's paradox.

**Deeper:** [correlation and causation](../../../../data-analytics/03-experimentation-and-causality/notes/04-correlation-and-causation.md)

### W38. Revenue is users × conversion rate × average order value. Users rise 10%, the conversion rate falls 5% and order value is flat. By what percentage does revenue change, to 1 decimal place?

**Answer:** 4.5

**Working:** Multiply the factors: 1.10 × 0.95 × 1.00 = 1.045, a rise of 4.5%. Adding the percentages would give 5%, which is close only because the changes are small.

**Deeper:** [metric trees](../../../../data-analytics/06-applied-analyses/notes/11-metric-trees.md)
