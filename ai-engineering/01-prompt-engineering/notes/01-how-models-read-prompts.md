---
origin: synthesis
sources:
  - "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly 2024) — Ch 1–3"
  - https://www.promptingguide.ai/introduction/basics
confidence: high
cleaned: 2026-10-28
---
# 1 — How Models Read Prompts

> The mechanism note. Every technique in this pillar is a way of working with — not against — the five properties below.

---

## The thesis

**An LLM is a document-completion engine. A prompt is the opening of a document whose most plausible continuation is the answer you want.**

The model is a *mimic*, not an oracle. Don't ask "how would a reasonable person reply to this?" Ask "if I pulled a random document from the training set that started with exactly this text, how would it continue?" Every higher-level capability — chat, tool calls, agents — is the application layer constructing text before the call and parsing text after it. There is no separate mechanism inside the model for "answering," "remembering," or "using a tool."

GPT-3's few-shot result (2020) is the origin of the discipline: task behavior became something you elicit by changing the *input*, with no weight updates.

---

## Property 1 — Tokens, not characters

Text is split into learned sub-word tokens (~4 English characters each) before the model sees it.

| Consequence | Example | Rule |
|---|---|---|
| Sub-token tasks are hard | letter counting ("strawberry"), reversing strings, ROT13 | Do these in pre/post-processing, not in the model |
| Typos change the token sequence | `ghost` = 1 token, `gohst` = 3 | Models notice typos well but don't silently autocorrect |
| Case and rare characters cost attention | `strange new worlds` = 4 tokens, `STRANGE NEW WORLDS` = 6 | Avoid SHOUTING, ASCII art, and random IDs where you can |
| Tokens are the unit of cost and length | context window = prompt + completion tokens | Measure with a real tokenizer, not character counts |

---

## Property 2 — Autoregressive: no lookahead, no backtracking

One forward pass produces one token; it's appended and the whole computation reruns.

- **Fixed compute per token.** The model can't "pause to think" on a hard token. The only way to buy more computation is to have it emit more tokens — the structural basis of [chain-of-thought](03-core-techniques.md#chain-of-thought).
- **No takebacks.** An emitted token becomes ground truth for everything after it. Early errors compound; the model rarely self-corrects because published documents rarely contain visible corrections. Error detection belongs in the surrounding system ([04-controlling-output](04-controlling-output.md), [09-evaluating-prompts](09-evaluating-prompts.md)).
- **Repetition traps.** Continuing an established pattern is usually the most likely next token, so lists can degenerate into loops. Mitigate with stop sequences, repetition detection, or penalties.

---

## Property 3 — Left-to-right attention: order matters

Each position can only attend to positions to its *left*, and higher-layer insights can only flow back to lower layers by becoming an emitted token.

Practical consequence: **put the instruction before the content it applies to when the task changes *how* the content must be read.** The book's example: asked to count words in a paragraph *after* reading it, ChatGPT answered 348 for a 173-word paragraph; asked *first*, it answered 173. The model wasn't keeping a word count while reading because it didn't know that was the job.

The counterweight for long documents is covered in [02-prompt-anatomy](02-prompt-anatomy.md#ordering): put bulk reference material first and *restate* the question at the end ("refocus"), so the instruction is both primed and fresh.

**One-pass heuristic:** could a domain expert who knew all the facts complete this prompt in a single read, without notes or backtracking? If not, restructure the task (reorder, decompose, or move computation out of the model) rather than asking more forcefully.

---

## Property 4 — Truth bias and hallucination are the same behavior

The model continues whatever the prompt asserts. Training documents rarely open with a false premise and then correct it, so:

- **Hallucination** is just a fluent completion that happens to be false. "Don't make things up" has limited effect because the model doesn't distinguish knowing from guessing.
  - Mitigate by asking for *checkable* output: names, quotes, sources, calculations. "Trust but verify — minus the trust."
  - Ground with retrieved context and ask it to quote before answering ([02-prompt-anatomy](02-prompt-anatomy.md)).
- **Truth bias** means a false premise in a programmatic prompt will be run with, not questioned. You are responsible for not feeding it nonsense.
  - Exploit it deliberately: assert a hypothetical as fact ("It's 2031, a year after the first Neanderthals were resurrected") rather than asking the model to pretend.

---

## Property 5 — Chat models are completion models wearing a transcript

**RLHF** turns a base model into an assistant: supervised fine-tuning on ideal transcripts → a reward model trained on human rankings → PPO fine-tuning constrained to stay close to the SFT model (otherwise it learns to game the reward model). The target is HHH: helpful, honest, harmless.

**ChatML** makes turn-taking explicit with reserved tokens:

```
<|im_start|>system
You are a terse technical assistant.<|im_end|>
<|im_start|>user
What does `git rebase` do?<|im_end|>
<|im_start|>assistant
```

| Property | Why it matters |
|---|---|
| Unambiguous turns | The model always knows it's answering, not continuing |
| System-message steerability | RLHF trains models to follow the `system` role closely — your main lever for persona and rules |
| Injection resistance | Reserved tokens can't be typed through the API; users are locked into the `user` role — **unless you paste user content into `system`** |

What chat costs you vs. raw completion:
1. **Alignment tax** — measurable capability loss on some tasks.
2. **Output control** — chat models wrap answers in preamble and disclaimers; a completion prompt ending in ` ```python ` with `stop="```"` returns only code.
3. **Range** — RLHF narrows voice toward polite and uniform; bad for realistic synthetic data.

**Two scripts.** The user's conversation with your product and the transcript you send the model are different documents. Yours can include synthetic turns, retrieved context, and tool results the user never sees. You're the showrunner of the second one.

---

## What prompt engineering covers

The book frames it as the whole request/response transformation layer, in four levels:

| Level | Application does | Covered in |
|---|---|---|
| 1. Thin wrapper | Passes user text through with light formatting | [02-prompt-anatomy](02-prompt-anatomy.md) |
| 2. Augmented input | Adds retrieved context, conversation history | [02-prompt-anatomy](02-prompt-anatomy.md), [02-context](../../02-context/README.md) |
| 3. Tool use | Model requests actions, app executes them | [05-tools-and-function-calling](05-tools-and-function-calling.md) |
| 4. Agency | Model decides *how* to reach a goal | [06-chaining-and-workflows](06-chaining-and-workflows.md), [03-harness](../../03-harness/README.md) |

---

## Go deeper

- Book: [Ch 1](../sources/prompt-eng-for-llms/01-introduction.md) (architecture lineage, four levels) · [Ch 2](../sources/prompt-eng-for-llms/02-understanding-llms.md) (tokens, sampling, attention) · [Ch 3](../sources/prompt-eng-for-llms/03-moving-to-chat.md) (RLHF, ChatML)
- Sampling parameters (temperature, top-p, penalties) are in [04-controlling-output](04-controlling-output.md).

---

→ Next: [02-prompt-anatomy.md](02-prompt-anatomy.md) — what goes in a prompt, and in what order.
