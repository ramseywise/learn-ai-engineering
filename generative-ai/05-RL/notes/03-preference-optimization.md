---
origin: web-authored
sources:
  - https://arxiv.org/abs/2503.14476
  - https://arxiv.org/abs/2507.12507 (NVIDIA prolonged RL, KL plus reference-policy resets)
  - https://arxiv.org/abs/2512.16649 (JustRL, single-stage fixed-hyperparameter GRPO at 1.5B)
  - https://arxiv.org/abs/2509.03646 (HICRA, planning-token credit assignment)
  - https://arxiv.org/abs/2607.13394 (GFlowRL, partition-free GFlowNet-style RL)
  - https://arxiv.org/abs/2305.18290 (DPO)
  - "https://arxiv.org/abs/2311.10702 (Tülu 2: DPO scaled to 70B)"
  - https://arxiv.org/abs/2402.03300 (DeepSeekMath / GRPO)
  - https://arxiv.org/abs/2501.12948 (DeepSeek-R1)
  - https://arxiv.org/abs/2402.01306 (KTO)
  - https://arxiv.org/abs/2404.02078 (Eurus, DPO vs KTO/NCA on reasoning pairs)
  - https://arxiv.org/abs/2506.21495 (offline vs semi-online vs online DPO/GRPO)
  - https://arxiv.org/abs/2503.01067 (All Roads Lead to Likelihood)
  - https://arxiv.org/abs/2504.13837 (RLVR and the base model's reasoning boundary)
  - https://arxiv.org/abs/2507.18071 (GSPO)
  - https://arxiv.org/abs/2501.12599 (Kimi k1.5)
  - https://arxiv.org/abs/2503.24290 (Open-Reasoner-Zero)
  - https://arxiv.org/abs/2505.07608 (MiMo-7B)
  - https://arxiv.org/abs/2504.21801 (DeepSeek-Prover-V2)
  - https://arxiv.org/abs/2507.20673 (GMPO, geometric-mean token ratios)
  - https://arxiv.org/abs/2406.08414 (DiscoPOP, LLM-discovered preference loss)
  - https://arxiv.org/abs/2501.18101 (DivPO, diversity-aware pair selection)
  - https://arxiv.org/abs/2406.17744 (LIFT, length-instruction fine-tuning)
  - https://arxiv.org/abs/2311.08401 (FactTune, DPO on automatic factuality preferences)
  - https://arxiv.org/abs/2404.03862 (Quote-Tuning, DPO toward verbatim Wikipedia quotes)
  - https://arxiv.org/abs/2509.25137 (RLHI, DPO from real user conversations)
  - https://arxiv.org/abs/2307.12966 (Aligning LLMs with Human survey)
  - Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), ch. 6
  - "Koenigstein, AI Agents: The Definitive Guide (O'Reilly, 2026), ch. 3"
  - https://arxiv.org/abs/2310.16944
  - https://arxiv.org/abs/2401.08967
  - https://arxiv.org/abs/2402.14740
  - https://arxiv.org/abs/2405.07863
  - https://arxiv.org/abs/2405.14333
  - https://arxiv.org/abs/2411.15124
  - https://arxiv.org/abs/2504.12216
  - https://arxiv.org/abs/2510.07242
  - https://arxiv.org/abs/2601.05242
  - https://arxiv.org/abs/2606.08501 (Back on Track, step rewards for diffusion-LLM RL)
confidence: medium
cleaned: 2026-11-01
---

# 3 — Preference Optimization Algorithms

> **Pillar:** [05-RL](../README.md)
> **Presumes:** [RLHF pipeline](02-rlhf-pipeline.md) — understand the three-stage baseline first
> **Papers:** DPO (2305.18290), DeepSeek-R1 (2501.12948), GRPO (2402.03300), GSPO (2507.18071)
> **Books:** Iusztin & Labonne, *LLM Engineer's Handbook*, ch. 6; Koenigstein, *AI Agents: The Definitive Guide*, ch. 3 (see [references](../references.md#books))

The three-stage pipeline in [02](02-rlhf-pipeline.md) holds four models in memory and stakes everything on a reward model that the policy learns to cheat. Each algorithm here answers one question: what can we remove? DPO removes the reward model and the rollouts. GRPO removes the critic and, with a checkable answer, the reward model too. This chapter gives the objective of each, a small runnable version of the two that matter most, and a framework for choosing.

---

## The algorithm evolution

The alignment field has moved steadily toward simpler, cheaper, more stable optimization:

```text
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

The diagram skips a side branch. In 2023, DPO had offline rivals: ranking losses (RRHF, PRO,
SLiC) and language-based ones that put a "good"/"bad" prefix on each response and train with
SFT (Chain of Hindsight, conditional behavior cloning). Few open models used any of them. In a
mid-2023 survey table of 27 open aligned models, **none used PPO, one used a ranking loss and two
used a language-based one; the rest were SFT or LoRA on distilled data**
([arXiv:2307.12966](https://arxiv.org/abs/2307.12966) (Wang et al., 2023-07, preprint)).

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

The KL term ([defined](../../01-llm-fundamentals/notes/06-pretraining-data-and-objectives.md#entropy-cross-entropy-kl-and-perplexity)) prevents policy collapse away from the SFT initialization. The pretrain
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

![RLHF fits a reward model to preference data by maximum likelihood, then runs reinforcement learning against it with the policy sampling completions. DPO skips both and fits the final language model to the preference data directly.](../sources/images/rafailov-dpo-fig1.png)
*Image Source: Rafailov et al., [Direct Preference Optimization](https://arxiv.org/abs/2305.18290) (2023), Fig. 1*

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

The model is trained to assign higher log-probability ([what that is](../../01-llm-fundamentals/notes/06-pretraining-data-and-objectives.md#entropy-cross-entropy-kl-and-perplexity)) to preferred responses relative to
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
SimPO, [13](13-preference-variants.md#simpo--no-reference-model-length-normalized-reward), measures it).
Does not generalize beyond the preference distribution seen in training.

**When to use DPO:** You have a clean preference dataset, want stability over online
exploration, and can't afford PPO compute. The dominant choice in industry for RLHF
at moderate scale.

You can see what the objective pays for with four cases and no model at all. Each case passes in the log-probabilities the policy and the reference give to the chosen and the rejected answers:

```python
import numpy as np

def dpo_loss(logp_w, logp_l, ref_w, ref_l, beta=0.1):
    margin = beta * ((logp_w - ref_w) - (logp_l - ref_l))
    return np.log1p(np.exp(-margin))             # -log sigmoid(margin)

ref_w, ref_l = -20.0, -20.0                      # reference likes both answers equally
for label, logp_w, logp_l in [("no change", -20, -20),
                              ("shifted to chosen", -15, -25),
                              ("shifted to rejected", -25, -15),
                              ("both more likely", -15, -15)]:
    print(f"{label:<20} loss={dpo_loss(logp_w, logp_l, ref_w, ref_l):.3f}")
```

```text
no change            loss=0.693
shifted to chosen    loss=0.313
shifted to rejected  loss=1.313
both more likely     loss=0.693
```

Only the *relative* shift pays. Making both answers more likely leaves the loss at log 2, so the policy can't win by turning up everything.

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
- **How many pairs:** see the table in [06](06-data-and-environments.md#preference-data-at-practitioner-scale).
  Task-level style or refusal changes need 100–10k.

```python
# illustrative: needs TRL, a GPU, a loaded LoRA model and a preference dataset
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

Falling chosen rewards matter most on reasoning, where one correct answer faces many wrong ones. Eurus trained Mistral-7B on UltraInteract, 220K correct/incorrect action pairs over math, code and logic problems. **DPO lowered the SFT model's average over 12 benchmarks from 46.5 to 44.5, and LeetCode from 20.0 to 8.3. KTO raised it to 48.8 and NCA to 48.1.** DPO's chosen rewards went below zero, while KTO's and NCA's kept rising. At 70B the rewards went to −∞ and DPO did not train at all. The same idea helped the reward model: adding −log σ(r_chosen) − log σ(−r_rejected) to the Bradley–Terry loss raised RewardBench reasoning from 77.5 to 87.0. This is one dataset and β = 0.1, with GPT-3.5 Turbo writing the correct actions and the explanation read from reward curves ([arXiv:2404.02078](https://arxiv.org/abs/2404.02078) (Yuan et al., 2024-04, preprint)).

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

Tülu 2 took Zephyr's DPO recipe unchanged (UltraFeedback, 3 epochs, β = 0.1, learning rate
5e-7) to Llama-2 at 7B, 13B and 70B ([arXiv:2311.10702](https://arxiv.org/abs/2311.10702)
(Ivison et al., 2023-11, preprint)). **The same hyperparameters were stable at every size and
raised AlpacaEval by 8.5 to 11.2 points, while MMLU, GSM8K and BBH moved by 3.5 points or less.**
The cost landed where the data was thin: the SFT and DPO mixes are mostly English, and the
multilingual TydiQA fell by 13.5 points at 13B and 17.8 at 70B. Mean AlpacaEval answer length
rose by about 40% at 70B (1,011 to 1,414), so part of the win-rate gain is the
length bias above. All gains are on GPT-4-judged benchmarks, and the paper does not compare DPO
with PPO.

The preference does not have to come from a person. FactTune samples ten biographies per
prompt and prefers whichever has the higher share of claims that FactScore finds supported in
Wikipedia ([arXiv:2311.08401](https://arxiv.org/abs/2311.08401) (Tian et al., ICLR 2024)). **On
Llama-2-7B, DPO on those pairs raised the correct share of biography claims from 0.701 (SFT) to
0.895, against 0.748 for Llama-2-Chat**, and cut incorrect claims per answer from 5.19 to 2.00.
The reference-free variant uses the model's own agreement over 20 resamples of each claim, and
reached 0.846. It was the only method that both added correct facts and removed wrong ones; ITI
and DoLa traded one for the other. Human checkers agreed with the gain (0.58 to 0.85 on
Llama-1 biographies). The answers turn terser and less conversational, though, and it is 7B only,
on 296 training people and 150 medical conditions.

Quote-Tuning uses a cheaper automatic signal still: the share of character 25-grams that a Bloom
filter finds in the Pile's Wikipedia. It keeps one pair per prompt out of 32 samples, and the
two answers must be within 10% of each other in length
([arXiv:2404.03862](https://arxiv.org/abs/2404.03862) (Zhang et al., NAACL 2025)). **On Natural
Questions, DPO on about 20k such pairs lifted Llama-2-7B-Chat's quoted share from 34.9% to 54.5%,
above best-of-32 reranking (50.4%), at unchanged answer length.** TruthfulQA truthful-and-informative
rose 46.6 to 51.5, and MMLU, GSM8K, BBH and HellaSwag each fell by under 1.6. Without the length
filter, answers came out about 10% shorter. The score counts many short quotes the same as a few
long ones, and it says nothing about whether the quoted text answers the question.

---

## GRPO and GSPO

GRPO and GSPO moved to [3b — GRPO and GSPO](03b-grpo-and-gspo.md): the group-relative advantage, the verifiable-reward setup from DeepSeek-R1, GRPO in code, and the sequence-level ratio.

---

## Variants and extensions

DPO has spawned a family, each member changing one thing. **KTO** takes unpaired thumbs up or down. **IPO** swaps in a squared loss to stop pairs collapsing. **ORPO** folds the preference term into SFT, so there is one training run and no reference model. **SimPO** normalizes by length. **DiscoPOP** searched for a loss automatically. **SPIN, SPPO, DITTO and RLHI** build pairs from the model's own samples or from logged chats. [13 — Preference variants](13-preference-variants.md) has the numbers and limits for each. The framework below chooses among all of them.

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

![The Tülu 3 recipe: curate prompts and identify core skills, then supervised finetuning, direct preference optimization and RL with verifiable rewards, each checked against development evals, with unseen evals held out.](../sources/images/lambert-tulu3-fig1.png)
*Image Source: Lambert et al., [Tülu 3: Pushing Frontiers in Open Language Model Post-Training](https://arxiv.org/abs/2411.15124) (2024), Fig. 1*

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

## Pitfalls

- **Picking DPO for reasoning.** Offline preference pairs can't explore answers no one wrote down. Where a checker exists, online methods tend to win, as the comparisons in this chapter report.
- **Ignoring length drift with DPO.** A longer chosen answer becomes the thing learned. Check average length before and after, and consider a length-normalized variant. Or make length part of the instruction: LIFT adds "answer in N words or less" to the prompts and, when the limit falls between the two answers, flips the pair so the longer winner loses. On 3,200 OpenAssistant pairs with Llama-2-70B-Base, **length-instruction violations fell from 65.8% under plain DPO to 7.1%**, and length-instructed win rate rose from 4.6% to 13.6%. R-DPO's length penalty only got to 45.0%, and standard AlpacaEval 2 did not drop. The same runs show length-controlled AlpacaEval can still be moved from 23% to 29% just by changing the requested length. The constraint is a word count from one fixed template, max only, and the judge is GPT-4 ([arXiv:2406.17744](https://arxiv.org/abs/2406.17744) (Yuan et al., 2024-06, preprint)).
- **Losing diversity to best-vs-worst pairs.** Win rate can rise while every sample says the same thing. Asked for a random persona, Llama-3.1-8B-Instruct named "Astrid" over 10% of the time, and online DPO cut the share of unique attributes from 24% to 9%. DivPO keeps the DPO loss and changes only the pair: the chosen is the *least* likely response within ρ of the top reward, and the rejected is the most likely one near the bottom. Online DivPO reached 54% unique attributes at the same reward-model score. Trained on WildChat prompts, AlpacaEval 2 LC was 44.1 at ρ = 0.2 against 41.3 for DPO, with more unique words (1,178 against 995; the seed model had 1,393). Push ρ to 0.5 and quality drops to 31.3. All runs use Llama-3.1-8B-Instruct and ArmoRM as the reward ([arXiv:2501.18101](https://arxiv.org/abs/2501.18101) (Lanchantin et al., 2025-01, preprint)).

## Try it

1. In the DPO block, call `dpo_loss` with `beta=0.5` and then `beta=5` on the "shifted to chosen" case. What happens to the loss, and what does that mean for how far the policy needs to move?
2. Add a DPO case where chosen and rejected both fall by the same amount. Predict the loss before you run it.

<details><summary>Answers</summary>

1. It falls from 0.313 to 0.007, and then to about zero, because β multiplies the margin. With a large β a small shift already satisfies the loss, so the policy stays closer to the reference.
2. Unchanged at 0.693. DPO depends only on the *difference* between the two log-ratios.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What does DPO optimize? | A logistic loss on the gap between the log-ratios of chosen and rejected against a frozen reference, with no reward model or sampling. |
| What does β do in DPO? | It sets how hard the reference pulls. Lower β moves further and tends to get wordier. |
| When offline, when online? | Offline for style and refusal with pairs available. Online for reasoning and tasks where a checker can score new behaviour. |
| What is DPO's main failure? | Length and format drift, plus no way to discover behaviour outside the dataset. |

## Next

[04 — Constitutional AI](04-constitutional-ai.md) keeps the optimizer and replaces the source of the preference labels. For what GRPO did for reasoning, go to [08 — DeepSeek-R1](08-reasoning-rl-deepseek-r1.md). Baseline: [02](02-rlhf-pipeline.md); foundations: [01](01-rl-foundations.md). Papers (local copies indexed in [references.md](../references.md#core-papers)): [arXiv:2305.18290](https://arxiv.org/abs/2305.18290) (DPO), [arXiv:2402.01306](https://arxiv.org/abs/2402.01306) (KTO), [arXiv:2506.21495](https://arxiv.org/abs/2506.21495) (semi-online DPO vs GRPO), [arXiv:2503.01067](https://arxiv.org/abs/2503.01067) (why online beats offline), [arXiv:2504.13837](https://arxiv.org/abs/2504.13837) (RLVR pass@k boundary), DeepSeek-R1 ([arXiv:2501.12948](https://arxiv.org/abs/2501.12948)), GRPO ([arXiv:2402.03300](https://arxiv.org/abs/2402.03300)), GSPO ([arXiv:2507.18071](https://arxiv.org/abs/2507.18071)).
