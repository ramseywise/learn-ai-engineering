# 05 — RL & Alignment

> Depth layer. Summary: [interviewing/guides/2-llm-fundamentals](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/2-llm-fundamentals/00-overview.md)
> Position: fifth pillar of [generative-ai](../README.md). Presumes [01-llm-fundamentals](../01-llm-fundamentals/README.md); feeds [03-agentic-foundations](../03-agentic-foundations/README.md) and [ai-engineering/06-eval](../../ai-engineering/06-eval/README.md).

---

## What it is

Reinforcement learning is how a pretrained model becomes an assistant. It is also, more and more, how agents learn to plan, call tools and recover from mistakes. This pillar starts in plain language, moves to the RL vocabulary (MDPs, value and policy methods, exploration) and then follows RL through the LLM stack: RLHF, preference optimization, Constitutional AI and post-training for agents.

## Why it matters

The thread through all twelve chapters is that **the reward signal is the product**. Where it comes from (humans, a reward model, a constitution, a verifier, an environment), how dense it is and how easy it is to game decides more than the choice of optimizer. If you build, buy or evaluate a trained model, this is the part that tells you what the model was actually asked to do.

## The story

A small agent in a treasure hunt knows nothing and is told only a score. It wins 0 of 100 games after 1,000 episodes of practice and 100 of 100 after 10,000, because the score was a good one. Put a language model in the agent's seat and the same loop becomes RLHF: humans supply the score, a reward model scales it, PPO or DPO optimizes it, and a KL penalty stops the model from hacking it. A written constitution can replace some of the humans. A verifier can replace the reward model, which is how DeepSeek-R1 learned to reason at scale. Agents then add long horizons, real tools and environments that cost more to build than the training run, and every step still comes back to one question: what is the score, and what happens when the model finds its loophole?

---

## Reading order

New to RL? Start at 00. It assumes no notation and no data-science pillar. If you already know MDPs, TD and PPO, skim 01 and start at 02.

| # | Chapter | Covers |
|---|---|---|
| 00 | [RL in plain language](notes/00-rl-in-plain-language.md) | Agent, reward, exploration, value and policy in plain words with small runnable examples; why this matters for LLMs |
| 01 | [RL foundations](notes/01-rl-foundations.md) | MDP tuple; Bellman and TD; DQN and offline RL; policy gradients to the PPO clip; maximum entropy; exploration; how RL maps onto LLMs |
| 02 | [RLHF pipeline](notes/02-rlhf-pipeline.md) | SFT and SFT in practice; reward-model training; PPO with a KL penalty; reward hacking and overoptimization; alignment tax |
| 03 | [Preference optimization](notes/03-preference-optimization.md) | PPO, DPO, GRPO and GSPO; KTO, IPO, ORPO, SimPO and self-play; the decision framework |
| 04 | [Constitutional AI and RLAIF](notes/04-constitutional-ai.md) | The constitution; critique and revision; RLAIF labels; red-teaming; self-improvement and scaling |
| 05 | [Post-training for agents](notes/05-post-training-for-agents.md) | The three stages; SFT memorizes, RL generalizes; LLMs inside classic RL; learning without weights; when to pick SFT or RL |
| 06 | [Data and environments](notes/06-data-and-environments.md) | Environments as practice fields; simulators; data quality; dataset engineering; preference data at practitioner scale |
| 07 | [Reward design and tool calling](notes/07-reward-design-and-tool-calling.md) | Multi-turn rewards; judges as rewards; RLVP; RL for tool calling; dense signals and distillation |
| 08 | [Reasoning RL and DeepSeek-R1](notes/08-reasoning-rl-deepseek-r1.md) | The R1 story; how little data and reward reasoning needs |
| 09 | [Test-time search and training](notes/09-test-time-search-and-training.md) | MCTS, AB-MCTS, search instead of training; measuring the selection bottleneck |
| 10 | [Engineering RL systems](notes/10-engineering-rl-systems.md) | Imitation and inverse RL; hierarchy and curricula; engineering an RL problem; scaling; running RL in production; what has dated |
| 11 | [Multi-agent and RAG RL](notes/11-multi-agent-and-rag-rl.md) | CTDE, VDN/QMIX, MADDPG, MAPPO; path finding; RL over retrieval and tool actions; Self-RAG |

Short route for a working engineer: 02, 03, 05, 07, then run the [Q-learning lab](practice/01-q-learning-treasure-hunt/).

---

## Layout

```
05-RL/
├── README.md
├── references.md           every source, mapped to notes; open gaps
├── notes/                  00–11, read in order
├── slides/                 deck.yaml and rl-and-alignment.pptx
├── practice/
│   └── 01-q-learning-treasure-hunt/   tabular Q-learning lab (offline, numpy)
└── sources/                local PDFs: Sutton & Barto, Winder ch. 1–11, bandits, RLHF/DPO/PPO papers
    ├── images/             figures from Li ch. 8, Huyen ch. 7–8, Koenigstein ch. 3, Albada ch. 7, Winder
    ├── huyen-ai-engineering/, ai-agents-definitive-guide/, building-applications-with-ai-agents/,
    │   building-ai-agents-llms-rag-kgs/   purchased chapter PDFs (see references.md § Books)
    ├── misfiled/           non-RL papers from the old dump, kept for their owning pillar
    └── winder-reinforcement-learning/
```

---

## Rules of thumb

| Rule | Note |
|---|---|
| Learn the words first: agent, state, action, reward, policy, value, exploration. Every later paper assumes them | 00, 01 |
| The KL penalty to the SFT model is what keeps PPO from drifting into reward hacking. Remove it and the policy finds the reward model's blind spots | 02 |
| A reward model is a proxy. Past some point, more optimization against it lowers true quality (overoptimization) | 02 |
| Default to DPO when you have preference pairs and no verifier. Use GRPO/PPO when you can score outputs online (code that runs, math that checks) | 03 |
| Constitutional AI swaps human harmlessness labels for AI critiques guided by written principles. The principles become the thing you audit | 04 |
| Fine-tuning is for form, RAG is for facts. When in doubt, don't fine-tune: try prompts, retrieval and in-context learning (Reflexion, ExpeL) first | 02, 05 |
| Start fine-tuning with about 50 good examples. If they show no gain, fix the setup before buying more data | 06 |
| Apply LoRA to all linear layers, not only attention. For DPO, start at β = 0.1 (raise it if outputs turn wordy) with a learning rate about 100× below LoRA SFT's | 02, 03 |
| Gate a learned judge behind a verifiable check: correctness first, judge ranking second | 07 |
| Good SFT data often removes the need for RL. Data decides how far you can go; RL decides how much higher | 05, 06 |
| SFT memorizes the demonstrations; RL generalizes to held-out scenarios. Use SFT for format, RL for behaviour under distribution shift | 05 |
| Reward the outcome and penalize verifiable process violations (RLVP). Do not reward a lucky path that broke a constraint | 07 |
| Mask tool outputs out of the loss when training tool-calling agents. The model should learn to call tools, not to predict their output | 07 |
| Try search before training when pass@k already covers the task and a verifier exists. Train when you need the answer fast at one sample | 09 |
| Check a random policy and a simple baseline before training, and compare runs across many seeds: three seeds can put two identical agents far apart | 10 |

---

## Resource map

**Related notes**

- [generative-ai/01-llm-fundamentals](../01-llm-fundamentals/README.md): pretraining and SFT, the stage before this pillar.
- [generative-ai/03-agentic-foundations](../03-agentic-foundations/README.md): RL-trained agent patterns (ReAct, Reflexion) and multi-agent coordination.
- [generative-ai/07-agentic-applications](../07-agentic-applications/README.md): the deep-research-bot has an RL-for-deep-research notebook.
- [ai-engineering/06-eval](../../ai-engineering/06-eval/README.md): environments as training grounds, trajectory scoring, preference annotation.
- [ai-engineering/04-loop-engineering](../../ai-engineering/04-loop-engineering/README.md): failure modes and guardrails, the runtime side of reward hacking.

**Books and courses:** Sutton & Barto (★), Li *AI Agents in Depth* ch. 8 (★), Huyen *AI Engineering* ch. 7–8 (★), *LLM Engineer's Handbook* ch. 5–6 (★), Raschka ch. 6–7, Koenigstein ch. 3, Albada ch. 7, Raieli & Iuculano ch. 8, Winder, Lattimore & Szepesvári, HF Deep RL Course, OpenAI Spinning Up. Full list with chapter → note mapping in [references.md](references.md).

**Practice and slides**

Deck: [slides/rl-and-alignment.pptx](slides/rl-and-alignment.pptx), built from [slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=generative-ai/05-RL STRICT=1 PREVIEW=1`.

| Lab | What it shows | Run |
|---|---|---|
| [01-q-learning-treasure-hunt](practice/01-q-learning-treasure-hunt/) | Tabular Q-learning on a text adventure with hidden rules: 0% wins at 1k episodes, 100% at 10k | offline; from the lab folder, `uv run --no-project --with numpy python test_rl_learning.py --episodes 1000 10000` (~10 s) |

**Readings:** local PDFs in [sources/](sources/), indexed with arXiv ids in [references.md](references.md#core-papers). Open gaps (TRL notebook, reward-model architecture note) are in [references.md § Gaps](references.md#gaps).

**Interviewing guide:** [2-llm-fundamentals](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/2-llm-fundamentals/00-overview.md): RLHF, alignment and preference optimization compressed for interview prep.

**Previous:** [04-agentic-frameworks](../04-agentic-frameworks/README.md) · **Next:** [06-observability](../06-observability/README.md): once agents are trained and deployed, tracing and scoring close the feedback loop.
