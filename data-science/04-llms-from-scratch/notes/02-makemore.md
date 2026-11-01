---
origin: vendored snapshot: nn-zero-to-hero (Karpathy, MIT; kept as practice)
sources:
  - ../practice/nn-zero-to-hero/makemore/
  - ../../sources/ioffe-2015-batch-normalization.pdf
  - ../../sources/wu-2021-rethinking-batch-batchnorm.pdf
  - https://github.com/karpathy/makemore
  - Bengio et al. 2003, A Neural Probabilistic Language Model
  - van den Oord et al. 2016, WaveNet
  - https://arxiv.org/abs/2105.07576
  - https://arxiv.org/abs/1609.03499
  - https://arxiv.org/abs/1607.06450
confidence: high
cleaned: 2026-10-31
---
# 16 — makemore: Character-Level Language Models

> Five lectures on one task: given a dataset of 32,033 names, learn to generate new ones that sound like names. The model gets better at each step (bigram counts → neural bigram → MLP → deep MLP with BatchNorm → WaveNet-style hierarchy), and along the way you learn the whole language-modelling framework, how to keep a deep network trainable, and how to backpropagate through tensors by hand.

The arc continues from [15](01-micrograd.md) (scalar autograd) and ends at [17](03-nanogpt.md) (the transformer).

---

## The framework: a language model is a next-token distribution

A language model assigns a probability to the next token given the previous ones, `P(x_t | x_<t)`. Train it by maximising the likelihood of the data, which is the same as minimising the **average negative log-likelihood** (cross-entropy) of each true next character. Generate by sampling from the distribution one token at a time and feeding the sample back in.

Setup used throughout: 26 letters plus `.` as a start/end token (27 classes), `stoi`/`itos` maps, and an 80/10/10 train/dev/test split of the names.

```python
words = open("names.txt").read().splitlines()          # 32,033 names, from the makemore repo
chars = sorted(set("".join(words)))
stoi = {s: i + 1 for i, s in enumerate(chars)}; stoi["."] = 0
itos = {i: s for s, i in stoi.items()}
```

A model that guesses uniformly over 27 characters has loss `−log(1/27) = 3.30`. Every model below is measured against that.

---

## Part 1: bigrams, counted and learned

**Counting.** Tally how often each character follows each other one in a 27×27 matrix, normalise rows into probabilities, sample.

```python
N = torch.zeros((27, 27), dtype=torch.int32)
for w in words:
    chs = ["."] + list(w) + ["."]
    for c1, c2 in zip(chs, chs[1:]):
        N[stoi[c1], stoi[c2]] += 1

P = (N + 1).float()                     # +1 = add-one smoothing: no zero probabilities, no infinite loss
P /= P.sum(1, keepdim=True)             # keepdim matters: (27,1) broadcasts across columns correctly;
                                        # P.sum(1) is (27,) and broadcasts across ROWS — a silent bug
g = torch.Generator().manual_seed(2147483647)
ix, out = 0, []
while True:
    ix = torch.multinomial(P[ix], num_samples=1, generator=g).item()
    if ix == 0: break
    out.append(itos[ix])
```

Loss over the training set: about **2.45**. Samples ("mor", "axx", "minaymoryles") are name-ish and mostly bad: one character of context is not enough.

**The same model as a neural network.** One-hot encode the previous character, multiply by a 27×27 weight matrix to get *logits* (log-counts), exponentiate and normalise (softmax), and train `W` by gradient descent on the NLL.

```python
xenc = F.one_hot(xs, num_classes=27).float()     # (n, 27)
W = torch.randn((27, 27), generator=g, requires_grad=True)
for k in range(100):
    logits = xenc @ W                             # selecting row xs of W, really
    probs = logits.exp() / logits.exp().sum(1, keepdim=True)
    loss = -probs[torch.arange(len(ys)), ys].log().mean() + 0.01 * (W**2).mean()
    W.grad = None
    loss.backward()
    W.data += -50 * W.grad
```

It converges to the same ~2.45, because it *is* the same model: `W.exp()` ends up proportional to the count matrix. Two lessons: the L2 term plays the role of add-one smoothing (pulling `W` towards 0 makes the distribution more uniform), and the neural version scales to more context where the counting table would explode (27ⁿ rows).

---

## Part 2: an MLP over a context window (Bengio et al. 2003)

Use the previous `block_size = 3` characters. Embed each into a learned vector, concatenate, pass through a hidden layer.

```python
def build_dataset(words, block_size=3):
    X, Y = [], []
    for w in words:
        context = [0] * block_size                 # start padded with '.'
        for ch in w + ".":
            X.append(context); Y.append(stoi[ch])
            context = context[1:] + [stoi[ch]]     # slide the window
    return torch.tensor(X), torch.tensor(Y)

C  = torch.randn((27, 10))          # embedding table: 27 chars → 10-d
W1 = torch.randn((30, 200)); b1 = torch.randn(200)
W2 = torch.randn((200, 27)); b2 = torch.randn(27)

for i in range(200_000):
    ix = torch.randint(0, Xtr.shape[0], (32,))                 # minibatch of 32
    emb = C[Xtr[ix]]                                           # (32, 3, 10): indexing IS the embedding lookup
    h = torch.tanh(emb.view(-1, 30) @ W1 + b1)                 # (32, 200)
    logits = h @ W2 + b2                                       # (32, 27)
    loss = F.cross_entropy(logits, Ytr[ix])                    # fused, numerically stable softmax + NLL
    for p in params: p.grad = None
    loss.backward()
    lr = 0.1 if i < 100_000 else 0.01                          # step decay
    for p in params: p.data += -lr * p.grad
```

| Technique introduced | Detail |
|---|---|
| Minibatches | The gradient from 32 examples is noisy but cheap; many approximate steps beat few exact ones |
| `F.cross_entropy` over hand-written softmax | Subtracts the max logit internally; `exp` of large logits would overflow to `inf` |
| Learning-rate finder | Sweep `lr = 10**linspace(-3, 0)` over 1,000 steps, plot loss vs exponent, pick the valley (~0.1) |
| Train / dev / test | Tune on dev; touch test once. With 11k params and 228k examples, train ≈ dev means underfitting: scale up |
| Embedding visualisation | With 2-d embeddings, vowels cluster together: the model learned that they are interchangeable-ish |

Dev loss: about **2.17**. Samples become plausible ("carmahela", "jhovi", "kimrin").

---

## Part 3: activations, gradients and BatchNorm

The MLP trains, but the start of training is wasteful and deeper versions don't train at all. The lecture diagnoses why, one fix at a time, with the dev loss logged after each:

| Step | Problem seen | Fix | Train / val |
|---|---|---|---|
| Original | First loss ~27 instead of 3.30: logits are huge, so softmax is confidently wrong; the "hockey stick" loss curve is the network wasting steps shrinking them | — | 2.12 / 2.17 |
| 1 | Confidently wrong softmax | Initialise `W2 * 0.01`, `b2 * 0` so initial logits ≈ 0 and loss ≈ 3.30 | 2.07 / 2.13 |
| 2 | Histogram of `h` piles up at ±1: tanh is **saturated**, its local gradient `1 − t²` ≈ 0, so gradients vanish; a neuron that is saturated for every example is dead | Scale `W1` down (`* 0.2`) so pre-activations are small | 2.04 / 2.10 |
| 3 | The 0.2 was hand-tuned | **Kaiming init**: `W1 * gain / sqrt(fan_in)`, gain 5/3 for tanh (√2 for ReLU) | 2.04 / 2.11 |
| 4 | Init still fragile in deep nets | **BatchNorm** after the linear layer | 2.07 / 2.10 |

Kaiming scaling keeps the variance of activations roughly constant from layer to layer: with unit-variance inputs and `fan_in` inputs per neuron, weights of std `1/sqrt(fan_in)` give unit-variance pre-activations, and the gain compensates for the nonlinearity squashing them. `torch.nn.init.kaiming_normal_` does it.

### BatchNorm

Make the pre-activations unit Gaussian *by construction*, per minibatch, then let the network rescale them:

```python
hpreact = embcat @ W1                                    # no bias: BatchNorm's beta replaces it
mean, std = hpreact.mean(0, keepdim=True), hpreact.std(0, keepdim=True)
hpreact = bngain * (hpreact - mean) / std + bnbias       # gamma, beta are learned
with torch.no_grad():                                    # running stats for inference
    bnmean_running = 0.999 * bnmean_running + 0.001 * mean
    bnstd_running  = 0.999 * bnstd_running  + 0.001 * std
```

| Property | Consequence |
|---|---|
| Normalises with **batch** statistics | Each example's output depends on the others in its batch: a jitter that acts as a regulariser |
| Training vs inference differ | At inference use running (or post-training calibrated) mean/var; forgetting `model.eval()` is a classic bug |
| Makes the preceding bias redundant | Use `bias=False` in the linear layer before it |
| Small batches → noisy statistics | Hence LayerNorm (normalise across features of one example) in transformers ([17](03-nanogpt.md)) |

Wu & Johnson's *Rethinking "Batch" in BatchNorm* ([arXiv:2105.07576](https://arxiv.org/abs/2105.07576), 2021-05) catalogues the problems that come from that batch dependence, using ImageNet ResNet-50s. The running average in the code above lags behind the weights. That is worst early in training and in large-batch runs, where the learning rate is higher and there are fewer updates. With a total batch of 8,192 the validation error swung from epoch to epoch. **Recomputing the statistics once after training on 10³–10⁴ samples** ("PreciseBN", the calibrated option in the table) stayed stable and cost about 0.5% extra compute if done every epoch. It also cut error by 3.5 points for a model normalised over batches of 2. The other caveats are that small normalisation batches widen the gap between training and test behaviour, and that mixing domains in one batch shifts the statistics. Examples in a batch can also leak information to each other through the shared mean. Ioffe & Szegedy's original ([PDF](../../sources/ioffe-2015-batch-normalization.pdf)) motivated it as reducing "internal covariate shift", an explanation later work disputes even though the method works. Ba et al. introduced LayerNorm to remove exactly this batch dependence. It takes the mean and variance over one example's hidden units, so it runs at batch size 1 and does the same thing in training and inference. They tested it in recurrent networks. In convolutional nets they found that BatchNorm still won ([arXiv:1607.06450](https://arxiv.org/abs/1607.06450) (Ba et al., 2016, preprint)).

### PyTorch-ifying, and the diagnostics to look at

The lecture rewrites the network as `Linear`, `BatchNorm1d`, `Tanh` classes with the `torch.nn` API, stacks them deeper, and plots four things during the first ~1,000 steps:

| Plot | Healthy |
|---|---|
| Histogram of each tanh layer's outputs | Saturation (\|t\| > 0.97) under ~5%; similar spread across layers |
| Histogram of gradients at each layer | Similar magnitude across layers: none vanishing or exploding |
| Weight-gradient to data std ratio per parameter | Roughly the same order everywhere; the last layer often stands out at init |
| **Update-to-data ratio** `log10(std(lr * grad) / std(data))` over steps | Around **−3**: each step changes a weight by ~1/1000 of its size. Much lower: lr too small; much higher: too large |

These plots are the tool for "my deep net won't train". [07](../../02-deep-learning/notes/01-neural-networks-fundamentals.md) covers the same initialisation and normalisation ideas from Ng's course.

---

## Part 4: becoming a backprop ninja

Write the backward pass of the whole MLP (embedding, linear, BatchNorm, tanh, linear, cross-entropy) by hand at the tensor level, and check each gradient against autograd with a `cmp(name, dt, t)` helper. The forward pass is broken into atomic steps (`logit_maxes`, `norm_logits`, `counts`, `counts_sum_inv`, `probs`, `logprobs`) so each can be differentiated alone.

Rules that cover nearly every line:

| Forward | Backward |
|---|---|
| `y = a @ W` | `da = dy @ W.T`, `dW = a.T @ dy` (shapes force the answer) |
| `y = x.sum(dim, keepdim=True)` | `dx = dy` broadcast back |
| Broadcast in the forward pass (`counts * counts_sum_inv`, a (n,1) column) | **Sum** over the broadcast dimension in the backward |
| Variable used twice | Gradients add (`+=`), as in micrograd |
| `y = tanh(x)` | `dx = (1 − y²) * dy` |
| `emb = C[X]` | Scatter-add rows of `demb` into `dC` at the indices in `X` |

Then the two analytic shortcuts:

```python
# Cross-entropy all at once: gradient of mean NLL w.r.t. logits is (softmax − one_hot) / n
dlogits = F.softmax(logits, 1)
dlogits[range(n), Yb] -= 1
dlogits /= n
# Intuition: each row pulls the wrong classes' logits down by their probability and pushes
# the correct one up by (1 − p); the pulls and pushes in a row sum to zero.

# BatchNorm all at once (bnraw = normalised input, bnvar_inv = 1/sqrt(var + eps), Bessel n−1):
dhprebn = bngain * bnvar_inv / n * (n * dhpreact - dhpreact.sum(0)
            - n / (n - 1) * bnraw * (dhpreact * bnraw).sum(0))
```

Why bother when autograd exists: backprop is a *leaky abstraction*. Knowing that saturated tanh kills gradient, that `dlogits` is `p − y`, or that BatchNorm couples examples is what lets you debug training that silently fails.

---

## Part 5: a WaveNet-style hierarchy

Longer context helps, but crushing 8 characters into one hidden layer at once is crude. WaveNet fuses information gradually: pairs of characters, then pairs of pairs.

```python
class FlattenConsecutive:            # (B, T, C) → (B, T/n, C·n): concatenate n neighbours
    def __init__(self, n): self.n = n
    def __call__(self, x):
        B, T, C = x.shape
        x = x.view(B, T // self.n, C * self.n)
        return x.squeeze(1) if x.shape[1] == 1 else x

model = Sequential([
    Embedding(vocab_size, 24),                                                       # block_size = 8
    FlattenConsecutive(2), Linear(24 * 2, 128, bias=False), BatchNorm1d(128), Tanh(),  # 8 → 4
    FlattenConsecutive(2), Linear(128 * 2, 128, bias=False), BatchNorm1d(128), Tanh(), # 4 → 2
    FlattenConsecutive(2), Linear(128 * 2, 128, bias=False), BatchNorm1d(128), Tanh(), # 2 → 1
    Linear(128, vocab_size),
])
```

`Linear` works on 3-d input because `@` broadcasts over leading dimensions. **The bug:** the hand-written `BatchNorm1d` computed statistics over dimension 0 only, so with (B, T, C) input it kept separate statistics for each of the T positions. The fix reduces over `(0, 1)`:

```python
dim = 0 if x.ndim == 2 else (0, 1)
xmean, xvar = x.mean(dim, keepdim=True), x.var(dim, keepdim=True)
```

(PyTorch's `nn.BatchNorm1d` expects (B, C, T), channels in the middle, which is another way to get this wrong.)

The performance log from the notebook:

| Change | Params | Train | Val |
|---|---|---|---|
| Part 3 MLP: context 3, 200 hidden | 12k | 2.058 | 2.105 |
| Context 3 → 8 (flat) | 22k | 1.918 | 2.027 |
| Flat → hierarchical | 22k | 1.941 | 2.029 |
| Fix BatchNorm bug | 22k | 1.912 | 2.022 |
| Scale up: n_embd 24, n_hidden 128 | 76k | 1.769 | **1.993** |

The closing preview: running the model at every position of a name separately repeats work. A **dilated causal convolution** computes all positions in one pass, sharing the intermediate nodes; that is WaveNet proper, and the same "process every position in parallel" idea is what the transformer does with attention.

The original WaveNet ([arXiv:1609.03499](https://arxiv.org/abs/1609.03499) (van den Oord et al., SSW 2016)) predicts raw audio, at least 16,000 samples a second, using the same next-token setup as these names. Dilations of 1, 2, 4, …, 512 give each block a receptive field of 1,024 samples, and several blocks are stacked. A μ-law transform squashes 16-bit audio to 256 classes, so the output is a 256-way softmax, the same as a character vocabulary, instead of 65,536 values. The parallelism holds only during training. Sampling still feeds each new sample back in as input, one step at a time. In blind listening tests on US English text-to-speech, it scored a mean opinion score of 4.21 out of 5, against 3.86 for the best concatenative system and 4.55 for natural 16-bit speech. Its receptive field was still only about 240–300 ms, which the authors say is too short for long-range coherence or prosody in speech. The music models had receptive fields of several seconds and still lacked long-range consistency.

---

## Results across the series

| Model | Context | Val loss |
|---|---|---|
| Uniform | — | 3.30 |
| Bigram (counts or one-layer net) | 1 char | ~2.45 |
| MLP (Part 2) | 3 | ~2.17 |
| MLP + init fixes + BatchNorm (Part 3) | 3 | ~2.10 |
| WaveNet-style (Part 5) | 8 | ~1.99 |
| Transformer ([17](03-nanogpt.md)) | block_size | lower again; the makemore repo's transformer reaches ~1.9 |

---

## Practice

All need `names.txt` from [karpathy/makemore](https://github.com/karpathy/makemore) (not in this snapshot) next to the notebook, plus `torch` and `matplotlib`; CPU is enough.

| Notebook | Covers | Runs |
|---|---|---|
| [`makemore_part1_bigrams`](../practice/nn-zero-to-hero/makemore/makemore_part1_bigrams.ipynb) | Counting, sampling, NLL, one-hot neural bigram | Needs `names.txt`; runs offline after |
| [`makemore_part2_mlp`](../practice/nn-zero-to-hero/makemore/makemore_part2_mlp.ipynb) | Embeddings, MLP, minibatches, lr finder, splits | Needs `names.txt` |
| [`makemore_part3_bn`](../practice/nn-zero-to-hero/makemore/makemore_part3_bn.ipynb) | Init, saturation, Kaiming, BatchNorm, diagnostics | Needs `names.txt` |
| [`makemore_part4_backprop`](../practice/nn-zero-to-hero/makemore/makemore_part4_backprop.ipynb) | Manual tensor backprop, the exercises | Needs `names.txt`; exercise cells are blanks to fill |
| [`makemore_part5_cnn1`](../practice/nn-zero-to-hero/makemore/makemore_part5_cnn1.ipynb) | Hierarchical model, `FlattenConsecutive`, BatchNorm 3-d bug | Needs `names.txt` |

---

→ Next: [17-nanogpt.md](03-nanogpt.md) — self-attention, the transformer block, and reproducing GPT-2 (124M).
