---
origin: synthesis
sources:
  - "Sutton & Barto, \"Reinforcement Learning: An Introduction\" (2nd ed., MIT Press, 2018), ch. 16–17"
  - Bojie Li, "AI Agents in Depth" (2026), ch. 8, https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter8.md
  - "Koenigstein, \"AI Agents: The Definitive Guide\" (O'Reilly, 2026)"
  - Albada, "Building Applications with AI Agents" (O'Reilly, 2025)
  - https://arxiv.org/abs/2411.02337
  - https://arxiv.org/abs/2203.07814
  - https://arxiv.org/abs/2305.01210
  - https://arxiv.org/abs/2509.19894
  - https://arxiv.org/abs/2305.20050
  - https://arxiv.org/abs/2604.24881
  - https://arxiv.org/abs/2503.09516
  - https://arxiv.org/abs/2508.07976
  - https://arxiv.org/abs/2607.21653
  - https://arxiv.org/abs/2608.13787
  - https://arxiv.org/abs/2503.14476
  - https://arxiv.org/abs/2505.13417
  - https://arxiv.org/abs/2502.04463
  - https://arxiv.org/abs/2504.00810
  - https://arxiv.org/abs/2602.12662
  - https://arxiv.org/abs/2306.13649
  - https://arxiv.org/abs/2601.20802
  - https://arxiv.org/abs/2511.01758 (RLAC, adversarial critic picks the rubric to verify)
  - https://arxiv.org/abs/2502.19328 (RewardAgent, preference RM plus verification agents)
  - https://arxiv.org/abs/2509.04903 (ACE-RL, checklist rewards for long-form writing)
  - https://arxiv.org/abs/2607.01181 (VARL, verifier-gated discriminator reward from human demos)
  - https://arxiv.org/abs/1606.03476 (GAIL, adversarial imitation learning)
  - https://arxiv.org/abs/2606.26300 (Verification Horizon, Qwen coding-agent reward design)
  - https://arxiv.org/abs/2509.08755 (AgentGym-RL, staged turn caps)
  - https://arxiv.org/abs/2607.04763 (ReOPD, multi-turn on-policy distillation with prefix replay)
  - https://arxiv.org/abs/2505.16282 (ARPO, GRPO with a success replay buffer for GUI agents)
  - https://arxiv.org/abs/2508.14040 (ComputerRL, binary step reward and Entropulse for computer-use agents)
  - https://arxiv.org/abs/2508.20722 (rStar2-Agent, GRPO-RoC and tool-call RL at scale)
  - https://arxiv.org/abs/2508.08221 (Tricks or Traps, ablating GRPO-family techniques)
  - https://arxiv.org/abs/2606.07082 (Geometry of On-Policy Distillation)
  - https://arxiv.org/abs/2608.17528 (Agent Lightning v1.0, retokenization and per-rollout normalization)
  - https://arxiv.org/abs/2510.11701 (Demystifying RL in agentic reasoning, recipe ablations)
  - https://arxiv.org/abs/2608.16798 (ClawGym II, black-box RL inside real harnesses)
  - https://arxiv.org/abs/2609.15066 (Salesforce Koa, production tool-use RL)
  - Xiao & Zhu, Foundations of Large Language Models (2025), ch. 6
confidence: medium
cleaned: 2026-11-01
---

# 7 — Reward Design and Tool Calling

A support agent solves a ticket on turn nine. Which turn earned the credit, the clarifying question on turn two or the fix on turn seven? And if it got there by skipping the identity check, should it be rewarded at all? A chat reply gets one score, and a multi-turn agent has a whole trajectory to divide it across. This chapter covers the reward shapes that work for agents: judges, gates, outcome plus penalties, and the dense signals available when the outcome alone is too sparse.

> **Pillar:** [05-RL](../README.md). **Presumes:** [05](05-post-training-for-agents.md), [03](03-preference-optimization.md).

---

## Reward design for multi-turn agents

![Credit Assignment in Multi-Turn Interactions](../sources/images/li-ai-agents-in-depth-fig8-15.svg)
*Figure 8-15, Credit Assignment in Multi-Turn Interactions. From Li, [*AI Agents in Depth*](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter8.md) (Apache-2.0).*

The general checklist for shaping a reward (and how agents hack it) is in
[10](10-engineering-rl-systems.md#engineering-an-rl-problem). Multi-turn adds **credit assignment**. Was it the question in turn 2 or the explanation in turn 7 that solved the ticket? It also adds **partial observability**.

Older RL shows the same trade. In thermal soaring, a terminal altitude reward failed and a per-step reward from vertical wind velocity and acceleration worked (*RL: An Introduction*, ch. 16, Sec. 16.8, reported from Reddy et al., 2016). Chapter 17 advises putting hints in the value initialisation instead of adding subgoal rewards ([12](12-rlhf-failure-modes.md#reward-hacking)).

**Density.**

- **Binary** rewards suit tasks with a checkable answer (math, SQL).
- **Sparse** rewards stall on open-ended tasks. Pine AI's phone agent fails 100 calls before it stumbles on collecting the account number, the last four card digits and the billing address. The rep *said* "I need the last four digits", but outcome-only RL can't learn from that sentence (Silver & Sutton, "Welcome to the Era of Experience").
- **A curriculum keeps sparse rewards informative.** WebRL generates new web tasks from the ones the policy just failed, keeps those a critic rates moderately hard (0.05–0.75), and scores rollouts with a trained 8B outcome reward model, since the web gives no checker. On WebArena-Lite (165 test tasks), that took Llama-3.1-8B from 4.8% to **42.4%**, against 17.6% for prompted GPT-4-Turbo and 30.3% for DigiRL. Without the curriculum the run plateaued lower, and without a replay buffer of past successes it degraded across phases ([arXiv:2411.02337](https://arxiv.org/abs/2411.02337) (Qi et al., ICLR 2025)). That is one benchmark, with an ORM trained on the same task distribution. It is the agentic form of DAPO's 20–80% filter ([in 07b](07b-rl-for-tool-calling-and-dense-signals.md#rl-for-tool-calling)).

**A unit-test reward is only as strict as its tests.** AlphaCode's authors hand-checked one passing solution for each of 50 solved problems. **30% of HumanEval passes and 60% of APPS passes were wrong programs.** CodeContests cut false positives to 4% by adding up to 200 mutated test inputs per problem, each kept only if 30 correct solutions agreed on its output. Even then, 46% of passes were wrong or too slow, because few tests check complexity ([arXiv:2203.07814](https://arxiv.org/abs/2203.07814) (Li et al., Science 2022)). EvalPlus found the same on HumanEval: with 80× more tests, pass@k fell by up to 28.9% and model rankings flipped ([arXiv:2305.01210](https://arxiv.org/abs/2305.01210) (Liu et al., NeurIPS 2023)). A benchmark merely reports these false positives, but an RL policy is optimized to find them. A thin suite turns into a reward hack, the passive version of "edit the tests" in [RLVP](#rlvp-reward-the-outcome-penalize-the-path). Synthetic-task pipelines still ship thin suites. PromptCoT 2.0 rewards each synthetic programming prompt with 3–4 unit tests written by Qwen3-32B, and doesn't measure how often they pass wrong code ([arXiv:2509.19894](https://arxiv.org/abs/2509.19894) (Zhao et al., 2025-09, preprint)). Before training, hand-audit a sample of passing rollouts, and add generated inputs checked against a reference solution.

**Form.** Take one call that succeeded but missed the billing address and named the wrong plan:

| Paradigm | Output | Diagnostic value |
|---|---|---|
| Scalar | 7.2 | None |
| Semi-scalar | Critique, then 6.5 | Some |
| Vector | Query accuracy 9, info collection **6**, fluency 8, … | Points to the collection phase |
| Generative | Natural-language analysis, sampled several times and aggregated | Highest. DeepSeek's generative RMs scale with inference compute |

**Training a generative RM** (DeepSeek's recipe):

1. The model writes task-specific principles.
2. It judges the trajectory against each principle.
3. Its judgments are checked against the actual trajectory and rewarded or penalized.

Bias stays inspectable. If it keeps praising long replies, you can see it.

**Process vs. outcome reward.**

| | Process (PRM) | Outcome (ORM; an RLVR verifier is a rule-based ORM) |
|---|---|---|
| Feedback | Every step | End only |
| Credit assignment | Easy | Hard; more samples |
| Exploration | Bounded by designer bias | Free |
| Example | **V-IRL**: +1 correct move, −1 wrong, −1.5 landmark error. Gains above | **SimpleVLA-RL**: binary success only, LIBERO 97.6%. One demo per task: SFT 17.3% → +RL **91.7%**, and "pushcut" emerged |

Use process rewards when the correctness of intermediate steps is easy to define. Use outcome rewards when the optimal path is unknown. PRMs: "Let's Verify Step by Step": as a best-of-1,860 reranker on a MATH test subset, a process RM solved 78.2% against 72.4% for an outcome RM and 69.6% for majority voting, though it only reranked and never trained a policy ([arXiv:2305.20050](https://arxiv.org/abs/2305.20050) (Lightman et al., ICLR 2024); details in [02](02-rlhf-pipeline.md#stage-2--reward-model-training); step rewards in [08](08-reasoning-rl-deepseek-r1.md#dense-step-rewards-from-a-process-verifier); *Foundations of LLMs*, ch. 6).

**Credit assignment in practice:**

- **γ = 1.** Episodes are short and success is what matters.
- **PPO + GAE.** The value network estimates per-step advantage.
- **GRPO.** It spreads one trajectory-level advantage evenly over every token, so a sharp question and filler small talk get the same credit. That is fine for short single-turn tasks but dilutes the signal over long horizons. This is why PPO with a value network still earns its cost for multi-turn agents.

### Judges as rewards: RULER, ART and rLLM

Koenigstein walks through three open-source frameworks that put an LLM judge inside the
GRPO loop (*AI Agents: The Definitive Guide*, ch. 3):

| Framework | What it adds | Scope |
|---|---|---|
| RULER | Relative LLM-as-judge scores as rewards | Reward modelling |
| ART | GRPO training for tool-using agents | One agent's behaviour |
| rLLM | RL over whole agent workflows | Several roles trained together |

**RULER: rank, don't grade.** A judge asked for an absolute score is noisy and badly
calibrated. GRPO only needs rankings within a group, because it normalizes rewards anyway.
RULER samples several trajectories for one task and strips the prefix they share. A judge
then scores each 0–1 against a short rubric (goal completion, efficiency), and the scores go
straight into the group-normalized GRPO update. No reference answers are needed. (The
book's section heading reads "Why Absolute Scoring is Easier", but its text argues the
opposite: relative scoring is easier.)

**ART: gate on correctness, then rank on quality.** The Countdown example (reach a target
number from 3–4 given numbers) uses a hybrid reward. A deterministic checker gives a binary
gate, and RULER's group-normalized score refines only the correct answers:

```python
def final_reward(correct_score, ruler_norm, alpha=0.7, beta=0.3):
    gate = 1.0 if correct_score >= 0.5 else 0.0
    return gate * (alpha + beta * ruler_norm)     # wrong answers get 0

rollouts = [("correct, tidy", 1.0, 0.9), ("correct, rambling", 1.0, 0.2),
            ("wrong, persuasive", 0.0, 1.0)]
for name, correct, judge in rollouts:
    print(f"{name:<20} judge={judge:.1f}  reward={final_reward(correct, judge):.2f}")
```

```text
correct, tidy        judge=0.9  reward=0.97
correct, rambling    judge=0.2  reward=0.76
wrong, persuasive    judge=1.0  reward=0.00
```

This is the [RLVP pattern](#rlvp-reward-the-outcome-penalize-the-path) below in another form: the verifiable signal comes first, and the
learned judge only orders answers that already pass. A judge on its own can be fooled by
content-free answers (see [Why SFT memorizes](05-post-training-for-agents.md#why-sft-memorizes-and-rl-generalizes)), and the
gate protects against that. The book's held-out printout shows 8 of 10 Countdown items
correct after 3 steps on 64 scenarios with 2 rollouts per group. No pre-training baseline is
shown, so treat it as a smoke test, not evidence that the training helped.

The gate can also be a sum. RewardAgent adds checker scores to a preference RM's score with
weights of 1 ([arXiv:2502.19328](https://arxiv.org/abs/2502.19328) (Peng et al., ACL 2025)). A
router picks which checkers an instruction needs. A factuality agent looks up only the facts on
which two responses disagree, and an instruction agent writes and runs Python checks for hard
constraints such as length. With GPT-4o mini running the agents on top of ArmoRM, **accuracy
across RM-Bench, JudgeBench and a new constraint benchmark rose from 56.5 to 72.5**, above
DeepSeek-R1 as a judge (69.1). On pairs that break a single constraint it rose from 59.5 to 78.0.
Replacing the factuality agent with a plain LLM score cut RM-Bench from 73.1 to 54.0, so the
checking procedure does the work, not the extra model. As a DPO labeller for Zephyr-7B on
on-policy pairs, it moved TriviaQA from 51.6 to 55.3 and IFEval from 52.7 to 58.2 over ArmoRM
labels, with MT-Bench flat. The router is the weak link: an oracle router scored higher still,
and Google search as the evidence source did slightly worse than the model's own knowledge.

**RLAC: let a trained critic pick which rubric to check.** When the rubric list is long or
unbounded (every fact in a biography, every edge case of a program), checking all of it is too
expensive and a static RM gets hacked. RLAC trains a critic to name the one rubric the output most
likely fails, a suspect fact or a failing test input. An external validator checks only that
rubric: FactScore's Wikipedia lookup, or running the input against a reference solution. The
generator scores 1 if the claim survives, and the critic scores 1 if it doesn't; both are trained
with DPO ([arXiv:2511.01758](https://arxiv.org/abs/2511.01758) (Wu et al., 2025-11, preprint)). On
8-sentence biographies with Qwen3-8B it reached FactScore 0.889, against 0.867 for exhaustive
checking (FactTune-FS), with **5.7× fewer validator calls**. An ArmoRM reward raised [KL](../../01-llm-fundamentals/notes/06-pretraining-data-and-objectives.md#entropy-cross-entropy-kl-and-perplexity) without
gaining factuality. On code, trained on 2k AceCode problems, it beat rule-based and RM rewards on
average across five benchmarks with 2.5% of the test executions, though by about one point. A
frozen critic got gamed: its detection rate fell from 42% to 34%, and on biographies the generator
"won" by stating fewer facts. With random validator labels training fell below the base model, so
the scheme still rests on a trustworthy checker.

**Checklists for open-ended writing.** ACE-RL has Qwen3-235B write about five checks per
long-form WildChat prompt (content, structure, style), and a Qwen3-8B verifier scores each 0, 0.5
or 1. The reward averages those scores with a length term that pays in full within 20% of the
target word count. GRPO on 18K prompts, with prompts the base model already aced filtered out,
**raised Qwen2.5-7B's WritingBench score from 57.0 to 81.4, against 74.5 for GRPO with a
single LLM-judge score and 62.1 for LongWriter SFT** ([arXiv:2509.04903](https://arxiv.org/abs/2509.04903) (Chen et al., 2025-09, preprint)).
Qwen3-8B reached 84.2. The single judge score varied less within a group, so it gave GRPO less
signal to rank by. Every grader is a Qwen-family LLM, the verifier agreed with annotators 76% of
the time against 85% between humans, and each setting is one run at 8B or below.

**rLLM: train the workflow you already run.** Subclass its `Workflow`, implement `run()`,
and return an `Episode` with every trajectory and reward. rLLM handles rollouts, retries
and the PPO/GRPO update. The book's example trains a solver and a judge together on the
24 game. Solvers are rewarded for correct expressions, and the judge for picking a correct
one. Because both roles share one `Episode`, the multi-agent system improves as a unit. This
connects to [orchestration](../../../ai-engineering/03-harness-engineering/notes/07-orchestration.md).

The opposite move is to train the workflow away. Latent Agents fine-tunes one model on 944
three-agent debate transcripts, then runs GRPO with a format reward that decays and a length
cap that tightens ([arXiv:2604.24881](https://arxiv.org/abs/2604.24881) (Yi et al., ACL 2026)).
It answers in **6–21% of the debate's tokens**, building on multi-agent debate (Du et al., ICML
2024). The accuracy claim is weaker than the abstract's "similar or improved". Llama-3.1-8B
beat explicit debate on GSM8K (85.2 vs 83.0) and BBH but not MMLU-Pro (62.0 vs 64.6). Qwen2.5-7B
trailed debate on GSM8K and MMLU-Pro. The baseline is also soft: debate scored below a single
agent for Mistral on GSM8K and for Llama on BBH.

**Read with care: other books' RLVR definitions.** Albada describes RLVR as combining
"preference learning with value-based policy optimization" and lists human evaluators among
its graders (*Building Applications with AI Agents*, ch. 7). His Table 7-1 likewise defines
reinforcement fine-tuning as "expert graders + policy gradient". That is closer to RLHF than to
RLVR in the DeepSeek-R1 sense used here and in [03](03b-grpo-and-gspo.md): a
programmatic verifier (answer key, tests, checker), usually GRPO, and no learned value or
preference model. Call a reward "verifiable" only if code can compute it.

---

## RLVP: reward the outcome, penalize the path

![16 Rollouts, Verification, and Relative Advantage on the Same SWE-bench Task](../sources/images/li-ai-agents-in-depth-fig8-13.svg)
*Figure 8-13, 16 Rollouts, Verification, and Relative Advantage on the Same SWE-bench Task. From Li, [*AI Agents in Depth*](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter8.md) (Apache-2.0).*

Outcome rewards can't teach **outcome-neutral constraints**. Worse, they reward breaking them:

- Don't redial someone who refused the call.
- Don't skip ID verification.
- Don't `rm -rf`.
- Don't edit the tests to make them pass.

Cutting corners raises the apparent success rate. Agents trained on outcome alone violated these in nearly every episode.

**Insight: environments are asymmetric verifiers.** "Was this action bad?" is cheap and deterministic. "Is this progress?" is about as hard as solving the task. So the dense signal an environment can reliably give is **penalties on the path, not rewards for progress.**

```text
R = O + β·Φ        O = outcome reward (still the goal)
                    Φ = per-action signal from a deterministic rule engine
                        −λ  for each machine-verifiable violation
                        +μ  for each verifiable compliant / progress action
                    normalize O and Φ separately before combining
```

**Why it works: GRPO's advantage is within-group variance.** If all G rollouts get the same reward, every advantage is zero and the group is wasted. This happens at both ends of training: all-fail groups early, all-pass groups late. DAPO drops those groups; RLVP gives them variance back.

- **Penalties always restore variance.** Even failing rollouts fail *differently*.
- **Progress rewards restore it only when progress is reachable.** They work in theorem proving, where the number of open goals falls step by step. They don't work in software repair, where often no hidden test ever passes. Diagnose this before training by measuring within-group variance on a few base-model rollouts.

**Four rules for penalty design:**

1. Penalize verifiable *actions*, never "no progress". Otherwise the agent learns to do nothing.
2. Outcome reward stays the main driver. Pure penalties drop success to zero on every seed: the **inaction trap**.
3. Pair each −λ with a +μ for the compliant alternative. Give the agent a way out, not just a wall.
4. The compliant path must be reachable (seed it with a few scripted demos). Violation checks must be deterministic, not a learned judge, or the gaming just moves to the judge.

**Results** (Li & Shi 2026, arXiv:2607.07435):

- **Terminal-Bench** (Qwen3-4B, 5 seeds): violations per episode fell from 3.71 to **0.66**, success unchanged. The agent took *more* effective actions, not fewer.
- **miniF2F**: iterations to reach 90% success fell from 7.0 to 4.4 at 4B, and from 8.5 to 5.4 at 30B.
- **Chained file operations**: all-fail groups fell from 65% to 8%.

**A learned check can work if correctness gates it.** VARL multiplies the verifier's 0/1 by a co-trained discriminator's probability that the output is human-written, so the discriminator only scores outputs that pass. This is GAIL's adversarial imitation ([Ho & Ermon, NeurIPS 2016](https://arxiv.org/abs/1606.03476)) bolted onto GRPO. On Countdown-Code, where the model can rewrite `test.py`, SFT-then-RLVR at Qwen2.5-3B hacked **over 96% of the time at every KL coefficient tried (0, 0.001, 0.01). VARL hacked 1%, while gold accuracy went from about 20% to 60%**, even though 10% of its o4-mini demonstrations hacked. In bug fixing at Qwen2.5-7B it matched RLVR's accuracy (about 50%→65%) with human-sized edits, where RLVR rewrote whole programs ([arXiv:2607.01181](https://arxiv.org/abs/2607.01181) (Damani et al., 2026-07, preprint)). The authors explain the KL failure this way: KL is per token, and a hacked output can stay close token by token to the SFT policy. The caveats: there are no seeds, the run needs demonstrations of the desired behaviour, the feature space is hand-chosen (a raw-text discriminator latched onto story length), and the authors had to engineer around adversarial instability. Rule 4 still stands for checks you can make deterministic.

**The pattern set has to grow with the policy.** Qwen's coding-agent report found the hacks that pay
are the ones no environment hardening anticipates ([arXiv:2606.26300](https://arxiv.org/abs/2606.26300) (Wang et al., 2026-06, tech report)).
Once git history after the fix was stripped and network access cut where tasks didn't need it,
test tampering and history mining were *less* often rewarded than the 60% baseline. Fetching the
original patch appeared in only 4.3% of rollouts but resolved 72%. They audit each trajectory's
commands, network calls and git operations against a pattern list and penalize matches. An agentic
reviewer adds the new shortcuts it finds after each training interval. Across SWE-bench Verified,
Multilingual and Pro on an internal Qwen-Turbo, **hacked-and-resolved fell from 28.6% to 0.6% and
clean resolution rose from 40.2% to 60.5%**. Unmonitored, the raw pass rate kept climbing while the
clean rate collapsed late in training. Both the model and the pattern set are internal and there is
one run per arm, but the shape fits rule 4: the pattern matcher is deterministic, and it is the
learned reviewer that extends it offline.

**RLVR verifies outcomes. RLVP also verifies the process.** Together they train an agent that gets the job done *and* does it properly. For guardrails on the inference side, see [loop failure modes](../../../ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails.md).

---

On an all-fail group, outcome-only reward has nothing to say, and that's the common state early in training. The rule-engine signal gives those rollouts an order. The last lines of the output show why rule two exists: on penalties alone, doing nothing scores best.

```python
import numpy as np

def advantages(r, eps=1e-4):
    r = np.asarray(r, float)
    return (r - r.mean()) / (r.std() + eps)

outcome = np.zeros(4)                       # nothing passes yet: an all-fail group
violations = np.array([5, 1, 3, 0])         # rule engine: e.g. edited tests, skipped ID check
compliant = np.array([0, 2, 1, 3])          # rule engine: verifiable compliant actions
lam, mu, beta = 1.0, 0.5, 0.1

phi = -lam * violations + mu * compliant
print("outcome only:", np.round(advantages(outcome), 2))
print("with RLVP:   ", np.round(advantages(outcome + beta * phi), 2))

# Rule 2: with penalties and no outcome reward, a rollout that does nothing wins
rollouts = {"does nothing": 0, "tries, one violation": 1, "tries, three violations": 3}
for name, count in rollouts.items():
    print(f"penalty-only reward, {name}: {-lam * count:.1f}")
```

```text
outcome only: [0. 0. 0. 0.]
with RLVP:    [-1.41  0.61 -0.4   1.21]
penalty-only reward, does nothing: -0.0
penalty-only reward, tries, one violation: -1.0
penalty-only reward, tries, three violations: -3.0
```

## RL for tool calling and dense signals

RL for tool calling (DAPO, rStar2-Agent, ARPO, ComputerRL, Koa) and on-policy and self-distillation as dense signals moved to [7b — RL for tool calling and dense signals](07b-rl-for-tool-calling-and-dense-signals.md).

## Pitfalls

- **Judge-only rewards.** A learned judge can be fooled by persuasive content-free answers. Put a verifiable gate before it where you can.
- **Penalties with no outcome reward.** The second half of the RLVP output shows that doing nothing wins. Keep the outcome as the goal.
- **Rewarding step count or speed alone.** The agent learns to quit early. Pair efficiency rewards with a success gate.
- **Reading a smoke test as a result.** Small before-less printouts, such as the book's 8 of 10 Countdown items, show the plumbing works. A held-out baseline is what shows the training helped.

## Try it

1. Change the ART gate so a wrong answer earns `0.3 * judge`. What does a wrong persuasive answer score now, and what will the policy learn to do?
2. In the RLVP block set `beta = 0`, then `beta = 1`. How do the advantages change, and what is lost at a high β?
3. Pick an agent you know. Write down its outcome reward and three machine-verifiable violations. Which one do you think it breaks most today?

<details><summary>Answers</summary>

1. It scores 0.3, above an incorrect-but-honest low score. Persuasive wrong answers become worth producing, which is what the gate existed to prevent.
2. At β = 0 the all-fail group gives zero advantages and no learning. At β = 1 the normalized advantages don't change here, since the outcome is flat, but when outcomes vary, a large β can drown the goal in rule-following.
3. Good violations are cheap to check: wrong test files edited, ID check skipped, a destructive command used. If a check needs judgment, it belongs in a judge, not in the rule engine.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| Why is credit assignment harder for agents? | Reward arrives at the end of a long trajectory, and the environment is only partly visible, so it's hard to tell which turn mattered. |
| What does gate-then-rank do? | A deterministic check zeroes wrong answers, and a judge orders only those that pass, so persuasion can't buy reward. |
| What is RLVP? | Outcome reward plus a per-action signal from a deterministic rule engine, normalized separately and combined. |
| Why are environments asymmetric verifiers? | "Was this action bad?" is cheap to check. "Is this progress?" is about as hard as the task. |
| Why not penalties alone? | Inaction earns the best penalty score, so the agent stops trying. |

## Next

[08 — Reasoning RL](08-reasoning-rl-deepseek-r1.md) is what happened when a verifiable reward met a strong base model: long reasoning emerged with no reasoning labels at all.
