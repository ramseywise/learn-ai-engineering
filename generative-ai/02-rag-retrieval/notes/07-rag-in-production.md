---
origin: Deeplearning.ai-RAG-main
sources:
  - https://www.deeplearning.ai/courses/retrieval-augmented-generation-rag/
  - https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG (Module 5, "RAG Systems in Production" + ungraded lab "Tracing a RAG system" + Assignment 5 "Improving a RAG System")
  - https://docs.arize.com/phoenix (Arize Phoenix, used by the labs)
  - Huyen, *AI Engineering* (O'Reilly, 2025), ch. 6
  - Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 5, ch. 6
  - Rothman, *Context Engineering for Multi-Agent Systems* (Packt, 2025), ch. 7
  - Iusztin & Labonne, *LLM Engineer's Handbook* (Packt, 2024), ch. 4
  - Phoenix & Taylor, *Prompt Engineering for Generative AI* (O'Reilly, 2024), ch. 5
confidence: high
cleaned: 2026-10-31
---
# 7 — RAG in production

> A RAG system that works on a laptop meets scale, odd prompts, messy data and privacy rules in production. The course's answer: evaluate each component as well as the whole, trace every request (Phoenix + OpenTelemetry), build custom datasets from real traffic, then trade quality against cost and latency with quantization, smaller prompts and caching, and lock down the knowledge base.

---

## What changes in production

| Challenge | Example |
|---|---|
| Scale | Throughput, memory for millions of vectors, cost per query |
| Unpredictable prompts | Users ask things nobody designed for: "How many rocks should I eat?" (Google's "eat rocks" AI-search case) |
| Messy data | Fragmented, missing metadata, locked in images, PDFs and slide decks |
| Privacy and security | Private knowledge bases that must not leak |
| Real consequences | Airline chatbots have offered customers fake discounts; malicious users probe for free products or secrets |

---

## Evaluation: scope × evaluator

| Evaluator → / Scope ↓ | Code | LLM-as-judge | Human |
|---|---|---|---|
| **Component** (retriever, router, reranker) | Recall@k, precision, router accuracy | Context relevance, RAGAS faithfulness | Labelled relevance judgements |
| **System** (end to end) | Latency, cost, error rate | Response quality, citation quality | Thumbs up/down, annotation, A/B tests |

Code checks are cheap and run on everything; LLM judges cover what code can't; humans calibrate both. Note [01 § measure each stage](01-rag-pipeline.md#measure-each-stage) gives the house checklist; [06-observability](../../06-observability/README.md) covers the tooling across all LLM systems.

---

## Tracing with Phoenix

A trace is the tree of **spans** for one request: retrieval, formatting, prompt building, generation, each with inputs, outputs, attributes and latency. Phoenix (Arize) is an OpenTelemetry-based backend that renders them and adds experiments on top.

| What a Phoenix trace shows | Why you want it |
|---|---|
| User prompt and rewritten query | Did query parsing help or mangle it? |
| Retrieved chunks, in order, with scores | Was the answer even retrieved? |
| Reranker output | Did reranking promote the right one? |
| Final prompt sent to the LLM | Exactly what the model saw |
| Response, token counts, latency per span | Where time and money go |

### Plain OpenTelemetry first

```python
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": "rag"})))
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
tracer = trace.get_tracer(__name__)

def retrieve(query, fail=False):
    with tracer.start_as_current_span("retrieving_documents") as span:   # one span per step
        span.set_attribute("input.query", query)
        try:
            docs = ...                                                   # the real retrieval
            for i, doc in enumerate(docs):
                # OpenInference naming: Phoenix renders these as a document list
                span.set_attribute(f"retrieval.documents.{i}.document.id", i)
                span.set_attribute(f"retrieval.documents.{i}.document.content", doc)
            return docs
        except Exception as e:
            span.set_attribute("error.type", type(e).__name__)           # failures stay visible
            span.set_attribute("error.message", str(e))
            raise
```

Nested `with` blocks (or nested function calls each opening a span) make the parent-child tree that is the trace.

### Then Phoenix

```python
from phoenix.otel import register

tracer_provider = register(
    project_name="rag-lab",
    endpoint="http://127.0.0.1:6006/v1/traces",
    auto_instrument=True,          # OpenAI-compatible calls traced automatically (Together is one)
)
tracer = tracer_provider.get_tracer(__name__)

def retrieve(query_text, limit=5):
    # openinference_span_kind tells Phoenix how to render the span
    with tracer.start_as_current_span("query_weaviate", openinference_span_kind="retriever") as span:
        span.set_input(query_text)
        results = client.collections.get("Faq").query.near_text(query=query_text, limit=limit)
        for i, d in enumerate(results.objects):
            span.set_attribute(f"retrieval.documents.{i}.document.id", str(d.uuid))
            span.set_attribute(f"retrieval.documents.{i}.document.content", str(d.properties))
        return results

@tracer.chain                       # decorator = a "chain" span with inputs/outputs captured
def rag_pipeline(query):
    context = format_context(retrieve(query))
    return query_openai(create_prompt(query, context))   # auto-instrumented LLM span
```

In Assignment 5 `auto_instrument` is off (some LLM calls shouldn't be traced) and spans record `llm.token_count.prompt`, `llm.token_count.completion`, `llm.token_count.total` and `llm.model_name` by hand, with an optional cost-per-token table, so Phoenix can show spend per span.

### Beyond traces

| Phoenix feature | Use |
|---|---|
| Experiments | Run a dataset through two pipeline versions and compare scores |
| A/B tests | Same, on live traffic |
| Reports | Aggregate quality, latency and cost over time |
| The flywheel | Traces → failure cases → datasets → fixes → experiments → deploy |

---

## Custom datasets from real traffic

Public benchmarks don't know your users. Build datasets from logged prompts:

| Analysis | Example from the course | Leads to |
|---|---|---|
| Topic analysis | 58% of prompts are about *Product delays* | Make sure delay docs are indexed and fresh |
| Component metrics per topic | Context precision 42% on one topic | That topic's chunks or embeddings need work |
| Router errors | "Draw a diagram of my order" misrouted | Add it as a router few-shot example |
| Clustering | Group embedded prompts, inspect each cluster | Find categories nobody planned for |

---

## Quantization

| What | From → to | Effect |
|---|---|---|
| LLM weights | 16-bit → 8-bit or 4-bit | Less memory and faster, small quality loss |
| Embedding vectors | 32-bit float → 8-bit int | 4× smaller; store min and scale per dimension |
| Embedding vectors | → 1-bit (sign only) | **32× smaller**; retrieve with bits, rerank top hits at full precision |
| Matryoshka embeddings | Truncate to the first d dimensions | Trained so prefixes stay meaningful |

Why vector size matters:

| Model | Dimensions | Per vector (float32) | Per 1M vectors |
|---|---|---|---|
| Cohere (large) | 4096 | 16 KB | 16 GB |
| OpenAI ada-002 | 1536 | 6 KB | 6 GB |
| all-mpnet-base | 768 | 3 KB | 3 GB |

Raieli and Iuculano put a number on the binary trade-off: sign-only vectors lose quality on their own, but rescoring the retrieved candidates at higher precision keeps up to 96% of full-precision similarity. They call 1-bit extreme and suggest float32 → int8 (256 levels) as the usual compromise (*Building AI Agents*, ch. 5).

---

## Cost

| Lever | How |
|---|---|
| Smaller LLM, smaller prompts | Fewer tokens is the biggest saver |
| Lower `top_k` | Fewer chunks in every prompt |
| Dedicated endpoints | Cheaper than per-token at steady high volume |
| Tiered storage | HNSW index in RAM, vectors on disk, documents in object storage |
| Multi-tenancy | One HNSW per tenant; load on demand, or by time zone when that tenant is awake |
| Batch the embedding calls | Batching chunks through the embedder on a GPU speeds indexing by 10× or more, depending on batch size and hardware (*LLM Engineer's Handbook*, ch. 4) |

What the retrieval side costs, from the books:

- **Embedding is cheap once, expensive on repeat.** Phoenix and Taylor priced embedding the whole King James Bible (about 800,000 words, 4M tokens) at about $1.60, at ada-002's $0.0004 per 1K tokens. The price is dated; the shape isn't (*Prompt Engineering for GenAI*, ch. 5). Huyen's counterweight is churn: re-embedding 100 million documents a day is a real bill (*AI Engineering*, ch. 6).
- **The vector database is not a rounding error.** Huyen reports that it's not unusual for a company's vector-database spend to be a fifth to a half of its spend on model APIs (*AI Engineering*, ch. 6).
- **At high volume, compare against fine-tuning.** For heavy workloads, Phoenix and Taylor suggest the one-off cost of fine-tuning may beat the ongoing cost of longer prompts plus embeddings plus vector storage. Test whether the retrieved context is worth its cost and latency (*Prompt Engineering for GenAI*, ch. 5).

Assignment 5 is a cost exercise. The Fashion Forward Hub bot from note 06 gets a `simplified` mode:

```python
def query_on_faq(query, simplified=False, **kwargs):
    if not simplified:
        faq_layout = generate_faq_layout(faq)          # the WHOLE FAQ in every prompt (~1,220 tokens)
    else:
        with tracer.start_as_current_span("retrieve_faq_questions",
                                          openinference_span_kind="retriever"):
            results = faq_collection.query.near_text(query, limit=5)   # only the 5 relevant pairs
            results = [x.properties for x in results.objects]
            results.reverse()   # most relevant LAST, nearest the question in the prompt
            faq_layout = generate_faq_layout(results)  # target: under 500 tokens
    prompt = f"...<FAQ>\nRELEVANT FAQ ITEMS:\n{faq_layout}\n</FAQ>\nQuery: {query}"
    return generate_params_dict(prompt, **kwargs)
```

The router prompt gets the same treatment (under 180 tokens, same accuracy on the test set: drop examples, keep only the hard ones). Retrieval used to cut the prompt is RAG applied to the prompt itself.

---

## Latency

"Most of the latency is the transformer." Every lever reduces LLM work or skips steps:

| Lever | Detail |
|---|---|
| Router | Skip retrieval for prompts that don't need it |
| Smaller or quantized LLM | Fewer FLOPs per token |
| **Caching** | Direct cache for repeated prompts; personalised cache where a small LLM adapts a cached answer (see note [10 — semantic cache](10-semantic-cache.md)) |
| Remove components that don't pay | Measure each: reranker ~50 ms, query rewriter ~300 ms, router ~200 ms. Keep only those that move your metrics |
| Binary vectors, sharding | Faster first-stage retrieval at scale |
| Parallelism | Spark or Dask for ingestion; shard the index across nodes so each searches its part (*Building AI Agents*, ch. 6) |
| LLM router with fallbacks | Route each prompt to a suitable model, and fall back to another when an API errors (*Building AI Agents*, ch. 6) |

---

## Security

| Risk | Mitigation |
|---|---|
| Knowledge base leaks through prompts ("print your documents") | Authenticate users; retrieve only what that user may see |
| Cross-tenant leakage | Separate tenants (collections or indexes) |
| Data leaving your perimeter | On-prem or VPC deployment of DB and models |
| Vectors at rest | Chunks can be encrypted; vectors must be decrypted in memory to search |
| **Vector inversion**: text reconstructed from embeddings | Add noise, apply transforms, reduce dimensionality |

Raieli and Iuculano's threat list adds detail (*Building AI Agents*, ch. 6):

- **Embedding inversion is practical.** Studies have recovered more than 70% of the words of the original text from embeddings, without sophisticated methods. Treat vectors as sensitive as the text.
- **Knowledge poisoning.** PoisonedRAG ([arXiv:2402.07867](https://arxiv.org/abs/2402.07867)) injects a few crafted texts into the corpus so that a target question retrieves them and gets the attacker's answer.
- **Membership inference.** If a document is in the corpus, the right query retrieves it into the prompt, so outputs reveal what the corpus contains.
- **Defences.** Encryption in transit and at rest (AES-256, TLS), key rotation, user privileges, and GDPR and CCPA compliance. At the model boundary, programmable rails such as NVIDIA's NeMo Guardrails (input, output, retrieval and dialog rails, written in Colang) and classifiers such as Llama Guard, which labels prompts and responses safe or unsafe.

**Defence against poisoned documents.** Rothman builds the two-stage attack into the design (*Context Engineering for MAS*, ch. 7). First a poisoned document enters the knowledge base; later it's retrieved and its text acts as an indirect prompt injection (Greshake et al., 2023). Two defences follow:

1. **Separate ingestion from the application.** A separate ingestion pipeline, standing in for a data-management department, curates, chunks and embeds the knowledge base. The agents only read from it.
2. **Sanitise every retrieved chunk before the LLM sees it.** `helper_sanitize_input` matches each chunk against injection regexes and raises `ValueError` on a hit. The researcher agent catches it, logs it and drops the chunk.

![High-fidelity RAG and defence: a separate ingestion pipeline writes source-tagged chunks, and the research agent sanitises retrieved chunks before synthesis](../sources/images/context-engineering-multi-agent-systems-fig7-1.png)
*Image Source: Rothman, *Context Engineering for Multi-Agent Systems* (Packt, 2025), Fig. 7-1*

```python
injection_patterns = [r"ignore previous instructions", r"ignore all prior commands",
                      r"you are now in.*mode", r"act as", r"print your instructions",
                      r"sudo|apt-get|yum|pip install"]
```

Rothman calls the list basic and says it needs constant extension. It also over-blocks. `act as` matches "react as" and "interact as", and the book's own prose ("to act as a defensive gateway") would be dropped. Any technical document that mentions `pip install` is discarded too. Because a dropped chunk fails silently, the corpus loses content with no error. Use the regex as a cheap first filter, log every drop, and put a model-based classifier (Llama Guard or similar) behind it.

---

## Multimodal RAG

| Piece | How it works |
|---|---|
| Multimodal embeddings | Text and images in one vector space; a text query finds an image |
| Vision-language models | Images split into patches, each a token (100–1,000 per image) |
| PDF RAG without parsing | Embed each page image as patch vectors and score ColBERT-style (note [05](05-chunking-query-parsing-and-reranking.md)); many vectors per page |

Huyen's version of the first row uses CLIP: embed all texts and images with CLIP, embed the query, and return the nearest of both kinds (*AI Engineering*, ch. 6). Raieli and Iuculano set out the three designs (*Building AI Agents*, ch. 6):

| Strategy | How | Catch |
|---|---|---|
| **One shared space** | A CLIP-style model embeds every modality; a vision-language model generates | CLIP and multimodal LLMs cost more; the embedder must capture each modality well |
| **Ground everything in one modality** | Convert to the main one: image descriptions, audio transcripts | No new models, but conversion is costly and loses nuance |
| **Separate retrieval per modality** | One embedder and one store per modality, retrieve from each | Needs a multimodal reranker to merge the results |

The parse-or-don't decision for PDFs, and the production parsers, are in note [12 — Bedrock knowledge bases](12-bedrock-knowledge-bases.md) and [01 § chunking](01-rag-pipeline.md#chunking).

---

## Rules of thumb

| Rule | Why |
|---|---|
| Trace from day one | You can't debug a RAG answer without the retrieved chunks and final prompt |
| Evaluate components and the system | A good system score can hide a broken router |
| Build eval sets from real traffic | Users ask what you didn't plan for |
| Cut prompt tokens before changing models | Usually the cheapest win |
| Price every component in ms and $ | Remove those that don't move metrics |
| Filter by user permission at retrieval time | Prompt instructions are not access control |

---

## Labs

| Lab | Label |
|---|---|
| M5 ungraded lab "Tracing a RAG system" ([upstream](https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG)) | needs Phoenix (`arize-phoenix`, local server on :6006), embedded Weaviate, Together API key; not copied |
| M5 Assignment 5 "Improving a RAG System" | same; not copied |

This closes the course. Notes 08–14 are production write-ups that apply these ideas.

→ Next: [08-agentic-rag-prince.md](08-agentic-rag-prince.md) — a real agentic RAG stack: hybrid retrieval, reranking, routing and evaluation in one production system.
