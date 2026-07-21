# GCP Vertex AI Search vs AWS Bedrock KB

Comparison of the two managed RAG backends used across our codebases.

| | **AWS Bedrock KB** | **GCP Vertex AI Search (Discovery Engine)** |
|---|---|---|
| **Used in** | galactus — VA agents | chat-agent — production backend |
| **Service name** | Amazon Bedrock Knowledge Bases | Vertex AI Search / Agent Builder / Discovery Engine |
| **Underlying store** | OpenSearch Serverless | Google's proprietary search stack |
| **Indexing** | Data source sync (S3, web crawl, Confluence…) | Data store ingestion (web crawl, Intercom, GCS, BigQuery…) |
| **Chunking** | Bedrock-managed hierarchical (leaf + parent) | Managed chunk mode — chunk boundaries opaque |
| **Hybrid search** | Dense (HNSW) + BM25 — `HYBRID` hardcoded | Internal, not configurable |
| **Reranking** | `amazon.rerank-v1:0` — explicit config | Internal to `:answer` endpoint; not exposed in Search API |
| **Raw scores via API** | ✅ cosine similarity (0–1) for fast mode; reranker score (0.05–0.35) | ✅ `relevance_score` per chunk result (0–1 float) |
| **Grounding score** | Not returned | ✅ `answer.grounding_score` (`:answer` endpoint) |
| **Session management** | Stateless — caller owns session | ✅ Native session concept (`Session` resource), persisted in Firestore for multi-replica |
| **Language support** | Corpus language agnostic | Defaults to corpus language (French for Shine); needs preamble override per query |
| **Answer generation** | Caller sends passages to LLM | Optional: `:answer` endpoint generates answer internally |
| **Cost unit** | Per `retrieve()` call + reranker calls | $0.003/query retrieval + $0.006/query if AI model enabled |
| **Auth** | `boto3` + AWS credentials / IAM | Application Default Credentials (ADC) / service account |
| **EU data residency** | `eu-north-1`, `eu-central-1` | `eu` location endpoint (`eu-discoveryengine.googleapis.com`) |

---

## Architecture in each codebase

### galactus — Bedrock KB

```
User query
  │
  ├─ retrieve() — fast, cosine, top-5, no rerank      (AgentTool)
  └─ retrieve_reranking() — top-15, reranker pass      (Eval / complex)
        │
        └── Bedrock KB (OpenSearch HYBRID)
               │
               ├── AMAZON_BEDROCK_TEXT_CHUNK  ← leaf match
               └── AMAZON_BEDROCK_TEXT         ← parent context → sent to LLM
```

Key env vars:
```bash
BEDROCK_KNOWLEDGE_BASE_ID=<id>   # required
AWS_REGION=eu-central-1
VA_RETRIEVAL_MODE=bedrock        # or 'rag' to call hc_rag agent instead
```

Full spec: [bedrock-kb.md](bedrock-kb.md)

---

### chat-agent — GCP Discovery Engine (two modes)

chat-agent supports three retrieval backends selectable at runtime:

```
┌─────────────────────────────────────────────────────────────────┐
│  Mode A — Local pgvector                                         │
│  agent.py + tools.py                                             │
│  PostgreSQL + pgvector, Gemini embeddings, exact cosine search   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Mode B — GCP Agentic RAG                                        │
│  gcp_agent.py + gcp_tools.py                                     │
│  ADK agentic loop: classify → search → grade → rewrite → search  │
│  GCP Discovery Engine Search (chunk mode) does retrieval         │
│  Gemini grades relevance + synthesizes answer                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Mode C — GCP Built-in Answer (:answer endpoint)                 │
│  gcp_agent_search.py                                             │
│  GCP owns retrieval + ranking + answer generation                 │
│  Thin wrapper: send query, stream tokens back                     │
│  Benchmark target: compare vs Modes A and B                       │
└─────────────────────────────────────────────────────────────────┘
```

Key env vars (chat-agent):
```bash
GCP_PROJECT_ID=<id>
GCP_DISCOVERY_LOCATION=eu
GCP_ENGINE_ID=<engine_id>
GCP_DISCOVERY_SERVING_CONFIG=<serving_config>
```

---

## Key behavioural differences

### Language handling
Bedrock KB is language-agnostic — retrieval returns whatever language the docs are in. The LLM generates in the query language.

GCP Discovery Engine **defaults to the corpus language** (French for Shine) when the user writes plain ASCII/English. chat-agent works around this with a per-query preamble injection:
```python
# gcp_agent_search.py — _effective_preamble()
override = (
    f"CRITICAL: The user's message is in {lang}. "
    f"You MUST respond in {lang} only. Do not use French or any other language."
)
```

### Score semantics

| Backend | Score field | Range | Meaning |
|---|---|---|---|
| Bedrock fast | `score` | 0–1 | Cosine similarity |
| Bedrock reranker | `score` | 0.05–0.35 typical | Reranker relevance |
| GCP Search | `relevance_score` | 0–1 float | Internal relevance (not documented) |
| GCP `:answer` | `grounding_score` | 0–1 | Citation support confidence |

**Never compare scores across backends or modes** — they are calibrated on different scales.

### Session state
- Bedrock: stateless per-call — no session concept.
- GCP `:answer`: maintains a `Session` resource on GCP side. chat-agent persists the GCP session name in Firestore keyed by caller `session_id` so all replicas share session state without sticky routing.

### Answer generation ownership
- Bedrock: Bedrock retrieves passages; your LLM (Claude, Gemini, etc.) generates the answer. Full control.
- GCP `:answer` endpoint: GCP retrieves + generates internally. You get `answer_text` + grounding references back. Less control but simpler integration.
- GCP Search (agentic mode): GCP retrieves chunks; Gemini (via ADK) grades and synthesizes. Hybrid ownership.

---

## Eval comparison axis

When running retrieval evals, keep backends strictly separated:

| Axis | System | Metric |
|---|---|---|
| Retrieval quality | Bedrock fast vs reranker | MRR, hit_rate, precision@5 |
| Retrieval quality | GCP Search vs pgvector | MRR, hit_rate |
| End-to-end quality | GCP `:answer` vs GCP agentic vs local agentic | GroundingGrader, AnswerQualityGrader |
| Cost | All three | `gcp_search_cost_usd` tracked in Langfuse |

Retrieval evals for galactus: `evals/graders/retrieval/url_coverage.py` against `data/va/qa_golden.jsonl`.
Retrieval evals for chat-agent: `eval/evaluate.py` / Langfuse dataset experiment flow.

---

## When to consider switching

**Bedrock → GCP Discovery Engine**: only if your entire infra moves to GCP. Bedrock's hybrid + reranker is genuinely strong; GCP's retrieval quality is comparable but the stack is opaque.

**GCP `:answer` → GCP agentic**: when you need CRAG-style correction loops or want to control answer synthesis. `:answer` is faster but you can't intercept or grade the retrieval step.

**Either → pgvector**: only for local dev or if Postgres is already your stack. Loses hybrid search and managed reranking. Not production-ready at scale without significant infrastructure work.
