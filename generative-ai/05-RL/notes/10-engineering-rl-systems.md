---
origin: book-condensed
sources:
  - Phil Winder, "Reinforcement Learning: Industrial Applications of Intelligent Agents" (O'Reilly, 2020)
  - https://arxiv.org/abs/2503.14476
  - https://arxiv.org/abs/2605.02572
  - https://arxiv.org/abs/2309.06180
  - https://arxiv.org/abs/2511.16652
  - https://arxiv.org/abs/2610.06647
  - https://arxiv.org/abs/2512.16144
  - https://arxiv.org/abs/2602.15763
confidence: medium
cleaned: 2026-11-01
---

# 10 — Engineering RL Systems

Most RL projects don't fail because someone picked the wrong algorithm. They fail because the reward was wrong, the logs had a silent shape bug, one lucky seed looked like progress, or nobody planned how a learning system gets updated in production. This chapter is the engineering around the update rule, mostly from Winder's practical chapters, each tested against what LLM RL does now: learning from experts, hierarchy, problem design, measuring runs, scaling actors and learners, and then running the result safely.

> **Pillar:** [05-RL](../README.md). **Presumes:** [01](01-rl-foundations.md). All "(ch. N)" references without a title are to Winder, *Reinforcement Learning* (O'Reilly, 2020).

---

## Learning from experts: imitation and inverse RL

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

## Beyond the flat MDP: hierarchy and curricula

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

**Horizon length alone can break LLM RL, and shortening it is the fix.** Kim et al.
([arXiv:2605.02572](https://arxiv.org/abs/2605.02572), ICML 2026) built Sudoku and Rush Hour tasks in
which only the number of required moves changes. Every Sudoku needs only basic solving techniques,
and they kept only puzzles the model could already solve when asked for the whole answer in one step. Qwen3-1.7B was given an SFT warm start
and then trained with REINFORCE and a batch-normalized baseline. On 11–20 empty cells RL improved
steadily. On 21–30 it collapsed, and the collapse came with a surge of maximum-length responses.
Letting the policy emit a variable-length **macro action** (several moves per turn) kept training
stable. Forcing the same policy back to one move per turn brought the collapse back, so the horizon
was the cause and not the better starting policy. Fixed-length macros did worse than flexible ones.
Per-subgrid rewards, a hand-designed subgoal hierarchy, also fixed it. The pattern held on WebShop,
at 4B, and with a GRPO-style optimizer. Policies trained on short horizons generalized to longer
unseen ones, which makes a short-to-long curriculum work on Rush Hour where training on the long tasks
directly did not. These are puzzle environments with one small model family, and most results are
reported as curves.

## Engineering an RL problem

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
same checklist applies to [multi-turn agent rewards](07-reward-design-and-tool-calling.md#reward-design-for-multi-turn-agents).

**Action design.** Decide whether actions are binary, discrete, continuous or mixed; whether
several can happen at once; and whether a hierarchy is hiding in them. Changing that choice
later can force a change of algorithm. For massive action spaces, policy gradients avoid the
`max`. The book's YouTube example ranks the top k items rather than choosing a combination
(ch. 9).

**Online, offline, concurrent.** Online learning explores but needs a live or simulated
environment. Offline learning uses logs but cannot explore and suffers distribution shift
(see [DQN](01-rl-foundations.md#deep-q-networks-and-learning-from-logs)). Concurrent learning runs many agents in
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

You can see the problem without training anything. These two "agents" are the same distribution, so any gap between them is an accident of the seeds:

```python
import numpy as np
from math import sqrt

rng = np.random.default_rng(0)
# Two agents with the same true mean return. Same code, different seeds.
def run_returns(n):
    return rng.normal(100, 25, n)

def welch_t(a, b):
    return (a.mean() - b.mean()) / sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))

for n in [3, 5, 15]:
    gaps, false_alarms = [], 0
    for _ in range(5000):
        a, b = run_returns(n), run_returns(n)
        gaps.append(abs(a.mean() - b.mean()))
        false_alarms += abs(welch_t(a, b)) > 2.1
    print(f"{n:2d} seeds per arm: typical gap {np.median(gaps):5.1f}, 90th percentile gap {np.percentile(gaps, 90):5.1f}, |t|>2.1 in {false_alarms / 5000:.1%}")
```

```text
 3 seeds per arm: typical gap  13.7, 90th percentile gap  33.4, |t|>2.1 in 10.2%
 5 seeds per arm: typical gap  10.5, 90th percentile gap  25.3, |t|>2.1 in 6.0%
15 seeds per arm: typical gap   6.3, 90th percentile gap  15.1, |t|>2.1 in 4.5%
```

A 14-point gap between identical agents is typical at three seeds. In the same runs, a t-statistic above 2.1 fired 10% of the time at three seeds and about 4.5% at fifteen, which is one more reason to want more runs.

## Scaling: actors and learners

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

In LLM RL the actor is usually a serving engine, most often vLLM. Its PagedAttention
([arXiv:2309.06180](https://arxiv.org/abs/2309.06180), Kwon et al., SOSP 2023) lets the samples
drawn for one prompt share that prompt's KV blocks copy-on-write, which is exactly the access
pattern of a GRPO or RLOO group. The paper measured a 6.1–9.8% KV-memory saving for 2–6 parallel
samples on OPT-13B with short Alpaca prompts, so the saving grows with prompt length. The mechanism
is covered in
[inference engineering](../../../ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache.md#pagedattention).
Because the trainer and the serving engine are separate programs, their log-probs can disagree,
which is the mismatch the reports below correct for.

**Evolution strategies are the extreme of the actor–learner split.** ES perturbs the weights,
scores each perturbed copy and averages the perturbations weighted by score. Workers exchange only
scalar fitnesses, and no gradient flows through the model. Salimans et al. (2017) scaled it this way
on MuJoCo and Atari. Sarkar et al. ([arXiv:2511.16652](https://arxiv.org/abs/2511.16652),
2025-11, preprint) make it practical at billions of parameters. EGGROLL uses rank-r (often rank-1)
perturbations, the way LoRA does, and regenerates the noise from a seed. Training then runs at **up
to 91% of pure batch-inference throughput**, where naive ES manages 0.41%. They run the
population inside vLLM as multi-LoRA serving, so the inference engine is the trainer and no
mismatch is left to correct. The results:

- On Qwen3-4B-Base with DeepScaleR maths, EGGROLL averaged 41.4% across five maths benchmarks, the same
  as an RL run. That RL figure is copied from another paper with matched settings, not rerun.
- A 14B RWKV-7 went from 13% to 30% on AIME24 after 12 hours on 32 GPUs. At that size GRPO did not
  fit in memory with Adam.
- Because fitness needs no gradient, ES can optimize pass@k directly. On Qwen3-1.7B with k=4, the
  number of distinct answers per four samples rose under pass@k training and fell under pass@1
  training.

The head-to-head wins over GRPO are on RWKV models at equal hardware and wall-clock.

Optimizer memory is also what stops gradient-based full-weight RL from fitting, and it can be cut
without leaving gradients behind. LoGRA keeps each weight's gradient as a low-rank sketch, lets the
optimizer act on the sketch, and sets the step size from a predicted-KL budget
([arXiv:2610.06647](https://arxiv.org/abs/2610.06647) (Zhang et al., 2026-10, preprint)). On
Qwen2.5-Math with PPO on one 8×H100 node, **average training memory fell 21.8% at 1.5B and 45.7% at
7B, and a 27B Qwen model trained for over 1,100 steps where dense Adam ran out of memory.** Peak MATH-500
Pass@1 was 67.87 vs 63.77 at 1.5B and 72.33 vs 72.48 at 7B. The setup is deliberately simple: math
only, one sample per prompt, a running-mean baseline. In its own comparison at 1.5B, plain LoRA had
higher mean Pass@1 (70.45 vs 68.47) at more memory (13.2 vs 7.2 GiB).

Two 2025–26 open reports show what that correction looks like now: double-sided masking of the
token-level ratio π_train / π_inference rather than a V-trace-style truncated weight.

- **INTELLECT-3.** A 106B-total / 12B-active MoE post-trained from GLM-4.5-Air on prime-rl.
  - The setup: 16 training nodes and 44 inference nodes, with in-flight weight updates.
  - Rollouts more than 8 policy versions old are discarded.
  - Tokens whose ratio falls outside [0.5, 5] are masked out of the loss
    ([arXiv:2512.16144](https://arxiv.org/abs/2512.16144) (Prime Intellect Team, 2025-12)).
  - Without the masking, runs crashed days in. In-flight updates more than halved step time.
- **GLM-5.** Agentic RL runs fully asynchronously, with the rollout engine's own log-probs as
  the behaviour policy.
  - Tokens outside [1−ε_l, 1+ε_h] are masked, and samples older than a version gap τ are
    dropped ([arXiv:2602.15763](https://arxiv.org/abs/2602.15763) (GLM-5 Team, 2026-02)).
  - Its sharpest lesson is about mismatch: a non-deterministic top-k in the sparse-attention
    indexer collapsed RL entropy within a few steps.

Neither report ablates the correction quantitatively, and GLM-5 does not disclose ε or τ.

## Running RL in production

A learning system has three lives, and Winder's advice is to optimize each for something different (*Reinforcement Learning*, ch. 10). In **development**, what counts is how fast the feedback loop turns. In **hardening**, it is provenance and the ability to rebuild a model offline. In **production**, it is preserving the policy's state and monitoring what it does. He sums up the operational needs as reliability, scalability and flexibility, and offers a hierarchy of needs for the level of automation worth paying for. His advice is to get the basics right first.

| Challenge | Required | Valuable | Optimal |
|---|---|---|---|
| Infrastructure | Manual deployment | Automated deployment | Self-healing |
| State representation | Fixed mapping | Model-driven dimensionality reduction | Continuously learning |
| Environment | Simulation | Real life | A combination |
| Learning | Online | Offline | Meta |
| Algorithm improvement | Manual | Brute-force selection | Automated |

*Adapted from Winder,* Reinforcement Learning *(O'Reilly, 2020), Table 10-1.*

**Partial feedback and delayed rewards drive the architecture.** A reward can arrive days after the action that caused it, and for a user who left it never arrives. So give Markov state changes a dedicated log, tie events together with a correlation ID so you can rebuild a trajectory, and log shapes, since a wrong shape is a common bug. Winder calls checks on this data "unit testing for data". The block below is one such check. It costs nothing, and it fails before a training run wastes a week.

```python
import numpy as np

EXPECTED = {"obs": (4,), "action": (), "reward": (), "logp": ()}

def check_transition(t):
    """Unit test for data: every logged transition has the shape and range we think it has."""
    problems = []
    for name, shape in EXPECTED.items():
        got = np.shape(t[name])
        if got != shape:
            problems.append(f"{name} shape {got}, expected {shape}")
        elif not np.all(np.isfinite(t[name])):
            problems.append(f"{name} is not finite")
    if not problems and t["logp"] > 0:
        problems.append("logp above 0 is not a probability")
    return problems

good = {"run_id": "r7", "obs": np.zeros(4), "action": 1, "reward": 0.5, "logp": -0.7}
batched = {**good, "reward": np.ones((1, 32))}     # the classic bug: a batch where a scalar belongs
broken = {**good, "logp": 0.3}
for name, t in [("good", good), ("batched reward", batched), ("bad logp", broken)]:
    print(f"{name:<15}", check_transition(t) or "ok")
```

```text
good            ok
batched reward  ['reward shape (1, 32), expected ()']
bad logp        ['logp above 0 is not a probability']
```

**Experiment tracking and tuning.** Track every run, because you'll want to compare them later. Tools like Optuna handle hyperparameter search, but beware of early stopping: it can kill slow starters, and RL is full of those.

**Rolling out a new policy.** The standard options all work, with RL-specific catches:

- **Canary** with stickiness, so one user stays on one policy for a whole trajectory.
- **Shadowing**, which tests decisions at no risk, but a hidden agent can't explore: its actions never happen, so it only sees the data produced by the current policy.
- **Bandit A/B**, which shifts traffic automatically towards the winner.
- **Ensembles**, which combine several policies at the cost of explaining their joint behaviour.

**Stay close to "never".** Updates run along a continuum from continuous, through batch, to never, and Winder argues for staying as near to never as your problem allows. Treat every policy update as a new immutable deployment. Matsushima et al.'s deployment-efficiency work, which he cites, updates only when trajectory divergence is large. LLM products sit at the far end: weights stay frozen between releases, and learning happens in a training run offline.

```text
how often the live policy changes

 continuous            batch                     never
 ──┬────────────────────┬─────────────────────────┬──▶
   │                    │                         │
   learns in place      new version, on a         frozen after training;
   highest risk         schedule, deployed        this is where almost every
                        like any release          LLM deployment sits
```

**Safe RL.** How do you stop an agent from learning safety by doing unsafe things? Winder lists four approaches, and calls the problem open:

- **Constrained optimization**, as in TRPO and PPO, constrained SAC, and the work of Ha et al.
- **Reward penalties**, which are simple and hardcoded, and offer no guarantee. The agent has to do the unsafe thing to learn the penalty. This is the penalty half of [RLVP](07-reward-design-and-tool-calling.md#rlvp-reward-the-outcome-penalize-the-path).
- **External filters** over known-safe states, or abort and reset controllers (Eysenbach et al.).
- **Formal constraints**, mostly shown on toy problems so far (Hunt et al.'s action filter).

**Secure RL.** RL has a bigger attack surface than ordinary ML: environment, observations, rewards, actions, replay buffer and parameter server. Attacks come at training time (poisoning) or at prediction time, in white-box and black-box forms, and they transfer between models. Fix the basics first. He cites a 2019 Symantec report in which 65% of targeted attacks used phishing and 23% unpatched software, against 1% aimed at data storage, so open SSH ports and missing MFA come before adversarial defences. Then monitor data integrity and rate-limit. For research-grade defences, Behzadan & Munir perturb agents during training, and Liu et al. detect attacks from divergence in next-state predictions.

**Ethical RL.** An engineer who sets a reward holds real power over whoever the system acts on. Keep humans responsible for important decisions, and be able to explain the system to stakeholders. Winder's checklist is short enough to run before launch: bias, personal impact, climate, unintended use, nefarious use, legality, human rights, justification and explainability, and honest claims about performance. Fairness problems may only appear over time: ML-fairness-gym simulates long-term effects, such as what credit decisions do to credit scores across a population.

**Choosing a framework.** The same chapter's checklist still applies: right abstractions, simplicity, observability, scalability, minimal dependencies, documentation, the algorithms you need, ancillary tooling, support and commercial terms. In LLM RL the candidates are newer ([TRL](https://huggingface.co/docs/trl/), veRL, and the tooling in [07](07-reward-design-and-tool-calling.md#judges-as-rewards-ruler-art-and-rllm)), and the questions are the same.

## What has dated since 2020

Winder's book predates LLM RL. The foundations hold; the defaults have moved:

| 2020 view (*Reinforcement Learning*) | 2025–26 LLM RL |
|---|---|
| Most state-of-the-art algorithms are off-policy (ch. 1) | PPO and GRPO are on-policy; replay buffers are rare |
| SAC beats PPO; entropy bonuses drive exploration (ch. 7) | Discrete tokens, KL to a reference model; entropy *collapse* is the problem |
| Behavior cloning overfits and is unpopular (ch. 8) | Pretraining plus SFT is behavior cloning, and it comes first |
| A learned critic (A2C, PPO) is the standard baseline (ch. 5–6) | GRPO and RLOO drop the critic and use group statistics ([03](03-preference-optimization.md), and the REINFORCE paragraph in [01](01-rl-foundations.md#policy-gradients-from-reinforce-to-the-ppo-clip)) |
| Rewards are shaped by hand or learned by IRL (ch. 8–9) | Learned reward models (RLHF) or verifiable checkers (RLVR) |
| Tabula rasa agents are sample-inefficient (ch. 11) | A pretrained prior makes exploration targeted: in [05](05-post-training-for-agents.md)'s treasure hunt, Q-learning needs ~10,000 episodes and an LLM agent wins on the first try |
| Offline learning is the field's biggest open challenge (ch. 11) | Partly solved for preferences (DPO); online RL is still preferred for reasoning |

## Pitfalls

- **Publishing a single seed.** One run is one sample. The table above shows how far two identical agents can land apart with three seeds. Colas et al. needed at least 15 to separate SAC from TD3.
- **Rushing to a deep model.** Check a random policy and a simple baseline first. If a random policy never stumbles on the right behaviour, RL is unlikely to find it.
- **Silent shape bugs.** A batched reward broadcast against a scalar value trains without any error. Check shapes in the log.
- **Trusting the training reward.** A rising reward can mean the agent found a hack. Keep a separate metric of the true goal.
- **Learning live by default.** Continuous learning is the riskiest end of the continuum. Choose it only with a reason, and with a rollback.

## Try it

1. Add another check to `check_transition`: rewards must lie within the range you defined for the problem. Feed it a reward of `1e6`.
2. In the seed block, double the noise while keeping the true gap at zero. Does the false-positive rate of `|t| > 2.1` change? Why not?
3. Pick an RL or post-training idea of your own and fill in the three lives: what is the feedback loop in development, what do you need to rebuild the model in hardening, and which single signal would you alert on in production?

<details><summary>Answers</summary>

1. Add `if abs(t["reward"]) > 100: problems.append("reward out of range")`, inside the same guard as the `logp` check. A range check is often the first thing to catch a reward-function bug.
2. It stays about the same: the t-statistic divides by the noise, so scale cancels. The typical *gap* doubles, though. A raw gap looks like progress even if the test says otherwise.
3. There's no single answer. A good production signal measures the goal and is independent of the training reward, such as a held-out human-graded sample.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| How many seeds should you run? | More than feels necessary: Colas et al. needed at least 15 to separate SAC from TD3 on one task. Plot per-seed curves, then test. |
| What are the actors and learners for? | Actors generate experience and learners update the policy, so sampling and optimization scale separately. |
| How do you deploy a new RL policy? | As an immutable release, with a canary or shadow stage. Stay as near to "never update live" as the problem allows. |
| How do you make RL safe? | Constrain the optimizer, filter actions, abort and reset, or add penalties, knowing penalties alone give no guarantee. It is an open problem. |
| What's different about RL security? | A bigger attack surface: rewards, observations and replay buffers can all be poisoned. Fix basics such as phishing and patching first. |
| What has dated since 2020 in Winder's advice? | Behaviour cloning is now the first step, critics are often dropped, and offline RL is partly solved for preferences. |

## Next

[11 — Multi-agent RL and RAG](11-multi-agent-and-rag-rl.md) covers the two places RL meets the rest of the agent stack: several learners at once, and retrieval as a decision problem.
