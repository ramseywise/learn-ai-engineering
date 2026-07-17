# Pillar 3 — RAG (retrieval-augmented generation)

The default pattern for giving an LLM knowledge it wasn't trained on: chunk documents,
embed them, retrieve the relevant pieces, ground the answer in them. Most enterprise LLM
systems are RAG systems — and most interview design questions have a RAG core.

## Learning path

1. **The idea** — the original RAG paper (2005.11401) + the RAG survey (2312.10997) in
   `readings/3-rag/` for the landscape.
2. **Build one** — a chatbot from `generative-ai/coursera-references/` (RAG course repos)
   or extend `generative-ai/chatbot/`; embed → store → retrieve → answer with citations.
3. **Make retrieval good** — hybrid search + reranking + query rewriting: librarian's
   *RAG Retrieval Strategies* page, then the advanced-pattern papers (Self-RAG 2310.11511
   — note the terminology trap in the interview guide, CRAG, RAPTOR-era work in
   `readings/3-rag/`).
4. **Measure it** — RAGAS (2309.15217 + `ragas_automated_evaluation.pdf`) and ARES
   (2311.09476); pairs with pillar 6.
5. **Knowledge graphs as the next step** — *Knowledge Graphs and LLMs in Action* (full
   book, `readings/3-rag-knowledge-graphs/`): building KGs with LLMs, GraphRAG (ch 13),
   QA agents over graphs (ch 15 uses LangGraph).

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| RAG (2005.11401) · RAG survey (2312.10997) | pdf | `readings/3-rag/` | the founding pattern + taxonomy |
| Self-RAG (2310.11511) · corrective/advanced retrieval papers | pdf | `readings/3-rag/` | reflection + retry loops |
| RAGAS (2309.15217) · ARES (2311.09476) | pdf | `readings/3-rag/` | RAG evaluation frameworks |
| *Knowledge Graphs and LLMs in Action* (chs 1–15 + appendices) | pdf | `readings/3-rag-knowledge-graphs/` | KG construction, GNNs, KG-RAG, Neo4j |
| coursera RAG course repos | code | `generative-ai/coursera-references/` | guided builds |
| chatbot projects | code | `generative-ai/chatbot/` | working RAG codebases incl. deep-research bot |
| RAG Retrieval Strategies · RAG Evaluation · Agentic RAG — Advanced Patterns (+ 13 more) | wiki | librarian `wiki/rag/` | compiled production patterns (RRF, E5 prefixes, reranking) |
| rag.md | note | [../../notes/rag.md](../../notes/rag.md) | 9 RAG architectures + prod checklist |
| 9 RAG architectures diagram | image | [../../images/9-rag-architectures.png](../../images/9-rag-architectures.png) | visual taxonomy |

## Test yourself
[interview-guide.md](interview-guide.md) · rounds:
[system-design-round](../../rounds/system-design-round.md),
[technical-questions](../../rounds/technical-questions.md).
