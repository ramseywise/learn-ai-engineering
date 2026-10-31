# References — Agentic Applications

> Every source the notes cite, mapped to notes. **★** = read first. Local PDFs live in [sources/](sources/). Rows marked *queued* are PDFs routed here by `/readings` that no note cites yet; fold them in with `/papers` or `/chapter`. Licences of the kept and removed projects are in [Source quality](#source-quality).

---

## Books and courses

| | Source | Notes |
|---|---|---|
| ★ | Weights & Biases, *Building Agents from Scratch* (Fully Connected London 2025 workshop), [morganmcg1/deep-research-bot](https://github.com/morganmcg1/deep-research-bot) (Apache-2.0). Kept in [practice/deep-research-bot/](practice/deep-research-bot/): notebooks 01–03, package, RACE eval | 02 |
| ★ | Bojie Li, *AI Agents in Depth* (2026), [ch. 6 real-time multimodal agents](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter6.md) (Apache-2.0): voice paradigms, fast/slow thinking, computer use, robotics. Figures as `li-ai-agents-in-depth-fig6-*` | 03 |
| | Li, *AI Agents in Depth*, other application labs upstream: web search and search + codegen agents ([ch. 1](https://github.com/bojieli/ai-agent-book/tree/main/chapter1)); paper → slides → video, log diagnosis, text-to-SQL ([ch. 5](https://github.com/bojieli/ai-agent-book/tree/main/chapter5)) | — |
| | *Context Engineering for Multi-Agent Systems*, [ch. 9 brand-agility marketing engine](sources/context-engineering-multi-agent-systems/ch09-architecting-brand-agility-strategic-marketing-engine.pdf). *Queued* | — |

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
| | Jimenez et al., *SWE-bench* (2023). [Site](https://www.swebench.com/); [Terminal-Bench](https://www.tbench.ai/) is the shell-task counterpart | [2310.06770](https://arxiv.org/abs/2310.06770) | — |
| | Vlasov et al., *Dialogue Transformers* (TED, 2019). [PDF](sources/vlasov-2019-dialogue-transformers.pdf) | [1910.00486](https://arxiv.org/abs/1910.00486) | *queued* |
| | Bunk et al., *DIET: Lightweight Language Understanding for Dialogue Systems* (2020). [PDF](sources/bunk-2020-diet.pdf) | [2004.09936](https://arxiv.org/abs/2004.09936) | *queued* |
| | Chen et al., *BERT for Joint Intent Classification and Slot Filling* (2019). [PDF](sources/chen-2019-bert-joint-intent-classification-slot.pdf) | [1902.10909](https://arxiv.org/abs/1902.10909) | *queued* |
| | Louvan & Magnini, *Recent Neural Methods on Slot Filling and Intent Classification* (2020). [PDF](sources/louvan-2020-recent-neural-methods-slot-filling.pdf) | [2011.00564](https://arxiv.org/abs/2011.00564) | *queued* |
| | Fu et al., *Learning towards conversational AI: A survey* (AI Open, 2022; CC BY-NC-ND). [PDF](sources/learning-towards-conversational-ai-survey.pdf) | — | *queued* |
| | Bansal et al., *Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance* (CHI 2021). [PDF](sources/bansal-2020-does-whole-exceed-its-parts.pdf) | [2006.14779](https://arxiv.org/abs/2006.14779) | *queued* |
| | Amershi et al., *Guidelines for Human-AI Interaction* (CHI 2019). [PDF](sources/guidelines-human-ai-interaction-camera-ready.pdf) | — | *queued* |
| | Yang et al., *Re-examining Whether, Why, and How Human-AI Interaction Is Uniquely Difficult to Design* (CHI 2020). [PDF](sources/re-examining-whether-why-how-human.pdf) | — | *queued* |

---

## Source quality

| Source | Issue | Prefer |
|---|---|---|
| internet-search-agent | Uses the Bing Search API, which Microsoft retired in August 2025; several parsing bugs (see 01 § Review) | The graphs as a pattern; swap the search client |
| deep-research-bot | Workshop code: `--deep` prompt bug, docstring-parser bug, notebook 03 needs an upstream branch (see 02 § Review) | Upstream repo for notebook 03 |
| deep_research_bench README | Leaderboard "news" is vendor-heavy and moves weekly | The paper and the Hugging Face leaderboard |
| `learning-towards-conversational-ai-survey-07d04bbf.pdf` | A second, different-sized copy of the Fu et al. survey (and 02 holds a third as `conversational-ai.pdf`) | Keep `learning-towards-conversational-ai-survey.pdf` |
| `louvan-2020-…pdf` | Byte-identical to 02's `2011.00564v1.pdf` | This copy (07 is the better home) |
| Licences | Kept: deep-research-bot (Apache-2.0), deep_research_bench (Apache-2.0 file; README badge says MIT). Removed: internet-search-agent snapshot (MIT, © 2025 Omidreza Amrollahi). Paper PDFs are redistributed as downloaded; Fu et al. is CC BY-NC-ND | Link upstream if the repo goes public |
