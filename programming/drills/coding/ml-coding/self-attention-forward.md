---
title: "Self-attention forward pass"
track: coding
topic: ml-coding
difficulty: hard
timebox_min: 40
concepts: [ml-coding]
source: https://github.com/alexeygrigorev/ai-engineering-gym
---
## Prompt

Implement a single self-attention forward pass (scaled dot-product attention) in
NumPy. Given an input sequence and the Q/K/V projection weights, return the
attention output. Then note what changes for multi-head and for causal masking.

## Starter

Blank file in `programming/drills/coding/scratch/`. NumPy allowed unless the prompt says otherwise.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

The formula is softmax(Q K^T / sqrt(d_k)) V. First get Q, K, V by projecting the input with three weight matrices.

</details>

<details><summary>Hint 2</summary>

Q K^T gives an (L, L) score matrix: entry (i,j) is token i's affinity for token j. Divide by sqrt(d_k) before softmax so large dot products don't saturate it.

</details>

<details><summary>Hint 3</summary>

Softmax runs row-wise (each query's weights sum to 1), and you multiply the weights by V for the output. For causal masking, set the upper triangle of scores to -inf before softmax.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Scaled dot-product attention is Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V. Steps for a length-L sequence with model dim d: (1) project the input X (L, d) into queries, keys, and values via learned matrices. That gives Q = X W_q, K = X W_k, V = X W_v, each (L, d_k). (2) Compute raw scores Q K^T, an (L, L) matrix where entry (i, j) is how much token i attends to token j. (3) Scale by 1/sqrt(d_k), because without this the dot products grow with d_k, pushing softmax into a saturated, low-gradient regime. (4) Apply row-wise softmax to get attention weights that sum to 1 per query. (5) Multiply by V to produce the output (L, d_k), a weighted average of value vectors. Multi-head just runs this h times on d/h-sized slices in parallel and concatenates. Causal (decoder) masking adds -inf to the upper triangle of the scores before softmax so a token can't attend to future positions. Reuse a numerically stable softmax (subtract the row max).

```python
def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)

def self_attention(X, Wq, Wk, Wv, mask=None):
    Q = X @ Wq                       # (L, d_k)
    K = X @ Wk                       # (L, d_k)
    V = X @ Wv                       # (L, d_k)
    d_k = Q.shape[-1]
    scores = (Q @ K.T) / np.sqrt(d_k)          # (L, L)
    if mask is not None:                        # causal: upper triangle = -inf
        scores = np.where(mask, scores, -np.inf)
    weights = softmax(scores)                   # row-wise, sums to 1 per query
    return weights @ V                          # (L, d_k)
```

**Complexity** — time O(L^2 * d_k) — the L x L score matrix is the quadratic cost people cite for long contexts; space O(L^2) for the attention weight matrix

</details>

## Notes

Follow-ups an interviewer may push on:

- Why divide by sqrt(d_k) specifically, and what breaks without it?
- How does multi-head attention differ from just making d_k bigger?
- How does causal masking make this work for autoregressive generation?
- Why is attention O(L^2), and what do FlashAttention / linear-attention variants do about it?
- Where do the positional encodings enter, since attention is permutation-invariant?

Sources:

- [The Annotated Transformer (Harvard NLP)](https://nlp.seas.harvard.edu/2018/04/03/attention.html)
- [Build Self-Attention in Numpy](https://codewithdark.vercel.app/blog/SelfAttentionWithNumpy)
- [UvA Deep Learning — Transformers and Multi-Head Attention](https://uvadlc-notebooks.readthedocs.io/en/latest/tutorial_notebooks/tutorial6/Transformers_and_MHAttention.html)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-self-attention-forward.yaml`.
