---
origin: curated
sources:
  - ../sources/
confidence: high
cleaned: 2026-11-01
---
# 05-time-series-and-recommenders references

★ = changed a claim in the notes. ⚑ = preprint only. PDFs we hold live in the shared [`../sources/`](../sources/) and are linked from their row; every other row links the public copy read when writing the note. Notes: [01 time series](notes/01-time-series-ml.md), [02 collaborative filtering](notes/02-collaborative-filtering-and-matrix-factorisation.md), [03 two towers and evaluation](notes/03-two-tower-and-evaluation.md), [04 entity matching and learning to rank](notes/04-entity-matching-and-learning-to-rank.md).

## Books

| Book | Why read it | Local | Maps to |
|---|---|---|---|
| Hyndman and Athanasopoulos, [*Forecasting: Principles and Practice*, 3rd ed.](https://otexts.com/fpp3/) (OTexts, free online) | The statistical side this chapter skips: ETS, ARIMA, hierarchies, and the [time series cross-validation](https://otexts.com/fpp3/tscv.html) section behind our backtest | web only | [01](notes/01-time-series-ml.md) |
| Christen, [*Data Matching*](https://doi.org/10.1007/978-3-642-31164-2) (Springer, 2012) | The standard book on record linkage. Further reading only: behind a paywall, not read, bibliographic record checked, and no claim in the notes rests on it | none | [04](notes/04-entity-matching-and-learning-to-rank.md) |

## Core papers

### Time series

| Paper | Why read it | Link | Maps to |
|---|---|---|---|
| ★ Makridakis, Spiliotis and Assimakopoulos, *M5 accuracy competition: results, findings, and conclusions* (*IJF*, 2022) | 42,840 Walmart series. LightGBM and cross-learning dominate, yet only 35.8% of teams beat seasonal naive. Sets our default of features plus trees | [page](https://ideas.repec.org/a/eee/intfor/v38y2022i4p1346-1364.html) | [01](notes/01-time-series-ml.md#feature-based-models) |
| ★ Zeng, Chen, Zhang and Xu, *Are Transformers Effective for Time Series Forecasting?* (AAAI 2023) | One linear layer beat Transformers on nine long-horizon datasets. Source of DLinear, which we implement | [arXiv](https://arxiv.org/abs/2205.13504) | [01](notes/01-time-series-ml.md#sequence-models) |
| ★ Bergmeir, Hyndman and Koo, *A note on the validity of cross-validation for evaluating autoregressive time series prediction* (*CSDA*, 2018) | When K-fold is actually fine, which corrects the blanket rule | [DOI](https://doi.org/10.1016/j.csda.2017.11.003) | [01](notes/01-time-series-ml.md#a-backtest-that-matches-the-decision) |
| Hyndman and Koehler, *Another look at measures of forecast accuracy* (*IJF*, 2006) | Why percentage errors fail, and the case for MASE | [DOI](https://doi.org/10.1016/j.ijforecast.2006.03.001) | [01](notes/01-time-series-ml.md#baselines-and-a-scale-free-metric) |
| Salinas, Flunkert, Gasthaus and Januschowski, *DeepAR* (*IJF*, 2020) | The global, probabilistic RNN forecaster | [arXiv](https://arxiv.org/abs/1704.04110) | [01](notes/01-time-series-ml.md#sequence-models) |
| ⚑ Bai, Kolter and Koltun, *An Empirical Evaluation of Generic Convolutional and Recurrent Networks for Sequence Modeling* (2018) | Dilated causal convolutions beat canonical LSTMs on sequence tasks | [arXiv](https://arxiv.org/abs/1803.01271) | [01](notes/01-time-series-ml.md#sequence-models) |
| Oreshkin, Carpov, Chapados and Bengio, *N-BEATS* (ICLR 2020) | A deep fully connected stack competitive on M3, M4 and TOURISM | [arXiv](https://arxiv.org/abs/1905.10437) | [01](notes/01-time-series-ml.md#sequence-models) |
| Januschowski et al., *Forecasting with trees* (*IJF*, 2022) | Review of why trees work so well for forecasting. Listed as further reading; abstract only was checked | [DOI](https://doi.org/10.1016/j.ijforecast.2021.10.004) | [01](notes/01-time-series-ml.md#feature-based-models) |
| Fanaee-T and Gama, *Event labeling combining ensemble detectors and background knowledge* (*Progress in AI*, 2014) | Required citation for the Bike Sharing data | [DOI](https://doi.org/10.1007/s13748-013-0040-3) | [01](notes/01-time-series-ml.md) |
| ★ Montero-Manso and Hyndman, *Principles and algorithms for forecasting groups of time series: Locality and globality* (*IJF*, 2021) | Global models need no similarity between series, and a random partition can help a constrained model. Sets our expectation for per-segment against global | [DOI](https://doi.org/10.1016/j.ijforecast.2021.03.004), [PDF](../sources/montero-manso-2021-locality-globality.pdf) | [01](notes/01-time-series-ml.md#case-forecasting-each-segments-cash-flow) |
| Bandara, Bergmeir and Smyl, *Forecasting across time series databases using recurrent neural networks on groups of similar series: A clustering approach* (*Expert Systems with Applications*, 2020) | The case for one model per cluster, with a gain on one dataset, none on another, and simple exponential smoothing beating both on the first | [DOI](https://doi.org/10.1016/j.eswa.2019.112896), [PDF](../sources/bandara-2020-forecasting-across-time-series.pdf) | [01](notes/01-time-series-ml.md#case-forecasting-each-segments-cash-flow) |

### Entity matching and learning to rank

| Paper | Why read it | Link | Maps to |
|---|---|---|---|
| ★ Fellegi and Sunter, *A Theory for Record Linkage* (*JASA* 64(328), 1969) | $m$ and $u$, additive weights, the three-way decision, and blocking as implicit non-links. Read in full in the US Internal Revenue Service's reprint, an OCR copy that drops some formula symbols; the journal page not read | [reprint](https://www.irs.gov/pub/irs-soi/1985preprintar28.pdf), [DOI](https://doi.org/10.1080/01621459.1969.10501049) | [04](notes/04-entity-matching-and-learning-to-rank.md#scoring-a-pair-fellegi-and-sunter) |
| ★ Burges, *From RankNet to LambdaRank to LambdaMART: An Overview* (Microsoft Research TR-2010-82) | The gradient factorisation, why NDCG has no gradient, and the $\lvert\Delta\text{NDCG}\rvert$ factor we test. Read in full. It reports no experiments of its own | [PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/MSR-TR-2010-82.pdf) | [04](notes/04-entity-matching-and-learning-to-rank.md#why-ndcg-cant-be-optimised-directly-and-lambdamart) |
| ★ Bruch, *An Alternative Cross Entropy Loss for Learning-to-Rank* (WWW 2021) | XE-NDCG, and the objection that LambdaMART has no loss. Read in full. It beat LambdaMART on his sets and lost to it on ours. Added beyond the plan's list, for the listwise case | [arXiv](https://arxiv.org/abs/1911.09798), [DOI](https://doi.org/10.1145/3442381.3449794) | [04](notes/04-entity-matching-and-learning-to-rank.md#the-results) |
| Li, Li, Suhara, Doan and Tan, *Deep Entity Matching with Pre-Trained Language Models* (*PVLDB* 14(1), 2020) | Ditto: sequence-pair classification on serialised records, and its warning about numeric data. Read in full. The abstract says up to 29% and its Table 5 shows 31.89 points. Not run here | [arXiv](https://arxiv.org/abs/2004.00584), [DOI](https://doi.org/10.14778/3421424.3421431) | [04](notes/04-entity-matching-and-learning-to-rank.md#where-a-language-model-fits) |
| ★ Wang et al., *Bridging the Gap between Reality and Ideality of Entity Matching* (IJCAI 2022) | Measured how much of the common benchmarks' test data appears in training, and how far scores fall on unseen entities: Ditto 93.06 to 67.82, text only at 1:3 mismatches | [arXiv](https://arxiv.org/abs/2205.05889) | [04](notes/04-entity-matching-and-learning-to-rank.md#splitting-pairs-without-leaking-the-answer) |
| ★ Peeters, Der and Bizer, *WDC Products* (EDBT 2024) | A benchmark built on the seen and unseen dimension, with corner cases and three training sizes. Most matchers fall on unseen products. Magellan's similarity features stay level, but well below the neural models (36.61 against Ditto's 70.24). The identity reading is ours | [arXiv](https://arxiv.org/abs/2301.09521) | [04](notes/04-entity-matching-and-learning-to-rank.md#splitting-pairs-without-leaking-the-answer) |
| De Meer Pardo et al., *GraLMatch: Matching Groups of Entities with Graphs and Language Models* (EDBT 2025) | Pairwise F1 against group F1 before and after cleanup. With DistilBERT on real companies 96.53 falls to 56.92 and recovers to 91.64; its securities data doesn't fall | [arXiv](https://arxiv.org/abs/2406.15015) | [04](notes/04-entity-matching-and-learning-to-rank.md#splitting-pairs-without-leaking-the-answer) |
| Park and Marcotte, *Flaws in evaluation schemes for pair-input computational predictions* (*Nature Methods*, 2012) | The classic statement of pair-class leakage, from protein interactions, and when a seen-entity score is still fine | [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3531800/) | [04](notes/04-entity-matching-and-learning-to-rank.md#splitting-pairs-without-leaking-the-answer) |

### Learning a similarity function

| Paper | Why read it | Link | Maps to |
|---|---|---|---|
| ★ Musgrave, Belongie and Lim, *A Metric Learning Reality Check* (ECCV 2020) | 13 losses under one fair protocol on three vision datasets: training is the big step, and newer losses barely beat 2006 contrastive. Vision only. Read in full | [arXiv:2003.08505](https://arxiv.org/abs/2003.08505) | notes/05 |
| Schroff, Kalenichenko and Philbin, *FaceNet* (CVPR 2015) | The warning that the hardest negatives can collapse a model. The benefit of semi-hard is asserted, not measured | [arXiv:1503.03832](https://arxiv.org/abs/1503.03832) | notes/05 |
| Khosla et al., *Supervised Contrastive Learning* (NeurIPS 2020) | Closed-set image classification, under one point of gain on ImageNet. Not evidence about retrieval | [arXiv:2004.11362](https://arxiv.org/abs/2004.11362) | notes/05 |
| ★ Huang et al., *Embedding-based Retrieval in Facebook Search* (KDD 2020) | Non-click negatives cost 55% recall, online and offline mining rationed, rank 101 to 500 best, hard-only no better than random. Not reproducible | [arXiv:2006.11632](https://arxiv.org/abs/2006.11632) | notes/05 |
| Karpukhin et al., *Dense Passage Retrieval* (EMNLP 2020) | One BM25 negative added to in-batch training helps, and a second doesn't | [arXiv:2004.04906](https://arxiv.org/abs/2004.04906) | notes/05 |
| Xiong et al., *Approximate Nearest Neighbor Negative Contrastive Learning* (ANCE, ICLR 2021) | Negatives sampled from the current model's top 200, refreshed asynchronously: with BM25 warm-up, MRR@10 0.330 against 0.279 and 0.280 for warmed in-batch on MS MARCO. No frozen baseline. Read in full ([PDF](../../generative-ai/02-rag-retrieval/sources/xiong-2021-approximate-nearest-neighbor-negative-contrastive.pdf)) | [arXiv:2007.00808](https://arxiv.org/abs/2007.00808) | notes/05 |
| ★ Wang et al., *GPL: Generative Pseudo Labeling* (NAACL 2022) | Tuning with no labels on six BeIR sets: narrows the gap to a reranker without closing it, and hard negatives lost 2.5 points through false negatives | [arXiv:2112.07577](https://arxiv.org/abs/2112.07577) | notes/05 |
| ★ Peeters and Bizer, *Supervised Contrastive Learning for Product Matching* (WWW 2022 companion) | Contrastive gain shrinks as labels grow, from 8.84 to 0.84 F1 points on WDC Computers. A four-page poster | [arXiv:2202.02098](https://arxiv.org/abs/2202.02098) | notes/05 |
| Thakur et al., *Augmented SBERT* (NAACL 2021) | A bi-encoder trails a cross-encoder at 1,400 to 10,000 samples, and silver labels close most of the gap | [arXiv:2010.08240](https://arxiv.org/abs/2010.08240) | notes/05 |
| ⚑ Rosa et al., *In Defense of Cross-Encoders for Zero-Shot Retrieval* | Bi-encoders match cross-encoders when training and test are similar, and the gap opens when they differ | [arXiv:2212.06121](https://arxiv.org/abs/2212.06121) | notes/05 |
| Zeakis et al., *Pre-trained Embeddings for Entity Resolution* (PVLDB 2023) | 12 language models on 17 datasets: SentenceBERT gains less from last-layer tuning than BERT-style models, on pair classification over five of them. Conclusions read closely, not every table | [arXiv:2304.12329](https://arxiv.org/abs/2304.12329) | notes/05 |
| Databricks, *Improving retrieval and RAG with embedding model finetuning* (vendor blog, February 2025) | Base and tuned recall@10 on three datasets, from no gain to large. Small test sets, vendor | [Blog](https://www.databricks.com/blog/improving-retrieval-and-rag-embedding-model-finetuning) | notes/05 |
| `sentence-transformers` 6 documentation | The default loss, `mine_hard_negatives`, and the Euclidean margin default on `BatchSemiHardTripletLoss` | [Losses](https://sbert.net/docs/sentence_transformer/loss_overview.html), [loss reference](https://sbert.net/docs/package_reference/sentence_transformer/losses.html), [sampler](https://sbert.net/docs/package_reference/sentence_transformer/sampler.html), [mining](https://sbert.net/docs/package_reference/util/hard_negatives.html) | notes/05 |
| Weaviate, *Fine-tune an embedding model* (vendor blog) | The source of the "1,000 to 5,000 samples" figure for narrow domains, which cites no study. A claim to check, not evidence | [Blog](https://weaviate.io/blog/fine-tune-embedding-model) | notes/05 |

### Recommenders

| Paper | Why read it | Link | Maps to |
|---|---|---|---|
| Järvelin and Kekäläinen, *Cumulated Gain-Based Evaluation of IR Techniques* (ACM TOIS 2002) | The origin of cumulated gain and its normalised form. Read in full in the Tampere preprint, titled *Cumulated gain-based indicators of IR performance*; the journal text not read | [DOI](https://doi.org/10.1145/582415.582418), [preprint](https://trepo.tuni.fi/handle/10024/65718) | [03](notes/03-two-tower-and-evaluation.md#offline-evaluation-sampled-metrics) |
| ★ Dacrema, Cremonesi and Jannach, *Are We Really Making Much Progress?* (RecSys 2019) | 18 algorithms, 7 reproducible, simple methods often better. The reason baselines come first | [arXiv](https://arxiv.org/abs/1907.06902) | [02](notes/02-collaborative-filtering-and-matrix-factorisation.md#the-reproducibility-warning) |
| ★ Rendle, Krichene, Zhang and Anderson, *Neural Collaborative Filtering vs. Matrix Factorization Revisited* (RecSys 2020) | A tuned dot product beats the learned MLP similarity | [arXiv](https://arxiv.org/abs/2005.09683) | [02](notes/02-collaborative-filtering-and-matrix-factorisation.md#the-reproducibility-warning) |
| ★ Steck, *Embarrassingly Shallow Autoencoders for Sparse Data* (WWW 2019) | EASE, the closed-form model that tops our table | [arXiv](https://arxiv.org/abs/1905.03375) | [02](notes/02-collaborative-filtering-and-matrix-factorisation.md#a-linear-model-with-a-closed-form) |
| Koren, Bell and Volinsky, *Matrix Factorization Techniques for Recommender Systems* (*IEEE Computer*, 2009) | The clear account of biased MF from the Netflix Prize | [DOI](https://doi.org/10.1109/MC.2009.263) | [02](notes/02-collaborative-filtering-and-matrix-factorisation.md#predicting-ratings-biases-and-matrix-factorisation) |
| ★ Hu, Koren and Volinsky, *Collaborative Filtering for Implicit Feedback Datasets* (ICDM 2008) | Confidence weighting and the iALS closed form. Its $\alpha = 40$ did not transfer to our binary data | [DOI](https://doi.org/10.1109/ICDM.2008.22) | [02](notes/02-collaborative-filtering-and-matrix-factorisation.md#implicit-feedback) |
| Rendle, Freudenthaler, Gantner and Schmidt-Thieme, *BPR* (UAI 2009) | Pairwise ranking from implicit data | [arXiv](https://arxiv.org/abs/1205.2618) | [02](notes/02-collaborative-filtering-and-matrix-factorisation.md#implicit-feedback) |
| Sarwar, Karypis, Konstan and Riedl, *Item-based Collaborative Filtering Recommendation Algorithms* (WWW 2001) | The case for item neighbourhoods | [DOI](https://doi.org/10.1145/371920.372071) | [02](notes/02-collaborative-filtering-and-matrix-factorisation.md#neighbourhoods-item-based-filtering) |
| Cremonesi, Koren and Turrin, *Performance of Recommender Algorithms on Top-N Recommendation Tasks* (RecSys 2010) | RMSE-tuned models need not do well at top-N. Abstract-level claim only; the full text was not available to read | [DOI](https://doi.org/10.1145/1864708.1864721) | [02](notes/02-collaborative-filtering-and-matrix-factorisation.md#the-metric-that-matters-top-n-ranking) |
| He et al., *Neural Collaborative Filtering* (WWW 2017) | The claim Rendle et al. tested | [arXiv](https://arxiv.org/abs/1708.05031) | [02](notes/02-collaborative-filtering-and-matrix-factorisation.md#the-reproducibility-warning) |
| Harper and Konstan, *The MovieLens Datasets* (*ACM TiiS*, 2015) | Required citation for the data | [DOI](https://doi.org/10.1145/2827872) | [02](notes/02-collaborative-filtering-and-matrix-factorisation.md) |
| ★ Yi et al., *Sampling-Bias-Corrected Neural Modeling for Large Corpus Item Recommendations* (RecSys 2019) | The logQ correction, streaming frequency estimates and normalised towers. The single line that rescued our tower | [PDF](https://storage.googleapis.com/gweb-research2023-media/pubtools/5716.pdf) | [03](notes/03-two-tower-and-evaluation.md#training-in-batch-softmax-and-its-bias) |
| Covington, Adams and Sargin, *Deep Neural Networks for YouTube Recommendations* (RecSys 2016) | The retrieval and ranking funnel, example age, and surrogate problems | [DOI](https://doi.org/10.1145/2959100.2959190) | [03](notes/03-two-tower-and-evaluation.md#why-large-systems-retrieve-first) |
| ⚑ Khrylchenko et al., *Correcting the LogQ Correction* (2025) | Argues the standard derivation mistreats the positive | [arXiv](https://arxiv.org/abs/2507.09331) | [03](notes/03-two-tower-and-evaluation.md#training-in-batch-softmax-and-its-bias) |
| ★ Krichene and Rendle, *On Sampled Metrics for Item Recommendation* (KDD 2020) | Sampled metrics can flip model order, which we reproduce | [page](https://research.google/pubs/on-sampled-metrics-for-item-recommendation/) | [03](notes/03-two-tower-and-evaluation.md#offline-evaluation-sampled-metrics) |
| Li, Chu, Langford and Schapire, *A Contextual-Bandit Approach to Personalized News Article Recommendation* (WWW 2010) | Replay evaluation from randomised logs. Local copy in the [RL pillar](../../generative-ai/05-RL/sources/li-2010-contextual-bandit-news-recommendation.pdf) | [arXiv](https://arxiv.org/abs/1003.0146) | [03](notes/03-two-tower-and-evaluation.md#offline-evaluation-counterfactual-estimates) |
| Gomez-Uribe and Hunt, *The Netflix Recommender System* (*ACM TMIS*, 2015) | What recommenders are worth, and how offline and A/B fit together | [DOI](https://doi.org/10.1145/2843948) | [03](notes/03-two-tower-and-evaluation.md#online-evaluation-the-ab-test) |

## Courses and videos

| Course | Platform, cost | Supports | Which parts |
|---|---|---|---|
| [Kaggle Learn: Time Series](https://www.kaggle.com/learn/time-series) | Kaggle, free | [01](notes/01-time-series-ml.md) | All lessons: trend, seasonality, lags, hybrid models, forecasting strategies |
| [Google: Recommendation Systems](https://developers.google.com/machine-learning/recommendation) | Google for Developers, free | [02](notes/02-collaborative-filtering-and-matrix-factorisation.md), [03](notes/03-two-tower-and-evaluation.md) | Candidate generation, matrix factorisation, softmax retrieval |
| [Andrew Ng, Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction) | Coursera, paid (audit available) | [02](notes/02-collaborative-filtering-and-matrix-factorisation.md) | Course 3, recommender systems week |
| [Stanford CS229](https://cs229.stanford.edu/) | Stanford, free materials and lecture videos | [01](notes/01-time-series-ml.md) | Generalisation and evaluation lectures, as background |
