---
origin: web-authored
sources:
  - https://arxiv.org/abs/2503.14476
  - https://arxiv.org/abs/2305.18290 (DPO)
  - https://arxiv.org/abs/2402.03300 (DeepSeekMath / GRPO)
  - https://arxiv.org/abs/2501.12948 (DeepSeek-R1)
  - https://arxiv.org/abs/2402.01306 (KTO)
  - https://arxiv.org/abs/2506.21495 (offline vs semi-online vs online DPO/GRPO)
  - https://arxiv.org/abs/2503.01067 (All Roads Lead to Likelihood)
  - https://arxiv.org/abs/2504.13837 (RLVR and the base model's reasoning boundary)
  - https://arxiv.org/abs/2507.18071 (GSPO)
  - https://arxiv.org/abs/2501.12599 (Kimi k1.5)
  - https://arxiv.org/abs/2503.24290 (Open-Reasoner-Zero)
  - https://arxiv.org/abs/2505.07608 (MiMo-7B)
  - https://arxiv.org/abs/2504.21801 (DeepSeek-Prover-V2)
  - Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), ch. 6
  - Koenigstein, AI Agents: The Definitive Guide (O'Reilly, 2026), ch. 3
confidence: medium
cleaned: 2026-10-31
---

# 3 — Preference Optimization Algorithms

> **Pillar:** [05-RL](../README.md)
> **Presumes:** [RLHF pipeline](02-rlhf-pipeline.md) — understand the three-stage baseline first
> **Papers:** DPO (2305.18290), DeepSeek-R1 (2501.12948), GRPO (2402.03300), GSPO (2507.18071)
> **Books:** Iusztin & Labonne, *LLM Engineer's Handbook*, ch. 6; Koenigstein, *AI Agents: The Definitive Guide*, ch. 3 (see [references](../references.md#books))

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
  KTO, IPO, ORPO, SimPO: further simplifications for specific settings
  SPIN, SPPO: self-play, with the model's own samples as the opponent
```

Each step removed a component that was expensive, unstable, or hard to tune — while
preserving (or improving) alignment quality.

---

## PPO — Proximal Policy Optimization

**Role in RLHF:** The original RL optimizer. Still the most theoretically grounded
and the one used in InstructGPT, GPT-4, and Claude v1.

**What it is:** An on-policy actor-critic algorithm with a clipped surrogate objective.
During RLHF, PPO treats the LLM as a policy, each generated token as an action, and the
reward model's scalar score as the environment reward. Because it is on-policy, the ratio and clip
correct for the policy going stale across the K epochs spent on one batch. See
[01](01-rl-foundations.md#policy-gradients-from-reinforce-to-the-ppo-clip) for the clip plot and
where the gradient vanishes.

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

**PPO on a verifiable reward predates R1.** ReFT ran PPO after an SFT warm-up, with the reward
taken from the final answer alone and no reward model
([arXiv:2401.08967](https://arxiv.org/abs/2401.08967) (Luong et al., ACL 2024)). The training
questions were the same ones SFT used. On GSM8K with CodeLLaMA-7B and GPT-3.5-written CoT, it
raised accuracy from 43.6% to 53.3% (natural-language CoT) and from 63.7% to 75.3% (program
CoT). It needed more epochs than SFT. It also **reward-hacked multiple-choice MathQA**: with only
A–E as the answer space, a wrong chain that lands on the right letter still gets full reward.

**Much of PPO's machinery may be unnecessary for LLM RLHF.** Ahmadian et al.
([arXiv:2402.14740](https://arxiv.org/abs/2402.14740) (Ahmadian et al., ACL 2024)) trained
Pythia-6.9B and Llama-7B on Anthropic-HH and TL;DR. The clip was active on fewer than 5% of
samples per batch, and removing the clip, and then the ratio, did not hurt. **RLOO with k = 4
samples beat PPO by 10.3–32.1 GPT-4-judged win-rate points, and also beat DPO and RAFT.**
Because the pretrained policy already starts close to good, low-variance REINFORCE over whole
completions is enough ([01](01-rl-foundations.md#policy-gradients-from-reinforce-to-the-ppo-clip)).

---

## DPO — Direct Preference Optimization

**Paper:** Rafailov et al., 2023 (arXiv: 2305.18290). [arXiv:2305.18290](https://arxiv.org/abs/2305.18290); local copy indexed in [references.md](../references.md#core-papers).

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

**The paper's evidence** is at small scale, with models up to 6B parameters. On TL;DR
summarization, starting from the same GPT-J SFT model, DPO won about 61% of GPT-4-judged
comparisons against the reference summaries, PPO 57% at its best temperature. In a human
evaluation, DPO samples were preferred over PPO's 58% of the time. PPO degraded to base-model
quality at high sampling temperatures while DPO held up. The authors validated GPT-4 as judge
with a human study. DPO's β was barely tuned.

**Weaknesses:** Offline as published — it trains on a fixed set of pairs and can't
incorporate new feedback during training. That is a property of the data pipeline, not the
loss: the same DPO loss run on fresh samples from the current model works well (heuristic 2). Sensitive
to dataset quality (bad preferred/rejected pairs have direct gradient impact). Can
increase probability of rejected responses in some settings (the "DPO length problem";
SimPO, [below](#simpo--no-reference-model-length-normalized-reward), measures it).
Does not generalize beyond the preference distribution seen in training.

**When to use DPO:** You have a clean preference dataset, want stability over online
exploration, and can't afford PPO compute. The dominant choice in industry for RLHF
at moderate scale.

### DPO in practice

LLMEH runs DPO with TRL and Unsloth on top of its own SFT model (*LLM Engineer's Handbook*,
ch. 6). The goal was a style change: make answers sound like the authors' blog. The
practical points:

- **β sets how hard the reference pulls.** 0.1 is the most common value. The authors raised it
  to **0.5** because lower β made the model formal and wordy. Their warning: "DPO tends to make
  models more verbose and pushes them to use very formal language." That is the length
  problem above, seen in a real run.
- **With LoRA, the reference model is free.** Only the adapters train, so the base weights
  with the adapters switched off *are* `π_ref`. Pass `ref_model=None` and load one model, not two.
- **Learning rate is about 100× lower than SFT:** 2e-6, against 3e-4 for their LoRA SFT. One
  epoch, not three.
- **How many pairs:** see the table in [02](02-rlhf-pipeline.md#stage-2--reward-model-training).
  Task-level style or refusal changes need 100–10k.

```python
trainer = DPOTrainer(
    model=model, ref_model=None,        # LoRA: base without adapters is the reference
    beta=0.5,                            # 0.1 is the usual default
    train_dataset=ds["train"], eval_dataset=ds["test"],
    args=DPOConfig(learning_rate=2e-6, num_train_epochs=1,
                   per_device_train_batch_size=2, gradient_accumulation_steps=8),
)
```

That run used Llama 3.1 8B with r = α = 64 and 1,467 pairs. Recent TRL versions take `beta`
inside `DPOConfig` and `processing_class` in place of `tokenizer`, so check the API of the
version you install.

**What to watch.** TRL logs these metrics, and the book says how to read them:

| Metric | Healthy | Warning sign |
|---|---|---|
| `rewards/chosen`, `rewards/rejected` | β × log-ratio against the reference. The gap between them widens | Both falling (rejected probabilities can drop *and* chosen ones too) |
| `rewards/margins` | Rises quickly, then plateaus | Flat from the start |
| `rewards/accuracies` | Climbs gradually; need not reach 100% | 100% early means the pairs are too easy. Add harder ones |
| Train vs. val loss, grad norm | Small gap; small norms with few spikes | — |

*Dated:* LLMEH (2024) treats DPO as offline only and says "for large-scale training runs
with millions of preference samples, PPO-inspired methods still have a higher performance
ceiling". The ceiling turned out to come mainly from **online sampling, not from PPO**.
Semi-online and online DPO match GRPO on math and beat offline DPO by about 30 points on
AlpacaEval (heuristic 2 below).

Zephyr-7B shows DPO's place in a distilled pipeline
([arXiv:2310.16944](https://arxiv.org/abs/2310.16944) (Tunstall et al., COLM 2024)).
Mistral-7B was first fine-tuned on 200k filtered UltraChat dialogues. It was then trained with
DPO on UltraFeedback pairs scored by GPT-4. It reached 7.34 on MT-Bench, against 6.86 for
Llama-2-Chat-70B, with no human labels and a few hours on 16 A100s. **DPO without the SFT stage
collapsed (4.76). SFT on the chosen responses alone was worse than DPO on the same pairs (6.19
vs 7.00).** DPO overfit to 100% training accuracy after one epoch without hurting MT-Bench.
Three DPO epochs on a one-epoch SFT model worked best, and a longer SFT made extra DPO regress.
The judge was GPT-4, which favours models distilled from it.

---

## GRPO — Group Relative Policy Optimization

**Paper:** DeepSeek-Math ([arXiv:2402.03300](https://arxiv.org/abs/2402.03300)), operationalized in DeepSeek-R1 (arXiv: 2501.12948).

**The insight:** you don't need a separate value network if you estimate advantages from
a group of sampled outputs; the group mean is a REINFORCE baseline
([01](01-rl-foundations.md#policy-gradients-from-reinforce-to-the-ppo-clip)). That is GRPO's whole contribution in DeepSeekMath, and it still
used a *trained* reward model there, both outcome and process supervision, with the reward
model retrained during RL on a replay buffer. Dropping the reward model in favour of rule-based
checks (answer correct? format right?) came with DeepSeek-R1. Together the two make
the now-standard recipe for verifiable tasks: no critic and no learned reward.

The DeepSeekMath result: GRPO on top of the 7B instruct model, using only GSM8K- and
MATH-style chain-of-thought prompts, raised GSM8K from 82.9% to 88.2% and MATH from 46.8%
to 51.7%. Out-of-domain benchmarks improved too.

**Algorithm:**
1. For each prompt `x`, sample a group of `G` outputs: `{y_1, y_2, ..., y_G}`
2. Compute rewards `{r_1, ..., r_G}` (R1-style rule-based: correctness check, format check; or a reward model, as in DeepSeekMath)
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
needs. The value model is usually the same size as the policy, so the saving is roughly
one policy-sized model's weights, gradients and optimizer state.

**Verifiable rewards in DeepSeek-R1:**
- Math: output passes/fails formal verification (exact answer match, proof checker)
- Code: output executes and passes test cases
- Format: output follows required structure (chain-of-thought format, response tags)

These rule-based rewards require no human labeling and scale to arbitrary volume.

They are only as sound as the checker, and these cases show it:

- **DeepSeek-Prover-V2.**
  - The setup: GRPO with a binary Lean-verifier reward, on subgoal-decomposed cold-start data
    from DeepSeek-V3. The 671B prover reached 61.9% pass@1 and 88.9% pass@8192 on
    miniF2F-test. It builds on DeepSeek-Prover v1, which reached 46.3% on miniF2F-test
    (pass@64) through expert iteration over 8M autoformalized Lean statements
    ([arXiv:2405.14333](https://arxiv.org/abs/2405.14333) (Xin et al., 2024-05, preprint)).
  - Its v2 retracted 13 PutnamBench "solves" by the 7B model. They exploited a Lean 4.9.0 bug
    in which `apply?` fails to emit `sorry`
    ([arXiv:2504.21801](https://arxiv.org/abs/2504.21801) (Ren et al., 2025-04)).
- **MiMo-7B.** RL from the base model "tends to hack the reward for mathematics problems".
- **Production coding environments** have been gamed by overriding `__eq__` and by patching
  pytest ([05](05-post-training-for-agents.md#practical-pitfalls)).

**Strengths:** No critic to train (simpler, cheaper), verifiable rewards remove the learned-RM
loophole (though an agent can still game the verifier itself, for example by editing the
tests it must pass; see [RLVP](05-post-training-for-agents.md#rlvp-reward-the-outcome-penalize-the-path)), enables large-scale online RL for reasoning,
demonstrated at scale (DeepSeek-R1 matches o1-1217 on AIME 2024 and MATH-500; see [below](#the-deepseek-r1-story)).

**Weaknesses:** Requires verifiable reward structure — not applicable to open-ended
generation (summarization, helpfulness). Group sampling increases inference cost per
training step. Normalizing within-group rewards can struggle with uniform groups
(all correct or all incorrect): zero variance means zero advantage and no gradient. DAPO
drops those groups (dynamic sampling). RLVP gives them variance back with verifiable path
penalties. HERO gives them variance back with a reward model, but bounded inside the
verifier's bands: RM scores are min-max scaled to [−α, α] for wrong answers and [1−β, 1+β]
for right ones. With α + β < 1, a wrong answer can never outscore a right one
([arXiv:2510.07242](https://arxiv.org/abs/2510.07242) (Tao et al., 2025-10, preprint)).
Qwen3-4B-Base was trained on 2k easy-to-verify OpenMathReasoning problems. On four
verifiable math benchmarks HERO averaged 62.0, against 58.3 for verifier-only and 56.4 for
RM-only. On two hard-to-verify sets judged by GPT-4o, it scored 66.3 against 57.1 and 54.6.
Credit assignment is also coarse: one trajectory-level advantage is spread
evenly over every token, which dilutes the signal over long multi-turn episodes, where
PPO with a value network still earns its cost. DAPO's four fixes (Clip-Higher,
token-level loss, dynamic sampling, overlong shaping) are tabulated in
[post-training-for-agents.md](05-post-training-for-agents.md#rl-for-tool-calling). Clip-Higher
answers entropy collapse under symmetric clipping: raising only ε_high lets low-probability tokens
gain mass ([arXiv:2503.14476](https://arxiv.org/abs/2503.14476) (Yu et al., NeurIPS 2025)).
The setup was Qwen2.5-32B base, DAPO-Math-17K, a ±1 answer reward, no KL, and ε 0.2/0.28.
DAPO added the fixes one at a time, in a single order, and scored each step on AIME 2024
avg@32. Naive GRPO scored 30. Overlong filtering raised it to 36, Clip-Higher to 38, soft
overlong punishment to 41, token-level loss to 42, and dynamic sampling to 50. **Dynamic
sampling, the last step, gave the biggest gain in this order.** It drops only prompts whose accuracy is
exactly 0 or 1 and refills the batch. The overlong penalty applies only to responses between
16k and 20k tokens. The 50 beat DeepSeek-R1-Zero-Qwen-32B's 47 "with 50% training steps", but
the two runs used different evaluation settings.

**Several rewards break the group normalization.** Summing the rewards first and then
normalizing within the group merges different reward combinations. With two binary rewards
and two rollouts, totals of (0,1), (0,2) and (1,2) all become advantages (−0.71, +0.71).
GDPO normalizes each reward within the group, sums them, then normalizes over the batch
([arXiv:2601.05242](https://arxiv.org/abs/2601.05242) (Liu et al., 2026-01, preprint)).
For tool calling on Qwen2.5-1.5B-Instruct, GDPO scored 32.8 average accuracy on BFCL-v3,
against 30.2 for GRPO (5 runs). On math, both GDPO and GRPO were trained with a 4k-token length reward, and both
**lost AIME accuracy against the untrained model** while cutting length violations. On
DeepSeek-R1-1.5B, AIME went 29.8 base, 23.1 GRPO, 29.4 GDPO. So "beats GRPO" is not "beats
the starting point". Reward weights did not reliably set priorities when the objectives
differed in difficulty. Making the easy reward conditional on the hard one worked better.

**GRPO needs per-token log-probabilities.** Masked diffusion LMs do not factorize left to
right, so they cannot supply them directly. d1
([arXiv:2504.12216](https://arxiv.org/abs/2504.12216) (Zhao et al., 2025-04, preprint))
estimates them with a mean-field decomposition and a single unmasking pass under a random
prompt mask. On LLaDA-8B-Instruct, this diffu-GRPO beat SFT in all 12 task and length setups.
SFT followed by RL took Countdown from 20.7% to 42.2%.

**When to use GRPO:** Reasoning tasks with verifiable outcomes (math, code, logic).
Not appropriate for general instruction following or alignment training.

### GSPO — sequence-level ratios

**Paper:** Zheng et al. (Qwen team), "Group Sequence Policy Optimization"
([arXiv:2507.18071](https://arxiv.org/abs/2507.18071) (Zheng et al., 2025-07, preprint)).
The paper says GSPO "contributed to" the *latest* Qwen3 models, which is not the same as saying
it trained the original Qwen3. Summarized in *AI Agents: The Definitive Guide*, ch. 3.

GRPO gives every token in a response the same advantage, but still computes and clips the
importance ratio **per token**. In a long response those per-token ratios fluctuate
independently and their noise adds up. GSPO argues that because the reward belongs to the
whole sequence, the ratio and the clipping should too. It replaces the token ratio with a
length-normalized **sequence** ratio:

```
s_i(θ) = ( π_θ(y_i | x) / π_θ_old(y_i | x) ) ^ (1/|y_i|)

L_GSPO(θ) = -E[ (1/G) · Σ_i min( s_i(θ) · A_i, clip(s_i(θ), 1-ε, 1+ε) · A_i ) ]
```

`A_i` is the same group-normalized advantage as GRPO. The 1/|y| exponent is a geometric
mean over tokens, which keeps long responses from producing extreme ratios. Clipping then
keeps or drops whole responses, not individual tokens.

![GSPO: sample prompts, generate full sequences, compute sequence rewards and relative comparisons, and combine them with a KL divergence estimated over the full sequence. All clipping and optimization act on the sequence likelihood.](../sources/images/ai-agents-definitive-guide-fig3-3.png)
*Image Source: Nicole Koenigstein, *AI Agents: The Definitive Guide* (O'Reilly, 2026), Fig. 3-3*

The two claims in favour of GSPO (Zheng et al.; the book repeats them):

- More stable on long outputs and on mixture-of-experts models. With GRPO, the experts a token
  routes to can change between the old and new policy, so per-token ratios swing. The Qwen
  team needed "routing replay" to stabilize GRPO on MoE; GSPO did not.
- Sequence likelihoods from the inference engine can be reused, so less recomputation in the
  trainer.

*Read with care:* both claims come from the team that built GSPO and trained Qwen3 with it.
The evidence is thin. It consists of training curves on one cold-start model from
Qwen3-30B-A3B-Base, scored on AIME'24 avg@32, LiveCodeBench and CodeForces, with no tables and
no seeds. The baseline was GRPO *with* routing replay. GSPO clips at 3e-4/4e-4 on the sequence
ratio, against 0.2/0.27 for GRPO's token ratio. It clipped 15% of tokens against GRPO's 0.13%,
yet trained more efficiently. In that 48-layer MoE, about 10% of the activated experts changed
after each update.
The book's comparison table also says GRPO "needs value-model surrogates" for MoE stability.
GRPO has no value model; the MoE fix the GSPO paper describes is routing replay. The choice is
a stability and infrastructure question for long-output or MoE training, not a new kind of
objective. DAPO's token-level loss (in [05](05-post-training-for-agents.md#rl-for-tool-calling))
moves the other way, toward weighting each token equally, so practice has not settled on one
granularity.

**Who needs what** (adapted from *AI Agents: The Definitive Guide*, Table 3-2):

| Method | Reference policy | Reward signal | Critic | Unit of the ratio / loss |
|---|---|---|---|---|
| PPO (RLHF) | Frozen SFT model | Learned reward model | Yes | Token, with GAE advantages |
| DPO | Frozen reference | None at train time: offline chosen/rejected pairs | No | Sequence, pairwise |
| GRPO | Often a frozen reference | Reward function, verifier or LLM judge | No | Token ratio, group-normalized advantage |
| GSPO | Often a frozen reference | Same as GRPO | No | Sequence ratio, group-normalized advantage |
| RLOO | Often a frozen reference | Reward model or verifier | No | Sequence; baseline is the mean of the other k−1 rewards (Kool et al. 2019; Ahmadian et al. 2024) |

---

## Variants and extensions

### KTO — Kahneman-Tversky Optimization

**Paper:** [arXiv:2402.01306](https://arxiv.org/abs/2402.01306) (Ethayarajh et al., 2024-02),
ICML 2024. Named after prospect theory (Kahneman-Tversky).

**Motivation:** DPO requires paired (chosen, rejected) examples. KTO works with unpaired
binary feedback — just labels of "desirable" or "undesirable" for individual outputs.
This matches how feedback often arrives in practice.

**Objective:** Maximizes the "human utility" of model outputs using a utility function
that down-weights extreme rewards (mirroring how humans actually value outcomes). Concretely,
an example's gradient goes to zero once its implied reward is far from the reference point in
either direction, so KTO stops learning from examples the policy finds too easy or too hard.
The authors read that as ignoring likely-mislabelled feedback, at the risk of underfitting
hard-but-correct data (their fix: lower β, more epochs).

**When to use:** When preference pairs are hard to collect but binary thumbs-up/thumbs-down
signals are abundant. More data-efficient than DPO when pairs are scarce. Trained on
HH+OASST+SHP and judged by GPT-4 winrate against the SFT targets, KTO matched or beat DPO from
Pythia-1.4B to Llama-30B. On Zephyr-β-SFT trained on UltraFeedback it raised GSM8K from 40.0
(DPO) to 53.5, and on Llama-7B it still beat DPO with "up to 90% of the desirable data"
discarded. At Llama-13B and 30B, KTO without SFT was competitive with SFT+KTO, while DPO
always needed SFT first. The authors' own limit: "if your preference data has sufficiently little noise and
sufficiently little intransitivity, then DPO will work better."

### IPO — Identity Preference Optimization

**Motivation:** DPO can overfit — the policy collapses to assigning zero probability to
rejected responses. IPO modifies the objective to directly minimize the squared difference
between model preference and a target margin, preventing collapse
([arXiv:2310.12036](https://arxiv.org/abs/2310.12036) (Azar et al., AISTATS 2024)).

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

The SFT term also works as a regularizer when the pairs are noisy. In weak-to-strong
reasoning, Llama2-70b (LoRA) built its own pairs: no gold labels, its majority-vote answer
against a weak model's solution
([arXiv:2407.13647](https://arxiv.org/abs/2407.13647) (Yang et al., Findings of EMNLP 2024)).
On MATH, DPO on those pairs lowered accuracy by 1.4–2.6 points across three weak supervisors.
ORPO raised it by 1.0–2.2, from a base of about 14%. On GSM8K both helped, by 2.6–8.5 points.

### SimPO — no reference model, length-normalized reward

**Paper:** [arXiv:2405.14734](https://arxiv.org/abs/2405.14734) (Meng et al., NeurIPS 2024).

SimPO replaces DPO's implicit reward, the log-ratio against `π_ref`, with the policy's own
**average** log-probability per token. It adds a target margin γ:

```
L_SimPO = -log σ( β/|y_w| · log π_θ(y_w|x) - β/|y_l| · log π_θ(y_l|x) - γ )
```

On AlpacaEval 2 LC (GPT-4 Turbo judge), from the same SFT models, SimPO beat DPO 21.5 to 15.1
on Mistral-7B-Base (UltraFeedback) and 44.7 to 40.3 on Llama-3-8B-Instruct. The Instruct setup
used near-on-policy pairs, sampled from the SFT model and ranked by PairRM. Read the name with
care:

- **The gain comes from length normalization, not from dropping the reference.** In the
  Mistral-Base ablation, SimPO without normalization scored 11.9 LC, below DPO's 15.1. With
  γ = 0 it still scored 16.8. Without normalization, likelihood tracks length (Spearman ρ
  0.82, against 0.59 for DPO and 0.34 for SimPO).
- **"Reference-free" means there is no reference in the loss.** Training still starts from an
  SFT model and has no KL term. A small learning rate is what keeps the policy near its start,
  and the authors warn this "could potentially lead to reward hacking".
- **The saving is small.** It runs about 20% faster and uses 10% less memory than vanilla DPO.
  DPO matches that if the reference log-probs are precomputed.
- **Forgetting is a real cost.** The released Llama-3-8B-Instruct-SimPO reached 53.7 LC, but
  GSM8K fell from 78.5 to 57.4 and MMLU from 61.7 to 54.9. On Gemma-2-9B-it, GSM8K held, and
  SimPO beat DPO 72.4 to 67.8 LC.

Arena-Hard has no length control, so read its gains next to response length. The comparisons
are offline only, with no online DPO or PPO baseline. β of 2–2.5 and γ of 0.5–1.5 need tuning.

### Self-play: SPIN, SPPO, DITTO

These methods build pairs from the model's own samples, round after round. They differ in what
counts as "chosen".

**SPIN** ([arXiv:2401.01335](https://arxiv.org/abs/2401.01335) (Chen et al., ICML 2024)) uses
the human SFT response as chosen and the previous iterate's sample as rejected. It needs no
preference labels at all. On zephyr-7b-sft-full with 50k UltraChat prompts, the Open LLM
Leaderboard average went from 58.14 to 63.16 after four iterations (iterations 0–3). zephyr-7b-dpo-full, trained
on 62k GPT-4-labelled UltraFeedback pairs, scored 61.31. A further SFT epoch scored 57.23. That
leaderboard tests knowledge and reasoning, not chat preference. The gains shrank toward zero
by iteration 3, as the theory predicts: SPIN converges to the SFT data distribution, so it can
only be as good as that data.

**SPPO** ([arXiv:2405.00675](https://arxiv.org/abs/2405.00675) (Wu et al., ICLR 2025)) drops
Bradley-Terry. It treats alignment as a two-player constant-sum game and approximates the Nash
equilibrium with multiplicative weights. In practice that is a square loss pushing
`log π_θ/π_t` toward `η·(P̂(y ≻ π_t) − ½)`, with the win rate estimated by PairRM-0.4B over 5
samples. On Mistral-7B-Instruct-v0.2 with 60k UltraFeedback prompts over 3 iterations,
AlpacaEval 2 LC went from 17.1 to 28.5. The authors' iterative DPO peaked at 24.2 and iterative
IPO at 23.8. Average length also grew, from 1,676 to 2,163. Hyperparameters were chosen by
PairRM win rate, and PairRM itself prefers IPO's longer outputs. Open LLM Leaderboard averages
fell after iteration 1–2.

**DITTO** ([arXiv:2406.00888](https://arxiv.org/abs/2406.00888) (Shaikh et al., ICLR 2025))
takes SPIN's pairing down to fewer than 10 user demonstrations: the user's text is chosen and
the model's samples are rejected. It aligns to one author's style, using Mistral-7B-Instruct
with LoRA. Judged by GPT-4 on 20 authors from CMCC and CCAT50, it won 77% head-to-head on
average, 11.7 points above SFT. The paper puts its lead over SPIN at 20.2 points in the
introduction and 9.3 in the results. In a 16-person user study it won
68.8%, against 55.5% for SFT and 51.6% for few-shot GPT-4. Two limits: updating `π_ref` every
iteration, SPIN-style, dropped the win rate from 70.1% to 45.8%, and the adapter lost general
skills such as coding.

---

## Decision framework

| Property | PPO | DPO | GRPO (and GSPO) | KTO | ORPO |
|----------|-----|-----|------|-----|------|
| Needs reward model | Yes | No | Optional (DeepSeekMath used one; R1 used rules) | No | No |
| Needs reference model | Yes (SFT) | Yes (SFT) | Yes (SFT) | Yes (SFT) | No |
| Needs value function | Yes | No | No | No | No |
| Online / offline | Online | Offline as published; online and semi-online variants work | Online | Offline | Offline |
| Requires paired data | Yes | Yes | No (verifiable) | No | Yes |
| Memory cost | 4x model | 2x model | 3x model | 2x model | 1x model |
| Reward hacking risk | High | Low | Lower, not none: the verifier can be gamed | Low | Low |
| Best for | General alignment, complex tasks | General alignment, stable training | Reasoning (math/code) | Unpaired feedback | Compute-constrained |

**Practitioner heuristics:**
1. **Start with DPO.** It's cheaper, more stable, and works well for most instruction
   following and general alignment tasks. Requires a clean preference dataset. Tülu 3 ran a
   controlled comparison on the same preference mix. Untuned PPO against a reward model scored
   a slightly lower average than DPO, and took about 28 hours on two nodes, against about 4
   hours on one node for DPO. So the team kept length-normalized DPO for preferences and used
   PPO only for verifiable rewards
   ([arXiv:2411.15124](https://arxiv.org/abs/2411.15124) (Lambert et al., 2024-11, preprint)).
2. **Go online when you can afford generation, but that does not require PPO.** What helps
   is sampling fresh responses from the current model and labelling them with an RM or a
   verifier. The loss matters less. Lanchantin et al.
   ([arXiv:2506.21495](https://arxiv.org/abs/2506.21495) (Lanchantin et al., 2025-06)) trained
   Llama-3.1-8B-Instruct with offline DPO, semi-online DPO (generator re-synced every s steps),
   online DPO and GRPO. On NuminaMath math, Math500 accuracy was 53.7% offline, against 58.9%
   for semi-online DPO at s=100, 58.7% for online DPO and 58.1% for GRPO. On WildChat prompts
   with an Athene-RM-8B reward, AlpacaEval 2.0 LC winrate (GPT-4-1106 judge) went from 53.2
   offline to 83.1 for online DPO and 75.2 for GRPO. The gain shows up even with no new human
   data. Swamy et al. ([arXiv:2503.01067](https://arxiv.org/abs/2503.01067) (Swamy et al.,
   2025-03)) used Pythia-1.4B/2.8B on TL;DR. Online DPO ranked its own samples with an RM
   trained on the *same* preferences, and it beat offline DPO on that data, including offline
   DPO run for two epochs. Their explanation is a generation-verification gap. A reward model
   is a simpler function to learn than a policy, and RL against it limits the search to
   policies such a simple verifier supports, so "online PFT trades data for computation".
   Where the gap disappears (two-word summaries), online gives "a minimal at best improvement
   of ≈1% winrate". RLHF Workflow published an open recipe
   ([arXiv:2405.07863](https://arxiv.org/abs/2405.07863) (Dong et al., TMLR 2024)). It ran
   three rounds of iterative DPO on its own Llama-3-8B SFT model, with 20k prompts per round,
   16 samples each and best-vs-worst pairs ranked by an open BT reward model. Against vanilla
   DPO on the same model, AlpacaEval 2 LC went from 22.5 to 31.3 and Arena-Hard from 22.4 to
   29.1. **Online loops amplify the reward model's length bias.** A character-length penalty
   cut the average Arena-Hard response length from 656 to 382 (the paper gives no unit). LC rose to 38.1, but Arena-Hard,
   which has no length control, fell to 22.1. Online is not automatic, though. Tülu 3 ran online DPO from a DPO
   checkpoint for 200k episodes on math, with a learned RM as the labeller. It gave little or no
   gain on GSM8K and lowered MATH, so it was dropped from the recipe (Lambert et al., 2024).
3. **Use GRPO for verifiable reasoning tasks.** Math, code, logic — anything where
   you can compute a reward without a human. DeepSeek-R1 is the existence proof.
4. **Consider KTO when pairs are scarce.** Binary feedback (thumbs up/down) is easier
   to collect than ranked pairs. If your feedback data is unpaired, KTO is the right tool.
   If you have clean, consistent pairs, its authors expect DPO to do better.
5. **ORPO for single-stage training.** If you can't run SFT + DPO sequentially (cost,
   latency), ORPO collapses them into one pass.

---

## The DeepSeek-R1 story

DeepSeek-R1 (2025) demonstrated that pure RL with verifiable rewards can develop
emergent chain-of-thought reasoning — the model learned to "think" (producing long
reasoning traces) without any explicit CoT supervision.

Key findings ([arXiv:2501.12948](https://arxiv.org/abs/2501.12948) (DeepSeek-AI, 2025-01)):

- **R1-Zero.** GRPO on DeepSeek-V3-Base with only rule-based accuracy and format rewards,
  and no SFT.
  - AIME 2024 pass@1 (mean of 16 samples) rose from 15.6% to 71.0%, and to 86.7% with
    majority voting over 64.
  - Response length on the training set grew from hundreds to thousands of tokens.
  - DeepSeek chose rules over a neural reward model because the latter "may suffer from
    reward hacking" at scale.

  ![DeepSeek-R1-Zero AIME 2024 accuracy over about 8,500 RL steps. Pass@1 climbs from about 0.16 to 0.71 and cons@16 from about 0.25 to 0.87, with dashed reference lines for o1-0912 at 0.74 pass@1 and 0.83 cons@64.](../sources/images/deepseek-r1-zero-aime-fig2.png)
  *Image Source: DeepSeek-AI, [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) (2025), Fig. 2*

- **The "aha moment".** It is one qualitative transcript, an intermediate checkpoint writing
  "Wait, wait… That's an aha moment" and re-planning. There is no quantitative measure behind it.
- **Model size still matters.** The same paper is the counter-example to "scale RL, not the
  model".
  - On Qwen-32B, more than 10K steps of R1-Zero-style RL reached 47.0% AIME pass@1.
  - SFT on 800k samples from the 671B R1 reached 72.6%.
  - DeepSeek's conclusion: distilling a strong model beats RL on a small one, though small
    models still benefit from RL afterwards.
  - That is one RL run, confounded by the teacher's size.
- **Full R1.** A cold start of "thousands" of long-CoT examples, then reasoning RL with a
  language-consistency reward, rejection sampling (about 600k reasoning + 200k other samples),
  and a final all-scenario RL.
  - R1 reached 79.8% AIME 2024 and 97.3% MATH-500, against 79.2% and 96.4% for o1-1217.
  - It trails o1-1217 on GPQA Diamond (71.5 vs 75.7).
  - The o1 numbers are copied from OpenAI's reports, not rerun.
  - Process reward models and MCTS were tried and abandoned.
  - MCTS survives as an offline data tool instead. Mulberry
    ([arXiv:2412.18319](https://arxiv.org/abs/2412.18319) (Yao et al., NeurIPS 2025)) searched
    reasoning trees jointly with GPT-4o, Qwen2-VL-7B/72B and Llama-3.2-11B-Vision to build 260K
    multimodal SFT traces. Qwen2-VL-7B tuned on them went from 58.2% to 63.1% on MathVista
    (+4.2 points averaged over eight benchmarks). No RL is involved.

Kimi k1.5 reached a similar result by a different route
([arXiv:2501.12599](https://arxiv.org/abs/2501.12599) (Kimi Team, 2025-01)):

- **Method.** RL with a 128k context and partial rollouts; online mirror descent toward the
  previous iterate; no value network, MCTS or PRM.
- **Long CoT.** 77.5% AIME 2024 pass@1 against o1's 74.4%. It lost on LiveCodeBench
  (62.5 vs 67.2) and MMMU (70.0 vs 77.3).
- **long2short RL** (a length penalty plus a shorter rollout cap) produced a short-CoT model
  at 60.8% AIME using 3,272 tokens on average. "Short" is relative.
- **Caveats.** The model size is undisclosed, as are τ, the penalty weight and the
  partial-rollout budget.

Open-Reasoner-Zero reproduced R1-Zero-style length and accuracy scaling with vanilla PPO, no
KL and a binary reward ([arXiv:2503.24290](https://arxiv.org/abs/2503.24290) (Hu et al.,
2025-03)):

- **Result.** On Qwen2.5-32B base it scored 48.1% AIME24 against R1-Zero-Qwen-32B's 47.0%,
  with about 1,200 steps against DeepSeek's ">10K".
- **Caveats.**
  - Steps are not equal compute: ORZ's are 128 prompts × 64 samples, and DeepSeek's batch is
    undisclosed.
  - The margin is about a third of one AIME problem.
  - It is below QwQ-32B-Preview (50.0).

This validated the verifiable rewards paradigm and shifted the field's attention from
"what alignment technique" to "what reward structure."

**What RLVR adds, measured at large k.** Yue et al.
([arXiv:2504.13837](https://arxiv.org/abs/2504.13837) (Yue et al., 2025-04)) compared base
models with their zero-RL counterparts: Qwen2.5-7B/14B/32B and LLaMA-3.1-8B trained with GRPO
via SimpleRL-Zoo, plus Oat-Zero, DAPO, and code and vision RL runs. They measured pass@k up to
k=1024. RL models win at small k, but the base models catch up and pass them as k grows. On
Minerva at 32B, the base model solves about 9% more problems at k=128. On AIME24 with
Qwen2.5-7B at k=1024, 13.3% of problems are solved only by the base model and 0.0% only by the
RL model. The paper concludes that current RLVR "rarely elicits fundamentally new reasoning
patterns". It makes the base model better at sampling paths it already had. The six
algorithms they tried (PPO, GRPO, Reinforce++, RLOO, ReMax, DAPO) behave alike. Distillation
from a stronger teacher, unlike RLVR, did push pass@k past the base model. The paper did not
evaluate DeepSeek-R1-Zero itself. *This note's reading:* treat the "spontaneous"
self-verification above as RL making existing base-model behaviour reliable at pass@1, not as
proof of new capability.

Xiaomi's MiMo-7B points the same way from the pretraining side
([arXiv:2505.07608](https://arxiv.org/abs/2505.07608) (Xiaomi, 2025-05)):

- **Pretraining.** About 25T reasoning-dense tokens with a multi-token-prediction objective.
- **Base model.** 32.9% AIME 2024 against Qwen2.5-7B-Base's 10.1%, and higher pass@k at every
  k.
- **RL.** GRPO on 130K math and code problems.
  - It lifted the model to 68.2% AIME 2024 and 55.4% AIME 2025, the latter against o1-mini's
    50.7%.
  - It still loses badly on MMLU-Pro (58.6 vs 80.3).
- **What the RL changed.**
  - The code reward gives partial credit by test difficulty.
  - The RL data drops easy problems but resamples 10% of them.
  - Dropping them entirely "introduces significant instability".
- **Caveat.** The "base" saw about 10% synthetic reasoning traces in its last pretraining
  stage, so it is not a clean base.

![Left: search trees for two problems, where RLVR concentrates sampling on a rewarded path the base model already had (Problem A) and loses a correct path the base model could reach (Problem B). Right: pass@k on Omni-MATH-Train for Qwen2.5-7B and GRPO checkpoints at steps 150, 300 and 450, where pass@1 rises with training while pass@256 falls slightly below the base model.](../sources/images/yue-rlvr-reasoning-boundary-fig1.png)
*Image Source: Yue et al., [Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?](https://arxiv.org/abs/2504.13837) (2025), Fig. 1*

### How little data and reward reasoning needs

The cheap recipes of 2025 are the best evidence for the Yue reading, and most of them were
measured on Qwen2.5.

**Small SFT sets work on a strong base with a strong teacher.** The idea is LIMA's
([arXiv:2305.11206](https://arxiv.org/abs/2305.11206) (Zhou et al., NeurIPS 2023)), applied to
long CoT.

- **s1** ([arXiv:2501.19393](https://arxiv.org/abs/2501.19393) (Muennighoff et al., EMNLP
  2025)) fine-tuned Qwen2.5-32B-Instruct on 1,000 questions with traces distilled from Gemini
  2.0 Flash Thinking, in 26 minutes on 16 H100s.
  - It scored 50.0% on AIME24, and 56.7% with **budget forcing**: suppress the end-of-thinking
    token and append "Wait" so the model keeps checking. AIME24 has 30 problems, so that is two
    problems. The gain flattens after about six "Wait"s, when the model starts to loop.
  - Selection mattered more than size. 1,000 random traces scored 36.7%. The full 59K pool
    scored 53.3% (95% CI against s1K: −13% to +20%) for 56× the GPU hours.
- **LIMO** ([arXiv:2502.03387](https://arxiv.org/abs/2502.03387) (Ye et al., COLM 2025)) took
  the same base from 16.5% to 63.3% AIME24 with about 800 traces from R1-class models. **The
  same 800 examples on Qwen1.5-32B-Chat gave 9.2%.** The knowledge has to be there from
  pretraining; the examples only show how to use it.
- **At 7B, scale still pays.** OpenThoughts
  ([arXiv:2506.04178](https://arxiv.org/abs/2506.04178) (Guha et al., ICLR 2026)) ran 1,000+
  data-pipeline ablations on Qwen2.5-7B-Instruct.
  - Its data beat s1.1 and LIMO at every matched size, and accuracy was still rising at 1.2M
    examples. OpenThinker3-7B reached 53.3% AIME25 against 38.0% for R1-Distill-Qwen-7B.
  - QwQ-32B was a better teacher than DeepSeek-R1, although R1 scores higher itself.
  - Filtering traces for correct answers gave no significant gain.
- **AM-Thinking-v1** ([arXiv:2505.08311](https://arxiv.org/abs/2505.08311) (Ji et al., 2025-05,
  preprint)) is the same recipe at 32B, followed by RL.
  - 2.84M distilled SFT samples on Qwen2.5-32B base, then GRPO without KL on 54K math and code
    queries whose pass rate under the SFT model is strictly between 0 and 1.
  - It reports 85.3% AIME24 and 74.4% AIME25. No ablation separates the SFT from the RL.
- **s1K does not rescue a weak base.** On the diffusion LLM LLaDA-8B-Instruct, SFT on it moved
  MATH500 from 36.2% to 34.8% at 512 tokens (d1,
  [arXiv:2504.12216](https://arxiv.org/abs/2504.12216) (Zhao et al., 2025-04, preprint)).

**RL amplifies behaviours the base model already shows.**

- Gandhi et al. ([arXiv:2503.01307](https://arxiv.org/abs/2503.01307) (Gandhi et al., COLM
  2025)) ran identical PPO on Countdown for 250 steps.
  - Qwen2.5-3B reached about 60% and Llama-3.2-3B about 30%. Qwen's base outputs already
    contained verification and backtracking; Llama's did not.
  - Priming Llama with backtracking traces closed the gap, **even when every primed solution
    had the wrong answer**. Thoughts of the same length filled with placeholder tokens did not
    help.
  - Continued pretraining on 8.3M tokens of OpenWebMath, filtered for these behaviours, did
    the same.
- Yeo et al. ([arXiv:2502.03373](https://arxiv.org/abs/2502.03373) (Yeo et al., 2025-02,
  preprint)) reran SimpleRL-style PPO on Qwen2.5-Math-7B.
  - Accuracy rose, but the rate of "wait", "recheck" and "alternatively" did not.
  - Response length recovered after an early dip but never exceeded the base model's, while
    KL to the base fell. Some "emergent" length growth is the policy drifting back to the
    base.
  - Their recipe for Llama-3.1-8B was long-CoT SFT first, then a cosine length reward with a
    repetition penalty. Without the penalty the length reward was hacked by repetition.

**Weak or no reward still moves Qwen2.5-Math.** Each of these tests the sharpening reading,
and each gain shrinks off Qwen.

- **One example.** 1-shot RLVR ([arXiv:2504.20571](https://arxiv.org/abs/2504.20571) (Wang et
  al., NeurIPS 2025)) ran GRPO on one problem.
  - Qwen2.5-Math-1.5B went from 36.0% to 73.6% on MATH500, matching a 1.2K-problem set.
  - **A format-only reward already reaches 65.0%. Entropy loss alone, with no reward, reaches
    63.4% after 20 steps.**
  - On Llama-3.2-3B-Instruct the six-benchmark average moved from 17.5% to 19.0%.
- **Majority vote as the label.** TTRL ([arXiv:2504.16084](https://arxiv.org/abs/2504.16084)
  (Zuo et al., 2025-04, preprint)) runs GRPO on the unlabeled test questions themselves. The
  reward is agreement with the majority of 64 samples, an RL form of self-consistency
  ([arXiv:2203.11171](https://arxiv.org/abs/2203.11171) (Wang et al., ICLR 2023)).
  - Qwen2.5-Math-7B went from 12.9% to 40.2% on AIME24, but from 29.1% to 27.7% on GPQA.
  - The reward is maj@n, so by construction it turns what voting already finds into pass@1.
    It does end above the initial maj@64.
  - Mistral-Nemo-Instruct went from 0.8% to 0.0% on AIME.
- **Confidence as the reward.** INTUITOR ([arXiv:2505.19590](https://arxiv.org/abs/2505.19590)
  (Zhao et al., ICLR 2026)) rewards self-certainty, the KL from uniform to the next-token
  distribution.
  - On Qwen2.5-3B it reached 61.2% MATH500 against 63.6% for GRPO with gold answers (base
    54.4%). It beat GRPO on LiveCodeBench, 15.3% against 8.5%.
  - The Qwen2.5-1.5B base starts at 9.0% because it emits repetitive text under the chat
    template, so much of that gain is format.
  - Scoring with a frozen copy of the base was hacked within about 100 steps: the policy
    appended an already-solved problem to its answer.
  - A random 0/1 reward on Qwen2.5-3B (not the Math variant) degraded the model.
- **No data at all.** Absolute Zero ([arXiv:2505.03335](https://arxiv.org/abs/2505.03335) (Zhao
  et al., 2025-05, preprint)) has one model propose code-reasoning tasks and solve them, with a
  Python executor as the verifier.
  - Qwen2.5-Coder-7B's code-and-math average rose from 40.2 to 50.4, and math alone from 23.9
    to 39.1.
  - On Llama-3.1-8B the gain was 3.2 points, below SimpleRL-Zoo's 4.5 with curated data.
  - The Llama run also wrote of outsmarting "less intelligent humans" (the paper's "uh-oh
    moment").
- **Almost no SFT signal.** UPFT ([arXiv:2503.02875](https://arxiv.org/abs/2503.02875) (Ji et
  al., NeurIPS 2025)) fine-tunes mostly on the first few tokens (as few as 8) of the model's own
  unfiltered solutions. It matched rejection-sampling fine-tuning on Llama-3.1-8B-Instruct
  (average 38.3% against 38.5%, base 36.2%) with 0.2M sampled tokens against 36.9M. Both
  gains are small.

*This note's reading.* Where the base already samples the right behaviour (Qwen2.5, and
Qwen2.5-Math most of all), almost any signal that rewards confident, well-formatted,
self-consistent output turns it into pass@1. The gains shrink on Llama and Mistral. The
survey by Zhang et al. ([arXiv:2509.08827](https://arxiv.org/abs/2509.08827) (Zhang et al.,
2025-09, preprint)) frames the debate as "sharpening vs. discovery". It reports the same
Qwen-versus-Llama split for random and spurious rewards (Shao et al., 2025, not read here). On
the discovery side it cites ProRL (Liu et al., 2025), where prolonged RL raised pass@k as well
as pass@1. Before trusting a reasoning-RL result, check two things: is there a format-only
baseline, and was it run on a second model family?

---

## Cross-links

- **Baseline:** [02-rlhf-pipeline.md](02-rlhf-pipeline.md) — the three-stage PPO pipeline these
  algorithms evolved from
- **Constitutional AI:** [04-constitutional-ai.md](04-constitutional-ai.md) — RLAIF as an
  alternative feedback source (still uses PPO or DPO at the optimization step)
- **RL foundations:** [01-rl-foundations.md](01-rl-foundations.md) — MDP
  framing, value functions, policy gradients
- **Papers:** (local copies indexed in [references.md](../references.md#core-papers)) [arXiv:2305.18290](https://arxiv.org/abs/2305.18290) (DPO),
  [arXiv:2402.01306](https://arxiv.org/abs/2402.01306) (KTO),
  [arXiv:2506.21495](https://arxiv.org/abs/2506.21495) (semi-online DPO vs GRPO),
  [arXiv:2503.01067](https://arxiv.org/abs/2503.01067) (why online beats offline),
  [arXiv:2504.13837](https://arxiv.org/abs/2504.13837) (RLVR pass@k boundary)
- **External:** DeepSeek-R1 (arXiv: 2501.12948), GRPO (arXiv: 2402.03300), GSPO ([arXiv:2507.18071](https://arxiv.org/abs/2507.18071))
