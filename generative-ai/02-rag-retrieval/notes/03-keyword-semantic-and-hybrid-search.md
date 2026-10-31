---
origin: Deeplearning.ai-RAG-main
sources:
  - "James Phoenix & Mike Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 5"
  - https://www.deeplearning.ai/courses/retrieval-augmented-generation-rag/
  - https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG (Module 2, "Information Retrieval and Search Foundations" + Assignment 2)
  - Huyen, *AI Engineering* (O'Reilly, 2025), ch. 6
  - Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 5, ch. 6
  - Iusztin & Labonne, *LLM Engineer's Handbook* (Packt, 2024), ch. 4
confidence: high
cleaned: 2026-10-31
---
# 3 — Keyword, semantic and hybrid search

> A retriever ranks documents. Keyword search (TF-IDF, BM25) ranks by shared words, semantic search ranks by embedding distance, metadata filters cut the set without ranking, and hybrid search fuses the rankings with RRF. Precision, recall, MAP and MRR tell you which one is working.

---

## The retriever's three tools

| Technique | Matches on | Good at | Bad at |
|---|---|---|---|
| **Keyword search** | Exact terms | Product codes, names, jargon, rare words | Synonyms, paraphrase |
| **Semantic search** | Meaning (embedding similarity) | Paraphrase, "something like X" | Exact identifiers, negation |
| **Metadata filtering** | Structured fields | Hard constraints: region, tier, date | Anything fuzzy — it is not search |

Production retrievers run all three. The house version of this argument, with the BM25 maths written out, is note [01 § BM25 from scratch](01-rag-pipeline.md#bm25-from-scratch) and [01 § hybrid retrieval](01-rag-pipeline.md#hybrid-retrieval). The theory lives in [ai-engineering 02 — retrieval](../../../ai-engineering/02-context-engineering/notes/04-retrieval.md). This note keeps the course's numbers and lab code.

---

## Keyword search

### Bag of words to TF-IDF

Each document becomes a **sparse vector**: one slot per vocabulary word, mostly zeros. The prompt becomes one too, and documents are scored by overlap.

| Score | Formula | Fixes |
|---|---|---|
| Term frequency (TF) | count of word in doc | — |
| Normalised TF | count / doc length | Long docs winning by size |
| **TF-IDF** | TF × log(N / df) | Common words ("the", "pizza" in a pizza corpus) dominating |

N is the number of documents; df is how many contain the word. A word in every document gets log(1) = 0.

### BM25

BM25 is TF-IDF with two tunable fixes, and it is still the default keyword scorer.

| Parameter | Typical | Effect |
|---|---|---|
| **k1** term saturation | 1.2–2.0 | Diminishing returns on repeats. A doc saying "pizza" 20 times scores about 1.3× one saying it 10 times, not 2× |
| **b** length normalisation | 0–1 (0.75 common) | How much to penalise long docs. b = 0 ignores length |

Raieli and Iuculano give the same defaults: b = 0.75 and k between 1.2 and 2 (*Building AI Agents*, ch. 5). Their edge case makes saturation clear: at k = 0 the term-frequency factor collapses to 1, so BM25 scores only whether each query term is present.

Why keyword search survives: it is cheap, interpretable, needs no model, and nails exact matches that embeddings blur. Huyen's example is an error code. A user searching for `EADDRNOTAVAIL (99)` wants documents containing exactly that string, and an embedding retriever may return generic networking pages instead. She also quotes Perplexity's CEO saying BM25 remains a hard baseline to beat (*AI Engineering*, ch. 6).

Notes from the same chapter:

- **The inverted index** maps each term to the documents containing it. Lookup cost depends on how many documents contain the query terms, not on corpus size.
- **Variants.** BM25+ fixes long documents being scored below short ones that don't contain the term at all. BM25F scores fields (title, body) with separate weights.
- **n-grams.** Tokenising "hot dog" as two words matches pages about hot weather and dogs. Indexing bigrams keeps the phrase.
- **Framing.** Huyen splits retrievers into *term-based* and *embedding-based* rather than sparse and dense, because learned sparse models such as SPLADE are sparse but embedding-based.

```python
import bm25s

# Index once: tokenise the corpus, build the inverted index
BM25_RETRIEVER = bm25s.BM25(corpus=corpus)
BM25_RETRIEVER.index(bm25s.tokenize(corpus))

def bm25_retrieve(query: str, top_k: int = 5) -> list[int]:
    # Tokenise the query the same way as the corpus
    results, scores = BM25_RETRIEVER.retrieve(bm25s.tokenize(query), k=top_k)
    # bm25s returns the documents themselves (batch of 1); map back to indices
    return [corpus.index(doc) for doc in results[0]]
```

---

## Semantic search

An **embedding model** maps text to a dense vector so that similar meanings land close together. It learns this by **contrastive training**: pull positive pairs (question, its answer) together and push negative pairs apart, over millions of examples.

### Distance measures

| Measure | Uses | Note |
|---|---|---|
| **Cosine similarity** | Angle only | The default for text. Length-invariant |
| Euclidean distance | Straight-line distance | Sensitive to vector length |
| Dot product | Angle × length | Equals cosine when vectors are normalised |

![Two vectors [10,10] and [100,100] on the same direction: cosine similarity 1 despite very different lengths, angle θ between direction lines](../sources/images/hasan-dlai-rag-cosine.png)
*Image Source: Hasan, DeepLearning.AI RAG course, Module 2*

A correction to one book: the *LLM Engineer's Handbook* (ch. 4) says cosine distance ranges from −1 to 1. That is the range of cosine *similarity*. Cosine distance, 1 − similarity, ranges from 0 to 2. *Prompt Engineering for GenAI* (ch. 5) makes the same slip, calling cosine similarity "a measure of distance": higher similarity means *closer*. Check which one a library returns before setting a threshold. A FAISS `IndexFlatL2`, for instance, returns squared L2 distances ([04](04-vector-databases-and-ann.md)).

Rule: **only compare vectors from the same model**. Two models' spaces are unrelated, even at the same dimension.

```python
from sentence_transformers import SentenceTransformer
import joblib, numpy as np

model = SentenceTransformer("BAAI/bge-base-en-v1.5")
EMBEDDINGS = joblib.load("embeddings.joblib")  # the course ships the corpus pre-embedded

def cosine_similarity(v1, array_of_vectors):
    # The course writes its own: dot product over the product of norms
    v1 = np.asarray(v1); arr = np.atleast_2d(array_of_vectors)
    return arr @ v1 / (np.linalg.norm(arr, axis=1) * np.linalg.norm(v1))

def semantic_search_retrieve(query: str, top_k: int = 5) -> list[int]:
    query_embedding = model.encode(query)                  # same model as the corpus
    similarity_scores = cosine_similarity(query_embedding, EMBEDDINGS)
    return np.argsort(-similarity_scores)[:top_k].tolist() # highest similarity first
```

A trap the assignment surfaces: **bge-base-en-v1.5 truncates at 512 tokens**. Embedding a full article and embedding its first 3000 characters give the same vector, because everything past the limit is dropped. This is the first argument for chunking (note [05](05-chunking-query-parsing-and-reranking.md)).

### How embedders are trained, and where cosine misleads

Raieli and Iuculano cover the training side (*Building AI Agents*, ch. 5):

- **Two ways to score.** A *cross-encoder* reads `[CLS] query [SEP] document` and scores the pair. It is accurate, but the query and document together must fit BERT's 512 tokens, and every pair is a forward pass. A *bi-encoder* embeds each side once, so document vectors can be precomputed.
- **Training data and losses.** Bi-encoders are trained on labelled pairs; MultiNLI (433K sentence pairs) is the classic source. A cosine-similarity loss regresses on graded labels. *Multiple negatives ranking loss* (InfoNCE) uses only positive pairs and treats the other answers in the batch as negatives. Random negatives are too easy. *Hard negatives*, passages that look relevant but aren't, teach the boundary.
- **Rogue dimensions.** In many transformer embeddings one to five dimensions have very large magnitude and dominate cosine similarity, so two texts look similar because of a few dimensions that track little meaning. Standardising each dimension (z-score over the corpus) before comparing reduces the effect.

![Four panels (XLNet, GPT-2, RoBERTa, BERT, layer 12) showing each dimension's share of cosine similarity: in each model one or a few dimensions take most of the cosine similarity, while model behaviour is spread across many dimensions](../sources/images/building-ai-agents-llms-rag-kgs-fig5-6.png)
*Image Source: Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), Fig. 5.6 (from Timkey & van Schijndel, EMNLP 2021)*

**Choosing an embedder.** Start from the MTEB leaderboard, which ranks retrieval by NDCG, but don't stop there. Scores are self-reported, and some models may have trained on the benchmark data. Test two or three candidates on your own queries (*Building AI Agents*, ch. 5). Huyen points to BEIR (14 retrieval benchmarks) for the same comparison (*AI Engineering*, ch. 6).

---

## Metadata filtering

Filters are SQL-style constraints on fields (`region == "EU"`, `tier >= "pro"`, `date > 2024-01-01`). They are rigid: a document either passes or not, and there is no ranking. Use them for access control, subscription tiers and freshness. Never as a substitute for search.

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

**Check which way alpha points.** Raieli and Iuculano define hybrid weight α so that α = 0 is pure vector search and α = 1 is pure keyword, with typical values of 0.4–0.5 (some recommend 0.3) (*Building AI Agents*, ch. 6). Weaviate's `hybrid(alpha=…)`, used in note [04](04-vector-databases-and-ann.md#4-query), runs the other way: α = 1 is pure vector. The same "0.3" means mostly keyword in one convention and mostly vector in the other. Read the library's definition before copying a number.

```python
def reciprocal_rank_fusion(list1, list2, top_k=5, K=60):
    rrf_scores = {}
    for lst in [list1, list2]:
        for rank, item in enumerate(lst, start=1):   # ranks start at 1
            rrf_scores.setdefault(item, 0)
            rrf_scores[item] += 1 / (rank + K)       # agreement across lists adds up
    sorted_items = sorted(rrf_scores, key=rrf_scores.get, reverse=True)
    return [int(x) for x in sorted_items[:top_k]]
```

The assignment's output shows fusion at work:

| Retriever | Top 5 indices |
|---|---|
| Semantic | 743, 673, 626, 752, 326 |
| BM25 | 752, 673, 289, 626, 43 |
| **RRF** | **673, 752, 626, 743, 289** |

673, 752 and 626 appear in both lists, so they rise to the top. Each retriever's unique pick (743, 289) survives in lower places.

---

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

**Recall@k is the most cited** for RAG: the LLM can ignore a bad document, but it can't use one you never retrieved. Note [01 § measure each stage](01-rag-pipeline.md#measure-each-stage) puts these in the pipeline context.

---

## Rules of thumb

| Rule | Why |
|---|---|
| Default to hybrid (BM25 + dense + RRF) | Each covers the other's blind spot; cost is small |
| Retrieve 20–50 per retriever before fusion | RRF needs depth to find agreement |
| Check your embedder's token limit | Past it, text is silently ignored |
| Filters for constraints, search for relevance | Mixing them up hides docs or leaks them |
| Track Recall@k first | Generation can't fix a missing doc |

---

## Labs

| Lab | Label |
|---|---|
| M2 ungraded labs (TF-IDF, BM25, embeddings) and Assignment 2 (hybrid retriever) ([upstream](https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG)) | needs `bm25s`, `sentence-transformers`; course data; not copied |

→ Next: [04-vector-databases-and-ann.md](04-vector-databases-and-ann.md) — semantic search with a linear scan doesn't scale; ANN indexes and a vector database make it fast.
