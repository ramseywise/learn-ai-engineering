# LangFuse — Reference Spec

Primary observability platform for galactus support agents. Handles tracing, online
scoring, datasets, and experiment comparison. LangSmith is used for VA agents
(LangGraph auto-instrumentation) — see [langsmith.md](langsmith.md).

What to log (metadata contract + experiment schemas) → [support-agents/observability.md](support-agents/observability.md)

---

## hc_adk instrumentation — `lf.trace()` + per-KB child spans

hc_adk uses `lf.trace()` directly (not `@observe`) because ADK's runner loop
is not a regular Python call stack — ContextVar propagation is more reliable
with an explicit trace reference threaded via a ContextVar.

**Actual trace structure:**

```
Trace: hc_adk_turn                              ← lf.trace() in main.py
  input:    {message}
  output:   {message, contact_support}
  metadata: prompt_version, retrieval_mode, thinking_budget,
            total_latency_ms, kb_top_score, adk_steps,
            prompt_tokens, output_tokens, failure_reason

  ├── Span: bedrock-kb-retrieve                 ← lf_trace.span() per tool call (mode=bedrock)
  │     input:    {queries: [...], cache_key}
  │     output:   {passage_count, top_score, urls: [...]}
  │     metadata: {duration_ms}
  │
  ├── Span: rag-retrieve                        ← lf_trace.span() per tool call (mode=rag)
  │     input:    {queries: [..., max 3]}
  │     output:   {doc_count, urls: [...]}
  │     metadata: {duration_ms}
  │
  Score: retrieval_quality                      ← lf.score() — kb_top_score from best call
  Score: citation_hallucination                 ← push_online_scores() async
  Score: missing_citation                       ← push_online_scores() async
  Score: language_consistency                   ← push_online_scores() async
```

**How the trace reference reaches tool functions:**

```python
# main.py — before runner.run_async()
_lf_token = _lf_trace_ctx.set(_lf_trace)   # set ContextVar
try:
    async for event in _runner.run_async(...):
        ...
finally:
    _lf_trace_ctx.reset(_lf_token)          # always reset

# agent.py — inside the KB tool function
lf_trace = _lf_trace_ctx.get()             # read ContextVar
if lf_trace is not None:
    lf_span = lf_trace.span(name="bedrock-kb-retrieve", input={"queries": queries})
    ...
    lf_span.end(output={...}, metadata={...})
```

ADK's OTEL auto-instrumentation also fires (`invoke_agent`, `call_llm`,
`generate_content` spans) — these appear as a sibling branch to the
`bedrock-kb-retrieve` spans in the Langfuse trace tree.

---

## Per-framework tracing: no unified span layer

Each agent uses its framework's native instrumentation — `@observe` decorators for hc_rag/hc_adk, `CallbackHandler` for hc_lg (LangGraph), LangSmith auto-tracing for VA agents. There is no adapter layer that normalizes spans across frameworks.

**Why:** A unified tracing abstraction would add an adapter layer with no framework-neutral benefit. Native instrumentation gives framework-specific depth (ADK tool call sequences, LangGraph node transitions) that a generic wrapper would lose. The cost is that cross-framework query latency breakdowns require joining two platforms (LangFuse + LangSmith) — accepted as the right tradeoff given data ownership requirements.

**Consequence:** Don't add a `galactus_trace()` wrapper that all agents call. Wire each agent to its platform directly.

---

## Why LangFuse

- Open source, self-hostable — data stays in your infrastructure
- Native OpenTelemetry support — no vendor lock-in on instrumentation
- Online scoring API — attach grader results to traces post-hoc
- Dataset + prompt management built in
- Actively shipping: annotation queues, evals, playground improving fast

LangSmith comparison: richer eval experiment UI and native LangGraph integration, but
closed source and requires exporting data for offline analysis. LangFuse wins on data
ownership and the support-agent use case (custom RAG, ADK).

---

## Setup

```bash
uv add langfuse
```

```bash
# .env
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://cloud.langfuse.com   # or your self-hosted URL
```

---

## Wiring by framework

### hc_rag — `@observe` decorator

hc_rag uses `@observe` because it has a regular Python call stack where
ContextVar propagation works naturally.

```python
from langfuse.decorators import observe, langfuse_context

@observe(name="hc_rag_turn")
async def _run_turn(query: str, session_id: str = "") -> dict:
    langfuse_context.update_current_observation(
        session_id=session_id or None,
        metadata={"prompt_version": PROMPT_VERSION},
    )
    result = await run_turn(query)       # RAG internals auto-captured
    _trace_id = langfuse_context.get_current_trace_id()
    if _trace_id:
        asyncio.create_task(push_online_scores(trace_id=_trace_id, ...))
    return result
```

**Note:** `retrieved_urls` is not yet surfaced at the `main.py` level for hc_rag,
so only `language_consistency` is posted — `citation_hallucination` and
`missing_citation` are skipped.

### hc_adk — `lf.trace()` + ContextVar

See the [hc_adk instrumentation](#hc_adk-instrumentation--lftrace--per-kb-child-spans)
section above for the full pattern. In short: create the trace in `main.py`,
set it on `_lf_trace_ctx`, read it inside tool functions to create child spans.

Capture `_lf_trace.id` from the trace object and include it in `ExperimentRun`
when writing eval output.

### hc_lg (LangGraph) — callback handler

```python
from langfuse.callback import CallbackHandler

handler = CallbackHandler(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    session_id=session_id,
    metadata={"agent": "hc_lg", "prompt_version": PROMPT_VERSION},
)

result = await graph.ainvoke(
    {"messages": [HumanMessage(content=query)]},
    config={"callbacks": [handler]},
)
```

Every node, edge, and LLM call is captured automatically. Add extra metadata via
`handler.trace.update(metadata={...})` after the invoke.

### va_google_adk / va_langgraph

VA agents use LangSmith (see [langsmith.md](langsmith.md)). LangFuse covers support
agents only. If both platforms are needed for the same agent, use OTEL export from
LangFuse → LangSmith via the OTEL collector.

---

## Attaching scores post-hoc (online scoring)

Run graders offline against completed traces and write scores back:

```python
from langfuse import Langfuse

langfuse = Langfuse()

# After running GroundingGrader on a batch of traces
for trace_id, result in grader_results.items():
    langfuse.score(
        trace_id=trace_id,
        name="grounding",
        value=result.score,
        comment=result.explanation,
    )
    langfuse.score(
        trace_id=trace_id,
        name="answer_relevancy",
        value=result.relevancy_score,
    )
```

### Standard score keys for galactus

**Heuristic grounding tiers (free, no LLM)**

| Key | Grader | Range | Tier |
|---|---|---|---|
| `citation_hallucination` | `CitationHallucinationGrader` | 0 / 1 | Tier 1 — response URL ∉ retrieved set |
| `missing_citation` | `MissingCitationGrader` | 0 / 1 | Tier 2 — substantive response, no citations |
| `citation_recall` | `CitationRecallGrader` | 0–1 | Golden URL recall (alias: `source_match`) |
| `language_consistency` | `LanguageConsistencyGrader` | 0 / 1 | Tier 4 — da query → non-da response |

**LLM graders (calibrated tier)**

| Key | Grader | Range |
|---|---|---|
| `grounding` | `GroundingGrader` | 0–1 |
| `answer_relevancy` | `AnswerRelevancyGrader` | 0–1 |
| `completeness` | `CompletenessGrader` | 0–1 |
| `escalation_correct` | `EscalationGrader` | 0 / 1 |
| `routing_accuracy` | intent label match | 0 / 1 |

---

## Datasets

LangFuse datasets group input/output examples for systematic evaluation.

```python
from langfuse import Langfuse

langfuse = Langfuse()

# Create dataset
dataset = langfuse.create_dataset(
    name="sa-quality-eval-v1",
    description="SA quality eval — 541 clean strict-answer intercom rows, context-dependent queries removed",
)

# Seed from quality eval JSONL (see data/datasets/README.md for full seeding reference)
import json
with open("data/datasets/canonical_seed__intercom__strict_answer__clean.jsonl") as f:
    for line in f:
        row = json.loads(line)
        langfuse.create_dataset_item(
            dataset_name="sa-quality-eval-v1",
            input={"query": row["query"]},
            expected_output={"expected_urls": row["expected_urls"], "expected_answer": row.get("expected_answer")},
            metadata={"task_id": row["task_id"], "gt_confidence": row.get("gt_confidence")},
        )
```

### Adding from traces

In the LangFuse UI: open a trace → "Add to dataset". Use for interesting/failing
traces you want to turn into regression fixtures.

---

## Experiment runs

Each run against a dataset creates an experiment. Link it to `ExperimentRun` by
passing `run_id` in the metadata.

```python
from langfuse import Langfuse
from evals.pipelines.lib.models import ExperimentRun
import uuid, subprocess

run = ExperimentRun(
    run_id=str(uuid.uuid4()),
    experiment_name="hc-rag-chunking-v4",
    created_at=datetime.utcnow().isoformat(),
    git_commit=subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip(),
    dataset="data/datasets/canonical_seed__intercom__strict_answer__clean.jsonl",
    pipeline="hc_rag",
    rag_config=rag_config,
)

dataset = langfuse.get_dataset("sa-quality-eval-v1")
for item in dataset.items:
    with item.observe(run_name=run.experiment_name, metadata={"run_id": run.run_id}) as trace_id:
        output = await handle_request(item.input["query"], session_id=run.run_id)
        # score inline or post-hoc
```

Compare across runs in the LangFuse UI (Experiments tab) — filter by `experiment_name`
or `run_id` metadata, diff grader scores column by column.

---

## Annotation queues (HITL path)

Route low-confidence grader outputs to LangFuse annotation instead of file-based `hitl.py`:

```python
# Create queue once
queue = langfuse.create_annotation_queue("hc-uncertain-cases")

# After grading, submit uncertain traces
for trace_id, score in grader_results.items():
    if score < 0.6:
        langfuse.add_trace_to_queue(queue_id=queue.id, trace_id=trace_id)
```

Reviewers label in the LangFuse UI; export completed labels as JSONL for regression fixtures.

---

## get_langfuse_prompt — remote prompt management

Fetch a prompt from Langfuse at startup, fall back to a local string silently:

```python
from observability import get_langfuse_prompt

instruction = get_langfuse_prompt(
    prompt_name="hc_adk_instruction",   # Langfuse prompt name
    fallback=ADK_INSTRUCTION,           # local fallback when Langfuse is off
)
```

| Agent | Langfuse prompt name | Fallback |
|-------|---------------------|---------|
| `hc_adk` | `hc_adk_instruction` | `prompts.ADK_INSTRUCTION` |
| `hc_lg`  | `hc_lg_answer_prompt` | `prompts.ANSWER_PROMPT` |

The fetch is called inside a lazy `get_root_agent()` factory (hc_adk) or
`_get_answer_prompt()` (hc_lg), so Langfuse must be initialised via
`configure_runtime()` before the agent is constructed. The result is cached
for the process lifetime — no per-request fetch.

---

## Files in galactus

| File | Purpose |
|---|---|
| `src/support_agents/observability.py` | Shared module: `configure_runtime()`, `get_langfuse()`, `push_online_scores()`, `get_langfuse_prompt()` |
| `src/support_agents/hc_adk/agent.py` | `_lf_trace_ctx` ContextVar + KB child spans (`bedrock-kb-retrieve`, `rag-retrieve`) |
| `src/support_agents/hc_adk/main.py` | `lf.trace()` root, ContextVar wiring, `retrieval_quality` score |
| `src/support_agents/hc_lg/main.py` | `CallbackHandler` root, `retrieval_quality` score (grading_score) |
| `evals/pipelines/langfuse_utils/langfuse_scorer.py` | Post-hoc score writer (extend with standard keys as needed) |
| `evals/pipelines/lib/models.py` | `ExperimentRun`, `RagConfig`, `QATask`, `EvalReport` — schema source of truth |
