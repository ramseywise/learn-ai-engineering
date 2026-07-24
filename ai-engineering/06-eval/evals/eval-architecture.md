# Eval Architecture — Multi-Agent VA

> **Canonical reference:** `evals/README.md` — layout, flows, LangFuse integration, run commands.
> **This doc covers:** architectural decisions not in the README — routing vs domain eval distinction, Strand A/E/F, ADK native gaps, HITL annotation vs runtime interrupts.

**Date:** 2026-05-09
**Sources:** eval-strategy-adk-langsmith plan, eval-strategy-adk-langsmith research

---

## The core gap: routing vs domain evals

Two orthogonal eval dimensions exist for multi-agent VA:

| Strand | Question | Agent | Metric type |
|---|---|---|---|
| **A — Routing eval** | Does the VA root pick the right sub-agent? | va_google_adk (root) | `tool_trajectory_avg_score` |
| **F — Domain eval** | Does each domain agent call the right tools and produce the right output? | va_google_adk (sub-agents) | tool trajectory + output structure + quality |

Strand A seeds from queries that exercise routing boundaries. Strand F seeds from representative domain tasks that assume routing is correct. The two datasets are complementary — neither replaces the other.

**Why this is non-obvious:** galactus current evals only measure retrieval quality (MRR, P@k) and response quality (grounding, completeness). Neither catches "right answer, wrong tool path" or "routed to wrong sub-agent." These failures are invisible to all current graders.

---

## Strand A — ADK tool trajectory eval

`tool_trajectory_avg_score` is the only metric that validates routing and tool call sequence correctness. It's available via ADK's `AgentEvaluator` and supports EXACT / IN_ORDER / ANY_ORDER matching.

**Dataset format:** `data/adk/eval_sets/routing_eval.jsonl` — 50–100 labeled examples, each with `query` + `expected_tool_calls` + `expected_sub_agent`.

**Zero-cost bootstrap (Strand E connection):** `table_type` + `nav_buttons.route` values collected from VA staging responses are labeled routing examples at near-zero cost — queries where `table_type` is non-null name the expected domain. Seed `routing_eval.jsonl` from these before manual labeling.

---

## Strand E — Response metadata signals

The VA staging and SA API responses already contain model-inferred decision signals that are not being stored or analyzed. Capturing these costs nothing (no new LLM calls) and enables two things: report breakdown dimensions and routing eval dataset bootstrapping.

### VA staging — fields to capture

| Field | Type | Eval use |
|---|---|---|
| `table_type` | `"invoices" \| "customers" \| "products" \| "quotes" \| null` | Domain breakdown axis in report; seeds routing_eval.jsonl |
| `contact_support` | `bool` | Model's raw escalation decision |
| `has_chart` | `bool` (derived from `chart_data != null`) | Response modality: structured vs prose |
| `has_form` | `bool` (derived from `form != null`) | Write action triggered |

### Support Agent — coverage_decision enum

Derive from (`insufficient_information`, `contact_support`):
- `"answered"` — both false
- `"no_coverage"` — `insufficient_information=true`
- `"escalated"` — `contact_support=true`

Use `coverage_decision` as the comparable breakdown axis for SA in the combined report. Use `table_type` as the equivalent axis for VA. They align as cross-agent comparisons of how often each agent handles vs deflects vs escalates.

---

## Strand F — Domain agent eval

Once routing is correct, domain correctness asks: did the sub-agent call the right Billy API tools, produce the expected structured output, and give a complete answer?

### Three eval dimensions

**1. Tool trajectory** (reuse Strand A runner)
Did the agent call the expected Billy API tools in the expected order?

**2. Output structure correctness** — `OutputStructureGrader`
Did the response include the expected structured fields? `table_type` match, `chart_data` populated, `metric_cards` present, `contact_support` flag, `form` presence. Binary per-field: present/absent + type correct.

Location: `evals/graders/judges/output_structure.py`
Input: actual `AssistantResponse` dict + expected output spec from task
Output: `GraderOutput` with per-field pass/fail in `dimensions`

**3. Response quality**
Reuse existing `CompletenessGrader`, `GroundingGrader`. Context = the Billy API tool outputs.

### Dataset format

```jsonc
{
  "task_id": "inv_001",
  "domain": "invoices",
  "query": "Show me all overdue invoices from last quarter",
  "session_context": {
    "table_type_hint": "invoices",
    "date_range": "last_quarter"
  },
  "expected_tool_calls": [
    {"name": "get_invoices", "match": "ANY_ORDER"},
    {"name": "filter_by_status", "args": {"status": "overdue"}, "match": "ANY_ORDER"}
  ],
  "expected_output": {
    "table_type": "invoices",
    "chart_data": null,
    "metric_cards": false,
    "contact_support": false
  },
  "graders": ["tool_trajectory", "output_structure", "completeness"]
}
```

Storage: `data/adk/eval_sets/domain_tasks/{domain}_tasks.jsonl`. Scope: 15 invoices + 15 expenses + 10 forecasts + 10 customers = 50 total.

---

## ADK eval framework — native capabilities gap

galactus currently has no `tool_trajectory_avg_score` equivalent. ADK provides this via `AgentEvaluator`. Other ADK-native metrics:

| Metric | Galactus equivalent |
|---|---|
| `tool_trajectory_avg_score` | `adk_steps` diagnostic + experimental `ToolTrajectoryGrader` |
| `final_response_match_v2` | Similar to GroundingGrader |
| `hallucinations_v1` | Similar to GroundingGrader |
| `safety_v1` | ❌ Not in galactus |
| `rubric_based_final_response_quality_v1` | Similar to quality graders |

ADK also exposes Vertex AI managed eval (pointwise, pairwise, AutoSxS) for systematic model comparison.

### Why we use custom graders instead of ADK's built-in eval

Evaluated and ruled out `AgentEvaluator` (trajectory + response match) for the help-center eval pipeline:

- **Trajectory** (`tool_trajectory_avg_score`) requires per-query `expected_tool_use` annotations. Our 541-item eval set has expected URLs and intercom gold responses — not tool-level labels. Annotating expected tool sequences would be new work, and the signal it adds (did `fetch_support_knowledge` fire?) is already captured for free via `adk_steps` and `kb_calls[].top_score` in the output JSONL.
- **Response match** (`final_response_match_v2`) uses ROUGE-L, which is a poor fit for conversational helpdesk answers where wording varies substantially from the reference. Our `ComparisonGrader` and quality judges score relevance, grounding, and coverage via an LLM, which is more informative for this domain.
- **Framework neutrality**: forcing ADK-specific eval infrastructure before the hc_adk vs hc_lg winner is decided would create asymmetric grader coverage. Custom framework-neutral graders (MRR, grounding ratio, composite quality) keep the comparison clean.

The experimental `ToolTrajectoryGrader` in `evals/graders/judges/_experimental/routing.py` is the right starting point if trajectory analysis is needed later — it works from the actual tool call trace rather than requiring pre-labeled expected sequences.

---

## Observability + experiment tracking

Platform wiring and online scoring → [langfuse.md](../../../generative-ai/04-agentic-frameworks/notes/langfuse.md) (support agents) and [langsmith.md](../../../generative-ai/04-agentic-frameworks/notes/langsmith.md) (VA agents).
Metadata contract and ExperimentRun / RagConfig schemas → [observability.md](../../../generative-ai/06-observability/observability.md).

---

## ADK vs LangGraph: parallel evaluation candidates

`hc_adk` and `hc_lg` are deliberately feature-equal — same schema, same safeguard layers, same eval dataset. Neither is primary. The winner is selected by composite eval score after ablation completes, not assumed in advance.

**Why:** Committing to a framework before measuring quality differences would make the comparative method circular. The 3-agent comparison (hc_adk / hc_lg / hc_rag) is the improvement story — every change is measurable via MRR delta. Framework selection is an output of that process, not an input.

**Implication for evals:** Avoid graders or metrics that assume a specific execution model (e.g. LangGraph node sequences, ADK tool call counts) until a winner is selected. Use framework-neutral metrics (MRR, grounding ratio, composite quality) for the primary comparison.

---

## HITL: annotation vs runtime interrupts (important distinction)

`evals/graders/hitl.py` = **post-hoc annotation** for eval datasets. File-based async queue — `submit(task_id, query, response)` → pending.jsonl → human annotates → regression fixture. Framework-agnostic.

`LangGraph GraphInterrupt` = **runtime approval gates**. Graph suspends, waits for human input, resumes via `Command`. LangGraph-specific.

These are different concerns. No migration needed between them. LangSmith annotation queues are a future upgrade path for `hitl.py`'s file-based approach.
