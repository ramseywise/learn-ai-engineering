---
origin: web-authored
sources:
  - https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
  - https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
  - https://platform.openai.com/docs/guides/prompt-engineering
confidence: high
cleaned: 2026-07-21
---
# Prompt Engineering

## Position in the stack

Prompt engineering is the **innermost layer**: context contains prompts. Every assembled context window ultimately delivers one or more prompts to the model; the quality of those prompts determines what the model does with the surrounding context. Where prompt engineering ends and context engineering begins: once you're deciding *what documents, memory chunks, or tool outputs to include* alongside the instructions, you're in context engineering territory. Prompt engineering governs the *instructions and examples themselves* — what you ask, how you structure it, and how you format the request.

---

## Core principle

**Be clear and direct.** Claude (and GPT models) respond to explicit instructions. Vague prompts produce vague outputs. Think of the model as a capable but context-free new employee: the more precisely you explain the task, constraints, and desired output, the better the result.

**Golden rule (Anthropic):** Show your prompt to a colleague with minimal context. If they'd be confused, the model will be too.

---

## Techniques

### 1. System prompts and role setting

The system prompt is the highest-authority instruction layer. It sets the model's role, tone, behavioral constraints, and task framing before any user message arrives. A single focused sentence in the system prompt is often more effective than extensive inline instructions:

```
You are a helpful coding assistant specializing in Python.
```

**Authority hierarchy (OpenAI model):** developer role > user role > instructions parameter. Foundational directives (tone, goals, format) take precedence over user queries when conflicts arise.

### 2. Zero-shot vs. few-shot prompting

- **Zero-shot**: instruct the model with no examples; relies on the model's general knowledge.
- **Few-shot (multishot)**: provide 3–5 worked examples before the actual task. Examples are one of the most reliable ways to steer output format, tone, and structure.

Few-shot best practices (Anthropic):
- **Relevant** — mirror your actual use case.
- **Diverse** — cover edge cases; vary enough that the model doesn't pick up unintended patterns.
- **Structured** — wrap examples in `<example>` tags so the model distinguishes them from instructions.

### 3. Chain-of-thought (CoT)

Ask the model to reason step-by-step before producing a final answer. This is especially effective for multi-step reasoning, math, or planning tasks:

```
Think through this step by step before giving your final answer.
```

For reasoning models (Claude Opus, o1/o3 family): they perform internal CoT automatically; explicit step-by-step prompts may be redundant but remain valid. For standard models, CoT prompting materially improves accuracy on complex tasks.

### 4. Structured output and XML structuring

**Structured output**: request JSON (or another schema) to get parseable, reliable results. Pair with schema validation in your harness. Example:

```
Return your answer as JSON with keys: "summary", "confidence", "next_steps".
```

**XML structuring within the prompt**: wrap distinct sections of a complex prompt in XML tags to reduce misinterpretation:

```xml
<instructions>Summarize the document below.</instructions>
<context>{{DOCUMENT}}</context>
<constraints>Max 3 sentences. Plain text only.</constraints>
```

Best practices: consistent, descriptive tag names; nest tags for hierarchical content (`<documents>` > `<document index="n">` > `<document_content>`).

### 5. Prompt templates and variables

Separate the *fixed* instruction skeleton from *variable* content. Use `{{PLACEHOLDER}}` notation (or equivalent) so the same template can be reused across inputs:

```
You are a data analyst. Answer this question about the dataset:
Question: {{USER_QUESTION}}
Dataset: {{DATASET_EXCERPT}}
```

The `instructions` API parameter (OpenAI) serves a similar role: high-level behavioral guidance that overrides input-level prompts, useful for maintaining consistent personality across multi-turn conversations.

### 6. Add context and motivation

Explaining *why* a constraint exists helps the model generalize correctly:

```
Never use ellipses — this response will be read aloud by a text-to-speech engine that
cannot pronounce them.
```

vs. `NEVER use ellipses` (abrupt; model may interpret narrowly).

### 7. Long-context prompting

When working with large documents (20k+ tokens):
- **Put longform data at the top**, above your query and examples — Anthropic tests show up to 30% quality improvement when the query appears at the end.
- **Structure multi-document inputs** with XML tags (`<document index="1">`, `<source>`, `<document_content>`).
- **Ground responses in quotes**: ask the model to extract relevant quotes before answering, keeping focus on the relevant content.

### 8. Prompt chaining

Break complex multi-step tasks into a sequence of smaller prompts where the output of one becomes the input of the next. Each prompt is simpler, more testable, and easier to debug. This is the gateway to harness engineering — when prompt chains become stateful and conditional, you've crossed into loop/harness territory.

### 9. Output format control

- Tell the model what to do rather than what *not* to do: "Respond in flowing prose paragraphs" > "Do not use markdown".
- Use XML format indicators: `"Write your analysis in <analysis> tags."`.
- Match your prompt style to the desired output style — markdown-heavy prompts tend to produce markdown-heavy responses.

---

## Prompt ↔ context boundary

| Prompt engineering | Context engineering |
|---|---|
| The instructions and examples themselves | What to *include* alongside the instructions |
| How you phrase the task, format requests, structure XML | Which documents, memory chunks, tool outputs, conversation history to inject |
| Role setting, CoT, few-shot, output format | Context window composition, token budget, retrieval strategy |

Once you are making decisions about *what* is in the window (not *how* to phrase what's already there), you are in context engineering.

---

## Security facet

Prompt injection — manipulating model behavior via adversarial input embedded in user data — is the primary security concern for systems with external inputs. See [`prompt-injection.md`](prompt-injection.md) and pillar [`7-security-safety`](../guides/7-security-safety/00-overview.md) for the defense patterns.

---

## Resources

- Pillar guide: [`2-llm-fundamentals`](../guides/2-llm-fundamentals/00-overview.md)
- Security facet: [`prompt-injection.md`](prompt-injection.md)
- Anthropic interactive tutorial: https://github.com/anthropics/prompt-eng-interactive-tutorial
- Anthropic best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- OpenAI guide: https://platform.openai.com/docs/guides/prompt-engineering
