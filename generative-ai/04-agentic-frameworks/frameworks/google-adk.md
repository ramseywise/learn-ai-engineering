# Google ADK — Reference Spec

Reference for building agents with the Google Agent Development Kit (Python). Relevant if we add an ADK-backed agent layer on top of galactus graders, or extend to ADK-hosted evaluators.

Canonical docs:
- Local (librarian): `/.docs/adk/llms-full.txt` and `llms.txt`
- Upstream: `https://google.github.io/adk-docs/llms-full.txt`

---

## Core primitives

| Primitive | What it is |
|---|---|
| `Agent` | Stateful unit with identity, model, instruction, tools, optional sub-agents |
| `SequentialAgent` | Linear pipeline: runs sub-agents in order |
| `LoopAgent` | Retry loop: runs sub-agent up to `max_iterations` |
| `FunctionTool` | Python function auto-wrapped as an ADK tool |
| `runner.run_async()` | Executes the agent, yields an async event stream |
| `session.state` | Mutable dict shared across turns via `ToolContext` |

---

## ADK vs LangGraph mental model

| Dimension | Google ADK | LangGraph |
|---|---|---|
| **Core unit** | `Agent` (stateful, has identity) | `Node` (stateless function on shared state) |
| **Composition** | Recursive tree: `Agent(sub_agents=[...])` | DAG: `graph.add_edge(A, B)` |
| **Control flow** | Agent decides (LLM chooses tool/sub-agent) | Explicit: conditional edges + routing functions |
| **State** | Mutable dict via `ToolContext` | Immutable `TypedDict` passed through; nodes return diffs |
| **Execution** | `runner.run_async()` → async event generator | `graph.ainvoke(state)` → final state dict |
| **Observability** | Lifecycle callbacks: `before/after_model`, `before/after_tool` | Langfuse `CallbackHandler` in `config={"callbacks": [...]}` |
| **Default model** | Gemini (configured via `model=` param) | Anthropic / Claude (Anthropic SDK) |

Use ADK when: agent structure is recursive/tree-shaped, Gemini is the model, fast prototype.  
Use LangGraph when: deterministic pipeline with explicit routing, need state reducers, HITL gates.

---

## Quick patterns

### Basic agent
```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

def get_eval_score(dataset: str) -> dict:
    """Return latest heuristic score for a named eval dataset."""
    # ... load from data/bkh/stats/{dataset}_stats.json
    return {"dataset": dataset, "score": 0.87}

agent = Agent(
    name="eval_agent",
    model="gemini-2.0-flash",
    instruction="You help users query eval pipeline results.",
    tools=[FunctionTool(get_eval_score)],
)
```

### Sequential pipeline
```python
from google.adk.agents import SequentialAgent

pipeline = SequentialAgent(
    name="eval_pipeline",
    sub_agents=[preprocessor, grader, reporter],
)
```

### Accessing session state in a tool
```python
from google.adk.tools import ToolContext

def my_tool(query: str, tool_context: ToolContext) -> dict:
    # Read state
    context = tool_context.state.get("context", [])
    # Write state
    tool_context.state["last_query"] = query
    return {"result": "..."}
```

---

## Implementation rules

- Only use ADK decorators and APIs confirmed in local docs (`llms-full.txt`)
- Prefer `async` implementations
- Use Pydantic for structured schemas (input/output types)
- Keep reusable helpers in `shared/` before creating new ones
- Check if a similar agent/tool already exists before creating new

---

## Testing ADK agents

```bash
adk run agent_name        # interactive REPL
adk web                   # browser UI
uv run pytest tests/ -v   # unit tests
```

For eval: create `tests/evalsuite/` with JSON fixtures, run via `make eval-capability`.

---

## ADK Eval Framework

### Built-in metrics

| Metric | Key | What it measures |
|---|---|---|
| `tool_trajectory_avg_score` | trajectory | Tool call sequence vs. expected (EXACT / IN_ORDER / ANY_ORDER) |
| `final_response_match_v2` | response_match | Semantic similarity to golden response |
| `hallucinations_v1` | hallucination | Unsupported claims vs. tool outputs |
| `safety_v1` | safety | Harmful content / PII |
| `rubric_based_final_response_quality_v1` | rubric | Custom scoring criteria |

`tool_trajectory_avg_score` is the most unique — it validates routing correctness (did the
right sub-agent get called?) not just final answer quality. Nothing in the galactus custom
graders covers this.

### Eval config format (from samples)

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 0.8,
    "rubric_based_final_response_quality_v1": {
      "rubric": "Response must be in the same language as the query.",
      "weight": 1.0
    }
  },
  "eval_set": "eval_sets/routing_eval.jsonl"
}
```

### Running evals

```python
from google.adk.evaluation import AgentEvaluator

evaluator = AgentEvaluator(
    agent=root_agent,
    eval_config="eval_configs/routing_eval_config.json",
)
results = await evaluator.evaluate()
```

### Vertex AI managed eval (post-hoc)

Accessible via ADK's eval runner for pointwise and pairwise scoring:
- **Pointwise:** Judge model scores single candidate (0–5); maps to `rubric_based_final_response_quality_v1`
- **Pairwise:** Compare two model outputs; returns winner — useful for ADK vs LangGraph comparison
- **AutoSxS:** Systematic side-by-side pipeline

Evaluation is post-hoc (not at runtime). Runs via ADK's eval runner against saved JSONL.

### Eval runner location

For galactus support-agent experiments, use the unified eval dispatcher:

```bash
uv run python -m evals.pipelines.run live --run-name hc-adk-smoke --jsonl <dataset.jsonl> --endpoint http://localhost:8011/chat --tier heuristic
uv run python -m evals.pipelines.run langfuse --run-name hc-adk --dataset hc-support-agents-golden-597 --endpoint http://localhost:8011/chat --tier calibrated
```

ADK-native `adk eval` remains useful for standalone ADK projects and tool
trajectory tests, but it is not the primary galactus eval path.

---

## Guardrails pattern

Inject callbacks at the runner level, not inside agents:

```python
from google.adk.agents.callback_context import CallbackContext

def pii_redaction_callback(context: CallbackContext) -> None:
    # Intercept model output, scrub PII before tool/user sees it
    ...

runner = Runner(agent=agent, callbacks=[pii_redaction_callback])
```

Reusable guardrails live in `shared/guardrails/`.
