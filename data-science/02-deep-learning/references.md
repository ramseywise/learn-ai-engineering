---
origin: curated
sources:
  - ../sources/
confidence: high
cleaned: 2026-11-01
---
# 02-deep-learning references

★ = changed a claim in the notes. ⚑ = preprint only. Books shared across pillars are in the [subject references](../references.md). PDFs live in the shared [`../sources/`](../sources/), with some in [`generative-ai/01-llm-fundamentals/sources/`](../../generative-ai/01-llm-fundamentals/sources/).

## Books

| Book | Why read it | Local | Maps to |
|---|---|---|---|
| Ng, [*Machine Learning Yearning*](https://home-wordpress.deeplearning.ai/wp-content/uploads/2022/03/andrew-ng-machine-learning-yearning.pdf) (draft, 2018) | Error analysis as a count on a sample, the mislabelled column, and the Eyeball and Blackbox dev sets. Chapters 13 to 19 read, not the whole book | Link only | ch. 14 to 18 → 03 |
| ★ Buduma, *Fundamentals of Deep Learning* (O'Reilly) | Parallel text in TensorFlow for the whole pillar | [PDF](../sources/buduma-fundamentals-of-deep-learning.pdf) | ch. 1 to 2 → 01; ch. 3 → 01 translation table; ch. 4 → 02; ch. 5 → 04; ch. 6 → 04, 05, 06; ch. 7 → 05, 06 |
| Raschka, *Build a Large Language Model (From Scratch)* (Manning, 2024), appendix A | A compact PyTorch introduction, including the training loop and DDP | [PDF](../../generative-ai/01-llm-fundamentals/sources/build-a-large-language-model-from-scratch/appendix-a-intro-to-pytorch.pdf) | 01 |
| Sarkar, *Text Analytics with Python*, 2nd ed. (Apress, 2019), ch. 10 | Transfer learning with sentence encoders on IMDb, and the figure in the chapter. The [PDF in `sources/`](../sources/sarkar-text-analytics-with-python-2e.pdf) is the seven-chapter 1st edition and doesn't have this chapter | [Companion notebooks](../03-nlp/practice/text-analytics-with-python/), `Ch10a` | 06 |
| Raieli and Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 1 | The same arc from one-hot to RNN, LSTM, GRU and CNN classifiers | [PDF](../sources/building-ai-agents-llms-rag-kgs/ch01-analyzing-text-data-deep-learning.pdf) | 06 |

## Core papers

| Paper | Why read it | Local | Maps to |
|---|---|---|---|
| Rumelhart, Hinton and Williams, [*Learning representations by back-propagating errors*](https://doi.org/10.1038/323533a0) (Nature 1986) | The method every framework automates | Link only | 01, 05 |
| ★ Wilson, [*Deep Learning is Not So Mysterious or Different*](https://arxiv.org/abs/2503.02113) (ICML 2025) | Soft inductive biases, and why overparameterised fits aren't unique to neural networks | [PDF](../sources/wilson-2025-deep-learning-not-so-mysterious.pdf) | 01 |
| Glorot and Bengio, [*Understanding the difficulty of training deep feedforward neural networks*](https://proceedings.mlr.press/v9/glorot10a.html) (AISTATS 2010) | Why initialisation scale matters | Link only | 02 |
| He et al., [*Delving Deep into Rectifiers*](https://arxiv.org/abs/1502.01852) (ICCV 2015) | The ReLU initialisation | Link only | 02 |
| ★ Ioffe and Szegedy, [*Batch Normalization*](https://arxiv.org/abs/1502.03167) (ICML 2015) | The layer, and its train and eval modes | [PDF](../sources/ioffe-2015-batch-normalization.pdf) | 02 |
| ★ Wu and Johnson, [*Rethinking "Batch" in BatchNorm*](https://arxiv.org/abs/2105.07576) (2021) ⚑ | Batch dependence, precise statistics, and when BatchNorm misleads | [PDF](../sources/wu-2021-rethinking-batch-batchnorm.pdf) | 02 |
| Chen et al., [*Stronger Normalization-Free Transformers*](https://arxiv.org/abs/2512.10938) (2025) ⚑ | Derf; tested on an MLP in the chapter, where it loses | [PDF](../sources/chen-2025-stronger-normalization-free-transformers.pdf) | 02 |
| Kingma and Ba, [*Adam*](https://arxiv.org/abs/1412.6980) (ICLR 2015) | The default optimiser | [PDF](../../generative-ai/01-llm-fundamentals/sources/kingma-2014-adam.pdf) | 02 |
| ★ Loshchilov and Hutter, [*Decoupled Weight Decay Regularization*](https://arxiv.org/abs/1711.05101) (ICLR 2019) | Why L2 inside Adam differs from weight decay | [PDF](../../generative-ai/01-llm-fundamentals/sources/loshchilov-2017-decoupled-weight-decay-regularization.pdf) | 02 |
| ★ Chen et al., [*Symbolic Discovery of Optimization Algorithms*](https://arxiv.org/abs/2302.06675) (NeurIPS 2023) | Lion, its claims and what a small run can't test | [PDF](../sources/chen-2023-symbolic-discovery-optimization-algorithms.pdf) | 02 |
| ★ Dahl et al., [*Benchmarking Neural Network Training Algorithms*](https://arxiv.org/abs/2306.07179) (2023) ⚑ | How to compare optimisers fairly | [PDF](../sources/dahl-2023-benchmarking-neural-network-training-algorithms.pdf) | 02 |
| ★ Defazio and Mishchenko, [*Learning-Rate-Free Learning by D-Adaptation*](https://proceedings.mlr.press/v202/defazio23a.html) (ICML 2023) | Removes the rate search, sometimes; one seed in five failed here | [PDF](../sources/defazio-2023-learning-rate-free-learning-d.pdf) | 02 |
| Srivastava et al., [*Dropout*](https://jmlr.org/papers/v15/srivastava14a.html) (JMLR 2014) | The regulariser | Link only | 02 |
| ★ Liu et al., [*Dropout Reduces Underfitting*](https://arxiv.org/abs/2303.01500) (ICML 2023) | Early dropout, and when dropout hurts | [PDF](../sources/liu-2023-dropout-reduces-underfitting.pdf) | 02 |
| Caruana, [*Multitask Learning*](https://doi.org/10.1023/A:1007379606734) (Machine Learning 1997) | The argument for a shared representation | Link only | 03 |
| Yosinski et al., [*How transferable are features in deep neural networks?*](https://arxiv.org/abs/1411.1792) (NeurIPS 2014) | Transfer depends on task similarity | Link only | 03 |
| LeCun et al., [*Gradient-Based Learning Applied to Document Recognition*](https://doi.org/10.1109/5.726791) (Proc. IEEE 1998) | LeNet-5 and MNIST | [PDF](../../generative-ai/01-llm-fundamentals/sources/lecun-1998-gradient-based-learning-applied-document.pdf) | 04 |
| He et al., [*Deep Residual Learning for Image Recognition*](https://arxiv.org/abs/1512.03385) (CVPR 2016) | The degradation problem and skip connections | Link only | 04 |
| Woo et al., [*ConvNeXt V2*](https://arxiv.org/abs/2301.00808) (CVPR 2023) | Where ConvNets went next | [PDF](../sources/woo-2023-convnext-v2.pdf) | 04 |
| Redmon and Farhadi, [*YOLO9000*](https://arxiv.org/abs/1612.08242) (CVPR 2017) | The detector in the notebook | Link only | 04 |
| Schroff, Kalenichenko and Philbin, [*FaceNet*](https://arxiv.org/abs/1503.03832) (CVPR 2015) | The triplet loss | Link only | 04 |
| Gatys, Ecker and Bethge, [*A Neural Algorithm of Artistic Style*](https://arxiv.org/abs/1508.06576) (2015) ⚑ | Optimising the input, and Gram matrices | Link only | 04 |
| Hénaff et al., [*Data-Efficient Image Recognition with Contrastive Predictive Coding*](https://arxiv.org/abs/1905.09272) (ICML 2020) | Contrastive prediction on patches | [PDF](../../generative-ai/01-llm-fundamentals/sources/henaff-2019-data-efficient-image-recognition-contrastive.pdf) | 04 |
| He et al., [*Momentum Contrast*](https://arxiv.org/abs/1911.05722) (CVPR 2020) | Decouples negatives from batch size | [PDF](../../generative-ai/01-llm-fundamentals/sources/he-2020-momentum-contrast-unsupervised-visual-representation.pdf) | 04 |
| Chen et al., [*SimCLR*](https://arxiv.org/abs/2002.05709) (ICML 2020) | The simple recipe with NT-Xent | [PDF](../../generative-ai/01-llm-fundamentals/sources/chen-2020-simple-framework-contrastive-learning-visual.pdf) | 04 |
| Baevski et al., [*wav2vec 2.0*](https://arxiv.org/abs/2006.11477) (NeurIPS 2020) | The same idea on raw audio | [PDF](../../generative-ai/01-llm-fundamentals/sources/baevski-2020-wav2vec-2-0.pdf) | 04 |
| Hochreiter and Schmidhuber, [*Long Short-Term Memory*](https://doi.org/10.1162/neco.1997.9.8.1735) (Neural Computation 1997) | The original LSTM | Link only | 05 |
| Cho et al., [*Learning Phrase Representations using RNN Encoder-Decoder*](https://arxiv.org/abs/1406.1078) (EMNLP 2014) | The GRU | Link only | 05 |
| ★ Jozefowicz, Zaremba and Sutskever, [*An Empirical Exploration of Recurrent Network Architectures*](https://proceedings.mlr.press/v37/jozefowicz15.html) (ICML 2015) | The forget-gate bias | Link only | 05 |
| Sutskever, Vinyals and Le, [*Sequence to Sequence Learning*](https://arxiv.org/abs/1409.3215) (NeurIPS 2014) | Seq2seq and its bottleneck | Link only | 05 |
| Bahdanau, Cho and Bengio, [*Neural Machine Translation by Jointly Learning to Align and Translate*](https://arxiv.org/abs/1409.0473) (ICLR 2015) | Attention | Link only | 05 |
| Pennington, Socher and Manning, [*GloVe*](https://aclanthology.org/D14-1162/) (EMNLP 2014) | The vectors in the notebooks | Link only | 05 |
| Bolukbasi et al., [*Man is to Computer Programmer as Woman is to Homemaker?*](https://arxiv.org/abs/1607.06520) (NeurIPS 2016) | Neutralise and equalise | Link only | 05 |
| Maas et al., [*Learning Word Vectors for Sentiment Analysis*](https://aclanthology.org/P11-1015/) (ACL 2011) | The IMDb dataset | Link only | 06 |
| ★ Hinton and Salakhutdinov, [*Reducing the Dimensionality of Data with Neural Networks*](https://doi.org/10.1126/science.1127647) (*Science* 2006) | The deep autoencoder as non-linear PCA. Read in full in the [authors' copy](https://www.cs.toronto.edu/~hinton/absps/science.pdf); the supporting material not read | Link only | [05](notes/05-sequence-models.md#autoencoders-the-bottleneck-on-its-own) |
| ★ Vincent, Larochelle, Bengio and Manzagol, [*Extracting and Composing Robust Features with Denoising Autoencoders*](https://www.cs.toronto.edu/~larocheh/publications/icml-2008-denoising-autoencoders.pdf) (ICML 2008) | Corruption in place of a bottleneck. Read in full | Link only | [05](notes/05-sequence-models.md#autoencoders-the-bottleneck-on-its-own) |
| Kim, [*Convolutional Neural Networks for Sentence Classification*](https://arxiv.org/abs/1408.5882) (EMNLP 2014) | Filters as n-gram detectors | Link only | 06 |
| Cer et al., [*Universal Sentence Encoder*](https://arxiv.org/abs/1803.11175) (2018) ⚑ | The encoder in Sarkar's comparison | Link only | 06 |
| Reimers and Gurevych, [*Sentence-BERT*](https://arxiv.org/abs/1908.10084) (EMNLP 2019) | The encoder family behind `all-MiniLM-L6-v2` | Link only | 06 |
| Devlin et al., [*BERT*](https://arxiv.org/abs/1810.04805) (NAACL 2019) | Most of the pipelines' encoders | Link only | 06 |
| Sanh et al., [*DistilBERT*](https://arxiv.org/abs/1910.01108) (2019) ⚑ | A smaller distilled encoder | Link only | 06 |
| Vaswani et al., [*Attention Is All You Need*](https://arxiv.org/abs/1706.03762) (NeurIPS 2017) | Where this pillar hands over | Link only | 06 |

## Courses and videos

| Course | Platform, cost | Supports | Which parts |
|---|---|---|---|
| [Ng, Deep Learning Specialization](https://www.coursera.org/specializations/deep-learning) | Coursera; paid certificate, audit options vary | 01 to 05 | One course per note: 1 → 01, 2 → 02, 3 → 03, 4 → 04, 5 → 05. Your assignments are in [`practice/ng-deep-learning/`](practice/ng-deep-learning/) |
| [DeepLearning.AI, Neural Networks and Deep Learning](https://www.youtube.com/playlist?list=PLkDaE6sCZn6Ec-XTbcX1uRg2_u4xOEky0) | YouTube, free | 01 | The first course's lectures |
| [Stanford CS231n](https://cs231n.stanford.edu/) | Free course site | 02, 04 | Notes on optimisation, CNN architectures and detection |
| [Stanford CS224N, Winter 2021](https://www.youtube.com/playlist?list=PLoROMvodv4rOSH4v6133s9LFPRHjEmbmJ) | YouTube, free | 05, 06 | Word vectors, RNNs, LSTMs, seq2seq and attention lectures |
| [fast.ai, Practical Deep Learning for Coders](https://course.fast.ai/) | Free | 03, 06 | The top-down view of training, transfer learning and NLP |
| [Karpathy, Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html) | YouTube, free | 01, 05, 06 | micrograd and makemore lectures, which [the LLMs from scratch pillar](../../generative-ai/09-llms-from-scratch/README.md) builds on |
| [PyTorch tutorials, Learn the Basics](https://pytorch.org/tutorials/beginner/basics/intro.html) | Free docs | 01 | Tensors to the training loop |
| [Hugging Face, LLM Course](https://huggingface.co/learn/llm-course) | Free | 06 | Chapter 1, the source of the pipeline examples |
