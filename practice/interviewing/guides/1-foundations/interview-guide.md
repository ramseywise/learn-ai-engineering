---
origin: synthesized
sources:
  - data-science/01-classical-ml/notes/
  - data-science/02-deep-learning/notes/
  - data-engineering/06-ml-platform/notes/04-drift.md
confidence: high
cleaned: 2026-11-02
units:
  - data-science/01-classical-ml
  - data-science/02-deep-learning
  - data-analytics/01-python-for-data-analysis
  - data-analytics/06-applied-analyses/notes/06-sql-for-analytics.md
---
# ML Foundations (+ SQL/Analytics) — Study Guide

The classical round. It still opens most MLE and DS loops, analyst loops take the metrics and
SQL parts, and AI engineering loops use it as a sanity check. The bar is fluency on trade-offs
and metrics, not derivations. New to all this? Read [00-overview.md](00-overview.md) first,
then work through this guide in order.

**How to read it.** Each topic gives the plain meaning, the answer an interviewer expects, the
honest nuance where the common answer is too simple, and a link to the course note that teaches
it properly. Numbers are always one note's measured result on one dataset. Quote them as an
example ("in one experiment I've seen…"), never as a general rule.

## 0. Three jobs, and what each is interviewed on

Titles blur between companies, so read the job description rather than the title.

| | Data analyst | Data scientist | Data engineer |
|---|---|---|---|
| **The question they own** | What happened, and is the difference real? | What will happen on rows nobody has seen, and can we trust it? | Does the right data arrive on time, correct, in a usable shape? |
| **What they hand over** | An answer, chart or experiment readout that someone acts on | A model plus evidence that it works, or an experiment and its reading | Pipelines, tables and contracts that other people build on |
| **Main interview rounds** | SQL, statistics and A/B tests, product sense | ML fundamentals, statistics, coding, ML or product case | SQL, coding, data modelling, pipeline and system design |
| **In this guide** | §2, §6, plus the [stats guide](../11-stats-experimentation/interview-guide.md) | All of it, plus the stats guide | §5, §6, Q2, Q7, Q8, plus [data eng & MLOps](../8-data-eng-mlops/interview-guide.md) |
| **Course subject** | [Data analytics](../../../../data-analytics/README.md) | [Data science](../../../../data-science/README.md), after analytics | [Data engineering](../../../../data-engineering/README.md) |

Two neighbours share the word "engineer". An **ML engineer** gets the data scientist's ML
questions plus deployment and system design. An **AI engineer** builds on LLMs and gets the
pillars from [LLM fundamentals](../2-llm-fundamentals/interview-guide.md) on, with this guide as
the sanity check.

**Expect this question:** "What's the difference between an analyst and a scientist here?" A
good answer: the analyst explains the past and tests claims about it, the scientist predicts on
unseen data, and the engineer makes both possible. Then ask which of those this team most needs.

## 1. Supervised learning core

Supervised learning means learning from examples that have the answer attached: past loans
marked "repaid" or "defaulted". The aim is to do well on *new* rows. Almost everything below
exists to stop you fooling yourself about that.

### Baseline first

**Always name the naive baseline first**: majority class for classification, the mean for
regression. An improvement only means something against it. On the course's adult census data, a
dummy model scores 0.759 accuracy by never predicting a high earner, with AUC 0.500. Logistic
regression reaches validation AUC 0.906 and boosting 0.925.
Course: [training and tuning](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md#split-baseline-fit).

### Train, validation and test

- **Train** fits the model's weights.
- **Validation** chooses between models and settings.
- **Test** gives one final number, and you read it once.

The analogy is homework, mock exam and final exam. If you keep checking the final, it stops
being a final. **The usual interview answer:** a 60/20/20 split. **The nuance:** the ratio
matters less than how you split. Time-ordered data must train on the past and validate on the
future. Rows from the same customer must stay on one side.
Course: [train, validation, test](../../../../data-science/01-classical-ml/notes/01-statistical-foundations.md#train-validation-test).

### Leakage: the #1 practical sin

Leakage means information from the rows you score reaches training, so scores look better than
reality will be. Three rules: fit scalers and encoders on train only; split *before* any
target-aware transform; use time-based splits for temporal data. Wrap preprocessing and model in
one pipeline so it can't leak. In the course's credit lab, resampling before the split gave a
cross-validation score of 0.98 for a model that truly scored about 0.70.
Course: [leakage and pipelines](../../../../data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines.md#leakage-and-why-pipelines-exist),
[the resampling leak](../../../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md#the-leak-resampling-before-you-split).

### Cross-validation

Split the data into k equal parts (folds). Each takes a turn as the scored rows while the rest
train, and you average the k scores. It uses small data better than one split and shows how much
the score moves.

Pick the splitter to match how production will differ from training:

| Data | Splitter | Why |
|---|---|---|
| Classes unbalanced or few rows | Stratified k-fold | Keeps the positive rate steady in each fold |
| Several rows per customer or group | Group k-fold | The same entity can't sit on both sides |
| Ordered in time | Forward-chaining split | Never train on the future |

The choice changes the answer. In the course's experiments, grouping adult census by occupation
moved AUC from 0.9279 to 0.9122 and fold spread from 0.0041 to 0.0286. Shuffling Citi Bike rides
gave R² 0.648 against 0.590 with a forward split.

**Common answer:** "the fold standard deviation is the error of my estimate." **Honest nuance:**
it gives the rough size of the noise and isn't a clean standard error, because folds share
training rows. Bengio and Grandvalet showed that no universal unbiased estimator of that variance
exists. To compare two models, use the same folds and look at the paired differences: in the
note, boosting won all 5 folds with a paired spread of 0.0025, against about 0.004 for each model
alone. **Nested cross-validation** gives an honest score for a whole tuning procedure, mainly
worth its cost on small data.
Course: [k-fold and fold spread](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md#k-fold-and-what-a-folds-spread-tells-you),
[splitters](../../../../data-science/01-classical-ml/notes/04-model-evaluation.md#splitters),
[nested CV](../../../../data-science/01-classical-ml/notes/04-model-evaluation.md#nested-cross-validation).

### Bias and variance

**Bias** is being wrong in the same way whatever data you see, because the model is too simple.
**Variance** is changing a lot with the sample, because the model is flexible enough to learn the
noise. A dart player who always lands low-left has bias, and one who scatters around the bullseye
has variance. Expected squared error is bias² + variance + irreducible noise.

Read it from training and validation scores together:

| Pattern | Means | Try |
|---|---|---|
| Both poor and close together | Underfit (high bias) | More features, more flexible model, less regularisation |
| Train good, validation much worse | Overfit (high variance) | More data, simpler model, more regularisation |
| Both good, small gap | Healthy | Stop, or check whether it's worth more effort |

From the course's learning curves at 16,000 rows (AUC, train then validation): a depth-2 tree
0.834 and 0.833, an unlimited tree 0.999 and 0.760, boosting 0.953 and 0.927. Note the first
row: a small gap says nothing about whether the model is any good.

**Honest nuance:** the textbook U-shape doesn't describe everything. Parameter count is a poor
proxy for complexity, and very large networks can generalise.
Course: [bias, variance and complexity](../../../../data-science/01-classical-ml/notes/01-statistical-foundations.md#bias-variance-and-model-complexity),
[reading performance during training](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md#reading-performance-during-training),
[is deep learning different?](../../../../data-science/02-deep-learning/notes/01-neural-networks-fundamentals.md#is-deep-learning-a-different-kind-of-model).

### Regularisation

Regularisation is a cost on complexity. It removes more noise than signal, because noise doesn't
repeat from sample to sample.

| Method | What it does | Use it when |
|---|---|---|
| **L1 (lasso)** | Penalises absolute weights, so it drives some to exactly zero | You want a sparse model that drops features |
| **L2 (ridge, weight decay)** | Penalises squared weights, so it shrinks all without zeroing | The default for linear models and networks |
| **Dropout** | Zeroes random units during training, off at test time | Larger networks that overfit |
| **Early stopping** | Stops when validation stops improving, since weights grow with training | Boosting and networks; nearly free |

**Figures from the notes, on their setups only.** On 1,500 adult census rows, L1 and L2 tied
(0.901 and 0.902), with L1 at C=1 keeping 29 of 83 weights. A network with no regularisation
scored train 0.999 and validation 0.860, and the right weight decay lifted validation to 0.904,
while too much (100) dropped it to 0.500. So the strength matters and values don't copy between
setups.

**Honest nuance on dropout:** rates have fallen as data has grown, and dropout hurts a model that
already underfits. Fix the learning rate first. **On early stopping:** keep the best weights, not
the last. In the note's scikit-learn run, the waiting rounds stayed in the model, and more
patience gave a worse loss (0.2960 to 0.3561) until the model was cut back to its best round
(0.2918).
Course: [regularisation is one idea](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md#regularisation-is-one-idea),
[early stopping](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md#early-stopping-is-regularisation-too),
[dropout in networks](../../../../data-science/02-deep-learning/notes/02-optimisation-and-regularisation.md#regularisation).

### Hyperparameter search

**Common answer:** "random beats grid." It comes from Bergstra and Bengio: few knobs matter, and
for the same budget random tries each one at more values. **Honest nuance:** random isn't always
better. In the course's test (32 fits, five seeds), two grids, random and TPE all tied, within
0.0003 on search rows and 0.0016 on report rows. The note puts this down to a wide plateau, one
knob carrying most of the importance, and grid values chosen by someone who knew the model.

| Situation | Reasonable choice |
|---|---|
| One or two knobs, cheap fits | Grid |
| Several knobs, unfamiliar model | Random |
| Expensive fits | TPE or Optuna with pruning |
| Number of boosting rounds | Early stopping, not search |

Keep it in proportion. In that note tuning moved test AUC by 0.0009, and moving from logistic to
boosting moved it by 0.025. The winner's score is also optimistic, because it was chosen partly
for luck: 0.0085 on 100 selection rows, 0.0013 on 1,000.
Course: [hyperparameter search](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md#hyperparameter-search),
[the honest final number](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md#the-honest-final-number).

### Feature scaling

Scaling puts columns on comparable ranges, so "income in dollars" doesn't drown out "age in years".

| Needs scaling | Doesn't |
|---|---|
| Anything using distances (kNN, k-means, kernel SVM), PCA, penalised linear models, neural nets | Trees and tree ensembles, which only ask "is x above this cut?" |

| Name | Does | Watch out |
|---|---|---|
| **Standardisation** | Mean 0, variance 1 | The usual default |
| **Min-max** (often called normalisation) | Squeezes into [0, 1] | One outlier squashes everything else |
| **Robust scaling** | Uses median and interquartile range | For outliers |
| **Row normalisation** (`Normalizer`) | Makes each *row* unit length | A different thing; used for cosine similarity |

"Normalisation" means different things to different people, so say which you mean. Fit on train
only. In the course's example, a kernel SVM on breast cancer data scored 0.63 unscaled, 0.97 with
min-max and 0.96 standardised.
Course: [preprocessing and scaling](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md#preprocessing-and-scaling).

### Model menu, with reasons

Linear or logistic regression: baseline, interpretable, often reasonably calibrated. Random
forest: robust first serious model. Gradient boosting (LightGBM, CatBoost, XGBoost): usually the
strongest on tables, with native categorical handling. SVM: small clean data. kNN: lazy baseline.
Neural nets: images, text, audio, or very large data.
Course: [supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md),
[ensembles](../../../../data-science/01-classical-ml/notes/06-ensembles.md),
[boosting in practice](../../../../data-science/01-classical-ml/notes/07-boosting-in-practice.md).

### Class imbalance, SMOTE and threshold choice

Imbalance means one outcome is rare: fraud, default, a disease. Accuracy stops helping, because
approving everyone scores 97% when 3% default, and catches nobody.

**Remedies people name:** class weights, undersampling, oversampling, SMOTE (which makes synthetic
rare-class rows by interpolating between neighbours), and moving the decision threshold.

**The threshold is often the real lever.** A model outputs a probability, and 0.5 is only a
default. If calibrated, the cheapest rule is to act when P ≥ c_FP / (c_FP + c_FN). With a missed
defaulter costing 5 times a wrongly declined customer, that's 1/6. Choose thresholds on validation,
never on test.

**SMOTE is not a default fix.** Interviewers often expect it to be named, so name it, then say this:

- In the course's credit data (UCI credit card default, thinned by the authors to 3% defaults),
  no method beat doing nothing on ranking. SMOTE's ROC-AUC was 0.022 lower (SD 0.018), lower on
  18 of 20 seeds.
- Across 10 combinations of learner, rate and cost ratio, SMOTE at a fixed 0.5 lost to a tuned
  threshold beyond noise in 8, tied in 2 and never won. SMOTE with its own tuned threshold was
  within noise in all 10.
- It also broke the probabilities: a mean predicted default of 30.5% on a book defaulting at 3.0%.

That's one dataset, thinned by choice, so **don't claim SMOTE generally loses**. The note cites
Elor and Averbuch-Elor's preprint on 73 datasets, which supports a tie for strong classifiers
rather than a general loss, with weak learners (MLP, SVM) sometimes gaining. Balancing may still
help when you can't move the threshold.

If you do resample, do it inside the pipeline, training folds only, and repair the probabilities
afterwards. A rare class also limits what you can measure: with 50 defaulters in test, ROC-AUC had
an SD of 0.039 in that note. Count events, not rows.
Course: [what each remedy does](../../../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md#imbalance-what-each-remedy-does),
[does SMOTE lose?](../../../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md#does-smote-lose-to-a-tuned-threshold),
[power on rare events](../../../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md#significance-power-and-what-a-rare-event-needs).

## 2. Metrics (choose and defend)

The pattern interviewers want: **metric ← decision the system drives.** "AUROC over accuracy
because we rank-order for a capacity-limited intervention."

### Type I and Type II errors

- **Type I, false positive:** raising an alarm when nothing is there. A healthy patient is told
  they're ill.
- **Type II, false negative:** missing the real thing. A sick patient is told they're fine.

The names depend on what you call the null hypothesis. With H0 "applicant is good", Type I
declines a good customer and Type II approves a defaulter; flip H0 and they swap. So say the
outcome in words as well, then put a cost on each, since those costs decide the threshold.
Course: [accuracy lies; errors cost](../../../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md#accuracy-lies-errors-cost).

### Classification metrics

| Metric | Formula | Plain question | Reach for it when |
|---|---|---|---|
| **Accuracy** | (TP+TN)/all | How often is it right? | Classes are balanced and errors cost the same |
| **Precision** | TP/(TP+FP) | Of those flagged, how many were real? | False alarms are costly (spam filter) |
| **Recall** (sensitivity) | TP/(TP+FN) | Of the real ones, how many did we catch? | Misses are costly (cancer screening) |
| **Specificity** | TN/(TN+FP) | Of the real negatives, how many did we clear? | Medical tests, paired with sensitivity |
| **F1** | 2PR/(P+R) | Balance of precision and recall | A single number when no costs are known |

**F1 nuance:** it weights the two errors equally and ignores true negatives. With real costs, use
them. Every one of these depends on the threshold.
Course: [confusion matrix, precision, recall, F1](../../../../data-science/01-classical-ml/notes/04-model-evaluation.md#confusion-matrix-precision-recall-f1).

### ROC and PR curves

Both sweep over every threshold.

- **ROC** plots recall against false positive rate. Its AUC is the chance that a random positive
  ranks above a random negative: 0.5 is random, 1.0 is perfect.
- **PR** plots precision against recall. A random model's level equals the positive rate, so read
  it against that, not against 0.

**Common answer:** "PR-AUC is better under heavy imbalance." **Nuance:** PR ignores true negatives,
so it shows what you pay per catch. ROC isn't wrong, as it answers a different question and doesn't
move with the class mix. PR-AUC does move, so don't compare it across datasets with different base
rates. In the credit note, a model with ROC-AUC 0.76 had PR-AUC 0.142, nearly 5 times the random
0.03. Neither curve tells you whether the probabilities are right.
Course: [threshold, PR and ROC](../../../../data-science/01-classical-ml/notes/04-model-evaluation.md#threshold-precisionrecall-and-roc),
[ROC and AUC](../../../../data-science/01-classical-ml/notes/04-model-evaluation.md#roc-curve-and-auc).

### Regression metrics

- **MAE:** average size of the error, in the target's units. Resists outliers.
- **RMSE:** squares first, so big misses count more. Outlier-sensitive.
- **MAPE:** percentage error. Undefined at zero and unstable near it.
- **R²:** share of variance explained, compared with always predicting the mean. 1 is perfect, 0
  matches the mean, and it can go negative on new data. **Nuance:** it doesn't tell you how large
  the errors are, and it depends on how spread out the target is. Fine for comparing models on the
  same data; report an error in real units too.

Course: [multiclass and regression metrics](../../../../data-science/01-classical-ml/notes/04-model-evaluation.md#multiclass-and-regression-metrics).

### Clustering: silhouette

Silhouette asks whether each point is closer to its own cluster than the next nearest, from −1 to 1.
**Nuance:** it favours round clusters. In the course's example, DBSCAN's correct split of
two_moons scores worse than k-means's wrong one. Compare against shuffled data and check stability
across seeds. In the music case, silhouette was 0.258 against 0.107 on shuffled data. With true
labels available, use ARI or NMI instead.
Course: [comparing and evaluating](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md#comparing-and-evaluating).

### Ranking: NDCG and MRR

For search, recommendations and RAG retrieval, the order is the product.

- **MRR:** the mean of 1 / rank of the first relevant result. Use it when one good result is enough
  and people read top-down. If the first hit is at ranks 1 and 3, and a third query misses, MRR is
  (1 + 1/3 + 0) / 3 = 0.44.
- **NDCG@k:** gives credit for each relevant item, discounted further down the list, then divides by
  the ideal order's score, so 1.0 is perfect. It handles graded relevance (highly, partly, not).
- **Precision@k** and **recall@k** ignore order within the top k.

Pick k to match what the user or model actually sees. **Nuance:** evaluate on a time split, and report
coverage too. In the course's MovieLens 100K experiment, a random split raised one model's NDCG@10
from about 0.126 to 0.309, none of it skill. A model with high NDCG and tiny coverage is a bestseller
list.
Course: [metrics for retrieval](../../../../generative-ai/08-eval/notes/07-evaluating-rag-and-grounding.md),
[top-N ranking](../../../../data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation.md#the-metric-that-matters-top-n-ranking).

### Calibration

A model is calibrated if, among cases it scores 0.8, about 80% are truly positive. Ranking and
calibration are separate properties: a model can rank perfectly with wrong probabilities. You need
calibration whenever the number itself drives a decision: pricing, a cost-based threshold, an
expected-value sum.

- **Check:** reliability curve, Brier score, calibration intercept.
- **Repair on held-out data:** Platt (sigmoid) or intercept recalibration when data is short, isotonic
  only with plenty of data, temperature scaling for deep nets. In the credit note, isotonic fitted on
  144 defaulters gave a slope near 0.8.
- **Usual habits, not laws:** logistic regression is often well calibrated, naive Bayes is pushed to
  0 and 1, deep nets run overconfident, random forests are pulled away from 0 and 1.

Course: [is a 0.8 really 80%?](../../../../data-science/01-classical-ml/notes/04-model-evaluation.md#calibration-is-a-08-really-80),
[score to price](../../../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md#calibration-the-bridge-from-score-to-price).

## 3. Deep learning basics (Ng structure)

Backprop is the chain rule from the loss back to each weight. Vanishing and exploding gradients are
tackled by initialisation, norm layers and residual connections. Optimisers run SGD → momentum → Adam,
with learning-rate schedules and batch size effects. Batch norm stabilises layer inputs, with caveats.
Check in order: does the signal survive through the layers, does the optimiser make progress, does what
it learned generalise? CNNs use locality and weight sharing; RNNs then transformers handle sequences
(see [llm-fundamentals](../2-llm-fundamentals/interview-guide.md)).

**Structuring ML Projects** is interview gold: orthogonalisation, a single-number metric, human-level
performance as a proxy for Bayes error, error analysis by slicing. Its two case-study quizzes (bird
detection, autonomous driving) are effectively practice case interviews.
Course: [network basics](../../../../data-science/02-deep-learning/notes/01-neural-networks-fundamentals.md),
[optimisation and regularisation](../../../../data-science/02-deep-learning/notes/02-optimisation-and-regularisation.md),
[structuring ML projects](../../../../data-science/02-deep-learning/notes/03-structuring-ml-projects.md).

## 4. Unsupervised learning and embeddings

No labels, so no answer key: use it to explore or to make features. k-means (k is a modelling choice),
GMM (soft assignments), hierarchical. PCA keeps linear variance; UMAP and t-SNE keep neighbourhoods, and
are for looking rather than for downstream features without care. Embeddings are learned representations:
word2vec's predict-your-neighbours trick generalises to items or tracks anywhere co-occurrence exists.
Course: [unsupervised learning](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md),
[embeddings and similarity](../../../../data-science/03-nlp/notes/04-embeddings-and-similarity.md).

## 5. ML system hygiene (bridges to MLOps)

**Reproducibility:** seeds, pinned configs, logged params and metrics. **Technical debt:** entanglement,
feedback loops, pipeline jungles (Sculley et al., NIPS 2015). **Interpretability:** feature importance
versus SHAP and LIME (local additive explanations), and when interpretability beats accuracy (healthcare,
credit). Course: [model interpretability](../../../../data-science/01-classical-ml/notes/08-model-interpretability.md).

### Data drift and train/serve skew

The world after launch differs from your training data.

| Name | What moves | Visible without labels? |
|---|---|---|
| **Covariate (data) drift** | The inputs, P(x) | Yes |
| **Prior (label) shift** | The outcome rate, P(y) | Hardly, for rare classes |
| **Concept drift** | The relationship, P(y given x) | No: you need labels |
| **Train/serve skew** | Serving computes features differently; the world didn't change | Sometimes |

A broken feed isn't drift, and it's a more common cause than people assume. In Shankar et al.'s
practitioner interviews, delayed feedback came up first, then "unnatural" drift from missing or corrupt
data, then natural drift. So check the pipeline before you retrain.

The note's simulated cases show why one monitor isn't enough, all on real rows from the credit data:

- Covariate shift: worst PSI 0.319, ROC-AUC unchanged at 0.759. Loud and harmless to the model.
- Concept shift: PSI no different from no change, ROC-AUC 0.764 down to 0.600. Silent.
- Prior shift: default rate doubled to 6%, PSI still 0.011. Nearly silent.
- A key feature filled with zeros: PSI 3.5, score PSI only 0.073, declines down from 2.4% to 0.1%.

**Common answer:** "PSI over 0.25 means retrain." **Nuance:** the 0.1 and 0.25 lines are conventions the
course couldn't trace to a study, so calibrate on your own windows. Statistically significant isn't the
same as large. And 100 features tested daily at α = 0.05 will alarm every day. **What to do:** check the
pipeline, measure the cost, retrain if it's worth it, gate the new model. Start with scheduled retraining.
Course: [drift](../../../../data-engineering/06-ml-platform/notes/04-drift.md),
[drift when the world moves](../../../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md#drift-when-the-world-moves).

## 6. SQL & analytics screen (folded in)

Patterns that recur: GROUP BY + HAVING, multi-table JOINs (know LEFT vs INNER result-count reasoning),
CASE bucketing, date truncation, **window functions** (ROW_NUMBER vs RANK vs DENSE_RANK, LAG/LEAD, running
aggregates), CTEs over nested subqueries, and the dedup-latest-row idiom (ROW_NUMBER … PARTITION BY … ORDER
BY ts DESC = 1). Analytics judgment: define the metric before writing the query, and know one funnel,
retention or cohort query cold. Watch for fan-out: a many-to-many join inflates revenue without an error.
Practise locally with DuckDB.
Course: [SQL for analytics](../../../../data-analytics/06-applied-analyses/notes/06-sql-for-analytics.md),
[cohorts](../../../../data-analytics/06-applied-analyses/notes/03-cohort-and-retention.md),
[funnels](../../../../data-analytics/06-applied-analyses/notes/04-funnel-and-conversion.md).

## 7. Question bank

### 7.1 Answer sketches

- *"Model does great offline, poorly in prod."* — leakage, train/serve skew, drift, survivorship in
  training data, feedback loops, eval metric ≠ business metric — in that checking order.
- *"Explain regularisation to a stakeholder."* — a penalty on complexity, so the model must earn every
  parameter; L1 also does feature selection.
- *"Why gradient boosting over a neural net for tabular?"* — sample efficiency, native missing and
  categorical handling, less tuning, interpretability tooling; NNs win with huge data or mixed modalities.
- *"Why AUROC over accuracy here?"* — accuracy is fixed at one threshold and flatters the majority class;
  if the system ranks cases for a limited number of interventions, how well it ranks is what you need.
- *"Second-highest salary per department."* — window function idiom; discuss ties → RANK vs ROW_NUMBER.
- *"How do you pick K in k-means?"* — elbow or silhouette, plus the honest answer: K encodes the product
  decision (how many segments can ops act on?).

### 7.2 The ML Fundamentals questions

Eighteen reported questions. Rehearse
**Say** aloud: it's the 60-second version from the
[technical round](../../rounds/technical-questions/README.md), and **Follow-up** is the one level deeper.

#### Q1. Pre-processing and feature engineering

*"How do you approach data pre-processing and feature engineering?"*

**Say:** I split first, so nothing from validation or test shapes a transformation. Then I check types,
missing values, duplicates and how the target is defined, and ask whether each column will really exist at
prediction time. I add features from domain knowledge, encode categories, transform skewed values and scale
where the model needs it, all inside one pipeline. Each change has to beat the baseline on validation to stay.

**Follow-up:** *"Why does the scaler go inside cross-validation?"* Otherwise its statistics include the
validation fold, so the scores come out optimistic.

**Course:** [feature engineering and pipelines](../../../../data-science/01-classical-ml/notes/03-feature-engineering-and-pipelines.md)

#### Q2. SQL versus NoSQL for AI workloads

*"Explain SQL versus NoSQL databases for AI workloads."*

**Say:** Relational databases suit data with many-to-one and many-to-many links, since each fact is stored
once, joins live in the database and transactions are strong. NoSQL covers several things: document stores
for self-contained records read as a unit, key-value stores for fast lookups such as online features, and
wide-column stores for key-based access at high write volume. An AI system usually uses several: relational
for users and metadata, a warehouse for training data, key-value for serving features, and a vector index for
embeddings. I'd choose from the access pattern, not from the label.

**Follow-up:** *"Do you need a dedicated vector database?"* Often not at first. Ask how many vectors, how many
dimensions, and whether a query needs keyword and dense search together. pgvector inside Postgres or even exact
search can be enough at small scale.

**Nuance:** the split is dated. Postgres stores JSON and vectors, and many NoSQL stores offer SQL-like queries.
The course has no note framed as SQL vs NoSQL; the links below cover the parts.

**Course:** [data models](../../../../data-engineering/01-storage-and-compute-foundations/notes/01-data-systems-and-data-models.md#data-models-are-layers),
[row and column stores](../../../../data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores.md),
[vector database comparison](../../../../generative-ai/02-rag-retrieval/notes/09-vector-database-comparison.md)

#### Q3. Diagnosing performance bugs

*"What steps would you take to diagnose performance bugs in a model?"*

**Say:** First I'd ask whether "performance" means quality or speed. For quality, I compare with a baseline, check
the data and labels, then compare train and validation to separate underfitting from overfitting, and count errors
by slice before building any fix. If it's good offline and poor in production, I check leakage, train/serve skew,
drift, survivorship, feedback loops and the metric, in that order. For speed I profile first, because the time
usually goes to feature fetches, network and framework rather than the model.

**Follow-up:** *"Train and validation are both fine, but test is bad. Why?"* Validation may have been overused, or
it may not match the test distribution. A train-dev set, drawn from the training distribution, separates variance
from data mismatch.

**Course:** [structuring ML projects](../../../../data-science/02-deep-learning/notes/03-structuring-ml-projects.md#error-analysis-count-before-you-build),
[where the milliseconds go](../../../../data-engineering/06-ml-platform/notes/03-batch-and-online-serving.md#where-the-milliseconds-go)

#### Q4. Latency or throughput for a one-request assistant

*"Should you optimize for latency or throughput? (for a personal assistant with one request)"*

**Say:** Latency. A person is waiting, and with one request at a time there's no queue, so throughput buys nothing.
For an LLM that splits into time to first token, which is when it feels alive, and time per output token, which is
how fast it reads. Throughput matters when many requests compete for the same hardware.

**Follow-up:** *"And at a thousand users?"* Now they trade off: batching raises throughput while each request waits
longer. Tune goodput, the throughput that still meets your latency target, rather than raw tokens per second.

**Course:** [throughput, cost and goodput](../../../../ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline.md#throughput-cost-and-goodput),
[batching](../../../../ai-engineering/07-inference-engineering/notes/06-serving-at-scale.md#batching)

#### Q5. Data parallelism for a one-request assistant

*"Should you use data parallelism for a single-request personal assistant? Why or why not?"*

**Say:** No. Data parallelism means full copies of the model, each handling different requests, so it scales
throughput and leaves the time for one request unchanged. Replicas cut latency only by removing queueing, and one
request has no queue. To make one request faster I'd look at a faster or quantised model, better hardware, or tensor
parallelism if it's on several GPUs anyway.

**Follow-up:** *"What does tensor parallelism do differently?"* It splits each operation's work across GPUs, so it can
cut latency and fit larger models, at the cost of communication inside every layer.

**Nuance:** sources use the term differently. The course note compares three books that disagree on data parallelism
in serving. In training it means different batches on different GPUs. State your meaning. A second replica can still
be justified for availability.

**Course:** [parallelism for inference](../../../../ai-engineering/07-inference-engineering/notes/06-serving-at-scale.md#parallelism-for-inference)

#### Q6. How Transformers work

*"Explain how Transformers work. Why are they foundational?"*

**Say:** A transformer builds each token's representation with attention: the token's query is compared with the other
tokens' keys, and the resulting weights average their values. A block adds a small feed-forward network, with residual
connections and LayerNorm so that deep stacks train, and several heads can each attend to different relationships. It's
foundational because any token can use any other directly, which recurrent models struggled with over long distances,
and it scaled well enough to underlie today's LLMs.

**Follow-up:** *"Why divide by √d_k?"* Dot products grow with dimension, which would push the softmax towards one-hot and
shrink its gradients. Note that d_k is the key dimension, not the sequence length.

**Course:** [attention and the transformer block](../../../../generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block.md);
guide: [LLM fundamentals](../2-llm-fundamentals/interview-guide.md)

#### Q7. Real-time versus batch

*"How would you handle real-time versus batch processing for data updates? When is one preferred over the other?"*

**Say:** I pick by when the consumer needs the answer. Batch is my default, because there's no service to keep up,
failures are reruns, and consumers read the last good table. I'd use a stream if a system can act within seconds, and a
synchronous service if a person is waiting. "Real-time" is vague, so I'd ask for the freshness needed in seconds and who
pays for it.

**Follow-up:** *"When does precomputing predictions fail?"* When traffic spreads across many keys, or inputs include
session data you can't know in advance.

**Course:** [batch and online serving](../../../../data-engineering/06-ml-platform/notes/03-batch-and-online-serving.md),
[choosing batch or stream](../../../../data-engineering/02-ingest-and-modelling/notes/01-ingest.md#choosing-batch-or-stream)

#### Q8. Ingesting structured, unstructured and event data

*"How do you ingest and process different types of data (structured, unstructured, event data)?"*

**Say:** Whatever the type, I land it raw, check the schema and make the load safe to repeat. Structured tables come in
by scheduled batch or change data capture, merging on a key. Unstructured documents get crawled, parsed and chunked with
metadata, ready for embedding or search. Events go through a log such as Kafka, where delivery is usually at-least-once,
so consumers have to handle duplicates.

**Follow-up:** *"A retry doubled a table. Why, and how do you fix it?"* An append ran twice after a timeout. Change the
loader to replace a whole window or merge on a key, then rebuild the affected days.

**Course:** [ingest](../../../../data-engineering/02-ingest-and-modelling/notes/01-ingest.md),
[Kafka and stream semantics](../../../../data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics.md),
[chunking](../../../../generative-ai/02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking.md)

#### Q9. The bias-variance trade-off

*"Explain the bias-variance tradeoff in simple terms."*

**Say:** Bias is being wrong in the same way every time because the model is too simple. Variance is the model changing a
lot with the data it happened to see, because it's flexible enough to learn noise. Making a model more flexible usually
lowers bias and raises variance, so you look for the point where the total error on new data is lowest. In practice I read
it from the training and validation scores side by side.

**Follow-up:** *"How do you tell which you have?"* Both poor and close together is high bias. Train good and validation much
worse is high variance. A small gap alone doesn't mean the model is good.

**Nuance:** very large networks don't always follow the textbook curve. Raise this only if pressed.

**Course:** [bias, variance and complexity](../../../../data-science/01-classical-ml/notes/01-statistical-foundations.md#bias-variance-and-model-complexity)

#### Q10. Neural networks and tabular data

*"Why are neural networks usually not the first choice for tabular data?"*

**Say:** On medium-sized tables, tree ensembles usually do at least as well for much less effort. They're sample-efficient,
handle missing values and categories natively, need less tuning and have good interpretability tooling. Grinsztajn and
colleagues benchmarked 45 tabular datasets and found trees still state of the art at around 10,000 samples. So I'd start
with boosting and need a reason to move.

**Follow-up:** *"When would you choose a network?"* Very large data, mixed inputs such as text or images alongside the table,
or when you want learned embeddings for high-cardinality entities.

**Nuance:** that benchmark covers medium-sized data, so it isn't a law for every table.

**Course:** [boosting in practice](../../../../data-science/01-classical-ml/notes/07-boosting-in-practice.md),
[supervised learning](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md)

#### Q11. Imbalanced datasets

*"How do you handle imbalanced datasets in real projects?"*

**Say:** I start with the cost of each error and a metric that reflects it, usually PR-AUC or expected cost, since accuracy
misleads here. I train on the data as it is, then choose the threshold on validation from those costs. If that isn't enough
I try class weights, then resampling inside the pipeline, and I recalibrate if the probabilities are used. I also count how
many rare events I have, because that limits what I can measure.

**Follow-up:** *"Isn't SMOTE the standard fix?"* It's the standard answer, but not a default. In one experiment I know, on a
credit dataset thinned to 3% defaults, SMOTE at a fixed 0.5 usually lost to a tuned threshold and tied with its own tuned
threshold, while wrecking the probabilities. That's one dataset. A 73-dataset preprint it cites supports a tie for strong
classifiers, with weak ones sometimes gaining, so I'd test rather than assume.

**Course:** [imbalance, errors and drift](../../../../data-science/01-classical-ml/notes/10-imbalance-errors-and-drift.md#imbalance-what-each-remedy-does)

#### Q12. RNN versus LSTM

*"Explain the difference between RNN and LSTM."*

**Say:** An RNN applies the same cell at each step and feeds its hidden state forward. Backprop through time multiplies one
factor per step, so gradients decay or grow exponentially and it struggles with long-range patterns. An LSTM adds a cell state
updated additively, with forget, update and output gates deciding what to keep, so information and gradients travel further.

**Follow-up:** *"LSTM or GRU?"* A GRU has fewer parameters and often similar results, so try it first where size matters. Also
know that setting the forget-gate bias to 1 starts the gate near "keep", and that clipping handles exploding gradients.

**Course:** [sequence models](../../../../data-science/02-deep-learning/notes/05-sequence-models.md#vanishing-gradients-and-the-forget-gate-bias)

#### Q13. Debugging a model that runs but doesn't learn

*"Debug a model that runs but doesn't learn. Identify broadcasting errors and dimension mismatches."*

**Say:** I check the loss at step 0 against what chance would give, then try to overfit one small batch, since a model that
can't memorise a batch has a bug. Next I print the shape at every step, because broadcasting bugs raise no error. The classic is
targets of shape `(n,)` against predictions of shape `(n, 1)`: subtracting them gives `(n, n)`, so the loss compares every
prediction with every target. After that I check the learning rate, gradients, and that the optimiser's steps run in the right
order.

```python
import numpy as np
y = np.arange(4.0)                     # shape (4,)
pred = (y + 0.1).reshape(-1, 1)        # shape (4, 1): off by only 0.1

print((y - pred).shape)                # (4, 4): no error raised
print(((y - pred) ** 2).mean())        # 2.51, the wrong loss
print(((y - pred.squeeze()) ** 2).mean())  # 0.01, the right loss
```

**Follow-up:** *"What other silent bugs do you look for?"* A softmax before a loss that expects logits, forgetting `zero_grad`,
a forgotten `model.eval()`, a transposed batch dimension, and labels shuffled separately from features. Asserting shapes in
tests catches most of the shape bugs.

**Course:** [checks that catch most bugs](../../../../generative-ai/01-llm-fundamentals/notes/12-build-a-tiny-gpt.md#checks-that-catch-most-bugs),
[optimisation and regularisation](../../../../data-science/02-deep-learning/notes/02-optimisation-and-regularisation.md),
[network basics](../../../../data-science/02-deep-learning/notes/01-neural-networks-fundamentals.md), and the
[arrays notebook](../../../../data-analytics/01-python-for-data-analysis/practice/3_Arrays.ipynb) for broadcasting rules. The course
has no note on broadcasting bugs themselves.

#### Q14. The statistics questions

*"Statistics questions: probability, distributions, regression, Bayesian analysis, hypothesis testing."*

This is a topic list, not one question, so the depth lives in the
[stats and experimentation guide](../11-stats-experimentation/interview-guide.md). A short version of each:

**Say:** Probability gives the rules, especially Bayes' rule for updating on evidence, and distributions describe how data
behaves, with the central limit theorem explaining why sample means are often near normal. A hypothesis test asks how surprising
the data would be if there were no effect, and that's the p-value, not the chance the effect is real. Regression estimates how the
outcome moves with each input, holding the others fixed, and GLMs extend it to binary or count outcomes. Bayesian analysis starts
with a prior and returns a posterior, so you can say directly how probable it is that B beats A.

**Follow-up:** *"What does a 95% confidence interval mean?"* The procedure captures the true value 95% of the time over repeated
samples. It isn't a 95% chance for this one interval; that's what a Bayesian credible interval says.

**Course:** [probability and statistics](../../../../data-analytics/02-probability-and-statistics/README.md),
[Bayesian analysis](../../../../data-analytics/04-bayesian-analysis/README.md)

#### Q15. Supervised versus unsupervised

*"Explain supervised vs. unsupervised learning. When would you use each?"*

**Say:** Supervised learning trains on examples with known answers to predict that answer on new rows, as with churn or spam, and
you can score it directly against labels. Unsupervised learning has no labels and looks for structure, such as clusters, or a
compressed representation. I use supervised when I have a target and reliable labels, and unsupervised to explore, segment, detect
anomalies or build features. The catch with unsupervised is that there's no answer key, so judging it takes domain sense.

**Follow-up:** *"How do you evaluate clusters with no labels?"* Silhouette as a rough guide, knowing it favours round clusters, a
comparison with shuffled data, stability across seeds, and whether the business can act on the groups.

**Course:** [problem setting](../../../../data-science/01-classical-ml/notes/01-statistical-foundations.md#the-problem-setting),
[two kinds, one problem](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md#two-kinds-one-problem)

#### Q16. Regularisation: L1, L2 and dropout

*"What is regularization? Compare L1, L2, and dropout."*

**Say:** Regularisation is a cost on complexity that trades a little training fit for better results on new data. L1 penalises
absolute weights and drives some to zero, so it also selects features. L2 penalises squared weights and shrinks all of them, which is
the usual default. Dropout randomly zeroes units during training, which stops a network relying on any one unit, and it's off at test
time.

**Follow-up:** *"Is early stopping regularisation?"* Yes: weights grow with training, so training time acts like penalty strength.
Keep the best weights, not the last. *"Does dropout ever hurt?"* Yes, on a model that already underfits.

**Course:** [regularisation is one idea](../../../../data-science/01-classical-ml/notes/09-training-and-tuning.md#regularisation-is-one-idea),
[dropout in networks](../../../../data-science/02-deep-learning/notes/02-optimisation-and-regularisation.md#regularisation)

#### Q17. Feature scaling

*"What is feature scaling and when is it necessary? Compare normalization vs standardization."*

**Say:** Scaling puts features on comparable ranges so that large-valued columns don't dominate. It's necessary for methods using
distances, gradients or penalties, such as kNN, SVMs, PCA, regularised linear models and neural nets, and trees don't need it because
they only compare a value with a cut. Standardisation gives mean 0 and variance 1, and min-max normalisation squeezes into 0 to 1, but a
single outlier can squash it. Standardisation is my default, fitted on training data only.

**Follow-up:** *"What about outliers?"* Robust scaling, using median and interquartile range. Also, "normalisation" can mean making each
row unit length, as in scikit-learn's `Normalizer`, so clarify which is meant.

**Course:** [preprocessing and scaling](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md#preprocessing-and-scaling)

#### Q18. Cosine similarity in NumPy

*"Implement cosine similarity in NumPy."*

**Say:** Cosine similarity is the dot product divided by the product of the lengths, so it measures direction and ignores magnitude. It
runs from −1 to 1. I handle the zero vector explicitly, because otherwise it divides by zero, and for many vectors I normalise the rows
once and take a matrix product.

```python
import numpy as np

def cosine_similarity(a, b, eps=1e-12):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return 0.0 if denom < eps else float(a @ b / denom)

def cosine_matrix(A, B, eps=1e-12):
    """All pairs: A is (n, d), B is (m, d), result is (n, m)."""
    A = A / np.maximum(np.linalg.norm(A, axis=1, keepdims=True), eps)
    B = B / np.maximum(np.linalg.norm(B, axis=1, keepdims=True), eps)
    return A @ B.T
```

**Follow-up:** *"Why cosine rather than dot product?"* The dot product grows with length. After L2 normalisation, cosine, dot and Euclidean
all give the same ranking, which is why many vector stores normalise and use dot. Returning 0.0 for a zero vector is a choice, so mention it.

**Course:** [similarity and distance](../../../../data-science/03-nlp/notes/04-embeddings-and-similarity.md#similarity-and-distance)

## Sources

- Course: the notes linked in each section of [learn-ai-engineering](../../../../README.md), read November 2026. Measured figures belong to those notes' datasets.
- Rounds: [technical-questions](../../rounds/technical-questions/README.md) for method and drills, [MCQ section B](../../rounds/technical-questions/mcq-bank.md) for self-testing, [case-study](../../rounds/case-study/README.md) for ML cases.
