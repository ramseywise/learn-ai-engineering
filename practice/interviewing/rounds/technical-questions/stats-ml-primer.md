# Probability, Statistics and ML Primer

Nine short lessons that teach the ideas behind [stats-ml-cheat-sheet.md](stats-ml-cheat-sheet.md), in the order
they build on each other. Each lesson has the idea in plain words, one worked example with numbers, the sentence
to say in an interview, and the cards in [stats-ml-bank.md](stats-ml-bank.md) to drill straight after. Read a
lesson, close it, and say the "say it" line from memory before moving on. The cheat sheet is for the last pass,
once these make sense.

Most examples use one setting: a payments app where a small share of transactions are fraud.

## 1. Random variables, expectation and variance

A **random variable** is a number whose value depends on chance: whether a transaction is fraud (1 or 0), how many
tickets arrive this hour, how much a customer spends. A **distribution** lists which values it can take and how
likely each is.

Two numbers summarise a distribution:

- The **expectation** (mean) is the long-run average. Multiply each value by its probability and add up.
- The **variance** is how far values typically fall from the mean, squared. The **standard deviation** is its
  square root, in the original units.

Worked example. A promotion pays £10 cashback with probability 0.1 and nothing otherwise.

- Mean: 10 × 0.1 + 0 × 0.9 = £1.
- Variance: the mean of the squares minus the square of the mean. 100 × 0.1 − 1² = 9. Standard deviation £3.

So the average payout is £1, but any one customer is far from that: the spread is three times the mean.

One rule does a lot of work: **the mean of a sum is the sum of the means**, always. Give the promotion to 1,000
customers and the expected cost is £1,000, with no further calculation. Variances also add, but only when the
pieces are independent.

**Say it:** "A random variable maps an outcome to a number. Its mean is the probability-weighted average and its
variance is the expected squared distance from the mean."

Drill: D1, D9, D13, D14.

## 2. Bernoulli and Binomial: one trial, then many

A **Bernoulli(p)** variable is a single yes/no trial: 1 with probability p, 0 otherwise. Its mean is p and its
variance is p(1 − p). The variance is largest at p = 0.5 (a coin flip is the least predictable trial) and zero
when p is 0 or 1.

A **Binomial(n, p)** variable counts the successes in n independent Bernoulli trials with the same p. Because it
is a sum of n Bernoullis, its mean is np and its variance is np(1 − p), by the rule from lesson 1.

Worked example. 2% of transactions are fraud. In a batch of 100:

- Expected fraud count: 100 × 0.02 = 2.
- Variance: 100 × 0.02 × 0.98 = 1.96. Standard deviation 1.4.
- P(no fraud at all) = 0.98^100 = 0.133.
- P(exactly one) = 100 × 0.02 × 0.98^99 = 0.271. The 100 counts which transaction is the fraudulent one.

The general formula is P(k successes) = C(n, k) p^k (1 − p)^(n − k): the probability of one particular pattern
with k successes, times the number of patterns.

Check the two conditions before using it: a **fixed number of trials**, and trials that are **independent with
the same p**. Fraud that comes in bursts from one stolen card breaks the second.

**Say it:** "Bernoulli is one yes/no trial. Binomial counts successes in n independent ones, with mean np and
variance np(1 − p)."

Drill: D2, D3, P10, P16.

## 3. Poisson: counts with no fixed number of trials

Use a **Poisson(λ)** when you count events in a stretch of time or space and there is no natural n: tickets per
hour, card declines per minute, typos per page. λ is the average count. The mean and the variance are both λ.

P(k events) = e^(−λ) λ^k / k!

Worked example. Support tickets arrive at 3 an hour on average.

- P(none in an hour) = e^(−3) = 0.050.
- For a different window, scale λ first. In 20 minutes λ = 1, so P(none) = e^(−1) = 0.368.

How it links to the Binomial. Lesson 2 had n = 100 and p = 0.02, so np = 2. A Poisson with λ = 2 gives
P(0) = e^(−2) = 0.135 and P(1) = 0.271, against 0.133 and 0.271 from the Binomial. When n is large and p is
small, the Poisson is the Binomial with less arithmetic.

One check to mention: real counts often have a variance well above the mean (busy days and quiet days). That is
**overdispersion**, and a Poisson model will then be too confident.

**Say it:** "Poisson models counts of independent events at a constant average rate. Mean and variance both equal
λ, and it approximates a Binomial with large n and small p."

Drill: D4, D5, D11, D12, P9.

## 4. Normal, the Central Limit Theorem and the standard error

The **Normal** (Gaussian) distribution is the bell curve, set by a mean μ and a standard deviation σ. About 68%
of values lie within 1σ of the mean, 95% within 2σ (1.96 exactly) and 99.7% within 3σ.

To compare any Normal value with those rules, convert it to a **z-score**: z = (x − μ) / σ, the number of
standard deviations from the mean.

Worked example. Payment processing time is Normal with mean 30 seconds and standard deviation 5. A 40-second
payment has z = (40 − 30) / 5 = 2. About 95% of payments are within 2σ, so 5% are outside, half on each side:
roughly 2.5% take longer than 40 seconds.

Why the Normal matters: the **Central Limit Theorem**. Take the average of n independent draws from almost any
distribution. For large n that average is approximately Normal, centred on the true mean, with standard deviation
σ / √n. That last quantity is the **standard error**: the spread of an estimate, as opposed to the spread of the
data.

Worked example. Transaction amounts are heavily skewed, with mean £50 and standard deviation £100. The average of
400 transactions has standard error 100 / √400 = £5. So 95% of such averages land within about £10 of £50.

Two points interviewers probe:

- The CLT is about the **average**, not the data. The amounts stay skewed however many you collect.
- Because of the square root, **four times the data halves the error**.

For a proportion the standard error is √(p(1 − p) / n). With p = 0.10 and n = 10,000 that is 0.003, or 0.3
points. Lesson 8 uses this.

**Say it:** "The CLT says the sample mean is approximately Normal with standard deviation σ over root n, whatever
the shape of the data. That is why z-tests and confidence intervals work."

Drill: D6, D7, D8, D10, P18.

## 5. Solving probability problems out loud

Most screen questions need one of four moves. Name the move before you calculate.

**Move 1: "at least one" means use the complement.** P(at least one six in four rolls) = 1 − P(no six) =
1 − (5/6)^4 = 0.518.

**Move 2: a rare thing and an imperfect test means Bayes, done with counts.** 1% of transactions are fraud. A
model flags 95% of fraud and 5% of legitimate transactions. A transaction is flagged: how likely is it fraud?

Take 10,000 transactions.

| | Flagged | Not flagged | Total |
|---|---|---|---|
| Fraud | 95 | 5 | 100 |
| Legitimate | 495 | 9,405 | 9,900 |

590 are flagged and 95 of them are fraud: 95 / 590 = 16%. The model is good, but legitimate transactions
outnumber fraud 99 to 1, so most flags are false alarms. The formula P(A given B) = P(B given A) P(A) / P(B) gives
the same number; the table is harder to get wrong.

**Move 3: "expected number of tries until" means condition on the first step.** Expected flips until the first
head: call it E. You always use one flip. Half the time you are done, half the time you are back at the start.
So E = 1 + 0.5 × E, which gives E = 2. In general a success with probability p takes 1/p tries on average.

**Move 4: an expected total means add the expected pieces.** Expected fraud count in 100 transactions at 2% is
100 × 0.02 = 2. This works even when the pieces are dependent.

Two definitions to keep apart:

- **Independent**: knowing one event tells you nothing about the other. P(A and B) = P(A) × P(B).
- **Mutually exclusive**: they cannot both happen. P(A and B) = 0. Exclusive events are as dependent as it gets.

Finish every answer with a sanity check on an extreme case: does the formula give the right thing when p = 0 or
p = 1?

**Say it:** state the event, name the move, compute, check an extreme.

Drill: P1 to P8, then P11 to P17. Work each on paper before flipping. Run
[probability_puzzles.py](../../../../data-analytics/02-probability-and-statistics/practice/probability_puzzles.py)
to see each answer confirmed by simulation.

## 6. Bias and variance of an estimator, and bias in data

An **estimator** is a rule that turns a sample into a guess: the sample mean guesses the true mean. Draw a new
sample and the guess changes. Picture many guesses as darts on a board whose bullseye is the truth.

- **Bias**: how far the centre of the darts is from the bullseye. Average guess minus truth.
- **Variance**: how scattered the darts are around their own centre.
- **Mean squared error** = bias² + variance. It measures total miss, and it is what you usually want small.

Worked example. Estimate a variance whose true value is 4 from samples of 5. Dividing the sum of squared
deviations by n = 5 gives 3.2 on average: biased low, because deviations are measured from the sample mean, which
sits closer to the sample than the true mean does. Dividing by n − 1 = 4 gives 4.0 on average: unbiased. That is
the whole reason for n − 1.

Unbiased is not automatically best. A slightly biased estimator with much lower variance can have the lower mean
squared error. Regularisation in lesson 9 is the same trade.

"Bias" has a second meaning, and "bias in statistics" on a topic list usually includes it: the **data** are
unrepresentative.

| Bias | Example |
|---|---|
| Selection | Surveying only active app users about satisfaction |
| Survivorship | Studying only companies that still exist |
| Non-response | Only very happy or very angry customers reply |
| Measurement | A tracker that drops events on one platform |
| Confounding | Premium users spend more, but they were richer to begin with |

More data shrinks variance. It does nothing for these: a million biased answers are precisely wrong.

**Say it:** "Bias is the systematic error of an estimator, variance is its sample-to-sample noise, and mean
squared error is bias squared plus variance. Bias in data collection is a separate problem that more data does
not fix."

Drill: S1, S2, S3, S4, S12, S13. Lab:
[distributions_and_estimators.py](../../../../data-analytics/02-probability-and-statistics/practice/distributions_and_estimators.py),
part 4.

## 7. Statistical significance

A significance test asks one question: **if nothing were going on, how surprising would this data be?**

1. State the **null hypothesis**, the "nothing is going on" claim: the coin is fair.
2. Work out what the data would look like if the null were true.
3. The **p-value** is the probability of a result at least as extreme as yours under the null.
4. If p is below a threshold set in advance (α, usually 0.05), reject the null.

Worked example. A coin gives 60 heads in 100 flips. Under a fair coin the count has mean 50 and standard
deviation √(100 × 0.5 × 0.5) = 5. Sixty is z = (60 − 50) / 5 = 2 standard deviations out. By the 95% rule the
chance of landing that far out on either side is about 5%; the exact figure is 0.046. Borderline evidence against
a fair coin.

What the p-value is **not**: the probability that the null is true, or the probability the result is due to
chance. It assumes the null and describes the data.

Two ways to be wrong:

| | Null is true | Null is false |
|---|---|---|
| Reject | **Type I error** (false positive), rate α | Correct. Its rate is the **power** |
| Do not reject | Correct | **Type II error** (missed effect), rate β |

Power is 1 − β and rises with sample size, effect size and α, and falls with noise.

A **95% confidence interval** is estimate ± 1.96 × standard error. The method covers the true value in 95% of
repeated samples. It says more than a p-value, because it shows the size of the effect and its uncertainty.

**Statistical significance is not practical significance.** With millions of users a 0.01 point lift can be
significant and worthless. With a small sample a large effect can be missed.

**Say it:** "The p-value is the probability of data at least this extreme if the null is true. Below α we reject,
accepting a false positive rate of α."

Drill: S5, S6, S7, S8, S9, S10, S11, P11.

## 8. A/B testing, end to end

An A/B test is lesson 7 applied to two groups. Random assignment is what makes it causal: the groups differ only
in the change, so confounding (lesson 6) is removed.

Design, in the order to say it:

1. Hypothesis and one **primary metric**. Add **guardrail metrics** that must not get worse.
2. The **unit** to randomise, usually the user.
3. α (0.05), power (0.8) and the **minimum detectable effect**: the smallest lift worth shipping.
4. The **sample size** those imply, and so the duration. Fix it before starting.
5. Run it, check the split is what you designed, then analyse once.

Worked example. Control converts 1,000 of 10,000 users (10.0%) and treatment 1,100 of 10,000 (11.0%).

- Difference: 1.0 point.
- Pooled rate: 2,100 / 20,000 = 0.105.
- Standard error of the difference: √(0.105 × 0.895 × (1/10,000 + 1/10,000)) = 0.0043.
- z = 0.010 / 0.0043 = 2.31, so p = 0.021. Significant at 5%.
- 95% interval for the lift: about 0.15 to 1.85 points. Real, but the size is not pinned down.

Sample size shortcut for α = 0.05 and 80% power: n per arm ≈ 16 × p(1 − p) / δ². For a 10% baseline and a 1 point
lift: 16 × 0.09 / 0.0001 = 14,400 per arm. Halve the lift you want to detect and you need four times the users.

What breaks a test:

- **Peeking.** Checking daily and stopping at the first p < 0.05 turns a 5% false positive rate into about 25%
  with 20 looks. Fix the horizon or use a sequential design.
- **Sample ratio mismatch.** A 50/50 design that logs 10,000 against 10,500 users has a bug in assignment or
  logging. Do not read the metrics until it is fixed.
- **Many metrics or segments.** Test 20 things and one will be "significant" by chance.
- **Novelty.** Users click a new thing because it is new. Run long enough for that to fade.
- **Wrong unit.** Randomise users but analyse sessions, and the standard error is too small.
- **Not significant is not "no effect".** Read the interval against the minimum detectable effect.

**Say it:** "Randomise, fix the sample size from the minimum detectable effect, look once, and decide from the
confidence interval, not only the p-value."

Drill: A1 to A13. Lab:
[ab_test_from_scratch.py](../../../../data-analytics/03-experimentation-and-causality/practice/ab_test_from_scratch.py).

## 9. Machine learning models and their trade-offs

A trained model is an estimator, so lesson 6 applies directly. Train the same model on a different sample and its
predictions change.

- **High bias (underfitting)**: the model is too simple for the pattern. Training error and validation error are
  both high.
- **High variance (overfitting)**: the model has memorised its training sample. Training error is low and
  validation error is much higher.

Every model sits somewhere on that line, and most techniques move it along: more flexibility lowers bias and
raises variance; regularisation, averaging and more data lower variance.

| Model | In one line | Reach for it when | Main weakness |
|---|---|---|---|
| Linear regression | Weighted sum of features predicts a number | You need a fast, explainable baseline | Only straight-line relationships |
| Logistic regression | The same weighted sum, squashed to a probability | You need probabilities and reasons, as in credit decisions | Linear boundary |
| Decision tree | A flowchart of yes/no splits | You need rules a person can read | Unstable: overfits on its own |
| Random forest | Many trees on resampled data, averaged | You want strong results with little tuning | Slower and harder to explain |
| Gradient boosting | Trees added one at a time, each fixing the last one's errors | Tabular data and accuracy matters most | Needs tuning; can overfit |
| k-nearest neighbours | Predict from the k most similar examples | Small data, irregular boundary | Slow to predict; fails with many features |
| Naive Bayes | Bayes' rule, treating features as independent | Text, tiny data, speed | The independence assumption is false |
| Neural network | Layers that learn their own features | Images, text, audio, very large data | Data, compute, opacity |

How the forest and boosting differ is a favourite follow-up. A forest averages many independent, deep trees: this
lowers **variance**. Boosting adds many shallow trees in sequence: this lowers **bias**.

A structure for any "pros and cons of model X" question:

1. What it assumes about the data.
2. Where it wins.
3. Where it fails.
4. What it needs: feature scaling, data volume, tuning.
5. How easily you can explain a prediction.

Worked example. "Which model for fraud detection?" Start with logistic regression as the baseline, because it is
fast and explainable. Move to gradient boosting, the usual best on tabular data. Fraud is about 1% of
transactions or less, so accuracy is useless: a model that says "never fraud" is 99% accurate. Use precision and
recall, and set the decision threshold from the cost of a missed fraud against the cost of blocking a good
customer. This is the table from lesson 5 again.

**Say it:** "Simple models have high bias and low variance; flexible ones the reverse. I start with a linear
baseline, move to boosted trees on tabular data, and judge by validation error with a metric that fits the class
balance."

Drill: M1 to M20. Labs: [overfit_curve.py](../../../../data-science/01-classical-ml/practice/overfit_curve.py),
[trees_vs_rounds.py](../../../../data-science/01-classical-ml/practice/trees_vs_rounds.py).

## Where to go deeper

- [Probability foundations](../../../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md),
  [distributions and sampling](../../../../data-analytics/02-probability-and-statistics/notes/03-distributions-and-sampling.md)
  for lessons 1 to 5.
- [Estimation](../../../../data-analytics/02-probability-and-statistics/notes/04-estimation.md) and
  [hypothesis testing](../../../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md)
  for lessons 6 and 7.
- [A/B testing](../../../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md) for lesson 8.
- [Supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md) and
  [ensembles](../../../../data-science/01-classical-ml/notes/06-ensembles.md) for lesson 9.
