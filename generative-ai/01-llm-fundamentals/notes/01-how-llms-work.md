---
origin: synthesis
sources:
  - https://arxiv.org/abs/1706.03762
  - https://arxiv.org/abs/2005.14165
  - https://arxiv.org/abs/2001.08361
  - https://arxiv.org/abs/2203.15556
  - https://arxiv.org/abs/2302.13971
  - https://arxiv.org/abs/2303.08774
  - "Raschka, Build a Large Language Model (From Scratch) (Manning, 2024), ch. 1–5"
  - "Phoenix & Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 2"
  - "Huyen, AI Engineering (O'Reilly, 2025), ch. 1–2"
  - "Raieli & Iuculano, Building AI Agents with LLMs, RAG, and Knowledge Graphs (Packt, 2025), ch. 2–3"
  - https://github.com/rasbt/LLMs-from-scratch
  - https://arxiv.org/abs/2108.12409
  - https://arxiv.org/abs/2303.12712
  - https://arxiv.org/abs/2303.18223
  - https://arxiv.org/abs/2312.11805
  - https://arxiv.org/abs/2403.08295
  - https://arxiv.org/abs/2309.16609
  - https://arxiv.org/abs/2412.15115
  - https://arxiv.org/abs/2502.05171
  - https://arxiv.org/abs/2503.09573
  - https://arxiv.org/abs/2405.21060
  - https://arxiv.org/abs/2405.04517
  - https://arxiv.org/abs/2309.16588
  - https://arxiv.org/abs/2306.05284
  - https://arxiv.org/abs/2305.07922
  - https://arxiv.org/abs/2301.00704
confidence: high
cleaned: 2026-10-31
---

# 1 — How LLMs Work

> An LLM is a decoder-only transformer trained to predict the next token. Tokens, embeddings, causal self-attention and scale explain most of its behaviour, including the failures.

---

## The one-sentence model

A large language model takes a sequence of tokens and returns a probability distribution over the next token. Generation is that step in a loop: sample a token, append it, predict again. Everything else in this pillar (prompting, fine-tuning, RLHF, tools) changes *which* distribution the model produces. None of it changes the loop.

That framing explains three things you will meet constantly:

| Behaviour | Why it follows from next-token prediction |
|---|---|
| Fluent but wrong answers (hallucination) | Training rewards *plausible* continuations, not true ones. A confident-sounding citation is a likely sequence of tokens whether or not the paper exists |
| Sensitivity to wording | The prompt is the conditioning context. Different tokens give a different distribution |
| Few-shot learning | Examples in the prompt make the desired pattern the most likely continuation, with no weight update ([arXiv:2005.14165](https://arxiv.org/abs/2005.14165), Brown et al., 2020) |

The loop has a fourth consequence: the model has no scratchpad except the tokens it has already written. Bubeck et al. probed an early, pre-release GPT-4 on `a*b + c*d`. With single-digit numbers it got "only 58% accuracy" on 100 random samples, and with numbers from 10 to 19 it got 16%. When the prompt asked it to write out every intermediate step first, accuracy rose to 100% for numbers from 1 to 40. Asked how many primes lie between 150 and 250, it answered 13. Asked to list them first and then count, it got the right answer. The authors put these failures down to "the model's lack of planning, working memory, ability to backtrack," and separate *incremental* tasks, which can be written one step at a time, from *discontinuous* ones that need an idea before the first word. They also warn that "all quantitative results will be different on the final" model ([arXiv:2303.12712](https://arxiv.org/abs/2303.12712) (Bubeck et al., 2023-03)). This is why chain-of-thought prompting helps arithmetic: the intermediate tokens are the working memory.

---

## Tokens

Models do not see characters or words. A **tokenizer** splits text into subword units from a fixed vocabulary and maps each to an integer id.

- **Byte-pair encoding (BPE)** starts from bytes or characters and repeatedly merges the most frequent adjacent pair until the vocabulary reaches a target size. GPT-2's BPE vocabulary has 50,257 entries (*LLMs from Scratch*, ch. 2). WordPiece (BERT) and SentencePiece (T5, Llama) are close relatives. Vocabulary size is a design choice: Mixtral 8x7B uses 32,000 tokens and GPT-4's tokenizer 100,256 (*AI Engineering*, ch. 1).
- Why subwords and not words or characters? Huyen gives three reasons. Subwords carry meaning that characters do not ("cook" + "ing"). There are far fewer unique subwords than unique words, so the vocabulary and the embedding table stay small. A made-up word still splits into known pieces ("chatgpt" + "ing"), so nothing is out of vocabulary (*AI Engineering*, ch. 1).
- Common words are one token; rare words, code identifiers and non-English text split into several. A rough English rule: **100 tokens ≈ 75 words** (*Prompt Engineering for GenAI*, ch. 2; *AI Engineering*, ch. 1). GPT-4's tokenizer turns "I can't wait to build AI applications" into nine tokens.
- Tokens are the unit of **cost, latency and context length**. A 200k-token context window is a token budget, not a word budget.
- **The tax is not the same for every language.** On the MASSIVE dataset (the same short sentences translated into 52 languages), the median length with GPT-4's tokenizer was 7 tokens in English, 32 in Hindi and 72 in Burmese. Burmese text therefore costs about ten times as much and takes about ten times as long per API call for the same content. English also makes up 45.88% of Common Crawl, which helps explain why GPT-4 scores best in English on MMLU (*AI Engineering*, ch. 2, citing Yennie Jun's 2023 analysis).

Tokenization explains several odd failures: counting letters in a word, reversing strings and arithmetic on long numbers are hard because the model never sees the individual characters.

```python
import tiktoken                      # OpenAI's BPE; Anthropic exposes a count_tokens endpoint instead
enc = tiktoken.get_encoding("gpt2")
enc.encode("Tokenization isn't free.")   # -> list of ints; decode() inverts it
```

---

## Embeddings and position

Each token id indexes a row of a learned **embedding matrix** (vocab_size × d_model; 50,257 × 768 for GPT-2 small). The row is a dense vector that ends up encoding meaning: similar tokens land near each other.

Attention by itself is order-blind, so position is added in:

| Scheme | Used by | Idea |
|---|---|---|
| Learned absolute positions | GPT-2, GPT-3 | A second embedding table indexed by position, added to the token embedding |
| Sinusoidal | Original transformer | Fixed sine/cosine patterns ([arXiv:1706.03762](https://arxiv.org/abs/1706.03762)) |
| Rotary (RoPE) | Llama, most open models | Rotate query/key vectors by an angle that depends on position ([arXiv:2104.09864](https://arxiv.org/abs/2104.09864)); extends to longer contexts more gracefully |
| ALiBi | BLOOM, MPT | No position embedding; subtract a per-head linear penalty proportional to query–key distance from the attention scores ([arXiv:2108.12409](https://arxiv.org/abs/2108.12409)) |

ALiBi's paper (Press et al., 2021-08) tested whether a model trained on short sequences still works on longer ones. On WikiText-103, sinusoidal models got worse as soon as the input passed the training length, and rotary was only somewhat better. A 1.3B ALiBi model trained on 1,024 tokens matched the perplexity of a sinusoidal model trained on 2,048 when both were tested at 2,048, and it trained **11% faster with 11% less memory**. Perplexity was best at about twice the training length, then held steady out to 10,000 tokens. The authors' own appendix limits what that shows. With nonoverlapping evaluation windows, the gain from longer inputs came from fewer tokens sitting at the start of a window with little context (the "early token curse"). It did not come from the model using text far back. Under sliding-window evaluation, where every token gets full context, ALiBi's perplexity stayed flat as the input grew, while the sinusoidal model's still blew up. ALiBi extrapolates without breaking. That is not the same as making use of the extra context.

RoPE models break the same way unless something is changed at inference. Qwen-7B, trained on 2,048 tokens, has an arXiv perplexity of 3.78 at 2,048 tokens, 39.35 at 4,096 and 2,645 at 16,384. **With dynamic NTK scaling, LogN attention scaling and window attention added at inference, without retraining, it holds 3.49 at 8,192 and 4.32 at 16,384** ([arXiv:2309.16609](https://arxiv.org/abs/2309.16609) (Bai et al., 2023-09), Table 3). Like ALiBi's result, that shows the model doesn't break. It doesn't show the model uses the far context.

---

## Attention

Self-attention lets every token build its representation from every other token it can see ([arXiv:1706.03762](https://arxiv.org/abs/1706.03762), Vaswani et al., 2017). Each token is projected into a **query**, a **key** and a **value**:

```
Attention(Q, K, V) = softmax(Q Kᵀ / √d_k) · V
```

- `Q Kᵀ` scores how relevant each token is to each other token.
- Dividing by `√d_k` keeps the softmax from saturating as dimensions grow. `d_k` is the dimension of each key vector (64 per head in the original transformer), not the sequence length. *Building AI Agents* (ch. 2) says the scores are divided by "the size of the sequence"; Vaswani et al. divide by the square root of the key dimension, and that is what every implementation does.
- The softmax turns scores into weights; the output is a weighted sum of values.

Three refinements make it a language-model layer (*LLMs from Scratch*, ch. 3 builds each in turn):

1. **Causal mask.** A decoder may only attend to earlier positions. Future positions are set to −∞ before the softmax, so training on "predict token *t* from tokens < *t*" is honest.
2. **Multi-head attention.** Several attention heads run in parallel on lower-dimensional projections and are concatenated. Different heads learn different relations (syntax, coreference, copying).
3. **Dropout on attention weights** during training, for regularization.

![Two 6×6 attention-weight matrices for "Your journey starts with one step": the left one is full, the right one has every entry above the diagonal greyed out and each row renormalized to sum to 1](../sources/images/build-a-large-language-model-from-scratch-fig3-19.png)
*Image Source: Raschka, *Build a Large Language Model (From Scratch)* (Manning, 2024), Fig. 3-19*

The whole causal head fits in four lines. This is a rewrite of the idea in Raschka's `CausalAttention` class, not his code; the full version is at [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) (ch03):

```python
# q, k, v: (batch, T, d_k), already projected from the token embeddings
scores = q @ k.transpose(-2, -1) / k.shape[-1] ** 0.5         # (batch, T, T)
future = torch.triu(torch.ones(T, T, dtype=torch.bool), diagonal=1)
weights = torch.softmax(scores.masked_fill(future, float("-inf")), dim=-1)
out = dropout(weights) @ v                                     # (batch, T, d_k)
```

Masking with −∞ *before* the softmax matters. Raschka first zeroes the weights after the softmax and renormalizes, then shows that the −∞ version gives the same result in one step and leaks nothing from the masked positions.

In an encoder–decoder model there is a second kind, **cross-attention**: the *queries* come from the decoder and the *keys and values* from the encoder's output, so each target token can look at the whole source sentence. *Building AI Agents* (ch. 2) has this the wrong way round, with queries from the encoder.

Large transformers also put tokens to uses nobody designed. Darcet et al. studied vision transformers, where the tokens are image patches ([arXiv:2309.16588](https://arxiv.org/abs/2309.16588) (Darcet et al., 2023-09)). In DINOv2 ViT-g, about 2% of patch tokens, almost all on plain background, ended up with roughly 10× the norm of the rest. Linear probes showed these tokens had dropped their own patch's content and position and held image-wide information instead. In effect, the model was using them as scratch space. They appeared only in ViT-L and larger, and only after about a third of training. The fix was to append four learned "register" tokens that carry no input and are thrown away at the output. That removed the outliers and lifted DINOv2 ViT-L's ADE20k segmentation from 46.6 to 47.9 mIoU, with ImageNet linear-probe accuracy at 84.3 before and 84.8 after. Those are single training runs.

Attention cost grows with the square of sequence length. *Building AI Agents* (ch. 3) puts it as 4,096 tokens costing 64× the attention compute of 512, which is (4,096 / 512)². The parameter count does not grow with context; only compute and the cache of keys and values do (next section).

---

## The transformer block and the GPT stack

A GPT is a stack of identical blocks (*LLMs from Scratch*, ch. 4):

```
x → LayerNorm → masked multi-head attention → + x  (residual)
  → LayerNorm → feed-forward (expand 4×, GELU, project back) → + x  (residual)
```

Then a final LayerNorm and a linear **output head** that projects back to vocabulary size to produce logits. GPT-2 small: 12 layers, 12 heads, d_model 768, 1,024-token context, about 124M parameters.

Three details that the diagram hides:

- **Pre-LayerNorm.** The norm sits *before* attention and the feed-forward layer, inside the residual branch. The original transformer normalized after the residual add (Post-LN), which trains worse in deep stacks (*LLMs from Scratch*, ch. 4). Many newer open models swap LayerNorm for the cheaper RMSNorm.
- **Weight tying.** Count Raschka's GPT-2 module by module and you get 163,009,536 parameters, not 124M. The gap is the output head (50,257 × 768 ≈ 38.6M). GPT-2 reuses the token-embedding matrix as the output projection, which brings the count to 124,412,160. Untied, the model takes 621.83 MB in 32-bit floats (*LLMs from Scratch*, ch. 4). Raschka keeps the two separate in his own model, saying separate layers train better and that "the same is true for modern LLMs". That holds for Llama 2 and most large open models, but small models often still tie (Gemma, Llama 3.2 1B and 3B), because there the embedding table is a large share of the total. Gemma 2B ties a 256,128-token vocabulary, and its embeddings alone are 524.6M of about 2.5B parameters, roughly 21% ([arXiv:2403.08295](https://arxiv.org/abs/2403.08295) (Gemma Team, 2024-03)). Qwen untied its embeddings "for better performance with the price of memory costs" ([arXiv:2309.16609](https://arxiv.org/abs/2309.16609) (Bai et al., 2023-09)). Qwen2.5 draws the line by size: **tied at 0.5B, 1.5B and 3B, untied from 7B up** ([arXiv:2412.15115](https://arxiv.org/abs/2412.15115) (Qwen Team, 2024-12)).
- **Where the parameters are.** Each block has four `d × d` attention matrices (Q, K, V and the output projection) and two feed-forward matrices of `d × 4d`. That is about 4d² + 8d² = 12d² per block, so the **feed-forward layer holds about two-thirds of a block's parameters**, and attention a third. *Building AI Agents* (ch. 3) says attention layers "hold the most parameters"; the arithmetic says otherwise.

![Diagram of a transformer: token and positional embeddings feed N transformer blocks, each with four attention matrices (Q, K, V, O) and two larger MLP matrices (FF1, FF2), followed by an output layer; a legend gives each matrix's shape in terms of d_model, d_ff, vocab size V and context C](../sources/images/huyen-ai-engineering-fig2-6.png)
*Image Source: Huyen, *AI Engineering* (O'Reilly, 2025), Fig. 2-6*

Huyen's figure makes a second point visible: no matrix inside the block has a dimension that depends on how many tokens you feed in. The only context-sized matrix is the learned position table (`C × d_model`), and rotary models do not have one. Context length changes compute and memory, not the parameter count (*AI Engineering*, ch. 2). *Building AI Agents* (ch. 3) says the weight matrices "can grow in size with context length", which is wrong for the same reason.

For scale, Huyen's table of Llama shapes (*AI Engineering*, ch. 2), from Meta's papers:

| Model | Blocks | d_model | Feed-forward dim | Vocab | Context |
|---|---|---|---|---|---|
| Llama 2-7B | 32 | 4,096 | 11,008 | 32K | 4K |
| Llama 2-70B | 80 | 8,192 | 22,016 | 32K | 4K |
| Llama 3-8B | 32 | 4,096 | 14,336 | 128K | 128K |
| Llama 3-405B | 126 | 16,384 | 53,248 | 128K | 128K |

The book labels the third row "Llama 3-7B"; the model is Llama 3-8B. Its 128K context is Llama 3.1's: Llama 3 as released in April 2024 had an 8K window. Llama's feed-forward layer uses SwiGLU, with three matrices and a hidden size of about 2.7 × d_model in place of GPT-2's two at 4×, so the 12d² rule is approximate for it.

### Prefill, decode and the KV cache

Running a decoder has two phases (*AI Engineering*, ch. 2):

- **Prefill.** The whole prompt goes through the model in one parallel pass. Every prompt token's keys and values are computed at once.
- **Decode.** Output tokens come one at a time, and each new token needs a full forward pass. The new token attends to the keys and values of everything before it, so those are stored rather than recomputed. That store is the **KV cache**; it grows linearly with context length and is what makes long contexts expensive to *serve*.

Decode is sequential, so latency adds up per token. Huyen's arithmetic: at 10 ms per token, a 100-token answer takes a full second, against the roughly 100 ms that users expect from a web request (*AI Engineering*, ch. 1). Serving tricks for both phases (batching, paged KV cache, speculative decoding) are in [ai-engineering/07-inference-engineering](../../../ai-engineering/07-inference-engineering/README.md).

One-token-per-step decoding comes from the training objective, not from the transformer itself. Muse trains a transformer to fill in masked image tokens, the way BERT fills in words, and then decodes a 256-token image in 24 parallel steps instead of 256. On Google's own TPUv4 timings, Muse-3B took 0.5 s per 256×256 image against 6.4 s for the autoregressive Parti-3B, with a similar zero-shot COCO FID (7.88 against 8.10) ([arXiv:2301.00704](https://arxiv.org/abs/2301.00704) (Chang et al., 2023-01)). The cost is an assumption that tokens filled in during the same step are independent of each other, given everything else. MusicGen measures that cost on audio tokens, where each time step has four codebook tokens. The test used a 300M model on 30-second clips from an in-domain test set ([arXiv:2306.05284](https://arxiv.org/abs/2306.05284) (Copet et al., 2023-06)):

- **Fully sequential** (6,000 steps): FAD 0.86.
- **All four codebooks at once** (1,500 steps): FAD worsened to 2.58.
- **Each codebook offset by one step from the last** (still 1,500 steps): FAD 0.96, recovering most of the loss.

![Four grids of audio tokens, codebooks k1 to k4 by sequence step: Flattening puts one codebook token per step, taking 4n steps; Parallel predicts all four codebooks of a time step together in n steps; Coarse First does all k1 tokens, then k2 to k4 together, in 2n steps; Delay shifts each codebook one step later than the one below, still about n steps](../sources/images/copet-musicgen-fig1.png)
*Image Source: Copet et al., [Simple and Controllable Music Generation](https://arxiv.org/abs/2306.05284) (2023), Fig. 1*

| Architecture | Attention | Training objective | Examples | Good at |
|---|---|---|---|---|
| Encoder-only | Bidirectional | Masked-token prediction | BERT ([arXiv:1810.04805](https://arxiv.org/abs/1810.04805)) | Classification, embeddings, retrieval |
| Decoder-only | Causal | Next-token prediction | GPT, Llama, Claude, Gemini | Generation, chat, tool use |
| Encoder–decoder | Both | Sequence-to-sequence | Original transformer, T5 | Translation, summarization |

BERT masks 15% of input tokens and learns to fill them in from both sides; the two original sizes were 110M and 340M parameters (*Building AI Agents*, ch. 2). Huyen frames the same split as *masked* versus *autoregressive* language models: the first sees both directions and suits classification and embeddings, the second sees only the past and can generate (*AI Engineering*, ch. 1).

Almost every chat model is decoder-only. Embedding models used in [02-rag-retrieval](../../02-rag-retrieval/README.md) are usually encoder-style.

The table says how a model was trained, but one model can serve more than one row. CodeT5+ trains a single encoder–decoder on a mix of span denoising, causal language modelling and text–code contrastive matching. It then runs the encoder alone for code search and the decoder alone for completion ([arXiv:2305.07922](https://arxiv.org/abs/2305.07922) (Wang et al., 2023-05)). After task fine-tuning, the 770M model scored 77.4 MRR on CodeSearchNet text-to-code retrieval, against UniXcoder's 74.4. The decoder-only mode depends on having trained for it: without the causal-LM objective, the same 770M model's line-completion exact match on PY150 fell from 44.9 to 36.2. These are the authors' own evaluations. The authors also say that Codex and CodeGen were trained on GitHub code without removing overlap with these benchmarks, so comparisons against those models are not clean.

---

## Scale

Three results explain why "large" is in the name:

| Result | Finding | Paper |
|---|---|---|
| Scaling laws | Loss falls as a smooth power law in parameters, data and compute | Kaplan et al. [arXiv:2001.08361](https://arxiv.org/abs/2001.08361) |
| In-context learning | At 175B parameters, GPT-3 does new tasks from a few examples in the prompt | Brown et al. [arXiv:2005.14165](https://arxiv.org/abs/2005.14165) |
| Compute-optimal training | For a fixed compute budget, train a smaller model on more data, roughly 20 tokens per parameter. Chinchilla (70B, 1.4T tokens) beat the 280B Gopher | Hoffmann et al. [arXiv:2203.15556](https://arxiv.org/abs/2203.15556) |

LLaMA ([arXiv:2302.13971](https://arxiv.org/abs/2302.13971)) applied the Chinchilla lesson with public data only: its 13B model beat GPT-3 (175B) on most benchmarks reported in the paper. The GPT-4 report ([arXiv:2303.08774](https://arxiv.org/abs/2303.08774)) adds that final loss could be predicted from runs using under 1/1,000th of the compute, while giving almost no architectural detail.

Lower loss does not translate directly into better task scores. Zhao et al.'s survey warns that "a direct decrease in language modeling loss does not always indicate an improvement of model performance on downstream tasks", and on some tasks performance gets worse as loss falls (inverse scaling). It defines *emergent abilities* as those "not present in small models but arise in large models", such as GPT-3's in-context learning. It also reports the debate over whether emergence is real: the sharp jumps "might be partially attributed to the evaluation setting for special tasks (e.g., the discontinuous evaluation metrics)", and they flatten when the metric is changed. The survey's reply is that users experience many tasks as pass/fail anyway, so code that fails its tests is worth nothing however close it came ([arXiv:2303.18223](https://arxiv.org/abs/2303.18223) (Zhao et al., 2023-03; v16, 2025-03)).

### Reading a model's size

Huyen names three numbers that signal scale: **parameters** (capacity to learn), **training tokens** (how much it learned) and **training FLOPs** (what it cost) (*AI Engineering*, ch. 2). Some reference points, all as reported in the book:

- **Parameters to memory.** At 2 bytes per parameter (16-bit weights), a 7B model needs at least 14 GB just to hold its weights, before activations and the KV cache.
- **Training tokens keep rising.** Llama 1 saw 1.4T tokens, Llama 2 2T and Llama 3 15T. GPT-3 trained on 300B tokens drawn from a 499B-token dataset (*LLMs from Scratch*, ch. 1).
- **"Large" moves.** GPT-1 had 117M parameters (2018) and GPT-2 1.5B (2019). Huyen calls 100B "large" at the time of writing (2024). *Building AI Agents* (ch. 3) defines an LLM as anything over 10B parameters and admits the line is arbitrary; read both as snapshots, not definitions.

**Sparse models break the link between parameters and cost.** In a mixture-of-experts (MoE) layer, the feed-forward block is replaced by several expert feed-forward blocks and a small router that sends each token to a few of them. Mixtral 8x7B has 46.7B parameters in total, but each token passes through only 12.9B, so it runs at roughly the cost of a 13B dense model while needing the memory of a 47B one (*AI Engineering*, ch. 2). *Building AI Agents* (ch. 3) says GPT-4 and Gemini are MoE models, and *Prompt Engineering for GenAI* (ch. 2) gives GPT-4 1.7T parameters. Neither figure has been confirmed by OpenAI or Google; they are press estimates. The same chapter dates GPT-4 to 2024; it was released in March 2023.

**Not every LLM is a transformer.** Huyen surveys the alternatives to quadratic attention (*AI Engineering*, ch. 2): RWKV, an RNN that can be trained in parallel; state-space models (S4, H3, Mamba), whose cost grows linearly with sequence length, with Mamba-3B reported to beat transformers of its size and match transformers twice its size; and Jamba, which interleaves transformer and Mamba layers in a 52B-total, 12B-active MoE with a 256K-token context. The Mamba comparison is the authors' own, on language-modelling benchmarks at up to 3B parameters. Every architecture in this note is still the transformer; the alternatives matter when context length, not parameter count, is the cost that hurts. Nor does every LLM generate left to right. Block diffusion is autoregressive over blocks of tokens and fills in each block by denoising, keeping the KV cache across blocks ([arXiv:2503.09573](https://arxiv.org/abs/2503.09573) (Arriola et al., 2025-03)). At 110M parameters on OpenWebText it narrows the perplexity gap with block size 4 (at most 20.73, against 17.54 for autoregressive and at most 22.98 for the earlier masked-diffusion model MDLM). It still trails, and the paper shows no wall-clock speedup at that scale.

The line between transformers and the alternatives is thinner than it looks. Mamba-2 shows that a state-space layer whose state transition is a scalar times the identity computes causal attention with the softmax removed and a learned, input-dependent decay applied to the scores. The same layer can therefore run as a linear-time recurrence or as quadratic matrix multiplications on tensor cores ([arXiv:2405.21060](https://arxiv.org/abs/2405.21060) (Dao & Gu, 2024-05)). At 2.7B parameters trained on 300B Pile tokens, Mamba-2 matched a Transformer++ baseline (Pile perplexity 6.09 against 6.13, zero-shot average 60.2 for both). Replacing 6 of its 64 layers with attention beat both (5.95, 61.0). The authors' guess is that attention does exact look-up of earlier tokens, while the SSM has to compress everything into a fixed-size state. In their 350M sweep, about 10% attention layers was best, but anything from 3 to 9 attention layers landed within 0.03 perplexity. xLSTM rebuilds the LSTM with exponential gates and a matrix-valued memory. At 1.3B parameters on 300B SlimPajama tokens it reached validation perplexity 8.89, against 9.14 for Mamba and 9.44 for a Llama-style transformer ([arXiv:2405.04517](https://arxiv.org/abs/2405.04517) (Beck et al., 2024-05)). Read both papers' comparisons with care: the authors trained every baseline themselves, ran each configuration once and stopped at 2.7B and 1.3B parameters. xLSTM's own paper says its kernels were about 4× slower than FlashAttention.

---

## Decoding

The model outputs logits; the decoder picks a token.

| Setting | Effect | Use |
|---|---|---|
| Greedy (temperature 0) | Always the top token | Extraction, classification, tests. Not perfectly deterministic on hosted APIs |
| Temperature > 0 | Flattens (>1) or sharpens (<1) the distribution before sampling | Creative or diverse output |
| Top-k / top-p (nucleus) / min-p | Sample only from the k most likely tokens, from the smallest set whose probabilities add up to p ([arXiv:1904.09751](https://arxiv.org/abs/1904.09751)), or from tokens above a minimum probability | Cuts off the long tail of nonsense |
| Max tokens / stop sequences | Hard stop | Cost control; the API reports `stop_reason` so you can tell truncation from completion |

**Temperature** divides the logits before the softmax: `softmax(logits / T)`. Huyen's two-token example (*AI Engineering*, ch. 2): with logits [1, 2], T = 1 gives probabilities [0.27, 0.73], and T = 0.5 gives [0.12, 0.88]. Below about T = 0.1 the model almost always picks the second token. Temperature 0 cannot literally be computed (division by zero), so it is implemented as "take the argmax". Providers usually cap T at 2, and Huyen reports 0.7 as a common starting point for creative work.

![Line chart of the softmax probabilities of two tokens with logits 1 and 2 as temperature goes from 0 to 5: token B starts at 1.0 and falls towards 0.55, token A rises from 0 towards 0.45, crossing 0.27/0.73 at temperature 1](../sources/images/huyen-ai-engineering-fig2-16.png)
*Image Source: Huyen, *AI Engineering* (O'Reilly, 2025), Fig. 2-16*

Raschka makes the same point by counting (*LLMs from Scratch*, ch. 5). On a toy nine-word vocabulary, sampling the next token 1,000 times from his model's distribution after "every effort moves you" gave "forward" 582 times, "toward" 343, "closer" 73 and "inches" 2. At T = 5 the nonsense continuation "pizza" came up about 4% of the time. Top-k with k = 3 removes it entirely. The sampling step, rewritten from his `generate()` (full version in [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch), ch05):

```python
logits = model(idx[:, -context_len:])[:, -1, :]               # last position only
if top_k:                                                      # keep the k largest logits
    kth = torch.topk(logits, top_k).values[:, [-1]]
    logits = logits.masked_fill(logits < kth, float("-inf"))
if temperature > 0:
    next_id = torch.multinomial(torch.softmax(logits / temperature, -1), 1)
else:
    next_id = logits.argmax(-1, keepdim=True)                  # greedy
idx = torch.cat([idx, next_id], dim=1)
```

Two things the books get wrong or overstate here:

- **Why top-k exists.** Huyen presents top-k as a way to "reduce the computation workload" of the softmax over a large vocabulary (*AI Engineering*, ch. 2). The model computes the full logit vector either way, and a softmax over 100K numbers is cheap next to the forward pass. The reason top-k was introduced (Fan et al., 2018) and the reason top-p replaced it (Holtzman et al., [arXiv:1904.09751](https://arxiv.org/abs/1904.09751)) is quality: the long tail of unlikely tokens, sampled often enough, derails the text. Huyen's practical ranges stand: k between 50 and 500, p between 0.9 and 0.95.
- **Greedy decoding is not obsolete.** *Building AI Agents* (ch. 2) says greedy decoding "is no longer used" because it is too predictable. It is the default for extraction, classification, code and evaluation runs, where predictable is the point.

**Logprobs** (the log of each sampled token's probability) are the window into all of this, useful for classification confidence and for debugging. Availability varies by provider and changes often: when Huyen wrote, OpenAI returned the top 20 alternatives per token and many providers exposed none, partly because logprobs make a model easier to copy (*AI Engineering*, ch. 2).

### Spending more compute at inference

Sampling a whole answer several times and picking one is **test-time compute** (*AI Engineering*, ch. 2):

- **Best-of-N.** Generate N answers and keep the one a reward model or verifier scores highest, or the one with the highest average log probability (average, so long answers are not penalized). **Beam search** does this token by token, keeping the k most promising partial sequences.
- **Majority vote (self-consistency).** For questions with one right answer, sample several and take the most common. Google's Gemini report did not score MMLU by plain majority vote. Its "uncertainty-routed chain-of-thought" takes 32 chain-of-thought samples and uses the majority answer only when agreement clears a threshold tuned on the validation split. Below that threshold it falls back to the greedy answer without chain of thought ([arXiv:2312.11805](https://arxiv.org/abs/2312.11805) (Gemini Team, 2023-12), appendix 10.2). The routing did the work. **Plain majority over 32 samples moved Gemini Ultra only from 84.0% to 85.0%; routing reached 90.04%.** GPT-4 (gpt-4-0613) got 87.3% either way. The headline compared Ultra's 90.04% with GPT-4's 86.4% at 5-shot, so the two numbers come from different methods. All of these are Google's own runs.
- **Verifiers are worth a lot.** On grade-school maths problems, OpenAI found a trained verifier gave about the same boost as a 30× larger model: a 100M-parameter model with a verifier matched a 3B model without one (Cobbe et al., 2021). Gains stopped at 400 samples per problem and then fell, which the authors attributed to more samples meaning more wrong answers that fool the verifier. Brown et al.'s "Monkey Business" (2024) found instead that the share of problems solved kept rising log-linearly up to 10,000 samples.

![Scatter plot with a fitted line of test solve rate (%) against completions per test problem on a log scale from 25 to 3,200: the rate rises from about 34.5% at 25 to a peak near 39.5% at 400, then declines to about 37% at 3,200](../sources/images/huyen-ai-engineering-fig2-19.png)
*Image Source: Huyen, *AI Engineering* (O'Reilly, 2025), Fig. 2-19, reproducing Cobbe et al. (2021)*

Huyen adds that she does not "believe anyone in production samples 400 or 10,000 different outputs for each input." That was written before reasoning models (OpenAI o1 shipped in September 2024). They spend their extra inference compute on one long chain of thought rather than many parallel samples, and most providers now charge for those hidden tokens. Test-time compute became a product setting; see [ai-engineering/01-prompt-engineering note 07](../../../ai-engineering/01-prompt-engineering/notes/07-prompting-reasoning-models.md).

A model can also spend extra compute without writing tokens, by running a block of layers more times. Geiping et al. trained a 3.5B model whose 4-layer core is iterated r times at inference, on 800B tokens ([arXiv:2502.05171](https://arxiv.org/abs/2502.05171) (Geiping et al., 2025-02)). **On GSM8K with chain of thought it scored 0.0% at r=1 and 34.8% (strict match) at r=32.** At r=32 its compute is about that of a 32–50B dense model. A fixed-depth model trained the same way to 180B tokens scored 1.8% against the recurrent model's 9.0% at that point. This is one training run, with the baseline compared only at 180B tokens and not matched for FLOPs, and the model still trails OLMo-2-7B (66.7%).

Sampling several outputs and checking whether they agree is also a cheap hallucination signal. SelfCheckGPT ([arXiv:2303.08896](https://arxiv.org/abs/2303.08896), Manakul et al., 2023) flags sentences that vary across samples as likely fabricated.

### Structured output is a decoding problem

If code will parse the answer, you need more than a polite request. Huyen ranks the options by how deep in the stack they act (*AI Engineering*, ch. 2): prompting for the format; post-processing (LinkedIn's defensive YAML parser took correct outputs from 90% to 99.99%); **constrained sampling**, which at each step masks the logits of every token the grammar does not allow, the same `-inf` trick as top-k; and fine-tuning, up to replacing the language-model head with a classifier head. A provider's "JSON mode" usually guarantees valid JSON, not JSON that matches your schema, and a response cut off by `max_tokens` is invalid whatever the mode. The API patterns are in [note 06](06-calling-models-from-code.md).

---

## Same input, different output

Huyen calls the probabilistic nature of a model the root of its two most reported problems (*AI Engineering*, ch. 2):

- **Inconsistency.** Sampling makes outputs vary by design. Fixing the temperature, top-p, top-k and seed reduces this but does not remove it: hosted models run on different machines, which do not execute the same arithmetic in exactly the same way, and on an API you do not choose the machine. Cache answers that must stay the same.
- **Hallucination.** Huyen reports two hypotheses for *why*, neither settled. In the first (Ortega et al., 2021, DeepMind), a model cannot tell the text it was given from the text it generated, so an early wrong token gets treated as fact and built on; Zhang et al. (2023) call this snowballing, with an example where a model, having started from a wrong assumption, claims that 9,677 is divisible by 13 although it answers correctly when asked directly. In the second (Leo Gao, then John Schulman in an April 2023 talk, both at OpenAI), supervised fine-tuning teaches a model to imitate labelers' answers that use knowledge the model does not have, which trains it to make things up. The first blames self-supervision, the second supervision, so they can both be true. Schulman said RLHF reduced hallucination at OpenAI; the InstructGPT paper measured the opposite, with RLHF plus SFT hallucinating more than SFT alone on its closed-domain tasks, even though labelers preferred the RLHF model overall. The practical upshot is the same either way: answer from provided context, ask for concise answers (fewer tokens, fewer chances to invent), and check claims.

---

## What a base model is not

A pretrained model continues text. Huyen calls it a "completion machine" (*AI Engineering*, ch. 1). Its training is *self-supervised*: the label for each position is the next token of the text, so the sentence "I love street food." yields six training examples, from (BOS → "I") to ("I love street food." → EOS), with no human labelling. That is why pretraining scales to trillions of tokens, and why the model learns what text looks like rather than what is true. Ask it a question and it may produce more questions. The assistant behaviour (answering, refusing, following a system prompt, calling tools) comes from post-training: supervised fine-tuning on demonstrations and then preference optimization. That pipeline is [note 02](02-training-and-adapting.md) and, in depth, [05-RL](../../05-RL/README.md).

---

**Next:** [02 — Training and adapting models](02-training-and-adapting.md) follows the weights from pretraining through SFT, RLHF and LoRA.
