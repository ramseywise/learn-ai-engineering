# Vector Databases — Reference & Trade-offs

Landscape of vector stores relevant to our RAG architecture. Scoped to what appears in our codebase or is a realistic migration target.

---

## What we currently use

| Store | Where | Mode |
|---|---|---|
| OpenSearch | Bedrock KB (galactus VA agents) | Managed — Bedrock owns the index |
| DuckDB | hc_rag default vector backend | Embedded, self-managed, no server |
| ChromaDB | hc_rag optional backend (`chroma` extra) | Embedded, persistent HNSW |
| pgvector | chat-agent local/dev | Self-managed PostgreSQL extension |
| GCP Discovery Engine | chat-agent production | Fully managed — GCP owns everything |

---

## Side-by-side comparison

| | DuckDB + VSS | ChromaDB | pgvector | OpenSearch | Elasticsearch | Pinecone | Bedrock KB |
|---|---|---|---|---|---|---|---|
| **Type** | Embedded / in-process | Embedded / client-server | PostgreSQL extension | Dedicated search engine | Dedicated search engine | Managed vector DB | Managed RAG service |
| **Hosting** | Embedded / file | Embedded or cloud | Self-hosted or RDS/Supabase | Self-hosted or AWS AOSS | Self-hosted or Elastic Cloud | SaaS only | AWS managed |
| **Hybrid search** | Dense only | Dense only | Manual (dense + BM25 plugin) | Native HNSW + BM25 | Native HNSW + BM25 | Dense only (no sparse) | Native hybrid (Bedrock default) |
| **Max index dim** | No limit (exact) | No limit | 2000 (HNSW) / unlimited exact | 16k (HNSW) | 4096 (ANN) | 20k | Managed |
| **ANN algorithm** | Flat (exact) or HNSW | HNSW (cosine) | HNSW / IVFFlat | HNSW | HNSW | HNSW + proprietary | Managed |
| **Reranking** | Manual | Manual | Manual (cross-encoder) | Manual | Manual | Via Cohere plugin | `amazon.rerank-v1:0` built-in |
| **Metadata filtering** | SQL WHERE | `where={}` dict | SQL WHERE | Query DSL | Query DSL | Filter expressions | Inline filter |
| **Operational overhead** | Zero | Zero | Low (rides your DB) | High | High | Zero | Zero |
| **Cost model** | Free | Free / Chroma Cloud | Storage + compute (shared) | Cluster cost | Cluster cost | Per-vector + per-query | Per-query + storage |
| **Streaming ingest** | COPY or INSERT | `upsert()` | psycopg batch insert | Bulk API | Bulk API | upsert API | Data source sync |

---

## When to use which

### pgvector
Best for: dev environments, prototypes, teams already running Postgres.

Constraints in chat-agent:
- Gemini `gemini-embedding-2-preview` outputs 3072 dims → exceeds pgvector's 2000-dim HNSW index limit → **exact search only** (no ANN index). This is fine at our dataset size but won't scale to millions of docs.
- Cosine similarity via `<=>` operator.
- No sparse/BM25 hybrid without a separate plugin (pg_bm25 / ParadeDB).

```python
# chat-agent pattern: cosine similarity query
SELECT text, metadata, 1 - (embedding <=> %s::vector) AS score
FROM documents
ORDER BY embedding <=> %s::vector
LIMIT %s
```

### OpenSearch (Bedrock KB)
Best for: AWS-native production, multilingual corpora, hybrid search without extra infrastructure.

How Bedrock uses it:
- Two-level hierarchical chunking: leaf chunk (`AMAZON_BEDROCK_TEXT_CHUNK`) + parent context window (`AMAZON_BEDROCK_TEXT`).
- `HYBRID` search mode hardcoded — dense (HNSW) + sparse (BM25) combined automatically.
- `amazon.rerank-v1:0` ARN reranker available as a second pass.
- Vector field: `bedrock-knowledge-base-default-vector`.
- Raw `_score` is NOT exposed by the Bedrock KB API (always returns 0.0 via API; only visible in OpenSearch dashboard).

See [bedrock-kb.md](bedrock-kb.md) for full field mapping, retrieval modes, and env vars.

### Elasticsearch
Comparable to OpenSearch (shared lineage). Prefer when:
- Already running Elastic Cloud / on-prem ES cluster.
- Need Elastic's ML node ecosystem (ELSER sparse encoder for better hybrid).
- Cross-language relevance tuning matters.

Diverges from OpenSearch post-v7.10 (license split). API-compatible for basic queries; Elastic-specific features (ELSER, Elastic Learned Sparse EncodeR) don't port directly.

### Pinecone
Best for: pure-play vector similarity with no operational burden. Weakness: no native BM25 hybrid — dense only. Not a good fit for our multilingual support KB where keyword precision matters (product names, billing codes).

### DuckDB
Two roles in our codebase:

**hc_rag production backend (default):** `VECTOR_STORE_BACKEND=duckdb` — the `DuckDBVectorIndex` in `rag/datastore/local.py` stores embeddings in a `.duckdb` file and does exact cosine search. No server, no infra. Ships as a core dep in the hc_rag `pyproject.toml` (`duckdb>=1.0`).

```bash
VECTOR_STORE_BACKEND=duckdb VECTORDB_PATH=data/corpus/v1/knowledge.duckdb uv run uvicorn main:app
```

**Eval / analysis backend:** DuckDB's `vss` extension adds HNSW for offline retrieval sweeps without spinning up a server.

```sql
INSTALL vss; LOAD vss;
CREATE TABLE docs AS SELECT * FROM read_parquet('chunks.parquet');
ALTER TABLE docs ADD COLUMN embedding FLOAT[3072];
CREATE INDEX ON docs USING HNSW (embedding);
SELECT * FROM docs ORDER BY array_distance(embedding, ?::FLOAT[3072]) LIMIT 5;
```

Limitation: no hybrid search (dense only). For keyword-heavy queries (Danish product names, billing codes) retrieval quality is lower than OpenSearch hybrid.

### ChromaDB
Optional backend in hc_rag (`pip install chromadb` or `uv sync --extra chroma`). `ChromaVectorIndex` in `rag/datastore/local.py` uses `PersistentClient` with HNSW cosine distance.

```bash
VECTOR_STORE_BACKEND=chroma VECTOR_STORE_DIR=data/corpus/chroma uv run uvicorn main:app
```

When to prefer over DuckDB: when you want persistent HNSW (approximate search at larger corpus sizes) or plan to use the Chroma Cloud managed tier later. For our current corpus size (< 50k chunks), DuckDB exact search is fast enough and simpler.

**Not installed in the main galactus venv.** Tests that exercise ChromaDB use `pytest.importorskip("chromadb")` and run only under `make test-agents` with the hc_rag extras venv.

### GCP Discovery Engine (Vertex AI Search)
Best for: fully managed RAG on GCP — no index to manage, no reranker to wire up.

Two modes we use in chat-agent:

| Mode | Client class | Who generates the answer |
|---|---|---|
| Agentic RAG | `GcpAgentSearchClient` | Gemini ADK agentic loop (grade + rewrite) |
| Built-in answer | `GcpAnswerSearchClient` | GCP Discovery Engine (black box) |

See [gcp-vertex-vs-bedrock.md](gcp-vertex-vs-bedrock.md) for a detailed head-to-head comparison.

---

## Embedding model ↔ dimension ↔ store compatibility

| Embedding model | Dim | pgvector HNSW? | Notes |
|---|---|---|---|
| `gemini-embedding-2-preview` | 3072 | ❌ (>2000 limit) | Exact search only in pgvector |
| `amazon.titan-embed-text-v2:0` | 1024 | ✅ | Used by Bedrock KB |
| `text-embedding-3-large` (OpenAI) | 3072 / 256 (MRL) | ✅ at 256 | Matryoshka allows dimension reduction |
| `text-embedding-004` (Google) | 768 | ✅ | Cheaper, fits HNSW |

**The 2000-dim pgvector limit is for HNSW.** IVFFlat has no hard limit but requires `lists` tuning. Exact search (no index) works at any dimension — only trade-off is O(n) scan cost.

---

## Retrieval quality levers (apply to any store)

1. **Hybrid search** — combine dense (semantic) + sparse (BM25/ELSER) scores. Bedrock does this automatically; pgvector requires ParadeDB or a separate BM25 index.
2. **Reranking** — cross-encoder as a second pass over top-k candidates. Bedrock: `amazon.rerank-v1:0`. Elsewhere: Cohere Rerank, Jina Reranker, BGE-Reranker.
3. **Multi-query** — fire 2–3 reformulated queries in parallel, deduplicate by URL fingerprint. Used in galactus hc_lg and chat-agent.
4. **Parent-child chunking** — retrieve at leaf granularity, send parent context to LLM. Bedrock's native hierarchy maps to our `level=0` / `level=1` in `ChunkRecord`.
5. **CRAG (Corrective RAG)** — grade retrieved docs, rewrite query if below threshold, retry. Used in hc_lg and chat-agent agentic pipeline.

---

## Migration notes

**pgvector → OpenSearch**: straightforward if you're already on AWS. Main work is ingestion pipeline + adding BM25 hybrid config. Reranker is a one-line config change in Bedrock.

**OpenSearch (Bedrock) → pgvector**: lose hybrid search and managed reranking. Not recommended for production unless you add ParadeDB + a cross-encoder.

**pgvector → Pinecone**: lose keyword/hybrid, gain SaaS zero-ops. Only viable if your queries are purely semantic and corpus is English.

**Any → GCP Discovery Engine**: only viable if your stack is already GCP-native. Retrieval is a black box — you lose visibility into score calibration, chunk boundaries, and reranker behaviour. Suitable when you want GCP to own the full RAG loop (as in chat-agent's `:answer` backend).
