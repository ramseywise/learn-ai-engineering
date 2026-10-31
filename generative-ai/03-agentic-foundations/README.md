# 03 — Agentic Foundations

> Depth layer. Summary: [interviewing/guides/4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md)
> Position in the path: third generative-ai pillar, after [02-rag-retrieval](../02-rag-retrieval/README.md) and before [04-agentic-frameworks](../04-agentic-frameworks/README.md).
> Presumes: [01-llm-fundamentals](../01-llm-fundamentals/README.md), [02-rag-retrieval](../02-rag-retrieval/README.md).

---

## What it is

This pillar is where an LLM call becomes an agent: a model in a loop that chooses tools, remembers across turns and works with other agents. It covers the mechanics framework-agnostically, then shows how each framework packages them.

> **Agent = Model + Context + Tools, run in a loop.** Everything else (memory, multi-agent, frameworks) is a way to manage one of those three across many steps.

Three questions organise the notes:

| Question | Answer in this pillar |
|---|---|
| How does a model act? | It emits a tool call; your code runs it and returns the result (02) |
| How does it remember? | It edits its own memory with tool calls, and pages old context out to databases (03) |
| How do agents work together? | Conversations with stop conditions, nested chats, group chats, shared memory (04) |

The two frameworks this course builds with, LangGraph and Google ADK, get full treatment in [04-agentic-frameworks](../04-agentic-frameworks/README.md); here they appear in the survey only (05). The engineering discipline on top (harness, loop, graph, eval) is in [ai-engineering](../../ai-engineering/).

---

## Start here

1. Read [01 — agent fundamentals](notes/01-agent-fundamentals.md) for the formula and the ReAct loop.
2. Read notes 02–04 in order; each one is built from a course whose labs are linked upstream.
3. Skim [05 — framework survey](notes/05-framework-survey.md), then go to [04-agentic-frameworks](../04-agentic-frameworks/README.md) for the frameworks you will use.
4. Keep the [rules of thumb](#rules-of-thumb) as the one-page summary.

## Layout

```
README.md      this file: overview, start here, rules of thumb, resource map
references.md  every source the notes cite, mapped to notes
notes/         01–06, the course; figures and code inline
sources/       Generative AI Design Patterns chapter PDFs, the Letta lab handbook
  images/      every figure the notes use (<author>-<slug>-fig<N>)
```

---

## Syllabus

| # | Note | Covers |
|---|---|---|
| 1 | [Agent fundamentals](notes/01-agent-fundamentals.md) | Agent = LLM + context + tools, the context ablation, ReAct trajectory, model-as-agent, workflow vs autonomous, guardrails, how agents learn |
| 2 | [Tool use and the ReAct loop](notes/02-tool-use-and-react.md) | The four-step tool-call mechanism, the raw loop, ReAct as a prompt, caller/executor split, MCP servers, code execution, reliability rules, six prompt-injection defenses |
| 3 | [Memory as an operating system](notes/03-memory-as-an-operating-system.md) | MemGPT's OS analogy, context compilation, core/recall/archival tiers, heartbeats, the Letta API, agentic RAG, P28 memory types, LangMem, shared blocks |
| 4 | [Multi-agent design patterns](notes/04-multi-agent-design-patterns.md) | Ng's four patterns, AutoGen L1–L6 (conversation, sequential chats, reflection, tool use, coding, planning), Letta multi-agent, P23 architectures, why multi-agent systems fail |
| 5 | [Framework survey](notes/05-framework-survey.md) | AutoGen, CrewAI, LangGraph deep research, Google ADK, OpenAI Agents SDK, smolagents, MCP vs A2A, MLflow eval, choosing a framework |
| 6 | [Google ADK intensive](notes/06-google-adk-intensive.md) | Kaggle five-day course notes, Days 1–3: agentic engineering, context types, the new SDLC, harness, protocols, agent skills |

## Rules of thumb

| Rule | Note |
|---|---|
| The model proposes a call; your code decides whether and how to run it | [02](notes/02-tool-use-and-react.md) |
| Keep the tool list to roughly 3–10 tools, each with one job and a clear description | [02](notes/02-tool-use-and-react.md) |
| Never make the model fill in values your code already knows | [02](notes/02-tool-use-and-react.md) |
| Return readable errors from tools so the model can retry | [02](notes/02-tool-use-and-react.md), [05](notes/05-framework-survey.md) |
| Generated code runs in a sandbox, never on the host | [02](notes/02-tool-use-and-react.md) |
| Tool output is untrusted input: pick a prompt-injection pattern before you ship | [02](notes/02-tool-use-and-react.md) |
| Small core memory, big searchable archive; show the agent what it is not seeing | [03](notes/03-memory-as-an-operating-system.md) |
| Tell the agent when to save and when to search; it will not do either by default | [03](notes/03-memory-as-an-operating-system.md) |
| Every multi-agent conversation needs a turn cap and a semantic stop | [04](notes/04-multi-agent-design-patterns.md) |
| Constrain who speaks after whom; free speaker selection derails | [04](notes/04-multi-agent-design-patterns.md) |
| Share facts through shared state, not through more messages | [04](notes/04-multi-agent-design-patterns.md) |
| Start with one agent; most multi-agent failures are coordination failures | [04](notes/04-multi-agent-design-patterns.md) |
| Pick the framework by its unit of programming: conversation, crew, graph or agent object | [05](notes/05-framework-survey.md) |

---

## Resource map

### Related notes elsewhere
- [ai-engineering/02-context-engineering 06 — memory](../../ai-engineering/02-context-engineering/notes/06-memory.md): memory theory and production designs; note 03 here covers only the MemGPT/Letta OS framing.
- [ai-engineering/02-context-engineering 10 — tools and multi-agent](../../ai-engineering/02-context-engineering/notes/10-tools-and-multi-agent.md) and [09 — protocols](../../ai-engineering/02-context-engineering/notes/09-protocols.md).
- [ai-engineering/03-harness-engineering](../../ai-engineering/03-harness-engineering/README.md): [01 — what a harness is](../../ai-engineering/03-harness-engineering/notes/01-what-a-harness-is.md), [03 — tool design](../../ai-engineering/03-harness-engineering/notes/03-tool-design.md), [04 — execution boundaries](../../ai-engineering/03-harness-engineering/notes/04-execution-boundaries.md), [07 — orchestration](../../ai-engineering/03-harness-engineering/notes/07-orchestration.md).
- [ai-engineering/04-loop-engineering](../../ai-engineering/04-loop-engineering/README.md): termination, scorekeepers, [framework bindings](../../ai-engineering/04-loop-engineering/notes/10-framework-bindings.md).
- [ai-engineering/05-graph-engineering](../../ai-engineering/05-graph-engineering/README.md): multi-agent topology.
- [ai-engineering/06-eval 06 — evaluating agents](../../ai-engineering/06-eval/notes/06-evaluating-agents.md) and [06-observability](../06-observability/README.md): tracing and scoring agents.
- [07-agentic-applications](../07-agentic-applications/README.md): deployed projects built with these frameworks.

### Books and courses
- Bojie Li, *AI Agents in Depth* (2026, [upstream](https://github.com/bojieli/ai-agent-book), Apache-2.0): ch. 1 → note 01.
- Lakshmanan & Hapke, *Generative AI Design Patterns* (O'Reilly, 2025): chapter PDFs in [sources/](sources/); ch. 6–8 and 10 → notes 02–05.
- DeepLearning.AI, *LLMs as Operating Systems: Agent Memory* → notes 02–04.
- DeepLearning.AI, *AI Agentic Design Patterns with AutoGen* → notes 02, 04.
- Google × Kaggle, *5-Day AI Agents Intensive* → note 06.

### Coursework and practice
The labs are not copied into this repo. Run them from upstream:

| Lab | Upstream | Runs |
|---|---|---|
| Letta L1: self-editing memory from scratch | [frankwwu/LLMs-as-Operating-Systems--Agent-Memory](https://github.com/frankwwu/LLMs-as-Operating-Systems--Agent-Memory) | needs an OpenAI key |
| Letta L3–L6: agents, custom memory, agentic RAG, multi-agent | same | needs a local Letta server (`letta==0.6.50`, port 8283) + OpenAI key |
| AutoGen L1–L3: conversation, sequential chats, reflection | [ksm26/AI-Agentic-Design-Patterns-with-AutoGen](https://github.com/ksm26/AI-Agentic-Design-Patterns-with-AutoGen) | needs an OpenAI key |
| AutoGen L4–L6: chess, coding, planning | same | needs an OpenAI key (gpt-4-turbo); L5–L6 execute generated code locally and fetch data with yfinance |
| Framework POCs (AutoGen, CrewAI, LangGraph, ADK, smolagents, MCP, A2A, MLflow) | [adv-11/AgenticAIFrameworks](https://github.com/adv-11/AgenticAIFrameworks) | needs provider keys (OpenAI, Anthropic, Gemini, Mistral, Serper, Tavily, HF) per script; the MCP server runs offline except for arXiv search |

### Readings
- [sources/](sources/): *Generative AI Design Patterns* ch. 1–10 PDFs; [the Letta lab handbook](sources/packer-wooders-agent-memory-handbook.pdf).
- Papers (ReAct, MemGPT, Toolformer, prompt-injection patterns, multi-agent failures, Mem0) and the curated guides: [references.md](references.md).

### Interviewing guide
- [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md): compressed summary for interview prep: agent harness, tool use, loop design, memory, multi-agent orchestration.

### Previous and next layer
← [02-rag-retrieval](../02-rag-retrieval/README.md): retrieval, which note 03 turns into agentic RAG.
→ [04-agentic-frameworks](../04-agentic-frameworks/README.md): LangGraph and Google ADK in depth, LangSmith, framework selection.
