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
cleaned: 2026-11-01
---
# 4 — Vector databases and approximate nearest neighbours

Tallybook's 18 help articles search instantly with a NumPy dot product. Add every customer's invoices and support threads, and the same line of code becomes the slowest thing in the request, because it still compares the query with every stored vector. Teams usually discover this in production, when latency climbs with the corpus and the fix looks like "buy a database". Understanding what the database does first tells you what you're buying and what you give up, which is a small and measurable share of the true nearest neighbours.

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

Exact, simple, and linear. Past a few hundred thousand vectors it is too slow for interactive search. You can watch it happen on random 384-dimensional vectors, the size of a small sentence embedder:

```python
import time
import numpy as np

rng = np.random.default_rng(0)
query = rng.normal(size=384)
query /= np.linalg.norm(query)

for n in [10_000, 100_000, 400_000]:
    vectors = rng.normal(size=(n, 384)).astype("float32")
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    start = time.perf_counter()
    for _ in range(20):
        scores = vectors @ query
        np.argpartition(-scores, 5)[:5]
    ms = (time.perf_counter() - start) / 20 * 1000
    print(f"{n:>7} vectors  {ms:7.2f} ms per query  {vectors.nbytes / 1e6:6.0f} MB")
```

```text
  10000 vectors     0.71 ms per query      15 MB
 100000 vectors     6.96 ms per query     154 MB
 400000 vectors    29.00 ms per query     614 MB
```

Times are from one laptop and will differ on yours. The shape is the point: ten times the vectors costs roughly ten times the time. One query is survivable, but a RAG request can fan out into several queries, and a server handles many requests at once.

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

Here is that walk from scratch, on 2,000 random vectors. The graph links each point to its 8 nearest neighbours, which is built by brute force here because this is a demo. The walk counts how many distances it computes:

```python
import numpy as np

rng = np.random.default_rng(1)
points = rng.normal(size=(2_000, 16))
points /= np.linalg.norm(points, axis=1, keepdims=True)
similarity = points @ points.T
np.fill_diagonal(similarity, -1)
graph = np.argsort(-similarity, axis=1)[:, :8]       # the proximity graph

def greedy_walk(query, start):
    current, computed = start, 1
    while True:
        neighbours = graph[current]
        computed += len(neighbours)
        best = neighbours[np.argmax(points[neighbours] @ query)]
        if points[best] @ query <= points[current] @ query:
            return current, computed                 # no neighbour is closer: stop
        current = best

hits, costs = 0, []
for _ in range(200):
    query = rng.normal(size=16)
    query /= np.linalg.norm(query)
    found, computed = greedy_walk(query, start=int(rng.integers(2_000)))
    hits += found == int(np.argmax(points @ query))
    costs.append(computed)

print(f"exact scan cost: {len(points)} distances")
print(f"greedy walk:     {np.mean(costs):.0f} distances on average")
print(f"found the true nearest neighbour {hits / 200:.0%} of the time")
```

```text
exact scan cost: 2000 distances
greedy walk:     34 distances on average
found the true nearest neighbour 17% of the time
```

The walk computes a small fraction of the distances and misses the true best match often, because it stops at local optima. That is the bargain ANN offers, in its crudest form. Everything below is engineering to get the savings and most of the recall back.

### Hierarchical NSW (HNSW)

HNSW speeds up the early part of the walk by stacking proximity graphs of decreasing size:

| Layer | Vectors (course example) | Role |
|---|---|---|
| 3 (top) | 10, randomly sampled | Big jumps: start at a random node, get as close as possible |
| 2 | 100 | Intermediate: start from layer 3's best candidate |
| 1 (bottom) | All 1,000, full proximity graph | Precise final search from layer 2's best candidate |

Each layer has exponentially fewer vectors (1000 → 100 → 10), which makes the search approximately logarithmic and lets it scale to billions of vectors.

```text
layer 3   o-----------------o-----------o            10 nodes: long jumps
          |                 |
layer 2   o-----o-----o-----o-----o-----o           100 nodes: narrower
                      |
layer 1   o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o         1,000 nodes: full graph
                      ^
              search drops down here, then walks to the query's neighbours
```

`ef` is the width of the beam on the bottom layer: how many candidates the search keeps while it walks. It is the knob that buys recall with latency, so measure it. FAISS has HNSW built in, which lets us compare it with exact search on the same vectors:

```python
import time
import faiss
import numpy as np

faiss.omp_set_num_threads(1)                         # one core, so the timings compare
rng = np.random.default_rng(0)
# Clustered vectors: random ones are harder than real embeddings.
centres = rng.normal(size=(200, 128))
vectors = (centres[rng.integers(200, size=100_000)]
           + 0.6 * rng.normal(size=(100_000, 128))).astype("float32")
queries = (centres[rng.integers(200, size=200)]
           + 0.6 * rng.normal(size=(200, 128))).astype("float32")

exact = faiss.IndexFlatL2(128)
exact.add(vectors)
start = time.perf_counter()
_, truth = exact.search(queries, 10)
print(f"exact         {(time.perf_counter() - start) / 200 * 1000:7.3f} ms/query  recall@10=1.000")

index = faiss.IndexHNSWFlat(128, 16)                 # M = 16 links per node
index.hnsw.efConstruction = 100
start = time.perf_counter()
index.add(vectors)
print(f"HNSW build    {time.perf_counter() - start:7.1f} s")

for ef in [10, 40, 160]:
    index.hnsw.efSearch = ef
    start = time.perf_counter()
    _, found = index.search(queries, 10)
    ms = (time.perf_counter() - start) / 200 * 1000
    recall = np.mean([len(set(f) & set(t)) / 10 for f, t in zip(found, truth)])
    print(f"HNSW ef={ef:<4}   {ms:7.3f} ms/query  recall@10={recall:.3f}")
```

```text
exact           0.810 ms/query  recall@10=1.000
HNSW build        6.1 s
HNSW ef=10       0.018 ms/query  recall@10=0.736
HNSW ef=40       0.038 ms/query  recall@10=0.972
HNSW ef=160      0.102 ms/query  recall@10=1.000
```

These are synthetic vectors and one machine's clock, so don't quote the numbers. Do copy the method: compute exact results on a sample, then sweep `ef` until recall is good enough for your latency budget. Build time is the cost you pay once.

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
import os, tempfile
import faiss
from ragkit import Retriever

retriever = Retriever()
vectors = retriever.vectors.astype("float32")        # FAISS wants float32, shape (n, dim)
dim, k = vectors.shape[1], 3

index = faiss.IndexFlatL2(dim)                       # brute force: exact KNN, no training
index.add(vectors)
query = vectors[3:4]                                 # kb-04's own vector as the query
D, I = index.search(query, k)
# D holds SQUARED L2 distances (smaller = closer); I holds row positions, not your IDs
print("positions:", I[0], "squared L2:", D[0].round(3))
print("doc ids:  ", [retriever.ids[i] for i in I[0]])

path = os.path.join(tempfile.mkdtemp(), "docs.faiss")
faiss.write_index(index, path)                       # persist ...
index = faiss.read_index(path)                       # ... and reload

index2 = faiss.IndexFlatL2(dim)
index2.add(vectors[:2])
index.add(index2.reconstruct_n(0, index2.ntotal))    # merge two flat indexes
print("total after merge:", index.ntotal)
```

```text
positions: [ 3  4 17] squared L2: [0.    0.149 0.448]
doc ids:   ['kb-04', 'kb-05', 'kb-18']
total after merge: 20
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

The failure is easy to reproduce. A signed-in screen for account settings restricts search to `area="account"`, and the user wants 3 results:

```python
from ragkit import DOC_BY_ID, Retriever

retriever = Retriever()
query = "invite an accountant to the team"
allowed = {d.id for d in DOC_BY_ID.values() if d.area == "account"}

def post_filter(q, k=3):
    return [i for i in retriever.dense(q, k=k) if i in allowed]

def pre_filter(q, k=3):
    return [i for i in retriever.dense(q, k=len(retriever.ids)) if i in allowed][:k]

print("documents in the area:", len(allowed))
print("post-filter:", post_filter(query))
print("pre-filter: ", pre_filter(query))
```

```text
documents in the area: 3
post-filter: ['kb-16']
pre-filter:  ['kb-16', 'kb-14', 'kb-15']
```

Post-filtering asked for 3, threw away the two from other areas, and returned 1. The other two weren't missing from the corpus. They ranked below the cut before the filter ran.

`pre_filter` is written here as "rank everything, then filter", which is correct and slow. Real engines get the same answer by searching inside the allowed subset, which is why filter support is a property of the index and not an afterthought.

**Do you need a separate vector database at all?** Oshin and Campos argue for pgvector when your data already lives in Postgres. Vectors sit next to the rows they describe, one transaction updates both, and there's one less system to secure and back up (*Learning LangChain*, ch. 2). Raieli and Iuculano's caveat: SQL vector extensions have historically capped dimensions and scaled less far than dedicated stores (*Building AI Agents*, ch. 5). Their selection criteria are licence, language support, maturity, insert and query speed, access control, framework integration, and cost including backups.

Weaviate is the open-source one the course uses. Note [09](09-vector-database-comparison.md) compares the stores used in production work: pgvector, OpenSearch (Bedrock KB), Elasticsearch, Pinecone, DuckDB, ChromaDB and Vertex AI Search.

---

## The Weaviate API, condensed from the lab

The lab runs **embedded Weaviate** with a local Flask server providing the embedding and reranker models. The dataset is travel destinations (place, state, description, season, attractions, budget, ratings).

### 1. Connect

```python
# illustrative: needs weaviate-client v4, embedded Weaviate and a local inference server on :5000
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
# illustrative: needs weaviate-client v4, embedded Weaviate and a local inference server on :5000
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
# illustrative: needs weaviate-client v4, embedded Weaviate and a local inference server on :5000
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
# illustrative: needs weaviate-client v4, embedded Weaviate and a local inference server on :5000
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
# illustrative: needs a Pinecone account and API key, plus `index`, `docs` and `q` from the book's walkthrough
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

---

## Pitfalls

- **Quoting ANN latency without recall.** Symptom: a benchmark looks great and relevance falls after the migration. Report recall@k against exact search next to every latency figure.
- **Post-filtering a selective filter.** Symptom: some queries come back with one result or none while matching documents exist. Filter inside the index, or over-fetch and check the count.
- **Trusting FAISS row positions as IDs.** Symptom: citations point at the wrong document after a merge or rebuild. Keep your own position to ID map and rebuild it with the index.
- **Mixing distance metrics.** Symptom: scores look inverted, because FAISS L2 is smaller-is-better and cosine is larger-is-better. Normalise vectors and check the direction on a known pair.
- **Random UUIDs at ingestion.** Symptom: rerunning the loader doubles the corpus and duplicates fill your top k. Derive the ID from the content or source key.
- **Reading alpha the wrong way.** Symptom: "mostly keyword" hybrid behaves like pure vector after a port. Check each engine's definition before reusing a value.

---

## Try it

1. Change the greedy walk to restart from 5 random entry points and keep the best result. What happens to recall and to cost?
2. In the HNSW block, add `ef = 640`. What do you expect, and what would make you stop raising it in production?
3. You have 5M vectors, filters on `tenant_id`, and the data already lives in Postgres. Which store do you try first, and what do you measure before moving off it?

<details>
<summary>Answers</summary>

1. On the same seed, cost goes from 34 to about 173 distances and recall from 17% to about 56%. That is five times the work for a large gain and still a miss almost half the time. HNSW's layers and beam search spend that budget more cleverly than blind restarts do.
2. Recall can only get close to 1.0, and latency keeps climbing. Stop when recall meets the target you measured against answer quality, or when latency hits the budget.
3. pgvector with an HNSW index and the filter in SQL: vectors sit next to their rows, and one transaction updates both (Oshin and Campos). Measure recall against exact search on a sample, p95 latency under filter, and index build time, then compare with a dedicated store only if those miss the target.

</details>

---

## Interview checklist

| Question | Answer |
|---|---|
| Why not just scan every vector? | KNN cost grows linearly with the corpus, so each query at 1B vectors computes 1B distances. |
| What does ANN give up? | The guarantee of the true top k. You trade a measurable loss in recall for far fewer distance calculations. |
| How does HNSW search? | It walks stacked proximity graphs from a sparse top layer down to the full bottom layer, greedily moving closer to the query at each level, for roughly logarithmic cost. |
| What are `M`, `efConstruction` and `ef`? | Links per node, the beam width while building, and the beam width at query time. Higher values raise recall and cost memory, build time or latency respectively. |
| When would you use IVF, PQ or LSH instead? | IVF to probe a few k-means clusters, PQ to shrink memory with approximate distances, LSH for fast cheap builds with lower recall. FAISS commonly combines IVF and PQ. |
| What does a vector database add over FAISS? | Create, update and delete, metadata filters, persistence and backups, plus keyword, hybrid and reranked search in many cases. |
| Pre-filter or post-filter? | Post-filter can return fewer than k results under a selective filter. Pre-filter keeps k but needs index support. |
| When is pgvector enough? | When your data is already in Postgres and scale is modest: one system and one transaction. Check its dimension and scale limits against your load. |
| How do you compare ANN indexes? | On recall, queries per second, build time and index size, as ANN-Benchmarks does. |
| How do you make ingestion idempotent? | Derive object IDs deterministically from the content, such as `generate_uuid5`, so a rerun overwrites instead of duplicating. |

---

## Next

[05 — Chunking, query parsing and reranking](05-chunking-query-parsing-and-reranking.md): what to store in the collection (chunks), what to send it (a parsed query), and how to clean up what comes back (reranking).
