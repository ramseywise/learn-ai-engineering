---
origin: curated
sources:
  - https://karpathy.ai/zero-to-hero.html
  - https://github.com/karpathy/nanoGPT
  - https://github.com/rasbt/LLMs-from-scratch
  - "Raschka, Build a Large Language Model (From Scratch) (Manning, 2024), ch. 2–5, appendix A"
confidence: high
cleaned: 2026-10-31
---

# 5 — Build a Tiny GPT

> The fastest way to make [note 01](01-how-llms-work.md) stick is to write it: a character-level GPT that trains on a laptop in minutes. Two routes cover the same ground; this note maps them and says what to check at each step.

---

## The two routes

| | Karpathy, *Neural Networks: Zero to Hero* | Raschka, *Build a Large Language Model (From Scratch)* |
|---|---|---|
| Format | Video lectures + notebooks | Book chapters + notebooks |
| Local copy | [data-science/practice/nn-zero-to-hero](../../../data-science/04-llms-from-scratch/practice/nn-zero-to-hero/README.md) (MIT) | Chapter PDFs listed in [references.md](../references.md#books) (purchased); code at [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) |
| Starts from | Scalar autograd (micrograd) | PyTorch basics (appendix A) |
| Tokenizer | Characters first; BPE in lecture 8 | BPE (tiktoken GPT-2) from ch. 2 |
| Ends at | GPT-2 (124M) reproduction in `build-nanogpt/` | Loading GPT-2 weights, then fine-tuning (ch. 6–7) |
| Best for | Intuition for gradients and training dynamics | A clean, chapter-by-chapter GPT-2 implementation |

Doing both is not redundant: Karpathy builds intuition from the bottom up, Raschka gives a tidy reference implementation to compare against.

---

## Step by step

| Step | Karpathy | Raschka | What you build |
|---|---|---|---|
| 1. Autograd and backprop | Lecture 1, `micrograd/` | Appendix A | A scalar `Value` class with `.backward()`, then the same idea in PyTorch tensors |
| 2. Language modelling framework | Lecture 2, `makemore_part1_bigrams` | Ch. 2 | Bigram model; negative log-likelihood; sampling |
| 3. Text → tensors | Lectures 2, 8 | Ch. 2 | Tokenizer, vocabulary, sliding-window (input, target) pairs, `DataLoader` |
| 4. MLP language model and training hygiene | Lectures 3–5 | — | Embeddings, train/dev/test splits, learning-rate search, activation and gradient statistics, BatchNorm, manual backprop |
| 5. Attention | Lecture 7 (first half) | Ch. 3 | Self-attention → causal mask → multi-head |
| 6. The GPT | Lecture 7, `nanogpt/gpt.py` | Ch. 4 | Transformer block (LayerNorm, attention, MLP, residuals), stacked, with an output head |
| 7. Pretraining | Lecture 7, `nanogpt/gpt.py` | Ch. 5 | Training loop, loss curves, temperature and top-k sampling, saving and loading weights |
| 8. Real scale | `nanogpt/build-nanogpt/` (GPT-2 on FineWeb, HellaSwag eval) | Ch. 5 (load OpenAI GPT-2 weights) | Confidence that your architecture matches the real one |

---

## The tiny model

The config in [`nanogpt/gpt.py`](../../../data-science/04-llms-from-scratch/practice/nn-zero-to-hero/nanogpt) trains a character-level model on Tiny Shakespeare:

```python
batch_size = 64      # sequences per step
block_size = 256     # context length in characters
n_embd     = 384     # model width
n_head     = 6
n_layer    = 6
dropout    = 0.2
learning_rate = 3e-4
max_iters  = 5000
```

That is about 10M parameters. It needs a GPU for the full run; on a laptop CPU, shrink `n_layer`, `n_embd` and `block_size` and it still learns recognisable pseudo-Shakespeare. Raschka's GPT-2 config (12 layers, 12 heads, width 768; *LLMs from Scratch*, ch. 4–5) is the same code at larger settings. OpenAI's released GPT-2 sizes are 124M, 355M, 774M and 1,558M parameters; the smallest checkpoint is a 498 MB download, and the larger ones differ only in width, depth and head count.

---

## Checks that catch most bugs

| Check | Expected | If not |
|---|---|---|
| Loss at step 0 | ≈ `ln(vocab_size)`: 4.17 for 65 characters, 10.8 for GPT-2's 50,257 tokens | Initialization or a wrong target shift |
| Overfit one batch | Loss falls towards 0 within a few hundred steps | Bug in the model or optimizer wiring |
| Causal mask | Changing token *t+1* does not change the logits at position *t* | The mask is missing or transposed |
| Train vs val loss | Track together; a widening gap means overfitting. On a 5,145-token story, 10 epochs drive train loss to 0.39 while validation stalls near 6.4: the model is memorizing ([note 02](02-training-and-adapting.md#pretraining) has the plot) | More data, more dropout or a smaller model |
| Samples during training | Gibberish → words → plausible lines | If samples stop improving while loss falls, check the sampling code |
| Parameter count | Matches a hand calculation (embedding + 12·d² per block + head, roughly). For GPT-2 small: 163,009,536 with a separate output head, 124,412,160 with the head tied to the token embedding (*LLMs from Scratch*, ch. 4) | Weight tying or layer sizes are off |
| Pretrained weights load | Every tensor shape matches and sampled text is fluent | For OpenAI's GPT-2 checkpoints, set `qkv_bias=True` and context 1,024: GPT-2 has bias terms on the Q/K/V projections. Raschka says biases are "not commonly used in LLMs anymore"; that is true of Llama, but not of every family (Qwen2 keeps a Q/K/V bias), so read the config of the model you load |

---

## What this teaches that the API does not

- Why context length costs quadratic compute: you will write the `T × T` attention matrix yourself.
- Why temperature 0 and top-k behave as they do: you will implement them. The ten-line sampling step is in [note 01](01-how-llms-work.md#decoding). Raschka's own settings are a useful reference: `top_k=25, temperature=1.4` for his story-trained model, `top_k=50, temperature=1.5` once the real GPT-2 weights are loaded (*LLMs from Scratch*, ch. 5).
- Why fine-tuning on a few examples overfits: you will watch val loss turn.
- Why hallucination is structural: the model you trained produces confident text with no notion of truth.

---

**Next:** [06 — Calling models from code](06-calling-models-from-code.md) goes back up to the API, now knowing what sits behind it.
