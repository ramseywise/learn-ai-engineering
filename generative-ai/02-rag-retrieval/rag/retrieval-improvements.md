# Retrieval Improvement Research

Status: Research — evaluating options after initial ablation run (2026-05-09)

## Current baseline (44-task eval, 32 annotated)

| Config | MRR | P@1 | Latency |
|--------|-----|-----|---------|
| va_staging benchmark | 0.625 | 0.625 | ~9.3s (smoke/10) |
| hc_adk + thinking1024 | 0.583 | 0.531 | 7.3s |
| hc_lg + CRAG | 0.547 | 0.531 | 7.7s |
| hc_lg no CRAG | 0.542 | 0.531 | 4.4s ← best latency/quality tradeoff |
| hc_adk baseline | 0.418 | 0.219 | 2.6s |

Gap to va_staging: **-0.042 MRR** (best local vs benchmark on smoke subset).

## What we learned from ablations

- **Thinking budget (+1024)**: huge gain for hc_adk (+0.165 MRR), hurts hc_lg when combined with CRAG (interaction effect — thinking changes citation style, breaking CRAG's grading alignment)
- **CRAG**: +0.005 MRR vs no-CRAG, costs +3.4s. Confidence gate (threshold=0.7) short-circuits most runs since Bedrock returns decent scores. Marginal value.
- **LLM planner**: -0.031 MRR vs regex router, +4s latency. Regex is better for our edge-case vocabulary.
- **va_staging advantage**: (1) gemini-3-flash-preview (newer model), (2) ThinkingLevel.LOW internally, (3) multi-query retrieval before KB call.

## Research items

### 1. Upgrade model: gemini-3-flash-preview

**Expected gain**: ~+0.04–0.08 MRR — likely the biggest single lever.
**Cost**: Same latency profile, slightly higher per-token cost.
**How**: `GEMINI_MODEL=gemini-3-flash-preview uv run uvicorn hc_adk.main:app --port 8011`
**Run path**: use `evals.pipelines.run live` or `evals.pipelines.run langfuse`
with `GEMINI_MODEL=gemini-3-flash-preview` set in the agent environment.
**Status**: TODO — run ablation.

---

### 2. Multi-query retrieval

**What**: Generate 2–3 reformulated queries per user question → retrieve for each → merge/deduplicate results by URL → pass top-N to answer node.
Matches va_staging's internal strategy (it generates Danish keyword phrases before retrieval).

**Expected gain**: +0.05–0.10 MRR, especially on:
- Short/vague queries (single query has high lexical variance)
- Abstract accounting terms (Danish spelling variants)
- Cross-lingual queries (DA question → EN article)

**Cost**: +1 LLM call (query generation), +N Bedrock calls (one per variant). No grading loop.
**Implementation in hc_lg**: New node `multi_query` between `planner` and `retrieve`.

```python
# Sketch: generate_queries node
async def generate_queries_node(state: State) -> State:
    llm = ChatGoogleGenerativeAI(model=_MODEL, temperature=0.3)
    result = await llm.ainvoke([
        ("system", MULTI_QUERY_PROMPT),
        ("human", state["query"])
    ])
    queries = parse_queries(result.content)  # extract list of reformulations
    return {**state, "queries": [state["query"]] + queries[:2]}

# retrieve node runs bedrock_kb.retrieve for each query, merges
```

**Implementation in hc_adk**: Modify `fetch_support_knowledge` tool to accept and execute multiple queries.

**Status**: PLANNED — implement after model upgrade ablation.

---

### 3. HyDE (Hypothetical Document Embeddings)

**What**: Instead of embedding the user query for retrieval, generate a "hypothetical ideal article" that answers the query, embed that, and retrieve by similarity.
Bridges the domain gap between customer support language (informal Danish) and help center language (formal structured articles).

**Why it works**: Accounting queries use informal vocabulary ("gebyr", "moms indberette") while articles use formal Danish ("momsafregning", "indberetning til SKAT"). HyDE closes this gap.

**Cost**: +1 LLM call to generate the hypothetical article, no retrieval loop.
**Limitation**: Works best with pure vector retrieval (hc_rag). Bedrock HYBRID search (BM25 + vector) may dilute the benefit since BM25 is keyword-based.

**Best implementation path**: hc_rag's retrieval endpoint, not hc_adk/hc_lg with Bedrock.

```python
# Sketch for hc_rag
async def hyde_retrieve(query: str) -> list[dict]:
    hyp = await generate_hypothetical_doc(query)   # LLM call
    hyp_embedding = embed(hyp)                      # multilingual-e5-large
    return vector_search(hyp_embedding)             # DuckDB ANN
```

**Status**: PLANNED — implement as `RETRIEVAL_MODE=hyde` flag on hc_rag after multi-query.

---

### 4. hc_rag as retrieval backend for hc_adk / hc_lg

**What**: Route all Bedrock KB calls through hc_rag's local DuckDB+multilingual-e5-large endpoint.
**Why**: Zero Bedrock cost, full control over embedding model, enables HyDE.
**Flags**: `VA_RETRIEVAL_MODE=rag` (hc_adk), `VA_RETRIEVAL_BACKEND=rag` (hc_lg)
**Baseline**: hc_rag alone scores MRR=0.42 on retrieval-only. LLM agents + local rag TBD.

**Status**: TODO — add Makefile ablation targets, run comparison.

---

### 5. DPO / Preference Fine-tuning

**What**: Curate (query, good_response, bad_response) preference pairs from our eval set.
Fine-tune either:
  - Query generation (retrieval query construction): prefer queries that lead to gold URL
  - Answer synthesis: prefer responses that cite the golden article

**Blocked on**: Sufficient annotated golden responses (need 200+ preference pairs).
**Current state**: 32 annotated queries in eval set, 0 golden responses stored.

**Path to unblock**:
1. Run comparable agent configs through `uv run python -m evals.pipelines.run live ...` or LangFuse experiments to identify tasks where some configs hit and others miss
2. For hit tasks: va_staging / hc_lg+thinking responses as preferred, adk_baseline as rejected
3. Collect 200+ pairs before starting DPO

**Status**: BLOCKED — collect golden responses via ablation_analysis.ipynb first.

---

## Priority order

1. **gemini-3-flash-preview ablation** (zero engineering, big expected gain)
2. **hc_rag as backend** (free latency/cost benchmark)
3. **Multi-query retrieval** (best quality lever after model upgrade)
4. **HyDE on hc_rag** (complements multi-query, different failure mode coverage)
5. **DPO** (long-term, blocked on data collection)

---

## hc_rag baseline (smoke, 2026-05-09)

10 tasks from golden_traces, 32 annotated:

| Metric | Score |
|---|---|
| MRR | 0.26 |
| P@1 | 0.22 |
| R@3 | 0.33 |
| NDCG@3 | 0.28 |

3/9 annotated tasks hit in top-5. **2 misses are Billypedia URLs not ingested — this is a coverage gap, not a ranking error.** When filtering those, effective MRR on ingested content is higher.

This eval loop uses a different retrieval path than the citation proxy: `query → POST /api/v1/retrieval → ranked chunks → compare URLs to golden set → P@k / MRR / NDCG`. The existing retrieval proxy measures citation sentiment on BKH conversation data; it can't measure ranked chunk quality.

### URL normalization

**Design decision:** `kb_url_map.json` is a stateless lookup table committed to the repo. Agents never contain version-aware URL logic — KB migrations (Billy → Shine) are a data operation, not a code redeploy. This keeps agents KB-agnostic and prevents grounding false-positives when the underlying domain changes.

Match on path-only (`/da/articles/622808-...`) to avoid protocol/domain drift between `help.billy.dk` and `help.shine.co`.

**Aliasing rules:**
1. Intercom articles: extract numeric ID from `/articles?/(\d+)` — locale-agnostic.
2. `help.billy.dk ↔ help.shine.co`: same article ID, rewrite domain + locale prefix. `help.billy.dk/en/articles/<id>-<slug>` → `help.shine.co/da/articles/<id>-<slug>`.
3. Billypedia (`www.billy.dk/billypedia/<slug>/`): **no canonical Shine URL**. These are excluded from grounding/citation coverage (implemented in `url_coverage.py` as `topic_proxy`). Do NOT alias; tag `content_type: "glossary_term"` if ever ingested.

### Billypedia: never the primary retrieval target

Billypedia is a flat concept glossary with no numeric article IDs and no Shine equivalent. For `definition` queries it provides a context frame only — the actual answer still comes from help center articles. This is why Billypedia misses in eval results are **expected and correct** (not ranking failures). The source router in `semantic-cache.md` encodes this: `definition` intent → Billypedia as context enrichment + help center for the answer.
