---
origin: book-condensed
sources:
  - "Fregly, AI Systems Performance Engineering (O'Reilly, 2025), ch. 15, 16, 19"
  - "Huyen, AI Engineering (O'Reilly, 2025), ch. 9"
  - "Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), ch. 8"
  - https://arxiv.org/abs/2302.01318
  - https://arxiv.org/abs/2208.07339
  - https://pytorch.org/blog/accelerating-generative-ai-2/
  - https://arxiv.org/abs/2306.11695
  - https://arxiv.org/abs/2312.12456
  - https://arxiv.org/abs/2410.00037
  - https://arxiv.org/abs/2211.05102
  - https://arxiv.org/abs/2401.10774
  - https://arxiv.org/abs/2406.16858
  - https://arxiv.org/abs/2403.00835
  - https://arxiv.org/abs/2604.12374
  - https://arxiv.org/abs/2511.14617
  - https://arxiv.org/abs/2408.11049
  - https://arxiv.org/abs/2506.17298
  - https://arxiv.org/abs/2602.08676
  - https://arxiv.org/abs/2509.25188
  - https://arxiv.org/abs/2510.14973
  - https://arxiv.org/abs/1510.00149
  - https://arxiv.org/abs/2301.00774
  - https://arxiv.org/abs/2401.15024
  - https://arxiv.org/abs/2308.07633
  - https://arxiv.org/abs/2306.03078
  - https://arxiv.org/abs/2304.13013
  - https://arxiv.org/abs/2402.17764
  - https://arxiv.org/abs/1308.3432
  - https://arxiv.org/abs/2406.02528
  - https://arxiv.org/abs/2410.00907
  - https://arxiv.org/abs/2412.18653
  - https://arxiv.org/abs/2404.02258
  - https://arxiv.org/abs/2510.12773
  - https://arxiv.org/abs/2410.20672
  - https://arxiv.org/abs/2503.24377
confidence: medium
cleaned: 2026-10-31
---
# 8 — Adaptive Inference

> Decode leaves the GPU's compute mostly idle while it waits on memory. Each technique here spends some of that idle compute, or cuts the bytes moved, to produce more tokens per second. Some keep the output distribution exactly; others trade a little quality.

---

## Why decode leaves compute idle

Each decode step reads every weight (and the whole KV cache) to produce one token per sequence ([01](01-why-inference-is-its-own-discipline.md#two-bottlenecks-compute-and-memory-bandwidth)). At small batch sizes, arithmetic intensity is far below the roofline ridge, so Tensor Cores sit idle. Two families of fixes follow from that:

- **Do more work per weight read.** Speculative and parallel decoding check several candidate tokens in one forward pass. The check costs about as much as generating one token, because the pass is bandwidth-bound either way (*AI Engineering*, ch. 9).
- **Read fewer bytes.** Quantization shrinks weights and KV entries, so each step moves less data.

A third family adapts *per request or per token*: dynamic precision, early exit and layer skipping. These are less mature (*AISPE*, ch. 19).

Huyen's caveat applies to the whole note: if your batches already saturate compute (high MFU), the idle FLOPs are gone, and speculative methods help less or hurt (*AI Engineering*, ch. 9). Long contexts are the exception: KV reads keep large batches bandwidth-bound (see [below](#variants)).

---

## Speculative decoding

![Speculative decoding: draft model proposes, target model verifies in parallel](../sources/images/ai-systems-performance-engineering-fig15-8.png)

*Image Source: Fregly, *AI Systems Performance Engineering* (O'Reilly, 2025), Fig. 15-8*

A small **draft model** proposes *K* tokens. The large **target model** scores all *K* in one forward pass, accepts the longest prefix that matches what it would have sampled, and adds one token of its own. With the standard rejection-sampling rule, the output distribution is **identical to the target's** (Chen et al., 2023), so quality is unchanged by construction. In the figure the draft proposes four tokens and the target rejects "there", so the step yields the accepted prefix plus the target's correction.

Huyen gives three reasons it works (*AI Engineering*, ch. 9):

1. Verifying *K* tokens is parallel, like prefill; generating them is sequential.
2. Some tokens are easy, so a weak model often guesses them right.
3. Decode is bandwidth-bound, so the verification FLOPs are nearly free.

Fregly's text says the target "verifies these tokens one by one" (*AISPE*, ch. 15). That contradicts both the method and his own Fig. 15-8: verification is one parallel pass.

**Requirements.** The draft must share the target's tokenizer and vocabulary. Fregly says it should be at least **~4× faster** than the target, or the draft time eats the gain (*AISPE*, ch. 15). Acceptance rates are domain-dependent: higher for code and structured text. A larger *K* means fewer target calls but a lower chance that all *K* are accepted.

**How much speedup.** The three books disagree, because they report different conditions:

| Claim | Condition | Source |
|---|---|---|
| Latency more than halved | Chinchilla-70B with a 4B draft at 1.8 vs 14.1 ms/token; DeepMind's TPU setup | *AI Engineering*, ch. 9, citing Chen et al. 2023 |
| Theoretical *K*×, ~2× in practice, 1.5–2.5× "common" | Generic; no model or hardware | *AISPE*, ch. 15 |
| 3–4× at 90% draft acceptance; "2–4× or more" | No model or hardware; acceptance rate assumed | *LLM Engineer's Handbook*, ch. 8 |
| "Not significant" | Qwen1.5-1.8B target, 0.5B draft, on a T4 | *LLM Engineer's Handbook*, ch. 8 (its own demo) |

The Handbook's own demo is the most instructive row. When the target is already small, the draft is not much cheaper, and the gain disappears. Plan on Fregly's ~2× for a well-matched pair on a large target, and measure.

The Hugging Face API is one argument (*LLM Engineer's Handbook*, ch. 8):

```python
out = model.generate(**inputs, assistant_model=draft_model)        # draft model
out = model.generate(**inputs, prompt_lookup_num_tokens=4)         # no draft model
```

### Variants

| Method | Where drafts come from | Reported gain (condition) |
|---|---|---|
| **EAGLE** (1–3) | A light head on the target's own hidden states predicts features, then tokens | EAGLE up to ~3.5× (4-token draft); EAGLE-2 +20–40% over EAGLE; EAGLE-3 up to 1.4× over EAGLE-2, up to 6.5× over no speculation (*AISPE*, ch. 15; paper numbers, chat benchmarks). EAGLE-2 sizes its draft tree from the draft's own confidence, which tracks acceptance well: on Vicuna-13B, MT-bench, temperature 0, batch 1, it reaches 4.26× against EAGLE's 3.07× and Medusa's 2.07× in the same harness, and it stays lossless ([arXiv:2406.16858](https://arxiv.org/abs/2406.16858) (Li et al., EMNLP 2024)) |
| **Medusa** | Extra decoding heads, each predicting token *t+k*; candidates checked with tree attention | Up to 1.9× on Llama 3.1, HGX H200 (*AI Engineering*, ch. 9, citing NVIDIA); 2.2–3.6× published, ~2–3× in practice (*AISPE*, ch. 15). The paper: >2.2× with heads trained on a frozen backbone, 2.3–2.8× when trained jointly, on Vicuna 7–33B at batch 1. Its "typical acceptance" is not lossless at temperature > 0 ([arXiv:2401.10774](https://arxiv.org/abs/2401.10774) (Cai et al., ICML 2024)) |
| **Multi-token prediction (MTP)** | Heads trained with the model in pretraining draft for it at serving time | Nemotron 3 Super reuses one shared MTP head recursively and accepts 3.45 tokens per verification at draft length 7 on SPEED-Bench; acceptance still decays with draft depth, but more slowly than with separate per-offset heads ([arXiv:2604.12374](https://arxiv.org/abs/2604.12374) (NVIDIA, 2026-04, preprint)) |
| **Self-speculative** | The target with half its layers skipped acts as its own draft | ~2× (*AISPE*, ch. 15) |
| **Prompt lookup / inference with reference** | N-gram matches copied from the prompt | 2× when output overlaps input: RAG, code edits, multi-turn (*AI Engineering*, ch. 9, citing Yang et al. 2023). In RL rollouts, sibling responses to the same prompt make a better reference: Seer's per-group suffix tree gains up to 1.3× over other drafting strategies, inside a system that raises rollout throughput up to 2.04× on Moonshot's production RL jobs ([arXiv:2511.14617](https://arxiv.org/abs/2511.14617) (Qin et al., OSDI 2026)) |
| **Lookahead (Jacobi) decoding** | The same model guesses several future positions and iterates until they are consistent | (*AI Engineering*, ch. 9); no number given. Plain Jacobi rarely gets more than one token right per iteration. CLLMs fine-tune the model to jump to the fixed point, giving 2.4–3.4× on GSM8K, Spider and code, from ~1M training tokens on LLaMA-7B and with no extra heads. Because the model itself changes, the output is not that of the original model ([arXiv:2403.00835](https://arxiv.org/abs/2403.00835) (Kou et al., ICML 2024)) |

Two of the Handbook's descriptions are wrong or dated. Its Medusa passage, roughly "a 70M-parameter model approximates a 7B model", garbles how Medusa works: the heads sit on the target, they are not a separate small model. Its Table 8.1 lists speculative decoding (and pipeline parallelism) as TensorRT-LLM only. vLLM and SGLang ship both (*LLM Engineer's Handbook*, ch. 8).

**Is it a default or a special case?** Fregly's ch. 16 calls speculative decoding and Medusa "typically reserved for extreme cases" (*AISPE*, ch. 16). His own ch. 15 treats it as mainstream, and as of 2026 vLLM, SGLang and TensorRT-LLM all ship EAGLE-style speculation as a standard option. The real condition is whether decode is still bandwidth-bound. That depends on sequence length as well as batch size. For short sequences, speculation pays at low-to-moderate batch and fades as batches grow and compute fills up. For long sequences, every step also reads each sequence's KV cache, and that read grows with batch × context. Past a critical sequence length (set by the model and hardware), KV loading dominates even at large batch, so speculation helps throughput again. MagicDec measures up to 2.51× for LLaMA-3.1-8B on 8×H100 at batch 32–256, using a draft that attends over a sparse, StreamingLLM-style KV cache ([arXiv:2408.11049](https://arxiv.org/abs/2408.11049) (Sadhukhan et al., ICLR 2025)).

### Diffusion LLMs: parallel decoding without a draft

Diffusion LLMs (dLLMs) drop left-to-right generation altogether. They start from masked positions and unmask several tokens per forward pass. Inception's Mercury Coder Mini runs at 1,109 tokens/s on an H100, measured by Artificial Analysis, with coding quality close to speed-tuned frontier models. The report does not give model size, data or architecture ([arXiv:2506.17298](https://arxiv.org/abs/2506.17298) (Inception Labs, 2025-06, preprint)). LLaDA2.1-Flash (100B) peaks at 892 tokens/s on HumanEval+ in its speed mode, and the authors say a clear speed–accuracy tradeoff remains: the speed mode scores below LLaDA2.0, and speed varies widely by domain ([arXiv:2602.08676](https://arxiv.org/abs/2602.08676) (Bie et al., 2026-02, preprint)). Large headline speedups for dLLM decoders are usually measured against *vanilla dLLM decoding*, not a tuned autoregressive server. Learn2PD's 22.58× (57.51× with a KV cache) is on LLaDA at generation length 1024, and much of it comes from no longer denoising padding after the answer ends ([arXiv:2509.25188](https://arxiv.org/abs/2509.25188) (Bao et al., ICLR 2026)). Elastic-Cache's 8.7× (45.1× on long outputs) comes from not recomputing every layer's KV at every denoising step ([arXiv:2510.14973](https://arxiv.org/abs/2510.14973) (Nguyen-Tri et al., 2025-10, preprint)).

---

## Quantization

Quantization stores numbers in fewer bits. Weight-only quantization is "by far the most popular approach", because it works out of the box and decode is bandwidth-bound (*AI Engineering*, ch. 9). Pope et al. measured it on PaLM 540B on 64 TPU v4 chips: int8 weights cut decode from 36.9 to 28.5 ms/token at batch 64. The cost benefit is more than 2× at small batch and near zero at large batch, where weight loading is no longer the bottleneck ([arXiv:2211.05102](https://arxiv.org/abs/2211.05102) (Pope et al., MLSys 2023)). Huyen also notes the floor: you can't go below 1 bit per value. Zhu et al. survey the whole compression toolbox for LLMs: quantization, pruning, distillation and low-rank ([arXiv:2308.07633](https://arxiv.org/abs/2308.07633) (Zhu et al., TACL 2024)).

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

### Low-precision floating point

On Hopper and Blackwell, the main path is low-precision *floating point* with hardware support, not integer formats (*AISPE*, ch. 16):

- **FP8** (E4M3/E5M2): 2× the Tensor Core math rate of FP16, half the bytes. NVIDIA's Transformer Engine manages per-tensor scales, either static (calibrated) or from a running history of the max absolute value (amax).
- **FP4 / NVFP4** (Blackwell): the book gives an effective ~1.8× over FP8 and ~3.5× over FP16, with no model or batch size. The book says "per-block microscaling". To be precise, NVFP4 uses 16-element blocks with an FP8 scale, while the OCP MXFP4 format uses 32-element blocks.
- **SmoothQuant**: activations have outliers and weights do not, so it moves scale from activations into weights with a per-channel factor. That makes W8A8 (8-bit weights *and* activations) work.

Fregly is inconsistent about how ready FP4 is. Ch. 17 says to prefer it where supported; ch. 18 calls it "maturing" (*AISPE*, ch. 17–18). Treat FP8 as the safe default and FP4 as something to validate per model, against your eval suite. Models that are *trained* in low precision make the inference conversion easier. Nemotron 3 Super (120B total, 12B active) was pretrained in NVFP4 on 25T tokens ([arXiv:2604.12374](https://arxiv.org/abs/2604.12374) (NVIDIA, 2026-04, preprint)). Outliers are partly a training artifact. On CLIP ViT-Huge, Wortsman et al. found that standard FP8 recipes (only simulated, at the time) work once training keeps feature magnitudes small, here via layer-scale initialized at zero ([arXiv:2304.13013](https://arxiv.org/abs/2304.13013) (Wortsman et al., NeurIPS 2023)).

### Below 2 bits: ternary weights

Going below 4 bits usually means training the model that way, not converting it afterwards. BitNet b1.58 trains every weight as {-1, 0, +1}, passing gradients through the rounding with the straight-through estimator ([arXiv:1308.3432](https://arxiv.org/abs/1308.3432) (Bengio et al., 2013-08, preprint)). It matches an FP16 LLaMA-style model from 3B parameters on the same 100B tokens, with 2.71× lower decode latency and 3.55× less memory; below 3B it still trails ([arXiv:2402.17764](https://arxiv.org/abs/2402.17764) (Ma et al., 2024-02, preprint)). MatMul-free LMs also replace attention with a ternary recurrent token mixer. Up to 2.7B they come within a point of Transformer++ (49.9 vs 50.7 average), and the gap narrows with scale ([arXiv:2406.02528](https://arxiv.org/abs/2406.02528) (Zhu et al., 2024-06, preprint)). Two cautions apply. First, the energy wins in this line of work need hardware that does not exist yet. L-Mul's "95% less energy" for element-wise multiplies is a gate-count estimate, simulated on GPUs ([arXiv:2410.00907](https://arxiv.org/abs/2410.00907) (Luo & Sun, 2024-10, preprint)). Second, smaller weights are not faster on their own. 1.58-bit FLUX quantizes a text-to-image model's weights to ternary for 7.7× less storage and 5.1× less memory, but latency improves only 5% on an A100, because activations stay in 16-bit ([arXiv:2412.18653](https://arxiv.org/abs/2412.18653) (Yang et al., 2024-12, preprint)).

Quantization changes outputs, unlike exact speculative decoding. Every format change needs an eval run ([06-eval](../../06-eval/README.md)), not just a perplexity check.

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

## Stacking the gains

![Throughput gains from compile, INT8, INT4 and speculative decoding on Llama-7B](../sources/images/huyen-ai-engineering-fig9-14.png)

*Image Source: Huyen, *AI Engineering* (O'Reilly, 2025), Fig. 9-14*

Huyen reproduces PyTorch's 2023 case study (*AI Engineering*, ch. 9). The setup is Llama-7B on one A100-80GB, measured in tokens/s per user at batch size 1:

| Step | Tokens/s | Gain over previous |
|---|---|---|
| Eager PyTorch | 25.5 | — |
| + `torch.compile` | 107.0 | 4.2× |
| + INT8 weights | 157.4 | 1.5× |
| + INT4 weights | 202.1 | 1.3× |
| + speculative decoding | 244.7 | 1.2× |

Three lessons:

- **Order matters.** At batch 1, launch overhead dominates eager PyTorch, so compiling gives the largest single gain ([05](05-compilers-and-frameworks.md#what-a-compiler-does-for-inference)). After that, each step works on a smaller remaining bottleneck.
- **The gains multiply but shrink.** That is what happens when one bottleneck after another is removed.
- **Quality was not measured.** Huyen notes it was unclear how these steps affected output quality. INT4 needs an eval run before you ship it. At large batch the picture changes: compile helps less, and speculation may not help at all.

---

## Dynamic precision

Fregly's ch. 19 proposes choosing precision **per token or per step** at runtime (*AISPE*, ch. 19). The model runs in FP8 or FP4 while a confidence signal (such as the logit margin or entropy) is healthy. It switches up to BF16 when the signal degrades.

- **Use hysteresis.** Use different thresholds to enter and exit high precision (his example: enter at 6.0, exit at 3.0, both calibrated on your data), so the model does not flap between modes every token.
- **Tooling.** PyTorch autocast covers only FP16/BF16. FP8 needs Transformer Engine (or an engine's FP8 kernels).
- **Status.** His Table 19-2 of gains is illustrative, not measured. This is a research-stage pattern; no mainstream serving engine switches precision per token.

---

## Early exit and layer skipping

If a token is easy, stop computing early (*AISPE*, ch. 19):

- **Early exit** adds a classifier at intermediate layers. If it is confident, the token is emitted without running the remaining layers.
- **DASH-style layer skipping** uses a learned gate to skip 20–40% of layers per token. It needs a model trained or fine-tuned with those gates; you cannot apply it to an off-the-shelf checkpoint.
- **Speculative MoE routing** predicts expert assignment ahead of time, to start all-to-all transfers early. The book reports about 30% less communication time.

The book's "30–50% savings on reasoning tasks" for early exit mixes two things: cutting a chain of thought short (fewer *tokens*) and exiting layers early (fewer *layers per token*). They are different mechanisms with different risks. Cutting tokens is a lever in its own right. Reasoning models **overthink**, adding verification and alternative paths after they already have the right answer. One survey sorts the fixes into post-training ones (length penalties, and preference pairs that favour the first correct answer, which shortened responses by 30–40% in one study) and test-time ones (token budgets, early stopping of the trace) ([arXiv:2503.24377](https://arxiv.org/abs/2503.24377) (Wang et al., 2025-03, preprint)). In batched serving, per-token early exit also has a practical problem: sequences in one batch exit at different depths, which leaves the GPU partly idle unless the kernels handle ragged depth.

The research designs that look promising fix the compute budget in advance, or retrofit routing onto a frozen model:

- **Mixture-of-Depths.** A router picks a fixed top-*k* of tokens per block, so tensor shapes stay static. With 12.5% capacity on every other block, a 220M model matches its isoFLOP baseline while stepping 66% faster. Sampling needs a small causal predictor in place of the top-*k*, which is non-causal ([arXiv:2404.02258](https://arxiv.org/abs/2404.02258) (Raposo et al., 2024-04, preprint)).
- **Dr.LLM.** Per-layer routers decide to skip, execute or repeat each block on a frozen LLaMA-3.2 or Qwen-2.5. They are trained on only 4k MCTS-searched paths, and save about 5 layers per example while adding up to 3.4 points on ARC and DART. The paper counts layers, not wall-clock time in a batched server ([arXiv:2510.12773](https://arxiv.org/abs/2510.12773) (Heakl et al., ICLR 2026)).
- **Recursive Transformers.** One shared block is looped with per-depth LoRA. This lets a batch mix tokens that sit at different loop depths ("continuous depth-wise batching"), which attacks the ragged-depth problem directly. The 2–3× throughput gain is a theoretical simulation, not a serving implementation ([arXiv:2410.20672](https://arxiv.org/abs/2410.20672) (Bae et al., ICLR 2025)).

Activation sparsity skips neurons instead of layers. PowerInfer finds that in ReLU models a small hot set of neurons fires for most tokens (17% of OPT-30B's neurons account for 80% of activations). It keeps the hot neurons on the GPU, computes the cold ones on the CPU, and predicts which will fire. On one RTX 4090 at batch 1 it averages 7.23× llama.cpp in FP16 (up to 11.69× on Falcon-40B) and 2.89× in INT4 ([arXiv:2312.12456](https://arxiv.org/abs/2312.12456) (Song et al., 2023-12)). It needs ReLU-sparse models, so SwiGLU models such as Llama must be ReLU-fied first; the gains shrink with long prompts and larger batches, and on an A100 it is 18–29% slower than vLLM.

Ch. 19 closes with an **RL-based runtime tuner** that adjusts batch size, precision and parallelism on the fly. It insists on a **kill switch** that reverts to a known-good static configuration. That is the right shape for any adaptive controller: bounded actions, monitored rewards, and a fast fallback.

---

## Where the books disagree

| Topic | Disagreement | Read it as |
|---|---|---|
| Spec-decoding speedup | Handbook 3–4× at 90% acceptance; Fregly ~2× (1.5–2.5×); Chen et al. ">2×" latency | Depends on acceptance rate, draft/target cost ratio and batch size. ~2× is a fair planning number at low batch |
| Spec decoding's role | Fregly ch. 16 "extreme cases" vs ch. 15 and 2026 engines | Default option at low-to-moderate batch, and at large batch too once contexts are long (MagicDec) |
| Verification | Fregly's text "one by one" vs his Fig. 15-8 | Parallel, in one pass |
| Medusa | Handbook "70M approximates 7B"; Huyen 1.9× (H200); Fregly 2.2–3.6× | Heads on the target; ~2× in practice |
| LLM.int8 outliers | Handbook "weights" vs the paper | Activation features |
| GPTQ bit-widths | Handbook "4-bit only" | 2/3/4/8 |
| FP4 readiness | Fregly ch. 17 "prefer" vs ch. 18 "maturing" | Validate per model |
| Engine support | Handbook Table 8.1: spec decoding TRT-LLM only | Dated; vLLM and SGLang support it |

---

## Working reference

- Know your regime first. At low batch you are bandwidth-bound: quantize weights and add speculation. At high batch with short contexts you are compute-bound: speculation fades, FP8/FP4 math helps. At high batch with long contexts, KV reads bring back the bandwidth bound, and speculation can pay again.
- Start with FP8 weights (Hopper/Blackwell) or 4-bit AWQ/GPTQ (older GPUs). Run your eval suite, not just perplexity.
- Add EAGLE-style speculation in the engine, and watch the acceptance rate per traffic type.
- Use prompt lookup for RAG, code editing and other copy-heavy outputs.
- Enable FP8 KV cache for long contexts, and re-test long-context tasks.
- Treat dynamic precision, early exit and RL tuners as experiments with a kill switch.
