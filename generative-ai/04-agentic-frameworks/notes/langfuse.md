# LangFuse — Reference Spec

Observability platform for LLM agents. Handles tracing, online scoring, datasets, and
experiment comparison.

---

## Trace with child spans for tool calls

For agents that aren't a regular Python call stack (e.g. a runner/event-loop pattern like
Google ADK), using `lf.trace()` directly rather than `@observe` is more reliable — thread
an explicit trace reference via a `ContextVar` since propagation doesn't depend on a
normal call stack.

**Example trace structure:**

```
Trace: agent_turn                               ← lf.trace() in main.py
  input:    {message}
  output:   {message, escalated}
  metadata: prompt_version, retrieval_mode, thinking_budget,
            total_latency_ms, top_score, steps,
            prompt_tokens, output_tokens, failure_reason

  ├── Span: kb-retrieve                         ← lf_trace.span() per tool call
  │     input:    {queries: [...], cache_key}
  │     output:   {passage_count, top_score, urls: [...]}
  │     metadata: {duration_ms}
  │
  ├── Span: rag-retrieve                        ← lf_trace.span() per tool call
  │     input:    {queries: [..., max 3]}
  │     output:   {doc_count, urls: [...]}
  │     metadata: {duration_ms}
  │
  Score: retrieval_quality                      ← lf.score() — top_score from best call
  Score: citation_hallucination                 ← posted async post-hoc
  Score: missing_citation                       ← posted async post-hoc
  Score: language_consistency                   ← posted async post-hoc
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
    lf_span = lf_trace.span(name="kb-retrieve", input={"queries": queries})
    ...
    lf_span.end(output={...}, metadata={...})
```

A framework's own OTEL auto-instrumentation (e.g. ADK's `invoke_agent`, `call_llm`,
`generate_content` spans) fires alongside manually-created spans, appearing as a sibling
branch in the same trace tree.

---

## Per-framework tracing: no unified span layer

Each agent uses its framework's native instrumentation — `@observe` decorators for a
regular call-stack agent, `CallbackHandler` for LangGraph, LangSmith auto-tracing for
frameworks with native LangSmith integration. There is no adapter layer that normalizes
spans across frameworks.

**Why:** A unified tracing abstraction would add an adapter layer with no framework-neutral
benefit. Native instrumentation gives framework-specific depth (tool call sequences, graph
node transitions) that a generic wrapper would lose. The cost is that cross-framework
latency breakdowns require joining two platforms — accepted as the right tradeoff when
data ownership requirements favor a self-hosted platform for some agents and a managed one
for others.

**Consequence:** Don't build a single `trace()` wrapper that every agent calls regardless
of framework. Wire each agent to its platform directly.

---

## Why LangFuse

- Open source, self-hostable — data stays in your infrastructure
- Native OpenTelemetry support — no vendor lock-in on instrumentation
- Online scoring API — attach grader results to traces post-hoc
- Dataset + prompt management built in
- Actively shipping: annotation queues, evals, playground improving fast

LangSmith comparison: richer eval experiment UI and native LangGraph integration, but
closed source and requires exporting data for offline analysis. LangFuse wins on data
ownership and custom-RAG/ADK use cases.

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

### Regular call-stack agent — `@observe` decorator

Use `@observe` when the agent has a normal Python call stack, where ContextVar
propagation works naturally.

```python
from langfuse.decorators import observe, langfuse_context

@observe(name="rag_turn")
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

### Runner/event-loop agent (e.g. ADK) — `lf.trace()` + ContextVar

See the [trace-with-child-spans](#trace-with-child-spans-for-tool-calls) section above
for the full pattern. In short: create the trace in `main.py`, set it on a ContextVar,
read it inside tool functions to create child spans.

### LangGraph — callback handler

```python
from langfuse.callback import CallbackHandler

handler = CallbackHandler(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    session_id=session_id,
    metadata={"agent": "my_langgraph_agent", "prompt_version": PROMPT_VERSION},
)

result = await graph.ainvoke(
    {"messages": [HumanMessage(content=query)]},
    config={"callbacks": [handler]},
)
```

Every node, edge, and LLM call is captured automatically. Add extra metadata via
`handler.trace.update(metadata={...})` after the invoke.

### Mixed-platform agents

If one agent needs both LangFuse and LangSmith coverage (e.g. it's built with LangGraph
but the rest of the system standardizes on LangFuse), use OTEL export from LangFuse →
LangSmith via the OTEL collector rather than double-instrumenting.

---

## Attaching scores post-hoc (online scoring)

Run graders offline against completed traces and write scores back:

```python
from langfuse import Langfuse

langfuse = Langfuse()

# After running a grounding grader on a batch of traces
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

### Standard score keys

**Heuristic grounding tiers (free, no LLM)**

| Key | Grader | Range | Tier |
|---|---|---|---|
| `citation_hallucination` | `CitationHallucinationGrader` | 0 / 1 | Tier 1 — response URL ∉ retrieved set |
| `missing_citation` | `MissingCitationGrader` | 0 / 1 | Tier 2 — substantive response, no citations |
| `citation_recall` | `CitationRecallGrader` | 0–1 | Golden URL recall (alias: `source_match`) |
| `language_consistency` | `LanguageConsistencyGrader` | 0 / 1 | Tier 4 — query language ≠ response language |

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

dataset = langfuse.create_dataset(
    name="quality-eval-v1",
    description="Clean strict-answer eval set, context-dependent queries removed",
)

import json
with open("data/datasets/eval_seed.jsonl") as f:
    for line in f:
        row = json.loads(line)
        langfuse.create_dataset_item(
            dataset_name="quality-eval-v1",
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

Each run against a dataset creates an experiment. Tag it with a `run_id` in the metadata
so results can be joined back to your own experiment-tracking schema.

```python
from langfuse import Langfuse
import uuid, subprocess

run_id = str(uuid.uuid4())
git_commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()

dataset = langfuse.get_dataset("quality-eval-v1")
for item in dataset.items:
    with item.observe(run_name="rag-chunking-v4", metadata={"run_id": run_id}) as trace_id:
        output = await handle_request(item.input["query"], session_id=run_id)
        # score inline or post-hoc
```

Compare across runs in the LangFuse UI (Experiments tab) — filter by `experiment_name`
or `run_id` metadata, diff grader scores column by column.

---

## Annotation queues (HITL path)

Route low-confidence grader outputs to LangFuse annotation instead of a file-based
review queue:

```python
# Create queue once
queue = langfuse.create_annotation_queue("uncertain-cases")

# After grading, submit uncertain traces
for trace_id, score in grader_results.items():
    if score < 0.6:
        langfuse.add_trace_to_queue(queue_id=queue.id, trace_id=trace_id)
```

Reviewers label in the LangFuse UI; export completed labels as JSONL for regression fixtures.

---

## Remote prompt management

Fetch a prompt from Langfuse at startup, fall back to a local string silently:

```python
def get_langfuse_prompt(prompt_name: str, fallback: str) -> str:
    ...

instruction = get_langfuse_prompt(
    prompt_name="agent_instruction",   # Langfuse prompt name
    fallback=AGENT_INSTRUCTION,        # local fallback when Langfuse is off
)
```

Call the fetch inside a lazy factory function so LangFuse is initialised before the agent
is constructed, and cache the result for the process lifetime — no per-request fetch.
