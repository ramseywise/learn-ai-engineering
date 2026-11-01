---
origin: book-condensed
sources:
  - "Fregly, AI Systems Performance Engineering (O'Reilly, 2025), ch. 17–18, 19"
  - "Huyen, AI Engineering (O'Reilly, 2025), ch. 9"
  - "Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), ch. 8"
  - https://arxiv.org/abs/2401.09670
  - https://arxiv.org/abs/2309.06180
  - https://arxiv.org/abs/2308.16369
  - https://arxiv.org/abs/2311.18677
  - https://arxiv.org/abs/2407.00079
  - https://arxiv.org/abs/2405.04434
  - https://arxiv.org/abs/2502.13189
  - https://arxiv.org/abs/2211.05102
  - https://arxiv.org/abs/1911.02150
  - https://arxiv.org/abs/2305.13245
  - https://arxiv.org/abs/2508.15884
  - https://arxiv.org/abs/2309.17453
  - https://arxiv.org/abs/2502.11089
  - https://arxiv.org/abs/2303.06865
  - https://arxiv.org/abs/2207.00032
  - https://arxiv.org/abs/2607.29678
  - https://arxiv.org/abs/2608.15127
  - https://arxiv.org/abs/2305.13048
confidence: medium
cleaned: 2026-10-31
---
# 7 — Prefill, Decode and the KV Cache

> Prefill is a compute problem. Decode is a memory problem. The KV cache is the state that links them. Most modern serving architecture is about where that cache lives, how it is shared, and which GPU computes it.

---

## Two phases, one request

Every request runs a **prefill** pass (all prompt tokens in parallel; compute-bound; sets TTFT) and then many **decode** steps (one token per step; bandwidth-bound; sets TPOT) ([01](01-why-inference-is-its-own-discipline.md#two-bottlenecks-compute-and-memory-bandwidth)). The decoder-only loop the Handbook walks through (*LLM Engineer's Handbook*, ch. 8) makes the link explicit: prefill writes keys and values for every prompt token into the **KV cache**, and each decode step reads the whole cache and appends one more entry.

On one GPU the phases **interfere**. A long prefill entering a continuous batch stalls every decode in that batch for its duration, and short requests queue behind long ones (**head-of-line blocking**). Fregly's framing (*AISPE*, ch. 17): interactive services often target p99 TTFT under 200–300 ms. MLPerf Inference v5.0's SLOs give scale: **Llama 2 70B: p99 TTFT ~450 ms, p99 TPOT 40 ms; Llama 3.1 405B: ~6 s TTFT, 175 ms TPOT**. Holding both tails with one mixed queue is hard.

There are two ways to deal with interference: slice the prefill so decodes can run between the slices (chunked prefill), or move prefill to different GPUs (disaggregation).

---

## Chunked prefill

Split a long prefill into chunks and schedule each chunk in the same step as the running decodes. This is **piggybacking** decodes on prefill chunks.

![Chunked prefill: prefill chunks (green) interleaved with decode steps (blue) as requests R2–R4 arrive](../sources/images/ai-systems-performance-engineering-fig19-7.png)

*Image Source: Fregly, *AI Systems Performance Engineering* (O'Reilly, 2025), Fig. 19-7*

R1 keeps decoding every step while R2, R3 and R4 prefill in two or three chunks each. No request waits for another's whole prompt. **SARATHI** (Agrawal et al., 2023) reported **~1.3–1.9×** throughput over naive scheduling. Fregly's rule of thumb is a chunk that takes **~50–100 ms** of GPU time, which is a few thousand tokens depending on model and GPU (*AISPE*, ch. 19). His example splits a 10,000-token prefill into five 2,000-token chunks. Chunking does **not reduce total work** (*AISPE*, ch. 16). It reorders work so decodes are not starved. A small chunk also re-reads the KV cache of earlier chunks, so very small chunks cost extra.

Chunked prefill is on by default in vLLM V1, and it is what the TGI `MAX_BATCH_PREFILL_TOKENS` knob approximates ([06](06-serving-at-scale.md#monolith-or-microservice)). It is the right first answer to interference on a single pool.

**POD-Attention** goes one level lower: a single attention kernel whose thread blocks decide at runtime, per SM, whether to do prefill or decode work, so compute-bound and bandwidth-bound work share each SM. Fregly quotes "up to about 29%" (*AISPE*, ch. 18). The paper reports up to 59% faster attention, with a mean around 28%. The book appears to have reported the mean as the peak.

---

## Disaggregated prefill and decode

Run prefill and decode on **separate GPU pools**. A router sends the prompt to a prefill worker, which computes the KV cache and **transfers** it to a decode worker that generates the tokens ([06](06-serving-at-scale.md#parallelism-for-inference), Fig. 15-2). Each pool gets its own batch size, parallelism, and even its own hardware.

![Colocated vs disaggregated (2 prefill GPUs + 1 decode GPU) under P90 TTFT ≤ 400 ms and P90 TPOT ≤ 40 ms](../sources/images/ai-systems-performance-engineering-fig17-2.png)

*Image Source: Fregly, *AI Systems Performance Engineering* (O'Reilly, 2025), Fig. 17-2 (after DistServe)*

The worked example, from DistServe (Zhong et al., 2024): a colocated GPU can sustain 3 RPS before prefill breaks the TTFT SLO and only **1.6 RPS** before decode breaks the TPOT SLO, so the system runs at 1.6 RPS per GPU. Split into 2 prefill GPUs (5.6 RPS each) and 1 decode GPU (10 RPS), the system runs at min(11.2, 10) / 3 GPUs = **3.3 RPS per GPU**, about 2× the goodput from the same hardware. DistServe's headline across workloads is **up to 7.4× more goodput or 12.6× tighter SLOs** (*AISPE*, ch. 15). Goodput here is the SLO-based definition ([01](01-why-inference-is-its-own-discipline.md#three-definitions-of-goodput)).

### When disaggregation pays

Fregly writes as if disaggregation were the standard architecture. Huyen is more careful (*AI Engineering*, ch. 9): it depends on the workload. Citing a Meta talk, she gives **prefill:decode instance ratios of 2:1 to 4:1** for long inputs when TTFT matters most, and **1:2 to 1:1** for short inputs when TPOT matters most. Both sources' details point to the same conditions:

| Disaggregate when | Stay colocated (with chunked prefill) when |
|---|---|
| Long prompts (RAG, agents, long chat history) dominate | Prompts are short and outputs long |
| Strict TTFT *and* TPOT SLOs at high load | Load is low or SLOs are loose |
| Fast interconnect for KV transfer (NVLink, RDMA/InfiniBand) | KV would cross slow Ethernet |
| Fleet is big enough to size two pools | A handful of GPUs |

Routing rules from Fregly's chapter (*AISPE*, ch. 17): **don't offload short prompts** (transfer cost exceeds the prefill saved; his example threshold is 256 tokens) and **don't offload prompts with a large prefix-cache hit**. Use *effective* prompt length = prompt length − cached prefix length, and keep high-hit requests local. Queue-depth thresholds decide when the prefill pool is saturated and local prefill should take over. The vLLM flags in his YAML examples are V0-era. Check them against current docs.

### Moving the cache

KV transfer is the cost of disaggregation, and a whole layer of tooling exists for it:

- **NIXL** (NVIDIA Inference Xfer Library) moves KV between GPUs, hosts and storage over NVLink, RDMA or TCP. Used by Dynamo, and by vLLM and SGLang connectors.
- **LMCache** stores and moves KV across engines and tiers. Fregly's example (*AISPE*, ch. 18): sending a 7,500-token KV cache as **470 small transfers took ~20 ms**; collating 16-token pages into ≥128-token chunks cut it to **~8 ms**. Batch your transfers.
- **Mooncake** (Moonshot AI / Kimi) builds the whole system around a disaggregated KV pool across GPU HBM, CPU DRAM and SSD, with a KV-centric scheduler.
- **llm-d** and **NVIDIA Dynamo** package router, prefill/decode pools and KV movement for Kubernetes.

### Heterogeneous pools

Because the phases want different things, they can run on different chips. Prefill wants FLOP/s; decode wants HBM capacity and bandwidth. **Splitwise** (Patel et al., 2024) reported **1.4× throughput at 20% lower cost**, or **2.35× throughput at the same cost and power**, by mixing GPU generations. **HexGen-2** reports up to 2× on Llama 2 70B. **Arrow** and **TetriInfer** go further and flip instances between prefill and decode roles as the mix changes; Arrow reports up to 5.6× higher request rate (*AISPE*, ch. 18).

Disaggregation also lets each pool pick its own parallelism. The chapter contradicts itself on which choice to make. One paragraph recommends **TP=8 for prefill** and TP=1 for decode, to minimize prompt latency. The paragraph right after Fig. 18-7 picks **pipeline parallelism for prefill instead**, because TP's all-reduce costs most when many tokens are in flight (*AISPE*, ch. 18). Both can be right: TP lowers the latency of one long prompt, while PP gives better throughput across many prompts. The consistent part is decode, where splitting one token's work over many GPUs adds communication to every step and hurts TPOT. Pick by measuring your prompt-length mix.

---

## Sizing the cache

```
KV bytes per token = 2 (K and V) × n_layers × n_kv_heads × head_dim × bytes_per_element
```

This is Fregly's formula in ch. 17, and the one to use. Note `n_kv_heads`, not attention heads. Three of the sources write it differently:

| Source | Formula uses | Effect |
|---|---|---|
| Huyen (*AI Engineering*, ch. 9): 2 × B × S × L × H × M | Model dim H | Correct for MHA; **overstates GQA/MQA models** by the query-to-KV head ratio |
| Handbook (*LLM Engineer's Handbook*, ch. 8) | Attention heads | Same overstatement |
| Fregly ch. 17 | KV heads | Correct for all |
| Fregly ch. 18 (Mooncake example) | `num_heads × head_dim` | Same overstatement, plus a wrong config (below) |

Worked numbers, all FP16 unless stated:

- **Llama 2 13B** (40 layers, 40 heads × 128, MHA). Fregly gets **0.82 MB/token**, so a 4,096-token context is **3.36 GB** (1.68 GB in FP8). Huyen's batch of 32 × 2,048 tokens is **54 GB**. These agree, because 13B is MHA. With GQA-8 the same 4,096 tokens would be **0.67 GB**; with MQA, **0.084 GB** (*AISPE*, ch. 17).
- **"7B exceeds 2 GB above 2,048 tokens"** (*LLM Engineer's Handbook*, ch. 8). For Llama 2 7B (32 layers, d = 4,096, MHA) a single sequence is 0.5 MB/token: 1.07 GB at 2,048 tokens, crossing 2 GB around 4,096. Loose, but the right order of magnitude.
- **Pope et al. (2022), via Huyen:** a 500B+ MHA model at batch 512 and context 2,048 needs **~3 TB** of KV, **3× the weights**. This is why MQA and GQA exist. In the paper, PaLM 540B's multi-query attention, with the attention computation split across chips by batch, allows up to 32× longer context on 64 TPU v4 chips ([arXiv:2211.05102](https://arxiv.org/abs/2211.05102) (Pope et al., MLSys 2023)).
- **Fregly's 250,000-token example** (*AISPE*, ch. 18) assumes a 70B model with 80 layers and 32 MHA heads × 128 and gets **1.31 MB/token, 328 GB**. Real 70B Llama models use **8 KV heads** (GQA), which gives **0.33 MB/token, ~82 GB**. The conclusion that it won't fit beside the weights on one GPU survives. The number is 4× too high.

Capacity budget: free memory after weights is the KV budget. Fregly's example is 70 GB of weights on a 180 GB-usable B200, leaving about 110 GB. The book prints 122 GB, an arithmetic slip, and the true figure is lower still once activations and CUDA graph buffers are counted. Divide the budget by bytes per token to get the total tokens in flight across all sequences. That number, not FLOP/s, usually caps batch size in decode. Jet-Nemotron's architecture search found the same thing from the other side. At a fixed KV-cache size, models with different parameter counts had similar long-context generation throughput on H100, so KV size, not parameter count, was the variable to cut. Its 2B hybrid, which keeps only a few full-attention layers and uses linear attention elsewhere, decodes 53.6× faster than Qwen3-1.7B at 256K context, with comparable accuracy ([arXiv:2508.15884](https://arxiv.org/abs/2508.15884) (Gu et al., NeurIPS 2025)).

### Shrinking the cache

| Technique | Mechanism | Typical effect | Source |
|---|---|---|---|
| **MQA / GQA** | Share K/V across query heads | KV ÷ (query heads / KV heads), e.g. 8× for 64→8 | Huyen ch. 9; Fregly ch. 17 |
| **MLA** (DeepSeek) | Store a low-rank latent instead of full K/V | DeepSeek-V2 caches 576 values per token per layer (512 latent + 64 RoPE key), the size of GQA with 2.25 groups; in its MoE ablations MLA kept 4–14% of MHA's KV and scored slightly higher. Fast decode kernels (FlashMLA; ThunderMLA claims +20–35% over it) | Fregly ch. 1, 18; [arXiv:2405.04434](https://arxiv.org/abs/2405.04434) (DeepSeek-AI, 2024-05) |
| **Local / sliding-window attention** | Attend to the last W tokens only | Huyen: 10k context with a 1k window ≈ 10× smaller | Huyen ch. 9 |
| **Cross-layer attention** | Share KV across adjacent layers | Character.AI: >20× KV reduction, with conversations averaging 180 messages | Huyen ch. 9 |
| **KV quantization** | FP8 (or INT8/INT4) K/V | 2× (FP8) to 4× (INT4); vLLM and TensorRT-LLM support FP8 KV | Fregly ch. 18–19 ([08](08-adaptive-inference.md#kv-cache-quantization)) |
| **Eviction / compression** | Drop or merge low-importance entries | Workload-dependent; only safe with restricted-attention layers. A plain sliding window collapses once text outruns the cache, because models dump attention on the first tokens. Keeping 4 of these "attention sink" tokens plus the window holds perplexity stable to 4M tokens on Llama-2, MPT, Falcon and Pythia, with no fine-tuning. Evicted tokens are gone, so this gives streaming, not long-context recall ([arXiv:2309.17453](https://arxiv.org/abs/2309.17453) (Xiao et al., ICLR 2024)) | Fregly ch. 18 |
| **Offload / tiering** | Spill cold KV to CPU DRAM or NVMe; fetch on reuse | Capacity; costs PCIe/NVLink-C2C bandwidth. Offloading buys throughput, not latency. FlexGen runs OPT-175B on one 16 GB T4 at 1 token/s with an effective batch of 144, 100× the throughput of DeepSpeed ZeRO-Inference, at about 4,000 s per batch ([arXiv:2303.06865](https://arxiv.org/abs/2303.06865) (Sheng et al., ICML 2023); [arXiv:2207.00032](https://arxiv.org/abs/2207.00032) (Aminabadi et al., SC 2022)) | Fregly ch. 17–18 |

The MLA trade is real but its headline numbers are stacked. DeepSeek-V2's 93.3% KV cut and 5.76× generation throughput (8×H800) are measured against the dense DeepSeek 67B, with FP8 weights, ~6-bit KV quantization and MoE sparsity on top of MLA, so they are not MLA's effect alone. Its own 7B dense ablation shows why plain sharing is not free: MMLU falls from 45.2 (MHA) to 41.2 (GQA-8) and 37.9 (MQA) ([arXiv:2405.04434](https://arxiv.org/abs/2405.04434) (DeepSeek-AI, 2024-05)).

The original papers measured smaller losses, in narrower settings. Shazeer introduced MQA on a WMT14 en-de Transformer on TPUv2. Incremental decoder time fell from 46 to 3.8 µs per token, and BLEU moved by only 0.2 either way ([arXiv:1911.02150](https://arxiv.org/abs/1911.02150) (Shazeer, 2019-11, preprint)). GQA was mainly a conversion recipe: mean-pool an MHA checkpoint's K/V heads into groups, then uptrain with 5% of the original pretraining compute. On T5-XXL, GQA-8 scored 47.1 against MHA's 47.2 and MQA's 46.6, at close to MQA's speed (0.28 vs 1.51 s per sample for MHA) ([arXiv:2305.13245](https://arxiv.org/abs/2305.13245) (Ainslie et al., EMNLP 2023)). Both results are on encoder–decoder models scored with BLEU or ROUGE. DeepSeek's decoder-only MMLU ablation is the harsher test, and the closer match to how GQA is used today.

Block-sparse attention cuts prefill compute, not cache size. MoBA scores key blocks by their mean-pooled key and lets each query attend to its top-k blocks plus its own. On Llama-3.1-8B extended to 1M tokens (4,096-token blocks, top-12, last 3 layers kept dense) it matched full attention on RULER (0.782 vs 0.785) and ran the attention layers 6.5× faster at 1M-token prefill. Decode switches back to full attention, so the KV cache stays the same size ([arXiv:2502.13189](https://arxiv.org/abs/2502.13189) (Lu et al., 2025-02)). It is a vendor report on one model, and the speedup is for attention alone, not end to end.

DeepSeek's NSA makes the sparsity trainable and keeps it at decode, where MoBA does not. It combines compressed-block, selected-block and sliding-window branches over a GQA cache. A 27B MoE pretrained with it on 260B tokens matched or beat full attention on general, LongBench and reasoning evals. At 64K context it measured 9.0× faster forward and 6.0× faster backward passes. Its 11.6× decode figure is an *expected* speedup, computed from the KV tokens loaded per step (5,632 vs 65,536), not a timed run ([arXiv:2502.11089](https://arxiv.org/abs/2502.11089) (Yuan et al., ACL 2025)). The far end of the spectrum has no growing cache at all. RWKV runs as an RNN at inference, with constant memory per token, and matched transformers of similar size up to 14B. The cost is that everything must pass through one fixed-size state, so the model cannot look back at the prompt, and its results depend more on how the prompt is ordered ([arXiv:2305.13048](https://arxiv.org/abs/2305.13048) (Peng et al., Findings of EMNLP 2023)).

---

## PagedAttention

Before **PagedAttention** (Kwon et al., 2023, the vLLM paper), engines reserved a contiguous KV slab per request sized for the maximum length. Reserved-but-unused space and fragmentation wasted most of the memory: the paper measured only 20–38% of KV memory holding real tokens ([06](06-serving-at-scale.md#watching-a-fleet)). PagedAttention stores KV in fixed-size **blocks** (16 tokens by default in vLLM) and maps each sequence's logical blocks to physical blocks through a block table, as an OS maps virtual pages.

![Two sequences with the same prefix map their logical KV blocks to the same physical blocks](../sources/images/ai-systems-performance-engineering-fig18-3.png)

*Image Source: Fregly, *AI Systems Performance Engineering* (O'Reilly, 2025), Fig. 18-3*

Paging gives three things: near-zero fragmentation (waste under 4% in the paper), growth one block at a time, and **sharing**. Sequences with a common prefix point at the same physical blocks, with copy-on-write when they diverge. The Handbook cites the sharing win for parallel sampling and beam search: memory overhead down **up to 55%**, throughput up **up to 2.2×** (*LLM Engineer's Handbook*, ch. 8). Every major engine (vLLM, SGLang, TensorRT-LLM, TGI) now uses paged KV, and it is what lets continuous batching admit requests without knowing their final length ([06](06-serving-at-scale.md#batching)).

---

## Prefix caching

Sharing blocks *within* a request generalizes to sharing *across* requests. If a new prompt starts with tokens whose KV is already cached, skip their prefill.

- **vLLM automatic prefix caching** hashes each full 16-token block, chained with the hash of its prefix, and looks blocks up in a global table (*AISPE*, ch. 18). Only full blocks are shared, and the match must be exact from the first token.
- **SGLang RadixAttention** keeps a radix tree over token sequences, giving longest-prefix matching at token granularity with LRU eviction. In practice both get the same effect, with different data structures.

The hit rate depends on **prompt layout**. Put stable content first (system prompt, tool definitions, few-shot examples, documents) and variable content last. Changing one token early in the prompt invalidates everything after it. This is the same rule that drives API prompt-cache pricing ([02/04](../../02-context-engineering/notes/04-retrieval.md#caching)). Fregly's "10× faster" prefix-cache example (*AISPE*, ch. 16) is the ideal case of a long shared document and a short question. Real gains scale with the cached fraction of each prompt.

At fleet scale the router has to send a request to **the replica that holds its prefix** (cache-aware routing in llm-d, Dynamo, SGLang router). Otherwise every replica recomputes and caches the same prefixes ([06](06-serving-at-scale.md#routing)).

Agent sessions push prefix caching to its limits, and the costs move elsewhere. In one production agent session in AgentSysBench, accumulated tool calls and observations grew to 84.3% of the input. The final step emitted 151 tokens after a 166,721-token input. Sessions also sit idle for minutes to hours between steps, which outlasts cache lifetimes, so the same long prefix is prefilled again ([arXiv:2608.15127](https://arxiv.org/abs/2608.15127) (Chang et al., 2026-08, preprint)). When the cache does hit, the next bottleneck is the CPU front end. Across 153,951 agent calls the median call appended only ~1.4K characters, yet most front ends re-tokenize the whole transcript. As the prefix-cache hit rate rises toward 0.99, tokenization grows from 10% to 64% of TTFT. Splicing a re-tokenized window onto the session's previous token IDs, checked for exact equality with full tokenization, cut median TTFT 16–34% under load in vLLM ([arXiv:2607.29678](https://arxiv.org/abs/2607.29678) (Zhang et al., 2026-07, preprint)).

### Prompt caching in provider APIs

The same mechanism, sold as a feature. From Huyen (*AI Engineering*, ch. 9), with **2024 prices** that have since changed:

- A 1,000-token system prompt sent 1M times a day is **1B input tokens a day** that caching can avoid recomputing.
- Gemini (2024): cached input tokens at a **75% discount**, plus storage at **$1.00 per million tokens per hour**.
- Anthropic (2024): **up to 90% cost and up to 75% latency** reduction, larger for longer cached contexts. Anthropic's measurements (Table 9-3):

| Use case | Latency without → with cache | Cost reduction |
|---|---|---|
| Chat with a book (100k-token cached prompt) | 11.5 s → 2.4 s (−79%) | −90% |
| Many-shot prompting (10k-token prompt) | 1.6 s → 1.1 s (−31%) | −86% |
| Multi-turn conversation (long system prompt) | ~10 s → ~2.5 s (−75%) | −53% |

The trend holds in 2026; the prices don't. Check current pricing and minimum cacheable lengths before using these numbers.

---

## Working reference

- **Turn on chunked prefill first**; disaggregate only when long prompts and strict TTFT+TPOT SLOs coincide at scale.
- **Size the KV budget with `n_kv_heads`**, at your real precision and max concurrency.
- **FP8 KV** is the cheapest capacity win on Hopper and Blackwell. Evaluate quality on long-context tasks.
- **Lay out prompts stable-first** and route on prefix affinity.
- **Don't ship KV for short or prefix-hit prompts**; batch KV transfers into ≥128-token chunks.
- **Watch KV utilization and swap/copy-engine activity**; they predict latency spikes ([06](06-serving-at-scale.md#watching-a-fleet)).
