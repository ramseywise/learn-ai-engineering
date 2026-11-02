# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "fastembed==0.7.*", "onnxruntime<1.24"]
# ///
"""One-variable-at-a-time ablation on the Tallybook kit: which embedding model, dense or hybrid.

    cd generative-ai/02-rag-retrieval/practice && uv run ablation.py

onnxruntime is capped because later versions refuse the symlinked e5 weights in fastembed's cache.
Local models only, no API key. The first run downloads about 2.5 GB of ONNX weights, almost all of
it multilingual-e5-large. Note 11 quotes the output. It answers a question about Tallybook's 18
pages and 20 queries, not about any production corpus.
"""
# %%
import time

import numpy as np
from fastembed import TextEmbedding
from ragkit import DOCS, QUERIES, Retriever, recall_at_k, reciprocal_rank, rrf, top_k

ROUNDS, SEED = 10_000, 0
ids = [d.id for d in DOCS]
toy = Retriever()

# name -> (fastembed id, query prefix, passage prefix). The e5 models are trained with these prefixes.
MODELS = {
    "minilm-l6": ("sentence-transformers/all-MiniLM-L6-v2", "", ""),
    "bge-small": ("BAAI/bge-small-en-v1.5", "", ""),
    "bge-base": ("BAAI/bge-base-en-v1.5", "", ""),
    "e5-large": ("intfloat/multilingual-e5-large", "query: ", "passage: "),
}


# %% Each configuration is a search function: query, k -> ranked ids.
def dense_search(name):
    model_id, query_prefix, passage_prefix = MODELS[name]
    model = TextEmbedding(model_id)
    vectors = np.array(list(model.embed([passage_prefix + d.full for d in DOCS])))
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)

    def search(query, k=5):
        vector = np.array(list(model.embed([query_prefix + query])))[0]
        return top_k(vectors @ (vector / np.linalg.norm(vector)), ids, k)

    return search


def hybrid_of(dense, pool=10):
    def search(query, k=5):
        return rrf([toy.sparse(query, pool), dense(query, pool)])[:k]

    return search


configs = {"bm25": toy.sparse, "toy dense": toy.dense}
for name in MODELS:
    configs[name] = dense_search(name)
for name in ["toy dense", *MODELS]:
    configs[f"{name} + bm25"] = hybrid_of(configs[name])


# %% Score every configuration on the same 20 queries, keeping the per-query values.
def score(search):
    rr, r3, p1, seconds = [], [], [], []
    for query, relevant, _ in QUERIES:
        start = time.perf_counter()
        ranked = search(query, k=10)
        seconds.append(time.perf_counter() - start)
        rr.append(reciprocal_rank(ranked, relevant))
        r3.append(recall_at_k(ranked, relevant, 3))
        p1.append(float(ranked[:1] == sorted(relevant)))
    return np.array(rr), np.mean(r3), np.mean(p1), 1000 * np.median(seconds)


scores = {name: score(search) for name, search in configs.items()}
print(f"{'config':18s} {'MRR':>6s} {'P@1':>6s} {'R@3':>6s} {'ms/query':>9s}")
for name, (rr, r3, p1, ms) in scores.items():
    print(f"{name:18s} {rr.mean():6.3f} {p1:6.3f} {r3:6.3f} {ms:9.1f}")


# %% Paired bootstrap on the per-query reciprocal rank, as in note 11.
def paired(a, b):
    diff = scores[a][0] - scores[b][0]
    rng = np.random.default_rng(SEED)
    means = diff[rng.integers(0, len(diff), (ROUNDS, len(diff)))].mean(axis=1)
    low, high = np.percentile(means, [2.5, 97.5])
    wins, losses = (diff > 0).sum(), (diff < 0).sum()
    print(f"{a + ' - ' + b:30s} {diff.mean():+.3f}  95% interval [{low:+.3f}, {high:+.3f}]  "
          f"wins {wins}, losses {losses}, ties {len(diff) - wins - losses}")


print()
for a, b in [("e5-large", "bm25"), ("bge-small", "bm25"),
             ("bge-base", "bge-small"), ("e5-large", "bge-small"), ("minilm-l6", "bge-small"),
             ("bge-small + bm25", "bge-small"), ("e5-large + bm25", "e5-large"),
             ("toy dense", "bge-small")]:
    paired(a, b)
