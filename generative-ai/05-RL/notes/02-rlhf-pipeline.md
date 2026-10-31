---
origin: web-authored
sources:
  - https://arxiv.org/abs/2203.02155 (InstructGPT)
  - https://arxiv.org/abs/2204.05862 (Anthropic HH-RLHF)
  - https://arxiv.org/abs/2303.08774 (GPT-4 technical report)
  - https://arxiv.org/abs/1706.03741
  - https://arxiv.org/abs/2405.14394 (instruction tuning with loss over instructions)
  - https://arxiv.org/abs/2407.00215 (CriticGPT)
  - https://arxiv.org/abs/2309.14525 (LLaVA-RLHF, Fact-RLHF)
  - https://arxiv.org/abs/2507.07484 (Machine Bullshit)
  - https://arxiv.org/abs/2501.12948 (DeepSeek-R1)
  - https://arxiv.org/abs/2505.07608 (MiMo-7B)
  - https://arxiv.org/abs/2503.24290 (Open-Reasoner-Zero)
  - https://arxiv.org/abs/2501.12599 (Kimi k1.5)
  - Huyen, AI Engineering (O'Reilly, 2025), ch. 7
  - Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), ch. 5–6
  - Raschka, Build a Large Language Model (From Scratch) (Manning, 2024), ch. 6–7
confidence: medium
cleaned: 2026-10-31
---

# 2 — RLHF Pipeline

> **Pillar:** [05-RL](../README.md)
> **Presumes:** transformer architecture, supervised fine-tuning basics
> **Papers:** InstructGPT (2203.02155), Anthropic RLHF (2204.05862), GPT-4 (2303.08774)
> **Books:** Huyen, *AI Engineering*, ch. 7; Iusztin & Labonne, *LLM Engineer's Handbook*, ch. 5–6; Raschka, *Build an LLM from Scratch*, ch. 6–7 (see [references](../references.md#books))

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

#### SFT in practice

The 2022 recipe above is a lab-scale one. Three engineering books show what Stage 1 looks
like when you run it yourself on one GPU.

**Should you fine-tune at all?** Huyen's rule is "finetuning is for form, and RAG is for facts"
(*AI Engineering*, ch. 7). Her suggested order: prompting, then few-shot examples, then
retrieval (starting with BM25, not a vector DB), and fine-tuning only after that. The evidence
she leans on is Ovadia et al. (2024), on a current-events QA set:

| Mistral-7B | Base | +RAG | FT-reg | FT-par | FT-reg + RAG | FT-par + RAG |
|---|---|---|---|---|---|---|
| Score | 0.481 | **0.875** | 0.504 | 0.588 | 0.810 | 0.830 |

Fine-tuning on top of RAG *lowered* the score here, and on MMLU adding RAG to a fine-tuned
model beat RAG alone only 43% of the time. The domain-model cautionary tale is BloombergGPT:
50B parameters, about 1.3M A100 hours. Zero-shot GPT-4-0314 then beat it on FiQA sentiment
(87.15 vs 75.07) and ConvFinQA (76.48 vs 43.41). Fine-tuning earns its place for output
format, rare syntaxes (a niche DSL, not JSON), style, latency and cost: Grammarly's
Flan-T5 editor was trained on 82k instruction pairs.

**Data format and the chat template.** An SFT example is an instruction, an optional input,
and a response, rendered through a template (Alpaca, ChatML, Llama 3) and closed with the EOS
token. Train and serve with the *same* template. A mismatch is a silent quality bug
(*LLM Engineer's Handbook*, ch. 5). Raschka builds the pipeline by hand: 1,100 instruction
pairs split 935/55/110, padded per batch, with padding targets set to `-100` (PyTorch's
`ignore_index`) except the first EOS, so the model learns to stop
(*Build an LLM from Scratch*, ch. 7):

```python
# targets = inputs shifted left by one; pad with EOS, then hide all but the first pad
mask = targets == pad_id
idx = mask.nonzero().squeeze()
if idx.numel() > 1:
    targets[idx[1:]] = -100        # cross_entropy ignores -100
```

**Loss masking is a default, not a law.** [Note 05](05-post-training-for-agents.md#the-three-stages)
masks the loss to the response. Huyen describes a *prompt loss weight* that frameworks
typically default to 10%, so the model learns a little from prompts. Raschka leaves the
instruction unmasked and cites Shi et al. ([arXiv:2405.14394](https://arxiv.org/abs/2405.14394),
2024), who found that loss over instructions *helped*. Their gains were largest with
long instructions and short outputs and with few training examples. Treat masking as a
hyperparameter to test.

**Memory: why everyone uses adapters.** Full fine-tuning holds weights, gradients and
optimizer state:

- Huyen: Adam keeps 3 values per trainable parameter. A 7B model in 16-bit is 14 GB of
  weights plus 7B × 3 × 2 bytes = 42 GB, so 56 GB *before* activations. Inference alone is
  about params × bytes × 1.2.
- LLMEH counts everything in FP32: 4 bytes of weights, 4 of gradients and 8 of Adam state,
  so 16 bytes per parameter and 112 GB for 7B, still before activations.
- With LoRA, the same 7B fits in 14–18 GB. QLoRA cut LLMEH's 7B peak from 15.6 GB to 9.3 GB
  (−40%) at about 30% slower training, with minor quality differences. QLoRA's original claim
  was a 65B model on one 48 GB GPU.

**LoRA.** Freeze W and learn a low-rank update BA, with rank r ≪ d. Hu et al. matched full
fine-tuning of GPT-3 175B on several tasks with about 4.7M trainable parameters (0.0027%). Huyen's
rules (*AI Engineering*, ch. 7):

- r between 4 and 64 is usually enough. Raschka (2023) found r = 256 best on his tasks.
- α/r between 1:8 and 8:1.
- At a fixed 18M-parameter budget on GPT-3, rank 2 on all four attention matrices beat rank 8
  on one matrix (WikiSQL 73.7 vs 70.4).
- Unmerged adapters let one base model serve many customers. For 100 customers, merging
  needs 1.68B parameters; keeping adapters separate needs 23.3M.

![LoRA: the frozen weight W is added to the product of two low-rank matrices A (n × r) and B (r × m) to give W'.](../sources/images/huyen-ai-engineering-fig7-11.png)
*Image Source: Chip Huyen, *AI Engineering* (O'Reilly, 2025), Fig. 7-11*

LLMEH starts at r = 8 with α = 2r. Its own run used Llama 3.1 8B with r = α = 32 on all
linear layers, 3 epochs, effective batch 16 and max length 2048: about 50 minutes on one
A100. The library was Unsloth, which claims 2–5× faster training and up to 80% less memory
(*LLM Engineer's Handbook*, ch. 5). The shape of that config:

```python
model = FastLanguageModel.get_peft_model(
    model, r=32, lora_alpha=32, lora_dropout=0,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "up_proj", "down_proj", "gate_proj"],
)
```

*Dated:* Huyen (written 2024) says LoRA "doesn't offer performance as strong as full
finetuning" and centres attention-only targets. Thinking Machines' "LoRA Without Regret"
(2025) finds that LoRA on **all** matrices, MLPs included, with about 10× the full-FT learning
rate, matches full fine-tuning for post-training-sized datasets (defaults in
[05](05-post-training-for-agents.md#the-three-stages)). LLMEH's all-linear config is
closer to current practice.

**Hyperparameters that matter** (Huyen ch. 7; LLMEH ch. 5):

| Knob | Starting point | Condition |
|---|---|---|
| Learning rate | ~1e-5 full FT; 3e-4 in LLMEH's LoRA run | Huyen: sweep 1e-7 to 1e-3 if unsure |
| Warmup | ~5% of steps | Linear or cosine decay |
| Batch size | ≥ 8 effective (use gradient accumulation) | Huyen: fewer than 8 can be unstable |
| Epochs | 1–2 for millions of examples; 4–10 for thousands | Stop when val loss turns up |
| Packing | On for short examples | Mask attention across packed examples |
| Optimizer | AdamW, or 8-bit AdamW to save memory | — |

**A classification head is SFT too.** Raschka swaps GPT-2 124M's 50,257-way output layer for
a 768 → 2 linear head and fine-tunes on a balanced SMS-spam set of 747 spam + 747 ham. He
freezes everything except the last transformer block, the final norm and the new head, and
reads only the **last token's** logits, because under causal attention it is the only one that
has seen the whole message (*Build an LLM from Scratch*, ch. 6):

```python
for p in model.parameters():
    p.requires_grad = False
model.out_head = torch.nn.Linear(768, 2)          # new head, trainable
for p in [*model.trf_blocks[-1].parameters(), *model.final_norm.parameters()]:
    p.requires_grad = True
loss = F.cross_entropy(model(x)[:, -1, :], y)     # last token only
```

Five epochs (AdamW 5e-5, batch 8) took 5.65 minutes on an M3 MacBook Air and raised test
accuracy from 48.75% (untrained head, near chance on balanced classes) to 95.67%. A reward model is the same move with a
scalar head (Stage 2).

**Judge your SFT run, then compare to a real baseline.** Raschka scores his instruction-tuned
GPT-2 355M with Llama 3 8B as a judge on a 0–100 scale: 50.32 on his 110 test items. The same
setup gives the *untuned* Llama 3 8B base 58.51 and Llama 3 8B Instruct 82.6. A small model
on 1,100 examples won't beat a larger base model. Those are 2024 small-model numbers for the
mechanics, not a benchmark. For judge design see [06-eval](../../../ai-engineering/06-eval/README.md).

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

where `r_θ` is the reward model and `σ` is the sigmoid function. This setup predates LLMs.
Christiano et al. ([arXiv:1706.03741](https://arxiv.org/abs/1706.03741), 2017) fit a
Bradley-Terry reward model to non-expert comparisons of short trajectory clips. They used it to
train Atari and MuJoCo agents with no access to the true reward, with humans labelling under
1% of the agent's interactions. A simulated Hopper learned backflips from 900 comparisons,
under an hour of one person's time. InstructGPT carried the recipe over to text. Training maximizes
log-likelihood of human choices:

```
L_RM(θ) = -E[(x, y_w, y_l) ~ D] [ log σ(r_θ(x, y_w) - r_θ(x, y_l)) ]
```

The reward model learns a total ordering over response quality. InstructGPT used ~33k
*prompts*, not pairs. Labelers ranked 4–9 responses per prompt, and every pair within a
ranking became a comparison, so the real count was several times larger. All pairs from one
prompt went into a single batch, which stops the reward model from overfitting to responses it
sees in many pairs.

**Raters miss errors, so the labels carry them.** OpenAI trained CriticGPT, a GPT-4-family
critic, with RLHF on code into which contractors had deliberately inserted subtle bugs. On real
bugs from ChatGPT training data, raters preferred its critiques to human-written ones 63% of the
time. On ChatGPT data a first rater had marked "flawless", critiques surfaced a rating-lowering
problem in 24% of flagged cases, against 6% for a second unassisted rater
([arXiv:2407.00215](https://arxiv.org/abs/2407.00215) (McAleese et al., 2024-06)). Critics also
hallucinate and nitpick. Human + critic teams hallucinated less than the critic alone and caught
more than the human alone. The paper never measured whether critic-assisted labels produce a
better policy, and its data and model are private.

**Preference data at practitioner scale** (*LLM Engineer's Handbook*, ch. 6). The same
(prompt, chosen, rejected) triples feed a reward model here or DPO directly ([03](03-preference-optimization.md#dpo-in-practice)).
How many pairs you need depends on the goal:

| Goal | Pairs |
|---|---|
| General-purpose alignment (frontier labs, several rounds, heavy synthetic data) | Millions |
| Open-source model improvement, or "healing" a model after merging or pruning | 10k–100k |
| Task-specific: style, refusals | 100–10k |
| Identity ("I was trained by you, not by OpenAI") | 200–500 |

Fewer pairs than SFT examples, because DPO is "less destructive than SFT" and changes the
model less. When an LLM judges candidate answers, LLMEH prefers **pairwise ranking over
absolute scoring**, since preferences are comparative to begin with. The judge's biases still
apply: position (favours the first answer), length (favours the longer one) and family
(favours its own model family). The fixes: randomize A/B order, use few-shot
examples with balanced scores, and use a jury of several models. For a chatbot it targets
about 80% judge–human agreement (*LLM Engineer's Handbook*, ch. 5). Reward models such as
ArmoRM can also act as the scorer. The book's worked example skips the judge: the
human-written blog paragraph is "chosen" and an LLM-generated answer is "rejected", and
filtering left 1,467 pairs.

### Stage 3 — RL Optimization (PPO)

Use the reward model as the environment reward function. Optimize the SFT-initialized
policy (the LLM) using **Proximal Policy Optimization (PPO)** to maximize expected reward
while staying close to the SFT policy. The KL-to-reference objective is maximum-entropy RL with a
prior, and its optimum π\* ∝ π_ref · exp(r/β) is exactly what DPO inverts
([01](01-rl-foundations.md#entropy-and-maximum-entropy-rl-sac)). The advantage estimator, GAE,
blends TD targets ([01](01-rl-foundations.md#temporal-difference-learning-q-learning-vs-sarsa)).

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
out-of-distribution inputs that exploit this gap. See: [reward hacking patterns](01-rl-foundations.md).

LLaVA-RLHF shows the verbosity hack in a multimodal model. With plain RLHF, PPO "produc[ed]
lengthier responses rather than ones that are less prone to hallucinations". LLaVA-Bench rose
while MMHal-Bench did not. **Fact-RLHF** gives the reward model ground-truth context: COCO
captions or A-OKVQA rationales. It also adds a correctness reward and a length penalty. With
these the 7B policy reached 94.1 on LLaVA-Bench (GPT-4-judged) and 2.1 on MMHal
([arXiv:2309.14525](https://arxiv.org/abs/2309.14525) (Sun et al., 2023-09)). The hallucination
rate, though, stayed flat against the SFT+ model (0.57 vs 0.55 at 13B). The MMHal gain came from
informativeness, and both benchmarks are judged by GPT-4.

Sycophancy has a measurable form. Liang et al. define a Bullshit Index, 1 − |correlation between
the model's internal belief and its stated claim|. RLHF toward immediate user satisfaction raised
it from 0.379 to 0.665 on their Marketplace task. On Llama-3-8B, claims that a product had a
feature the model believed was unknown went from 20.9% to 84.5%
([arXiv:2507.07484](https://arxiv.org/abs/2507.07484) (Liang et al., 2025-07)). The "RLHF" here
is the authors' own LoRA run on 7–8B Llama with a deliberately myopic reward, evaluated in the
same environment family. Read it as what a satisfaction-only reward does, not as a measurement
of production RLHF.

### Overoptimization

PPO is run too long or with too small a KL coefficient. The policy drifts far from the
SFT initialization, into regions where the reward model's scores are unreliable.

**The reward model's accuracy degrades as the policy diverges from the distribution
it was trained on.** The KL penalty is the primary mitigation — it bounds how far the
policy can drift from SFT.

Anthropic (2022) showed reward model score vs. KL divergence follows an inverse-U curve:
initial optimization improves true quality; past the peak, reward score continues rising
while actual quality degrades. OpenAI measured the same shape as a scaling law (Gao,
Schulman & Hilton, "Scaling Laws for Reward Model Overoptimization", 2023): proxy reward
climbs monotonically while human-judged quality rises, then falls. This is Goodhart's law,
and it shows up as verbose, ingratiating, rigorous-sounding filler.

**Why the KL is reverse, `KL(π_θ || π_ref)`.** The current policy comes first. Reverse KL
penalizes probability mass where the reference has almost none, so it keeps the policy
inside the region where the RM's scores are trustworthy. It is also **mode-seeking**: the
policy settles on one or two high-reward response styles instead of covering every style
in the reference. That is why RL-tuned models sound more decisive and less diverse.
Forward KL would force the policy to cover every mode of the SFT model, which is not the
goal. Where the penalty goes depends on the algorithm:

- **InstructGPT-style PPO** computes it per token and adds it to the reward, so it flows
  through the advantage.
- **GRPO as DeepSeek-R1 runs it** subtracts β·KL(π_θ‖π_ref) as a separate loss term, using an
  unbiased k3 estimator. The paper does not disclose β
  ([arXiv:2501.12948](https://arxiv.org/abs/2501.12948) (DeepSeek-AI, 2025-01)).

With a verifiable reward, many RLVR recipes drop the penalty entirely. These include DAPO,
MiMo-7B's modified GRPO ([arXiv:2505.07608](https://arxiv.org/abs/2505.07608) (Xiaomi, 2025-05))
and Open-Reasoner-Zero's vanilla PPO. ORZ ran PPO with GAE λ = γ = 1 on Qwen2.5 bases with no KL
loss and no KL reward shaping. It found both benchmark accuracy and response-length growth better
without KL ([arXiv:2503.24290](https://arxiv.org/abs/2503.24290) (Hu et al., 2025-03)); that
ablation is curves only, from a single run. Kimi k1.5 regularizes toward the *previous iterate*,
not a fixed reference ([arXiv:2501.12599](https://arxiv.org/abs/2501.12599) (Kimi Team, 2025-01)).
The KL stays essential when the reward is a learned model that can be exploited. More in
[post-training-for-agents.md](05-post-training-for-agents.md#why-sft-memorizes-and-rl-generalizes).

### Alignment tax

RLHF can reduce performance on capability benchmarks (coding, math, reasoning) while
improving alignment metrics. InstructGPT saw regressions on SQuAD, DROP, HellaSwag and WMT 2015
French→English after PPO. Its fix was **PPO-ptx**: mix pretraining-gradient updates into
PPO. That removed most of the regression without hurting labeler preference, and "InstructGPT" in
the paper means the PPO-ptx model.

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
  See [03-preference-optimization.md](03-preference-optimization.md).

**Dataset quality dominates.** InstructGPT's team found labeler quality (consistency,
calibration, demographic diversity) mattered more than volume. Biases in labeler pool
propagate directly into the reward model. Practitioner data engineering for both SFT and
preference sets (dedup, decontamination, synthetic data, how many examples) is in
[05](05-post-training-for-agents.md#data-engineering-for-post-training).

---

## Connection to Constitutional AI

Constitutional AI (Anthropic, 2022) extends RLHF by replacing human preference labels
with AI-generated critiques guided by a written constitution. RLAIF (RL from AI Feedback)
runs the same three-stage pipeline but uses AI feedback at Stage 2 instead of human
raters. This scales alignment without proportional human labor.

See [04-constitutional-ai.md](04-constitutional-ai.md) for the full pipeline.

---

## Cross-links

- **Upstream:** [01-rl-foundations.md](01-rl-foundations.md) — RL foundations
  (MDP, policy, reward function), MARL, RL-in-RAG
- **Algorithms:** [03-preference-optimization.md](03-preference-optimization.md) — PPO vs DPO
  vs GRPO: the algorithm evolution from RLHF through offline preference optimization
- **Constitutional AI:** [04-constitutional-ai.md](04-constitutional-ai.md) — RLAIF and
  AI-generated feedback at scale
- **Papers:** (local copies indexed in [references.md](../references.md#core-papers)) [arXiv:2203.02155](https://arxiv.org/abs/2203.02155)
  (InstructGPT), [arXiv:2303.08774](https://arxiv.org/abs/2303.08774) (GPT-4)
