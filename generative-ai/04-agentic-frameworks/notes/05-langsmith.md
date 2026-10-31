---
origin: own coursework
sources:
  - https://docs.smith.langchain.com/
  - https://docs.smith.langchain.com/evaluation
  - "James Phoenix & Mike Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 4"
confidence: medium
cleaned: 2026-10-31
---
# 5 — LangSmith

> LangChain's hosted tracing and eval platform: auto-tracing for LangGraph, manual `@traceable` wiring for ADK, datasets, `evaluate()`, and annotation queues.

Tracing, evaluation, and dataset management for the eval platform agents. Both `support_adk`
and `support_lg` send traces here; LangSmith is the eval loop for live agent runs.

---

## Wiring by framework

### Google ADK (manual wiring — no auto-instrumentation)

ADK doesn't use LangChain, so `LANGCHAIN_TRACING_V2` has no effect. Wiring is done
manually in `observability.py` using the LangSmith SDK directly.

```python
# src/multi_agents/support_adk/observability.py
from langsmith import Client
from langsmith.run_helpers import traceable

client = Client()  # reads LANGSMITH_API_KEY from env

# Wrap agent invocations
@traceable(name="support_adk", run_type="chain")
async def run_agent(query: str, session_id: str) -> dict:
    ...
```

Required env vars:
```bash
LANGSMITH_API_KEY=<key>
LANGSMITH_PROJECT=google-adk       # project name in LangSmith UI
LANGSMITH_TRACING=true                # ADK-specific flag (not LANGCHAIN_*)
```

### LangGraph (auto-instrumentation via env vars)

LangGraph is native to LangSmith — set two env vars and all graph runs are traced
automatically, including subgraph calls, node transitions, and tool invocations.

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<same key as LANGSMITH_API_KEY>
LANGCHAIN_PROJECT=langgraph        # project name in LangSmith UI
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
    "google-adk-eval-v1",
    description="SupportAgent ADK routing + quality eval set, seeded from support corpus A regression"
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
            dataset_name="google-adk-eval-v1"
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
    # call the eval platform GroundingGrader
    from evals.graders.judges.quality import GroundingGrader
    result = GroundingGrader().grade(run.outputs["response"], run.outputs.get("sources", []))
    return {"score": result.score, "key": "grounding"}

results = evaluate(
    lambda inputs: run_agent(inputs["query"], inputs["session_id"]),
    data="google-adk-eval-v1",
    evaluators=[routing_accuracy, grounding_score],
    experiment_prefix="adk-eval",
)
```

### Standard evaluator set for the eval platform

| Evaluator | Key | Maps to the eval platform grader |
|---|---|---|
| `routing_accuracy` | routing_accuracy | intent from run vs expected_intent in dataset |
| `grounding_score` | grounding | `GroundingGrader` |
| `completeness_score` | completeness | `CompletenessGrader` |
| `escalation_correct` | escalation | `EscalationGrader` |
| `answer_relevancy` | relevancy | `AnswerRelevancyGrader` |

### Testing whether a cheaper model is good enough

*Prompt Engineering for Generative AI* (ch. 4) walks through the most common reason to run an eval: checking whether a cheaper model can take over a task. The setup:

1. GPT-4 classifies a set of bank-transaction descriptions into a `transaction_type` and a `transaction_category`. **Those labels are treated as ground truth.**
2. Mixtral 8x7b (`mistral-small` in Mistral's API) runs the same chain, `prompt | model | StrOutputParser() | remove_back_slashes | PydanticOutputParser`. The extra step strips backslashes Mistral put into JSON keys.
3. An exact-match comparison against the GPT-4 labels scores Mistral at **77.5%**. The book doesn't give the number of transactions.
4. GPT-3.5-turbo runs the same chain in JSON mode (`response_format={"type": "json_object"}`), and a GPT-4 pairwise judge (`labeled_pairwise_string`) compares the two smaller models against the reference and explains its choice.

Four things to know before copying this setup:

- **The score measures agreement with GPT-4, not correctness.** Where GPT-4 mislabels a transaction, a small model that gets it right scores as wrong. The book's own warning covers the judge too: "if GPT-4 is bad at a task, it may also be bad at evaluating that task", so read the judge's reasoning by hand. Spot-check a sample of the reference labels before trusting any accuracy against them ([06-eval](../../../ai-engineering/06-eval/README.md)).
- **Parse failures count as wrong answers.** The loop's `except` branch writes a `None` row instead of crashing, and `None` never matches. So the 77.5% mixes misclassifications with output that failed to parse. Track the parse-failure rate as its own metric. A model that classifies well but formats badly needs a different fix (JSON mode, `with_structured_output`) from one that classifies badly.
- **Exact match needs no framework.** The book says so itself: a string comparison is a pandas one-liner. The LLM judges are where a library earns its place. For near-miss answers, the book points to Levenshtein and embedding-distance evaluators.
- **The API is legacy.** `load_evaluator(...)` and `evaluate_string_pairs(...)` come from `langchain.evaluation`. In current code, store the GPT-4 labels as dataset `outputs`, write exact match as a custom evaluator like `routing_accuracy` above, and run both models through `evaluate()` as two experiments. Use LangSmith's pairwise comparison for the head-to-head.

The book's case for doing this at all still holds. If the small model is good enough, the task gets cheaper and faster, and an open-weights model can run on your own servers so sensitive data never leaves. Its advice is to test against the hosted API first, before self-hosting.

---

## Annotation queues (upgrade path for hitl.py)

LangSmith has a native annotation UI. To route uncertain grader outputs there instead
of the file-based `hitl.py`:

```python
client.create_annotation_queue("uncertain-cases", description="Low-confidence grader outputs")

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
client.list_runs(project_name="google-adk", filter='eq(feedback_key, "grounding")')
```

---

## Files in the eval platform

| File | Purpose |
|---|---|
| `docs/frameworks/langfuse.md` | Primary experiment-tracking reference for current the eval platform evals |
| `evals/pipelines/langfuse_utils/evaluation.py` | Current LangFuse experiment runner |
| `evals/graders/judges/` | Current grader packages used by offline and online evals |

LangSmith references in this doc are historical/secondary. Prefer LangFuse for
new the eval platform experiments unless a specific workflow explicitly requires
LangSmith.

---

→ Next: [06-framework-selection.md](06-framework-selection.md) — choosing between LangGraph, ADK and the other agent SDKs once you have seen what each makes easy.
