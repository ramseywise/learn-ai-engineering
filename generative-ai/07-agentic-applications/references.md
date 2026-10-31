# References — Agentic Applications

> Every source the notes cite, mapped to notes. **★** = read first. Local PDFs live in [sources/](sources/). Rows marked *queued* are PDFs routed here by `/readings` that no note cites yet; fold them in with `/papers` or `/chapter`. Licences of the kept and removed projects are in [Source quality](#source-quality).

---

## Books and courses

| | Source | Notes |
|---|---|---|
| ★ | Weights & Biases, *Building Agents from Scratch* (Fully Connected London 2025 workshop), [morganmcg1/deep-research-bot](https://github.com/morganmcg1/deep-research-bot) (Apache-2.0). Kept in [practice/deep-research-bot/](practice/deep-research-bot/): notebooks 01–03, package, RACE eval | 02 |
| ★ | Bojie Li, *AI Agents in Depth* (2026), [ch. 6 real-time multimodal agents](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter6.md) (Apache-2.0): voice paradigms, fast/slow thinking, computer use, robotics. Figures as `li-ai-agents-in-depth-fig6-*` | 03 |
| | Li, *AI Agents in Depth*, other application labs upstream: web search and search + codegen agents ([ch. 1](https://github.com/bojieli/ai-agent-book/tree/main/chapter1)); paper → slides → video, log diagnosis, text-to-SQL ([ch. 5](https://github.com/bojieli/ai-agent-book/tree/main/chapter5)) | — |
| | Denis Rothman, *Context Engineering for Multi-Agent Systems* (Packt, 2025). Chapter PDF in [sources/context-engineering-multi-agent-systems/](sources/context-engineering-multi-agent-systems/). Folded in as: ch. 9 → [04](notes/04-application-patterns.md#worked-example-one-engine-a-new-domain) (re-tasking the Context Engine to marketing by changing only the corpus and goals, the 69.63 s run, and the ungrounded ROI pitch). The engine itself (ch. 4, 5, 8) is in [ai-engineering/03-harness-engineering](../../ai-engineering/03-harness-engineering/references.md). Notes cite it as (*Context Engineering for Multi-Agent Systems*, ch. N). Figure `context-engineering-multi-agent-systems-fig9-1` | 04 |
| | Mayo Oshin & Nuno Campos, *Learning LangChain* (O'Reilly, 2025). Chapter PDFs in [../01-llm-fundamentals/sources/learning-langchain/](../01-llm-fundamentals/sources/learning-langchain/). Folded in as: ch. 11 → [04](notes/04-application-patterns.md) (chatbot, collaborative editing and ambient patterns, with the building blocks each needs). Notes cite it as (*Learning LangChain*, ch. N) | 04 |

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
| | Coding agents: [Claude Code](https://code.claude.com/), [Codex CLI](https://github.com/openai/codex), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [Aider](https://aider.chat/), [OpenHands](https://docs.all-hands.dev/), [Cline](https://github.com/cline/cline). The largest class of shipped agentic applications; harness depth in [03-harness](../../ai-engineering/03-harness-engineering/README.md) | — |
| | OpenAI, [*Harness engineering*](https://openai.com/index/harness-engineering/): a field report on software built by agents | — |
| | [FunASR](https://github.com/modelscope/FunASR): open ASR toolkit for the cascaded voice pipeline in 03 | 03 |
| | [500 AI/ML/DL/CV/NLP projects with code](https://github.com/ashishpatel26/500-AI-Machine-learning-Deep-learning-Computer-vision-NLP-Projects-with-code): project idea bank | — |

## Papers

| | Paper | arXiv | Notes |
|---|---|---|---|
| ★ | Du et al., *DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents* (2025): 100 tasks, RACE and FACT. Code in [practice/deep_research_bench/](practice/deep_research_bench/) | [2506.11763](https://arxiv.org/abs/2506.11763) | 02 |
| | Wu et al., *Grounded Persuasive Language Generation for Automated Marketing* (2025). Cited by Rothman ch. 9; not yet read | [2502.16810](https://arxiv.org/abs/2502.16810) | 04 |
| | Li et al., *LLM Generated Persona is a Promise with a Catch* (2025). Rothman ch. 9 further reading; not yet read | [2503.16527](https://arxiv.org/abs/2503.16527) | 04 |
| | Jimenez et al., *SWE-bench* (2023). [Site](https://www.swebench.com/); [Terminal-Bench](https://www.tbench.ai/) is the shell-task counterpart | [2310.06770](https://arxiv.org/abs/2310.06770) | — |
| | Vlasov et al., *Dialogue Transformers* (TED, 2019). [PDF](sources/vlasov-2019-dialogue-transformers.pdf) | [1910.00486](https://arxiv.org/abs/1910.00486) | *queued* |
| | Bunk et al., *DIET: Lightweight Language Understanding for Dialogue Systems* (2020). [PDF](sources/bunk-2020-diet.pdf) | [2004.09936](https://arxiv.org/abs/2004.09936) | *queued* |
| | Chen et al., *BERT for Joint Intent Classification and Slot Filling* (2019). [PDF](sources/chen-2019-bert-joint-intent-classification-slot.pdf) | [1902.10909](https://arxiv.org/abs/1902.10909) | *queued* |
| | Louvan & Magnini, *Recent Neural Methods on Slot Filling and Intent Classification* (2020). [PDF](sources/louvan-2020-recent-neural-methods-slot-filling.pdf) | [2011.00564](https://arxiv.org/abs/2011.00564) | *queued* |
| | Fu et al., *Learning towards conversational AI: A survey* (AI Open, 2022; CC BY-NC-ND). [PDF](sources/learning-towards-conversational-ai-survey.pdf) | — | *queued* |
| | Bansal et al., *Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance* (CHI 2021). [PDF](sources/bansal-2020-does-whole-exceed-its-parts.pdf) | [2006.14779](https://arxiv.org/abs/2006.14779) | *queued* |
| | Amershi et al., *Guidelines for Human-AI Interaction* (CHI 2019). [PDF](sources/guidelines-human-ai-interaction-camera-ready.pdf) | — | *queued* |
| | Yang et al., *Re-examining Whether, Why, and How Human-AI Interaction Is Uniquely Difficult to Design* (CHI 2020). [PDF](sources/re-examining-whether-why-how-human.pdf) | — | *queued* |

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

---

## Source quality

| Source | Issue | Prefer |
|---|---|---|
| internet-search-agent | Uses the Bing Search API, which Microsoft retired in August 2025; several parsing bugs (see 01 § Review) | The graphs as a pattern; swap the search client |
| deep-research-bot | Workshop code: `--deep` prompt bug, docstring-parser bug, notebook 03 needs an upstream branch (see 02 § Review) | Upstream repo for notebook 03 |
| deep_research_bench README | Leaderboard "news" is vendor-heavy and moves weekly | The paper and the Hugging Face leaderboard |
| `learning-towards-conversational-ai-survey-07d04bbf.pdf` | A second, different-sized copy of the Fu et al. survey (and 02 holds a third as `conversational-ai.pdf`) | Keep `learning-towards-conversational-ai-survey.pdf` |
| `louvan-2020-…pdf` | Byte-identical to 02's `2011.00564v1.pdf` | This copy (07 is the better home) |
| Rothman, *Context Engineering for Multi-Agent Systems* ch. 9 | Presents an ungrounded ROI pitch (claims no source states, against the brand guide's own no-unguaranteed-promises rule) as the chapter's key success; one run per use case; end-of-chapter questions refer to a `BrandChecker` agent and an email-nurture use case the chapter doesn't contain (see 04) | The pattern (new corpus, same engine); check grounding claim by claim |
| Licences | Kept: deep-research-bot (Apache-2.0), deep_research_bench (Apache-2.0 file; README badge says MIT). Removed: internet-search-agent snapshot (MIT, © 2025 Omidreza Amrollahi). Paper PDFs are redistributed as downloaded; Fu et al. is CC BY-NC-ND | Link upstream if the repo goes public |
