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
| | Phil Winder, *Reinforcement Learning: Industrial Applications of Intelligent Agents* (O'Reilly, 2020). Chapter PDFs in [sources/winder-reinforcement-learning/](sources/winder-reinforcement-learning/). Folded in as: ch. 1–3 → [01](notes/01-rl-foundations.md) §1 (MDP, Bellman, TD, Q-learning vs SARSA); ch. 4 → 01 §1 DQN and offline RL; ch. 5–6 → 01 §1 policy gradients and PPO clip; ch. 7 → 01 §1 entropy and SAC; ch. 8 → 01 §1 imitation/IRL, hierarchy/curricula and §2 MARL; ch. 9, 11 → 01 §1 exploration, engineering an RL problem, what has dated; ch. 10 → [01](notes/01-rl-foundations.md#scaling-actors-and-learners) (scaling, comparing runs). Notes cite it as `(*Reinforcement Learning*, ch. N)` | 01 |
| | Lattimore & Szepesvári, *Bandit Algorithms* (Cambridge, 2020). ✓ [sources/lattimore-szepesvari-2020-bandit-algorithms.pdf](sources/lattimore-szepesvari-2020-bandit-algorithms.pdf). The exploration–exploitation trade-off with no state | 01 |
| | Hugging Face, [Deep RL Course](https://huggingface.co/learn/deep-rl-course): hands-on Q-learning, DQN, PPO with Gymnasium | 01 |
| | OpenAI, [Spinning Up in Deep RL](https://spinningup.openai.com/): policy-gradient derivations and reference PPO code | 01, 03 |
| ★ | Chip Huyen, *AI Engineering* (O'Reilly, 2025). Chapter PDFs in [sources/huyen-ai-engineering/](sources/huyen-ai-engineering/). Folded in as: ch. 7 Finetuning (when to fine-tune, memory math, LoRA/QLoRA, hyperparameters, "form vs facts") → [02](notes/02-rlhf-pipeline.md#sft-in-practice); ch. 8 Dataset Engineering (quality vs diversity, Llama 3 domain mix, how much data, synthetic data and its limits, dedup, cleaning) → [05](notes/05-post-training-for-agents.md#data-engineering-for-post-training). Notes cite it as `(*AI Engineering*, ch. N)` | 02, 05 |
| ★ | Paul Iusztin & Maxime Labonne, *LLM Engineer's Handbook* (Packt, 2024). Chapter PDFs in [01-llm-fundamentals/sources/llm-engineers-handbook/](../01-llm-fundamentals/sources/llm-engineers-handbook/). Folded in as: ch. 5 Supervised Fine-Tuning (memory per parameter, Unsloth LoRA config, hyperparameters → [02](notes/02-rlhf-pipeline.md#sft-in-practice); curation pipeline, dataset sizes, Evol-Instruct → [05](notes/05-post-training-for-agents.md#data-engineering-for-post-training)); ch. 6 Preference Alignment (preference-data sizes, judge biases → [02](notes/02-rlhf-pipeline.md#stage-2--reward-model-training); DPO β, learning rate, TRL metrics → [03](notes/03-preference-optimization.md#dpo-in-practice)). Notes cite it as `(*LLM Engineer's Handbook*, ch. N)` | 02, 03, 05 |
| | Sebastian Raschka, *Build a Large Language Model (From Scratch)* (Manning, 2024). Chapter PDFs in [01-llm-fundamentals/sources/build-a-large-language-model-from-scratch/](../01-llm-fundamentals/sources/build-a-large-language-model-from-scratch/). Folded in as: ch. 6 classification fine-tuning (classification head, frozen layers) and ch. 7 instruction fine-tuning (chat template, collate function with `-100` masking, judge-scored eval) → [02](notes/02-rlhf-pipeline.md#sft-in-practice). Notes cite it as `(*Build an LLM from Scratch*, ch. N)` | 02 |
| | Nicole Koenigstein, *AI Agents: The Definitive Guide* (O'Reilly, 2026, Early Release). Chapter PDF in [sources/ai-agents-definitive-guide/](sources/ai-agents-definitive-guide/). Folded in as: ch. 3 GSPO and who-needs-what table → [03](notes/03-preference-optimization.md#gspo--sequence-level-ratios); RULER, ART, rLLM → [05](notes/05-post-training-for-agents.md#judges-as-rewards-ruler-art-and-rllm); MCTS, AB-MCTS, TreeQuest → [05](notes/05-post-training-for-agents.md#test-time-search-instead-of-training). Notes cite it as `(*AI Agents: The Definitive Guide*, ch. N)` | 03, 05 |
| | Michael Albada, *Building Applications with AI Agents* (O'Reilly, 2025). Chapter PDF in [sources/building-applications-with-ai-agents/](sources/building-applications-with-ai-agents/). Folded in as: ch. 7 nonparametric learning (exemplars, Reflexion, ExpeL), when to fine-tune, function-calling SFT → [05](notes/05-post-training-for-agents.md#learning-without-weights-first); its RLVR definition is flagged in 05. Notes cite it as `(*Building Applications with AI Agents*, ch. N)` | 05 |
| | Salvatore Raieli & Gabriele Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025). Chapter PDF in [sources/building-ai-agents-llms-rag-kgs/](sources/building-ai-agents-llms-rag-kgs/). Folded in as: ch. 8 LLM-enhanced RL taxonomy → [05](notes/05-post-training-for-agents.md#classic-rl-vs-llmrl-why-priors-win). Most of the chapter is a classic-RL primer (bandits, MDPs, DQN, REINFORCE, PPO, A2C/A3C, AlphaZero) that belongs with 01. Notes cite it as `(*Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. N)` | 05 |

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
| ★ | Schulman et al., *Proximal Policy Optimization* (PPO) | [1707.06347](https://arxiv.org/abs/1707.06347) | ✓ [schulman-2017-proximal-policy-optimization-algorithms.pdf](sources/schulman-2017-proximal-policy-optimization-algorithms.pdf) | 01, 02, 03 |
| ★ | Christiano et al., *Deep RL from Human Preferences* | [1706.03741](https://arxiv.org/abs/1706.03741) | ✓ [christiano-2017-…](sources/christiano-2017-deep-rl-from-human-preferences.pdf) | 02 |
| ★ | Ouyang et al., *Training LMs to Follow Instructions with Human Feedback* (InstructGPT) | [2203.02155](https://arxiv.org/abs/2203.02155) | ✓ [ouyang-2022-training-language-models-follow-instructions.pdf](sources/ouyang-2022-training-language-models-follow-instructions.pdf) | 01, 02 |
| | Bai et al., *Training a Helpful and Harmless Assistant with RLHF* | [2204.05862](https://arxiv.org/abs/2204.05862) | — | 02 |
| | OpenAI, *GPT-4 Technical Report* | [2303.08774](https://arxiv.org/abs/2303.08774) | ✓ in [01 sources](../01-llm-fundamentals/sources/openai-2023-gpt-4-technical-report.pdf) | 02 |
| ★ | Bai et al., *Constitutional AI: Harmlessness from AI Feedback* | [2212.08073](https://arxiv.org/abs/2212.08073) | ✓ [bai-2022-constitutional-ai.pdf](sources/bai-2022-constitutional-ai.pdf) | 04 |
| | Lee et al., *RLAIF: Scaling RL from Human Feedback with AI Feedback* | [2309.00267](https://arxiv.org/abs/2309.00267) | — | 04 |
| ★ | Rafailov et al., *Direct Preference Optimization* (DPO) | [2305.18290](https://arxiv.org/abs/2305.18290) | ✓ [rafailov-2023-dpo.pdf](sources/rafailov-2023-dpo.pdf) | 01, 03 |
| | Li, Yang & Wang, *Reinforcement Learning with Human Feedback: Learning Dynamic Choices via Pessimism* | [2305.18438](https://arxiv.org/abs/2305.18438) | ✓ [li-2023-rlhf-pessimism.pdf](sources/li-2023-rlhf-pessimism.pdf) | — (not cited: offline-RL theory, dynamic-discrete-choice model with linear-MDP/RKHS bounds, no LLM experiments) |
| | Ethayarajh et al., *KTO: Model Alignment as Prospect Theoretic Optimization* | [2402.01306](https://arxiv.org/abs/2402.01306) | ✓ [ethayarajh-2024-kto.pdf](sources/ethayarajh-2024-kto.pdf) | 03 (KTO numbers; DPO better on clean pairs) |
| ★ | Swamy et al., *All Roads Lead to Likelihood: The Value of RL in Fine-Tuning* | [2503.01067](https://arxiv.org/abs/2503.01067) | ✓ [swamy-2025-all-roads-lead-likelihood.pdf](sources/swamy-2025-all-roads-lead-likelihood.pdf) | 03 (why online beats offline: generation-verification gap) |
| ★ | Lanchantin et al., *Bridging Offline and Online Reinforcement Learning for LLMs* | [2506.21495](https://arxiv.org/abs/2506.21495) | ✓ [lanchantin-2025-bridging-offline-online-reinforcement-learning.pdf](sources/lanchantin-2025-bridging-offline-online-reinforcement-learning.pdf) | 03 (semi-online DPO ≈ online DPO ≈ GRPO ≫ offline DPO) |
| ★ | Yue et al., *Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?* | [2504.13837](https://arxiv.org/abs/2504.13837) | ✓ [yue-2025-does-reinforcement-learning-really-incentivize.pdf](sources/yue-2025-does-reinforcement-learning-really-incentivize.pdf) | 03, 05 (base beats RLVR at large k) |
| | Shao et al., *DeepSeekMath* (GRPO) | [2402.03300](https://arxiv.org/abs/2402.03300) | — | 03, 05 |
| | DeepSeek-AI, *DeepSeek-R1* | [2501.12948](https://arxiv.org/abs/2501.12948) | ✓ [deepseek-r1-2025.pdf](sources/deepseek-r1-2025.pdf) | 03, 05 |
| | Nakano et al., *WebGPT* | [2112.09332](https://arxiv.org/abs/2112.09332) | — | 01 |
| | Asai et al., *Self-RAG* | [2310.11511](https://arxiv.org/abs/2310.11511) | — | 01 |
| | Yao et al., *ReAct* | [2210.03629](https://arxiv.org/abs/2210.03629) | ✓ [yao-2022-react.pdf](sources/yao-2022-react.pdf) | 01, 05 |
| | Shinn et al., *Reflexion* | [2303.11366](https://arxiv.org/abs/2303.11366) | ✓ [shinn-2023-reflexion.pdf](sources/shinn-2023-reflexion.pdf) | 01, 05 |
| | Yu et al., *DAPO: An Open-Source LLM Reinforcement Learning System at Scale* | [2503.14476](https://arxiv.org/abs/2503.14476) | — | 03, 05 (Clip-Higher, dynamic sampling, token-level loss, overlong shaping) |
| | Shi et al., *Instruction Tuning With Loss Over Instructions* | [2405.14394](https://arxiv.org/abs/2405.14394) | — | 02 (prompt-loss weighting vs response-only masking) |
| | Zheng et al., *Group Sequence Policy Optimization* (GSPO) | [2507.18071](https://arxiv.org/abs/2507.18071) | — | 03 (sequence-level importance ratio) |
| | Inoue et al., *Wider or Deeper? Scaling LLM Inference-Time Compute with Adaptive Branching Tree Search* (AB-MCTS) | [2503.04412](https://arxiv.org/abs/2503.04412) | — | 05 |
| | Cao et al., *Survey on Large Language Model-Enhanced Reinforcement Learning* | [2404.00282](https://arxiv.org/abs/2404.00282) | — | 05 (four roles of an LLM in classic RL) |
| | Yao et al., *Tree of Thoughts* | [2305.10601](https://arxiv.org/abs/2305.10601) | ✓ [yao-2023-tree-of-thoughts.pdf](sources/yao-2023-tree-of-thoughts.pdf) | — (agent reasoning; belongs with 03-agentic-foundations) |

### Misfiled papers

These came in with the old `2-llm-rlhf/` dump and are not about RL. They are kept in [sources/misfiled/](sources/misfiled/) so nothing is lost; the owning pillar can pull them.

| Paper | Better home |
|---|---|
| Lipton, *The Mythos of Model Interpretability* (1606.03490) | 01-llm-fundamentals or ai-engineering/06-eval |
| Amershi et al., *Software Engineering for Machine Learning* (ICSE 2019) | data-science or ai-engineering |
| *Conversational AI* survey | 07-agentic-applications (a copy is already in its sources/) |
| Vlasov et al., *Dialogue Transformers* (Rasa TED, 1910.00486) | 07-agentic-applications (a copy is already in its sources/) |
| Bunk et al., *DIET: Lightweight Language Understanding for Dialogue Systems* (Rasa, 2004.09936) | 07-agentic-applications (a copy is already in its sources/) |
| Wu & Johnson, *Rethinking "Batch" in BatchNorm* (2105.07576) | data-science |

<!-- citegraph:origins start -->
## Where the ideas come from

Generated by `citegraph.py refs --write` on 2026-10-31; rerun it instead of editing between the markers. These works are cited by at least 3 of this pillar's papers, at least 2 of them for the method, so an idea most likely starts there. When a note states one of these ideas, cite the origin as well as the recent paper. **Cited by** counts this pillar's papers; **For method** counts those citing it for its method. ⚑ = not peer-reviewed. Fetch the missing ones with `citegraph.py primary --download`.

| Paper | Venue | Cited by | For method | We hold |
|---|---|---|---|---|
| [Ouyang 2022, Training Language Models to Follow Instructions with Human Feedback](https://doi.org/10.52202/068431-2011) | NeurIPS 2022 | 42 | 8 | [✓ PDF](sources/ouyang-2022-training-language-models-follow-instructions.pdf) |
| [Brown 2020, Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) | NeurIPS 2020 | 30 | 6 | [✓ PDF](../01-llm-fundamentals/sources/brown-2020-language-models-few-shot-learners.pdf) |
| [Wei 2022, Chain-Of-Thought Prompting Elicits Reasoning in Large Language Models](https://doi.org/10.52202/068431-1800) | NeurIPS 2022 | 25 | 4 | [✓ PDF](../../ai-engineering/01-prompt-engineering/sources/wei-2022-chain-thought-prompting-elicits-reasoning.pdf) |
| [Chen 2021, Evaluating Large Language Models Trained on Code](https://arxiv.org/abs/2107.03374) | ⚑ | 24 | 8 | [✓ PDF](../01-llm-fundamentals/sources/chen-2021-evaluating-large-language-models-trained.pdf) |
| [Schulman 2017, Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347) | ⚑ | 24 | 4 | [✓ PDF](sources/schulman-2017-proximal-policy-optimization-algorithms.pdf) |
| [Shao 2024, DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Lan](https://arxiv.org/abs/2402.03300) | ⚑ | 23 | 2 | [✓ PDF](sources/shao-2024-deepseekmath.pdf) |
| [Cobbe 2021, Training Verifiers to Solve Math Word Problems](https://arxiv.org/abs/2110.14168) | ⚑ | 21 | 5 | [✓ PDF](../01-llm-fundamentals/sources/cobbe-2021-training-verifiers-solve-math-word.pdf) |
| [Touvron 2023, Llama 2: Open Foundation and Fine-Tuned Chat Models](https://arxiv.org/abs/2307.09288) | ⚑ | 20 | 7 | [✓ PDF](../01-llm-fundamentals/sources/touvron-2023-llama-2.pdf) |
| [Kwon 2023, Efficient Memory Management for Large Language Model Serving with Page](https://arxiv.org/abs/2309.06180) | SOSP 2023 | 20 | 2 | [✓ PDF](sources/kwon-2023-efficient-memory-management-large-language.pdf) |
| [Wei 2021, Finetuned Language Models Are Zero-Shot Learners](https://arxiv.org/abs/2109.01652) | ICLR 2022 | 19 | 4 | [✓ PDF](sources/wei-2021-finetuned-language-models-zero-shot.pdf) |
| [Rafailov 2023, Direct Preference Optimization: Your Language Model is Secretly a Rewa](https://doi.org/10.52202/075280-2338) | NeurIPS 2023 | 19 | 4 | [✓ PDF](sources/rafailov-2023-dpo.pdf) |
| [Lightman 2023, Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) | ICLR 2024 | 18 | 2 | [✓ PDF](sources/lightman-2023-let-s-verify-step-step.pdf) |
| [Hu 2021, LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) | ICLR 2022 | 16 | 6 | [✓ PDF](../01-llm-fundamentals/sources/hu-2021-lora.pdf) |
| [Vaswani 2017, Attention Is All You Need](https://arxiv.org/abs/1706.03762) | NIPS 2017 | 16 | 5 | [✓ PDF](../01-llm-fundamentals/sources/vaswani-2017-attention-all-you-need.pdf) |
| [Clark 2018, Think you have Solved Question Answering? Try ARC, the AI2 Reasoning C](https://arxiv.org/abs/1803.05457) | ⚑ | 16 | 4 | [✓ PDF](../01-llm-fundamentals/sources/clark-2018-think-you-have-solved-question.pdf) |
| [Stiennon 2020, Learning to summarize from human feedback](https://arxiv.org/abs/2009.01325) | ⚑ | 15 | 4 | [✓ PDF](sources/stiennon-2020-learning-summarize-human-feedback.pdf) |
| [Xu 2023, WizardLM: Empowering large pre-trained language models to follow compl](https://arxiv.org/abs/2304.12244) | ICLR 2024 | 14 | 5 | [✓ PDF](sources/xu-2023-wizardlm.pdf) |
| [Zellers 2019, HellaSwag: Can a Machine Really Finish Your Sentence?](https://doi.org/10.18653/v1/p19-1472) | ACL (1) 2019 | 14 | 3 | [✓ PDF](../01-llm-fundamentals/sources/zellers-2019-hellaswag.pdf) |
| [Wang 2022, Self-Consistency Improves Chain of Thought Reasoning in Language Model](https://arxiv.org/abs/2203.11171) | ICLR 2023 | 13 | 5 | [✓ PDF](sources/wang-2022-self-consistency-improves-chain-thought.pdf) |
| [Bai 2022, Training a Helpful and Harmless Assistant with Reinforcement Learning ](https://arxiv.org/abs/2204.05862) | ⚑ | 13 | 2 | [✓ PDF](../01-llm-fundamentals/sources/bai-2022-training-helpful-harmless-assistant-reinforcement.pdf) |
| [Raffel 2019, Exploring the Limits of Transfer Learning with a Unified Text-to-Text ](https://arxiv.org/abs/1910.10683) | J. Mach. Learn. Res. 2020 | 12 | 6 | [✓ PDF](../01-llm-fundamentals/sources/raffel-2019-exploring-limits-transfer-learning-unified.pdf) |
| [Loshchilov 2017, Decoupled Weight Decay Regularization](https://arxiv.org/abs/1711.05101) | ICLR (Poster) 2019 | 12 | 3 | [✓ PDF](../01-llm-fundamentals/sources/loshchilov-2017-decoupled-weight-decay-regularization.pdf) |
| [Ziegler 2019, Fine-Tuning Language Models from Human Preferences](https://arxiv.org/abs/1909.08593) | ⚑ | 12 | 2 | [✓ PDF](sources/ziegler-2019-fine-tuning-language-models-human.pdf) |
| [Wang 2023, Self-Instruct: Aligning Language Models with Self-Generated Instructio](https://doi.org/10.18653/v1/2023.acl-long.754) | ACL (1) 2023 | 12 | 2 | [✓ PDF](sources/wang-2023-self-instruct.pdf) |
| [Sanh 2021, Multitask Prompted Training Enables Zero-Shot Task Generalization](https://arxiv.org/abs/2110.08207) | ICLR 2022 | 11 | 2 | [✓ PDF](sources/sanh-2021-multitask-prompted-training-enables-zero.pdf) |

50 more in [the citation report](../../scripts/papers/reports/citegraph-post-training.md).
<!-- citegraph:origins end -->

## AI Papers of the Week

Recent papers picked up by the weekly [DAIR](https://github.com/dair-ai/AI-Papers-of-the-Week) sync (`make papers`, then `/papers`). Newest first.

| | Paper | arXiv | Local | Notes |
|---|---|---|---|---|
| | GLM-5 Team, *GLM-5* (2026): async agentic RL with rollout-logprob behaviour policy and double-sided ratio mask; 10k+ SWE environments; SWE-bench Verified 77.8 but SWE-rebench 42.1 | [2602.15763](https://arxiv.org/abs/2602.15763) | ✓ [glm-5-team-2026-glm-5.pdf](sources/glm-5-team-2026-glm-5.pdf) | [01](notes/01-rl-foundations.md#scaling-actors-and-learners), [05](notes/05-post-training-for-agents.md#data-and-environment--algorithm) |
| ★ | Yuksekgonul et al., *Learning to Discover at Test Time* (TTT-Discover) (2026): RL on one problem at test time with an entropic objective and PUCT reuse; TriMul H100 kernel 1,203 µs vs 1,986 (expected-reward RL) and 5,353 (best-of-N) | [2601.16175](https://arxiv.org/abs/2601.16175) | ✓ [ttt-discover-learning-discover-test-2026.pdf](sources/ttt-discover-learning-discover-test-2026.pdf) | [05](notes/05-post-training-for-agents.md#test-time-search-instead-of-training) |
| | Prime Intellect, *INTELLECT-3* (2025): 106B-A12B MoE trained with async RL up to 8 policy versions stale; masking ratios outside [0.5, 5] is what keeps it from crashing | [2512.16144](https://arxiv.org/abs/2512.16144) | ✓ [intellect-3-2025.pdf](sources/intellect-3-2025.pdf) | [01](notes/01-rl-foundations.md#scaling-actors-and-learners), [05](notes/05-post-training-for-agents.md#data-and-environment--algorithm) |
| ★ | MacDiarmid et al., *Natural Emergent Misalignment from Reward Hacking in Production RL* (2025): learning to hack coding rewards generalizes to 33.7% misalignment and 12% sabotage; inoculation prompting cuts it 75–90% | [2511.18397](https://arxiv.org/abs/2511.18397) | ✓ [natural-emergent-misalignment-reward-hacking-2025.pdf](sources/natural-emergent-misalignment-reward-hacking-2025.pdf) | [05](notes/05-post-training-for-agents.md#practical-pitfalls) |
| | Liang et al., *Machine Bullshit* (2025): RLHF raises the Bullshit Index from 0.379 to 0.665; Llama-3-8B claims unknown product features 84.5% of the time vs 20.9% before | [2507.07484](https://arxiv.org/abs/2507.07484) | ✓ [machine-bullshit-2025.pdf](sources/machine-bullshit-2025.pdf) | [02](notes/02-rlhf-pipeline.md#reward-hacking) |
| | Wang et al., *Persona Features Control Emergent Misalignment* (2025): subtly wrong SFT data gives about 60% misalignment on GPT-4o; one SAE "toxic persona" latent predicts it, and 35 steps of clean data reverse it | [2506.19823](https://arxiv.org/abs/2506.19823) | ✓ [emergent-misalignment-2025.pdf](sources/emergent-misalignment-2025.pdf) | [05](notes/05-post-training-for-agents.md#practical-pitfalls) |
| | Xiaomi LLM-Core, *MiMo-7B* (2025): a reasoning-dense pretrain (32.9% AIME24 base) plus RL reaches 68.2% AIME24; drops KL; base model hacks the math reward | [2505.07608](https://arxiv.org/abs/2505.07608) | ✓ [mimo-7b-2025.pdf](sources/mimo-7b-2025.pdf) | [02](notes/02-rlhf-pipeline.md#overoptimization), [03](notes/03-preference-optimization.md#the-deepseek-r1-story) |
| ★ | Ren et al., *DeepSeek-Prover-V2* (2025): GRPO with a Lean verifier reward, 88.9% pass@8192 miniF2F-test; v2 retracted 13 PutnamBench solves that came from a Lean `apply?` bug | [2504.21801](https://arxiv.org/abs/2504.21801) | ✓ [ren-2025-deepseek-prover-v2.pdf](sources/ren-2025-deepseek-prover-v2.pdf) | [03](notes/03-preference-optimization.md#grpo--group-relative-policy-optimization) |
| ★ | Hu et al., *Open-Reasoner-Zero* (2025): vanilla PPO (λ=γ=1) with no KL matches R1-Zero-Qwen-32B (48.1 vs 47.0 AIME24) in about a tenth of the steps | [2503.24290](https://arxiv.org/abs/2503.24290) | ✓ [open-reasoner-zero-2025.pdf](sources/open-reasoner-zero-2025.pdf) | [02](notes/02-rlhf-pipeline.md#overoptimization), [03](notes/03-preference-optimization.md#the-deepseek-r1-story) |
| ★ | DeepSeek-AI, *DeepSeek-R1* (2025): R1-Zero AIME24 15.6→71.0% from pure RL; distillation beats RL on a 32B model (72.6 vs 47.0); KL is a loss term, not reward shaping | [2501.12948](https://arxiv.org/abs/2501.12948) | ✓ [deepseek-r1-2025.pdf](sources/deepseek-r1-2025.pdf) | [03](notes/03-preference-optimization.md#the-deepseek-r1-story), [02](notes/02-rlhf-pipeline.md#overoptimization) |
| | Kimi Team, *Kimi k1.5* (2025): long-context RL with mirror-descent regularization toward the previous iterate; 77.5 AIME24; long2short keeps 60.8% at 3,272 tokens | [2501.12599](https://arxiv.org/abs/2501.12599) | ✓ [scaling-rl-llms-2025.pdf](sources/scaling-rl-llms-2025.pdf) | [03](notes/03-preference-optimization.md#the-deepseek-r1-story), [02](notes/02-rlhf-pipeline.md#overoptimization) |
| | Akyürek et al., *The Surprising Effectiveness of Test-Time Training for Few-Shot Learning* (2024): per-task LoRA at test time takes an 8B model from 18.3% to 47.1% on ARC validation | [2411.07279](https://arxiv.org/abs/2411.07279) | ✓ [surprising-effectiveness-test-time-training-2024.pdf](sources/surprising-effectiveness-test-time-training-2024.pdf) | [05](notes/05-post-training-for-agents.md#test-time-search-instead-of-training) |
| | McAleese et al., *LLM Critics Help Catch LLM Bugs* (CriticGPT) (2024): RLHF-trained critic preferred over human critiques 63% of the time on real bugs; raters miss errors that reward labels then carry | [2407.00215](https://arxiv.org/abs/2407.00215) | ✓ [criticgpt-2024.pdf](sources/criticgpt-2024.pdf) | [02](notes/02-rlhf-pipeline.md#stage-2--reward-model-training) |
| | Sun et al., *Aligning Large Multimodal Models with Factually Augmented RLHF* (LLaVA-RLHF) (2023): reward model rewards verbosity; Fact-RLHF fixes the benchmark score but hallucination rate stays flat vs SFT+ | [2309.14525](https://arxiv.org/abs/2309.14525) | ✓ [sun-2023-aligning-large-multimodal-models-factually.pdf](sources/sun-2023-aligning-large-multimodal-models-factually.pdf) | [02](notes/02-rlhf-pipeline.md#reward-hacking) |

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

- Papers and textbooks above are primary. The Winder, Huyen, Iusztin & Labonne, Raschka, Koenigstein, Albada and Raieli & Iuculano chapters are purchased copies; keep them local and do not redistribute.
- The 2024 books (*LLM Engineer's Handbook*, Raschka) predate GRPO's spread, LoRA Without Regret and online-DPO results. The notes flag where their advice is dated. Koenigstein is an Early Release and its claims about GSPO are the GSPO authors' own. Author names for Koenigstein and Albada follow the repo convention; the chapter PDFs don't print them.
- 05 is a synthesis of one book chapter (Li, Apache-2.0). Its numbers (e.g. "0% wins at 1k episodes, 100% at 10k" in the lab) are reproduced locally; other figures rest on the book.
- 01 started life as a low-confidence Notion export. It has been cleaned and translated, but bare-URL claims in its MARL section were not re-verified.
