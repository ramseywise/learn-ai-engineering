# Bedrock Knowledge Base — Reference Spec

Retrieval from AWS Bedrock KB used in VA support agents. Ported from `va-agents/src/agents/tools/support-knowledge-v2.ts`.

---

## Known KB identities

| Product | KB ID | Region | Language |
|---|---|---|---|
| VA staging / Billy (Danish) | `IZIPVEXDSF` | `eu-north-1` | Danish — `opret faktura` |
| VA production / Billy (Danish) | `AOZUJEDRLC` | `eu-north-1` | Danish |
| Legacy Billy (Danish) | `I7ZRQ0SJCB` | `eu-north-1` | Danish |
| Billy MCP | `C36YGJVEQP` | `eu-central-1` | Danish |
| Clara (German) | *env var required* | `eu-central-1` | German — Clara tickets |

**Do not run Clara/German tickets against the Danish KB.** Confirm `BEDROCK_KNOWLEDGE_BASE_ID` before running any retrieval eval.

---

## Staging KB scope and composition

The staging KB (`IZIPVEXDSF`) currently ingests four data sources via web crawl: Danish Intercom help center articles, English Intercom help center articles, Billypedia glossary terms, and pricing pages.

**Aligned decisions (Jun 2026):**

| Decision | Rationale |
|----------|-----------|
| Restrict KB to **Danish-only Intercom pages** | Current market focus is Danish; English articles duplicate content and degrade retrieval precision |
| Remove **Billypedia** from Bedrock staging | Data quality and parsing issues; content is available in local DuckDB corpus for `hc_rag` testing |
| Suspend **pricing page** ingestion pending fix | Table-based page structure produces chunks that are too small to contain sufficient context; requires a parsing fix or supplemented content before re-ingestion |

These changes (removing English articles, Billypedia, and pricing from Bedrock) are tracked as a backlog ticket assigned to Marco.

The local DuckDB corpus (`data/corpus/`) is a separate artifact and is not subject to these Bedrock scope restrictions — it can include Billypedia and pricing for local `hc_rag` testing.

---

## Two retrieval modes

| Mode | Function | `numResults` | `scoreThreshold` | Reranker | Use case |
|---|---|---|---|---|---|
| Fast | `retrieve()` | 5 | 0.4 (cosine) | No | Agent tool, low latency |
| Reranking | `retrieve_reranking()` | 15 | 0.05 (reranker) | `amazon.rerank-v1:0` | Eval, complex/multi-concept queries |

**Score scale differs by mode.** Raw cosine similarity (0–1) is calibrated differently from reranker relevance scores (borderline matches 0.05–0.35). Never compare scores across modes.

---

## Pipeline

```
queries[] ─→ parallel boto3.retrieve() ─→ flat results
                                             ↓
                                    deduplicate (URL + content fingerprint)
                                             ↓
                                    score filter (threshold)
                                             ↓
                                    text clean + title extract
                                             ↓
                                    Passage[id, score, title, url, text]
```

**Parallel multi-query:** all queries fired concurrently via `asyncio.to_thread` (boto3 is sync). Use 2–3 queries for focused questions, 4–6 for multi-concept.

**Deduplication:** sort by score desc, fingerprint = `url|content_snippet[:200]`. First occurrence wins.

**Search type:** always `HYBRID` (dense + sparse). Hardcoded in the retrieval config.

---

## Text cleaning

FM-parsed chunks (Claude 4.5 Bedrock KB parser) contain XML artifacts:
- Strip `<markdown>` / `</markdown>` wrappers
- Strip `<figure>` blocks where `<figure_type>` is `Logo` or `Icon`

Web-crawled chunks are plain text — cleaning is safe to run on both.

---

## Title extraction (two patterns)

| Chunk type | Pattern | Example |
|---|---|---|
| Web-crawled | `"Page Title \| Site Name"` prefix in first 120 chars | `"Create Invoice \| Billy Support"` |
| FM-parsed | First `# Heading` or `## Heading` in text | `## Opret en faktura` |
| Metadata | `result.metadata["title"]` if not a URL | Prefer this when present |

Strip the site name suffix (`split(" | ")[0]`) from the final title.

---

## Implementation location

Inline in each agent (separate uv projects — no shared package):

```
galactus/agents/va_google_adk/bedrock_kb.py
galactus/agents/va_langgraph/bedrock_kb.py
```

Both files are identical. If logic diverges, keep them separate; do not add a `sys.path` hack.

---

## Retrieval mode switch

Both support agents read `VA_RETRIEVAL_MODE` at startup:

```bash
VA_RETRIEVAL_MODE=bedrock   # call Bedrock KB directly
VA_RETRIEVAL_MODE=rag       # call HC_RAG_AGENT_URL (default)
```

`rag` is the default so existing behaviour is unchanged without the env var.

---

## Env vars (consolidated)

```bash
BEDROCK_KNOWLEDGE_BASE_ID=<kb_id>       # required — no default
AWS_REGION=eu-central-1                 # default
AWS_PROFILE=<profile>                   # or explicit keys below
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
```

---

## Reranker ARN

```
arn:aws:bedrock:{AWS_REGION}::foundation-model/amazon.rerank-v1:0
```

Constructed at runtime from `AWS_REGION`. Reranker config: 5 reranked results, metadata `selectionMode=ALL`.

---

## Storage field mapping

Raw fields observed in the OpenSearch/Bedrock KB index and how they map to our eval schemas (`evals/pipelines/utils/schemas.py`):

| Production field | Schema | Notes |
|---|---|---|
| `id` | `ChunkRecord.chunk_id` | Bedrock internal chunk ID |
| `_id` | `ChunkRecord.opensearch_id` | OpenSearch document ID — differs from `id` |
| `_index` | `ChunkRecord.opensearch_index` | OpenSearch index name |
| `AMAZON_BEDROCK_TEXT_CHUNK` | `ChunkRecord.text` | Leaf chunk that triggered the retrieval hit |
| `AMAZON_BEDROCK_TEXT` | `ChunkRecord.parent_text` | Parent context window sent to the LLM — Bedrock's native hierarchical chunking |
| `x-amz-bedrock-kb-source-uri` | `ChunkRecord.url` | Original source URL |
| `x-amz-bedrock-kb-source-file-modality` | `ChunkRecord.source_modality` | `"TEXT"` \| `"IMAGE"` |
| `x-amz-bedrock-kb-data-source-id` | `ChunkRecord.data_source_id` / `BedrockConfig.data_source_id` | Specific ingestion source within the KB |
| `AMAZON_BEDROCK_METADATA` | — | Serialised metadata object — deserialise to access title, category, etc. |
| `bedrock-knowledge-base-default-vector` | `BedrockConfig.kb_vector_field` | Embedding vector field name in OpenSearch |
| `_score` | `ChunkRecord.opensearch_score` | **Not exposed by Bedrock KB API** — visible in OpenSearch dashboard only; always `0.0` via API |
| `_type` | — | OpenSearch/ES internal type field — not tracked |

**`AMAZON_BEDROCK_TEXT` vs `AMAZON_BEDROCK_TEXT_CHUNK`** is Bedrock's native two-level hierarchy: the chunk field is what matched, the text field is the larger context window the LLM actually reads. Maps directly to our `level=0` (leaf) / `level=1` (parent) in `ChunkRecord`.

---

## Eval comparison

The retrieval eval (M3–M4 in va-migration plan) compares:

| Axis | Mode A | Mode B |
|---|---|---|
| Reranking gap | `retrieve()` (fast, no rerank) | `retrieve_reranking()` |
| RAG vs Bedrock | `VA_RETRIEVAL_MODE=bedrock` | `VA_RETRIEVAL_MODE=rag` |

Score against `data/va/qa_golden.jsonl` using `evals/graders/retrieval/url_coverage.py`.
Metrics: hit_rate, MRR, precision@5, recall@5.

---

## Quick smoke test

```bash
cd agents/va_google_adk
BEDROCK_KNOWLEDGE_BASE_ID=<id> AWS_REGION=eu-central-1 \
  uv run python -c "
import asyncio, bedrock_kb
passages = asyncio.run(bedrock_kb.retrieve(['how to create an invoice']))
for p in passages:
    print(p.id, p.score, p.url)
"
```
