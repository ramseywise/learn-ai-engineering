# 02 — RAG & Retrieval

> Depth layer. Summary: [interviewing/guides/3-rag](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/3-rag/00-overview.md)
> Position in the path: second generative-ai pillar, the first production pattern built on LLMs. Builds on [01-llm-fundamentals](../01-llm-fundamentals/README.md).

---

## What it is

Retrieval-augmented generation (RAG) gives a language model external knowledge at inference time. It fetches relevant documents, puts them into the context and lets the model write the answer from them. It was the first widely deployed pattern that turned LLMs from demos into production systems.

This pillar covers the pipeline end to end:
- ingestion and chunking;
- keyword, semantic and hybrid search;
- vector databases and ANN indexes;
- query parsing and reranking;
- grounded generation and citations;
- tracing, evaluation, cost and latency in production.

Then come five write-ups from production: one published stack and four chapters from a real support-agent RAG project, the last of which compares two managed services with building your own.

> **Retrieval sets the ceiling: the LLM can't cite a document the retriever never returned.**

Retrieval as one context lever (just-in-time retrieval, contextual retrieval, memory) lives in [02-context 04](../../ai-engineering/02-context-engineering/notes/04-retrieval.md). Knowledge graphs as a retrieval layer live in [05-graph 11](../../ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher.md). This pillar does not repeat either.

## Why it matters

Most LLM applications at work need to answer from a company's own documents, and RAG is the default way to do it. Nearly all of its failures are retrieval failures that look like model failures: the answer reads well and is wrong, because the right passage never reached the prompt, or a stale one did. Knowing how to find which stage broke, and how to measure the fix, is the core skill here. It is also a standard topic in AI engineering interviews.

## The story

The whole pillar follows one running example. Tallybook is a small invoicing product, and its support bot tells a customer they have 14 days to get a refund. The current policy says 30. The 14 came from a 2024 archive page that is still in the index, and it scores about as well as the real one. Chasing that one wrong answer takes you through the pipeline. You ask how the bot found the page at all ([01](notes/01-rag-pipeline.md), [02](notes/02-why-rag-and-the-augmented-prompt.md)), then why search scored it highly and how to measure that ([03](notes/03-keyword-semantic-and-hybrid-search.md)). You look at where the vectors live ([04](notes/04-vector-databases-and-ann.md)), how the page was cut up and reranked ([05](notes/05-chunking-query-parsing-and-reranking.md)), what the model does with two contradictory passages ([06](notes/06-generation-for-rag.md)) and how you would catch this in production ([07](notes/07-rag-in-production.md)). The later chapters widen the view: a real multi-agent stack, choosing a store, caching answers, deciding which fix is worth building from an eval table, and finally asking whether to buy all of it from a cloud provider.

## Reading order

1. Read [01 The RAG pipeline](notes/01-rag-pipeline.md) for the map.
2. Work through 02–07, the DeepLearning.AI course condensed with its lab code and worked examples, one note per module.
3. Read 08–12 as case studies: Bayer's PRINCE stack, then the support-agent project's store comparison, cache, ablations and managed backends.
4. Keep the [rules of thumb](#rules-of-thumb) as the one-page summary, and the [deck](slides/rag-retrieval.pptx) for review.

Note 01 is the overview. Notes 02–07 are the course. Notes 08–12 are production write-ups that apply it.

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
| 11 | [Retrieval improvements](notes/11-retrieval-improvements.md) | Baseline eval, what the ablations showed, how much 32 queries can prove, prioritised research items |
| 12 | [Managed RAG: Bedrock, Vertex, and building your own](notes/12-managed-rag.md) | Bedrock KB reference spec, Vertex comparison, score semantics, when to switch, and the `kb_rag` decision record |

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DS 03/01 Text representation](../../data-science/03-nlp/notes/01-text-representation.md) | TF-IDF, derived from scratch |
| [DS 03/02 Text classification](../../data-science/03-nlp/notes/02-text-classification.md) | TF-IDF with a linear model as the baseline |
| [DS 03/04 Embeddings and similarity](../../data-science/03-nlp/notes/04-embeddings-and-similarity.md) | BM25 built by hand |
| [DS 03/07 LLM embeddings as features](../../data-science/03-nlp/notes/07-llm-embeddings-as-features.md) | What a sentence embedding is |
| [DS 01/04 Model evaluation](../../data-science/01-classical-ml/notes/04-model-evaluation.md) | The confusion matrix under recall@k |
| [DS 05/02 Collaborative filtering](../../data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation.md) | Recall and NDCG computed on a ranking |

**Feeds into**

| Chapter | Why |
|---|---|
| [AIE 02/04 Retrieval](../../ai-engineering/02-context-engineering/notes/04-retrieval.md) | Retrieval as a context decision |
| [AIE 03/05 Verification loops](../../ai-engineering/03-harness-engineering/notes/05-verification-loops.md) | Checking agentic RAG's output |
| [AIE 05/11 KG-RAG and text-to-Cypher](../../ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher.md) | Retrieval over a graph |
| [AIE 08/03 Multimodal RAG](../../ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag.md) | The same pipeline with images |

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
| On a small eval set, test a difference with a paired bootstrap before believing it | [11](notes/11-retrieval-improvements.md) |
| Never compare scores across modes or backends. Compare systems on eval metrics | [12](notes/12-managed-rag.md) |
| A managed service takes the index, not the eval set or the decision about what goes in | [12](notes/12-managed-rag.md) |

## Deck and practice

- **Deck:** [slides/rag-retrieval.pptx](slides/rag-retrieval.pptx), one slide or more for every note, built from [slides/deck.yaml](slides/deck.yaml). Rebuild with `make slides PILLAR=generative-ai/02-rag-retrieval STRICT=1` from the repo root.
- **Practice:** [practice/](practice/README.md) holds the Tallybook corpus and a small retrieval kit that needs only NumPy, plus the checker that runs every code block in these notes:

```bash
cd generative-ai/02-rag-retrieval/practice
uv run --with numpy python ragkit.py        # the BM25, dense and hybrid scoreboard
```

## Layout

```
README.md      this file: what, why, reading order, rules of thumb, resource map
references.md  every source the notes cite, mapped to notes; source quality
notes/         01–12; figures and code inline
practice/      ragkit.py (Tallybook corpus and retrieval kit), check_blocks.py
slides/        deck.yaml and the built deck
sources/       paper PDFs, routed book chapters (<book-slug>/chNN-*.pdf)
  images/      every figure the notes use (<author>-<slug>-…)
```

---

## Resource map

### Related notes elsewhere
- [02-context 04 — retrieval](../../ai-engineering/02-context-engineering/notes/04-retrieval.md): retrieval as a context lever. [06 — memory](../../ai-engineering/02-context-engineering/notes/06-memory.md): memory formats and Mem0.
- 05-graph, knowledge graphs for RAG: [09 KG fundamentals and Cypher](../../ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher.md), [10 building KGs with LLMs](../../ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms.md), [11 KG-RAG and text-to-Cypher](../../ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher.md).

### Books and courses
- Zain Hasan, DeepLearning.AI, *Retrieval Augmented Generation (RAG)*: condensed into notes 02–07. The local snapshot was removed on 2026-10-31.
- Li, *AI Agents in Depth*, ch. 3: synthesised into 01.
- Huyen, *AI Engineering*, ch. 6 (RAG half): folded into 01–05 and 07.
- Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. 5–6: folded into 01–07.
- Rothman, *Context Engineering for Multi-Agent Systems*, ch. 3 and 7: folded into 01, 06 and 07.
- Oshin & Campos, *Learning LangChain*, ch. 2–3; Iusztin & Labonne, *LLM Engineer's Handbook*, ch. 4 and 9; Phoenix & Taylor, *Prompt Engineering for Generative AI*, ch. 5: folded into 01 and 03–07. Their PDFs live in [01-llm-fundamentals/sources/](../01-llm-fundamentals/sources/).
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
