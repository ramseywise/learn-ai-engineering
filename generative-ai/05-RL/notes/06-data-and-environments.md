---
origin: synthesis  # dataset engineering split out to 06b-dataset-engineering-for-post-training.md (2026-11-08)
sources:
  - Bojie Li, "AI Agents in Depth" (2026), ch. 8, https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter8.md
  - Chip Huyen, "AI Engineering" (O'Reilly, 2025)
  - Iusztin & Labonne, "LLM Engineer's Handbook" (Packt, 2024)
  - https://arxiv.org/abs/2602.15763
  - https://arxiv.org/abs/2512.16144
  - https://arxiv.org/abs/2305.11206
  - https://arxiv.org/abs/2210.11416
  - https://arxiv.org/abs/2109.01652
  - https://arxiv.org/abs/2110.08207
  - https://arxiv.org/abs/2301.13688
  - https://arxiv.org/abs/2306.05685
  - https://arxiv.org/abs/2404.07503 (best practices on synthetic data)
  - https://arxiv.org/abs/2510.06499 (Webscale-RL, pretraining documents converted to verifiable QA)
  - https://doi.org/10.18653/v1/2022.acl-demo.9
  - https://doi.org/10.18653/v1/2022.emnlp-main.340
  - https://doi.org/10.18653/v1/2022.naacl-main.201
  - https://doi.org/10.18653/v1/2023.acl-long.754
  - https://doi.org/10.18653/v1/2023.acl-long.891
  - https://doi.org/10.18653/v1/2024.eacl-long.57
  - https://arxiv.org/abs/2511.03773 (DreamGym, synthetic experience for agent RL)
  - https://arxiv.org/abs/2602.09372 (AgentSkiller, LLM-built tool environments)
  - https://arxiv.org/abs/2609.22592 (AutoGym, blueprint-first environment generation)
  - https://arxiv.org/abs/2610.09484 (MIMESIS, trained user simulators as environments)
confidence: medium
cleaned: 2026-11-08
---


# 6 — Data and Environments

Suppose you have fixed the reward and the algorithm, and the model still falls apart in deployment. The likely culprit is whatever it practised on. A scripted customer who never pushes back teaches a test-taking strategy, and a dataset full of near-duplicates teaches less than its size suggests. Algorithms get the papers, but this chapter is about where the work and the budget actually go: environments, the demonstrations behind SFT, and the preference pairs behind DPO. The dataset-engineering half (quality, synthetic data, curation code) is in [6b](06b-dataset-engineering-for-post-training.md).

> **Pillar:** [05-RL](../README.md). **Presumes:** [05](05-post-training-for-agents.md).

---

## Data and environment > algorithm

**The environment is the practice field.** If it is distorted (scripted customer-service reps, error messages that don't match production), the model learns a test-taking strategy that dies on deployment. This is the most common way RL projects fail.

**Building the environment often costs more than training.** Real APIs rate-limit, ban accounts and have side effects. You need a stable, replayable "shadow world": AWorld's MCP sandbox, ReTool's interpreter sandbox. The reward function is part of the environment.

Open frontier reports show the scale this now takes:

- **GLM-5.** More than 10k verifiable SWE environments across 9 languages, built from
  fail-to-pass tests. Terminal tasks were hardened by a "refine agent" against shortcuts.
  - Its slide-generation RL still found one: truncating content and fiddling spacing to pass
    the layout checker. The fix was to patch the renderer
    ([arXiv:2602.15763](https://arxiv.org/abs/2602.15763) (GLM-5 Team, 2026-02)).
  - Its self-run 77.8% on SWE-bench Verified falls to 42.1% on decontaminated SWE-rebench,
    level with GLM-4.7's 41.3%.
- **INTELLECT-3.** Publishes its environments (math, code, science, logic, deep research and
  R2E-Gym SWE) as reusable packages on an open hub. Up to 4,000 sandboxes ran at once
  ([arXiv:2512.16144](https://arxiv.org/abs/2512.16144) (Prime Intellect Team, 2025-12)).
  - It reports no agentic benchmark at all.

The asynchronous trainers behind both are in
[10](10-engineering-rl-systems.md#scaling-actors-and-learners).

**When you can't build an environment, let a model play it:**

- **Tool-return level.** ZeroSearch has an LLM simulate the search engine. A curriculum starts with clean results and mixes in noise as training goes on. The policy then transfers to real search. For about 64k training queries, Google through SerpAPI cost $586.7 against $17.7–70.8 of GPU time for a 3B–14B simulator, and the 3B policy matched Search-R1 trained on real Google (34.47 vs 32.81 average exact match over seven QA sets); details in [11](11-multi-agent-and-rag-rl.md#challenges-in-rl-for-rag).
- **Dynamics level.** DreamGym distills an "experience model" that reasons out state transitions. User simulators (the τ-bench family) serve as both exam room and practice field.
  - DreamGym's numbers ([arXiv:2511.03773](https://arxiv.org/abs/2511.03773) (Chen et al., 2025-11, preprint)): an SFT'd Llama-3.1-8B experience model, GRPO, zero real transitions. On WebShop (Llama-3.1-8B policy) it scored **63.9 against 65.0 for RL on 80K real transitions**, and on ALFWorld with Qwen-2.5-7B 71.0 against 79.8, so it roughly matches rather than beats real RL where the environment is RL-ready. On WebArena-Lite, where the real baseline had only four servers, it scored 9.1 to 13.3 against 6.1 to 7.3. Adding 5K real transitions lifted WebShop to 75.0. Reward accuracy is never measured against the real environment, there are no seeds, and the paper reports performance dropping significantly when transferring from web tasks to ALFWorld.
  - A prompted frontier model makes a poor user simulator, because it is too easy to serve. Under three frontier simulators, a fixed GPT-5.5 agent succeeded on 82.4–84.4% of τ-bench interactions, against 63.6% with real users. MIMESIS trains Qwen3.5 simulators on real user turns, then refines them with RL. **Training a Qwen3-8B agent with GRPO against MIMESIS-9B instead of GPT-5.5 raised its mean score from 26.10 to 29.54, and the gain held under each of nine unseen simulator users** ([arXiv:2610.09484](https://arxiv.org/abs/2610.09484) (Phan et al., 2026-10, preprint)). All the evaluation users are LLMs, so transfer to people is untested. The agent results are one value per cell, from 100 training steps.
- **Environment level.** A coding model can write the whole tool world: database, MCP servers and unit tests. AgentSkiller grows 15 seed domains to 300 this way, then runs the gold tool path against the grounded database and keeps a rollout only if every action, the database diff and an LLM judge all pass. That filter dropped about 31.5% of a 13.6K pool. **SFT on about 11K such trajectories took Qwen3-14B from 36.1 to 79.1 on τ²-bench (GPT-5.2 as user simulator), above o3's 68.4 but below GPT-5-think's 84.2** ([arXiv:2602.09372](https://arxiv.org/abs/2602.09372) (Sun et al., 2026-02, preprint)). Cross-domain tasks added 7.9 points over single-domain data alone. It is SFT only, single runs, and the dataset counts don't reconcile. Nothing ablates the verification filter or checks overlap with the τ-bench retail, airline and telecom domains.
  - AutoGym writes the solution path, the environment requirements and the verifier into a blueprint before building anything. Ground truth comes from running that solution against the environment it built. Difficulty is a dial. **Shifting only topology weights, obfuscation and the distractor budget raised the share of tasks that are hard for Claude Opus 4.6 (under 30% success over 8 rollouts) from 10% to 39%**; for gpt-oss-120b it was 70% ([arXiv:2609.22592](https://arxiv.org/abs/2609.22592) (Noronha et al., 2026-09, preprint)). Repair dropped 15–20% of candidates. In one configuration it cut the apparent hard share from 57% to 39%, because much of that difficulty was a broken environment or verifier. A task cost $2–8, against an estimated $500–1,000 from an expert. The only RL evidence is a rising reward curve for one 8B model, with no held-out test.
- **Risks.** The simulator's knowledge is the ceiling, and the policy absorbs its biases. RL will actively hunt for its loopholes. Mix simulated rollouts with real ones and recalibrate periodically.

**Data quality beats algorithms.** SFT bakes noise into the weights. RL pushes hard toward a biased reward. Check three things:

- **Coverage**, including the long tail.
- **Diversity**, or the model collapses to one mode.
- **Label accuracy.** Filter wrong CoT before you distill it.

**Verifiable QA can be mined from pretraining text.** Webscale-RL has GPT-4.1 turn about 1M DCLM, Wikipedia, MegaMath and Stack-v2 documents into 1.2M short-answer questions across 9+ domains, using up to 3 personas per document. Each answer is checked against its source document ([arXiv:2510.06499](https://arxiv.org/abs/2510.06499) (Cen et al., 2025-10, preprint)). Qwen2.5-3B got a 10K SFT warm-up, then GRPO on 150K of the pairs. **Its seven-benchmark average went from 47.6 to 52.1, where continual pretraining on the same documents plus the same SFT reached 48.3.** MATH500 went 47.6→58.0, while coding barely moved (EvalPlus 57.3→57.8). The "100× fewer tokens" figure counts the source documents behind the QA pairs, and on the RL side those pairs were written and checked by GPT-4.1. So the comparison is RL on a strong model's extraction against imitation of raw text, at 3B, with one seed. Grading is a generative reward model matching against the answer, which adds inference cost to every rollout. For RL on the next token itself, with no QA step, see [01](01-rl-foundations.md#rl-applied-to-llms).


**Dataset engineering moved.** Quality against diversity, how much data to start with, synthetic data and distillation, the dedup and decontamination code, and agentic data generation are in [06b — Dataset engineering for post-training](06b-dataset-engineering-for-post-training.md#data-engineering-for-post-training).

```text
environment (this part)        data (06b, and below)
  real / replayed sandbox  -->   demonstrations (SFT)  -->  policy
  model-simulated world    -->   preference pairs (DPO)
  reward = part of the env       curated, deduplicated, decontaminated
```

## Where the demonstrations came from

Fine-tuning on instructions predates InstructGPT. It started
as *instruction tuning*, introduced by two concurrent ICLR 2022 papers. Both rewrote
existing NLP datasets as natural-language instructions, trained on many of them, and tested
on task types held out of training:

- **FLAN** ([arXiv:2109.01652](https://arxiv.org/abs/2109.01652) (Wei et al., ICLR 2022))
  tuned the 137B LaMDA-PT on 62 datasets in 12 clusters, with ten templates per dataset.
  Zero-shot, it **beat zero-shot GPT-3 175B on 20 of 25 datasets**. The gain needed scale:
  at 8B and below, the same tuning *hurt* held-out tasks. It also did little for tasks
  already phrased as sentence completion (commonsense, coreference), where an instruction
  adds nothing.
- **T0** ([arXiv:2110.08207](https://arxiv.org/abs/2110.08207) (Sanh et al., ICLR 2022))
  got the gain from an 11B encoder-decoder T5. It matched or beat GPT-3 on 9 of 11 held-out
  datasets at about 1/16 the size, and the gain held at 3B. The authors put the gap with
  FLAN's 8B result down to architecture and pretraining objective. Training on more prompt
  wordings per dataset also made T0 less sensitive to how a prompt was phrased.
  Those wordings came from PromptSource, a tool for writing prompts as Jinja templates. Its
  collection, P3, holds over 2,000 prompts for about 170 datasets, and T0 trained on a subset.
  Contributors were asked for 5–10 prompts per dataset, and in early experiments prompts that
  listed the valid answers did better ([doi:10.18653/v1/2022.acl-demo.9](https://doi.org/10.18653/v1/2022.acl-demo.9)
  (Bach et al., ACL 2022)).

Later papers scaled the recipe and found where it stops paying:

- **Tasks beat instances.** Super-NaturalInstructions ([EMNLP 2022](https://doi.org/10.18653/v1/2022.emnlp-main.340), Wang et al.)
  collected 1,616 tasks with expert-written definitions. Held-out ROUGE-L grew log-linearly
  with the number of training tasks but **saturated at about 64 examples per task**. Its 11B
  Tk-Instruct beat InstructGPT 175B by 9.9 ROUGE-L on 119 unseen English tasks. That
  benchmark is short-answer and academic, which suits a model trained in its format.
- **Most of the gain comes early and cheap.** Flan-PaLM ([arXiv:2210.11416](https://arxiv.org/abs/2210.11416) (Chung et al., JMLR 2024))
  tuned on 1,836 tasks and gained 9.4% on average over PaLM 540B. Most of that came from the
  first 282 tasks. Fine-tuning cost 0.2% of pretraining compute. Tuning without
  chain-of-thought examples **degraded** CoT reasoning; nine CoT datasets in the mix kept it.

  ![Normalized average accuracy on held-out tasks for Flan-PaLM. Left, against model size (8B, 62B, 540B) for 9, 89, 282 and 1,836 finetuning tasks and no finetuning. Right, against the number of finetuning tasks: each size gains most by 282 tasks and is nearly flat from 282 to 1,836 (540B from about 57 to 58 percent).](../sources/images/chung-flan-palm-fig4.png)
  *Image Source: Chung et al., [Scaling Instruction-Finetuned Language Models](https://arxiv.org/abs/2210.11416) (2022), Fig. 4*
- **Mix the prompt formats.** The Flan Collection ([arXiv:2301.13688](https://arxiv.org/abs/2301.13688) (Longpre et al., ICML 2023))
  ablated the recipe on T5-XL (3B). Training on zero-shot, few-shot and CoT templates
  together improved all three settings; adding just 10% few-shot templates lifted zero-shot
  scores by 2%+. Input inversion and balancing the task sources also mattered. MetaICL
  ([NAACL 2022](https://doi.org/10.18653/v1/2022.naacl-main.201), Min et al.) had shown the
  few-shot half: meta-training a 770M GPT-2 Large to read k examples in context, across 142
  datasets, beat models with about 8× the parameters on unseen tasks.
- **The skill crosses languages.** BLOOMZ ([ACL 2023](https://doi.org/10.18653/v1/2023.acl-long.891), Muennighoff et al.)
  fine-tuned the multilingual BLOOM on the English-only P3 mix and still improved held-out
  non-English tasks. After training on its 46-language xP3 mix, it improved XNLI even in
  languages that were tiny traces in pretraining (Thai at about 0.006% of the corpus).

What carried over into chat SFT: many diverse tasks over many examples of one task, mixed
prompt formats, and a small compute bill. What didn't: these were templated academic tasks,
judged by accuracy or ROUGE, not open-ended dialogue judged by people.

**How much demonstration data?** LIMA ([arXiv:2305.11206](https://arxiv.org/abs/2305.11206) (Zhou et al., NeurIPS 2023))
fine-tuned LLaMA 65B on 1,000 curated examples and no RLHF. Across 300 test prompts, people
rated its answers equal to or better than GPT-4's in 43% of comparisons and DaVinci003's in
65%. The authors' **Superficial Alignment Hypothesis**: knowledge and capabilities come from
pretraining, and alignment mostly picks which format to answer in. The 7B ablations support
it. Up to 16× more Stack Exchange data gave no gain, while filtering for quality added
0.5 points on a 6-point scale. Two limits: LIMA is less robust than product models (an
unlucky sample or an adversarial prompt often gets a weak answer), and the 1,000 examples
took real effort to write.


## Preference data at practitioner scale

The same (prompt, chosen, rejected) triples feed a reward model ([02](02-rlhf-pipeline.md#stage-2--reward-model-training)) or DPO directly ([03](03-preference-optimization.md#dpo-in-practice)).
How many pairs you need depends on the goal (*LLM Engineer's Handbook*, ch. 6):

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
(favours its own model family). Zheng et al. measured the first two on MT-Bench: given two similar
answers in both orders, GPT-4 gave the same verdict 65% of the time and Claude-v1 23.8%. Padding an
answer with a reworded copy of its own list fooled Claude-v1 and GPT-3.5 on 91.3% of 23 answers and
GPT-4 on 8.7% ([arXiv:2306.05685](https://arxiv.org/abs/2306.05685) (Zheng et al., NeurIPS 2023)).
Their self-preference data was too thin for the authors to call it a bias. The fixes: randomize A/B order, use few-shot
examples with balanced scores, and use a jury of several models. For a chatbot it targets
about 80% judge–human agreement (*LLM Engineer's Handbook*, ch. 5). Reward models such as
ArmoRM can also act as the scorer. The book's worked example skips the judge: the
human-written blog paragraph is "chosen" and an LLM-generated answer is "rejected", and
filtering left 1,467 pairs.

## Pitfalls

- **Training on your eval set by accident.** Near-duplicates and rephrased synthetic items leak in easily. The decontamination steps and the private in-house eval set are in [6b](06b-dataset-engineering-for-post-training.md#pitfalls).
- **Trusting a verifier because it is deterministic.** A checker that passes shortcuts teaches shortcuts, as GLM-5's layout checker did. Red-team the checker before you train on it.
- **Simulator drift.** An environment that doesn't match production trains for the simulator. Replay production failures through it regularly.

## Try it

1. List the three most expensive mistakes your agent could make in production, then decide whether your environment can even represent each one.
2. Take 50 pairs from your domain and label them twice, a week apart. What agreement rate do you get? How does this compare with the handbook's 80% judge-human agreement target?

<details><summary>Answers</summary>

1. If the environment can't represent a mistake, training cannot teach the agent to avoid it. The first engineering work is to add a way for that mistake to happen and be detected.
2. Any human self-agreement number is your practical ceiling. A judge can't be shown to be better than the noise in the labels it is scored against.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| Why does the environment matter more than the algorithm? | The policy learns whatever earns reward in the environment. A distorted environment produces strategies that die on deployment. |
| Where can training data go wrong besides quality? | Near-duplicates, eval contamination, unbalanced coverage, and synthetic data repeating the generator's errors. |
| Where did instruction tuning come from? | Two concurrent ICLR 2022 papers that rewrote NLP datasets as instructions and tested on task types held out of training. |
| How many preference pairs do you need? | It depends on the goal: see the table in this chapter, where task-level style or refusal changes need 100–10k. |
| What is the handbook's shortcut for preference pairs? | Use a real blog paragraph as chosen and an LLM answer as rejected, then filter. |

## Next

[6b — Dataset engineering for post-training](06b-dataset-engineering-for-post-training.md) takes the dataset half further: quality against diversity, synthetic data, curation code. Then [07 — Reward design and tool calling](07-reward-design-and-tool-calling.md) turns from what the agent practises on to how each step of a multi-turn run gets scored. Eval set discipline is in [generative-ai/08-eval](../../08-eval/README.md).
