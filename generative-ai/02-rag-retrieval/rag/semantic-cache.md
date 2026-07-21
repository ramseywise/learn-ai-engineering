# Semantic Cache for Support Agents

> **Hackathon experiment slot.** Zero-RAG-cost path for queries that closely match the golden dataset.
>
> **Prerequisite**: `golden-dataset.md` pipeline must complete first — specifically `semantic_cache_seed.jsonl` (high-scoring SA responses, composite ≥ 0.75).
>
> **Hypothesis**: A meaningful fraction of incoming queries are paraphrases of already-answered questions from the golden set. Routing those directly to a cache hit saves the full CRAG round-trip (~3–6s, 2+ LLM calls) without quality loss because the cached answers are already grader-validated.

---

## How it works — 3-tier pipeline

```
planner ──▶ cache_lookup ──▶ hit (sim ≥ 0.85)? ──YES──▶ cache_respond ──▶ END
                                        │
                                       NO
                                        ▼
                             source_router ──▶ route by intent_type
                                        │              │              │
                                  how_to/regulatory  definition  escalation
                                        │              │              │
                               help_center KB    billypedia     skip retrieval
                                        │         (context       → respond
                                        ▼           enrichment)
                              retrieve (CRAG) ──▶ answer ──▶ END
```

**Tier 1 — Semantic cache** (zero LLM, zero retrieval): embed query, cosine match against golden seed. Hit ≥ 0.85 → return cached answer.

**Tier 2 — Embedding source router** (zero LLM, ~1ms): reuse the already-loaded `multilingual-e5-base` model to classify `intent_type` by cosine distance to pre-computed intent centroids. Routes to the right Bedrock KB source before retrieval. See [Source routing](#source-routing--tier-2) below.

**Tier 3 — CRAG** (full pipeline, LLM calls): only reached when cache misses and routing resolves to an answerable intent.

For Tier 1: after `planner` classifies intent as `answerable`, a new `cache_lookup` node embeds the query and does a cosine nearest-neighbour search over the pre-built embeddings from `semantic_cache_seed.jsonl`. If the top match exceeds `SEMANTIC_CACHE_THRESHOLD` (default `0.85`), return the cached answer directly — no retrieval, no grading, no answer LLM call. Below threshold, or when `SEMANTIC_CACHE_ENABLED=false`, the query flows to Tier 2.

---

## Offline phase — build the cache index

**Input**: `data/datasets/bkh/semantic_cache_seed.jsonl` (output of the golden dataset pipeline — grader-validated SA responses, composite ≥ 0.75)

**Notebook**: `nbks/sa/build_semantic_cache.ipynb`

### Embed queries

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("intfloat/multilingual-e5-base")  # handles Danish
queries = [row["query"] for row in seed]
embeddings = model.encode(queries, normalize_embeddings=True)  # (N, 768) float32
```

No clustering needed — the golden dataset pipeline already deduplicated via stratification. Keep all rows.

### Persist

```python
import numpy as np, json
np.savez(
    "data/corpus/datastores/semantic_cache.npz",
    embeddings=embeddings.astype("float32"),
    queries=np.array([r["query"] for r in seed]),
    answers=np.array([r["response"] for r in seed]),
    sources=np.array([json.dumps(r.get("sources", [])) for r in seed]),
    scores=np.array([r["composite_score"] for r in seed]),
)
```

Typical size: ~150–200 rows → single matrix multiply at query time, no FAISS needed.

---

## Runtime module

**File**: `src/support_agents/hc_lg/semantic_cache.py`

```python
"""Semantic cache: ANN lookup over grader-validated QA embeddings.

SEMANTIC_CACHE_ENABLED=true  (default false)
SEMANTIC_CACHE_THRESHOLD     (default 0.85, sweep 0.75–0.95)
SEMANTIC_CACHE_PATH          (default data/corpus/datastores/semantic_cache.npz)
SEMANTIC_CACHE_MODEL         (default intfloat/multilingual-e5-base)
"""
import os, json
import numpy as np
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer

_ENABLED   = os.getenv("SEMANTIC_CACHE_ENABLED", "false").lower() == "true"
_THRESHOLD = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.85"))
_PATH      = os.getenv("SEMANTIC_CACHE_PATH", "data/corpus/datastores/semantic_cache.npz")
_MODEL     = os.getenv("SEMANTIC_CACHE_MODEL", "intfloat/multilingual-e5-base")

@dataclass
class CacheResult:
    matched_query: str
    answer: str
    sources: list[dict]
    similarity: float
    composite_score: float

_store: dict = {}

def _load():
    if _store:
        return
    data = np.load(_PATH, allow_pickle=True)
    _store.update({
        "embeddings": data["embeddings"].astype("float32"),
        "queries":    data["queries"],
        "answers":    data["answers"],
        "sources":    data["sources"],
        "scores":     data["scores"],
        "model":      SentenceTransformer(_MODEL),
    })

def lookup(query: str) -> CacheResult | None:
    if not _ENABLED:
        return None
    _load()
    vec = _store["model"].encode([query], normalize_embeddings=True)
    sims = (_store["embeddings"] @ vec.T).flatten()
    idx = int(np.argmax(sims))
    sim = float(sims[idx])
    if sim < _THRESHOLD:
        return None
    return CacheResult(
        matched_query=str(_store["queries"][idx]),
        answer=str(_store["answers"][idx]),
        sources=json.loads(_store["sources"][idx]) if _store["sources"][idx] else [],
        similarity=sim,
        composite_score=float(_store["scores"][idx]),
    )
```

---

## Graph changes

### `state.py`

Add two fields:
```python
cache_hit: bool          # True when semantic cache short-circuited retrieval
cache_similarity: float  # cosine sim of match (0.0 when no hit)
```

### `agent.py`

New node and updated routing:

```python
from hc_lg.semantic_cache import lookup as _cache_lookup

async def cache_node(state: State) -> State:
    result = _cache_lookup(state["query"])
    if result is None:
        return {**state, "cache_hit": False, "cache_similarity": 0.0}
    response = AssistantResponse(
        message=result.answer,
        sources=result.sources,
        contact_support=False,
    )
    return {
        **state,
        "cache_hit": True,
        "cache_similarity": result.similarity,
        "response": response.model_dump(),
    }

def route_after_planner(state: State) -> str:
    intent = state.get("intent", "answerable")
    if intent in ("clarification", "escalation"):
        return "respond"
    return "cache"                        # was "retrieve"

def route_after_cache(state: State) -> str:
    return "end" if state.get("cache_hit") else "retrieve"
```

Graph wiring addition:
```python
_builder.add_node("cache", cache_node)
_builder.add_conditional_edges("planner", route_after_planner,
    {"cache": "cache", "respond": "respond"})
_builder.add_conditional_edges("cache", route_after_cache,
    {"end": END, "retrieve": "retrieve"})
```

---

## Source routing — Tier 2

> The taxonomy below is the full Phase C spec from `kb-content-taxonomy.md` (now archived). The same `multilingual-e5-base` model loaded for the cache is reused — no second model, no LLM call.

### Taxonomy spec

```
domain:
  accounting        — general bookkeeping, accounts, chart of accounts
  vat               — moms, momsindberetning, momsopgørelse, momsfradrag
  invoicing         — faktura, kreditnota, EAN, tilbud, rykker
  payroll           — løn, ansatte, B-skat, kørselsgodtgørelse
  banking           — bankafstemning, postering, kontoudtog, kassekladde
  reporting         — årsregnskab, årsrapport, resultatopgørelse, afslutning
  subscription      — abonnement
  escalation        — human handoff, friction

intent_type:
  how_to            — step-by-step task execution
  error             — something isn't working
  definition        — "what is X?"
  regulatory        — tax rules, compliance, legal requirements
  escalation        — user wants human support
```

**Classifier approach** — start rule-based, promote if needed:

| Option | Cost | Quality | Effort |
|---|---|---|---|
| Rule-based keyword map | Free | Medium | Low — start here |
| Few-shot LLM classifier | ~$0.01/item | High | Medium |
| Embedding centroid (reuse `multilingual-e5-base`) | Free inference | High | Medium |

**Key architectural decision:** eval coverage analysis and runtime source routing share the same classifier artifact (`evals/graders/taxonomy/intent_classifier.py`). The taxonomy does double duty — coverage gap analysis in eval pipeline and KB source routing at request time. Don't build two separate classifiers.

### Intent → source mapping

| `intent_type` | Bedrock KB source | Behaviour |
|---|---|---|
| `how_to` | help center (`WOHA5CGA4I`) | Standard CRAG retrieval |
| `regulatory` | help center + pricing (`SWYMRRPC0O`) | Both sources, re-rank by domain |
| `definition` | Billypedia (`ZCSAKEVYKK`) as **context enrichment** only | Retrieve top-1 Billypedia passage as background context, then retrieve help center for answer |
| `lookup` | pricing (`SWYMRRPC0O`) | Pricing source only |
| `escalation` | skip retrieval | Route directly to escalation node |
| `low_confidence` | all three sources | Fallback to flat search (current behaviour) |

**Key insight:** Billypedia is never the primary retrieval target. For `definition` queries it provides a context frame; the actual answer still comes from help center articles. This prevents glossary pages from crowding out instructional articles.

### Offline phase — build intent centroids

**Input:** golden 597 queries with `compare_category` labels + the 4,700-item BKH pool (has domain/intent labels).

```python
from sentence_transformers import SentenceTransformer
import numpy as np, json

model = SentenceTransformer("intfloat/multilingual-e5-base")

# Load exemplar queries per intent_type (from BKH labelled pool)
exemplars = {
    "how_to":     [...],   # "Hvordan opretter jeg en faktura?"
    "definition": [...],   # "Hvad er bankafstemning?"
    "regulatory": [...],   # "Hvornår skal jeg indberette moms?"
    "lookup":     [...],   # "Hvad koster Pro-abonnementet?"
    "escalation": [...],   # "Jeg vil gerne tale med en person"
}

centroids = {
    k: model.encode(queries, normalize_embeddings=True).mean(axis=0)
    for k, queries in exemplars.items()
}
np.savez("data/corpus/datastores/intent_centroids.npz", **centroids)
```

### Runtime classifier

```python
# src/support_agents/hc_lg/source_router.py
import numpy as np
from sentence_transformers import SentenceTransformer

SOURCE_MAP = {
    "how_to":     ["help_center"],
    "definition": ["help_center", "billypedia"],   # billypedia = context enrichment
    "regulatory": ["help_center", "pricing"],
    "lookup":     ["pricing"],
    "escalation": [],
}
CONFIDENCE_FLOOR = float(os.getenv("ROUTER_CONFIDENCE_FLOOR", "0.55"))

def route(query: str, model: SentenceTransformer, centroids: dict) -> tuple[str, list[str]]:
    vec = model.encode([query], normalize_embeddings=True)[0]
    sims = {k: float(vec @ c) for k, c in centroids.items()}
    best = max(sims, key=sims.get)
    if sims[best] < CONFIDENCE_FLOOR:
        return "low_confidence", ["help_center", "pricing", "billypedia"]
    return best, SOURCE_MAP[best]
```

`ROUTER_CONFIDENCE_FLOOR` maps directly to the existing `ROUTING_CONFIDENCE_THRESHOLD` pattern — low-confidence routes fall through to flat search.

### Ablation: do we need an LLM for source routing?

**Hypothesis:** embedding centroid classification (free at inference time) matches LLM routing quality on source selection, making `LLM_PLANNER=true` unnecessary for this decision.

| Variant | Classifier | Cost | Ablation flag |
|---|---|---|---|
| A (baseline) | Flat search, all 3 sources | baseline | `ROUTER_ENABLED=false` |
| B | Rule-based keyword map | ~0ms, free | `ROUTER_MODE=keyword` |
| C | Embedding centroid (this plan) | ~1ms, free | `ROUTER_MODE=embedding` |
| D | LLM classifier (`LLM_PLANNER`) | +1 LLM call | `ROUTER_MODE=llm` |
| E | Cache → embedding → LLM fallback | tiered | `ROUTER_MODE=tiered` |

Run variants B–D against the golden 597, comparing:
- `source_precision` — did we retrieve from the right source?
- `MRR@5` — did the right article rank in top 5?
- `composite` quality score
- latency

If B ≈ C ≈ D on quality: ship B (keyword, zero infra). If C > B and C ≈ D: ship C. Only invest in D if LLM routing shows a meaningful quality lift.

---

## Eval — what to measure

Run against `hackathon_eval.jsonl` (500 labeled queries from the golden dataset pipeline).

| Metric | Target |
|--------|--------|
| Cache hit rate | Report as % of `answerable` queries |
| Hit quality | `answer_relevancy` + `completeness` + `grounding` (calibrated tier) on cache-served answers — should match or beat baseline composite |
| Latency on hits | ≤ 500ms end-to-end (embed only, no LLM) |
| Miss path MRR | Must not regress vs. `SEMANTIC_CACHE_ENABLED=false` |

### Threshold sweep

Run the 50-task eval at `[0.75, 0.80, 0.85, 0.90, 0.95]`. Plot hit rate vs. composite quality. Pick the threshold that maximises `hit_rate × quality` without degrading miss-path MRR.

### AB notebook cell additions

In `hackathon_ab.ipynb`, add a cell that splits results into `cache_hit == True` vs `cache_hit == False` subsets and shows separate composite scores + MRR for each.

---

## Merge criteria

- ΔMRR ≥ 0 on the 500-task run (miss path must not regress)
- Cache hit composite ≥ baseline composite on the hit subset
- Latency on cache hits ≤ 500ms
- Default: `SEMANTIC_CACHE_ENABLED=false`

---

## Hackathon day sequence

### Pre-hackathon (requires golden dataset pipeline complete)
- [ ] `semantic_cache_seed.jsonl` built and validated
- [ ] `build_semantic_cache.ipynb` run → `semantic_cache.npz` committed to Drive / repo LFS
- [ ] `sentence-transformers` + deps pinned in `pyproject.toml`
- [ ] `SEMANTIC_CACHE_*` vars added to `.env.hackathon.example`

### Day 1 — Build
- [ ] Implement `hc_lg/semantic_cache.py`
- [ ] Add `cache_hit` + `cache_similarity` to `State`
- [ ] Wire `cache_node` into `agent.py`
- [ ] Smoke test: send 5 queries from the seed set, confirm hits; send 5 novel queries, confirm misses
- [ ] Run 50-task eval at default threshold

### Day 1–2 — Tune
- [ ] Threshold sweep
- [ ] Grade cache hits with calibrated tier (`--tier calibrated`) on a 20-query sample

### Day 2 — Demo
- [ ] AB notebook: hit rate chart, latency improvement, 3 hit/miss examples
- [ ] 500-task final eval if hit rate ≥ 10% and quality holds

---

## Open questions

- **Cache staleness**: if Billy product changes, cached answers become wrong. Add a `build_date` field to the npz and log a warning if the file is > 30 days old. Rebuild cadence TBD.
- **Language mismatch**: seed is Danish; if a user writes in English, similarity will be lower and queries will fall through to CRAG — which is correct behaviour. Track hit rate by detected `query_language` in the AB notebook to confirm.
- **Seed size**: if the golden dataset pipeline yields < 50 high-scoring rows (e.g. BKH responses are generally low quality), the cache hit rate on real traffic will be negligible. In that case, expand the seed by running the SA agent on the full 500-query stratified set and using its responses (rather than original BKH responses) as the cache source.
