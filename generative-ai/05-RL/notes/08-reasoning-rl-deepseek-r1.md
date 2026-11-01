---
origin: synthesis
sources:
  - https://arxiv.org/abs/2501.12948
  - https://arxiv.org/abs/2412.18319
  - https://arxiv.org/abs/2501.12599
  - https://arxiv.org/abs/2503.24290
  - https://arxiv.org/abs/2504.13837
  - https://arxiv.org/abs/2505.07608
  - https://arxiv.org/abs/2305.11206
  - https://arxiv.org/abs/2501.19393
  - https://arxiv.org/abs/2502.03387
  - https://arxiv.org/abs/2506.04178
  - https://arxiv.org/abs/2505.08311
  - https://arxiv.org/abs/2504.12216
  - https://arxiv.org/abs/2503.01307
  - https://arxiv.org/abs/2502.03373
  - https://arxiv.org/abs/2504.20571
  - https://arxiv.org/abs/2504.16084
  - https://arxiv.org/abs/2203.11171
  - https://arxiv.org/abs/2505.19590
  - https://arxiv.org/abs/2505.03335
  - https://arxiv.org/abs/2503.02875
  - https://arxiv.org/abs/2509.08827
confidence: medium
cleaned: 2026-11-01
---

# 8 — Reasoning RL: the DeepSeek-R1 Story

In early 2025 a lab showed a model learning to reason by being told only whether its final answer was right. Nobody labeled the reasoning, and yet long traces with self-correction appeared. It looked like RL had created a new skill out of nothing, and the field split over whether that was true. Did RL create the skill, or did it find something the base model could already do and make it common? The answer changes how you budget, and this chapter walks through the evidence.

> **Pillar:** [05-RL](../README.md). **Presumes:** [03](03-preference-optimization.md#grpo--group-relative-policy-optimization).

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

The Yue reading makes a testable prediction that takes a few lines to illustrate. The data below is synthetic: each problem has a chance that the base model samples a correct answer, RL raises the chance on paths it already samples, and it drops some rare paths. Sharpening shows up as a win at small k, and lost paths as a loss at large k.

```python
import numpy as np

rng = np.random.default_rng(0)
n = 2000
# Per-problem chance one base-model sample is correct: many low, some unreachable
base_p = rng.beta(0.4, 2.0, n)
base_p[rng.random(n) < 0.15] = 0.0

sharpened = np.clip(base_p ** 0.5, 0, 1)        # RL raises what the model already samples
lost = (base_p < 0.03) & (rng.random(n) < 0.5)   # and drops some rare correct paths
sharpened[lost] = 0.0

def pass_at_k(p, k):
    return (1 - (1 - p) ** k).mean()

print("    k   base    RL")
for k in [1, 4, 16, 64, 256, 1024]:
    print(f"{k:5d}  {pass_at_k(base_p, k):.3f}  {pass_at_k(sharpened, k):.3f}")
```

```text
    k   base    RL
    1  0.139  0.267
    4  0.322  0.519
   16  0.519  0.659
   64  0.660  0.700
  256  0.745  0.712
 1024  0.798  0.716
```

This shape, with RL ahead at low k and behind at high k, is what to look for in your own pass@k curves. The toy only shows the mechanism, and its numbers are not a measurement of any model.

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

## Pitfalls

- **Reading pass@1 alone.** It can't tell whether RL created a skill or sharpened one. Plot pass@k against k.
- **Assuming long traces mean reasoning.** Length can grow while accuracy doesn't. Check length against correctness.
- **Using the 2025 cheap recipes off-domain.** Most were measured on Qwen2.5 and on math. Ask what the baseline was, and whether it ran on a second model family.
- **Trusting answer-only checkers on hard problems.** Lucky answers and bad proofs can pass. Reward quality is capped by checker quality ([03](03-preference-optimization.md#grpo--group-relative-policy-optimization)).

## Try it

1. In the pass@k block, make `lost` drop 90% of the rare paths, not 50%. Where does the crossover move?
2. Set `lost` to all false. Does RL's curve ever fall below the base curve? What would that mean for the Yue reading?
3. Suppose your own model gets pass@1 of 0.30 and pass@64 of 0.31. Should you run RL? Why?

<details><summary>Answers</summary>

1. It moves left: between k = 16 and k = 64 instead of between 64 and 256. With more paths lost, RL flattens at 0.60.
2. No: `base_p ** 0.5` is at least `base_p`, so RL is never below the base. The crossover in this toy comes entirely from lost paths. It is a demonstration of the mechanism, not evidence for it.
3. Not on this evidence. Almost nothing the model can reach with more samples is left, so sharpening has little to work with. Look at data or a better base model.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What did DeepSeek-R1 show? | Pure RL with verifiable rewards on a strong base model produced long chain-of-thought reasoning, without reasoning supervision. |
| What is pass@k? | The chance that at least one of k samples is correct. It measures what a model can reach, not what it usually does. |
| What is the Yue et al. reading? | RLVR sharpens paths the base model can already sample. At large k the base model can overtake it. |
| Why does the distinction matter? | It tells you whether to invest in RL, in search, or in the base model. |
| How little data can reasoning take? | LIMA's idea applied to long CoT: small SFT sets work on a strong base with a strong teacher, with s1 using 1,000 questions. Check the baseline before you believe the headline. |

## Next

[09 — Test-time search](09-test-time-search-and-training.md) follows the pass@k argument to its other conclusion: if the model can reach the answer given enough samples, you may not need to train at all.
