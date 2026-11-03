---
title: "Cosine similarity in NumPy"
track: coding
topic: ml-coding
difficulty: easy
timebox_min: 15
concepts: [ml-coding]
source: https://github.com/alexeygrigorev/ai-engineering-gym
---
## Prompt

Implement cosine similarity in NumPy. Start with two 1-D vectors, then generalize
to computing the full pairwise similarity matrix between two batches of embeddings.

## Starter

Blank file in `programming/drills/coding/scratch/`. NumPy allowed unless the prompt says otherwise.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Cosine = dot product divided by the product of the two L2 norms. It's scale-invariant, which is why it's used for embeddings.

</details>

<details><summary>Hint 2</summary>

For the batch version, don't loop. Normalize each row of both matrices once, then a single A_norm @ B_norm.T produces every pairwise score.

</details>

<details><summary>Hint 3</summary>

Add a small epsilon to the norm so a zero vector doesn't divide by zero. If inputs are already unit vectors, it collapses to a plain matmul.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Cosine similarity is the dot product of two vectors divided by the product of their L2 norms: cos(a, b) = (a·b) / (||a|| ||b||). It measures the angle between vectors and ignores magnitude. That's exactly why it's the default metric for comparing embeddings (query vs. document, sentence vs. sentence). For the batched case, L2-normalize every row once, then a single matrix multiply A_norm @ B_norm.T gives the entire pairwise similarity matrix, with no Python loops. Guard against divide-by-zero for zero vectors (add a tiny epsilon to the norm). Note: if the embeddings are already unit-normalized (many models return normalized vectors), cosine similarity reduces to a plain dot product.

```python
# single pair
def cosine(a, b, eps=1e-8):
    return (a @ b) / (norm(a) * norm(b) + eps)

# batched: A is (m, d), B is (n, d) -> (m, n) similarity matrix
def cosine_matrix(A, B, eps=1e-8):
    A_norm = A / (np.linalg.norm(A, axis=1, keepdims=True) + eps)
    B_norm = B / (np.linalg.norm(B, axis=1, keepdims=True) + eps)
    return A_norm @ B_norm.T
```

**Complexity** — time O(d) for a single pair; O(m*n*d) for the (m,n) pairwise matrix; space O(1) extra for a pair; O(m*n) for the similarity matrix

</details>

## Notes

Follow-ups an interviewer may push on:

- Why is cosine preferred over Euclidean distance for high-dimensional embeddings?
- How does cosine similarity relate to the dot product when vectors are already L2-normalized?
- How would you find the top-k most similar rows efficiently instead of the full matrix?
- What changes if the batches are too large to fit the (m,n) matrix in memory?

Sources:

- [GeeksforGeeks — How to Calculate Cosine Similarity in Python](https://www.geeksforgeeks.org/python/how-to-calculate-cosine-similarity-in-python/)
- [Reddit — ML Engineer GenAI Amazon (phone screen: cosine similarity in NumPy)](https://www.reddit.com/r/datascience/comments/1jrdrpx/ml_engineer_genai_amazon/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-cosine-similarity-numpy.yaml`.
