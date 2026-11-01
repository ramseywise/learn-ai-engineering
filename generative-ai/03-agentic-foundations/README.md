# 03 — Agentic Foundations

> Depth layer. Summary: [interviewing/guides/4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md)
> Position in the path: third generative-ai pillar, after [02-rag-retrieval](../02-rag-retrieval/README.md) and before [04-agentic-frameworks](../04-agentic-frameworks/README.md).
> Presumes: [01-llm-fundamentals](../01-llm-fundamentals/README.md), [02-rag-retrieval](../02-rag-retrieval/README.md).

---

## What it is

This pillar is where an LLM call becomes an agent: a model in a loop that chooses tools, remembers across turns and works with other agents. It covers the mechanics framework-agnostically, then shows how each framework packages them.

> **Agent = Model + Context + Tools, run in a loop.** Everything else (memory, multi-agent, frameworks) is a way to manage one of those three across many steps.

Four questions organise the notes:

| Question | Answer in this pillar |
|---|---|
| How does a model act? | It emits a tool call; your code runs it and returns the result (02) |
| How does it remember? | It edits its own memory with tool calls, and pages old context out to databases (03) |
| How do agents work together? | Conversations with stop conditions, nested chats, group chats, shared memory (04) |
| How do you keep it safe? | Lower the risk first, then filter, gate actions in code and keep people at the irreversible points (07) |

The two frameworks this course builds with, LangGraph and Google ADK, get full treatment in [04-agentic-frameworks](../04-agentic-frameworks/README.md); here they appear in the survey only (05). The engineering discipline on top (harness, loop, graph, eval) is in [ai-engineering](../../ai-engineering/).

---

## Why it matters

Agents fail in ways that a single model call does not. Errors compound across steps, an action can't be taken back, and a confident explanation is not evidence that the step was right. The value of this pillar is the set of mechanics that stay true whichever framework you pick, so that you can read a framework's abstraction and see what it does, and what it leaves to you.

## The story

One example runs through every note: a restock agent, from the inventory manager that opens *Generative AI Design Patterns*. It starts as one model call that orders 300 units of itemB, and arithmetic shows that it missed a stockout ([01](notes/01-agent-fundamentals.md)). It gets tools, and with them the rule that the model proposes while your code executes ([02](notes/02-tool-use-and-react.md)). It forgets last Monday's delivery-time change, so it gets a small core and a searchable archive ([03](notes/03-memory-as-an-operating-system.md)). A reviewer would catch bad orders, but that brings stop conditions and coordination failures ([04](notes/04-multi-agent-design-patterns.md)). A framework can then pause it for human approval, as long as resuming doesn't place the order twice ([05](notes/05-framework-survey.md)). Its growing policy moves into a skill, and evals check the path as well as the answer ([06](notes/06-google-adk-intensive.md)). Once it can spend money, the limits move out of the prompt and into code ([07](notes/07-guardrails-and-autonomy.md)).

## Start here

1. Read [01 — agent fundamentals](notes/01-agent-fundamentals.md) for the formula and the ReAct loop.
2. Read notes 02–04 in order. Each draws on a course whose labs are linked upstream.
3. Skim [05 — framework survey](notes/05-framework-survey.md), then go to [04-agentic-frameworks](../04-agentic-frameworks/README.md) for the frameworks you will use.
4. Read [06 — Google ADK intensive](notes/06-google-adk-intensive.md) for the engineering around the loop, and [07 — guardrails and autonomy](notes/07-guardrails-and-autonomy.md) before anything you build can act on the world.
5. Keep the [rules of thumb](#rules-of-thumb) as the one-page summary.

## Deck

[slides/agentic-foundations.pptx](slides/agentic-foundations.pptx) is the lecture for this pillar, in six parts plus a wrap-up, built from [slides/deck.yaml](slides/deck.yaml). Rebuild it with `make slides PILLAR=generative-ai/03-agentic-foundations`.

## Run the code

Every block in the notes without an `# illustrative` comment runs offline with the standard library, using stubs for the model, so you can paste it into a file and run `python3 file.py`. The one exception is the A2A status block in [05](notes/05-framework-survey.md), which needs Pydantic: `uv run --with pydantic python file.py`. Blocks marked `# illustrative` say on their first line what they need, usually a framework and an API key. This pillar has no `practice/` folder; the labs live upstream and are listed under [Coursework and practice](#coursework-and-practice).

## Layout

```
README.md      this file: overview, start here, rules of thumb, resource map
references.md  every source the notes cite, mapped to notes
notes/         01–07, the course; figures and code inline
slides/        deck.yaml and the built agentic-foundations.pptx
sources/       chapter PDFs (Generative AI Design Patterns, AI Agents: The Definitive Guide,
               Building Applications with AI Agents, Building AI Agents with LLMs, RAG, and KGs),
               the Letta lab handbook
  images/      every figure the notes use (<author>-<slug>-fig<N>)
```

---

## Syllabus

| # | Note | Covers |
|---|---|---|
| 1 | [Agent fundamentals](notes/01-agent-fundamentals.md) | The restock agent, Agent = LLM + context + tools, the context ablation, ReAct trajectory, a loop in one screen, model-as-agent, agents as state machines, choosing and staffing models, workflow vs autonomous, how agents learn |
| 2 | [Tool use and the ReAct loop](notes/02-tool-use-and-react.md) | The four-step tool-call mechanism, the raw loop, ReAct as a prompt, what reasoning steps fix and what they do not, caller/executor split, MCP servers, code execution, reliability rules, always call a tool first, tool preselection, six prompt-injection defenses |
| 3 | [Memory as an operating system](notes/03-memory-as-an-operating-system.md) | MemGPT's OS analogy, context compilation, core/recall/archival tiers, heartbeats, the Letta API, agentic RAG, P28 memory types, LangMem, shared blocks |
| 4 | [Multi-agent design patterns](notes/04-multi-agent-design-patterns.md) | Ng's four patterns, AutoGen L1–L6 (conversation, sequential chats, reflection, tool use, coding, planning), planning strategies (plan-and-execute, ToT), Letta multi-agent, P23 architectures, supervisor/hierarchical/swarm, why multi-agent systems fail |
| 5 | [Framework survey](notes/05-framework-survey.md) | AutoGen, CrewAI, LangGraph deep research, Google ADK, OpenAI Agents SDK, smolagents, LangGraph subgraphs and `interrupt`, MCP vs A2A, MLflow eval, choosing a framework |
| 6 | [Google ADK intensive](notes/06-google-adk-intensive.md) | Kaggle five-day course notes, Days 1–3: agentic engineering, tests vs evals, trajectory evaluation, context types, the new SDLC, harness, protocols, agent skills |
| 7 | [Guardrails and autonomy](notes/07-guardrails-and-autonomy.md) | Where controls sit, lowering risk before filtering (P29–P32), self-check limits, execution gates, what the user must see, autonomy levels |

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
| Use plain code or a fixed workflow when the steps are known; reach for an agent only when the path depends on what it finds | [01](notes/01-agent-fundamentals.md) |
| Cap the loop and make the last step a wrap-up, not a silent cutoff | [01](notes/01-agent-fundamentals.md) |
| A prompt restriction is not a permission: enforce limits in credentials and code | [07](notes/07-guardrails-and-autonomy.md) |
| Staff models by role: a cheap fast model for routine steps, a reasoning budget only where it pays | [01](notes/01-agent-fundamentals.md) |
| Past roughly ten tools, retrieve the relevant few per turn instead of sending all of them | [02](notes/02-tool-use-and-react.md) |
| Plan with the model, execute arithmetic and lookups in code | [02](notes/02-tool-use-and-react.md) |
| Count the calls before you search over plans: width and depth multiply | [04](notes/04-multi-agent-design-patterns.md) |
| Keep the verbatim record and curate the index on top of it | [03](notes/03-memory-as-an-operating-system.md) |
| Never put a side effect in the same node as an `interrupt` | [05](notes/05-framework-survey.md) |
| Evaluate the trajectory as well as the output: a lucky run passes an output check | [06](notes/06-google-adk-intensive.md) |
| Keep task-specific rules in skills, and test that their descriptions trigger | [06](notes/06-google-adk-intensive.md) |
| Ask how much the model needs to write before adding filters: templates, then assembled facts, then guardrails | [07](notes/07-guardrails-and-autonomy.md) |
| Rate tools by what they can undo, deny by default, and keep hard limits no approval can override | [07](notes/07-guardrails-and-autonomy.md) |

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
- Lakshmanan & Hapke, *Generative AI Design Patterns* (O'Reilly, 2025): chapter PDFs in [sources/](sources/); ch. 1, 5–10 → notes 01–05, 07.
- DeepLearning.AI, *LLMs as Operating Systems: Agent Memory* → notes 02–04.
- DeepLearning.AI, *AI Agentic Design Patterns with AutoGen* → notes 02, 04.
- Google × Kaggle, *5-Day AI Agents Intensive* → note 06.
- More courses and videos, with platform and cost: [references.md](references.md#courses-and-videos).
- Koenigstein, *AI Agents: The Definitive Guide* (O'Reilly, 2026; Early Release): ch. 1, 2, 4 → notes 01, 02, 04, 05 (agents as state machines, staffing models by role, cheap ToT, handoffs, `interrupt`).
- Oshin & Campos, *Learning LangChain* (O'Reilly, 2025): ch. 6–7 → notes 02, 04, 05 (always call a tool first, tool preselection, reflection graph, supervisor, subgraphs).
- Phoenix & Taylor, *Prompt Engineering for Generative AI* (O'Reilly, 2024): ch. 6 → notes 01–04 (ReAct parsing, step caps, legacy memory classes, plan-and-execute, ToT).
- Albada, *Building Applications with AI Agents* (O'Reilly, 2025): ch. 1–2 → notes 01, 02, 04, 05 (when an agent is warranted, scoping the first agent, model choice).
- Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025): ch. 4, 11 → notes 02, 04, 05, 07 (planning taxonomy, autonomy levels, CoT limits, single vs multi-agent).

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
- [sources/](sources/): *Generative AI Design Patterns* ch. 1–10, *AI Agents: The Definitive Guide* ch. 1, 2, 4, *Building Applications with AI Agents* ch. 1–2, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* ch. 4, 11 PDFs; *Learning LangChain* and *Prompt Engineering for Generative AI* live in [01-llm-fundamentals/sources/](../01-llm-fundamentals/sources/); [the Letta lab handbook](sources/packer-wooders-agent-memory-handbook.pdf).
- Papers (ReAct, MemGPT, Toolformer, prompt-injection patterns, multi-agent failures, Mem0, Tree of Thoughts, the planning survey, CoT limits) and the curated guides: [references.md](references.md).

### Interviewing guide
- [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md): compressed summary for interview prep: agent harness, tool use, loop design, memory, multi-agent orchestration.

### Previous and next layer
← [02-rag-retrieval](../02-rag-retrieval/README.md): retrieval, which note 03 turns into agentic RAG.
→ [04-agentic-frameworks](../04-agentic-frameworks/README.md): LangGraph and Google ADK in depth, LangSmith, framework selection.
