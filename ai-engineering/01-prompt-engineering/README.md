# 01 — Prompt Engineering

> Depth layer. Summary: [interviewing/guides/2-llm-fundamentals](../../interviewing/guides/2-llm-fundamentals/00-overview.md)
> Position in the stack: innermost — *context contains prompts*.
> Jump to: [Rules of thumb](#rules-of-thumb) · [Topic notes](#topic-notes-notes) · [References](#references)

---

## What it is

Prompt engineering is the craft of writing instructions and examples that consistently elicit desired outputs from language models. It governs what you *ask* and how you *structure* the ask — not what you put in the context window alongside it. Once you're deciding *which documents, memory or tool outputs to include*, you're doing context engineering ([02-context](../02-context/README.md)).

| Prompt engineering | Context engineering |
|---|---|
| The instructions and examples themselves | What to *include* alongside them |
| Phrasing, structure, XML, output format | Which documents, memory, tool outputs and history to inject |
| Role, CoT, few-shot, sampling | Window composition, token budget, retrieval |

**Inherits the weaknesses of:** nothing — this is the innermost layer. But its failures propagate outward: a poorly engineered prompt degrades context utilization, loop reliability, and eval scores at every layer above it.

---

## The mental model

**A prompt is a document the model continues.** Every rule below follows from that ([01](notes/01-how-models-read-prompts.md)):

- It reads **tokens**, left to right, once. **Order matters**, and it can't look ahead or take back what it wrote.
- It produces **plausible** text, not true text. Hallucination is the same behavior as fluency.
- A chat model is a completion model continuing a **transcript**. The system and user roles are document structure, not a security boundary.

**Golden rule (Anthropic):** show your prompt to a colleague with no context. If they'd be confused, so will the model.

---

## Rules of thumb

The rules from the topic notes on one page. Each group links to the note that explains it.

**Writing the prompt** ([02](notes/02-prompt-anatomy.md))
- Be clear, direct and specific. Say *what to do* rather than what not to do, and **explain why** a constraint exists.
- Separate instructions from data with **XML tags or delimiters**, and use consistent tag names.
- **Long content first, question last.** Ask the model to quote the relevant parts before it answers.
- Pick a **familiar document type** (email, report, transcript) that the model has seen completed many times.
- Version the **template**, not the rendered prompt.

**Choosing a technique** ([03](notes/03-core-techniques.md))
- Start with **zero-shot**. Add **few-shot** examples (diverse, consistent, shuffled) for format or style.
- Use **CoT** for multi-step reasoning on standard models. Use **self-consistency** when you can afford several samples.
- Use **PAL** for arithmetic, **ReAct** for tool use, and **Reflexion** when there's a checkable signal to retry against.

**Controlling output** ([04](notes/04-controlling-output.md))
- Lower the temperature for factual or parseable output. Set stop sequences.
- Climb the structured-output ladder only as far as you need: ask → show → fence → prefill → constrained decoding → tool schema.

**Tools, chains and models** ([05](notes/05-tools-and-function-calling.md), [06](notes/06-chaining-and-workflows.md), [07](notes/07-prompting-reasoning-models.md))
- Tool names and descriptions *are* prompts. **Gate side effects in code**, not in the prompt.
- If one prompt does too much, **split it into a chain**. Use a workflow before an agent.
- With **reasoning models**, state the goal rather than the steps, drop "think step by step", and tune *effort* rather than wording.

**Shipping** ([08](notes/08-prompt-optimization.md), [09](notes/09-evaluating-prompts.md), [10](notes/10-adversarial-prompting.md))
- **Build the eval before you tune the prompt.** Change one thing at a time and re-score.
- For LLM judges: **specific, ordinal, multi-aspect** questions, and never self-grading.
- **Assume the system prompt will leak, and assume injection will happen.** Least privilege, human approval in code, and quarantined models are the defenses that hold.

---

## Where to start

- **New to this:** watch the [DAIR lecture](https://youtu.be/dOxUroR57xs) (1 h), read notes 01–06 alongside book Ch 1–9 and run the matching [notebooks](#primary-sources-in-this-pillar), then read notes 07–11.
- **Building something now:** the [vendor guides](#vendor-guides) for your model, then [09 — evaluating prompts](notes/09-evaluating-prompts.md).
- **Need an example prompt:** the [prompt library](notes/prompt-library.md).
- **Security:** [10](notes/10-adversarial-prompting.md) and [prompt-injection.md](../../interviewing/guides/7-security-safety/prompt-injection.md).

---

## Layout

```
01-prompt-engineering/
├── README.md               ← you are here: summary, rules of thumb, all references
├── notes/                  ← the topic notes (read in order), plus the DAIR lecture slides
├── sources/
│   ├── prompt-eng-for-llms/  ← per-chapter book notes, figures (images/), chapter PDFs (reading/)
│   └── images/               ← the DAIR guide's figures
└── notebooks/              ← runnable examples (mapped to notes under References)
```

### Topic notes ([notes/](notes/))

**Foundations**
1. [How models read prompts](notes/01-how-models-read-prompts.md) — tokens, autoregression, attention order, truth bias, and chat as a transcript.
2. [Prompt anatomy](notes/02-prompt-anatomy.md) — the elements, writing instructions, ordering, document types, templates.

**Techniques**

3. [Core techniques](notes/03-core-techniques.md) — zero/few-shot, CoT, self-consistency, ToT, PAL, ReAct, Reflexion and more, with a "which technique when" table.
4. [Controlling output](notes/04-controlling-output.md) — sampling, stop sequences, the structured-output ladder, logprobs, fine-tuning.
5. [Tools and function calling](notes/05-tools-and-function-calling.md) — the loop, writing tool definitions, safety gates, debugging.
6. [Chaining and workflows](notes/06-chaining-and-workflows.md) — prompt chains, topologies, Anthropic's workflow patterns, workflows vs. agents.
7. [Prompting reasoning models](notes/07-prompting-reasoning-models.md) — what changes, effort settings, failure modes, deep-research agents.

**Practice**

8. [Prompt optimization](notes/08-prompt-optimization.md) — prompts as versioned artifacts, APE/OPRO, meta-prompting, DSPy.
9. [Evaluating prompts](notes/09-evaluating-prompts.md) — the offline tech tree, LLM-as-judge (SOMA), online metrics, a case study.
10. [Adversarial prompting](notes/10-adversarial-prompting.md) — injection, leaking, jailbreaks, layered defenses, bias, factuality.
11. [Applications](notes/11-applications.md) — synthetic data, code, images and multimodal prompts.

**Reference:** [prompt-library.md](notes/prompt-library.md) — copyable example prompts by task.

### Book notes — *Prompt Engineering for LLMs* (Berryman & Ziegler, O'Reilly 2024)
- [sources/prompt-eng-for-llms/00-overview.md](sources/prompt-eng-for-llms/00-overview.md) — index of the
  11 per-chapter notes (`01-introduction` … `11-looking-ahead`), with figure screenshots
  and `PDF p. N` quote citations. PDFs are in [sources/prompt-eng-for-llms/reading/](sources/prompt-eng-for-llms/reading/).
  Chapters 9 and 10 cross-link to the `04-loop` and `06-eval` pillars.

### Interviewing guides
- [2-llm-fundamentals](../../interviewing/guides/2-llm-fundamentals/00-overview.md) — compressed summary for interview prep.
- [7-security-safety](../../interviewing/guides/7-security-safety/00-overview.md) — security angle on prompt injection.
    - [prompt-injection.md](../../interviewing/guides/7-security-safety/prompt-injection.md) — the security facet: adversarial input manipulation.

### Next layer
→ [02-context/](../02-context/README.md) — context engineering assembles the window that delivers your prompts.

---

## References

Every source behind the notes, in one place. Local files come first, followed by vendor docs and papers grouped to match the notes. arXiv IDs resolve at `https://arxiv.org/abs/<id>`. **★** marks the one or two to read first in each section.

### Primary sources (in this pillar)

| Source | Where | Use it for |
|---|---|---|
| ★ Berryman & Ziegler, *Prompt Engineering for LLMs* (O'Reilly 2024) | PDFs: [sources/prompt-eng-for-llms/reading/](sources/prompt-eng-for-llms/reading/) · chapter notes: [sources/prompt-eng-for-llms/](sources/prompt-eng-for-llms/00-overview.md) | The backbone of notes 01, 02, 04, 05, 06 and 09. Written by two of the original GitHub Copilot engineers |
| DAIR.AI *Prompt Engineering Guide* | [promptingguide.ai](https://www.promptingguide.ai/) · [GitHub](https://github.com/dair-ai/Prompt-Engineering-Guide) | The technique catalog (notes 03, 08, 10, 11). Its pages are absorbed into the notes, so check the live site for new additions |
| DAIR lecture (Elvis Saravia) | [video](https://youtu.be/dOxUroR57xs) · [slides (PDF)](notes/dair-prompt-engineering-lecture.pdf) · [figures](sources/images/) | A one-hour overview; a good first pass |
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

### Elsewhere in this repo

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

### Technique papers

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

### Reasoning models

For [07](notes/07-prompting-reasoning-models.md). This area moves fastest, so check the vendor guides above first.

- ★ DAIR *Reasoning LLMs Guide* — [promptingguide.ai/guides/reasoning-llms](https://www.promptingguide.ai/guides/reasoning-llms)
- DeepSeek-AI, *DeepSeek-R1: Incentivizing Reasoning Capability via RL* — 2501.12948
- Raschka, [*Understanding Reasoning LLMs*](https://magazine.sebastianraschka.com/p/understanding-reasoning-llms) — an overview of how reasoning models are trained
- *The Pitfalls of Reasoning for Instruction Following* — 2505.11423 (explicit CoT hurts instruction-following)
- Anthropic, *Reasoning Models Don't Always Say What They Think* — 2505.05410 (CoT faithfulness)
- Shojaee et al., [*The Illusion of Thinking*](https://machinelearning.apple.com/research/illusion-of-thinking) (Apple, 2025) — collapse on harder puzzles; read it with the rebuttals it prompted

### Evaluation

For [09](notes/09-evaluating-prompts.md). Deeper material is in [06-eval](../06-eval/README.md).

- ★ Book Ch 10 — [sources/prompt-eng-for-llms/10-evaluating-llm-applications.md](sources/prompt-eng-for-llms/10-evaluating-llm-applications.md)
- Clavié et al., *Large Language Models in the Workplace* — 2303.07142 (the case-study table)
- Huyen, *AI Engineering* Ch 3–4 — [readings/ai_engineering/ai engineer/](<../readings/ai_engineering/ai engineer/>)
- Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* — 2306.05685 (judge biases: position, verbosity, self-preference)
- Husain, [*Your AI Product Needs Evals*](https://hamel.dev/blog/posts/evals/) — the practitioner's case for building the eval first

### Safety and adversarial

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

### Applications

For [11](notes/11-applications.md).

| Topic | Paper | arXiv |
|---|---|---|
| Combinatorial seeding | Eldan & Li, *TinyStories* | 2305.07759 |
| Textbook-quality synthetic data | Gunasekar et al., *Textbooks Are All You Need* (phi-1) | 2306.11644 |
| Synthetic retrieval queries | Dai et al., *Promptagator* | 2209.11755 |
| Code generation and HumanEval | Chen et al., *Evaluating LLMs Trained on Code* (Codex) | 2107.03374 |
| Tool-use fine-tuning | Patil et al., *Gorilla* · Qin et al., *ToolLLM* | 2305.15334 · 2307.16789 |

### Other readings

These are broader or more opinionated pieces, good once the notes feel familiar.

- ★ Schulhoff et al., *The Prompt Report: A Systematic Survey of Prompting Techniques* — 2406.06608. A taxonomy of 58 text techniques, with terminology; the best "did I miss anything?" check
- Weng, [*Prompt Engineering*](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/) (2023) — a dense, research-oriented survey
- Yan, [*Prompting Fundamentals and How to Apply Them Effectively*](https://eugeneyan.com/writing/prompting/) — a practitioner's view with production examples
- [Learn Prompting](https://learnprompting.org) — a beginner-friendly open course, an alternative to DAIR
- Context engineering — the successor framing (Karpathy, LangChain, Schmid, Lance Martin). Collected in [02-context](../02-context/README.md)

---

## Working References

Claude Code convention references that map to this pillar. These files live at `~/.claude/refs/` and can be consulted in any Claude Code session.

### `agent-safety.md`
Conventions for what the agent cannot do and where that is enforced. Directly relevant to prompt injection defense and the instruction hierarchy that governs how prompts interact with system-level constraints.

Key topics for this pillar:
- Five protection layers — Layer 1 (pre-input sanitization) and Layer 4 (post-generate output check) are the prompt-layer guards
- Prompt injection: structural delimiting of untrusted content, deny-list patterns, instruction hierarchy (system prompt > developer context > user input)
- Credential and secret custody — rules for what must never appear in a prompt context window
- Write-operation confirm gate — two-phase pattern for irreversible actions triggered by prompt instructions
