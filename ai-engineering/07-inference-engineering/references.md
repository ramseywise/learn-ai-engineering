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
| Yuksekgonul et al., [*Learning to Discover at Test Time*](https://arxiv.org/abs/2601.16175) (Jan 2026) | Test-time RL on gpt-oss-120b writes a TriMul kernel at 1,161 µs on H100 vs 1,371 µs for the best human; fusion is what the search finds. Ablation: 1,203 µs (entropic objective) vs 1,986 (expected reward) vs 5,274 (no reuse); ~$500 a run. Folded into post-training | [ttt-discover](../../generative-ai/05-RL/sources/ttt-discover-learning-discover-test-2026.pdf) | [04](notes/04-kernels.md#fusion) |
| Lu et al., [*MoBA: Mixture of Block Attention for Long-Context LLMs*](https://arxiv.org/abs/2502.13189) (Feb 2025) | Top-k block-sparse attention: Llama-3.1-8B at 1M tokens matches full attention on RULER (0.782 vs 0.785) with 6.5× faster attention in prefill. Vendor report; decode stays dense | [moba-2025](sources/moba-2025.pdf) | [07](notes/07-prefill-decode-kv-cache.md#shrinking-the-cache) |
| ★ Shah et al., [*FlashAttention-3*](https://arxiv.org/abs/2407.08608) (Jul 2024) | Warp specialization and GEMM-softmax pingpong on H100: 740 TFLOPs/s (75%) only at head dim 256; ~616–648 (~65%) at head dim 128; 1.5–2.0× FA2 | [flashattention-3-2024](sources/flashattention-3-2024.pdf) | [04](notes/04-kernels.md#warp-specialization) |
| Défossez et al., [*Moshi: a speech-text foundation model for real-time dialogue*](https://arxiv.org/abs/2410.00037) (Sep 2024) | Quantization depends on the fine-tune: 7B Helium at W4A8 (block 32) keeps MMLU at 52.97 vs 54.3 BF16, but the speech-instruct Moshi falls from 49.7 to 42.2. PDF filed under multimodal | [moshi](../08-multimodal-engineering/sources/moshi-2024.pdf) | [08](notes/08-adaptive-inference.md#weight-formats-you-will-meet) |
| ★ DeepSeek-AI, [*DeepSeek-V2*](https://arxiv.org/abs/2405.04434) (May 2024) | Introduces MLA: 4–14% of MHA's KV with slightly better scores in MoE ablations; headline 93.3% KV cut and 5.76× throughput stack FP8 and KV quantization on top | [deepseek-v2](sources/deepseek-ai-2024-deepseek-v2.pdf) | [07](notes/07-prefill-decode-kv-cache.md#shrinking-the-cache) |
| Zhao et al., [*GaLore*](https://arxiv.org/abs/2403.03507) (Mar 2024) | Low-rank gradient projection cuts optimizer memory up to 65.5%; 7B pre-training fits on a 24 GB GPU. Training, not inference | [galore](sources/zhao-2024-galore.pdf) | — (training: [llm-fund 02](../../generative-ai/01-llm-fundamentals/notes/02-training-and-adapting.md#parameter-efficient-fine-tuning)) |
| Song et al., [*PowerInfer*](https://arxiv.org/abs/2312.12456) (Dec 2023) | Hot neurons on GPU, cold on CPU: 7.23× llama.cpp on one RTX 4090 at batch 1 (FP16). Needs ReLU-sparse models | [powerinfer-2023](sources/powerinfer-2023.pdf) | [08](notes/08-adaptive-inference.md#early-exit-and-layer-skipping) |
| Sun et al., [*A Simple and Effective Pruning Approach for LLMs (Wanda)*](https://arxiv.org/abs/2306.11695) (Jun 2023) | Retraining-free pruning by \|W\|·‖X‖: LLaMA-7B at 50% goes 5.68→7.26 perplexity, 70% breaks it; 2:4 gives 1.24× end to end | [wanda](sources/sun-2023-simple-effective-pruning-approach-large.pdf) | [08](notes/08-adaptive-inference.md#quantization) |
| Chen et al., [*FrugalGPT*](https://arxiv.org/abs/2305.05176) (May 2023) | Cascade over 12 APIs matches GPT-4 at 59–98% lower cost on short-answer tasks (2023 prices). Needs labelled data for the scorer | [frugalgpt](sources/chen-2023-frugalgpt.pdf) | [06](notes/06-serving-at-scale.md#routing) |
