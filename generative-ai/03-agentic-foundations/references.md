# References — Agentic Foundations

> Every source the notes cite, mapped to notes. **★** = read first. Local PDFs live in [sources/](sources/); figures in [sources/images/](sources/images/). Rows under [From the curated list](#from-the-curated-list) are copied from `generative-ai/resources.md` (retired 2026-10-31), section 03/04.

---

## Books and courses

| | Source | Notes |
|---|---|---|
| ★ | Bojie Li, *AI Agents in Depth* (2026), [ch. 1](https://github.com/bojieli/ai-agent-book): Agent = Model + Context + Tools, the agent loop, how agents learn. Figures `li-ai-agents-in-depth-fig1-*` | 01, 02 |
| ★ | Lakshmanan & Hapke, *Generative AI Design Patterns* (O'Reilly, 2025). Chapter PDFs in [sources/](sources/) as `lakshmanan-hapke-genai-design-patterns-chNN-*.pdf`. Folded in as: ch. 7 (P21 Tool Calling, P22 Code Execution) → 02; ch. 7 (P23 Multiagent Collaboration) and ch. 6 (P18 Reflection) → 04; ch. 8 (P28 Long-Term Memory) → 03; ch. 10 (Composable Agentic Workflows) → 05. Ch. 1–5 and 9 are kept for reference and not yet folded in (ch. 2–4 belong with [02-rag-retrieval](../02-rag-retrieval/README.md)) | 02, 03, 04, 05 |
| ★ | DeepLearning.AI, [*LLMs as Operating Systems: Agent Memory*](https://www.deeplearning.ai/short-courses/llms-as-operating-systems-agent-memory/) (Charles Packer, Sarah Wooders, Letta). Snapshot upstream: [frankwwu/LLMs-as-Operating-Systems--Agent-Memory](https://github.com/frankwwu/LLMs-as-Operating-Systems--Agent-Memory). L1 editable memory → 02, 03; L2 MemGPT → 03; L3–L5 Letta agents, custom memory, agentic RAG → 03; L6 multi-agent → 04. Figures `packer-wooders-agent-memory-fig1..8`; Lab 5's document is [sources/packer-wooders-agent-memory-handbook.pdf](sources/packer-wooders-agent-memory-handbook.pdf) | 02, 03, 04 |
| ★ | DeepLearning.AI, [*AI Agentic Design Patterns with AutoGen*](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/) (Chi Wang, Qingyun Wu). Snapshot upstream: [ksm26/AI-Agentic-Design-Patterns-with-AutoGen](https://github.com/ksm26/AI-Agentic-Design-Patterns-with-AutoGen). L1–L6 → 04; L4 and L5 also → 02. Figures `wang-wu-autogen-patterns-fig1..6` | 02, 04 |
| | [adv-11/AgenticAIFrameworks](https://github.com/adv-11/AgenticAIFrameworks): proof-of-concept scripts for AutoGen, CrewAI (incl. DeepLearning.AI CrewAI notebooks), LangGraph deep research, LangMem, Google ADK, OpenAI Agents SDK, smolagents, Letta, MCP, A2A, MLflow. Folded into 02 (ReAct prompt, calculator, MCP server, Anthropic tool loop), 03 (LangMem), 05 (everything else). Figure `langchain-deep-research-fig1` | 02, 03, 05 |
| | Google × Kaggle, [*5-Day AI Agents Intensive (vibe-coding edition)*](https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google), Days 1–3 whitepapers | 06 |

## Papers

| | Paper | arXiv | Notes |
|---|---|---|---|
| ★ | Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models* (2022) | [2210.03629](https://arxiv.org/abs/2210.03629) | 01, 02 |
| ★ | Packer et al., *MemGPT: Towards LLMs as Operating Systems* (2023) | [2310.08560](https://arxiv.org/abs/2310.08560) | 03 |
| | Schick et al., *Toolformer: Language Models Can Teach Themselves to Use Tools* (2023) | [2302.04761](https://arxiv.org/abs/2302.04761) | 02 |
| | Beurer-Kellner et al., *Design Patterns for Securing LLM Agents against Prompt Injections* (2025) | [2506.08837](https://arxiv.org/abs/2506.08837) | 02 |
| ★ | Cemri et al., *Why Do Multi-Agent LLM Systems Fail?* (2025): 14 failure modes, 3 categories | [2503.13657](https://arxiv.org/abs/2503.13657) | 04 |
| | Chhikara et al., *Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory* (2025) | [2504.19413](https://arxiv.org/abs/2504.19413) | 03 |

## First-party docs

| | Source | Notes |
|---|---|---|
| | [Letta docs](https://docs.letta.com/) | 03, 04 |
| | [AutoGen](https://microsoft.github.io/autogen/) (0.2 docs are archived; 0.4 is the current line) | 02, 04, 05 |
| | [CrewAI docs](https://docs.crewai.com/) | 05 |
| | [LangMem docs](https://langchain-ai.github.io/langmem/) | 03 |
| | [smolagents docs](https://huggingface.co/docs/smolagents/) | 05 |
| | [Model Context Protocol](https://modelcontextprotocol.io/) | 02, 05 |
| | [A2A protocol](https://a2a-protocol.org/) | 05 |
| | Andrew Ng, [*Agentic design patterns*](https://www.deeplearning.ai/the-batch/how-agents-can-improve-llm-performance/) (The Batch, 2024) | 04 |

## From the curated list

Copied from `generative-ai/resources.md` (retired 2026-10-31) § 03/04 — Agents and frameworks.

**Guides**

| | Source | Notes |
|---|---|---|
| ★ | [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (Anthropic) | 01, 04 |
| | [A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) (OpenAI) | 04 |
| | [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) | 02, 05 |
| | [ReAct](https://arxiv.org/abs/2210.03629): the reason + act paper | 02 |

**Frameworks**

| | Source | Notes |
|---|---|---|
| | [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) · [Google ADK](https://google.github.io/adk-docs/): both covered in [04-agentic-frameworks](../04-agentic-frameworks/README.md) | 05, 06 |
| | [Pydantic AI](https://ai.pydantic.dev/) · [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) · [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/) (AutoGen's successor) | 05 |

**Durable and long-running agents** (deeper in [ai-engineering/03-harness](../../ai-engineering/03-harness-engineering/README.md))

| | Source | Notes |
|---|---|---|
| | [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 03 |
| | OpenAI Agents SDK: [running agents](https://openai.github.io/openai-agents-python/running_agents/) · [human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/) | 05 |
| | [Gemini + Temporal durable agent](https://ai.google.dev/gemini-api/docs/temporal-example) | 05 |
| | [How We Built Our Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) (Anthropic) | 04, 05 |

---

## Source quality

| Source | Problem | Corroborate via |
|---|---|---|
| AgenticAIFrameworks | Personal POC scripts, early-to-mid 2025 APIs, little error handling; several examples unfinished (deep research implements only the scope phase) | The framework's own docs |
| AutoGen course | pyautogen 0.2 API; AutoGen has since been rewritten (0.4) and superseded by Microsoft Agent Framework | Current AutoGen / Agent Framework docs |
| Letta course | Pinned to `letta==0.6.50`; the client API has changed in later releases | Letta docs |
| Lakshmanan & Hapke | Point-in-time numbers ("3–10 tools as of June 2025", MCP limits as of May 2025) | Current provider docs and the MCP spec |
| Note 06 (Kaggle notes) | Notion export; three diagrams missing; images link to an external repo | The Kaggle whitepapers |
