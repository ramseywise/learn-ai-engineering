# Support Agents — Observability & Experiment Tracking

Schema contract for what every agent logs and how eval runs are identified, reproduced,
and compared. Platform wiring lives in the tooling docs:
→ [langfuse.md](../04-agentic-frameworks/notes/langfuse.md) (primary)
→ [langsmith.md](../04-agentic-frameworks/notes/langsmith.md) (secondary / VA agents)

---

## Base trace metadata

Every agent call — regardless of framework — must emit these fields. They are the
minimal contract that makes a trace queryable and a run reproducible.

| Field | Type | Description |
|---|---|---|
| `run_id` | `str` | `uuid4` — unique per invocation |
| `session_id` | `str` | conversation thread ID (passed in by caller) |
| `agent` | `str` | `"hc_adk"` \| `"hc_lg"` \| `"hc_rag"` \| `"va_langgraph"` \| `"va_google_adk"` |
| `model` | `str` | model name/ARN used for generation |
| `prompt_version` | `str` | `PROMPT_VERSION` constant from the agent module |
| `git_commit` | `str` | short SHA — ties log entry to exact code state |
| `latency_ms` | `float` | wall-clock time from request in to response out |
| `input_tokens` | `int` | prompt token count (if available from model response) |
| `output_tokens` | `int` | completion token count |
| `guardrail_triggered` | `bool` | true if Layer 1 input guard fired |
| `escalated` | `bool` | true if Layer 5 escalation path was taken |
| `retrieval_k` | `int` | number of passages retrieved (0 for non-RAG agents) |
| `grounding_score` | `float \| None` | Layer 4 output guard score (null if not run) |
| `contact_support` | `bool` | `AssistantResponse.contact_support` value |

These map directly to `langfuse.trace()` metadata and to `ExperimentRun` below.

---

## Experiment tracking schemas

### ExperimentRun — top-level experiment identity

Wraps every eval invocation so runs are reproducible and diffable across ablations.

```python
@dataclass
class ExperimentRun:
    run_id: str                      # uuid4 — unique per eval invocation
    experiment_name: str             # human label, e.g. "hc-rag-chunking-v3"
    created_at: str                  # ISO 8601 UTC
    git_commit: str                  # short SHA
    dataset: str                     # path to .jsonl eval set
    pipeline: str                    # "hc_rag" | "hc_adk" | "hc_lg" | "bedrock_kb"
    rag_config: RagConfig | None = None
    bedrock_config: BedrockConfig | None = None
    notes: str = ""
```

### RagConfig — retrieval pipeline snapshot

Captures full configuration for a single retrieval experiment. Extend, don't replace,
the existing shallow `RagConfig` in `evals/pipelines/lib/models.py`.

```python
@dataclass
class RagConfig:
    # Chunking
    chunker: str = ""                # "fixed" | "semantic" | "recursive" | "hierarchical"
    chunk_size: int = 0              # retrieval chunk size (chars or tokens)
    chunk_overlap: int = 0
    parent_chunk_size: int = 0       # parent window size (hierarchical only — 0 = flat)
    chunk_unit: str = "chars"        # "chars" | "tokens"

    # Embedding
    embedding_model: str = ""
    embedding_dim: int = 0

    # Indexing
    vector_store_backend: str = ""   # "faiss" | "opensearch" | "pinecone" | "bedrock_kb"
    index_name: str = ""
    distance_metric: str = "cosine"
    index_created_at: str = ""

    # Retrieval
    search_strategy: str = "dense"   # "dense" | "sparse" | "hybrid"
    hybrid_alpha: float = 1.0        # 1.0 = pure dense, 0.0 = pure sparse
    retrieval_k: int = 0
    score_threshold: float = 0.0

    # Reranking
    reranker: str = ""
    reranker_top_k: int = 0
```

### BedrockConfig — Bedrock request tracing

Captures everything needed to reproduce a Bedrock call and trace it in AWS. Populate
`request_id` and `latency_ms` from the response metadata.

```python
@dataclass
class BedrockConfig:
    model_id: str = ""               # full ARN
    anthropic_version: str = ""      # "bedrock-2023-05-31"
    aws_region: str = ""

    max_tokens: int = 0
    temperature: float = 0.0
    top_p: float | None = None
    stop_sequences: list[str] = field(default_factory=list)

    # Knowledge Base
    knowledge_base_id: str = ""
    kb_retrieval_k: int = 0
    kb_search_type: str = ""         # "SEMANTIC" | "HYBRID"
    kb_filter: dict = field(default_factory=dict)

    # Populated from response
    request_id: str = ""             # x-amzn-requestid header
    http_status: int = 0
    latency_ms: float = 0.0
```

### ChunkRecord — per-chunk document metadata

Critical for hierarchical chunking experiments. Extends what the scraper writes.

```python
@dataclass
class ChunkRecord:
    chunk_id: str                    # deterministic hash(doc_id + start_char)
    doc_id: str
    parent_id: str = ""              # parent chunk ID (hierarchical only)
    level: int = 0                   # 0 = leaf (retrieved), 1 = parent window

    text: str = ""
    char_start: int = 0
    char_end: int = 0
    section: str = ""

    url: str = ""
    source_type: str = ""            # "help" | "blog" | "faq"
    scraped_at: str = ""

    embedding_model: str = ""
    embedded_at: str = ""
```

Hierarchical structure at retrieval time:
```
doc_123
  └─ chunk c_abc  (level=1, parent_id="")        ← parent window returned to LLM
       ├─ chunk c_def  (level=0, parent_id="c_abc")  ← retrieved by vector search
       └─ chunk c_ghi  (level=0, parent_id="c_abc")
```
Fetch the leaf, return `parent_id`'s text as LLM context.

---

## Custom RAG vs. Bedrock KB — field coverage

| Capability | hc_rag (custom) | Bedrock KB |
|---|---|---|
| `chunk_id` / `parent_id` | ✅ can implement | ❌ opaque |
| Retrieved passage text | ✅ `sources[].text` | ❌ URL only |
| Retrieval score per chunk | ✅ `scores[]` | ❌ not exposed |
| `request_id` for tracing | via HTTP header | ✅ `x-amzn-requestid` |
| RAGAS faithfulness / context precision | ✅ | ❌ (no text) |
| Rerank scores | 🟡 stub only | ❌ |

For fair comparison use only fields both surfaces expose: hit rate / MRR (URL match),
latency, LLM-as-judge scores (both supply the final answer text), cost per query.

---

## Grounding tier promotion policy

Layer 4 grounding tiers are promoted to hard failures conservatively — new checks start as log-only diagnostics before becoming response-blocking.

**Pattern:** Implement → observe false-positive rate in production → promote to escalation trigger only after confirming false-positive rate is acceptable.

**Current state:** Tiers 1–2 (hallucinated citation IDs, missing citations) are hard fails. Tier 3 (quote overlap = 0) is a hard fail. Tiers 3 partial (paraphrase) and 4 (relevance score, language mismatch, suggestion URLs) are log-only.

**Why:** Overly aggressive grounding checks in a multilingual (Danish/English) context with paraphrase-heavy answers would cause excessive `contact_support` escalations. The log-only phase provides evidence to calibrate thresholds before they affect users.

---

## Current implementation state

### What's live

| Item | Agent | Where | Notes |
|------|-------|-------|-------|
| `lf.trace()` root with full metadata | hc_adk | `main.py:_run_turn` | prompt_version, retrieval_mode, thinking_budget, tokens, failure_reason |
| `lf_trace.span()` KB child spans | hc_adk | `agent.py:_search_bedrock/rag` | per tool call: queries, passage_count, top_score, urls, duration_ms |
| `retrieval_quality` score | hc_adk | `main.py` | kb_top_score from highest-scoring tool call |
| `CallbackHandler` root + node spans | hc_lg | `main.py:_run_turn` | all graph nodes auto-captured |
| `retrieval_quality` score (CRAG formula) | hc_lg | `main.py` | `(relevant×1.0 + ambiguous×0.5) / total` |
| `@observe` root + RAG internals | hc_rag | `main.py:_run_turn` | session_id, prompt_version |
| Online scoring (3 heuristics) | all | `observability.push_online_scores()` | citation_hallucination, missing_citation, language_consistency |
| Remote prompt fetch at startup | hc_adk, hc_lg | `get_root_agent()`, `_get_answer_prompt()` | via `get_langfuse_prompt()` in observability.py |

### Still pending

| Priority | Item | Where |
|---|---|---|
| P0 | Surface `retrieved_urls` in hc_rag `main.py` → enable citation scores | `hc_rag/main.py` + `agent.py:run_turn()` |
| P0 | Wire `ExperimentRun` wrapper into eval runners | `evals/pipelines/eval_quality.py`, `eval_stats.py` |
| P1 | Capture `BedrockConfig.request_id` from `x-amzn-requestid` header | `clients/bedrock_kb.py` |
| P1 | Add `git_commit` to trace metadata (all agents) | `observability.configure_runtime()` |
| P1 | Add `ChunkRecord` with `chunk_id`, `parent_id`, `level` | `core/chunking/schemas.py` |
| P2 | Expand `RagConfig` with `overlap`, `parent_chunk_size`, `hybrid_alpha`, `dim` | `evals/pipelines/lib/models.py` |
| P2 | Wire retrieval-run metadata into local RAG/eval outputs | `evals/pipelines/evaluation.py`, `src/support_agents/hc_rag/rag/ingestion/` |

---

## Related files

| File | Role |
|---|---|
| `evals/pipelines/lib/models.py` | `RagConfig`, `QATask`, `EvalReport` — extend here |
| `evals/metrics/retrieval.py` | Retrieval metrics and URL matching helpers |
| `evals/pipelines/evaluation.py` | Live local eval runner that writes graded output JSON |
| `core/preprocessing/bkh/pii_scrub.py` | Call before any external LLM grader (GDPR layer) |
