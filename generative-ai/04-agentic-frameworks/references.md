---
origin: curated
sources:
  - ../resources.md (section "03/04 — Agents and frameworks", copied 2026-10-31)
  - https://github.com/ksm26/AI-Agents-in-LangGraph
  - https://github.com/YunghuiHsu/Long-Term-Agentic-Memory-With-LangGraph
confidence: high
cleaned: 2026-10-31
---
# References — Agentic Frameworks

> Every source the notes cite, mapped to notes. **★** = read first. Theory sources for graphs and memory live in the ai-engineering pillars' references and are not repeated here.

---

## Courses (condensed into the notes)

| | Source | Upstream snapshot | Licence | Notes |
|---|---|---|---|---|
| ★ | DeepLearning.AI, [*AI Agents in LangGraph*](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) (Harrison Chase, Rotem Weiss, 2024). L1 ReAct from scratch, L2 LangGraph components, L3 agentic search, L4 persistence and streaming, L5 human in the loop, L6 essay writer. Figures in [sources/images/](sources/images/) as `ksm26-ai-agents-in-langgraph-fig1..6` | [ksm26/AI-Agents-in-LangGraph](https://github.com/ksm26/AI-Agents-in-LangGraph): L1–L4 notebooks, README, 6 figures; no L5–L6 notebooks | No licence file; course material © DeepLearning.AI, figures reused with attribution | [01](notes/01-react-from-scratch-to-langgraph.md), [02](notes/02-agentic-search-persistence-streaming.md) |
| ★ | DeepLearning.AI × LangChain, [*Long-Term Agentic Memory with LangGraph*](https://www.deeplearning.ai/short-courses/long-term-agentic-memory-with-langgraph/) (Harrison Chase, 2025). L2 baseline email assistant, L3 semantic, L4 episodic, L5 procedural memory | [YunghuiHsu/Long-Term-Agentic-Memory-With-LangGraph](https://github.com/YunghuiHsu/Long-Term-Agentic-Memory-With-LangGraph): Lesson 2–5 notebooks and `prompts.py` | No licence file; course material © DeepLearning.AI | [03](notes/03-long-term-memory-with-langgraph.md) |

## Framework and library docs

| | Source | Notes |
|---|---|---|
| ★ | [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview): [persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [memory](https://docs.langchain.com/oss/python/langgraph/memory) | 01, 02, 03, 06 |
| | [langmem](https://langchain-ai.github.io/langmem/): memory tools and prompt optimizers | 03 |
| | [Tavily docs](https://docs.tavily.com/) | 02 |
| ★ | [Google ADK docs](https://google.github.io/adk-docs/) ([llms-full.txt](https://google.github.io/adk-docs/llms-full.txt), [evaluate](https://google.github.io/adk-docs/evaluate/)) | 04, 06 |
| | [LangSmith docs](https://docs.smith.langchain.com/) ([evaluation](https://docs.smith.langchain.com/evaluation)) | 05, 06 |
| | Simon Willison, [*A simple Python implementation of the ReAct pattern*](https://til.simonwillison.net/llms/python-react-pattern): the basis of L1 | 01 |

## From the subject reading list

Copied from `generative-ai/resources.md` (retired 2026-10-31), section *03/04 — Agents and frameworks*, on 2026-10-31.

**Guides**

| | Source | Notes |
|---|---|---|
| ★ | [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (Anthropic) | 06 |
| | [A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) (OpenAI) | 06 |
| | [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) | 06 |
| | [ReAct](https://arxiv.org/abs/2210.03629): the reason + act paper | 01 |

**Frameworks**

| | Source | Notes |
|---|---|---|
| | [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) · [Google ADK](https://google.github.io/adk-docs/): both covered in this pillar | 01–06 |
| | [Pydantic AI](https://ai.pydantic.dev/) · [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) · [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/) (AutoGen's successor) | 06 |

**Durable and long-running agents.** These go deeper in [ai-engineering/03-harness](../../ai-engineering/03-harness-engineering/README.md).

| | Source | Notes |
|---|---|---|
| | [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 02, 06 |
| | OpenAI Agents SDK: [running agents](https://openai.github.io/openai-agents-python/running_agents/) · [human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/) | 02, 06 |
| | [Gemini + Temporal durable agent](https://ai.google.dev/gemini-api/docs/temporal-example) | 06 |
| | [How We Built Our Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) (Anthropic) | 06 |

## Source quality

| Source | Flag |
|---|---|
| Both course snapshots | Pinned to their release-era APIs; notes 01–03 list the renames. Check current docs before copying imports |
| Framework comparison table in note 06 | Synthesised from vendor docs; only the LangGraph and ADK columns are worked through in code here. Confidence medium |
| Notes 04–05 | Own reference specs written for a support-agent eval platform; paths to that project's files are illustrative |
