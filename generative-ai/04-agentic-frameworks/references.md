---
origin: curated
sources:
  - ../resources.md (section "03/04 — Agents and frameworks", copied 2026-10-31)
  - https://github.com/ksm26/AI-Agents-in-LangGraph
  - https://github.com/YunghuiHsu/Long-Term-Agentic-Memory-With-LangGraph
confidence: high
cleaned: 2026-11-01
---
# References — Agentic Frameworks

> Every source the notes cite, mapped to notes. **★** = read first. Theory sources for graphs and memory live in the ai-engineering pillars' references and are not repeated here.

---

## Courses and videos

| Course | Platform, cost | Where | Use it for |
|---|---|---|---|
| *AI Agents in LangGraph* (Harrison Chase, Rotem Weiss) | DeepLearning.AI, free with an account | [course](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) | The original of notes 01 and 02, with L5 and L6 runnable on the platform |
| *Long-Term Agentic Memory with LangGraph* (Harrison Chase) | DeepLearning.AI, free with an account | [course](https://www.deeplearning.ai/short-courses/long-term-agentic-memory-with-langgraph/) | The original of note 03 |
| *Introduction to LangGraph* | LangChain Academy, free | [course](https://academy.langchain.com/courses/intro-to-langgraph) | A longer, video-led path through notes 01 and 02 |
| *Introduction to LangSmith* | LangChain Academy, free | [course](https://academy.langchain.com/courses/intro-to-langsmith) | The hosted UI that note 05 can only describe |
| *Build Your First Agent with Agent Development Kit (ADK)* (Google Cloud) | DataCamp, free account per its listing, about 90 minutes | [course](https://www.datacamp.com/courses/google-build-your-first-agent-with-agent-development-kit-adk) | ADK on a live model after note 04. Check the current price before enrolling |

### Course snapshots condensed into the notes

| | Source | Upstream snapshot | Licence | Notes |
|---|---|---|---|---|
| ★ | DeepLearning.AI, [*AI Agents in LangGraph*](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) (Harrison Chase, Rotem Weiss, 2024). L1 ReAct from scratch, L2 LangGraph components, L3 agentic search, L4 persistence and streaming, L5 human in the loop, L6 essay writer. Figures in [sources/images/](sources/images/) as `ksm26-ai-agents-in-langgraph-fig1..6` | [ksm26/AI-Agents-in-LangGraph](https://github.com/ksm26/AI-Agents-in-LangGraph): L1–L4 notebooks, README, 6 figures; no L5–L6 notebooks | No licence file; course material © DeepLearning.AI, figures reused with attribution | [01](notes/01-react-from-scratch-to-langgraph.md), [02](notes/02-agentic-search-persistence-streaming.md) |
| ★ | DeepLearning.AI × LangChain, [*Long-Term Agentic Memory with LangGraph*](https://www.deeplearning.ai/short-courses/long-term-agentic-memory-with-langgraph/) (Harrison Chase, 2025). L2 baseline email assistant, L3 semantic, L4 episodic, L5 procedural memory | [YunghuiHsu/Long-Term-Agentic-Memory-With-LangGraph](https://github.com/YunghuiHsu/Long-Term-Agentic-Memory-With-LangGraph): Lesson 2–5 notebooks and `prompts.py` | No licence file; course material © DeepLearning.AI | [03](notes/03-long-term-memory-with-langgraph.md) |

## Books

| | Source | Notes |
|---|---|---|
| ★ | James Phoenix & Mike Taylor, *Prompt Engineering for Generative AI* (O'Reilly, 2024). Chapter PDFs in [../01-llm-fundamentals/sources/prompt-engineering-for-generative-ai/](../01-llm-fundamentals/sources/prompt-engineering-for-generative-ai/). Folded in as: ch. 4 → [07](notes/07-lcel-composition-in-practice.md) (passthrough and `itemgetter` data flow, sequential scene generation, `max_concurrency`, `tool_choice` and hallucinated parameters, query planning, map-reduce and Table 4-1, few-shot limits, `load_prompt`) and [05](notes/05-langsmith.md#testing-whether-a-cheaper-model-is-good-enough) (GPT-4 labels as ground truth, Mixtral at 77.5% exact match, the pairwise judge). The chapter's basics (templates, parsers, LCEL) are in [01-llm-fundamentals note 11](../01-llm-fundamentals/notes/11-langchain-basics.md). Notes cite it as (*Prompt Engineering for Generative AI*, ch. N). Figure `prompt-engineering-for-generative-ai-fig4-7` | 05, 07 |
| ★ | Ali Arsanjani & Juan Pablo Bustos, *Agentic Architectural Patterns for Building Multi-Agent Systems* (Packt, 2026; ISBN 978-1-80602-957-0). Home is the agents pillar ([03-agentic-foundations](../03-agentic-foundations/references.md)); chapter PDFs in [../03-agentic-foundations/sources/agentic-architectural-patterns/](../03-agentic-foundations/sources/agentic-architectural-patterns/). Folded in as: ch. 13 → [04](notes/04-google-adk.md#a-thinking-budget-is-not-a-loop-guard) (the ADK loan agent: `BuiltInPlanner` with `ThinkingConfig(thinking_budget=1024)` is the only enforced limit, N=3 and the success criteria are prompt text, the compliance stub always passes; API names checked against `google-adk` 2.14.0; `start_agent_run` is called but its definition is not printed); ch. 14 → [04](notes/04-google-adk.md#agents-as-tools-agenttool) (supervisor over four `AgentTool` specialists, Fig. 14.2; nothing measured) and [04](notes/04-google-adk.md#a-thinking-budget-is-not-a-loop-guard) (the `ratelimit` and `tenacity` wrapper is defined but `runner.run` is called directly, and a decorator on a generator-returning call would not retry anyway, shown with a 30-line check); ch. 15, Tables 15.1–15.3 → [06](notes/06-framework-selection.md#what-a-books-three-framework-tables-add) (feature grid agrees with the frameworks table; Table 15.1 dates checked against PyPI first uploads, the ADK 2024 prototype date dropped; maturity-to-framework mapping with its Level 4/5/6 inconsistency; the level 4 CrewAI and LangGraph feature list is unsourced). The CrewAI-versus-LangGraph loan build is confounded and is covered in [03-agentic-foundations note 05](../03-agentic-foundations/notes/05-framework-survey.md#the-same-workflow-in-crewai-and-langgraph), not repeated here. All scores, thresholds and applicants in ch. 13–15 are invented mock data, and prose and code disagree in several places (maturity levels, "default settings" against a set thinking budget). Figure `agentic-architectural-patterns-fig14-2`. Notes cite it as (*Agentic Architectural Patterns*, ch. N) | 04, 06 |
| | Mayo Oshin & Nuno Campos, *Learning LangChain* (O'Reilly, 2025). Chapter PDFs in [../01-llm-fundamentals/sources/learning-langchain/](../01-llm-fundamentals/sources/learning-langchain/). Folded in as: ch. 1 → [07](notes/07-lcel-composition-in-practice.md#book-apis-and-their-current-form) (import and model-class bugs only; the rest of ch. 1 is covered in [01-llm-fundamentals note 11](../01-llm-fundamentals/notes/11-langchain-basics.md)); ch. 9 → [02](notes/02-agentic-search-persistence-streaming.md#double-texting) (`multitask_strategy`; the concepts are in harness 07). Notes cite it as (*Learning LangChain*, ch. N) | 02, 07 |

## Core papers

| | Paper | Read for | Notes |
|---|---|---|---|
| ★ | Wang et al., [*An Empirical Study of Agent Developer Practices in AI Agent Frameworks*](https://arxiv.org/abs/2512.01939) (preprint, Dec 2025). [PDF](sources/wang-2025-empirical-study-agent-developer-practices.pdf) | What fails in practice: logic control 34.83% in Fig. 6 (termination 21.63%), tools 25.61%, versions 23.53%, performance 16.03% of 8,710 GPT-4-classified discussions across 1,575 projects; shares of complaints, not failure rates | [01](notes/01-react-from-scratch-to-langgraph.md), [05](notes/05-langsmith.md), [06](notes/06-framework-selection.md) |
| ★ | Liu et al., [*A Large-Scale Study on the Development and Issues of Multi-Agent AI Systems*](https://arxiv.org/abs/2601.07136) (preprint, Jan 2026). [PDF](sources/liu-2026-large-scale-study-development-issues.pdf) | How eight frameworks evolve: 40.83% perfective commits by a DistilBERT classifier, PR-linked issues only, bugs outnumber agent issues 22% to 10% | [05](notes/05-langsmith.md), [06](notes/06-framework-selection.md) |
| | Furgale et al., [*NVIDIA-labs OO Agents*](https://arxiv.org/abs/2607.20709) (preprint, 2026). [PDF](sources/furgale-2026-nvidia-labs-oo-agents.pdf) | Validated typed termination, and a July-2026 pinned comparison of 14 frameworks and harnesses on a six-capability rubric; the authors' own NVIDIA system is the only system strong on all six, and the 77% early-stop figure for OpenCode comes without trial counts | [04](notes/04-google-adk.md), [06](notes/06-framework-selection.md) |
| | Zhou et al., [*Agents: An Open-source Framework for Autonomous Language Agents*](https://arxiv.org/abs/2309.07870) (preprint, 2023). [PDF](sources/zhou-2023-agents.pdf) | Symbolic plans as state graphs, and long-term memory | [02](notes/02-agentic-search-persistence-streaming.md), [03](notes/03-long-term-memory-with-langgraph.md) |
| | Dibia et al., [*AutoGen Studio*](https://aclanthology.org/2024.emnlp-demo.8/) (EMNLP 2024 System Demonstrations). [PDF](sources/dibia-2024-autogen-studio.pdf) | Declarative workflows and a run profiler | [05](notes/05-langsmith.md), [06](notes/06-framework-selection.md) |

## AI Papers of the Week

Papers routed here by the weekly [DAIR](https://github.com/dair-ai/AI-Papers-of-the-Week) sync: Zhou et al. (week of 2023-09-11) and Dibia et al. (week of 2024-08-26). Both are in the table above.

| | Paper | Read for | Notes |
|---|---|---|---|
| | Dibia et al., [*AutoGen Studio*](https://aclanthology.org/2024.emnlp-demo.8/) (EMNLP 2024 System Demonstrations). [PDF](sources/dibia-2024-autogen-studio.pdf) | Over 200K installs in 5 months and over 135 issues are its only evidence; no user study or benchmark; "not production ready" | [06](notes/06-framework-selection.md) |
| | Zhou et al., [*Agents: An Open-source Framework for Autonomous Language Agents*](https://arxiv.org/abs/2309.07870) (⚑ preprint, 2023). [PDF](sources/zhou-2023-agents.pdf) | Symbolic state-graph control flow claimed more stable, never measured; self-scored feature table | [06](notes/06-framework-selection.md#the-dimensions) |

## Framework and library docs

| | Source | Notes |
|---|---|---|
| ★ | [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview): [persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [memory](https://docs.langchain.com/oss/python/langgraph/memory) | 01, 02, 03, 06 |
| | [langmem](https://langchain-ai.github.io/langmem/): memory tools and prompt optimizers | 03 |
| | [Tavily docs](https://docs.tavily.com/) | 02 |
| ★ | [Google ADK docs](https://adk.dev/) ([evaluate](https://adk.dev/evaluate/)) | 04, 06 |
| | [LangSmith docs](https://docs.langchain.com/langsmith/observability) ([evaluation](https://docs.langchain.com/langsmith/evaluation)) | 05, 06 |
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
| | [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) · [Google ADK](https://adk.dev/): both covered in this pillar | 01–06 |
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
| Phoenix & Taylor, *Prompt Engineering for Generative AI* ch. 4 | `pydantic.v1` imports and legacy helpers (`create_extraction_chain_pydantic`, `load_summarize_chain`, `langchain.evaluation`); suggests pickle for saving prompts (unsafe to load); the batch result is named `synchronous_llm_result`; the pairwise-evaluator walkthrough is introduced as "the simple exact string matching evaluator"; the 77.5% counts parse failures as wrong answers and gives no sample size. Modern forms in 07's version table | Current LangChain docs; 07 |
| Oshin & Campos, *Learning LangChain* ch. 1 | `from langchain_openai.llms import ChatOpenAI` fails (wrong module); `OpenAI(model="gpt-3.5-turbo")` puts a chat model on the completions class | `from langchain_openai import ChatOpenAI` or `init_chat_model` |
| Wang et al. | Percentages disagree inside the paper: termination 25.6% against 21.63%, tool failures 14% against 25.61%, LangGraph 9.6K stars against 20.6K. Note 01 also corrects its description of LangGraph as DAG-based. Classification is LLM-assisted with manual spot checks. Trust the ordering of problems over any one figure |
| Liu et al. | Eight frameworks, not including LangGraph or ADK. Open-source repositories only. Mean resolution times are skewed by a long tail |
| Furgale et al. | The authors built a competing system and score it highest. Use the facts, not the ranking |
| Measurements in note 06 | One laptop and a stub model at `langgraph` 1.2.19 and `google-adk` 2.13.0. Rerun `compare.py` for your setup, and recheck default limits after an upgrade |
