# LangSmith — Reference Spec

Tracing, evaluation, and dataset management for galactus agents. Both `va_google_adk`
and `va_langgraph` send traces here; LangSmith is the eval loop for live agent runs.

---

## Wiring by framework

### Google ADK (manual wiring — no auto-instrumentation)

ADK doesn't use LangChain, so `LANGCHAIN_TRACING_V2` has no effect. Wiring is done
manually in `observability.py` using the LangSmith SDK directly.

```python
# src/multi_agents/va_google_adk/observability.py
from langsmith import Client
from langsmith.run_helpers import traceable

client = Client()  # reads LANGSMITH_API_KEY from env

# Wrap agent invocations
@traceable(name="va_google_adk", run_type="chain")
async def run_agent(query: str, session_id: str) -> dict:
    ...
```

Required env vars:
```bash
LANGSMITH_API_KEY=<key>
LANGSMITH_PROJECT=va-google-adk       # project name in LangSmith UI
LANGSMITH_TRACING=true                # ADK-specific flag (not LANGCHAIN_*)
```

### LangGraph (auto-instrumentation via env vars)

LangGraph is native to LangSmith — set two env vars and all graph runs are traced
automatically, including subgraph calls, node transitions, and tool invocations.

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<same key as LANGSMITH_API_KEY>
LANGCHAIN_PROJECT=va-langgraph        # project name in LangSmith UI
```

No code changes needed. Add to `.env` and `pyproject.toml` dev dependencies:
```bash
uv add langsmith
```

---

## Trace anatomy (what LangSmith captures)

| Framework | What's traced |
|---|---|
| ADK (manual) | Only what's wrapped with `@traceable` — agent call, tool calls if decorated |
| LangGraph (auto) | Every node, every edge transition, all LLM calls, tool invocations, subgraph state |

LangGraph traces are richer by default. For ADK, wrap individual tool calls with
`@traceable` in `sub_agents/` to get per-tool spans.

---

## Datasets

LangSmith datasets are collections of input/output examples used to run evaluations.

### Creating a dataset

```python
from langsmith import Client

client = Client()
dataset = client.create_dataset(
    "va-google-adk-eval-v1",
    description="VA ADK routing + quality eval set, seeded from BKH regression"
)
```

### Adding examples from existing JSONL

```python
import json
with open("data/bkh/eval_sets/regression_main.jsonl") as f:
    for line in f:
        row = json.loads(line)
        client.create_example(
            inputs={"query": row["query"], "session_id": row["task_id"]},
            outputs={"response": row.get("response", "")},
            dataset_name="va-google-adk-eval-v1"
        )
```

### Adding from traces (UI or SDK)

In the LangSmith UI: open a run → "Add to dataset". Fastest way to seed from
interesting/failing traces already in the project.

---

## Evaluators

Evaluators are Python functions that score a single run against its expected output.
Register them when running an eval experiment.

```python
from langsmith.evaluation import evaluate, LangChainStringEvaluator

def routing_accuracy(run, example) -> dict:
    predicted = run.outputs.get("intent")
    expected = example.outputs.get("expected_intent")
    return {"score": 1.0 if predicted == expected else 0.0, "key": "routing_accuracy"}

def grounding_score(run, example) -> dict:
    # call galactus GroundingGrader
    from evals.graders.judges.quality import GroundingGrader
    result = GroundingGrader().grade(run.outputs["response"], run.outputs.get("sources", []))
    return {"score": result.score, "key": "grounding"}

results = evaluate(
    lambda inputs: run_agent(inputs["query"], inputs["session_id"]),
    data="va-google-adk-eval-v1",
    evaluators=[routing_accuracy, grounding_score],
    experiment_prefix="adk-eval",
)
```

### Standard evaluator set for galactus

| Evaluator | Key | Maps to galactus grader |
|---|---|---|
| `routing_accuracy` | routing_accuracy | intent from run vs expected_intent in dataset |
| `grounding_score` | grounding | `GroundingGrader` |
| `completeness_score` | completeness | `CompletenessGrader` |
| `escalation_correct` | escalation | `EscalationGrader` |
| `answer_relevancy` | relevancy | `AnswerRelevancyGrader` |

---

## Annotation queues (upgrade path for hitl.py)

LangSmith has a native annotation UI. To route uncertain grader outputs there instead
of the file-based `hitl.py`:

```python
client.create_annotation_queue("va-uncertain-cases", description="Low-confidence grader outputs")

# After a grader run, submit uncertain cases
for run_id, score in grader_results.items():
    if score < 0.6:
        client.add_runs_to_annotation_queue(queue_id, run_ids=[run_id])
```

Reviewers label in the LangSmith UI; completed labels export as JSONL for regression fixtures.

---

## Experiment comparison

Each `evaluate()` call creates an experiment. Compare across runs in the LangSmith UI
(Experiments tab) or via SDK:

```python
# Compare ADK vs LangGraph on same dataset
client.list_runs(project_name="va-google-adk", filter='eq(feedback_key, "grounding")')
```

---

## Files in galactus

| File | Purpose |
|---|---|
| `docs/frameworks/langfuse.md` | Primary experiment-tracking reference for current galactus evals |
| `evals/pipelines/langfuse_utils/evaluation.py` | Current LangFuse experiment runner |
| `evals/graders/judges/` | Current grader packages used by offline and online evals |

LangSmith references in this doc are historical/secondary. Prefer LangFuse for
new galactus experiments unless a VA-specific workflow explicitly requires
LangSmith.
