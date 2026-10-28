---
origin: book
source: "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly) — Ch 3: Moving to Chat"
confidence: high
cleaned: 2026-07-29
---

# Ch 3 — Moving to Chat

## Why base models aren't enough

A base model only completes documents — it has no concept of "answer this question."
Prompt it with `What is a good dish for chicken?` and, absent training, it's just as
likely to continue the pattern with more questions (`What is a good dish for beef?
What is a good dish for pork?...`) as it is to answer. Base models are also
unfiltered: trained on the whole internet, they'll complete a lasagna recipe or a
meth recipe with equal fluency. Production use needs models that are (a) reliably
assistant-shaped and (b) safe by default. That's the gap RLHF closes.

## Model alignment: the HHH frame

Anthropic's 2021 paper on using a general language assistant as a laboratory for
alignment work defined the target: **HHH** — Helpful, Honest, Harmless.

- **Helpful** — completions follow instructions, stay on-topic, are concise and useful.
- **Honest** — no hallucinating facts and presenting them as true; if uncertain, say so.
- **Harmless** — no offensive content, discriminatory bias, or dangerous information.

## RLHF pipeline (OpenAI's InstructGPT/GPT-3 case study)

Four models, three fine-tuning stages, going from a raw base model to an
HHH-aligned assistant:

| Model | Purpose | Training data | Scale |
|---|---|---|---|
| Base (GPT-3) | Predict next token | Common Crawl, WebText, Wikipedia, Books1/2 | 499B tokens |
| SFT | Follow instructions, chat | Human-written ideal prompt/completion pairs | ~13,000 docs |
| Reward model (RM) | Score completion quality | Human-ranked completion sets (SFT-generated) | ~33,000 ranked docs → order of magnitude more pairs |
| RLHF (PPO) | Follow directions + stay HHH | SFT-generated completions scored by RM | ~31,000 prompts |

**Stage 1 — Supervised fine-tuning (SFT).** Fine-tune the base model on ~13,000
handcrafted transcripts of a helpful/honest/harmless assistant conversing with a
user. Same mechanics as pretraining (predict next token) just at much smaller scale
and on curated data. Result: a model that's noticeably more obedient — but it lies.

**Stage 2 — Reward model.** This is the "RL" in RLHF. General RL framing: an *agent*
in an *environment* takes *actions* to maximize *reward*. Here the agent is the LLM,
the environment is the document being completed, actions are next-token choices, and
reward is a learned proxy for "how good is this completion." To build it: sample the
SFT model at high temperature to get 4–9 diverse completions per prompt, have human
judges rank them best-to-worst, then train a model (seeded from the SFT model, since
it needs at least SFT-level competence to judge quality) to take *two* completions and
pick the better one. Ranked-pairs training means 33,000 ranked documents yield an
order of magnitude more actual training pairs.

**Stage 3 — RLHF via PPO.** Take the SFT model, generate a completion for a prompt,
score it with the reward model, and update weights to increase that score — this is
now fine-tuning against a *learned* objective rather than human-written text. Naive
maximization lets the model **cheat**: it can learn to game the reward model's score
without producing genuinely better text. Fix: **Proximal Policy Optimization (PPO)**,
which allows weight updates toward higher reward *only* so long as output doesn't
diverge significantly from the SFT model's output distribution. This constraint is
what keeps the final model coherent rather than reward-hacked gibberish.

## Why honesty specifically needs RLHF (not just SFT)

SFT alone doesn't fix hallucination, and the mechanism is subtle. Human labelers
writing "ideal" completions don't actually know what's inside the base model's
knowledge — they can't calibrate to it. Two failure modes result:
- Labeler writes confident content beyond the model's real knowledge → model learns
  "confidently fabricating is fine."
- Labeler hedges on things the model actually knows well → model learns to hedge
  everything, becoming uselessly uncertain.

RLHF sidesteps this because the *SFT model itself* — not human labelers — generates
the completions that get ranked. When human rankers score factually-wrong SFT
completions below factually-right ones, the model learns a direct signal: content
inconsistent with its own internal knowledge is "bad," content consistent with it is
"good." The result is a model that expresses confidence in things it's actually
certain of, and falls back to hedging language pointing the user to an original
source when it isn't.

## Practical properties of the RLHF process

- **Idiosyncrasy control.** SFT completions were hand-written by ~40 screened
  contractors — a small enough group that individual writing quirks could leak into
  the model, so OpenAI screened for this. Reward-model training data was different:
  humans only *ranked* SFT-generated text, and rankers were calibrated toward
  agreement with each other, further diluting individual idiosyncrasy. Net effect:
  the reward model approximates an aggregate/average human preference, not any one
  labeler's voice.
- **Cost-efficient labor curve.** The expensive step is the 13,000 hand-crafted SFT
  documents. Once SFT exists, reward-model data collection is just *ranking*
  SFT-generated completions (cheaper than writing from scratch — 33K documents). The
  final RLHF stage needs almost no human labor at all — ~31,000 prompts scored
  automatically by the reward model.
- **The alignment tax.** RLHF optimizes for helpful/honest/harmless, which is a
  different objective than raw capability — and optimizing for it can measurably
  *decrease* performance on other tasks. Mitigation: mix some of the original
  base-model pretraining data back into RLHF training to preserve capability while
  still pushing toward the three Hs.

## From instruct models to chat models

**Instruct models** (the first generation) were trained by mixing instruction-style
examples (prompt → answer, e.g. "What are 10 sci-fi books I should read next?" →
answer) into the training data, conditioning the model to treat prompts as requests
rather than documents to extend. Problem: instruct-style prompts are structurally
ambiguous. Nothing in the raw prompt string signals "now it's your turn, answer me" —
the model has to infer from data-mix patterns whether it's in completion mode or
answer mode, and training a mix of both objectives (needed to fight the alignment
tax) directly works against making that signal unambiguous.

**Chat models** fix this with explicit structural markup: **ChatML**. Example:

```
<|im_start|>system
You are a helpful, very proper British personal valet named Jeeves.
Answer questions with one sentence.<|im_end|>
<|im_start|>user
What is a good indoor activity for a family of four?<|im_end|>
<|im_start|>assistant
```

Three roles — `system`, `user`, `assistant` — each message wrapped in
`<|im_start|>ROLE ... <|im_end|>`. The `<|im_end|>` after the user's turn makes it
structurally unambiguous that the question is finished and a response is expected;
injecting `<|im_start|>assistant` after it forces the model into answer mode, no
inference required. The `system` message isn't part of the dialogue — it's
persistent instructions defining the assistant's persona and behavioral rules —
prompt engineers commonly use it to specify off-topic redirects or how to
de-escalate an argumentative user.

Benefits of ChatML over the ambiguous instruct format:
1. **Unambiguous turn-taking** — model always knows whether it's continuing or
   responding.
2. **System-message steerability** — because chat models are RLHF-trained
   specifically on ChatML-annotated transcripts, they learn to closely follow the
   system role. This is the main lever for persona/constraint customization (and,
   used adversarially, for pushing past default safety behavior).
3. **Prompt-injection resistance** — `<|im_start|>` and `<|im_end|>` are *reserved
   special tokens*, not encodable as regular text. If a user's API input literally
   contains the string `<|im_start|>`, it gets tokenized as six separate ordinary
   tokens (`<`, `|`, `im`, `_start`, `|`, `>`), never as the single reserved token.
   So a user talking through the API can never inject a fake `system` or `assistant`
   turn into the transcript — they're structurally locked into the `user` role.

**Practical corollary:** never copy raw user-supplied content into a `system`
message (directly or via retrieved documents) — doing so throws away ChatML's
injection protection, since now attacker-controlled text sits in the
highest-trust role.

## The chat completion API hides ChatML

Modern chat APIs (OpenAI's `chat.completions.create`, etc.) take a `messages` list of
`{role, content}` dicts — ChatML tags are never visible to the API caller; the API
serializes to ChatML internally before hitting the model, and strips it back out of
the response. This is also a security boundary: since the caller can't produce the
literal reserved tokens through the JSON interface either, injection protection holds
end-to-end.

Useful API parameters beyond the obvious (`messages`, `model`): `max_tokens` (cap
length), `stop` (list of strings that halt generation — good for parsing structured
output), `n` (parallel completions — `n=128` costs little extra latency vs `n=1`,
useful for eval/sampling), `logprobs`/`top_logprobs` (expose per-token confidence and
alternatives), `logit_bias` (nudge specific token likelihoods), `stream` (token-by-
token delivery for responsive UX), and `temperature` (0 = deterministic-ish and safe
but repetitive; ~1.0 is close to the practical "sweet spot" (PDF p. 17); near 2.0
degrades to noise).

## What you give up moving from completion to chat

1. **Alignment tax**, again — chat-specialized models can regress on some raw
   capability tasks relative to base/completion use (per a 2023 Stanford study
   showing GPT-4 behavior drift over time on certain tasks).
2. **Loss of output control.** Chat models are chatty by RLHF design — they wrap
   answers in commentary, disclaimers, and cheerful lead-in framing. A
   completion API prompted with `The following is a program that implements
   quicksort in python:\n\`\`\`python` gives you code and only code, and you can set
   `stop="\`\`\`"` to cut exactly at the end — no parsing the answer out of prose.
   Chat models will often ignore instructions to "return only code."
3. **Loss of raw-humanity range.** RLHF deliberately narrows the model toward
   polite, uniform, safe outputs. The pretraining corpus encodes the full range of
   how humans actually write and think — vulgar, biased, blunt, unfiltered — and
   that range is sometimes exactly what's needed: generating realistic synthetic
   data, letting a doctor brainstorm bluntly, letting law enforcement discuss
   illegal activity without the model refusing to engage. Chat/RLHF trades this
   range away for safety-by-default.

## Beyond chat: tool calling

About half a year after chat, OpenAI added tool/function execution: the model emits
a structured request, the *application* (not the model) executes the real API call,
and the result gets spliced back into the prompt for the next completion. Conceptually
this changes nothing about the fundamental nature of LLMs — they're still just
document completion engines. Chat made the "document" a ChatML transcript; tools just
add special syntax within that transcript for describing and invoking function calls,
with results appended back in.

## Prompt engineering as playwriting

Useful mental model for building chat applications: two conversations exist, and they
are *not* the same. One is the real human user talking to your product. The other is
the application's transcript sent to the model — which may include synthetic `user`/
`assistant` turns, retrieved context, and tool results the end user never sees.

Frame it as theater: the ChatML roles (`system`, `user`, `assistant`, `tool`) are
*characters*; the prompt is the *script*; there are multiple *playwrights* — you (the
prompt engineer, who writes the system message and boilerplate structure), the human
user (who supplies the core problem via their messages), the LLM itself (which
"performs" the assistant's lines), and external APIs/tools (which inject retrieved
content or results into the script). As the prompt engineer you're the showrunner:
responsible for how the whole play unfolds, even though you don't control every line.

## Key takeaways

- Base models complete documents; they have no built-in notion of "answer this
  question" or "stay safe" — RLHF is the mechanism that bolts on Helpful/Honest/
  Harmless behavior via SFT → reward model → PPO-constrained fine-tuning.
- Honesty specifically requires RLHF, not SFT: only by ranking completions the *SFT
  model itself* generated (rather than human-written text) can the model learn to
  calibrate confidence to its own actual knowledge.
- PPO's key trick is constraining reward-maximization to stay close to the SFT
  output distribution — otherwise the model learns to game the reward model instead
  of writing better text.
- ChatML's `<|im_start|>`/`<|im_end|>` are reserved tokens unreachable from normal API
  input — this is what makes prompt injection into `system`/`assistant` roles
  structurally impossible, unless you defeat it yourself by pasting raw user content
  into the system message.
- Chat/RLHF is a trade: unambiguous turn-taking and steerable personas, at the cost
  of alignment-tax capability loss, chatty/uncontrollable output formatting, and a
  narrowed range of "voice" relative to a raw base model.
- Model the application prompt and the user-facing conversation as two distinct
  scripts with multiple playwrights (you, the user, the LLM, external tools) — they
  look similar but are not the same conversation.
