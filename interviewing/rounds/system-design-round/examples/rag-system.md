# Example: Document-QA for a Legal Firm

## Prompt
"Design a document-QA system for a legal firm. They have 50K contracts and legal documents. Lawyers need to ask questions like 'What are the termination clauses in our agreements with Company X?' and get answers with citations."

## Step 1: Clarify & scope (3 min)

**Questions I'd ask**:
- Document types? (PDFs, Word, scanned images → OCR needed?)
- Query patterns: factual lookup ("what's the termination clause?") vs synthesis ("summarize all IP provisions across our portfolio")?
- Latency: is this interactive (< 3s) or batch ("run overnight, email results")?
- Data sensitivity: can docs leave the network? On-prem requirement?
- Scale: 50K now — growing how fast? How many concurrent users?
- Accuracy priority: legal context means wrong answers are high-consequence

**Assumptions after clarify**:
- Mostly PDFs with some scans (need OCR/layout parser for tables)
- Interactive use, p95 < 3s
- Data stays on-prem (client privilege) → self-hosted models or private cloud
- Accuracy > latency > cost (legal context — wrong citations are unacceptable)

## Step 2: Requirements (2 min)

**Functional**: Natural-language query, multi-turn conversation, answers with document-level and page-level citations, filter by client/document type/date range.

**Non-functional**: p95 < 3s, faithfulness > 0.95 (legal-grade accuracy), data residency (no external API calls with document content), audit trail (who queried what, when), access control (not all lawyers see all clients' documents).

## Step 3: Design (15 min)

### Ingestion pipeline
```
Documents → Layout parser (extract text, tables, headings)
  → Structure-aware chunking (heading-based, ~512 tokens, 64 overlap)
  → Tables extracted separately (serialized text + caption)
  → Embed (self-hosted model, e.g. E5-large)
  → Index in pgvector (multi-tenant, per-client access control)
  → Metadata: client, doc_type, date, page_number, section_heading
```

**Why pgvector over dedicated vector DB**: On-prem constraint, already running Postgres for app state, multi-tenant access control maps to RLS (row-level security). Tradeoff: slower than HNSW-optimized stores, but at 50K docs (~500K chunks) brute-force is still viable.

### Query pipeline
```
Query → Access control check (user can see which clients?)
  → Query rewrite (coreference resolution for multi-turn)
  → Hybrid search: vector (E5) + BM25 over exact terms
    → RRF fusion (k=60)
    → Metadata pre-filter (client, doc_type if specified)
  → Cross-encoder rerank top-20 → top-5
  → CRAG confidence gate:
    → Score > 0.7: generate with retrieved context
    → Score 0.4-0.7: expand query (multi-query), retry
    → Score < 0.4: "I couldn't find relevant information" + suggest refining
  → Generate with citations:
    → System prompt enforces citation format: [DocName, p.X]
    → Structured output: {answer, citations: [{doc, page, quote}]}
  → Output validation: verify each citation actually appears in retrieved chunks
  → Response
```

### Key trade-off narrated

**RAG vs fine-tuning**: RAG. Legal corpus changes (new contracts added weekly), citations/provenance are required (can't get them from a fine-tuned model), and client isolation is easier with per-tenant indexes than per-tenant models. Fine-tuning would only make sense for the response *style* (legal language patterns), not the *knowledge*.

**Self-hosted vs API**: Self-hosted given data residency. Use an open model (Llama 3 or Mistral) for generation. Trade-off: lower capability than frontier models, mitigated by strong retrieval (the model mostly needs to synthesize well-retrieved chunks, not reason from scratch).

### Sidecars
- **Trace/observability**: Langfuse (self-hosted), every query traced with retrieval scores, generation, and citation verification results
- **Eval**: Golden set of 100 query-answer pairs with expected citations, run on deploy
- **Semantic cache**: Repeat queries common in legal ("what's the NDA standard?") → cache with invalidation on document updates
- **Audit log**: Append-only log of queries and responses per user

## Step 4: Shortcomings (3 min)

- **Tables**: Layout parsing is imperfect; complex legal tables may chunk poorly → would need manual QA of table extraction quality
- **Cross-document synthesis**: "Compare termination clauses across all vendor agreements" requires retrieving from many documents — may exceed context window. Mitigation: map-reduce pattern (summarize per-doc, then synthesize).
- **Model capability**: Self-hosted models weaker at complex legal reasoning than frontier models. Mitigation: strong retrieval reduces the reasoning burden.
- **Freshness**: New docs need re-embedding. If a doc is updated, stale chunks persist until re-indexed. Need an incremental refresh pipeline with version tracking.

## Step 5: Close with measurement (2 min)

**Metrics**: Hit rate@5 > 0.85, faithfulness > 0.95, citation accuracy > 0.90 (every cited passage actually supports the claim), p95 < 3s, cost per query (compute, not API).

**Future improvements**:
- GraphRAG for relationship queries ("which agreements reference this clause?")
- User feedback loop: thumbs-down → flag for human review → enrich golden set
- Distilled model for simple FAQ-type queries (reduce GPU load)
- Batch mode for portfolio-wide analysis ("run this query across all 50K docs overnight")

---

**Study refs**: [RAG guide §1-5](../../../guides/3-rag/interview-guide.md) for pipeline details; [security guide §5](../../../guides/7-security-safety/interview-guide.md) for compliance; librarian wiki: RAG Retrieval Strategies, pgvector migration pattern.
