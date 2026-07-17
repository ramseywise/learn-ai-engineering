# Pillar 4 — Agents (orchestration, tools, memory, harness)

Systems where the LLM decides what to do next: call tools, keep state, plan multi-step
work, recover from failures. This is the deepest pillar in the repo's sources — it's what
the librarian wiki and most of the cleaned notes are about — and the center of gravity of
2026 AI-engineering work.

## Learning path

1. **Concepts before frameworks** — *Building Applications with AI Agents* chs 1–5
   (`readings/ai_engineering/ai_agent_applications/`): agents, tool use, orchestration.
   Pair with the ReAct paper (pillar 2) — the loop everything else elaborates.
2. **One framework, properly** — LangGraph *or* Google ADK via
   `generative-ai/coursera-references/` course repos; librarian's `wiki/langgraph/` and
   `wiki/adk/` pages are the compiled experience layer on top.
3. **Tools & MCP** — *Model Context Protocol* chapters (`readings/ai_engineering/mcp/`);
   tool-design-as-UX (ACI/poka-yoke) from the wiki patterns pages.
4. **Memory & state** — notes ([memory.md](../../notes/memory.md),
   [deep-agents.md](../../notes/deep-agents.md)) + `wiki/memory/` + the Memoria/
   memory-augmented-RAG flow; chatbot-memory pilot paper (Yan et al. 2025, `readings/`).
5. **Harness engineering** — the notes cluster unique to this repo:
   [agent-harness](../../notes/agent-harness.md), [loop-engineering](../../notes/loop-engineering.md),
   [reliable-agents](../../notes/reliable-agents.md) — acceptance baselines, execution
   boundaries, feedback signals, rollback.
6. **Multi-agent, skeptically** — *From One Agent to Many* (agent applications ch 8),
   `readings/ai_engineering/multiagent context/`, notes
   [agents-design.md](../../notes/agents-design.md); protocol/task-graph/isolation triad.

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| *Building Applications with AI Agents* (chs 1–13) | pdf | `readings/ai_engineering/ai_agent_applications/` | full agent lifecycle incl. validation, monitoring, protection |
| *Generative AI Design Patterns* (chs 1–10) | pdf | `readings/ai_engineering/ai design/` | pattern language: knowledge, actions, safeguards, composable workflows |
| *AI Engineering* (Huyen, ch 6 RAG & Agents) | pdf | `readings/ai_engineering/ai engineer/` | agents in the app-architecture frame |
| MCP · LangChain · multiagent-context books | pdf | `readings/ai_engineering/{mcp,langchain,multiagent context}/` | protocol + framework depth |
| Generative agents (2304.03442) · Gorilla (2305.15334) · ToolLLM (2307.16789) | pdf | `readings/2-llm-rlhf/` | tool-use research lineage |
| LangGraph/ADK course repos | code | `generative-ai/coursera-references/` | guided framework builds |
| deep-research bot | code | `generative-ai/chatbot/deep_research_bench/` | a real multi-step agent |
| wiki/adk (19pp) · wiki/langgraph · wiki/deep-agents · wiki/patterns · wiki/memory · wiki/mcp | wiki | librarian | ~50 compiled pages of design experience |
| agent-harness · loop-engineering · reliable-agents · agents-design · agents-google-adk · deep-agents · memory | note | [../../notes/](../../notes/) | harness engineering + framework notes |

## Test yourself
[interview-guide.md](interview-guide.md) · rounds:
[system-design-round](../../rounds/system-design-round.md),
[project-deep-dive](../../rounds/project-deep-dive.md).
