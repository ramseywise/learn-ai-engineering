---
origin: notion-export
sources:
  - own work notes (support-agent RAG project)
  - https://aclanthology.org/2023.nlposs-1.24/
confidence: medium
cleaned: 2026-11-01
---
# 10 — Semantic cache for support agents

Tallybook's support bot answers "how do I get a refund on my annual plan?" dozens of times a day, in dozens of wordings, and each time it runs the whole pipeline: rewrite, retrieve, grade, generate. In our project that corrective round trip took about 3 to 6 seconds and at least two LLM calls for an answer the system had already produced and graded. An exact-match cache does not help, because no two customers type the same sentence. So you embed the question and reuse the stored answer when a past question is close enough.

The danger is the phrase "close enough". A customer asks about cancelling an invoice, the nearest stored question is about cancelling a subscription, and the bot confidently tells them how to close their account. Retrieval failures tend to look like a weak answer. A cache failure looks like a perfect answer to a different question, delivered in 50 milliseconds, with nothing downstream to catch it. The whole design of this chapter follows from that asymmetry.

The first half is the idea rebuilt on Tallybook, with a real small embedder and measured numbers. The second half keeps the original plan from our support-agent project, which is a useful example of how to scope such an experiment: a hypothesis, a flag, an ablation and merge criteria. The cache idea has a citable open-source origin in [GPTCache](https://aclanthology.org/2023.nlposs-1.24/) (Bang, NLP-OSS workshop at EMNLP 2023).

> **Hackathon experiment slot.** Zero-RAG-cost path for queries that closely match the golden dataset.
>
> **Prerequisite**: `golden-dataset.md` pipeline must complete first — specifically `semantic_cache_seed.jsonl` (high-scoring SA responses, composite ≥ 0.75).
>
> **Hypothesis**: A meaningful fraction of incoming queries are paraphrases of already-answered questions from the golden set. Routing those directly to a cache hit saves the full CRAG round-trip (~3–6s, 2+ LLM calls) without quality loss because the cached answers are already grader-validated.

---

## How it works — 3-tier pipeline

```text
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

## A cache in thirty lines

The mechanism is a matrix multiply. Store normalised question vectors, multiply by the new question's vector, and take the best row. With a few hundred rows there is no reason for an ANN index: the project's seed held about 150 to 200 rows, and [note 09](09-vector-database-comparison.md#how-far-exact-search-goes) shows that a scan of 10,000 vectors takes a fraction of a millisecond. Each row keeps what it needs later: the answer, the documents behind it, and the date it was built.

```python
import numpy as np
from fastembed import TextEmbedding

model = TextEmbedding("BAAI/bge-small-en-v1.5")


def encode(texts: list[str]) -> np.ndarray:
    return np.array(list(model.embed(texts)))         # unit vectors, 384 dimensions


SEED = [("How do I get a refund on my annual plan?", "Within 30 days, in full. See kb-04.", ["kb-04"]),
        ("How do I cancel my subscription?", "Settings, then Plan. See kb-06.", ["kb-06"]),
        ("How do I reset my password?", "Use the sign-in page link. See kb-15.", ["kb-15"])]
matrix = encode([q for q, _, _ in SEED])


def lookup(query: str, threshold: float = 0.85):
    sims = matrix @ encode([query])[0]
    best = int(sims.argmax())
    hit = sims[best] >= threshold
    return (SEED[best][1] if hit else None), SEED[best][0], round(float(sims[best]), 3)


for q in ["Can I get my money back for the yearly plan?",
          "how can I end my subscription",
          "How do I cancel an invoice?",
          "What is the VAT rate in Germany?"]:
    answer, nearest, sim = lookup(q)
    print(f"{sim:.3f} {'HIT ' if answer else 'miss'} {q}\n      nearest: {nearest}")
```

```text
0.929 HIT  Can I get my money back for the yearly plan?
      nearest: How do I get a refund on my annual plan?
0.951 HIT  how can I end my subscription
      nearest: How do I cancel my subscription?
0.809 miss How do I cancel an invoice?
      nearest: How do I cancel my subscription?
0.526 miss What is the VAT rate in Germany?
      nearest: How do I get a refund on my annual plan?
```

The first two are the cache doing its job. The last is an easy miss. The third is the interesting one: at 0.809 the invoice question stays below the default threshold, but only by a small margin.

---

## The threshold has no clean setting

How much margin is there in general? Measure it. The labelled set below has twelve true paraphrases of six seed questions, twelve near misses (same shape, different meaning), and four unrelated questions. The set is small and written by hand to be hard, so read it as a stress test and not as a traffic estimate.

```python
import numpy as np
from fastembed import TextEmbedding

model = TextEmbedding("BAAI/bge-small-en-v1.5")


def encode(texts: list[str]) -> np.ndarray:
    return np.array(list(model.embed(texts)))


SEED = ["How do I get a refund on my annual plan?", "How do I cancel my subscription?",
        "How do I reset my password?", "How do I export my invoices as CSV?",
        "Why does my bank feed say BANK-112?", "How do I invite an accountant to my team?"]
SAME = [("Can I get my money back for the yearly plan?", 0),
        ("what's the refund process for an annual subscription", 0),
        ("I want to cancel my subscription", 1), ("how can I end my subscription", 1),
        ("forgot my password, how do I reset it", 2), ("password reset steps", 2),
        ("download invoices to a csv file", 3), ("can I export invoices to CSV", 3),
        ("what does BANK-112 mean on my bank feed", 4), ("my bank feed shows error BANK-112", 4),
        ("add my accountant to the team", 5), ("how do I give my accountant access", 5)]
NEAR = ["How do I get a refund on my monthly plan?", "How do I issue a refund to my customer?",
        "How do I cancel an invoice?", "How do I cancel a team member's seat?",
        "How do I reset my API key?", "How do I change my password policy for the team?",
        "How do I export my customers as CSV?", "How do I import invoices from a CSV?",
        "Why does my bank feed say BANK-113?", "Why does my bank feed show duplicate entries?",
        "How do I remove an accountant from my team?", "How do I invite a client to view an invoice?"]
FAR = ["What is the VAT rate for Germany?", "how do webhooks retry",
       "what does HTTP-429 mean", "Do you offer a nonprofit discount?"]

seed = encode(SEED)
same = encode([q for q, _ in SAME]) @ seed.T
same_top = same.max(axis=1)
same_right = same.argmax(axis=1) == np.array([i for _, i in SAME])
near_top = (encode(NEAR) @ seed.T).max(axis=1)
far_top = (encode(FAR) @ seed.T).max(axis=1)

print("threshold  good hits /12  false hits /12  unrelated hits /4")
for t in (0.70, 0.75, 0.80, 0.85, 0.90, 0.95):
    print(f"{t:9.2f}  {int(((same_top >= t) & same_right).sum()):13d}  "
          f"{int((near_top >= t).sum()):14d}  {int((far_top >= t).sum()):17d}")
print("highest near misses:")
for i in np.argsort(-near_top)[:4]:
    print(f"  {near_top[i]:.3f} {NEAR[i]}")
print("lowest paraphrases:")
for i in np.argsort(same_top)[:3]:
    print(f"  {same_top[i]:.3f} {SAME[i][0]}")
```

```text
threshold  good hits /12  false hits /12  unrelated hits /4
     0.70             12              12                  0
     0.75             12              10                  0
     0.80             12               7                  0
     0.85             10               4                  0
     0.90              9               4                  0
     0.95              4               0                  0
highest near misses:
  0.935 How do I import invoices from a CSV?
  0.930 How do I get a refund on my monthly plan?
  0.929 Why does my bank feed say BANK-113?
  0.912 How do I export my customers as CSV?
lowest paraphrases:
  0.803 how do I give my accountant access
  0.849 what's the refund process for an annual subscription
  0.883 password reset steps
```

Three things stand out. Unrelated questions are easy, topping out near 0.63, so the threshold's job is not to reject those. The two distributions that matter overlap: "import invoices" scores higher than a true paraphrase like "password reset steps", and BANK-113 matches BANK-112 at 0.929. And at 0.85, the default from the project plan, the sweep serves four wrong answers out of twelve hard cases. Even 0.90 has the same four. Only at 0.95 do false hits reach zero, and by then just four paraphrases of twelve still hit. These numbers belong to bge-small on this set. The project used `multilingual-e5-base` on Danish queries, and a threshold never moves between models.

This is why the plan below sweeps the threshold over `[0.75, 0.80, 0.85, 0.90, 0.95]` and does not trust a default. It is also why a cost argument should decide the setting. A false hit costs a wrong answer and maybe a support ticket. A miss costs a few seconds and the price of the normal pipeline. So start high, accept a low hit rate, and lower it only with evidence.

---

## Guarding the hit

A threshold looks at one number. A cheap second check can catch the near misses that matter most: any identifier in the question must also be in the stored question. Error codes, plan names and dates are exactly the tokens that embeddings blur, as [note 03](03-keyword-semantic-and-hybrid-search.md) showed, and they are what changes the answer.

```python
import re

CRITICAL = re.compile(r"\b[A-Z]{2,}-\d+\b|\b(?:annual|yearly|monthly|import|export)\b", re.I)
SYNONYM = {"yearly": "annual"}


def terms(text: str) -> set[str]:
    found = {t.lower() for t in CRITICAL.findall(text)}
    return {SYNONYM.get(t, t) for t in found}


def guard(query: str, stored: str) -> bool:
    return terms(query) == terms(stored)


PAIRS = [("what does BANK-112 mean on my bank feed", "Why does my bank feed say BANK-112?"),
         ("Why does my bank feed say BANK-113?", "Why does my bank feed say BANK-112?"),
         ("Can I get my money back for the yearly plan?", "How do I get a refund on my annual plan?"),
         ("How do I get a refund on my monthly plan?", "How do I get a refund on my annual plan?"),
         ("How do I import invoices from a CSV?", "How do I export my invoices as CSV?"),
         ("How do I reset my API key?", "How do I reset my password?")]
for query, stored in PAIRS:
    print(f"{'serve' if guard(query, stored) else 'block'}  {query}")
```

```text
serve  what does BANK-112 mean on my bank feed
block  Why does my bank feed say BANK-113?
serve  Can I get my money back for the yearly plan?
block  How do I get a refund on my monthly plan?
block  How do I import invoices from a CSV?
serve  How do I reset my API key?
```

The rule catches the code, the plan and the direction, and the last line shows where it stops: "API key" against "password" passes, because neither word is on the list. A guard list is a set of known hazards that you grow from reviewed false hits. It can never be complete, so a cache in production also needs a sampled review of what it served.

---

## Staleness and scope

A cached answer is a snapshot of the documents it came from. Our project's open question was to log a warning when the file is older than 30 days. Age alone is a weak signal, since an answer can go wrong the day after the build and stay correct for years. If each row records its source documents, you can invalidate by what actually changed.

```python
from dataclasses import dataclass
from datetime import date

from ragkit import DOC_BY_ID


@dataclass
class Entry:
    question: str
    sources: list[str]
    built: str
    scope: str = "public"


CACHE = [Entry("How do I get a refund?", ["kb-04"], "2026-10-01"),
         Entry("How do I rotate an API key?", ["kb-02"], "2026-01-10"),
         Entry("What is my outstanding balance?", ["kb-11"], "2026-10-20", scope="workspace-77")]


def valid(entry: Entry, today: str, caller: str, max_age_days: int = 365) -> tuple[bool, str]:
    if entry.scope not in ("public", caller):
        return False, "other tenant"
    if any(DOC_BY_ID[s].updated > entry.built for s in entry.sources):
        return False, "source changed since build"
    if (date.fromisoformat(today) - date.fromisoformat(entry.built)).days > max_age_days:
        return False, "too old"
    return True, "serve"


for e in CACHE:
    print(f"{e.question:36s} {DOC_BY_ID[e.sources[0]].updated} built {e.built}  "
          f"{valid(e, '2026-11-01', 'workspace-12')[1]}")
```

```text
How do I get a refund?               2026-10-01 built 2026-10-01  serve
How do I rotate an API key?          2026-06-02 built 2026-01-10  source changed since build
What is my outstanding balance?      2026-04-08 built 2026-10-20  other tenant
```

The third row is the security version of a false hit. Caching a personal answer in a shared cache hands one customer's balance to another. The project's seed held only general support answers, which is the simple rule to copy: cache only answers that do not depend on who is asking. If you must cache per user, make the tenant part of the key and check it before serving, as this code does.

---

## Offline phase — build the cache index

**Input**: `data/datasets/bkh/semantic_cache_seed.jsonl` (output of the golden dataset pipeline — grader-validated SA responses, composite ≥ 0.75)

**Notebook**: `nbks/sa/build_semantic_cache.ipynb`

### Embed queries

```python
# illustrative: needs the project's semantic_cache_seed.jsonl and a download of multilingual-e5-base
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("intfloat/multilingual-e5-base")  # handles Danish
queries = [row["query"] for row in seed]
embeddings = model.encode(queries, normalize_embeddings=True)  # (N, 768) float32
```

No clustering needed — the golden dataset pipeline already deduplicated via stratification. Keep all rows.

### Persist

```python
# illustrative: needs `seed` and `embeddings` from the block above
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

**File**: `src/support_agents/kb_lg/semantic_cache.py`

```python
# illustrative: needs semantic_cache.npz from the offline phase and sentence-transformers
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
# illustrative: fields on the project's LangGraph State
cache_hit: bool          # True when semantic cache short-circuited retrieval
cache_similarity: float  # cosine sim of match (0.0 when no hit)
```

### `agent.py`

New node and updated routing:

```python
# illustrative: needs the project's kb_lg package and LangGraph State
from kb_lg.semantic_cache import lookup as _cache_lookup

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
# illustrative: extends the project's LangGraph builder
_builder.add_node("cache", cache_node)
_builder.add_conditional_edges("planner", route_after_planner,
    {"cache": "cache", "respond": "respond"})
_builder.add_conditional_edges("cache", route_after_cache,
    {"end": END, "retrieve": "retrieve"})
```

---

## Source routing — Tier 2

> The taxonomy below is the full Phase C spec from `kb-content-taxonomy.md` (now archived). The same `multilingual-e5-base` model loaded for the cache is reused — no second model, no LLM call.

A miss does not have to mean "search everything". Once a query vector exists, it costs almost nothing to compare it with a few more vectors: one average per intent, built from example questions. The router then picks the source before retrieval runs. Here it is on Tallybook, with a floor that sends unsure queries to flat search. The labelled test queries are separate from the exemplars.

```python
import numpy as np
from fastembed import TextEmbedding

model = TextEmbedding("BAAI/bge-small-en-v1.5")


def encode(texts: list[str]) -> np.ndarray:
    return np.array(list(model.embed(texts)))


EXEMPLARS = {
    "how_to": ["How do I create an invoice?", "How do I add a team member?", "How do I export my data?"],
    "error": ["I get an error when calling the API", "My bank feed stopped working", "The invoice email bounced"],
    "regulatory": ["When do I have to report VAT?", "What VAT applies to EU customers?", "Do invoice numbers have to be sequential by law?"],
    "lookup": ["How much does the Pro plan cost?", "What is the API rate limit?", "How many seats does the Scale plan include?"],
    "escalation": ["I want to talk to a person", "Please connect me to support staff", "This is unacceptable, get me a manager"],
}
SOURCE_MAP = {"how_to": ["help_center"], "error": ["help_center"],
              "regulatory": ["help_center", "pricing"], "lookup": ["pricing"], "escalation": []}
names = list(EXEMPLARS)
centroids = np.array([encode(q).mean(axis=0) for q in EXEMPLARS.values()])
centroids /= np.linalg.norm(centroids, axis=1, keepdims=True)
FLOOR = 0.55


def route(query: str) -> tuple[str, list[str], float]:
    sims = centroids @ encode([query])[0]
    best, score = names[int(sims.argmax())], float(sims.max())
    if score < FLOOR:
        return "low_confidence", ["help_center", "pricing"], score
    return best, SOURCE_MAP[best], score


TEST = [("how do I invite my accountant", "how_to"), ("how can I change my invoice template", "how_to"),
        ("webhook deliveries keep failing", "error"), ("I am seeing HTTP-403 on every call", "error"),
        ("do I charge VAT to a German company", "regulatory"), ("what are the rules for keeping invoices", "regulatory"),
        ("what does the Scale plan cost per month", "lookup"), ("how many API calls can I make", "lookup"),
        ("let me speak with a human", "escalation"), ("I need a real person to help me", "escalation")]
right = 0
for query, label in TEST:
    got, sources, score = route(query)
    right += got == label
    print(f"{'ok ' if got == label else 'BAD'} {query:42s} {got:14s} {score:.2f} {sources}")
print(f"{right}/{len(TEST)} correct")
```

```text
ok  how do I invite my accountant              how_to         0.79 ['help_center']
ok  how can I change my invoice template       how_to         0.78 ['help_center']
ok  webhook deliveries keep failing            error          0.70 ['help_center']
ok  I am seeing HTTP-403 on every call         error          0.72 ['help_center']
ok  do I charge VAT to a German company        regulatory     0.83 ['help_center', 'pricing']
ok  what are the rules for keeping invoices    regulatory     0.80 ['help_center', 'pricing']
ok  what does the Scale plan cost per month    lookup         0.81 ['pricing']
ok  how many API calls can I make              lookup         0.75 ['pricing']
ok  let me speak with a human                  escalation     0.84 []
ok  I need a real person to help me            escalation     0.84 []
10/10 correct
```

ROUTER_PROSE

### Taxonomy spec

```text
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
| `definition` | ProductWiki (`KB_GLOSSARY`) as **context enrichment** only | Retrieve top-1 ProductWiki passage as background context, then retrieve help center for answer |
| `lookup` | pricing (`SWYMRRPC0O`) | Pricing source only |
| `escalation` | skip retrieval | Route directly to escalation node |
| `low_confidence` | all three sources | Fallback to flat search (current behaviour) |

**Key insight:** ProductWiki is never the primary retrieval target. For `definition` queries it provides a context frame; the actual answer still comes from help center articles. This prevents glossary pages from crowding out instructional articles.

### Offline phase — build intent centroids

**Input:** golden 597 queries with `compare_category` labels + the 4,700-item support corpus A pool (has domain/intent labels).

```python
# illustrative: needs the project's labelled Danish exemplars and a download of multilingual-e5-base
from sentence_transformers import SentenceTransformer
import numpy as np, json

model = SentenceTransformer("intfloat/multilingual-e5-base")

# Load exemplar queries per intent_type (from support corpus A labelled pool)
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
# illustrative: needs `centroids` from the offline phase and a download of multilingual-e5-base
# src/support_agents/kb_lg/source_router.py
import os

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
- [ ] Implement `kb_lg/semantic_cache.py`
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

- **Cache staleness**: if Product product changes, cached answers become wrong. Add a `build_date` field to the npz and log a warning if the file is > 30 days old. Rebuild cadence TBD.
- **Language mismatch**: seed is Danish; if a user writes in English, similarity will be lower and queries will fall through to CRAG — which is correct behaviour. Track hit rate by detected `query_language` in the AB notebook to confirm.
- **Seed size**: if the golden dataset pipeline yields < 50 high-scoring rows (e.g. support corpus A responses are generally low quality), the cache hit rate on real traffic will be negligible. In that case, expand the seed by running the SA agent on the full 500-query stratified set and using its responses (rather than original support corpus A responses) as the cache source.

---

## Pitfalls

- **Trusting a default threshold.** Symptom: a good hit rate and an occasional confidently wrong answer that nobody reports. Sweep on labelled near misses for your model, as above.
- **Near misses that differ in one token.** Symptom: BANK-113 gets the BANK-112 answer. Guard identifiers, plan names and directions with an exact check.
- **Caching personal answers.** Symptom: one customer sees another's data. Cache only general answers, or put the tenant in the key.
- **A cache that outlives its sources.** Symptom: old policy served after the document changed. Store source ids and invalidate when a source is updated; add an age limit as a backstop.
- **Seeding from unvalidated answers.** Symptom: the cache serves your worst answers fast and forever. Seed only from graded answers, as the project did with a composite of 0.75 or higher.
- **Measuring only hit rate.** Symptom: hit rate rises and support tickets rise with it. Score the hit subset separately, as the AB cell below does.
- **Regressing the miss path.** Symptom: cached queries look great while the rest got slower or worse. Require MRR on misses to hold.
- **Building a second classifier.** Symptom: eval coverage and runtime routing drift apart. Share one classifier artifact, as the plan says.

---

## Try it

1. In the threshold sweep, add a `SAME` entry `("reset password", 2)` and a `NEAR` entry `("How do I reset my password on the mobile app?")`. Predict the effect at 0.85, then run it.
2. Extend `CRITICAL` so the `"How do I reset my API key?"` case is blocked. What does your rule cost on the paraphrases?
3. In the router block, set `FLOOR = 0.80`. What happens to the routes, and what does that cost?
4. Using the project's numbers, a miss costs about 4.5 s and two LLM calls. If you had a hit rate of 30% with one wrong answer per 100 hits, what would you need to know to decide whether to ship?

<details>
<summary>Answers</summary>

ANSWERS_10

</details>

---

## Interview checklist

| Question | Answer |
|---|---|
| What does a semantic cache save? | The whole retrieval and generation path on a hit: in our project about 3 to 6 s and two or more LLM calls, for the price of one embedding and a matrix multiply. |
| How does it differ from an exact cache? | It matches on meaning, so it catches paraphrases, and it can match wrongly. An exact cache never serves the wrong answer. |
| What is the main risk? | A false hit: a near-identical question with a different meaning gets a confident wrong answer, and no later stage checks it. |
| How do you set the threshold? | Sweep it on labelled paraphrases and hard near misses for your model, then choose on the relative cost of a wrong answer and a miss. |
| Why not always use 0.95? | On our stress test it cut false hits to zero but kept only 4 of 12 paraphrases. A cache that rarely hits is cheap and useless. |
| Does a threshold transfer across embedders? | No. Cosine scales differ by model and by language. |
| What goes in a cache row? | The question vector, the answer, the source ids, the build date, a quality score, and the scope if not public. |
| How do you handle staleness? | Invalidate rows when a source document changes, with an age limit as a backstop. |
| Do you need an ANN index for it? | Not at a few hundred rows. A matrix multiply is enough. |
| What is a centroid router? | The mean embedding of example queries per intent; a query takes the closest one, or falls to flat search below a floor. It reuses the embedding with no LLM call. |
| How do you decide between keyword, centroid and LLM routing? | Run an ablation on source precision, MRR, quality and latency. Ship the cheapest variant that ties. |
| What should block a merge? | Regression on the miss path, a hit subset below baseline quality, or hit latency above budget. |

---

## Next

[11 — Retrieval improvements](11-retrieval-improvements.md): what an ablation run says about which retrieval changes are worth making.
