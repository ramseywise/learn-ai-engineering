---
origin: notion-export
confidence: medium
cleaned: 2026-07-25
sources:
  - Sutton & Barto, "Reinforcement Learning: An Introduction" (2020)
  - https://arxiv.org/abs/2203.02155 (InstructGPT)
  - https://arxiv.org/abs/2305.18290 (DPO)
  - https://cdn.openai.com/WebGPT.pdf (WebGPT)
---

# Reinforcement Learning for LLMs

This note covers RL foundations as they apply to LLM alignment and agentic systems.
Three sections:

1. [RL Foundations](#1-rl-foundations) — MDP, agent/environment, exploration vs. exploitation
2. [Multi-Agent RL (MARL)](#2-multi-agent-rl-marl) — CTDE, MADDPG, QMIX — for agent coordination
3. [RL in RAG](#3-rl-in-rag) — query rewriting, retrieval policy, tool use, Self-RAG

**For RLHF pipeline depth** (SFT → reward model → PPO, Bradley-Terry, reward hacking):
see [05-RL/rlhf-pipeline.md](../05-RL/rlhf-pipeline.md)

**For algorithm comparison** (PPO vs DPO vs GRPO vs KTO/ORPO):
see [05-RL/preference-optimization.md](../05-RL/preference-optimization.md)

---

## 1. RL Foundations

Unlike supervised learning (trained on a labeled answer key) or unsupervised learning
(finds patterns in unlabeled data), RL relies on **trial and error**. An agent learns
to make decisions by interacting with an unknown environment, maximizing cumulative
reward over time.

### Markov Decision Process (MDP)

The mathematical foundation of RL. Formally: a tuple `(S, A, P, R, γ)` where:

- **S** — state space: the set of all situations the agent can observe
- **A** — action space: the set of all decisions the agent can make
- **P(s'|s, a)** — transition function: probability of reaching state s' after taking
  action a in state s
- **R(s, a)** — reward function: scalar feedback received after taking action a in state s
- **γ** — discount factor (0 ≤ γ ≤ 1): how much to weight future vs. immediate rewards

**Markov property:** The next state depends only on the current state and action, not
on the full history. This is the key simplifying assumption that makes RL tractable.

### Core components

- **Agent:** The learner and decision-maker
- **Environment:** The world the agent interacts with
- **State:** The agent's current observation of the environment
- **Action:** The decision the agent makes given the state
- **Reward:** Scalar feedback (positive or negative) after taking an action
- **Policy (π):** The strategy mapping states to actions — the thing being optimized.
  Policies can be deterministic (`π(s) → a`) or stochastic (`π(a|s) → [0,1]`)

### Algorithm families

**Value-based:** The agent estimates the expected long-term return (the "value") of
states or state-action pairs, then acts greedily. Examples: Q-Learning, DQN (Deep Q-Networks).

**Policy-based:** Directly optimize the policy without an explicit value function.
Policy gradient methods compute `∇E[R]` and update `π_θ` toward higher-reward trajectories.

**Actor-Critic:** Hybrid approach. An "actor" decides actions (policy); a "critic"
estimates value (how good the state is), providing a lower-variance signal for updating
the actor. PPO is the dominant actor-critic algorithm today [1].

**Model-free vs. model-based:** Model-free agents learn purely from experience.
Model-based agents learn the transition function P(s'|s,a) and use it for planning —
more sample-efficient but harder to learn accurate models.

### Exploration vs. exploitation

A fundamental tension: should the agent **exploit** the best action it knows (maximize
immediate reward) or **explore** new actions that might yield higher rewards in the long
run? Strategies:
- **ε-greedy:** With probability ε, take a random action; otherwise exploit
- **UCB (Upper Confidence Bound):** Choose actions with high uncertainty to reduce
  uncertainty faster
- **Entropy regularization (used in SAC, GRPO):** Add an entropy bonus to the reward to
  encourage diverse action distributions

In LLM contexts, temperature sampling at inference time is the primary exploration
mechanism during data collection.

### RL applied to LLMs

LLMs are trained using RL primarily at two stages:

1. **RLHF alignment (post-pretraining):** The LLM is the policy; each token is an
   action; the reward model scores completed responses. See [05-RL/rlhf-pipeline.md](../05-RL/rlhf-pipeline.md).

2. **Agentic RL (tool use, retrieval, reasoning):** The LLM takes multi-step actions
   in an environment (web browser, code executor, knowledge base). Rewards are task
   completion signals. This section and the next cover this use case.

---

## 2. Multi-Agent RL (MARL)

MARL applies RL to systems with multiple interacting agents — each observing the
environment and making decisions, with each agent's actions affecting other agents'
environments.

**When to use MARL vs. single-agent RL:**
- MARL: every agent's action influences others — leads to state changes that affect the
  joint reward. Trading systems, multi-robot coordination, multi-agent LLM pipelines.
- Single-agent RL in RAG: the environment is the RAG system + user feedback. One agent,
  multiple actions (rewrite, retrieve, answer). See Section 3.

### The non-stationarity problem

In a multi-agent system, as each agent updates its policy, the environment appears to
shift from every other agent's perspective — other agents are changing, which changes
the effective transition function. This makes standard single-agent RL unstable.

**Centralized Training with Decentralized Execution (CTDE)** is the dominant framework
for addressing this. During training, the critic gets global state information (what all
agents are doing). At deployment, each agent's actor uses only local observations —
no central server required.

CTDE stabilizes training because: the critic always has the full picture and can correctly
attribute credit or blame to each agent's actions. The learned knowledge is baked into
the actor weights.

### Algorithm families

**Value Decomposition Methods:** Decompose the joint value function into individual
agent value functions that sum (or combine) to give the global Q-value.
- **VDN (Value Decomposition Networks):** `Q_total = Σ Q_i` — simple sum; assumes
  agent rewards are independent
- **QMIX:** Uses a monotonic mixing network to combine agent Q-values; the global Q-value
  is a non-linear monotone function of individual Q-values. Handles coordination without
  requiring full independence.

**Central-Critic Methods (Actor-Critic under CTDE):**
- **MADDPG (Multi-Agent Deep Deterministic Policy Gradient):** Each agent has its own
  actor (local observations) and critic (global state + all agents' actions).
  Deterministic policy gradients for continuous action spaces.
- **COMA (Counterfactual Multi-Agent):** Addresses the credit assignment problem —
  "how much did my action contribute to the joint reward?" Uses a counterfactual baseline
  to isolate each agent's marginal contribution.
- **MAPPO (Multi-Agent PPO):** PPO extended to CTDE. Each agent uses PPO's clipped
  surrogate objective; the critic receives global state. Empirically strong for
  cooperative tasks.

**Competitive methods:**
- **Nash-Q:** Generalizes Q-learning to Nash equilibria in zero-sum games
- **Self-play:** Agents are trained against copies of themselves — used for games
  (AlphaGo, AlphaStar) and increasingly for LLM red-teaming

### MARL challenges

- **Non-stationarity:** Partially addressed by CTDE; not fully solved
- **Credit assignment:** Hard to attribute joint outcomes to individual agent actions
- **Scalability:** Coordination complexity grows with agent count; most MARL algorithms
  struggle beyond ~10-20 agents
- **Sample efficiency:** Multi-agent interaction space is large; collecting useful
  experiences requires many environment steps
- **Evaluation:** Standard single-agent metrics don't transfer; need to measure emergent
  coordination quality

### Multi-Agent Path Finding (MAPF)

A specialized MARL subproblem: planning collision-free routes for multiple agents from
start to goal. Used in warehouse robotics, autonomous vehicle coordination. Requires
exact collision avoidance — standard RL exploration is inadequate, so MAPF often uses
hybrid approaches (classical search + RL for local decisions).

---

## 3. RL in RAG

RAG can be modeled as a sequential decision process with multiple decision points:

- When to retrieve (or skip retrieval)?
- How to rewrite the query for better retrieval?
- Which retrieved evidence to use?
- When to stop and generate an answer?

RL provides a principled framework for learning policies over these decisions, optimizing
for end-to-end task quality rather than intermediate retrieval metrics.

### Decision points and reward signals

| Sub-task | Action space | Reward signal |
|----------|-------------|---------------|
| Query rewriting | Rewritten query variants | Retrieval quality (NDCG, recall@k) |
| Evidence selection | Rank/rerank retrieved passages | Answer F1, faithfulness |
| Continue-or-stop retrieval | Stop / continue (multi-hop) | Accuracy minus latency cost |
| Tool use | Search / click / synthesize | Human preference or task completion |
| End-to-end | Full pipeline | QA F1 or human evaluation |

### Pattern 1 — Online RL over retrieval and tool actions

The model interacts with a retrieval or browsing environment via discrete actions,
trained with behavior cloning (imitation from demonstrations) then optimized against a
reward model built from human preferences.

**WebGPT** (OpenAI, 2021) is the canonical example: a model trained to use a web browser
via search, click, and quote actions. Reward model trained on human comparisons of
web-browsing-augmented vs. direct LLM answers. The RL loop: generate action sequence →
execute in browser → collect human preference over final answer → update policy.

This is structurally identical to RLHF except the "response" is an action sequence
rather than text, and the environment is the web browser rather than the generation step.

### Pattern 2 — RL module for specific sub-task

Instead of end-to-end RL, train a specialized RL module for one decision (e.g., query
rewriting). The rewriting strategy is optimized based on whether the rewrite improves
final retrieval/response quality — not supervised on "what the ideal rewrite looks like."

**Advantage:** Decomposes the problem. Each module has a clear reward signal. Simpler
to train and debug than full-pipeline RL.

**Disadvantage:** Sub-optimal if sub-task rewards don't align with end-task quality.
Query recall improvement doesn't always translate to answer quality improvement.

### Pattern 3 — Self-RAG: adaptive retrieval without classic RL

Self-RAG (Asai et al., 2023) trains a model to retrieve on demand and emit **reflection
tokens** — special tokens that critique evidence and generation quality at inference time.
Not classic RL (no online rollouts, no reward model), but operationalizes a *policy over
retrieval decisions* learned during training.

Key reflection token types:
- `[Retrieve]` — should I retrieve?
- `[IsREL]` — is this passage relevant to the query?
- `[IsSUP]` — is the claim supported by the passage?
- `[IsUSE]` — is the generated response useful?

These tokens allow inference-time controllability: retrieval can be turned off for
factual queries the model is confident about and turned on for uncertain claims. This
substantially improves groundedness and citation accuracy over fixed-retrieval RAG.

### RL vs. DPO for RAG optimization

Standard RLHF/PPO requires online rollouts — expensive at RAG pipeline scale (each
rollout involves retrieval). **DPO** is increasingly used as the optimizer for preference-
tuned retrieval decisions: collect (prompt, good-retrieval-outcome, bad-retrieval-outcome)
triples, then train with DPO's offline objective.

See [05-RL/preference-optimization.md](../05-RL/preference-optimization.md) for DPO details.

### Challenges in RL for RAG

- **Reward sparsity:** End-task reward (final answer quality) is a single signal at the
  end of a multi-step trajectory. Intermediate retrieval actions have no direct reward.
  Partial mitigation: reward shaping (intermediate retrieval quality scores).
- **Scalability:** Each RL training step requires retrieval — slow and expensive.
  Offline methods (Self-RAG, DPO over retrieval decisions) are faster but lose online
  adaptation.
- **Evaluation difficulty:** RAG quality is multi-dimensional (retrieval quality +
  faithfulness + answer quality + latency). Single reward scalars are imperfect proxies.
- **Reward hacking:** Model learns to retrieve passages that trigger high reward model
  scores without genuine factual grounding.
- **Distribution shift:** The retrieval corpus and user query distribution change over
  time; policies trained on historical data degrade.

---

## RLHF and DPO — pointer

The RLHF pipeline (SFT → reward model → PPO) and preference optimization algorithms
(DPO, GRPO, KTO, ORPO) are covered in depth in the 05-RL pillar:

- **RLHF pipeline:** [05-RL/rlhf-pipeline.md](../05-RL/rlhf-pipeline.md) — three stages,
  Bradley-Terry model, KL penalty, reward hacking failure modes
- **Algorithm comparison:** [05-RL/preference-optimization.md](../05-RL/preference-optimization.md)
  — PPO vs DPO vs GRPO vs KTO/IPO/ORPO, decision framework, DeepSeek-R1 story
- **Constitutional AI / RLAIF:** [05-RL/constitutional-ai.md](../05-RL/constitutional-ai.md)
  — AI-generated feedback, critique-revision loop, scaling alignment

---

## Tooling

**Python RL frameworks:**
- **HuggingFace TRL** — RLHF, DPO, GRPO training on top of HuggingFace models.
  The standard library for preference optimization. [docs](https://huggingface.co/docs/trl/)
- **OpenRLHF** — distributed RLHF training; supports PPO at large scale

**MARL simulators and frameworks:**
- **Ray RLlib** — general-purpose RL with multi-agent support
- **PyMARL** — MARL-specific: QMIX, COMA, VDN implementations
- **PettingZoo** — multi-agent Gymnasium-compatible environments

---

## Cross-links

- **Upstream:** [05-RL/README.md](../05-RL/README.md) — full topic map and resource
  index for the RL & alignment pillar
- **Downstream:** [03-agentic-foundations/README.md](../03-agentic-foundations/README.md)
  — RL-trained agents (ReAct, Reflexion), multi-agent coordination
- **RLHF depth:** [05-RL/rlhf-pipeline.md](../05-RL/rlhf-pipeline.md)
- **Algorithm depth:** [05-RL/preference-optimization.md](../05-RL/preference-optimization.md)
- **Constitutional AI:** [05-RL/constitutional-ai.md](../05-RL/constitutional-ai.md)
