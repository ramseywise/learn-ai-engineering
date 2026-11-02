# 01 — Prompt Engineering

> Depth layer. Summary: [interviewing/guides/2-llm-fundamentals](../../practice/interviewing/guides/2-llm-fundamentals/00-overview.md)
> Position in the stack: innermost — *context contains prompts*.
> Jump to: [Rules of thumb](#rules-of-thumb) · [Topic notes](#topic-notes-notes) · [References](#references)

---

## What it is

Prompt engineering is the craft of writing instructions and examples that consistently elicit desired outputs from language models. It governs what you *ask* and how you *structure* the ask — not what you put in the context window alongside it. Once you're deciding *which documents, memory or tool outputs to include*, you're doing context engineering ([02-context](../02-context-engineering/README.md)).

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

- **Lecture deck:** [slides/prompt-engineering.pptx](slides/prompt-engineering.pptx) — the notes as a 4-part talk (source: [slides/deck.yaml](slides/deck.yaml); rebuild with `make slides PILLAR=01-prompt-engineering`).
- **New to this:** watch the [DAIR lecture](https://youtu.be/dOxUroR57xs) (1 h), read notes 01–06 alongside book Ch 1–9 and run the code snippets in each note, then read notes 07–11.
- **Building something now:** the [vendor guides](references.md#vendor-guides) for your model, then [09 — evaluating prompts](notes/09-evaluating-prompts.md).
- **Need an example prompt:** the [prompt library](notes/prompt-library.md).
- **Security:** [10](notes/10-adversarial-prompting.md) and [prompt-injection.md](../../practice/interviewing/guides/7-security-safety/prompt-injection.md).

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DA 03/01 A/B testing](../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md) | Prompt A against prompt B online |
| [GA 01 LLM fundamentals](../../generative-ai/01-llm-fundamentals/README.md) | How models read text, which prompting assumes |
| [GA 08/09 Reading results](../../generative-ai/08-eval/notes/09-reading-results.md) | Whether a prompt change is real |
| [GA 08/04 Graders](../../generative-ai/08-eval/notes/04-graders.md) | How prompt outputs get scored |

**Feeds into**

| Chapter | Why |
|---|---|
| None in other subjects | AI engineering is the last subject in the path |

---

## Lab

A prompt eval harness: three prompt variants over twelve labelled tickets, three checks, and what each change fixed and broke. It comes in both languages, side by side, on the same inputs. Both run offline with a stub by default, and each README says how to swap in a real model.

| Language | Folder | Run |
|---|---|---|
| TypeScript | [practice/prompt-eval-harness/](practice/prompt-eval-harness/README.md) | `cd practice/prompt-eval-harness && npx tsx run.ts` |
| Python | [practice/prompt-eval-harness-py/](practice/prompt-eval-harness-py/README.md) | `cd practice/prompt-eval-harness-py && uv run run.py` |

## Layout

```
01-prompt-engineering/
├── README.md               ← you are here: summary, rules of thumb
├── references.md           ← every source, mapped to the notes
├── notes/                  ← the topic notes (read in order)
├── slides/                 ← lecture deck built from the notes (deck.yaml → prompt-engineering.pptx)
├── practice/               ← the lab, in TypeScript and Python
└── sources/
    ├── prompt-eng-for-llms/  ← book chapter PDFs (reading/), absorbed into notes/
    └── images/               ← figures used by notes and deck, flat: <author>-<slug>-fig<N>.<ext>
                                (subfolders hold the DAIR guide's figures that are not used yet)
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

### Interviewing guides
- [2-llm-fundamentals](../../practice/interviewing/guides/2-llm-fundamentals/00-overview.md) — compressed summary for interview prep.
- [7-security-safety](../../practice/interviewing/guides/7-security-safety/00-overview.md) — security angle on prompt injection.
    - [prompt-injection.md](../../practice/interviewing/guides/7-security-safety/prompt-injection.md) — the security facet: adversarial input manipulation.

### Next layer
→ [02-context-engineering/](../02-context-engineering/README.md) — context engineering assembles the window that delivers your prompts.

---

## Primary texts

- Berryman and Ziegler, *Prompt Engineering for LLMs*: the backbone of this pillar
- Huyen, *AI Engineering*, ch. 5: prompts and defences
- Phoenix and Taylor, *Prompt Engineering for Generative AI*: the five principles, ch. 1 and 3

Everything else: [references.md](references.md).

## References

Every source behind the notes, mapped to chapters: [references.md](references.md).

## Working References

Claude Code convention references that map to this pillar. These files live at `~/.claude/refs/` and can be consulted in any Claude Code session.

### `agent-safety.md`
Conventions for what the agent cannot do and where that is enforced. Directly relevant to prompt injection defense and the instruction hierarchy that governs how prompts interact with system-level constraints.

Key topics for this pillar:
- Five protection layers — Layer 1 (pre-input sanitization) and Layer 4 (post-generate output check) are the prompt-layer guards
- Prompt injection: structural delimiting of untrusted content, deny-list patterns, instruction hierarchy (system prompt > developer context > user input)
- Credential and secret custody — rules for what must never appear in a prompt context window
- Write-operation confirm gate — two-phase pattern for irreversible actions triggered by prompt instructions
