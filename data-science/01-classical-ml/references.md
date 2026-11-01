---
origin: curated
sources:
  - ../sources/
confidence: high
cleaned: 2026-11-01
---
# 01-classical-ml references

★ = changed a claim in the notes. ⚑ = preprint only. Books shared across pillars are in the [subject references](../references.md). PDFs live in the shared [`../sources/`](../sources/).

## Books

| Book | Why read it | Local | Maps to |
|---|---|---|---|
| ★ Müller and Guido, *Introduction to Machine Learning with Python* (O'Reilly, 2016) | The practical spine of this pillar, with companion notebooks in [`practice/intro-to-ml-in-python/`](practice/intro-to-ml-in-python/) | [PDF](../sources/mueller-guido-introduction-to-ml-with-python.pdf) | ch. 1 → 01; ch. 2 → 02, 06; ch. 3 → 05; ch. 4 → 03; ch. 5 → 04; ch. 6 → 03 |
| James, Witten, Hastie, Tibshirani and Taylor, *An Introduction to Statistical Learning with Applications in Python* (Springer, 2023) | The statistical reasoning behind the same models | [PDF](../../data-analytics/sources/An-Introduction-to-Statistical-Learning-with-Applications-in-Python.pdf) | ch. 2 to 6 → 01 to 04; ch. 8 → 06; ch. 12 → 05 |

## Core papers

| Paper | Why read it | Local | Maps to |
|---|---|---|---|
| Pedregosa et al., [*Scikit-learn: Machine Learning in Python*](https://arxiv.org/abs/1201.0490) (JMLR 2011) | Why the estimator API is uniform | [PDF](../sources/pedregosa-2012-scikit-learn.pdf) | 01 |
| Tibshirani, [*Regression Shrinkage and Selection via the Lasso*](https://doi.org/10.1111/j.2517-6161.1996.tb02080.x) (JRSS B 1996) | The origin of the lasso | Link only | 02 |
| Cortes and Vapnik, [*Support-Vector Networks*](https://doi.org/10.1007/bf00994018) (Machine Learning 1995) | The origin of soft-margin SVMs | [PDF](../sources/cortes-1995-support-vector-networks.pdf) | 02 |
| Niculescu-Mizil and Caruana, [*Predicting Good Probabilities with Supervised Learning*](https://doi.org/10.1145/1102351.1102430) (ICML 2005) | Which families distort probabilities, and how to fix them | Link only | 02, 04 |
| Varma and Simon, [*Bias in Error Estimation When Using Cross-Validation for Model Selection*](https://doi.org/10.1186/1471-2105-7-91) (BMC Bioinformatics 2006) | Why nested CV exists | [PDF](../sources/varma-2006-bias-error-estimation-when-using.pdf) | 04 |
| Davis and Goadrich, [*The Relationship Between Precision-Recall and ROC Curves*](https://doi.org/10.1145/1143844.1143874) (ICML 2006) | How the two curves relate | [PDF](../sources/davis-2006-relationship-between-precision-recall-roc.pdf) | 04 |
| ★ Guo et al., [*On Calibration of Modern Neural Networks*](https://arxiv.org/abs/1706.04599) (ICML 2017) | Temperature scaling, and why accurate models can be miscalibrated | [PDF](../sources/guo-2017-calibration-modern-neural-networks.pdf) | 04 |
| ★ Minderer et al., [*Revisiting the Calibration of Modern Neural Networks*](https://arxiv.org/abs/2106.07998) (NeurIPS 2021) | Newer architectures qualify Guo's finding | [PDF](../sources/minderer-2021-revisiting-calibration-modern-neural-networks.pdf) | 04 |
| Arthur and Vassilvitskii, [*k-means++*](https://dl.acm.org/doi/10.5555/1283383.1283494) (SODA 2007) | The default initialisation | Link only | 05 |
| Ester et al., [*A Density-Based Algorithm for Discovering Clusters*](https://cdn.aaai.org/KDD/1996/KDD96-037.pdf) (KDD 1996) | DBSCAN | Link only | 05 |
| van der Maaten and Hinton, [*Visualizing Data using t-SNE*](https://jmlr.org/papers/v9/vandermaaten08a.html) (JMLR 2008) | t-SNE | Link only | 05 |
| McInnes et al., [*UMAP*](https://arxiv.org/abs/1802.03426) (preprint 2018) | The faster neighbour embedding | [PDF](../sources/mcinnes-2018-umap.pdf) | 05 |
| Liu et al., [*Isolation Forest*](https://doi.org/10.1109/icdm.2008.17) (ICDM 2008) | Anomaly detection by random splits | Link only | 05 |
| Breiman, [*Random Forests*](https://doi.org/10.1023/a:1010933404324) (Machine Learning 2001) | The method, out-of-bag estimates, and permutation importance | Link only | 06, 08 |
| Friedman, [*Greedy Function Approximation*](https://doi.org/10.1214/aos/1013203451) (Annals of Statistics 2001) | Gradient boosting, and partial dependence | Link only | 06, 08 |
| ★ Chen and Guestrin, [*XGBoost*](https://arxiv.org/abs/1603.02754) (KDD 2016) | Second-order leaf weights, regularisation, sparsity-aware splits, the systems design | [PDF](../sources/chen-2016-xgboost.pdf) | 07 |
| Ke et al., [*LightGBM*](https://papers.nips.cc/paper/6907-lightgbm-a-highly-efficient-gradient-boosting-decision-tree) (NeurIPS 2017) | GOSS and EFB | Link only | 07 |
| ★ Prokhorenkova et al., [*CatBoost*](https://arxiv.org/abs/1706.09516) (NeurIPS 2018) | Why target statistics and residuals leak, and ordered fixes | [PDF](../sources/prokhorenkova-2017-catboost.pdf) | 07 |
| ⚑ Karbasi and Larsen, [*The Impossibility of Parallelizing Boosting*](https://arxiv.org/abs/2301.09627) (preprint 2023) | Why rounds are sequential, in theory | [PDF](../sources/karbasi-2023-impossibility-parallelizing-boosting.pdf) | 07 |
| Grinsztajn et al., [*Why do tree-based models still outperform deep learning on tabular data?*](https://arxiv.org/abs/2207.08815) (NeurIPS 2022) | Trees or neural networks on tables | Link only | 07 |
| ★ Lundberg and Lee, [*A Unified Approach to Interpreting Model Predictions*](https://arxiv.org/abs/1705.07874) (NIPS 2017) | SHAP, and its unifying theorem | [PDF](../sources/lundberg-2017-unified-approach-interpreting-model-predictions.pdf) | 08 |
| Lundberg et al., [*From Local Explanations to Global Understanding with Explainable AI for Trees*](https://doi.org/10.1038/s42256-019-0138-9) (Nature MI 2020) | `TreeExplainer` | Link only | 08 |
| Ribeiro et al., [*"Why Should I Trust You?"*](https://arxiv.org/abs/1602.04938) (KDD 2016) | LIME, and the wolf and snow experiment | [PDF](../sources/ribeiro-2016-why-should-i-trust-you.pdf) | 08 |
| Lipton, [*The Mythos of Model Interpretability*](https://arxiv.org/abs/1606.03490) (2016, later CACM) | What "interpretable" can mean | [PDF](../sources/lipton-2016-mythos-model-interpretability.pdf) | 08 |
| Miller, [*Explanation in Artificial Intelligence*](https://arxiv.org/abs/1706.07269) (Artificial Intelligence 2019) | What people want from an explanation | [PDF](../sources/miller-2017-explanation-artificial-intelligence.pdf) | 08 |
| Dodge et al., [*Explaining Models*](https://arxiv.org/abs/1901.07694) (IUI 2019) | Explanation style changes fairness judgements | [PDF](../sources/dodge-2019-explaining-models.pdf) | 08 |
| ★ Wang and Yin, [*Are Explanations Helpful?*](https://doi.org/10.1145/3397481.3450650) (IUI 2021) | Comparison of explanation types on human desiderata | [PDF](../sources/explanations-helpful-comparative-study-effects-explanations.pdf) | 08 |
| Strobl et al., [*Bias in Random Forest Variable Importance Measures*](https://doi.org/10.1186/1471-2105-8-25) (BMC Bioinformatics 2007) | Why impurity importance favours high-cardinality features | Link only | 08 |
| Goldstein et al., [*Peeking Inside the Black Box*](https://arxiv.org/abs/1309.6392) (JCGS 2015) | ICE plots | Link only | 08 |
| Hooker et al., [*Unrestricted Permutation Forces Extrapolation*](https://arxiv.org/abs/1905.03151) (Statistics and Computing 2021) | The other permutation trap | Link only | 08 |
| ⚑ Huang et al., [*Can Large Language Models Explain Themselves?*](https://arxiv.org/abs/2310.11207) (preprint 2023) | Self-explanations against occlusion and LIME | [PDF](../sources/huang-2023-can-large-language-models-explain.pdf) | 08 |
| ⚑ Grosse et al., [*Studying Large Language Model Generalization with Influence Functions*](https://arxiv.org/abs/2308.03296) (preprint 2023) | Attributing behaviour to training examples | [PDF](../sources/grosse-2023-studying-large-language-model-generalization.pdf) | 08 |

## Courses and videos

Linked, never vendored.

| Course | Platform | Cost | What it supports |
|---|---|---|---|
| [Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction) (Ng) | Coursera | Paid certificate, audit options vary | 01, 02, 05, 06. The current version of the course whose older exercises are in [`practice/ng-machine-learning/`](practice/ng-machine-learning/) |
| [StatQuest: Machine Learning playlist](https://www.youtube.com/playlist?list=PLblh5JKOoLUICTaGLRoHQDuF_7q2GfuJF) (Starmer) | YouTube | Free | 02, 04, 06, for visual explanations |
| [CS229 Machine Learning, Autumn 2018](https://www.youtube.com/playlist?list=PLoROMvodv4rMiGQp3WXShtMGgzqpfVfbU) (Ng, Stanford) | YouTube | Free | 01, 02, 05, at a mathematical level |
| [Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning) | Kaggle Learn | Free | 02 |
| [Intermediate Machine Learning](https://www.kaggle.com/learn/intermediate-machine-learning) | Kaggle Learn | Free | 03, 06, 07 |
| [Feature Engineering](https://www.kaggle.com/learn/feature-engineering) | Kaggle Learn | Free | 03 |

Library documentation: [scikit-learn](https://scikit-learn.org/stable/user_guide.html), [XGBoost](https://xgboost.readthedocs.io/), [LightGBM](https://lightgbm.readthedocs.io/), [CatBoost](https://catboost.ai/docs/), [SHAP](https://shap.readthedocs.io/).
