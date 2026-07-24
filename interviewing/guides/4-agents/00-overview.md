# Pillar 4 — Agents (orchestration, tools, memory, harness)

Systems where the LLM decides what to do next: call tools, keep state, plan multi-step
work, recover from failures. This is the deepest pillar in the repo's sources — it's what
the librarian wiki and most of the cleaned notes are about — and the center of gravity of
2026 AI-engineering work.

## Learning path

1. **Concepts before frameworks** — *Building Applications with AI Agents* chs 1–5
   (`ai-engineering/readings/ai_engineering/ai_agent_applications/`): agents, tool use, orchestration.
   Pair with the ReAct paper (pillar 2) — the loop everything else elaborates.
2. **One framework, properly** — LangGraph *or* Google ADK via
   `generative-ai/03-agentic-foundations/` course repos; librarian's `wiki/langgraph/` and
   `wiki/adk/` pages are the compiled experience layer on top.
3. **Tools & MCP** — *Model Context Protocol* chapters (`ai-engineering/readings/ai_engineering/mcp/`);
   tool-design-as-UX (ACI/poka-yoke) from the wiki patterns pages.
4. **Memory & state** — notes ([memory.md](../../../ai-engineering/05-graph/memory.md),
   [deep-agents.md](../../../ai-engineering/04-loop/deep-agents.md)) + `wiki/memory/` + the Memoria/
   memory-augmented-RAG flow; chatbot-memory pilot paper (Yan et al. 2025, see librarian wiki).
5. **Harness engineering** — the notes cluster unique to this repo:
   [agent-harness](../../../ai-engineering/03-harness/agent-harness.md), [loop-engineering](../../../ai-engineering/04-loop/loop-engineering.md),
   [reliable-agents](../../../ai-engineering/03-harness/reliable-agents.md) — acceptance baselines, execution
   boundaries, feedback signals, rollback.
6. **Multi-agent, skeptically** — *From One Agent to Many* (agent applications ch 8),
   `ai-engineering/readings/ai_engineering/multiagent context/`, notes
   [agents-design.md](../../../ai-engineering/03-harness/agents-design.md); protocol/task-graph/isolation triad.

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| *Building Applications with AI Agents* (chs 1–13) | pdf | `ai-engineering/readings/ai_engineering/ai_agent_applications/` | full agent lifecycle incl. validation, monitoring, protection |
| *Generative AI Design Patterns* (chs 1–10) | pdf | `ai-engineering/readings/ai_engineering/ai design/` | pattern language: knowledge, actions, safeguards, composable workflows |
| *AI Engineering* (Huyen, ch 6 RAG & Agents) | pdf | `ai-engineering/readings/ai_engineering/ai engineer/` | agents in the app-architecture frame |
| MCP · LangChain · multiagent-context books | pdf | `ai-engineering/readings/ai_engineering/{mcp,langchain,multiagent context}/` | protocol + framework depth |
| Generative agents (2304.03442) · Gorilla (2305.15334) · ToolLLM (2307.16789) | pdf | `generative-ai/01-llm-fundamentals/readings/` | tool-use research lineage |
| LangGraph/ADK course repos | code | `generative-ai/03-agentic-foundations/` | guided framework builds |
| deep-research bot | code | `generative-ai/chatbot/deep_research_bench/` | a real multi-step agent |
| wiki/adk (19pp) · wiki/langgraph · wiki/deep-agents · wiki/patterns · wiki/memory · wiki/mcp | wiki | librarian | ~50 compiled pages of design experience |
| agent-harness · agents-design · agents-guardrails · reliable-agents | note | [ai-engineering/03-harness/](../../../ai-engineering/03-harness/) | harness engineering |
| loop-engineering · deep-agents | note | [ai-engineering/04-loop/](../../../ai-engineering/04-loop/) | loop design |
| memory | note | [ai-engineering/05-graph/memory.md](../../../ai-engineering/05-graph/memory.md) | memory architectures |
| agents-google-adk | note | [generative-ai/03-agentic-foundations/](../../../generative-ai/03-agentic-foundations/) | ADK framework |

## Test yourself
[interview-guide.md](interview-guide.md) · rounds:
[system-design-round](../../rounds/system-design-round/README.md),
[project-deep-dive](../../rounds/project-deep-dive/README.md).
