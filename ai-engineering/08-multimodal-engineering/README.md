# 08 — Multimodal Engineering

> Depth layer. Summary: no dedicated interview guide yet; the closest are 2-llm-fundamentals and 4-agents, from [00-start-here](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md).
> Position in the stack: *the same six layers, with inputs and outputs that aren't text*.
> Jump to: [Scope](#scope) · [Planned notes](#planned-notes) · [References](#references)

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
| Image and document input: vision-language models, OCR vs. VLM, image token cost, resolution and cropping | How ViTs, CLIP and diffusion models work inside: [generative-ai/01](../../generative-ai/01-llm-fundamentals/README.md) |
| Multimodal RAG: page-as-image retrieval (ColPali), captioning vs. embedding figures, tables | Text RAG pipelines: [generative-ai/02](../../generative-ai/02-rag-retrieval/README.md) |
| Speech: ASR, TTS, cascaded vs. end-to-end voice pipelines, latency budgets | Building a full voice or computer-use agent: [generative-ai/07 note 03](../../generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents.md) |
| Image and video generation as an API: prompting, editing, cost, provenance | Serving the models on GPUs: [07-inference](../07-inference-engineering/README.md) |
| Evaluating multimodal output: VLM hallucination, grading images and transcripts | Multimodal jailbreaks and image-borne injection: [09-safety-and-security](../09-safety-and-security/README.md) |

---

## Planned notes

Notes are written from the sources by `/papers` and `/chapter`. The outline below is the
target; rename or merge as the material dictates.

| # | Note | Main sources |
|---|---|---|
| 01 | What changes when the input isn't text: modalities, encoders, token cost | Huyen, *Multimodality and LMMs*; Hands-On LLMs ch. 9 |
| 02 | Vision-language models in practice: image input, resolution, prompting with images | *Vision Language Models* (O'Reilly, 2026); LLaVA; Molmo |
| 03 | Documents: OCR, layout, charts and tables, OCR vs. VLM | *Vision Language Models*; ledger papers |
| 04 | Multimodal RAG: page-as-image retrieval, captioning, mixed indexes | ColPali; *Vision Language Models* RAG chapter |
| 05 | Speech in and out: ASR, TTS, cascaded vs. end-to-end | HF Audio Course; Whisper; Moshi; Qwen2.5-Omni |
| 06 | Generating images and video: APIs, editing, cost, provenance | HF Diffusers docs; ledger papers |
| 07 | Evaluating multimodal systems: VLM hallucination, grading non-text output | *Hallucination in LVLMs*; MMMU |
| 08 | Failure modes and when to fall back to text | synthesis |

---

## Layout

```
notes/                       topic notes (see Planned notes)
references.md                papers and books, mapped to notes
sources/<book-slug>/chNN-*.pdf   book chapters
sources/<author-year-slug>.pdf   papers
sources/images/              figures used in notes and slides
slides/                      lecture deck (deck.yaml → .pptx + .pdf)
```

## References

See [references.md](references.md).
