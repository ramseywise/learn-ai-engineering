---
origin: own lab on open data (UCI Default of Credit Card Clients, CC BY 4.0) and simulated targets and queries, organised around Gneiting's point on scoring functions
sources:
  - ../practice/metric_map.py
  - https://arxiv.org/abs/0912.0902
  - https://doi.org/10.1186/s12864-019-6413-7
  - https://doi.org/10.1371/journal.pone.0118432
  - https://doi.org/10.1109/ICPR.2010.764
  - https://doi.org/10.1145/582415.582418
  - https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-unranked-retrieval-sets-1.html
confidence: high
cleaned: 2026-11-02
---
# Choosing a Metric: Start from the Target

> A metric is a question, and the target and the decision decide which question is worth asking. This chapter is the map: for each kind of target, which loss, which metric, which baseline, and where the detail lives. Two worked runs show what goes wrong when the question and the decision part ways.

**In plain words.** Ask a friend to guess the bill for a round of drinks. Fine them by the square of the error and their best guess is the average bill. Fine them by the plain size of the error and their best guess is the middle bill. Fine them ten times more for guessing low and they will guess high. Same friend, same bills, three right answers. Scoring a model works the same way, so choose the fine before you read the score.

Earlier chapters define most of these metrics where they first came up: [DS 01/04](04-model-evaluation.md) for classification and regression, [DS 01/10](10-imbalance-errors-and-drift.md) for costs on a rare class, [DS 05/01](../../05-time-series-and-recommenders/notes/01-time-series-ml.md) for forecasts, [DS 05/02](../../05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation.md) and [05/03](../../05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md) for ranking. This chapter doesn't repeat them. It connects them, and it adds the argument that says which one to reach for. The code is in [`practice/metric_map.py`](../practice/metric_map.py), and every table below is its output.

## The loss decides what you are estimating

A **loss** is the fine a model pays during training. A **metric** is the score you report afterwards. A **baseline** is the score of the cheapest thing you could do instead. People often choose these three separately, and that is where the trouble starts, because each loss has a particular answer it rewards.

[Gneiting's "Making and Evaluating Point Forecasts"](https://arxiv.org/abs/0912.0902) (JASA 2011; read here in the arXiv version) sets this out for forecasters. Squared error rewards the mean. Absolute error rewards the median. The asymmetric piecewise linear loss, which everyone else calls **pinball loss**, rewards a chosen quantile. Gneiting's warning is that a score means little "unless the scoring function and the forecasting task are carefully matched".

The script takes one skewed target, a lognormal with 100,000 draws (seed 0), and scores four constant forecasts on four metrics:

```python
y = np.random.default_rng(seed).lognormal(mean=0.0, sigma=1.0, size=n)
forecasts = {"the mean": y.mean(), "the median": np.median(y), "90th percentile": np.quantile(y, 0.9),
             "best for MAPE": grid[np.argmin([mape(c) for c in grid])]}
```

```text
                 forecast   RMSE    MAE  pinball 0.9   MAPE
the mean            1.648  2.191  1.261        0.631  1.978
the median          0.996  2.286  1.125        0.824  1.125
90th percentile     3.586  2.925  2.505        0.477  4.994
best for MAPE       0.367  2.538  1.323        1.174  0.684
share of outcomes above the MAPE forecast: 0.842
```

Each column has a different winner, and the winner is the forecast built for that column. Nothing here is a better or worse model, since all four are one number. RMSE picks the mean, MAE the median, pinball the 90th percentile. So "which forecast is best?" has no answer until someone says which decision it feeds. Stocking a shop where a stock-out costs nine times an overstock is a 90th-percentile decision, and [DA 06/01](../../../data-analytics/06-applied-analyses/notes/01-forecasting.md) works that kind of critical ratio through.

The last row is the warning about MAPE, the mean absolute percentage error. Its favourite forecast is 0.367, far under the median of 0.996, and about 84% of outcomes sit above it. A percentage error is largest when the actual value is small, and an overforecast can be penalised without limit while an underforecast can't go past 100%. So MAPE rewards forecasting low. Gneiting's simulation reaches the same place with three forecasters. A statistician knows the process and predicts the true conditional mean, an optimist always says 5, and a pessimist always says 0.05. Yet "the pessimist has the best (lowest) score both under the absolute error and the absolute percentage error scoring functions". A team judged on MAPE, whether it knows this or not, is being paid to underforecast.

Two limits on the idea, both Gneiting's. It runs one way only: squared error implies the mean, but the mean doesn't imply squared error, since a whole family of losses (the Bregman functions) also rewards it. And the paper is about scoring forecasts, with estimation only as a closing analogy. Two workable routes follow from it. Either name the score up front and let forecasters optimise it, or name the quantity you want, such as the 90th percentile, and score with something that rewards it.

## The map

| Target | Model family | Loss | Metric | Baseline | Detail |
|---|---|---|---|---|---|
| Continuous | OLS, boosted regressors | Squared or absolute error | RMSE, MAE, R² out of sample, adjusted R² in sample | Predict the mean | [DS 01/04](04-model-evaluation.md#multiclass-and-regression-metrics), [DA 02/06](../../../data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md), adjusted R² in [DA 02/07](../../../data-analytics/02-probability-and-statistics/notes/07-data-generating-process.md#comparing-models) |
| Binary | Logistic, boosted trees | Log loss | PR-AUC, ROC-AUC, Brier, Matthews correlation, balanced accuracy, cost at a threshold | Base rate, majority class | [DS 01/04](04-model-evaluation.md#confusion-matrix-precision-recall-f1), [DS 01/10](10-imbalance-errors-and-drift.md#accuracy-lies-errors-cost) |
| Count | Poisson, negative binomial | Poisson deviance | Deviance, dispersion, MAE | Constant rate | [DA 02/06](../../../data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md#poisson-and-other-glms) |
| Ranking | Two-tower, retrieval, learning to rank | Pairwise or listwise | NDCG, MRR, recall at k | Popularity | [DS 05/02](../../05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation.md#the-metric-that-matters-top-n-ranking), [DS 05/03](../../05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md#offline-evaluation-sampled-metrics), [GA 08/07](../../../generative-ai/08-eval/notes/07-evaluating-rag-and-grounding.md#retrieval-metrics) |
| Clusters | k-means, hierarchical | Inertia, or none | Silhouette without labels, Adjusted Rand Index for stability or known labels | Permuted control | [DS 01/05](05-unsupervised-learning.md), [DA 06/05](../../../data-analytics/06-applied-analyses/notes/05-segmentation-and-rfm.md) |
| Forecast | ETS, boosting on lags | Squared error, pinball | MASE, pinball; MAPE with its warning | Seasonal naive | [DS 05/01](../../05-time-series-and-recommenders/notes/01-time-series-ml.md#baselines-and-a-scale-free-metric), [DA 06/01](../../../data-analytics/06-applied-analyses/notes/01-forecasting.md) |

Read it from left to right. The target narrows the family, the family brings a loss, and the decision picks a metric. The last column before the links matters most. A metric with no baseline can't be read: an RMSE of 2 is good or bad depending on what predicting the mean gets, and MASE builds this in by dividing by the seasonal naive error. The cluster row has the oddest baseline, because the structure itself is in doubt: [DS 01/05](05-unsupervised-learning.md#case-clustering-a-music-library) shuffles each column to destroy any real groups and watches silhouette fall from 0.258 to 0.107, so a higher score than the shuffled data is the least you should ask.

Note the training loss and the metric needn't match. Boosted trees train on log loss and get judged on cost at a threshold. What has to hold is that the metric matches the decision, and that the loss estimates something the metric can use. Log loss gives probabilities, and a threshold needs probabilities.

## A worked example: the rare class

Here is the binary row on the credit lab's 3% data from [DS 01/10](10-imbalance-errors-and-drift.md#the-data-and-a-choice-we-made), with its 5:1 cost ratio and decline threshold of 1/6. Two metrics join the usual ones.

**Balanced accuracy** is the mean of recall on each class, $\tfrac12(TP/P + TN/N)$, where $P$ and $N$ count the actual positives and negatives. [Brodersen et al.](https://doi.org/10.1109/ICPR.2010.764) (ICPR 2010) make the case for it: "if the conventional accuracy is high only because the classifier takes advantage of an imbalanced test set, then the balanced accuracy, as desired, will drop to chance."

**Matthews correlation (MCC)** is the Pearson correlation between predicted and true labels, $(TP\cdot TN - FP\cdot FN)/\sqrt{(TP+FP)(TP+FN)(TN+FP)(TN+FN)}$. It runs from −1 through 0 at chance to 1. [Chicco and Jurman](https://doi.org/10.1186/s12864-019-6413-7) (BMC Genomics 2020) argue it beats accuracy and F1 once you have a threshold, because it scores high "only if the prediction obtained good results in all of the four confusion matrix categories". [DS 01/04](04-model-evaluation.md#confusion-matrix-precision-recall-f1) has both on a smaller example.

```python
models, yva, yte = scored(raw, seed=0)
print(pd.DataFrame({k: report(yte, v[1], lab.BAYES) for k, v in models.items()}).T.round(3))
```

```text
--- 3% default rate, test set 4818 rows, 145 defaulters, seed 0 ---
decisions at the 5:1 threshold, 1/6; cost per 1,000 applicants
                  accuracy  balanced    MCC  PR-AUC  ROC-AUC  Brier     cost  declined
approve everyone     0.970     0.500  0.000   0.030    0.500  0.029  150.477     0.000
tree, depth 2        0.948     0.599  0.184   0.085    0.667  0.028  144.666     0.035
logistic             0.966     0.508  0.036   0.089    0.711  0.029  152.345     0.006
boosted              0.958     0.548  0.122   0.120    0.750  0.028  148.609     0.018

mean over seeds 0-9 (a new rare subset and split each time)
                  accuracy  balanced    MCC  PR-AUC  ROC-AUC  Brier     cost  declined
model
approve everyone     0.970     0.500  0.000   0.030    0.500  0.029  150.477     0.000
tree, depth 2        0.950     0.605  0.199   0.102    0.684  0.028  141.428     0.034
logistic             0.964     0.531  0.105   0.118    0.729  0.028  147.904     0.010
boosted              0.954     0.592  0.188   0.143    0.761  0.028  141.490     0.028
seeds where each metric ranks 'approve everyone' above 'tree, depth 2':
  accuracy  10 of 10
  balanced   0 of 10
  MCC        0 of 10
  PR-AUC     0 of 10
  cost       1 of 10
```

Accuracy puts the model that does nothing first. On all ten seeds, it ranks approving everyone above a two-level decision tree, even though the tree costs less on nine of the ten. Every other metric here sees through that, including Brier if you compare it with the baseline's 0.029 and don't read it alone. That is the accuracy failure, and it took one column to show.

The other columns disagree among themselves, and that is more useful. Averaged over seeds, the boosted model and the shallow tree tie on cost (141.5 and 141.4 per 1,000 applicants) and on MCC, while boosting ranks far better on PR-AUC (0.143 against 0.102). They answer different questions. PR-AUC asks how good the ordering is across every threshold, and cost asks what happens at this one. At a 3% base rate, few applicants reach a probability of 1/6 at all, so a better ordering mostly changes rows that aren't declined either way. If the threshold is settled, the cost column decides. If it will move, or if the scores feed something else, the ordering matters.

### What each metric would do with the threshold

A metric doesn't just report a threshold. If you tune against it, it chooses one. The boosted model's threshold is chosen on validation by each metric, then scored on test:

```text
--- boosted model: threshold chosen on validation by each metric, scored on test (seed 0) ---
                       t  declined  cost 5:1  cost 20:1
accuracy           0.448     0.000   150.477    601.910
balanced accuracy  0.029     0.266   303.030    471.150
MCC                0.078     0.053   150.062    467.621
cost 5:1, tuned    0.223     0.010   148.817    572.229
cost 20:1, tuned   0.052     0.101   172.893    428.186
approve everyone costs 150.5 at 5:1, 601.9 at 20:1
N/P on this test set is 32.2
```

![Three metrics against threshold on the 3% credit data, each peaking in a different place, above the cost per 1,000 applicants at 5:1. Accuracy peaks at thresholds where almost nobody is declined, balanced accuracy peaks near 0.03, Matthews correlation near 0.06, cost near 0.11.](../../sources/images/metric-map-threshold.png)

Dots in the figure mark each line's best on the test set, so they sit a little apart from the validation choices in the table.

Accuracy's pick declines nobody. Balanced accuracy's pick declines 27% of applicants and costs 303 per 1,000 at 5:1, twice the 150.5 of approving everyone. That isn't a defect in balanced accuracy, and a little algebra shows why. Since $\text{balanced accuracy} = 1 - \tfrac12(FN/P + FP/N)$, maximising it is the same as minimising $N\cdot FN + P\cdot FP$. So it is a cost ratio, of $N:P$. On this test set that means 32:1. Balanced accuracy pretends a missed defaulter costs 32 good customers, which is right for nobody here, and it changes that ratio whenever the base rate changes.

MCC's pick is close to the cost-tuned one at 5:1 (150.1 against 148.8, a small gap on one seed) and further from it at 20:1 (467.6 against 428.2). MCC has no cost in it, so it has no way to respond when the ratio changes: it picks the same threshold at both. Chicco and Jurman's paper doesn't discuss costs, and its scope is cases with a threshold; without one, it advises PR and ROC curves. So use MCC or balanced accuracy to check that a thresholded classifier isn't a trick when nobody can give you costs, and use cost when somebody can.

MCC also isn't quite the all-four-categories guarantee the quote suggests. Here are Chicco and Jurman's case A1 and a table of our own:

```text
Chicco and Jurman A1           accuracy 0.900  recall 0.989  balanced 0.495  MCC -0.032
recall 0.45, no false alarms   accuracy 0.945  recall 0.450  balanced 0.725  MCC 0.651
```

The first row is theirs: accuracy looks excellent, and MCC reports that the classifier is no better than chance. The second is ours: MCC reaches 0.65 while the classifier misses 55% of positives. Whether that counts as high is a judgement, but a lender would have a view. The paper also says MCC is "unaffected by the unbalanced datasets issue", and the next run doesn't support that.

### ROC holds roughly still, and PR moves

[Saito and Rehmsmeier](https://doi.org/10.1371/journal.pone.0118432) (PLoS ONE 2015) title their paper for this: the PR plot is more informative than ROC on imbalanced data. Their evidence is about reading, not about information, since each ROC point maps to one PR point. The defect they name is "an intuitive but wrong interpretation of specificity". With 1,000 positives and 10,000 negatives, 500 true positives with 1,600 false positives gives the same ROC point as 500 and 160 with 1,000 negatives, but precision of 25% against 75%. Here is the same effect with one fitted model scored at two base rates:

```text
--- one model, trained at 22.1%, scored on the natural test set and on a 3% subset of it ---
natural    rows  6000  rate 0.221  ROC-AUC 0.766  PR-AUC 0.535  balanced 0.694  MCC 0.326  accuracy 0.679
3% subset  rows  4818  rate 0.030  ROC-AUC 0.779  PR-AUC 0.167  balanced 0.700  MCC 0.144  accuracy 0.670
```

ROC-AUC moves by a little, and only because the 3% subset keeps a random 145 of the test set's defaulters. PR-AUC falls from 0.535 to 0.167, and this is the honest drop: precision depends on the base rate. Read PR-AUC against its baseline, which is the base rate itself (0.221 and 0.030 here). Balanced accuracy stays put, as its formula says it should. MCC halves with the same model and threshold, which is the contradiction with "unaffected". Neither is wrong to do this: they answer different questions. If the deployed base rate differs from your test set, ROC and balanced accuracy tell you about the model and PR-AUC tells you what the user will see.

## Counts

Deviance is the count row's version of squared error: how much worse the model's log likelihood is than a model that fits each row exactly. The Poisson form is $\tfrac{2}{n}\sum_i\big[y_i\log(y_i/\hat\mu_i) - (y_i - \hat\mu_i)\big]$, and `mean_poisson_deviance` computes it. Dispersion is the Pearson statistic per degree of freedom, $\sum_i (y_i-\hat\mu_i)^2/\hat\mu_i\,/(n-p)$, and it should be near 1 if the Poisson's variance assumption holds. On simulated counts with extra variance (one real predictor, one column of noise, a gamma multiplier, seed 0):

```text
constant rate  deviance 2.672  D2 -0.000  MAE 1.721  dispersion 3.23
Poisson model  deviance 1.968  D2 +0.263  MAE 1.494  dispersion 2.01
```

The Poisson model beats the constant rate on deviance and MAE, and D², the deviance version of R², says it removes 26% of the constant-rate deviance. Dispersion of 2.01 says the point predictions are usable but the Poisson's standard errors would be too small, which is why the map also names the negative binomial. MAE is still useful on the row, because it speaks to a stakeholder in counts. The GLM itself is in [DA 02/06](../../../data-analytics/02-probability-and-statistics/notes/06-regression-and-glms.md#poisson-and-other-glms).

## Ranking: the table swept along the list

Ranking looks like a separate world, and it isn't. Precision and recall at k are the same confusion table at one cut-off, with k as the threshold. For one simulated query with 100 documents and 5 relevant:

```text
     TP  FP  FN  TN  precision  recall  accuracy
k
1     1   0   4  95       1.00     0.2      0.96
3     2   1   3  94       0.67     0.4      0.96
5     2   3   3  92       0.40     0.4      0.94
10    4   6   1  89       0.40     0.8      0.93
20    4  16   1  79       0.20     0.8      0.83
100   5  95   0   0       0.05     1.0      0.05
relevant documents at positions [1, 2, 8, 10, 50]
```

Read the accuracy column. It is 0.96 at k = 1, where four of the five relevant documents are missed, and falls as the list gets more complete. [Manning, Raghavan and Schütze](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-unranked-retrieval-sets-1.html) derive precision and recall from this table and explain why accuracy fails: "normally over 99.9% of the documents are in the nonrelevant category", so "a system tuned to maximize accuracy can appear to perform well by simply deeming all documents nonrelevant to all queries." True negatives are the rest of the corpus, and they say nothing.

MRR and NDCG go a step further. They weight positions, so no single confusion table produces them; they summarise across cut-offs.

- **MRR**, mean reciprocal rank, averages $1/\text{rank}$ of the first relevant result. It stops looking after that one.
- **NDCG**, normalised discounted cumulative gain, sums the gain at each position with a discount for depth, then divides by the score of the ideal ordering. [Järvelin and Kekäläinen](https://doi.org/10.1145/582415.582418) (ACM TOIS 2002) introduced it to reward graded relevance and to discount documents found late. Theirs divides by $\log_b(\text{rank})$. `sklearn.metrics.ndcg_score` divides by $\log_2(\text{rank}+1)$, as do most libraries. So NDCG figures from different tools or papers needn't agree.

Two rankers built to differ show them disagreeing. The finder lifts one relevant document by 4 standard deviations and does nothing for the rest, like a search engine that nails the single best match. The broad ranker lifts all five by 1.7.

```python
def mrr(rel, score):
    order = np.argsort(-score, axis=1)
    hits = np.take_along_axis(rel, order, axis=1)
    return np.mean(1 / (hits.argmax(axis=1) + 1))  # argmax finds the first relevant position
```

```text
--- 500 simulated queries, 100 documents, 5 relevant each ---
          MRR  NDCG@10  recall@10
ranker
finder  0.952    0.375      0.272
broad   0.816    0.588      0.614
mean over seeds 0-4
          MRR  NDCG@10  recall@10
ranker
broad   0.810    0.589      0.614
finder  0.947    0.374      0.273
```

The finder wins MRR by 0.14, and the broad ranker wins NDCG@10 by 0.21 and more than doubles recall. The two lifts were set to make the point, so this tells you the metrics can disagree and says nothing about how often real rankers do. Which one is right depends on the task. If one good answer ends the search, MRR measures that. If the answer needs several sources, NDCG and recall do. On a [RAG pipeline](../../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md#measure-each-stage), a factoid question and a question that spans four documents can want different metrics from the same retriever, and [DS 05/03](../../05-time-series-and-recommenders/notes/03-two-tower-and-evaluation.md#offline-evaluation-sampled-metrics) computes all three on real recommenders. Remember to compare against popularity, the baseline in the map, before believing any of them.

## One table, four jobs

Every retrieval, ranking, judge and guardrail metric in the later subjects is this table with different labels.

| | Credit model | Retrieval and RAG | LLM judge | Guardrail |
|---|---|---|---|---|
| Positive class | Will default | Chunk is relevant | Output passes ([GA 08/05](../../../generative-ai/08-eval/notes/05-llm-as-judge.md)'s convention) | Input is an attack |
| Predicted positive | Declined | Retrieved in top k | Judge passes it | Guard blocks it |
| False positive | Good customer declined | Irrelevant chunk spends context budget | Judge passes a bad output | Benign message blocked |
| False negative | Defaulter approved | Relevant chunk missed, so the answer can't be grounded | Judge fails a good output | Attack gets through |
| True negative | Good customer approved | Rest of the corpus, so huge accuracy means nothing | Judge fails a bad output | Benign message allowed |
| Threshold | Score cut-off | k | Judge prompt and any score cut-off | Guard threshold |

Each later note has its own version. [GA 08/07](../../../generative-ai/08-eval/notes/07-evaluating-rag-and-grounding.md#retrieval-metrics) sets out hit rate, recall and precision at k, [GA 02/03](../../../generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search.md) compares retrievers, [AIE 02/12](../../../ai-engineering/02-context-engineering/notes/12-evaluating-context.md#metrics-by-lever) reads low precision as budget spent on distractors, [GA 08/05](../../../generative-ai/08-eval/notes/05-llm-as-judge.md) treats the judge as a classifier, and [AIE 09/03](../../../ai-engineering/09-safety-and-security/notes/03-guardrail-models.md) tunes a guard. The questions carry over too: state the positive class before naming the errors, since the judge row flips it, set the threshold from what the errors cost, and be suspicious of any number that true negatives can inflate. The [next chapter](12-reading-the-errors.md) takes the same table and reads what falls into its cells.

## Pitfalls

- **Choosing the metric after seeing the scores.** Six metrics give you six chances to find one your model wins. Write it down first, from the decision.
- **Reading a score without its baseline.** A PR-AUC of 0.17 at a 3% base rate is a lot more than it sounds. A Brier of 0.028 is barely more than doing nothing.
- **Treating balanced accuracy as cost-free.** It is a cost ratio of $N:P$, and it changes when the base rate does. On the 3% data, tuning against it cost twice what approving everyone would.
- **Treating MCC as a guarantee.** It reached 0.65 with recall of 0.45, and it moved by half on the same model between base rates. It also isn't defined when a row or column of the table is empty, and scikit-learn returns 0 there.
- **Judging a forecast on MAPE and wondering why it runs low.** MAPE's favourite forecast sat well below the median.
- **Comparing PR-AUC across different base rates.** The drop from 0.535 to 0.167 was the same model.
- **Reporting MRR when the task needs several documents.** It can't see anything past the first hit.
- **Mixing NDCG definitions.** Gain, discount and cut-off all vary. State them, and compare only like with like.
- **Tuning against the metric you report.** The threshold table above was chosen on validation and scored on test. Choosing and scoring on one set flatters every row.

## Try it

1. In the four-forecast table, which forecast would a team choose if bonuses were paid on MAPE? What would that do to a shop's stock?
2. What cost ratio does balanced accuracy imply on the natural 22.1% credit data? How does this compare with the 5:1 the lab assumes?
3. How large does the finder's lift have to be before it beats the broad ranker on MRR? Change the lift in `simulate_rankers` and find out.
4. In the single-query sweep, accuracy is 0.96 when recall is 0.2. Which cell of the table is responsible, and what would you report instead?
5. A colleague reports MCC 0.65 on a fraud model and calls it strong. Which single further question would you ask, and why?

<details><summary>Answers</summary>

1. The 0.367 forecast, far below the median of 0.996. A shop stocked to it would run out most of the time, since about 84% of outcomes sit above it.
2. $N:P = 0.779/0.221$, about 3.5:1, and it would be 32:1 at the 3% rate. So balanced accuracy is closer to the lab's 5:1 on natural data than on the rare data, by accident of the base rate.
3. Between 3 and 4 on seed 0. Output from the script:

```text
lift 1  finder MRR 0.253  NDCG@10 0.127  broad MRR 0.816  NDCG@10 0.588
lift 2  finder MRR 0.512  NDCG@10 0.236  broad MRR 0.816  NDCG@10 0.588
lift 3  finder MRR 0.793  NDCG@10 0.330  broad MRR 0.816  NDCG@10 0.588
lift 4  finder MRR 0.952  NDCG@10 0.375  broad MRR 0.816  NDCG@10 0.588
```

The broad ranker's NDCG@10 stays well ahead at every lift, so MRR flips and NDCG doesn't.

4. True negatives: 95 of the 100 documents. Report precision and recall at k, or MRR and NDCG.
5. What is its recall? The table from the MCC section reaches 0.65 while missing 55% of positives, and fraud costs follow the misses.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What does squared error estimate? Absolute error? Pinball? | Mean, median and a chosen quantile. So the loss has to match the decision. |
| Why is MAPE risky? | It rewards forecasting low: percentage errors blow up on small actuals. In the run its best forecast was 0.367 against a median of 0.996. |
| What does accuracy miss on rare classes? | The always-negative model scores the base rate. It ranked approve-everyone first on 10 of 10 seeds. |
| What is balanced accuracy, in cost terms? | Minimising it is minimising errors at a cost ratio of N:P. It is 32:1 on the 3% data, and changes with the base rate. |
| When use Matthews correlation? | With a threshold and no costs, as a check for a trick classifier. It gives 0 for always-negative and needs all four cells. It isn't a cost and can stay high with poor recall. |
| ROC or PR on imbalanced data? | Both come from the same ranking. ROC-AUC barely moves with base rate (0.766 and 0.779), and PR-AUC shows what users see (0.535 and 0.167). Read PR-AUC against the base rate. |
| What is deviance? | The count and GLM analogue of squared error: twice the gap in log likelihood from a model that fits every row exactly. Compare to a constant rate. |
| What does dispersion near 2 mean? | Variance about twice what the Poisson assumes, so the standard errors are too small. Consider negative binomial. |
| MRR or NDCG? | MRR when the first good result ends the task, NDCG when several matter or relevance is graded. They can rank systems differently. |
| How are retrieval metrics related to the confusion matrix? | P and R at k are one table with k as threshold. TN is the rest of the corpus. MRR and NDCG weight position, so they summarise across cut-offs. |
| What baseline for each target? | Mean, base rate, constant rate, popularity, permuted control, seasonal naive. |

## Next

[Reading the errors](12-reading-the-errors.md): a metric says how much the model gets wrong. The next chapter finds which rows, why, and how to learn from them without fitting to them.
