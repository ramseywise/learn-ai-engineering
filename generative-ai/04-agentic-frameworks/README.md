# 04 — Agentic Frameworks

> Depth layer. Summary: [interviewing/guides/4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md)
> Position: fourth generative-ai pillar, the framework layer. Builds on [03-agentic-foundations](../03-agentic-foundations/README.md); the theory it implements is [ai-engineering/05-graph-engineering](../../ai-engineering/05-graph-engineering/README.md).

---

## What it is

The hands-on framework layer: how the agent ideas from 03 and from ai-engineering's loop and graph pillars look in real code, and how to choose between the frameworks that implement them.

The pillar builds one agent several times. First it is a 40-line Python loop around a chat model. Then it is a two-node LangGraph graph, then a graph with a checkpointer, streaming and human approval, and finally an email assistant with semantic, episodic and procedural memory in a LangGraph store. Google ADK and LangSmith follow as reference specs. A selection note closes the pillar by turning all of that into a decision.

> **Build the loop by hand once. Then a framework is a set of things you no longer write, and you can judge whether that set is worth its indirection.**

Theory stays in ai-engineering. Why an agent is a cyclic graph, how reducers merge parallel writes, and where approval gates go are covered in [05-graph-engineering](../../ai-engineering/05-graph-engineering/README.md) notes 02–05. The memory taxonomy is in [02-context-engineering 06](../../ai-engineering/02-context-engineering/notes/06-memory.md). The notes here link to those rather than repeat them.

---

## Start here

1. Read notes 01–03 in order. They are the two DeepLearning.AI LangGraph courses, condensed with their code and figures inline.
2. Read 04 (ADK) and 05 (LangSmith) as reference specs, when you need them.
3. Read 06 before choosing a framework for anything new.
4. Keep the [rules of thumb](#rules-of-thumb) as the one-page summary.

## Layout

```
README.md      this file: overview, start here, syllabus, rules of thumb, resource map
references.md  every source the notes cite, mapped to notes, with licences
notes/         01–06, the course; code and figures inline
sources/
  images/      course figures (ksm26-ai-agents-in-langgraph-fig1..6)
```

---

## Syllabus

| # | Note | Covers |
|---|---|---|
| 1 | [ReAct from scratch to LangGraph](notes/01-react-from-scratch-to-langgraph.md) | L1 hand-rolled ReAct loop (prompt protocol, registry, regex parser); L2 the same agent as a `StateGraph`: state, reducer, nodes, conditional edge, `bind_tools`, `ToolMessage`; API drift |
| 2 | [Agentic search, persistence, streaming](notes/02-agentic-search-persistence-streaming.md) | L3 agent-oriented search vs scrape; L4 checkpointers and threads, node vs token streaming; L5 HITL (interrupt, inspect, edit, time travel); L6 essay-writer graph |
| 3 | [Long-term memory with LangGraph](notes/03-long-term-memory-with-langgraph.md) | Triage router + ReAct agent; semantic memory (store + langmem tools), episodic (few-shot from labelled examples), procedural (prompts in the store, `create_multi_prompt_optimizer`); namespace map |
| 4 | [Google ADK](notes/04-google-adk.md) | Primitives, ADK vs LangGraph, workflow agents, `ToolContext` state, `adk run`/`adk web`, ADK eval metrics and config, guardrail callbacks |
| 5 | [LangSmith](notes/05-langsmith.md) | Wiring for LangGraph (env vars) and ADK (`@traceable`), trace anatomy, datasets, `evaluate()`, annotation queues, experiment comparison |
| 6 | [Framework selection](notes/06-framework-selection.md) | Do you need one; the dimensions; LangGraph, ADK, Pydantic AI, OpenAI Agents SDK, MS Agent Framework compared; decision table; running two frameworks side by side; lock-in checklist |

## Rules of thumb

| Rule | Note |
|---|---|
| Build the loop by hand once before adopting a framework | [01](notes/01-react-from-scratch-to-langgraph.md) |
| Use native tool calling and structured output; never regex-parse the model's prose for control flow | [01](notes/01-react-from-scratch-to-langgraph.md), [03](notes/03-long-term-memory-with-langgraph.md) |
| Return a bad tool name to the model as an observation instead of raising | [01](notes/01-react-from-scratch-to-langgraph.md) |
| Tool output is context: prefer tools that return short, structured results | [02](notes/02-agentic-search-persistence-streaming.md) |
| A checkpointer is short-term memory for one thread; cross-thread facts go in a store | [02](notes/02-agentic-search-persistence-streaming.md), [03](notes/03-long-term-memory-with-langgraph.md) |
| Interrupt before the action whose consequences you can't undo | [02](notes/02-agentic-search-persistence-streaming.md) |
| Namespace memory by user id from the run config, never from model output | [03](notes/03-long-term-memory-with-langgraph.md) |
| Correct behaviour with labelled examples before rewriting rules | [03](notes/03-long-term-memory-with-langgraph.md) |
| Treat an optimizer's prompt rewrite as a deploy: diff it, log it, be able to roll back | [03](notes/03-long-term-memory-with-langgraph.md) |
| Choose a framework by control flow and durability, not by demo | [06](notes/06-framework-selection.md) |
| Keep tools, prompts and eval data framework-neutral | [06](notes/06-framework-selection.md) |

---

## Resource map

### Related notes elsewhere
- Theory: [ai-engineering/05-graph-engineering](../../ai-engineering/05-graph-engineering/README.md) notes [02 primitives](../../ai-engineering/05-graph-engineering/notes/02-graph-primitives.md), [03 state and reducers](../../ai-engineering/05-graph-engineering/notes/03-state-and-reducers.md), [04 durable execution and interrupts](../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md), [05 topology patterns](../../ai-engineering/05-graph-engineering/notes/05-topology-patterns.md).
- Loops and harnesses: [ai-engineering/04-loop-engineering](../../ai-engineering/04-loop-engineering/README.md), [ai-engineering/03-harness-engineering](../../ai-engineering/03-harness-engineering/README.md).
- Memory: [ai-engineering/02-context-engineering 06 — memory](../../ai-engineering/02-context-engineering/notes/06-memory.md).
- Tracing and evaluating these agents: [06-observability](../06-observability/README.md). Langfuse is covered there in [01 — tracing with Langfuse](../06-observability/notes/01-tracing-with-langfuse.md).

### Books and courses
- DeepLearning.AI, *AI Agents in LangGraph* → notes 01–02.
- DeepLearning.AI × LangChain, *Long-Term Agentic Memory with LangGraph* → note 03.
- Full citations, upstream repos and licences: [references.md](references.md).

### Coursework and practice
The course snapshots were condensed into the notes and removed. Each note ends with a **Labs** table linking the upstream notebooks:

| Lab | Note | Runs |
|---|---|---|
| ReAct from scratch, LangGraph components (L1–L2) | [01](notes/01-react-from-scratch-to-langgraph.md#labs) | Needs `OPENAI_API_KEY`; L2 also `TAVILY_API_KEY` |
| Agentic search, persistence, streaming (L3–L4) | [02](notes/02-agentic-search-persistence-streaming.md#labs) | Needs `OPENAI_API_KEY`, `TAVILY_API_KEY` |
| HITL, essay writer (L5–L6) | [02](notes/02-agentic-search-persistence-streaming.md#labs) | DeepLearning.AI platform only |
| Email assistant with memory (L2–L5) | [03](notes/03-long-term-memory-with-langgraph.md#labs) | Needs `OPENAI_API_KEY`; L3 and L5 also `ANTHROPIC_API_KEY` |
| ADK `adk run` / `adk web` / `adk eval` | [04](notes/04-google-adk.md) | Needs a Gemini API key or Vertex project |

### Readings
- Framework docs and guides (Anthropic, OpenAI, 12-Factor Agents, ReAct): [references.md](references.md).

### Interviewing guide
- [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md): compressed summary for interview prep.

### Previous and next layer
← [03-agentic-foundations](../03-agentic-foundations/README.md)
→ [05-RL](../05-RL/README.md): how the models inside these agents are post-trained, including RL for agentic behaviour.
