---
origin: synthesis
sources:
  - ../practice/serving_encoders_vlm_lab.py (generated text and invoices, M4 Pro, 24 GB)
  - https://arxiv.org/abs/2311.03285
  - https://raw.githubusercontent.com/huggingface/text-embeddings-inference/main/README.md
  - https://docs.vllm.ai/en/latest/models/pooling_models/
  - https://sbert.net/docs/sentence_transformer/usage/efficiency.html
  - https://sbert.net/docs/cross_encoder/usage/efficiency.html
  - https://www.runpod.io/blog/gpu-embedding-workloads-benchmark
  - https://vllm.ai/blog/v1-alpha-release
  - https://docs.vllm.ai/en/latest/design/mm_processing/
  - https://docs.vllm.ai/en/latest/configuration/optimization/
  - https://docs.vllm.ai/en/latest/features/multimodal_inputs/
  - https://docs.vllm.ai/en/latest/features/lora/
  - https://vllm.ai/blog/vllm-epd
confidence: medium
cleaned: 2026-11-03
---
# 8b — Serving Encoders and Vision Models

> Sorting 3,000 texts by length made the same encoder on the same GPU about three times faster, with no new hardware and no change to the model. Most of what you've learned about serving a language model, including KV caches, streaming and token-by-token scheduling, doesn't apply to an encoder. A vision-language model is both at once, so you need to know which half is costing you.

[Chapter 7](07-prefill-decode-kv-cache.md) split a language model's work into prefill and decode. Two other kinds of model sit next to it in most products. Take an invoice assistant, the running example of the [multimodal pillar](../../08-multimodal-engineering/README.md). It embeds every line of its catalogue, and that's an **encoder**: one forward pass in, one vector out. It also reads pages with a small vision-language model (VLM), fine-tuned in [Fine-tuning a vision-language model](../../08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model.md), and that's an encoder feeding a language model. You can read this chapter before that one.

| | Language model | Text encoder | Vision-language model |
|---|---|---|---|
| Work per request | Prefill, then one step per token | One forward pass | Image preparation on the CPU, one vision pass, then prefill and decode |
| KV cache | Yes | No | In the language half only |
| What you measure | Time to first token, tokens per second | Texts per second | Pages per second, and time before the first token |
| Main lever | Scheduling | Batch shape | Pixels you keep |

## The experiment

The numbers come from [`practice/serving_encoders_vlm_lab.py`](../practice/serving_encoders_vlm_lab.py), on an M4 Pro with 24 GB using its GPU, in one process with no server. The encoder is all-MiniLM-L6-v2, on 3,000 generated catalogue lines, random strings from an 18-word vocabulary, with a median of 17 tokens and a maximum of 256. That's fine for timing, but the neighbour overlaps below come from an artificial corpus, so treat them as a reason to test yours and not as an estimate. The vision-language model is SmolVLM-256M on generated invoices, generating 50 tokens.

Timings are the fastest of several passes, from the quietest of four full runs (144 s). The machine was shared, and a disturbed run tripled some absolute times, so we only draw conclusions from ratios that held across all four. A datacentre GPU will change those ratios too, so the method is what transfers.

## Encoders: the batch's shape is the cost

A batch is a rectangle. Every text is padded to the longest one in its batch, so one long text makes every short text beside it expensive:

```python
import random

r = random.Random(0)
lengths = [min(256, max(5, int(r.lognormvariate(2.5, 1.0)))) for _ in range(3000)]


def chunks(xs, size):
    return [xs[i:i + size] for i in range(0, len(xs), size)]


def report(name, batches):
    computed = sum(max(b) * len(b) for b in batches)  # shorter texts are padded to the longest in their batch
    print(f"{name:<22} {computed:>7,} tokens computed, {1 - sum(lengths) / computed:.0%} of them padding")


report("arrival order", chunks(lengths, 32))
report("sorted by length", chunks(sorted(lengths, reverse=True), 32))
```

```text
arrival order          300,072 tokens computed, 80% of them padding
sorted by length        63,928 tokens computed, 6% of them padding
```

Our real run used the encoder's own tokenizer:

| Batching | Batches | Texts per second | Tokens computed | Padding |
|---|---:|---:|---:|---:|
| 32 per batch, arrival order | 94 | 1,025 | 419,016 | 80% |
| 32 per batch, sorted by length | 94 | 3,162 | 87,480 | 5% |
| Token budget 2048, arrival order | 167 | 991 | 306,142 | 73% |
| Token budget 2048, sorted by length | 44 | 3,573 | 87,246 | 4% |

Sorting gave 2.8 to 4.5× across the four runs. A token budget without sorting ranged from 0.7 to 1.3×, so we saw no reliable gain, and with sorting its gain wasn't stable either. What a budget gives you is a ceiling: no batch can exceed 2,048 tokens, where a sorted batch of 32 can reach 8,192. That's a memory guarantee, and it's why [TEI](https://raw.githubusercontent.com/huggingface/text-embeddings-inference/main/README.md), Hugging Face's embedding server, has `max_batch_tokens` (default 16,384).

Sorting has a limit online, since you can only sort what's waiting. That's why a backfill, embedding a whole catalogue offline, gets all of this gain, while a live queue gets only part of it. Our data is generated and heavily skewed on purpose, so a corpus of even lengths would gain far less. Measure your own padding share first, because it's one line of code.

### How long to wait for a batch

We measured one batch of the first n texts at each size (6 ms for one text, 21 ms for 32, 110 ms for 64) and simulated a single worker over those times with random arrivals. Those times aren't a clean price for batch size. The 64 includes one 256-token text, so most of its jump is the padding from the last section, and the loads below are set from that 110 ms. A batch leaves when its oldest request has waited the window, or once the worker frees up if that's later, and it takes at most 64:

| Load | p50, no wait | p50, 2 ms | p50, 10 ms | p50, 50 ms | p99, no wait | p99, 50 ms |
|---|---:|---:|---:|---:|---:|---:|
| 58 requests/s | 5.5 ms | 7.5 | 15.5 | 40.6 | 11.0 | 58.3 |
| 292 requests/s | 8.6 ms | 8.4 | 13.7 | 41.3 | 12.6 | 65.9 |
| 526 requests/s | 9.9 ms | 9.8 | 14.4 | 47.1 | 16.0 | 83.6 |

A busy worker makes its own batches, because requests pile up while it runs. Here a wait window never helped much: 2 ms changed almost nothing, and 50 ms added about 35 ms at the median and about its own length or more at p99. The queue is simulated, and these loads stayed below this worker's real limit (32 per batch in arrival order handles about 1,000 per second), so we can't tell you what happens close to saturation. Start at zero wait, and add a window only if a measurement says it pays.

### Precision and runtime depend on the hardware

Top ten kept is the share of fp32's ten nearest neighbours that each variant still returns, averaged over 300 of the texts used as queries on the GPU and 100 on the CPU.

| On the GPU, sorted batches of 32 | Texts per second | Top ten kept, against fp32 |
|---|---:|---:|
| fp32 | 3,007 | 1.000 |
| bf16 autocast | 3,284 | 0.990 |
| fp16 autocast | 3,234 | 0.998 |

| On the CPU, 600 texts | Texts per second | Top ten kept, against fp32 |
|---|---:|---:|
| PyTorch fp32 | 400 | 1.000 |
| ONNX fp32 | 226 | 1.000 |
| ONNX int8 | 240 | 0.916 |

On our machine, half precision barely paid on the GPU, and PyTorch beat ONNX on the CPU.

Published results mostly point the other way. [Sentence Transformers' benchmark](https://sbert.net/docs/sentence_transformer/usage/efficiency.html) reports fp16 at 2.92× fp32 on an RTX 3090, a median over four models and three datasets. On an i7-13700K it reports ONNX int8 at 1.92× PyTorch fp32, a median over eight combinations of three models and their workloads, with an average of 99.58% of the task quality across retrieval and sentence similarity. Its plain ONNX fp32, at 0.90×, is slightly behind PyTorch, as ours was. On our Apple GPU, half precision gained under 1.2×. On our Apple CPU, PyTorch beat ONNX by 1.8 to 2×, and int8 reached about 0.6× PyTorch in the table, while losing 8% of the top ten. We used ONNX's default threads and didn't tune them. Their quality measure and ours differ, too. The [cross-encoder guide](https://sbert.net/docs/cross_encoder/usage/efficiency.html) warns that "ONNX and OpenVINO can even perform slightly worse than PyTorch".

So don't copy a runtime choice from a benchmark on other hardware. Check any quantized encoder on retrieval, since its speed gain is what you see and its lost neighbours aren't.

The server matters as well. RunPod's [vendor benchmark](https://www.runpod.io/blog/gpu-embedding-workloads-benchmark) (September 2026) reports engine differences of "up to 11x", with TEI a median 4.4× faster than vLLM on MiniLM, and a tie (median ratio 1.08) on bge-m3. [vLLM's docs](https://docs.vllm.ai/en/latest/models/pooling_models/) say its pooling support, which is how it serves encoders, is "primarily for convenience". The same benchmark prices bge-m3 at 512 tokens on TEI, at that date's rental prices:

| GPU | Texts per second | Dollars per billion tokens |
|---|---:|---:|
| RTX A5000 | ~190 | 0.78 |
| RTX A6000 | ~265 | 1.08 |
| H100 SXM | ~1,240 | 1.53 |
| RTX 6000 Ada | ~275 | 1.65 |
| H200 | ~1,345 | 1.85 |
| L40S | ~277 | 2.14 |

The fastest card isn't the cheapest. A backfill wants dollars per token. For a live search box, RunPod found single-query p50 latency too small to matter on any of these cards, 3 to 16 ms on TEI, and says to check its full table for a strict p99 budget under load. RunPod sells these GPUs, and we didn't reproduce the table.

## Vision-language models: where a page's time goes

SmolVLM's processor cuts a page into tiles of 512 pixels and turns each tile into 64 image tokens, which sit in the prompt like words ([2b](../../08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model.md#what-a-page-costs-before-training-starts)). So the longest edge you set decides the tiles, each tile costs vision work, and its image tokens lengthen the prefill.

| Longest edge | Tiles | Prompt tokens | Decode and prepare (CPU) | Vision pass | Rest of generation | Whole page | Share in vision |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 512 | 1 | 96 | 10 ms | 47 ms | 197 ms | 254 ms | 19% |
| 1024 | 5 | 362 | 25 ms | 222 ms | 252 ms | 499 ms | 45% |
| 2048 | 13 | 892 | 67 ms | 628 ms | 462 ms | 1,156 ms | 54% |

The lab also counts the calls for one reply. The vision tower is the model's image encoder, and running it is the vision pass:

```text
one reply of 50 tokens: the vision tower ran 1 time, the language model 50 times, on [96, 1, 1, 1]... tokens
```

The first language-model call is the prefill, which is 96 tokens, and the rest take one new token each, using the KV cache. The vision tower runs once and has no cache of its own. So a page is a large fixed cost paid before the first token. At a 2048 edge it's more than half of a 50-token reply, and it's the same whether the reply is long or short. Short extractions feel this most. Since the vision pass is proportional to tiles, resolution is your main serving control as well as your main accuracy control, and [chapter 2b](../../08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model.md#is-it-the-model-or-the-pixels) shows when you can't lower it.

```text
One page at a 2048 edge, 50 tokens out: 1,156 ms
|CPU 67|---- vision pass 628 ----|---- prefill and decode 462 ----|
```

The first two segments are paid once per page, however short the reply.

Multiple images multiply this. vLLM's `limit_mm_per_prompt` ([docs](https://docs.vllm.ai/en/latest/features/multimodal_inputs/)) exists to cap it per request. Set it, or one client's 30-page upload can take the fixed cost 30 times over. Here's that from the table, assuming pages run one after another:

```python
fixed = {512: 10 + 47, 1024: 25 + 222, 2048: 67 + 628}
for edge, ms in fixed.items():
    print(f"{edge} edge: {ms} ms a page, {30 * ms / 1000:.1f} s for a 30-page upload")
```

```text
512 edge: 57 ms a page, 1.7 s for a 30-page upload
1024 edge: 247 ms a page, 7.4 s for a 30-page upload
2048 edge: 695 ms a page, 20.9 s for a 30-page upload
```

### Is the CPU the bottleneck?

[vLLM's team warned](https://vllm.ai/blog/v1-alpha-release) that preprocessing "can consume significant CPU cycles, possibly leaving the GPU idle". [Its design](https://docs.vllm.ai/en/latest/design/mm_processing/) now caches processor output ([`mm_processor_cache_gb`](https://docs.vllm.ai/en/latest/configuration/optimization/), default 4 GiB) and normalises on the GPU for supported architectures. On our laptop it wasn't the bottleneck:

| CPU pages per second, by threads | 1 | 2 | 4 | 8 |
|---:|---:|---:|---:|---:|
| 512 edge | 97.8 | 185.3 | 351.0 | 609.0 |
| 1024 edge | 38.6 | 71.6 | 127.8 | 191.4 |
| 2048 edge | 14.1 | 25.2 | 44.4 | 67.7 |

| Pages in one batch, 512 edge, 50 tokens | Seconds | GPU pages per second |
|---:|---:|---:|
| 1 | 0.25 | 4.0 |
| 2 | 0.36 | 5.5 |
| 4 | 0.48 | 8.4 |
| 8 | 0.89 | 9.0 |

One CPU thread outruns this GPU roughly tenfold, and the CPU is 4 to 6% of a page on a quiet run. That's our laptop and our pages, which are clean 0.05 MB PNGs. A large datacentre GPU and heavy scans could reverse it, and we found no published CPU-to-GPU breakdown for any VLM. So measure both rates: if pages per second from your preparing threads is below what the GPU can take, your GPU is idling. Batching helped too, at 2.0 to 2.4× from one page to eight across runs. The cost is latency: the eighth page waits as long as the whole batch, 0.89 s against 0.25 s.

Because the vision pass is a separate cost, it can run separately. vLLM's [encoder-disaggregation benchmark](https://vllm.ai/blog/vllm-epd) (December 2025) moved it to its own GPU: on 4×A100, Qwen3-VL-4B, 640×640 images and 150 output tokens, QPS went from 6 to 12 with four images per short prompt, and only from 23 to 24 with one. With prompts of about 2,000 tokens, sustainable QPS rose from 8 to 18 with one image and from 4 to 8 with four, by the post's ordering of its figures. So the only case with almost no gain was one image on a short prompt. That's the vendor's own project reporting on its own setup.

### The same page, a second question

Users ask several questions about one document. Cached image features skip the vision pass:

```text
the same page again: 258 ms encoding it fresh, 198 ms from cached image features, same reply: True
```

That saved 60 ms, about the vision pass in the table. It should save more at larger edges, up to the 628 ms the table shows at 2048, but we only measured it at 512.

The API has a trap. In Transformers 5.20 the argument is `mm_encoder_outputs`, and it takes `dict(image=...)`. When we passed the output as a bare list it was ignored with no error. The model read no image, returned something, and looked faster. That's why our line prints `same reply`. Any reuse path needs that check, because a cache that loses the image still answers.

## Adapters at serving time

An adapter here is a LoRA: a small low-rank update trained beside frozen weights ([PEFT and fine-tuning in practice](../../../generative-ai/01-llm-fundamentals/notes/09-peft-and-fine-tuning-in-practice.md)), where r is its rank. Attached means it stays separate and runs at every wrapped layer. Merged means it has been added into the weights.

| One page, 50 tokens | Milliseconds |
|---|---:|
| Base model | 247 |
| Adapter attached | 447 |
| Adapter merged | 254 |

An r=8 adapter on the language model, attached through PEFT, cost 1.8 to 1.9× in all four runs. Merged, it cost 1.01 to 1.15×. This measures speed only, using untrained weights, in Python, and an engine built for it will differ. But the direction is what you'd expect from the extra multiplications at each wrapped layer.

That looks like an easy win for merging, and for one adapter on a float base it is. There are two reasons it may not be:

- **Many adapters.** [S-LoRA](https://arxiv.org/abs/2311.03285) (MLSys 2024) keeps adapters unmerged in one engine. On one A100 80GB, Llama-7B with rank 8 fell only from 8.05 to 7.61 requests per second as adapters went from 5 to 2,000, while vLLM, serving one merged copy of the model per adapter on the same GPU, ran out of memory by 100. In a separate ablation (mixed ranks on an A10G 24GB), a merge-and-switch variant beat on-the-fly computation only at one adapter and declined beyond two. It's text-only, and doesn't report swap latency, tail latency or quality, so the extension to VLMs is ours. If each customer has an adapter, this is the design to read.
- **A 4-bit base.** Merging into it took our model's field accuracy on generated invoices from 0.91 to 0.00, as [chapter 2b](../../08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model.md#saving-it-can-undo-it) shows.

Engine support is also narrower for vision than for text. vLLM's [LoRA docs](https://docs.vllm.ai/en/latest/features/lora/) mark adapters on the vision tower as experimental, and each model needs token helper functions implemented for its tower and connector. Its section on default multimodal LoRAs adds "we only allow one LoRA per prompt". An adapter that wraps both towers, as [2b's suffix list](../../08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model.md#which-layers-you-reached) does, would need checking before you ship it there.

## Pitfalls

| Symptom | Likely cause | Fix |
|---|---|---|
| Encoder throughput is far below the benchmark, while the GPU is busy | Padding: one long text in each batch | Measure padding share. Sort, or bucket by length |
| Encoder runs out of memory on a rare batch | Batching by count, so one long text makes a huge rectangle | Cap tokens per batch |
| Quantized encoder is faster, yet search got worse | Neighbours changed, and no retrieval test caught it | Compare top-k overlap and a retrieval metric before switching |
| ONNX or int8 runs slower than expected | Benchmark came from different hardware | Measure on your own CPU |
| VLM's time to first token is high, though the reply is short | The vision pass and prefill scale with tiles | Lower the longest edge if the text survives, and cap images per prompt |
| GPU is idle under VLM load | CPU preparation can't keep up | Compare the two rates, then add threads or a processor cache |
| Reply from cached features is faster and wrong | Features ignored, so no image reached the model | Assert the same reply against a fresh pass |
| Latency nearly doubled after shipping an adapter | Adapter attached through PEFT | Merge into a float base if there's one adapter, and score it after |

## Try it

Lab: `cd practice && uv run serving_encoders_vlm_lab.py`, about two and a half minutes on a quiet machine, and it downloads about 0.6 GB on first use. Run it twice and see which ratios move.

1. **Before running it:** in the padding code, use arrival order at batch 8, then at batch 128. Which padding share is lower, and what does that tell you about raising the batch size to go faster?

<details><summary>Answer</summary>

```text
arrival, batch 8       178,928 tokens computed, 66% of them padding
arrival, batch 128     438,432 tokens computed, 86% of them padding
```

The bigger the batch, the more likely it holds a long text, so the padding share climbs. Raising batch size in arrival order gives each extra text a bigger rectangle to pay for, so sort first.

</details>

2. **Your search API embeds one query per request at 40 requests per second, and a colleague proposes a 20 ms batching window to use the GPU better.** What do you say, and what would change your mind?

<details><summary>Answer</summary>

A window delays nearly every request at that rate, by up to its own length: the 50 ms column added about 35 ms at the median at low load, and an encoder that's mostly idle doesn't need the throughput. Measure service time at batch 1, and reconsider only if the queue grows at peak. Run the offline backfill separately, sorted, with a large batch.

</details>

3. **A support bot answers about five follow-up questions per uploaded page, with SmolVLM at a 2048 edge. Roughly how much model time could caching image features save, and what must you check first?**

<details><summary>Answer</summary>

About 628 ms of each 1,156 ms reply for the four follow-ups, or a little over 40% of the total, if the 50-token split holds. That's arithmetic from the table, since we measured the saving only at 512. First check that replies match a fresh pass, because a cache that the API ignores produces answers with no image.

</details>

## Interview checklist

| Question | Short answer |
|---|---|
| How does serving an embedding model differ from an LLM? | One forward pass, with no KV cache or streaming. Throughput is set by the batch's rectangle, the longest text times the batch size. |
| How do you speed up an encoder without new hardware? | Sort or bucket by length. Here that cut padding from 80% to about 5% and gave about 3×. Check the padding share first. |
| Why have a token budget per batch? | It caps memory on a rare long batch. It gave no reliable speed-up without sorting. |
| Would you set a batching window? | Start at zero. A busy worker batches by itself. In a simulation over measured service times, waiting 50 ms added about 35 ms at the median and at least 47 ms at p99, and gave nothing back. |
| Is int8 or ONNX faster? | It depends on hardware. Published x86 results favoured int8. On an Apple CPU, PyTorch won by about 1.8× and int8 lost 8% of the top ten. |
| Where does a VLM's time go? | Before the first token, the vision pass and the prefill both scale with tiles. At a 2048 edge the vision pass was 54% of a 50-token reply. It runs once, and the decode uses the KV cache. |
| Is preprocessing the bottleneck? | Measure both rates. Here one CPU thread was about ten times the GPU's rate, but on clean pages and a laptop GPU. |
| Merge the adapter, or serve it attached? | One adapter on a float base: merge, since attached cost 1.8× here. Many adapters: an engine like S-LoRA. A 4-bit base: keep it attached. |

## Next

[09-checklist-and-ai-assisted-tuning.md](09-checklist-and-ai-assisted-tuning.md): everything so far as an ordered checklist, plus how to let a model search for kernels safely.
