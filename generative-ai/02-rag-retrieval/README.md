# 02 — RAG & Retrieval

> Depth layer. Summary: [interviewing/guides/3-rag](../../interviewing/guides/3-rag/00-overview.md)
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
- **[`../../ai-engineering/05-graph/Knowledge_Graphs_for_RAG-main/`](../../ai-engineering/05-graph/Knowledge_Graphs_for_RAG-main/)** —
  knowledge graphs as a retrieval layer: structured retrieval over graph databases,
  KG-augmented context assembly.

### Interviewing guides

- [3-rag](../../interviewing/guides/3-rag/00-overview.md) — compressed summary for
  interview prep: embedding models, vector stores, chunking, reranking, faithfulness.

### Cleaned notes

- [rag.md](rag.md) — RAG architecture: retrieval pipeline,
  chunking strategies, hybrid search, reranking, faithfulness and groundedness evaluation.
- [graph-engineering.md](../../ai-engineering/05-graph/graph-engineering.md) — knowledge
  graph patterns: entity extraction, graph construction, KG-for-RAG, graph traversal.

### Readings

- [`3-rag/`](3-rag/) — RAG reference papers and book chapters.
- [`../../ai-engineering/05-graph/3-rag-knowledge-graphs/`](../../ai-engineering/05-graph/3-rag-knowledge-graphs/) — knowledge
  graphs for retrieval reference material.

---

## Cross-links to ai-engineering

RAG is fundamentally a **context assembly pattern** — the retrieved documents become the
context window. The ai-engineering depth layer for this:

- [ai-engineering/02-context/](../../ai-engineering/02-context/README.md) — context
  engineering: assembling, compressing, and budgeting the context window that delivers
  your retrieved documents.
- [ai-engineering/05-graph/](../../ai-engineering/05-graph/README.md) — graph engineering:
  the LangGraph/knowledge-graph layer that makes multi-step retrieval programmable.

---

## Next pillar

→ [03-agentic-foundations/](../03-agentic-foundations/README.md) — agents extend RAG:
instead of a single retrieve-then-generate call, an agent plans, retrieves, acts, and
iterates over multiple turns.
