# hc_rag pipeline — architecture reference

> **Note:** This is an ADR (architecture decision record) distilled from the 2026-06-04 module refactor. It captures decisions and deferred items from that point in time. For the current module layout see `src/support_agents/hc_rag/README.md`.

Distilled from the 2026-06-04 module refactor. Source of truth for module boundaries, config, and follow-up decisions.

## Architecture

`hc_rag` is a **deterministic LangChain pipeline** — not agentic, no graph, no retry loops:

```
guardrail → retrieve_graded_chunks → rerank_graded_chunks → confidence gate → llm.ainvoke() → output guard
```

| Agent | Framework | Control flow |
|---|---|---|
| `hc_rag` | LangChain | Deterministic — retrieve once, rerank, generate, done |
| `hc_lg` | LangGraph | Explicit graph — intent router + CRAG grade/rewrite retry |
| `hc_adk` | Google ADK | ReAct loop — model decides what to search |

## Module map

```
rag/
  chunkers/      ← one file per strategy; get_chunker() factory in __init__.py
  reranker/      ← one file per strategy; get_reranker() factory in __init__.py
  retrieval/     ← ensemble search, RRF, scoring, snippet cache; pipeline.py is request-time entry
  ingestion/     ← offline CLI: JSONL → DuckDB; corpus_v2.py is the main ingest path
  parsing/       ← text cleaning, dedup, enrichment; wired into corpus_v2.py preprocess step
  datastore/     ← vector index implementations + DuckDB sidecar stores; factory.py is entry point
  schemas/       ← GradedChunk → RankedChunk type progression
```

Each folder has a `README.md` with per-file descriptions and tuning knobs.

## Chunkers (`rag/chunkers/`)

Six strategies, all implementing `chunk_document(doc: dict) -> list[Chunk]`:

| Strategy | Default | Notes |
|---|---|---|
| `fixed` | ✅ production default | Hard word-count splits; baseline benchmark |
| `overlapping` | — | Overlap between adjacent chunks; used in `corpus_v2.py` ingest |
| `html_aware` | — | Heading-boundary first; best fit for Billy/Intercom HTML corpus |
| `hierarchical` | — | Two-level parent+child; not wired in ingestion pipeline yet |
| `adjacency` | — | Positional IDs for neighbour expansion; `neighbors()` not called anywhere |
| `structured` | — | Recursive paragraph split; for prose without headings |

Select via factory:
```python
from support_agents.hc_rag.rag.chunkers import get_chunker
chunker = get_chunker("html_aware")
```

**Open follow-ups:**
- Wire `CHUNKER_STRATEGY` env var into `config.py` and `/config` endpoint (one-liner)
- Evaluate `html_aware` as the new ingest default — it's a better fit for the Billy HTML corpus than `fixed`

## Rerankers (`rag/reranker/`)

Five strategies via `RERANKER_BACKEND` env var. Factory in `rag/reranker/__init__.py`.

| Strategy | Default | Cost |
|---|---|---|
| `passthrough` | ✅ default | Free — vector score order only |
| `cross_encoder` | — | Local CPU, ~50–150ms, best general-purpose option |
| `colbert` | — | ~440MB download, ragatouille dep, GPU recommended |
| `pairwise` | — | O(n²) cross-encoder calls — offline eval only |
| `llm_listwise` | — | 1 LLM call for all passages — highest quality, API cost |

**Open follow-up:**
- Wire `SCORE_DELTA_ENABLED` / `SCORE_DELTA_MIN` into `agent.py` confidence gate. Both are defined in `config.py` but not yet read at request time. The intent: if the absolute score is borderline, require `score[0] - score[1] >= SCORE_DELTA_MIN` before accepting the top result.

## Ingestion preprocessing (`rag/parsing/`)

`preprocess_corpus()` now runs in `corpus_v2.ingest_v2_to_duckdb()` between load and embed:

```python
preprocess_corpus(
    docs,
    clean=True,            # strip email/app noise, normalize horizontal whitespace
    deduplicate=True,      # normalized text hash dedup before embedding
    filter_language=False, # Danish corpus — no language filtering
    enrich=False,          # JSONL already has metadata; skip to protect Bedrock source map
)
```

`enrich=False` is intentional: `_BEDROCK_SOURCE_MAP` in `IngestionPipeline` is keyed on `(source, content_type)`. If `enrich=True`, heuristic `content_type` values ("procedural", "faq") could be set on docs that don't have one, potentially interfering with the map lookup.

`clean_text` was fixed to use `[^\S\n]+` (not `\s+`) so newlines are preserved — required for `HtmlAwareChunker` to detect `## Section` markers.

## Removed config vars

Removed from `config.py` in the 2026-06-04 refactor — all were hc_lg orchestrator concepts that leaked into hc_rag:

```
RAG_LLM_PLANNER, RAG_PLANNER_LIGHT_MODEL     ← planner node (hc_lg concept)
CHECKPOINTER_BACKEND, SQLITE_PATH, DATABASE_URL  ← session checkpointing (LangGraph)
RAG_SUMMARIZATION_ENABLED/THRESHOLD/KEEP    ← conversation summarization (LangGraph state)
RAG_POST_ANSWER_EVALUATOR                   ← post-answer node (hc_lg concept)
RAG_POLICY_HYBRID_BORDER_LOW                ← unused (RAG_POLICY_MODE still exists)
METADB_PATH                                 ← read via os.getenv() directly in run_ingest, no var needed
```

Kept: `SCORE_DELTA_ENABLED`, `SCORE_DELTA_MIN` — valid reranker confidence signals, just not yet wired.

## Deferred items

| Item | Why deferred | Where to pick up |
|---|---|---|
| `CHUNKER_STRATEGY` env var + `/config` endpoint | One-liner; no design needed | `config.py` + `main.py:/config` |
| `HtmlAwareChunker` as ingest default | Needs ablation to validate vs FixedChunker | `retrieval-improvements.md` |
| `SCORE_DELTA` wiring in `agent.py` | Valid signal, just not read at request time | `agent.py` confidence gate check |
| Split `datastore/local.py` (587 lines) | Different risk profile; `ChromaVectorIndex` has test coverage | Separate PR |
