---
origin: Deeplearning.ai-RAG-main
sources:
  - https://www.deeplearning.ai/courses/retrieval-augmented-generation-rag/
  - https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG (Module 3 part 2, ungraded lab "Chunking" + Assignment 3 "Building RAG systems with a Vector Database")
  - https://github.com/FullStackRetrieval-com/RetrievalTutorials (Kamradt, "5 Levels of Text Splitting", cited by the course)
  - https://arxiv.org/abs/2402.05131
  - https://arxiv.org/abs/2407.01219
  - https://arxiv.org/abs/2410.13070
  - https://aclanthology.org/2024.naacl-industry.23/
  - Huyen, *AI Engineering* (O'Reilly, 2025), ch. 6
  - Oshin & Campos, *Learning LangChain* (O'Reilly, 2025), ch. 2, ch. 3
  - Phoenix & Taylor, *Prompt Engineering for Generative AI* (O'Reilly, 2024), ch. 5
  - Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 5, ch. 6
  - Iusztin & Labonne, *LLM Engineer's Handbook* (Packt, 2024), ch. 4, ch. 9
confidence: high
cleaned: 2026-11-01
---
# 5 — Chunking, query parsing and reranking

A Tallybook customer asks how long a refund takes. The answer is one sentence inside a 90-line page on refunds and cancellations, and the page's vector is an average of refund windows, card rules, disputes and data deletion. The search misses it, or finds it and hands the model the entire page. Even with the right chunk indexed, the question "how long will it take?" is two turns into a chat and names no subject at all, and the best match may sit at rank 14 where the model never sees it. Each of those is a different failure, and each has its own fix: what you index, what you search for, and what you keep.

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

Phoenix and Taylor name the "too large" effect: an embedding of a long, mixed chunk regresses toward the mean, drifting toward the centre of the vector space where it is moderately similar to everything (*Prompt Engineering for GenAI*, ch. 5). Huyen names the "too small" cost: halving the chunk size doubles the number of vectors to store and search, and a boundary can cut the meaning in two. Her example is "I left my wife a note", split so that the retrieved half reads "I left my wife" (*AI Engineering*, ch. 6). Her candidate units are characters (say 2,048), words (512), sentences (20) or paragraphs. Raieli and Iuculano report 100 or 256 tokens, or 500 characters, as common starting sizes (*Building AI Agents*, ch. 6).

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

**What overlap to use is a convention, not a finding.** Huyen's own example overlaps 20 characters on 2,048-character chunks, about 1% (*AI Engineering*, ch. 6). The framework examples run much higher: 200 on 1,000 characters (20%) in *Learning LangChain* (ch. 2), 50 on 500 (10%) in the *LLM Engineer's Handbook* (ch. 4), and 20 on 100 tokens in *Prompt Engineering for GenAI* (ch. 5). None of the four measures the choice. Treat the course's 10–20% as a starting point to test, and drop it if a cheaper setting retrieves as well.

**Recursive splitting in LangChain** is `RecursiveCharacterTextSplitter`. It tries separators in order (`"\n\n"`, then `"\n"`, then `" "`) and only falls to the next one when a piece is still too long. `RecursiveCharacterTextSplitter.from_language(Language.PYTHON, ...)` swaps in code-aware separators such as `class` and `def` (*Learning LangChain*, ch. 2). The Handbook's article chunker is a cruder version: split into sentences, append sentences until the next one would pass `max_length`, and keep the chunk only if it has reached `min_length` (*LLM Engineer's Handbook*, ch. 4). Its article handler sets both to 1,000 characters. With `min_length == max_length`, a chunk is kept only if it ends within a character or so of 1,000, so most chunks, and every article's tail, are silently dropped. Set the minimum well below the maximum. The same run turns 76 documents into 2,373 chunks with the generic 500/50 splitter.

**Less common chunkers** from Raieli and Iuculano (*Building AI Agents*, ch. 6):

| Chunker | How | Catch |
|---|---|---|
| Clustering (k-means on sentence embeddings) | Group sentences by topic | Loses the original order |
| Proposition | An LLM rewrites the text as atomic, self-contained statements | One LLM pass over the corpus |
| Statistical merging | Merge neighbouring sentences while a similarity statistic stays high | A threshold to tune |

Their guidelines match the course: match the chunk to the query type, respect the embedder's input limit, and evaluate on your own data.

**Contextual retrieval, the mechanics.** Huyen describes the index-time step behind context-aware chunking: an LLM writes a short context, typically 50–100 tokens, that situates the chunk in its document, and the context is prepended before embedding and BM25 indexing (*AI Engineering*, ch. 6). Her other augmentations: product descriptions with reviews, or the questions an article answers.

![Contextual retrieval: an LLM, given the whole document and one chunk, writes a short context that is prepended to the chunk before indexing](../sources/images/huyen-ai-engineering-fig6-5.png)
*Image Source: Huyen, *AI Engineering* (O'Reilly, 2025), Fig. 6-5*

**Element-based chunking** is recursive splitting taken further: a document-layout model labels each element (title, narrative text, table, list), and chunks break at element boundaries. On FinanceBench (10-K and 10-Q filings, top-10 chunks, GPT-4 generator), element-based chunking answered 53.2% of questions correctly against 48.2% for the best fixed size (512 tokens) and 35.5% for 128 tokens, on manual grading. It also indexed about half as many chunks (62,529 vs 112,155) and needed no chunk-size tuning ([arXiv:2402.05131](https://arxiv.org/abs/2402.05131), Jimeno Yepes et al., 2024-02). The setting is one domain of table-heavy, strongly structured documents, so expect less on prose.

**Semantic chunking** has the weaker evidence. A Vectara study ran fixed-size, breakpoint (the threshold method in the table) and clustering chunkers over ten retrieval sets and five evidence and answer sets, with the stella-1.5B embedder and gpt-4o-mini as generator. On the four real long-document sets, fixed-size chunks retrieved the right document best (HotpotQA F1@5 90.59 vs 87.37 for breakpoint). Evidence-retrieval F1 differed by under 2 points, and answer BERTScore by at most 0.01. Breakpoint chunking won big only on synthetic documents stitched together from unrelated short ones (NQ 63.93 vs 43.79), where topic boundaries are artificially sharp. Swapping the embedder mattered more: stella beat bge-large by 7.44% average F1 ([arXiv:2410.13070](https://arxiv.org/abs/2410.13070), Qu et al., 2024-10). The authors' own caveats: sentence embeddings without context, and no chunk-level ground truth.

## Chunking code

Start with the page from the opening, `LONG_DOC` in the practice kit. The course's lab has two chunkers. Its fixed-size chunker counts words and steps back to repeat a tail. Its mixed chunker splits on section markers and merges short fragments. The lab's corpus is Asciidoc, so it splits on `"\n=="`. Tallybook's page is Markdown, so the marker here is `"\n## "`:

```python
from ragkit import LONG_DOC

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

def mixed_chunking(source_text: str, marker: str = "\n## ") -> list[str]:
    # Variable-size: split on section markers (the lab's Asciidoc uses "\n==")...
    chunks = source_text.split(marker)
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

answer = "5 to 10 working days"
for name, chunks in [("fixed 28, no overlap", get_chunks_fixed_size_with_overlap(LONG_DOC, 28, 0.0)),
                     ("fixed 28, 20% overlap", get_chunks_fixed_size_with_overlap(LONG_DOC, 28, 0.2)),
                     ("by section", mixed_chunking(LONG_DOC))]:
    whole = sum(answer in c for c in chunks)
    print(f"{name:<22} chunks={len(chunks)}  longest={max(len(c.split()) for c in chunks):>2} words  "
          f"holds the whole answer: {whole}")
    if name == "by section":
        print("section chunk starts:", [c[:18] for c in chunks])
```

```text
fixed 28, no overlap   chunks=7  longest=28 words  holds the whole answer: 0
fixed 28, 20% overlap  chunks=7  longest=33 words  holds the whole answer: 1
by section             chunks=4  longest=49 words  holds the whole answer: 1
section chunk starts: ['# Refunds and canc', 'How refunds are pa', 'Cancelling a works', 'Disputed charges\nI']
```

At 28 words with no overlap, a chunk boundary lands inside "5 to 10 working days", so no chunk holds the answer whole. Overlap repairs that, at the cost of longer chunks. Splitting by section needs no repair, because the page's author already grouped each idea, and that is why structure is the better default when a document has it. Chunk size 28 is picked to show the failure, since any given boundary only cuts one sentence in many.

Each chunk is stored with metadata (`chapter_title`, `filename`, `chunk_index`, `chunking_strategy`) so one Weaviate collection can hold all strategies and a filter picks one.

Fixed-size with overlap is a few lines over token ids. The stride is `size - overlap`, so a sentence cut at one boundary appears whole in the next chunk:

```python
import tiktoken
from ragkit import LONG_DOC

def text_to_chunks(text, size=512, overlap=64, enc=tiktoken.get_encoding("cl100k_base")):
    ids = enc.encode(text)
    chunks = []
    for start in range(0, len(ids), size - overlap):   # stride = size - overlap
        window = ids[start:start + size]
        if window:
            chunks.append(enc.decode(window))
    return chunks

chunks = text_to_chunks(LONG_DOC, size=40, overlap=8)
print(len(chunks), "chunks. Chunk 2 starts:", repr(chunks[1][:44]))
```

```text
7 chunks. Chunk 2 starts: ' the unused months minus a 10 percent fee. M'
```

Adapted from the DAIR prompt-engineering course's `04_rag_recipes.py`, which defaults to 1,000 tokens with 200 overlap and to `gpt-3.5-turbo` and `text-embedding-ada-002`. **Both models are legacy**; swap in a current embedding model.

Token windows ignore structure. The Handbook's version splits on paragraphs first, then caps each piece at the embedder's own input limit, using the embedder's tokenizer (*LLM Engineer's Handbook*, ch. 4):

```python
from langchain_text_splitters import (RecursiveCharacterTextSplitter,
                                      SentenceTransformersTokenTextSplitter)
from ragkit import LONG_DOC

def chunk_text(text, model_id, max_tokens, chunk_overlap=50):
    paragraphs = RecursiveCharacterTextSplitter(separators=["\n\n"], chunk_size=500,
                                                chunk_overlap=0).split_text(text)
    by_tokens = SentenceTransformersTokenTextSplitter(       # the embedder's tokenizer,
        model_name=model_id, tokens_per_chunk=max_tokens,    # so no chunk is truncated
        chunk_overlap=chunk_overlap)
    return [c for p in paragraphs for c in by_tokens.split_text(p)]

chunks = chunk_text(LONG_DOC, "sentence-transformers/all-MiniLM-L6-v2", max_tokens=64, chunk_overlap=8)
print(len(chunks), "chunks; longest is", max(len(c.split()) for c in chunks), "words")
```

```text
4 chunks; longest is 54 words
```

Counting in the embedder's tokens has a cost: switch embedders and the chunks must be rebuilt, not just re-embedded (*AI Engineering*, ch. 6). Per-chunk sizes and overlaps from the books are compared in [§ strategies](#strategies).

## Index small, return large

Three ways to separate what you match on from what you hand the LLM. The general pattern, and LangChain's `MultiVectorRetriever`, are in [01 § embed one thing, return another](01-rag-pipeline.md#embed-one-thing-return-another). Raieli and Iuculano list the variants (*Building AI Agents*, ch. 6):

| Variant | Index | Return |
|---|---|---|
| **Hypothetical questions** | Questions an LLM generates for each chunk, at index time | The chunk |
| **Sentence window** | Single sentences | The sentence plus its neighbours |
| **Parent document** | Small child chunks | The parent, when more than n of the top-k children come from it |

Hypothetical questions are HyDE turned around. HyDE generates a fake answer at query time and matches it against chunks. Hypothetical questions are generated once at index time and matched against the user's question, so they add no query latency.

![Hypothetical questions versus HyDE, with an acetaminophen example: index-time generated questions matched to the query, versus a query-time hypothetical answer matched to chunks](../sources/images/building-ai-agents-llms-rag-kgs-fig6-4.png)
*Image Source: Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), Fig. 6.4*

The sentence-window variant takes a few lines. Match on single sentences, then hand back the sentence with its neighbours:

```python
import re
import numpy as np
from ragkit import LONG_DOC, embed

sentences = [s for line in LONG_DOC.splitlines() if line and not line.startswith("#")
             for s in re.split(r"(?<=[.])\s+", line)]
vectors = embed(sentences)

def sentence_window(query, window=1):
    best = int(np.argmax(vectors @ embed([query])[0]))
    return sentences[best], " ".join(sentences[max(best - window, 0): best + window + 1])

matched, returned = sentence_window("how long until the refund reaches the customer")
print("matched: ", matched)
print("returned:", returned)
```

```text
matched:  Refunds go back to the original card.
returned: Monthly plans are not refunded. Refunds go back to the original card. They reach the customer in 5 to 10 working days.
```

The search landed one sentence away from the answer. Returned alone, that sentence would tell the model nothing about timing. The window carries the neighbouring sentence with the answer in it, along with the pronoun's referent ("They" only makes sense after "Refunds go back"). The search needs the small unit for precision, and the model needs the larger one to know what it is reading.

## The experiment: Pro Git, four strategies

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

Raieli and Iuculano's HyDE variant generates several answers, five in their example, and averages their embeddings, so one odd generation doesn't steer the search (*Building AI Agents*, ch. 6).

### Query transformations

Oshin and Campos group the rewrites by how far they move from the user's words (*Learning LangChain*, ch. 3).

![Query transformation strategies arranged by how much more or less abstract they make the user's question](../sources/images/learning-langchain-fig3-5.png)
*Image Source: Oshin & Campos, *Learning LangChain* (O'Reilly, 2025), Fig. 3-5*

| Transformation | What it does | Cost |
|---|---|---|
| **Rewrite-Retrieve-Read** (Ma et al., 2023) | An LLM rewrites the question, then retrieval and answering run as usual | Two LLM calls in sequence |
| **Multi-query** | An LLM writes several versions of the question (five, from different perspectives); retrieve for each, deduplicate the union | One extra call; k × versions retrievals |
| **RAG-Fusion** | Multi-query, then merge the result lists with reciprocal rank fusion instead of a plain union | As multi-query |
| **Step-back** | Generate a more general question; retrieve for it and for the original, and give both contexts to the LLM (*Building AI Agents*, ch. 6) | One extra call |

```python
def reciprocal_rank_fusion(results: list[list], k=60):
    fused = {}
    for docs in results:                       # one ranked list per query version
        for rank, doc in enumerate(docs):
            fused[doc] = fused.get(doc, 0) + 1 / (rank + k)
    return sorted(fused, key=fused.get, reverse=True)
```

`rrf` in the practice kit is the same function. Here is why anyone pays for the extra call. BM25 on "can I get my money back" finds nothing about refunds, because no help article uses those words. The two rewrites below are written by hand and stand in for what an LLM would produce, and the same goes for the hypothetical answer in the HyDE line:

```python
from ragkit import Retriever, rrf

retriever = Retriever()
question = "can I get my money back"
versions = [question, "refund policy", "how do I get a refund for a payment"]
hypothetical = ("Refunds are available for a set number of days after payment "
                "and are returned to the original card.")

print("original:   ", retriever.sparse(question, k=3))
print("multi-query:", rrf([retriever.sparse(q, k=5) for q in versions])[:3])
print("HyDE:       ", retriever.sparse(hypothetical, k=3))
```

```text
original:    ['kb-03']
multi-query: ['kb-04', 'kb-18', 'kb-05']
HyDE:        ['kb-04', 'kb-05', 'kb-11']
```

The right documents here are `kb-04` and its stale twin `kb-05`. Either rewrite gets there, and neither knows `kb-05` is out of date, so the stale copy still needs a filter ([03](03-keyword-semantic-and-hybrid-search.md)). The block also shows HyDE's hidden gamble: the hypothetical document works because it used the word "refund". An LLM that guesses the wrong vocabulary steers the search away from the answer.

The same RRF is used for hybrid search ([03](03-keyword-semantic-and-hybrid-search.md#hybrid-search-and-reciprocal-rank-fusion)). The book's examples use `gpt-3.5-turbo` and `retriever.get_relevant_documents`; current LangChain spells the call `retriever.invoke`. Query expansion pulls in more marginal chunks, so pair it with a post-filter or a reranker (*Building AI Agents*, ch. 6).

Two rewrites from Huyen matter in chat (*AI Engineering*, ch. 6). Identity resolution: after "Who is John Doe?", "How about his wife?" needs rewriting to name John Doe's wife before retrieval. And when the rewrite can't be resolved, the rewriter should say so rather than guess. Multi-turn rewriting is covered in [§ conversational retrieval](#conversational-retrieval).

### Self-query: letting the LLM write the filter

A self-query retriever has an LLM split the question into a semantic query and a metadata filter. LangChain's `SelfQueryRetriever` takes a list of `AttributeInfo(name, description, type)` describing the filterable fields, and `enable_limit=True` lets it read "Return 2 Fantasy books" as a genre filter plus a limit of 2 (*Learning LangChain*, ch. 3; *Prompt Engineering for GenAI*, ch. 5). The descriptions are part of the prompt, so they need care. Phoenix and Taylor's example indexes books but keeps the content description "Brief summary of a movie". Nothing errors; the LLM just gets a wrong description of the corpus, which is how these slips go unnoticed. The Handbook does a narrower version by hand: an LLM extracts the author's name from the query, and the search filters on it (*LLM Engineer's Handbook*, ch. 9).

---

## Conversational retrieval

In a chat, the current message often can't be searched as written: "how long will it take?" has no subject. Three families of fixes run from cheapest to most capable, and the benchmarks below measure the turns where they differ.

### Query rewriting

Turn the context-dependent utterance into a standalone query that drives retrieval reliably. **CONQRR** trains the rewriter with reinforcement learning against a retrieval reward, so rewriting is optimised for what the retriever returns, and it works with any off-the-shelf retriever. **CANARD** and **QReCC** are the standard rewrite datasets. The limitation, emphasised since 2023–2024: a single rewritten question loses context in long dialogues, which is why systems move toward summaries and structured memory objects.

NVIDIA's [RAG blueprint](https://docs.nvidia.com/rag/latest/multiturn.html) offers two modes: **query rewriting**, recommended for accuracy, and **history concatenation** (paste the last few turns into the query), which is cheap and low-latency but drags irrelevant history into retrieval as conversations grow. That it still ships the simple mode shows how common it is.

The trade-off shows up in a three-turn chat. The rewrite is written by hand, standing in for the small LLM:

```python
from ragkit import Retriever

retriever = Retriever()
history = ["How do I rotate my API keys?", "What happens to the old key?"]
turn = "how long do I have to ask for my money back"

print("this turn only:", retriever.sparse(turn, k=3))
print("concatenated:  ", retriever.sparse(" ".join(history + [turn]), k=3))
print("rewritten:     ", retriever.sparse("refund window in days", k=3))
```

```text
this turn only: ['kb-03', 'kb-12']
concatenated:   ['kb-02', 'kb-01', 'kb-03']
rewritten:      ['kb-18', 'kb-04', 'kb-05']
```

The turn alone misses too, since "money back" isn't Tallybook's vocabulary. Concatenation returned the key articles from the earlier turns, because the topic had changed and the concatenated query hadn't. The rewrite found the refund pages.

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

MaxSim is four lines of NumPy once a model gives you token vectors. This runs a small real ColBERT model on the course's Canada example, and the first run downloads it:

```python
import numpy as np
from fastembed import LateInteractionTextEmbedding

docs = ["Toronto is in Canada.",
        "Canada is the maple syrup capital of the world.",
        "Ottawa is the capital of Canada."]
model = LateInteractionTextEmbedding("answerdotai/answerai-colbert-small-v1")
query = next(iter(model.query_embed(["What is the capital of Canada?"])))
doc_vectors = list(model.embed(docs))

def maxsim(q, d):
    return float((q @ d.T).max(axis=1).sum())        # best doc token per query token, summed

print("query shape:", query.shape)
for doc, d in sorted(zip(docs, doc_vectors), key=lambda x: -maxsim(query, x[1])):
    print(f"{maxsim(query, d):6.2f}  {d.shape}  {doc}")
```

```text
query shape: (32, 96)
 31.41  (9, 96)  Ottawa is the capital of Canada.
 31.31  (12, 96)  Canada is the maple syrup capital of the world.
 30.96  (7, 96)  Toronto is in Canada.
```

The ranking is right, and the query is padded to 32 tokens here, so the sums sit on a different scale from the course's 3.6. The shapes are the storage cost: a matrix per document in place of a single vector.

---

## Reranking

Retrieval is fast and imprecise; reranking is slow and precise. Run them in sequence:

1. **Over-retrieve** 20–50 candidates with hybrid search.
2. **Rerank** each (query, candidate) pair with a cross-encoder or an LLM scorer.
3. **Return** the best 3–10 to the LLM.

The context budget is the same as without reranking; what changes is how relevant those 5–10 documents are. A banking-QA study at JPMorgan shows why recall alone is the wrong target. With the gold passage present, answer quality fell as the list grew (top-3 > top-5 > top-20), and less so when the gold passage sat near the top. Placing the gold passage first beat placing it last. The authors conclude that retrieval can't be optimised for recall alone, so "investing in a re-ranking system ... is still necessary" ([Zhao et al., NAACL 2024 Industry](https://aclanthology.org/2024.naacl-industry.23/), 2024-06). Most of their numbers are in figures only, and they assume each answer lives in one passage. The course's toy case: "What is the capital of Canada?" retrieves "Toronto is in Canada" and "Canada is the maple syrup capital of the world" alongside "Ottawa is the capital of Canada". A bi-encoder scores them close together; the cross-encoder puts Ottawa first.

Both of those can be checked with small real models. The block below scores the three sentences each way, then adds the cross-encoder to the Tallybook retriever and scores the 20 labelled questions. The first run downloads about 150 MB:

```python
import numpy as np
from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder
from ragkit import DOC_BY_ID, Retriever, evaluate

query = "What is the capital of Canada?"
docs = ["Toronto is in Canada.",
        "Canada is the maple syrup capital of the world.",
        "Ottawa is the capital of Canada."]

bi_encoder = TextEmbedding("BAAI/bge-small-en-v1.5")
cross_encoder = TextCrossEncoder("Xenova/ms-marco-MiniLM-L-6-v2")
doc_vectors = np.array(list(bi_encoder.embed(docs)))
query_vector = next(iter(bi_encoder.embed([query])))

print("bi-encoder cosine:   ", (doc_vectors @ query_vector).round(2))
print("cross-encoder score: ", np.round(list(cross_encoder.rerank(query, docs)), 2))

retriever = Retriever()

def rerank(q, k=3, pool=10):
    ids = retriever.hybrid(q, k=pool, pool=18)
    scores = list(cross_encoder.rerank(q, [DOC_BY_ID[i].full for i in ids]))
    return [ids[i] for i in np.argsort(scores)[::-1]][:k]

for name, search in [("hybrid", lambda q, k=3: retriever.hybrid(q, k=k)), ("hybrid+rerank", rerank)]:
    print(name, {m: round(v, 3) for m, v in evaluate(search).items()})
```

```text
bi-encoder cosine:    [0.74 0.79 0.84]
cross-encoder score:  [-2.87  5.29  8.1 ]
hybrid {'recall@3': 0.95, 'mrr': 0.742, 'ndcg@3': 0.789}
hybrid+rerank {'recall@3': 0.9, 'mrr': 0.84, 'ndcg@3': 0.845}
```

The bi-encoder's three scores are close and the cross-encoder pulls them apart. On the labelled questions the reranker improves rank order, which is what it is for, and in this run it pushes one correct document out of the top 3. A general web-search model hasn't seen Tallybook's error codes, so one small corpus says little about reranking in general and a lot about why you measure on your own questions. Toy-embedder caveats from [03](03-keyword-semantic-and-hybrid-search.md) apply to the first stage.

| Reranker | Quality | Cost |
|---|---|---|
| Cross-encoder | High | Minor added latency on 20–50 pairs |
| LLM scoring (fine-tuned, outputs e.g. 0.95) | Highest | Costly; reranking only, never first stage |

Raieli and Iuculano's fuller list (*Building AI Agents*, ch. 5–6):

| Family | Examples | Trade-off |
|---|---|---|
| Cross-encoder | BGE reranker | The default |
| Multi-vector (late interaction) | jina-colbert, ColBERTv2 | Cheapest; doc vectors precomputed |
| LLM pointwise, pairwise or listwise | Prompt an LLM to score one doc, compare two, or order a list | Best quality, highest cost |
| Fine-tuned seq2seq | RankT5 | Between the two |

ColBERTv2 runs as a reranker in a few lines through RAGatouille: `RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")`, then `.rerank(query, documents, k)`.

Why rerank at all, from the Handbook: the first stage optimises for speed over a whole corpus, a reranker sees query and document together, and fewer, better chunks cut prompt cost and noise (*LLM Engineer's Handbook*, ch. 4). Oshin and Campos add that a low k is not a false economy: more documents make the app slower, and irrelevant ones push the LLM toward hallucination (*Learning LangChain*, ch. 3). Huyen notes two differences from web search. Rank position matters less, because the LLM reads all k chunks; and time is a legitimate reranking signal, for news or changing docs (*AI Engineering*, ch. 6).

Cheaper post-retrieval steps (*Building AI Agents*, ch. 6):

- Drop chunks below a score threshold, or without a required keyword, metadata value or date.
- Expand a hit with its neighbouring chunks, so a fragment arrives with its context.

Raieli and Iuculano cite Wang et al.'s pipeline sweep as recommending query classification, HyDE, reranking, repacking and summarization together, and they stress that reranking was the one stage whose removal hurt clearly. Wang's own Table 11 shows the HyDE step's price (see the rules of thumb below), so take the full combination as an upper bound on quality, not a default.

```python
# illustrative: needs a Weaviate collection with a reranker module, as in the lab
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
| Start with fixed-size or recursive chunks; test 10–20% overlap against less | Good defaults; measure before getting clever. The overlap figure is a convention: book examples range from 1% to 20%, unmeasured. Semantic chunking did not beat fixed-size on real documents in Qu et al.; a better embedder moved results more |
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

---

## Pitfalls

- **Chunking without checking what got dropped.** Symptom: tails of documents never come back. Count input and output words, and use a minimum length well below the maximum (the Handbook's 1,000/1,000 trap above).
- **Choosing a chunker from a blog post.** Symptom: weeks on semantic chunking, little movement. Qu et al. found a better embedder moved results more on real documents. Evaluate first.
- **Chunks with no metadata.** Symptom: citations can't name a section, and you can't compare two chunkers in one index. Store source, position and strategy on each chunk.
- **Pronouns in chunks.** Symptom: "They reach the customer" matches and the model can't tell what "they" means. Return a window, or prepend context at index time.
- **Concatenating chat history forever.** Symptom: answers follow the previous topic as the conversation grows. Use a rewrite and let it say "can't resolve".
- **Assuming HyDE helps.** Symptom: latency jumps and quality is flat or worse. Wang et al.'s sweep went from 1.5 s to 11.7 s per query and dropped medical QA from 0.750 to 0.460.
- **Reranking with a model trained on a different domain.** Symptom: rank order improves on some queries and correct documents fall out of the top k. Over-retrieve, measure recall after the rerank, and consider a domain-tuned model.

---

## Try it

1. In the first chunking block, set overlap to `0.5`. How many chunks does the fixed chunker make, and is that the same as without overlap? Why does the code behave that way?
2. Add `"how do I get a refund"` to the conversational block's rewrites and compare with `"refund window in days"`. Which would you prefer for this question, and how would you decide in production?
3. Your cross-encoder lifts MRR and lowers recall@3. Ship it or not? What would change your decision?

<details>
<summary>Answers</summary>

1. The same number of chunks. The loop's stride is `chunk_size`, and overlap only reaches backward from each start, so overlap adds length and not chunks. `text_to_chunks` does the opposite: its stride is `size - overlap`, so more overlap means more chunks of the same size.
2. Try it and look at where `kb-04` lands. A single query can't settle it. Decide on a labelled set of real conversations, using later turns and non-standalone questions in particular.
3. Check the top-k the generator actually reads. If the lost documents are ones the model needs, raise k or the pool, or retune the reranker. If k is 3 and recall drops on a question type you care about, don't ship it. If rank matters more (one answer shown, or citations by position) and answer-level eval improves, ship it.

</details>

---

## Interview checklist

| Question | Answer |
|---|---|
| Why chunk at all? | A whole document's vector averages its meaning, retrieval returns too much text, and embedders silently truncate past their limit. |
| What goes wrong at each extreme of chunk size? | Too large: the vector drifts toward the mean of the space. Too small: more vectors to store and a boundary can cut the meaning in two. |
| What overlap should you use? | Start at 10–20% and test it, because it is a convention. Book examples range from 1% to 20% and none measures it. |
| Does semantic chunking beat fixed-size? | Not on real long documents in Qu et al.: HotpotQA F1@5 was 90.59 fixed vs 87.37 breakpoint. Its big win came only on synthetic stitched documents, and the embedder mattered more. |
| When does element-based chunking pay? | On structured, table-heavy documents. Jimeno Yepes et al. got 53.2% vs 48.2% on FinanceBench with about half the chunks. |
| What is contextual retrieval? | An index-time LLM writes a 50–100 token context for each chunk, prepended before embedding and BM25. It adds no query latency. |
| HyDE vs hypothetical questions? | HyDE generates a fake answer at query time. Hypothetical questions are generated at index time and matched against the user's question, so they add no query latency. |
| Multi-query vs RAG-Fusion? | Both search with several versions of the question. Multi-query unions the results and RAG-Fusion merges them with RRF. |
| How do you make a chat turn searchable? | Rewrite it into a standalone query with a small LLM. Concatenating history is cheap, and it drags old topics into retrieval. |
| Bi-encoder vs cross-encoder vs ColBERT? | Bi-encoder: one vector per text, precomputable and fast. Cross-encoder: scores each pair jointly, best and slowest, so reranking only. ColBERT: per-token vectors with MaxSim, near cross-encoder quality and heavy storage. |
| Why rerank if recall is fine? | Zhao et al. found answer quality falls as the list grows even when the gold passage is present, and gold first beats gold last. Fewer and better chunks also cut cost. |
| What is the standard reranking recipe? | Over-retrieve 20–50 with hybrid search, rerank the pairs, return the best 3–10. |

---

## Next

[06 — Generation for RAG](06-generation-for-rag.md): the retriever's half is done. Now the LLM: sampling, model choice, prompts for grounded answers, citations and hallucination checks.
