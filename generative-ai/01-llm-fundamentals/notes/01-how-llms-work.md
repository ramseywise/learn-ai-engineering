---
origin: synthesis
sources:
  - https://arxiv.org/abs/1706.03762
  - https://arxiv.org/abs/2005.14165
  - https://arxiv.org/abs/2001.08361
  - https://arxiv.org/abs/2203.15556
  - https://arxiv.org/abs/2302.13971
  - https://arxiv.org/abs/2303.08774
  - "Raschka, Build a Large Language Model (From Scratch) (Manning, 2024), ch. 1–4"
  - "Phoenix & Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 2"
  - https://arxiv.org/abs/2108.12409
  - https://arxiv.org/abs/2303.12712
  - https://arxiv.org/abs/2303.18223
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

- **Byte-pair encoding (BPE)** starts from bytes or characters and repeatedly merges the most frequent adjacent pair until the vocabulary reaches a target size. GPT-2's BPE vocabulary has 50,257 entries (Raschka ch. 2). WordPiece (BERT) and SentencePiece (T5, Llama) are close relatives.
- Common words are one token; rare words, code identifiers and non-English text split into several. A rough English rule: **100 tokens ≈ 75 words** (O'Reilly ch. 2).
- Tokens are the unit of **cost, latency and context length**. A 200k-token context window is a token budget, not a word budget.

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

---

## Attention

Self-attention lets every token build its representation from every other token it can see ([arXiv:1706.03762](https://arxiv.org/abs/1706.03762), Vaswani et al., 2017). Each token is projected into a **query**, a **key** and a **value**:

```
Attention(Q, K, V) = softmax(Q Kᵀ / √d_k) · V
```

- `Q Kᵀ` scores how relevant each token is to each other token.
- Dividing by `√d_k` keeps the softmax from saturating as dimensions grow.
- The softmax turns scores into weights; the output is a weighted sum of values.

Three refinements make it a language-model layer (Raschka ch. 3 builds each in turn):

1. **Causal mask.** A decoder may only attend to earlier positions. Future positions are set to −∞ before the softmax, so training on "predict token *t* from tokens < *t*" is honest.
2. **Multi-head attention.** Several attention heads run in parallel on lower-dimensional projections and are concatenated. Different heads learn different relations (syntax, coreference, copying).
3. **Dropout on attention weights** during training, for regularization.

Attention cost grows with the square of sequence length. That is why long contexts are expensive and why inference engines cache keys and values (the KV cache; see [ai-engineering/07-inference-engineering](../../../ai-engineering/07-inference-engineering/README.md)).

---

## The transformer block and the GPT stack

A GPT is a stack of identical blocks (Raschka ch. 4):

```
x → LayerNorm → masked multi-head attention → + x  (residual)
  → LayerNorm → feed-forward (expand 4×, GELU, project back) → + x  (residual)
```

Then a final LayerNorm and a linear **output head** that projects back to vocabulary size to produce logits. GPT-2 small: 12 layers, 12 heads, d_model 768, 1,024-token context, about 124M parameters.

| Architecture | Attention | Training objective | Examples | Good at |
|---|---|---|---|---|
| Encoder-only | Bidirectional | Masked-token prediction | BERT ([arXiv:1810.04805](https://arxiv.org/abs/1810.04805)) | Classification, embeddings, retrieval |
| Decoder-only | Causal | Next-token prediction | GPT, Llama, Claude, Gemini | Generation, chat, tool use |
| Encoder–decoder | Both | Sequence-to-sequence | Original transformer, T5 | Translation, summarization |

Almost every chat model is decoder-only. Embedding models used in [02-rag-retrieval](../../02-rag-retrieval/README.md) are usually encoder-style.

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

---

## Decoding

The model outputs logits; the decoder picks a token.

| Setting | Effect | Use |
|---|---|---|
| Greedy (temperature 0) | Always the top token | Extraction, classification, tests. Not perfectly deterministic on hosted APIs |
| Temperature > 0 | Flattens (>1) or sharpens (<1) the distribution before sampling | Creative or diverse output |
| Top-k / top-p (nucleus) | Sample only from the k most likely, or the smallest set with cumulative probability p ([arXiv:1904.09751](https://arxiv.org/abs/1904.09751)) | Cuts off the long tail of nonsense |
| Max tokens / stop sequences | Hard stop | Cost control; the API reports `stop_reason` so you can tell truncation from completion |

Sampling several outputs and checking whether they agree is a cheap hallucination signal. SelfCheckGPT ([arXiv:2303.08896](https://arxiv.org/abs/2303.08896), Manakul et al., 2023) flags sentences that vary across samples as likely fabricated.

---

## What a base model is not

A pretrained model continues text. Ask it a question and it may produce more questions. The assistant behaviour (answering, refusing, following a system prompt, calling tools) comes from post-training: supervised fine-tuning on demonstrations and then preference optimization. That pipeline is [note 02](02-training-and-adapting.md) and, in depth, [05-RL](../../05-RL/README.md).

---

**Next:** [02 — Training and adapting models](02-training-and-adapting.md) follows the weights from pretraining through SFT, RLHF and LoRA.
