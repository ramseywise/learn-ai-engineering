---
title: "Gradient check: MSE for linear regression"
track: coding
topic: ml-coding
difficulty: medium
timebox_min: 25
concepts: [ml-coding]
units: [data-science/01-classical-ml/notes/02-supervised-learning.md, generative-ai/09-llms-from-scratch/notes/01-micrograd.md]
source: original
---
## Prompt

Linear regression predicts `X @ w` for a feature matrix `X` of shape `(n, d)` and weights `w` of shape `(d,)`. Its
loss is the mean squared error of the residual `r = X @ w - y`.

1. On paper, derive the gradient of the loss with respect to `w`. Write it as one matrix expression and check its
   shape is `(d,)`.
2. In NumPy, write four functions:
   - `mse_loss(w, X, y)` returns a float.
   - `mse_grad(w, X, y)` returns your derived gradient, with no loops.
   - `numerical_grad(f, w, eps=1e-6)` returns the gradient of any scalar function `f` by central differences,
     `(f(w + eps e_j) - f(w - eps e_j)) / 2 eps` for each coordinate `j`.
   - `grad_check(f, grad_f, w)` returns the relative error `||a - b|| / (||a|| + ||b||)` between the analytic
     gradient `a` and the numerical one `b`. Guard against division by zero.

A correct gradient scores below about 1e-6. A wrong one scores above 1e-3.

## Starter

Blank file in `programming/drills/coding/scratch/`. NumPy only.

## Tests

Put your four functions above this block in a file and run it. Every assertion must pass.

```python
rng = np.random.default_rng(0)
n, d = 50, 4
X = rng.normal(size=(n, d))
y = X @ np.array([1.0, -2.0, 0.5, 3.0]) + 0.1 * rng.normal(size=n)
w = rng.normal(size=d)
f = lambda w: mse_loss(w, X, y)

# 1. the loss is the mean, not the sum
assert np.isclose(mse_loss(np.zeros(d), X, y), np.mean(y ** 2))
# 2. numerical_grad on a function you can differentiate in your head: f(v) = sum(v**2) -> 2v
v = np.array([1.0, -3.0, 0.5])
assert np.allclose(numerical_grad(lambda v: np.sum(v ** 2), v), 2 * v, atol=1e-6)
# 3. it returns one partial per weight, as floats, even for an integer w
assert numerical_grad(lambda v: np.sum(v ** 2), np.array([1, 2])).dtype.kind == "f"
# 4. the hand-derived gradient has shape (d,) and passes the check
assert mse_grad(w, X, y).shape == (d,)
assert grad_check(f, lambda w: mse_grad(w, X, y), w) < 1e-6
# 5. the check catches the three usual slips
slips = {
    "dropped the 2":  lambda w: (1 / n) * X.T @ (X @ w - y),
    "sum, not mean":  lambda w: 2 * X.T @ (X @ w - y),
    "sign flipped":   lambda w: (2 / n) * X.T @ (y - X @ w),
}
for name, bad in slips.items():
    assert grad_check(f, bad, w) > 1e-3, name
# 6. the check is scale-free: same verdict when the loss is 1e6 times bigger
big = lambda w: 1e6 * f(w)
assert grad_check(big, lambda w: 1e6 * mse_grad(w, X, y), w) < 1e-6
# 7. at the least-squares minimum both gradients are ~0: compare them absolutely
w_star = np.linalg.lstsq(X, y, rcond=None)[0]
assert np.abs(mse_grad(w_star, X, y) - numerical_grad(f, w_star)).max() < 1e-8
```

## Hints

One at a time. Open the next only after trying with the last.

<details><summary>Hint 1</summary>

Write the loss as `(1/n) * r.T @ r`. Differentiate `r.T @ r` with respect to `r` first (it is `2r`), then apply the
chain rule through `r = X @ w - y`, whose derivative with respect to `w` is `X`.

</details>

<details><summary>Hint 2</summary>

Check the shapes. `r` is `(n,)` and the answer must be `(d,)`, so `X` has to appear transposed: `(d, n) @ (n,)`.

</details>

<details><summary>Hint 3</summary>

In `numerical_grad`, build a fresh float vector `e` with `eps` in slot `j` for each `j`. Don't write into `w`
itself, and don't let an integer `w` give you an integer result array.

</details>

## Solution

<details><summary>Solution: derivation and code</summary>

$L(w) = \frac{1}{n}\lVert Xw - y\rVert^2$. Put $r = Xw - y$. Then $dL = \frac{2}{n} r^\top dr$, and
$dr = X\,dw$, so $dL = \frac{2}{n} r^\top X\,dw$. The gradient is the vector that multiplies $dw$, transposed:
$\nabla L = \frac{2}{n} X^\top (Xw - y)$, with shape $(d, n)(n,) = (d,)$.

```python
import numpy as np

def mse_loss(w, X, y):
    r = X @ w - y
    return np.mean(r ** 2)

def mse_grad(w, X, y):
    n = X.shape[0]
    return (2 / n) * X.T @ (X @ w - y)

def numerical_grad(f, w, eps=1e-6):
    g = np.zeros_like(w, dtype=float)
    for j in range(w.size):
        e = np.zeros_like(w, dtype=float)
        e[j] = eps
        g[j] = (f(w + e) - f(w - e)) / (2 * eps)
    return g

def grad_check(f, grad_f, w, eps=1e-6):
    a = grad_f(w)
    b = numerical_grad(f, w, eps)
    return np.linalg.norm(a - b) / max(np.linalg.norm(a) + np.linalg.norm(b), 1e-12)
```

The central difference has error of order `eps**2`. A forward difference, `(f(w + e) - f(w)) / eps`, has error of
order `eps` and fails test 7. Dividing by the norms makes the check scale-free (test 6): the absolute error grows
with the size of the loss, but a fixed absolute tolerance doesn't.

**Complexity**: `mse_grad` is O(nd). `numerical_grad` needs two loss evaluations per weight, so O(nd²) here.
That is why you use it to check a gradient and never to train.

</details>

## Notes

- **The minimum breaks the relative error.** At `w_star` both gradients are about 1e-12. The relative error is then
  noise divided by noise and comes out near 1.0 even though `mse_grad` is correct. Test 7 compares them absolutely for
  that reason. Run a gradient check at a random point, not at the solution.
- **Common slips the check catches**: dropping the 2 (relative error 0.33 on the test data), summing instead of
  averaging (0.96), a flipped residual sign (1.0). A missing transpose is caught earlier, as a shape error.
- **Follow-ups**: add an L2 penalty `lam * w @ w` and re-derive the gradient. Check the logistic-regression gradient
  in [logistic-regression-numpy](logistic-regression-numpy.md) the same way. Explain why the network version uses
  backpropagation rather than `numerical_grad` ([Why backward beats nudging](../../../../generative-ai/09-llms-from-scratch/notes/01-micrograd.md#why-backward-beats-nudging)).
- Theory: [Vectors, matrix products and the gradient](../../../../data-science/01-classical-ml/notes/02-supervised-learning.md#vectors-matrix-products-and-the-gradient)
  and [Derivatives, numerically](../../../../generative-ai/09-llms-from-scratch/notes/01-micrograd.md#derivatives-numerically).
