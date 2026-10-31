# 02 — RAG & Retrieval

> Depth layer. Summary: [interviewing/guides/3-rag](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/3-rag/00-overview.md)
> Position: second pillar — the first killer app pattern built on LLMs.
> Presumes: [01-llm-fundamentals](../01-llm-fundamentals/README.md).

---

## What it is

Retrieval-augmented generation (RAG) is the pattern of augmenting a language model with
external knowledge at inference time — fetch relevant documents, inject them into context,
let the model synthesize. It was the first broadly-deployed pattern that turned LLMs from
demos into production systems.

This pillar covers: embedding and retrieval mechanics, chunking strategies, reranking,
citation and faithfulness measurement, and knowledge-graph-augmented retrieval.

---

## Resource map

### Course material (hands-on)

- **[`Deeplearning.ai-RAG-main/`](Deeplearning.ai-RAG-main/)** —
  DeepLearning.AI RAG course: building a document-QA pipeline with embeddings, vector
  stores, and faithfulness evaluation.
- **05-graph-engineering, knowledge graphs for RAG** —
  [KG fundamentals and Cypher](../../ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher.md),
  [building KGs with LLMs](../../ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms.md) and
  [KG-RAG and text-to-Cypher](../../ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher.md):
  knowledge graphs as a retrieval layer, with structured retrieval over graph databases.

### Interviewing guides

- [3-rag](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/3-rag/00-overview.md) — compressed summary for
  interview prep: embedding models, vector stores, chunking, reranking, faithfulness.

### Cleaned notes

- [rag.md](rag.md) — the RAG pipeline: architectures (naive / advanced / modular, nine named
  patterns), pre-retrieval stage order, ingestion and parser tiers, chunking, hybrid retrieval
  (BM25 + dense, RRF and weighted fusion, rerank, metrics), a first production pipeline (Bedrock KB),
  a tuned one (Bayer's PRINCE, Text-to-SQL), index-time structures (RAPTOR, GraphRAG, filesystems),
  agentic RAG (Li Exp. 3-9), conversational multi-turn RAG, monitoring and production checklist.
  Most of the pipeline material moved here from [02-context 04](../../ai-engineering/02-context-engineering/notes/04-retrieval.md),
  which now covers retrieval as one context lever.
- [rag/agent-rag-patterns.md](rag/agent-rag-patterns.md) — retrieval inside an agent: patterns for
  retrieval as a tool, planning and verification.
- [rag/vector-databases.md](rag/vector-databases.md) — store comparison, ANN index types (HNSW vs. ANNOY),
  embedding dimension compatibility.
- [rag/bedrock-kb.md](rag/bedrock-kb.md), [rag/gcp-vertex-vs-bedrock.md](rag/gcp-vertex-vs-bedrock.md),
  [rag/hc-rag-pipeline.md](rag/hc-rag-pipeline.md), [rag/retrieval-improvements.md](rag/retrieval-improvements.md),
  [rag/semantic-cache.md](rag/semantic-cache.md) — project reference specs.
- [images/](images/) — figures used by rag.md.

### Worked examples

- [BM25 from scratch](rag.md#bm25-from-scratch) — tokenisation, IDF, the k1/b term score and ranking
  in ~40 lines, with sample output. Full engine and tests upstream:
  [Li 3-5 sparse-embedding](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/sparse-embedding).
- [Retrieved few-shot examples with ChromaDB](rag.md#text-to-sql-is-a-retrieval-strategy) — the DAIR
  `pe-rag` pipeline; notebook upstream at
  [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide/blob/main/notebooks/pe-rag.ipynb).

### Readings

- [`3-rag/`](3-rag/) — RAG reference papers and book chapters.
- Li, *AI Agents in Depth*, [ch. 3 User Memory and Knowledge Base](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter3.md). Synthesized into [rag.md](rag.md) (hybrid stages, metrics, RAPTOR/GraphRAG/filesystem, agentic RAG), [02-context 04 — retrieval](../../ai-engineering/02-context-engineering/notes/04-retrieval.md) (just-in-time retrieval, contextual retrieval, index-time distillation) and [06 — memory](../../ai-engineering/02-context-engineering/notes/06-memory.md) (formats, Mem0, two-tier memory, three-level eval). Pipeline material is in [rag.md](rag.md). Worked example: [BM25 from scratch](rag.md#bm25-from-scratch). The other labs (ANNOY vs. HNSW, hybrid + rerank, agentic RAG, RAPTOR vs. GraphRAG) need models or API keys: [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter3).
- [`../../ai-engineering/05-graph-engineering/sources/`](../../ai-engineering/05-graph-engineering/sources/) — knowledge
  graphs for retrieval reference material.

---

## Cross-links to ai-engineering

RAG is fundamentally a **context assembly pattern** — the retrieved documents become the
context window. The ai-engineering depth layer for this:

- [ai-engineering/02-context-engineering/](../../ai-engineering/02-context-engineering/README.md) — context
  engineering: assembling, compressing, and budgeting the context window that delivers
  your retrieved documents.
- [ai-engineering/05-graph-engineering/](../../ai-engineering/05-graph-engineering/README.md) — graph engineering:
  the LangGraph/knowledge-graph layer that makes multi-step retrieval programmable.

---

## Next pillar

→ [03-agentic-foundations/](../03-agentic-foundations/README.md) — agents extend RAG:
instead of a single retrieve-then-generate call, an agent plans, retrieves, acts, and
iterates over multiple turns.
