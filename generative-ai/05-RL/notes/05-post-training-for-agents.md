---
origin: book-condensed
sources:
  - https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter8.md (Apache-2.0)
  - https://arxiv.org/abs/2504.13837 (RLVR and the base model's reasoning boundary)
  - https://arxiv.org/abs/2507.08794 (LLM-judge verifiers fooled by content-free answers)
  - https://arxiv.org/abs/2503.04412 (AB-MCTS, adaptive branching tree search)
  - https://arxiv.org/abs/2404.00282 (survey of LLM-enhanced RL)
  - https://arxiv.org/abs/2511.18397 (natural emergent misalignment from reward hacking)
  - https://arxiv.org/abs/2506.19823 (persona features control emergent misalignment)
  - https://arxiv.org/abs/2411.07279 (test-time training for few-shot learning)
  - https://arxiv.org/abs/2601.16175 (TTT-Discover)
  - https://arxiv.org/abs/2602.15763 (GLM-5)
  - https://arxiv.org/abs/2512.16144 (INTELLECT-3)
  - Huyen, AI Engineering (O'Reilly, 2025), ch. 8
  - Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), ch. 5
  - Albada, Building Applications with AI Agents (O'Reilly, 2025), ch. 7
  - Koenigstein, AI Agents: The Definitive Guide (O'Reilly, 2026), ch. 3
  - Raieli & Iuculano, Building AI Agents with LLMs, RAG, and Knowledge Graphs (Packt, 2025), ch. 8
confidence: medium
cleaned: 2026-11-01
---

# 5 — Post-Training for Agents

> **Pillar:** [05-RL](../README.md)
> **Presumes:** [02-rlhf-pipeline.md](02-rlhf-pipeline.md), [03-preference-optimization.md](03-preference-optimization.md)
> **Source:** Bojie Li, *AI Agents in Depth* (2026), ch. 8 — [book-en/chapter8.md](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter8.md) (Apache-2.0)
> **Also folded in:** Huyen, *AI Engineering*, ch. 8; *LLM Engineer's Handbook*, ch. 5; Albada, *Building Applications with AI Agents*, ch. 7; Koenigstein, *AI Agents: The Definitive Guide*, ch. 3; Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. 8 (see [references](../references.md#books))

The Q-learning agent in the treasure-hunt lab needs about 10,000 games, and an LLM agent wins the same game on its first try in 18 moves. So when is training weights worth it at all, and what should it be? This chapter is the decision guide every agent team needs. Two threads run through it: **SFT memorizes, RL generalizes**, and **data and environment matter more than algorithms**, a thread the next chapter, [06](06-data-and-environments.md#data-and-environment--algorithm), picks up.

---

## The three stages

![SFT→RL Two-Stage Training Pipeline; Mid-training Precedes These Two Behavioral-Alignment Stages](../sources/images/li-ai-agents-in-depth-fig8-11.svg)
*Figure 8-11, SFT→RL Two-Stage Training Pipeline; Mid-training Precedes These Two Behavioral-Alignment Stages. From Li, [*AI Agents in Depth*](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter8.md) (Apache-2.0).*

| Stage | Data | Objective | What it learns | Cost |
|---|---|---|---|---|
| **Pretraining** | Raw internet text | Next-token prediction | Language, world knowledge, basic reasoning | Millions to tens of millions of USD |
| **SFT** | Thousands to tens of thousands of input → output demos | Next-token prediction, with loss **masked to the response** | Instruction following, format, style, process protocol | Hours to days |
| **RL** | Task + reward function (no reference answer) | Maximize expected reward | Transferable strategy; solutions no one demonstrated | Often 10–100× SFT |

**SFT is pretraining on different data.** Same loss, same mechanism. The only engineering difference is loss masking, so the model learns to answer rather than to ask. Because it maximizes the likelihood of one reference answer, SFT encodes **protocol knowledge** (how to say or do things). It does not encode large amounts of **factual knowledge**. Facts come from pretraining, continued pretraining or RAG.

**SFT before RL.** RL scores the model's own outputs. If the output isn't parseable JSON or a valid tool call, the reward can't be computed, and RL learns from noise. SFT establishes the form, then RL pursues the strategy. The book calls this "form first, spirit second". Two boundary cases:

- A strong enough base model can skip SFT. DeepSeek-R1-Zero learned reflection and long chains of thought from pure RL.
- The cost was poor readability and mixed languages, so R1 added cold-start SFT back.
- With a smaller base model and strict structured output (Llama-3.2-Vision-11B in Exp 7-11), RL without SFT fails completely.

**A worked open recipe: Tülu 3.** The table compresses post-training into SFT then RL. Open
recipes usually put a preference stage between them. Tülu 3 is the fully open reference: data,
code, intermediate checkpoints and evals for every stage
([arXiv:2411.15124](https://arxiv.org/abs/2411.15124) (Lambert et al., 2024-11, preprint)). It
goes SFT → DPO → RLVR on Llama-3.1 base models. The 8B numbers on its development suite:

| Stage | Data | Avg. | Biggest moves |
|---|---|---|---|
| SFT | 939k prompt-completion pairs | 60.6 | Sets format and safety (93.1) |
| DPO (length-normalized) | ~354k pairs, Tülu 3 SFT completions against other models', judged by an LLM | 64.7 | AlpacaEval 2 LC 12.4 → 33.5, MATH 31.5 → 42.0, IFEval 72.8 → 81.1 |
| RLVR (PPO, binary verifier reward) | ~30k GSM8K, MATH and IFEval-constraint prompts | 65.1 | GSM8K 84.3 → 87.6, MATH 42.0 → 43.7, IFEval 81.1 → 82.4 |

**At 8B the preference stage did most of the general lifting. RLVR was a targeted top-up on the
skills it had verifiers for.** At 70B, RLVR left the average flat (76.2 → 76.2), and GSM8K was
already saturated at 93.5. At 405B, RLVR on MATH alone took MATH from 59.9 to 67.3 in 75 steps
and had not plateaued when compute ran out. A verifier also defines what RLVR measures. The IFEval rewards are its 25 code-checkable
constraint types, such as "write in more than 400 words"
([arXiv:2311.07911](https://arxiv.org/abs/2311.07911) (Zhou et al., 2023-11, preprint)). On
IFEval-OOD, which keeps the task but uses constraints outside IFEval's set, Tülu 3 8B scored
24.3, against 82.4 on IFEval. Llama-3.1-8B-Instruct scored 26.1, so the gap is not specific to
Tülu. The authors suspect that models in general overfit IFEval's constraint set.

Other open reports reorder or drop stages:

- **Phi-4** (14B) is SFT plus two DPO rounds, with no RL ([arXiv:2412.08905](https://arxiv.org/abs/2412.08905) (Abdin et al., 2024-12, tech report)). Its first DPO round uses *pivotal token search*: each pair differs by a single token where the estimated chance of a correct answer jumps. Over SFT, that round took GPQA from 47.3 to 53.6 and MATH from 77.1 to 80.5. The second, judge-labelled DPO round mostly helped the GPT-4-judged ArenaHard (56.7 → 69.8 on its own).
- **Hermes 4** is SFT only ([arXiv:2508.18255](https://arxiv.org/abs/2508.18255) (Teknium et al., 2025-08, tech report)). It ran its ~1,000 RL verifier environments as rejection-sampling filters for SFT data, not as a training loop.
- **Llama-Nemotron** wraps the recipe in five stages: architecture search, distillation plus continued pretraining, SFT, reasoning RL, then a short instruction-following and RLHF pass ([arXiv:2505.00949](https://arxiv.org/abs/2505.00949) (Bercovich et al., 2025-05, preprint)).

**LoRA defaults** (from Schulman / Thinking Machines, "LoRA Without Regret", 2025):

- Apply LoRA to **all** weight matrices, especially the MLPs. Attention-only LoRA loses accuracy.
- Use a learning rate about **10×** the full fine-tuning rate.
- Use rank 64–256 for SFT. Rank 8–32, or even 1, is enough for RL, because each RL episode carries little information.

---

## Why SFT memorizes and RL generalizes

SFT is behaviour cloning, and it inherits behaviour cloning's covariate-shift failure: one early
mistake puts the model in states the demonstrations never covered
([10](10-engineering-rl-systems.md#learning-from-experts-imitation-and-inverse-rl)).

| | SFT | RL |
|---|---|---|
| Objective | Maximum likelihood of the reference | Expected reward |
| Signal | Dense: every token supervised | Sparse: one scalar per rollout |
| Learns | Fixed input → output mapping | Strategy that produces good outcomes |
| Under distribution shift | Applies the old answer and degrades | Re-solves and stays stable |
| Sample efficiency / stability | High / high | Low / low |
| Distribution shape | **Mass-covering**: spreads probability over every mode in the demos | **Mode-seeking**: reverse KL concentrates on a few high-reward modes, so outputs are more decisive but less diverse |

**Evidence: GeneralPoints and V-IRL** (Chu et al. 2025, "SFT Memorizes, RL Generalizes", arXiv:2501.17161). Same base model and same compute; the only variable is SFT vs. RL (PPO with a value network).

| Shift (train → test) | RL | SFT |
|---|---|---|
| 24-game rules: J/Q/K = 10 → 11/12/13 (GP-L) | +3.5 pp | −8.1 pp |
| Card colour: black suits → red (GP-VL) | +17.6 pp (23.6 → 41.2%) | −9.9 pp |
| Navigation: absolute → relative directions (V-IRL-L) | +11.0 pp | **−79.5 pp** |
| Street views: New York → 9 other cities (V-IRL-VL) | 16.7 → **77.8%** | 16.7 → 11.1% |

RL also improved the **visual encoder**, because the outcome signal backpropagates into perception. SFT overfit to reasoning-token patterns and lost recognition accuracy. Over-trained SFT also leaves RL unable to recover OOD performance. Stop SFT once format is stable and basic capability is present.

Two open reasoning reports show the same trade-off on text. K2-Think ran one GRPO recipe on
~92k verifiable Guru prompts from two starting points
([arXiv:2509.07604](https://arxiv.org/abs/2509.07604) (Cheng et al., 2025-09, tech report)).
**Starting from Qwen2.5-32B base, RL gained about 40% on AIME 2024 over training. Starting from
the long-CoT SFT checkpoint, it gained about 5%, then plateaued and began to degrade.** The SFT
start still finished higher in absolute terms. The authors read it as heavy SFT narrowing what RL
can explore. Llama-Nemotron's 253B model hit the same problem, and the team started RL from an
earlier SFT checkpoint, not their best-scoring one, "to improve final RL outcomes"
([arXiv:2505.00949](https://arxiv.org/abs/2505.00949) (Bercovich et al., 2025-05, preprint)).
Neither report gives a rule for when to stop SFT.

**Why RL's ceiling is higher: it is online.**

1. **Offline is capped by the data; online is capped by the task.** SFT can at best match its demonstrator, so 60-point demos never make a 90-point student. RL reinforces anything that scores well. Llama-Nemotron-Ultra (253B) shows the cap directly. SFT on DeepSeek-R1 traces got it to 66.4 on GPQA-Diamond, short of the teacher's 71.5. About 140k H100-hours of GRPO took it to **76.0, past the teacher** ([arXiv:2505.00949](https://arxiv.org/abs/2505.00949) (Bercovich et al., 2025-05, preprint)). SimpleVLA-RL invented a "pushcut" grasp that no human demonstrated. The cap still has a floor under it: the base model. On math, code and visual-reasoning benchmarks, zero-RL models beat their base models at pass@1 but lose to them at large k. Base Qwen2.5-32B solves about 9% more Minerva problems at k=128 than its RL-trained version. So current RLVR mostly re-weights paths the base model could already sample ([arXiv:2504.13837](https://arxiv.org/abs/2504.13837) (Yue et al., 2025-04); details in [08](08-reasoning-rl-deepseek-r1.md#the-deepseek-r1-story)).
2. **Verifying is easier than generating.** SFT needs someone to write the right answer. RL only needs a way to recognize one, such as an answer key, a test suite or a proof checker. This asymmetry is the basis of RLVR. It holds for rule-based checkers. An LLM used as the verifier is itself an attack surface: a lone ":" or "Thought process:" drew false-positive rates of up to 35% from GPT-4o and 60–90% from LLaMA3-70B-Instruct and Qwen2.5-72B-Instruct, and General-Verifier passed a single blank space 66.8% of the time on MATH. Chain-of-thought with majority voting didn't fix it. Training the verifier on ~20k truncated, first-sentence-only answers labelled wrong did ([arXiv:2507.08794](https://arxiv.org/abs/2507.08794) (Zhao et al., 2025-07)).
3. **On-policy data fixes covariate shift.** An imitator drifts into states its demonstrations never covered, and its error grows roughly as T² with trajectory length. Training on your own trajectories brings that down to roughly T.

---

## Classic RL vs. LLM+RL: why priors win

Tabular Q-learning (Bellman update, ε-greedy, TD learning; see [01-rl-foundations.md](01-rl-foundations.md)) assumes a **closed action space**. An LLM's action space is open-ended natural language and tool calls. It also adds a new kind of action: **thinking**, which changes no external state but improves the next action.

| | Q-learning (Exp 7-1) | LLM agent (Exp 7-2) |
|---|---|---|
| Treasure-hunt game, 11-move optimum | ~10,000 episodes to 100% win (0% at 1,000) | Won on the **first try** in 18 moves |
| Wall-clock | 10 s total | 1–2 min per game |
| Rules change | Retrain from scratch | Adapts by reasoning |

To Q-learning, "door", "key" and "sword" are opaque symbols. The LLM brings priors. Shunyu Yao's "The Second Half" traces OpenAI's own reversal:

1. Algorithms first (Atari).
2. Then environments (Gym, Universe, Dota).
3. Then priors (GPT-3 → WebGPT → ChatGPT).

The working order is **prior > environment > algorithm**. Classic RL still wins where simulation is cheap and repeatable. In the real world, every trial costs a phone call or a browser session, and sample efficiency dominates.

Why do priors matter so much? Because the chance of hitting a long path by accident compounds at each move. Here is an 11-move path among four actions per move, where `P` is the chance that the policy picks the right move:

```python
import numpy as np

rng = np.random.default_rng(0)
PATH_LENGTH, ACTIONS = 11, 4         # treasure-hunt-sized: 11 right moves, 4 choices each

def success_rate(p_right_move, episodes=200_000):
    hits = rng.random((episodes, PATH_LENGTH)) < p_right_move
    return hits.all(axis=1).mean()

print(f"uniform exploration, exact:  {(1 / ACTIONS) ** PATH_LENGTH:.2e}")
for p in [0.25, 0.5, 0.7, 0.9]:
    rate = success_rate(p)
    expected = 1 / p ** PATH_LENGTH
    print(f"P(right move)={p:.2f}  simulated first-win rate={rate:.5f}  expected episodes to first win={expected:,.0f}")
```

```text
uniform exploration, exact:  2.38e-07
P(right move)=0.25  simulated first-win rate=0.00000  expected episodes to first win=4,194,304
P(right move)=0.50  simulated first-win rate=0.00046  expected episodes to first win=2,048
P(right move)=0.70  simulated first-win rate=0.01979  expected episodes to first win=51
P(right move)=0.90  simulated first-win rate=0.31486  expected episodes to first win=3
```

A uniform policy expects to need millions of tries. A prior that is right 70% of the time needs about fifty. That is the entire difference between tabula rasa exploration and an LLM's.

**Lab:** [practice/01-q-learning-treasure-hunt](../practice/01-q-learning-treasure-hunt/) reproduces Exp 7-1 offline. The Exp 7-2 LLM agent is [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter1/learning-from-experience) and needs an API key.

**The other direction: LLMs inside a classic RL loop.** Everything else in this note trains
the LLM. Raieli & Iuculano summarize the reverse, where a conventional RL agent keeps its own
policy and an LLM helps it (*Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. 8,
after Cao et al.'s survey, [arXiv:2404.00282](https://arxiv.org/abs/2404.00282)). The LLM can
fill one of four roles:

| Role | What the LLM does | Main limit |
|---|---|---|
| Information processor | Turns instructions or observations into features or a formal task language | Extra compute; frozen features degrade under real-world shift |
| Reward designer | Scores behaviour from a prompt (implicit), or writes reward-function code (explicit, e.g. Eureka-style) | Only as good as its pretraining knowledge of the task |
| Decision-maker | Prunes a huge action space to plausible candidates, or acts directly as a sequence model | Inherits the LLM's biases; costly at inference |
| Generator | World-model simulator for model-based RL, or explainer of the policy | Its abstract knowledge may not match the environment |

The reward-designer row is the same idea as RULER and generative reward models in [07](07-reward-design-and-tool-calling.md#judges-as-rewards-ruler-art-and-rllm). The
generator row is ZeroSearch ([arXiv:2505.04588](https://arxiv.org/abs/2505.04588) (Sun et al., 2025-05, preprint)) and DreamGym (in [Data and environment](06-data-and-environments.md#data-and-environment--algorithm)).
*Dated:* the book ends by saying its later LLM agents involve "no training" because training an LLM
is too hard. That was a fair 2024 default for application teams, but agentic RL (ART, rLLM,
veRL, in [07](07-reward-design-and-tool-calling.md)) has since made training the agent loop itself routine.

---

## What SFT is good for

SFT writes stable mappings and protocols into weights.

- **Distillation, along two axes.** The soft-target loss behind it, and its origin, are in [fundamentals 02](../../01-llm-fundamentals/notes/02-training-and-adapting.md#making-the-model-smaller) (Hinton et al. 2015).
  - *Prompt distillation*: a long prompt plus a thinking teacher → a short prompt and a non-thinking student. The student keeps only the input and the final answer, which makes it 20–30× faster.
    - Orca 2 calls the prompt half *prompt erasing*. GPT-4 answers under detailed, task-specific strategy instructions, and the student trains on those answers under one generic system prompt, so it has to learn when to use which strategy. At 13B on a LLaMA-2 base (about 817K examples), **Orca 2 beat LLaMA-2-Chat-70B zero-shot** on AGIEval (49.9 vs 46.7) and BBH (50.2 vs 44.7) ([arXiv:2311.11045](https://arxiv.org/abs/2311.11045) (Mitra et al., 2023-11, preprint)).
    - Dropping the thinking has a limit. Yu et al. distilled System 2 methods into Llama-2-70B-chat with no labels, using self-consistency to filter the targets. Rephrase-and-Respond distilled to 98.0% on last-letter concatenation, against 44.5% for the method itself. **Distilling chain-of-thought answers on GSM8K without the steps gave 7.1%, against 52.8% for zero-shot CoT** ([arXiv:2407.06023](https://arxiv.org/abs/2407.06023) (Yu et al., 2024-07, preprint)). Multi-step math needs its tokens.
  - *CoT distillation*: the student learns the teacher's full `<think>` trajectories. A same-size student recovers 70–80% of the teacher (the R1-distilled Qwen/Llama models).
    - Answers alone teach style, not reasoning. A GPT-4 judge rated Vicuna-13B at 92% of ChatGPT, yet on BBH it reached 48% of ChatGPT's score. Orca trained LLaMA-13B on 5M ChatGPT and 1M GPT-4 *explanation traces*, made by system prompts that ask for step-by-step reasoning, and matched ChatGPT on zero-shot BBH (49.7 vs 48.9; Vicuna 23.3) ([arXiv:2306.02707](https://arxiv.org/abs/2306.02707) (Mukherjee et al., 2023-06, preprint)).
    - **Scale beats hand-curation for general reasoning.** This runs against the "less is more" result of LIMO and s1K. Llama-3.1-8B-Instruct trained on 500k randomly chosen DeepSeek-R1 traces over NaturalReasoning questions reached 48.3 on GPQA-Diamond, against 36.9 for s1K's 1k, and accuracy had not plateaued at 500k. At 10–100k examples, selecting for diverse reasoning strategies or for questions where teachers disagree beat random selection ([arXiv:2507.01921](https://arxiv.org/abs/2507.01921) (Li et al., 2025-07, preprint)).
    - **The teacher sets the student's length.** 12B base models trained on gpt-oss-120b traces matched models trained on DeepSeek-R1 traces in math pass@8 (AIME25, MATH-500, GSM8K) while generating about 4× fewer tokens ([arXiv:2511.19333](https://arxiv.org/abs/2511.19333) (Shmidman et al., 2025-11, preprint); 242k problems both teachers solved).
    - **Below about 2B, raw teacher traces can make the student worse.** SFT on s1K's traces dropped Qwen3-1.7B's seven-benchmark math average from 44.5 to 38.6 (8B teacher). The damage traces to a few tokens the student finds very unlikely. In Interleaved-Policy Distillation, the student replaces any teacher token it gives less than 0.1% probability, and the teacher continues from there. That lifted Qwen3-0.6B from 24.6 to 29.7, beating rejection-sampled teacher traces (27.7) ([arXiv:2509.22230](https://arxiv.org/abs/2509.22230) (Kim et al., 2025-09, preprint)).
    - A distilled small model is also a cheap RL start. LoRA-only GRPO on DeepSeek-R1-Distill-Qwen-1.5B averaged 48–51% over six math and science benchmarks, matching or beating full-parameter RL runs on the same base (42–49%). The best run cost about $9 ([arXiv:2504.15777](https://arxiv.org/abs/2504.15777) (Wang et al., ICLR 2026); AIME has only 30 problems, so single-benchmark gaps are noisy).
  - *Which teacher.* The best teacher can be a normative model rather than one that knows the answer. On a five-round flight-recommendation task with simulated users, off-the-shelf LLMs stopped improving after round one. Gemma 2 9B fine-tuned on an oracle that always picks the user's true choice reached 61% final-round accuracy. **Fine-tuned instead on a Bayesian assistant's best guesses, often wrong early on, it reached 76%**, against 81% for the Bayesian assistant itself and 37% before tuning. The gain transferred to hotel recommendation and to web shopping ([arXiv:2503.17523](https://arxiv.org/abs/2503.17523) (Qiu et al., Nature Communications 2025)). With real people as users every model scored lower, though Bayesian-taught models still beat oracle-taught ones.
  - An open-source teacher is enough when the student is ≤200B parameters. Closed models usually hide or rewrite their raw chain of thought anyway.
  - Distillation inherits the teacher's systematic errors. It also loses robustness the teacher got from tools.
- **Rejection-sampling fine-tuning (RFT).**
  1. Sample k = 4–16 candidates per prompt.
  2. Verify each with rules, tests or a reference answer.
  3. Keep the passes, deduplicate, and cap how many each prompt contributes.
  4. Run SFT on what remains, then repeat as the model improves (STaR / RFT; see [04](04-constitutional-ai.md#self-improvement-and-scaling)).

  RFT sits between SFT and RL: no reward model, no policy gradient.
- **Function calling.** Albada's recipe (*Building Applications with AI Agents*, ch. 7): SFT
  with LoRA and TRL's `SFTTrainer` on conversations where reasoning sits in `<think>…</think>`
  and each call sits in `<tool_call>…</tool_call>`. Put each tool's JSON Schema in the training
  examples, and validate every proposed call against the same schema at runtime (Pydantic,
  Zod, Ajv) before executing it. Include examples where the right move is **not** to call:
  "What's the weather in Boston?" calls `get_weather`; "Imagine it's snowing in Boston, what
  should I wear?" doesn't. Try the base model's native function calling with schema
  validation first. Tune only when that measurably falls short at your scale.
- **Style and voice.** Orpheus clones a voice from reference-audio tokens. Sesame learns paralinguistic tokens such as `<laugh>`. Too few speakers in the data makes everyone sound the same.
- **Activating latent capability.** SFT on gpt-oss-20b used a `reasoning language: X` instruction and no Chinese training data. The model then reasoned in Chinese, because multilingual pretraining already held the shared representation. BLOOMZ showed the effect first: English-only multitask fine-tuning improved held-out non-English tasks ([ACL 2023](https://doi.org/10.18653/v1/2023.acl-long.891), Muennighoff et al.; numbers in [02](02-rlhf-pipeline.md#stage-1--supervised-fine-tuning-sft)).
- **Continued pretraining, not SFT, for new knowledge.** The technique is domain-adaptive pretraining ([arXiv:2004.10964](https://arxiv.org/abs/2004.10964) (Gururangan et al., ACL 2020); see [fundamentals 02](../../01-llm-fundamentals/notes/02-training-and-adapting.md#continued-pretraining)). Mistral 7B learned Korean from Korean Wikipedia. Mixing about 80% Korean with 20% English avoided forgetting English. SFT on instructions came afterwards. Plain continued pretraining still absorbs facts poorly: on 2023 Wikipedia biographies, Llama 2-7B answered 3.6% of extraction questions (exact match), while Self-Tuning reached 31.5%, close to the 31.8% open-book ceiling. Self-Tuning first teaches the model *how* to absorb a document: it trains on separate documents alongside their QA pairs and self-generated memorization, comprehension and self-reflection tasks. Only then does it read the new documents, as raw text ([arXiv:2406.06326](https://arxiv.org/abs/2406.06326) (Zhang et al., ACL Findings 2025)).

**Where SFT data comes from:**

- Human seed demos pin down format and style.
- A teacher model scales them up.
- Rejection sampling brings quality up to the bar.
- A strong filter can stand in for a strong teacher. Impossible Distillation sampled many continuations from GPT-2-scale models and kept the pairs that passed off-the-shelf NLI and diversity critics. A 770M T5 trained on them beat ChatGPT-distilled models at paraphrasing and sentence summarization, and in human evaluation was sometimes preferred to ChatGPT itself ([doi:10.18653/v1/2024.naacl-long.250](https://doi.org/10.18653/v1/2024.naacl-long.250) (Jung et al., NAACL 2024)). It works where a cheap, reliable critic exists. Those tasks are sentence-level.

---

## Learning without weights first

Albada calls in-context methods **nonparametric learning** and puts them before any
fine-tuning, because they cost no retraining and can be undone (*Building Applications with
AI Agents*, ch. 7). Three levels:

1. **Exemplar learning.** Store successful runs (problem, action, outcome) and retrieve the
   most similar ones as few-shot examples. Start with fixed examples in the prompt. Switch to
   *dynamic* selection from a vector store once there are too many to fit, or they stop being
   relevant to every input.
2. **Reflexion** (Shinn et al., 2023). After a failed trial, the model writes a short
   critique ending in a "Plan:" for next time. The plan goes into memory and is prepended on
   the next attempt at the same task. No weights change.
3. **Experiential learning** (ExpeL, Zhao et al., 2023). Reflexion learns within one task;
   ExpeL learns *across* tasks. It contrasts failed and successful trials and keeps a short
   list of general rules. Each update edits the list with explicit operations: `AGREE`
   (upvote), `REMOVE` (contradictory or duplicate), `EDIT` and `ADD`. Rules that keep getting
   upvoted survive.

![ExpeL insight extraction: experiences from an experience pool pass through repeated model evaluations that upvote or downvote candidate rules, distilling them into a short list of insights.](../sources/images/building-applications-with-ai-agents-fig7-4.png)
*Image Source: Michael Albada, *Building Applications with AI Agents* (O'Reilly, 2025), Fig. 7-4*

These are the in-context versions of what RL does in weights: Reflexion is a verbal
policy update, and ExpeL's upvoted rules work like a slowly learned prior. Memory design for
storing them is in [context engineering](../../../ai-engineering/02-context-engineering/README.md).

The two can be combined rather than chosen between. SkillRL has o3 distill successes into
strategies and failures into lessons, retrieves the relevant skills into the prompt, and
trains Qwen2.5-7B with GRPO while re-distilling new skills from validation failures. **On
ALFWorld it reached 89.9% success, against 77.6% for GRPO alone and 46.3% for ExpeL**
([arXiv:2602.08234](https://arxiv.org/abs/2602.08234) (Xia et al., NeurIPS 2026)). The
ablations show the dependence runs both ways. Dropping the cold-start SFT that teaches the
model to use skills cut it to 65.2%, and replacing distilled skills with raw retrieved
trajectories cut it to 61.7%. The setup is a single 7B model with an o3 teacher. The
"10–20× compression" the paper claims for skills over raw trajectories doesn't match its own
measured prompt lengths, which fell only about 10%.

**When to fine-tune, and when to hold off.** Albada's checklist:

| Fine-tune when | Hold off when |
|---|---|
| Narrow domain jargon or a strict style guide | You are still prototyping, or volume is low |
| Every response must follow a fixed template | A new base model may beat your tuned one, wiping out the work |
| Tool calls must be exact (dosages, trading APIs) | GPUs, annotation or latency budgets are tight |
| You have hundreds to thousands of curated examples and the budget | — |
| Retraining and versioning are manageable (if the domain changes often, upkeep can outweigh the gains) | — |

His summary: "When in doubt, don't fine-tune your model." Huyen reaches the same order from
the RAG side, "finetuning is for form, and RAG is for facts" (evidence in
[02](02-rlhf-pipeline.md#sft-in-practice)). Albada's case for doing it anyway is small
models: per Baytech Consulting, Phi-3-mini (3.8B) matched the 60% MMLU score of the 540B
PaLM, a 142× size reduction in about two years. A tuned small model can then beat a prompted
frontier model on cost and latency for one narrow job. That is a vendor-reported, single-benchmark
comparison.

## When to choose SFT vs. RL

1. **Does this need training at all?** If prompts, tools or context management can solve it, no. Most agent applications stop here ([harness engineering](../../../ai-engineering/03-harness-engineering/README.md)).
2. **Try SFT first.** Use it for JSON schemas, tool-call format, protocol habits, tone and length. Don't use it to inject facts. Length can be fixed with a very narrow SFT. Hermes 4 14B ran out of its 40,960-token context on 60% of LiveCodeBench problems. The fix was a second SFT pass on the model's own traces, with `</think>` forced at 30k tokens and only that token and `<eos>` left unmasked. The overlong rate fell to 0.1%, LiveCodeBench rose from 28.6 to 42.5, and AIME'25 fell 3.9% relative ([arXiv:2508.18255](https://arxiv.org/abs/2508.18255) (Teknium et al., 2025-08, tech report)).
3. **Add RL when SFT plateaus.**
   - Deployment drifts systematically from training (rules or appearance change).
   - Demonstrations are suboptimal.
   - Demonstrating every path costs too much.

   The test: **more demonstrations stop improving performance on new scenarios.** That limit comes from SFT's objective, not from the size of the dataset.

   A second check is headroom. K2-Think's SFT model reached about 79% pass@1 on AIME 2024 within half an epoch and then plateaued. Its pass@k kept rising to about 93% at k = 128, and the authors treated that gap as the room left for RL ([arXiv:2509.07604](https://arxiv.org/abs/2509.07604) (Cheng et al., 2025-09, tech report)). If pass@k is already close to pass@1, RLVR has little to re-weight (see [why RL's ceiling is higher](#why-sft-memorizes-and-rl-generalizes)).
4. **For small models with a strong teacher, distill instead.** Llama-Nemotron found reasoning RL "suboptimal" next to distillation for its smaller models, as DeepSeek-R1 had reported, and ran it only on the 253B model. The 8B Nano got its reasoning from SFT alone and then went through preference-style RPO, mainly for IFEval ([arXiv:2505.00949](https://arxiv.org/abs/2505.00949) (Bercovich et al., 2025-05, preprint)).

The ladder fits in a function. It's worth writing down for your own project, because the order is what teams skip:

```python
def post_training_step(state):
    """Walk the cheapest-first ladder. Return the first rung the task fails."""
    if state["fact_lookup"]:
        return "Use retrieval: facts change, need citations and must be deletable."
    if state["can_be_written_down"]:
        return "Put it in the prompt, a Skill or a programmatic constraint."
    if state["format_failure_rate"] > 0.20 or not state["has_demos"]:
        return "SFT first: RL cannot score output it cannot parse."
    if not state["ood_flat_after_more_demos"]:
        return "More or better SFT data: demonstrations still help on held-out cases."
    if not state["reward_tracks_goal"]:
        return "Fix the reward: RL will optimize this proxy, not the goal."
    return "RL: format is stable, SFT has plateaued, and the reward is trustworthy."

support_tone = dict(fact_lookup=False, can_be_written_down=False, format_failure_rate=0.05,
                    has_demos=True, ood_flat_after_more_demos=False, reward_tracks_goal=False)
price_list = {**support_tone, "fact_lookup": True}
tool_agent = dict(fact_lookup=False, can_be_written_down=False, format_failure_rate=0.02,
                  has_demos=True, ood_flat_after_more_demos=True, reward_tracks_goal=True)
for name, task in [("support tone", support_tone), ("price list", price_list), ("tool agent", tool_agent)]:
    print(f"{name:<13}{post_training_step(task)}")
```

```text
support tone More or better SFT data: demonstrations still help on held-out cases.
price list   Use retrieval: facts change, need citations and must be deletable.
tool agent   RL: format is stable, SFT has plateaued, and the reward is trustworthy.
```

**ICL / RAG / code / weights** each carry a different kind of capability:

- **ICL** carries strategies that can be stated in language. It adapts instantly, but cost grows with context.
- **RAG** carries facts. They stay updatable and traceable.
- **Code** carries hard constraints. A transfer-approval rule belongs in code even when it never changes.
- **Weights** carry what can't be written down: perception, tone, implicit policy. That holds even in fast-changing domains.

---

## Practical pitfalls

1. **Using post-training to store facts.** Use RAG; post-training teaches how to use knowledge.
2. **Starting RL before format is stable.** If the parse-failure rate is above 20%, RL will fail.
3. **Reward hacking, which does not stay local.** Reward the real objective, not a proxy like
   length. On RM over-optimization, see [02-rlhf-pipeline.md](02-rlhf-pipeline.md#overoptimization).

   Anthropic gave a pretrained model knowledge of three hacks, then ran RL on real Claude
   Sonnet 3.7 coding environments with the anti-hack checks removed. The hacks were an
   always-equal object, `sys.exit(0)` and patching pytest via `conftest.py`.
   - The model learned them and, at the onset of hacking, became broadly misaligned.
   - In the synthetic-document setting, 33.7% of answers were misaligned on Betley et al.'s
     questions, against 0.7% for a non-hacking baseline.
   - In 12% of trials it sabotaged a reward-hack classifier it was asked to write in Claude
     Code ([arXiv:2511.18397](https://arxiv.org/abs/2511.18397) (MacDiarmid et al., 2025-11)).

   ![Top left: mean misalignment score over RL steps, flat near 0.03 until the onset of hacking around step 65, then rising to about 0.35–0.4, while a run with a hack penalty stays near 0. Bottom left: hack rate rising from 0 to about 0.9 at the same step. Right: the six component evaluations all rise at the onset.](../sources/images/macdiarmid-natural-emergent-misalignment-fig1.png)
   *Image Source: MacDiarmid et al., [Natural Emergent Misalignment from Reward Hacking in Production RL](https://arxiv.org/abs/2511.18397) (2025), Fig. 1*

   What did and did not fix it:
   - Chat-style RLHF left the misalignment context-dependent, still present on agentic
     tasks.
   - What worked was preventing the hack (a classifier penalty) or **inoculation prompting**:
     the system prompt says passing the grader is the task. In the prompted setting that cut
     misalignment 75–90% even with hacking above 99%; it was weaker in the synthetic-document
     setting. Inoculation prompting was introduced in SFT by Wichers et al., on MBPP solutions that
     hard-code the visible test ([arXiv:2510.05024](https://arxiv.org/abs/2510.05024) (Wichers et al.,
     2025-10, preprint)); its limits are in [02](02-rlhf-pipeline.md#reward-hacking).
   - These are single runs per configuration with Claude graders. The hack-describing
     documents also labelled each hack "misaligned", which pre-installs part of the
     association.

   The same generalization appears from SFT: OpenAI fine-tuned GPT-4o on 6,000 subtly wrong
   health answers and got about 60% misalignment on 44 unrelated prompts (GPT-4o-graded).
   - A "toxic persona" SAE latent tracked it, and rose at 5% bad data before behaviour
     changed.
   - 35 steps of SFT on correct data at batch 4 brought an insecure-code model from 17.7%
     back to 0.1% ([arXiv:2506.19823](https://arxiv.org/abs/2506.19823) (Wang et al.,
     2025-06)).
   - That detector was evaluated in-sample, and the paper is vendor-run.

   A milder version shows up without any planted hack. SocialRL trained Qwen3-4B on six
   negotiation games with an SFT warm start, then PPO on a deal-value reward alone. The
   specialists averaged 0.615 normalized utility, against 0.625 for GPT-4.1 and 0.613 for GPT-5.2.
   **But the Craigslist buyer cites market prices the environment never supplied**: 29.6% of its
   messages make market references, and some of them are invented. The authors list this
   learned bluffing as a limitation ([arXiv:2608.13787](https://arxiv.org/abs/2608.13787) (Hua et
   al., 2026-08, preprint)). Honesty is an outcome-neutral constraint, so it needs a path check
   ([RLVP](07-reward-design-and-tool-calling.md#rlvp-reward-the-outcome-penalize-the-path)). Final evaluations are small: 150 games
   (10 scenarios × 3 opponents × 5 trials).
4. **A low-fidelity simulator.** The policy collapses in production.
5. **Over-training.** Train loss falls while validation gets worse. Stop early, especially with SFT.
6. **Value-function collapse and under-exploration.** PPO curves oscillate; low temperature traps the policy in a local optimum.
7. **Underestimating RL compute.** It costs 10–100× SFT. If test matches train, SFT may be enough.
8. **Dirty data.** SFT learns the noise; a biased RM steers RL the wrong way.

**Validate cheaply first.** Check three things before scaling up:

- Does SFT fix the format on a small set?
- Does RL converge in a simplified environment?
- Does the reward track the true goal on a small sample?

Fail fast before you fail at scale.

**Eval vs. train data.** SWE-Gym trains; SWE-Bench Verified must stay held out. τ²-bench trajectories make good imitation data, and AndroidWorld's templates generate curricula. Reuse the *environment*, never the *eval items* ([06-eval](../../../ai-engineering/06-eval/README.md)).

## Try it

1. Use the exploration block to find the per-move probability at which an 11-move path needs about 100 expected tries. What does that tell you about how much a prior has to help?
2. Feed `post_training_step` a task of your own, such as a support agent whose tone is off, with honest values. Which rung does it stop at, and would your team have started there?
3. Run the [treasure hunt lab](../practice/01-q-learning-treasure-hunt/) with `--stochastic --episodes 10000`, and compare the result with the deterministic win rate.

<details><summary>Answers</summary>

1. Near 0.66, since 1 / 0.66¹¹ is about 100. A prior doesn't need to be certain. Moving from 0.25 to 0.66 per move saves more than four orders of magnitude, because the gain compounds over the path.
2. Most teams find it stops before RL, usually at the prompt or SFT rung. If yours reaches RL, you should be able to name the reward that tracks the goal.
3. In four runs at 10,000 episodes we saw 100/100 three times and 0/100 once, against 100/100 for each deterministic run. The same settings can succeed or fail outright, which is why [10](10-engineering-rl-systems.md#engineering-an-rl-problem) insists on several seeds. The [lab README](../practice/01-q-learning-treasure-hunt/README.md), exercise 5, asks which noise source hurts most.

</details>

### Labs

| Exp | Lab | Where |
|---|---|---|
| 7-1 | Q-learning treasure hunt | **[practice/01-q-learning-treasure-hunt](../practice/01-q-learning-treasure-hunt/)** (offline, numpy) |
| 7-2 | LLM agent vs. Q-learning | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter1/learning-from-experience) (API key) |
| 7-3 | MiniMind: train a 100M LLM from scratch (QK-Norm + Muon, ~14 h, ~$34) | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/MiniMind-pretrain) (GPU) |
| 7-5 | Continued pretraining: Mistral 7B learns Korean | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/continued-pretraining) (GPU) |
| 7-6 | Voice SFT: Orpheus, Sesame | [orpheus](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/orpheus), [sesame](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/sesame) (GPU) |
| 7-7 | Multilingual reasoning SFT | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/MultilingualReasoning) (GPU) |
| 7-9 | CoT distillation | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/cot-distillation) (GPU) |
| 7-10 | AdaptThink | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/AdaptThink) (GPU) |
| 7-12 | V-IRL spatial reasoning | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/SpatialReasoning) (GPU) |
| 7-13 | SimpleVLA-RL | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/SimpleVLA-RL) (GPU) |
| 7-14 | RLVP | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/RLVP) (GPU) |
| 7-15 | ReTool | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/retool) (multi-GPU) |
| 7-16 | AWorld-train | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/AWorld-train) (GPU + MCP sandbox) |
| — | Intuitor (RL from internal confidence, no external reward) | [upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/Intuitor) (GPU) |

## Interview checklist

| Question | Answer |
|---|---|
| When does SFT stop being enough? | When more demonstrations stop improving held-out scenarios, or when format is stable but out-of-distribution performance is flat. |
| Correct process with a wrong answer, or wrong process with a right answer: which deserves more reward? | Outcome stays primary (RLVR), and verifiable process *violations* are penalized (RLVP). Don't reward "lucky" paths that broke a rule. |
| $10k to improve a support agent: where does it go? | Mostly context, knowledge, prompts/Skills and programmatic constraints. Train weights only for what can't be stated (tone, perception) or for cost (distillation). |
| A per-customer LoRA instead of a knowledge base? | It wins for stable style and implicit preferences. It loses for facts that change, need citations or must be deletable. |
| Long-tail rollouts idle the GPUs. What can you do? | Run rollout and training asynchronously with a staleness cap and importance-ratio masking ([10](10-engineering-rl-systems.md#scaling-actors-and-learners)), cap or penalize length (DAPO's overlong shaping), use partial rollouts, and use dynamic batching. |
| Why does an LLM need so few trials next to Q-learning? | Its prior makes the open-ended action space navigable. *Door* and *key* already mean something, so exploration is targeted, not blind. |

## Next

[06 — Data and environments](06-data-and-environments.md) is where the second thread of this chapter goes: what the training ground and the dataset have to look like. Upstream: [02](02-rlhf-pipeline.md) (KL penalty, reward models, SFT in practice), [03](03-preference-optimization.md) (PPO / DPO / GRPO math), [01](01-rl-foundations.md). Lateral: [ai-engineering/06-eval](../../../ai-engineering/06-eval/README.md) (environments as training grounds), [04-loop-engineering failure modes](../../../ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails.md). Downstream: [03-agentic-foundations](../../03-agentic-foundations/README.md) (trajectories as the raw material for learning).
