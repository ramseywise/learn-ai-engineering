# Support Agent Feature Parity

**Last updated:** June 2024  
**Source:** Live codebase audit — hc_adk, hc_lg, hc_rag vs production `va-agents/help-center-assistant` (TypeScript).

> **Comparison target:** `va-agents/help-center-assistant` — the TS help-center agent in production (Bedrock HYBRID KB, single-turn, no CRAG, no post-gen grounding).  
> `chat-agent/agentic-rag` (Intercom RAG template) is referenced only as an inspiration source for graders and the 3-layer guardrail pattern — it is not the production comparison target.

---

## Feature Matrix

| Feature | VA help-center-assistant (TS) | hc_adk | hc_lg | hc_rag |
|---|---|---|---|---|
| **Knowledge source** | Bedrock HYBRID KB | Bedrock HYBRID KB | Bedrock HYBRID KB | DuckDB / Chroma / OpenSearch |
| **Retrieval** | Bedrock managed (BM25 + vector) | Bedrock managed | Bedrock managed | BM25 + multilingual-e5 + RRF fusion |
| **Reranking** | Bedrock managed | Bedrock managed | ColBERT / cross-encoder / LLM listwise | ColBERT / cross-encoder / LLM listwise |
| **CRAG / reflection loop** | ❌ | ✅ `CRAG_ENABLED` flag — `grade_relevance` + `rewrite_query` tools (`tools.py:76`) | ✅ `qa_policy` confidence gates + graph nodes (`nodes/eval.py`) | ✅ pre-gen confidence gate (`agent.py:56`) |
| **Multi-query reformulation** | ❌ | ❌ no `MULTI_QUERY` flag | ✅ `MULTI_QUERY` flag (`config.py:29`) — 2 Danish keyword variants | ❌ |
| **Layer 1 — Input guardrail** | ✅ regex + PII | ✅ `run_input_guard()` (`main.py:97`) | ✅ `run_input_guard()` (`main.py:180`) | ✅ `_GuardrailMiddleware` (`main.py:79`) |
| **Layer 3 — LLM domain classifier** | ❌ | ❌ | ❌ | ❌ |
| **Layer 4 — Post-gen grounding** | ❌ | ✅ `run_output_guard()` (`main.py:256`) | ✅ `grounding_node` (`graph/nodes/grounding.py`) | ✅ `run_output_guard()` (`agent.py:125`) |
| **Structured output** | TS typed schema | ❌ post-hoc `_extract_response()` (`main.py:388`) | ✅ `with_structured_output(AssistantResponse)` (`answer.py:35`) | ✅ `with_structured_output(AssistantResponse)` (`agent.py:94`) |
| **Multi-turn support** | ❌ single-turn | ✅ ADK `InMemorySession` | ✅ SQLite/PostgreSQL checkpointer | Partial |
| **Langfuse observability** | ❌ LangSmith | ✅ manual `lf.trace()` | ✅ `CallbackHandler` spans | ✅ `@observe` decorator |
| **PROMPT_VERSION in trace** | ❌ | ✅ | ✅ | ✅ |
| **PII redaction** | Partial | ✅ shared `input_pipeline.py` | ✅ | ✅ |

---

## Where Galactus Exceeds VA

All three Python agents are **ahead of the TS baseline** on:

- **Layer 4 post-gen grounding** — VA has none; all three galactus agents enforce citation grounding on every response
- **CRAG loop** — hc_adk and hc_lg both have reflection/retry; VA has no retrieval quality loop
- **Langfuse observability** — VA uses LangSmith; galactus has per-turn traces with score write-back
- **Structured output contract** — hc_lg and hc_rag use `with_structured_output(AssistantResponse)` natively; VA relies on TS type casting

---

## Remaining Prod Gaps

Ordered by priority. None are blockers for the ablation study, but all are needed before recommending a galactus agent for production.

| Item | Agent(s) | Location | Effort |
|---|---|---|---|
| `MULTI_QUERY` flag — hc_adk missing parity with hc_lg | hc_adk | `config.py`, `retrieval.py` | Low–Medium |
| Native `output_schema=AssistantResponse` — eliminate post-hoc parsing | hc_adk | `main.py:388`, `agent.py` | Low–Medium |
| Layer 3 LLM domain classifier (from chat-agent's 3-layer pattern) | all | `guardrails/input_pipeline.py` | Medium |
| Langfuse per-guardrail-layer child spans (block rate dashboardable) | all | `guardrails/` + each `main.py` | Medium |
| Passage ID continuity (P1, P2… labels persist across turns) | all | answer nodes / schema | Medium |
| `CorrectiveLoopEfficiency` grader — measures CRAG loop cost vs quality | evals | `evals/graders/metrics/` | Medium |
| LangSmith dead code removal | all | each agent | Low |
| Prompt versioning — Langfuse prompt fetch with fallback | all | each `main.py` | Low |
| `langdetect` integration (already in `pyproject.toml`) | all | each agent | Low |

---

## Eval Coverage

Galactus is **ahead of chat-agent** on evals — it has more graders, a calibrated voting layer, and full retrieval metrics that chat-agent lacks.

| Grader / Metric | chat-agent | galactus |
|---|---|---|
| Answer relevancy | ✅ | ✅ `AnswerRelevancyGrader` (voted) |
| Faithfulness / grounding | ✅ claim-level | ✅ `GroundingGrader` (post-gen, offline) |
| F1 Correctness (token P/R) | ✅ | ✅ `F1CorrectnessGrader` (`heuristic/correctness.py:152`) |
| Confidence calibration | ✅ | ✅ `compute_confidence_calibration()` (`metrics/suite.py:42`) |
| Corrective loop efficiency | ✅ | ❌ not implemented |
| Completeness | ❌ | ✅ `CompletenessGrader` (voted) |
| Escalation | ❌ | ✅ `EscalationGrader` (voted) |
| Friction / EPA | ❌ | ✅ `FrictionGrader`, `EPAGrader` |
| Source match / MRR / NDCG | ❌ | ✅ retrieval metrics (free, URL-based) |
| Routing (Strand A) | ❌ | ✅ `AgentEvaluator` trajectory scoring |
| RAGAS faithfulness + context precision | Partial | ✅ voted variants in registry |