---
origin: book
source: "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly) — index"
confidence: high
cleaned: 2026-07-29
---

# Prompt Engineering for LLMs — chapter notes index

One note per chapter of *Prompt Engineering for LLMs* (John Berryman & Albert Ziegler,
O'Reilly, 2024). Page citations use each chapter PDF's own page numbering (`PDF p. N`) —
the source PDFs are O'Reilly web exports with no printed book page numbers. Figures
referenced as `images/fig-*.png` are screenshots of the book's figures.

## Part I — Foundations

- [Ch 1 — Introduction](01-introduction.md) — LLMs are document completers, not
  answerers; prompt engineering is arranging a document whose most plausible
  continuation is the answer you want.
- [Ch 2 — Understanding LLMs](02-understanding-llms.md) — how next-token prediction,
  tokenization, and attention shape model behavior, and the failure modes (hallucination,
  repetition traps) that follow directly from the mechanics.
- [Ch 3 — Moving to Chat](03-moving-to-chat.md) — RLHF (SFT → reward model → PPO) turns
  base models into HHH assistants; ChatML's reserved tokens give structural
  injection-resistance; chat trades raw range for steerability.
- [Ch 4 — Designing LLM Applications](04-designing-llm-applications.md) — the LLM
  application loop (user problem → prompt → completion → parsed result) and the Little
  Red Riding Hood principle: stay on well-trodden training-data paths.

## Part II — Core techniques

- [Ch 5 — Prompt Content](05-prompt-content.md) — what goes *in* the prompt: static vs.
  dynamic content, sourcing context, and the clarity/precision rules for instructions.
- [Ch 6 — Assembling the Prompt](06-assembling-the-prompt.md) — prompt anatomy
  (introduction → context → refocus → transition), the Valley of Meh, document-type
  archetypes (conversation / report / structured), and snippet formatting rules.
- [Ch 7 — Taming the Model](07-taming-the-model.md) — controlling the completion:
  preamble/fluff management, stop sequences, logprobs for confidence and classification,
  model selection, and fine-tuning as prompt engineering by other means.
- [Ch 8 — Conversational Agency](08-conversational-agency.md) — building an agent from
  the conversation loop: tool calls, chain-of-thought and plan-and-solve reasoning, and a
  worked conversational-agent design.

## Part III — Applications

- [Ch 9 — LLM Workflows](09-llm-workflows.md) — decomposing tasks into multi-step
  workflows; the generality-vs-strength trade-off between one big prompt and many small
  ones. (Deep dive pillar: `04-loop`.)
- [Ch 10 — Evaluating LLM Applications](10-evaluating-llm-applications.md) — offline
  evals (the tech tree from asserts to model-graded) and online measurement; evaluation
  is the engine of iteration. (Deep dive pillar: `06-eval`.)
- [Ch 11 — Looking Ahead](11-looking-ahead.md) — what stays true as models improve: the
  document-completion frame, context economics, and the enduring role of the prompt
  engineer.
