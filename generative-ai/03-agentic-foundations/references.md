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
| ★ | Nicole Koenigstein, *AI Agents: The Definitive Guide* (O'Reilly, 2026; Early Release). Chapter PDFs in [sources/ai-agents-definitive-guide/](sources/ai-agents-definitive-guide/). Folded in as: ch. 1 → [01](notes/01-agent-fundamentals.md) (agents as FSM/HSM, LangGraph mapping, orchestrated autonomy, AI Scientist v2, capped loop with wrap-up) and [02](notes/02-tool-use-and-react.md) (docstring as contract); ch. 2 → [04](notes/04-multi-agent-design-patterns.md) (cheap ToT, supervisor/hierarchical/swarm table, handoff history) and [05](notes/05-framework-survey.md) (`interrupt` patterns, side-effect rule, dated `AgentExecutor`/`create_react_agent`); ch. 4 → [01](notes/01-agent-fundamentals.md) (staffing models by role, thinking budgets, cost, hybrid path, KV-cache prefix). Ch. 4's GQA/vLLM/encoder/LoRA material belongs with [01-llm-fundamentals](../01-llm-fundamentals/README.md). Notes cite it as (*AI Agents: The Definitive Guide*, ch. N). Figure `ai-agents-definitive-guide-fig1-2` | 01, 02, 04, 05 |
| | Mayo Oshin & Nuno Campos, *Learning LangChain* (O'Reilly, 2025). Chapter PDFs in [../01-llm-fundamentals/sources/learning-langchain/](../01-llm-fundamentals/sources/learning-langchain/). Folded in as: ch. 6 → [02](notes/02-tool-use-and-react.md) (always call a tool first, tool preselection by retrieval, `ToolNode` errors, the calculator caution); ch. 7 → [04](notes/04-multi-agent-design-patterns.md) (reflection graph with role swap, topologies, supervisor) and [05](notes/05-framework-survey.md) (subgraphs). Notes cite it as (*Learning LangChain*, ch. N). Figures `learning-langchain-fig6-3`, `learning-langchain-fig7-3` | 02, 04, 05 |
| | James Phoenix & Mike Taylor, *Prompt Engineering for Generative AI* (O'Reilly, 2024). Chapter PDFs in [../01-llm-fundamentals/sources/prompt-engineering-for-generative-ai/](../01-llm-fundamentals/sources/prompt-engineering-for-generative-ai/). Folded in as: ch. 6 → [01](notes/01-agent-fundamentals.md) (step caps, SQL-agent prompt-is-not-permission), [02](notes/02-tool-use-and-react.md) (ReAct parsing and stop sequence, dated Table 6-2, `args_schema`, steering return strings), [03](notes/03-memory-as-an-operating-system.md) (legacy memory classes as trimming strategies), [04](notes/04-multi-agent-design-patterns.md) (plan-and-execute/BabyAGI, ToT 4% → 74%). Notes cite it as (*Prompt Engineering for Generative AI*, ch. N) | 01, 02, 03, 04 |
| | Michael Albada, *Building Applications with AI Agents* (O'Reilly, 2025). Chapter PDFs in [sources/building-applications-with-ai-agents/](sources/building-applications-with-ai-agents/). Folded in as: ch. 1 → [01](notes/01-agent-fundamentals.md) (code / workflow / RAG / agent tiers, multimodel routing, autoscaling) and [05](notes/05-framework-survey.md) (framework rule of thumb); ch. 2 → [01](notes/01-agent-fundamentals.md) (scoping the first agent, minimal eval, price vs MMLU), [02](notes/02-tool-use-and-react.md) (MCP misdescription corrected), [04](notes/04-multi-agent-design-patterns.md) (token overhead). Notes cite it as (*Building Applications with AI Agents*, ch. N) | 01, 02, 04, 05 |
| | Chip Huyen, *AI Engineering* (O'Reilly, 2025). Ch. 6 PDF in [../02-rag-retrieval/sources/huyen-ai-engineering/](../02-rag-retrieval/sources/huyen-ai-engineering/) (its RAG half is folded into 02-rag-retrieval). Folded in as: ch. 6, agents half → [01](notes/01-agent-fundamentals.md#workflow-vs-autonomous-agent) (compound error, failure taxonomy as eval buckets). Notes cite it as `(*AI Engineering*, ch. N)` | 01 |
| | Salvatore Raieli & Gabriele Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025). Chapter PDFs in [sources/building-ai-agents-llms-rag-kgs/](sources/building-ai-agents-llms-rag-kgs/). Folded in as: ch. 4 → [04](notes/04-multi-agent-design-patterns.md) (planning taxonomy from Huang et al.; the web-scraping build is dropped); ch. 11 → [01](notes/01-agent-fundamentals.md) (human-agent communication checklist, autonomy levels, Mitchell), [02](notes/02-tool-use-and-react.md) (CoT limits, GSM-Symbolic), [04](notes/04-multi-agent-design-patterns.md) (single vs multi-agent table, Cemri detail). Notes cite it as (*Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. N) | 01, 02, 04 |
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
| | Yao et al., *Tree of Thoughts: Deliberate Problem Solving with Large Language Models* (2023): Game of 24, 4% CoT vs 74% ToT; cited via Phoenix & Taylor | [2305.10601](https://arxiv.org/abs/2305.10601) · [PDF](sources/yao-2023-tree-thoughts.pdf) | 04 |
| | Huang et al., *Understanding the planning of LLM agents: A survey* (2024); cited via Raieli & Iuculano | [2402.02716](https://arxiv.org/abs/2402.02716) | 04 |
| | Sprague et al., *To CoT or not to CoT? Chain-of-thought helps mainly on math and symbolic reasoning* (2024); cited via Raieli & Iuculano | [2409.12183](https://arxiv.org/abs/2409.12183) | 02 |
| | Mirzadeh et al., *GSM-Symbolic: Understanding the Limitations of Mathematical Reasoning in Large Language Models* (2024); cited via Raieli & Iuculano | [2410.05229](https://arxiv.org/abs/2410.05229) | 02 |

## AI Papers of the Week

| | Paper | arXiv | Notes |
|---|---|---|---|
| ★ | Zhou et al., *Filesystem-Based Memory for LLM Agents: Organization, Evolution, and Sustainability* (2026): verbatim or per-session stores match or beat agent curation; reorganizing condenses unless told to keep every fact; spend on the reader, not the writer; raw episodes for strong executors, distilled guidance for weak ones | [2607.26637](https://arxiv.org/abs/2607.26637) · [PDF](sources/zhou-2026-filesystem-based-memory-llm-agents.pdf) | [03](notes/03-memory-as-an-operating-system.md#designing-a-memory-agent) |
| | Xu et al., *Rethinking the Value of Multi-Agent Workflow: A Strong Single Agent Baseline* (2026): a homogeneous workflow run as one role-playing agent keeps accuracy at lower (simulated KV-cache) cost, with a HotpotQA drop | [2601.12307](https://arxiv.org/abs/2601.12307) · [PDF](sources/xu-2026-rethinking-value-multi-agent-workflow.pdf) | [04](notes/04-multi-agent-design-patterns.md#why-multi-agent-systems-fail) |
| | Li et al., *MemOS: An Operating System for Memory-Augmented Generation (MAG) in Large Language Models* (2025): parametric / activation / plaintext memory and the MemCube governance header; architecture only, no experiments | [2505.22101](https://arxiv.org/abs/2505.22101) · [PDF](sources/li-2025-memos.pdf) | [03](notes/03-memory-as-an-operating-system.md#memory-types-in-other-frameworks) |

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
| Albada, *Building Applications with AI Agents* | Ch. 2 misdescribes MCP as injecting context "without invoking separate tools", unlike API calls that need a round trip; MCP tools are `tools/call` round trips (corrected in [02](notes/02-tool-use-and-react.md#mcp-tools-served-over-a-protocol)). Table 2-1 contradicts its own text: it says models up to ~14B fit a 24 GB RTX 3090, yet lists Phi-3 at 14.7B / 29.4 GB needing an A100, and its "full precision" VRAM is ~2 bytes/param (fp16). Ch. 2 code listings have syntax errors. Price and HELM tables are mid-2025 snapshots | The MCP spec; current price pages and leaderboards |
| Koenigstein, *AI Agents: The Definitive Guide* | Early Release, still changing. Calls `AgentExecutor` "often preferable in production" (legacy) and uses `create_react_agent` (deprecated in LangGraph 1.0 for `langchain.agents.create_agent`). Ch. 4 passes `rope_scaling` to a ModernBERT load call as a way to extend context, which is model-dependent and not a free 4× context gain. Examples use `gpt-4o`; o1-pro pricing is dated | LangChain/LangGraph 1.x docs; model cards |
| Oshin & Campos, *Learning LangChain* | Ch. 6 calculator uses `ast.literal_eval`, which rejects arithmetic such as `"1933-1872"`, and the model's own subtraction gives Coolidge's age as 61 (it was 60). Ch. 7 Python supervisor: `AgentState` lacks `messages`, and `"FINISH"` isn't mapped to `END` (the JS version is correct). `gpt-3.5-turbo` examples | Run the code; LangGraph docs |
| Phoenix & Taylor, *Prompt Engineering for Generative AI* | 2024 LangChain APIs: `AgentExecutor`, LCEL agents, hub prompts, `Conversation*Memory` classes (deprecated in favor of LangGraph persistence). Table 6-2 says function calling lacks sequential tool execution; native tool-calling loops do sequential and parallel calls | LangChain/LangGraph docs |
| Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* | Ch. 4 code uses `initialize_agent` with `zero-shot-react-description`, `langchain.utilities` and LangServe, all legacy. Ch. 11's single- vs multi-agent table carries the caption "Potential causes of multi-agent system failure" | The cited papers (Cemri, Sprague, Mirzadeh, Gao, Bansal, Mitchell) |
| Note 06 (Kaggle notes) | Notion export; three diagrams missing; images link to an external repo | The Kaggle whitepapers |
