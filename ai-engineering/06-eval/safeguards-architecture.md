# Safeguards Architecture — Five Protection Layers

**Last updated:** May 2026

Every agent in galactus passes through up to five protection layers before a response reaches the user. This doc describes how those layers work, where each one lives in the codebase, and what gaps remain compared to the TS production system.

> **Scope:** High-level architecture overview and layer definitions. For Layer 4 implementation detail (grounding tier pipeline, hard/soft fail table, `enforce_grounding()` internals), see [invocation-flow.md](invocation-flow.md).

---

---

## Context: What va-agents TS implemented

The TS production system added a runtime `enforceGrounding` after-model callback with a three-tier structural verification model:

| Tier | Check | Mechanism | On fail |
|---|---|---|---|
| **1** | Citation IDs exist in retrieved set | Set membership O(n) | Hard fail → escalation |
| **2** | Claim-level citations declared in top-level array | Cross-reference | Hard fail → escalation |
| **Missing citation guard** | KB called but no citations + no `insufficient_information` | Boolean | Hard fail → escalation |
| **3** | Supporting quotes appear verbatim in cited passage | Token overlap score | **Soft only — log/warn** |

The check runs in < 1ms (no LLM calls), rewrites the response in-flight to `{contactSupport: true, sources: []}` on hard fail. Tests are Jest unit tests with fake context/state objects — no I/O.

---

## Current state of galactus safeguards

### What exists

| Layer | Where | What it protects | When |
|---|---|---|---|
| Injection guard | `va_google_adk/agent.py:_guardrail_callback` | Prompt injection, jailbreaks | Pre-model (ADK callback) |
| Injection + PII guard | `va_langgraph/graph/nodes/guardrail.py` | Injection + PII redaction + size limit | Pre-LLM (LG node) |
| Routing confidence gate | `va_langgraph/graph/builder.py:_route_intent` | Low-confidence intent routing → direct | Post-analyze (routing) |
| Routing confidence gate | `hc_lg/agent.py:_llm_classify` | Low-confidence LLM intent → fallback | Pre-generation |
| CRAG confidence gate | `hc_lg/subgraphs/retrieval.py:confidence_gate` | Skips re-grading when top passage ≥ 0.7 | Pre-generation (retrieval) |
| Escalation regex | `va_google_adk/agent.py:_ESCALATION_RE` | Direct "talk to human" requests | Pre-model |
| Offline LLM grounding | `evals/graders/judges/grounding/grounding.py:GroundingGrader` | Semantic grounding score (LLM judge) | **Eval pipeline only** |

### Layer 4 status — gap closed

Layer 4 post-generation structural citation check is now implemented in all Python agents via `enforce_grounding()` in `src/support_agents/guardrails/grounding/`. Gap closed — see `src/support_agents/guardrails/grounding/` and `docs/support-agents/invocation-flow.md` for implementation detail.

```
TS va-agents:      [input guardrail] → [retrieval] → [generate] → [grounding check] → user
galactus hc_lg:    [input guardrail] → [CRAG gate] → [generate] → [grounding check] → user
galactus hc_adk:                      [retrieval]  → [generate] → [grounding check] → user
galactus va_lg:    [input guardrail] → [analyze]   → [domain]   → [grounding check] → user
```

### Schema difference: IDs vs URLs

The TS system uses `citations: string[]` (passage IDs) to cross-reference against the retrieved set. galactus uses `AssistantResponse.sources: list[Source]` where each Source has `{title, url}`. This means:

- TS: `cited_id ∈ retrieved_ids` (exact set membership)
- Python: `cited_url ∈ retrieved_urls` (URL string matching)

Both work — the Python check operates on URLs instead of opaque IDs. The Python schema is actually slightly better for observability (URLs are human-readable).

---

## Architecture analysis: Where to put the grounding check

### Option A: Embedded into each node/agent response handler

Merge the grounding check into the existing `format_node` or at the end of each domain subgraph.

**Pro:** Less boilerplate, no new files.
**Con:** Mixed concerns, hard to disable per-agent, untestable in isolation, invisible in graph visualization.

### Option B: Dedicated `grounding_check` node (LangGraph) / callback (ADK)

A dedicated LangGraph node inserted between domain subgraphs and `format`. For ADK, an `after_agent_callback` on the support agent.

**Pro:** Single responsibility, matches existing guardrail pattern, toggleable via env flag, independently testable, visible in LG graph diagram, can emit structured state for eval pipeline.
**Con:** Two more lines in the builder wiring.

### Option C: Separate "grounding validator" sub-agent with its own LLM call

A small agent that reads the response and passage text and scores grounding semantically.

**Pro:** Semantic understanding of grounding (not just structural).
**Con:** +1.5–3s latency, +$0.002–0.006 per call, the semantic evaluation already exists in the offline eval pipeline. The runtime check should be fast structural validation — semantic eval is the eval harness's job.

### Recommendation: Option B

**Use dedicated node/callback for all pipeline variants.** The pattern is already established in the codebase (`guardrail_node`, `_guardrail_callback`). A grounding node is the direct parallel for post-generation.

Do **not** use a separate sub-agent for runtime grounding. The `GroundingGrader` LLM judge belongs in the eval pipeline, not the hot path.

---

## The five protection layers (full picture)

```
Layer 1:  Pre-input     — injection + PII guardrail (exists)
Layer 2:  Pre-retrieval — routing confidence gate (exists, partial)
Layer 3:  Pre-generate  — retrieval quality gate / CRAG (exists in hc_lg, not hc_adk)
Layer 4:  Post-generate — structural citation check (✅ all agents via `guardrails/grounding/`)
Layer 5:  Escalation    — friction signal routing (partial: regex escalation exists,
                          but not wired to grounding failures or low-confidence signals)
```

Eval pipeline sits outside this hot path and provides the LLM-as-judge semantic layer (offline, batch).

---

## Limitations of the TS approach

1. **Tier 3 is soft-only.** The most semantically meaningful check (quote verbatim in passage) never triggers escalation. A model can fabricate a supporting quote with zero token overlap and still pass through. `score === 0` fabricated claims should be a configurable hard fail (`STRICT_QUOTE_CHECK=true`).

2. **`relevance_score` threshold is a warning, not a gate.** Self-rated confidence below 0.6 logs but does not escalate. Should be configurable: `GROUNDING_MIN_RELEVANCE=0.5` as a hard-fail threshold.

3. **No retrieval-side quality gate.** Unlike CRAG, grounding.ts improves nothing before generation — it only rejects bad responses. The Python CRAG is complementary and should be ported to hc_adk.

4. **Schema coupling.** Silently degrades if `citations`/`claims`/`supportingQuote` keys change. The `catch {}` eats parse errors — should at minimum log them.

5. **Missing citation guard only fires when KB returns results.** If the KB consistently returns poor passages, the model will always answer "from memory" and the guard won't fire. The retrieval-side gate (CRAG) is needed as the complementary check.

6. **No structured metrics output.** Grounding failures are console.warn/debug only — they don't feed into dashboards, alerting, or the eval pipeline.

---

## Metrics unlocked by proper grounding instrumentation

Adding structured failure logging to the grounding check enables metrics that currently don't exist at runtime:

| Metric | What it reveals | Where to route |
|---|---|---|
| `grounding.hallucination_rate` | % of responses citing un-retrieved passages | LangSmith / artefact_store |
| `grounding.missing_citation_rate` | % of KB-answered turns with no sources | Friction analysis (VIR-129) |
| `grounding.escalation_rate` | % of responses rewritten to contactSupport | Support team dashboard |
| `grounding.low_relevance_rate` | % of turns with relevance_score < threshold | Model quality signal |
| `grounding.zero_score_claims` | % of claims with no token overlap (fabricated) | Hallucination dataset seeding |

These are **not possible with the current offline-only GroundingGrader** — it only runs on sampled eval sets. Runtime grounding logging gives continuous production coverage.

---

## Connection to friction detection

The existing `evals/graders/judges/friction.py` and VIR-129 (friction signal analysis) depend on offline signals. Runtime grounding failures are a strong friction predictor:

- `hallucinated` citations → model is confused about KB content → likely produces a wrong answer → user repeats question
- `unansweredFromMemory` → KB coverage gap → user escalates
- `insufficient_information` + no `contactSupport` → graceful deflection opportunity missed

Routing these signals to the artefact store at runtime means friction analysis can be done on production traffic, not just eval samples.

---

## Confirm gate: HITL design for write operations (ADK)

**Status:** Blocked on write tools (test Billy account not provisioned). Design is complete.

`confirm: bool` exists in `AssistantResponse` schema but nothing gates write operations behind it. In TS va-agents, edit operations return `confirm: true` on the first call, the frontend shows an approval prompt, then the user re-sends to actually execute.

**Two-phase prompt design:**

- **Phase 1 (first call):** "When asked to edit/update a record, do NOT call the tool yet. Summarize the intended change clearly and set `confirm: true` in your response."
- **Phase 2 (confirmed call):** When the user message contains an affirmation ("yes", "confirm", "go ahead") after a prior `confirm: true` response, call the write tool.

The ADK `InvocationContext` / session state carries a `pending_action: Optional[dict]` between turns. Store the intended tool call params on phase 1, execute on phase 2.

**Files (when write tools land):**
- Add `pending_action: Optional[dict]` to session state schema in `agent.py`
- Add two-phase prompt addendum to each edit sub-agent (`invoice.py`, `customer.py`, `product.py`, `quote.py`)
- Wire in order: `invoice → customer → product → quote → email → invitation`

**P0 gap audit result (2026-05-09):** All other ADK feature gaps were already closed before the audit:
- Sources (Gap 2): `prompts/support_agent.txt` already extracts title/url/score ≥ 0.5
- Frustration detection (Gap 5): `va_assistant.txt` escalation rules already wired
- `table_type` (Gap 6): All domain agents already set it
- Charts (Gap 3): `insights_agent.txt` already has full `chart_data` rules
- Confirm gate design (Gap 4): `pending_action` stubbed as TODO comment in `agent.py:82`

The only real gap remaining is write tools (blocked on test account) and confirm gate wiring (blocked on write tools).

---

## TS Reference: Module Structure

```
help-center-assistant/
├── grounding/              ← content trust: did the model say something true?
│   ├── citation.ts         ← Tier 1+2: hallucinated IDs, cross-claim consistency
│   ├── quote.ts            ← Tier 3: verbatim quote with word-boundary checks
│   ├── audit.ts            ← Tier 4: diagnostics (relevance, language, URLs)
│   ├── result.ts           ← GroundingResult type
│   └── index.ts            ← enforceGrounding() — public API
│
├── guardrails/             ← pipeline safety: is the input safe?
│   ├── sanitize.ts         ← strip HTML, decode entities, remove control chars
│   ├── pii.ts              ← redact 21 patterns (email, phone, CPR, card, API keys...)
│   ├── injection.ts        ← 11-group injection detection
│   ├── index.ts            ← runInputGuard() — input pipeline entry point
│   └── output.ts           ← runOutputGuard() — wraps enforceGrounding(), typed result
│
├── __tests__/
└── help-center-assistant.ts   ← callbacks: wires guardrails + grounding into ADK
```

**Multi-agent boundary note:** `guardrails/` is correctly scoped per-agent today. When a second agent lands it must move to `src/middleware/guardrails/` — run once at `POST /api/chat`, not duplicated per-agent. Layer 4 grounding stays per-agent (output-specific).

---

## TS/Python Parity

| Feature | galactus (Python) | va-agents (TypeScript) |
|---|---|---|
| Sanitize step (HTML, control chars) | ✅ `sanitize.py` | ✅ `guardrails/sanitize.ts` |
| PII redaction | ✅ `pii_redaction.py` | ✅ `guardrails/pii.ts` |
| Injection detection | ✅ `prompt_injection.py` | ✅ `guardrails/injection.ts` |
| `sanitizeWarnings` in result | ✅ | ✅ |
| Score delta guard | ✅ `callbacks.py` | ✅ `help-center-assistant.ts` |
| Word-boundary fix (prefix + suffix + all occurrences) | ✅ `grounding/quote.py` | ✅ `grounding/quote.ts` |
| Suggestion URL check (Tier 4c) | ✅ `grounding/audit.py` | ✅ `grounding/audit.ts` |
| Grounding subpackage (citation/quote/audit) | ✅ `grounding/` | ✅ `grounding/` |
| `GroundingResult` typed return | ✅ | ✅ `grounding/result.ts` |
| `runOutputGuard()` wrapper | ✅ `output_pipeline.py` | ✅ `guardrails/output.ts` |
| Context caching | ❌ | ✅ `cache.ts` singleton |
| Context window pruning | ✅ `callbacks.py` | ✅ `history.ts` |
| Multi-language escalation | ✅ 7 languages (da/en/de/nl/sv/no/fi) | ✅ 9 languages |

---

## Latency Picture

| Path segment | Typical cost | Notes |
|---|---|---|
| Input guardrails (sanitize → PII → inject) | < 1ms | Negligible |
| AWS Bedrock retrieve + rerank | 500–1500ms | **Main bottleneck** |
| LLM call (Gemini + ThinkingLevel.LOW) | 800–2000ms | — |
| Grounding tiers 1–4 (post-LLM) | < 1ms | Tier 4c added negligible cost |
| Score delta guard (skip second LLM call) | −1000–2000ms | **Saves ~1–2s on dead-end queries** |

---

## Open questions

- [ ] Should `STRICT_QUOTE_CHECK` (Tier 3 hard fail) be on or off by default? Off in production to avoid false positives from paraphrasing; on in eval/staging.
- [ ] What is the right `GROUNDING_MIN_RELEVANCE` threshold? The TS code uses 0.6 as a warn threshold — test at 0.5 hard fail.
- [ ] Should grounding failures be stored in `artefact_store.py` (va_langgraph/va_google_adk pattern) or appended to eval JSONL directly?
- [ ] CRAG confidence gate needs porting to hc_adk — what's the right threshold? Currently hc_lg uses 0.7.
- [ ] For `hc_lg` specifically: does the grounding check run before or after the CRAG rewrite loop? Answer: after — the grounding check is on the final generated response, CRAG is on retrieved passages before generation.
