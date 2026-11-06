---
title: "Low-rank approximation with the SVD"
track: coding
topic: ml-coding
difficulty: medium
timebox_min: 20
concepts: [ml-coding]
units: [generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block.md, data-science/01-classical-ml/notes/05-unsupervised-learning.md]
source: original
---
## Prompt

The singular value decomposition writes any `(m, n)` matrix as `A = U @ diag(s) @ Vt`. The singular values `s` are
non-negative and sorted largest first. Keeping only the first `k` of them gives the best rank-`k` approximation to
`A`. This is the idea behind PCA and LoRA.

Write three functions with NumPy (`np.linalg.svd` is allowed):

1. `rank_k(A, k)` returns the rank-`k` reconstruction of `A`, with the same shape as `A`.
2. `k_for_energy(A, frac)` returns the smallest `k` whose first `k` squared singular values make up at least
   `frac` of the total sum of squares.
3. `stored_numbers(m, n, k)` returns how many numbers you store to keep `U_k`, `s_k` and `V_k`.

## Starter

Blank file in `programming/drills/coding/scratch/`. NumPy only.

## Tests

Put your three functions above this block in a file and run it. Every assertion must pass.

```python
rng = np.random.default_rng(0)
m, n = 60, 40

# 1. a matrix of rank 3 comes back exactly from 3 components
L = rng.normal(size=(m, 3)) @ rng.normal(size=(3, n))
assert np.allclose(rank_k(L, 3), L)
# 2. shape is kept, and the result really has rank k
A = rng.normal(size=(m, n))
Ak = rank_k(A, 5)
assert Ak.shape == (m, n)
assert np.linalg.matrix_rank(Ak) == 5
# 3. the error is the discarded singular values: ||A - A_k||_F^2 = sum_{i>k} s_i^2
S = np.linalg.svd(A, compute_uv=False)
for k in (1, 5, 20):
    assert np.isclose(np.linalg.norm(A - rank_k(A, k)) ** 2, np.sum(S[k:] ** 2))
# 4. no other rank-5 matrix does better (try a random rank-5 one)
R = rng.normal(size=(m, 5)) @ rng.normal(size=(5, n))
assert np.linalg.norm(A - Ak) < np.linalg.norm(A - R)
# 5. full rank gives A back; it also works on a wide matrix
assert np.allclose(rank_k(A, min(m, n)), A)
assert np.allclose(rank_k(A.T, 5), Ak.T)
# 6. energy: singular values 3, 2, 1 have energies 9, 4, 1 out of 14
D = np.diag([3.0, 2.0, 1.0])
assert k_for_energy(D, 0.5) == 1     # 9/14 = 0.64
assert k_for_energy(D, 0.9) == 2     # 13/14 = 0.93
assert k_for_energy(D, 0.95) == 3
assert k_for_energy(D, 9 / 14) == 1  # exactly reaching the target counts
# 7. storage for U_k, s_k and V_k against the full matrix
assert stored_numbers(1000, 1000, 4) == 8004
assert stored_numbers(m, n, 5) < m * n
```

## Hints

One at a time. Open the next only after trying with the last.

<details><summary>Hint 1</summary>

Call `np.linalg.svd(A, full_matrices=False)`. With `p = min(m, n)`, the shapes are `U` `(m, p)`, `s` `(p,)` and
`Vt` `(p, n)`. The rows of `Vt` are the right singular vectors.

</details>

<details><summary>Hint 2</summary>

Keep the first `k` columns of `U` and the first `k` rows of `Vt`. `U[:, :k] * s[:k]` scales each column by its
singular value through broadcasting, so you never build `diag(s)`.

</details>

<details><summary>Hint 3</summary>

Take the cumulative sum of `s**2`, divide it by the total, and find the first position that reaches `frac`.
`np.searchsorted` returns a 0-based index. `k` is a count.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

```python
import numpy as np

def rank_k(A, k):
    U, S, Vt = np.linalg.svd(A, full_matrices=False)
    return (U[:, :k] * S[:k]) @ Vt[:k, :]

def k_for_energy(A, frac):
    S = np.linalg.svd(A, compute_uv=False)
    energy = np.cumsum(S ** 2) / np.sum(S ** 2)
    return int(np.searchsorted(energy, frac) + 1)

def stored_numbers(m, n, k):
    return k * (m + n + 1)
```

Test 3 is the reason this works. The squared Frobenius error of the rank-`k` reconstruction equals the sum of the
squared singular values you dropped. So `s**2` measures how much of the matrix each component carries, and
`k_for_energy` uses squares, not `s` itself. The Eckart–Young theorem says no rank-`k` matrix has a smaller
error. Test 4 checks that against one random competitor.

**Complexity**: the SVD of an `(m, n)` matrix costs O(mn·min(m, n)). The reconstruction costs O(mnk) on top of it.

</details>

## Notes

- **Storage.** `k(m + n + 1)` numbers against `mn`. Fold `s` into `U` and you have two factors,
  `(m, k)` and `(k, n)`, so `k(m + n)`. That is the count in [Matrix products, transpose and rank](../../../../generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block.md#matrix-products-transpose-and-rank)
  (8,000 against 1,000,000 for a rank-4 1,000 × 1,000 matrix).
- **Common slips**: forgetting to scale by `s`, slicing `Vt[:, :k]` (columns) instead of `Vt[:k, :]` (rows), measuring
  energy with `s` instead of `s**2`, and an off-by-one when the energy exactly reaches `frac`.
- **Follow-ups**: center the columns of `A` first and show that the rows of `Vt[:k]` are the top `k` principal
  components ([PCA](../../../../data-science/01-classical-ml/notes/05-unsupervised-learning.md#principal-component-analysis)).
  Then explain why LoRA trains the two thin factors directly instead of taking an SVD of the weight update
  ([PEFT in practice](../../../../generative-ai/01-llm-fundamentals/notes/09-peft-and-fine-tuning-in-practice.md)).
