---
origin: Deeplearning.ai-RAG-main
sources:
  - https://www.deeplearning.ai/courses/retrieval-augmented-generation-rag/
  - https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG (Module 3, "Information Retrieval with Vector Databases" part 1 + ungraded lab "Introduction to Weaviate API")
  - Huyen, *AI Engineering* (O'Reilly, 2025), ch. 6
  - Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 5
  - Iusztin & Labonne, *LLM Engineer's Handbook* (Packt, 2024), ch. 4
  - Phoenix & Taylor, *Prompt Engineering for Generative AI* (O'Reilly, 2024), ch. 5
  - Oshin & Campos, *Learning LangChain* (O'Reilly, 2025), ch. 2
confidence: high
cleaned: 2026-10-31
---
# 4 — Vector databases and approximate nearest neighbours

> Exact nearest-neighbour search is linear in corpus size. ANN indexes, HNSW above all, make it roughly logarithmic by walking a layered proximity graph, at the cost of sometimes missing the true best match. A vector database wraps that index with storage, filters, keyword search and reranking. The course uses Weaviate; this note keeps its API.

---

## Why a linear scan stops working

The note 03 retriever computes a cosine score against every document. That is **k-nearest neighbours (KNN)**:

1. Embed the prompt.
2. Compute the distance to every document vector.
3. Sort and return the closest k.

| Corpus | Distance calculations per query |
|---|---|
| 1,000 docs | 1,000 |
| 1M docs | 1M |
| 1B docs | 1B, every time |

Exact, simple, and linear. Past a few hundred thousand vectors it is too slow for interactive search.

---

## Approximate nearest neighbours (ANN)

ANN algorithms trade a guarantee for speed. They build an extra data structure ahead of time and use it to visit only a small part of the corpus.

| Property | KNN | ANN |
|---|---|---|
| Finds the true top k | Always | Usually, not guaranteed |
| Query cost | Linear | ~Logarithmic (HNSW) |
| Index build | None | Expensive, but precomputed |
| Memory | Vectors only | Vectors + graph |

### Navigable Small World (NSW)

1. Compute distances between document vectors.
2. Add one graph node per document.
3. Connect each node to its nearest neighbours: a **proximity graph**.

Search is greedy: start at an entry point, move to whichever neighbour is closest to the query vector, repeat until no neighbour is closer. It picks the best step at each moment, not the best overall path, so it can stop at a local optimum. In practice it performs well and is much faster than KNN.

### Hierarchical NSW (HNSW)

HNSW speeds up the early part of the walk by stacking proximity graphs of decreasing size:

| Layer | Vectors (course example) | Role |
|---|---|---|
| 3 (top) | 10, randomly sampled | Big jumps: start at a random node, get as close as possible |
| 2 | 100 | Intermediate: start from layer 3's best candidate |
| 1 (bottom) | All 1,000, full proximity graph | Precise final search from layer 2's best candidate |

Each layer has exponentially fewer vectors (1000 → 100 → 10), which makes the search approximately logarithmic and lets it scale to billions of vectors.

The knobs (`M`, `efConstruction`, `ef`) and the HNSW-vs-Annoy comparison are in note [09 § ANN index types](09-vector-database-comparison.md#ann-index-types-hnsw-vs-annoy).

### The other index families

HNSW is one of several. Huyen's list (*AI Engineering*, ch. 6):

| Family | Idea | Trade-off |
|---|---|---|
| **LSH** (locality-sensitive hashing) | Hash so that close vectors collide in the same bucket | Fast, cheap build; lower recall. The mirror image of HNSW |
| **HNSW** | Layered proximity graph (above) | Fast, accurate queries; slow, memory-hungry build |
| **IVF** (inverted file) | k-means clusters; search only the clusters nearest the query. Typical clusters hold 100–10,000 vectors | Recall depends on how many clusters you probe |
| **PQ** (product quantization) | Split each vector into sub-vectors and replace each with a codebook ID | Much less memory; approximate distances |
| **Annoy** | A forest of random-projection trees | Simple, static index ([09](09-vector-database-comparison.md#ann-index-types-hnsw-vs-annoy)) |

Libraries combine them: FAISS's workhorse is IVF plus PQ. ScaNN, SPTAG and FLANN are the other common ones. Compare indexes on four numbers, as ANN-Benchmarks does: recall, queries per second, build time and index size.

### FAISS by hand

FAISS is the library most tutorials start with. Phoenix and Taylor's walkthrough shows the parts that matter in practice (*Prompt Engineering for GenAI*, ch. 5):

```python
import faiss, numpy as np

index = faiss.IndexFlatL2(dim)                   # brute force: exact KNN, no training
index.add(vectors.astype("float32"))             # FAISS wants float32, shape (n, dim)
D, I = index.search(query.reshape(1, -1).astype("float32"), k)
# D holds SQUARED L2 distances (smaller = closer); I holds row positions, not your IDs

faiss.write_index(index, "docs.faiss")           # persist ...
index = faiss.read_index("docs.faiss")           # ... and reload

index1.add(index2.reconstruct_n(0, index2.ntotal))   # merge two flat indexes
```

Two traps. FAISS returns row positions, and merging renumbers them, so keep your own position → document-ID map. And `reconstruct_n` works directly only on flat indexes. The book says IVF indexes can't be reconstructed and must be rebuilt; FAISS can do it after `index.make_direct_map()`, but keeping the source vectors and rebuilding is simpler.

---

## What a vector database adds

A relational database doing vector search is running an inefficient KNN. A vector database is built for the ANN case:

| Operation | What it does |
|---|---|
| Setup | Create a collection with a schema and a vectorizer |
| Load | Batch-insert documents, with error handling |
| Sparse vectors | Build the BM25 index for keyword search |
| Dense vectors | Call the embedding model on each object |
| HNSW index | Build the ANN graph |
| Search | Vector, keyword, hybrid, filtered, reranked |

A library such as FAISS is only the index. Iusztin and Labonne list what a database adds on top: create, update and delete; metadata filtering; persistence and backups (*LLM Engineer's Handbook*, ch. 4). Raieli and Iuculano call FAISS a good fit for immutable data for the same reason (*Building AI Agents*, ch. 5).

**Filter before or after the vector search?** Filtering after the ANN search is simple, but can leave fewer than k results when the filter is selective. Filtering first, inside the index, keeps k results but needs index support (*LLM Engineer's Handbook*, ch. 4). PRINCE filters first ([01](01-rag-pipeline.md#a-tuned-pipeline-bayers-prince)).

**Do you need a separate vector database at all?** Oshin and Campos argue for pgvector when your data already lives in Postgres. Vectors sit next to the rows they describe, one transaction updates both, and there's one less system to secure and back up (*Learning LangChain*, ch. 2). Raieli and Iuculano's caveat: SQL vector extensions have historically capped dimensions and scaled less far than dedicated stores (*Building AI Agents*, ch. 5). Their selection criteria are licence, language support, maturity, insert and query speed, access control, framework integration, and cost including backups.

Weaviate is the open-source one the course uses. Note [09](09-vector-database-comparison.md) compares the stores used in production work: pgvector, OpenSearch (Bedrock KB), Elasticsearch, Pinecone, DuckDB, ChromaDB and Vertex AI Search.

---

## The Weaviate API, condensed from the lab

The lab runs **embedded Weaviate** with a local Flask server providing the embedding and reranker models. The dataset is travel destinations (place, state, description, season, attractions, budget, ratings).

### 1. Connect

```python
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import Filter, Rerank
from weaviate.util import generate_uuid5

client = weaviate.connect_to_embedded(
    persistence_data_path="./.collections",          # persisted between sessions
    environment_variables={
        "ENABLE_API_BASED_MODULES": "true",
        "ENABLE_MODULES": "text2vec-transformers, reranker-transformers",
        "TRANSFORMERS_INFERENCE_API": "http://127.0.0.1:5000/",  # local embedder
        "RERANKER_INFERENCE_API": "http://127.0.0.1:5000/",      # local cross-encoder
    },
)
```

### 2. Configure the vectorizer and create a collection

```python
vectorizer_config = [Configure.NamedVectors.text2vec_transformers(
    name="vector",                         # how you address this vector later
    source_properties=["place", "state", "description",
                       "best_season_to_visit", "attractions", "budget"],  # concatenated, then embedded
    vectorize_collection_name=False,       # don't prepend the collection name
    inference_url="http://127.0.0.1:5000",
)]

collection = client.collections.create(
    name="example_collection",
    vectorizer_config=vectorizer_config,
    reranker_config=Configure.Reranker.transformers(),   # enables rerank= at query time
    properties=[
        Property(name="place", vectorize_property_name=True, data_type=DataType.TEXT),
        # ... state, description, best_season_to_visit, attractions, budget: TEXT
        Property(name="user_ratings", data_type=DataType.NUMBER),  # filterable, not embedded
        Property(name="last_updated", data_type=DataType.DATE),
    ],
)
```

Creating a collection that already exists raises, so the lab deletes first or calls `client.collections.get(name)`.

### 3. Batch insert

```python
with collection.batch.fixed_size(batch_size=1, concurrent_requests=1) as batch:
    for document in data:
        batch.add_object(
            properties=document,               # dict keyed by property name
            uuid=generate_uuid5(document),     # deterministic: re-running won't duplicate
        )
len(collection)                                # number of stored objects
```

### 4. Query

```python
q = "I want suggestions to travel during Winter. I want cheap places."

# Filter only, no ranking
collection.query.fetch_objects(limit=2,
    filters=Filter.by_property("user_ratings").greater_or_equal(3.5))

# Semantic search, with and without a metadata filter
collection.query.near_text(query=q, limit=4)
collection.query.near_text(query=q, limit=4,
    filters=Filter.by_property("budget").contains_any(["Low", "Moderate"]))

# Keyword search: same arguments, BM25 underneath
collection.query.bm25(query=q, limit=4,
    filters=Filter.by_property("budget").contains_any(["Low", "Moderate"]))

# Hybrid: RRF-style fusion. alpha = 1 is pure vector, 0 is pure BM25
collection.query.hybrid(query=q, alpha=0.3, limit=4,
    filters=Filter.by_property("budget").contains_any(["Low", "Moderate"]))

# Rerank the top results with the cross-encoder, on one property, with its own query
collection.query.near_text(query=q, limit=5,
    rerank=Rerank(prop="attractions", query="Fun places"))

client.close()                                 # embedded server keeps running otherwise
```

| Method | Ranking | Note 03 equivalent |
|---|---|---|
| `fetch_objects(filters=…)` | none | metadata filter |
| `near_text` | cosine on dense vectors | `semantic_search_retrieve` |
| `bm25` | BM25 on the inverted index | `bm25_retrieve` |
| `hybrid(alpha=…)` | fused | `reciprocal_rank_fusion` |
| `rerank=Rerank(…)` | cross-encoder on top-k | note 05 |

The lecture example weights hybrid as 25% vector / 75% keyword; the lab uses `alpha=0.3`. Some sources define alpha the other way round, with 0 as pure vector ([03 § hybrid search](03-keyword-semantic-and-hybrid-search.md#hybrid-search-and-reciprocal-rank-fusion)). Check before porting a value. Tune alpha on your own eval set: keyword-heavy for catalogues with SKUs, vector-heavy for conversational queries.

---

## Pinecone: a hosted example

Phoenix and Taylor's Pinecone walkthrough shows the hosted side (*Prompt Engineering for GenAI*, ch. 5). Hosted means no servers to run and scaling handled for you. The cost is per-vector pricing, data leaving your network, and a vendor API that changes. The book's code already shows API drift: `create_index(dimension=1536, metric="cosine", spec=ServerlessSpec(...))` and `text-embedding-ada-002` were current in 2024.

```python
for i in range(0, len(docs), 10):                       # upsert in small batches
    batch = docs[i:i + 10]
    for attempt in range(5):                            # retry transient API errors
        try:
            index.upsert(vectors=[(d.id, d.vector, {"batch": i // 10, "text": d.text})
                                  for d in batch])
            break
        except Exception:
            time.sleep(5)

index.query(vector=q, top_k=3, include_metadata=True,
            filter={"batch": {"$eq": 1}})               # MongoDB-style metadata filter
```

Pinecone stores metadata numbers as 64-bit floats; the book's output shows `'batch': 10.0`. Compare IDs as strings, not as numbers in metadata. More metadata per vector also raises storage cost.

---

## Rules of thumb

| Rule | Why |
|---|---|
| Use an ANN index past ~100k vectors | KNN latency grows linearly |
| Measure recall of the ANN index itself | "Approximate" means some true neighbours are missed |
| Make UUIDs deterministic (`generate_uuid5`) | Re-ingestion stays idempotent |
| Embed text fields, store numbers and dates as filterable properties | Embedding a rating adds noise; filtering on it is exact |
| Close embedded clients | They hold ports and file locks |

---

## Labs

| Lab | Label |
|---|---|
| M3 ungraded lab "Introduction to Weaviate API" ([upstream](https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG)) | needs `weaviate-client` v4 + embedded Weaviate and a local transformers inference server on :5000; not copied |

→ Next: [05-chunking-query-parsing-and-reranking.md](05-chunking-query-parsing-and-reranking.md) — what to store in the collection (chunks), what to send it (a parsed query), and how to clean up what comes back (reranking).
