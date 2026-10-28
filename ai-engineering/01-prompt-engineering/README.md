# 01 — Prompt Engineering

> Depth layer. Summary: [interviewing/guides/2-llm-fundamentals](../../interviewing/guides/2-llm-fundamentals/00-overview.md)
> Position in the stack: innermost — *context contains prompts*.
> One-page summary: [prompt-engineering.md](prompt-engineering.md) · All sources: [references.md](references.md)

---

## What it is

Prompt engineering is the craft of writing instructions and examples that consistently elicit desired outputs from language models. It governs what you *ask* and how you *structure* the ask — not what you put in the context window alongside it (that's context engineering).

**Inherits the weaknesses of:** nothing — this is the innermost layer. But its failures propagate outward: a poorly engineered prompt degrades context utilization, loop reliability, and eval scores at every layer above it.

---

## Layout

```
01-prompt-engineering/
├── README.md               ← you are here
├── prompt-engineering.md   ← one-page summary and rules of thumb
├── references.md           ← every source: books, vendor guides, papers, other readings
├── notes/                  ← the topic notes (read in order)
├── sources/                ← per-chapter notes on the book
├── reading/                ← PDFs: the book chapters and the DAIR lecture slides
└── notebooks/              ← runnable examples (mapped to notes in references.md)
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
  and `PDF p. N` quote citations. PDFs are in [reading/prompt-eng-for-llms/](reading/prompt-eng-for-llms/).
  Chapters 9 and 10 cross-link to the `04-loop` and `06-eval` pillars.

### Suggested path
1. Watch the [DAIR lecture](https://youtu.be/dOxUroR57xs) (1 h) for the overview.
2. Read notes 01–06 alongside book Ch 1–9, and run the matching notebooks.
3. Read notes 07–11, then use [references.md](references.md) to go deeper on whatever you'll build next.

### Interviewing guides
- [2-llm-fundamentals](../../interviewing/guides/2-llm-fundamentals/00-overview.md) — compressed summary for interview prep.
- [7-security-safety](../../interviewing/guides/7-security-safety/00-overview.md) — security angle on prompt injection.
    - [prompt-injection.md](../../interviewing/guides/7-security-safety/prompt-injection.md) — the security facet: adversarial input manipulation.

### Next layer
→ [02-context/](../02-context/README.md) — context engineering assembles the window that delivers your prompts.

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
