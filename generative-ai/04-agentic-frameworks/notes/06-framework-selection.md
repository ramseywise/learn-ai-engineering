---
origin: web-authored
sources:
  - https://docs.langchain.com/oss/python/langgraph/overview
  - https://google.github.io/adk-docs/
  - https://ai.pydantic.dev/
  - https://openai.github.io/openai-agents-python/
  - https://learn.microsoft.com/en-us/agent-framework/overview/
  - https://www.anthropic.com/engineering/building-effective-agents
  - https://github.com/humanlayer/12-factor-agents
confidence: medium
cleaned: 2026-10-31
---
# 6 — Framework Selection

> Pick the framework from the shape of the work, not the brand: how much control flow you must own, where state lives, which model you are tied to, and how you will trace and evaluate it. Start with no framework when you can.

Notes 01–05 built the same ideas in two frameworks and two tracing platforms. This note turns that into a decision. Framework details move fast; the dimensions below move slowly. Check each framework's docs for current APIs.

---

## First question: do you need one?

Anthropic's *Building Effective Agents* and *12-Factor Agents* make the same point: most production "agents" are a model call, a few tools and a loop you can read. Note 01's L1 agent is 40 lines.

| Signal | Framework earns its keep? |
|---|---|
| One model, a handful of tools, no pause/resume | No: a loop over the provider SDK's tool calling |
| You need checkpointed threads, HITL approval, or replay | Yes: durable execution is hard to hand-roll correctly |
| Several specialised steps with auditable routing | Yes: an explicit graph |
| You need built-in eval and a dev UI for non-engineers | Probably: ADK or a hosted platform |
| You are prototyping the prompt, not the system | No: framework abstractions hide what the model sees |

The cost of a framework is indirection: when a run goes wrong you debug the framework's prompt assembly and state merging as well as your own logic. [ai-engineering/05-graph-engineering 06 — when not to build a graph](../../../ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph.md) covers the same trade from the topology side.

---

## The dimensions

| Dimension | Question | Why it decides |
|---|---|---|
| Control flow | Who picks the next step: your code or the model? | Explicit edges are auditable; model-chosen handoffs are flexible |
| State | Typed shared state with reducers, a mutable session dict, or just the transcript? | Determines how parallel steps merge and what you can inspect |
| Durability | Checkpoint after every step? Resume after a crash? | Required for HITL and long runs |
| Model coupling | Any provider, or tuned for one? | Lock-in, and which features (caching, thinking) are exposed |
| Memory | Built-in cross-thread store? | Note 03 needs one |
| Observability | Native tracing, or bring your own? | Pillar 06 depends on it |
| Eval | Built-in harness? | ADK ships one; others rely on LangSmith/Langfuse/your own |
| Deployment | Library you host, or a managed runtime? | Ops burden vs vendor dependency |

---

## The frameworks

| | LangGraph | Google ADK | Pydantic AI | OpenAI Agents SDK | Microsoft Agent Framework |
|---|---|---|---|---|---|
| Core unit | Node over typed state | `Agent` with sub-agents | `Agent` with typed deps and output | `Agent` with tools and handoffs | Agents plus workflows |
| Control flow | Explicit edges, conditional edges, `Command` | LLM delegation + workflow agents (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) | Code calls agents; graph module for multi-step | Handoffs chosen by the model; guardrails | Agent orchestration plus typed graph workflows |
| State | `TypedDict` + reducers, checkpointed | `session.state` dict via `ToolContext` | Dependency injection, typed results | Run context, sessions | Thread and workflow state |
| Durability / HITL | Checkpointers, `interrupt()`, time travel (note 02) | Session services; resumability | Durable execution via integrations | `needs_approval` style HITL, sessions | Checkpointing in workflows |
| Long-term memory | `BaseStore` + langmem (note 03) | Memory service | Bring your own | Sessions; bring your own | Memory providers |
| Model coupling | Any (LangChain chat models) | Gemini-first, others via LiteLLM | Any; strong typing focus | OpenAI-first, others via adapters | Azure OpenAI-first, others supported |
| Tracing | LangSmith native; Langfuse via callback | Callbacks; Cloud Trace; Langfuse/LangSmith via OTEL | Logfire native (OTEL) | Built-in tracing to OpenAI dashboard; exportable | OpenTelemetry |
| Eval | External (LangSmith, Langfuse) | Built in: `adk eval`, trajectory and response metrics (note 04) | `pydantic-evals` | External | External / Azure AI Foundry |
| Best when | You need explicit, durable, auditable control flow | Gemini/Vertex shop, tree-shaped agents, want eval + dev UI in the box | You want plain typed Python and minimal magic | OpenAI-centric, handoff-shaped multi-agent | .NET or Azure shop; AutoGen/Semantic Kernel migrants |

Rows marked as "bring your own" are where you will write glue. Confidence is medium on everything in this table except the LangGraph and ADK columns, which the notes in this pillar work through in code.

---

## Decision table

| If your system… | Use | Note |
|---|---|---|
| Is one model + tools + a loop, no pause | Provider SDK, no framework | [01](01-react-from-scratch-to-langgraph.md) L1 |
| Needs approval gates, resume after crash, or replay | LangGraph | [02](02-agentic-search-persistence-streaming.md) |
| Must remember users across sessions and learn from feedback | LangGraph store + langmem | [03](03-long-term-memory-with-langgraph.md) |
| Runs on Gemini/Vertex and needs a built-in eval harness | ADK | [04](04-google-adk.md) |
| Is mostly typed I/O with a few model calls | Pydantic AI | — |
| Is a set of specialists that hand off to each other, on OpenAI | OpenAI Agents SDK | — |
| Lives in .NET/Azure | Microsoft Agent Framework | — |
| Has steps you can't name ahead of time (open research) | A harness with a good loop, not a graph | [graph-engineering 06](../../../ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph.md) |

---

## Running two frameworks side by side

The support-agent worked example in pillar 06 runs the same agent on ADK and LangGraph. What makes that workable:

| Practice | Why |
|---|---|
| Keep tools as plain functions, wrap per framework | Tool logic is tested once; only the adapter differs |
| Keep prompts outside the framework (files or a prompt registry) | Prompt changes don't fork per framework |
| One trace schema across both (same metadata keys, same score names) | Experiments compare frameworks, not tracing quirks |
| One eval dataset and one set of graders | The comparison is apples to apples |
| Put the framework name in trace metadata | Filter and diff by framework in the tracing UI |

The trace schema is [06-observability 05](../../06-observability/notes/05-support-agent-observability.md); the wiring per platform is [06-observability 01](../../06-observability/notes/01-tracing-with-langfuse.md) and [05 — LangSmith](05-langsmith.md).

---

## Tracing platform choice

| | Langfuse | LangSmith |
|---|---|---|
| Hosting | Open source, self-host or cloud | Hosted (self-host on enterprise plans) |
| LangGraph integration | `CallbackHandler` | Native: environment variables only |
| Other frameworks | Decorators, OTEL | `@traceable`, OTEL |
| Datasets and experiments | Yes | Yes |
| Prompt management | Yes | Yes (Prompt Hub) |
| MCP server for agents to query traces | Community server ([06-observability 04](../../06-observability/notes/04-langfuse-mcp-server.md)) | — |

Pick the one your team will look at every day. The data model (trace → span → score, dataset → run) is the same in both.

---

## The same agent, three ways

The L2 search agent from note 01, in outline. Exact imports drift; the shape doesn't.

```python
# No framework: provider tool calling + a while loop (note 01, L1 shape)
while True:
    msg = client.messages.create(model=..., tools=tool_schemas, messages=messages)
    messages.append(msg)
    calls = [b for b in msg.content if b.type == "tool_use"]
    if not calls:
        break
    messages.append({"role": "user", "content": [run_tool(c) for c in calls]})

# LangGraph prebuilt: the note-01 graph in one call, plus a checkpointer for threads
agent = create_react_agent("openai:gpt-4o", tools=[search], checkpointer=InMemorySaver())
agent.invoke({"messages": [("user", "weather in SF?")]}, {"configurable": {"thread_id": "1"}})

# ADK: an Agent with a FunctionTool, run through a Runner with a session service (note 04)
agent = Agent(name="search_agent", model="gemini-2.5-flash", instruction=..., tools=[search])
runner = Runner(agent=agent, app_name="demo", session_service=InMemorySessionService())
```

| | No framework | LangGraph prebuilt | ADK |
|---|---|---|---|
| Lines for the loop | ~10 | 1 | 2 |
| Threads / resume | Yours to build | Checkpointer | Session service |
| See the exact prompt sent | Trivially | Via tracing | Via callbacks / tracing |
| Swap the model | Rewrite for the other SDK | Change the model string | LiteLLM wrapper for non-Gemini |

---

## Lock-in checklist

Before committing, answer these for the candidate framework:

| Question | Bad answer |
|---|---|
| Can I export a run as plain messages + tool calls? | Only via the vendor's UI |
| Where is state persisted, and can I read it without the framework? | Opaque blobs only |
| Can I trace to an OTEL backend I choose? | Only the vendor's |
| Can I unit-test a node/tool without a model call? | Needs a live model |
| How many breaking releases in the last year? | More than you can absorb |

---

## Rules of thumb

| Rule | Why |
|---|---|
| Build the loop by hand once before adopting a framework | You learn what the framework hides ([01](01-react-from-scratch-to-langgraph.md)) |
| Choose by control flow and durability, not by demo | Those are the expensive things to change later |
| Keep tools, prompts and eval data framework-neutral | Switching cost drops to the adapter layer |
| Trace from day one, with framework and version in metadata | You can't compare what you didn't record |
| Pin versions; re-check imports against current docs | Every framework here renamed APIs within a year |

---

→ Next: this is the last note of the pillar. Tracing and evaluating these agents is [06-observability](../../06-observability/README.md); training the models inside them is [05-RL](../../05-RL/README.md).
