# Example: Scaling a RAG System 100x

## Prompt
"Your RAG-based customer support system handles 1K queries/day. Product wants to roll it out company-wide: 100K queries/day. What changes?"

## Step 1: Clarify & scope (3 min)

**Questions I'd ask**:
- Same corpus or expanding? (More teams = more knowledge bases?)
- Same query types or new use cases? (Support → sales → internal ops?)
- Latency SLA change? (Batch-OK for some use cases?)
- Budget scaling linearly with traffic, or need to optimize cost?
- Multi-tenant now? (Different teams see different docs?)

**Assumptions after clarify**:
- Corpus grows 5x (new departments), traffic grows 100x
- Mixed latency: interactive support (< 2s), batch analytics (async OK)
- Budget grows 10x, not 100x — need 10x cost efficiency
- Multi-tenant: per-department access control required

## Step 2: What changes (organized by component)

### Ingestion pipeline
**Before**: Single-process embedding job, runs nightly.
**After**:
- Async ingestion queue with priority (new docs > updates > bulk re-index)
- Incremental embedding: only re-embed changed/new docs, not full corpus
- Parallel embedding workers (shard by department/collection)
- Staleness tracking: docs have `last_embedded` timestamp, alert if > 24h stale

### Vector index
**Before**: Single pgvector table, brute-force scan.
**After**:
- HNSW indexes (pgvector supports this, but at 100x may need dedicated vector store)
- Partition by department (multi-tenant isolation + query scoping)
- Pre-filter by metadata before vector search (department, doc_type, date range) — reduces the search space by 5-10x
- Periodic index rebuild (weekly) to handle tombstones and optimize recall

**Trade-off narrated**: pgvector vs dedicated vector DB (Pinecone, Weaviate). pgvector: simpler ops, co-located with app data, RLS for access control. Dedicated: better performance at scale, managed scaling. Decision depends on whether ops complexity or query latency is the bigger risk. At 100K queries/day, I'd likely stay with pgvector + HNSW unless p95 exceeds SLA.

### Caching
**Before**: No caching.
**After**:
- **Prefix cache**: System prompt + common instruction prefix cached across requests. Saves ~30-50% of input tokens (same system prompt on every query).
- **Semantic cache**: Hash embedding of query → if similar query answered in last N hours, return cached response. Hit rate on support queries is typically 20-40% (many users ask similar questions). Cache invalidation on corpus update.
- **Expected impact**: 30-50% reduction in LLM calls, proportional cost savings.

### Model serving
**Before**: Single model, all queries.
**After**:
- **Model routing**: Classify queries by complexity:
  - Simple (FAQ-like, high cache hit) → small/fast model (Haiku-tier) or cached response
  - Medium (standard RAG) → mid-tier model (Sonnet-tier)
  - Complex (multi-step reasoning, synthesis) → large model (Opus-tier)
- **Queue management**: Priority tiers (interactive > batch), per-tenant rate limits
- **Fallback chain**: Primary model → secondary provider → graceful degradation message
- **Expected cost impact**: 60-70% of queries route to small model → ~3-5x cost reduction vs all-large

### Retrieval quality
**Before**: Works well at 50K chunks.
**After at 500K+ chunks**:
- Recall may drop as corpus grows (more noise, more near-misses)
- Cross-encoder reranker becomes critical (was nice-to-have, now load-bearing)
- Need to bound reranker N (top-20 not top-100 — latency constraint)
- Eval golden set must grow with corpus — stale set gives false confidence

### Observability & eval
**Before**: Basic logging.
**After**:
- Trace sampling: 100% at 1K queries is fine; at 100K, sample 5-10% for detailed traces
- Per-tenant quality dashboards
- Cost tracking per department (chargeback model)
- Online quality graders on sampled traffic
- Latency percentile monitoring with alerting

## Step 3: What doesn't change

- The fundamental pipeline: retrieve → rerank → generate → validate
- The eval methodology (just runs on a sample, not every query)
- The safety layer (scales linearly with traffic — it's cheap)
- The HITL path for escalation
- The feedback loop (thumbs-down → golden set)

## Step 4: Cost model (the "one cost line" close)

| Component | At 1K queries/day | At 100K queries/day | With optimization |
|---|---|---|---|
| LLM calls | ~$30/day | ~$3,000/day | ~$600/day (routing + caching) |
| Embedding (inference) | ~$2/day | ~$20/day (incremental) | $20/day |
| Vector DB compute | ~$5/day | ~$50/day (HNSW) | $50/day |
| Reranker | ~$3/day | ~$300/day | $150/day (bounded N) |
| **Total** | **~$40/day** | **~$3,370/day** | **~$820/day** |

"At 100K queries/day, naive scaling costs $3,400/day (~$100K/month). With model routing and caching, I'd get it to ~$820/day (~$25K/month) — a 4x cost reduction. The biggest lever is routing simple queries to a small model."

## Step 5: What breaks first

1. **Retrieval quality** — more corpus = more noise. Measure recall@k regression early.
2. **Cache invalidation** — stale cached answers when corpus updates. Need TTL + corpus-change triggers.
3. **Per-tenant fairness** — one heavy tenant can starve others. Need per-tenant rate limits and quota.
4. **Eval set representativeness** — golden set curated for old query distribution. Must refresh.
5. **Reranker latency** — becomes the bottleneck at high N. Bound it.

---

**Study refs**: [study guide §4](../study-guide.md) bottleneck tables; [RAG guide §5](../../../guides/3-rag/interview-guide.md) for latency budgets; [context/cost guide](../../../guides/5-context-cost/interview-guide.md) for caching and token economics; librarian wiki: Semantic Cache Pipeline, Production Hardening Patterns.
