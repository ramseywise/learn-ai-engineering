# References — Data Science

> Every source the notes cite, mapped to notes. **★** = read first. Local PDFs live in [sources/](sources/); figures in [sources/images/](sources/images/). Licence and size flags are in [Source quality](#source-quality).

---

## Books and courses

| | Source | Notes |
|---|---|---|
| ★ | Müller & Guido, *Introduction to Machine Learning with Python* (O'Reilly, 2016), [sources/](sources/mueller-guido-introduction-to-ml-with-python.pdf). Companion notebooks kept in [practice/Intro to Machine Learning in Python/](01-classical-ml/practice/intro-to-ml-in-python) (from [amueller/introduction_to_ml_with_python](https://github.com/amueller/introduction_to_ml_with_python), with `mglearn`). Ch. 1 → 01; ch. 2 → 02; ch. 3 → 05; ch. 4 → 03; ch. 5 → 04; ch. 6 → 03; ch. 7 → 08, 09. Figures as `mueller-guido-*` | 01–05, 08, 09 |
| ★ | Sarkar, *Text Analytics with Python*, 2nd ed. (Apress, 2019), [sources/](sources/sarkar-text-analytics-with-python-2e.pdf). Companion notebooks kept in [practice/Text Analytics with Python/](03-nlp/practice/text-analytics-with-python) (from [dipanjanS/text-analytics-with-python](https://github.com/dipanjanS/text-analytics-with-python), Apache-2.0). Ch. 1, 3 → 08; ch. 4 → 08, 11; ch. 5 → 09; ch. 6 → 10; ch. 7 → 10, 11; ch. 8 → 12; ch. 9 → 13; ch. 10 → 14. Figures as `sarkar-*` | 08–14 |
| ★ | Karpathy, [*Neural Networks: Zero to Hero*](https://karpathy.ai/zero-to-hero.html) (YouTube lectures + [karpathy/nn-zero-to-hero](https://github.com/karpathy/nn-zero-to-hero), MIT). Kept in [practice/nn-zero-to-hero/](04-llms-from-scratch/practice/nn-zero-to-hero), including the nanoGPT lecture code and [build-nanogpt](https://github.com/karpathy/build-nanogpt) | 15, 16, 17 |
| ★ | Ng, *Machine Learning* (Stanford / Coursera, 2011 edition). Own Python ports of ex1–ex8 in [Ng's Machine Learning Nbks/](01-classical-ml/practice/ng-machine-learning) | 02, 04, 05, 07 |
| | Ng, *Deep Learning Specialization* (deeplearning.ai / Coursera, 2017–18 edition, five courses). Own assignments in [Ng's Deep Learning Nbks/](02-deep-learning/practice/ng-deep-learning) | 07, 11, 14 |
| | James, Witten, Hastie, Tibshirani & Taylor, *An Introduction to Statistical Learning with Applications in Python* (2023). Held in [`../data-analytics/sources/`](../data-analytics/sources/); ch. 2–6 pair with 01–04, ch. 8 with 06, ch. 12 with 05 | 01–06 |
| | Bird, Klein & Loper, *Natural Language Processing with Python* (the NLTK book; online edition CC BY-NC-ND 3.0), [sources/](sources/bird-klein-loper-nlp-with-python.pdf) | 08, 12 |
| | Buduma, *Fundamentals of Deep Learning* (O'Reilly), [sources/](sources/buduma-fundamentals-of-deep-learning.pdf). Embeddings and recurrent chapters | 07, 14 |
| | Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 1 only, [sources/building-ai-agents-llms-rag-kgs/](sources/building-ai-agents-llms-rag-kgs/ch01-analyzing-text-data-deep-learning.pdf). Text representation through RNN/LSTM/CNN classifiers; the rest of the book lives under `ai-engineering/`. Folded in as: ch. 1 → [11](03-nlp/notes/04-embeddings-and-similarity.md#embedding-geometry-analogies-and-bias) (antonyms, window size, polysemy as superposition; dot product vs. cosine). Notes cite it as `(*Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. 1)` | 08, 11, 14 |
| | Raschka, *Build a Large Language Model (From Scratch)* (Manning, 2024), appendix A (PyTorch). PDF in [../generative-ai/01-llm-fundamentals/sources/build-a-large-language-model-from-scratch/](../generative-ai/01-llm-fundamentals/sources/build-a-large-language-model-from-scratch/appendix-a-intro-to-pytorch.pdf). Folded in as: appendix A → [07](02-deep-learning/notes/01-neural-networks-fundamentals.md#the-pytorch-training-loop) (training-loop pitfalls, DDP changes). Notes cite it as `(*Build a Large Language Model (From Scratch)*, appendix A)` | 07 |
| | Thakur, [*Approaching (Almost) Any NLP Problem on Kaggle*](https://www.kaggle.com/code/abhishek/approaching-almost-any-nlp-problem-on-kaggle) (Kaggle notebook). Own copy in [practice/](03-nlp/practice/approaching-almost-any-nlp-problem-on-kaggle.ipynb) | 09 |
| | Hugging Face, [*LLM Course*, ch. 1 "Transformers, what can they do?"](https://huggingface.co/learn/llm-course/chapter1/3). Source of the pipeline examples | 14 |

## Papers and docs

| Source | Notes |
|---|---|
| [scikit-learn user guide](https://scikit-learn.org/stable/user_guide.html) and [release highlights](https://scikit-learn.org/stable/whats_new.html) | 01–06 |
| Guo et al. 2017, *On Calibration of Modern Neural Networks* ([sources/](sources/guo-2017-calibration-modern-neural-networks.pdf)); Minderer et al. 2021, *Revisiting the Calibration of Modern Neural Networks* ([sources/](sources/minderer-2021-revisiting-calibration-modern-neural-networks.pdf)) | 04 |
| Ribeiro et al. 2016, LIME ([sources/](sources/ribeiro-2016-why-should-i-trust-you.pdf)); Lundberg & Lee 2017, SHAP ([sources/](sources/lundberg-2017-unified-approach-interpreting-model-predictions.pdf)); Lipton 2016 ([sources/](sources/lipton-2016-mythos-model-interpretability.pdf)); Miller 2017 ([sources/](sources/miller-2017-explanation-artificial-intelligence.pdf)); Dodge et al. 2019 ([sources/](sources/dodge-2019-explaining-models.pdf)); *Are Explanations Helpful?* ([sources/](sources/explanations-helpful-comparative-study-effects-explanations.pdf)) | 06, 13 |
| Ioffe & Szegedy 2015, *Batch Normalization* ([sources/](sources/ioffe-2015-batch-normalization.pdf)); Wu & Johnson 2021, *Rethinking "Batch" in BatchNorm* ([sources/](sources/wu-2021-rethinking-batch-batchnorm.pdf)) | 07, 16 |
| Chen et al. 2023, *Symbolic Discovery of Optimization Algorithms* (Lion, [arXiv:2302.06675](https://arxiv.org/abs/2302.06675), [sources/](sources/chen-2023-symbolic-discovery-optimization-algorithms.pdf)). Sign-of-momentum optimizer: up to 5× less pre-training compute for ViT on JFT, similar to or better than AdamW on language modelling, with smaller gains on some large LM runs | 07 |
| LeCun et al. 1998, *Gradient-Based Learning Applied to Document Recognition* (Proc. IEEE, [doi:10.1109/5.726791](https://doi.org/10.1109/5.726791), [PDF](../generative-ai/01-llm-fundamentals/sources/lecun-1998-gradient-based-learning-applied-document.pdf)). LeNet-5 and MNIST: 60k trainable parameters over 345k connections through weight sharing; 0.95% test error (0.8% with distortions) against 12% linear, 4.7% MLP and 1.4% for an SVM; names the collapse problem a discriminative loss fixes | 07 |
| Hénaff et al. 2020, *Data-Efficient Image Recognition with Contrastive Predictive Coding* (CPC v2, ICML 2020, [arXiv:1905.09272](https://arxiv.org/abs/1905.09272), [PDF](../generative-ai/01-llm-fundamentals/sources/henaff-2019-data-efficient-image-recognition-contrastive.pdf)). ImageNet linear probe 48.7% → 71.5% from v1; with 1% of labels 78.3% top-5 against 44.1% supervised, across different architectures | 07 |
| He et al. 2020, *Momentum Contrast* (MoCo, CVPR 2020, [arXiv:1911.05722](https://arxiv.org/abs/1911.05722), [PDF](../generative-ai/01-llm-fundamentals/sources/he-2020-momentum-contrast-unsupervised-visual-representation.pdf)). Queue of negatives decoupled from batch size, momentum 0.999 key encoder (0 fails, 0.9 gives 55.2% vs 59.0%); 60.6% linear, yet beats supervised pretraining on 7 detection/segmentation tasks | 07 |
| Chen et al. 2020, *A Simple Framework for Contrastive Learning of Visual Representations* (SimCLR, ICML 2020, [arXiv:2002.05709](https://arxiv.org/abs/2002.05709), [PDF](../generative-ai/01-llm-fundamentals/sources/chen-2020-simple-framework-contrastive-learning-visual.pdf)). In-batch negatives with NT-Xent; crop + colour distortion and the pre-projection-head layer (>10 points) matter; ResNet-50 (4×) 76.5% linear | 07 |
| Baevski et al. 2020, *wav2vec 2.0* (NeurIPS 2020, [arXiv:2006.11477](https://arxiv.org/abs/2006.11477), [PDF](../generative-ai/01-llm-fundamentals/sources/baevski-2020-wav2vec-2-0.pdf)). Masked contrastive pretraining on raw audio with quantized targets; 10 min of labels gives 4.8/8.2 LibriSpeech WER with an LM (40.2/38.7 without) | 07 |
| Mikolov et al. 2013 (word2vec); Pennington et al. 2014 (GloVe); Bojanowski et al. 2017 (FastText) | 11 |
| Blei, Ng & Jordan 2003 (LDA); Mihalcea & Tarau 2004 (TextRank) | 10 |
| Hutto & Gilbert 2014, [VADER](https://github.com/cjhutto/vaderSentiment) | 13 |
| Bengio et al. 2003, *A Neural Probabilistic Language Model*; van den Oord et al. 2016, *WaveNet* | 16 |
| Vaswani et al. 2017, *Attention Is All You Need*; Radford et al. 2019 (GPT-2); Brown et al. 2020 (GPT-3, the training hyperparameters) | 17 |
| [spaCy](https://spacy.io/), [NLTK](https://www.nltk.org/), [gensim](https://radimrehurek.com/gensim/), [sklearn-crfsuite](https://sklearn-crfsuite.readthedocs.io/) docs | 08–12 |

## Dependency audits

The full per-notebook fix tables live in the notes; this is the index.

| Library | Status (2026-10-31) | Where |
|---|---|---|
| scikit-learn 0.20 → 1.4+ | Resolved for Müller & Guido 02, 04, 05 (2026-07) and, on 2026-10-31, `get_feature_names` → `get_feature_names_out` in eight notebooks (M&G 04, 07; Sarkar Ch04a, Ch06c, Ch06d, Ch06e, Ch07c, Ch09e) and `sklearn.externals.joblib` → `joblib` in Sarkar Ch08c. Kaggle NLP notebook still uses `needs_proba` (removed 1.6) and `iid` | [04 — migration map](01-classical-ml/notes/04-model-evaluation.md#scikit-learn-migration-map-020--14) |
| TensorFlow 1.x → 2.x | Ng DL notebooks: `tf.compat.v1` bridge done; Tensorflow Tutorial and Convolution model still need the `tf.contrib` rewrite. Sarkar Ch10a: confusion-matrix cell fixed, but `tf.estimator` (removed in TF 2.16) remains | [07 — TF map](02-deep-learning/notes/01-neural-networks-fundamentals.md#tensorflow-1x-to-2x-status-and-migration-map), [14 — text notebooks](02-deep-learning/notes/02-neural-text-models.md#tensorflow-status-of-the-text-notebooks) |
| Standalone keras, gensim 3, spaCy 2, pyLDAvis, skater | Not fixed (reported per notebook in the Practice tables): spaCy `'en'` shortcuts, `keras.layers.normalization`, gensim `size=` / `index2word`, `pyLDAvis.sklearn`, `skater` (dead) in Ch09d, Stanford NER paths `E:/stanford/...` in Ch08b | 08–14 |
| PyMC3 → PyMC 5 | Bayesian notebooks belong to data-analytics | [migration map](../data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc.md#pymc3-to-pymc-5-migration-map); status in data-analytics [references.md, PyMC version audit](../data-analytics/references.md#pymc-version-audit) |

## Source quality

| Item | Flag |
|---|---|
| Book PDFs in `sources/` (Müller & Guido, Sarkar, Buduma, the Packt chapter) | Publisher-copyrighted. Fine for private study; do not publish the repo with them in it |
| Müller & Guido companion repo | No licence file upstream, so all rights reserved by default. Kept because it is the main practice surface for 01–05; do not redistribute |
| Ng course notebooks | Own graded Coursera work containing solutions. Coursera's honour code asks that solutions not be posted publicly |
| Data not in the repo | Sarkar ch. 9–10 `movie_reviews.csv`, ch. 6 NIPS papers; makemore `names.txt`; Kaggle competition data (spooky authors, ventilator); FineWeb-Edu shards for build-nanogpt; Ng DL helper modules and weights |
| Size | `Ng's Deep Learning Nbks/` 163 MB and `Ng's Machine Learning Nbks/` 22 MB (own work, left untouched); `sources/` 55 MB; practice 28 MB |
| Accuracy figures quoted from the books | Notes 13 and 14 quote approximate accuracies from the book text where the stored notebooks have no outputs |
