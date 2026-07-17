---
origin: notion-export
confidence: low
sources:
  - https://www.nepjol.info/index.php/mujoei/article/view/91094
  - https://www.newline.co/@Dipen/top-10-realworld-applications-of-reinforcement-learning--a7df98a2
  - https://www.geeksforgeeks.org/machine-learning/what-is-markov-decision-process-mdp-and-its-relevance-to-reinforcement-learning/
cleaned: 2026-07-17
language: mixed zh/en — section headers translated, body partly untranslated
---

https://www.nepjol.info/index.php/mujoei/article/view/91094

https://www.newline.co/@Dipen/top-10-realworld-applications-of-reinforcement-learning--a7df98a2

Unlike *supervised learning* (which trains an AI using a "labeled" answer key) or *unsupervised learning* (which finds hidden patterns in unlabeled data), RL relies entirely on **trial and error**

an **artificial intelligence agent** learns to make decisions by interacting with an unknown environment. The ultimate goal of the agent is to maximize a cumulative reward over time

**How It Works: The Core Components** The mathematical foundation of RL is known as a **Markov Decision Process (MDP)**. It involves a continuous feedback loop consisting of the following key elements:

- **Agent:** The learner or decision-maker.
- **Environment:** The world or system the agent interacts with.
- **State:** The current situation the agent observes in the environment.
- **Action:** The move or decision made by the agent based on the state.
- **Reward:** The numerical feedback (positive or negative) the agent receives after taking an action.
- **Policy:** The underlying strategy or set of rules the agent develops to decide which action to take in any given situation.

https://www.geeksforgeeks.org/machine-learning/what-is-markov-decision-process-mdp-and-its-relevance-to-reinforcement-learning/

https://www.geeksforgeeks.org/machine-learning/types-of-reinforcement-learning/

https://toloka.ai/blog/proximal-policy-optimization/

**The Biggest Challenge: Exploration vs. Exploitation**

As the agent learns, it faces a fundamental dilemma: should it **exploit** the best actions it already knows to secure a guaranteed reward, or should it **explore** new, untested actions that might lead to a much bigger payoff in the long run? Striking the perfect balance is crucial. If an agent exploits too much, it might get stuck using a mediocre strategy. If it explores too much, it wastes time on irrelevant or dangerous actions

https://milvus.io/ai-quick-reference/why-is-balancing-exploration-and-exploitation-important-in-reinforcement-learning

important: https://www.mdpi.com/2079-9292/14/4/820

RL in LLM:

**Large Language Models (LLMs):** RL is heavily utilized to train modern AI assistants like ChatGPT. A technique called **Reinforcement Learning from Human Feedback (RLHF)** is used to align the AI's responses with human preferences, teaching the model to be helpful, honest, and harmless

https://www.digitalocean.com/community/tutorials/proximal-policy-optimization-implementation-applications

https://aws.amazon.com/blogs/machine-learning/fine-tune-large-language-models-with-reinforcement-learning-from-human-or-ai-feedback/

https://blog.darpanjain.com/reward-hacking/

frameworks use Deep Q-Networks to navigate massive data scales and real-time disruptions, such as equipment failure or order surges, to enhance supply chain agility. Experimental results across these platforms show significant improvements in processing efficiency and operational accuracy, reducing delays and costs through intelligent decision-making. 

**Multi-Agent Reinforcement Learning (MARL)**  — not for RAG, for agent planning and actions in complex environment

It combines the trial-and-error decision-making of reinforcement learning with the powerful pattern-recognition capabilities of deep neural networks

**1. How It Works**

In MARL, an "agent" is an independent software entity (like a virtual robot, an automated trader, or a self-driving car algorithm) that observes its surroundings and takes actions. 

- Through continuous interaction with their environment, agents learn by receiving **rewards or penalties** for their actions.
- Over time, they adjust their strategies to maximize their cumulative rewards, essentially learning from experience.

Reinforcement learning is a common approach to learning an optimal strategy for any problem. In this machine learning paradigm, an agent makes decisions and receives penalties/rewards, learning to optimize its actions with trial-and-error. Given the inherently competitive nature of the financial market, multiagent reinforcement learning, whereby multiple agents compete in a shared environment, offers a natural and exciting way to develop trading strategies.

https://blogs.mathworks.com/finance/2024/05/17/deep-learning-in-quantitative-finance-multiagent-reinforcement-learning-for-financial-trading/

*(missing diagram — not exported from Notion)*

how it works: In reinforcement learning, agents can be thought of as functions that take in some state, called an *observation*, and then output an *action*. Depending on how this action interacts with the *environment*, they will receive a *reward* for that action, and update their strategy depending on the strength of the reward. This strategy is called a *policy,* and is a function that maps observations to actions. This loop, which can be seen in figure 1, repeats to iteratively update the policy and maximize expected rewards.

1. definition: 

so need to define:

agent:

develop: https://se.mathworks.com/help/reinforcement-learning/ug/ppo-agents.html

define:  a. using the **Deep Network Designer**, 

       b. hard code 

environment: environment, which consists of an observation space, action space, and reward function.

observation space/ state: 

action space: agent’s possible actions/ decisions 

reward function:  several ones. example: Shared reward for all agents / Competitive reward for agents

1. Training 
    
    https://se.mathworks.com/help/reinforcement-learning/ref/rl.agent.rlqagent.train.html
    
    call the train function, specifying the length of each episode to be 2,597 steps, and there to be 2,500 episodes. 
    

**Approaches and algorithms.** 

file:///Users/yanzhang/Downloads/IJSET+-V2(1)-56-62.pdf

MARL approaches into: 

cooperative (e.g. centralized training with decentralized execution, or CTDE), 

competitive (Nash-Q, self-play)

hybrid methods. 

The three highlighted algorithms are MADDPG (an actor-critic method built on CTDE), QMIX (which uses a central network to combine agent rewards), and Mean Field RL (which reduces complexity by modeling the average behavior of other agents).

a branch of MARL-  Multi-Agent Path Finding (MAPF) 

the task of planning collision-free routes for multiple agents from start to goal.

**Three core algorithm families reviewed:**

- **DDPG / MADDPG** — deterministic policy gradient for continuous action spaces, extended to multi-agent settings with independent actor-critics.
- **PPO** — clips policy update ratios to prevent instability; noted for simplicity and strong empirical performance.
- **SAC / CTSAC** — maximum-entropy RL for better exploration; the CTSAC variant adds Transformer layers for long-range dependency modeling and curriculum learning to reduce catastrophic forgetting.

tools:

RL agent: 

New multiagent functionality has been added to the Reinforcement Learning Toolbox in MATLAB R2023b: 

https://se.mathworks.com/help/reinforcement-learning/ug/ppo-agents.html

**Frameworks.** TensorFlow, PyTorch, and Keras are covered as deep learning backends, alongside MARL-specific tools like PyMARL, Ray RLlib, and OpenAI Gym for simulation and testing.

**popular paradigm / training framework:** （CTDE, Centralized Training Decentralized Execution）

**DRL architecture:** 

**CTDE -** *centralized training, decentralized execution* (CTDE) paradigm

*(missing diagram — `Screenshot 2026-04-09 at 11.44.52.png` not exported from Notion)*

Why CTDE dominates for MAPF

The core problem CTDE solves is called **non-stationarity**: in a multi-agent system, as each agent learns and changes its policy, the environment appears to shift from every other agent's perspective, making learning unstable. By giving the critic global information during training, CTDE stabilizes learning — the critic always has the full picture and can correctly attribute credit or blame to each agent's actions. At deployment, this learned knowledge is baked into the actor weights, so no central server is needed.

**RL / MARL algorithms：**

**Main Types of RL Algorithms** The sources highlight several different ways agents can be trained:

- **Value-Based:** The agent calculates the expected long-term return (the "value") of specific states or actions and always tries to choose the highest-value option. **Q-Learning** and **DQN** (Deep Q-Networks) are classic examples.
- **Policy-Based:** Instead of calculating exact values, the agent directly optimizes its policy (its strategy) to output the best actions for a given state. (2)
- **Actor-Critic:** A hybrid approach. An "Actor" decides what action to take, and a "Critic" evaluates how good that action was, helping the actor improve.
    - **Proximal Policy Optimization (PPO)** is a highly popular, stable, and widely used actor-critic algorithm today. (3)
- **Model-Free vs. Model-Based:** Model-free agents learn strictly from direct experience in the environment. Model-based agents try to learn the "rules" of the environment to build an internal simulation, allowing them to plan ahead before acting.
1. https://www.geeksforgeeks.org/artificial-intelligence/differences-between-q-learning-and-sarsa/
2. https://datarootlabs.com/blog/state-of-reinforcement-learning-2025
3. https://www.digitalocean.com/community/tutorials/proximal-policy-optimization-implementation-applications 

### 1. Value Decomposition methods（值分解方法）

- VDN
- QMIX

👉 将整体价值函数拆分为多个 agent 的子价值

---

### 2. Central-critic methods / Actor-Critic（中央critic方法）

- MADDPG
- COMA
- MAPPO

👉 使用 centralized critic 解决 credit assignment

trade-offs:

**Challenges vs. advantages.** The paper is candid about MARL's limitations: poor scalability as agent counts grow, high GPU demands, training instability, difficulty finding stable equilibria, and over-reliance on simulated rather than real data. On the other side, it highlights flexibility, the ability to handle complex multi-dimensional environments, and broad applicability.

so, two directions and how to choose

1. Multi-Agent Systems, MAS —- MARL 
    1. each agent has RL model / algorithm in it  — agent collaborate 
    2. when to choose: every agent’s action/decision influence others . lead to state changes 
    3. 
2. **RL in RAG**
    1. **when to choose: environment is RAG system, user feedback, web browing** 

### ❌ MARL is hard（MARL 很难）

- non-stationarity
- unstable training
- hard credit assignment
- expensive

## **RL in RAG**

RAG can be considered as multi-decision process: 

when RAG

how RAG 

if continue RAG after one turn 

how to generate answer 

some improvement:

- 检索质量
- 答案正确性
- 事实一致性（faithfulness）
- 延迟（latency）
- 成本（cost）

👉 因此 RL 可用于：

- Query rewriting
- Retrieval policy
- Tool usage
- Multi-agent pipeline optimization

| 子任务 | Action | Reward |
| --- | --- | --- |
| Query rewriting | rewrite | retrieval metrics |
| Evidence selection | rerank | answer F1 |
| 是否继续检索 | stop / continue | accuracy - cost |
| Tool use | search/click | human preference |
| End-to-end | 全pipeline | QA F1 |

some patterns:

1. Policy learning over retrieval and tool actions **(online RL / RLHF-like).**

Web-browsing QA is a strong exemplar: a model interacts with a browser/search environment via discrete actions, trained with behavior cloning and then optimized against a reward model built from human preferences (a canonical RL-from-feedback pattern).

https://cdn.openai.com/WebGPT.pdf

1. RL module — RL specific agent, like rewrite or R. — Instead of directly supervising "how the model should be rewritten", the rewriting strategy is optimized in reverse based on "whether the rewriting makes the final retrieval/response better".
2. MARL: RAG can be considered as multi-decision process:  —- on paper, blue pens 
    
    when RAG
    
    how RAG 
    
    if continue RAG after one turn 
    
    how to generate answer
    
3. **Adaptive retrieval and self-critique without classic RL loops (inference-control tokens, self-reflection).**
    
    Self-RAG trains a model to retrieve on demand and emit reflection tokens to critique evidence and generations, improving groundedness and citation accuracy through learned control. This is not “agent RL” in the narrow sense, but it operationalizes a policy over retrieval decisions and control behaviors.
    
    - retrieve on demand
    - emit reflection tokens
    - critique evidence and generations
    - improve factuality and citation accuracy
    - inference-time controllability over retrieval behaviors

**RLHF**

Step1: 收集人类偏好（A比B好）
Step2: 训练 reward model
Step3: 用 RL（PPO）优化 policy

**Industry Preference optimization and offline RL substitutes - not full online RL / MARL —** high cost, low stability 

RL-adjacent: 

## alternatives of RL in RAG: DPO, ILQL— more stable, and popular in industry

1. DPO：不需要显式 reward model 和 on-policy rollouts  DPO（Direct Preference Optimization）
    
    RLHF need to train reward model
    
    (prompt, good answer, bad answer)
    → 直接训练模型：
    P(good) > P(bad)
    
    DPO 可以用于：
    
    - answer generation（让回答更符合人类偏好）
    - reasoning quality
    - citation correctness（通过 preference data）
2. ILQL：把 offline RL 的思想用于 language modeling，从固定数据中更稳定地做 utility optimization
    
    ILQL（Implicit Language Q-Learning）
    
    RLHF: needs online interaction — ILQL doesn’t need 
    
    ILQL needs existing data 
    

challenges: 

无论 MARL 还是 RAG + RL：

- 可扩展性（scalability）
- 样本效率（sample efficiency）
- 训练稳定性（stability）
- 评估困难（evaluation rigor）

risks: 

- reward hacking
- distribution shift
- cost explosion

### RL / RLHF

- HuggingFace TRL
- OpenRLHF

some materials haven’t beed looked into:

https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-overview?tabs=quickstarts

https://aclanthology.org/2022.emnlp-main.679/

https://openreview.net/forum?id=mlJLVigNHp

https://arxiv.org/abs/2310.06839

https://arxiv.org/abs/2307.03172

https://arxiv.org/abs/2212.10509

https://aclanthology.org/2021.eacl-main.74/
