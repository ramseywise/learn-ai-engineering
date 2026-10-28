---
origin: synthesis
sources:
  - notes/ (all eleven topic notes)
  - Prompt-Engineering-Guide (DAIR.AI) — pages absorbed into notes/
  - ../SOURCES.md, ../readings/
cleaned: 2026-10-28
---
# References — Prompt Engineering

> Every source behind the [notes](README.md#layout), in one place. Local files come first, followed by vendor docs and papers grouped to match the notes. arXiv IDs resolve at `https://arxiv.org/abs/<id>`. **★** marks the one or two to read first in each section.

---

## Primary sources (in this pillar)

| Source | Where | Use it for |
|---|---|---|
| ★ Berryman & Ziegler, *Prompt Engineering for LLMs* (O'Reilly 2024) | PDFs: [sources/prompt-eng-for-llms/reading/](sources/prompt-eng-for-llms/reading/) · chapter notes: [sources/prompt-eng-for-llms/](sources/prompt-eng-for-llms/00-overview.md) | The backbone of notes 01, 02, 04, 05, 06 and 09. Written by two of the original GitHub Copilot engineers |
| DAIR.AI *Prompt Engineering Guide* | [promptingguide.ai](https://www.promptingguide.ai/) · [GitHub](https://github.com/dair-ai/Prompt-Engineering-Guide) | The technique catalog (notes 03, 08, 10, 11). Its pages are absorbed into the notes, so check the live site for new additions |
| DAIR lecture (Elvis Saravia) | [video](https://youtu.be/dOxUroR57xs) · [slides (PDF)](notes/dair-prompt-engineering-lecture.pdf) · [figures](sources/dair-prompt-engineering-guide/images/) | A one-hour overview; a good first pass |
| Notebooks | [notebooks/](notebooks/) | Runnable versions of the techniques (see the table below) |

| Notebook | Pairs with |
|---|---|
| [pe-lecture.ipynb](notebooks/pe-lecture.ipynb), [pe-chatgpt-intro.ipynb](notebooks/pe-chatgpt-intro.ipynb), [pe-litellm-intro.ipynb](notebooks/pe-litellm-intro.ipynb) | [02 — anatomy](notes/02-prompt-anatomy.md), [03 — core techniques](notes/03-core-techniques.md) |
| [pe-pal.ipynb](notebooks/pe-pal.ipynb), [react.ipynb](notebooks/react.ipynb) | [03 — PAL, ReAct](notes/03-core-techniques.md#pal--program-aided-language-models) |
| [pe-function-calling.ipynb](notebooks/pe-function-calling.ipynb) | [05 — tools](notes/05-tools-and-function-calling.md) |
| [pe-chatgpt-langchain.ipynb](notebooks/pe-chatgpt-langchain.ipynb), [pe-rag.ipynb](notebooks/pe-rag.ipynb) | [06 — chaining](notes/06-chaining-and-workflows.md) |
| [pe-chatgpt-adversarial.ipynb](notebooks/pe-chatgpt-adversarial.ipynb) | [10 — adversarial](notes/10-adversarial-prompting.md) |
| [pe-code-llama.ipynb](notebooks/pe-code-llama.ipynb), [pe-mixtral-introduction.ipynb](notebooks/pe-mixtral-introduction.ipynb) | [11 — code](notes/11-applications.md#code), open-weight models |
| [gemini-context-caching.ipynb](notebooks/gemini-context-caching.ipynb) | [02-context](../02-context/README.md) |

---

## Elsewhere in this repo

These are books and papers already on disk that cover prompting from another angle.

| Reading | Where | Why |
|---|---|---|
| ★ Huyen, *AI Engineering* (O'Reilly 2025) — **Ch 5, Prompt Engineering** | [readings/ai_engineering/ai engineer/](<../readings/ai_engineering/ai engineer/5. Prompt Engineering _ AI Engineering.pdf>) | The best single chapter on prompting *as engineering*: in-context learning, prompt attacks and defenses, and prompt versioning. Ch 3–4 (evaluation) go with [09](notes/09-evaluating-prompts.md) |
| Phoenix & Taylor, *Prompt Engineering for Generative AI* (O'Reilly 2024) | [generative-ai/01-llm-fundamentals/readings/](<../../generative-ai/01-llm-fundamentals/readings/>) | The "five principles of prompting" (Ch 1), text-generation practice (Ch 3) and LangChain chaining (Ch 4). Ch 7–9 cover image prompting |
| *Building Applications with AI Agents* — Ch 4 (Tool Use), Ch 12 (Protecting Agentic Systems) | [readings/ai_engineering/ai_agent_applications/](<../readings/ai_engineering/ai_agent_applications/>) | Goes deeper than [05](notes/05-tools-and-function-calling.md) and [10](notes/10-adversarial-prompting.md) |
| Wei et al., *Chain-of-Thought Prompting* (2201.11903) | [readings/general/2201.11903v6.pdf](../readings/general/2201.11903v6.pdf) | The CoT paper ([03](notes/03-core-techniques.md#chain-of-thought)) |
| Ouyang et al., *InstructGPT* (2203.02155) | [readings/general/2203.02155v1.pdf](../readings/general/2203.02155v1.pdf) | Why chat models follow instructions ([01](notes/01-how-models-read-prompts.md)) |
| Bai et al., *Constitutional AI* (2212.08073) | [readings/general/2212.08073v1.pdf](../readings/general/2212.08073v1.pdf) | Principles-as-prompts; model self-critique |
| Manakul et al., *SelfCheckGPT* (2303.08896) | [readings/general/2303.08896v3.pdf](../readings/general/2303.08896v3.pdf) | Sampling-consistency hallucination checks ([10 — factuality](notes/10-adversarial-prompting.md#factuality)) |
| Zhao et al., *A Survey of LLMs* (2303.18223) | [readings/general/2303.18223v16.pdf](../readings/general/2303.18223v16.pdf) | Its section on prompting and in-context learning |

---

## Vendor guides

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

---

## Technique papers

These are the papers behind [03 — core techniques](notes/03-core-techniques.md), in the order the note covers them.

| Technique | Paper | arXiv |
|---|---|---|
| Few-shot / in-context learning | Brown et al., *Language Models are Few-Shot Learners* (GPT-3) | 2005.14165 |
| What makes few-shot work | ★ Min et al., *Rethinking the Role of Demonstrations* | 2202.12837 |
| Instruction tuning (why zero-shot works) | Wei et al., *Finetuned Language Models Are Zero-Shot Learners* (FLAN) | 2109.01652 |
| Chain-of-thought | ★ Wei et al. | 2201.11903 |
| Zero-shot CoT ("Let's think step by step") | Kojima et al. | 2205.11916 |
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

**Background:** Kaplan et al., *Scaling Laws* (2001.08361) · Christiano et al., *RLHF from human preferences* (1706.03741) · Bubeck et al., *Sparks of AGI* (2303.12712) — the source of the TiKZ unicorn and other probes in the [prompt library](notes/prompt-library.md).

---

## Prompt optimization

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

---

## Reasoning models

For [07](notes/07-prompting-reasoning-models.md). This area moves fastest, so check the vendor guides above first.

- ★ DAIR *Reasoning LLMs Guide* — [promptingguide.ai/guides/reasoning-llms](https://www.promptingguide.ai/guides/reasoning-llms)
- DeepSeek-AI, *DeepSeek-R1: Incentivizing Reasoning Capability via RL* — 2501.12948
- Raschka, [*Understanding Reasoning LLMs*](https://magazine.sebastianraschka.com/p/understanding-reasoning-llms) — an overview of how reasoning models are trained
- *The Pitfalls of Reasoning for Instruction Following* — 2505.11423 (explicit CoT hurts instruction-following)
- Anthropic, *Reasoning Models Don't Always Say What They Think* — 2505.05410 (CoT faithfulness)
- Shojaee et al., [*The Illusion of Thinking*](https://machinelearning.apple.com/research/illusion-of-thinking) (Apple, 2025) — collapse on harder puzzles; read it with the rebuttals it prompted

---

## Evaluation

For [09](notes/09-evaluating-prompts.md). Deeper material is in [06-eval](../06-eval/README.md).

- ★ Book Ch 10 — [sources/prompt-eng-for-llms/10-evaluating-llm-applications.md](sources/prompt-eng-for-llms/10-evaluating-llm-applications.md)
- Clavié et al., *Large Language Models in the Workplace* — 2303.07142 (the case-study table)
- Huyen, *AI Engineering* Ch 3–4 — [readings/ai_engineering/ai engineer/](<../readings/ai_engineering/ai engineer/>)
- Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* — 2306.05685 (judge biases: position, verbosity, self-preference)
- Husain, [*Your AI Product Needs Evals*](https://hamel.dev/blog/posts/evals/) — the practitioner's case for building the eval first

---

## Safety and adversarial

For [10](notes/10-adversarial-prompting.md). For interview depth, see [interviewing/7-security-safety/prompt-injection.md](../../interviewing/guides/7-security-safety/prompt-injection.md).

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

---

## Applications

For [11](notes/11-applications.md).

| Topic | Paper | arXiv |
|---|---|---|
| Combinatorial seeding | Eldan & Li, *TinyStories* | 2305.07759 |
| Textbook-quality synthetic data | Gunasekar et al., *Textbooks Are All You Need* (phi-1) | 2306.11644 |
| Synthetic retrieval queries | Dai et al., *Promptagator* | 2209.11755 |
| Code generation and HumanEval | Chen et al., *Evaluating LLMs Trained on Code* (Codex) | 2107.03374 |
| Tool-use fine-tuning | Patil et al., *Gorilla* · Qin et al., *ToolLLM* | 2305.15334 · 2307.16789 |

---

## Other readings

These are broader or more opinionated pieces, good once the notes feel familiar.

- ★ Schulhoff et al., *The Prompt Report: A Systematic Survey of Prompting Techniques* — 2406.06608. A taxonomy of 58 text techniques, with terminology; the best "did I miss anything?" check
- Weng, [*Prompt Engineering*](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/) (2023) — a dense, research-oriented survey
- Yan, [*Prompting Fundamentals and How to Apply Them Effectively*](https://eugeneyan.com/writing/prompting/) — a practitioner's view with production examples
- [Learn Prompting](https://learnprompting.org) — a beginner-friendly open course, an alternative to DAIR
- Context engineering — the successor framing (Karpathy, LangChain, Schmid, Lance Martin). Collected in [02-context](../02-context/README.md)

---

→ Back to [the pillar README](README.md)
