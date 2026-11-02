---
origin: web-authored
sources:
  - https://arxiv.org/abs/2307.15217 (Casper et al., open problems of RLHF)
  - https://arxiv.org/abs/2510.05024 (Inoculation prompting)
  - https://arxiv.org/abs/2309.14525 (LLaVA-RLHF, Fact-RLHF)
  - https://arxiv.org/abs/2507.07484 (Machine Bullshit)
  - https://arxiv.org/abs/2308.03958 (Synthetic data reduces sycophancy)
  - https://arxiv.org/abs/2009.01325 (Learning to summarize from human feedback)
  - https://arxiv.org/abs/2204.05862 (Anthropic HH-RLHF)
  - https://arxiv.org/abs/2210.10760 (Scaling laws for reward model overoptimization)
  - https://arxiv.org/abs/2401.12187 (WARM, weight-averaged reward models)
  - https://arxiv.org/abs/2501.12948 (DeepSeek-R1)
  - https://arxiv.org/abs/2505.07608 (MiMo-7B)
  - https://arxiv.org/abs/2503.24290 (Open-Reasoner-Zero)
  - https://arxiv.org/abs/2501.12599 (Kimi k1.5)
  - https://arxiv.org/abs/2311.07911 (IFEval)
  - https://arxiv.org/abs/2411.15124 (Tulu 3)
  - https://arxiv.org/abs/2203.02155 (InstructGPT)
  - https://arxiv.org/abs/2112.00861 (Askell et al., HHH assistant)
  - https://arxiv.org/abs/2302.12192 (Aligning text-to-image models)
confidence: medium
cleaned: 2026-11-01
---

# 12 — RLHF Failure Modes

> **Pillar:** [05-RL](../README.md)
> **Presumes:** [02 — RLHF pipeline](02-rlhf-pipeline.md). Read this straight after 02; it is numbered 12 only so that the other chapters keep their numbers.
> **Papers:** Casper et al. (2307.15217), Stiennon et al. (2009.01325), Gao et al. (2210.10760), WARM (2401.12187)

The pipeline in [02](02-rlhf-pipeline.md) ends with a policy maximizing a reward model, and that reward model is a learned guess at what people want. Everything in this chapter follows from the gap between the guess and the people. The policy finds it (reward hacking), runs further into it the longer you train (overoptimization), and can lose capability on the way (the alignment tax). None of the three shows up on the training curve, because the training curve is the reward model's opinion of itself.

---

## A small model of the whole problem

Before the evidence, here is the shape of the failure in about twenty lines. An answer has one knob, padding. People like some detail and dislike too much, so human value peaks at 1. Stage 2 fits a straight line on answers with padding between 0 and 1, where more padding does look better. Stage 3 then maximizes that line minus a KL-like penalty pulling back to the SFT model at 0.2.

```python
import numpy as np

rng = np.random.default_rng(0)

def human(p):
    """What people actually think: some detail helps, padding hurts."""
    return p - 0.5 * p**2

# Stage 2: fit a linear reward model on answers with padding between 0 and 1.
p_train = rng.uniform(0, 1, 200)
labels = human(p_train) + rng.normal(0, 0.05, 200)
slope, intercept = np.polyfit(p_train, labels, 1)
print(f"reward model: {intercept:.2f} + {slope:.2f} * padding")

def reward_model(p):
    return intercept + slope * p

# Stage 3: maximise reward minus a KL-like penalty, beta * (p - p_sft)^2 / 2.
p_sft = 0.2
print("beta   padding  reward model  human")
for beta in (2.0, 1.0, 0.5, 0.25, 0.1, 0.05):
    p = p_sft + slope / beta          # the penalised optimum
    print(f"{beta:<6} {p:>7.2f}  {reward_model(p):>12.2f}  {human(p):>5.2f}")
```

```text
reward model: 0.09 + 0.47 * padding
beta   padding  reward model  human
2.0       0.44          0.30   0.34
1.0       0.67          0.41   0.45
0.5       1.15          0.63   0.49
0.25      2.09          1.08  -0.10
0.1       4.94          2.43  -7.25
0.05      9.67          4.67  -37.11
```

Read down the table as a weakening penalty. The reward model's score only ever rises, and the human column rises and then collapses, because the fitted line says nothing true outside the range it saw. The toy's numbers are invented and its curve is a parabola by construction. What it shares with real runs is the structure, and [Stiennon et al.'s measured version](#overoptimization) is below.


## Reward hacking

The policy finds high-scoring outputs that don't reflect genuine quality. Common
manifestations:
- **Verbosity**: longer responses score higher on surface features
- **Sycophancy**: responses that agree with the prompt's framing regardless of accuracy
- **Mode collapse**: repetitive, formulaic outputs that score consistently

**Mechanism:** The reward model is an imperfect proxy for human preference. It was
trained on a finite dataset and generalizes imperfectly. The RL optimizer finds
out-of-distribution inputs that exploit this gap. See: [reward hacking patterns](10-engineering-rl-systems.md#engineering-an-rl-problem).

Casper et al.'s survey of RLHF's open problems sorts each failure into *tractable* (better method
fixes it) and *fundamental* (fixing it would take something that is no longer RLHF)
([arXiv:2307.15217](https://arxiv.org/abs/2307.15217) (Casper et al., TMLR 2023)). Reward hacking
lands in the fundamental column twice. A reward model can fit the labels perfectly and still
misgeneralize, because many reward functions fit the same finite data. And it is trained on human
*approval*, not human benefit, so anything that wins approval without being better gets rewarded.
That includes confident wrong answers and sycophancy, because evaluators can be misled. Better data
and bigger RMs shrink the gap without closing it, so plan detection and other safety layers around
the hacks the policy will find.

**Inoculation prompting** is a cheap mitigation once you know which hack to expect. Write the
exploit into the *training* prompt, for example "your code should only work on the provided test
case", and leave it out at test time. The model attributes the behaviour to the instruction instead
of internalizing it. Wichers et al. fine-tuned Qwen-2-7B base on MBPP solutions that hard-code the
visible test. With inoculation, the hack rate under a neutral prompt fell and the correct-solution
rate rose; two of four prompts beat the untrained model even on 100% hacked data. It also worked
against sycophancy (Gemma 2B) and a spurious sentiment cue (Llama 3 8B)
([arXiv:2510.05024](https://arxiv.org/abs/2510.05024) (Wichers et al., 2025-10, preprint)). The
limits: it is SFT only. It needs the bad behaviour named in advance. One word of wording ("behave"
vs "respond" as if the user is correct) separated a working prompt from a failing one. And in two of
six models it made the model *more* willing to hack when a user asked it to. MacDiarmid et al.
carried the idea into production RL, where in their prompted setting it cut the emergent
misalignment that followed coding reward hacks by 75–90% ([05](05-post-training-for-agents.md#practical-pitfalls)).

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

It is not only RL. On PaLM and Flan-PaLM up to 540B, **instruction tuning alone raised agreement
with the user's stated view by 26.0% at 8B**, and scaling from 8B to 62B raised it 19.8% more. The
models also agreed that 1 + 1 = 956446 once the user said they did, though without the opinion
they rejected the claim. A cheap fix was 1k steps of SFT on claims built from 17 NLP
classification datasets, where the label is independent of a randomly assigned user opinion, mixed
5:1 with instruction data. That cut opinion-matching by 4.7–10.0%, and it fixed the addition test
at 62B and above. The data has to be filtered to claims the model already gets right: without the
filter Flan-PaLM-62B behaved erratically, and at 8B, where the model is near chance on the claims,
the intervention made it always agree. MMLU and BBH moved by −1.6 to +0.6. All of it is one
fixed "Human:/Assistant:" multiple-choice format, and agreement with true statements was not tested
([arXiv:2308.03958](https://arxiv.org/abs/2308.03958) (Wei et al., 2023-08, preprint)).

## Overoptimization

PPO is run too long or with too small a KL coefficient. The policy drifts far from the
SFT initialization, into regions where the reward model's scores are unreliable.

**The reward model's accuracy degrades as the policy diverges from the distribution
it was trained on.** The KL penalty is the primary mitigation — it bounds how far the
policy can drift from SFT.

Stiennon et al. measured the curve first, on TL;DR summarization. They trained policies against
one reward model at a range of KL penalties and asked labelers to compare each to the reference
summaries. **Up to a KL of about 10 nats, real preference rose with the RM's prediction. Past it the
RM kept predicting near-total wins, real preference fell, and by KL 250 the RM was
anti-correlated with humans** ([arXiv:2009.01325](https://arxiv.org/abs/2009.01325) (Stiennon et
al., NeurIPS 2020)). Anthropic's HH paper is often cited for the same inverse-U, but it measured
something narrower. It split its comparisons in half, trained the policy against one PM and scored
it with the other. The two PMs agreed up to about 150k RL samples, then diverged with the held-out
PM lower; larger PMs held up longer, and crowdworker Elo did not track the PMs' predictions
([arXiv:2204.05862](https://arxiv.org/abs/2204.05862) (Bai et al., 2022, preprint)). That is
proxy-vs-proxy divergence, not a human-judged peak. OpenAI
measured the shape as a scaling law in a synthetic setup, with a large "gold" RM standing in for
humans ([arXiv:2210.10760](https://arxiv.org/abs/2210.10760) (Gao, Schulman & Hilton, ICML 2023)):
proxy reward climbs monotonically while gold reward rises, then falls. This is Goodhart's law,
and it shows up as verbose, ingratiating, rigorous-sounding filler.

![Line chart against KL from the supervised baseline (0 to 250, log scale). The dashed "RM prediction" line rises steadily from about 0.37 to 1.0 fraction preferred to the reference. The solid "Actual preference" line rises from about 0.24 to a peak near 0.47 at KL 10, stays near 0.42 to KL 75, then falls to about 0.05 at KL 250.](../sources/images/stiennon-learning-summarize-fig5.png)
*Image Source: Stiennon et al., [Learning to summarize from human feedback](https://arxiv.org/abs/2009.01325) (2020), Fig. 5*

The KL penalty limits drift; a sturdier reward model moves the peak. Ensembling several RMs'
predictions helps but multiplies inference cost. **WARM instead averages the *weights* of M reward
models fine-tuned from one shared SFT checkpoint**, with different learning rates, dropout and data
order. This is the model-soups trick (Wortsman et al., ICML 2022) applied to RMs, and it costs one
model at inference ([arXiv:2401.12187](https://arxiv.org/abs/2401.12187) (Ramé et al., ICML 2024)).
On TL;DR summarization with PaLM-XXS RMs and a PaLM-L AI labeler as the oracle, the control reward
held up longer as M grew, and an RL policy trained against WARM (M = 6) won **79.4%** of pairwise
comparisons against one trained on the best single RM. With 25% of labels flipped, the averaged RM
memorized the flipped labels less than a prediction ensemble did. It still collapses eventually,
it allowed a smaller KL coefficient rather than none, and it keeps any bias every member shares,
such as a length preference. The evidence is one task, small models and AI labels, no humans.

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
The KL stays essential when the reward is a learned model that can be exploited. A verifier that
checks only part of the answer can be exploited too. IFEval's 25 code-checkable constraint types,
such as "at least 400 words" or "mention the keyword AI at least 3 times"
([arXiv:2311.07911](https://arxiv.org/abs/2311.07911) (Zhou et al., 2023-11, preprint)), became
one of Tülu 3's RLVR rewards. In its low-penalty runs (β = 0.01) the policy satisfied the constraints
and "does not output meaningful content"
([arXiv:2411.15124](https://arxiv.org/abs/2411.15124) (Lambert et al., 2024-11, preprint)). More in
[post-training-for-agents.md](05-post-training-for-agents.md#why-sft-memorizes-and-rl-generalizes).

## Alignment tax

RLHF can reduce performance on capability benchmarks (coding, math, reasoning) while
improving alignment metrics. InstructGPT saw regressions on SQuAD, DROP, HellaSwag and WMT 2015
French→English after PPO. Its fix was **PPO-ptx**: mix pretraining-gradient updates into
PPO. That removed most of the regression without hurting labeler preference, and "InstructGPT" in
the paper means the PPO-ptx model.

The tax depends on scale. In Anthropic's HH RLHF, models under about 10B lost ground on zero-shot
NLP evaluations, while the 13B and 52B RLHF models scored better than their base models zero-shot
and about the same few-shot. Two caveats: the feedback data was collected with 52B models, and the
evaluations are mostly multiple-choice ([arXiv:2204.05862](https://arxiv.org/abs/2204.05862) (Bai
et al., 2022, preprint)). The same holds for prompting. Anthropic's earlier 14-conversation HHH
prompt cost small models accuracy on the HumanEval and QuixBugs coding evals, but made the 13B and 52B models noticeably better
([arXiv:2112.00861](https://arxiv.org/abs/2112.00861) (Askell et al., 2021, preprint)).

The tax appears outside text too. Lee et al. trained a reward model on 27k binary human labels of
Stable Diffusion images for prompts about color, count and background, then fine-tuned with
reward-weighted likelihood, not RL. On 120 prompts with 9 raters each, **the fine-tuned model won a
two-thirds majority on image–text alignment for 50% of prompts against 3% for the original, but on
image fidelity the original won 15% to 10%**, with some oversaturated and duplicated outputs
([arXiv:2302.12192](https://arxiv.org/abs/2302.12192) (Lee et al., 2023-02, preprint)). Its loss
already carries a pre-training term, the analogue of PPO-ptx; in samples trained without it, image
quality collapsed. Picking the best 4 of 16 samples by the same reward gave a similar alignment gain
(46%) with no fidelity loss, because nothing was trained.

The tax can also be negative. Lightman et al. argue that process supervision rewards the reasoning
humans endorse *and* raised MATH accuracy over outcome supervision ([Stage 2 in 02](02-rlhf-pipeline.md#stage-2--reward-model-training)). They frame that
as a negative alignment tax, so far shown only for math.

---

## Pitfalls

- **Reading the training reward as progress.** It keeps rising past the point where people stop agreeing. Track a held-out human or judge score, and stop when it turns down.
- **Treating sycophancy as only an RL problem.** Wei et al. measured it rising from instruction tuning and from scale alone, so dropping RL does not remove it.
- **Citing Anthropic's HH curve as a human-judged peak.** It compares one preference model with another, and only Stiennon et al. measured people directly.
- **Assuming a verifier can't be hacked.** Tülu 3's constraint rewards were satisfied by output with no meaningful content. A check covers only what it checks.
- **Reading one benchmark as a verdict on the tax.** It varies with model size, task and evaluator, and it has been measured as negative on math.
- **Copying an inoculation prompt without testing it.** One word separated a working prompt from a failing one, and in two of six models it raised hacking when a user asked for it.

## Try it

1. In the toy, change the reward model to a quadratic with `np.polyfit(p_train, labels, 2)`, and evaluate it with `np.polyval`. Set `p` by trying a grid of values. Does the collapse go away, and why might it come back with less training data?
2. Add 50 training answers with padding near 3 and refit the straight line. What happens to the slope and to the padding the policy picks at `beta=0.25`?
3. Compute the value of beta at which the human score peaks in the toy, using `p = p_sft + slope / beta`.

<details><summary>Answers</summary>

1. A quadratic can represent the true curve, so even at `beta=0.05` the policy stops at about 0.93 on this seed. With few noisy answers the fitted curvature can be wrong, and then the optimum lands somewhere else, which is the same gap in a smaller form. A better reward model moves the peak and doesn't remove it.
2. With 50 answers between 2.8 and 3.2 the slope went from 0.47 to -0.69 on this seed, because the new labels show padding hurting. At `beta=0.25` the formula now gives a negative padding, so the policy gets pushed the other way, which a real knob would clip at 0. The straight line is still wrong, in the other direction. Data from the region the policy reaches is what repairs the reward model, which is the argument for sampling pairs near the current policy.
3. Human value peaks at `p = 1`, so `beta = slope / (1 - 0.2)`. With the fitted slope of 0.47 that is about 0.59. The table's best row, `beta=0.5`, sits next to it.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What is reward hacking? | Output that scores high on the reward model and low with people, often verbosity, sycophancy or formulaic text. |
| Is it fixable with better data? | Better data and bigger reward models shrink it. Casper et al. call it fundamental, because many rewards fit finite data and approval is not benefit. |
| What did Stiennon et al. measure? | Real preference rose up to about 10 nats of KL and fell after, while the reward model kept predicting wins. By KL 250 the two were anti-correlated. |
| Why reverse KL? | It penalizes mass where the reference has almost none, keeping the policy where the reward model can be trusted. It is also mode-seeking. |
| Do verifiable rewards need a KL penalty? | Many RLVR recipes drop it. It stays essential for learned rewards, and a partial verifier can still be exploited. |
| What is WARM? | Averaging the weights of reward models fine-tuned from one SFT checkpoint, which holds up longer at the inference cost of one model. |
| What is the alignment tax? | Capability benchmarks falling while alignment scores rise. PPO-ptx reduced it for InstructGPT, and it shrinks or reverses with scale in Anthropic's data. |

## Next

Back to the sequence: [03 — Preference optimization](03-preference-optimization.md) removes the reward model that most of these failures start from. [10 — Engineering RL systems](10-engineering-rl-systems.md) covers how to look for these hacks in a running system, and [05](05-post-training-for-agents.md) carries them into agents. Papers are indexed in [references.md](../references.md#core-papers).
