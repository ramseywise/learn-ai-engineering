---
origin: book
source: "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly) — Ch 2: Understanding LLMs"
confidence: high
cleaned: 2026-07-29
---

# Ch 2 — Understanding LLMs

## Core model: LLM as document-completion engine

An LLM is a string-in, string-out service: `prompt → completion`. It is trained on a
corpus (the *training set* — a mixture of books, web text, code, Q&A/conversation data,
etc.; e.g. "The Pile" is ~18% CommonCrawl, ~14% PubMed, ~12% books, ~10% OpenWebText,
~7.6% GitHub, and a long tail of smaller sources). Training objective: given the start of
a real document, predict the statistically likely continuation. The model is a **mimic**,
not an oracle — it is not answering your question, it is continuing a document that
happens to start with your prompt.

Foundation models are pretrained generalists; most applications fine-tune rather than
train from scratch (e.g., early OpenAI Codex = GPT-3 fine-tuned on GitHub code). If a
model was fine-tuned on dataset B after pretraining on A, write prompts as if the model
was trained on B outright (covered further in Ch 7).

**Mental model for predicting output**: don't ask "how would a reasonable person reply to
this prompt?" Ask "if I picked a random document from the training set that happened to
start with this text, what's the statistically likely continuation?" The better you know
(or can guess) the training distribution, the better your intuition for completions. A
model trained mostly on narrative prose completes differently than one that's also seen
emails and customer-service transcripts — same prompt, different plausible continuation.

Overfitting (rote memorization of training chunks instead of general patterns) is
considered a defect and is actively guarded against by architecture and training
procedure — but a model that "solves" something seen in training may fail on a novel
variant of the same problem.

## Hallucinations and truth bias

Hallucinations — confident, plausible-sounding, factually wrong output — are not a
distinct failure mode from the model's perspective; they're just completions like any
other. Consequently, directives telling the model not to fabricate have limited effect,
because the model isn't distinguishing "knowing" from "guessing" internally.

**Practical mitigation**: ask for material that can be independently checked — reasoning
explanations, calculations, source links, specific keywords/names. The book's own example:
"There was an English king who married his cousin" (PDF p. 7) is unverifiable, but
"There was an English king who married his cousin, namely George IV, who married Caroline
of Brunswick" (PDF p. 7) is checkable. The book's antidote: "The best antidote to
hallucinations is 'Trust but verify,' just minus the trust." (PDF p. 7)

**Truth bias**: if a prompt asserts something false or nonexistent, the LLM will
typically continue as if it's true, because training documents rarely open with a false
claim and then correct it mid-stream. Two consequences:
- **Exploit it deliberately** for hypotheticals: instead of "Pretend that it's 2030 and
  Neanderthals have been resurrected." (PDF p. 7), write "It's 2031, a full year since
  the first Neanderthals were resurrected." (PDF p. 7) — a *make-believe prompt* that
  asserts the premise as fact rather than asking the model to role-play it.
- **Guard against it in programmatic prompts**: a human proofreading a weird or
  counterfactual auto-generated prompt would raise an eyebrow and stop; the LLM won't.
  It'll run with whatever the prompt asserts. You are responsible for not feeding it
  nonsense.

## Tokenization — how LLMs see text

Text is never processed as raw characters. A tokenizer first splits the string into
*tokens* (typically 3–4 characters on average for English; the token vocabulary is
learned, not fixed rules), converts them to integer IDs, and only that sequence goes into
the model. Output tokens are converted back to text afterward. Like humans reading in
word-chunks rather than letter-by-letter, LLMs operate one abstraction level above raw
characters — but the abstraction is different from human word-boundaries, which produces
systematic blind spots.

**Three concrete differences from human reading:**

1. **Tokenizers are deterministic, humans are fuzzy.** Humans "autocorrect" typos
   invisibly; LLMs don't — a typo can shatter a word into an unrecognizable token
   sequence. `ghost` is one token; `gohst` becomes three (`g`-`oh`-`st`), which is why
   models are oddly good at *noticing* typos (the token pattern looks wrong) even though
   they're not reading letter-by-letter.
2. **LLMs can't slow down and inspect individual letters** the way a human can
   consciously spell out a word. Any task requiring the model to break tokens apart or
   reassemble them at the sub-token level (reversing letters, counting letters, ROT13)
   is much harder than it looks and frequently fails outright — see the classic letter
   count failure on the word "strawberry" and ChatGPT failing to reverse and re-reverse a
   scrambled sentence.
3. **Capitalization and rare characters cost hidden "attention" budget.** `strange new
   worlds` tokenizes to 4 tokens; `STRANGE NEW WORLDS` tokenizes to 6 — a different,
   less-connected token sequence, not a case-flag on the same tokens. The model has
   learned the connection between cases from data, but it costs processing effort the
   model could spend on your actual task. Accented characters, ASCII art, and rare
   symbols are similarly costly (e.g., 😊 is 2 tokens; random alphanumeric strings like
   crypto keys are <2 chars/token, far worse than the ~4 chars/token typical of English).

**Practical rule**: avoid giving the model subtoken-level tasks (reversal, letter
counting, case conversion at scale) directly. If your application needs that, do it in
pre/post-processing outside the LLM call.

## Token economics

Tokens, not characters or words, are the model's unit of "length" — they determine read
time, generation time, API cost (billed per token; roughly 50K–1M output tokens per
dollar at time of writing, model-dependent), and fit against the **context window** (the
hard cap on prompt + completion tokens combined). There's no fixed
character-to-token ratio — it depends on language (tokenizers are optimized for English)
and content (digits and random strings compress worse than prose). Use a real tokenizer
(Hugging Face, `tiktoken`) rather than estimating by eyeball when precision matters.
Most vocabularies also include special tokens, e.g. an end-of-text token appended to
every training document so the model learns where completions should stop.

## Autoregressive generation

A single forward pass produces a probability distribution over the *next* token only.
The model samples one token, appends it to the sequence, and reruns the full computation
to get the next one — "autoregressive." This has hard consequences:

- **No lookahead, no pause-to-think.** Unlike a human who can stop and reflect mid
  sentence, the model spends the same fixed compute per token regardless of how "hard"
  that token is to choose correctly.
- **No backtracking.** Once a token is emitted, it's permanent context — the model can't
  erase it. It also won't natively self-correct ("actually, that's wrong") because
  finished training documents rarely contain explicit takebacks (people who write
  takebacks edit them out before publishing). If you need error-detection and
  backtracking in your application, you have to build it into the surrounding system —
  the model won't supply it on its own.
- **Repetition traps.** Because continuing an established pattern is usually the single
  most likely next token, models can fall into self-reinforcing loops (e.g., the book's
  Figure 2-10, PDF pp. 16–17: a reasons-for-liking-a-TV-show list that degenerates into
  repeating variants of "the franchise has a strong [foundation/legacy/following]"
  indefinitely, never naturally terminating). Mitigations: post-hoc repetition
  detection/filtering, or raise temperature to inject enough randomness to break the loop.

## Temperature and sampling

The model doesn't compute one answer — it computes a probability (returned as `logprob`,
natural log of probability, always ≤ 0; more likely tokens have logprobs closer to 0,
typically between -2 and 0 for a strong top candidate) for *every* token in the
vocabulary. **Sampling** is the separate step that turns that distribution into one
chosen token. **Temperature** (`t ≥ 0`) controls how sampling uses those probabilities:

```
p(token_i) = exp(logprob_i / t) / Σ_j exp(logprob_j / t)
```

| Temperature | Behavior | Use when |
|---|---|---|
| 0 | Always picks the single most likely token (near-deterministic; rounding can still cause drift) | Correctness matters, reproducibility matters |
| 0.1–0.4 | Small chance of a close second-place token | Slightly more colorful single output, or generating a few variants to filter |
| 0.5–0.7 | Meaningful chance of a "less likely but not absurd" token | Need many (10+) independent varied solutions |
| 1 | Sampling matches the *training set's own statistical distribution* | Want output whose properties (e.g. list length) mirror real documents |
| >1 | More random than the training set itself | Rarely useful directly |

**Trade-off table**: high temperature buys more alternatives and generation-property
diversity (e.g., list lengths distributed like real documents) at the cost of correctness
and reproducibility; low/zero temperature buys correctness and determinism at the cost of
variety.

High temperature degrades generation quality over long outputs, and the effect
compounds: once a high-temperature sample produces a slightly "off" token, the model
treats its own prior tokens as ground truth context and keeps building on the error,
so quality erodes progressively through a long generation (demonstrated by a
"how alcohol affects behavior" list that goes from coherent, to florid, to gibberish as
temperature rises from 0 to 2). An alternative sampling strategy, **beam search**, looks
ahead several tokens to avoid painting itself into a corner, trading much higher compute
cost for more globally coherent output — used less often in practice for this reason.

## The transformer: minibrains and attention

Reframe the architecture as **one small "minibrain" per token position**, all identical
in structure (same weights, different inputs), stacked in **layers** (tens of layers in
practice — GPT-3 has 96; GPT-4-class models exceed 100; simplified diagrams in the book
use 4). Each minibrain:

- Starts knowing only its token and its position.
- Runs a fixed number of layer-steps ("keeps thinking" for a fixed compute budget — it
  cannot request more steps for a harder token).
- At every step *before* the last, shares intermediate results with minibrains to its
  right.
- At the *last* step, produces a prediction for the token immediately to its right.

**Attention** is the regulated communication protocol between minibrains, structured as
a Q&A exchange: each minibrain (1) submits questions about what it wants to know, (2)
submits information it can offer, (3) questions get matched to best-fitting answers, (4)
the matched answer is revealed to the asking minibrain. This exchange happens in a
learned internal "language" (vector representations), not literal English.

**Two hard structural constraints (masking):**

- **Information only flows left → right.** A minibrain can only receive answers from
  minibrains to its left, never the right — this is what "unidirectional" / "GPT-style"
  transformer means. Nothing downstream of a position can influence it.
- **Information only flows bottom → top within a layer-step**, and *never back down* —
  except through one channel: when the top layer emits an actual output token, that
  token becomes the ground-floor input to a brand-new minibrain stack. This is the
  **only way the model can feed a "higher-layer insight" back into low-layer
  processing** — by first turning it into an explicit token and re-reading it. This is
  the structural basis of chain-of-thought prompting (Ch 8): forcing the model to
  externalize intermediate reasoning as tokens is not a stylistic nicety, it's the only
  mechanism available for that reasoning to influence subsequent computation.

**Practical consequence — order matters.** Because processing is single-pass,
left-to-right, with a fixed compute budget per token and no re-reading, a capability
implicitly requiring "read everything, then decide what mattered" (e.g., "here's a
paragraph, tell me how many words it contains" when the question is asked *after* the
paragraph) frequently fails — the model was busy attending to semantics and style while
reading, not maintaining a running word counter, because it didn't yet know counting was
the ask. Moving the instruction earlier measurably improves results (worked example:
ChatGPT given a chapter + trailing "how many words in the paragraph above?" answered 348
for a 173-word paragraph; given the question *first*, it answered 173 — still not
exact, but far closer). This motivates prompt-ordering guidance developed further in
Ch 6.

**Heuristic for whether a task is realistic for an LLM in one pass:** could a human
expert who already knows all the relevant facts by heart complete the prompt in a single
read-through, with no backtracking, editing, or note-taking? If not, the LLM will likely
struggle too — the fix is usually to restructure the task (reorder the prompt, break it
into steps, or move computation outside the model) rather than to ask more forcefully.

Parallelism note: because computation at one layer only depends on states to the left and
below, prompt tokens can be processed in parallel (triangle-shaped compute pattern), but
generation cannot — each new token requires a full pass before the next one starts. This
is why models read long prompts much faster than they generate long completions (roughly
an order of magnitude faster).

## Key takeaways

- LLMs are trained-document mimics, not question-answerers — predict completions by
  asking "what does a document starting this way continue with," not "how would someone
  reply."
- Hallucination and truth bias are the same underlying behavior (confident continuation
  of whatever's given) — combat by requesting checkable evidence, not by instructing
  "don't lie"; exploit truth bias deliberately via make-believe prompts that assert
  premises as fact.
- Tokenization, not character/word reading, is the model's real input unit — avoid
  subtoken tasks (reversal, letter-counting, case conversion) directly in-model; do them
  in pre/post-processing.
- Generation is strictly autoregressive: one token at a time, no lookahead, no
  backtracking, fixed compute per token — repetition traps and irrecoverable early
  errors are structural, not incidental.
- Temperature trades correctness/determinism (low) for variety/distributional realism
  (high); high temperature degrades coherence progressively over long outputs.
- The transformer's left-to-right, bottom-to-top information flow means a "higher-layer
  insight" can only reach earlier processing by being emitted as an explicit token and
  re-read — the structural justification for chain-of-thought prompting and for putting
  instructions before the content they apply to.
