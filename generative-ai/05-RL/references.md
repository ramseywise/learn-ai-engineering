---
origin: curated
sources:
  - generative-ai/resources.md (05 section)
  - old 05-RL/README.md curriculum tables
confidence: high
cleaned: 2026-10-31
---

# References — RL & Alignment

> Every source the notes cite, mapped to notes. **★** = read first. Local PDFs live in [sources/](sources/). Rows marked ✓ have a local copy. The open gaps that used to sit in the README's curriculum table are in [Gaps](#gaps).

---

## Books

| | Source | Notes |
|---|---|---|
| ★ | Sutton & Barto, [*Reinforcement Learning: An Introduction*](http://incompleteideas.net/book/the-book-2nd.html) (2nd ed., 2018). ✓ [sources/sutton-barto-2018-reinforcement-learning-2nd-ed.pdf](sources/sutton-barto-2018-reinforcement-learning-2nd-ed.pdf) (70 MB). Ch. 1–6 cover MDPs, DP, Monte Carlo, TD and Q-learning; ch. 13 covers policy gradients | 01, 05 |
| ★ | Bojie Li, *AI Agents in Depth* (2026), [ch. 8 Post-Training](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter8.md) (Apache-2.0). Synthesized into 05; figures 8-11, 8-13 and 8-15 are in [sources/images/](sources/images/) as `li-ai-agents-in-depth-*`. Experiment 7-1 is the [Q-learning lab](practice/01-q-learning-treasure-hunt/) | 05 |
| | Phil Winder, *Reinforcement Learning: Industrial Applications of Intelligent Agents* (O'Reilly, 2020). ✓ Chapter PDFs ch. 1–11 in [sources/winder-reinforcement-learning/](sources/winder-reinforcement-learning/). Ch. 2–5 parallel Sutton & Barto with code; ch. 9–10 cover RL in production | 01 |
| | Lattimore & Szepesvári, *Bandit Algorithms* (Cambridge, 2020). ✓ [sources/lattimore-szepesvari-2020-bandit-algorithms.pdf](sources/lattimore-szepesvari-2020-bandit-algorithms.pdf). The exploration–exploitation trade-off with no state | 01 |
| | Hugging Face, [Deep RL Course](https://huggingface.co/learn/deep-rl-course): hands-on Q-learning, DQN, PPO with Gymnasium | 01 |
| | OpenAI, [Spinning Up in Deep RL](https://spinningup.openai.com/): policy-gradient derivations and reference PPO code | 01, 03 |
| | *LLM Engineer's Handbook* ch. 5–6 (SFT and preference alignment with DPO). ✓ in [01-llm-fundamentals/sources/llm-engineers-handbook/](../01-llm-fundamentals/sources/llm-engineers-handbook/) | 02, 03 |
| | Raschka, *Build a Large Language Model (From Scratch)* ch. 6–7 (classification and instruction fine-tuning: stage 1 of RLHF). ✓ in [01-llm-fundamentals/sources/build-a-large-language-model-from-scratch/](../01-llm-fundamentals/sources/build-a-large-language-model-from-scratch/) | 02 |

## First-party docs

| | Source | Notes |
|---|---|---|
| ★ | Hugging Face [TRL docs](https://huggingface.co/docs/trl/): `SFTTrainer`, `RewardTrainer`, `PPOTrainer`, `DPOTrainer`, `GRPOTrainer` | 02, 03 |
| | [OpenRLHF](https://github.com/OpenRLHF/OpenRLHF): distributed PPO/GRPO | 03 |
| | OpenAI, [*Improving mathematical reasoning with process supervision*](https://openai.com/index/improving-mathematical-reasoning-with-process-reward-models/): process vs outcome reward models | 02, 05 |
| | Anthropic, [Claude's constitution](https://www.anthropic.com/news/claudes-constitution) | 04 |
| | Ray RLlib, PyMARL, PettingZoo: multi-agent frameworks listed in 01's tooling section | 01 |

## Core papers

| | Paper | arXiv | Local | Notes |
|---|---|---|---|---|
| | Mnih et al., *Playing Atari with Deep RL* (DQN) | [1312.5602](https://arxiv.org/abs/1312.5602) | ✓ [mnih-2013-dqn-atari.pdf](sources/mnih-2013-dqn-atari.pdf) | 01 |
| | Li et al., *A Contextual-Bandit Approach to Personalized News* (LinUCB) | [1003.0146](https://arxiv.org/abs/1003.0146) | ✓ [li-2010-…](sources/li-2010-contextual-bandit-news-recommendation.pdf) | 01 |
| | Zhou, *A Survey on Contextual Multi-armed Bandits* | [1508.03326](https://arxiv.org/abs/1508.03326) | ✓ [zhou-2015-…](sources/zhou-2015-contextual-bandits-survey.pdf) | 01 |
| | Riquelme et al., *Deep Bayesian Bandits Showdown* | [1802.09127](https://arxiv.org/abs/1802.09127) | ✓ [riquelme-2018-…](sources/riquelme-2018-deep-bayesian-bandits.pdf) | 01 |
| ★ | Schulman et al., *Proximal Policy Optimization* (PPO) | [1707.06347](https://arxiv.org/abs/1707.06347) | ✓ [schulman-2017-ppo.pdf](sources/schulman-2017-ppo.pdf) | 01, 02, 03 |
| ★ | Christiano et al., *Deep RL from Human Preferences* | [1706.03741](https://arxiv.org/abs/1706.03741) | ✓ [christiano-2017-…](sources/christiano-2017-deep-rl-from-human-preferences.pdf) | 02 |
| ★ | Ouyang et al., *Training LMs to Follow Instructions with Human Feedback* (InstructGPT) | [2203.02155](https://arxiv.org/abs/2203.02155) | ✓ [ouyang-2022-instructgpt.pdf](sources/ouyang-2022-instructgpt.pdf) | 01, 02 |
| | Bai et al., *Training a Helpful and Harmless Assistant with RLHF* | [2204.05862](https://arxiv.org/abs/2204.05862) | — | 02 |
| | OpenAI, *GPT-4 Technical Report* | [2303.08774](https://arxiv.org/abs/2303.08774) | ✓ in [01 sources](../01-llm-fundamentals/sources/openai-2023-gpt-4-technical-report.pdf) | 02 |
| ★ | Bai et al., *Constitutional AI: Harmlessness from AI Feedback* | [2212.08073](https://arxiv.org/abs/2212.08073) | ✓ [bai-2022-constitutional-ai.pdf](sources/bai-2022-constitutional-ai.pdf) | 04 |
| | Lee et al., *RLAIF: Scaling RL from Human Feedback with AI Feedback* | [2309.00267](https://arxiv.org/abs/2309.00267) | — | 04 |
| ★ | Rafailov et al., *Direct Preference Optimization* (DPO) | [2305.18290](https://arxiv.org/abs/2305.18290) | ✓ [rafailov-2023-dpo.pdf](sources/rafailov-2023-dpo.pdf) | 01, 03 |
| | Li, Yang & Wang, *Reinforcement Learning with Human Feedback: Learning Dynamic Choices via Pessimism* | [2305.18438](https://arxiv.org/abs/2305.18438) | ✓ [li-2023-rlhf-pessimism.pdf](sources/li-2023-rlhf-pessimism.pdf) | 02 |
| | Shao et al., *DeepSeekMath* (GRPO) | [2402.03300](https://arxiv.org/abs/2402.03300) | — | 03, 05 |
| | DeepSeek-AI, *DeepSeek-R1* | [2501.12948](https://arxiv.org/abs/2501.12948) | — | 03, 05 |
| | Nakano et al., *WebGPT* | [2112.09332](https://arxiv.org/abs/2112.09332) | — | 01 |
| | Asai et al., *Self-RAG* | [2310.11511](https://arxiv.org/abs/2310.11511) | — | 01 |
| | Yao et al., *ReAct* | [2210.03629](https://arxiv.org/abs/2210.03629) | ✓ [yao-2022-react.pdf](sources/yao-2022-react.pdf) | 01, 05 |
| | Shinn et al., *Reflexion* | [2303.11366](https://arxiv.org/abs/2303.11366) | ✓ [shinn-2023-reflexion.pdf](sources/shinn-2023-reflexion.pdf) | 01, 05 |
| | Yao et al., *Tree of Thoughts* | [2305.10601](https://arxiv.org/abs/2305.10601) | ✓ [yao-2023-tree-of-thoughts.pdf](sources/yao-2023-tree-of-thoughts.pdf) | — (agent reasoning; belongs with 03-agentic-foundations) |

### Misfiled papers

These came in with the old `2-llm-rlhf/` dump and are not about RL. They are kept in [sources/misfiled/](sources/misfiled/) so nothing is lost; the owning pillar can pull them.

| Paper | Better home |
|---|---|
| Lipton, *The Mythos of Model Interpretability* (1606.03490) | 01-llm-fundamentals or ai-engineering/06-eval |
| Amershi et al., *Software Engineering for Machine Learning* (ICSE 2019) | data-science or ai-engineering |
| *Conversational AI* survey | 07-agentic-applications/chatbot |
| Vlasov et al., *Dialogue Transformers* (Rasa TED, 1910.00486) | 07-agentic-applications/chatbot |
| Bunk et al., *DIET: Lightweight Language Understanding for Dialogue Systems* (Rasa, 2004.09936) | 07-agentic-applications/chatbot |
| Wu & Johnson, *Rethinking "Batch" in BatchNorm* (2105.07576) | data-science |

## Secondary

| Source | Notes |
|---|---|
| Lilian Weng, [*Reward Hacking in Reinforcement Learning*](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/) | 01, 02 |
| Hugging Face blog, [*Illustrating RLHF*](https://huggingface.co/blog/rlhf) | 02 |

## Gaps

The open items carried over from the old README's curriculum, quality assessment and priority roadmap. Topics 2, 3, 5 and 6 of that roadmap are done (notes 02–05); topic 4 (reward modeling) is mostly done in 05.

| Gap | Fill with |
|---|---|
| Hands-on RLHF/DPO notebook with TRL | TRL `DPOTrainer` quickstart on a small model; would become `practice/02-dpo-with-trl/` |
| Reward-model architecture note (scalar head, pairwise loss, PRM vs ORM training) | Anthropic 2204.05862 §3, OpenAI process-supervision post |
| Dedicated Sutton & Barto ch. 1–5 foundations note | 01 covers the LLM-relevant subset; a full note is low priority |
| RL for reasoning (o1-style) beyond R1 | 03's DeepSeek-R1 section and 05's three stages cover R1-Zero vs cold-start |
| 01's MARL and RL-in-RAG sections | Came from a mixed zh/en Notion export, now translated; confidence stays medium |

## Source quality

- Papers and textbooks above are primary. The Winder chapters and the two engineering handbooks are purchased copies; keep them local and do not redistribute.
- 05 is a synthesis of one book chapter (Li, Apache-2.0). Its numbers (e.g. "0% wins at 1k episodes, 100% at 10k" in the lab) are reproduced locally; other figures rest on the book.
- 01 started life as a low-confidence Notion export. It has been cleaned and translated, but bare-URL claims in its MARL section were not re-verified.
