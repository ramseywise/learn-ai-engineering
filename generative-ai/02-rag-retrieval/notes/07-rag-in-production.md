---
origin: synthesis  # was: Deeplearning.ai-RAG-main
sources:
  - https://arxiv.org/abs/2312.02724
  - https://www.deeplearning.ai/courses/retrieval-augmented-generation-rag/
  - https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG (Module 5, "RAG Systems in Production" + ungraded lab "Tracing a RAG system" + Assignment 5 "Improving a RAG System")
  - https://docs.arize.com/phoenix (Arize Phoenix, used by the labs)
  - Huyen, *AI Engineering* (O'Reilly, 2025), ch. 6
  - Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 5, ch. 6
  - Iusztin & Labonne, *LLM Engineer's Handbook* (Packt, 2024), ch. 4
  - Phoenix & Taylor, *Prompt Engineering for Generative AI* (O'Reilly, 2024), ch. 5
  - https://arxiv.org/abs/2311.09476
  - https://arxiv.org/abs/2404.13781
  - https://arxiv.org/abs/2408.01262
  - https://arxiv.org/abs/2407.21712
  - https://arxiv.org/abs/2412.02830
  - https://arxiv.org/abs/2604.15771
  - https://arxiv.org/abs/2604.26649
confidence: high
cleaned: 2026-11-01
---
# 7 — RAG in production

On a Tuesday, Tallybook's support bot tells a customer about the manual refund override, a procedure in an internal runbook that says never to share it. No test caught this, because the test questions never reached that document and nobody checked who could retrieve what. A day later someone asks why the bill doubled, and nobody can say which step spent the money, because nothing was traced. Production failures look like these more often than like a low benchmark score. They are about what you can see, what you can afford, and who can read what.

> A RAG system that works on a laptop meets scale, odd prompts, messy data and privacy rules in production. The course's answer: evaluate each component as well as the whole, trace every request (Phoenix + OpenTelemetry), build custom datasets from real traffic, then trade quality against cost and latency with quantization, smaller prompts and caching, and lock down the knowledge base. Security, rules that change by legal effect, multimodal RAG and live-index sync are in [07b](07b-security-changing-text-multimodal-and-live-indexes.md).

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

ARES formalises the "humans calibrate both" sentence. It fine-tunes lightweight judges on synthetic data for three scores (context relevance, answer faithfulness and answer relevance), then uses prediction-powered inference with a small human-labelled set to correct the judges' errors. The authors found about 150 annotated datapoints to be the minimum in their setup. Across eight tasks from KILT, SuperGLUE and AIS, it beat RAGAS by 59.3 and 14.4 percentage points on average at context-relevance and answer-relevance evaluation accuracy on the KILT and SuperGLUE sets, and came within 2.5 points of the true average answer hallucination rate on AIS ([arXiv:2311.09476](https://arxiv.org/abs/2311.09476), Saad-Falcon et al., NAACL 2024). The authors built these comparisons from mock RAG systems made by sampling known-good and known-bad outputs, so read the gap as evidence for the method more than as a forecast for your system. The practical lesson is cheap to copy: don't trust an unaudited judge's number, and keep a labelled sample to calibrate it against.

For the retriever alone, the "labelled relevance judgements" cell above is a weaker yardstick than it looks. eRAG feeds each retrieved document to the generator by itself and scores the answer against the task's ground truth, so the generator's own result becomes that document's relevance label. On KILT tasks with a T5-small Fusion-in-Decoder reader and 50 BM25 passages, Kendall's tau against end-to-end performance was about 0.30 to 0.64 for eRAG on NQ, TriviaQA, HotpotQA and FEVER with BM25 or Contriever (the range spans metrics), against 0.01 to 0.22 for KILT's human provenance labels on the same four. Having Mistral-7B label each document for relevance gave roughly zero (-0.04 to 0.19). eRAG also needed 1.2 to 3.3 times less runtime and 7 to 48 times less GPU memory than running the full pipeline ([arXiv:2404.13781](https://arxiv.org/abs/2404.13781), Salemi & Zamani, SIGIR 2024). The setup is small (60M-parameter reader, Wikipedia corpus, tasks with short answers), and correlation fell as more documents were retrieved. Treat it as a reason to check that your retrieval metric tracks answer quality, not as a replacement for recall@k.

RAGEval shows the same gap from the generation side. On its generated DragonBall set (finance, law and medical documents in Chinese and English, 50 questions per scenario and language, nine generators, BGE-M3 retrieval, top-5 chunks of 512 tokens), word-overlap scores and keypoint scores disagreed: Baichuan-2-7B-chat had the best ROUGE-L (38.30) and BLEU (21.55) in Chinese but a Completeness (share of the reference answer's 3-5 keypoints covered) of only 60.25, while GPT-4o had 79.13 Completeness and ROUGE-L 21.30. An LLM scoring keypoints differed from three human annotators by 1.67 points (Fleiss' kappa 0.77 across the annotators, on 210 questions answered by one 7B model). Retrieval recall and answer completeness moved together but not in lockstep: raising top-K from 2 to 5 lifted Completeness from 55.04 to 70.38 in Chinese, while going on to 8 added about 2 more points (72.32) though recall kept rising. The best chunk size and top-K varied with question type in the finance English slice, so a single setting tuned on average questions hides a loser. The data is synthetic, the tables show single runs with no variance, and the human check covered one 7B model's answers ([arXiv:2408.01262](https://arxiv.org/abs/2408.01262), Zhu et al., 2024, preprint).

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
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from ragkit import DOC_BY_ID, Retriever

# ConsoleSpanExporter prints the same spans as JSON. The in-memory one lets us print a short tree.
exporter = InMemorySpanExporter()
trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": "rag"})))
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))
tracer = trace.get_tracer(__name__)
retriever = Retriever()

def retrieve(query, fail=False):
    with tracer.start_as_current_span("retrieving_documents") as span:   # one span per step
        span.set_attribute("input.query", query)
        try:
            if fail:
                raise TimeoutError("vector store timed out")
            docs = retriever.hybrid(query, k=2)                          # the real retrieval
            for i, doc in enumerate(docs):
                # OpenInference naming: Phoenix renders these as a document list
                span.set_attribute(f"retrieval.documents.{i}.document.id", doc)
                span.set_attribute(f"retrieval.documents.{i}.document.content", DOC_BY_ID[doc].full)
            return docs
        except Exception as e:
            span.set_attribute("error.type", type(e).__name__)           # failures stay visible
            span.set_attribute("error.message", str(e))
            raise

def rag_pipeline(query, fail=False):
    with tracer.start_as_current_span("rag_pipeline"):
        return retrieve(query, fail=fail)

rag_pipeline("how do I rotate an API key")
try:
    rag_pipeline("how do I rotate an API key", fail=True)
except TimeoutError:
    pass

for span in exporter.get_finished_spans():
    parent = span.parent.span_id if span.parent else None
    kept = {k: v for k, v in span.attributes.items() if "content" not in k}
    print(f"{span.name:<22} child={parent is not None!s:<5} {kept}")
```

```text
retrieving_documents   child=True  {'input.query': 'how do I rotate an API key', 'retrieval.documents.0.document.id': 'kb-01', 'retrieval.documents.1.document.id': 'kb-02'}
rag_pipeline           child=False {}
retrieving_documents   child=True  {'input.query': 'how do I rotate an API key', 'error.type': 'TimeoutError', 'error.message': 'vector store timed out'}
rag_pipeline           child=False {}
```

The second trace is the reason to do this: the failed request records which step failed, and why, instead of disappearing into a generic error upstream.

Nested `with` blocks (or nested function calls each opening a span) make the parent-child tree that is the trace.

### Then Phoenix

```python
# illustrative: needs arize-phoenix on :6006, an embedded Weaviate client and `format_context`, `create_prompt`, `query_openai` from the lab
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

You can measure that trade-off on your own vectors in a few lines. Random clustered vectors stand in for embeddings here, so the recall values only show the method:

```python
import numpy as np

rng = np.random.default_rng(0)
centres = rng.normal(size=(100, 384))
docs = centres[rng.integers(100, size=50_000)] + 0.7 * rng.normal(size=(50_000, 384))
queries = centres[rng.integers(100, size=100)] + 0.7 * rng.normal(size=(100, 384))
docs = (docs / np.linalg.norm(docs, axis=1, keepdims=True)).astype("float32")
queries = (queries / np.linalg.norm(queries, axis=1, keepdims=True)).astype("float32")

def top(scores, k):
    return np.argpartition(-scores, k)[:k]

truth = [set(top(docs @ q, 10)) for q in queries]

lo, hi = docs.min(axis=0), docs.max(axis=0)          # store min and scale per dimension
scale = (hi - lo) / 255
int8_docs = np.round((docs - lo) / scale).astype("uint8")
binary_docs = np.packbits(docs > 0, axis=1)

def recall(search):
    return np.mean([len(set(search(q)) & t) / 10 for q, t in zip(queries, truth)])

def search_int8(q):
    return top((int8_docs * scale + lo) @ q, 10)

def hamming(q):
    return np.unpackbits(binary_docs ^ np.packbits(q > 0), axis=1).sum(axis=1)

def search_binary(q):
    return top(-hamming(q).astype("float32"), 10)

def search_binary_rescore(q):
    candidates = top(-hamming(q).astype("float32"), 100)
    return candidates[top(docs[candidates] @ q, 10)]

for name, size, search in [("int8", int8_docs.nbytes, search_int8),
                           ("1-bit", binary_docs.nbytes, search_binary),
                           ("1-bit + rescore top 100", binary_docs.nbytes, search_binary_rescore)]:
    print(f"{name:<24} {docs.nbytes / size:4.0f}x smaller  recall@10={recall(search):.3f}")
```

```text
int8                        4x smaller  recall@10=0.965
1-bit                      32x smaller  recall@10=0.138
1-bit + rescore top 100    32x smaller  recall@10=0.625
```

The size ratios are arithmetic. Rescoring needs the full vectors somewhere, usually on disk, so the memory saving is real and the storage saving isn't.

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
# illustrative: needs the assignment's FAQ data, Phoenix tracer, embedded Weaviate and a Together API key
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

Price it before you argue about it. The token counts below are the assignment's 1,220-token full FAQ and its 500-token target. The per-token prices and volume are assumptions, so put in your own:

```python
PRICE_IN, PRICE_OUT = 0.50 / 1e6, 1.50 / 1e6    # assumed $ per token; use your provider's
PER_DAY = 100_000                               # assumed queries per day
OUTPUT_TOKENS = 200

def daily_cost(prompt_tokens, cache_hit_rate=0.0):
    per_query = prompt_tokens * PRICE_IN + OUTPUT_TOKENS * PRICE_OUT
    return PER_DAY * (1 - cache_hit_rate) * per_query

baseline = daily_cost(1_220)
for name, cost in [("whole FAQ", baseline),
                   ("retrieved FAQ items", daily_cost(500)),
                   ("retrieved + 30% cache hits", daily_cost(500, cache_hit_rate=0.3))]:
    print(f"{name:<28} ${cost:7.2f}/day  {cost / baseline:5.0%} of baseline")
```

```text
whole FAQ                    $  91.00/day   100% of baseline
retrieved FAQ items          $  55.00/day    60% of baseline
retrieved + 30% cache hits   $  38.50/day    42% of baseline
```

Output tokens stay in the bill however small the prompt gets, which is why the prompt saving alone doesn't scale in proportion to the tokens removed.

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

The router row has a quality case as well as a speed case. RAGate trains a gate that decides per conversation turn whether to retrieve at all. On KETOD, a task-oriented dialogue set, with a GPT-2 generator and the top three snippets from a BERT ranker, retrieving on every turn (4,964 test turns) raised BLEU from 9.38 to 16.08 but cut the model's token-level confidence by 10.4%. A multi-head-attention gate that retrieved on 787 turns reached BLEU 12.14 and lost 0.36% confidence, against 1.65% for retrieving on 787 random turns. The gate itself was weak, with F1 at most 0.43 against human "needs knowledge" labels, only 12% of turns were positive, and there was no human review of the answers ([arXiv:2407.21712](https://arxiv.org/abs/2407.21712), Wang et al., 2024, preprint). It supports measuring what an always-on retrieval step costs, and does not show a gate recovers the always-on quality.

A gate can also act after retrieval fails, and pick the fix. The gate idea predates RAGate: Adaptive-RAG (Jeong et al., NAACL 2024) routes by predicted query complexity, and Probing-RAG (Baek et al., 2025) reads the model's hidden states with small probes instead of asking it. Skill-RAG keeps Probing-RAG's probes and, when an answer still looks wrong after retrieval, an LLM router chooses one of four moves: rewrite the query, decompose it, focus on the evidence already retrieved, or stop. With 7–9B open models, BM25 and probes trained on NQ, TriviaQA and HotpotQA, it beat Probing-RAG by up to **13.6 accuracy points on 2WikiMultiHopQA** (Gemma2-9B, 500 questions), but gained under 1.1 points in-domain, and on HotpotQA exact match it trailed DRAGIN (23.1 against 31.9, Llama3-8B). On 2,660 hard cases the stop move saved about 1.4 retrieval rounds per stopped query for 0.5–0.6 points of accuracy. The probes need white-box hidden states and labelled in-domain data, so they cannot gate a hosted API model. The paper counts rounds but reports no latency and does not cost the router call. Its claim that failures come in four types rests on t-SNE plots, and it never tests the router without the probes ([arXiv:2604.15771](https://arxiv.org/abs/2604.15771), Wei et al., 2026-04, preprint). The part that carries over to an API model is the routing. When retrieval misses, rewriting, decomposing and stopping each fix a different kind of failure, so log which kind each miss was before adding another round.

For reasoning models the question becomes when in the chain to retrieve. ReaLM-Retrieve scores each reasoning step from its output text alone: the model's stated confidence, how spread out the entity mentions are, and agreement across three resampled continuations. A trained policy then decides whether to retrieve at that step, against IRCoT's fixed retrieve-after-every-sentence schedule. On MuSiQue with DeepSeek-R1-Distill-Qwen-32B and ColBERTv2, it reached **71.2 F1 with 1.8 retrieval calls against IRCoT's 65.4 with 3.4**. Retrieving at random steps with the same 1.8 calls scored 62.7, so the timing carries the gain and not the reduced count. The gap widened from 3.2 points on 2-hop questions to 8.4 on 4-hop. Single retrieve-then-read still won on 12% of questions, mostly simple 2-hop ones, so the authors suggest routing by complexity first. The test sets are Wikipedia multi-hop only, and end-to-end latency was 14.1 s on 8 A100s, which the authors scope to asynchronous work. For API models without open weights, a learned proxy replaces stated confidence and drops its AUROC from 0.83 to 0.71. The policy took 2,400 GPU-hours to train ([arXiv:2604.26649](https://arxiv.org/abs/2604.26649), Guo et al., SIGIR 2026).

Verification against retrieved text buys accuracy at a steep token price. RARE runs a tree search over reasoning steps with extra retrieval actions, then scores each candidate path by the share of its statements that retrieved passages support. With LLaMA 3.1 8B on 250 MedQA questions, accuracy went from 70.0 for the search without retrieval to 74.8 with retrieval actions and the scorer, and a 70B model scored 87.43 against GPT-4o's 85.55 on MedQA. It used about 119.9k tokens per example against about 400 for chain-of-thought, averaged over three commonsense tasks, and the paper gives no latency or dollar figures. These are mostly multiple-choice benchmarks, the tables show means with no variance, and the scorer is the generator's own model ([arXiv:2412.02830](https://arxiv.org/abs/2412.02830), Tran et al., 2024, preprint). Price a verifier in tokens per answer before adding it.

Add up one request's budget before removing anything. The component figures are the course's estimates above; the generation time is an assumed placeholder:

```python
budget_ms = {"router": 200, "query rewriter": 300, "reranker": 50, "generation": 2_000}
total = sum(budget_ms.values())
for step, ms in budget_ms.items():
    print(f"{step:<16} {ms:>5} ms  {ms / total:4.0%}")
print(f"{'total':<16} {total:>5} ms")
```

```text
router             200 ms    8%
query rewriter     300 ms   12%
reranker            50 ms    2%
generation        2000 ms   78%
total             2550 ms
```

The reranker is the cheapest item here and often the first cut. Cut a component only once its effect on your metrics sits next to its cost.

That 50 ms assumes a cross-encoder. A listwise LLM reranker costs more calls but can be distilled: RankZephyr, an open 7B model distilled from RankGPT, matched RankGPT4 on TREC DL19/DL20 (nDCG@10 0.7816 and 0.8159 vs 0.7464 and 0.7076; SPLADE++ ED top 100, window 20) and trailed it on DL22 (0.6692 vs 0.7175). On DL19 shuffling the candidates cost it 0.015 nDCG@10 against 0.15 for GPT-3.5 listwise. English passage ranking, no latency reported ([arXiv:2312.02724](https://arxiv.org/abs/2312.02724), Pradeep et al., 2023-12, preprint).


Security, text that changes by legal effect, multimodal RAG and keeping a live index in sync continue in [07b](07b-security-changing-text-multimodal-and-live-indexes.md).

---

## Monitoring: metrics and checklist

Tracing tells you about one request. These tell you about the system over time, and the checklist is what to confirm before calling a pipeline production-ready.

**Metrics:**

- **Hallucination rate**: share of answers with at least one false claim (manual + automated).
- **Precision@k / recall@k**: retrieval quality ([01 § measure each stage](01-rag-pipeline.md#measure-each-stage)).
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

## Rules of thumb

| Rule | Why |
|---|---|
| Evaluate components and the system | A good system score can hide a broken router |
| Build eval sets from real traffic | Users ask what you didn't plan for |
| Cut prompt tokens before changing models | Usually the cheapest win |

---

## Labs

| Lab | Label |
|---|---|
| M5 ungraded lab "Tracing a RAG system" ([upstream](https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG)) | needs Phoenix (`arize-phoenix`, local server on :6006), embedded Weaviate, Together API key; not copied |
| M5 Assignment 5 "Improving a RAG System" | same; not copied |

---

## Pitfalls

- **No tracing until the first incident.** Symptom: "the bot said something wrong yesterday" can't be reproduced, because the retrieved chunks and the final prompt weren't logged. Trace from day one, and keep PII rules in mind for what you store.
- **Trusting an uncalibrated LLM judge.** Symptom: scores trend up while users complain. Keep a labelled sample, and correct against it as ARES does with PPI.
- **Quantizing without rescoring or measuring.** Symptom: recall falls after a memory-saving migration. Measure recall against exact search before and after.
- **Optimising the wrong step.** Symptom: weeks saving 50 ms on a reranker while generation takes seconds. Price every component in ms and dollars first.

---

## Try it

1. Rerun the quantization block with 1,000 candidates in place of 100. What happens to recall, and what is the extra cost?
2. In the cost block, set `OUTPUT_TOKENS = 1_000`. What share of baseline does "retrieved FAQ items" reach, and what do you conclude?

<details>
<summary>Answers</summary>

1. Recall reaches 1.00 on this synthetic set, up from 0.625, and you rescore ten times as many full vectors per query, so disk reads and latency grow. Pick the smallest candidate count that meets your recall target.
2. It reaches about 83% of baseline, up from about 60% at 200 output tokens: output now costs far more than the prompt, so a 59% prompt cut moves the bill little. Measure input and output separately before picking a lever.

</details>

---

## Interview checklist

| Question | Answer |
|---|---|
| How do you evaluate a RAG system? | By scope and evaluator: component and system, each with code checks, LLM judges and humans. Code runs on everything, judges cover the rest, and humans calibrate both. |
| What does a trace need to show? | The original and rewritten query, retrieved chunks with scores, reranker output, the final prompt, the response, and tokens and latency per span. |
| What is the flywheel? | Traces to failure cases to datasets to fixes to experiments to deployment, then round again. |
| How do you reduce memory for vectors? | float32 to int8 is 4× smaller. 1-bit is 32× smaller and needs rescoring at higher precision. Matryoshka embeddings can be truncated. |
| Where does the money go? | Mostly LLM tokens, so cut prompt size and `top_k` first. Huyen reports vector-database spend at a fifth to a half of model API spend at some companies, so it's not negligible either. |
| Where does the latency go? | Mostly the transformer. Then measure each component (the course estimates reranker ~50 ms, rewriter ~300 ms, router ~200 ms) and keep those that move a metric. |
| What does ARES add? | Lightweight judges fine-tuned on synthetic data, corrected with about 150 human labels through prediction-powered inference. |
| Which production metrics do you watch? | Hallucination rate, precision and recall at k, p95 latency, cost per query, user trust, and claim-level accuracy for CRAG systems. |

---

## Next

[07b — Security, changing text, multimodal RAG and live indexes](07b-security-changing-text-multimodal-and-live-indexes.md): lock down who can retrieve what, handle rules that change by legal effect, extend to images and PDFs, and keep a live index in sync.
