---
origin: curated
sources:
  - notes/ and sources/ of this pillar
confidence: high
cleaned: 2026-11-01
---
# References — Agentic Applications

> Every source the notes cite, mapped to notes. **★** = start here, or a reading that changed a claim in a note. **⚑** = preprint only, with no peer-reviewed version located. Local PDFs live in [sources/](sources/). Licences of the kept and removed projects are in [Source quality](#source-quality).

---

## Books

| | Source | Notes |
|---|---|---|
| ★ | Weights & Biases, *Building Agents from Scratch* (Fully Connected London 2025 workshop), [morganmcg1/deep-research-bot](https://github.com/morganmcg1/deep-research-bot) (Apache-2.0). Kept in [practice/deep-research-bot/](practice/deep-research-bot/): notebooks 01–03, package, RACE eval | 02 |
| ★ | Bojie Li, *AI Agents in Depth* (2026), [ch. 6 real-time multimodal agents](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter6.md) (Apache-2.0): voice paradigms, fast/slow thinking, computer use, robotics. Figures as `li-ai-agents-in-depth-fig6-*` | 03 |
| | Li, *AI Agents in Depth*, other application labs upstream: web search and search + codegen agents ([ch. 1](https://github.com/bojieli/ai-agent-book/tree/main/chapter1)); paper → slides → video, log diagnosis, text-to-SQL ([ch. 5](https://github.com/bojieli/ai-agent-book/tree/main/chapter5)) | — |
| | Denis Rothman, *Context Engineering for Multi-Agent Systems* (Packt, 2025). Chapter PDF in [sources/context-engineering-multi-agent-systems/](sources/context-engineering-multi-agent-systems/). Folded in as: ch. 9 → [06](notes/06-application-patterns.md#worked-example-one-engine-a-new-domain) (re-tasking the Context Engine to marketing by changing only the corpus and goals, the 69.63 s run, and the ungrounded ROI pitch). The engine itself (ch. 4, 5, 8) is in [ai-engineering/03-harness-engineering](../../ai-engineering/03-harness-engineering/references.md). Notes cite it as (*Context Engineering for Multi-Agent Systems*, ch. N). Figure `context-engineering-multi-agent-systems-fig9-1` | 06 |
| | Mayo Oshin & Nuno Campos, *Learning LangChain* (O'Reilly, 2025). Chapter PDFs in [../01-llm-fundamentals/sources/learning-langchain/](../01-llm-fundamentals/sources/learning-langchain/). Folded in as: ch. 11 → [06](notes/06-application-patterns.md) (chatbot, collaborative editing and ambient patterns, with the building blocks each needs). Notes cite it as (*Learning LangChain*, ch. N) | 06 |

## Core papers

Grouped by note: research agents, then GUI and voice, coding, data analysis, and dialogue and human-AI interaction.

| | Paper | Link | Notes |
|---|---|---|---|
| ★ | Du et al., *DeepResearch Bench* (2025): 100 tasks, RACE and FACT. Code in [practice/deep_research_bench/](practice/deep_research_bench/) | [2506.11763](https://arxiv.org/abs/2506.11763) | [02](notes/02-deep-research-bot.md) |
| ⚑ | Huang et al., *Deep Research Agents* (2025): a survey, and the map note 02 uses: workflows, planning, retrieval, tuning | [2506.18096](https://arxiv.org/abs/2506.18096) · [PDF](sources/huang-2025-deep-research-agents.pdf) | [02](notes/02-deep-research-bot.md) |
| ⚑ | Han et al., *Deep Researcher with Test-Time Diffusion* (TTD-DR, 2025): draft first, revise with retrieval; 69.1% and 74.5% win rates against OpenAI Deep Research on two long-form tasks, the authors' own judging | [2507.16075](https://arxiv.org/abs/2507.16075) · [PDF](sources/han-2025-deep-researcher-test-time-diffusion.pdf) | [02](notes/02-deep-research-bot.md) |
| ⚑ | Alzubi et al., *Open Deep Search* (2025): with DeepSeek-R1, 88.3% on SimpleQA and 75.3% on FRAMES, up from 82.4% and 30.1% | [2503.20201](https://arxiv.org/abs/2503.20201) · [PDF](sources/alzubi-2025-open-deep-search.pdf) | [02](notes/02-deep-research-bot.md) |
|  | Li et al., *WebThinker* (NeurIPS 2025): interleaves think, search and draft; online DPO for tool use | [2504.21776](https://arxiv.org/abs/2504.21776) · [PDF](sources/li-2025-webthinker.pdf) | [02](notes/02-deep-research-bot.md) |
| ⚑ | Belcak et al., *Universal Deep Research* (2025): users write the strategy; the authors report that writing strategies was tedious | [2509.00244](https://arxiv.org/abs/2509.00244) · [PDF](sources/belcak-2025-universal-deep-research.pdf) | [02](notes/02-deep-research-bot.md) |
| ⚑ | Nguyen et al., *SFR-DeepResearch* (2025): one autonomous agent trained by RL on synthetic data; 28.7% on Humanity's Last Exam at best | [2509.06283](https://arxiv.org/abs/2509.06283) · [PDF](sources/nguyen-2025-sfr-deepresearch.pdf) | [02](notes/02-deep-research-bot.md) |
| ⚑ | Lu et al., *DeepDive* (2025): knowledge-graph questions and multi-turn RL; 15.3% on BrowseComp | [2509.10446](https://arxiv.org/abs/2509.10446) · [PDF](sources/lu-2025-deepdive.pdf) | [02](notes/02-deep-research-bot.md) |
| ⚑ | Hu et al., *Step-DeepResearch* (2025): atomic capabilities on a 32B model; ADR-Bench with expert judges | [2512.20491](https://arxiv.org/abs/2512.20491) · [PDF](sources/hu-2025-step-deepresearch-technical-report.pdf) | [02](notes/02-deep-research-bot.md) |
| ⚑ | Prabhakar et al., *Enterprise Deep Research* (2025): a planner over search agents, NL2SQL and visualization, with human steering | [2510.17797](https://arxiv.org/abs/2510.17797) · [PDF](sources/prabhakar-2025-enterprise-deep-research.pdf) | [02](notes/02-deep-research-bot.md), [05](notes/05-data-analysis-agent.md) |
| ⚑ | Lu et al., *The AI Scientist* (2024): ideation to simulated review, under $15 a paper | [2408.06292](https://arxiv.org/abs/2408.06292) · [PDF](sources/lu-2024-ai-scientist.pdf) | [02](notes/02-deep-research-bot.md) |
| ⚑ | Schmidgall et al., *Agent Laboratory* (2025): the same span with human oversight, $2.33 for its full process | [2501.04227](https://arxiv.org/abs/2501.04227) · [PDF](sources/schmidgall-2025-agent-laboratory.pdf) | [02](notes/02-deep-research-bot.md) |
| ★ | Jansen et al., *CodeScientist* (Findings of ACL 2025): 19 candidate discoveries, 6 judged at least minimally sound and incrementally novel, checked by code review and replication. The most sobering figure in note 02 | [2503.22708](https://arxiv.org/abs/2503.22708) · [PDF](sources/jansen-2025-codescientist.pdf) | [02](notes/02-deep-research-bot.md) |
| ⚑ | Lange et al., *Agentic Scientist* (2026-10): headless coding agents, sandboxed experiments, rubric verification at each stage | [2610.18933](https://arxiv.org/abs/2610.18933) · [PDF](sources/lange-2026-agentic-scientist.pdf) | [02](notes/02-deep-research-bot.md) |
| ⚑ | Zheng et al., *AI Co-Mathematician* (2026): orchestration from software engineering for iterative mathematics | [2605.06651](https://arxiv.org/abs/2605.06651) · [PDF](sources/zheng-2026-ai-co-mathematician.pdf) | [02](notes/02-deep-research-bot.md) |
|  | Zhang et al., *Large Language Model-Brained GUI Agents* (TMLR 2025): survey of frameworks, data, action models and benchmarks | [2411.18279](https://arxiv.org/abs/2411.18279) · [PDF](sources/zhang-2024-large-language-model-brained-gui.pdf) | [03](notes/03-real-time-multimodal-agents.md) |
|  | Wang et al., *Enabling Conversational Interaction with Mobile UI* (CHI 2023): one prompted LLM on four mobile UI tasks | [2209.08655](https://arxiv.org/abs/2209.08655) · [PDF](sources/wang-2022-enabling-conversational-interaction-mobile-ui.pdf) | [03](notes/03-real-time-multimodal-agents.md) |
| ⚑ | Zhang et al., *AppAgent* (2023): taps and swipes, a knowledge base from exploration or demonstration; 50 tasks in 10 apps | [2312.13771](https://arxiv.org/abs/2312.13771) · [PDF](sources/zhang-2023-appagent.pdf) | [03](notes/03-real-time-multimodal-agents.md) |
| ★ | Zheng et al., *SeeAct* (2024): GPT-4V at 51.1% on live sites with oracle grounding, far lower with real grounding. Reframed grounding as the bottleneck | [2401.01614](https://arxiv.org/abs/2401.01614) · [PDF](sources/zheng-2024-gpt-4v-ision-generalist-web.pdf) | [03](notes/03-real-time-multimodal-agents.md) |
| ⚑ | Hu et al., *The Dawn of GUI Agent* (2024): a case study of Claude 3.5 Computer Use | [2411.10323](https://arxiv.org/abs/2411.10323) · [PDF](sources/hu-2024-dawn-gui-agent.pdf) | [03](notes/03-real-time-multimodal-agents.md) |
| ⚑ | Luo et al., *GUI-R1* (2025): reinforcement fine-tuning with a unified action space and GRPO | [2504.10458](https://arxiv.org/abs/2504.10458) · [PDF](sources/luo-2025-gui-r1.pdf) | [03](notes/03-real-time-multimodal-agents.md) |
|  | Wang et al., *OpenCUA* (NeurIPS 2025): the AgentNet dataset over 3 operating systems and 200+ apps | [2508.09123](https://arxiv.org/abs/2508.09123) · [PDF](sources/wang-2025-opencua.pdf) | [03](notes/03-real-time-multimodal-agents.md) |
| ★⚑ | Gonzalez-Pumariega et al., *The Unreasonable Effectiveness of Scaling Agents for Computer Use* (Agent S3, 2025): 72.6% on OSWorld at 100 steps against a 72.36% human figure, by selecting among rollouts. Spending tries for accuracy is the reverse of the voice story | [2510.02250](https://arxiv.org/abs/2510.02250) · [PDF](sources/gonzalez-pumariega-2025-scaling-agents-computer-use.pdf) | [03](notes/03-real-time-multimodal-agents.md) |
| ⚑ | Fang et al., *LLaMA-Omni* (2024): an open small end-to-end speech model; InstructS2S-200K | [2409.06666](https://arxiv.org/abs/2409.06666) · [PDF](sources/fang-2024-llama-omni.pdf) | [03](notes/03-real-time-multimodal-agents.md) |
| ★ | Yang et al., *SWE-agent* (NeurIPS 2024): agent-computer interface design, and the source of the note's reproduce, localize, patch, verify arc | [2405.15793](https://arxiv.org/abs/2405.15793) · [PDF](../../ai-engineering/03-harness-engineering/sources/yang-2024-swe-agent.pdf) | [04](notes/04-coding-agent.md) |
|  | Jimenez et al., *SWE-bench* (ICLR 2024). [Site](https://www.swebench.com/); [Terminal-Bench](https://www.tbench.ai/) is the shell-task counterpart | [2310.06770](https://arxiv.org/abs/2310.06770) | [04](notes/04-coding-agent.md) |
| ⚑ | Bui, *Building Effective AI Coding Agents* (2026-03): OpenDev's defaults for reads, truncation and context | [2603.05344](https://arxiv.org/abs/2603.05344) · [PDF](../../ai-engineering/03-harness-engineering/sources/bui-2026-building-effective-ai-coding-agents.pdf) | [04](notes/04-coding-agent.md) |
| ★⚑ | Shen & Tamkin, *How AI Impacts Skill Formation* (2026-01): randomized trial of 52 Python users learning a new library, with a quiz afterwards. Who supervises the agent matters | [2601.20245](https://arxiv.org/abs/2601.20245) · [PDF](sources/shen-2026-how-ai-impacts-skill-formation.pdf) | [04](notes/04-coding-agent.md) |
|  | Liu et al., *A Survey of Text-to-SQL in the Era of LLMs* (2024) | [2408.05109](https://arxiv.org/abs/2408.05109) · [PDF](../../ai-engineering/07-inference-engineering/sources/liu-2024-survey-text-sql-era-llms.pdf) | [05](notes/05-data-analysis-agent.md) |
| ★⚑ | Biswal et al., *Text2SQL is Not Enough* (2024): table-augmented generation; many real questions need reasoning beyond the query | [2408.14717](https://arxiv.org/abs/2408.14717) · [PDF](../02-rag-retrieval/sources/biswal-2024-text2sql-not-enough.pdf) | [05](notes/05-data-analysis-agent.md) |
| ⚑ | Xie et al., *OpenAgents* (2023): a Data Agent that generates Python and SQL, profiles data and renders charts | [2310.10634](https://arxiv.org/abs/2310.10634) · [PDF](sources/xie-2023-openagents.pdf) | [05](notes/05-data-analysis-agent.md) |
|  | Liu & Lane, *Attention-Based RNN Models for Joint Intent Detection and Slot Filling* (INTERSPEECH 2016) | [1609.01454](https://arxiv.org/abs/1609.01454) · [PDF](sources/liu-2016-attention-based-recurrent-neural-network.pdf) | [06](notes/06-application-patterns.md) |
|  | Goo et al., *Slot-Gated Modeling* (NAACL 2018): 4.2% and 1.9% relative frame-accuracy gains on ATIS and Snips | [ACL Anthology](https://aclanthology.org/N18-2118/) · [PDF](sources/goo-2018-slot-gated-modeling-joint-slot.pdf) | [06](notes/06-application-patterns.md) |
| ⚑ | Chen et al., *BERT for Joint Intent Classification and Slot Filling* (2019) | [1902.10909](https://arxiv.org/abs/1902.10909) · [PDF](sources/chen-2019-bert-joint-intent-classification-slot.pdf) | [06](notes/06-application-patterns.md) |
|  | Louvan & Magnini, *Recent Neural Methods on Slot Filling and Intent Classification* (COLING 2020): the datasets are solved, not the problem | [2011.00564](https://arxiv.org/abs/2011.00564) · [PDF](sources/louvan-2020-recent-neural-methods-slot-filling.pdf) | [06](notes/06-application-patterns.md) |
| ★⚑ | Bunk et al., *DIET* (2020): no clear benefit from large pretrained embeddings; beats fine-tuned BERT at about six times the training speed | [2004.09936](https://arxiv.org/abs/2004.09936) · [PDF](sources/bunk-2020-diet.pdf) | [06](notes/06-application-patterns.md) |
| ⚑ | Vlasov et al., *Dialogue Transformers* (TED, 2019): self-attention over turns, for interleaved topics | [1910.00486](https://arxiv.org/abs/1910.00486) · [PDF](sources/vlasov-2019-dialogue-transformers.pdf) | [06](notes/06-application-patterns.md) |
|  | Henderson et al., *Training Neural Response Selection for Task-Oriented Dialogue Systems* (ACL 2019): pretrain on Reddit, fine-tune on six domains | [ACL Anthology](https://aclanthology.org/P19-1536/) · [PDF](sources/henderson-2019-training-neural-response-selection-task.pdf) | [06](notes/06-application-patterns.md) |
|  | Fu et al., *Learning towards conversational AI: A survey* (AI Open, 2022; CC BY-NC-ND) | [DOI](https://doi.org/10.1016/j.aiopen.2022.02.001) · [PDF](sources/learning-towards-conversational-ai-survey.pdf) | [06](notes/06-application-patterns.md) |
| ⚑ | Adiwardana et al., *Towards a Human-like Open-Domain Chatbot* (Meena, 2020): SSA 72% to 79%, against 86% for people | [2001.09977](https://arxiv.org/abs/2001.09977) · [PDF](sources/adiwardana-2020-towards-human-like-open-domain.pdf) | [06](notes/06-application-patterns.md) |
| ★⚑ | Lu et al., *Blending Is All You Need* (2024): three 6 to 13B models beat 175B+ ChatGPT on retention in CHAI A/B tests | [2401.02994](https://arxiv.org/abs/2401.02994) · [PDF](sources/lu-2024-blending-all-you-need.pdf) | [06](notes/06-application-patterns.md) |
|  | Park et al., *A Practical Approach for Building Production-Grade Conversational Agents with Workflow Graphs* (2025): 52% task accuracy and 50% format adherence improvement over their baseline | [2505.23006](https://arxiv.org/abs/2505.23006) · [PDF](sources/park-2025-practical-approach-building-production-grade.pdf) | [06](notes/06-application-patterns.md) |
| ⚑ | Li et al., *Eliciting Human Preferences with Language Models* (GATE, 2023): models ask, users report less effort | [2310.11589](https://arxiv.org/abs/2310.11589) · [PDF](sources/li-2023-eliciting-human-preferences-language-models.pdf) | [06](notes/06-application-patterns.md) |
| ★ | Bansal et al., *Does the Whole Exceed its Parts?* (CHI 2021): over 1,500 participants; explanations helped when the AI was right and hurt when it was wrong; none beat showing confidence. This changed how note 06 treats confirmation | [2006.14779](https://arxiv.org/abs/2006.14779) · [PDF](sources/bansal-2020-does-whole-exceed-its-parts.pdf) | [06](notes/06-application-patterns.md) |
|  | Amershi et al., *Guidelines for Human-AI Interaction* (CHI 2019): 18 guidelines tested by 49 practitioners on 20 products | [DOI](https://doi.org/10.1145/3290605.3300233) · [PDF](sources/guidelines-human-ai-interaction-camera-ready.pdf) | [06](notes/06-application-patterns.md) |
|  | Yang et al., *Re-examining Whether, Why, and How Human-AI Interaction Is Uniquely Difficult to Design* (CHI 2020): capability uncertainty and output complexity, four levels | [DOI](https://doi.org/10.1145/3313831.3376301) · [PDF](sources/re-examining-whether-why-how-human.pdf) | [06](notes/06-application-patterns.md) |
|  | Wu et al., *Grounded Persuasive Language Generation for Automated Marketing* (2025). Cited by Rothman ch. 9; not yet read for this course | [2502.16810](https://arxiv.org/abs/2502.16810) | [06](notes/06-application-patterns.md) |
|  | Li et al., *LLM Generated Persona is a Promise with a Catch* (2025). Rothman ch. 9 further reading; not yet read for this course | [2503.16527](https://arxiv.org/abs/2503.16527) | [06](notes/06-application-patterns.md) |

<!-- citegraph:origins start -->
## Where the ideas come from

Generated by `citegraph.py refs --write` on 2026-10-31; rerun it instead of editing between the markers. These works are cited by at least 3 of this pillar's papers, at least 2 of them for the method, so an idea most likely starts there. When a note states one of these ideas, cite the origin as well as the recent paper. **Cited by** counts this pillar's papers; **For method** counts those citing it for its method. ⚑ = not peer-reviewed. Fetch the missing ones with `citegraph.py primary --download`.

| Paper | Venue | Cited by | For method | We hold |
|---|---|---|---|---|
| [Vaswani 2017, Attention Is All You Need](https://arxiv.org/abs/1706.03762) | NIPS 2017 | 5 | 3 | [✓ PDF](../01-llm-fundamentals/sources/vaswani-2017-attention-all-you-need.pdf) |
| [Devlin 2019, BERT: Pre-training of Deep Bidirectional Transformers for Language Und](https://doi.org/10.18653/v1/n19-1423) | NAACL-HLT (1) 2019 | 4 | 4 | [✓ PDF](../01-llm-fundamentals/sources/devlin-2018-bert.pdf) |
| [Henderson 2019, Training Neural Response Selection for Task-Oriented Dialogue Systems](https://doi.org/10.18653/v1/p19-1536) | ACL (1) 2019 | 3 | 3 | [✓ PDF](sources/henderson-2019-training-neural-response-selection-task.pdf) |
<!-- citegraph:origins end -->

## AI Papers of the Week

| | Paper | arXiv | Notes |
|---|---|---|---|
| | Shao et al., *DR Tulu: Reinforcement Learning with Evolving Rubrics for Deep Research* (2025): RLER, with search-grounded persistent rubrics plus positive/negative rubrics regenerated from each rollout group; 8B averages 60.7 vs 53.9 SFT-only; highest train reward ≠ best downstream | [PDF (Ai2)](https://www.datocms-assets.com/64837/1763496622-dr_tulu_draft.pdf) · [PDF](sources/dr-tulu-2025.pdf) | [02](notes/02-deep-research-bot.md#rl-on-the-same-agent-notebook-03) |
| | Singh et al., *Code Researcher: Deep Research Agent for Large Systems Code and Commit History* (2025): commit-history search and a filtered (action, result) memory; 48% vs SWE-agent 31.5% on 200 kernel crashes; "resolved" = crash prevented | [PDF (MSR)](https://www.microsoft.com/en-us/research/wp-content/uploads/2025/06/Code_Researcher-1.pdf) · [PDF](sources/code-researcher-2025.pdf) | [02](notes/02-deep-research-bot.md#context-engineering-compaction-at-80) |
| | Kimi Team, *Kimi-Audio Technical Report* (2025): 7B audio LLM, 13M hours of audio; VoiceBench 76.93 vs 72.83 for Qwen2.5-Omni on its own toolkit; served turn-based behind VAD. Filed under multimodal | [Kimi-Audio PDF](https://github.com/MoonshotAI/Kimi-Audio/blob/master/assets/kimia_report.pdf) · [PDF](../../ai-engineering/08-multimodal-engineering/sources/kimi-audio-2025.pdf) | [03](notes/03-real-time-multimodal-agents.md#paradigm-2-end-to-end-omnimodal-omni) |
| | Yamada et al., *The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search* (2025): staged best-first experiment tree; of three submitted manuscripts, one averaged 6.33 at an ICLR workshop (above the acceptance bar) and was withdrawn as agreed | [PDF (Sakana)](https://pub.sakana.ai/ai-scientist-v2/paper/paper.pdf) · [PDF](sources/ai-scientist-v2-2025.pdf) | [03-agentic-foundations 01](../03-agentic-foundations/notes/01-agent-fundamentals.md#agents-as-state-machines) |
| | Qwen Team, *Qwen2.5-Omni Technical Report* (2025): origin of the Thinker–Talker split; MMLU-Pro 47.0 vs 56.3 for text-only Qwen2.5-7B. Filed under multimodal | [Qwen2.5-Omni PDF](https://github.com/QwenLM/Qwen2.5-Omni/blob/main/assets/Qwen2.5_Omni.pdf) · [PDF](../../ai-engineering/08-multimodal-engineering/sources/qwen2-5-omni-2025.pdf) | [03](notes/03-real-time-multimodal-agents.md#paradigm-2-end-to-end-omnimodal-omni) |
| | Qin et al., *UI-TARS: Pioneering Automated GUI Interaction with Native Agents* (2025): one model for perception, grounding and action; ScreenSpot-Pro 38.1, OSWorld 22.7 at 15 steps vs Claude 14.9; DPO +3.9; mostly self-run evals | [2501.12326](https://arxiv.org/abs/2501.12326) · [PDF](sources/qin-2025-ui-tars.pdf) | [03](notes/03-real-time-multimodal-agents.md#computer-use) |
| | Défossez et al., *Moshi: a speech-text foundation model for real-time dialogue* (2024): full-duplex, two audio streams plus an inner-monologue text stream; 160 ms theoretical, ~200 ms practical latency; text MMLU 54.3 → 49.7 after audio training. Filed under multimodal | [2410.00037](https://arxiv.org/abs/2410.00037) · [PDF](../../ai-engineering/08-multimodal-engineering/sources/moshi-2024.pdf) | [03](notes/03-real-time-multimodal-agents.md#paradigm-3-full-duplex) |
| | Hong et al., *CogAgent: A Visual Language Model for GUI Agents* (2023): high-resolution cross-attention branch reads 1120×1120 screenshots; Mind2Web from pixels 58.2 vs HTML-reading LLaMA2-70B 54.4 | [2312.08914](https://arxiv.org/abs/2312.08914) · [PDF](sources/hong-2023-cogagent.pdf) | [03](notes/03-real-time-multimodal-agents.md#computer-use) |

## Courses and videos

Links and prices were checked on 2026-11-01. Prices change, so confirm before you pay.

| | Course or video | Platform and cost | Length | Notes |
|---|---|---|---|---|
| ★ | [CS294/194-196 Agentic AI](https://rdi.berkeley.edu/agentic-ai/f25) (Fall 2025) | UC Berkeley; free slides and YouTube lectures | One term | All. Guest lectures on training and deploying agents |
| | [Agentic AI](https://www.deeplearning.ai/courses/agentic-ai/), Andrew Ng | DeepLearning.AI; PRO membership | 9h55m | [01](notes/01-internet-search-agent.md), [02](notes/02-deep-research-bot.md), [05](notes/05-data-analysis-agent.md) |
| | [Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course/unit0/introduction) | Hugging Face; free | Self-paced | [01](notes/01-internet-search-agent.md), [02](notes/02-deep-research-bot.md) |
| | [Introduction to LangGraph](https://academy.langchain.com/courses/intro-to-langgraph) | LangChain Academy; free | 6 hours of video | [01](notes/01-internet-search-agent.md) |
| | [AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) | DeepLearning.AI; enroll for free | 1h42m | [01](notes/01-internet-search-agent.md) |
| | [Building Code Agents with Hugging Face smolagents](https://www.deeplearning.ai/short-courses/building-code-agents-with-hugging-face-smolagents/) | DeepLearning.AI; enroll for free | 54m | [04](notes/04-coding-agent.md), [05](notes/05-data-analysis-agent.md) |
| | [Claude Code: A Highly Agentic Coding Assistant](https://www.deeplearning.ai/short-courses/claude-code-a-highly-agentic-coding-assistant/) | DeepLearning.AI; enroll for free | 2h | [04](notes/04-coding-agent.md) |
| | [Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action) | Anthropic Academy; free | Self-paced | [04](notes/04-coding-agent.md) |
| | [Building toward Computer Use with Anthropic](https://www.deeplearning.ai/short-courses/building-towards-computer-use-with-anthropic/) | DeepLearning.AI; enroll for free | 1h47m | [03](notes/03-real-time-multimodal-agents.md) |
| | [Building Live Voice Agents with Google's ADK](https://www.deeplearning.ai/short-courses/building-live-voice-agents-with-googles-adk/) | DeepLearning.AI; enroll for free | 1h25m | [03](notes/03-real-time-multimodal-agents.md) |
| | [Andrej Karpathy: Software Is Changing (Again)](https://www.youtube.com/watch?v=LCEmiRjPEtQ) | Y Combinator, YouTube; free | One talk | [06](notes/06-application-patterns.md). Partial autonomy and the human review loop |

## First-party docs and engineering posts

| | Source | Notes |
|---|---|---|
| ★ | Omidreza Amrollahi, [internet-search-agent](https://github.com/omidreza-amrollahi/internet-search-agent) (MIT): two LangGraph graphs behind FastAPI | 01 |
| ★ | LangGraph [docs](https://docs.langchain.com/langgraph): `StateGraph`, `MessagesState`, checkpointers, `Command(resume=…)` | 01 |
| | [crawl4ai](https://github.com/unclecode/crawl4ai): the `/md` endpoint used for page crawling | 01 |
| | [Exa](https://docs.exa.ai/) `search_and_contents`; [W&B Inference](https://docs.wandb.ai/guides/inference/) (OpenAI-compatible); [Weave](https://weave-docs.wandb.ai/) ops and `weave.Evaluation` | 02 |
| | OpenPipe [ART](https://art.openpipe.ai/) and [RULER](https://art.openpipe.ai/fundamentals/ruler): relative LLM-judge rewards for agent RL | 02 |
| | Anthropic, [*The "think" tool*](https://www.anthropic.com/engineering/claude-think-tool) (2025): a no-op tool for structured reflection | 02 |
| | Anthropic [computer-use demo](https://github.com/anthropics/claude-quickstarts/tree/main/computer-use-demo); [browser-use](https://github.com/browser-use/browser-use) | 03 |
| | Coding agents: [Claude Code](https://code.claude.com/), [Codex CLI](https://github.com/openai/codex), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [Aider](https://aider.chat/), [OpenHands](https://docs.all-hands.dev/), [Cline](https://github.com/cline/cline). The largest class of shipped agentic applications; harness depth in [03-harness](../../ai-engineering/03-harness-engineering/README.md) | [04](notes/04-coding-agent.md) |
| | OpenAI, [*Harness engineering*](https://openai.com/index/harness-engineering/): a field report on software built by agents | — |
| | [FunASR](https://github.com/modelscope/FunASR): open ASR toolkit for the cascaded voice pipeline in 03 | 03 |
| | [500 AI/ML/DL/CV/NLP projects with code](https://github.com/ashishpatel26/500-AI-Machine-learning-Deep-learning-Computer-vision-NLP-Projects-with-code): project idea bank | — |

---

## Source quality

| Source | Issue | Prefer |
|---|---|---|
| internet-search-agent | Uses the Bing Search API, which Microsoft retired in August 2025; several parsing bugs (see 01 § Review) | The graphs as a pattern; swap the search client |
| deep-research-bot | Workshop code: `--deep` prompt bug, docstring-parser bug, notebook 03 needs an upstream branch (see 02 § Review) | Upstream repo for notebook 03 |
| deep_research_bench README | Leaderboard "news" is vendor-heavy and moves weekly | The paper and the Hugging Face leaderboard |
| `learning-towards-conversational-ai-survey-07d04bbf.pdf` | A second, different-sized copy of the Fu et al. survey (and 02 holds a third as `conversational-ai.pdf`) | Keep `learning-towards-conversational-ai-survey.pdf` |
| `louvan-2020-…pdf` | Byte-identical to 02's `2011.00564v1.pdf` | This copy (07 is the better home) |
| Rothman, *Context Engineering for Multi-Agent Systems* ch. 9 | Presents an ungrounded ROI pitch (claims no source states, against the brand guide's own no-unguaranteed-promises rule) as the chapter's key success; one run per use case; end-of-chapter questions refer to a `BrandChecker` agent and an email-nurture use case the chapter doesn't contain (see 06) | The pattern (new corpus, same engine); check grounding claim by claim |
| Licences | Kept: deep-research-bot (Apache-2.0), deep_research_bench (Apache-2.0 file; README badge says MIT). Removed: internet-search-agent snapshot (MIT, © 2025 Omidreza Amrollahi). Paper PDFs are redistributed as downloaded; Fu et al. is CC BY-NC-ND | Link upstream if the repo goes public |
