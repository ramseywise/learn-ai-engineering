# Lab 1 — BM25 from scratch

> Adapted from Bojie Li, *AI Agents in Depth*, Experiment 3-5 ([upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/sparse-embedding), Apache-2.0). This lab keeps only the standard-library engine, the quickstart and the tests. The upstream FastAPI server, the HTTP demo and the CLI's Chinese corpus are left out. Concepts: [note 04 — Hybrid retrieval](../../notes/04-retrieval.md#hybrid-retrieval).

Sparse retrieval is still the half of a hybrid pipeline that finds exact names, error codes and identifiers. This lab builds it from first principles, with logging at every step, so you can trace a score by hand:

| Piece | Class | What it does |
|---|---|---|
| Text processing | `TextProcessor` | Lowercases text, tokenizes it and drops English stop words |
| Inverted index | `InvertedIndex` | Maps each term to the documents that contain it, plus term and length statistics |
| Ranking | `BM25` | IDF × saturated term frequency, normalized by document length (`k1=1.5`, `b=0.75`) |
| Facade | `SparseSearchEngine` | `index_document`, `index_batch`, `search`, `get_index_info` |

No dependencies, no API key, no network.

## Run

```bash
python quickstart.py     # indexes 10 sample docs, runs example queries, then an interactive prompt ('quit' to exit)
python test_engine.py    # tokenizer, index, IDF, scoring and ranking tests
```

## The formula

For query term *t* in document *d*:

```
score(t, d) = IDF(t) · tf · (k1 + 1) / (tf + k1 · (1 − b + b · |d| / avgdl))
IDF(t)      = ln((N − df + 0.5) / (df + 0.5) + 1)
```

- **`k1` saturates term frequency.** The 20th mention of "distillation" adds far less than the 2nd, so long documents can't win by repetition.
- **`b` normalizes for length.** `b=0` ignores length. `b=1` normalizes fully.
- **The `+ 1` inside the log** is the Lucene variant. It keeps IDF positive even for terms that appear in more than half the documents. The book's worked example uses the classic form without it, so its numbers are slightly lower than this engine's.

## Exercises

1. **Hand-check one score.** Turn on `DEBUG` logging in `quickstart.py`. Pick a query term and use the logged `tf`, `|d|`, `avgdl`, `N` and `df` to reproduce its contribution to the score.
2. **Rare beats frequent.** Index three documents where "model" appears often and "distillation" only once. Query "model distillation" and confirm the rarer term contributes more per occurrence.
3. **Sweep `k1` and `b`.** `index_document` rebuilds BM25 with the defaults, so set `engine.bm25 = BM25(engine.index, k1=..., b=...)` after indexing. Try `k1 ∈ {0.5, 1.2, 2.0}` and `b ∈ {0, 0.75, 1}` on a corpus with one very long document. Watch how its rank changes.
4. **Find the blind spot.** Query "kitty" against a document that only says "cat", and "HTTP-403" against one that says "forbidden error". Sparse retrieval misses both. That is the gap dense retrieval and reranking fill ([note 04](../../notes/04-retrieval.md#hybrid-retrieval)).
5. **Contextual prefix.** Index a chunk such as "Revenue grew 3% in the second quarter." with and without a prefix like "ACME Corp 2025 Q2 financial report:". Then query "ACME revenue". The prefix adds matchable keywords, which is the sparse half of [contextual retrieval](../../notes/04-retrieval.md#contextual-retrieval).

Hybrid retrieval and reranking on top of this engine: upstream [3-6 retrieval-pipeline](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/retrieval-pipeline) (needs local embedding and reranker models).
