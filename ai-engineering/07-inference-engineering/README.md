# 07 — Inference Engineering

> Depth layer. Summary: no dedicated interview guide yet; the closest is 9-system-design, from [00-start-here](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md).
> Position in the stack: *the substrate every other layer runs on*.
> Jump to: [Scope](#scope) · [Planned notes](#planned-notes) · [References](#references)

---

## What it is

Inference engineering is the discipline of making a model answer fast enough and cheaply
enough to ship: how requests are batched and scheduled, where the KV cache lives, how
prefill and decode are split across hardware, and what the GPU is actually doing while it
waits. The six layers above it decide *what* the model is asked. This layer decides what
each of those calls costs in latency, throughput and money.

**Inherits the weaknesses of:** the hardware and the model. A badly sized context
([02](../02-context-engineering/README.md)) or a loop that makes ten calls where two would do
([04](../04-loop-engineering/README.md)) is a cost this layer can shave but not remove.

**Why a pillar, not a note.** Added 2026-10-31 (see [CURRICULUM.md](../../CURRICULUM.md#definition-of-done)).
The readings backlog held a full book on AI systems performance plus Huyen's inference
chapter and a steady stream of serving papers, and none of the six pillars could hold them
without turning into a GPU course.

---

## Scope

| In | Out (lives elsewhere) |
|---|---|
| Serving: batching, scheduling, routing, autoscaling | How transformers work: [generative-ai/01](../../generative-ai/01-llm-fundamentals/README.md) |
| KV cache, prefix caching, prefill/decode disaggregation | Prompt caching as a context decision: [02/04](../02-context-engineering/notes/04-retrieval.md) |
| Quantization, speculative decoding, compilers (torch.compile, Triton, XLA) | Fine-tuning and RL: [generative-ai/05](../../generative-ai/05-RL/README.md) |
| GPU architecture, CUDA kernels, memory hierarchy, profiling | Cost per task as an eval metric: [06](../06-eval/README.md) |
| Multi-node networking, storage I/O, Kubernetes for GPUs | |

---

## Planned notes

Notes are written from the sources by the `/chapter` skill, one source chapter at a time.
The outline below is the target; rename or merge as the material dictates.

| # | Note | Main sources |
|---|---|---|
| 01 | Why inference is its own discipline: latency, throughput, cost | Huyen ch. 9; *AI Systems Performance Engineering* ch. 1 |
| 02 | The hardware: GPUs, memory hierarchy, interconnect | ch. 2, 6 |
| 03 | The platform: OS, containers, Kubernetes, storage, networking | ch. 3–5 |
| 04 | Kernels: occupancy, memory access, arithmetic intensity, pipelining | ch. 7–12 |
| 05 | Compilers and frameworks: PyTorch profiling, torch.compile, Triton, XLA | ch. 13–14 |
| 06 | Serving at scale: batching, routing, multi-node inference | ch. 15–16 |
| 07 | Prefill, decode and the KV cache | ch. 17–18 |
| 08 | Adaptive inference: speculative decoding, quantization, early exit | ch. 19; Huyen ch. 9 |
| 09 | Checklist and AI-assisted tuning | ch. 20, appendix |

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
