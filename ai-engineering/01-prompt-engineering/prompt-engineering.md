---
origin: synthesis
sources:
  - notes/01–11 (this pillar)
  - https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
  - https://platform.openai.com/docs/guides/prompt-engineering
confidence: high
cleaned: 2026-10-28
---
# Prompt Engineering — One-Page Summary

> The rules of thumb from the topic notes on one page. Each line links to the note that explains it. Sources are in [references.md](references.md).

---

## Position in the stack

Prompt engineering is the **innermost layer**: context contains prompts. It covers the *instructions and examples themselves*: what you ask, how you structure it, and how you format the request. Once you're deciding *which documents, memory or tool outputs to include*, you're doing context engineering ([02-context](../02-context/README.md)).

| Prompt engineering | Context engineering |
|---|---|
| The instructions and examples themselves | What to *include* alongside them |
| Phrasing, structure, XML, output format | Which documents, memory, tool outputs and history to inject |
| Role, CoT, few-shot, sampling | Window composition, token budget, retrieval |

---

## The mental model

**A prompt is a document the model continues.** Every rule below follows from that ([01](notes/01-how-models-read-prompts.md)):

- It reads **tokens**, left to right, once. **Order matters**, and it can't look ahead or take back what it wrote.
- It produces **plausible** text, not true text. Hallucination is the same behavior as fluency.
- A chat model is a completion model continuing a **transcript**. The system and user roles are document structure, not a security boundary.

**Golden rule (Anthropic):** show your prompt to a colleague with no context. If they'd be confused, so will the model.

---

## Rules of thumb

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

- New to this: the [DAIR lecture](https://youtu.be/dOxUroR57xs), then notes [01](notes/01-how-models-read-prompts.md) → [03](notes/03-core-techniques.md).
- Building something now: the [vendor guides](references.md#vendor-guides) for your model, then [09 — evaluating prompts](notes/09-evaluating-prompts.md).
- Need an example prompt: the [prompt library](notes/prompt-library.md).
- Security: [10](notes/10-adversarial-prompting.md) and [prompt-injection.md](../../interviewing/guides/7-security-safety/prompt-injection.md).
