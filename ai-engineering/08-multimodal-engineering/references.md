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
| Yang et al., [The Dawn of LMMs: Preliminary Explorations with GPT-4V(ision)](https://arxiv.org/abs/2309.17421) (2023) | A 166-page catalogue of hand-picked GPT-4V examples, deliberately without benchmarks. Useful for visual referring prompting (drawing arrows and boxes on the input image) and for using a VLM to judge or rewrite text-to-image prompts. Weak on reliability: the authors say some cases work only with tailored prompts | [2309.17421](sources/yang-2023-dawn-lmms.pdf) | [06](notes/06-generating-images-and-video.md#sweep-dont-guess), 02 (planned) |
| Bai et al., [Qwen-VL: A Versatile Vision-Language Model for Understanding, Localization, Text Reading, and Beyond](https://arxiv.org/abs/2308.12966) (2023) | A 9.6B open VLM trained in 3 stages. It reaches 448 px input and 256 compressed visual tokens, and emits bounding boxes as plain text. DocVQA 65.1, TextVQA 63.8, RefCOCO val 89.4. Mixing pure-text data into training kept MMLU at 50.7 vs 49.9 for its LLM init. Caveat: VQAv2, GQA, DocVQA and TextVQA are in its stage-2 training mix, so those scores are not zero-shot | [2308.12966](sources/bai-2023-qwen-vl.pdf) | 02 (planned), 03 (planned) |
| Awadalla et al., [OpenFlamingo: An Open-Source Framework for Training Large Autoregressive Vision-Language Models](https://arxiv.org/abs/2308.01390) (2023) | An open replication of Flamingo (3B–9B) that reaches 80–89% of Flamingo's scores. Its useful negative results: on VQAv2, OF-9B scores 30.5% on counting questions vs 70.6% on yes/no. Retrieving similar in-context examples adds +19.8 AUC on HatefulMemes (32-shot) but costs −20.3 CIDEr on Flickr30K (0-shot), where the model parrots neighbours' captions | [2308.01390](sources/awadalla-2023-openflamingo.pdf) | 02 (planned) |
| Dai et al., [InstructBLIP: Towards General-purpose Vision-Language Models with Instruction Tuning](https://arxiv.org/abs/2305.06500) (2023) | Instruction tuning BLIP-2's Q-Former on 13 datasets, with 13 held out. The clean result: on unseen datasets, instruction templates beat plain multitask training (held-out avg 52.9 vs 45.5–46.8, FlanT5-XL), while the two tie on seen ones | [2305.06500](sources/dai-2023-instructblip.pdf) | 02 (planned) |
| Liu et al., [Visual Instruction Tuning (LLaVA)](https://arxiv.org/abs/2304.08485) (2023) | The recipe most open VLMs copied: CLIP ViT-L/14, a linear projector and Vicuna, tuned on 158K GPT-4-generated instructions. It is evaluated by GPT-4 as judge on small sets (30 COCO images; 24 in-the-wild images). Its own failure analysis is the useful part: the model says "yes" to strawberry yogurt when the fridge holds only yogurt and strawberries ("bag of patches") | [2304.08485](sources/liu-2023-visual-instruction-tuning.pdf) | 02 (planned), 07 (planned) |
| Oquab et al., [DINOv2: Learning Robust Visual Features without Supervision](https://arxiv.org/abs/2304.07193) (2023) | Self-supervised image features that match OpenCLIP on ImageNet linear probe (86.5 vs 86.2) and beat it by a wide margin on retrieval and dense tasks (Oxford-Hard 54.0 vs 19.7). The case for choosing a non-CLIP encoder when pixels matter more than captions | [2304.07193](sources/oquab-2023-dinov2.pdf) | 01 (planned) |
| Wu et al., [Visual ChatGPT: Talking, Drawing and Editing with Visual Foundation Models](https://arxiv.org/abs/2303.04671) (2023) | ChatGPT orchestrating 22 vision tools through a prompt manager. Worth reading for the tool-description format and the lineage-encoding filenames. Case studies only, no quantitative eval | [2303.04671](sources/wu-2023-visual-chatgpt.pdf) | [06](notes/06-generating-images-and-video.md#editing-img2img-inpainting-control-images) |
| Driess et al., [PaLM-E: An Embodied Multimodal Language Model](https://arxiv.org/abs/2303.03378) (2023) | Image and state embeddings injected into PaLM, up to 562B. The transferable finding is about forgetting: unfreezing the LLM for multimodal training lost 87.3% of NLG performance at 12B but only 3.9% at 562B | [2303.03378](sources/driess-2023-palm-e.pdf) | 02 (planned) |
| Huang et al., [Language Is Not All You Need: Aligning Perception with Language Models (Kosmos-1)](https://arxiv.org/abs/2302.14045) (2023) | A 1.6B MLLM trained from scratch on interleaved web data. On web-page QA (WebSRC), screenshot + extracted text gets 31.3 F1, against 17.9 for text alone and 10.6 for the image alone: keep the text next to the pixels | [2302.14045](sources/huang-2023-language-not-all-you-need.pdf) | 02 (planned), 03 (planned) |
| Akkus et al., [Multimodal Deep Learning](https://arxiv.org/abs/2301.04856) (2023) | A 272-page LMU student seminar book covering image–text architectures up to 2022. Background reading only; filed as a whole book | [2301.04856](sources/akkus-2023-multimodal-deep-learning.pdf) | 01 (planned) |
