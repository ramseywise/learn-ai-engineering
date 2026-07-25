# Preference Optimization Algorithms

> **Pillar:** [05-RL](README.md)
> **Presumes:** [RLHF pipeline](rlhf-pipeline.md) — understand the three-stage baseline first
> **Papers:** DPO (2305.18290), DeepSeek-R1 (2501.12948), GRPO (2402.03300)

---

## The algorithm evolution

The alignment field has moved steadily toward simpler, cheaper, more stable optimization:

```
RLHF (2017–2022)
  PPO with explicit reward model + value function
      |
      | DPO (2023): "we don't need the reward model"
      v
  Direct preference optimization on (prompt, chosen, rejected) triples
      |
      | GRPO (2024): "we don't need the critic either"
      v
  Group-based advantage estimation, no separate value network
      |
      v
  KTO, IPO, ORPO: further simplifications for specific settings
```

Each step removed a component that was expensive, unstable, or hard to tune — while
preserving (or improving) alignment quality.

---

## PPO — Proximal Policy Optimization

**Role in RLHF:** The original RL optimizer. Still the most theoretically grounded
and the one used in InstructGPT, GPT-4, and Claude v1.

**What it is:** An on-policy actor-critic algorithm with a clipped surrogate objective.
During RLHF, PPO treats the LLM as a policy, each generated token as an action, and the
reward model's scalar score as the environment reward.

**Objective:**

```
L_PPO(θ) = E[min(r_t(θ) · A_t, clip(r_t(θ), 1-ε, 1+ε) · A_t)]
```

where `r_t(θ) = π_θ(a_t|s_t) / π_θ_old(a_t|s_t)` is the probability ratio between new
and old policy, and `A_t` is the advantage estimate from the value function.

**In LLM RLHF context:**

```
L_total = L_PPO + β · KL[π_θ || π_SFT] + γ · L_pretrain
```

The KL term prevents policy collapse away from the SFT initialization. The pretrain
term (optional) preserves general capability.

**What PPO requires:**
- Trained reward model (separate neural network)
- Value function / critic (usually another copy of the LLM with a scalar head)
- Online rollouts: policy generates responses, reward model scores them, optimizer updates

**Memory cost:** Four models running simultaneously — policy, reference SFT, reward model,
value function. For a 7B model: ~28GB at 4-bit quantization, more in practice.

**Strengths:** Theoretically sound, stable with proper KL tuning, handles complex reward
landscapes, supports online learning (can improve reward model iteratively).

**Weaknesses:** Expensive (4x model memory), requires careful hyperparameter tuning
(ε clipping, KL coefficient β), sensitive to reward model quality, training instability
common at scale.

---

## DPO — Direct Preference Optimization

**Paper:** Rafailov et al., 2023 (arXiv: 2305.18290). Currently at `2-llm-rlhf/2305.18290v3.pdf`.

**The insight:** The RLHF objective (maximize reward subject to KL constraint) has a
closed-form optimal policy. DPO reparameterizes the reward model in terms of the policy
itself, eliminating the need to train a separate reward model.

**The closed-form connection:**

Given the RLHF objective `max_π E[r(x,y)] - β·KL[π||π_ref]`, the optimal policy is:

```
π*(y|x) = π_ref(y|x) · exp(r*(x,y)/β) / Z(x)
```

where `Z(x)` is the partition function. Rearranging:

```
r*(x,y) = β · log(π*(y|x) / π_ref(y|x)) + β · log Z(x)
```

DPO plugs this into the Bradley-Terry preference model and cancels the intractable `Z(x)`:

**DPO training objective:**

```
L_DPO(θ) = -E[(x, y_w, y_l) ~ D] [
    log σ( β · log(π_θ(y_w|x) / π_ref(y_w|x))
          - β · log(π_θ(y_l|x) / π_ref(y_l|x)) )
]
```

The model is trained to assign higher log-probability to preferred responses relative to
the reference model, and lower log-probability to rejected responses — without ever
explicitly scoring either.

**What DPO removes:** The reward model. No separate RM training, no RM inference during
optimization, no online rollouts.

**What DPO requires:**
- A reference model `π_ref` (typically the SFT model, frozen)
- Offline preference dataset: `(prompt, chosen_response, rejected_response)` triples
- Standard supervised training loop — no RL required

**Strengths:** 2x cheaper than PPO (two models: policy + frozen reference), more stable
training, no reward hacking through the reward model, simpler to implement.

**Weaknesses:** Offline only — can't incorporate new feedback during training. Sensitive
to dataset quality (bad preferred/rejected pairs have direct gradient impact). Can
increase probability of rejected responses in some settings (the "DPO length problem").
Does not generalize beyond the preference distribution seen in training.

**When to use DPO:** You have a clean preference dataset, want stability over online
exploration, and can't afford PPO compute. The dominant choice in industry for RLHF
at moderate scale.

---

## GRPO — Group Relative Policy Optimization

**Paper:** DeepSeek-Math (arXiv: 2402.03300), operationalized in DeepSeek-R1 (arXiv: 2501.12948).

**The insight:** For tasks with verifiable outcomes (math proofs, code execution, formal
logic), you don't need a trained reward function — you can compute rewards directly. And
you don't need a separate value network if you estimate advantages from a group of
sampled outputs.

**Algorithm:**
1. For each prompt `x`, sample a group of `G` outputs: `{y_1, y_2, ..., y_G}`
2. Compute rewards `{r_1, ..., r_G}` (rule-based: correctness check, format check)
3. Normalize within the group: `A_i = (r_i - mean(r)) / std(r)`
4. Update policy to increase probability of outputs with positive normalized advantage

**GRPO objective:**

```
L_GRPO(θ) = -E[
    (1/G) · Σ_i [ min(r_t,i(θ) · A_i, clip(r_t,i(θ), 1-ε, 1+ε) · A_i) ]
] + β · KL[π_θ || π_ref]
```

where `r_t,i(θ)` is the token-level probability ratio for output `i`.

**What GRPO removes:** The critic / value function. Advantages come from within-group
comparison rather than a trained value estimator. This eliminates the fourth model PPO
needs, cutting memory cost by ~25%.

**Verifiable rewards in DeepSeek-R1:**
- Math: output passes/fails formal verification (exact answer match, proof checker)
- Code: output executes and passes test cases
- Format: output follows required structure (chain-of-thought format, response tags)

These rule-based rewards require no human labeling and scale to arbitrary volume.

**Strengths:** No critic to train (simpler, cheaper), verifiable rewards eliminate reward
hacking entirely for applicable tasks, enables large-scale online RL for reasoning,
demonstrated at scale (DeepSeek-R1 achieves o1-level math reasoning).

**Weaknesses:** Requires verifiable reward structure — not applicable to open-ended
generation (summarization, helpfulness). Group sampling increases inference cost per
training step. Normalizing within-group rewards can struggle with uniform groups
(all correct or all incorrect).

**When to use GRPO:** Reasoning tasks with verifiable outcomes (math, code, logic).
Not appropriate for general instruction following or alignment training.

---

## Variants and extensions

### KTO — Kahneman-Tversky Optimization

**Paper:** Ethayarajh et al., 2023. Named after prospect theory (Kahneman-Tversky).

**Motivation:** DPO requires paired (chosen, rejected) examples. KTO works with unpaired
binary feedback — just labels of "desirable" or "undesirable" for individual outputs.
This matches how feedback often arrives in practice.

**Objective:** Maximizes the "human utility" of model outputs using a utility function
that down-weights extreme rewards (mirroring how humans actually value outcomes).

**When to use:** When preference pairs are hard to collect but binary thumbs-up/thumbs-down
signals are abundant. More data-efficient than DPO when pairs are scarce.

### IPO — Identity Preference Optimization

**Motivation:** DPO can overfit — the policy collapses to assigning zero probability to
rejected responses. IPO modifies the objective to directly minimize the squared difference
between model preference and a target margin, preventing collapse.

**When to use:** When DPO training is unstable or collapses to mode-dropping behavior.

### ORPO — Odds Ratio Preference Optimization

**Motivation:** Eliminates the reference model. ORPO integrates the preference objective
directly into the SFT loss using an odds ratio term, so you train once (not SFT-then-DPO).

**Objective:**

```
L_ORPO = L_SFT - λ · log σ( log(odds_θ(y_w|x) / odds_θ(y_l|x)) )
```

where `odds_θ(y|x) = π_θ(y|x) / (1 - π_θ(y|x))`.

**When to use:** Compute-constrained settings where running SFT and then DPO is too
expensive. Trades some alignment quality for efficiency (no reference model inference).

---

## Decision framework

| Property | PPO | DPO | GRPO | KTO | ORPO |
|----------|-----|-----|------|-----|------|
| Needs reward model | Yes | No | No (rule-based) | No | No |
| Needs reference model | Yes (SFT) | Yes (SFT) | Yes (SFT) | Yes (SFT) | No |
| Needs value function | Yes | No | No | No | No |
| Online / offline | Online | Offline | Online | Offline | Offline |
| Requires paired data | Yes | Yes | No (verifiable) | No | Yes |
| Memory cost | 4x model | 2x model | 3x model | 2x model | 1x model |
| Reward hacking risk | High | Low | None (verifiable) | Low | Low |
| Best for | General alignment, complex tasks | General alignment, stable training | Reasoning (math/code) | Unpaired feedback | Compute-constrained |

**Practitioner heuristics:**
1. **Start with DPO.** It's cheaper, more stable, and works well for most instruction
   following and general alignment tasks. Requires a clean preference dataset.
2. **Use PPO when you need online learning.** If the task distribution shifts (online
   deployment, iterative labeling), PPO can adapt. DPO cannot.
3. **Use GRPO for verifiable reasoning tasks.** Math, code, logic — anything where
   you can compute a reward without a human. DeepSeek-R1 is the existence proof.
4. **Consider KTO when pairs are scarce.** Binary feedback (thumbs up/down) is easier
   to collect than ranked pairs. If your feedback data is unpaired, KTO is the right tool.
5. **ORPO for single-stage training.** If you can't run SFT + DPO sequentially (cost,
   latency), ORPO collapses them into one pass.

---

## The DeepSeek-R1 story

DeepSeek-R1 (2025) demonstrated that pure RL with verifiable rewards can develop
emergent chain-of-thought reasoning — the model learned to "think" (producing long
reasoning traces) without any explicit CoT supervision.

Key findings:
- GRPO with math verification rewards alone produces models that spontaneously develop
  self-verification, backtracking, and extended reasoning
- Scaling RL (not model size) is the key lever for reasoning improvement
- The "aha moment": the model learns to allocate more computation to hard problems

This validated the verifiable rewards paradigm and shifted the field's attention from
"what alignment technique" to "what reward structure."

---

## Cross-links

- **Baseline:** [rlhf-pipeline.md](rlhf-pipeline.md) — the three-stage PPO pipeline these
  algorithms evolved from
- **Constitutional AI:** [constitutional-ai.md](constitutional-ai.md) — RLAIF as an
  alternative feedback source (still uses PPO or DPO at the optimization step)
- **RL foundations:** [../01-llm-fundamentals/rl.md](../01-llm-fundamentals/rl.md) — MDP
  framing, value functions, policy gradients
- **Papers in repo:** [`2-llm-rlhf/2305.18290v3.pdf`](2-llm-rlhf/2305.18290v3.pdf) (DPO)
- **External:** DeepSeek-R1 (arXiv: 2501.12948), GRPO (arXiv: 2402.03300)
