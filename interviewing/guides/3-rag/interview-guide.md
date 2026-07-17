# RAG — Study Guide

The default enterprise GenAI pattern and the most likely deep-dive topic in AIE/FDE loops.
Interviewers probe three levels: component choices (chunking/embedding/search), architecture
selection (which RAG variant and why), and production judgment (eval, latency, failure modes).

## 1. Core pipeline and component trade-offs

Ingest → chunk → embed → index; query → (rewrite) → retrieve → (rerank) → generate → (verify).

**Chunking** — split on document structure first (headings), recursively on
paragraph/sentence boundaries, to a token budget (~512) with overlap (~64). Fixed windows
are baseline-only; semantic chunking is expensive at ingest and inconsistent. Parent/child
chunking (index small chunks, generate from their parent) helps long documents. Watch the
silent failure: a `min_tokens` filter can drop short-but-valid sections (one-line FAQ
answers) from the index entirely.

**Embeddings** — model choice is corpus-dependent: multilingual corpora need a multilingual
model (`multilingual-e5-large`, 1024-dim); English-only can use smaller/faster models.
E5-family gotcha worth citing in interviews: the `"query: "` / `"passage: "` prefix rule is
mandatory — violating it silently degrades recall ~15–20%. Small English-only models
(`all-MiniLM-L6-v2`) silently fail on non-English text.

**Vector stores** — decision axes: local vs managed, native BM25 support, write concurrency,
multi-tenancy. ChromaDB (HNSW, local) for dev/small prod; DuckDB brute-force is fine to
~50K chunks; OpenSearch/pgvector for production multi-tenant. See
[vector-databases comparison] in the librarian wiki for the full matrix.

**Hybrid search** — vector-only misses exact tokens (product names, error codes); BM25-only
misses paraphrases. Fuse with **RRF** (Reciprocal Rank Fusion): `1/(k+rank_bm25) +
1/(k+rank_vec)`, k=60. RRF beats linear score-weighting because BM25 and cosine scores have
incomparable distributions — rank fusion is parameter-free and typically adds 3–8% hit rate.

**Reranking** — cross-encoder rerank of the top-N is the single highest-leverage add-on.
Production benchmark from one of my deployments: dense-only 45% → BM25 50% → hybrid RRF 58%
→ **hybrid + cross-encoder 68% hit rate**. Cite numbers like this — interviewers reward
measured claims over vibes.

## 2. Architecture menu (know when, not just what)

| Pattern | Mechanism | Use when |
|---|---|---|
| Standard RAG | retrieve top-k → prompt → generate | baseline; always implement first |
| Conversational RAG | + dialogue state, query condensation (coreference rewrite) | chat products |
| **CRAG** (Corrective) | retrieve → grade chunks (confidence gate) → retry/fallback below threshold | accuracy-critical, predictable retrieval |
| **Self-RAG** | LLM emits reflection tokens (`[Retrieve]`, `[IsRel]`, `[IsSup]`) mid-generation, decides when to retrieve | retrieval is expensive, many queries don't need it |
| Adaptive RAG | complexity/intent router → simple/moderate/complex pipelines | mixed workloads; cost control |
| Fusion RAG | multiple retrievers (vector + web + SQL) → merge → synthesize | breadth of sources matters |
| HyDE | LLM writes a hypothetical answer, embed *that* for search | lexical gap: short/vague queries vs dense docs |
| Agentic RAG | retrieval as a tool inside planner → executor → verifier loop | multi-step reasoning, actions, provenance |
| GraphRAG | entity/relationship graph + traversal beside vector search | relationship queries ("what do all X share?") |

**Terminology trap (real interview risk):** some blogs use "Self-RAG" for LLM query
expansion. The canonical Self-RAG (Asai et al.) is the reflection-token pattern above. If an
interviewer's definition differs from yours, surface the ambiguity — that itself scores.

**CRAG vs Self-RAG in one line:** CRAG decides *in the graph topology* before generation;
Self-RAG decides *inside the LLM* during generation.

**GraphRAG restraint:** it's overkill for factual lookup. For wiki-shaped corpora,
existing link structure (e.g. wikilinks) already gives you a traversable graph — say this
before proposing entity extraction + community detection.

**Knowledge-graph RAG in depth:** chapters in `readings/2.knowledge graphs/` (KG-powered
retrieval, QA agents over graphs) cover the build path: entity linking → graph features →
KG-RAG.

## 3. Query-side upgrades

- **Query condensation / rewrite**: resolve coreferences ("what about its pricing?") with a
  small fast model before retrieval — standard in conversational RAG.
- **Multi-query (RAG-Fusion)**: 3 paraphrase variants, parallel retrieve, global dedup by
  chunk fingerprint, highest score wins. +10–15% recall; diminishing returns past 3 variants.
- **HyDE**: one extra small-model call (~100–200ms); regenerate hypothetical docs when the
  model or corpus changes.

## 4. What to measure (the eval answer)

Retrieval: hit rate / recall@k, precision@k, MRR. Generation: faithfulness/groundedness
(claims supported by retrieved evidence), answer relevance, hallucination rate. System:
p95 latency, cost per query, deflection/trust metrics. Agentic additions: evidence coverage
per answer, self-correction rate, human-override frequency.

Method: golden dataset + LLM-as-judge calibrated against human labels — full treatment in
the [evals-observability guide](evals-observability.md).

## 5. Latency and cost budgets (memorize one)

| Pipeline | p50 | p95 |
|---|---|---|
| single retrieve, no rerank | 300ms | 800ms |
| CRAG-gated Q&A | 800ms | 2s |
| CRAG with one retry | 1.5s | 4s |
| agentic plan+execute | 2s | 6s |

Component budget for the full path: rewrite ~200ms → hybrid retrieval ~100ms → grading
~300ms → cross-encoder ~100ms → streaming generation 800–1500ms ≈ **1.4–2.1s total**.

## 6. Production checklist (the "what else?" answer)

Chunk-size discipline within prompt budget · cross-encoder on top-N · incremental embedding
refresh for changing corpora · semantic/prefix caching for repeat queries · token-budget
enforcement with summarization · vector-DB snapshot/rebuild plan · PII redaction + access
control · HITL review for flagged outputs · claim-level provenance if CRAG/agentic.

## 7. Question bank (answer sketches)

- *"Walk me through chunking strategy for 10K PDFs with tables."* — structure-aware chunking;
  tables extracted separately (layout parser) and indexed with serialized text + caption;
  parent/child for long sections; state the eval you'd run to pick parameters.
- *"Retrieval quality is poor — debug it."* — decompose: measure recall@k on a golden set
  first; check embedding/corpus language match, prefix rules, chunk truncation, then hybrid
  + reranker before touching the LLM.
- *"RAG vs fine-tuning?"* — RAG for knowledge freshness, provenance, per-tenant corpora;
  fine-tuning for format/style/task behavior; they compose. Cost/update-cadence trade-off.
- *"Corpus grows 10× — what breaks?"* — index build time, brute-force scans (→ ANN/HNSW),
  reranker N, dedup, stale-content ratio (→ recall ceiling), eval set representativeness.
- *"When would you NOT use RAG?"* — stable narrow knowledge that fits the context window or
  a fine-tune; latency-critical paths; poor-quality corpora (garbage in).

## Sources

- notes: [rag.md](../notes/rag.md) (9-architectures + production checklist), [memory.md](../notes/memory.md) (memory-augmented conversational RAG)
- images: [9 RAG architectures](../images/9-rag-architectures.png)
- readings: `0.rag/` (RAG, Self-RAG, RAGAS, survey papers), `2.knowledge graphs/` (KG-RAG chapters)
- librarian wiki: RAG Retrieval Strategies · Agentic RAG — Advanced Patterns · RAG Reranking · Reciprocal Rank Fusion · RAG Evaluation · CRAG Retry Logic · Semantic Cache Pipeline · Vector Database Comparison · HistoryCondenser
- course refs: `generative-ai/coursera-references/Deeplearning.ai-RAG-main`, `Knowledge_Graphs_for_RAG-main`
