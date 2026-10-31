---
origin: Deeplearning.ai-RAG-main
sources:
  - https://www.deeplearning.ai/courses/retrieval-augmented-generation-rag/
  - https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG (Module 3 part 2, ungraded lab "Chunking" + Assignment 3 "Building RAG systems with a Vector Database")
  - https://github.com/FullStackRetrieval-com/RetrievalTutorials (Kamradt, "5 Levels of Text Splitting", cited by the course)
  - https://arxiv.org/abs/2402.05131
  - https://arxiv.org/abs/2407.01219
confidence: high
cleaned: 2026-10-31
---
# 5 — Chunking, query parsing and reranking

> Three production techniques around the vector database: chunking decides what one vector stands for, query parsing turns a messy prompt into a good search query, and reranking spends extra compute on the top 20–50 hits to return the best 3–10. Bi-encoders, cross-encoders and ColBERT are the three ways to score a (query, document) pair.

---

## Chunking

### Why chunk

| Without chunking | Effect |
|---|---|
| 1,000 books → 1,000 vectors | One vector per book |
| Whole book squeezed into one vector | Meaning is *averaged*; no chapter or page stands out |
| Retrieval returns whole books | Fills the context window at once |
| Embedder token limit (512 for bge-base) | Most of the book is never embedded (note [03](03-keyword-semantic-and-hybrid-search.md)) |

Chunk size is a balance. Too large (chapters): too many topics per vector, context fills fast. Too small (words, short sentences): each chunk loses its surrounding context and relevance drops.

### Strategies

| Strategy | How | Cost | Course verdict |
|---|---|---|---|
| **Fixed size** | Every N characters or words | Trivial | Good default |
| Fixed + **overlap** | Each chunk repeats the end of the previous one | ~10–20% more storage | Fewer ideas cut in half |
| **Recursive character splitting** | Split on structure: `\n\n`, headings, `<p>`, `def` | Trivial | Good default; respects document structure |
| **Semantic** | Walk sentence by sentence; start a new chunk when cosine distance to the running chunk crosses a threshold | One embedding per sentence | Smarter boundaries, more compute; experiment |
| **LLM-based** | Prompt an LLM to split by concept | One LLM pass per doc | Performs well, getting cheaper |
| **Context-aware** | Keep any chunking, but have an LLM prepend a line of context per chunk ("context: launch announcement") | One LLM call per chunk, at index time only | Improves any strategy. A good "first improvement" |

![Fixed-size chunks of 250 characters with 25-character (10%) overlap: chunk 1 = 1–250, chunk 2 = 226–475, chunk 3 = 451–700](../sources/images/hasan-dlai-rag-chunk-overlap.png)
*Image Source: Hasan, DeepLearning.AI RAG course, Module 3*

Context-aware chunking is the same idea as Anthropic's *contextual retrieval* (2024). The house treatment, with the numbers, is in [01 § chunking](01-rag-pipeline.md#chunking) and [ai-engineering 02 — retrieval](../../../ai-engineering/02-context-engineering/notes/04-retrieval.md).

**Element-based chunking** is recursive splitting taken further: a document-layout model labels each element (title, narrative text, table, list), and chunks break at element boundaries. On FinanceBench (10-K and 10-Q filings, top-10 chunks, GPT-4 generator), element-based chunking answered 53.2% of questions correctly against 48.2% for the best fixed size (512 tokens) and 35.5% for 128 tokens, on manual grading. It also indexed about half as many chunks (62,529 vs 112,155) and needed no chunk-size tuning ([arXiv:2402.05131](https://arxiv.org/abs/2402.05131), Jimeno Yepes et al., 2024-02). The setting is one domain of table-heavy, strongly structured documents, so expect less on prose.

### Code from the chunking lab

```python
def get_chunks_fixed_size_with_overlap(text: str, chunk_size: int,
                                       overlap_fraction: float) -> list[str]:
    text_words = text.split()                        # word-level, not character-level
    overlap_int = int(chunk_size * overlap_fraction) # e.g. 100 words × 0.2 = 20
    chunks = []
    for i in range(0, len(text_words), chunk_size):
        # Step back overlap_int words so each chunk repeats the previous tail
        chunk_words = text_words[max(i - overlap_int, 0): i + chunk_size]
        chunks.append(" ".join(chunk_words))
    return chunks

def mixed_chunking(source_text: str) -> list[str]:
    # Variable-size: split on Asciidoc section markers...
    chunks = source_text.split("\n==")
    new_chunks, chunk_buffer, min_length = [], "", 25
    for chunk in chunks:
        new_buffer = chunk_buffer + chunk
        if len(new_buffer.split(" ")) < min_length:  # ...but merge fragments under 25 words
            chunk_buffer = new_buffer                # carry over to the next section
        else:
            new_chunks.append(new_buffer)
            chunk_buffer = ""
    if chunk_buffer:
        new_chunks.append(chunk_buffer)              # don't drop the tail
    return new_chunks
```

Each chunk is stored with metadata (`chapter_title`, `filename`, `chunk_index`, `chunking_strategy`) so one Weaviate collection can hold all strategies and a filter picks one.

### The experiment: Pro Git, four strategies

The lab chunks chapters of the *Pro Git* book four ways (20% overlap on the fixed ones) and runs the same queries against each, filtered by `chunking_strategy`:

| Strategy | Chunks per query sent to the LLM | "history of git" (broad) | "how to add the url of a remote repository" (specific) |
|---|---|---|---|
| `fixed_size_25` | 8 | Matches, but too little context to explain anything | **Best**: pinpoints `git remote add <shortname> <url>` |
| `fixed_size_100` | 2 | Good | Answer present, buried in more text |
| `para_chunks` | 8 | Mixed | Mixed |
| `para_chunks_min_25` | 2 | **Best**: whole coherent paragraphs | Answer present, more to read |

Lesson: the right size depends on the query. Broad questions want long chunks; specific lookups want short ones. Retrieve more short chunks and fewer long ones to keep the context budget level (8 vs 2 above).

---

## Query parsing

The prompt a user types is rarely the best search query.

| Technique | What it does | Cost |
|---|---|---|
| **LLM query rewriting** | An LLM rewrites the prompt into a clean query | One small LLM call; "benefits easily justify costs" |
| **Named entity recognition** | Tag people, places, dates, titles (GLiNER) to drive filters and targeted search | One small model call |
| **HyDE** | An LLM writes a *hypothetical answer document*; embed that instead of the prompt | One LLM call + latency |

The course's rewriting prompt for a medical knowledge base:

```text
The following prompt was submitted by a user in order to query a database of
medical articles. Rewrite it to make it better suited for querying the database
by doing the following:
- Clarify ambiguous phrases
- Use medical terminology where applicable
- Add synonyms that increase odds of finding matching documents
- Remove unnecessary or distracting information.
{user prompt}
```

| Before | After |
|---|---|
| "I was out walking my dog, a beautiful black lab named Poppy, when she raced away from me and yanked on her leash hard while I was holding it. Three days later my shoulder is still numb and my fingers are all pins and needles. What's going on?" | "Experienced a sudden, forceful pull on the shoulder, resulting in persistent shoulder numbness and finger numbness for three days. What are the potential causes or diagnoses, such as neuropathy or nerve impingement?" |

HyDE changes what is being matched: normally prompt-to-document, with HyDE document-to-document, where one side is the "perfect" document generated from the prompt.

GLiNER example: *"I read The Great Gatsby by F. Scott Fitzgerald last summer while visiting New York…"* → BOOK, PERSON, DATE, LOCATION. The DATE and LOCATION can become metadata filters.

---

## Three ways to score a query against a document

| | Bi-encoder | Cross-encoder | ColBERT |
|---|---|---|---|
| Input | Query and doc embedded **separately** | Query + doc **concatenated** | Each **token** embedded separately |
| Output | One vector each; cosine | A relevance score 0–1 | Many vectors each; MaxSim |
| Doc vectors precomputable | Yes | **No**; every pair is a forward pass | Yes |
| Quality | Good | Best | Nearly cross-encoder |
| Speed | Great (ANN) | Extremely slow at scale | Decent, near real-time |
| Storage | Minimal | Minimal | **Heavy**: one vector per token |
| Role | Default first-stage retrieval | Reranker only | First stage or reranker; growing DB support |

**ColBERT scoring (MaxSim):** for each query-token vector, find the most similar document-token vector, then sum those maxima. The course example ("Great places to eat in New York" against a NYC cuisine passage) sums to 3.6. Each query word finds its best partner, which captures interactions a single vector loses.

---

## Reranking

Retrieval is fast and imprecise; reranking is slow and precise. Run them in sequence:

1. **Over-retrieve** 20–50 candidates with hybrid search.
2. **Rerank** each (query, candidate) pair with a cross-encoder or an LLM scorer.
3. **Return** the best 3–10 to the LLM.

The context budget is the same as without reranking; what changes is how relevant those 5–10 documents are. The course's toy case: "What is the capital of Canada?" retrieves "Toronto is in Canada" and "Canada is the maple syrup capital of the world" alongside "Ottawa is the capital of Canada". A bi-encoder scores them close together; the cross-encoder puts Ottawa first.

| Reranker | Quality | Cost |
|---|---|---|
| Cross-encoder | High | Minor added latency on 20–50 pairs |
| LLM scoring (fine-tuned, outputs e.g. 0.95) | Highest | Costly; reranking only, never first stage |

```python
from weaviate.classes.query import Rerank

def semantic_search_with_reranking(query, rerank_property, collection,
                                   rerank_query=None, top_k=5):
    if rerank_query is None:
        rerank_query = query                  # default: rerank on the same question
    reranker = Rerank(query=rerank_query,     # can differ from the retrieval query
                      prop=rerank_property)   # which property the cross-encoder reads
    response = collection.query.near_text(query=query, limit=top_k, rerank=reranker)
    return [x.properties for x in response.objects]

# Assignment 3 (BBC news chunks): "Tell me about the conflicts in Latin America"
semantic_search_with_reranking("Tell me about the conflicts in Latin America",
                               rerank_property="chunk", collection=collection, top_k=2)
# → "Spain-Argentina row over drug-use accusation",
#   "Protests across Venezuela as election dispute goes on"
```

Assignment 3 rebuilds Assignment 1's news RAG on Weaviate: `filter_by_metadata`, `semantic_search_retrieve`, `bm25_retrieve`, `hybrid_retrieve`, `semantic_search_with_reranking`, then a `generate_final_prompt(query, top_k, retrieve_function, rerank_query, rerank_property, use_rerank, use_rag)` that takes any of them as a parameter.

The house version of the reranking stage, with production numbers, is note [08 — PRINCE](08-agentic-rag-prince.md) and [11 — retrieval improvements](11-retrieval-improvements.md).

---

## Rules of thumb

| Rule | Why |
|---|---|
| Start with fixed-size or recursive chunks, 10–20% overlap | Good defaults; measure before getting clever |
| Try context-aware chunking first when recall is low | Index-time cost only; no query latency |
| Size `top_k` to chunk size | Many small or few large, same token budget |
| Rewrite queries with a small LLM | Cheap, large gains on conversational prompts |
| Over-retrieve 20–50, rerank to 3–10 | Cross-encoders are affordable on a short list |
| Treat HyDE as an experiment | Helps on some corpora; always adds latency. In one full-pipeline sweep, adding HyDE to hybrid search moved the average score 0.477 → 0.478, raised open-domain QA EM 0.347 → 0.393, dropped medical QA 0.750 → 0.460, and took latency from 1.5 s to 11.7 s per query ([arXiv:2407.01219](https://arxiv.org/abs/2407.01219), Wang et al., 2024-07, Table 11) |

---

## Labs

| Lab | Label |
|---|---|
| M3 ungraded lab "Chunking" ([upstream](https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG)) | needs embedded Weaviate + local inference server, and a Together API key for the generation step; not copied |
| M3 Assignment 3 (Weaviate news RAG) | same; not copied |

→ Next: [06-generation-for-rag.md](06-generation-for-rag.md) — the retriever's half is done; now the LLM: sampling, model choice, prompts for grounded answers, citations and hallucination checks.
