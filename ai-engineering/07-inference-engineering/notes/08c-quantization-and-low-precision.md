---
origin: book-condensed
sources:
  - "Fregly, AI Systems Performance Engineering (O'Reilly, 2025), ch. 19"
  - "Huyen, AI Engineering (O'Reilly, 2025), ch. 9"
  - "Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), ch. 8"
  - "Lakshmanan & Hapke, Generative AI Design Patterns (O'Reilly, 2025), ch. 8"
  - https://arxiv.org/abs/2208.07339
  - https://arxiv.org/abs/2306.11695
  - https://arxiv.org/abs/2410.00037
  - https://arxiv.org/abs/2211.05102
  - https://arxiv.org/abs/2604.12374
  - https://arxiv.org/abs/1510.00149
  - https://arxiv.org/abs/2301.00774
  - https://arxiv.org/abs/2401.15024
  - https://arxiv.org/abs/2308.07633
  - https://arxiv.org/abs/2306.03078
  - https://arxiv.org/abs/2304.13013
  - https://arxiv.org/abs/2310.18313
  - https://arxiv.org/abs/2409.11055
  - https://arxiv.org/abs/2411.11843
  - https://arxiv.org/abs/2401.15347
  - https://arxiv.org/abs/2312.00678
  - https://arxiv.org/abs/2409.04833
  - https://arxiv.org/abs/2402.17764
  - https://arxiv.org/abs/1308.3432
  - https://arxiv.org/abs/2406.02528
  - https://arxiv.org/abs/2410.00907
  - https://arxiv.org/abs/2412.18653
  - https://arxiv.org/abs/2411.04330
  - https://arxiv.org/abs/2505.13840
  - https://arxiv.org/abs/2504.12285
confidence: medium
cleaned: 2026-11-08
---
# 8c — Quantization and Low-Precision Inference

> Decode is bandwidth-bound, so storing weights and the KV cache in fewer bits is the most reliable way to move fewer bytes per token. Unlike exact speculative decoding it changes the numbers the model computes, so every format change needs its own eval.

[Chapter 8](08-adaptive-inference.md) covers the techniques that spend decode's idle compute: speculative decoding, diffusion drafting, early exit and distillation. This chapter is the other half of the pair: the quantization schemes, the weight and floating-point formats you will meet, ternary weights, and KV-cache quantization. [Stacking the gains](08-adaptive-inference.md#stacking-the-gains) there puts both halves back together on one model.

```text
Weight bytes read per decode step, 7B parameters (arithmetic: parameters x bits / 8, ignoring scales and the KV cache)

FP16     16 bits  |################################|  14.0 GB
FP8       8 bits  |################                |   7.0 GB
INT4      4 bits  |########                        |   3.5 GB
Ternary  ~1.58    |###                             |  ~1.4 GB
```

---

## Quantization

Quantization stores numbers in fewer bits. Weight-only quantization is "by far the most popular approach", because it works out of the box and decode is bandwidth-bound (*AI Engineering*, ch. 9). Pope et al. measured it on PaLM 540B on 64 TPU v4 chips: int8 weights cut decode from 36.9 to 28.5 ms/token at batch 64. The cost benefit is more than 2× at small batch and near zero at large batch, where weight loading is no longer the bottleneck ([arXiv:2211.05102](https://arxiv.org/abs/2211.05102) (Pope et al., MLSys 2023)). Huyen also notes the floor: you can't go below 1 bit per value. Zhu et al. survey the whole compression toolbox for LLMs: quantization, pruning, distillation and [low-rank](../../../generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block.md#matrix-products-transpose-and-rank) ([arXiv:2308.07633](https://arxiv.org/abs/2308.07633) (Zhu et al., TACL 2024)).

Pruning is older than LLMs. Deep Compression pruned 9–13× of the connections in CNNs (with retraining), then quantized the rest to about 5 bits, shrinking AlexNet 35× and VGG-16 49× with no accuracy loss ([arXiv:1510.00149](https://arxiv.org/abs/1510.00149) (Han et al., ICLR 2016)). Pruning can remove more than 90% of weights in small research networks (Frankle & Carbin, 2019), but LLMs tolerate much less. SparseGPT prunes in one shot with no retraining, using an approximate second-order weight update. It takes OPT-175B to 50% sparsity in under 4.5 hours on one A100, and perplexity moves from 8.35 to 8.21 (8.74 at 2:4); magnitude pruning at the same 50% collapses the model. Smaller models pay more (OPT-2.7B: 12.47 → 13.48), and the 2:4 speedup it reports is 1.54–1.79× at the layer level, not end to end ([arXiv:2301.00774](https://arxiv.org/abs/2301.00774) (Frantar & Alistarh, ICML 2023)). Wanda prunes by weight magnitude times input-activation norm, with no retraining: LLaMA-7B at 50% unstructured sparsity goes from 5.68 to 7.26 WikiText perplexity, but at 70% it reaches 84.5. Unstructured sparsity buys no GPU speed, and its 2:4 pattern gives ~1.6× on linear-layer matmuls but only 1.24× end to end on 7B ([arXiv:2306.11695](https://arxiv.org/abs/2306.11695) (Sun et al., 2023-06)). So pruning is rare in production. Sparse kernels need hardware support, and the gains are usually smaller than quantization's. *Structured* pruning sidesteps the kernel problem by deleting whole rows and columns, so the matrices stay dense and just get smaller. SliceGPT rotates each layer with PCA and then slices. It removes up to 25% of parameters while keeping 99%, 99% and 90% of zero-shot accuracy on Llama-2 70B, OPT-66B and Phi-2, with no recovery fine-tuning. The 25%-sliced models run up to 1.55× faster on H100s, but at 50% slicing perplexity is worse than SparseGPT's 2:4 ([arXiv:2401.15024](https://arxiv.org/abs/2401.15024) (Ashkboos et al., ICLR 2024)).

### The two basic schemes

The Handbook works both by hand (*LLM Engineer's Handbook*, ch. 8):

- **Absmax (symmetric):** scale by `127 / max|X|` and round. In its example, 0.1 in a tensor spanning [-3.0, 3.2] maps to 4.
- **Zero-point (asymmetric):** scale by the range and add an offset, so the full [-128, 127] is used even when the data is skewed.

```python
def absmax_quantize(X):
    scale = 127 / X.abs().max()
    return (scale * X).round().to(torch.int8), scale   # dequantize: q / scale
```

One max value sets the scale for the whole tensor, so a single outlier crushes everyone else into a few levels. Every serious method below is a way around outliers. Methods are either **post-training (PTQ)**, applied after training, or **quantization-aware (QAT)**, simulated during training.

### Weight formats you will meet

| Method | Idea | Notes (condition) |
|---|---|---|
| **LLM.int8** | Keep outlier feature dimensions in FP16, everything else INT8 | <1% degradation, ~20% slower than FP16 (*LLM Engineer's Handbook*, ch. 8). The paper reports no degradation up to 175B and end-to-end latency "slightly slower" than FP16. It is a memory saving, not a speedup |
| **SpQR** | Keep the ~1% most sensitive *weights* in FP16 as a sparse side matrix, the rest at 3–4 bits in small groups | Within 1% relative perplexity of FP16 on LLaMA and Falcon at 3.4–4.75 average bits; a 33B model fits a 24 GB GPU; ~15% faster than FP16. Evaluated on perplexity and zero-shot only, not generation quality ([arXiv:2306.03078](https://arxiv.org/abs/2306.03078) (Dettmers et al., ICLR 2024)) |
| **NF4** (bitsandbytes) | 4-bit levels spaced for normally distributed weights | `load_in_4bit=True`; the QLoRA format |
| **GPTQ** | Layer-wise quantization that uses second-order information to correct error | 2, 3, 4 or 8 bits; Fregly gives 4-bit GPTQ "99%+ accuracy, ~2× speed, ~4× smaller", with no model or task (*AISPE*, ch. 16) |
| **AWQ** | Protect the ~1% of weight channels with large activations by scaling them | Similar accuracy to GPTQ; the Handbook finds it slightly slower |
| **EXL2** | Mixed 2–8 bits per layer to hit a target bits-per-weight | A 70B model fits in 24 GB at 2.55 bpw (*LLM Engineer's Handbook*, ch. 8) |
| **GGUF** (llama.cpp) | Block-wise formats Q2–Q8 and importance-weighted IQ variants | Q4_K uses super-blocks of 8 blocks × 32 weights; CPU and Apple-silicon friendly. Quantizing took about an hour on a T4 in the Handbook's run |
| **QuIP#, HQQ** | Very low-bit (2–3 bit) methods | The Handbook's rule of thumb: a >30B model at low bits beats a 7–13B model at full precision |

Two corrections to the Handbook's text. It says LLM.int8's outliers are "extreme weight values (~0.1%)". In the LLM.int8 paper they are **activation** feature dimensions, which is why that method decomposes the matmul by input feature. They appear abruptly at around 6.7B parameters. At that size about 150k outliers per sequence sit in just 6 hidden dimensions, up to 20× larger than the rest, and zeroing those dimensions (0.1% of features) raises perplexity by 600–1000% ([arXiv:2208.07339](https://arxiv.org/abs/2208.07339) (Dettmers et al., NeurIPS 2022)). It also says GPTQ is "limited to 4-bit", but GPTQ supports 2, 3, 4 and 8 bits (*LLM Engineer's Handbook*, ch. 8).

How well a model survives 4 bits depends on what it was trained to do, not just its size. Kyutai's 7B Helium text model, quantized to 4-bit weights and 8-bit activations with blocks of 32, scores 52.97 on MMLU against 54.3 at BF16. The same backbone after speech instruction tuning (Moshi) falls from 49.7 to 42.2 under the same scheme, and blocks of 256 cost both models more ([arXiv:2410.00037](https://arxiv.org/abs/2410.00037) (Défossez et al., 2024-09)). Re-run the eval on the fine-tuned checkpoint you will actually serve.

Re-run it per task, too, because an average hides where 4 bits bite. EfficientLLM's inference table covers nine models from 1.5B to 34B in BF16, FP16 and weight-only INT4 on GH200s (quantization method, engine and batch size unstated). Averaged over six benchmarks, INT4 costs 0.8 to 4.3 points, but on MATH Qwen2.5-14B falls from 0.170 to 0.053 and Qwen2.5-32B from 0.402 to 0.219 while its average moves only from 0.552 to 0.510. Read the table rather than the prose: the abstract's "up to 3.9×" memory and energy saving is a size ratio the paper defines, while measured memory fell 4–34% and tokens/s rose 5–9% ([arXiv:2505.13840](https://arxiv.org/abs/2505.13840) (Yuan et al., 2025-05, preprint)).

### Low-precision floating point

On Hopper and Blackwell, the main path is low-precision *floating point* with hardware support, not integer formats (*AISPE*, ch. 16):

- **[FP8](../../../programming/computer-science/notes/04-numbers-and-memory.md#smaller-floats)** (E4M3/E5M2): 2× the Tensor Core math rate of FP16, half the bytes. NVIDIA's Transformer Engine manages per-tensor scales, either static (calibrated) or from a running history of the max absolute value (amax).
- **FP4 / NVFP4** (Blackwell): the book gives an effective ~1.8× over FP8 and ~3.5× over FP16, with no model or batch size. The book says "per-block microscaling". To be precise, NVFP4 uses 16-element blocks with an FP8 scale, while the OCP MXFP4 format uses 32-element blocks.
- **SmoothQuant**: activations have outliers and weights do not, so it moves scale from activations into weights with a per-channel factor. That makes W8A8 (8-bit weights *and* activations) work.

Fregly is inconsistent about how ready FP4 is. Ch. 17 says to prefer it where supported; ch. 18 calls it "maturing" (*AISPE*, ch. 17–18). Treat FP8 as the safe default and FP4 as something to validate per model, against your eval suite. Models that are *trained* in low precision make the inference conversion easier. Nemotron 3 Super (120B total, 12B active) was pretrained in NVFP4 on 25T tokens ([arXiv:2604.12374](https://arxiv.org/abs/2604.12374) (NVIDIA, 2026-04, preprint)). Outliers are partly a training artifact. On CLIP ViT-Huge, Wortsman et al. found that standard FP8 recipes (only simulated, at the time) work once training keeps feature magnitudes small, here via layer-scale initialized at zero ([arXiv:2304.13013](https://arxiv.org/abs/2304.13013) (Wortsman et al., NeurIPS 2023)). FP8-LM is the training version: GPT-175B on H100s (TP8, PP4, DP4) trains 75% faster than BF16 Megatron-LM with 39% less memory (FP8 gradients and all-reduce, FP8 first Adam moment, 6 bytes per parameter against 16). The 75% compares micro-batch 4 with BF16 at 1; at equal micro-batch it is 21%, and the 175B run saw only 40B tokens. An FP8 second moment diverges. It says nothing about FP8 serving ([arXiv:2310.18313](https://arxiv.org/abs/2310.18313) (Peng et al., 2023-10, preprint)).

### Below 2 bits: ternary weights

Going below 4 bits usually means training the model that way, not converting it afterwards. BitNet b1.58 trains every weight as {-1, 0, +1}, passing gradients through the rounding with the straight-through estimator ([arXiv:1308.3432](https://arxiv.org/abs/1308.3432) (Bengio et al., 2013-08, preprint)). It matches an FP16 LLaMA-style model from 3B parameters on the same 100B tokens, with 2.71× lower decode latency and 3.55× less memory; below 3B it still trails ([arXiv:2402.17764](https://arxiv.org/abs/2402.17764) (Ma et al., 2024-02, preprint)). MatMul-free LMs also replace attention with a ternary recurrent token mixer. Up to 2.7B they come within a point of Transformer++ (49.9 vs 50.7 average), and the gap narrows with scale ([arXiv:2406.02528](https://arxiv.org/abs/2406.02528) (Zhu et al., 2024-06, preprint)). Two cautions apply. First, the energy wins in this line of work need hardware that does not exist yet. L-Mul's "95% less energy" for element-wise multiplies is a gate-count estimate, simulated on GPUs ([arXiv:2410.00907](https://arxiv.org/abs/2410.00907) (Luo & Sun, 2024-10, preprint)). Second, smaller weights are not faster on their own. 1.58-bit FLUX quantizes a text-to-image model's weights to ternary for 7.7× less storage and 5.1× less memory, but latency improves only 5% on an A100, because activations stay in 16-bit ([arXiv:2412.18653](https://arxiv.org/abs/2412.18653) (Yang et al., 2024-12, preprint)).

BitNet b1.58 2B4T tested the recipe at a larger scale: 2B parameters trained from scratch on 4T tokens, ternary weights with int8 activations. After instruction tuning its average over 16 benchmarks is 54.19, against 55.23 for Qwen2.5-1.5B, and it trails that model on MMLU (53.17 vs 60.25) and HumanEval+ (38.40 vs 50.60). Non-embedding memory is 0.4 GB against 2.6 GB for Qwen2.5-1.5B. Against that model quantized after training, on three benchmarks (MMLU, GSM8K, IFEval) it averages 55.01 against 52.15 for GPTQ INT4 and 51.17 for AWQ INT4 (both 0.7 GB), and 55.72 for bf16. CPU decoding takes 29 ms per token on a laptop Core i7-13800H, against 41 to 124 ms for the peers. That compares bitnet.cpp with llama.cpp for the others. The 0.028 J per token energy figure is an arithmetic-only estimate at 7 nm, not a measurement. The report gives no GPU latency, and the authors list scaling to 7B and 13B as future work ([arXiv:2504.12285](https://arxiv.org/abs/2504.12285) (Ma et al., 2025-04, preprint)).

Bi-Mamba binarizes the linear layers of Mamba-2 and trains them against a LLaMA2-7B teacher on 105B tokens: 2.7B averages 50.6 on seven zero-shot tasks against 59.6 for FP16. Accuracy is simulated; one real CPU run (llama.cpp, M4 Pro) cuts memory from 5.03 to 1.04 GB ([arXiv:2411.11843](https://arxiv.org/abs/2411.11843) (Tang et al., TMLR 2025)).

How long the model was trained changes what quantization costs. Kumar et al. trained 465 OLMo-style Transformer++ runs on Dolma (30M to 220M non-embedding parameters, up to 26B tokens, 3 to 16 bits) and quantized after training with GPTQ. The loss that post-training quantization adds grows as a power law in tokens per parameter and exponentially as bits fall (fit R² 0.97, INT3 to INT6). Past some data size, extra pretraining makes the quantized model worse, and at equal data larger models lose less. For training precision, fitted on integer-type runs, the compute-optimal value is about 7 to 8 bits, under a cost model that is linear in bits. Real kernels give under 2× for halving the bits. It measures loss only, on small models, and the authors call the fitted constants unlikely to be reusable ([arXiv:2411.04330](https://arxiv.org/abs/2411.04330) (Kumar et al., 2024-11, preprint)).

Lee et al. map where 4-bit breaks on instruction-tuned Llama 3.x (GPTQ, AWQ, SmoothQuant, FP8 against FP16; OpenLLM Leaderboards v1 and v2 and MT-Bench; tools and calibration sets differing by row). **Size decides:** Llama-3.2-1B with GPTQ W4A16 loses 25.32 points on GSM8k, while Llama-3.1-70B FP8 W8A8 matches FP16 (v1 average 78.55 vs 78.76). **Averages hide collapses:** 405B with AWQ W4A16 averages 82.20, above the FP16 70B's 78.76 at 202.5 GB against 140 GB, yet its IFEval falls from 76.18 to 47.52; SmoothQuant W8A8 fails at 405B, up to 10.86 points under FP8. Task difficulty does not predict loss. It measures accuracy and storage only, no latency ([arXiv:2409.11055](https://arxiv.org/abs/2409.11055) (Lee et al., 2024-09, preprint)).

Three surveys (literature to early 2024) quote other papers and cover static compression only, with no KV quantization or adaptive precision: Park et al. ([arXiv:2401.15347](https://arxiv.org/abs/2401.15347), 2024-01, preprint) on AWQ up to 3.9× at LLaMA2-70B, Ding et al. ([arXiv:2312.00678](https://arxiv.org/abs/2312.00678), 2023-12, preprint) on 50% sparsity needing 2:4 hardware to pay, Rostam et al. ([arXiv:2409.04833](https://arxiv.org/abs/2409.04833), 2024-09, preprint) with per-system numbers that are not comparable across rows.

Quantization changes outputs, unlike exact speculative decoding. Every format change needs an eval run ([the Eval pillar](../../../generative-ai/08-eval/README.md)), not just a perplexity check.

---

## KV-cache quantization

At long contexts and large batches, the KV cache, not the weights, dominates memory and bandwidth ([07](07-prefill-decode-kv-cache.md#sizing-the-cache)). Quantizing it to 8 or 4 bits roughly halves or quarters that traffic.

Fregly's recipe uses a **residual window** (*AISPE*, ch. 19). The most recent tokens, which attention weights most heavily, stay at full precision, and older entries are stored in 4 bits. In Hugging Face this is a cache option:

```python
out = model.generate(**inputs, cache_implementation="quantized",
                     cache_config={"nbits": 4, "residual_length": 128})
```

Production engines (vLLM, TensorRT-LLM, SGLang) expose FP8 KV cache as a flag, which is the common first step. Validate long-context tasks after enabling it, since errors accumulate over long sequences.

The same chapter describes **SpeCache**, under a figure titled "Speculative decoding with SpeCache". Despite the name, it is not speculative decoding. It *prefetches* KV blocks predicted to be needed, to hide transfer latency from offloaded cache tiers. It is a KV-tiering technique and belongs with [07](07-prefill-decode-kv-cache.md#prefix-caching).

---

## Where the books disagree

| Topic | Disagreement | Read it as |
|---|---|---|
| LLM.int8 outliers | Handbook "weights" vs the paper | Activation features |
| GPTQ bit-widths | Handbook "4-bit only" | 2/3/4/8 |
| FP4 readiness | Fregly ch. 17 "prefer" vs ch. 18 "maturing" | Validate per model |

## Working reference

- Start with FP8 weights (Hopper/Blackwell) or 4-bit AWQ/GPTQ (older GPUs). Run your eval suite, not just perplexity.
- Enable FP8 KV cache for long contexts, and re-test long-context tasks.

## Pitfalls

- **Treating quantization as exact.** Symptom: a format change ships on a perplexity check, and a product task regresses. Unlike exact speculation, quantization changes outputs. Fix: run the eval suite on every format change ([the Eval pillar](../../../generative-ai/08-eval/README.md)).
- **Absmax with an outlier.** Symptom: most values collapse into a few levels, since one maximum sets the scale for the whole tensor. Fix: use a method built around outliers, such as GPTQ, AWQ, LLM.int8 or FP8 with per-tensor scales.
- **Assuming FP4 is ready.** Symptom: a model that was fine in FP8 degrades on 4-bit floats. Fregly himself says both "prefer it" and "maturing". Fix: default to FP8, and validate FP4 per model against your evals.
- **Quantizing KV without a long-context test.** Symptom: quality decays as sequences grow, since errors accumulate. Fix: keep a residual window at full precision (`residual_length`), and evaluate long-context tasks.

## Try it

1. Apply absmax by hand: what does 0.1 map to in a tensor spanning [-3.0, 3.2]? Now add one outlier so the maximum is 32.

   <details><summary>Answer</summary>

   127 / 3.2 × 0.1 ≈ 3.97, which rounds to 4, the Handbook's answer. With a maximum of 32: 127 / 32 × 0.1 ≈ 0.40, which rounds to 0. One value erased the distinction between 0.1 and zero, which is why the serious methods all work around outliers.

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| Speculation and quantization both speed things up. What's the difference for quality? | Speculative decoding with the standard rejection-sampling rule keeps the output distribution. Quantization changes outputs, so every format change needs an eval run, and perplexity alone isn't enough. |
| FP8 or FP4 on Blackwell? | FP8 is the safe default, with 2× FP16's tensor-core math rate and half the bytes. The book gives FP4 an effective ~1.8× over FP8 with no model or batch size, so validate it per model. |

## Next

[08b-serving-encoders-and-vision-models.md](08b-serving-encoders-and-vision-models.md): the same questions for models that aren't only a decode loop, embedding encoders and vision-language models. Back to [08-adaptive-inference.md](08-adaptive-inference.md) for stacking the gains, dynamic precision and early exit.
