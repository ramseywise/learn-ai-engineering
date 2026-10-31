---
origin: notion-export
confidence: medium
cleaned: 2026-10-31
sources:
  - Sutton & Barto, "Reinforcement Learning: An Introduction" (2020)
  - Phil Winder, "Reinforcement Learning: Industrial Applications of Intelligent Agents" (O'Reilly, 2020), ch. 1–9, 11
  - https://arxiv.org/abs/2203.02155 (InstructGPT)
  - https://arxiv.org/abs/2305.18290 (DPO)
  - https://cdn.openai.com/WebGPT.pdf (WebGPT)
  - https://arxiv.org/abs/1312.5602
  - https://arxiv.org/abs/1707.06347
  - https://arxiv.org/abs/2402.03300
  - https://arxiv.org/abs/2503.14476 (DAPO)
  - https://arxiv.org/abs/1003.0146
  - https://arxiv.org/abs/1802.09127
  - https://arxiv.org/abs/1508.03326
---

# 1 — RL Foundations for LLMs

> The MDP vocabulary, the Bellman equations, and the path from Q-learning to the PPO clip and max-entropy RL, with each piece tied to where LLM RL uses it. Then how RL shows up in multi-agent systems and RAG. Notes 02–05 build on this.

This note covers RL foundations as they apply to LLM alignment and agentic systems.
Three sections:

1. [RL Foundations](#1-rl-foundations) — MDP, Bellman, TD and Q-learning, policy gradients up to the PPO clip, entropy and SAC, exploration, learning from experts, problem design
2. [Multi-Agent RL (MARL)](#2-multi-agent-rl-marl) — CTDE, MADDPG, QMIX — for agent coordination
3. [RL in RAG](#3-rl-in-rag) — query rewriting, retrieval policy, tool use, Self-RAG

**For RLHF pipeline depth** (SFT → reward model → PPO, Bradley-Terry, reward hacking):
see [02 — RLHF pipeline](02-rlhf-pipeline.md)

**For algorithm comparison** (PPO vs DPO vs GRPO vs KTO/ORPO):
see [03 — Preference optimization](03-preference-optimization.md)

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
When the agent sees only part of the state, the problem is a **POMDP** (partially
observable MDP). The agent then has to keep a *belief state*, its own estimate of the true
state, built from the history: stacked frames, a recurrent network, or a filter
(*Reinforcement Learning*, ch. 8). An LLM agent is in a POMDP by construction. Its context
window is the belief state, and context engineering is belief-state engineering.

**Return.** The agent maximizes the discounted sum of future rewards, not the next reward:

```
G_t = r_{t+1} + γ·r_{t+2} + γ²·r_{t+3} + … = r_{t+1} + γ·G_{t+1}
```

γ near 0 makes the agent myopic and γ near 1 makes it far-sighted. The recursive form on the
right is what every algorithm below exploits. Winder's test for whether a problem needs RL at
all comes from it: the problem has to be *sequential* and *strategic*. A recommender trained
by supervised learning to maximize the next click learns click-bait. One trained on the return
can trade a click now for a returning user later (*Reinforcement Learning*, ch. 1 and 9).

### Core components

- **Agent:** The learner and decision-maker
- **Environment:** Everything outside the agent's control that turns an action into a new
  state and a reward. Winder treats it as a bounded context in the domain-driven-design sense:
  you decide where the agent ends and the environment begins (*Reinforcement Learning*, ch. 9)
- **State / observation:** The state is the full description of the environment; the
  observation is the part the agent sees. They coincide only in a fully observable MDP
- **Action:** The decision the agent makes given the state
- **Reward:** Scalar feedback (positive or negative) after taking an action
- **Policy (π):** The strategy mapping states to actions — the thing being optimized.
  Policies can be deterministic (`π(s) → a`) or stochastic (`π(a|s) → [0,1]`)

### Value functions and the Bellman equations

Three quantities appear in every algorithm in this pillar:

```
V^π(s)    = E_π[ G_t | s_t = s ]                 how good is this state under π
Q^π(s, a) = E_π[ G_t | s_t = s, a_t = a ]        how good is this action here, then follow π
A^π(s, a) = Q^π(s, a) − V^π(s)                   how much better than π's average is this action
```

Substituting the recursive return gives the **Bellman expectation equation**, and asking for
the best action gives the **Bellman optimality equation**:

```
V^π(s)  = Σ_a π(a|s) Σ_s' P(s'|s,a) [ R(s,a) + γ·V^π(s') ]
Q*(s,a) = Σ_s' P(s'|s,a) [ R(s,a) + γ·max_a' Q*(s',a') ]
```

The value of a state is the immediate reward plus the discounted value of where you land.
That one idea lets an agent learn from single steps instead of waiting for the end of an
episode. Winder's point is that the Bellman update is the fixed constraint on all of RL: new
algorithms change how they represent state, explore or regularize, but "underneath, all RL
algorithms are value-based or policy-based" (*Reinforcement Learning*, ch. 9).

The advantage `A` is the quantity LLM RL actually optimizes. PPO estimates it with a critic,
and GRPO estimates it from a group of sampled answers (see
[policy gradients](#policy-gradients-from-reinforce-to-the-ppo-clip) below).

**Three ways to estimate value** (*Reinforcement Learning*, ch. 2–3):

| Method | Needs a model of P? | Updates from | Bias / variance |
|---|---|---|---|
| Dynamic programming | Yes | The Bellman equation over all next states | Exact, but only with a known model |
| Monte Carlo | No | The full return `G_t` at the end of an episode | Unbiased, high variance, episodic only |
| Temporal difference (TD) | No | One step plus its own estimate: `r + γ·V(s')` | Biased (it *bootstraps*), low variance, online |

All three are instances of **generalized policy iteration**: evaluate the current policy,
make it greedier against that evaluation, repeat.

### Algorithm families

**Value-based:** The agent estimates the expected long-term return (the "value") of
states or state-action pairs, then acts greedily. Examples: Q-Learning, DQN (Deep Q-Networks). DQN ([arXiv:1312.5602](https://arxiv.org/abs/1312.5602), Mnih et al., 2013) learned Q-values straight from raw pixels with a CNN. Its experience replay buffer broke the correlation between consecutive frames. With one architecture and one set of hyperparameters it played seven Atari games and beat a human expert on three.

**Policy-based:** Directly optimize the policy without an explicit value function.
Policy gradient methods compute `∇E[R]` and update `π_θ` toward higher-reward trajectories.
They sample from a distribution rather than maximize over actions, which is why they scale to
huge or continuous action spaces where a `max_a` is infeasible (*Reinforcement Learning*,
ch. 9). An LLM choosing one token from a vocabulary of tens of thousands, at every step, is
such a space.

**Actor-Critic:** Hybrid approach. An "actor" decides actions (policy); a "critic"
estimates value (how good the state is), providing a lower-variance signal for updating
the actor. PPO ([arXiv:1707.06347](https://arxiv.org/abs/1707.06347)) became the default
actor-critic algorithm for deep RL and for RLHF. For LLM reasoning with verifiable rewards,
critic-free GRPO has largely taken over ([03](03-preference-optimization.md)).

**Model-free vs. model-based:** Model-free agents learn purely from experience.
Model-based agents learn the transition function P(s'|s,a) and use it for planning —
more sample-efficient but harder to learn accurate models.

**On-policy vs. off-policy.** An *on-policy* method learns about the policy that is
generating the data (SARSA, REINFORCE, A2C, PPO). An *off-policy* method learns about one
policy, the *target*, from data generated by another, the *behavior* policy (Q-learning, DQN,
DDPG, SAC). Off-policy methods can reuse old data from a replay buffer, logs or a
demonstrator; the price is a mismatch between the two distributions that has to be corrected,
usually by importance sampling (*Reinforcement Learning*, ch. 1, 3 and 6).

> **Dated.** Winder writes that "most state-of-the-art algorithms are off-policy"
> (*Reinforcement Learning*, ch. 1). That held for 2020 benchmarks such as Atari and MuJoCo.
> LLM RL in 2025–26 is mostly on-policy: PPO and GRPO sample fresh completions from the current
> policy at every step. Winder's case for off-policy learning was exploration. A pretrained
> prior already makes on-policy samples informative, which removes much of that argument.

### Temporal-difference learning: Q-learning vs. SARSA

TD learning updates an estimate toward a one-step target. The gap between target and
estimate is the **TD error** δ, the single most reused quantity in RL:

```
δ_t = r_{t+1} + γ·V(s_{t+1}) − V(s_t)          TD error
V(s_t) ← V(s_t) + α·δ_t                         TD(0) update
```

Two control algorithms differ in one term of the target (*Reinforcement Learning*, ch. 3):

```
Q-learning (off-policy):  Q(s,a) ← Q(s,a) + α [ r + γ·max_a' Q(s',a') − Q(s,a) ]
SARSA      (on-policy):   Q(s,a) ← Q(s,a) + α [ r + γ·Q(s',a')        − Q(s,a) ]   a' ~ π
```

```python
def q_update(Q, s, a, r, s_next, done, alpha=0.1, gamma=0.99):
    target = r if done else r + gamma * max(Q[s_next].values())  # SARSA: Q[s_next][a_next]
    Q[s][a] += alpha * (target - Q[s][a])                        # alpha * TD error
```

Q-learning bootstraps from the best next action, so it learns the value of the greedy policy
while it explores with ε-greedy. SARSA bootstraps from the action it actually takes next, so it
learns the value of the exploring policy, random slips included. Winder's cliff world shows the
consequence. Each step costs −1, falling off the cliff costs −100 and ends the episode, and the
agent explores with ε-greedy:

![Two grid-world policies. Q-learning walks along the row next to the cliff; SARSA climbs to the top row and walks along it, far from the cliff.](../sources/images/winder-reinforcement-learning-fig3-3.png)
*Image Source: Phil Winder, *Reinforcement Learning* (O'Reilly, 2020), Fig. 3-3*

Q-learning finds the shortest path along the cliff edge, which is optimal only if the agent
never makes a random move. SARSA learns the safe route, because its value estimates include the
chance that an ε-greedy step kicks it over the edge. The on-policy agent optimizes the policy it
will actually run. That is the same argument LLM RL makes for on-policy rollouts.

**n-step returns and eligibility traces.** One step is the low-variance, high-bias extreme;
the full Monte Carlo return is the other. An n-step target uses n real rewards before
bootstrapping, and TD(λ) blends all n with weights `(1−λ)λ^(n−1)` via an eligibility trace
(*Reinforcement Learning*, ch. 3). Multi-step targets help most when rewards are sparse or
delayed. **GAE**, the advantage estimator inside PPO for RLHF, is exactly this λ-weighting
applied to TD errors:

```
Â_t = Σ_{l≥0} (γλ)^l · δ_{t+l}          λ = 0 → one-step TD;  λ = 1 → Monte Carlo minus V
```

### Deep Q-networks and learning from logs

DQN made Q-learning work with a neural network by fixing two sources of instability
(*Reinforcement Learning*, ch. 4):

- **Experience replay** samples past transitions at random, which breaks the correlation
  between consecutive steps.
- A **target network**, a lagged copy of the Q-network, computes `max_a' Q(s',a')` so the
  target does not move with every update.

DQN also uses the Huber loss, which is linear for large errors and so caps the gradient from
outliers. The `max` in the target overestimates values whenever estimates are noisy. **Double
Q-learning** picks the action with one network and scores it with the other. Rainbow
combines that with prioritized replay, dueling (V + A) heads, n-step targets, noisy-net
exploration and distributional returns.

**Offline (batch) RL** learns from a fixed log with no further interaction. Winder trains a
DQN agent on the replay buffer of another DQN agent on CartPole, with no environment access.
Its Q-values diverge, climbing on a log scale, and its reward stays poor. The `max` keeps
choosing actions that are not in the data, and with no way to try them nothing corrects the
optimistic estimate. Batch-constrained Q-learning (BCQ) converges on the same buffer because
it only considers actions a generative model says the log could contain (*Reinforcement
Learning*, ch. 4). The lesson carries over directly to LLMs. Offline preference methods such as
DPO ([03](03-preference-optimization.md)) are batch RL on a fixed preference set, and they
share its limit: the policy improves only where the data has coverage. Online and on-policy
methods keep the advantage of being able to check their own guesses.

### Policy gradients: from REINFORCE to the PPO clip

Policy gradient methods parameterize the policy directly and climb the gradient of expected
return. The **policy gradient theorem** gives that gradient without differentiating through
the environment:

```
∇_θ J(θ) = E_π[ Ψ_t · ∇_θ log π_θ(a_t | s_t) ]
```

`∇ log π` points toward making the action taken more likely; `Ψ_t` says by how much. Winder's
summary of ch. 5 is that the policy gradient algorithms differ *only* in what they use for
Ψ (*Reinforcement Learning*, ch. 5, Eq. 5-11):

| Ψ_t | Algorithm | Note |
|---|---|---|
| `G_t` (full return) | REINFORCE | Unbiased, very high variance, waits for the episode to end |
| `G_t − b(s_t)` | REINFORCE with baseline | Same expectation, far lower variance |
| `r + γ·V(s') − V(s)` = δ_t | One-step actor-critic | Critic supplies the baseline and bootstraps |
| n-step or GAE advantage `Â_t` | A2C / PPO | The bias–variance dial |
| group-normalized reward | GRPO | Baseline from sibling samples, no critic |

**Why a baseline.** With raw returns, a policy that happens to fail early gets a large update
even if it was good. In Pong every early episode scores near −21, so every action gets pushed
down. Subtracting a baseline turns "was this good?" into "was this better than usual?". The
expectation is unchanged because `E[∇ log π · b(s)] = 0`. Winder measured the effect on one
CartPole run:

![Standard deviation of the policy gradient per episode over 500 episodes. REINFORCE stays around 2 to 4 throughout; REINFORCE with baseline drops to near zero after about 170 episodes.](../sources/images/winder-reinforcement-learning-fig5-4.png)
*Image Source: Phil Winder, *Reinforcement Learning* (O'Reilly, 2020), Fig. 5-4. The printed
caption repeats Fig. 5-3's "average rewards"; the axis and the text show this is gradient
standard deviation*

Once the policy is decent, plain REINFORCE keeps making large updates that knock it about; the
baseline version settles. That is what "variance reduction" means in the papers. GRPO's
`(r_i − mean(r)) / std(r)` over a group of completions for the same prompt is this baseline
computed empirically instead of learned ([03](03-preference-optimization.md)).

```python
def reinforce_with_baseline_loss(logp, returns, values):
    # logp: log π(a_t|s_t) for the actions taken; returns: G_t; values: V(s_t)
    adv = (returns - values).detach()            # no gradient through the baseline
    policy_loss = -(adv * logp).mean()           # ascend E[A · ∇log π]
    value_loss = (returns - values).pow(2).mean()
    return policy_loss + 0.5 * value_loss
```

**Actor-critic tuning.** In Winder's CartPole experiments the n-step actor-critic learned far
faster than REINFORCE with baseline once the policy step size was raised; the Monte Carlo
version "acts like a brake". He recommends that the critic learn at least as fast as the
actor. With the actor's rate fixed, a critic rate of ~0.1 worked best, 0.01 did slightly better
in the long run, and 0.5 was unstable (*Reinforcement Learning*, ch. 5, CartPole with tile-coded
linear features). A critic that lags the actor feeds it stale advantages, and one that jumps
around feeds it noisy ones.

**Off-policy correction.** To reuse data from an older policy π_old, weight each sample by the
**importance ratio** `r_t(θ) = π_θ(a_t|s_t) / π_old(a_t|s_t)`. Winder's illustration recovers the
mean of a loaded die, 4.3, from rolls of a fair one by reweighting each face
(*Reinforcement Learning*, ch. 6). Large ratios make the estimate's variance explode, which is
why every practical method clips or constrains them.

**Trust regions.** A policy gradient step that is too large can destroy a good policy, and
nothing in the gradient tells you how large is too large. TRPO constrains each update to a
small KL divergence from the previous policy, solved with conjugate gradients. It works, but it
is expensive and awkward with shared policy/value networks. A KL *penalty* with coefficient β is
simpler but β is hard to tune (*Reinforcement Learning*, ch. 6). RLHF keeps that penalty, but
against the frozen reference model rather than the previous iterate
([02](02-rlhf-pipeline.md)).

**The PPO clip** replaces the trust region with a clipped surrogate:

```
L_CLIP(θ) = E_t[ min( r_t(θ)·Â_t ,  clip(r_t(θ), 1−ε, 1+ε)·Â_t ) ]
L_PPO     = L_CLIP − c1·(V_θ(s_t) − V_target)² + c2·H[π_θ(·|s_t)]
```

![Two plots of the PPO clipped objective against the ratio r. For A > 0 the objective rises linearly until 1+ε, then is flat. For A < 0 it is flat until 1−ε, then falls linearly as r grows.](../sources/images/winder-reinforcement-learning-fig6-5.png)
*Image Source: Phil Winder, *Reinforcement Learning* (O'Reilly, 2020), Fig. 6-5*

Read the plot as "where does the gradient vanish". With a positive advantage the objective
stops rewarding increases in the action's probability once `r > 1+ε`. With a negative advantage
it stops rewarding decreases once `r < 1−ε`. Outside those zones the unclipped term applies in
full, so a change that makes things *worse* is never clipped. The `min` makes the objective a
pessimistic lower bound on the unclipped one. Schulman et al. used ε between 0.1 and 0.3. The
full objective adds a value loss weighted by c1 when policy and value share a network, and an
entropy bonus weighted by c2, which some of their experiments set to zero (*Reinforcement
Learning*, ch. 6).

```python
def ppo_clip_loss(logp_new, logp_old, adv, eps=0.2):
    ratio = (logp_new - logp_old).exp()
    unclipped = ratio * adv
    clipped = ratio.clamp(1 - eps, 1 + eps) * adv
    return -torch.min(unclipped, clipped).mean()   # minimize the negative lower bound
```

> **Contradicts.** Winder describes the negative-advantage case as "at low ratios … the policy
> parameters will continue to change at the same rate", and says PPO ignores the importance
> sampling "when the policy is improving (take bigger steps)" (*Reinforcement Learning*, ch. 6).
> His own Fig. 6-5 shows the reverse. For A < 0 and r < 1−ε the objective is flat, so the
> gradient is zero and that sample stops pushing. For A > 0 the clip caps the gain at 1+ε, so
> improving moves are the ones that get limited. Use the plot, not that paragraph.

> **Framing differs.** Winder files PPO under off-policy methods, as importance sampling of
> advantages under the old policy. [03](03-preference-optimization.md) calls it on-policy
> actor-critic. Both are defensible. PPO collects data with the current policy and throws it
> away after a few epochs, so it is on-policy; within those epochs the policy drifts from the
> one that sampled the data, and the ratio and clip correct for that small staleness. Clip
> variants used in LLM RL, such as DAPO's *clip-higher*, which raises the upper bound only, are
> adjustments to the plot above.

**Off-policy actor-critics for continuous control.** DDPG learns a deterministic policy with a
Q-critic, replay, soft target updates and action noise. TD3 fixes its overestimation with
clipped double-Q, delayed policy updates and target-policy smoothing; Winder recommends TD3
over DDPG (*Reinforcement Learning*, ch. 6). Neither is used for LLMs. They matter here only
because MADDPG ([§2](#2-multi-agent-rl-marl)) is built on DDPG.

### Entropy and maximum-entropy RL (SAC)

The entropy of a policy, `H[π(·|s)] = −Σ_a π(a|s) log π(a|s)`, measures how spread out its
action choices are. **Maximum-entropy RL** adds it to the reward, so the agent is paid to stay
random wherever randomness costs little:

```
J(π) = E_π[ Σ_t r_t + α·H[π(·|s_t)] ]        α = temperature
π*(a|s) ∝ exp( Q_soft(s,a) / α )            the optimal policy is a softmax over soft Q-values
```

**Soft actor-critic (SAC)** learns soft Q-functions off-policy from a replay buffer and fits the
policy by minimizing the KL divergence to that softmax, using a reparameterized Gaussian for
continuous actions. Most implementations tune α automatically toward a target entropy, commonly
`−|A|` for an action space with |A| dimensions (*Reinforcement Learning*, ch. 7).

Winder's grid demo shows both sides of α. A soft Q-learning agent visits states far more evenly
than an ε-greedy one. At α = 1, though, the entropy bonus outweighs the goal reward of 1, and
the agent learns to hang around the high-entropy middle of the grid instead of reaching the
goal. Annealing α from 0.5 to 0.005 fixes it: explore early, become Q-learning-like late
(*Reinforcement Learning*, ch. 7). SAC is also sensitive to reward scale, for the same reason:
α only means something relative to the size of the rewards.

**Why this matters for LLMs.** Replace the entropy bonus with a KL penalty to a reference
policy and the same derivation goes through:

```
max_π E[r] − β·KL(π || π_ref)   ⇒   π*(y|x) ∝ π_ref(y|x) · exp( r(x,y) / β )
```

Entropy regularization is the special case where π_ref is uniform. This closed form is the
starting point of DPO, which inverts it to express the reward through the policy
([03](03-preference-optimization.md)). The RLHF objective in [02](02-rlhf-pipeline.md) is
max-entropy RL with the pretrained model as the prior. Schulman, Chen and Abbeel showed that
entropy-regularized policy gradients and soft Q-learning are equivalent, which Winder cites as
the bridge between the value and policy families (*Reinforcement Learning*, ch. 7).

> **Dated.** Winder's Table 7-1 shows SAC ahead of PPO on most MuJoCo tasks at 1M steps, for
> example Humanoid 4,831–5,723 for SAC against 806 for PPO. He adds that results vary widely
> by implementation and that papers rarely publish raw curves (*Reinforcement Learning*,
> ch. 7). That holds for continuous control. SAC plays no part in LLM training: the action
> space is discrete, rollouts are generated fresh, and the KL anchor to π_ref does the
> regularizing job. In RLVR the live entropy problem is the opposite one. DAPO reports policy
> entropy *collapsing* early in GRPO-style training, so the model stops sampling alternative
> solutions. Its clip-higher fix raises only the upper clip bound, which leaves room to raise the
> probability of unlikely tokens ([arXiv:2503.14476](https://arxiv.org/abs/2503.14476); the
> fix is listed in [05](05-post-training-for-agents.md)).

### Exploration vs. exploitation

A fundamental tension: should the agent **exploit** the best action it knows (maximize
immediate reward) or **explore** new actions that might yield higher rewards in the long
run? Strategies:
- **ε-greedy:** With probability ε, take a random action; otherwise exploit
- **UCB (Upper Confidence Bound):** Choose actions with high uncertainty to reduce
  uncertainty faster
- **Entropy regularization (SAC; optional in PPO):** Add an entropy bonus to the objective to
  encourage diverse action distributions. The PPO paper includes one for its Atari runs and
  turns it off for continuous control ([arXiv:1707.06347](https://arxiv.org/abs/1707.06347)).
  GRPO as published has no entropy term; its only regularizer is the KL penalty to the
  reference model ([arXiv:2402.03300](https://arxiv.org/abs/2402.03300)).

- **Softmax (Boltzmann) selection:** sample actions with probability ∝ `exp(Q/τ)`. Unlike
  ε-greedy, which explores uniformly, it explores in proportion to how promising each action
  looks. Winder recommends feeding it advantages rather than raw values (*Reinforcement
  Learning*, ch. 2 and 9)
- **Thompson sampling:** keep a posterior over each action's value, draw a sample, act
  greedily on the draw

In LLM contexts, temperature sampling at inference time is the primary exploration
mechanism during data collection. It is the softmax rule above, with logits in place of Q.

**Intrinsic motivation** adds a bonus for novelty when the extrinsic reward is sparse
(*Reinforcement Learning*, ch. 9). Count-based bonuses reward rarely visited states. Curiosity
rewards the error of a learned next-state predictor, and so gets stuck in front of a "noisy TV"
whose next frame is unpredictable. Random network distillation avoids that trap: it rewards the
error in predicting a *fixed random* network's embedding of the current observation, which a
static noisy screen does not keep generating. Winder's caution is that all of these work locally
and by reshaping the reward. Before reaching for them, try a denser reward, a demonstrator or a
simpler problem. Exploration needs prior knowledge, which is precisely what a pretrained LLM
brings.

**Contextual bandits** are the one-step case: observe a context, pick an action, get a
reward, with no state carried forward. It is the right model for recommendation, routing and
prompt or model selection. Two results anchor it:

- **LinUCB** ([arXiv:1003.0146](https://arxiv.org/abs/1003.0146), Li et al., 2010) fits a
  ridge regression per arm and picks the arm with the highest upper confidence bound. On over
  33M events from the Yahoo! front-page news module it got a 12.5% click lift over a
  context-free bandit. The paper's other lasting contribution is **replay evaluation**: a
  bandit policy can be scored offline, without bias, on logs collected under a uniformly
  random policy.
- **Thompson sampling with neural nets** ([arXiv:1802.09127](https://arxiv.org/abs/1802.09127),
  Riquelme et al., 2018) benchmarked approximate Bayesian deep nets as posteriors. Many methods
  that work in supervised learning did poorly here because their uncertainty estimates converge
  too slowly for online decisions. The robust choice was **NeuralLinear**: a network learns a
  representation, and an exact Bayesian linear regression on its last layer supplies the
  uncertainty.

Zhou's survey ([arXiv:1508.03326](https://arxiv.org/abs/1508.03326)) covers the wider family:
stochastic vs adversarial rewards, and UCB vs Thompson variants.

### Learning from experts: imitation and inverse RL

When demonstrations exist, an agent need not start from scratch (*Reinforcement Learning*,
ch. 8). Each classical method has a direct LLM counterpart:

| Classical method | What it does | LLM counterpart |
|---|---|---|
| **Behavior cloning** | Supervised learning of the expert's action in each demonstrated state | SFT on demonstrations ([02](02-rlhf-pipeline.md), stage 1) |
| **DQfD, GAIL, SQIL** | RL with a pull toward expert behavior, via a supervised loss, an adversarial discriminator, or replay-buffer reward relabelling | SFT warm start, then RL with a KL anchor |
| **Inverse RL** | Learn a reward that explains the demonstrations, solve the MDP, compare, repeat | A learned reward model ([02](02-rlhf-pipeline.md), stage 2) |

Winder's objection to behavior cloning is the one [05](05-post-training-for-agents.md) makes
about SFT. The clone is lost in any state the expert never visited, and in high dimensions it
will reach such states. SQIL's remedy is to let the agent deviate and then nudge it back toward
expert states, with a weight that sets how much expert advice to use. That is the role the KL
term plays in RLHF.

Inverse RL assumes the expert is optimal, which demonstrations rarely are, and it re-solves the
MDP at every iteration, which limits it to small state spaces. Preference-based reward
modelling sidesteps both: people compare outcomes rather than demonstrate them, and the reward
is fit once. Winder also notes that failed demonstrations are easier to collect than good ones
and can be used by demoting their reward (*Reinforcement Learning*, ch. 8). Rejected responses
in a preference pair play exactly that role.

> **Dated.** Winder says behavior cloning "isn't popular because it overfits the expert
> demonstrations" (*Reinforcement Learning*, ch. 8). For LLMs the order reversed: next-token
> prediction on human text is behavior cloning at internet scale, and it supplies the prior
> that makes later RL tractable. The covariate-shift objection still holds, and it is the
> argument for following SFT with on-policy RL.

### Beyond the flat MDP: hierarchy and curricula

- **Hierarchical RL** splits a problem into subtasks, with high-level policies choosing among
  low-level skills over longer timescales. Winder recommends designing the hierarchy by hand
  when the separation of concerns is obvious, before trying learned hierarchies such as HIRO
  (subgoals as intrinsic rewards) or DIAYN (unsupervised skill discovery) (*Reinforcement
  Learning*, ch. 8). A planner LLM delegating to tool-using executors is a hand-designed
  hierarchy.
- **Curriculum learning** orders tasks from easy to hard so the agent finds reward early;
  self-play generates the curriculum automatically. Winder's chapter 11 states the principle:
  learning works only when the gap between knowing and not knowing is small. RLVR uses the same
  idea when it keeps only prompts the current model solves sometimes but not always (DAPO's
  dynamic sampling, [arXiv:2503.14476](https://arxiv.org/abs/2503.14476)). A prompt solved by
  every sample in a group, or by none, gives GRPO zero advantage and no gradient.

### Engineering an RL problem

Winder's practical chapters argue that the algorithm is rarely the bottleneck. Most of the
work is in defining the MDP, the reward, the state and the actions (*Reinforcement Learning*,
ch. 9 and 11).

**Start simple.** Before training anything, picture a random policy acting in the environment.
If it never stumbles on the right behavior, RL is unlikely to help. Then ask whether you could
solve the task yourself from the agent's observations. Build up baselines in order: random,
then the cross-entropy method, then plain Q-learning or a policy gradient. Shrink the state and
action spaces, and simplify the goal, before scaling up (*Reinforcement Learning*, ch. 11).

**State engineering.** Represent the state as faithfully as you can and let the policy do the
rest. Engineering features that solve the task is a sign the problem is supervised. One reliable
measurement can beat learning from pixels: in QT-Opt, adding a gripper-height reading improved
grasping of unseen objects by 12% (*Reinforcement Learning*, ch. 9). Normalize observations to
zero mean and unit variance, and watch for statistics that drift (ch. 11).

**Reward engineering** is "arguably the most important task in RL" (*Reinforcement Learning*,
ch. 9). Agents optimize the reward you wrote, not the one you meant. Winder's example is a Unity
agent meant to use a box to jump a wall, which learned to slip around the edge of the arena.
His checklist for a reward:

- fast to compute, since it is called millions of times
- correlated with the true objective
- low-noise; combining several noisy proxies helps
- encodes non-functional requirements such as safety or cost
- discriminates between states by more than the noise in the value estimates, or the agent
  circles
- smooth, because discontinuous rewards give jerky policies
- simple

Clipping rewards to ±1, as DQN does, can throw away the signal. In Pac-Man it makes fruit worth
the same as a dot, and normalizing instead turns the agent into a ghost-hunting fruit-seeker
(ch. 9). The same failure appears in LLM RL as [reward hacking](02-rlhf-pipeline.md), and the
same checklist applies to [multi-turn agent rewards](05-post-training-for-agents.md).

**Action design.** Decide whether actions are binary, discrete, continuous or mixed; whether
several can happen at once; and whether a hierarchy is hiding in them. Changing that choice
later can force a change of algorithm. For massive action spaces, policy gradients avoid the
`max`. The book's YouTube example ranks the top k items rather than choosing a combination
(ch. 9).

**Online, offline, concurrent.** Online learning explores but needs a live or simulated
environment. Offline learning uses logs but cannot explore and suffers distribution shift
(see [DQN](#deep-q-networks-and-learning-from-logs)). Concurrent learning runs many agents in
parallel on one problem (ch. 9). Simulations are worth building first, but a policy that works
perfectly in simulation can still fail in the real world (ch. 9).

**Debugging.** RL bugs hide: rewards arrive late and noise masks errors. Winder cites Engstrom
et al.: code-level optimizations account for more of PPO's advantage over TRPO than the clip
does (ch. 11). Log and plot observations, actions and rewards. Track the value function at
fixed states over time, watching for oscillation or a stall. Monitor action entropy, which
shows whether the agent is still exploring, and the KL between successive policies, which shows
whether updates are too large or too small. Start with a linear model, a fixed seed and a single
thread. RLHF and GRPO runs are watched through the same kind of dashboard: reward, KL to the
reference model, entropy and response length.

**Comparing runs.** One training run is one sample. Colas et al. needed **at least 15 reruns
per algorithm**, each with a different seed, to show with statistical confidence that SAC beats TD3 on
Half-Cheetah-v2. At that sample size, and with roughly normal returns, Welch's t-test was the most robust
test. Nonparametric tests (Mann–Whitney, bootstrap, permutation) need many more runs to reach the
same power (ch. 10). RL returns are often not normal: rare stuck episodes, capped rewards, and
variances that differ between algorithms. A seed that "should" reproduce a run often doesn't,
because some library's RNG went unset. Plot the per-seed curves first, then test.

### Scaling: actors and learners

Rollouts are sequential, so you can't speed up one agent by adding GPUs. RL scales by splitting
**actors**, which generate experience, from **learners**, which update the policy (ch. 10). Two
designs bracket the space:

| Design | How it works | Cost |
|---|---|---|
| Synchronous (DD-PPO) | Every worker collects a batch, then all exchange gradients | Each update waits for the slowest worker, so stragglers are cut off preemptively. Wijmans et al. report near-linear scaling to 256 GPUs |
| Asynchronous (IMPALA, SEED) | Actors push trajectories into a queue; the learner trains on whatever arrives | The data is slightly off-policy and needs an importance-weighted correction (V-trace) |

Throughput is the reason to accept that staleness. Espeholt et al. priced one billion frames at
**\$236 for IMPALA against \$54 for SEED** on DeepMind Lab, and \$899 against \$369 on Google Research
Football. LLM RL faces the same choice in a different shape. Generation is the actor and dominates
wall-clock time. Asynchronous rollout pipelines trade freshness for throughput, and their
staleness correction plays the role V-trace played for IMPALA. The framing transfers from the
2020 book. The systems do not.

### What has dated since 2020

Winder's book predates LLM RL. The foundations hold; the defaults have moved:

| 2020 view (*Reinforcement Learning*) | 2025–26 LLM RL |
|---|---|
| Most state-of-the-art algorithms are off-policy (ch. 1) | PPO and GRPO are on-policy; replay buffers are rare |
| SAC beats PPO; entropy bonuses drive exploration (ch. 7) | Discrete tokens, KL to a reference model; entropy *collapse* is the problem |
| Behavior cloning overfits and is unpopular (ch. 8) | Pretraining plus SFT is behavior cloning, and it comes first |
| A learned critic (A2C, PPO) is the standard baseline (ch. 5–6) | GRPO drops the critic and uses group statistics ([03](03-preference-optimization.md)) |
| Rewards are shaped by hand or learned by IRL (ch. 8–9) | Learned reward models (RLHF) or verifiable checkers (RLVR) |
| Tabula rasa agents are sample-inefficient (ch. 11) | A pretrained prior makes exploration targeted: in [05](05-post-training-for-agents.md)'s treasure hunt, Q-learning needs ~10,000 episodes and an LLM agent wins on the first try |
| Offline learning is the field's biggest open challenge (ch. 11) | Partly solved for preferences (DPO); online RL is still preferred for reasoning |

### RL applied to LLMs

LLMs are trained using RL primarily at two stages:

1. **RLHF alignment (post-pretraining):** The LLM is the policy; each token is an
   action; the reward model scores completed responses. See [02-rlhf-pipeline.md](02-rlhf-pipeline.md).

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

**Two formalisms** (*Reinforcement Learning*, ch. 8). A **Markov game** extends the MDP to
agents acting in parallel: each has its own actions and rewards, and the state is shared. An
**extensive-form game** represents turns, chance and information as a tree, as in poker; it is
the more common model in the literature.

**Why independent learners struggle.** Running single-agent Q-learning or policy gradients in
each agent is the obvious first try. It can find stable but suboptimal policies in simple
settings, and it tends not to converge as complexity grows. Replay buffers stop helping, because
the stored transitions were generated by other agents' old policies. When learning must stay
decentralized, **hysteretic learning** uses a smaller learning rate for negative TD errors, on
the assumption that a bad outcome was caused by a teammate exploring. That makes agents
optimistic, which can cause problems of its own (*Reinforcement Learning*, ch. 8).

**Why the critic is the place to centralize.** The actor-critic gradient already conditions
the critic on the agent's action. Extending it to condition on *all* agents' actions makes the
environment stationary from the critic's point of view. Each agent keeps its own actor and
critic, so agents may have different rewards, which lets the same method handle cooperative and
competitive settings (*Reinforcement Learning*, ch. 8). For multi-agent LLM pipelines the
analogue is training against a judge that sees the whole transcript while each role acts on its
own context.

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
  Deterministic policy gradients for continuous action spaces. Each agent also learns
  approximations of the other agents' policies while they are changing, a source of
  nonstationarity that MADDPG damps by updating a random subset of policies
  (*Reinforcement Learning*, ch. 8).
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

See [03-preference-optimization.md](03-preference-optimization.md) for DPO details.

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

- **RLHF pipeline:** [02-rlhf-pipeline.md](02-rlhf-pipeline.md) — three stages,
  Bradley-Terry model, KL penalty, reward hacking failure modes
- **Algorithm comparison:** [03-preference-optimization.md](03-preference-optimization.md)
  — PPO vs DPO vs GRPO vs KTO/IPO/ORPO, decision framework, DeepSeek-R1 story
- **Constitutional AI / RLAIF:** [04-constitutional-ai.md](04-constitutional-ai.md)
  — AI-generated feedback, critique-revision loop, scaling alignment

---

## Tooling

**Python RL frameworks:**
- **HuggingFace TRL** — RLHF, DPO, GRPO training on top of HuggingFace models.
  The standard library for preference optimization. [docs](https://huggingface.co/docs/trl/)
- **OpenRLHF** — distributed RLHF training; supports PPO at large scale

**Classic RL environments:**
- **Gymnasium** (successor to OpenAI Gym) — the `reset()` / `step(action)` interface. Winder
  recommends wrapping a real system in the same interface as the simulator so agents move
  between them unchanged (*Reinforcement Learning*, ch. 9)

**MARL simulators and frameworks:**
- **Ray RLlib** — general-purpose RL with multi-agent support
- **PyMARL** — MARL-specific: QMIX, COMA, VDN implementations
- **PettingZoo** — multi-agent Gymnasium-compatible environments

---

## Cross-links

- **Upstream:** [05-RL README](../README.md) — full topic map and resource
  index for the RL & alignment pillar
- **Downstream:** [03-agentic-foundations/README.md](../../03-agentic-foundations/README.md)
  — RL-trained agents (ReAct, Reflexion), multi-agent coordination
- **RLHF depth:** [02-rlhf-pipeline.md](02-rlhf-pipeline.md)
- **Algorithm depth:** [03-preference-optimization.md](03-preference-optimization.md)
- **Constitutional AI:** [04-constitutional-ai.md](04-constitutional-ai.md)

---

**Next:** [02 — RLHF pipeline](02-rlhf-pipeline.md) applies the policy-gradient half of this note to language models.
