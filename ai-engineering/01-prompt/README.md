# 01 — Prompt Engineering

> Depth layer. Summary: [interviewing/guides/2-llm-fundamentals](../../interviewing/guides/2-llm-fundamentals/00-overview.md)
> Position in the stack: innermost — *context contains prompts*.
> Deep note: [prompt-engineering.md](prompt-engineering.md)

---

## What it is

Prompt engineering is the craft of writing instructions and examples that consistently elicit desired outputs from language models. It governs what you *ask* and how you *structure* the ask — not what you put in the context window alongside it (that's context engineering).

**Inherits the weaknesses of:** nothing — this is the innermost layer. But its failures propagate outward: a poorly engineered prompt degrades context utilization, loop reliability, and eval scores at every layer above it.

---

## Resource map

### Deep notes
- [prompt-engineering.md](prompt-engineering.md) — core techniques: system prompts, zero-shot/few-shot, chain-of-thought, structured output, XML structuring, prompt templates, prompt chaining, long-context patterns, and the prompt↔context boundary.
- [prompt-injection.md](prompt-injection.md) — the security facet: adversarial input manipulation.

### Interviewing guides
- [2-llm-fundamentals](../../interviewing/guides/2-llm-fundamentals/00-overview.md) — compressed summary for interview prep.
- [7-security-safety](../../interviewing/guides/7-security-safety/00-overview.md) — security angle on prompt injection.

### External references
- Anthropic interactive tutorial: https://github.com/anthropics/prompt-eng-interactive-tutorial
- Anthropic best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- OpenAI guide: https://platform.openai.com/docs/guides/prompt-engineering

### Next layer
→ [02-context/](../02-context/README.md) — context engineering assembles the window that delivers your prompts.
