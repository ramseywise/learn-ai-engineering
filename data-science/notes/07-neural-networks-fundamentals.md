---
origin: own coursework (Ng Machine Learning ex4; Ng Deep Learning Specialization) + curated
sources:
  - ../Ng's Machine Learning Nbks/ex4/ex4.ipynb
  - ../Ng's Deep Learning Nbks/
  - https://www.coursera.org/specializations/deep-learning
  - ../sources/buduma-fundamentals-of-deep-learning.pdf
  - https://www.tensorflow.org/guide/migrate
confidence: high
cleaned: 2026-10-31
---
# 7 — Neural Network Fundamentals

> A neural network is logistic regression stacked: forward pass, loss, backward pass by the chain rule, gradient step. Your Ng coursework builds that by hand in NumPy, then adds what makes deep networks train (initialisation, regularisation, optimisers, batch norm), then the two architectures that dominated before transformers: CNNs and RNNs.

The sklearn `MLPClassifier` in [02](02-supervised-learning.md#neural-networks-multilayer-perceptrons) hides all of this. This note opens it up; [15 — micrograd](15-micrograd.md) does it again as an autograd engine.

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

The rule behind both: keep the variance of activations constant across layers so signals neither vanish nor explode. [16 — makemore](16-makemore.md#part-3-activations-gradients-and-batchnorm) revisits this with Kaiming init and activation histograms.

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

On the "moons" data, after the same epochs: mini-batch GD 79.7%, momentum 79.7%, Adam 94%. Learning-rate decay and the *lectures'* batch normalisation complete the course; [17 — nanoGPT](17-nanogpt.md) uses AdamW with warmup and cosine decay.

### Tensorflow Tutorial

The course's first framework notebook: build a 3-layer softmax network for the SIGNS hand-gesture dataset in TF1 graph mode (placeholders, `tf.Session`, `tf.contrib.layers.xavier_initializer`). It is the notebook most broken by TF2; see the [migration section](#tensorflow-1x-to-2x-status-and-migration-map) below.

---

## Convolutional networks (DL course 4)

| Notebook | Builds | Key idea |
|---|---|---|
| Convolution model: Step by Step | `zero_pad`, `conv_single_step`, `conv_forward`, `pool_forward` and their backward passes in NumPy | Output size $\lfloor (n + 2p - f)/s \rfloor + 1$; parameter sharing; pooling has no parameters |
| Convolution model: Application | CONV2D → RELU → MAXPOOL ×2 → FLATTEN → FC on SIGNS, in TF | Shape bookkeeping in a framework |
| Residual Networks | ResNet-50 in Keras: identity block and convolutional block | Skip connection $a^{[l+2]} = g(z^{[l+2]} + a^{[l]})$ makes very deep nets trainable; learning the identity is easy |
| Car detection (YOLO) | YOLOv2 post-processing on a pretrained model: box scores, filtering, IoU, non-max suppression | One forward pass predicts a 19×19×5 grid of anchor boxes |
| Face Recognition | FaceNet-style encodings, triplet loss $\max(\lVert f(A)-f(P)\rVert^2 - \lVert f(A)-f(N)\rVert^2 + \alpha, 0)$, verification vs recognition | Learn an embedding where distance = identity ([11](11-embeddings-and-similarity.md)) |
| Neural Style Transfer | Content cost on one VGG-19 layer, style cost via Gram matrices across layers, optimise the *image* | Gradient descent on inputs, not weights |

Residual connections and learned embeddings with a contrastive loss are the two ideas from this course that carry straight into transformers and retrieval.

---

## Sequence models (DL course 5)

| Notebook | Builds | Key idea |
|---|---|---|
| Building an RNN: Step by Step | `rnn_cell_forward`, `lstm_cell_forward` and backward passes in NumPy | $a^{\langle t\rangle} = \tanh(W_{aa} a^{\langle t-1\rangle} + W_{ax} x^{\langle t\rangle} + b_a)$; LSTM gates (forget, update, output) protect the cell state from vanishing gradients |
| Dinosaurus Island | Character-level RNN language model on dinosaur names; gradient clipping; sampling | The same task as [16 — makemore](16-makemore.md), with an RNN instead of an MLP |
| Jazz improvisation with LSTM | Keras LSTM that generates music values; inference loop feeding samples back in | Training vs autoregressive sampling |
| Operations on word vectors | Cosine similarity, analogies with GloVe (`man : woman :: king : ?`), debiasing by neutralise/equalise | Embedding geometry; bias in embeddings ([11](11-embeddings-and-similarity.md)) |
| Emojify | Average of GloVe vectors → softmax; then a 2-layer LSTM over the embeddings | Pretrained embeddings let 127 training sentences generalise |
| Neural machine translation with attention | Date normalisation ("3 May 1979" → "1979-05-03") with a Bi-LSTM encoder and attention | Attention weights $\alpha^{\langle t, t'\rangle} = \text{softmax}(e)$: the bridge to [17](17-nanogpt.md) |
| Trigger word detection | Synthesise audio training data, spectrogram → Conv1D → GRU → per-timestep sigmoid | Data synthesis; sequence labelling |

**Structuring Machine Learning Projects** (course 3) has no programming notebook; its content (orthogonalisation, single-number metric, train/dev/test from the same distribution, error analysis, human-level performance as a proxy for Bayes error) is the practical half of [04](04-model-evaluation.md).

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

The text notebooks' TF status (Sarkar Ch10a fixed; the condensed NLP course was TF2-native) is in [14](14-neural-text-models.md#tensorflow-status-of-the-text-notebooks).

---

## Reading

*Fundamentals of Deep Learning* (Buduma) in [`../sources/buduma-fundamentals-of-deep-learning.pdf`](../sources/buduma-fundamentals-of-deep-learning.pdf): chapters on the neuron, training feed-forward networks, gradient descent variants and CNNs parallel DL courses 1, 2 and 4.

---

## Practice

All of these are your own Coursera submissions, kept untouched; outputs are not stored.

| Set | Runs |
|---|---|
| [`Ng's Machine Learning Nbks/ex4`](../Ng's%20Machine%20Learning%20Nbks/ex4/ex4.ipynb) | Legacy: Python 2.7 kernel; `scipy.misc.toimage` removed in SciPy 1.2; data in `ex4/data/` |
| [`Ng's Deep Learning Nbks/`](../Ng's%20Deep%20Learning%20Nbks/) (22 notebooks) | Legacy, reading-only as stored: Python 3.5–3.6 kernels; the Coursera helper modules (`lr_utils`, `dnn_app_utils`, `yad2k`, `emo_utils`, ...), `datasets/` and pretrained weights were not copied into the repo. NumPy-only notebooks run once their helpers and data are restored; TF ones per the table above |

---

→ Next: [08-text-representation.md](08-text-representation.md) — the NLP arc starts: turning text into features.
