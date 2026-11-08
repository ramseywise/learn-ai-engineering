# 04 — Agentic Frameworks

> Interview recall: the checklists in these notes. Role map: [interviewing](../../practice/interviewing/README.md).
> Position: fourth generative-ai pillar, the framework layer. Builds on [03-agentic-foundations](../03-agentic-foundations/README.md); the theory it implements is [ai-engineering/05-graph-engineering](../../ai-engineering/05-graph-engineering/README.md).

---

## What it is

The hands-on framework layer: how the agent ideas from 03 and from ai-engineering's loop and graph pillars look in real code, and how to choose between the frameworks that implement them.

The pillar builds one research agent several times, all on the question "Why do framework agents get stuck in loops, and what stops them?". First it is a 40-line Python loop around a chat model. Then it is a two-node LangGraph graph, then a graph with a checkpointer, streaming and human approval, then one with semantic, episodic and procedural memory in a store. The same agent moves to Google ADK, and LangSmith traces both builds. With three working builds in hand, a selection note measures what each costs, how each stops when the model won't, and what the research says about how these frameworks fail. A last note drops one layer down to the LCEL chains that sit inside graph nodes.

## Why it matters

Framework choice is one of the expensive decisions in an agent project, and the demos won't help you make it. All three builds in the lab return the identical answer. Left to run on a stuck model, one stops after 6 calls, one after 500 and one after 5,004. You find differences like that only by building the same thing more than once and measuring it, so that is how this pillar is organised. [Wang et al.](https://arxiv.org/abs/2512.01939) classified 8,710 developer discussions from 1,575 GitHub agent projects and put more than a third of the reported failures down to logic control: termination, message cooling and state. Those are shares of what developers complain about, not a failure rate, and the frameworks here leave all three to you.

> **Build the loop by hand once. Then a framework is a set of things you no longer write, and you can judge whether that set is worth its indirection.**

Theory stays in ai-engineering. Why an agent is a cyclic graph, how reducers merge parallel writes, and where approval gates go are covered in [05-graph-engineering](../../ai-engineering/05-graph-engineering/README.md) notes 02–05. The memory taxonomy is in [02-context-engineering 06](../../ai-engineering/02-context-engineering/notes/06-memory.md). The notes here link to those rather than repeat them.

---

## Start here

1. Read notes 01–03 in order, running each demo as you go. They begin from the two DeepLearning.AI LangGraph courses, grown onto the lab's research agent.
2. Read 04 to see the same agent on ADK, and 05 to trace both builds with LangSmith.
3. Read 06 before choosing a framework for anything new. It compares the three builds and weighs them against the research.
4. Read 07 when a node needs a multi-step chain, a fan-out, structured output or a plan of dependent queries. Read [01-llm-fundamentals note 11](../01-llm-fundamentals/notes/11-langchain-basics.md) first if LCEL is new.
5. Keep the [rules of thumb](#rules-of-thumb) as the one-page summary.

## Deck and practice

- **Deck:** [slides/agentic-frameworks.pptx](slides/agentic-frameworks.pptx), with a [PDF](slides/agentic-frameworks.pdf). Build it with `make slides PILLAR=generative-ai/04-agentic-frameworks`.
- **Lab:** [practice/01-research-agent/](practice/01-research-agent/README.md) runs every note offline with no API key. From that folder, try `uv run --with langgraph --with 'google-adk[eval]' python demo_06_selection.py`.

## Layout

```
README.md      this file: overview, start here, syllabus, rules of thumb, resource map
references.md  every source the notes cite, mapped to notes, with licences
notes/         01–07, the course; code and figures inline
practice/      01-research-agent: the same agent built each way, offline
slides/        deck.yaml and the built deck
sources/       the papers these notes cite, as PDFs
  images/      course figures (ksm26-ai-agents-in-langgraph-fig1..6),
               book figures (prompt-engineering-for-generative-ai-fig4-7,
               agentic-architectural-patterns-fig14-2)
```

---

## Syllabus

| # | Note | Covers |
|---|---|---|
| 1 | [ReAct from scratch to LangGraph](notes/01-react-from-scratch-to-langgraph.md) | L1 hand-rolled ReAct loop (prompt protocol, registry, regex parser); L2 the same agent as a `StateGraph`: state, reducer, nodes, conditional edge, `bind_tools`, `ToolMessage`; API drift |
| 2 | [Agentic search, persistence, streaming](notes/02-agentic-search-persistence-streaming.md) | L3 agent-oriented search vs scrape; L4 checkpointers and threads, node vs token streaming; L5 HITL (interrupt, inspect, edit, time travel); L6 essay-writer graph |
| 3 | [Long-term memory with LangGraph](notes/03-long-term-memory-with-langgraph.md) | Triage router + ReAct agent; semantic memory (store + langmem tools), episodic (few-shot from labelled examples), procedural (prompts in the store, `create_multi_prompt_optimizer`); namespace map |
| 4 | [Google ADK](notes/04-google-adk.md) | The research agent on ADK: primitives, ADK vs LangGraph, `Workflow`, `max_llm_calls`, `ToolContext` state, `adk run`/`adk web`, eval metrics and config, guardrail callbacks and plugins |
| 5 | [LangSmith](notes/05-langsmith.md) | Tracing both builds, with runs captured offline: wiring for LangGraph and ADK, trace anatomy, reading a stuck run, datasets, `evaluate()`, testing whether a cheaper model is good enough, annotation queues |
| 6 | [Framework selection](notes/06-framework-selection.md) | Do you need one; measured cost and stuck-run behaviour of the three builds; the dimensions; five frameworks compared; what the empirical studies found; running two side by side; lock-in checklist with an export test |
| 7 | [LCEL composition in practice](notes/07-lcel-composition-in-practice.md) | Data flow (`RunnablePassthrough.assign`, `itemgetter`, `RunnableParallel`), sequential vs batch with `max_concurrency`, three routes to structured output (`tool_choice`, hallucinated arguments), a query plan as a validated DAG, map-reduce, few-shot limits, book APIs and their current form |

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| None in other subjects | Starts from [GA 03](../03-agentic-foundations/README.md) in this subject |

**Feeds into**

| Chapter | Why |
|---|---|
| [AIE 05/02 Graph primitives](../../ai-engineering/05-graph-engineering/notes/02-graph-primitives.md) | The primitives under the frameworks |
| [AIE 02/10 Tools and multi-agent](../../ai-engineering/02-context-engineering/notes/10-tools-and-multi-agent.md) | Context in multi-agent systems |
| [AIE 03/07 Orchestration](../../ai-engineering/03-harness-engineering/notes/07-orchestration.md) | Orchestration from the harness side |

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
| An accuracy against labels from a stronger model measures agreement with that model; spot-check the labels, and count parse failures separately | [05](notes/05-langsmith.md#testing-whether-a-cheaper-model-is-good-enough) |
| Cap every `.batch()` with `max_concurrency` | [07](notes/07-lcel-composition-in-practice.md#fan-out-with-a-concurrency-cap) |
| Validate a model-written plan (unknown ids, cycles) before executing it | [07](notes/07-lcel-composition-in-practice.md#query-planning-a-plan-is-a-dag) |
| Never load prompts with pickle; keep them as text files under version control | [07](notes/07-lcel-composition-in-practice.md#few-shot-selection-and-prompt-files) |
| Choose a framework by control flow and durability, not by demo | [06](notes/06-framework-selection.md) |
| Set the loop limit on every invocation; the defaults allow 500 to 5,004 model calls | [06](notes/06-framework-selection.md#how-each-build-stops-when-the-model-wont) |
| Keep tools, prompts and eval data framework-neutral | [06](notes/06-framework-selection.md) |

---

## Primary texts

- Phoenix and Taylor, *Prompt Engineering for Generative AI*
- LangGraph documentation
- Google ADK documentation
- Chase and Weiss, *AI Agents in LangGraph*

Everything else: [references.md](references.md).

## Resource map

### Related notes elsewhere
- Theory: [ai-engineering/05-graph-engineering](../../ai-engineering/05-graph-engineering/README.md) notes [02 primitives](../../ai-engineering/05-graph-engineering/notes/02-graph-primitives.md), [03 state and reducers](../../ai-engineering/05-graph-engineering/notes/03-state-and-reducers.md), [04 durable execution and interrupts](../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md), [05 topology patterns](../../ai-engineering/05-graph-engineering/notes/05-topology-patterns.md).
- Loops and harnesses: [ai-engineering/04-loop-engineering](../../ai-engineering/04-loop-engineering/README.md), [ai-engineering/03-harness-engineering](../../ai-engineering/03-harness-engineering/README.md).
- Memory: [ai-engineering/02-context-engineering 06 — memory](../../ai-engineering/02-context-engineering/notes/06-memory.md).
- Tracing and evaluating these agents: [06-observability](../06-observability/README.md). Langfuse is covered there in [01 — tracing with Langfuse](../06-observability/notes/01-tracing-with-langfuse.md).

### Books and courses
- DeepLearning.AI, *AI Agents in LangGraph* → notes 01–02.
- DeepLearning.AI × LangChain, *Long-Term Agentic Memory with LangGraph* → note 03.
- Phoenix & Taylor, *Prompt Engineering for Generative AI* ch. 4 → notes 07 and 05. Oshin & Campos, *Learning LangChain* ch. 1 → note 07 (API flags only; the basics are in [01-llm-fundamentals note 11](../01-llm-fundamentals/notes/11-langchain-basics.md)).
- Full citations, upstream repos and licences: [references.md](references.md).

### Coursework and practice
[practice/01-research-agent/](practice/01-research-agent/README.md) runs the code from every note offline, with a stub model. Its README lists the command for each note. The course snapshots were condensed into the notes and removed, and each note's **Labs** table links the upstream notebooks, which need API keys. Running on real models takes a provider key, and ADK's `adk run`, `adk web` and `adk eval` need a Gemini key or a Vertex project.

### Readings
- Framework docs and guides (Anthropic, OpenAI, 12-Factor Agents, ReAct): [references.md](references.md).

### Interviewing guide
- [Interviewing](../../practice/interviewing/README.md): role map to these checklists, and the rounds.

### Previous and next layer
← [03-agentic-foundations](../03-agentic-foundations/README.md)
→ [05-RL](../05-RL/README.md): how the models inside these agents are post-trained, including RL for agentic behaviour.
