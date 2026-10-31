---
origin: book-condensed
sources:
  - "Phoenix & Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 1, 3, 10"
  - https://arxiv.org/abs/2201.11903
  - https://arxiv.org/abs/2205.11916
  - https://arxiv.org/abs/2210.03629
confidence: high
cleaned: 2026-10-31
---

# 3 — Prompting Fundamentals

> Five principles cover most of what makes a prompt work: give direction, specify format, provide examples, evaluate quality, divide labor. This note is the application-level summary; technique depth lives in [ai-engineering/01-prompt-engineering](../../../ai-engineering/01-prompt-engineering/README.md).

---

## Why prompts fail

Phoenix & Taylor open (O'Reilly ch. 1) by taking a one-line naive prompt and listing what is wrong with it. The list doubles as a checklist:

| Problem | What it looks like | Principle that fixes it |
|---|---|---|
| Vague direction | The model guesses style, audience and constraints | Give direction |
| Unformatted output | Prose when you needed a list you can parse | Specify format |
| No examples | The model invents its own idea of "good" | Provide examples |
| No evaluation | You judge from one lucky run | Evaluate quality |
| One giant task | Everything in one call, nothing checkable | Divide labor |

The reason any of this works is [note 01](01-how-llms-work.md): the prompt is the conditioning context for next-token prediction. Each principle makes the output you want a more likely continuation.

---

## The five principles

### 1. Give direction

Tell the model who it is writing as, for whom and under which rules.

- **Role or persona** ("You are a senior tax accountant…") shifts vocabulary and level of detail.
- **Insert the expert's rules.** If you know what a good answer must contain, say it; do not hope the model infers it.
- **Prewarming:** ask the model first for best practices on the task, then ask it to do the task following its own list. Cheap, and often better than a bare request.

Depth: [02 — Prompt anatomy](../../../ai-engineering/01-prompt-engineering/notes/02-prompt-anatomy.md), [03 — Core techniques](../../../ai-engineering/01-prompt-engineering/notes/03-core-techniques.md).

### 2. Specify format

Say exactly what shape the output takes: a numbered list of five, JSON with these keys, YAML, a table, a CSV with these headers.

- Machine-readable formats let code check the answer. If parsing fails, retry; that retry loop is the simplest reliability mechanism there is.
- Remove anything in the prompt that contradicts the format (an example in prose when you asked for JSON).
- Prefer the provider's structured-output or tool-call mechanism over "please return JSON" when you need a guarantee. See [note 06](06-calling-models-from-code.md) and [04 — Controlling output](../../../ai-engineering/01-prompt-engineering/notes/04-controlling-output.md).

### 3. Provide examples

| Shots | Behaviour |
|---|---|
| Zero-shot | Relies on direction alone; most creative, least predictable |
| One-shot | Fixes format quickly, but the model may copy the example's content too |
| Few-shot (3–5) | Reliable format and style. Beyond that, reliability keeps rising and variety falls |

The authors' advice: try direction first, then add examples. Examples are powerful and easy to over-fit to. Vary them so the model learns the pattern, not one instance.

### 4. Evaluate quality

"Blind prompting" means changing a prompt and eyeballing one output. Instead, run each variant several times and rate the outputs without knowing which prompt produced them. In the book's small test, a few-shot prompt earned three times the thumbs-up rate of the zero-shot version (0.6 vs 0.2). That is a toy sample, but it is the right method.

What to measure, once you have more than a handful of cases:

| Criterion | How |
|---|---|
| Cost, latency, number of calls | Logged per run |
| Correctness | Exact match or classification accuracy against labels |
| Faithfulness / hallucination | Check claims against the provided context |
| Safety and refusals | Rate of harmful completions and of unnecessary refusals |
| Similarity to a reference | BLEU/ROUGE, or embedding distance |
| Preference between variants | Pairwise comparison by humans or an LLM judge, ranked with Elo |

Depth: [09 — Evaluating prompts](../../../ai-engineering/01-prompt-engineering/notes/09-evaluating-prompts.md) and [ai-engineering/06-eval](../../../ai-engineering/06-eval/README.md).

### 5. Divide labor

Split a task into steps, each with its own prompt and its own check.

- **Chaining:** the output of one call is the input of the next (outline → draft → edit).
- **Self-evaluation:** a second call grades or critiques the first.
- **Reasoning before answering:** asking for step-by-step work improves multi-step problems. Chain-of-thought exemplars took PaLM 540B to state of the art on GSM8K ([arXiv:2201.11903](https://arxiv.org/abs/2201.11903), Wei et al., 2022). Even the zero-shot phrase "Let's think step by step" lifted text-davinci-002 from 17.7% to 78.7% on MultiArith ([arXiv:2205.11916](https://arxiv.org/abs/2205.11916), Kojima et al., 2022). Modern reasoning models do this internally; see [07 — Prompting reasoning models](../../../ai-engineering/01-prompt-engineering/notes/07-prompting-reasoning-models.md).
- **Meta-prompting:** have a model write or improve the prompt.
- **Reason + act:** interleave thoughts with tool calls (ReAct, [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)). This is where prompting turns into agents ([03-agentic-foundations](../../03-agentic-foundations/README.md)).

Depth: [06 — Chaining and workflows](../../../ai-engineering/01-prompt-engineering/notes/06-chaining-and-workflows.md).

---

## Standard practices

O'Reilly ch. 3 is a catalogue of everyday text tasks. The recurring patterns:

| Task | Practice |
|---|---|
| Lists and hierarchical lists | Fix the count, the bullet style and "no commentary before or after". For nested lists, define the levels explicitly and parse with code, not regex, once nesting gets deep |
| JSON / YAML | Give the schema and an example. YAML avoids quote escaping and reads better; filter the payload in code and handle invalid output with a retry |
| Ask for context | Let the model say "I need more information about X" by default, instead of guessing |
| Style unbundling | Extract a text's features (tone, length, vocabulary, structure) into a list, then generate new content against that list. Gives brand consistency without copying |
| Explain like I'm five, translation | The model's language skills are general; ask for a reading level or a target language directly |
| Summarization | Say the audience and length; for long input, chunk first |
| Chunking | Split by sentence, paragraph, topic, length or tokens (tiktoken). Overlapping sliding windows keep context across boundaries. Do not chunk short or single-topic documents |
| Sentiment and classification | Give the labels, examples per label and a rule for mixed cases |
| Least to most | Ask for the plan, then each part, then the tests, building up a larger artifact in steps |
| Role prompting | Assign the expert persona that would answer best |

Chapter 10 of the book assembles these into a full application (an AI blog writer: topic research, an expert-interview step that generates questions, outline, draft with retrieval, writing-style pass, title optimization, images and a Gradio UI). It is a good model of "divide labor" at system scale.

---

## Where to go deeper

| Need | Go to |
|---|---|
| How the model parses a prompt; system vs user turns | [01 — How models read prompts](../../../ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts.md) |
| The full technique set with examples | [03 — Core techniques](../../../ai-engineering/01-prompt-engineering/notes/03-core-techniques.md) |
| Tool use and function calling | [05 — Tools and function calling](../../../ai-engineering/01-prompt-engineering/notes/05-tools-and-function-calling.md) |
| Automatic prompt optimization (DSPy and friends) | [08 — Prompt optimization](../../../ai-engineering/01-prompt-engineering/notes/08-prompt-optimization.md) |
| Prompt injection and jailbreaks | [10 — Adversarial prompting](../../../ai-engineering/01-prompt-engineering/notes/10-adversarial-prompting.md) |
| Copy-paste templates | [Prompt library](../../../ai-engineering/01-prompt-engineering/notes/prompt-library.md) |

---

**Next:** [04 — LangChain basics](04-langchain-basics.md) turns these principles into reusable templates and chains.
