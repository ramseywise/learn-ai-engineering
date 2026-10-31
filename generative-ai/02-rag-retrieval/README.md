# 02 — RAG & Retrieval

> Depth layer. Summary: [interviewing/guides/3-rag](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/3-rag/00-overview.md)
> Position in the path: second generative-ai pillar, the first production pattern built on LLMs. Builds on [01-llm-fundamentals](../01-llm-fundamentals/README.md).

---

## What it is

Retrieval-augmented generation (RAG) augments a language model with external knowledge at inference time. It fetches relevant documents, puts them into the context and lets the model write the answer from them. It was the first widely deployed pattern that turned LLMs from demos into production systems.

This pillar covers the pipeline end to end:
- ingestion and chunking;
- keyword, semantic and hybrid search;
- vector databases and ANN indexes;
- query parsing and reranking;
- grounded generation and citations;
- tracing, evaluation, cost and latency in production.

Then come seven write-ups from a real support-agent RAG project.

> **Retrieval sets the ceiling: the LLM can't cite a document the retriever never returned.**

Retrieval as one context lever (just-in-time retrieval, contextual retrieval, memory) lives in [02-context 04](../../ai-engineering/02-context-engineering/notes/04-retrieval.md). Knowledge graphs as a retrieval layer live in [05-graph 11](../../ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher.md). This pillar does not repeat either.

## Start here

1. Read [01 The RAG pipeline](notes/01-rag-pipeline.md) for the map.
2. Work through 02–07, the DeepLearning.AI course condensed with its lab code, one note per module.
3. Read 08–14 as case studies: one published production stack (Bayer's PRINCE) and six project specs.
4. Keep the [rules of thumb](#rules-of-thumb) as the one-page summary.

## Layout

```
README.md      this file: overview, start here, rules of thumb, resource map
references.md  every source the notes cite, mapped to notes; source quality
notes/         01–14; figures and code inline
sources/       paper PDFs, routed book chapters (<book-slug>/chNN-*.pdf)
  images/      every figure the notes use (<author>-<slug>-…)
```

---

## Syllabus

Note 01 is the overview. Notes 02–07 are the course. Notes 08–14 are production write-ups that apply it.

| # | Note | Covers |
|---|---|---|
| 1 | [The RAG pipeline](notes/01-rag-pipeline.md) | Nine named architectures, pre-retrieval order, ingestion and parser tiers, chunking, hybrid retrieval, BM25 from scratch, PRINCE, RAPTOR and GraphRAG, agentic and multi-turn RAG, monitoring |
| 2 | [Why RAG, and the augmented prompt](notes/02-why-rag-and-the-augmented-prompt.md) | The knowledge gap, retriever vs. LLM, why not stuff the prompt, the smallest RAG as an f-string, Assignment 1 news RAG |
| 3 | [Keyword, semantic and hybrid search](notes/03-keyword-semantic-and-hybrid-search.md) | TF-IDF, BM25 (k1, b), embeddings and cosine, metadata filters, RRF, Recall@k / MRR / nDCG with worked numbers |
| 4 | [Vector databases and ANN](notes/04-vector-databases-and-ann.md) | KNN vs. ANN, NSW and HNSW, the Weaviate API: collections, `near_text`, `bm25`, `hybrid`, rerank |
| 5 | [Chunking, query parsing and reranking](notes/05-chunking-query-parsing-and-reranking.md) | Chunking strategies and overlap, query rewriting, GLiNER, HyDE, bi- vs. cross-encoder vs. ColBERT, over-retrieve and rerank |
| 6 | [Generation for RAG](notes/06-generation-for-rag.md) | Sampling (temperature, top-p), choosing an LLM, grounded prompts, structured output, hallucinations and citations, RAGAS, agentic routing, RAG vs. fine-tuning |
| 7 | [RAG in production](notes/07-rag-in-production.md) | Failure stories, the scope × evaluator matrix, Phoenix tracing, quantization, cost and latency budgets, security, multimodal RAG |
| 8 | [Agentic RAG: the PRINCE stack](notes/08-agentic-rag-prince.md) | Intent clarification, ingestion, the query-time pipeline, Text-to-SQL, domain sub-agents, NER metadata repair, evaluation |
| 9 | [Vector database comparison](notes/09-vector-database-comparison.md) | Side-by-side stores, when to use which, embedding ↔ dimension compatibility, HNSW vs. ANNOY, migration |
| 10 | [Semantic cache](notes/10-semantic-cache.md) | A three-tier cache for support agents: offline index, runtime module, routing, eval and merge criteria |
| 11 | [Retrieval improvements](notes/11-retrieval-improvements.md) | Baseline eval, what the ablations showed, prioritised research items |
| 12 | [Bedrock knowledge bases](notes/12-bedrock-knowledge-bases.md) | Reference spec: two retrieval modes, pipeline, cleaning, reranker, storage mapping, smoke test |
| 13 | [GCP Vertex vs. Bedrock](notes/13-gcp-vertex-vs-bedrock.md) | The same job on two clouds: architecture, behaviour, eval axis, when to switch |
| 14 | [kb_rag pipeline ADR](notes/14-kb-rag-pipeline-adr.md) | A self-built deterministic pipeline: module map, chunkers, rerankers, parsing, deferred items |

## Rules of thumb

| Rule | Note |
|---|---|
| Ingestion quality sets the ceiling. Fix parsing before tuning retrieval | [01](notes/01-rag-pipeline.md) |
| Default to hybrid search (BM25 + dense + RRF) | [03](notes/03-keyword-semantic-and-hybrid-search.md) |
| Track Recall@k first: generation can't fix a missing document | [03](notes/03-keyword-semantic-and-hybrid-search.md) |
| Check your embedder's token limit. Past it, text is silently dropped | [03](notes/03-keyword-semantic-and-hybrid-search.md) |
| Use metadata filters for constraints and search for relevance | [03](notes/03-keyword-semantic-and-hybrid-search.md), [04](notes/04-vector-databases-and-ann.md) |
| Start with fixed-size or recursive chunks and 10–20% overlap; measure before getting clever | [05](notes/05-chunking-query-parsing-and-reranking.md) |
| Over-retrieve 20–50, rerank to 3–10 | [05](notes/05-chunking-query-parsing-and-reranking.md) |
| Rewrite conversational queries with a small LLM; treat HyDE as an experiment | [05](notes/05-chunking-query-parsing-and-reranking.md) |
| Low temperature and an "answer only from the context" prompt with citations for factual RAG | [06](notes/06-generation-for-rag.md) |
| Trace from day one; evaluate components and the system | [07](notes/07-rag-in-production.md) |
| Cut prompt tokens before changing models | [07](notes/07-rag-in-production.md) |
| Filter by user permission at retrieval time. Prompt instructions are not access control | [07](notes/07-rag-in-production.md) |
| Ask a clarifying question before retrieving on an ambiguous query | [08](notes/08-agentic-rag-prince.md) |
| Counting, filtering and aggregation are Text-to-SQL jobs, not vector search | [01](notes/01-rag-pipeline.md), [08](notes/08-agentic-rag-prince.md) |

---

## Resource map

### Related notes elsewhere
- [02-context 04 — retrieval](../../ai-engineering/02-context-engineering/notes/04-retrieval.md): retrieval as a context lever. [06 — memory](../../ai-engineering/02-context-engineering/notes/06-memory.md): memory formats and Mem0.
- 05-graph, knowledge graphs for RAG: [09 KG fundamentals and Cypher](../../ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher.md), [10 building KGs with LLMs](../../ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms.md), [11 KG-RAG and text-to-Cypher](../../ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher.md).

### Books and courses
- Zain Hasan, DeepLearning.AI, *Retrieval Augmented Generation (RAG)*: condensed into notes 02–07. The local snapshot was removed on 2026-10-31.
- Li, *AI Agents in Depth*, ch. 3: synthesised into 01.
- Routed book chapters (Huyen ch. 6, Rothman ch. 5–6, *Context Engineering for Multi-Agent Systems* ch. 3 and 7) are in [sources/](sources/) and queued for `/chapter`.
- Rows and chapter maps are in [references.md](references.md).

### Coursework and labs
None are copied. Every lab is linked upstream, with its label in the note's `## Labs` table.

| Lab | Where | Label |
|---|---|---|
| DLAI M1–M5 ungraded labs and Assignments 1–5 | [upstream](https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG); notes 02–07 | needs API key (Together.ai via the Coursera proxy); M3–M5 also need embedded Weaviate + a local inference server; M5 needs Phoenix |
| BM25 from scratch | [01 § BM25 from scratch](notes/01-rag-pipeline.md#bm25-from-scratch); engine at [Li 3-5](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/sparse-embedding) | runs offline |
| Retrieved few-shot examples with ChromaDB | [01 § Text-to-SQL](notes/01-rag-pipeline.md#text-to-sql-is-a-retrieval-strategy); DAIR [`pe-rag.ipynb`](https://github.com/dair-ai/Prompt-Engineering-Guide/blob/main/notebooks/pe-rag.ipynb) | legacy |
| Li ch. 3 labs (ANNOY vs. HNSW, hybrid + rerank, agentic RAG, RAPTOR vs. GraphRAG) | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter3) | needs API key |

### Readings
- [sources/](sources/): paper PDFs and routed book chapters. Which note cites each, which are still queued, and which are duplicates or off-topic is in [references.md](references.md).

### Interviewing guide
- [3-rag](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/3-rag/00-overview.md): compressed summary for interview prep.

### Previous and next layer
← Builds on [01-llm-fundamentals/](../01-llm-fundamentals/README.md)
→ [03-agentic-foundations/](../03-agentic-foundations/README.md): agents extend RAG. Instead of one retrieve-then-generate call, an agent plans, retrieves, acts and iterates.
