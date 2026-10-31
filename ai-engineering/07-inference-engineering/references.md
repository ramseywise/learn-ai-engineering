---
origin: curated
sources:
  - "Fregly, AI Systems Performance Engineering (O'Reilly, 2025)"
  - "Huyen, AI Engineering (O'Reilly, 2025)"
  - "Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024)"
confidence: medium
cleaned: 2026-10-31
---
# Inference Engineering — Papers and Further Reading

> The books and papers behind the chapters in [notes/](notes/). PDFs are in [sources/](sources/). Course index: [README](README.md).

---

## Books

| | Source | Notes |
|---|---|---|
| ★ | Chris Fregly, *AI Systems Performance Engineering* (O'Reilly, 2025). Chapter PDFs in [sources/ai-systems-performance-engineering/](sources/ai-systems-performance-engineering/). Folded in as: ch. 1 → [01](notes/01-why-inference-is-its-own-discipline.md#throughput-cost-and-goodput); ch. 2, 6 → [02](notes/02-the-hardware.md); ch. 3–5 → [03](notes/03-the-platform.md); ch. 7–12 → [04](notes/04-kernels.md); ch. 13–14 → [05](notes/05-compilers-and-frameworks.md); ch. 15–16 → [06](notes/06-serving-at-scale.md), [08](notes/08-adaptive-inference.md#speculative-decoding); ch. 17–18 → [07](notes/07-prefill-decode-kv-cache.md); ch. 19 → [07](notes/07-prefill-decode-kv-cache.md#chunked-prefill), [08](notes/08-adaptive-inference.md#dynamic-precision); ch. 20 and appendix → [09](notes/09-checklist-and-ai-assisted-tuning.md). Gives three different definitions of goodput (ch. 1, 16); its KV-size formula ignores GQA in ch. 18 but not ch. 17; says speculative verification is "one by one" against its own Fig. 15-8; recommends TP=8 for prefill and then picks PP (ch. 18). Several arithmetic slips are flagged in the notes. Notes cite it as `(*AISPE*, ch. N)` | 01–09 |
| ★ | Chip Huyen, *AI Engineering* (O'Reilly, 2025), ch. 9. PDF in [sources/huyen-ai-engineering/](sources/huyen-ai-engineering/). Folded in as: ch. 9 → [01](notes/01-why-inference-is-its-own-discipline.md) (metrics, bottlenecks, goodput), [05](notes/05-compilers-and-frameworks.md#what-a-compiler-does-for-inference), [06](notes/06-serving-at-scale.md#batching), [07](notes/07-prefill-decode-kv-cache.md#prompt-caching-in-provider-apis), [08](notes/08-adaptive-inference.md#stacking-the-gains). Fig. 9-4's caption counts three requests meeting the SLO where the bars show two; its HBM bandwidth figure (up to 1.5 TB/s) and 2024 prompt-cache prices are dated. Notes cite it as `(*AI Engineering*, ch. 9)` | 01, 05, 06, 07, 08 |
| ★ | Paul Iusztin and Maxime Labonne, *LLM Engineer's Handbook* (Packt, 2024), ch. 8 and 10. Chapter PDFs in [generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/](../../generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/). Folded in as: ch. 8 → [05](notes/05-compilers-and-frameworks.md#static-kv-cache-the-handbooks-recipe), [06](notes/06-serving-at-scale.md), [07](notes/07-prefill-decode-kv-cache.md#sizing-the-cache), [08](notes/08-adaptive-inference.md#quantization); ch. 10 → [06](notes/06-serving-at-scale.md#deployment-shapes) (SageMaker and IAM specifics dropped). Says GPTQ is 4-bit only and that LLM.int8 outliers are weights (both wrong); lists speculative decoding as TensorRT-LLM only (dated); suggests autoscaling on GPU util and WebSockets for streaming. Notes cite it as `(*LLM Engineer's Handbook*, ch. N)` | 05, 06, 07, 08 |

## Core papers

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|

## AI Papers of the Week

Recent papers picked up by the weekly [DAIR](https://github.com/dair-ai/AI-Papers-of-the-Week) sync (`make papers`, then `/papers`).

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
