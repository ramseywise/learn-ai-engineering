# References — RAG & Retrieval

> Every source the notes cite, mapped to notes. **★** = read first. Local PDFs live in [sources/](sources/). Rows marked *queued* are PDFs routed here by `/readings` that no note cites yet; fold them in with `/papers rag` or `/chapter`. Vendor and secondary posts, duplicates and off-topic PDFs are listed in [Source quality](#source-quality).

---

## Books and courses

| | Source | Notes |
|---|---|---|
| ★ | Zain Hasan, DeepLearning.AI, [*Retrieval Augmented Generation (RAG)*](https://www.deeplearning.ai/courses/retrieval-augmented-generation-rag/) (Coursera, 2025). Labs and decks as mirrored in [MohammadWasiq0786/Deeplearning.ai-RAG](https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG) (MIT). Folded in as: M1 → [02](notes/02-why-rag-and-the-augmented-prompt.md); M2 → [03](notes/03-keyword-semantic-and-hybrid-search.md); M3 part 1 → [04](notes/04-vector-databases-and-ann.md); M3 part 2 → [05](notes/05-chunking-query-parsing-and-reranking.md); M4 → [06](notes/06-generation-for-rag.md); M5 → [07](notes/07-rag-in-production.md). Figures in [sources/images/](sources/images/) as `hasan-dlai-rag-*` | 02–07 |
| ★ | Bojie Li, *AI Agents in Depth* (2026), [ch. 3 User Memory and Knowledge Base](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter3.md): hybrid stages, metrics, RAPTOR vs GraphRAG, agentic RAG (Exp. 3-9), BM25 from scratch. Labs [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter3) | 01 |
| ★ | LangChain, [*RAG from Scratch*](https://www.youtube.com/watch?v=sVcwVQRHIc8) (video series): query translation, routing, indexing, retrieval, generation | — (companion viewing for 01 and 05) |
| ★ | Huyen, *AI Engineering* (O'Reilly, 2025). Chapter PDF in [sources/huyen-ai-engineering/](sources/huyen-ai-engineering/). Folded in as: ch. 6, RAG half → [01](notes/01-rag-pipeline.md) (hybrid order, text-to-SQL table selection, agentic RAG), [02](notes/02-why-rag-and-the-augmented-prompt.md) (RAG vs long context), [03](notes/03-keyword-semantic-and-hybrid-search.md) (term vs embedding retrieval, naming of metrics), [04](notes/04-vector-databases-and-ann.md) (ANN families), [05](notes/05-chunking-query-parsing-and-reranking.md) (chunk units and overlap, contextual retrieval, query rewriting, reranking), [07](notes/07-rag-in-production.md) (cost, CLIP). The agents half of ch. 6 belongs to other pillars and is not folded in here. Figures as `huyen-ai-engineering-fig6-*`. Notes cite it as (*AI Engineering*, ch. 6) | 01–05, 07 |
| | Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025). Chapter PDFs in [sources/building-ai-agents-llms-rag-kgs/](sources/building-ai-agents-llms-rag-kgs/). Folded in as: ch. 5 → [03](notes/03-keyword-semantic-and-hybrid-search.md) (BM25 parameters, embedder training, rogue dimensions), [04](notes/04-vector-databases-and-ann.md) (choosing a store), [06](notes/06-generation-for-rag.md) (extra RAGAS metrics, RAG vs fine-tuning), [07](notes/07-rag-in-production.md) (quantization); ch. 6 → [01](notes/01-rag-pipeline.md) (naive-RAG failures, routers, hierarchical indexing, iterative retrieval), [02](notes/02-why-rag-and-the-augmented-prompt.md) (training paradigms, long context), [05](notes/05-chunking-query-parsing-and-reranking.md) (chunkers, hypothetical questions, rerankers), [06](notes/06-generation-for-rag.md) (context vs prior, compression, synthesizers), [07](notes/07-rag-in-production.md) (security, scale, multimodal). Figures as `building-ai-agents-llms-rag-kgs-fig*`. Notes cite it as (*Building AI Agents*, ch. N) | 01–07 |
| | Rothman, *Context Engineering for Multi-Agent Systems* (Packt, 2025). Chapter PDFs in [sources/context-engineering-multi-agent-systems/](sources/context-engineering-multi-agent-systems/). Folded in as: ch. 3 → [01](notes/01-rag-pipeline.md) (dual RAG, index reset); ch. 7 → [06](notes/06-generation-for-rag.md) (source-tagged citations, negative-result test), [07](notes/07-rag-in-production.md) (poisoning defence, sanitizer). Figures as `context-engineering-multi-agent-systems-fig*`. Notes cite it as (*Context Engineering for MAS*, ch. N) | 01, 06, 07 |
| | Oshin & Campos, *Learning LangChain* (O'Reilly, 2025). Chapter PDFs in [../01-llm-fundamentals/sources/learning-langchain/](../01-llm-fundamentals/sources/learning-langchain/). Folded in as: ch. 2 → [01](notes/01-rag-pipeline.md) (RecordManager, MultiVectorRetriever), [04](notes/04-vector-databases-and-ann.md) (pgvector), [05](notes/05-chunking-query-parsing-and-reranking.md) (recursive splitter); ch. 3 → [01](notes/01-rag-pipeline.md) (routing), [05](notes/05-chunking-query-parsing-and-reranking.md) (query transformations, RAG-Fusion, self-query). Figures as `learning-langchain-fig*`. Notes cite it as (*Learning LangChain*, ch. N) | 01, 04, 05 |
| | Iusztin & Labonne, *LLM Engineer's Handbook* (Packt, 2024). Chapter PDFs in [../01-llm-fundamentals/sources/llm-engineers-handbook/](../01-llm-fundamentals/sources/llm-engineers-handbook/). Folded in as: ch. 4 → [01](notes/01-rag-pipeline.md) (feature pipeline, CDC, chunk IDs), [03](notes/03-keyword-semantic-and-hybrid-search.md) (cosine range), [04](notes/04-vector-databases-and-ann.md) (library vs database, filter order), [05](notes/05-chunking-query-parsing-and-reranking.md) (article chunker, why rerank), [07](notes/07-rag-in-production.md) (batch embedding); ch. 9 → [01](notes/01-rag-pipeline.md) (LLM Twin retrieval), [05](notes/05-chunking-query-parsing-and-reranking.md) (author filter). Figures as `llm-engineers-handbook-fig*`. Notes cite it as (*LLM Engineer's Handbook*, ch. N) | 01, 03, 04, 05, 07 |
| | Phoenix & Taylor, *Prompt Engineering for Generative AI* (O'Reilly, 2024). Chapter PDF in [../01-llm-fundamentals/sources/prompt-engineering-for-generative-ai/](../01-llm-fundamentals/sources/prompt-engineering-for-generative-ai/). Folded in as: ch. 5 → [04](notes/04-vector-databases-and-ann.md) (FAISS, Pinecone), [05](notes/05-chunking-query-parsing-and-reranking.md) (regression to the mean, self-query), [07](notes/07-rag-in-production.md) (embedding cost). No figures. Notes cite it as (*Prompt Engineering for GenAI*, ch. 5) | 04, 05, 07 |

## First-party docs and engineering posts

| | Source | Notes |
|---|---|---|
| ★ | Martin Fowler / Bayer, [*Building reliable LLM systems at Bayer*](https://martinfowler.com/articles/reliable-llm-bayer.html): PRINCE, hybrid retrieval, Text-to-SQL, evaluation | 01, 08 |
| ★ | Weaviate [docs](https://weaviate.io/developers/weaviate): collections, vectorizers, `near_text`, `bm25`, `hybrid`, rerank. The course's vector DB | 04, 05, 07 |
| | Arize [Phoenix docs](https://docs.arize.com/phoenix) and OpenInference span kinds: tracing a RAG pipeline | 07 |
| | Anthropic, [*Contextual retrieval*](https://www.anthropic.com/news/contextual-retrieval) (2024): chunk-context prefixes plus BM25 and rerank | 01, 05 |
| | AWS, [Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html): parsers, chunking, hybrid search, metadata filters | 01, 12, 13, 14 |
| | Google Cloud, [Vertex AI Search](https://cloud.google.com/generative-ai-app-builder/docs/introduction) | 09, 13 |
| | [RAGAS docs](https://docs.ragas.io/): faithfulness, answer relevance, context precision and recall | 06, 07, 08 |
| | [ContextCite](https://gradientscience.org/contextcite/) (MIT Madry lab): attributing a statement to context spans | 06 |
| | Kamradt, [*5 Levels of Text Splitting*](https://github.com/FullStackRetrieval-com/RetrievalTutorials), cited by the course | 05 |
| | [bm25s](https://github.com/xhluca/bm25s): the BM25 library the M2 labs use | 03 |
| | [LlamaIndex](https://docs.llamaindex.ai/), [Haystack](https://docs.haystack.deepset.ai/): RAG frameworks; not used by any note, listed as alternatives to hand-rolled pipelines | — |
| | [Docling](https://github.com/docling-project/docling): PDF and Office parsing into structured chunks; the open alternative to the parser tiers in 01 and 12 | — |

## Papers

| | Paper | arXiv | Notes |
|---|---|---|---|
| ★ | Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (2020). [PDF](sources/2005.11401v4.pdf) | [2005.11401](https://arxiv.org/abs/2005.11401) | 02 |
| ★ | Gao et al., *Retrieval-Augmented Generation for Large Language Models: A Survey* (2023): naive / advanced / modular RAG. [PDF](sources/2312.10997v5.pdf); figures `gao-rag-survey-fig*` | [2312.10997](https://arxiv.org/abs/2312.10997) | 01 |
| ★ | Es et al., *RAGAS: Automated Evaluation of Retrieval Augmented Generation* (2023). [PDF](sources/2309.15217v2.pdf) | [2309.15217](https://arxiv.org/abs/2309.15217) | 06, 07, 08 |
| | Saad-Falcon et al., *ARES: An Automated Evaluation Framework for RAG Systems* (2023). [PDF](sources/2311.09476v2.pdf) | [2311.09476](https://arxiv.org/abs/2311.09476) | *queued* (pairs with 07's evaluation section) |
| ★ | Asai et al., *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection* (2023): a trained model emits reflection tokens to decide when to retrieve and to critique passages. Corrects the catalogue's use of the name in 01. [PDF](sources/2310.11511v1.pdf) | [2310.11511](https://arxiv.org/abs/2310.11511) | 01 |
| | Gao et al., *Precise Zero-Shot Dense Retrieval without Relevance Labels* (HyDE, 2022) | [2212.10496](https://arxiv.org/abs/2212.10496) | 01, 05, 11 |
| | Khattab & Zaharia, *ColBERT* (2020) | [2004.12832](https://arxiv.org/abs/2004.12832) | 05 |
| | Sarthi et al., *RAPTOR* (2024) | [2401.18059](https://arxiv.org/abs/2401.18059) | 01 |
| | Edge et al., *From Local to Global: A Graph RAG Approach* (GraphRAG, 2024). Depth in [05-graph 11](../../ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher.md) | [2404.16130](https://arxiv.org/abs/2404.16130) | 01 |
| | Gao et al., *Enabling LLMs to Generate Text with Citations* (ALCE, 2023) | [2305.14627](https://arxiv.org/abs/2305.14627) | 06 |
| | Malkov & Yashunin, *Efficient and robust ANN search using HNSW graphs* (2016) | [1603.09320](https://arxiv.org/abs/1603.09320) | 04, 09 |
| | Qu et al., *Is Semantic Chunking Worth the Computational Cost?* (Findings of NAACL 2025). [PDF](sources/2025.findings-naacl.114.pdf) | [2410.13070](https://arxiv.org/abs/2410.13070) | [05](notes/05-chunking-query-parsing-and-reranking.md#strategies) |
| | Jimeno Yepes et al., *Financial Report Chunking for Effective RAG* (2024). [PDF](sources/2402.05131v3.pdf) | [2402.05131](https://arxiv.org/abs/2402.05131) | [05](notes/05-chunking-query-parsing-and-reranking.md#strategies) |
| | Wang et al., *Searching for Best Practices in RAG* (2024). [PDF](sources/2407.01219v1.pdf) | [2407.01219](https://arxiv.org/abs/2407.01219) | [05](notes/05-chunking-query-parsing-and-reranking.md#rules-of-thumb) |
| | Jiang et al., *Active Retrieval Augmented Generation* (FLARE, EMNLP 2023). [PDF](sources/2023.emnlp-main.495.pdf) | [2305.06983](https://arxiv.org/abs/2305.06983) | [01](notes/01-rag-pipeline.md) |
| | Shuster et al., *Retrieval Augmentation Reduces Hallucination in Conversation* (Findings of EMNLP 2021): retrieval cuts human-rated hallucination 68% → 8–21%; more documents raise it again. [PDF](sources/2021.findings-emnlp.320.pdf) | [2104.07567](https://arxiv.org/abs/2104.07567) | [02](notes/02-why-rag-and-the-augmented-prompt.md#what-rag-buys-you) |
| | Zhao et al., *Optimizing LLM Based Retrieval Augmented Generation Pipelines in the Financial Domain* (NAACL 2024 Industry Track): pseudo-helpfulness, top-k and gold-position effects. [PDF](sources/2024.naacl-industry.23.pdf) | — ([ACL Anthology](https://aclanthology.org/2024.naacl-industry.23/)) | [05](notes/05-chunking-query-parsing-and-reranking.md#reranking), [06](notes/06-generation-for-rag.md#hallucinations-and-citations) |
| | Cuconasu et al., *The Power of Noise: Redefining Retrieval for RAG Systems* (SIGIR 2024). [PDF](sources/3626772.3657834.pdf) | [2401.14887](https://arxiv.org/abs/2401.14887) | [06](notes/06-generation-for-rag.md#why-rag-works-attention) |
| | Xu et al., *Retrieval Meets Long Context Large Language Models* (ICLR 2024): 4K + retrieval ≈ 16K long context at 70B; retrieval still helps the 32K model. [PDF](sources/xu-2023-retrieval-meets-long-context-large.pdf) | [2310.03025](https://arxiv.org/abs/2310.03025) | [02](notes/02-why-rag-and-the-augmented-prompt.md#why-not-put-everything-in-the-prompt) |
| ★ | Li et al., *Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach* (Google DeepMind, 2024): long context beats RAG on quality with frontier models; Self-Route recovers it at 38–61% of the tokens. [PDF](sources/li-2024-retrieval-augmented-generation-or-long.pdf); figure `li-self-route-fig1` | [2407.16833](https://arxiv.org/abs/2407.16833) | [02](notes/02-why-rag-and-the-augmented-prompt.md#why-not-put-everything-in-the-prompt) |
| | Yu et al., *In Defense of RAG in the Era of Long-Context Language Models* (2024): order-preserving RAG; quality peaks then falls as retrieved context grows. Two datasets. [PDF](sources/yu-2024-defense-rag-era-long-context.pdf) | [2409.01666](https://arxiv.org/abs/2409.01666) | [02](notes/02-why-rag-and-the-augmented-prompt.md#why-not-put-everything-in-the-prompt) |
| | Balaguer et al., *RAG vs Fine-tuning: Pipelines, Tradeoffs, and a Case Study on Agriculture* (Microsoft, 2024): fine-tuning +6 p.p. and RAG +5 p.p., cumulative, on GPT-4. [PDF](sources/balaguer-2024-rag-vs-fine-tuning.pdf) | [2401.08406](https://arxiv.org/abs/2401.08406) | [06](notes/06-generation-for-rag.md#rag-vs-fine-tuning) |
| | Salemi & Zamani, *Evaluating Retrieval Quality in Retrieval-Augmented Generation* (eRAG, SIGIR 2024). [PDF](sources/3626772.3657957.pdf) | [2404.13781](https://arxiv.org/abs/2404.13781) | *queued* |
| | Touvron et al., *LLaMA* (2023). [PDF](sources/2302.13971v1.pdf) | [2302.13971](https://arxiv.org/abs/2302.13971) | background for 06; better homed in 01-llm-fundamentals |
| | OpenAI, *GPT-4 Technical Report* (2023). [PDF](sources/2303.08774v6.pdf) | [2303.08774](https://arxiv.org/abs/2303.08774) | background for 06; better homed in 01-llm-fundamentals |

## Secondary and vendor posts

Use these as gap-detectors, not citations of record (see [SOURCES.md](../../ai-engineering/SOURCES.md) Tier 2).

| Source | What the notes take from it | Notes |
|---|---|---|
| Towards AI, [*9 RAG architectures that save you months of dev work*](https://pub.towardsai.net/9-rag-architectures-that-save-you-months-of-dev-work-0e219eb637cb) | the nine named patterns and decision cheat-sheet | 01 |
| Weaviate, *Advanced RAG Techniques* ebook. [PDF](sources/weaviate-advanced-rag-techniques-ebook.pdf) (13.7 MB) | *queued*; overlaps 05 and 11 | — |
| Own work notes (support-agent RAG project) | vector DB choice, semantic cache, ablations, Bedrock KB, Vertex comparison, pipeline ADR | 09–14 |

---

## Source quality

| Source | Issue | Prefer |
|---|---|---|
| Towards AI "9 architectures" | Medium-style listicle; pattern names are not standard (e.g. "Self-RAG" used loosely for query generation) | Gao survey (2312.10997); Asai et al. for Self-RAG proper |
| Weaviate ebook | Vendor; examples assume Weaviate | Course M3 labs; Wang et al. best practices |
| DLAI course decks | Not kept (copyright, ~30 MB); the notes give the content | The course itself |
| Own work notes 09–14 | Single-project numbers, `confidence: medium` | Re-run on your own corpus |
| `ragas_automated_evaluation.pdf` | Byte-identical duplicate of `2309.15217v2.pdf` | `2309.15217v2.pdf` |
| `2024-naacl-industry-23.pdf`, `2025-findings-naacl-114.pdf`, `retrieval-augmentation-reduces-hallucination-conversation.pdf` | Duplicates (routed by `/readings`) of `2024.naacl-industry.23.pdf`, `2025.findings-naacl.114.pdf`, `2021.findings-emnlp.320.pdf` | Keep one copy each |
| `cuconasu-2024-power-noise.pdf`, `jiang-2023-active-retrieval-augmented-generation.pdf` | Second copies (arXiv builds, routed later) of `3626772.3657834.pdf` (SIGIR) and `2023.emnlp-main.495.pdf` (EMNLP) | The venue PDFs |
| `2011.00564v1.pdf` (Louvan & Magnini, slot filling survey) | Off-topic for RAG; identical to 07's `louvan-2020-recent-neural-methods-slot-filling.pdf` | 07's copy |
| `conversational-ai.pdf` (Fu et al., AI Open 2022, CC BY-NC-ND) | Dialogue-systems survey; 07 also holds two copies | 07 |
| `1901.07694v1.pdf` (Dodge et al., explanations and fairness), `rethinking-batch-norm.pdf` (Wu & Johnson) | Off-topic for RAG | Re-route with `/readings triage` |
