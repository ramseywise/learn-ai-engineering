---
origin: synthesis
sources:
  - Koenigstein, "AI Agents: The Definitive Guide" (O'Reilly, 2026)
  - https://arxiv.org/abs/2203.07814
  - https://arxiv.org/abs/2203.11171
  - https://arxiv.org/abs/2509.06870
  - https://arxiv.org/abs/2409.12917
  - https://arxiv.org/abs/2503.04412
  - https://arxiv.org/abs/2501.04519
  - https://arxiv.org/abs/2405.14333
  - https://arxiv.org/abs/2502.06807
  - https://arxiv.org/abs/2411.07279
  - https://arxiv.org/abs/2601.16175
confidence: medium
cleaned: 2026-11-01
---

# 9 — Test-Time Search Instead of Training

Training costs a GPU cluster and weeks. Sampling costs an API call. If pass@k in [08](08-reasoning-rl-deepseek-r1.md) says your model already reaches the answer within 40 samples, the cheapest way to buy accuracy may be to sample 40 times and pick well. Picking well turns out to be the hard part. This chapter climbs from repeated sampling to voting, trained aggregators, refinement and tree search, and shows why **selection, not generation, is the bottleneck**, with numbers you can reproduce.

> **Pillar:** [05-RL](../README.md). **Presumes:** [08](08-reasoning-rl-deepseek-r1.md).

---

## Test-time search instead of training

Training raises what the model gets right on the first sample. Search spends inference
compute to find answers it can already reach with enough samples. Yue et al.'s large-k
result ([Why SFT memorizes](05-post-training-for-agents.md#why-sft-memorizes-and-rl-generalizes)) is the argument for
trying search first: if the base model's pass@k already covers the task, a verifier plus
search may get you most of the RL gain with no training run (*AI Agents: The Definitive
Guide*, ch. 3).

```text
breadth   prompt ─┬─ answer 1 ─┐
                  ├─ answer 2 ─┼─ select: verify, vote or aggregate
                  └─ answer N ─┘

depth     prompt ── answer ── revise ── revise ── answer

tree      prompt ─┬─ answer ─┬─ revise ── (score flows back to the root)
                  │          └─ revise
                  └─ answer        UCT or Thompson sampling picks where to spend the next call
```

Koenigstein builds the idea up in steps:

- **Repeated sampling** (breadth): N independent answers, then pick the best. Best-of-N.
  AlphaCode is the origin of the sample-and-verify recipe at scale
  ([arXiv:2203.07814](https://arxiv.org/abs/2203.07814) (Li et al., Science 2022)).
  - It drew up to a million programs per problem, and the problem's example tests removed
    about 99% of them.
  - It clustered the survivors by their outputs on model-generated inputs and submitted
    one program per cluster, largest first, 10 in all.
  - The solve rate grew log-linearly with samples, and the system ranked in the top 54.3%
    across 10 Codeforces contests.
  - Without filtering, the 10-submission solve rate stays flat as samples grow. With
    filtering and clustering it still falls well short of pass@k, so **selection, not
    generation, is the bottleneck.**
  - With no verifier, the oldest selector is a vote. **Self-consistency** samples about 40
    chain-of-thought paths and returns the most common final answer. With PaLM 540B on
    GSM8K that gave **74.4% vs 56.5% for greedy CoT (+17.9 points)**. It beat
    sample-and-rank and beam search, and a plain unweighted vote did as well as weighting
    by probability. Most of the gain arrives within 5–10 paths, and it needs answers that
    can be compared for equality
    ([arXiv:2203.11171](https://arxiv.org/abs/2203.11171) (Wang et al., ICLR 2023)). This
    is where maj@k / cons@k numbers in reasoning reports come from.
  - A vote fails when the correct answer is in the minority. **AggLM** trains an aggregator
    with RLVR (GRPO) to read 8 candidate solutions and write a final answer, so it can
    pick a minority answer or combine partial work. Its training set keeps every
    "hard" set (majority wrong) plus a share of easy ones. On AIME25, with eight samples
    from Qwen3-1.7B, **a single sample scored 35.7%, majority vote 45.9% and the 1.7B aggregator
    50.0%**. It also beat
    best-of-N and weighted voting with a 72B math reward model, and transferred to
    solutions from Qwen3-8B. Gains are largest when the vote is split, and on easy
    problems it ties majority vote. The aggregator uses about a third of the tokens of a
    fresh solution, so aggregating 8 beats voting over 16 on three of four benchmarks
    ([arXiv:2509.06870](https://arxiv.org/abs/2509.06870) (Zhao et al., 2025-09, preprint)).
- **Sequential refinement** (depth): one answer, improved over and over. This only works if
  the model can actually improve its own answer, and prompted models usually can't: Gemini
  1.5 Flash fell from 52.6% to 41.4% on MATH when asked to revise. SCoRe trains revision
  with multi-turn RL ([04 Self-improvement](04-constitutional-ai.md#self-improvement-and-scaling)).
  With a 32-sample budget on MATH, **16 samples each self-corrected once, then voted, gained
  10.5 points, vs 7.4 from 32 parallel samples with self-consistency**
  ([arXiv:2409.12917](https://arxiv.org/abs/2409.12917) (Kumar et al., ICLR 2025)).
- **MCTS** combines the two. Select a node by UCT (average reward plus an exploration bonus),
  expand it, simulate and score, then backpropagate the score to the root.
- **AB-MCTS** (Inoue et al., 2025, [arXiv:2503.04412](https://arxiv.org/abs/2503.04412)).
  Standard MCTS fixes the branching factor, but an LLM can always produce another answer. So
  every node gets a **GEN** child meaning "sample a fresh answer here", and Thompson sampling
  decides between going wider (GEN) and deeper (refine an existing child). **AB-MCTS-M** fits
  a Bayesian mixed model per node, so it can estimate unexplored branches from their
  siblings' scores. **AB-MCTS-A** is simpler: each answer node gets a **CONT** ("continue
  refining") child next to GEN, with Gaussian or Beta priors on the scores.

The book's demo runs Sakana's open-source TreeQuest for 5 steps (`tq.ABMCTSA()`, one
`LLM-Refine` generator) on "write Fibonacci in Python". GPT-4o both writes the answer and
grades it, so the demo shows the mechanics, not a gain. The search is only as good as its
scorer. Use a real verifier (tests, a checker) whenever you have one. A self-judge brings
back the false-positive problem from Zhao et al.

**Search and training feed each other.** Search trajectories are rollouts, so rLLM can treat
each tree node as a step and train the policy to search better. Search can also generate
SFT data (keep the best leaf), which is how [distillation](06-data-and-environments.md#data-engineering-for-post-training)
recipes often start.
- **rStar-Math** runs this loop for four rounds. MCTS writes step-by-step math solutions
  whose steps are Python code, and any step whose code fails is dropped. Each step's
  Q-value from the search builds preference pairs that train a process preference model
  (PPM). Each round, the policy and PPM retrain on the new trajectories, and the next
  search uses them. With Qwen2.5-Math-7B, **MATH rose from 58.8% to 89.4% when searching
  over 8 trajectories (90.0% with 64)**, and AIME 2024 reached 53.3%. Two qualifications:
  round 1 was bootstrapped with DeepSeek-Coder-V2 236B, and **the 7B policy decoding
  greedily scores 78.4%, below Qwen2.5-Math-7B-Instruct's 82.6%**. Most of the result
  comes from the PPM plus search at test time
  ([arXiv:2501.04519](https://arxiv.org/abs/2501.04519) (Guan et al., ICML 2025)).
- **DeepSeek-Prover (v1)** is the same loop with a formal verifier. It translated
  competition problems into about 8M Lean 4 statements, filtered for quality, tried to
  prove each statement and its negation, and kept only proofs Lean accepted. Each
  round of fine-tuning (expert iteration) on DeepSeekMath 7B made a better prover for the
  next. **miniF2F-test went from 34.0% to 46.3% at pass@128 across iterations 0–4**, vs
  23.0% for GPT-4-turbo at pass@64. The 52.0% headline is cumulative across all runs, not
  a single sample budget
  ([arXiv:2405.14333](https://arxiv.org/abs/2405.14333) (Xin et al., 2024-05, preprint)).
  V2 continues this work with RL ([03 GRPO](03-preference-optimization.md)).

**Enough RL can absorb a hand-built search.** OpenAI compared the two on IOI 2024
([arXiv:2502.06807](https://arxiv.org/abs/2502.06807) (OpenAI, 2025-02, preprint)).
- **o1-ioi** used an AlphaCode-style pipeline: 10,000 samples per subtask, clustering on
  model-written test inputs, and a learned reranker. It scored 213 under the 50-submission
  rule, against 156 for 50 random picks.
- **An early o3** sampled 1,024 solutions per problem and simply submitted the 50 that used
  the most test-time compute. It scored **395.64, above the ~360 gold line**.
- On Codeforces, ratings went from 1673 (o1) to 2214 (o1-ioi with its full test-time
  strategy) to 2724 (o3).
- The o3 transcripts show the verifier moving inside the model. It writes a brute-force
  solution and cross-checks its optimized one against it.
- This is a report, not a controlled study. The o3 checkpoint used for IOI was later than the
  Codeforces one and had fresher data, the RL recipe and compute are undisclosed, and o3
  still drew a thousand samples.

**Test-time training sits between the two.** You update weights, but only temporarily, and for
one problem.

- **TTT for few-shot tasks.** Akyürek et al. train a per-task LoRA (rank 128) on leave-one-out
  tasks built from the task's own demonstrations, with invertible augmentations
  ([arXiv:2411.07279](https://arxiv.org/abs/2411.07279) (Akyürek et al., 2024-11)).
  - The model was an 8B Llama-3 already fine-tuned on synthetic ARC data.
  - It went from 18.3% to 47.1% pass@2 on the 400-task ARC public validation set.
  - It cost about 7 A100-minutes per task.
  - The headline ensemble's "average human" match (61.9% in the text, 62.8% in Table 1)
    drops to 47.5% on the hidden semi-private set.
- **TTT-Discover** runs RL on a single test problem with gpt-oss-120b (LoRA, 50 steps × 512
  rollouts, about $500 per problem)
  ([arXiv:2601.16175](https://arxiv.org/abs/2601.16175) (Yuksekgonul et al., 2026-01)).
  - It optimizes an *entropic* objective that tilts toward the best sample, not the mean.
  - It restarts from a PUCT-selected buffer of earlier solutions.
  - On the GPUMode TriMul kernel (H100, authors' evaluator) it reached 1,203 µs, against
    1,986 µs for the same loop with an expected-reward objective and 5,353 µs for Best-of-N.
    Plain test-time RL was no better than Best-of-N.
  - It set new bests on the Erdős minimum-overlap bound and on both AtCoder contests, but not
    on AC2 or MLA-Decode.
  - Each problem is one run, some margins are tiny, and several prompts described the prior
    best method.

Both need a dense, trustworthy score at test time: a verifier on the demonstrations, or a
continuous reward.

## Measuring the selection bottleneck

A simulation shows how much selection costs. Each synthetic problem has its own chance that one sample is right. We then compare three ways of using N samples: majority vote, a flawed checker, and pass@N, which assumes a perfect picker. The numbers below depend on those assumptions, so read the ordering, and not the values.

```python
import numpy as np

rng = np.random.default_rng(0)
PROBLEMS = 20000
p = rng.beta(1.2, 1.2, PROBLEMS)                # chance one sample is right, per problem
WRONG_ANSWERS = 3                               # wrong samples scatter over a few answers

def evaluate(n):
    correct = rng.binomial(n, p)
    wrong_top = rng.multinomial(n - correct, [1 / WRONG_ANSWERS] * WRONG_ANSWERS).max(axis=1)
    vote = correct > wrong_top                  # ties count as wrong
    # A flawed checker passes 70% of right samples and 10% of wrong ones; pick among the passes
    passed_right = rng.binomial(correct, 0.7)
    passed_wrong = rng.binomial(n - correct, 0.1)
    passed = passed_right + passed_wrong
    chance = np.where(passed > 0, passed_right / np.maximum(passed, 1), correct / n)
    flawed = rng.random(PROBLEMS) < chance
    return vote.mean(), flawed.mean(), (correct > 0).mean()   # last column is pass@k

print(f"one sample: {p.mean():.3f}")
print("  N   vote  flawed-checker  pass@N (perfect selection)")
for n in [5, 10, 40]:
    v, f, o = evaluate(n)
    print(f"{n:3d}  {v:.3f}  {f:.3f}           {o:.3f}")
```

```text
one sample: 0.499
  N   vote  flawed-checker  pass@N (perfect selection)
  5  0.537  0.736           0.848
 10  0.618  0.788           0.928
 40  0.710  0.800           0.984
```

A vote improves slowly because wrong answers can agree. An imperfect checker does better here, and then flattens at the rate its false positives allow, while pass@N races ahead of both. Nothing you do to generation closes that gap. Only better selection does.

Tree search adds a decision about where to spend the next model call. UCT scores each child by its average reward plus a bonus for being little tried:

```python
import math

def uct(total_reward, visits, parent_visits, c=1.4):
    if visits == 0:
        return math.inf                      # always try an unvisited child once
    return total_reward / visits + c * math.sqrt(math.log(parent_visits) / visits)

children = {"refine draft A": (6.0, 8), "refine draft B": (2.0, 2), "fresh sample": (0.0, 0)}
parent = sum(v for _, v in children.values())
for name, (reward, visits) in children.items():
    print(f"{name:<15} mean={reward / visits if visits else 0:.2f}  UCT={uct(reward, visits, parent):.2f}")
```

```text
refine draft A  mean=0.75  UCT=1.50
refine draft B  mean=1.00  UCT=2.50
fresh sample    mean=0.00  UCT=inf
```

Draft A has the higher visit count and a lower bonus, so draft B comes next even though it hasn't scored much better. The fresh sample comes first of all, since an unvisited child always gets one try. AB-MCTS replaces this rule with Thompson sampling and keeps a fresh-sample child at each node.

## Pitfalls

- **Reporting pass@k as if you could deploy it.** It assumes a perfect picker. In the table above, the flawed checker at 40 samples is well below pass@40.
- **Voting where answers can't be compared.** Voting needs equal answers, as in numbers or multiple choice. Free text needs a judge or a clustering step.
- **Paying for search on a flat curve.** If pass@k barely rises with k, more samples buy little.
- **Self-revision without training.** Prompted models often get worse when asked to revise their work, as the Gemini 1.5 Flash result shows.
- **Trusting a verifier's score of its own search.** A search with a flawed verifier finds the verifier's false positives faster.

## Try it

1. In the search table, change the checker to pass 70% of right samples and 50% of wrong ones. How does it compare with a plain vote at N = 40?
2. Change `WRONG_ANSWERS` to 50, so wrong answers rarely agree. What happens to the vote column and why?
3. In the UCT block, raise `c` from its value to 3. Does the fresh child still come first, and what happens to the order of the two drafts?

<details><summary>Answers</summary>

1. The vote wins clearly: 0.710 against 0.560 at N = 40. A checker that passes half of the wrong samples is barely better than one random sample, and more samples don't fix that.
2. The vote jumps to 0.922 at N = 40, up from 0.710, because wrong answers no longer pile up on one value. Votes work best when errors scatter.
3. The fresh child stays first because an unvisited node is always infinite. Draft B stays ahead of draft A, and by more (about 4.22 against 2.36), because the bonus grows for less-visited nodes.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What is best-of-N limited by? | The selector. More samples help only if you can pick the good one. |
| When does self-consistency work? | When answers can be compared for equality and the correct answer is the most common. |
| What does an aggregator like AggLM add? | It can pick a minority answer or combine partial work, which a vote can't do. |
| Why does refinement need training? | Prompted models usually can't improve their own answers. SCoRe trains revision with multi-turn RL. |
| What does AB-MCTS change in MCTS? | It drops the fixed branching factor: each node can always sample a fresh answer, and Thompson sampling chooses wider or deeper. |
| Search or training? | Try search first when pass@k already covers the task and a verifier exists. Train when you need it fast at one sample. |

## Next

[10 — Engineering RL systems](10-engineering-rl-systems.md) moves to what it takes when you do decide to train: problem design, measurement, scaling and running it safely.
