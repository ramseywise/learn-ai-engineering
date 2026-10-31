---
origin: curated
sources:
  - "Phoenix & Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 7, 9"
confidence: medium
cleaned: 2026-10-31
---
# Multimodal Engineering — Papers and Further Reading

> The books and papers behind the notes in [notes/](notes/). PDFs are in [sources/](sources/). Course index: [README](README.md).

---

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| ★ Phoenix & Taylor, *Prompt Engineering for Generative AI* (O'Reilly, 2024). Chapter PDFs live in [generative-ai/01-llm-fundamentals/sources/prompt-engineering-for-generative-ai/](../../generative-ai/01-llm-fundamentals/sources/prompt-engineering-for-generative-ai/). Folded in as: ch. 7 (diffusion models) → [06](notes/06-generating-images-and-video.md#how-a-diffusion-model-makes-an-image), [provenance](notes/06-generating-images-and-video.md#provenance-and-training-data-risk); ch. 9 (Stable Diffusion) → [06](notes/06-generating-images-and-video.md#the-controls) controls, editing, customizing, hosted vs self-hosted. Corrected: LoRA "adds new layers"; SDXL's 6.6B is base + refiner. Dated: model lineup, LoRA "experimental". Ch. 8 (Midjourney) not used. Notes cite it as `(*Prompt Engineering for GenAI*, ch. N)` | ch. 7, 9 | ✓ (in generative-ai/01) | 06 |
| Noyan, Marafioti, Farré, Zohar, *Vision Language Models: Building VLMs with Hugging Face* (O'Reilly, 2026). Not yet in the repo | the whole book: VLM architecture, document understanding, zero-shot use, multimodal RAG | not in repo | 02 · 03 · 04 |
| Alammar & Grootendorst, *Hands-On Large Language Models* (O'Reilly, 2024). Not yet in the repo; code is Apache-2.0 at [HandsOnLLM](https://github.com/HandsOnLLM/Hands-On-Large-Language-Models) | ch. 9 Multimodal LLMs | not in repo | 01 · 02 |

## Courses and repos

| Resource | Why read it | Maps to |
|---|---|---|
| [Hugging Face Audio Course](https://huggingface.co/learn/audio-course) | ASR, TTS and audio classification with open models, with runnable notebooks | 05 |
| [Hugging Face Computer Vision Course](https://huggingface.co/learn/computer-vision-course), unit 4 (multimodal models) | CLIP, VLMs and their supplementary reading list | 01 · 02 |
| Huyen, [*Multimodality and Large Multimodal Models*](https://huyenchip.com/2023/10/10/multimodal.html) (2023) | The clearest single overview of how LMMs are built (CLIP, Flamingo, BLIP-2, LLaVA) | 01 |
| CMU [11-777 Multimodal Machine Learning](https://cmu-multicomp-lab.github.io/mmml-course/) | Lecture course on representation, alignment and fusion, for theory depth | 01 |
| [Awesome-Multimodal-Large-Language-Models](https://github.com/BradyFU/Awesome-Multimodal-Large-Language-Models) | Maintained index of MLLM papers, benchmarks and datasets, for gap detection | — |

## Core papers

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| Faysse et al., [ColPali: Efficient Document Retrieval with Vision Language Models](https://arxiv.org/abs/2407.01449) (2024) | Retrieves PDF pages as images and skips OCR. This is the baseline for multimodal RAG | not yet downloaded | 04 |
| Radford et al., [Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)](https://arxiv.org/abs/2212.04356) (2022) | The default open ASR model, and the cascaded-pipeline baseline | not yet downloaded | 05 |

## AI Papers of the Week

Recent papers picked up by the weekly [DAIR](https://github.com/dair-ai/AI-Papers-of-the-Week) sync (`make papers`, then `/papers`).
205 multimodal papers are parked in the ledger under topic `multimodal`. The ones triaged at
relevance 1 include LLaVA, PaLM-E, OpenFlamingo, CogAgent, MoE-LLaVA, *Hallucination in LVLMs*,
GPT-4o, Moshi, Llama 3.2, Molmo, *Conversational Speech Model* and Qwen2.5-Omni. They are routed
here once `multimodal` is a home in `scripts/papers/potw.py`.

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
