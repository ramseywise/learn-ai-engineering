---
origin: vendored snapshot: nn-zero-to-hero (Karpathy, MIT; kept as practice)
sources:
  - ../practice/nn-zero-to-hero/nanogpt/ (bigram.py, gpt.py, build-nanogpt/)
  - https://www.youtube.com/watch?v=kCc8FmEb1nY (Let's build GPT)
  - https://youtu.be/l8pRSuU81PU (Let's reproduce GPT-2 124M)
  - Vaswani et al. 2017, Attention Is All You Need
  - Radford et al. 2019, Language Models are Unsupervised Multitask Learners (GPT-2)
confidence: high
cleaned: 2026-10-31
---
# 17 — nanoGPT: the Transformer from Scratch

> Two lectures. First, grow a character-level bigram model on Tiny Shakespeare into a decoder-only transformer, one idea at a time: self-attention, multiple heads, feed-forward, residual connections, LayerNorm, dropout. Second, write GPT-2 (124M) from an empty file, load OpenAI's weights to check it, then train it from scratch on 10B tokens with every trick that makes it fast. This is where data science hands over to [`../../generative-ai/01-llm-fundamentals/README.md`](../../generative-ai/01-llm-fundamentals/README.md).

---

## Part 1: Let's build GPT (`bigram.py` → `gpt.py`)

### Data and the baseline

Tiny Shakespeare (`input.txt`, 1.1 MB, 65 unique characters), character-level tokens, 90/10 train/val split. Batches are random windows of `block_size` characters; every position in a window is a training example, so a window of 8 gives 8 (context → next char) pairs.

```python
def get_batch(split):
    data = train_data if split == "train" else val_data
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i:i + block_size] for i in ix])
    y = torch.stack([data[i + 1:i + block_size + 1] for i in ix])   # targets: shifted by one
    return x, y

class BigramLanguageModel(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.token_embedding_table = nn.Embedding(vocab_size, vocab_size)   # each token reads off logits for the next
    def forward(self, idx, targets=None):
        logits = self.token_embedding_table(idx)                   # (B, T, C)
        loss = None if targets is None else F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss
    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            logits, _ = self(idx[:, -block_size:])                  # crop to the context the model supports
            probs = F.softmax(logits[:, -1, :], dim=-1)             # last position only
            idx = torch.cat((idx, torch.multinomial(probs, 1)), dim=1)
        return idx
```

The bigram reaches a val loss of about 2.5 and produces gibberish with Shakespearean formatting. `estimate_loss()` averages over `eval_iters` batches under `@torch.no_grad()` and `model.eval()`, so the reported number isn't the noise of one batch.

### The mathematical trick: weighted aggregation as a matrix multiply

Tokens need to talk to earlier tokens, and only earlier ones (the model must not see the future it is predicting). The simplest communication is averaging the past. Done with a lower-triangular matrix:

```python
T = 8
tril = torch.tril(torch.ones(T, T))
wei = torch.zeros(T, T).masked_fill(tril == 0, float("-inf"))   # future positions get -inf
wei = F.softmax(wei, dim=-1)                                    # each row: uniform weights over positions ≤ t
xbow = wei @ x                                                  # (T, T) @ (B, T, C) → (B, T, C): running averages
```

The three versions in the lecture (explicit loop, `tril / tril.sum`, masked softmax) are identical; the softmax version matters because the weights no longer have to be uniform. Make them **data-dependent** and you have attention.

### Self-attention

Every token emits a **query** (what am I looking for), a **key** (what do I contain), and a **value** (what I'll pass on if you attend to me). Affinity = query · key.

```python
class Head(nn.Module):
    def __init__(self, head_size):
        super().__init__()
        self.key   = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer("tril", torch.tril(torch.ones(block_size, block_size)))
        self.dropout = nn.Dropout(dropout)
    def forward(self, x):
        B, T, C = x.shape
        k, q = self.key(x), self.query(x)                               # (B, T, hs)
        wei = q @ k.transpose(-2, -1) * k.shape[-1] ** -0.5             # (B, T, T), scaled
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float("-inf"))   # causal mask: decoder
        wei = self.dropout(F.softmax(wei, dim=-1))
        return wei @ self.value(x)                                      # (B, T, hs)
```

| Note from the lecture | Why |
|---|---|
| Attention is communication on a directed graph | Nodes aggregate values from nodes that point to them; the mask defines the graph |
| No notion of position | Attention is a set operation, so add **positional embeddings** (`nn.Embedding(block_size, n_embd)`) to the token embeddings |
| Batch elements never talk | Each sequence is processed independently |
| Remove the mask → encoder block | Sentiment, NER: all tokens see each other ([14](14-neural-text-models.md)'s BERT pipelines) |
| Self- vs cross-attention | Self: q, k, v all from `x`. Cross: q from `x`, k and v from another source (an encoder, in translation) |
| Scale by `1/sqrt(head_size)` | q·k has variance ≈ head_size; without scaling softmax saturates towards one-hot at init (the same saturation story as tanh in [16](16-makemore.md#part-3-activations-gradients-and-batchnorm)) |

### From one head to a transformer block

```python
class MultiHeadAttention(nn.Module):              # several heads in parallel, concatenated, projected
    def __init__(self, num_heads, head_size):
        super().__init__()
        self.heads = nn.ModuleList([Head(head_size) for _ in range(num_heads)])
        self.proj = nn.Linear(head_size * num_heads, n_embd)
        self.dropout = nn.Dropout(dropout)
    def forward(self, x):
        return self.dropout(self.proj(torch.cat([h(x) for h in self.heads], dim=-1)))

class FeedForward(nn.Module):                     # per-token computation: "think about what was gathered"
    def __init__(self, n_embd):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(n_embd, 4 * n_embd), nn.ReLU(),
                                 nn.Linear(4 * n_embd, n_embd), nn.Dropout(dropout))
    def forward(self, x): return self.net(x)

class Block(nn.Module):
    def __init__(self, n_embd, n_head):
        super().__init__()
        self.sa = MultiHeadAttention(n_head, n_embd // n_head)
        self.ffwd = FeedForward(n_embd)
        self.ln1, self.ln2 = nn.LayerNorm(n_embd), nn.LayerNorm(n_embd)
    def forward(self, x):
        x = x + self.sa(self.ln1(x))        # residual + pre-norm
        x = x + self.ffwd(self.ln2(x))
        return x
```

The full model: token embedding + position embedding → `n_layer` blocks → final LayerNorm → linear head to vocabulary logits.

| Addition | Problem it solves | Val loss trend |
|---|---|---|
| Single head (`head_size = 32`) | Tokens can look back selectively | ~2.4 |
| 4 heads of 8 | Several kinds of relation at once | ~2.28 |
| Feed-forward per token | Computation after communication | ~2.24 |
| Stack blocks | Depth; but optimisation gets hard | worse without the next two |
| **Residual connections** | A gradient superhighway: `+` routes gradient unchanged to every block (micrograd's addition rule, [15](15-micrograd.md)); blocks start near identity and phase in | ~2.08 |
| **LayerNorm**, pre-norm | Normalise each token's features; per-example, so unlike BatchNorm no batch coupling and train = inference | ~2.06 |
| Scale up + dropout 0.2 | `n_embd=384, n_head=6, n_layer=6, block_size=256, lr=3e-4`, 10.8M params, ~15 min on an A100 | **~1.48** |

The output (`more.txt`) is convincingly Shakespeare-shaped nonsense: "LUCIO: We muse hath resistes him so sovere". Pre-norm (LayerNorm before each sublayer) differs from the 2017 paper's post-norm and is what GPT-2 onward use.

What Part 1 deliberately leaves out: the encoder and cross-attention (needed for translation, not for a pure language model), and everything after pre-training (supervised fine-tuning and RLHF; ChatGPT = this + those stages, see [`../../generative-ai/01-llm-fundamentals/README.md`](../../generative-ai/01-llm-fundamentals/README.md)).

---

## Part 2: Let's reproduce GPT-2 (124M) (`build-nanogpt/`)

### Same architecture, GPT-2 names

```python
@dataclass
class GPTConfig:
    block_size: int = 1024    # context length
    vocab_size: int = 50257   # 50,000 BPE merges + 256 byte tokens + <|endoftext|>
    n_layer: int = 12
    n_head: int = 12
    n_embd: int = 768
```

`train_gpt2.py` matches Hugging Face's parameter names (`transformer.wte`, `wpe`, `h.N.attn.c_attn`, `ln_f`, `lm_head`) so `GPT.from_pretrained("gpt2")` can copy OpenAI's weights in (transposing the Conv1D-style weights) and generate sensible text: the proof the architecture is right before spending money training it. `play.ipynb` explores the HF checkpoint: the 1024×768 learned position embeddings show sinusoid-like structure, and a manual sampling loop reproduces `pipeline("text-generation")` with top-k 50.

Differences from Part 1:

| Change | Detail |
|---|---|
| BPE tokens, not characters | `tiktoken.get_encoding("gpt2")`; 50,257 tokens; ~4 chars per token |
| Fused QKV + flash attention | One `c_attn` linear makes q, k, v; `F.scaled_dot_product_attention(q, k, v, is_causal=True)` never materialises the T×T matrix |
| GELU (tanh approximation) | Smoother than ReLU, as in GPT-2 |
| **Weight tying** | `wte.weight = lm_head.weight`: input embedding and output projection share 38.6M params (~30% of the model) |
| Init | std 0.02; residual projections scaled by `(2 · n_layer) ** -0.5` (`NANOGPT_SCALE_INIT`) so the residual stream's variance doesn't grow with depth |
| Sanity check | Initial loss should be `−ln(1/50257) ≈ 10.8` |

### Making it fast (on one GPU, then eight)

| Step | Effect (A100, as reported in the lecture) |
|---|---|
| Baseline fp32 | ~1,000 ms per step at B=16, T=1024 |
| `torch.set_float32_matmul_precision("high")` (TF32) | ~3× faster matmuls, same code |
| `torch.autocast(dtype=torch.bfloat16)` | Activations in bf16; no gradient scaler needed (same exponent range as fp32) |
| `torch.compile(model)` | Kernel fusion, fewer memory round-trips (disabled in the final script because it broke HellaSwag eval and generation) |
| Flash attention | Big win: memory-bound softmax avoided |
| "Nice numbers": vocab 50257 → 50304 (divisible by 128) | ~4% faster despite more work: kernels prefer powers of two |
| Fused AdamW | One kernel for the update |
| DDP on 8 GPUs (`torchrun --nproc_per_node=8`) | ~1.5M tokens/s; gradient all-reduce only on the last micro-step |

From ~1,000 ms to under 100 ms per step on one GPU, before going to eight. These are the same levers covered systematically in the ai-engineering inference and systems material.

### Training recipe (following GPT-3's paper)

```python
total_batch_size = 524_288                         # 2**19 ≈ 0.5M tokens per step, as GPT-3 small
B, T = 64, 1024
grad_accum_steps = total_batch_size // (B * T * ddp_world_size)

max_lr, min_lr = 6e-4, 6e-5
warmup_steps, max_steps = 715, 19_073              # 19,073 × 0.5M ≈ 10B tokens = 1 epoch of the data
def get_lr(it):
    if it < warmup_steps:
        return max_lr * (it + 1) / warmup_steps                         # linear warm-up
    if it > max_steps:
        return min_lr
    ratio = (it - warmup_steps) / (max_steps - warmup_steps)
    return min_lr + 0.5 * (1 + math.cos(math.pi * ratio)) * (max_lr - min_lr)   # cosine decay

optimizer = torch.optim.AdamW(groups, lr=max_lr, betas=(0.9, 0.95), eps=1e-8, fused=True)
# weight_decay=0.1 on 2-d params (matmuls, embeddings) only; none on biases and LayerNorm gains

for micro_step in range(grad_accum_steps):
    x, y = train_loader.next_batch()
    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        logits, loss = model(x, y)
    loss = loss / grad_accum_steps                 # accumulate the MEAN, not the sum
    loss.backward()
norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)   # guards against a bad batch
```

`loss / grad_accum_steps` is the subtle one: cross-entropy already averages over B·T, so summing gradients from several micro-batches without dividing makes the effective learning rate `grad_accum_steps` times too large.

### Data and evaluation

| Piece | File | Detail |
|---|---|---|
| Training data | `fineweb.py` | FineWeb-Edu `sample-10BT` from Hugging Face, tokenised with tiktoken into 100 shards of 100M tokens stored as `uint16` |
| Validation loss | `train_gpt2.py` | Held-out FineWeb shard every 250 steps |
| HellaSwag | `hellaswag.py` | 10k sentence-completion items, 4 endings each; score each ending by the model's average loss over its tokens, pick the lowest; random = 0.25 |
| Samples | `train_gpt2.py` | "Hello, I'm a language model," continued, every 250 steps |

Outcome: one epoch of 10B tokens (~2 hours on 8×A100, roughly $10–20 of rented GPU) surpasses OpenAI's GPT-2 124M on HellaSwag (~0.29), which was trained on ~100B tokens; training for 40B tokens approaches GPT-3 124M (~0.34). Cleaner, educational data (FineWeb-Edu vs WebText) accounts for much of the efficiency, with the caveat that HellaSwag may have leaked into newer web crawls.

---

## The whole data-science arc, in one table

| Note | Model | Learns from | Context |
|---|---|---|---|
| [02](02-supervised-learning.md) | Logistic regression | Hand-made features | — |
| [09](09-text-classification.md) | TF-IDF + LR | Word counts | Bag of n-grams |
| [11](11-embeddings-and-similarity.md) | word2vec | Co-occurrence | Window of ~5 |
| [14](14-neural-text-models.md) | LSTM | Labels or next word | Recurrent state |
| [16](16-makemore.md) | MLP / WaveNet | Next character | 3–8 chars |
| 17 | Transformer | Next token, 10B tokens | 1,024 tokens, full attention |

What comes next is scale, instruction tuning, RLHF, and using these models as components: tokenisation and model internals in [`../../generative-ai/01-llm-fundamentals/README.md`](../../generative-ai/01-llm-fundamentals/README.md), retrieval in [`../../generative-ai/02-rag-retrieval/README.md`](../../generative-ai/02-rag-retrieval/README.md).

---

## Practice

| File | Covers | Runs |
|---|---|---|
| [`nanogpt/bigram.py`](../practice/nn-zero-to-hero/nanogpt/bigram.py) | Batching, bigram LM, `estimate_loss`, generation | Runs offline on CPU in a minute; `input.txt` included |
| [`nanogpt/gpt.py`](../practice/nn-zero-to-hero/nanogpt/gpt.py) | Full decoder-only transformer, char-level | Runs offline; GPU for the default config (~15 min A100); shrink `n_embd`, `n_layer`, `block_size` to train on CPU or Apple `mps` |
| [`build-nanogpt/play.ipynb`](../practice/nn-zero-to-hero/nanogpt/build-nanogpt/play.ipynb) | HF GPT-2 weights, manual top-k sampling | Needs internet (HF download, ~500 MB); the sampling cell hard-codes `cuda` (change to `cpu`/`mps`) |
| [`build-nanogpt/train_gpt2.py`](../practice/nn-zero-to-hero/nanogpt/build-nanogpt/train_gpt2.py) | GPT-2 124M from scratch: init, bf16, flash attention, AdamW, cosine schedule, grad accumulation, DDP, HellaSwag | GPU: 8×A100/H100 for the full run (single GPU works, slowly); needs `fineweb.py` data (~20 GB of shards) and `tiktoken`; `--nproc_per_node` via `torchrun` |
| [`build-nanogpt/fineweb.py`](../practice/nn-zero-to-hero/nanogpt/build-nanogpt/fineweb.py) | Tokenise FineWeb-Edu 10B into shards | Needs internet, `datasets`, many CPU cores, ~20 GB disk |
| [`build-nanogpt/hellaswag.py`](../practice/nn-zero-to-hero/nanogpt/build-nanogpt/hellaswag.py) | HellaSwag download and evaluation | Needs internet; GPU recommended |

Lectures: [Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY) (2 h), [Let's reproduce GPT-2 (124M)](https://youtu.be/l8pRSuU81PU) (4 h). The step-by-step commit history is in [karpathy/build-nanogpt](https://github.com/karpathy/build-nanogpt).

---

→ Next layer: [`../../generative-ai/01-llm-fundamentals/README.md`](../../generative-ai/01-llm-fundamentals/README.md) — LLMs as systems: tokenisation, pre-training at scale, post-training, inference.
