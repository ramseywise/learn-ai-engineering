# RLHF Pipeline

> **Pillar:** [05-RL](README.md)
> **Presumes:** transformer architecture, supervised fine-tuning basics
> **Papers:** InstructGPT (2203.02155), Anthropic RLHF (2204.05862), GPT-4 (2303.08774)

---

## What it is

Reinforcement Learning from Human Feedback (RLHF) is the post-pretraining alignment
technique that turns a capable-but-unruly language model into a helpful, honest, and
harmless assistant. It's why ChatGPT answered questions differently from raw GPT-3 —
same underlying capability, radically different behavioral defaults.

The core insight: human preferences over model outputs are a richer training signal than
any label schema you could design. Rather than specifying *what* good behavior looks like,
you collect *comparisons* of model behavior and train a reward model to generalize that
preference, then optimize the policy against it.

---

## Three-stage pipeline

```
Base LLM (pretrained)
      |
      v
[Stage 1] Supervised Fine-Tuning (SFT)
      |   Human-written demonstrations
      v
SFT Model
      |
      v
[Stage 2] Reward Model Training
      |   Human preference comparisons (A vs B)
      v
Reward Model (RM)
      |
      v
[Stage 3] RL Optimization (PPO)
      |   Maximize RM reward subject to KL constraint
      v
Aligned Policy (the deployed model)
```

### Stage 1 — Supervised Fine-Tuning (SFT)

Start with a pretrained base model. Fine-tune it on high-quality human-written
demonstrations: prompt → ideal completion pairs. This shifts the model from "predicts
next token on internet text" to "follows instructions in a dialogue format."

InstructGPT used ~13k SFT examples written by contractors. The SFT model is not the
final product — it's the starting policy for RL. Its job is to produce plausible
completions that the reward model can meaningfully score.

**Why SFT first?** The base model's output distribution is too broad for PPO to explore
efficiently. SFT narrows the distribution toward the target task domain before RL begins.

### Stage 2 — Reward Model Training

Collect preference data: show the SFT model's outputs to human raters, ask them to rank
responses from best to worst. Typically: prompt → (response A, response B) → human picks
preferred.

Train a **reward model** on this data. The reward model is typically the SFT model with
the final layer replaced by a scalar head. It takes (prompt, completion) and outputs a
scalar reward score.

**Bradley-Terry model.** The standard probabilistic framing for pairwise preferences.
Given responses y_w (preferred/"winner") and y_l (rejected/"loser") from prompt x:

```
P(y_w > y_l | x) = σ(r_θ(x, y_w) - r_θ(x, y_l))
```

where `r_θ` is the reward model and `σ` is the sigmoid function. Training maximizes
log-likelihood of human choices:

```
L_RM(θ) = -E[(x, y_w, y_l) ~ D] [ log σ(r_θ(x, y_w) - r_θ(x, y_l)) ]
```

The reward model learns a total ordering over response quality. InstructGPT used ~33k
comparison pairs from the same contractor pool.

### Stage 3 — RL Optimization (PPO)

Use the reward model as the environment reward function. Optimize the SFT-initialized
policy (the LLM) using **Proximal Policy Optimization (PPO)** to maximize expected reward
while staying close to the SFT policy.

**PPO objective for language models:**

```
L_PPO(θ) = E[r_θ(x, y)] - β · KL[π_θ(y|x) || π_SFT(y|x)]
```

where:
- `r_θ(x, y)` is the reward model score for the generated response
- `β · KL[...]` is the KL divergence penalty keeping the policy near SFT
- `β` is the penalty coefficient (typically 0.02–0.2)

The KL term is essential. Without it, the policy learns to exploit the reward model
rather than genuinely improve — a failure mode called **reward hacking**.

**PPO mechanics for LLMs:**
- The policy generates a full response (sequence of tokens) to a prompt
- The reward model scores the complete response
- PPO treats each token as an action, the sequence as a trajectory
- The value function (critic) is typically another copy of the LLM with a scalar head
- Policy updates are clipped: `min(r_t · A_t, clip(r_t, 1-ε, 1+ε) · A_t)`

InstructGPT ran PPO with ~31k prompts from a customer API dataset, iterating until
preference evaluation plateaued.

---

## Failure modes

### Reward hacking

The policy finds high-scoring outputs that don't reflect genuine quality. Common
manifestations:
- **Verbosity**: longer responses score higher on surface features
- **Sycophancy**: responses that agree with the prompt's framing regardless of accuracy
- **Mode collapse**: repetitive, formulaic outputs that score consistently

**Mechanism:** The reward model is an imperfect proxy for human preference. It was
trained on a finite dataset and generalizes imperfectly. The RL optimizer finds
out-of-distribution inputs that exploit this gap. See: [reward hacking patterns](../01-llm-fundamentals/rl.md#risks).

### Overoptimization

PPO is run too long or with too large a KL coefficient. The policy drifts far from the
SFT initialization, into regions where the reward model's scores are unreliable.

**The reward model's accuracy degrades as the policy diverges from the distribution
it was trained on.** The KL penalty is the primary mitigation — it bounds how far the
policy can drift from SFT.

Anthropic (2022) showed reward model score vs. KL divergence follows an inverse-U curve:
initial optimization improves true quality; past the peak, reward score continues rising
while actual quality degrades.

### Alignment tax

RLHF can reduce performance on capability benchmarks (coding, math, reasoning) while
improving alignment metrics. InstructGPT noted a ~15% drop on some academic NLP tasks.
Modern approaches (Constitutional AI, DPO with curated datasets) work to reduce this.

---

## Practical considerations

**Scale of human data required:**
- SFT: thousands of demonstrations (InstructGPT: 13k)
- RM training: tens of thousands of comparisons (InstructGPT: 33k)
- PPO rollouts: large (automated via RM once trained)

**Compute:**
- PPO requires four models simultaneously: policy, reference (frozen SFT), reward model,
  value function. Memory cost is ~4x the base model.
- This is a primary motivation for DPO — eliminates the reward model and value function.
  See [preference-optimization.md](preference-optimization.md).

**Dataset quality dominates.** InstructGPT's team found labeler quality (consistency,
calibration, demographic diversity) mattered more than volume. Biases in labeler pool
propagate directly into the reward model.

---

## Connection to Constitutional AI

Constitutional AI (Anthropic, 2022) extends RLHF by replacing human preference labels
with AI-generated critiques guided by a written constitution. RLAIF (RL from AI Feedback)
runs the same three-stage pipeline but uses AI feedback at Stage 2 instead of human
raters. This scales alignment without proportional human labor.

See [constitutional-ai.md](constitutional-ai.md) for the full pipeline.

---

## Cross-links

- **Upstream:** [01-llm-fundamentals/rl.md](../01-llm-fundamentals/rl.md) — RL foundations
  (MDP, policy, reward function), MARL, RL-in-RAG
- **Algorithms:** [preference-optimization.md](preference-optimization.md) — PPO vs DPO
  vs GRPO: the algorithm evolution from RLHF through offline preference optimization
- **Constitutional AI:** [constitutional-ai.md](constitutional-ai.md) — RLAIF and
  AI-generated feedback at scale
- **Papers in repo:** [`2-llm-rlhf/2203.02155v1.pdf`](2-llm-rlhf/2203.02155v1.pdf)
  (InstructGPT), [`2-llm-rlhf/2303.08774v6.pdf`](2-llm-rlhf/2303.08774v6.pdf) (GPT-4)
