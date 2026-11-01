# 07 — Inference Engineering

> Depth layer. Summary: no dedicated interview guide yet; the closest is 9-system-design, from [00-start-here](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md).
> Position in the stack: *the substrate every other layer runs on*.
> Jump to: [Scope](#scope) · [Reading order](#reading-order) · [References](#references)

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

## Reading order

Notes are written from the sources by the `/chapter` skill, one source chapter at a time.

| # | Note | Main sources |
|---|---|---|
| 01 | [Why inference is its own discipline: latency, throughput, cost](notes/01-why-inference-is-its-own-discipline.md) | Huyen ch. 9; *AI Systems Performance Engineering* ch. 1 |
| 02 | [The hardware: GPUs, memory hierarchy, interconnect](notes/02-the-hardware.md) | ch. 2, 6 |
| 03 | [The platform: OS, containers, Kubernetes, storage, networking](notes/03-the-platform.md) | ch. 3–5 |
| 04 | [Kernels: occupancy, memory access, arithmetic intensity, pipelining](notes/04-kernels.md) | ch. 7–12 |
| 05 | [Compilers and frameworks: profiling, torch.compile, Triton, XLA](notes/05-compilers-and-frameworks.md) | ch. 13–14; Huyen ch. 9; *LLM Engineer's Handbook* ch. 8 |
| 06 | [Serving at scale: deployment, batching, routing, parallelism, autoscaling](notes/06-serving-at-scale.md) | ch. 15–16; Huyen ch. 9; *LLM Engineer's Handbook* ch. 8, 10 |
| 07 | [Prefill, decode and the KV cache](notes/07-prefill-decode-kv-cache.md) | ch. 17–19; Huyen ch. 9; *LLM Engineer's Handbook* ch. 8 |
| 08 | [Adaptive inference: speculative decoding, quantization, early exit](notes/08-adaptive-inference.md) | ch. 15, 16, 19; Huyen ch. 9; *LLM Engineer's Handbook* ch. 8 |
| 09 | [Checklist and AI-assisted tuning](notes/09-checklist-and-ai-assisted-tuning.md) | ch. 20, appendix |

---

## Layout

```
notes/                       topic notes (see Reading order)
references.md                papers and books, mapped to notes
sources/<book-slug>/chNN-*.pdf   book chapters
sources/<author-year-slug>.pdf   papers
sources/images/              figures used in notes and slides
slides/                      lecture deck (deck.yaml → .pptx + .pdf)
```

Lecture deck: [`slides/inference-engineering.pptx`](slides/inference-engineering.pptx), a 4-part talk following one Llama-7B on an A100 from its first bandwidth sum to 244.7 tokens/s. Build with `make slides PILLAR=07-inference-engineering`.

## References

See [references.md](references.md).
