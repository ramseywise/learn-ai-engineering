---
origin: curated
sources:
  - https://github.com/dair-ai/Prompt-Engineering-Guide
  - scripts/papers/ledger.jsonl (PDFs filed for this pillar)
confidence: high
cleaned: 2026-11-02
---
# Prompt Engineering: Papers and Further Reading

> Every source behind the chapters in [notes/](notes/). Course index: [README](README.md). arXiv IDs resolve at `https://arxiv.org/abs/<id>`. **★** marks the one or two to read first in each section.

---

## Books

| Reading | Where | Why |
|---|---|---|
| ★ Berryman & Ziegler, *Prompt Engineering for LLMs* (O'Reilly 2024) | PDFs: [sources/prompt-eng-for-llms/reading/](sources/prompt-eng-for-llms/reading/) · figures: `sources/images/berryman-prompt-engineering-for-llms-fig*.png` | The backbone of the pillar. Audited chapter by chapter (2026-10): ch. 1–3 → 01, 10; ch. 4–6 → 02, 03, 08; ch. 7–8 → 04, 05, 11; ch. 9 → 06; ch. 10 → 09 and eval [03–05](../../generative-ai/08-eval/notes); ch. 11 → 07. Each note's *Go deeper* links the chapter PDF. Written by two of the original GitHub Copilot engineers |
| ★ Huyen, *AI Engineering* (O'Reilly 2025) — **Ch 5, Prompt Engineering** | [sources/huyen-ai-engineering/ch05](sources/huyen-ai-engineering/ch05-prompt-engineering.pdf) · figures: `sources/images/huyen-ai-engineering-fig5-*.png` | The best single chapter on prompting *as engineering*. Folded in as: ch. 5 chat templates → [01](notes/01-how-models-read-prompts.md); lost-in-the-middle and NIAH → [02](notes/02-prompt-anatomy.md#ordering); few-shot on strong models → [03](notes/03-core-techniques.md#few-shot); decomposition cost → [06](notes/06-chaining-and-workflows.md#why-split); prompt catalogs and tool pitfalls → [08](notes/08-prompt-optimization.md); automated attacks, training-data extraction, instruction hierarchy, violation vs. false-refusal rate → [10](notes/10-adversarial-prompting.md). Notes cite it as `(*AI Engineering*, ch. N)`. Ch 3–4 (evaluation) and ch. 10 (user feedback) are folded into the eval pillar ([Eval references](../../generative-ai/08-eval/references.md#books-and-courses)) and back [09](notes/09-evaluating-prompts.md) |
| Phoenix & Taylor, *Prompt Engineering for Generative AI* (O'Reilly 2024) | [generative-ai/01-llm-fundamentals/sources/](<../../generative-ai/01-llm-fundamentals/sources/>) | The "five principles of prompting" (Ch 1), text-generation practice (Ch 3) and LangChain chaining (Ch 4). Ch 7–9 cover image prompting. Folded in (2026-10) as: ch. 1 → [02](notes/02-prompt-anatomy.md), [03](notes/03-core-techniques.md#few-shot), [04](notes/04-controlling-output.md) (including a contradiction on its Fig 1-13), [09](notes/09-evaluating-prompts.md); ch. 3 → [03](notes/03-core-techniques.md), [04](notes/04-controlling-output.md), [06](notes/06-chaining-and-workflows.md), eval [05](../../generative-ai/08-eval/notes/05-llm-as-judge.md); ch. 8 (Midjourney) → [11](notes/11-applications.md#prompting-image-generators); ch. 10 → [06](notes/06-chaining-and-workflows.md), [09](notes/09-evaluating-prompts.md). Figures: `sources/images/prompt-engineering-for-generative-ai-fig1-13.png`, `-fig10-1.png`. Notes cite it as `(*Prompt Engineering for Generative AI*, ch. N)` |
| *Building Applications with AI Agents* — Ch 4 (Tool Use), Ch 12 (Protecting Agentic Systems) | [ch04](../03-harness-engineering/sources/building-applications-with-ai-agents/ch04-tool-use.pdf), [ch12](../03-harness-engineering/sources/building-applications-with-ai-agents/ch12-protecting-agentic-systems.pdf) | Goes deeper than [05](notes/05-tools-and-function-calling.md) and [10](notes/10-adversarial-prompting.md) |

## Core papers

### Technique papers

These are the papers behind [03 — core techniques](notes/03-core-techniques.md), in the order the note covers them.

| Technique | Paper | arXiv |
|---|---|---|
| Few-shot / in-context learning | Brown et al., *Language Models are Few-Shot Learners* (GPT-3) | 2005.14165 |
| What makes few-shot work | ★ Min et al., *Rethinking the Role of Demonstrations* | 2202.12837 |
| Many-shot ICL and OOD brittleness | de Wynter, *Is In-Context Learning Learning?* · [PDF](sources/wynter-2025-context-learning-learning.pdf) | 2509.10414 |
| Instruction tuning (why zero-shot works) | Wei et al., *Finetuned Language Models Are Zero-Shot Learners* (FLAN) | 2109.01652 |
| Chain-of-thought | ★ Wei et al. | 2201.11903 |
| Zero-shot CoT ("Let's think step by step") | Kojima et al. | 2205.11916 |
| Where CoT helps (math and symbolic) | ★ Sprague et al., *To CoT or not to CoT?* · [PDF](sources/sprague-2024-cot-or-not-cot.pdf) | 2409.12183 |
| CoT under distribution shift | Zhao et al., *Is Chain-of-Thought Reasoning of LLMs a Mirage?* · [PDF](sources/zhao-2025-chain-thought-reasoning-llms-mirage.pdf) | 2508.01191 |
| Auto-CoT | Zhang et al. | 2210.03493 |
| Multimodal CoT | Zhang et al. | 2302.00923 |
| GraphPrompt | Liu et al. | 2302.08043 |
| Self-consistency | Wang et al. | 2203.11171 |
| Generated knowledge | Liu et al. | 2110.08387 |
| Tree of Thoughts | Yao et al. · Long | 2305.10601 · 2305.08291 |
| PAL — program-aided LMs | Gao et al. | 2211.10435 |
| ReAct | ★ Yao et al. | 2210.03629 |
| ART — automatic reasoning and tool use | Paranjape et al. | 2303.09014 |
| Active-Prompt | Diao et al. | 2302.12246 |
| Directional stimulus prompting | Li et al. | 2302.11520 |
| Reflexion | Shinn et al. | 2303.11366 |
| Format restrictions vs reasoning ([04](notes/04-controlling-output.md#structured-output)) | Tam et al., *Let Me Speak Freely?* · [PDF](sources/tam-2024-let-me-speak-freely.pdf) | 2408.02442 |

**Background:** Kaplan et al., *Scaling Laws* (2001.08361) · Christiano et al., *RLHF from human preferences* (1706.03741) · Bubeck et al., *Sparks of AGI* (2303.12712) — the source of the TiKZ unicorn and other probes in the [prompt library](notes/prompt-library.md).

### Prompt optimization

For [08](notes/08-prompt-optimization.md).

| Method | Paper / link | arXiv |
|---|---|---|
| APE — automatic prompt engineer | ★ Zhou et al., *LLMs Are Human-Level Prompt Engineers* | 2211.01910 |
| OPRO — LLM as optimizer | Yang et al., *Large Language Models as Optimizers* | 2309.03409 |
| Prompt-OIRL | Sun et al. | 2309.06553 |
| AutoPrompt | Shin et al. | 2010.15980 |
| Prefix tuning | Li & Liang | 2101.00190 |
| Prompt tuning (soft prompts) | Lester et al. | 2104.08691 |
| Meta-prompting (structure-oriented) | Zhang et al. | 2311.11482 |
| DSPy | ★ Khattab et al. · [dspy.ai](https://dspy.ai) | 2310.03714 |
| TextGrad | Yuksekgonul et al. | 2406.07496 |
| GEPA — reflective prompt evolution | Agrawal et al., *GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning* · [PDF](sources/agrawal-2025-gepa.pdf) | 2507.19457 |

### Reasoning models

For [07](notes/07-prompting-reasoning-models.md). This area moves fastest, so check the vendor guides above first.

- ★ DAIR *Reasoning LLMs Guide* — [promptingguide.ai/guides/reasoning-llms](https://www.promptingguide.ai/guides/reasoning-llms)
- DeepSeek-AI, *DeepSeek-R1: Incentivizing Reasoning Capability via RL* — 2501.12948
- Raschka, [*Understanding Reasoning LLMs*](https://magazine.sebastianraschka.com/p/understanding-reasoning-llms) — an overview of how reasoning models are trained
- *The Pitfalls of Reasoning for Instruction Following* — 2505.11423 (explicit CoT hurts instruction-following)
- Ma et al., *Reasoning Models Can Be Effective Without Thinking* — 2504.09858 · [PDF](sources/ma-2025-reasoning-models-can-be-effective.pdf) (NoThinking prefill plus parallel sampling)
- Anthropic, *Reasoning Models Don't Always Say What They Think* — 2505.05410 (CoT faithfulness)
- Lanham et al., *Measuring Faithfulness in Chain-of-Thought Reasoning* — 2307.13702 · [PDF](../../generative-ai/08-eval/sources/lanham-2023-measuring-faithfulness-cot.pdf) (early answering, adding mistakes, filler tokens, paraphrasing; how much the answer depends on the chain varies by task and falls with model size; for [03](notes/03-core-techniques.md))
- Shojaee et al., [*The Illusion of Thinking*](https://machinelearning.apple.com/research/illusion-of-thinking) (Apple, 2025) — collapse on harder puzzles; read it with the rebuttals it prompted

### Evaluation

For [09](notes/09-evaluating-prompts.md). Deeper material is in [the Eval pillar](../../generative-ai/08-eval/README.md).

- ★ Book Ch 10 — [sources/prompt-eng-for-llms/reading/10-evaluating-llm-applications.pdf](sources/prompt-eng-for-llms/reading/10-evaluating-llm-applications.pdf)
- Clavié et al., *Large Language Models in the Workplace* — 2303.07142 (the case-study table)
- Huyen, *AI Engineering* Ch 3–4 — [ch03](../../generative-ai/08-eval/sources/huyen-ai-engineering/ch03-evaluation-methodology.pdf), [ch04](../../generative-ai/08-eval/sources/huyen-ai-engineering/ch04-evaluate-ai-systems.pdf)
- Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* — 2306.05685 (judge biases: position, verbosity, self-preference)
- Ribeiro et al., *Beyond Accuracy: Behavioral Testing of NLP Models with CheckList* — 2005.04118 (minimum functionality, invariance and directional tests; pre-LLM NLP models)
- Husain, [*Your AI Product Needs Evals*](https://hamel.dev/blog/posts/evals/) — the practitioner's case for building the eval first

### Safety and adversarial

For [10](notes/10-adversarial-prompting.md). For interview depth, see [interviewing/7-security-safety/prompt-injection.md](../../practice/interviewing/guides/7-security-safety/prompt-injection.md).

- ★ Willison, [*Prompt injection attacks against GPT-3*](https://simonwillison.net/2022/Sep/12/prompt-injection/) (2022) — where the name comes from
- Willison, [*The Dual LLM pattern*](https://simonwillison.net/2023/Apr/25/dual-llm-pattern/) — the quarantined-model defense
- Greshake et al., *Not What You've Signed Up For* (indirect prompt injection) — 2302.12173
- Debenedetti et al., *Defeating Prompt Injections by Design* (CaMeL) — 2503.18813
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) — LLM01 is prompt injection
- NIST, [*Adversarial Machine Learning: A Taxonomy*](https://csrc.nist.gov/pubs/ai/100/2/e2023/final) (AI 100-2)
- Kang et al., *Exploiting Programmatic Behavior of LLMs* — 2302.05733 (jailbreaks as programs)
- 2303.07320 — cited on the DAIR adversarial page
- Armstrong & Gorman, *Using GPT-Eliezer against ChatGPT jailbreaking* (LessWrong, 2022) — the input-screening prompt
- Nardo, *The Waluigi Effect* (LessWrong, 2023)
- Lin et al., *TruthfulQA* — 2109.07958 (measuring imitative falsehoods)

### Applications

For [11](notes/11-applications.md).

| Topic | Paper | arXiv |
|---|---|---|
| Combinatorial seeding | Eldan & Li, *TinyStories* | 2305.07759 |
| Textbook-quality synthetic data | Gunasekar et al., *Textbooks Are All You Need* (phi-1) | 2306.11644 |
| Synthetic retrieval queries | Dai et al., *Promptagator* | 2209.11755 |
| Code generation and HumanEval | Chen et al., *Evaluating LLMs Trained on Code* (Codex) | 2107.03374 |
| Tool-use fine-tuning | Patil et al., *Gorilla* · Qin et al., *ToolLLM* | 2305.15334 · 2307.16789 |

### Filed elsewhere in this repo

| Reading | Where | Why |
|---|---|---|
| Wei et al., *Chain-of-Thought Prompting* (2201.11903) | [sources/wei-2022-…](sources/wei-2022-chain-thought-prompting-elicits-reasoning.pdf) | The CoT paper ([03](notes/03-core-techniques.md#chain-of-thought)) |
| Ouyang et al., *InstructGPT* (2203.02155) | [05-RL/sources/ouyang-2022-…](../../generative-ai/05-RL/sources/ouyang-2022-training-language-models-follow-instructions.pdf) | Why chat models follow instructions ([01](notes/01-how-models-read-prompts.md)) |
| Bai et al., *Constitutional AI* (2212.08073) | [05-RL/sources/bai-2022-…](../../generative-ai/05-RL/sources/bai-2022-constitutional-ai.pdf) | Principles-as-prompts; model self-critique |
| Manakul et al., *SelfCheckGPT* (2303.08896) | [generative-ai/08-eval/sources/manakul-2023-…](../../generative-ai/08-eval/sources/manakul-2023-selfcheckgpt.pdf) | Sampling-consistency hallucination checks ([10 — factuality](notes/10-adversarial-prompting.md#factuality)) |
| Zhao et al., *A Survey of LLMs* (2303.18223) | [01-llm-fundamentals/sources/zhao-2023-…](../../generative-ai/01-llm-fundamentals/sources/zhao-2023-survey-large-language-models.pdf) | Its section on prompting and in-context learning |

### Other readings

These are broader or more opinionated pieces, good once the notes feel familiar.

- ★ Schulhoff et al., *The Prompt Report: A Systematic Survey of Prompting Techniques* — 2406.06608. A taxonomy of 58 text techniques, with terminology; the best "did I miss anything?" check
- Weng, [*Prompt Engineering*](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/) (2023) — a dense, research-oriented survey
- Yan, [*Prompting Fundamentals and How to Apply Them Effectively*](https://eugeneyan.com/writing/prompting/) — a practitioner's view with production examples
- [Learn Prompting](https://learnprompting.org) — a beginner-friendly open course, an alternative to DAIR
- Li, *AI Agents in Depth*, [ch. 2 §Prompt Engineering](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter2.md) — system-prompt design for agents. Labs: τ-bench prompt ablation (2-4), injection attacks (2-5), attention visualization (2-2), prompt patches from failures (8-3). Synthesised into [02](notes/02-prompt-anatomy.md) and [10](notes/10-adversarial-prompting.md), which link the labs upstream.
- Context engineering — the successor framing (Karpathy, LangChain, Schmid, Lance Martin). Collected in [02-context](../02-context-engineering/README.md)

## Where the ideas come from

<!-- citegraph:origins start -->
<!-- citegraph:origins end -->

## AI Papers of the Week

Papers picked up by the weekly [DAIR](https://github.com/dair-ai/AI-Papers-of-the-Week) sync (`make papers`, then `/papers`).

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| de Wynter, [*Is In-Context Learning Learning?*](https://arxiv.org/abs/2509.10414) (Sep 2025 ⚑) | GPT-4 Turbo, GPT-4o, Mixtral 8x7B and Phi-3.5 MoE on nine synthetic formal-language tasks (0 to 100 exemplars, temperature 0) peaked at 50–100 exemplars. Accuracy fell as test inputs drifted from the exemplars, fastest for CoT (slope −1.4, against −0.5 for an APO prompt and −0.4 for modus ponens); related tasks differed by up to 31 points, and decision trees or kNN beat ICL in half the tasks | [2509.10414](sources/wynter-2025-context-learning-learning.pdf) | [03](notes/03-core-techniques.md#few-shot) · [08](notes/08-prompt-optimization.md#dspy-and-programmatic-optimization) · [eval 03](../../generative-ai/08-eval/notes/03-eval-datasets.md#coverage-and-balance) |
| Zhao et al., [*Is Chain-of-Thought Reasoning of LLMs a Mirage? A Data Distribution Lens*](https://arxiv.org/abs/2508.01191) (ACL Findings 2026) | Models trained from scratch (62K to 3B parameters) on synthetic letter transformations scored 100% full-chain exact match in distribution, 0.01% on new compositions of known transformations and 0% on unseen ones or on input lengths one letter off training; fine-tuned LLaMA3-8B and Qwen3-14B reached at most 8.52%. CoT trained into models on a toy domain, not CoT prompted from a general model | [2508.01191](sources/zhao-2025-chain-thought-reasoning-llms-mirage.pdf) | [03](notes/03-core-techniques.md#chain-of-thought) · [eval 03](../../generative-ai/08-eval/notes/03-eval-datasets.md#coverage-and-balance) |
| Agrawal et al., [*GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning*](https://arxiv.org/abs/2507.19457) (ICLR 2026) | An LLM reads full traces, diagnoses failures and rewrites one module's prompt, mutating from a Pareto front of candidates. With Qwen3 8B on six benchmarks it raised the aggregate 9.62 points, against 3.68 for GRPO with 24,000 rollouts and 2.61 for MIPROv2 (beating GRPO everywhere but AIME); with GPT-4.1 Mini, +12.19 vs +6.11 for TextGrad and +5.64 for MIPROv2, with prompts up to 9.2× shorter than MIPROv2's. Needs a metric that returns text feedback | [2507.19457](sources/agrawal-2025-gepa.pdf) | [08](notes/08-prompt-optimization.md#dspy-and-programmatic-optimization) |
| Shojaee et al. (Apple), [*The Illusion of Thinking*](https://arxiv.org/abs/2506.06941) (Jun 2025) | On puzzles with tunable difficulty, non-thinking models match or beat thinking ones on easy instances. Thinking helps on medium ones, and both collapse to zero on hard ones, where thinking tokens drop despite budget left. The collapse is partly an artifact: full move lists overrun the output limit, and some River Crossing instances are unsolvable ([Lawsen, 2506.09250](https://arxiv.org/abs/2506.09250)) | [2506.06941](sources/illusion-thinking-2025.pdf) | [07](notes/07-prompting-reasoning-models.md#whats-different) |
| Li et al., [*When Thinking Fails: The Pitfalls of Reasoning for Instruction-Following in LLMs*](https://arxiv.org/abs/2505.11423) (NeurIPS 2025) | CoT prompting lowered instruction-following accuracy for 13 of 14 models on IFEval and all of them on ComplexBench (Llama-3-8B-Instruct 75.2% to 59.0% on IFEval); thinking-enabled pairs (Claude 3.7 Sonnet, DeepSeek-R1 vs V3) dropped by under 2 points. A trained classifier that decides whether to reason recovered most of the loss | [2505.11423](sources/li-2025-when-thinking-fails.pdf) | [07](notes/07-prompting-reasoning-models.md#whats-different) |
| Ma et al., [*Reasoning Models Can Be Effective Without Thinking*](https://arxiv.org/abs/2504.09858) (Apr 2025 ⚑) | Prefilling a dummy thinking block ("NoThinking") in DeepSeek-R1-Distill-Qwen-32B used 2.0–5.1× fewer tokens and matched full thinking at large pass@k (at every k on theorem proving, with 3.3–3.7× fewer tokens); at a 700-token budget it scored 51.3 vs 28.9 on AMC23, and parallel NoThinking with a verifier beat thinking at 7× lower latency. Open-weight models only | [2504.09858](sources/ma-2025-reasoning-models-can-be-effective.pdf) | [07](notes/07-prompting-reasoning-models.md#hybrid-models-escalate-gradually) |
| Zaremba et al. (OpenAI), [*Trading Inference-Time Compute for Adversarial Robustness*](https://arxiv.org/abs/2501.18841) (Jan 2025) | More reasoning compute drives attack success on o1-preview and o1-mini towards zero for injections with an unambiguous goal, with no adversarial training. Human red-teamers needed 22.6 attempts at the highest compute vs. 11.0 at the lowest. No gain on ambiguous misuse prompts. Vendor-run | [2501.18841](sources/trading-test-time-compute-adversarial-2025.pdf) | [10](notes/10-adversarial-prompting.md#defenses-weakest-to-strongest) |
| OpenAI, [*OpenAI o1 System Card*](https://arxiv.org/abs/2412.16720) (Dec 2024) | Adds a developer role (system > developer > user). o1 resolves role conflicts better than GPT-4o (0.78 vs. 0.68 developer over user) and holds a tutor instruction against jailbreaks 0.95 vs. 0.33. A CoT monitor flagged 0.17% of 102,443 chains as deceptive. Vendor self-report | [2412.16720](sources/openai-o1-2024.pdf) | [10](notes/10-adversarial-prompting.md#defenses-weakest-to-strongest), [07](notes/07-prompting-reasoning-models.md#known-failure-modes) |
| Tam et al., [*Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of LLMs*](https://arxiv.org/abs/2408.02442) (EMNLP 2024 Industry) | In JSON mode, 100% of GPT-3.5 Turbo responses put "answer" before "reason", turning CoT into direct answering; on GSM8K, Claude 3 Haiku scored 86.99% told to "reply in JSON" and 23.44% with an explicit schema, and the losses were not parse failures. On classification JSON helped (Gemini 1.5 Flash on DDXPlus 41.6% to 60.3%). Only small and mid-size 2024 models on simple schemas | [2408.02442](sources/tam-2024-let-me-speak-freely.pdf) | [04](notes/04-controlling-output.md#structured-output) |
| Yuksekgonul et al., [*TextGrad: Automatic "Differentiation" via Text*](https://arxiv.org/abs/2406.07496) (Nature 2025) | Backpropagates LLM-written critiques through a pipeline as "textual gradients". Optimizing a system prompt for gpt-3.5-turbo with GPT-4o as the critic, on 36 training examples, lifted GSM8K from 72.9% to 81.1% with instructions alone, matching DSPy's 8-shot bootstrapped prompt. Its headline 51% to 55% on GPQA for GPT-4o is test-time refinement of each answer (3 rounds plus majority vote), not prompt optimization | [2406.07496](sources/yuksekgonul-2024-textgrad.pdf) | [08](notes/08-prompt-optimization.md#dspy-and-programmatic-optimization) |
| Andriushchenko (EPFL), [*Adversarial Attacks on GPT-4 via Simple Random Search*](https://www.andriushchenko.me/gpt4adv.pdf) (Dec 2023) | Random search over a 10-character suffix, guided by the top-5 logprobs, raises P("Sure") on `gpt-4-1106-preview` from ≈1% to >50% for under $1. Two hand-picked requests and no success rate; superseded by [2404.02151](https://arxiv.org/abs/2404.02151) | [gpt4adv](sources/adversarial-attacks-gpt-4-2023.pdf) | [10](notes/10-adversarial-prompting.md#automated-attacks) |
| Yang et al., [*Large Language Models as Optimizers*](https://arxiv.org/abs/2309.03409) (ICLR 2024) | OPRO shows the LLM past prompts with their scores and asks for better ones. With PaLM 2-L as scorer, the best instruction found ("Take a deep breath and work on this problem step-by-step.") scored 80.2% zero-shot on GSM8K against 71.8% for "Let's think step by step"; optimized prompts beat human-written ones by up to 8% on GSM8K and up to 50% on Big-Bench Hard tasks, and the best instruction differed by scorer model | [2309.03409](sources/yang-2023-large-language-models-as-optimizers.pdf) | [08](notes/08-prompt-optimization.md#ape--automatic-prompt-engineer) |
| Zhang et al., [*Multimodal Chain-of-Thought Reasoning in Language Models*](https://arxiv.org/abs/2302.00923) (TMLR 2024) | Two-stage fine-tuning (rationale from text + ViT image features, then answer) took a 738M T5 to 90.45% on ScienceQA, against 75.17% for few-shot GPT-3.5 with CoT and 83.99% for GPT-4. In a 200M text-only model, writing the rationale before the answer cut accuracy from 81.63% to 69.32% because the rationales hallucinated image content; captions recovered only 0.8 points. Fine-tuned small models, not a prompting result | [2302.00923](sources/zhang-2023-multimodal-chain-thought-reasoning-language.pdf) | [03](notes/03-core-techniques.md#chain-of-thought) |
| Diao et al., [*Active Prompting with Chain-of-Thought for Large Language Models*](https://arxiv.org/abs/2302.12246) (ACL 2024) | Annotating CoT for the training questions with the most disagreement across k sampled answers lifted code-davinci-002 on GSM8K to 82.2%, against 63.1% for hand-picked CoT exemplars. Most of that is self-consistency voting (78.0% alone); random selection with the same annotation got 78.6%, so the uncertainty selection adds about 4 points | [2302.12246](sources/diao-2023-active-prompting-chain-thought-large.pdf) | [03](notes/03-core-techniques.md#active-prompt) |

---

## Filed, not yet folded into a chapter

PDFs on disk for this pillar that no row above links. The ledger marks most of them `downloaded`, which means nobody has read them into a note. **Maps to** is the chapter the ledger proposes, not a citation that exists. Some arXiv IDs also appear in the tables above without a PDF link.

| Paper | arXiv | PDF | Maps to |
|---|---|---|---|
| Ahn et al. (2024), *LLMs for Mathematical Reasoning* | [2402.00157](https://arxiv.org/abs/2402.00157) | [PDF](sources/ahn-2024-large-language-models-mathematical-reasoning.pdf) | [03](notes/03-core-techniques.md) |
| Andriushchenko et al. (2024), *Does Refusal Training in LLMs Generalize to the Past Tense?* | [2407.11969](https://arxiv.org/abs/2407.11969) | [PDF](sources/andriushchenko-2024-does-refusal-training-llms-generalize.pdf) | [10](notes/10-adversarial-prompting.md) |
| Baherwani et al. (2026), *Invisible Reasoning* | [2607.22925](https://arxiv.org/abs/2607.22925) | [PDF](sources/baherwani-2026-not-all-llm-reasoning-visible.pdf) | [07](notes/07-prompting-reasoning-models.md) |
| Bertsch et al. (2024), *In-Context Learning with Long-Context Models* | [2405.00200](https://arxiv.org/abs/2405.00200) | [PDF](sources/bertsch-2024-context-learning-long-context-models.pdf) | [03](notes/03-core-techniques.md) |
| Bsharat et al. (2023), *Principled Instructions Are All You Need* | [2312.16171](https://arxiv.org/abs/2312.16171) | [PDF](sources/bsharat-2023-principled-instructions-all-you-need.pdf) | [02](notes/02-prompt-anatomy.md) |
| Chen et al. (2024), *Do NOT Think That Much for 2+3=? On the Overthinking of o1-Like LLMs* | [2412.21187](https://arxiv.org/abs/2412.21187) | [PDF](sources/chen-2024-do-not-think-that-much.pdf) | unassigned |
| Chen et al. (2026), *Deep-Thinking Tokens* | [2602.13517](https://arxiv.org/abs/2602.13517) | [PDF](sources/chen-2026-think-deep-not-just-long.pdf) | [07](notes/07-prompting-reasoning-models.md) |
| Creswell et al. (2022), *Selection-Inference: Exploiting Large Language Models for Interpretable Logical Reasoning* | [2205.09712](https://arxiv.org/abs/2205.09712) | [PDF](sources/creswell-2022-selection-inference.pdf) | unassigned |
| Deng et al. (2023), *Rephrase and Respond (RaR)* | [2311.04205](https://arxiv.org/abs/2311.04205) | [PDF](sources/deng-2023-rephrase-respond.pdf) | [03](notes/03-core-techniques.md) |
| Dubois et al. (2023), *AlpacaFarm: A Simulation Framework for Methods that Learn from Human Feedback* | [2305.14387](https://arxiv.org/abs/2305.14387) | [PDF](sources/dubois-2023-alpacafarm.pdf) | unassigned |
| Fu et al. (2025), *Deep Think with Confidence* | [2508.15260](https://arxiv.org/abs/2508.15260) | [PDF](sources/fu-2025-deep-think-confidence.pdf) | [07](notes/07-prompting-reasoning-models.md) |
| Gao et al. (2021), *Making Pre-trained Language Models Better Few-shot Learners* | [DOI](https://doi.org/10.18653/v1/2021.acl-long.295) | [PDF](sources/gao-2021-making-pre-trained-language-models.pdf) | unassigned |
| Goyal et al. (2022), *News Summarization and Evaluation in the Era of GPT-3* | [2209.12356](https://arxiv.org/abs/2209.12356) | [PDF](sources/goyal-2022-news-summarization-evaluation-era-gpt.pdf) | unassigned |
| Greshake et al. (2023), *Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection* | [2302.12173](https://arxiv.org/abs/2302.12173) | [PDF](sources/greshake-2023-not-what-you-ve-signed.pdf) | unassigned |
| He et al. (2024), *Does Prompt Formatting Impact LLM Performance* | [2411.10541](https://arxiv.org/abs/2411.10541) | [PDF](sources/he-2024-does-prompt-formatting-have-any.pdf) | [02](notes/02-prompt-anatomy.md) |
| Hong et al. (2024), *Mixtures of In-Context Learners* | [2411.02830](https://arxiv.org/abs/2411.02830) | [PDF](sources/hong-2024-mixtures-context-learners.pdf) | [03](notes/03-core-techniques.md) |
| Imani et al. (2023), *MathPrompter: Mathematical Reasoning using Large Language Models* | [2303.05398](https://arxiv.org/abs/2303.05398) | [PDF](sources/imani-2023-mathprompter.pdf) | [03](notes/03-core-techniques.md) |
| Kojima et al. (2022), *Large Language Models are Zero-Shot Reasoners* | [2205.11916](https://arxiv.org/abs/2205.11916) | [PDF](sources/kojima-2022-large-language-models-zero-shot.pdf) | unassigned |
| Lee et al. (2025), *How Well do LLMs Compress Their Own Chain-of-Thought?* | [2503.01141](https://arxiv.org/abs/2503.01141) | [PDF](sources/lee-2025-how-well-do-llms-compress.pdf) | [07](notes/07-prompting-reasoning-models.md) |
| Li et al. (2023), *Chain of Code* | [2312.04474](https://arxiv.org/abs/2312.04474) | [PDF](sources/li-2023-chain-code.pdf) | [03](notes/03-core-techniques.md) |
| Li et al. (2023), *ChatGPT for Information Extraction* | [2304.11633](https://arxiv.org/abs/2304.11633) | [PDF](sources/li-2023-evaluating-chatgpt-s-information-extraction.pdf) | [09](notes/09-evaluating-prompts.md) |
| Li et al. (2023), *Large Language Models Understand and Can Be Enhanced by Emotional Stimuli* | [2307.11760](https://arxiv.org/abs/2307.11760) | [PDF](sources/li-2023-large-language-models-understand-can.pdf) | unassigned |
| Li et al. (2025), *Implicit Reasoning in LLMs* | [2509.02350](https://arxiv.org/abs/2509.02350) | [PDF](sources/li-2025-implicit-reasoning-large-language-models.pdf) | [07](notes/07-prompting-reasoning-models.md) |
| Liang et al. (2024), *Controllable Text Generation for LLMs* | [2408.12599](https://arxiv.org/abs/2408.12599) | [PDF](sources/liang-2024-controllable-text-generation-large-language.pdf) | [04](notes/04-controlling-output.md) |
| Liu et al. (2024), *Logic-of-Thought* | [2409.17539](https://arxiv.org/abs/2409.17539) | [PDF](sources/liu-2024-logic-thought.pdf) | [03](notes/03-core-techniques.md) |
| Lu et al. (2022), *Fantastically Ordered Prompts and Where to Find Them: Overcoming Few-Shot Prompt Order Sensitivity* | [2104.08786](https://arxiv.org/abs/2104.08786) | [PDF](sources/lu-2022-fantastically-ordered-prompts-where-find.pdf) | unassigned |
| Miao et al. (2023), *Self-Check* | [2308.00436](https://arxiv.org/abs/2308.00436) | [PDF](sources/miao-2023-selfcheck.pdf) | [03](notes/03-core-techniques.md) |
| Nayab et al. (2024), *Constrained-CoT* | [2407.19825](https://arxiv.org/abs/2407.19825) | [PDF](sources/nayab-2024-concise-thoughts.pdf) | [07](notes/07-prompting-reasoning-models.md) |
| Nori et al. (2023), *Medprompt* | [2311.16452](https://arxiv.org/abs/2311.16452) | [PDF](sources/nori-2023-can-generalist-foundation-models-outcompete.pdf) | [03](notes/03-core-techniques.md) |
| Nye et al. (2021), *Show Your Work: Scratchpads for Intermediate Computation with Language Models* | [2112.00114](https://arxiv.org/abs/2112.00114) | [PDF](sources/nye-2021-show-your-work.pdf) | unassigned |
| Patel et al. (2021), *Are NLP Models really able to Solve Simple Math Word Problems?* | [2103.07191](https://arxiv.org/abs/2103.07191) | [PDF](sources/patel-2021-nlp-models-really-able-solve.pdf) | unassigned |
| Peng et al. (2024), *Mitigating LLM Jailbreaks with Few Examples* | [2411.07494](https://arxiv.org/abs/2411.07494) | [PDF](sources/peng-2024-rapid-response.pdf) | [10](notes/10-adversarial-prompting.md) |
| Ramnath et al. (2025), *A Systematic Survey of Prompt Optimization* | [2502.16923](https://arxiv.org/abs/2502.16923) | [PDF](sources/ramnath-2025-systematic-survey-automatic-prompt-optimization.pdf) | [08](notes/08-prompt-optimization.md) |
| Schick et al. (2021), *It’s Not Just Size That Matters: Small Language Models Are Also Few-Shot Learners* | [2009.07118](https://arxiv.org/abs/2009.07118) | [PDF](sources/schick-2021-its-not-just-size-that.pdf) | unassigned |
| Sclar et al. (2023), *Quantifying Prompt-Format Sensitivity* | [2310.11324](https://arxiv.org/abs/2310.11324) | [PDF](sources/sclar-2023-quantifying-language-models-sensitivity-spurious.pdf) | [09](notes/09-evaluating-prompts.md) |
| Shakarian et al. (2023), *An Independent Evaluation of ChatGPT on Mathematical Word Problems (MWP)* | [2302.13814](https://arxiv.org/abs/2302.13814) | [PDF](sources/shakarian-2023-independent-evaluation-chatgpt-mathematical-word.pdf) | unassigned |
| Shypula et al. (2023), *Learning Performance-Improving Code Edits* | [2302.07867](https://arxiv.org/abs/2302.07867) | [PDF](sources/shypula-2023-learning-performance-improving-code-edits.pdf) | unassigned |
| Sui et al. (2025), *A Survey on Efficient Reasoning* | [2503.16419](https://arxiv.org/abs/2503.16419) | [PDF](sources/sui-2025-stop-overthinking.pdf) | [07](notes/07-prompting-reasoning-models.md) |
| Turpin et al. (2023), *Unfaithful Explanations in Chain-of-Thought Prompting* | [2305.04388](https://arxiv.org/abs/2305.04388) | [PDF](sources/turpin-2023-language-models-don-t-always.pdf) | [03](notes/03-core-techniques.md) |
| Vatsal et al. (2024), *A Survey of Prompt Engineering Methods in LLMs* | [2407.12994](https://arxiv.org/abs/2407.12994) | [PDF](sources/vatsal-2024-survey-prompt-engineering-methods-large.pdf) | [03](notes/03-core-techniques.md) |
| Wang et al. (2017), *Program Induction by Rationale Generation: Learning to Solve and Explain Algebraic Word Problems* | [1705.04146](https://arxiv.org/abs/1705.04146) | [PDF](sources/wang-2017-program-induction-rationale-generation.pdf) | unassigned |
| Wang et al. (2024), *Chain-of-Table* | [2401.04398](https://arxiv.org/abs/2401.04398) | [PDF](sources/wang-2024-chain-table.pdf) | [03](notes/03-core-techniques.md) |
| Wang et al. (2024), *Chain-of-Thought Reasoning Without Prompting* | [2402.10200](https://arxiv.org/abs/2402.10200) | [PDF](sources/wang-2024-chain-thought-reasoning-without-prompting.pdf) | [03](notes/03-core-techniques.md) |
| Wang et al. (2024), *Retrieval Augmented Thoughts (RAT)* | [2403.05313](https://arxiv.org/abs/2403.05313) | [PDF](sources/wang-2024-rat.pdf) | [03](notes/03-core-techniques.md) |
| Wang et al. (2025), *Thoughts Are All Over the Place: On the Underthinking of o1-Like LLMs* | [2501.18585](https://arxiv.org/abs/2501.18585) | [PDF](sources/wang-2025-thoughts-all-over-place.pdf) | unassigned |
| Wei et al. (2022), *Emergent Abilities of Large Language Models* | [2206.07682](https://arxiv.org/abs/2206.07682) | [PDF](sources/wei-2022-emergent-abilities-large-language-models.pdf) | unassigned |
| Wei et al. (2023), *Larger language models do in-context learning differently* | [2303.03846](https://arxiv.org/abs/2303.03846) | [PDF](sources/wei-2023-larger-language-models-do-context.pdf) | [03](notes/03-core-techniques.md) |
| Wen et al. (2023), *Hard Prompts Made Easy: Gradient-Based Discrete Optimization for Prompt Tuning and Discovery* | [2302.03668](https://arxiv.org/abs/2302.03668) | [PDF](sources/wen-2023-hard-prompts-made-easy.pdf) | [08](notes/08-prompt-optimization.md) |
| Wen et al. (2025), *ParaThinker* | [2509.04475](https://arxiv.org/abs/2509.04475) | [PDF](sources/wen-2025-parathinker.pdf) | [07](notes/07-prompting-reasoning-models.md) |
| Willard et al. (2023), *Outlines (Efficient Guided Generation)* | [2307.09702](https://arxiv.org/abs/2307.09702) | [PDF](sources/willard-2023-efficient-guided-generation-large-language.pdf) | [04](notes/04-controlling-output.md) |
| Wu et al. (2023), *OpenICL: An Open-Source Framework for In-context Learning* | [2303.02913](https://arxiv.org/abs/2303.02913) | [PDF](sources/wu-2023-openicl.pdf) | [03](notes/03-core-techniques.md) |
| Wu et al. (2024), *Visualization-of-Thought* | [2404.03622](https://arxiv.org/abs/2404.03622) | [PDF](sources/wu-2024-mind-s-eye-llms.pdf) | [03](notes/03-core-techniques.md) |
| Xiang et al. (2025), *Towards System 2 Reasoning* | [2501.04682](https://arxiv.org/abs/2501.04682) | [PDF](sources/xiang-2025-towards-system-2-reasoning-llms.pdf) | [07](notes/07-prompting-reasoning-models.md) |
| Xu et al. (2024), *Faithful Logical Reasoning via Symbolic Chain-of-Thought* | [2405.18357](https://arxiv.org/abs/2405.18357) | [PDF](sources/xu-2024-faithful-logical-reasoning-symbolic-chain.pdf) | unassigned |
| Xu et al. (2025), *Chain-of-Draft* | [2502.18600](https://arxiv.org/abs/2502.18600) | [PDF](sources/xu-2025-chain-draft.pdf) | [03](notes/03-core-techniques.md) |
| Yang et al. (2024), *Number Understanding of LLMs* | [2411.03766](https://arxiv.org/abs/2411.03766) | [PDF](sources/yang-2024-number-cookbook.pdf) | [03](notes/03-core-techniques.md) |
| Yang et al. (2026), *SkillOpt* | [2605.23904](https://arxiv.org/abs/2605.23904) | [PDF](sources/yang-2026-skillopt.pdf) | [08](notes/08-prompt-optimization.md) |
| Yasunaga et al. (2023), *Analogical Prompting* | [2310.01714](https://arxiv.org/abs/2310.01714) | [PDF](sources/yasunaga-2023-large-language-models-as-analogical.pdf) | [03](notes/03-core-techniques.md) |
| Yeadon et al. (2024), *LLMs on University-Level Physics Coding* | [2403.16977](https://arxiv.org/abs/2403.16977) | [PDF](sources/yeadon-2024-comparison-human-gpt-3-5.pdf) | [09](notes/09-evaluating-prompts.md) |
| Zhang et al. (2024), *Attacking Vision-Language Agents via Pop-ups* | [2411.02391](https://arxiv.org/abs/2411.02391) | [PDF](sources/zhang-2024-attacking-vision-language-computer-agents.pdf) | [10](notes/10-adversarial-prompting.md) |
| Zhou et al. (2022), *Large Language Models Are Human-Level Prompt Engineers* | [2211.01910](https://arxiv.org/abs/2211.01910) | [PDF](sources/zhou-2022-large-language-models-human-level.pdf) | unassigned |
| Zhou et al. (2022), *Least-to-Most Prompting Enables Complex Reasoning in Large Language Models* | [2205.10625](https://arxiv.org/abs/2205.10625) | [PDF](sources/zhou-2022-least-most-prompting-enables-complex.pdf) | unassigned |
| Zhu et al. (2023), *Large Language Models can Learn Rules* | [2310.07064](https://arxiv.org/abs/2310.07064) | [PDF](sources/zhu-2023-large-language-models-can-learn.pdf) | unassigned |
| Zhu et al. (2025), *A Survey on Latent Reasoning* | [2507.06203](https://arxiv.org/abs/2507.06203) | [PDF](sources/zhu-2025-survey-latent-reasoning.pdf) | [07](notes/07-prompting-reasoning-models.md) |
| Zou et al. (2023), *Universal Adversarial LLM Attacks* | [2307.15043](https://arxiv.org/abs/2307.15043) | [PDF](sources/zou-2023-universal-transferable-adversarial-attacks-aligned.pdf) | [10](notes/10-adversarial-prompting.md) |

## Courses and videos

| Course or video | Platform, cost | Where | Use it for |
|---|---|---|---|
| DAIR.AI *Prompt Engineering Guide* | Web and GitHub, free | [promptingguide.ai](https://www.promptingguide.ai/) · [GitHub](https://github.com/dair-ai/Prompt-Engineering-Guide) | The technique catalog (notes 03, 08, 10, 11). Its pages are absorbed into the notes, so check the live site for new additions |
| DAIR lecture (Elvis Saravia) | YouTube, free, about one hour | [video](https://youtu.be/dOxUroR57xs) · [figures](sources/images/) | A one-hour 2023 overview; a good first pass. Its slides are superseded by our [deck](slides/deck.yaml) |

The DAIR notebooks were absorbed into the notes as code snippets (each is credited where it appears). The two that ran on their own (retrieval-augmented generation and Gemini context caching) went to 02-context and are folded into its notes ([04-retrieval](../02-context-engineering/notes/04-retrieval.md)).

### Vendor guides

Vendor guides are the most up-to-date advice for each model family. Re-read them when you switch models.

**Anthropic**
- ★ [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) — the current single page
- [Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) — XML tags, examples, prefill, chaining
- [Interactive prompt engineering tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial) — nine chapters of exercises, in notebooks
- [Building effective agents](https://www.anthropic.com/research/building-effective-agents) — the workflow taxonomy in [06](notes/06-chaining-and-workflows.md#workflow-patterns-anthropics-taxonomy)
- [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — tool descriptions as prompts ([05](notes/05-tools-and-function-calling.md))

**OpenAI**
- [Prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Function calling](https://platform.openai.com/docs/guides/function-calling) · [Structured outputs](https://platform.openai.com/docs/guides/structured-outputs) ([04](notes/04-controlling-output.md#structured-output))
- [Reasoning best practices](https://platform.openai.com/docs/guides/reasoning-best-practices) ([07](notes/07-prompting-reasoning-models.md))

**Google**
- [Gemini prompting strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies) · [Gemini thinking](https://ai.google.dev/gemini-api/docs/thinking)
