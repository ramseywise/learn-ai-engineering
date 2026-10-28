---
origin: book
source: "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly) — Ch 11: Looking Ahead"
confidence: high
cleaned: 2026-07-29
---

# Ch 11 — Looking Ahead

Closing chapter: extrapolates three trend lines (multimodality, UX/UI, raw intelligence)
and restates the book's two core lessons as durable mental models for prompt engineering.

## Multimodality

GPT-4 established image-in-prompt as a norm; likely implementation (per public literature,
OpenAI hasn't disclosed specifics): a convolutional network converts image regions into
embedding vectors of the same dimensionality as text-token embeddings, positional info is
imbued so spatial relationships survive, then image and text vectors are concatenated and
run through the same transformer stack used for text-only LLMs (Ch 2 architecture). Video
extends this naively — sample frames as a sequence of images (see OpenAI's cookbook
example).

Why multimodality matters beyond obvious use cases (accessibility — reading signs,
navigating environments for vision-impaired users):

- **Training-data scarcity**: text-only pretraining is approaching a ceiling — literally
  "the text of the entire public internet" (PDF p. 2) may not be enough data for the next
  generation of large models. Overtraining on a too-small text corpus causes overfitting
  (memorization instead of world-modeling).
- **Images/video are a qualitatively different data source**, not just "more data" — they
  encode spatial reasoning, social cues, and physical common sense that's hard to learn
  from text alone.

**Practical guidance for prompt engineers working with images:**
- Include only images relevant to the conversation — irrelevant images distract the model
  same as irrelevant text.
- Frame images with text that explicitly introduces their role in the conversation.
- Reuse patterns/motifs the model already saw in training rather than inventing new visual
  conventions — e.g., don't invent a novel diagram format when a standard one exists on
  the internet. This is the multimodal analog of the Little Red Riding Hood principle
  (Ch 4): follow well-trodden formats.

## User Experience and User Interface — stateful objects of discourse

Consumer UI is shifting toward conversational interfaces (humans have spoken for 200,000
years, clicked buttons for ~40). The chapter frames this shift through a specific concept:
**stateful objects of discourse** — in human collaboration (e.g., pair programming), we
talk *about* a persistent thing (a file), modify it, and discuss how it changed over time.

Most chat UIs today don't do this. Ask ChatGPT to write a function, then modify it, and it
doesn't edit the function in place — it rewrites the whole thing from scratch as a new
message. The conversation accumulates N separate objects rather than one evolving object,
and it becomes ambiguous which version/object you're even referring to once there are
multiple.

**Claude's Artifacts** are presented as a partial solution: the Artifact (SVG, HTML,
Mermaid diagram, code, any text fragment) is the stateful object of discourse — it persists
in a separate pane while the transcript captures only the back-and-forth *about* it. Asking
for a change updates the Artifact in place rather than re-pasting it into the transcript.

Chapter's critique of the current Artifacts implementation (useful as a design checklist
for building your own stateful-object UIs):
- Editing is prompt-engineering, not truly stateful — the model still regenerates the
  entire Artifact from scratch on each change; it's the UI, not the generation mechanism,
  that makes it feel stateful. Won't scale well to long documents.
- No multi-Artifact support — the UI assumes one Artifact at a time; switching topics
  gets treated as a new version of the same slot rather than a distinct object. No
  shorthand naming scheme to disambiguate multiple concurrent objects (in UI or prompt).
  Consider both when building similar interfaces.
- No user-side editing — if the user spots a small fixable error, there's no way to
  directly edit the Artifact; they must ask the assistant to retype the whole thing.
  Better: let the user edit directly and feed that diff back into the next prompt so the
  model is aware of the change.

Design takeaway: conversational interfaces are intuitive but easy to build badly — a
bare-bones chat wrapper is a gimmick unless the "object" layer is deliberately designed.
Tools gave assistants the ability to act on the world; stateful objects give conversations
something persistent to be about. Conversational UI also has a safety benefit independent
of statefulness: it keeps a human in the loop, catching drift (Ch 8: models left
unsupervised tend to stray off course) before it compounds.

## Intelligence trends

- **Benchmark saturation**: leading models now ace most popular benchmarks (MMLU,
  HellaSwag, TruthfulQA, Winogrande, ARC, GSM8K), making them useless for differentiating
  further improvement. Two causes: (1) models are genuinely getting smarter, and (2) data
  contamination — benchmark content gets duplicated across the internet and inadvertently
  pulled into training, unintentionally "cheating." Response: continuously upgrading
  leaderboards (e.g., Open LLM Leaderboard 2) and shifting to **nonmemorizable
  benchmarks** like ARC-AGI — algorithmically generated pattern-recognition tests drawn
  from an effectively unbounded space, so memorizing the test set isn't possible.
- **Training improvements**: better RLHF (Ch 3) is visibly improving chain-of-thought
  quality in shipped models, which drives more useful final responses.
- **Knowledge distillation**: a large "teacher" model trains a small "student" model not
  on next-token labels but on the teacher's full next-token probability distribution —
  richer training signal lets small models approach teacher accuracy at a fraction of the
  cost/latency.
- **Quantization**: representing weights in 8-bit instead of 32-bit floats, shrinking
  model size and cost while increasing speed, with modest accuracy tradeoffs.

**Forward-looking rule for prompt engineers**: expect cost, latency, and context-window
limits to keep improving — what's too expensive/slow/small-context today will resolve
itself over time. But intelligence gains don't remove the burden on the prompt: models
will never be psychic. If the prompt lacks information *you* would need to solve the
problem, it's insufficient for the model too, no matter how capable the model becomes.

## Conclusion — the book's two core lessons

1. **LLMs are text-completion engines that mimic training-distribution text** — nothing
   more. This was true when the book started (raw completion APIs) and remains true even
   as chat APIs, tool use, and Artifacts have been layered on top: at their core, models
   are still just completing documents that happen to look like chat transcripts.
   Practical corollary (Little Red Riding Hood principle, Ch 4): make prompts follow the
   patterns and formats seen in training data — e.g., use markdown for structured text,
   use standard document formats — rather than inventing new ones, to get well-behaved,
   predictable completions.

2. **Empathize with the LLM** — treat it as "your big, dumb mechanical friend who happens
   to know much of the content of the internet" (PDF p. 9), with real cognitive limits:
   - *Easily distracted* — don't fill the prompt with irrelevant information; every
     included detail should matter.
   - *Must be able to decipher the prompt* — if a human can't parse the fully-rendered
     prompt, the model probably can't either.
   - *Needs to be led* — give explicit instructions, and examples where useful.
   - *Isn't psychic* — the prompt engineer's job is ensuring the prompt (or the tools it's
     given) actually contains what's needed to solve the problem.
   - *Has no internal monologue* — letting the model reason out loud (chain of thought)
     produces measurably better solutions than forcing it straight to an answer.

## Key takeaways

- Multimodal training solves two problems at once: enabling non-text use cases (spatial
  reasoning, accessibility) and unlocking new training data as pure-text corpora approach
  exhaustion.
- "Stateful objects of discourse" is the mental model for evaluating/designing
  conversational UIs — a good conversational interface needs a persistent thing to talk
  about, not just a growing transcript. Claude's Artifacts is a first step, with real gaps
  (whole-object regeneration, no multi-object support, no user-side editing).
- Benchmarks saturate because models improve *and* because benchmark data leaks into
  training; nonmemorizable, algorithmically generated benchmarks (ARC-AGI) are the fix.
- Distillation and quantization are the two named levers making models cheaper/faster
  without comparably large accuracy loss — expect this trend to keep compressing cost,
  latency, and context limits over time.
- Two durable rules survive every architecture shift: LLMs are still just text-completion
  engines mimicking training data (follow established patterns/formats), and prompt
  engineering is fundamentally about empathizing with the model's real limitations
  (distractible, non-psychic, no internal monologue unless prompted for one).
