# 05 — RL & Alignment

> Depth layer. Summary: [interviewing/guides/2-llm-fundamentals](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/2-llm-fundamentals/00-overview.md)
> Position: fifth pillar of [generative-ai](../README.md). Presumes [01-llm-fundamentals](../01-llm-fundamentals/README.md); feeds [03-agentic-foundations](../03-agentic-foundations/README.md) and [ai-engineering/06-eval](../../ai-engineering/06-eval/README.md).

---

## What it is

Reinforcement learning is how a pretrained model becomes an assistant. It is also, more and more, how agents learn to plan, call tools and recover from mistakes. This pillar starts with the RL vocabulary (MDPs, value and policy methods, exploration) and then follows it into post-training: the three-stage RLHF pipeline, the preference-optimization family that replaced or simplified it (PPO → DPO → GRPO), Constitutional AI's swap of human labels for AI feedback, and post-training aimed at multi-turn, tool-using agents.

The thread through all five notes is that **the reward signal is the product**. Where it comes from (humans, a reward model, a constitution, a verifier, an environment), how dense it is and how easy it is to game decides more than the choice of optimizer.

---

## Start here

1. [01 — RL foundations](notes/01-rl-foundations.md), §1 only, for the MDP vocabulary.
2. [02 — RLHF pipeline](notes/02-rlhf-pipeline.md): SFT → reward model → PPO, and why each stage exists.
3. [03 — Preference optimization](notes/03-preference-optimization.md): the decision framework table.
4. [05 — Post-training for agents](notes/05-post-training-for-agents.md): "SFT memorizes, RL generalizes", then run the [Q-learning lab](practice/01-q-learning-treasure-hunt/).

---

## Layout

```
05-RL/
├── README.md
├── references.md           every source, mapped to notes; open gaps
├── notes/                  01–05, read in order
├── practice/
│   └── 01-q-learning-treasure-hunt/   tabular Q-learning lab (offline, numpy)
└── sources/                local PDFs: Sutton & Barto, Winder ch. 1–11, bandits, RLHF/DPO/PPO papers
    ├── images/             figures from Li, AI Agents in Depth ch. 8
    ├── misfiled/           non-RL papers from the old dump, kept for their owning pillar
    └── winder-reinforcement-learning/
```

---

## Syllabus

| # | Note | Covers |
|---|---|---|
| 01 | [RL foundations](notes/01-rl-foundations.md) | MDP tuple (S, A, P, R, γ); value-based, policy-gradient and actor-critic families; exploration vs exploitation; how RL maps onto LLMs; multi-agent RL (CTDE, VDN/QMIX, MADDPG, MAPPO); RL in RAG (WebGPT, RL over retrieval actions, Self-RAG reflection tokens) |
| 02 | [RLHF pipeline](notes/02-rlhf-pipeline.md) | SFT, reward-model training with the Bradley-Terry loss, PPO with a KL penalty; reward hacking, overoptimization, alignment tax; practical considerations |
| 03 | [Preference optimization](notes/03-preference-optimization.md) | PPO, DPO (no reward model, no rollouts), GRPO (no critic, group-relative advantage); KTO, IPO, ORPO; decision framework; the DeepSeek-R1 story |
| 04 | [Constitutional AI and RLAIF](notes/04-constitutional-ai.md) | The constitution; SL-CAI critique → revision; RLAIF preference labels; red-teaming; self-improvement and scaling; comparison with RLHF |
| 05 | [Post-training for agents](notes/05-post-training-for-agents.md) | The three stages; SFT memorizes vs RL generalizes; when to pick SFT or RL; data and environment over algorithm; reward design for multi-turn agents; RLVP; RL for tool calling (loss masking, ReTool, DAPO); on-policy and self-distillation; pitfalls; labs; interview questions |

---

## Rules of thumb

| Rule | Note |
|---|---|
| Learn the MDP words first: state, action, reward, policy, return, discount. Every later paper assumes them | 01 |
| The KL penalty to the SFT model is what keeps PPO from drifting into reward hacking. Remove it and the policy finds the reward model's blind spots | 02 |
| A reward model is a proxy. Past some point, more optimization against it lowers true quality (overoptimization) | 02 |
| Default to DPO when you have preference pairs and no verifier. Use GRPO/PPO when you can score outputs online (code that runs, math that checks) | 03 |
| Constitutional AI swaps human harmlessness labels for AI critiques guided by written principles. The principles become the thing you audit | 04 |
| Good SFT data often removes the need for RL. Data decides how far you can go; RL decides how much higher | 05 |
| SFT memorizes the demonstrations; RL generalizes to held-out scenarios. Use SFT for format, RL for behaviour under distribution shift | 05 |
| Reward the outcome and penalize verifiable process violations (RLVP). Do not reward a lucky path that broke a constraint | 05 |
| Mask tool outputs out of the loss when training tool-calling agents. The model should learn to call tools, not to predict their output | 05 |

---

## Resource map

**Related notes**

- [generative-ai/01-llm-fundamentals](../01-llm-fundamentals/README.md): pretraining and SFT, the stage before this pillar.
- [generative-ai/03-agentic-foundations](../03-agentic-foundations/README.md): RL-trained agent patterns (ReAct, Reflexion) and multi-agent coordination.
- [generative-ai/07-agentic-applications](../07-agentic-applications/README.md): the deep-research-bot has an RL-for-deep-research notebook.
- [ai-engineering/06-eval](../../ai-engineering/06-eval/README.md): environments as training grounds, trajectory scoring, preference annotation.
- [ai-engineering/04-loop-engineering](../../ai-engineering/04-loop-engineering/README.md): failure modes and guardrails, the runtime side of reward hacking.

**Books and courses:** Sutton & Barto (★), Li *AI Agents in Depth* ch. 8 (★), Winder, Lattimore & Szepesvári, HF Deep RL Course, OpenAI Spinning Up. Full list with chapter → note mapping in [references.md](references.md).

**Practice**

| Lab | What it shows | Run |
|---|---|---|
| [01-q-learning-treasure-hunt](practice/01-q-learning-treasure-hunt/) | Tabular Q-learning on a text adventure with hidden rules: 0% wins at 1k episodes, 100% at 10k | offline; needs `numpy`. `python test_rl_learning.py --episodes 1000 10000` (~10 s) |

**Readings:** local PDFs in [sources/](sources/), indexed with arXiv ids in [references.md](references.md#core-papers). Open gaps (TRL notebook, reward-model architecture note) are in [references.md § Gaps](references.md#gaps).

**Interviewing guide:** [2-llm-fundamentals](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/2-llm-fundamentals/00-overview.md): RLHF, alignment and preference optimization compressed for interview prep.

**Previous:** [04-agentic-frameworks](../04-agentic-frameworks/README.md) · **Next:** [06-observability](../06-observability/README.md): once agents are trained and deployed, tracing and scoring close the feedback loop.
