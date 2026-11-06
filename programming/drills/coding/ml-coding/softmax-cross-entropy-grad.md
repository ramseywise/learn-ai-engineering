---
title: "Softmax cross-entropy: stable loss and its gradient"
track: coding
topic: ml-coding
difficulty: medium
timebox_min: 25
concepts: [ml-coding]
units: [programming/computer-science/notes/04-numbers-and-memory.md, generative-ai/01-llm-fundamentals/notes/06-pretraining-data-and-objectives.md]
source: original
---
## Prompt

A classifier outputs logits `Z` of shape `(n, k)`: one row per example, one column per class. The labels `y` are
integers in `[0, k)`, shape `(n,)`. Do [Softmax in NumPy](softmax-numpy.md) first. This drill builds on it.

1. `log_softmax(Z)`: the log of the row-wise softmax. It must stay finite for logits like 1000 and -1000, so don't
   take `np.log(softmax(Z))`. Use log-sum-exp.
2. `cross_entropy(Z, y)`: the mean over rows of `-log p[i, y[i]]`.
3. `ce_grad(Z, y)`: the gradient of that mean loss with respect to `Z`, shape `(n, k)`. Derive it on paper first.
   It has a two-term closed form. Don't modify `Z`.

## Starter

Blank file in `programming/drills/coding/scratch/`. NumPy only.

## Tests

Put your three functions above this block in a file and run it. Every assertion must pass.

```python
rng = np.random.default_rng(0)
n, k = 8, 5
Z = rng.normal(size=(n, k))
y = rng.integers(0, k, size=n)

# 1. small logits: matches the naive formula
naive = np.log(np.exp(Z) / np.exp(Z).sum(axis=1, keepdims=True))
assert np.allclose(log_softmax(Z), naive)
# 2. each row of exp(log_softmax) sums to 1
assert np.allclose(np.exp(log_softmax(Z)).sum(axis=1), 1)
# 3. huge logits: finite, and shift-invariant
big = np.array([[1000.0, 999.0, -1000.0]])
assert np.all(np.isfinite(log_softmax(big)))
assert np.allclose(log_softmax(big), log_softmax(big - 1000.0))
# 4. a confidently wrong prediction gives a large finite loss, not inf
assert np.isclose(cross_entropy(np.array([[0.0, 1000.0]]), np.array([0])), 1000.0)
# 5. uniform logits: loss is log(k)
assert np.isclose(cross_entropy(np.zeros((n, k)), y), np.log(k))
# 6. gradient shape, and each row sums to 0 (probabilities sum to 1, the one-hot sums to 1)
G = ce_grad(Z, y)
assert G.shape == (n, k)
assert np.allclose(G.sum(axis=1), 0)
# 7. gradient check against central differences
eps = 1e-6
num = np.zeros_like(Z)
for i in range(n):
    for j in range(k):
        E = np.zeros_like(Z); E[i, j] = eps
        num[i, j] = (cross_entropy(Z + E, y) - cross_entropy(Z - E, y)) / (2 * eps)
assert np.linalg.norm(G - num) / (np.linalg.norm(G) + np.linalg.norm(num)) < 1e-6
# 8. gradient at huge logits is finite
assert np.all(np.isfinite(ce_grad(big, np.array([2]))))
# 9. ce_grad doesn't modify its input
Z1 = rng.normal(size=(n, k)); Z0 = Z1.copy()
ce_grad(Z1, y)
assert np.array_equal(Z1, Z0)
```

## Hints

One at a time. Open the next only after trying with the last.

<details><summary>Hint 1</summary>

`log softmax(z)_j = z_j - log sum_i exp(z_i)`. Subtract the row max `m` inside the log-sum-exp and add it back
outside: `log sum exp(z_i) = m + log sum exp(z_i - m)`.

</details>

<details><summary>Hint 2</summary>

For one row with label `c`, the loss is `-z_c + log sum_i exp(z_i)`. Differentiate each term with respect to `z_j`.
The first gives `-1` only when `j = c`. The second gives `softmax(z)_j`.

</details>

<details><summary>Hint 3</summary>

So the gradient of one row is `p - onehot(c)`. For the mean over `n` rows, divide by `n`. Use
`P[np.arange(n), y]` to touch exactly one entry per row. `P[:, y]` touches whole columns.

</details>

## Solution

<details><summary>Solution: derivation and code</summary>

For one row $z$ with label $c$, $\ell(z) = -\log \frac{e^{z_c}}{\sum_i e^{z_i}} = -z_c + \log \sum_i e^{z_i}$.
Then $\frac{\partial \ell}{\partial z_j} = -[j = c] + \frac{e^{z_j}}{\sum_i e^{z_i}} = p_j - [j = c]$.
Stacked over rows and averaged, the gradient is $G = (P - Y)/n$, where $Y$ is the one-hot label matrix.
Each row of $G$ sums to zero, because both $p$ and the one-hot row sum to 1 (test 6).

```python
import numpy as np

def log_softmax(Z):
    m = Z.max(axis=-1, keepdims=True)
    return Z - m - np.log(np.exp(Z - m).sum(axis=-1, keepdims=True))

def cross_entropy(Z, y):
    n = Z.shape[0]
    return -log_softmax(Z)[np.arange(n), y].mean()

def ce_grad(Z, y):
    n = Z.shape[0]
    P = np.exp(log_softmax(Z))
    P[np.arange(n), y] -= 1
    return P / n
```

`log_softmax` never forms a probability and then takes its log, so a probability that underflows to 0 can't become
`-inf`. That is test 4. The softmax-then-log version returns `inf` for a confidently wrong logit of 1000.
`exp(log_softmax(Z))` returns a new array, so the in-place `-= 1` doesn't touch `Z`.

**Complexity**: O(nk) time and memory for all three functions.

</details>

## Notes

- **Why the gradient is this simple.** The `log` in cross-entropy cancels the `exp` in softmax. Frameworks fuse
  them for that reason (PyTorch's `cross_entropy` takes logits, not probabilities), so the backward pass never
  divides by a small probability.
- **Common slips**: dividing by `n` in the loss but not in the gradient, indexing `P[:, y]`, and taking
  `np.log(softmax(Z))`. Every one of them fails a test above.
- **Follow-ups**: add a temperature `T` (softmax of `Z / T`) and re-derive the gradient (`(P - Y) / (nT)`). Add
  label smoothing, where `Y` puts `1 - a` on the label and `a / k` everywhere. Show the gradient is still
  `(P - Y)/n`. Then plug `ce_grad` into the final layer of [logistic-regression-numpy](logistic-regression-numpy.md)
  for the multiclass case.
- Theory: [Log-sum-exp](../../../computer-science/notes/04-numbers-and-memory.md#log-sum-exp) and
  [Entropy, cross-entropy, KL and perplexity](../../../../generative-ai/01-llm-fundamentals/notes/06-pretraining-data-and-objectives.md#entropy-cross-entropy-kl-and-perplexity).
  For checking a gradient you derived, see [gradient-check-numpy](gradient-check-numpy.md).
