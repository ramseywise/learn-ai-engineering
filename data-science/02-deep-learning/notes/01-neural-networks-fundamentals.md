---
origin: own coursework (Ng Machine Learning ex4; Ng Deep Learning Specialization) + curated
sources:
  - ../Ng's Machine Learning Nbks/ex4/ex4.ipynb
  - ../Ng's Deep Learning Nbks/
  - https://www.coursera.org/specializations/deep-learning
  - ../../sources/buduma-fundamentals-of-deep-learning.pdf
  - https://www.tensorflow.org/guide/migrate
  - "Raschka, Build a Large Language Model (From Scratch) (Manning, 2024), appendix A"
  - https://arxiv.org/abs/2302.06675
  - https://arxiv.org/abs/1711.05101
  - https://doi.org/10.1109/5.726791
  - https://arxiv.org/abs/1905.09272
  - https://arxiv.org/abs/1911.05722
  - https://arxiv.org/abs/2002.05709
  - https://arxiv.org/abs/2006.11477
confidence: high
cleaned: 2026-10-31
---
# 7 — Neural Network Fundamentals

> A neural network is logistic regression stacked: forward pass, loss, backward pass by the chain rule, gradient step. Your Ng coursework builds that by hand in NumPy, then adds what makes deep networks train (initialisation, regularisation, optimisers, batch norm), then the two architectures that dominated before transformers: CNNs and RNNs.

The sklearn `MLPClassifier` in [02](../../01-classical-ml/notes/02-supervised-learning.md#neural-networks-multilayer-perceptrons) hides all of this. This note opens it up; [15 — micrograd](../../04-llms-from-scratch/notes/01-micrograd.md) does it again as an autograd engine.

---

## The forward pass

For an $L$-layer network with weights $W^{[l]}$, biases $b^{[l]}$ and activation $g$:

$$Z^{[l]} = W^{[l]} A^{[l-1]} + b^{[l]}, \qquad A^{[l]} = g^{[l]}(Z^{[l]}), \qquad A^{[0]} = X$$

The Ng DL convention stores examples as **columns**: $X$ is $(n_x, m)$, $W^{[l]}$ is $(n^{[l]}, n^{[l-1]})$. Getting these shapes right is half of every assignment.

| Activation | $g(z)$ | $g'(z)$ | Use |
|---|---|---|---|
| Sigmoid | $1/(1+e^{-z})$ | $g(1-g)$ | Binary output layer |
| tanh | $\tanh z$ | $1 - g^2$ | Hidden layers (zero-centred), RNNs |
| ReLU | $\max(0, z)$ | $1[z>0]$ | Default hidden layer |
| Leaky ReLU | $\max(0.01z, z)$ | | Avoids dead units |
| Softmax | $e^{z_k}/\sum_j e^{z_j}$ | | Multiclass output |

**Logistic regression with a neural-network mindset** (DL course 1, week 2) is the one-layer case: flatten 64×64×3 cat images into 12,288-vectors, `sigmoid(w.T @ X + b)`, cross-entropy cost, gradient descent. About 70% test accuracy; the point is the structure, not the score.

---

## Backpropagation

The chain rule, applied layer by layer from the loss backwards. For cross-entropy loss with a sigmoid output, $dZ^{[L]} = A^{[L]} - Y$. Then for each layer:

$$dW^{[l]} = \tfrac{1}{m} dZ^{[l]} A^{[l-1]\top}, \quad db^{[l]} = \tfrac{1}{m}\textstyle\sum dZ^{[l]}, \quad dA^{[l-1]} = W^{[l]\top} dZ^{[l]}, \quad dZ^{[l-1]} = dA^{[l-1]} \odot g'(Z^{[l-1]})$$

**Building your Deep Neural Network: Step by Step** (DL course 1, week 4) structures this as cached forward and backward functions:

```python
def linear_activation_forward(A_prev, W, b, activation):
    Z = W @ A_prev + b
    A = np.maximum(0, Z) if activation == "relu" else 1 / (1 + np.exp(-Z))
    cache = (A_prev, W, b, Z)               # everything backward needs
    return A, cache

def linear_activation_backward(dA, cache, activation):
    A_prev, W, b, Z = cache
    m = A_prev.shape[1]
    if activation == "relu":
        dZ = dA * (Z > 0)
    else:
        s = 1 / (1 + np.exp(-Z)); dZ = dA * s * (1 - s)
    dW = dZ @ A_prev.T / m
    db = dZ.sum(axis=1, keepdims=True) / m
    dA_prev = W.T @ dZ
    return dA_prev, dW, db

def update_parameters(params, grads, lr):
    for l in range(1, len(params) // 2 + 1):
        params[f"W{l}"] -= lr * grads[f"dW{l}"]
        params[f"b{l}"] -= lr * grads[f"db{l}"]
    return params
```

**Deep Neural Network: Application** trains a 4-layer [12288, 20, 7, 5, 1] network on the cat data: 80% test accuracy against 72% for the 2-layer network.

**Planar data classification with one hidden layer** (week 3) shows the payoff of a hidden layer on a 2-D "flower" dataset logistic regression can't separate (47% → 90% with 4 tanh units), and sweeps hidden size 1–50 to show overfitting.

### Ng ML ex4: the same in the older notation

Ex4 trains a 400–25–10 network on 5,000 handwritten digits, with rows as examples and the bias as an explicit column of ones. It adds the two checks you should do on any hand-written backprop:

```python
# Gradient checking: compare backprop to a centred finite difference
def numerical_grad(J, theta, eps=1e-4):
    g = np.zeros_like(theta)
    for i in range(theta.size):
        e = np.zeros_like(theta); e.flat[i] = eps
        g.flat[i] = (J(theta + e) - J(theta - e)) / (2 * eps)
    return g
# relative difference ||g_num - g_bp|| / ||g_num + g_bp|| should be < 1e-7; turn it off for training

# Random initialisation: break symmetry, or every hidden unit computes the same thing
eps_init = 0.12
Theta1 = np.random.uniform(-eps_init, eps_init, (25, 401))
```

Ex4 reaches ~96% training accuracy with `scipy.optimize.fmin_cg` and visualises the 25 hidden units as 20×20 images. DL course 2's **Gradient Checking** notebook repeats the check for an $L$-layer network with a deliberately planted bug to find.

---

## Making deep networks train (DL course 2)

### Initialization

| Scheme | Weights | Result on the course's "circles" data |
|---|---|---|
| Zeros | All 0 | Symmetry never broken: 50% accuracy, a flat line |
| Large random | `randn * 10` | Sigmoid saturates, slow, loss starts huge |
| He | `randn * sqrt(2 / n_prev)` | 96% test: the right default for ReLU |
| Xavier / Glorot | `randn * sqrt(1 / n_prev)` | The default for tanh |

The rule behind both: keep the variance of activations constant across layers so signals neither vanish nor explode. [16 — makemore](../../04-llms-from-scratch/notes/02-makemore.md#part-3-activations-gradients-and-batchnorm) revisits this with Kaiming init and activation histograms.

### Regularization

| Technique | Implementation | Effect in the notebook (French football goalkeeper data) |
|---|---|---|
| None | | 95% train, 91.5% test, wiggly boundary |
| L2 | Add $\frac{\lambda}{2m}\sum\lVert W\rVert_F^2$ to cost; $dW \mathrel{+}= \frac{\lambda}{m}W$ ("weight decay") | 94% / 93% |
| Dropout | Mask $D = (\text{rand} < p_{keep})$; $A \mathrel{*}= D / p_{keep}$ (inverted dropout); same mask in backward; **off at test time** | 93% / 95% |

### Optimization methods

| Optimiser | Update | Why |
|---|---|---|
| Mini-batch GD | Gradient on batches of 64–512 (powers of 2) | Progress before seeing all data |
| Momentum | $v = \beta v + (1-\beta) dW$; $W \mathrel{-}= \alpha v$ | Smooths oscillation; $\beta = 0.9$ |
| RMSprop | $s = \beta s + (1-\beta) dW^2$; $W \mathrel{-}= \alpha\, dW / \sqrt{s + \epsilon}$ | Per-parameter step size |
| Adam | Momentum + RMSprop + bias correction $\hat v = v / (1 - \beta_1^t)$ | Default; $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\epsilon = 10^{-8}$ |
| AdamW | The Adam step, then $W \mathrel{-}= \alpha\lambda W$ applied outside the gradient | L2 and weight decay are the same thing only for plain SGD. Inside Adam the L2 gradient is divided by $\sqrt{s}$, so weights with large gradients are barely regularised. Decoupling cut test error by about 15% relative for ResNets on CIFAR-10 and ImageNet 32×32, and made the best $\alpha$ independent of the best $\lambda$ ([arXiv:1711.05101](https://arxiv.org/abs/1711.05101) (Loshchilov & Hutter, ICLR 2019)). The LLM default, though the paper's evidence is image classification |
| Lion | $W \mathrel{-}= \alpha\,(\operatorname{sign}(\beta_1 v + (1-\beta_1) dW) + \lambda W)$; then $v = \beta_2 v + (1-\beta_2) dW$ | Found by program search. Keeps only momentum, so less optimizer memory than Adam. Needs a 3–10× smaller learning rate and 3–10× larger weight decay than AdamW. Saved up to 5× pre-training compute for ViT on JFT, with gains growing with batch size ([arXiv:2302.06675](https://arxiv.org/abs/2302.06675) (Chen et al., 2023-02)) |

On the "moons" data, after the same epochs: mini-batch GD 79.7%, momentum 79.7%, Adam 94%. Learning-rate decay and the *lectures'* batch normalisation complete the course; [17 — nanoGPT](../../04-llms-from-scratch/notes/03-nanogpt.md) uses AdamW with warmup and cosine decay.

### Tensorflow Tutorial

The course's first framework notebook: build a 3-layer softmax network for the SIGNS hand-gesture dataset in TF1 graph mode (placeholders, `tf.Session`, `tf.contrib.layers.xavier_initializer`). It is the notebook most broken by TF2; see the [migration section](#tensorflow-1x-to-2x-status-and-migration-map) below.

### The PyTorch training loop

The TF1 notebook's role in current code belongs to PyTorch. The loop is the same everywhere, and each line of it hides a common bug (*Build a Large Language Model (From Scratch)*, appendix A):

```python
train_loader = DataLoader(train_ds, batch_size=32, shuffle=True,
                          drop_last=True,       # a tiny last batch gives a noisy final update
                          num_workers=4)        # 0 = load in the main process; the GPU waits
for epoch in range(num_epochs):
    model.train()                               # dropout / batch-norm in training mode
    for x, y in train_loader:
        x, y = x.to(device), y.to(device)
        logits = model(x)                       # no softmax: cross_entropy applies log-softmax itself
        loss = F.cross_entropy(logits, y)
        optimizer.zero_grad()                   # gradients accumulate across .backward() calls by default
        loss.backward()
        optimizer.step()
    model.eval()
    with torch.no_grad():                       # no graph built: less memory, faster
        val_acc = (model(x_val).argmax(1) == y_val).float().mean()
torch.save(model.state_dict(), "model.pth")      # weights only; rebuild the class, then load_state_dict
```

`num_workers=4` is Raschka's rule of thumb for real datasets. Keep it at 0 for tiny datasets and in notebooks, where worker processes cost more than they save and can crash the kernel. To go multi-GPU with `DistributedDataParallel`, run one process per GPU (from a script; DDP doesn't work inside Jupyter) and change four things:

- call `init_process_group("nccl", rank=rank, world_size=world_size)` at startup;
- wrap the model with `DDP(model.to(rank), device_ids=[rank])`;
- give the loader `sampler=DistributedSampler(train_ds)` and `shuffle=False`, so each rank sees a disjoint shard;
- call `train_loader.sampler.set_epoch(epoch)` every epoch, or every epoch reuses the same order.

Gradients are averaged across replicas after each backward pass, so the replicas stay identical. [17](../../04-llms-from-scratch/notes/03-nanogpt.md) runs the same pattern at GPT-2 scale with `torchrun`.

---

## Convolutional networks (DL course 4)

| Notebook | Builds | Key idea |
|---|---|---|
| Convolution model: Step by Step | `zero_pad`, `conv_single_step`, `conv_forward`, `pool_forward` and their backward passes in NumPy | Output size $\lfloor (n + 2p - f)/s \rfloor + 1$; parameter sharing; pooling has no parameters |
| Convolution model: Application | CONV2D → RELU → MAXPOOL ×2 → FLATTEN → FC on SIGNS, in TF | Shape bookkeeping in a framework |
| Residual Networks | ResNet-50 in Keras: identity block and convolutional block | Skip connection $a^{[l+2]} = g(z^{[l+2]} + a^{[l]})$ makes very deep nets trainable; learning the identity is easy |
| Car detection (YOLO) | YOLOv2 post-processing on a pretrained model: box scores, filtering, IoU, non-max suppression | One forward pass predicts a 19×19×5 grid of anchor boxes |
| Face Recognition | FaceNet-style encodings, triplet loss $\max(\lVert f(A)-f(P)\rVert^2 - \lVert f(A)-f(N)\rVert^2 + \alpha, 0)$, verification vs recognition | Learn an embedding where distance = identity ([11](../../03-nlp/notes/04-embeddings-and-similarity.md)) |
| Neural Style Transfer | Content cost on one VGG-19 layer, style cost via Gram matrices across layers, optimise the *image* | Gradient descent on inputs, not weights |

Residual connections and learned embeddings with a contrastive loss are the two ideas from this course that carry straight into transformers and retrieval.

The convolutional design in the first notebook goes back to LeCun et al. ([doi:10.1109/5.726791](https://doi.org/10.1109/5.726791) (LeCun et al., Proc. IEEE 1998)). LeNet-5 combines three ideas: local receptive fields, shared weights and subsampling. Because of weight sharing, its 345,308 connections need only about 60,000 trainable parameters. The same paper introduced MNIST, with 60,000 training and 10,000 test digits drawn from two NIST sets. LeNet-5 reached 0.95% test error, or 0.8% with distorted copies of the training images added. For comparison, a linear classifier got 12%, a one-hidden-layer MLP 4.7%, and a regular SVM 1.4% at about 14M multiply-adds per digit. Schölkopf's virtual-support-vector SVM reached 1.0% at about twice that cost, and boosting three LeNet-4s gave the best result, 0.7%. Its later sections train a whole reading pipeline end to end through graphs of candidate segmentations, an ancestor of CTC, and a check reader built that way was in commercial use from 1996. It also describes a collapse problem. If the loss only pulls the correct output's learned target closer, the network can make all targets equal and ignore its input. The fix is a discriminative loss that also pushes wrong answers away, which is the job negatives do in the contrastive methods below.

Self-supervised vision took the contrastive loss further, with no labels at all. CPC v2 trained a ResNet to predict the representation of a patch from the patches around it (above, below, left and right; the first version used only the context above), scored against negatives drawn from other patches and images ([arXiv:1905.09272](https://arxiv.org/abs/1905.09272) (Hénaff et al., ICML 2020)). It reached 71.5% ImageNet linear-probe accuracy, up from 48.7% for the first version. With 1% of the labels it scored 78.3% top-5 against 44.1% for supervised training, though the two runs used different architectures (over 500M parameters against ResNet-200's 60M). MoCo and SimCLR changed the positive pair to two augmented views of the same image. MoCo keeps a queue of encoded keys from past batches, so the number of negatives no longer depends on batch size. Keys come from a slowly updated copy of the encoder, with momentum 0.999 ([arXiv:1911.05722](https://arxiv.org/abs/1911.05722) (He et al., CVPR 2020)). With no momentum training failed, and at 0.9 linear accuracy was 55.2% against 59.0%. Its own linear accuracy was only 60.6%, yet its features transferred better than supervised ImageNet pretraining on 7 detection and segmentation tasks, by up to 3.7 AP on VOC when pretrained on 1B Instagram images (2.4 from ImageNet). SimCLR dropped the queue. Its negatives are the other 2(N−1) augmented images in a large batch, scored by cosine similarity with a temperature (the NT-Xent loss) ([arXiv:2002.05709](https://arxiv.org/abs/2002.05709) (Chen et al., ICML 2020)). Random cropping combined with colour distortion was the augmentation pair that mattered. The representation taken before a small projection head was over 10 points better than the one after it. A 4×-wide ResNet-50 reached 76.5% linear-probe accuracy, matching a supervised ResNet-50. Large batches mattered most for short training. With the learning rate scaled linearly with batch size, at 100 epochs batch 256 gave 57.5% against 64.8% at 8,192 (square-root scaling narrowed that to 62.8%), and at 800 epochs the gap narrowed to 66.6% against 69.0%. Speech took the CPC line and added BERT-style masking. wav2vec 2.0 encodes raw audio with a CNN into one frame per 20 ms, masks about half the frames, and has a transformer pick the true quantized frame at each masked position out of 100 distractors from the same utterance ([arXiv:2006.11477](https://arxiv.org/abs/2006.11477) (Baevski et al., NeurIPS 2020)). Only the targets are quantized. Quantizing the transformer's inputs as well raised dev WER from 7.97 to 12.18, and continuous targets made the task too easy (8.58). Pretrained on 53k hours of unlabelled LibriVox audio and fine-tuned with CTC on just 10 minutes of transcribed speech, the 317M model reached 4.8/8.2 WER on LibriSpeech test-clean/other, and with 1 hour it beat the previous best 100-hour system. Those numbers need a language model at decoding: without one, the 10-minute model scored 40.2/38.7. With all 960 labelled hours it tied supervised systems on the clean split (1.8 against 1.9) and led only on the noisy one (3.3 against 3.9). The same recipe of a contrastive loss with in-batch negatives trains the text embedding models in [11](../../03-nlp/notes/04-embeddings-and-similarity.md).

---

## Sequence models (DL course 5)

| Notebook | Builds | Key idea |
|---|---|---|
| Building an RNN: Step by Step | `rnn_cell_forward`, `lstm_cell_forward` and backward passes in NumPy | $a^{\langle t\rangle} = \tanh(W_{aa} a^{\langle t-1\rangle} + W_{ax} x^{\langle t\rangle} + b_a)$; LSTM gates (forget, update, output) protect the cell state from vanishing gradients |
| Dinosaurus Island | Character-level RNN language model on dinosaur names; gradient clipping; sampling | The same task as [16 — makemore](../../04-llms-from-scratch/notes/02-makemore.md), with an RNN instead of an MLP |
| Jazz improvisation with LSTM | Keras LSTM that generates music values; inference loop feeding samples back in | Training vs autoregressive sampling |
| Operations on word vectors | Cosine similarity, analogies with GloVe (`man : woman :: king : ?`), debiasing by neutralise/equalise | Embedding geometry; bias in embeddings ([11](../../03-nlp/notes/04-embeddings-and-similarity.md)) |
| Emojify | Average of GloVe vectors → softmax; then a 2-layer LSTM over the embeddings | Pretrained embeddings let 127 training sentences generalise |
| Neural machine translation with attention | Date normalisation ("3 May 1979" → "1979-05-03") with a Bi-LSTM encoder and attention | Attention weights $\alpha^{\langle t, t'\rangle} = \text{softmax}(e)$: the bridge to [17](../../04-llms-from-scratch/notes/03-nanogpt.md) |
| Trigger word detection | Synthesise audio training data, spectrogram → Conv1D → GRU → per-timestep sigmoid | Data synthesis; sequence labelling |

**Structuring Machine Learning Projects** (course 3) has no programming notebook; its content (orthogonalisation, single-number metric, train/dev/test from the same distribution, error analysis, human-level performance as a proxy for Bayes error) is the practical half of [04](../../01-classical-ml/notes/04-model-evaluation.md).

---

## TensorFlow 1.x to 2.x: status and migration map

Most Ng DL notebooks were written for TF 1.x and standalone Keras 2.x. Phase 1 (#36) put `import tensorflow.compat.v1 as tf` + `tf.disable_v2_behavior()` into the TF notebooks. Two notebooks still use `tf.contrib`, which does not exist in TF2 at all, so compat mode can't save them.

| Notebook | Status | Blocker |
|---|---|---|
| `Improving Deep Neural Networks.../Tensorflow Tutorial.ipynb` | Phase 1 done | `tf.contrib.layers.xavier_initializer`: **Phase 2 required** |
| `Convolutional Neural Networks/Week1/Convolution model - Application.ipynb` | Phase 1 done | `tf.contrib.layers.flatten`, `fully_connected`, `xavier_initializer`: **Phase 2 required** |
| `CNN/Week2/ResNets/Residual Networks.ipynb` | Phase 1 done | Standalone Keras; runs with TF2 via compat.v1 |
| `CNN/Week3/Car detection.../Autonomous driving application.ipynb` | Phase 1 done | No `tf.contrib`; needs `yad2k` and YOLO weights |
| `CNN/Week4/Face Recognition for the Happy House.ipynb` | Phase 1 done | No `tf.contrib`; `keras.engine.topology` import is gone in Keras ≥2.4 |
| `CNN/Week4/Art Generation with Neural Style Transfer.ipynb` | Phase 1 done | No `tf.contrib`; needs VGG-19 weights |
| Course 5 Keras notebooks | Not migrated | Standalone `keras` 2.x imports (`keras.layers.embeddings`) |
| NumPy-only notebooks (courses 1, 2 except TF Tutorial; CNN Step by Step; RNN Step by Step; word vectors) | No TF | NumPy only |

**Phase 2 map** for the two `tf.contrib` notebooks:

| TF 1.x | TF 2.x |
|---|---|
| `tf.contrib.layers.xavier_initializer(seed=N)` | `tf.keras.initializers.GlorotUniform(seed=N)` |
| `tf.contrib.layers.flatten(P)` | `tf.keras.layers.Flatten()(P)` or `tf.reshape(P, [tf.shape(P)[0], -1])` |
| `tf.contrib.layers.fully_connected(F, n, activation_fn=None)` | `tf.keras.layers.Dense(n, activation=None)(F)` |
| `tf.get_variable(name, shape, initializer=...)` | `tf.Variable(initializer(shape=shape))` |
| `tf.placeholder(dtype, shape)` | Function argument, or `tf.keras.Input(shape)` |
| `with tf.Session() as sess: sess.run(op)` | Eager: `op.numpy()`; wrap hot functions in `@tf.function` |
| `keras.layers.X` (standalone) | `tf.keras.layers.X` (or Keras 3 `keras.layers.X` with a backend) |

The text notebooks' TF status (Sarkar Ch10a fixed; the condensed NLP course was TF2-native) is in [14](02-neural-text-models.md#tensorflow-status-of-the-text-notebooks).

---

## Reading

*Fundamentals of Deep Learning* (Buduma) in [`../sources/buduma-fundamentals-of-deep-learning.pdf`](../../sources/buduma-fundamentals-of-deep-learning.pdf): chapters on the neuron, training feed-forward networks, gradient descent variants and CNNs parallel DL courses 1, 2 and 4.

---

## Practice

All of these are your own Coursera submissions, kept untouched; outputs are not stored.

| Set | Runs |
|---|---|
| [`Ng's Machine Learning Nbks/ex4`](../../01-classical-ml/practice/ng-machine-learning/ex4/ex4.ipynb) | Legacy: Python 2.7 kernel; `scipy.misc.toimage` removed in SciPy 1.2; data in `ex4/data/` |
| [`Ng's Deep Learning Nbks/`](../practice/ng-deep-learning) (22 notebooks) | Legacy, reading-only as stored: Python 3.5–3.6 kernels; the Coursera helper modules (`lr_utils`, `dnn_app_utils`, `yad2k`, `emo_utils`, ...), `datasets/` and pretrained weights were not copied into the repo. NumPy-only notebooks run once their helpers and data are restored; TF ones per the table above |

---

→ Next: [08-text-representation.md](../../03-nlp/notes/01-text-representation.md) — the NLP arc starts: turning text into features.
