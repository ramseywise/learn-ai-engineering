---
title: "Debug an embeddings pipeline"
track: coding
topic: ml-coding
difficulty: medium
timebox_min: 25
concepts: [ml-coding]
source: https://github.com/alexeygrigorev/ai-engineering-gym
---
## Prompt

Debug this embeddings-handling snippet. It's supposed to embed a batch of query
strings, compare each against a matrix of stored document embeddings, and return
the best-matching document per query. It runs without crashing but returns wrong
matches. Find and fix the bugs.

```python
import numpy as np

def best_match(queries, doc_embeddings, model):
    results = []
    for q in queries:
        q_emb = model.embed(q)                 # returns shape (1, 768)
        # cosine similarity vs every document
        sims = doc_embeddings @ q_emb          # doc_embeddings is (N, 768)
        best = np.argmax(sims)
        results.append(best)
    return results
```

## Starter

Blank file in `programming/drills/coding/scratch/`. NumPy allowed unless the prompt says otherwise.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

Print the shapes: model.embed returns (1, 768), but the code uses it as if it were (768,). That alone makes the matmul produce the wrong thing.

</details>

<details><summary>Hint 2</summary>

A raw dot product isn't cosine similarity because it's biased by vector magnitude. You need to divide by the L2 norms (or normalize both sides first).

</details>

<details><summary>Hint 3</summary>

Query and documents must be normalized the same way. Normalize the doc matrix once, reshape and normalize the query, then one matmul gives a clean 1-D score array to argmax over.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

The snippet has three classic embedding bugs. (1) Shape mismatch: model.embed(q) returns (1, 768) but the code treats q_emb as a 1-D (768,) vector. doc_embeddings (N, 768) @ q_emb (1, 768) fails or, after an implicit reshape, produces the wrong shape. You must squeeze q_emb to (768,) (or transpose so it's (768, 1) and then flatten the result). Assert dimensions at the boundary rather than trusting them. (2) It's not cosine similarity, it's a raw dot product. Cosine requires dividing by the norms. A raw dot product is dominated by vector magnitude, so a long document vector wins regardless of direction. Either L2-normalize both sides first, or divide by the norm product. (3) Recomputing/normalizing inconsistently: if the stored doc_embeddings were normalized at index time but the query isn't (or vice versa), the scores are meaningless. Both sides must live in the same space. The robust fix normalizes both and does one matrix multiply, and returns argmax over a proper 1-D score vector.

```python
def best_match(queries, doc_embeddings, model, eps=1e-8):
    # normalize stored docs ONCE (must match how they were indexed)
    docs = doc_embeddings / (np.linalg.norm(doc_embeddings, axis=1,
                                            keepdims=True) + eps)
    results = []
    for q in queries:
        q_emb = model.embed(q).reshape(-1)          # (1,768) -> (768,)
        assert q_emb.shape[0] == docs.shape[1], "embedding dim mismatch"
        q_emb = q_emb / (np.linalg.norm(q_emb) + eps)
        sims = docs @ q_emb                          # (N,) cosine scores
        results.append(int(np.argmax(sims)))
    return results
```

**Complexity** — time `O(len(queries) * N * d)`; space `O(N*d)` for the (normalized) document matrix

</details>

## Notes

Follow-ups an interviewer may push on:

- How would asserting shapes at each boundary have caught the first bug immediately?
- Why does a raw dot product favor high-magnitude vectors, and when is that actually what you want?
- How would you batch all queries into one matrix multiply instead of a Python loop?
- What if the query embedding model differs from the one used to build the index?

Sources:

- [Zilliz — Why do I see a dimension mismatch when using Sentence Transformer embeddings?](https://zilliz.com/ai-faq/why-do-i-see-a-dimension-mismatch-or-shape-error-when-using-embeddings-from-a-sentence-transformer-in-another-tool-or-network)
- [PromptLayer — The Agentic System Design Interview](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-debug-embeddings.yaml`.
