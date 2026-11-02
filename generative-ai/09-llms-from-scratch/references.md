---
origin: curated
sources:
  - ../../data-science/sources/
confidence: high
cleaned: 2026-11-01
---
# 04-llms-from-scratch references

★ = changed a claim in the notes. ⚑ = preprint only. Books shared across pillars are in the [subject references](../../data-science/references.md). PDFs live in the shared [`../../data-science/sources/`](../../data-science/sources/). Notes: [01 micrograd](notes/01-micrograd.md), [02 makemore](notes/02-makemore.md), [03 nanoGPT](notes/03-nanogpt.md).

## Books

| Book | Why read it | Local | Maps to |
|---|---|---|---|
| Raschka, [*Build a Large Language Model (From Scratch)*](https://www.manning.com/books/build-a-large-language-model-from-scratch) (Manning, 2024), with [public code](https://github.com/rasbt/LLMs-from-scratch) | The same journey in book form, slower and in more detail, going on to classification and instruction fine-tuning | web only | [03](notes/03-nanogpt.md) |
| Prince, [*Understanding Deep Learning*](https://udlbook.github.io/udlbook/) (free online) | Careful chapters on backpropagation, initialisation and transformers, with the figures these notes leave out | web only | [01](notes/01-micrograd.md), [02](notes/02-makemore.md), [03](notes/03-nanogpt.md) |
| Goodfellow, Bengio and Courville, [*Deep Learning*](https://www.deeplearningbook.org/) (free online) | The reference for backpropagation as an algorithm on graphs | web only | [01](notes/01-micrograd.md) |

## Core papers

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| Bengio, Ducharme, Vincent and Jauvin, [*A Neural Probabilistic Language Model*](https://www.jmlr.org/papers/v3/bengio03a.html) (*JMLR*, 2003) | The MLP over a context window of shared word vectors, as used in part 2 of makemore | web only | [02](notes/02-makemore.md) |
| ★ He, Zhang, Ren and Sun, *Delving Deep into Rectifiers* ([arXiv:1502.01852](https://arxiv.org/abs/1502.01852), ICCV 2015) | Kaiming init, with its variance argument | web only | [02](notes/02-makemore.md) |
| ★ Ioffe and Szegedy, *Batch Normalization* ([arXiv:1502.03167](https://arxiv.org/abs/1502.03167), ICML 2015) | Normalising activations with batch statistics | [PDF](../../data-science/sources/ioffe-2015-batch-normalization.pdf) | [02](notes/02-makemore.md) |
| ★ Wu and Johnson, *Rethinking "Batch" in BatchNorm* ([arXiv:2105.07576](https://arxiv.org/abs/2105.07576), 2021) ⚑ | The ways that batch coupling goes wrong | [PDF](../../data-science/sources/wu-2021-rethinking-batch-batchnorm.pdf) | [02](notes/02-makemore.md) |
| Ba, Kiros and Hinton, *Layer Normalization* ([arXiv:1607.06450](https://arxiv.org/abs/1607.06450), 2016) ⚑ | The per-example alternative, which transformers use | web only | [02](notes/02-makemore.md), [03](notes/03-nanogpt.md) |
| ★ van den Oord et al., *WaveNet* ([arXiv:1609.03499](https://arxiv.org/abs/1609.03499), SSW 2016) | Dilated causal convolutions, with the listening-test numbers quoted in makemore | web only | [02](notes/02-makemore.md) |
| ★ Vaswani et al., *Attention Is All You Need* ([arXiv:1706.03762](https://arxiv.org/abs/1706.03762), NeurIPS 2017) | Scaled dot-product attention, multi-head attention and the original post-norm block | web only | [03](notes/03-nanogpt.md) |
| ★ Radford, Wu, Child, Luan, Amodei and Sutskever, [*Language Models are Unsupervised Multitask Learners*](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) (OpenAI report, 2019) | GPT-2: pre-norm, the `1/√N` residual init, 50,257 tokens and 1,024 of context | web only | [03](notes/03-nanogpt.md) |
| ★ Brown et al., *Language Models are Few-Shot Learners* ([arXiv:2005.14165](https://arxiv.org/abs/2005.14165), NeurIPS 2020) | Table 2.1 and appendix B are where the training recipe comes from | web only | [03](notes/03-nanogpt.md) |
| ★ Xiong et al., *On Layer Normalization in the Transformer Architecture* ([arXiv:2002.04745](https://arxiv.org/abs/2002.04745), ICML 2020) | Why pre-norm reduces the need for warm-up | web only | [03](notes/03-nanogpt.md) |
| Press and Wolf, *Using the Output Embedding to Improve Language Models* ([arXiv:1608.05859](https://arxiv.org/abs/1608.05859), EACL 2017) | Weight tying | web only | [03](notes/03-nanogpt.md) |
| Inan, Khosravi and Socher, *Tying Word Vectors and Word Classifiers* ([arXiv:1611.01462](https://arxiv.org/abs/1611.01462), ICLR 2017) | The concurrent loss-framework explanation of tying. Abstract read | web only | [03](notes/03-nanogpt.md) |
| He, Zhang, Ren and Sun, *Deep Residual Learning* ([arXiv:1512.03385](https://arxiv.org/abs/1512.03385), CVPR 2016) | Residual connections. Abstract read | web only | [03](notes/03-nanogpt.md) |
| Hendrycks and Gimpel, *Gaussian Error Linear Units* ([arXiv:1606.08415](https://arxiv.org/abs/1606.08415), 2016) ⚑ | GELU. Abstract read | web only | [03](notes/03-nanogpt.md) |
| Loshchilov and Hutter, *Decoupled Weight Decay Regularization* ([arXiv:1711.05101](https://arxiv.org/abs/1711.05101), ICLR 2019) | AdamW. Abstract read | web only | [03](notes/03-nanogpt.md) |
| Zellers, Holtzman, Bisk, Farhadi and Choi, *HellaSwag* ([arXiv:1905.07830](https://arxiv.org/abs/1905.07830), ACL 2019) | The evaluation used in the GPT-2 reproduction. Abstract read | web only | [03](notes/03-nanogpt.md) |
| ★ Penedo et al., *The FineWeb Datasets* ([arXiv:2406.17557](https://arxiv.org/abs/2406.17557), NeurIPS 2024) | Where FineWeb-Edu's 1.3 trillion tokens come from | web only | [03](notes/03-nanogpt.md) |

## Courses and videos

| Resource | Why | Maps to |
|---|---|---|
| Karpathy, [*Neural Networks: Zero to Hero*](https://karpathy.ai/zero-to-hero.html), snapshot in [`practice/nn-zero-to-hero/`](practice/nn-zero-to-hero/) (MIT licence) | The spine of this pillar. These chapters are written to go with it | all |
| Karpathy, [micrograd lecture](https://www.youtube.com/watch?v=VMj-3S1tku0) | Backpropagation, spelled out | [01](notes/01-micrograd.md) |
| Karpathy, makemore lectures: [1](https://www.youtube.com/watch?v=PaCmpygFfXo), [2](https://www.youtube.com/watch?v=TCH_1BHY58I), [3](https://www.youtube.com/watch?v=P6sfmUTpUmc), [4](https://www.youtube.com/watch?v=q8SA3rM6ckI), [5](https://www.youtube.com/watch?v=t3YJ5hKiMQ0) | From bigrams to a WaveNet-style tree | [02](notes/02-makemore.md) |
| ★ Karpathy, [Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY) and [Let's reproduce GPT-2 (124M)](https://www.youtube.com/watch?v=l8pRSuU81PU) | Lecture numbers in the chapter were checked against the transcripts | [03](notes/03-nanogpt.md) |
| Karpathy, [Let's build the GPT tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE) | BPE, the piece this pillar skips, and the opening of [LLM fundamentals](../../generative-ai/01-llm-fundamentals/README.md) | [03](notes/03-nanogpt.md) |
| 3Blue1Brown, [Neural networks](https://www.3blue1brown.com/topics/neural-networks) | The visual intuition for backpropagation and attention | [01](notes/01-micrograd.md), [03](notes/03-nanogpt.md) |
| Alammar, [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) | Pictures of every tensor in the 2017 block | [03](notes/03-nanogpt.md) |
| Rush et al., [The Annotated Transformer](https://nlp.seas.harvard.edu/annotated-transformer/) | The 2017 paper, line by line, with encoder and cross-attention | [03](notes/03-nanogpt.md) |
| Stanford [CS224N](https://web.stanford.edu/class/cs224n/) | The academic course: language models, RNNs, attention, transformers | [02](notes/02-makemore.md), [03](notes/03-nanogpt.md) |
| fast.ai, [Practical Deep Learning](https://course.fast.ai) | The top-down complement to this bottom-up pillar | [01](notes/01-micrograd.md) |
| Hugging Face, [LLM course](https://huggingface.co/learn/llm-course) | What to do once you stop writing the model yourself | [03](notes/03-nanogpt.md) |
