# 08 — Multimodal Engineering

> Depth layer. Summary: no dedicated interview guide yet; the closest are 2-llm-fundamentals and 4-agents, from [00-start-here](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md).
> Position in the stack: *the same six layers, with inputs and outputs that aren't text*.
> Jump to: [Scope](#scope) · [Reading order](#reading-order) · [References](#references)

---

## What it is

Multimodal engineering is building systems whose inputs or outputs include images, documents,
audio or video: sending a screenshot or a scanned invoice to a vision model, retrieving over
pages that are mostly figures and tables, transcribing a call, speaking a reply, generating an
image. Each modality changes the six layers above it. An image costs tokens the way text does,
but you can't skim it to trim the budget. A PDF page can be retrieved as pixels instead of
extracted text. A voice agent has a latency budget measured in hundreds of milliseconds. A
vision answer can't be graded by string match.

**Inherits the weaknesses of:** the encoder. A vision model that misreads a chart, or an ASR
model that mishears a product name, hands every layer above it a wrong fact that looks like a
right one. Prompting can't recover detail the encoder never captured.

**Why a pillar, not a note.** Added 2026-10-31 (see [CURRICULUM.md](../../CURRICULUM.md#definition-of-done)).
The readings ledger had parked 205 multimodal papers as a watch topic with no home, and the
repo's only multimodal material was the voice and computer-use note in
[generative-ai/07](../../generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents.md).
Image input, document understanding, multimodal RAG and speech pipelines each need their
own engineering, which no existing pillar could hold.

---

## Scope

| In | Out (lives elsewhere) |
|---|---|
| Image and document input: vision-language models, OCR vs. VLM, image token cost, resolution and cropping | How ViTs and CLIP are built and trained: [generative-ai/01](../../generative-ai/01-llm-fundamentals/README.md) |
| Multimodal RAG: page-as-image retrieval (ColPali), captioning vs. embedding figures, tables | Text RAG pipelines: [generative-ai/02](../../generative-ai/02-rag-retrieval/README.md) |
| Speech: ASR, TTS, cascaded vs. end-to-end voice pipelines, latency budgets | Building a full voice or computer-use agent: [generative-ai/07 note 03](../../generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents.md) |
| Image and video generation as an API: prompting, editing, cost, provenance | Serving the models on GPUs: [07-inference](../07-inference-engineering/README.md) |
| Evaluating multimodal output: VLM hallucination, grading images and transcripts | Multimodal jailbreaks and image-borne injection: [09-safety-and-security](../09-safety-and-security/README.md) |

---

## The story in one paragraph

An invoice assistant works on text, then meets the world. A customer photographs an invoice, and a
downscale erases the digit that mattered. A supplier sends a PDF, and the extraction drops a row with no
error. A user asks about prices, and the answer sits in a chart the parser threw away. A customer phones,
and suddenly every reply has a deadline and can be interrupted. Marketing wants illustrations, and nobody
can reproduce the one they liked. Then the benchmark says 90% and users still complain, because the test
rewarded guessing over looking. Each chapter takes one of those failures and gives you the mechanism
behind it, a check that catches it, and the evidence for what to do about it.

## Reading order

| # | Chapter | Question it answers |
|---|---|---|
| 01 | [Image input](notes/01-image-input.md) | What does the model actually receive, and what did preprocessing destroy? |
| 02 | [Document understanding](notes/02-document-understanding.md) | Which route through a PDF, and how do you prove the result without trusting the model? |
| 03 | [Multimodal RAG](notes/03-multimodal-rag.md) | How do you retrieve an answer that exists only in a chart? |
| 04 | [Speech and voice agents](notes/04-speech-and-voice-agents.md) | Cascade or speech-to-speech, and how do you spend the latency budget? |
| 05 | [How image generators work](notes/05-how-image-generators-work.md) | What happens between noise and picture, and which families compete with diffusion? |
| 06 | [Generating images and video](notes/06-generating-images-and-video.md) | Which controls do you set and record, and how do you handle provenance? |
| 07 | [Evaluating multimodal systems](notes/07-evaluating-multimodal-systems.md) | How do you build tests in which guessing fails? |

Failure modes have no chapter of their own: each chapter ends with its own pitfalls, and chapter 07 pulls
the checks into one scorecard. Attacks that arrive through an image, a document or a voice are in
[09-safety-and-security](../09-safety-and-security/README.md).

## Rules of thumb

- Fix the input first. Honor EXIF, protect small text with a crop, and log the pixel height of the smallest text you need.
- Well-formed output proves nothing. Check facts the document must satisfy on its own terms, such as line items that sum to the subtotal.
- Route per page: a text layer is cheaper and often more accurate than OCR or vision, and the 95th percentile page can cost twenty times the median.
- On visually rich pages, improve ingestion before you swap embedders, and use late interaction as a second stage.
- For a voice agent, write the budget down per stage at the 95th percentile, and commit only what the caller heard to history.
- Pin and record the seed, sampler, steps, guidance and model version with every generated image.
- Score fields and critical terms, not only edit distance or WER. One wrong digit looks almost perfect on both.
- Build tests in which the shortcut fails: paired images, rotated options and plausible absent objects.

## Deck and practice

The lecture deck is [slides/multimodal-engineering.pptx](slides/multimodal-engineering.pptx), built from
[slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=ai-engineering/08-multimodal-engineering STRICT=1`.

This pillar has no `practice/` folder yet. Every chapter's code runs on synthetic data with
`uv run --with numpy --with pillow python <file>.py`, and the "Try it" sections are the exercises.

---

## Layout

```
notes/                       chapters (see Reading order)
references.md                papers and books, mapped to notes
sources/<book-slug>/chNN-*.pdf   book chapters
sources/<author-year-slug>.pdf   papers
sources/images/              figures used in notes and slides
slides/                      lecture deck (deck.yaml → .pptx + .pdf)
```

## References

See [references.md](references.md).
