---
origin: notion-export + ai-engineering/02-context-engineering/notes/04-retrieval.md (pipeline material moved here)
confidence: medium
sources:
  - https://arxiv.org/abs/2312.10997
  - https://pub.towardsai.net/9-rag-architectures-that-save-you-months-of-dev-work-0e219eb637cb
  - https://martinfowler.com/articles/reliable-llm-bayer.html
  - https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter3.md
  - https://arxiv.org/abs/2310.11511
  - https://arxiv.org/abs/2305.06983
  - Huyen, *AI Engineering* (O'Reilly, 2025), ch. 6
  - Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 6
  - Iusztin & Labonne, *LLM Engineer's Handbook* (Packt, 2024), ch. 4, ch. 9
  - Oshin & Campos, *Learning LangChain* (O'Reilly, 2025), ch. 2, ch. 3
  - Rothman, *Context Engineering for Multi-Agent Systems* (Packt, 2025), ch. 3
cleaned: 2026-10-31
---

# 1 — The RAG pipeline

Retrieval-augmented generation fetches relevant documents at inference time, puts them in the prompt, and lets the model answer from them. This note covers the **mechanics**: architectures, the pipeline stages, chunking, hybrid search, worked production pipelines, index-time structures, agentic and conversational RAG, and what to measure.

The context-engineering view, where retrieval is one lever among several (when to retrieve rather than cache or load everything, how much, where results land in the window), is in [02-context 04 — retrieval](../../../ai-engineering/02-context-engineering/notes/04-retrieval.md). Read that first if you're deciding *whether* to build a pipeline.

![The RAG process: documents are chunked and embedded at index time; at query time relevant chunks are retrieved and combined with the question in the prompt](../sources/images/gao-rag-survey-fig2.png)
*Image Source: Gao et al. (2024), [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997), Figure 2 ([PDF](../sources/2312.10997v5.pdf))*

---

## Architectures

### Naive, advanced, modular

The Gao et al. survey arranges RAG as three paradigms. **Naive RAG** is index → retrieve → read. **Advanced RAG** adds a pre-retrieval stage (query routing, rewriting, expansion) and a post-retrieval stage (rerank, summarise, fuse). **Modular RAG** treats each stage as a swappable module (search, routing, predict, memory, fusion, demonstrate) and composes them into patterns: rewrite → retrieve → rerank → read, or iterative retrieve ↔ read loops (ITER-RETGEN).

![Three RAG paradigms: Naive RAG (index, retrieve, prompt a frozen LLM); Advanced RAG with pre-retrieval and post-retrieval stages; Modular RAG with swappable modules and patterns](../sources/images/gao-rag-survey-fig3.png)
*Image Source: Gao et al. (2024), [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997), Figure 3*

The same progression in practice, each step adding control at the cost of latency and complexity:

| Architecture | Shape | Use when |
|---|---|---|
| **Naive RAG** | Embed query → top-k → stuff into prompt | One-hop factual questions over a clean corpus |
| **Modular RAG** | Swappable stages: query rewrite → retrieve → rerank → compress → generate | You need to tune or replace one stage without rebuilding the rest |
| **Agentic RAG** | The model decides *whether*, *what* and *when* to retrieve, and loops until it has enough | Multi-step questions ([below](#agentic-rag)) |
| **Graph-enhanced RAG** | Entities and relations extracted into a graph; retrieval walks edges | Multi-hop and "how is X related to Y" questions ([05-graph](../../../ai-engineering/05-graph-engineering/README.md)) |
| **Text-to-SQL** | Generate a query against structured data instead of searching chunks | Filtering, counting, aggregation ([below](#text-to-sql-is-a-retrieval-strategy)) |

### Where naive RAG fails

Each advanced-RAG module exists to fix one failure of the naive pipeline. Raieli and Iuculano map those failures onto the step where they start (*Building AI Agents*, ch. 6):

![Naive RAG pipeline (collection, indexing, query processing, search, ranked documents, prompt, LLM, answer) with red boxes marking the failures at each step: data-type issues and scalability at collection; missing content at the index; retrieval challenges, missed top ranks and not-in-context at search; contextual hallucination, wrong format, missed extraction and incorrect specificity at the answer](../sources/images/building-ai-agents-llms-rag-kgs-fig6-1.png)
*Image Source: Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), Fig. 6.1*

| Step | Failure | What it looks like |
|---|---|---|
| Collection and indexing | Data-type issues, missing content | One chunker applied to PDFs, HTML and tables alike; the answer was never indexed, or the index is stale |
| Search | Missed top ranks | The answer chunk exists but ranks below k. Often the embedder is too small or was trained on another domain |
| Context | Not in context | Retrieval found every relevant chunk, but too many to fit the window |
| Generation | Failed extraction | The answer is in the prompt, but noise or conflicting chunks hide it (*contextual hallucination*, [06](06-generation-for-rag.md#hallucinations-and-citations)) |
| Generation | Wrong format, incorrect specificity, incomplete | A table was asked for and prose came back; too general or too detailed; only part of a multi-part answer |
| System | Redundancy, scale, flexibility | Near-duplicate chunks crowd out others; latency grows with volume; one component can't be swapped |

Work out which row you are in before adding a module. A reranker fixes missed top ranks; it does nothing for missing content.

### Nine named patterns

A popular catalogue ([Towards AI](https://pub.towardsai.net/9-rag-architectures-that-save-you-months-of-dev-work-0e219eb637cb)) names nine variants. Start with standard RAG as the baseline, prototype **one** additional pattern for your main failure, and A/B test it.

| # | Pattern | Shape | When | Production tip |
|---|---|---|---|---|
| 1 | **Standard** | Retrieve top-k → inject → generate | Baseline | — |
| 2 | **Conversational** | Standard + dialogue state and query condensation | Chat | See [conversational RAG](#conversational-multi-turn-rag) |
| 3 | **Corrective (CRAG)** | Generate → extract claims → retrieve evidence → verify and rewrite | Accuracy-critical | Fewer factual errors, evidence-backed answers; higher latency and cost. Build a robust claim extractor (rules + NER) and track claim-level precision |
| 4 | **Adaptive** | Intent classifier → pipeline. Fast path: low-k, cached or templated answers. Deep path: high-k, multi-hop or iterative retrieval | Mixed workloads (FAQs, research, creative) | Keep the intent model small and cheap; make routing rules auditable. Speed for simple queries, depth where it matters |
| 5 | **Query generation** (the catalogue calls it "Self-RAG"; see below) | The LLM writes query expansions or keywords used for retrieval | Vague inputs; paraphrase-heavy domains | Validate or constrain generated queries so the model can't invent out-of-scope terms |
| 6 | **Fusion** | Vector search + web API + SQL → merge and rerank → synthesise with provenance labels | Enterprise: internal docs + web + DBs | Use it when breadth of sources matters |
| 7 | **HyDE** | An LLM writes a *hypothetical answer*; that answer, not the raw question, is embedded and searched. Variant: generate Q/A pairs per document at index time and index those | Short or vague queries; dense technical docs | Costs an extra LLM call but often much better recall. Regenerate index-time entries when models or documents change |
| 8 | **Agentic** | Planner → retriever-as-tool → executor → verifier, spawning sub-queries | Multi-step automation, research agents | Sandbox tool execution; step-level rollbacks. Moves you from Q&A to action |
| 9 | **GraphRAG** | Retrieve passages → entity-link to graph nodes → traverse for multi-hop → synthesise and show the path | Biotech, legal, research: provenance-critical | Invest in entity linking and a provenance UI |

**Quick decision cheat-sheet:** accuracy-critical → CRAG or GraphRAG. Conversational → conversational RAG + condensation. Mixed workload → adaptive or fusion. Paraphrase-heavy or sparse docs → HyDE or query generation. Automation → agentic.

The catalogue's "Self-RAG" label is wrong. **Self-RAG proper** ([arXiv:2310.11511](https://arxiv.org/abs/2310.11511), Asai et al., 2023-10) is a trained model, not a query-rewriting prompt. Llama 2 is fine-tuned on 150k examples to emit *reflection tokens*. These tokens decide whether to retrieve at all and grade each passage for relevance. They also check whether the passage supports the generated sentence and how useful the answer is. A GPT-4-distilled critic inserts the tokens offline, so no critic runs at inference. At 13B it beat retrieval-augmented Llama2-chat 13B on PopQA, TriviaQA, PubHealth, ARC and biography factuality, but not on ASQA exact match. On ASQA citation precision it beat retrieval-augmented ChatGPT (70.3 vs 65.1 at 13B). It belongs with **adaptive** (#4), except the model makes the routing decision itself. **FLARE** ([arXiv:2305.06983](https://arxiv.org/abs/2305.06983), Jiang et al., 2023-05) gets adaptive retrieval without training. It drafts the next sentence, and if any token falls below a confidence threshold, it uses the draft as the query and regenerates the sentence. On 2WikiMultihopQA with text-davinci-003 it reached 51.0 EM, against 39.4 for retrieving once and 47.8 for question decomposition. The authors report no significant gain on Wizard of Wikipedia or ELI5, where short or open-ended answers leave little to look ahead to. Every triggered retrieval also adds a generation pass.

---

## The pre-retrieval pipeline

When you retrieve up front, the operations compose in this order. Each stage narrows the candidate set, so cheap filters go first.

```
User Query
      ↓
Metadata Filtering       <- cheapest; drop by permission, date, source, tenant
      ↓
Vector Search            <- semantic top-k over what survived
      ↓
Context Ranking          <- rerank with a cross-encoder; send only top of rerank
      ↓
Deduplication            <- collapse near-identical chunks
      ↓
Compression              <- reduce each doc to what answers *this* query
      ↓
Memory Injection         <- add cross-session facts
      ↓
Structured Formatting    <- tag and delimit; never dump raw text
      ↓
LLM
```

Stage notes:

- **Metadata filtering first.** Permission checks and freshness filters are near-free compared with embedding search, and dropping candidates early makes every later stage cheaper. Push the filter *into* the vector query rather than applying it to the results (see the funnel in [PRINCE](#a-tuned-pipeline-bayers-prince)). Permission filtering here is a security control, not just an optimisation.
- **Ranking ≠ retrieval.** Bi-encoder vector search is fast and approximate; a cross-encoder reranker is slow and accurate. Retrieve wide, rerank, send narrow: order-of-magnitude k=50→5, though real numbers are corpus-specific.
- **Deduplication has a trap.** A chunk retrieved by several sub-queries is often the *most* relevant one, not redundant noise. Collapse duplicates but treat multi-retrieval as a positive ranking signal.
- **Compression is query-conditional.** Reduce each document to the part that answers the current question, not a generic summary, which discards the specific detail the query needed.
- **Structured formatting.** Wrap in tags with source attribution so the model can cite, and so injected content stays distinguishable from instructions ([framing](../../../ai-engineering/02-context-engineering/notes/04-retrieval.md#framing-retrieved-content)).

Iusztin and Labonne sort the same operations into three stages (*LLM Engineer's Handbook*, ch. 4):

- **Pre-retrieval** works on the data (sliding-window chunks, small-to-big, richer metadata) and on the query (routing, rewriting, HyDE, self-query).
- **Retrieval** improves the search itself: hybrid weighting, filtered vector search, or an *instructor* embedder that takes a domain instruction alongside the text.
- **Post-retrieval** trims what came back: prompt compression and cross-encoder reranking.

![The LLM Twin RAG layout: an ingestion pipeline (clean, chunk, embed) marked as pre-retrieval, a vector DB holding embedded chunks with metadata, a query embedded the same way for retrieval, and the K retrieved chunks passing a post-retrieval step into the prompt with the template and user input](../sources/images/llm-engineers-handbook-fig4-5.png)
*Image Source: Iusztin & Labonne, *LLM Engineer's Handbook* (Packt, 2024), Fig. 4.5*

One rule from the same chapter sits under all three stages. Preprocess the query exactly as you preprocessed the documents: the same cleaning and the same embedding model. Any mismatch is *training–serving skew*, and retrieval degrades without raising an error.

---

## Ingestion determines the ceiling

Retrieval can only return what parsing extracted. Parser capability comes in tiers:

![Three parser tiers: text-only extraction; text plus image descriptions, audio transcription and video summarisation; and visually rich document handling](../sources/images/aws-bedrock-kb-parser-tiers.png)
*Image Source: AWS Bedrock Knowledge Bases, parsing options (console screenshot)*

A tier-one parser over a PDF-heavy corpus silently turns every chart, diagram and table into nothing or garbled text. The retrieval layer then looks broken (low recall, irrelevant chunks) when the failure happened at ingestion. Check what the parser produced before tuning k, rerankers or chunk size.

**Multimodal ingestion.** Non-text content (charts, PDF layout, audio) enters here, and the path sets the ceiling. **Native multimodal** keeps layout and charts but costs the most. **Extract-to-text** (OCR, transcription) is cheap and cacheable, but anything visual is lost. **Extract plus an analysis tool** (`analyze_image`, `analyze_pdf`) answers most questions from the text and goes back to the original only when needed (Li, ch. 3; lab: upstream [multimodal-agent](https://github.com/bojieli/ai-agent-book/tree/main/chapter4/multimodal-agent)).

### Keeping the index in sync

The source changes after the first load. If re-ingestion is naive, the index either duplicates chunks or keeps ones whose source was deleted.

**Batch first.** The Handbook's advice is to start with a scheduled batch pipeline and move to streaming only when freshness demands it. A batch run every minute is fine for thousands of records (*LLM Engineer's Handbook*, ch. 4). To find what changed, it lists the *change data capture* (CDC) options:

| CDC method | How | Catch |
|---|---|---|
| Naive full pull | Re-read everything each run | Fine at thousands to tens of thousands of records |
| Timestamp | Pull rows with `updated_at` after the last run | Misses deletes; scans the table |
| Trigger | Database triggers write changes to an audit table | Adds write overhead to the source |
| Log-based | Read the database's transaction log | Best fidelity and no source load, but vendor-specific and needs a queue |

**Make writes idempotent.** The Handbook uses the MD5 of a chunk's content as its ID, so re-running the pipeline overwrites rather than duplicates. LangChain's indexing API goes further. A `RecordManager` stores a hash of each document's content and metadata, its write time and its source ID. On re-run it skips unchanged documents and, depending on `cleanup`, deletes stale ones (*Learning LangChain*, ch. 2):

```python
from langchain.indexes import SQLRecordManager, index

record_manager = SQLRecordManager("pgvector/my_docs", db_url=DB_URL)
record_manager.create_schema()

# cleanup=None: only add; "incremental": also delete old versions of the sources in this batch;
# "full": also delete every source NOT in this batch (pass the whole corpus, or lose data)
index(docs, record_manager, vectorstore, cleanup="incremental", source_id_key="source")
```

The book uses the 2025 `langchain` / `langchain_community` import paths. Check current docs before copying.

**Bulk deletes can be asynchronous.** Rothman's dual-RAG build clears a Pinecone namespace with `delete_all` and upserts straight after. Pinecone performs the delete in the background, so it can sweep away vectors written after the call returned. The fix is to poll the index stats until the namespace is empty before writing (*Context Engineering for MAS*, ch. 3):

```python
index.delete(delete_all=True, namespace=ns)
while index.describe_index_stats().namespaces.get(ns, {"vector_count": 0})["vector_count"] > 0:
    time.sleep(2)      # the delete is async: wait, or later upserts may be wiped
```

The Handbook also stores two snapshots of each document in its feature store: one cleaned (for fine-tuning) and one chunked and embedded (for RAG). Then a new chunking or embedding choice doesn't mean re-crawling.

---

## Chunking

| Strategy | Splits on | Trade-off |
|---|---|---|
| **Fixed-size + overlap** | Token count (e.g. 512 with 10–20% overlap) | Simple, predictable; cuts across meaning |
| **Structural** | Headings, sections, functions, table rows | Respects the document's own units; needs format-aware parsing |
| **Semantic** | Embedding-similarity breakpoints between sentences | Coherent chunks; slower ingestion, variable size |
| **Hierarchical** | Small chunks for matching, parent sections for context | Best precision *and* context; more index plumbing |

Chunk size is a recall/precision dial: small chunks match precisely but arrive without context; large chunks carry context but dilute the embedding. The hierarchical "retrieve small, return big" pattern sidesteps most of the trade-off. **Contextual retrieval** (an LLM-written prefix per chunk at index time) repairs the context a chunk loses; it's covered in [02-context 04](../../../ai-engineering/02-context-engineering/notes/04-retrieval.md#contextual-retrieval).

Fixed-size with overlap is a few lines over token ids. The stride is `size - overlap`, so a sentence cut at one boundary appears whole in the next chunk:

```python
import tiktoken

def text_to_chunks(text, size=512, overlap=64, enc=tiktoken.get_encoding("cl100k_base")):
    ids = enc.encode(text)
    chunks = []
    for start in range(0, len(ids), size - overlap):   # stride = size - overlap
        window = ids[start:start + size]
        if window:
            chunks.append(enc.decode(window))
    return chunks
```

Adapted from the DAIR prompt-engineering course's `04_rag_recipes.py`, which defaults to 1,000 tokens with 200 overlap and to `gpt-3.5-turbo` and `text-embedding-ada-002`. **Both models are legacy**; swap in a current embedding model.

Token windows ignore structure. The Handbook's version splits on paragraphs first, then caps each piece at the embedder's own input limit, using the embedder's tokenizer (*LLM Engineer's Handbook*, ch. 4):

```python
from langchain.text_splitter import (RecursiveCharacterTextSplitter,
                                     SentenceTransformersTokenTextSplitter)

def chunk_text(text, model_id, max_tokens, chunk_overlap=50):
    paragraphs = RecursiveCharacterTextSplitter(separators=["\n\n"], chunk_size=500,
                                                chunk_overlap=0).split_text(text)
    by_tokens = SentenceTransformersTokenTextSplitter(       # the embedder's tokenizer,
        model_name=model_id, tokens_per_chunk=max_tokens,    # so no chunk is truncated
        chunk_overlap=chunk_overlap)
    return [c for p in paragraphs for c in by_tokens.split_text(p)]
```

Counting in the embedder's tokens has a cost: switch embedders and the chunks must be rebuilt, not just re-embedded (*AI Engineering*, ch. 6). Per-chunk sizes and overlaps from the books are compared in [05 § strategies](05-chunking-query-parsing-and-reranking.md#strategies).

---

## Hybrid retrieval

![Hybrid Retrieval and Reranking Pipeline](../sources/images/li-ai-agents-in-depth-fig3-9.svg)
*Image Source: Li, [AI Agents in Depth](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter3.md) (2026), Figure 3-9: Hybrid Retrieval and Reranking Pipeline (Apache-2.0)*

Lexical search (BM25) finds exact terms: names, error codes, identifiers. Dense search finds paraphrases. Run both, fuse the rankings (reciprocal rank fusion is the common default), then rerank the fused top-n with a cross-encoder. That pipeline is the reasonable default for production retrieval.

Huyen names the two ways to combine retrievers (*AI Engineering*, ch. 6). **In sequence**: a cheap term-based retriever narrows the corpus, then vector search or a reranker reorders the survivors. **In parallel**: both run over the whole corpus and RRF merges the lists. Sequence is cheaper; parallel keeps documents that only one retriever would find.

Each stage has its own job:

- **Sparse.** BM25's `k1` saturates term frequency, so the 20th mention adds little. `b` normalises for document length. Rare terms dominate through IDF. *Learned sparse* models (SPLADE, BGE-M3's sparse head) learn the term weights and can add related terms that aren't in the text, while staying sparse and inspectable. Worked example below: [BM25 from scratch](#bm25-from-scratch).
- **Dense.** Cosine similarity compares direction, not magnitude, so length doesn't count. Contextual encoders (BERT, BGE-M3) give "bank" a different vector in each sentence; Word2Vec gave it one. The ANN index choice (HNSW for live corpora, ANNOY for static ones) is in [09 — vector database comparison](09-vector-database-comparison.md#ann-index-types-hnsw-vs-annoy). Lab: upstream [3-4 dense-embedding](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/dense-embedding).
- **Fusion.** Dense scores (roughly 0–1) and BM25 scores (0 to tens) aren't on the same scale. RRF (`Σ 1/(60 + rank)`) ignores scores and fuses ranks: robust, but it throws signal away. Normalise-and-weight keeps the scores but is hard to tune.
- **Rerank.** A cross-encoder reads the query and the candidate *together* (the interviewer), where the bi-encoder compares two independent vectors (the résumé screen). It's too slow to run over the corpus, so it reranks the fused top 50 or so. It refines fusion; it doesn't replace it. Lab: upstream [3-6 retrieval-pipeline](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/retrieval-pipeline) reports each document's rank before and after reranking.

Both fusions fit in a few lines. The weighted version is PRINCE's 0.7/0.3 split; it needs each score list normalised first, or BM25's larger range swamps the dense half:

```python
def rrf(rankings, k=60):                       # rankings: list of ranked doc-id lists
    scores = {}
    for ranked in rankings:
        for rank, doc in enumerate(ranked, start=1):
            scores[doc] = scores.get(doc, 0) + 1 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)

def minmax(s):                                 # {doc: score} -> scores in [0, 1]
    lo, hi = min(s.values()), max(s.values())
    return {d: (v - lo) / (hi - lo or 1) for d, v in s.items()}

def weighted(dense, sparse, w_dense=0.7):      # each: {doc: raw score}
    d, s = minmax(dense), minmax(sparse)
    fused = {doc: w_dense * d.get(doc, 0) + (1 - w_dense) * s.get(doc, 0)
             for doc in d.keys() | s.keys()}
    return sorted(fused, key=fused.get, reverse=True)
```

The DAIR course's `HybridRAG` (keyword weight 0.3, keyword score = query-term overlap) breaks off mid-method, so the combination step above was written for this note rather than copied.

### BM25 from scratch

The sparse half fits in about 40 lines of standard-library Python. For query term *t* in document *d*:

```
score(t, d) = IDF(t) · tf · (k1 + 1) / (tf + k1 · (1 − b + b · |d| / avgdl))
IDF(t)      = ln((N − df + 0.5) / (df + 0.5) + 1)
```

- **`k1` saturates term frequency.** The 20th mention adds far less than the 2nd, so a long document can't win by repetition. Typical values are 1.2–2.0.
- **`b` normalises for length.** `b=0` ignores length; `b=1` normalises fully. The usual default is 0.75.
- **The `+ 1` inside the log** is the Lucene variant. It keeps IDF positive for terms that appear in more than half the documents. Li's worked example uses the classic form without it, so his numbers come out slightly lower.

```python
import math, re
from collections import Counter

STOP = {"the", "is", "a", "an", "of", "to", "in", "and", "for", "on", "how", "what"}

def tokenize(text):
    # Keep codes like HTTP-403 whole; lowercase ordinary words; drop stop words.
    tokens = re.findall(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*", text)
    return [t if any(c.isdigit() for c in t) else t.lower()
            for t in tokens if t.lower() not in STOP]

class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(tokenize(d)) for d in docs]         # term counts per doc
        self.len = [sum(c.values()) for c in self.tf]          # |d|
        self.avgdl = sum(self.len) / len(docs)
        self.df = Counter(t for c in self.tf for t in c)       # docs containing t
        self.N = len(docs)

    def idf(self, t):
        # Lucene variant: the +1 keeps IDF positive for very common terms.
        df = self.df[t]
        return math.log((self.N - df + 0.5) / (df + 0.5) + 1)

    def term_score(self, t, i):
        tf = self.tf[i][t]
        if tf == 0:
            return 0.0
        norm = 1 - self.b + self.b * self.len[i] / self.avgdl   # length normalisation
        return self.idf(t) * tf * (self.k1 + 1) / (tf + self.k1 * norm)  # saturates in tf

    def search(self, query, k=3):
        q = tokenize(query)
        scores = [(sum(self.term_score(t, i) for t in q), i) for i in range(self.N)]
        return sorted((s for s in scores if s[0] > 0), reverse=True)[:k]

docs = [
    "Model distillation trains a small student model from a large teacher model.",
    "The model returned HTTP-403 when the API key had expired.",
    "A model card describes the model, its data and the model's limits.",
    "Forbidden errors usually mean the credentials lack permission.",
]
bm25 = BM25(docs)
for q in ["model distillation", "HTTP-403", "forbidden error"]:
    print(f"{q!r:22} ->", [(i, round(s, 2)) for s, i in bm25.search(q)])
```

```
'model distillation'   -> [(0, 1.68), (2, 0.59), (1, 0.37)]
'HTTP-403'             -> [(1, 1.24)]
'forbidden error'      -> [(3, 1.31)]
```

Three things to read off the output:

- **Rare beats frequent.** Doc 2 says "model" four times but ranks well below doc 0. "model" is in three of the four documents, so its IDF is low, and `k1` caps what repetition can add. "distillation" is in one document and carries the score.
- **Codes survive tokenisation.** `HTTP-403` stays one token and hits doc 1 exactly, which is what dense search tends to blur.
- **The blind spot.** "forbidden error" never reaches doc 1, the actual 403 incident, and it matches doc 3 on "forbidden" alone: "error" ≠ "errors", with no stemming and no synonyms. That gap is what the dense half and the reranker fill.

To build intuition, sweep `k1 ∈ {0.5, 1.2, 2.0}` and `b ∈ {0, 0.75, 1}` on a corpus with one very long document and watch its rank move. To see the sparse half of [contextual retrieval](../../../ai-engineering/02-context-engineering/notes/04-retrieval.md#contextual-retrieval), prefix a chunk with "ACME Corp 2025 Q2 financial report:" and query "ACME revenue". The fuller engine, with an inverted index, debug logging and tests, is upstream: Li, *AI Agents in Depth*, [Experiment 3-5 sparse-embedding](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/sparse-embedding) (Apache-2.0).

### Measure each stage

- **recall@k**: did a relevant document reach the top k? The metric closest to what RAG needs. Many reports, Anthropic's included, mean *hit rate*: at least one relevant document in the top k. "Retrieval failure rate" is 1 − recall@20.
- **MRR**: how high the first hit ranked.
- **nDCG**: grades the whole ranked list.

Check the definition and the k before comparing numbers across sources ([06-eval](../../../ai-engineering/06-eval/README.md)).

---

## A worked example

A first production pipeline: ingestion and indexing on the left, query and retrieval on the right.

![AWS Bedrock knowledge base pipeline: web crawl → semantic chunking → vector database, then query transformation → hybrid search → context injection → generation](../sources/images/billydk-bedrock-kb-pipeline.png)
*Image Source: Billy.dk support assistant on AWS Bedrock Knowledge Bases (author's diagram)*

Two things to note against the abstract pipeline. **Hybrid search** runs semantic and keyword retrieval together rather than choosing: vectors catch paraphrase, keywords catch exact identifiers, and each covers the other's failure mode. **Query transformation** sits before retrieval: the user's phrasing is rewritten into tool parameters, because the text a human types is rarely the text that retrieves best.

What the diagram omits is as informative: there's no reranking and no deduplication, typical of a first cut. Those are the stages teams add after retrieval quality plateaus. Configuration details: [12 — Bedrock knowledge bases](12-bedrock-knowledge-bases.md).

---

## A tuned pipeline: Bayer's PRINCE

Bayer's PRINCE platform ([Martin Fowler article](https://martinfowler.com/articles/reliable-llm-bayer.html); its verification loops in [03-harness — three kinds of reflection](../../../ai-engineering/03-harness-engineering/notes/05-verification-loops.md#three-kinds-of-reflection)) is the same pipeline after that plateau, with the numbers filled in. It retrieves over decades of preclinical study reports, and the query-time path runs:

1. **Keyword extraction and filter generation, concurrently.** One LLM pass pulls search keywords out of the question (domain terms like `piloerection`, `ataxia`); a second generates a structured metadata filter (`eq(study_id, T123456-2)`) via few-shot prompting over permutation examples.
2. **Query expansion, n=5.** A smaller, faster model rewrites the question into five semantically similar variants, covering phrasing and terminology drift.
3. **Metadata pre-filtering.** The generated filter is applied *inside* the vector database query, not after it, cutting the search space from millions of vectors to tens or hundreds before any similarity math runs.
4. **Parallel hybrid search, weighted 0.7/0.3.** Each expanded query runs its own hybrid search over the filtered space: kNN vector similarity (weight **0.7**) plus keyword search (weight **0.3**). The split was found by experiment, not derived. For a new corpus the right prior is "measure it", not "use 0.7". (OpenClaw's memory search lands on the same 70/30, [02-context 06](../../../ai-engineering/02-context-engineering/notes/06-memory.md#production-memory-designs).)
5. **Aggregate and rank, k≈20.** Union the chunks across all five searches, score each by its *highest* weighted score across the runs, keep the top ~20.
6. **Cross-encoder rerank, k=20 → 7.** A `bge-reranker-large` cross-encoder scores each candidate against the *original* question and keeps the top 7.

Three things generalise past the numbers:

- **Expansion multiplies retrieval, so the filter has to come first.** Five queries against an unfiltered corpus is five times the expensive search. Pre-filtering is what makes fan-out affordable.
- **Max-score aggregation is a dedup policy.** Taking the highest score a chunk earned, rather than summing or averaging, treats multi-retrieval as a ranking signal without letting a chunk win by appearing everywhere weakly. It's the practical answer to the deduplication trap.
- **The rerank scores against the original query.** Expansion is a recall device; the user's actual question is still the relevance target. Reranking against a rewrite would compound the rewrite's drift.

The funnel: **millions → hundreds (filter) → ~20 (hybrid + aggregate) → 7 (rerank)**. Retrieve wide, rerank hard, send narrow, with each narrowing done by a mechanism more accurate and more expensive than the last.

### The same funnel at small scale: the LLM Twin

The Handbook's retrieval module is PRINCE's shape, built over a Qdrant collection of one person's articles, posts and code (*LLM Engineer's Handbook*, ch. 9):

![LLM Twin retrieval module: the query goes to self-query (extract metadata) and query expansion (N queries); each expanded query runs a filtered vector search returning K results; the N×K results are reranked; the top K ranked chunks form the context in the prompt sent to a SageMaker LLM endpoint](../sources/images/llm-engineers-handbook-fig9-1.png)
*Image Source: Iusztin & Labonne, *LLM Engineer's Handbook* (Packt, 2024), Fig. 9.1*

1. **Self-query.** An LLM pulls the author's name out of the question; it becomes a metadata filter (`FieldCondition(key="author_id", match=MatchValue(value=...))`).
2. **Query expansion.** `gpt-4o-mini` at temperature 0 writes N=3 variants, separated by a `#next-question#` token so the output splits cleanly.
3. **Filtered vector search** per variant and per collection, in a thread pool.
4. **Merge and dedupe** the N×K results with a set.
5. **Rerank** with a small cross-encoder (`ms-marco-MiniLM-L-4-v2`) against the *original* query and keep the top K.

```python
def search(query: str, k: int = 3, expand_to_n: int = 3) -> list[Chunk]:
    author = self_query(query)                          # metadata filter, or None
    queries = expand(query, n=expand_to_n)              # includes the original
    with ThreadPoolExecutor() as pool:                  # searches are I/O-bound
        hits = pool.map(lambda q: vector_search(q, author, k), queries)
    unique = list({c.id: c for batch in hits for c in batch}.values())   # dedupe
    return rerank(query, unique, keep=k)                # score against the ORIGINAL query
```

Two details are worth copying, and one is a trap. The rerank target is the original question, the same rule PRINCE follows. Every chunk keeps its source link in metadata, so the answer can cite it. The trap: the book splits `k` across its three collections as `k // 3` and asserts `k >= 3`. With the default k=3, that is one chunk per collection, whatever the question needs.

The chapter's improvement list:

- Add chat memory: the last K messages, or a running summary plus the last K.
- Put a router in front of the collections, so most questions search one or two of the three.
- Add BM25 for hybrid search.
- Use a multi-index library (Superlinked) to weight several embeddings per item.

All four appear elsewhere in this note.

### Text-to-SQL is a retrieval strategy

Vector search over chunks is the wrong tool for questions that need precise filtering, aggregation or comparison: "give me 50 studies done on rat", or any numerical rollup. Embedding similarity doesn't count, sum or compare. PRINCE routes these to a Text-to-SQL tool, and the decisions inside it mirror the RAG path:

- **Schema subsetting.** Only the schema components relevant to the query are injected, not the full schema: pre-filtering applied to the prompt instead of the corpus.
- **Dynamic few-shot from a semantic layer.** Hand-picked (natural language → SQL) pairs live in their own vector collection. The user's query retrieves the most similar examples, which go into the prompt as in-context examples. This is retrieval used to *condition generation* rather than to supply answer content. New examples get added as failure patterns surface, and quality improves without retraining or prompt rewrites.
- **Validation over review.** Generated SQL is checked mechanically (SELECT-only; DELETE/INSERT/UPDATE blocked). An earlier LLM-review step was *removed*: it flagged valid queries as broken often enough to cost more than it saved. Deterministic validation beat model judgment on a task with a checkable answer.

Two more pieces from the books:

- **Show the model the schema and a few rows.** For each table, put its `CREATE TABLE` statement and three sample rows in the prompt; Rajkumar et al. (2022) found that format worked best (*Learning LangChain*, ch. 3). The rows show what values actually look like, such as `'NY'` vs `'New York'`.
- **Pick the table before writing SQL.** With many tables, Huyen adds a step in which the model chooses which tables are relevant. Only their schemas go into the Text-to-SQL prompt, and the query result goes to the generator alongside the question (*AI Engineering*, ch. 6).

![Tabular RAG: the question "How many units of Fruity Fedora were sold in the last 7 days?" goes to a Text-to-SQL step over a sales table; the SQL is executed, and the SQL result plus the original question go to the generative model, which writes the response](../sources/images/huyen-ai-engineering-fig6-7.png)
*Image Source: Huyen, *AI Engineering* (O'Reilly, 2025), Fig. 6-7*

**Lock the database down as well as validating the SQL** (*Learning LangChain*, ch. 3). Connect as a read-only user, expose only the tables the app needs, and set a query timeout so a generated cross-join can't stall the database. A SELECT-only check stops writes, but it doesn't stop a SELECT that reads a salary table or runs for an hour.

The same move works without SQL. The DAIR `pe-rag` notebook retrieves similar paper titles and uses them as style examples for generating new ones:

```python
import chromadb
from chromadb.utils import embedding_functions

ef = embedding_functions.SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
titles = chromadb.PersistentClient(path="./chromadb").get_or_create_collection(
    "ml_titles", embedding_function=ef)

# Index in batches; keep the URL and abstract as metadata for citing later.
for i in range(0, len(papers), 50):                 # papers: [{"Title", "PaperURL", "Abstract"}]
    batch = papers[i:i + 50]
    titles.upsert(
        ids=[str(i + j) for j in range(len(batch))],  # stable ids, so re-runs update, not duplicate
        documents=[p["Title"] or "No Title" for p in batch],
        metadatas=[{"url": p["PaperURL"], "abstract": p["Abstract"]} for p in batch])

hits = titles.query(query_texts=[user_topic], n_results=10)["documents"][0]
prompt = f"""Generate 5 titles for a paper on: {user_topic}
Mimic the style of these titles. Do not copy any of them.
<examples>
{chr(10).join(hits)}
</examples>"""
```

The examples are chosen per request, so the prompt stays short and on-topic. The notebook ran on Fireworks-hosted Llama 2 7B and Mistral 7B Instruct with Mistral's `[INST]` template. **Those models are legacy**; any current chat model works with the plain prompt above. The corpus was DAIR's ML Papers of the Week list. The original builds ids from a random hash of the title, so re-running it adds duplicates; the stable ids above fix that. Runnable original: DAIR [Prompt-Engineering-Guide `notebooks/pe-rag.ipynb`](https://github.com/dair-ai/Prompt-Engineering-Guide/blob/main/notebooks/pe-rag.ipynb).

The general shape: a retrieval layer that spans structured and unstructured data needs a **router**, not a single index. Choosing *which* retrieval mechanism to use is a decision made before any retrieval happens.

### Routing

Raieli and Iuculano list five kinds of router (*Building AI Agents*, ch. 6):

| Router | Decides by | Trade-off |
|---|---|---|
| Logical | Hand-written rules on the query or user | Predictable; brittle as queries vary |
| Keyword | Matching terms to sources | Cheap; misses paraphrase |
| Zero-shot classifier | A classifier over source labels | No training data; fixed label set |
| Function calling | The LLM picks a tool or source | Flexible; one LLM call per query |
| Semantic | Cosine similarity between the query and a description of each route | Fast after setup; needs good route descriptions |

Their banking and insurance example shows routing doing a second job. Sending a customer's question only to the indexes that customer may see is an access-control decision as well as a relevance one.

LangChain implements the last two (*Learning LangChain*, ch. 3). The *logical* version uses structured output: the model must return one of a `Literal["python_docs", "js_docs"]` set, and code maps that label to a retriever. The *semantic* version embeds one prompt template per route and picks the template closest to the query:

```python
routes = {"physics": PHYSICS_PROMPT, "math": MATH_PROMPT}
route_vecs = {name: embed(prompt) for name, prompt in routes.items()}   # once, at startup

def route(query: str) -> str:
    q = embed(query)
    return max(route_vecs, key=lambda name: cosine(q, route_vecs[name]))  # argmax similarity
```

The book's logical router matches the returned label by lowercase substring (`"python_docs" in result.datasource.lower()`). That's fine for two labels; validate against the exact set once routes multiply. The book's code imports `langchain_core.pydantic_v1`, a shim deprecated since LangChain 0.3; use plain Pydantic v2 models.

---

## Index-time structures: RAPTOR, GraphRAG, filesystems

Flat chunks fail on aggregation and rule-induction questions however good the retriever (the cats and nurse examples are in [02-context 04](../../../ai-engineering/02-context-engineering/notes/04-retrieval.md#distill-at-index-time-beyond-flat-chunks)). The fix is to spend LLM compute at index time and store structure:

| Structure | How it's built | Answers | Notes |
|---|---|---|---|
| **RAPTOR** | Cluster leaf chunks, summarise each cluster as a parent, recurse to a root | "Drill down from a concept to the details" | Retrieval works at any level of abstraction |
| **GraphRAG** | LLM-extracted entities and relations, then community detection and summaries | Multi-hop ("my doctor's hospital's address") and disambiguation (two Dr. Zhangs are two nodes) | Converting to triples loses meaning: "if it rains I'll cancel the beach and go to the museum" loses its condition. Use it as an index alongside natural-language text, not instead of it ([05-graph 11](../../../ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher.md)) |
| **Filesystem (OpenViking)** | Every resource gets L0 (~100-token abstract), L1 (~2k-token overview) and L2 (full text), with `.abstract`/`.overview` per directory | Navigation: most queries resolve at L1 | Progressive disclosure for a corpus. Needs **cross-links between files**, wiki-style, plus index pages. Weaker models append orphan files unless the writing prompt requires them to link and update the index |
| **Knowledge discovery** | Extract a schema per case (bottom-up factor discovery), encode it, cluster into prototypes, rank the factors | "What decides outcomes here?" | The ranked factors also tell the agent which questions to ask, in order. Lab: upstream [3-13](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/structured-knowledge-extraction) (Chinese legal data) |

Raieli and Iuculano's *hierarchical indexing* is the two-level version of RAPTOR. Summarise each document (one or more summaries per ~10 pages or 10K tokens), search the summaries first, then search chunks only inside the documents that matched. More levels give more precise routing, but the summaries multiply and each level adds a search step. The authors warn that with too many levels the number of summaries explodes combinatorially (*Building AI Agents*, ch. 6).

### Embed one thing, return another

What gets embedded doesn't have to be what goes to the model. LangChain's `MultiVectorRetriever` embeds a summary of each document (for tables and images, a summary written by a vision model) and stores the full original in a separate docstore under the same `doc_id`. Search runs over the summaries; the model gets the original (*Learning LangChain*, ch. 2).

![Multi-representation indexing: a full document, table or image is summarised by GPT-4V; the summary is embedded into a vector store and the original goes into a docstore; a question matches the summary and the relevant full document is returned](../sources/images/learning-langchain-fig2-5.png)
*Image Source: Oshin & Campos, *Learning LangChain* (O'Reilly, 2025), Fig. 2-5*

Rothman uses the same move for *procedural* context (*Context Engineering for MAS*, ch. 3). His system keeps two namespaces in one Pinecone index:

- a *KnowledgeStore* of fact chunks;
- a *ContextLibrary* of "semantic blueprints", JSON instructions for how to write a given kind of output.

For each blueprint only its one-line description is embedded (the library card), and the JSON rides along in metadata. A Librarian agent finds the blueprint for the user's intent, a Researcher retrieves and synthesises facts, and a Writer combines the two. Facts decide what to say; the blueprint decides how to say it.

![Dual RAG: in phase 1, raw-text knowledge data is chunked and semantic blueprints are reduced to descriptions; both are embedded into separate KnowledgeStore and ContextLibrary namespaces in Pinecone. In phase 2, an orchestrator sends an intent query to a Librarian agent (blueprint) and a topic query to a Researcher agent (facts), and a Writer agent combines them into the final output](../sources/images/context-engineering-multi-agent-systems-fig3-1.png)
*Image Source: Rothman, *Context Engineering for Multi-Agent Systems* (Packt, 2025), Fig. 3.1*

The Librarian has a gap. It queries with `top_k=1` and falls back to "generate the content neutrally" if nothing comes back. With no score threshold, nearest-neighbour search always returns *something* while the namespace holds any vector. The fallback fires only on an empty namespace, and an unrelated blueprint gets applied instead. Add a similarity floor.

**When to use it:** if questions are "find the passage that says X", hybrid retrieval is enough. If they need cross-document synthesis or multi-level navigation, structured indexing is worth its large up-front LLM cost. Lab: upstream [3-8 structured-index](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/structured-index) (RAPTOR vs. GraphRAG over an Intel architecture manual).

---

## Agentic RAG

Agentic RAG's loop is ReAct applied to retrieval: *assess what's missing → plan a query → retrieve → reason → check whether the question is answered*. It's the most capable design and the hardest to evaluate, because the retrieval path differs per run ([02-context 12](../../../ai-engineering/02-context-engineering/notes/12-evaluating-context.md)). It's just-in-time retrieval ([02-context 04](../../../ai-engineering/02-context-engineering/notes/04-retrieval.md#just-in-time-context)) with a search tool. Huyen frames it from the other side: RAG is a special case of an agent whose only tool is the retriever (*AI Engineering*, ch. 6). Raieli and Iuculano name three loop shapes (*Building AI Agents*, ch. 6). *Iterative* retrieval retrieves again with what the last generation produced. *Recursive* retrieval breaks the query into sub-queries. *Adaptive* retrieval lets the model decide when to retrieve, as FLARE and Self-RAG do ([above](#nine-named-patterns)). Agent-side patterns (retrieval as a tool, planners, verifiers) are in [08 — agentic RAG (PRINCE)](08-agentic-rag-prince.md).

### Agentic vs. single-pass: Li Experiment 3-9

Li runs the two side by side on legal Q&A. A simple question ("rules on self-defense") gives the same quality either way, and the single pass is faster. A compound question (sentencing for negligent serious injury while intoxicated, with a prior theft conviction) separates them. Single-pass retrieval with the wrong first keywords misses the link. The agent searches the three sub-questions in parallel, sees that what joins them is missing (how an unrelated prior conviction affects sentencing), and runs a second, targeted round on recidivism. Use agentic RAG when questions decompose; keep the single pass for narrow ones. Lab: upstream [3-9 agentic-rag](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/agentic-rag).

### When it pays

| Use agentic RAG when | Avoid it when |
|---|---|
| Questions need multi-step reasoning | One-shot retrieval works fine |
| Several sources must be compared | Latency is critical |
| Accuracy matters more than speed | You can't afford complex operations |
| Provenance is non-negotiable | Your data quality is poor |
| Human-level analysis is expected | |

**Before shipping**, check: multiple retrieval strategies are implemented; the planner is separate from the generator; a validation step exists; every claim has traceable evidence; tool use is rate-limited; human override paths exist; metrics go beyond answer quality. Skip one and pause.

**What to measure** beyond answer quality: retrieval precision, evidence coverage per answer, self-correction rate, human override frequency, and *time-to-trust* (how quickly reviewers approve). These predict real-world reliability.

The direction of travel is multi-agent collaboration, better self-verification, and personalisation with guardrails. The catch: agentic RAG doesn't make a system smarter; it makes good systems better and bad ones dangerous. *Retrieval without judgment is noise; judgment without evidence is hallucination.*

---

## Conversational multi-turn RAG

In multi-turn settings three things change (memory-side treatment in [02-context 06](../../../ai-engineering/02-context-engineering/notes/06-memory.md#conversational-memory-the-corpus-includes-the-conversation)):

1. **The corpus includes the conversation.** Systems store and retrieve prior user messages, assistant outputs, tool results and distilled memory objects, not just the knowledge base.
2. **The challenge is continuity and intent resolution, not only relevance.** Follow-ups contain pronouns, ellipsis, references ("what about the second one?") and topic drift. Query rewriting and memory selection often matter more than the retrieval model.
3. **The agent decides when and where to retrieve.** Retrieving every turn can be wasteful or harmful. Policies like "reuse previous evidence", "retrieve only if needed" or "ask a clarifying question first" become part of the system.

### Query rewriting

Turn the context-dependent utterance into a standalone query that drives retrieval reliably. **CONQRR** trains the rewriter with reinforcement learning against a retrieval reward, so rewriting is optimised for what the retriever returns, and it works with any off-the-shelf retriever. **CANARD** and **QReCC** are the standard rewrite datasets. The limitation, emphasised since 2023–2024: a single rewritten question loses context in long dialogues, which is why systems move toward summaries and structured memory objects.

NVIDIA's [RAG blueprint](https://docs.nvidia.com/rag/latest/multiturn.html) offers two modes: **query rewriting**, recommended for accuracy, and **history concatenation** (paste the last few turns into the query), which is cheap and low-latency but drags irrelevant history into retrieval as conversations grow. That it still ships the simple mode shows how common it is.

### History-aware retrieval

Use the chat history plus the current turn to build a retrieval *plan*. Two lines of work:

- **IR pipeline** (CAsT, ORConvQA, CORAL, mtRAG). ORConvQA shows that modelling history across *all* components (retriever, reranker, reader) improves open-retrieval conversational QA: history is a retrieval and ranking signal, not just a prompt trick.
- **Agentic retrieval** (industrial). In [Azure AI Search agentic retrieval](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-overview), an LLM reads the whole thread, decomposes it into focused subqueries (which can include chat history), runs them in parallel with semantic reranking, and returns grounding data plus a query plan the downstream agent can use.

### Dual retrieval data flow

1. The query reaches the orchestration layer.
2. **Dual retrieval**: the retrieval module (static knowledge) and the memory module (history, user context) are queried together.
3. A reasoning step merges the two into one context.
4. Generation is guided by both documents and memory.
5. **Memory update**: the session summary, feedback and new facts are written back.
6. The answer goes to the user.

The memory loop diagram and the production memory designs are in [02-context 06](../../../ai-engineering/02-context-engineering/notes/06-memory.md#the-memory-loop).

### Benchmarks

Evaluation shifts from single-turn QA to later-turn performance, non-standalone questions, topic switching, unanswerable queries and clarification.

- **CAsT** (TREC Conversational Assistance Track): conversational query understanding and retrieval/reranking. Reports large headroom between automatic systems and manually resolved "oracle" rewrites, which quantifies how much context resolution matters.
- **QReCC**: open-domain conversational QA over a large web corpus; supports training and evaluating rewriting, retrieval and reading separately.
- **TopiOCQA**: open-domain conversational QA with topic switching.
- **CORAL**: conversational RAG with passage retrieval, response generation and citation labelling under topic shifts.
- **mtRAG**: human-generated multi-turn RAG across domains, weighted toward later turns, non-standalone and unanswerable questions.
- **InSCIt, OR-ShARC**: mixed-initiative; test the decision to ask a clarifying question instead of answering.

---

## Monitoring and production

**Metrics:**

- **Hallucination rate**: share of answers with at least one false claim (manual + automated).
- **Precision@k / recall@k**: retrieval quality ([above](#measure-each-stage)).
- **Latency (p95)**: critical for UX.
- **Cost per query**: tokens plus API charges.
- **User trust**: human-review pass rate or NPS.
- **Claim-level accuracy**: for CRAG systems.

**Production checklist:**

- Semantic chunking with overlap; chunk sizes within prompt-window limits.
- Cross-encoder reranker over the top-N results.
- Incremental embedding refresh for frequently updated sources.
- Caching for high-frequency and repeat queries ([10 — semantic cache](10-semantic-cache.md)).
- Token-budget enforcement, with summarisation for long contexts.
- Snapshot, backup and rebuild plan for the vector database.
- PII redaction and strict access controls for private data (permissions belong at the retrieval layer: [02-context 04](../../../ai-engineering/02-context-engineering/notes/04-retrieval.md#context-validation)).
- Human review of flagged outputs, feeding back into re-indexing or retraining.

---

## Labs

- BM25 from scratch: [worked example above](#bm25-from-scratch); full engine upstream at [Li 3-5 sparse-embedding](https://github.com/bojieli/ai-agent-book/tree/main/chapter3/sparse-embedding) (offline, standard library).
- Retrieved few-shot examples with ChromaDB: [snippet above](#text-to-sql-is-a-retrieval-strategy); notebook upstream at DAIR [`pe-rag.ipynb`](https://github.com/dair-ai/Prompt-Engineering-Guide/blob/main/notebooks/pe-rag.ipynb) (legacy models).
- Upstream *AI Agents in Depth* ch. 3 labs (need models or API keys): [ANNOY vs. HNSW, hybrid + rerank, agentic RAG, RAPTOR vs. GraphRAG](https://github.com/bojieli/ai-agent-book/tree/main/chapter3).
- DeepLearning.AI *Retrieval Augmented Generation* course: condensed into [02](02-why-rag-and-the-augmented-prompt.md)–[07](07-rag-in-production.md); the graded labs are linked upstream from each note (need the course's Weaviate/Together/Phoenix environment).

---

→ Next: [02-why-rag-and-the-augmented-prompt.md](02-why-rag-and-the-augmented-prompt.md) — the course's first-principles walk through the same pipeline, starting from why retrieval beats retraining.
