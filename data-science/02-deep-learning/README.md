# 02 — Deep learning

> Train a network, debug it when it fails without an error, and match the architecture to the data. Deck: [`slides/deep-learning.pptx`](slides/deep-learning.pptx) (source [`slides/deck.yaml`](slides/deck.yaml)). Practice: [`practice/`](practice/). References: [`references.md`](references.md).

## What it is

Neural networks from the forward pass to pre-trained transformers, split along the five courses of Ng's Deep Learning Specialization, with a closing chapter on text models. Ng's coursework stays in `practice/` as it was submitted, in NumPy and TensorFlow 1.x. The chapters use PyTorch as the course framework, and [note 01](notes/01-neural-networks-fundamentals.md#translating-the-ng-notebooks-to-pytorch) has a table for translating any notebook to it.

## Why it matters

Classical models carry tabular data, but images, sequences and text need a model that learns its own representation. Networks are also harder to trust. A wrong initial weight, a forgotten `model.eval()` or `weight_decay` in the wrong optimiser raises no error and can cost anything from 9 points to the whole model. The value of this pillar is knowing what to measure when the loss looks wrong, and knowing what to try next. It is also the prerequisite for [LLMs from scratch](../../generative-ai/09-llms-from-scratch/README.md).

## The story

Logistic regression stops at 0.895 on two interleaved moons, because its boundary is a line, and one hidden layer lifts it to 0.955. Then training becomes the problem: the same network on digits scores 0.102 with zero initial weights and 0.970 with He initialisation, and the same `weight_decay=0.1` gives 0.102 in Adam and 0.972 in AdamW. With the training working, the next question is what to do with a month. A gap analysis says whether more data would help at all, and it warns when it wouldn't, as with the transfer learning that lost to training from scratch on a small digits task. The architecture then has to match the data. Moving a digit one pixel takes an MLP from 0.975 to 0.473 and a CNN only to 0.656. An LSTM stays at chance on a memory task until one bias changes, and attention takes date translation from 3% to 100% of dates correct. A transformer encoder drops the recurrence, and on digits the CNN still beats it at every data size. Finally, on 5,000 real reviews, TF-IDF at 0.886 beats every embedding model trained from scratch. A strong frozen encoder beats it on few labels, a small one never does, and fine-tuning DistilBERT reaches 0.905 once there are thousands of labels, because its representation was learned on far more text.

## Reading order

| # | Note | Question it answers | Ng course |
|---|---|---|---|
| 1 | [Neural network fundamentals](notes/01-neural-networks-fundamentals.md) | What does a network compute, and what does training do? | Neural Networks and Deep Learning |
| 2 | [Optimisation and regularisation](notes/02-optimisation-and-regularisation.md) | Why won't it train, and why won't it generalise? | Improving Deep Neural Networks |
| 3 | [Structuring ML projects](notes/03-structuring-ml-projects.md) | What should you try next? | Structuring Machine Learning Projects |
| 4 | [Convolutional networks](notes/04-convolutional-networks.md) | Why do images need a different architecture? | Convolutional Neural Networks |
| 5 | [Sequence models](notes/05-sequence-models.md) | How does a network carry memory? | Sequence Models |
| 5b | [Transformer encoders](notes/05b-transformer-encoders.md) | When is an encoder worth choosing over a CNN, an LSTM or a linear model? | Beyond Ng |
| 6 | [Neural text models](notes/06-neural-text-models.md) | What does it take for a neural model to beat word counts? | Beyond Ng: Sarkar `Ch10a` notebook, intro-to-nlp |

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| None in other subjects | Starts from [DS 01](../01-classical-ml/README.md) in this subject |

**Feeds into**

| Chapter | Why |
|---|---|
| [GA 01/02 Attention and the transformer block](../../generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block.md) | Attention began as a fix for recurrent networks |
| [GA 09/03 nanoGPT](../../generative-ai/09-llms-from-scratch/notes/03-nanogpt.md) | Builds the decoder side from scratch after [the encoder chapter](notes/05b-transformer-encoders.md) |
| [GA 01/06 Pretraining](../../generative-ai/01-llm-fundamentals/notes/06-pretraining-data-and-objectives.md) | Backprop, AdamW and the learning-rate sweep are assumed there |
| [GA 09/01 Micrograd](../../generative-ai/09-llms-from-scratch/notes/01-micrograd.md) | Builds backprop from scratch |
| [GA 08/02 Defining correct](../../generative-ai/08-eval/notes/02-defining-correct.md) | Error analysis, the same habit on an LLM's output |
| [GA 08/03 Eval datasets](../../generative-ai/08-eval/notes/03-eval-datasets.md) | The dev and held-out split answers the same overfitting question |
| [AIE 07/06 Serving at scale](../../ai-engineering/07-inference-engineering/notes/06-serving-at-scale.md) | One decode step is one forward pass |
| [AIE 08/01 Image input](../../ai-engineering/08-multimodal-engineering/notes/01-image-input.md) | CNNs came before the vision transformer used there |

## Rules of thumb

- Keep a from-scratch or linear control. Transfer, contrastive pretraining and neural text models all lost to one in small runs here.
- Before tuning, look at the initial activations. A network initialised with weights too small or too large can't start learning.
- Sweep the learning rate by factors of ten first. It moved test accuracy from 0.100 to 0.961 in a run where the choice of adaptive optimiser moved it by under a point.
- Use AdamW, and treat `weight_decay` in Adam as a different setting.
- Switch to `eval()` before scoring. Leaving batch norm in training mode cost 9 points with no error.
- With noisy labels, keep a clean validation set and stop early.
- Find the largest gap between human, train, train-dev, dev and test, then fix that one. Count what a fix could win before building it.
- Use residual connections when going deep. Plain networks of 62 layers train badly on digits, with a training score of 0.379.
- Measure what an initialisation change did. A forget-gate assignment to a wrong parameter name is silently ignored.
- Before choosing a transformer encoder, run a learning curve against a CNN or linear model. A CNN won at every size on digits, and an encoder that forgot `batch_first=True` fell from 0.966 to 0.658 on single requests.
- On text, run TF-IDF first. With few labels, measure a frozen encoder against it. With thousands, fine-tune one. Training your own embeddings came last here.

## Practice

| Folder | What | How to run |
|---|---|---|
| [`practice/ng-deep-learning/`](practice/ng-deep-learning) | Own assignments from the five Ng courses | `uv run --python 3.11 --with "tensorflow<2.16" --with matplotlib --with scipy --with jupyter jupyter lab`, from that folder. These are legacy: TF 1.x through `tf.compat.v1`, two notebooks still need `tf.contrib`, and some need course helper files and weights, so note 01 suggests reproducing them in PyTorch |
| [`practice/autoencoder.py`](practice/autoencoder.py) | The bottleneck, denoising and reconstruction error as an anomaly score, for [note 05](notes/05-sequence-models.md#autoencoders-the-bottleneck-on-its-own) | `uv run autoencoder.py`, from `practice/`; a few minutes on a laptop CPU |
| [`practice/transaction_sequence_lab.py`](practice/transaction_sequence_lab.py) | Generated card charges: boosted aggregates against a GRU, a random split against a time split, late chargebacks, a cost threshold and drift, for [note 05](notes/05-sequence-models.md#ordered-events-make-the-sequence-model-earn-its-place) | `uv run transaction_sequence_lab.py`, from `practice/`; about four minutes on a laptop CPU |
| [`practice/deep-learning-starter-simple-lstm.ipynb`](practice/deep-learning-starter-simple-lstm.ipynb) | Own Kaggle Ventilator Pressure LSTM, which note 06 reproduces on synthetic data | Needs the [competition data](https://www.kaggle.com/competitions/ventilator-pressure-prediction) and preferably a GPU |

Each chapter's code runs by itself: `uv run --with torch --with scikit-learn --with pandas --with matplotlib python <file>`, on the block copied to a file. Note 06 also needs `transformers`, `sentence-transformers`, `sentencepiece`, `sacremoses` and the IMDb download.

## Deck

```bash
make slides PILLAR=data-science/02-deep-learning STRICT=1 PREVIEW=1
```

## Primary texts

- Buduma, *Fundamentals of Deep Learning*
- Ng, *Machine Learning Yearning*
- Raschka, *Build a Large Language Model (From Scratch)*, appendix A
- Ng, *Deep Learning Specialization*

Everything else: [references.md](references.md).

Next pillar: [NLP](../03-nlp/README.md).
