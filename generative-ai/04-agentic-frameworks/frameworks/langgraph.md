# LangGraph — Reference Spec

Patterns and checklist for building LangGraph agents/pipelines. Not currently used in galactus eval pipeline, but relevant if we add an agent layer on top of the graders. Also useful context when comparing LangGraph vs Google ADK.

See also: [google-adk.md](google-adk.md), [langsmith.md](langsmith.md), playground `langgraph-vs-adk.md`.

---

## Before You Build

Write answers to these as a design note before touching the graph:

**State:** What new fields? What type and reducer? Are they serialisable (required for checkpointer)?

**Topology:** Sketch node/edge additions. New nodes pure transform or I/O? Where does the path branch and rejoin? Subgraph or inline?

**HITL:** Does this need a human approval gate? Static `interrupt_before` or dynamic `interrupt()` inside a node?

**Testing:** Can the node be unit-tested with a mock state dict?

---

## State design

- Always `TypedDict` with explicit field types — never raw dicts
- `total=False` makes all fields optional; use unless fields must always be present
- Messages field: `Annotated[list, add_messages]` — never plain `list`
- Parallel fan-out: `Annotated[list, operator.add]`, not overwrite
- Flat state — avoid nested dicts; they make reducers complex
- Nodes return partial dicts, never mutate state directly

```python
class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    query: str
    intent: str
    retrieved_chunks: list[RetrievalResult]
    confidence_score: float
    confident: bool
    retry_count: int
    escalate: bool
```

---

## Node conventions

- Every node is `async def` — even if no I/O today
- Return only the fields the node updates — nothing else
- Name after what they do: `condense_query` not `HistoryCondenserNode`
- Wrap blocking I/O in `asyncio.to_thread()`
- One responsibility per node — if it does two things, split it

---

## Graph wiring

- `add_conditional_edges` with a dict mapping return values to node names — no inline lambdas
- `Command(goto=..., update={...})` for routing that also writes state
- Compile once, reuse — never recompile per request
- Subgraphs for independently testable pipelines

```python
def route_by_intent(state: AgentState) -> str:
    if state["intent"] == "conversational":
        return "generate"
    return "retrieve"

graph.add_conditional_edges("plan", route_by_intent, {
    "generate": "generate",
    "retrieve": "retrieve",
})
```

---

## HITL

**Static breakpoints** — pause at a known node boundary:
```python
graph.compile(interrupt_before=["tool_executor"], checkpointer=checkpointer)
```

**Dynamic `interrupt()`** — pause inside a node when runtime state determines it:
```python
from langgraph.types import interrupt

async def review_node(state: AgentState) -> dict:
    draft = await generate_draft(state)
    approved = interrupt({"draft": draft, "prompt": "Approve?"})
    if not approved:
        return {"messages": [HumanMessage("Revise: rejected")]}
    return {"output": draft}
```

Resume: `await graph.ainvoke(Command(resume=True), config=thread_config)`. Requires checkpointer.

---

## Checkpointer

| Backend | When to use |
|---|---|
| `MemorySaver` | Dev, unit tests only |
| `AsyncSqliteSaver` | Local / single-instance |
| `AsyncPostgresSaver` | Production multi-instance |

Inject via config — never hardcode backend.

---

## Streaming modes

| Mode | Use for |
|---|---|
| `values` | Debug — full state snapshot after each node |
| `updates` | Progress — state delta per node |
| `events` | UI — token stream + tool activity |

---

## LangSmith integration

LangGraph auto-instruments when these env vars are set — no code changes needed:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<key>
LANGCHAIN_PROJECT=va-langgraph
```

Every graph run, node transition, LLM call, and tool invocation is captured as a trace.
See `ref/langsmith.md` for dataset management, evaluator patterns, and annotation queues.

---

## Send — parallel dispatch (map-reduce)

Use `Send` to fan out the same node across multiple state partitions simultaneously.
Unlike subgraphs-as-nodes, `Send` creates independent parallel branches that merge
via a reducer.

```python
from langgraph.types import Send

def dispatch_domains(state: AgentState) -> list[Send]:
    return [
        Send("domain_agent", {"domain": d, "query": state["query"]})
        for d in state["detected_domains"]
    ]

graph.add_conditional_edges("router", dispatch_domains)
```

The receiving node (`domain_agent`) runs once per `Send` in parallel. Results merge
via the field's reducer (e.g., `Annotated[list, operator.add]`).

Use `Send` for: parallel domain analysis in `insights_agent`, simultaneous sub-agent
execution when multiple intents are detected.

---

## Production checklist

- [ ] Embedder warmup in FastAPI lifespan before first request
- [ ] Checkpointer injected (not `MemorySaver`) for stateful services
- [ ] `AsyncAnthropic(max_retries=3)` — no custom retry logic
- [ ] All blocking I/O in `asyncio.to_thread()`
- [ ] DuckDB write paths: sync helper + `asyncio.to_thread` (single-writer lock)
- [ ] Chroma concurrent upsert behind `asyncio.Lock()`
- [ ] `escalate` flag surfaced in API response
- [ ] CORS origins explicit in production (not `"*"`)

## Never do

- Never `graph.compile()` inside a request handler
- Never `MemorySaver` in production
- Never mutate state in place inside a node
- Never `operator.add` on messages — always `add_messages`
- Never run Chroma/DuckDB/cross-encoder directly in `async def` without `to_thread`
