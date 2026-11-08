---
origin: synthesis  # split from 03-keyword-semantic-and-hybrid-search.md (2026-11-08) so each part stays under the chapter length cap
sources:
  - https://arxiv.org/abs/2402.03216
  - Huyen, *AI Engineering* (O'Reilly, 2025), ch. 6
  - Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 5, ch. 6
  - https://arxiv.org/abs/2404.13781
  - https://doi.org/10.1145/3404835.3463238
confidence: high
cleaned: 2026-11-08
---
# 3b — Metadata filters, hybrid search and evaluating a retriever

Keyword search and semantic search each fail where the other is strong, and neither knows which document a customer is allowed to see. This half takes the two rankers from [03](03-keyword-semantic-and-hybrid-search.md) and adds the pieces that make a retriever usable: filters that cut the set, fusion that merges the rankings, and the metrics that say whether it works.

> Metadata filters cut the set without ranking, hybrid search fuses the keyword and semantic rankings with RRF, and precision, recall, MAP and MRR tell you which retriever is working. The BM25, embeddings and cosine they build on are in [03](03-keyword-semantic-and-hybrid-search.md).

---

## Metadata filtering

Filters are SQL-style constraints on fields (`region == "EU"`, `tier >= "pro"`, `date > 2024-01-01`). They pass or fail a document and rank nothing. Use them for access control, subscription tiers and freshness. Never as a substitute for search.

Here the filter settles something search cannot. The current refund page and its archive are near-duplicates and both match, so ranking alone can surface the wrong one. A date filter removes the archive before scoring, and the audience filter removes the internal runbook:

```python
from ragkit import DOCS, Retriever

def search(query, **filters):
    allowed = [d for d in DOCS
               if d.audience == filters.get("audience", d.audience)
               and d.updated >= filters.get("updated_after", "")]
    return Retriever(allowed).sparse(query, k=3)

query = "refund policy for annual plans"
print("no filter:      ", search(query))
print("public, current:", search(query, audience="public", updated_after="2025-01-01"))
```

```text
no filter:       ['kb-04', 'kb-05', 'kb-18']
public, current: ['kb-04', 'kb-07', 'kb-06']
```

---

## Hybrid search and reciprocal rank fusion

The hybrid pipeline:

1. Keyword search returns its top 20–50.
2. Semantic search returns its top 20–50.
3. Metadata filters remove ineligible docs from both lists.
4. **RRF** fuses the two rankings into one.

RRF ignores raw scores (which are on different scales) and uses only ranks:

```
RRF(d) = Σ over lists  1 / (k + rank(d))
```

| k | 1st vs 10th place | Behaviour |
|---|---|---|
| 0 | 1/1 vs 1/10 = 10× | Top ranks dominate |
| 50 | 1/51 vs 1/60 ≈ 1.2× | Ranks matter less; agreement across lists matters more |
| 60 | common default | — |

A **beta** weight can tilt the fusion, e.g. 0.7 semantic / 0.3 keyword.

Why fuse at all: the two retrievers find different documents. In ANCE's TREC DL 2019 analysis (MS MARCO corpus), at most 25% of the dense retriever's top 100 were also in BM25's (Xiong et al., ICLR 2021). DPR's hybrid ran before RRF was common. It reranked the union of each retriever's top 2,000 by BM25 + 1.1 × dense score. That helped where the words matter, with DPR trained on each dataset separately, adding 5.4 top-20 points on TREC and 8.3 on SQuAD, and cost 1.8 points on Natural Questions, where dense alone was stronger (Karpukhin et al., EMNLP 2020).

**Check which way alpha points.** Raieli and Iuculano define hybrid weight α so that α = 0 is pure vector search and α = 1 is pure keyword, with typical values of 0.4–0.5 (some recommend 0.3) (*Building AI Agents*, ch. 6). Weaviate's `hybrid(alpha=…)`, used in note [04](04-vector-databases-and-ann.md#4-query), runs the other way: α = 1 is pure vector. The same "0.3" means mostly keyword in one convention and mostly vector in the other. Read the library's definition before copying a number.

```python
from ragkit import Retriever

def reciprocal_rank_fusion(list1, list2, top_k=5, K=60):
    rrf_scores = {}
    for lst in [list1, list2]:
        for rank, item in enumerate(lst, start=1):   # ranks start at 1
            rrf_scores.setdefault(item, 0)
            rrf_scores[item] += 1 / (rank + K)       # agreement across lists adds up
    sorted_items = sorted(rrf_scores, key=rrf_scores.get, reverse=True)
    return sorted_items[:top_k]                      # the course casts ids to int here

retriever = Retriever()
query = "Scale plan limit"
sparse, dense = retriever.sparse(query, 10), retriever.dense(query, 10)
print("bm25 ", sparse[:5])
print("dense", dense[:5])
for K in [0, 60]:
    print(f"rrf K={K:<2}", reciprocal_rank_fusion(sparse, dense, K=K))
```

```text
bm25  ['kb-03', 'kb-16', 'kb-07', 'kb-06']
dense ['kb-03', 'kb-07', 'kb-06', 'kb-04', 'kb-05']
rrf K=0  ['kb-03', 'kb-07', 'kb-16', 'kb-06', 'kb-04']
rrf K=60 ['kb-03', 'kb-07', 'kb-06', 'kb-16', 'kb-04']
```

Pages found by both lists rise to the top. K matters at the margin: K=0 lets `kb-16`, ranked second by BM25, climb above `kb-06`, which sits higher in the dense list and lower in the BM25 one. The assignment's output shows fusion at work on its news corpus:

| Retriever | Top 5 indices |
|---|---|
| Semantic | 743, 673, 626, 752, 326 |
| BM25 | 752, 673, 289, 626, 43 |
| **RRF** | **673, 752, 626, 743, 289** |

The three in both lists lead; each retriever's unique pick (743, 289) survives lower down.

---

Pyserini shows the case where fusion pays. On MS MARCO passage dev, with every system built on the same toolkit, BM25 scored 0.184 MRR@10, and tuning k1 and b moved it only to 0.187. Document expansion with doc2query-T5 kept retrieval bag-of-words and reached 0.272 at default settings, 0.282 tuned. A dense TCT-ColBERT retriever reached 0.335. A weighted interpolation of dense and BM25 scores reached 0.353, and 0.365 with expansion. HNSW lost almost nothing against an exact scan (recall@1000 0.962 vs 0.964). The dense index was 25 GB against 2.6 GB for the sparse one (which includes the text) ([SIGIR 2021](https://doi.org/10.1145/3404835.3463238), Lin et al.). The paper reports no latency or interpolation weight, and tests on MS MARCO only. Pyserini ships pre-built indexes for about three dozen test collections, so a BM25 baseline like the one above is one command.

---

M3-Embedding puts the three scorers in one model. An XLM-RoBERTa-large extended to 8,192 tokens gives a dense vector, per-token sparse weights and ColBERT-style multi-vectors, and the final score is a weighted sum, with the dense top-200 reranked by all three. On MIRACL dev (18 languages, nDCG@10) dense scored 69.2, sparse 53.9, multi-vector 70.5 and all three 71.5, against 31.9 for BM25 and 66.6 for mE5-large, so fusion added 2.3 over dense alone. On MLDR long documents (13 languages) sparse beat dense, 62.2 against 52.5, and all three reached 65.0. The weights were set by hand per benchmark (1/0.3/1 on MIRACL, 0.15/0.5/0.35 on MLDR), the fusion is a score sum from one model and not rank fusion of independent systems, and the main tables use BM25 on the XLM-R tokenizer. With a Lucene analyzer BM25 reached 64.1 on MLDR, above M3's sparse head (62.2) and just under all three (65.0), though on MIRACL the sparse head led (53.9 against 38.5). Training the sparse head without self-knowledge distillation dropped its MIRACL score from 53.9 to 36.7. Single runs, with no seeds or significance tests ([arXiv:2402.03216](https://arxiv.org/abs/2402.03216), Chen et al., Findings of ACL 2024).

## Evaluating a retriever

You need a labelled set: for each query, which documents are relevant.

| Metric | Formula | Question it answers |
|---|---|---|
| **Precision** | relevant retrieved / retrieved | How much of what I returned is useful? |
| **Recall** | relevant retrieved / total relevant | How much of what exists did I find? |
| P@k, R@k | Same, on the top k only | Comparable across systems |
| **MAP** | Mean over queries of average precision at each relevant hit | Are relevant docs ranked high? |
| **MRR** | Mean of 1 / rank of first relevant doc | How soon is the first good one? |

### Worked numbers from the course

| Case | Numbers |
|---|---|
| Return 12, 8 relevant; 10 relevant exist | P = 8/12 = 66%, R = 8/10 = 80% |
| Return 15, 9 relevant | P = 9/15 = 60%, R = 9/10 = 90% — recall up, precision down |
| P@5 = 2/5, P@10 = 6/10, 8 relevant exist | R@10 = 6/8 |
| Relevant at ranks 1, 4, 5 (of 3 relevant) | AP = (1/1 + 2/4 + 3/5) / 3 = (1 + 0.5 + 0.6) / 3 = 0.7 |
| First relevant at ranks 1, 3, 6, 2 over 4 queries | MRR = (1 + 0.33 + 0.17 + 0.5) / 4 = 0.5 |
| Relevance list [1, 0, 1, 0, 1] (*Building AI Agents*, ch. 5) | AP = (1/1 + 2/3 + 3/5) / 3 = (1 + 0.67 + 0.6) / 3 ≈ 0.76 |

Two naming notes from Huyen (*AI Engineering*, ch. 6). *Context precision* is sometimes called *context relevance*. *Context recall* needs every relevant document in the corpus labelled for each query, so it is expensive to measure.

These metrics are short enough to write out and check against the table above. Average precision for relevance at ranks 1, 4 and 5 should come to 0.7, and the four-query MRR to 0.5:

```python
from ragkit import Retriever, evaluate, QUERIES

def average_precision(flags):                 # flags: relevance by rank, e.g. [1, 0, 0, 1, 1]
    hits, total = 0, 0.0
    for rank, flag in enumerate(flags, start=1):
        if flag:
            hits += 1
            total += hits / rank
    return total / hits

print("AP, relevant at 1, 4, 5:", round(average_precision([1, 0, 0, 1, 1]), 2))
print("AP, [1, 0, 1, 0, 1]:    ", round(average_precision([1, 0, 1, 0, 1]), 2))
print("MRR, first hits 1,3,6,2:", round(sum(1 / r for r in [1, 3, 6, 2]) / 4, 2))

r = Retriever()
for name, search in [("bm25", r.sparse), ("dense", r.dense), ("hybrid", r.hybrid)]:
    print(f"{name:7}", {m: round(v, 3) for m, v in evaluate(search).items()})
```

```text
AP, relevant at 1, 4, 5: 0.7
AP, [1, 0, 1, 0, 1]:     0.76
MRR, first hits 1,3,6,2: 0.5
bm25    {'recall@3': 0.6, 'mrr': 0.562, 'ndcg@3': 0.563}
dense   {'recall@3': 0.9, 'mrr': 0.877, 'ndcg@3': 0.875}
hybrid  {'recall@3': 0.95, 'mrr': 0.742, 'ndcg@3': 0.789}
```

**Recall@k is the most cited** for RAG: the LLM can ignore a bad document, but it can't use one you never retrieved. Note [01 § measure each stage](01-rag-pipeline.md#measure-each-stage) puts these in the pipeline context.

**Relevance to a person is not usefulness to the model.** Salemi and Zamani test how well retrieval metrics predict a RAG system's final score ([arXiv:2404.13781](https://arxiv.org/abs/2404.13781), SIGIR 2024). With T5-small using Fusion-in-Decoder over 50 BM25 documents on Natural Questions, MRR against the KILT benchmark's human provenance labels correlates with downstream exact match at only Kendall's tau 0.177. LLM-judged relevance (Mistral 7B) does worse, at 0.060. Their method, eRAG, runs the system's own LLM on each retrieved document alone, scores each output against the task's ground truth, and feeds those scores to the same metric as relevance labels. Its MRR reaches tau 0.503 on the same setup, and across datasets the gain over the best baseline is 0.168 to 0.494. It also used far less GPU memory than end-to-end evaluation in their runs (1.5 GB per document against 75 GB on NQ). Two limits: this was a small model and the correlations fell as more documents were retrieved, since the metric judges each document alone while the LLM reads them together. Keep Recall@k for debugging, and check it still predicts your final answer quality before you optimise it for long.

---

## Rules of thumb

| Rule | Why |
|---|---|
| Default to hybrid (BM25 + dense + RRF) | Each covers the other's blind spot; cost is small |
| Retrieve 20–50 per retriever before fusion | RRF needs depth to find agreement |
| Filters for constraints, search for relevance | Mixing them up hides docs or leaks them |

---

## Pitfalls

- **A hybrid weight copied from elsewhere.** Symptom: a "0.3" setting behaves like the opposite of what the post promised. Alpha conventions differ. Read the library's definition.
- **Filtering after fusion.** Symptom: fewer than k results for filtered users, or forbidden documents in a trace. Apply filters to both lists, ideally inside the query.

---

## Try it

1. Compute by hand: a query's relevant pages sit at ranks 2 and 5 with two relevant pages in total. What are recall@3, MRR and AP?

<details>
<summary>Answers</summary>

1. Recall@3 = 1/2, because only the rank 2 page is in the top 3. MRR = 1/2. AP = (1/2 + 2/5) / 2 = 0.45.

</details>

---

## Interview checklist

| Question | Answer |
|---|---|
| Why fuse ranks and not scores? | BM25 and cosine live on different scales. RRF needs no calibration, at the cost of discarding score magnitude. |
| What does the k in RRF do? | It flattens the reward for top ranks. At k=0 first place is worth ten times tenth place; at k=60 about 1.2 times, so agreement across lists matters more. |
| Which retrieval metric first, and why? | Recall@k. A document that was not retrieved can't be used, so low recall caps the system. |
| MRR, MAP or nDCG? | MRR when one good document is enough. MAP when you want all relevant documents ranked high with binary labels. nDCG with graded labels. |
| Do human relevance labels predict RAG quality? | Weakly in Salemi and Zamani's tests: tau around 0.18 for provenance MRR on NQ, against 0.50 for eRAG, which scores each document by what the system's LLM does with it. |
| Why do filters not replace search? | A filter is a hard yes or no with no ranking. It enforces constraints but does not order what remains by relevance. |

---

## Next

[04 — Vector databases and ANN](04-vector-databases-and-ann.md): semantic search with a linear scan doesn't scale, and ANN indexes make it fast.
